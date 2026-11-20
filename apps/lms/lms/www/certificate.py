# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

from urllib.parse import quote
import frappe
from frappe import _
from frappe.utils import format_date, get_url


def get_context(context):
	context.no_cache = 1
	context.title = _("Certificate Verification")

	# Allow certificate_id, id, cert, or code in query params or POST form
	cert_id = (
		frappe.form_dict.get("certificate_id")
		or frappe.form_dict.get("id")
		or frappe.form_dict.get("cert")
		or frappe.form_dict.get("code")
	)

	if cert_id:
		cert_id = cert_id.strip()

	# If download=1 is requested, redirect directly to official PDF generation
	if cert_id and (frappe.form_dict.get("download") in ("1", "true", "yes")):
		cert_doc = frappe.db.get_value(
			"LMS Certificate",
			cert_id,
			["name", "template", "published"],
			as_dict=True,
		)
		if cert_doc:
			template = quote(cert_doc.template or "Certificate")
			frappe.local.flags.redirect_location = (
				f"/api/method/frappe.utils.print_format.download_pdf?doctype=LMS+Certificate&name={quote(cert_doc.name)}&format={template}&no_letterhead=1"
			)
			raise frappe.Redirect

	context.searched_id = cert_id or ""
	context.is_valid = False
	context.not_found = False

	# Fetch site / institute branding
	brand_name = frappe.db.get_single_value("Website Settings", "app_name") or "Frappe LMS Academy"
	banner_image = frappe.db.get_single_value("Website Settings", "banner_image") or "/assets/lms/images/lms-logo.png"
	context.institute_name = brand_name
	context.institute_logo = banner_image

	if not cert_id:
		return

	cert = frappe.db.get_value(
		"LMS Certificate",
		cert_id,
		[
			"name",
			"member",
			"member_name",
			"course",
			"course_title",
			"batch_name",
			"batch_title",
			"issue_date",
			"expiry_date",
			"template",
			"published",
		],
		as_dict=True,
	)

	if not cert:
		context.not_found = True
		return

	# Only public certificates or authenticated owner/admin
	user = frappe.session.user
	is_admin = False
	if user != "Guest":
		roles = frappe.get_roles(user)
		is_admin = bool({"System Manager", "Administrator", "Course Creator", "Moderator"} & set(roles))

	# Safe student public display name (never expose private email, phone, or password)
	member_name = cert.member_name
	if not member_name and cert.member:
		member_name = frappe.db.get_value("User", cert.member, "full_name") or cert.member

	# Course title
	title = cert.course_title or cert.batch_title
	if not title and cert.course:
		title = frappe.db.get_value("LMS Course", cert.course, "title") or cert.course

	context.is_valid = True
	context.certificate = {
		"id": cert.name,
		"member_name": member_name,
		"course_title": title,
		"issue_date": format_date(cert.issue_date, "dd MMMM yyyy") if cert.issue_date else "",
		"raw_issue_date": str(cert.issue_date or ""),
		"expiry_date": format_date(cert.expiry_date, "dd MMMM yyyy") if cert.expiry_date else None,
		"template": cert.template or "Certificate",
		"verification_url": get_url(f"/certificate?certificate_id={quote(cert.name)}"),
		"pdf_url": f"/certificate?certificate_id={quote(cert.name)}&download=1",
	}
	context.title = f"Verified: {member_name} - {title}"
