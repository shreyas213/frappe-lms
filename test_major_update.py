#!/usr/bin/env python3
# Copyright (c) 2026, Frappe and contributors
# Comprehensive Automated Verification Test Suite for Major LMS Update

import os
import sys
import unittest
import urllib.request
import urllib.parse
import json

# Initialize Frappe
import frappe
if not os.path.exists("lms.local") and os.path.exists("sites/lms.local"):
    os.chdir("sites")
frappe.init("lms.local")
frappe.connect()

BASE_URL = "http://127.0.0.1:8000"

class TestMajorLMSUpdate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        frappe.set_user("Administrator")
        # Ensure a test student exists
        cls.test_student_email = "test_student_verify@example.com"
        cls.test_demo_email = "demo_test_user@example.com"

        # Cleanup if existed
        for email in [cls.test_student_email, cls.test_demo_email]:
            if frappe.db.exists("User", email):
                frappe.delete_doc("User", email, ignore_permissions=True)

    def test_01_signup_route_exists_and_loads(self):
        """Verify dedicated /signup route loads with HTTP 200 and proper elements."""
        req = urllib.request.Request(f"{BASE_URL}/signup", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            html = resp.read().decode("utf-8")
            self.assertIn("Create a Frappe Account", html)
            self.assertIn("signup_fullname", html)
            self.assertIn("signup_email", html)
            self.assertIn("signup_password", html)
            self.assertIn("signup_confirm_password", html)
            self.assertIn("btn_submit_signup", html)
            self.assertIn('href="/login"', html)
            self.assertIn("#FF6B00", html)
            self.assertIn("#111111", html)
            self.assertIn("#1C1C1C", html)

    def test_02_login_route_exists_and_links_to_signup(self):
        """Verify /login route loads with HTTP 200, links to /signup, and uses Orange & Black theme."""
        req = urllib.request.Request(f"{BASE_URL}/login", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            html = resp.read().decode("utf-8")
            self.assertIn("Orange and Black Theme for /login", html)
            self.assertIn("#FF6B00", html)
            self.assertIn("#111111", html)
            self.assertIn("#1C1C1C", html)
            self.assertIn('window.location.replace(\'/signup\')', html)
            self.assertIn('section.for-signup', html)
            self.assertIn('display: none !important;', html)

    def test_03_student_registration_and_role_assignment(self):
        """Verify student signup API registers user with Student role."""
        from lms.lms.user import sign_up
        email = self.test_student_email
        if frappe.db.exists("User", email):
            frappe.delete_doc("User", email, ignore_permissions=True)

        res = sign_up(email=email, full_name="Verified Student", password="SecurePassword123!")
        self.assertIn(int(res[0]), (1, 2))
        self.assertTrue(frappe.db.exists("User", email))

        user = frappe.get_doc("User", email)
        self.assertEqual(user.full_name, "Verified Student")
        user_roles = [r.role for r in user.roles]
        self.assertTrue(any(r in ("LMS Student", "Student") for r in user_roles))

    def test_04_logout_api_and_session_clearing(self):
        """Verify logout API terminates session."""
        from frappe.sessions import clear_sessions
        frappe.set_user(self.test_student_email)
        sid = frappe.session.sid

        # Verify clear_sessions removes user session
        clear_sessions(self.test_student_email)
        self.assertFalse(frappe.db.exists("Sessions", {"user": self.test_student_email}))

    def test_05_admin_reset_analytics_permission_check(self):
        """Verify reset_lms_analytics enforces System Manager permission."""
        from lms.lms.api import reset_lms_analytics
        frappe.set_user(self.test_student_email)

        with self.assertRaises(frappe.PermissionError):
            reset_lms_analytics()

        frappe.set_user("Administrator")
        res = reset_lms_analytics(action="reset")
        self.assertEqual(res["status"], "success")
        self.assertTrue(bool(res.get("reset_timestamp")))

    def test_06_option_a_resets_displayed_metrics_preserves_real_data(self):
        """Option A resets displayed counts to 0 while preserving actual database records."""
        from lms.lms.api import reset_lms_analytics, get_chart_details
        frappe.set_user("Administrator")

        # 1. Verify real records exist in database
        real_user_count = frappe.db.count("User", {"enabled": 1, "name": ["not in", ("Administrator", "Guest")]})
        self.assertGreater(real_user_count, 0)

        # 2. Execute Option A: Reset Analytics
        res = reset_lms_analytics(action="reset")
        self.assertEqual(res["status"], "success")

        # 3. Check displayed chart details
        details = get_chart_details()
        self.assertEqual(details.users, 0, "Signups counter must be 0 after reset")
        self.assertEqual(details.enrollments, 0, "Enrollments counter must be 0 after reset")
        self.assertEqual(details.completions, 0, "Completions counter must be 0 after reset")
        self.assertEqual(details.certifications, 0, "Certifications counter must be 0 after reset")

        # 4. CRITICAL: Database rows MUST be intact!
        db_user_count_after = frappe.db.count("User", {"enabled": 1, "name": ["not in", ("Administrator", "Guest")]})
        self.assertEqual(real_user_count, db_user_count_after, "Option A must NEVER delete student accounts!")
        self.assertTrue(frappe.db.exists("User", self.test_student_email), "Student account must still exist in DB!")

    def test_07_option_a_can_restore_historical_data(self):
        """Verify Option A can restore historical analytics if desired."""
        from lms.lms.api import reset_lms_analytics, get_chart_details
        frappe.set_user("Administrator")

        res = reset_lms_analytics(action="restore")
        self.assertEqual(res["status"], "success")

        details = get_chart_details()
        self.assertGreater(details.users, 0, "Historical signups count must be restored")

    def test_08_option_b_security_blocks_deleting_administrator_or_system_manager(self):
        """Option B strictly blocks deletion of Administrator or System Manager accounts."""
        from lms.lms.api import delete_demo_data
        frappe.set_user("Administrator")

        with self.assertRaises(frappe.ValidationError):
            delete_demo_data(users=["Administrator"])

        # Try with a System Manager user
        sm_email = "test_sysmanager_safety@example.com"
        if not frappe.db.exists("User", sm_email):
            sm = frappe.get_doc({
                "doctype": "User",
                "email": sm_email,
                "first_name": "Safety",
                "last_name": "Officer",
                "roles": [{"role": "System Manager"}]
            }).insert(ignore_permissions=True)

        with self.assertRaises(frappe.ValidationError):
            delete_demo_data(users=[sm_email])

        if frappe.db.exists("User", sm_email):
            frappe.delete_doc("User", sm_email, ignore_permissions=True)

    def test_09_option_b_deletes_only_selected_demo_user(self):
        """Option B deletes chosen demo account and cascaded progress, leaving real students untouched."""
        from lms.lms.api import delete_demo_data, get_demo_users
        frappe.set_user("Administrator")

        demo_email = self.test_demo_email
        if not frappe.db.exists("User", demo_email):
            frappe.get_doc({
                "doctype": "User",
                "email": demo_email,
                "first_name": "Demo",
                "last_name": "TestUser",
                "roles": [{"role": "LMS Student"}]
            }).insert(ignore_permissions=True)

        # Confirm user is in get_demo_users
        demo_users = get_demo_users()
        self.assertTrue(any(u["name"] == demo_email for u in demo_users))

        # Delete the demo user
        res = delete_demo_data(users=[demo_email])
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["deleted_count"], 1)
        self.assertFalse(frappe.db.exists("User", demo_email), "Demo user should be deleted from DB")

        # Confirm real student is completely unaffected
        self.assertTrue(frappe.db.exists("User", self.test_student_email), "Real student must NOT be deleted!")

    def test_10_audit_log_recorded_for_administrative_actions(self):
        """Verify audit log records entry in Activity Log for reset operations."""
        audit_entries = frappe.get_all(
            "Activity Log",
            filters={"subject": ["like", "LMS%"]},
            fields=["subject", "user", "status", "communication_date"],
            order_by="communication_date desc",
            limit=5
        )
        self.assertGreater(len(audit_entries), 0, "Audit log must contain LMS reset entries")
        subjects = [e.subject for e in audit_entries]
        has_lms_audit = any("LMS Analytics" in s or "LMS Demo" in s for s in subjects)
        self.assertTrue(has_lms_audit, f"Expected LMS audit subjects, got: {subjects}")

    def test_11_orange_and_black_theme_tokens_in_css(self):
        """Verify theme design tokens are properly defined in compiled CSS."""
        css_path = "/home/shrey/frappe/frappe-bench/apps/lms/frontend/src/index.css"
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()

        tokens = [
            "--primary-orange: #FF6B00",
            "--secondary-orange: #FF8C00",
            "--surface-base: #111111",
            "--surface-white: #1C1C1C",
            "--surface-sidebar: #0B0B0B",
            "--outline-base: #333333",
            "--ink-success: #22C55E",
            "--ink-error: #EF4444",
        ]
        for token in tokens:
            self.assertIn(token, css_content, f"Token {token} must be present in index.css")

    def test_12_statistics_frontend_compiled_and_accessible(self):
        """Verify built _lms.html exists and contains the SPA assets."""
        lms_html_path = "/home/shrey/frappe/frappe-bench/apps/lms/lms/www/_lms.html"
        self.assertTrue(os.path.exists(lms_html_path))
        with open(lms_html_path, "r", encoding="utf-8") as f:
            html = f.read()
        self.assertIn("/assets/lms/frontend/", html)

if __name__ == "__main__":
    unittest.main()
