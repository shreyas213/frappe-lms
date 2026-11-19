# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.core.doctype.navbar_settings.navbar_settings import get_app_logo

no_cache = 1

def get_context(context):
	if frappe.session.user != "Guest":
		frappe.local.flags.redirect_location = "/lms"
		raise frappe.Redirect

	context.no_cache = 1
	context.title = _("Sign Up")
	context.app_name = (
		frappe.get_website_settings("app_name")
		or frappe.get_system_settings("app_name")
		or _("Frappe LMS")
	)
	context.logo = get_app_logo() or "/assets/lms/images/lms-logo.png"
	context.custom_signup_content = frappe.db.get_single_value(
		"LMS Settings", "custom_signup_content"
	)
	context.user_category = frappe.db.get_single_value("LMS Settings", "user_category")
