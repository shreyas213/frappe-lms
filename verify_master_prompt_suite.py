#!/usr/bin/env python3
"""
Comprehensive Automated Verification Suite for Master Prompt:
- Automatic Certification System (Auto-issue on 100% progress, duplicate prevention, notification log, enrollment link)
- Public Certificate Verification Portal (Valid ID, invalid ID, empty portal, PDF redirect)
- Global Search API (Courses, Lessons, Batches, Instructors, Jobs, Certifications, Categories, Counts)
- Student Dashboard Data (Real MariaDB metrics, learning hours, profile completion, notifications, recommendations)
- Administrator Management Dashboard (Real-time counts, published vs draft courses, enrollments, completion rate, jobs)
- Profile Custom Fields & Editing (Phone, Resume, Headline, Bio, Profile Completion)
"""

import os
import sys
import unittest

BENCH_DIR = "/home/shrey/frappe/frappe-bench"
sys.path.insert(0, os.path.join(BENCH_DIR, "apps", "frappe"))
sys.path.insert(0, os.path.join(BENCH_DIR, "apps", "lms"))

if os.path.exists("sites/lms.local"):
    os.chdir("sites")
elif not os.path.exists("lms.local") and os.path.exists(os.path.join(BENCH_DIR, "sites")):
    os.chdir(os.path.join(BENCH_DIR, "sites"))

import frappe
from frappe.utils import nowdate, random_string


class TestMasterPromptSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        frappe.init("lms.local")
        frappe.connect()
        frappe.local.request_ip = "127.0.0.1"

        # Ensure test student user exists
        cls.student_email = "master_student@test.local"
        if not frappe.db.exists("User", cls.student_email):
            user = frappe.get_doc({
                "doctype": "User",
                "email": cls.student_email,
                "first_name": "Master",
                "last_name": "Student",
                "username": "master_student_" + random_string(5).lower(),
                "phone": "+1234567890",
                "headline": "Full-Stack Software Learner",
                "bio": "Passionate about building scalable systems.",
                "user_image": "/assets/lms/images/default-avatar.png",
            })
            user.flags.ignore_permissions = True
            user.insert(ignore_permissions=True)
            user.add_roles("LMS Student")
        else:
            frappe.db.set_value("User", cls.student_email, {
                "phone": "+1234567890",
                "headline": "Full-Stack Software Learner",
                "bio": "Passionate about building scalable systems.",
                "user_image": "/assets/lms/images/default-avatar.png",
            })
        cls.student_username = frappe.db.get_value("User", cls.student_email, "username")

        # Ensure Category exists
        if not frappe.db.exists("LMS Category", "Technology"):
            cat = frappe.get_doc({"doctype": "LMS Category", "category": "Technology"})
            cat.insert(ignore_permissions=True)

        # Create a dedicated test course
        cls.course_title = "Master Cert Architecture Course " + random_string(5)
        course = frappe.get_doc({
            "doctype": "LMS Course",
            "title": cls.course_title,
            "short_introduction": "Complete guide to automated certification and LMS systems.",
            "description": "Comprehensive master course covering verification, automation and system architecture.",
            "category": "Technology",
            "published": 1,
            "enable_certification": 1,
        })
        course.flags.ignore_permissions = True
        course.insert(ignore_permissions=True)
        cls.course_name = course.name

        # Create chapter and 2 lessons
        cls.chapter = frappe.get_doc({
            "doctype": "Course Chapter",
            "title": "Module 1 - Architecture",
            "course": cls.course_name,
            "idx": 1,
        })
        cls.chapter.flags.ignore_permissions = True
        cls.chapter.insert(ignore_permissions=True)

        cls.lesson1 = frappe.get_doc({
            "doctype": "Course Lesson",
            "title": "Lesson 1: Verification Protocols",
            "course": cls.course_name,
            "chapter": cls.chapter.name,
            "body": "<p>Verification protocols content.</p>",
            "duration": 1800, # 30 mins
            "idx": 1,
        })
        cls.lesson1.flags.ignore_permissions = True
        cls.lesson1.insert(ignore_permissions=True)

        cls.lesson2 = frappe.get_doc({
            "doctype": "Course Lesson",
            "title": "Lesson 2: Automated Issuance",
            "course": cls.course_name,
            "chapter": cls.chapter.name,
            "body": "<p>Automated issuance content.</p>",
            "duration": 3600, # 60 mins
            "idx": 2,
        })
        cls.lesson2.flags.ignore_permissions = True
        cls.lesson2.insert(ignore_permissions=True)

        # Link lessons into chapter child table and chapter into course child table
        cls.chapter.reload()
        cls.chapter.append("lessons", {"lesson": cls.lesson1.name})
        cls.chapter.append("lessons", {"lesson": cls.lesson2.name})
        cls.chapter.save(ignore_permissions=True)

        course.reload()
        course.append("chapters", {"chapter": cls.chapter.name})
        course.save(ignore_permissions=True)

        frappe.db.commit()

    @classmethod
    def tearDownClass(cls):
        frappe.set_user("Administrator")
        # Clean up created test documents
        for cert in frappe.get_all("LMS Certificate", filters={"course": cls.course_name}, pluck="name"):
            frappe.delete_doc("LMS Certificate", cert, force=True)

        for enr in frappe.get_all("LMS Enrollment", filters={"course": cls.course_name}, pluck="name"):
            frappe.delete_doc("LMS Enrollment", enr, force=True)

        for prog in frappe.get_all("LMS Course Progress", filters={"course": cls.course_name}, pluck="name"):
            frappe.delete_doc("LMS Course Progress", prog, force=True)

        for notif in frappe.get_all("Notification Log", filters={"for_user": cls.student_email}, pluck="name"):
            frappe.delete_doc("Notification Log", notif, force=True)

        frappe.delete_doc("Course Lesson", cls.lesson1.name, force=True)
        frappe.delete_doc("Course Lesson", cls.lesson2.name, force=True)
        frappe.delete_doc("Course Chapter", cls.chapter.name, force=True)
        frappe.delete_doc("LMS Course", cls.course_name, force=True)
        frappe.db.commit()

    def setUp(self):
        frappe.local.request_ip = "127.0.0.1"

    # ---------------------------------------------------------
    # TEST 1: Automatic Certification System
    # ---------------------------------------------------------
    def test_01_auto_issue_certificate_logic(self):
        from lms.lms.api import auto_issue_course_certificate

        frappe.set_user("Administrator")

        # Create enrollment with 50% progress
        enr = frappe.get_doc({
            "doctype": "LMS Enrollment",
            "course": self.course_name,
            "member": self.student_email,
            "progress": 50,
        })
        enr.insert(ignore_permissions=True)

        # Attempt to auto issue certificate with < 100% progress -> should return None
        res_incomplete = auto_issue_course_certificate(self.course_name, self.student_email)
        self.assertIsNone(res_incomplete, "Should not issue certificate when progress < 100%")

        # Update enrollment progress to 100%
        frappe.db.set_value("LMS Enrollment", enr.name, "progress", 100)

        # Issue certificate
        cert_data = auto_issue_course_certificate(self.course_name, self.student_email)
        self.assertIsNotNone(cert_data, "Certificate should be issued when progress = 100%")
        self.assertTrue(cert_data.get("name"), "Certificate name must be returned")
        cert_id = cert_data["name"]

        # Verify LMS Certificate record in MariaDB
        cert_doc = frappe.get_doc("LMS Certificate", cert_id)
        self.assertEqual(cert_doc.member, self.student_email)
        self.assertEqual(cert_doc.course, self.course_name)
        self.assertEqual(cert_doc.published, 1, "Certificate must be published=1 for public verification")
        self.assertEqual(str(cert_doc.issue_date), nowdate())

        # Verify LMS Enrollment was updated with certificate link
        updated_enr_cert = frappe.db.get_value("LMS Enrollment", enr.name, "certificate")
        self.assertEqual(updated_enr_cert, cert_id, "Enrollment must be linked to issued certificate")

        # Verify Notification Log was created for student
        notifications = frappe.get_all(
            "Notification Log",
            filters={"for_user": self.student_email, "document_name": cert_id},
            fields=["name", "subject", "link"],
        )
        self.assertTrue(len(notifications) > 0, "Notification Log must be generated for student upon certification")
        self.assertIn("Certificate", notifications[0]["subject"])

        # Test duplicate prevention: calling auto_issue_course_certificate again must return the exact same certificate
        cert_data_dup = auto_issue_course_certificate(self.course_name, self.student_email)
        self.assertEqual(cert_data_dup["name"], cert_id, "Duplicate issuance must return existing certificate ID")

    # ---------------------------------------------------------
    # TEST 2: Course Progress Trigger for Auto-Certification
    # ---------------------------------------------------------
    def test_02_recalculate_course_progress_trigger(self):
        from lms.lms.utils import recalculate_course_progress

        frappe.set_user("Administrator")

        # Mark both lessons complete in LMS Course Progress
        for lsn in [self.lesson1.name, self.lesson2.name]:
            if not frappe.db.exists("LMS Course Progress", {"course": self.course_name, "lesson": lsn, "member": self.student_email}):
                p = frappe.get_doc({
                    "doctype": "LMS Course Progress",
                    "course": self.course_name,
                    "chapter": self.chapter.name,
                    "lesson": lsn,
                    "member": self.student_email,
                    "status": "Complete",
                })
                p.insert(ignore_permissions=True)
            else:
                frappe.db.set_value("LMS Course Progress", {"course": self.course_name, "lesson": lsn, "member": self.student_email}, "status", "Complete")

        # Recalculate course progress
        recalculate_course_progress(self.course_name, self.student_email)

        # Check enrollment progress is 100%
        progress = frappe.db.get_value("LMS Enrollment", {"course": self.course_name, "member": self.student_email}, "progress")
        self.assertEqual(progress, 100)

        # Check that a certificate exists and is linked
        cert = frappe.db.get_value("LMS Enrollment", {"course": self.course_name, "member": self.student_email}, "certificate")
        self.assertTrue(bool(cert), "recalculate_course_progress must auto-issue and link certificate on 100% completion")

    # ---------------------------------------------------------
    # TEST 3: Public Certificate Verification Portal
    # ---------------------------------------------------------
    def test_03_public_verification_portal(self):
        from apps.lms.lms.www import certificate as cert_portal

        cert_id = frappe.db.get_value("LMS Certificate", {"course": self.course_name, "member": self.student_email}, "name")
        self.assertTrue(bool(cert_id))

        # Case A: Valid Certificate ID
        frappe.form_dict = {"certificate_id": cert_id}
        ctx_valid = frappe._dict()
        cert_portal.get_context(ctx_valid)
        self.assertTrue(ctx_valid.is_valid, "Valid certificate must set is_valid=True")
        self.assertFalse(ctx_valid.not_found)
        self.assertEqual(ctx_valid.certificate["id"], cert_id)
        self.assertIn("/certificate?certificate_id=", ctx_valid.certificate["verification_url"])
        self.assertIn("download=1", ctx_valid.certificate["pdf_url"])

        # Case B: Invalid Certificate ID
        frappe.form_dict = {"certificate_id": "INVALID_CERT_ID_9999"}
        ctx_invalid = frappe._dict()
        cert_portal.get_context(ctx_invalid)
        self.assertFalse(ctx_invalid.is_valid)
        self.assertTrue(ctx_invalid.not_found, "Invalid certificate must set not_found=True")

        # Case C: Empty Certificate ID (Landing Search Form)
        frappe.form_dict = {}
        ctx_empty = frappe._dict()
        cert_portal.get_context(ctx_empty)
        self.assertFalse(ctx_empty.is_valid)
        self.assertFalse(ctx_empty.not_found)

        # Case D: PDF Download flag redirect
        frappe.form_dict = {"certificate_id": cert_id, "download": "1"}
        ctx_download = frappe._dict()
        with self.assertRaises(frappe.Redirect):
            cert_portal.get_context(ctx_download)

        # Verify template HTML file exists and has official styling
        html_path = os.path.join(BENCH_DIR, "apps/lms/lms/www/certificate.html")
        self.assertTrue(os.path.exists(html_path))
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        self.assertIn("Certificate of Completion", html_content)
        self.assertIn("Authentic & Verified Credential", html_content)
        self.assertIn("Download Official PDF", html_content)
        self.assertIn("Print Certificate", html_content)

    # ---------------------------------------------------------
    # TEST 4: Global Search API
    # ---------------------------------------------------------
    def test_04_global_search_api(self):
        from lms.lms.api import global_search

        frappe.set_user("Administrator")

        # Search for course by keyword
        res = global_search(query="Architecture", category="All")
        self.assertIn("results", res)
        self.assertIn("counts", res)
        self.assertTrue(any(self.course_title in r["title"] for r in res["results"]),
                        "Course should be found by keyword in global search")

        # Search specific category: Courses
        res_courses = global_search(query="Architecture", category="Courses")
        self.assertTrue(all(r["type"] == "Courses" for r in res_courses["results"]))

        # Search lessons by keyword
        res_lessons = global_search(query="Verification Protocols", category="Lessons")
        self.assertTrue(any("Verification Protocols" in r["title"] for r in res_lessons["results"]),
                        "Lesson should be found in lesson category search")

        # Search certifications by keyword
        res_certs = global_search(query=self.course_name, category="Certificates")
        self.assertIn("counts", res_certs)

        # Empty search handling
        res_empty = global_search(query="")
        self.assertEqual(len(res_empty["results"]), 0)
        self.assertEqual(res_empty["counts"]["All"], 0)

    # ---------------------------------------------------------
    # TEST 5: Student Dashboard Real-time Metrics
    # ---------------------------------------------------------
    def test_05_student_dashboard_metrics(self):
        from lms.lms.api import get_student_dashboard_data

        frappe.set_user(self.student_email)
        dash = get_student_dashboard_data()

        self.assertIsNotNone(dash)
        self.assertIn("stats", dash)
        self.assertIn("student_info", dash)
        self.assertIn("enrolled_courses", dash)
        self.assertIn("certificates", dash)
        self.assertIn("recent_notifications", dash)
        self.assertIn("recommended_courses", dash)

        # Check calculated fields
        stats = dash["stats"]
        self.assertTrue(stats["total_enrolled"] >= 1)
        self.assertTrue(stats["completed"] >= 1)
        self.assertIn("learning_hours", stats)
        self.assertGreater(stats["learning_hours"], 0, "Learning hours must reflect completed lesson durations")

        self.assertIn("profile_completion", stats)
        self.assertGreaterEqual(stats["profile_completion"], 50, "Profile completion must be calculated from filled fields")

        # Check certificates returned for student
        certs = dash["certificates"]
        self.assertTrue(any(c["course"] == self.course_name for c in certs))

    # ---------------------------------------------------------
    # TEST 6: Administrator Dashboard Metrics API
    # ---------------------------------------------------------
    def test_06_admin_dashboard_metrics(self):
        from lms.lms.api import get_admin_dashboard_metrics

        # Admin access
        frappe.set_user("Administrator")
        admin_data = get_admin_dashboard_metrics()

        self.assertIsNotNone(admin_data)
        self.assertIn("total_students", admin_data)
        self.assertIn("total_courses", admin_data)
        self.assertIn("published_courses", admin_data)
        self.assertIn("draft_courses", admin_data)
        self.assertIn("total_enrollments", admin_data)
        self.assertIn("completion_rate", admin_data)
        self.assertIn("certificates_issued", admin_data)
        self.assertIn("recent_enrollments", admin_data)
        self.assertIn("recent_certificates", admin_data)

        self.assertTrue(admin_data["total_courses"] >= admin_data["published_courses"])
        self.assertTrue(admin_data["total_enrollments"] >= 1)

        # Student access should be rejected with PermissionError
        frappe.set_user(self.student_email)
        with self.assertRaises(frappe.PermissionError):
            get_admin_dashboard_metrics()

    # ---------------------------------------------------------
    # TEST 7: Student Profile Custom Fields & Editing
    # ---------------------------------------------------------
    def test_07_profile_fields_and_persistence(self):
        from lms.lms.api import get_profile_details

        frappe.set_user(self.student_email)

        # Update profile fields via client API
        updated_phone = "+19876543210"
        updated_headline = "Senior LMS System Architect & Engineer"

        frappe.client.set_value(
            doctype="User",
            name=self.student_email,
            fieldname={
                "phone": updated_phone,
                "headline": updated_headline,
            }
        )

        # Read back via get_profile_details
        details = get_profile_details(self.student_username)
        self.assertEqual(details.phone, updated_phone)
        self.assertEqual(details.headline, updated_headline)
        self.assertIn("profile_completion", details)
        self.assertGreater(details.profile_completion, 0)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMasterPromptSuite)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(not result.wasSuccessful())
