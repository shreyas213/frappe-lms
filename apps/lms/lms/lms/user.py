import time

import frappe
from frappe import _
from frappe.model.naming import append_number_if_name_exists
from frappe.rate_limiter import rate_limit
from frappe.utils import cint, escape_html, random_string
from frappe.website.utils import cleanup_page_name, is_signup_disabled

from lms.lms.utils import get_country_code, get_lms_route


def validate_username_duplicates(doc, method):
	while not doc.username or doc.username_exists():
		doc.username = append_number_if_name_exists(
			doc.doctype, cleanup_page_name(doc.full_name), fieldname="username"
		)
	if " " in doc.username:
		doc.username = doc.username.replace(" ", "")

	if len(doc.username) < 4:
		doc.username = doc.email.replace("@", "").replace(".", "")


def add_lms_student_role(doc, method):
	doc.append_roles("LMS Student")


def get_signup_limit() -> int:
	"""Maximum allowed sign-ups per minute for rate limiting.
	Uses site_config / conf if specified, or Website Settings if the field exists in the running Frappe version;
	falls back safely to 500 without raising a ValidationError."""
	if frappe.conf.get("max_signups_per_minute"):
		return cint(frappe.conf.get("max_signups_per_minute"))

	if frappe.get_meta("Website Settings").has_field("max_signups_per_minute"):
		return cint(frappe.db.get_single_value("Website Settings", "max_signups_per_minute")) or 500

	return 500


@frappe.whitelist(allow_guest=True)  # nosemgrep: frappe-semgrep-rules.rules.security.guest-whitelisted-method
@rate_limit(limit=lambda: get_signup_limit(), seconds=60)
def sign_up(email: str, full_name: str, verify_terms: bool = False, user_category: str = "", password: str = None):
	"""Answers the same for every address: an account's existence, and whether it
	is disabled, are not for a guest to learn. No mail goes to an existing
	address either: the sign-up limit is far looser than the reset limit."""
	if is_signup_disabled():
		frappe.throw(_("Sign Up is disabled"), title=_("Not Allowed"))

	if password and len(password) < 6:
		frappe.throw(_("Password must be at least 6 characters long."), title=_("Invalid Password"))

	# Before the lookup, so the cap reads the same whatever the address. A 429
	# with a JSON body is what the sign-up page knows how to show.
	max_signups_allowed_per_hour = cint(frappe.get_system_settings("max_signups_allowed_per_hour") or 300)
	users_created_past_hour = frappe.db.get_creation_count("User", 60)
	if users_created_past_hour >= max_signups_allowed_per_hour:
		frappe.throw(
			_(
				"Too many users signed up recently, so the registration is disabled. Please try back in an hour"
			),
			frappe.RateLimitExceededError,
			title=_("Temporarily Disabled"),
		)

	reply = signed_up_reply(has_password=bool(password))
	if frappe.db.get("User", {"email": email}):
		return reply

	default_role = frappe.db.get_single_value("Portal Settings", "default_role")

	# Concurrent signups deadlock on User insert (Frappe doesn't retry 1213); retry, and append roles pre-insert to keep it to one transaction.
	for attempt in range(3):
		try:
			user = frappe.get_doc(
				{
					"doctype": "User",
					"email": email,
					"first_name": escape_html(full_name),
					"verify_terms": verify_terms,
					"user_category": user_category,
					"country": "",
					"enabled": 1,
					"new_password": password or random_string(10),
					"send_welcome_email": 0 if password else 1,
					"user_type": "Website User",
				}
			)
			user.flags.ignore_permissions = True
			user.flags.ignore_password_policy = True
			if default_role:
				user.append_roles(default_role)
			user.insert()
			break
		except frappe.DuplicateEntryError:
			# A concurrent signup for the same email won the race.
			frappe.db.rollback()
			return reply
		except frappe.QueryDeadlockError:
			frappe.db.rollback()
			if attempt == 2:
				raise
			time.sleep(0.1 * (attempt + 1))

	set_country_from_ip(None, user.name)
	return reply


def signed_up_reply(has_password: bool = False) -> tuple[int, str]:
	"""One reply for every address, from one question: can the site send mail.
	The welcome mail asks the same, so a new user's inbox matches the answer.
	The page shows code 1 as success and code 2 as "ask your administrator"."""
	from frappe.email.doctype.email_account.email_account import EmailAccount

	if has_password:
		return 1, _("Account created successfully! You can now log in.")
	if EmailAccount.find_default_outgoing():
		return 1, _("If this email can be used, you will get an email with the next step.")
	return 2, _("Signup successful. Please ask your administrator to verify your sign-up.")


@frappe.whitelist()
def admin_verify_student(email: str, new_password: str = None):
	"""Administrator-controlled verification fallback for local development or approval."""
	frappe.only_for("System Manager")

	if not email or not isinstance(email, str):
		frappe.throw(_("Email is required."))

	user = frappe.get_doc("User", email)
	user.enabled = 1
	if new_password:
		user.new_password = new_password
	user.flags.ignore_permissions = True
	user.flags.ignore_password_policy = True
	user.save()

	# Ensure student role is assigned
	if "LMS Student" not in frappe.get_roles(user.name):
		user.add_roles("LMS Student")

	return {
		"success": True,
		"email": user.email,
		"enabled": user.enabled,
		"message": _("Student account {0} verified and enabled successfully.").format(email),
	}


def set_country_from_ip(login_manager: object = None, user: str = None):
	if not user and login_manager:
		user = login_manager.user
	user_country = frappe.db.get_value("User", user, "country")
	if user_country:
		return
	frappe.db.set_value("User", user, "country", get_country_code())
	return


def on_login(login_manager):
	default_app = frappe.db.get_single_value("System Settings", "default_app")
	if default_app == "lms":
		frappe.local.response["home_page"] = get_lms_route()
