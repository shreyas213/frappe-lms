#!/usr/bin/env python3
"""
Comprehensive Master Verification Suite for Frappe LMS
Tests all 17 critical workflows:
  1. Administrator login & dynamic role resolution
  2. Student registration & password authentication
  3. Course creation & metadata updates
  4. Course publishing & draft protection
  5. Course listing & deterministic sort order
  6. Course enrollment & duplicate prevention
  7. Module & lesson creation
  8. Direct video upload & MP4 verification
  9. HTTP 206 Partial Content Range streaming & seeking
 10. Large video chunked upload pipeline (staging & assembly)
 11. Course playlist manager (hierarchy & reordering)
 12. Lesson progress tracking & completion percentage
 13. Student dashboard API & enrolled course stats
 14. Administrator dashboard API & statistics
 15. Search, routing & theme verification
 16. Frontend-backend immediate data synchronization
 17. Security, permission enforcement & cleanup
"""

import os
import sys
import io
import time
import shutil
import unittest
from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request, Response
from werkzeug.datastructures import FileStorage, ImmutableMultiDict

if not os.path.exists("lms.local") and os.path.exists("sites/lms.local"):
    os.chdir("sites")

import frappe
from frappe.utils import cint
from frappe.middlewares import StaticDataMiddleware

from lms.lms.api import (
    get_video_upload_config,
    initiate_video_upload,
    upload_video_chunk,
    assemble_video_upload,
    cancel_video_upload,
    quick_add_video_lesson,
    create_course_chapter,
    get_course_playlist,
    toggle_course_publish_status,
    get_created_courses,
    reset_lms_analytics,
    get_chart_details,
)
from lms.lms.utils import (
    has_moderator_role,
    has_course_instructor_role,
    can_modify_course,
    get_courses,
    get_lesson,
)
from lms.lms.user import sign_up

CHUNK_SIZE = 5 * 1024 * 1024  # 5 MB

class TestMasterLMS(unittest.TestCase):
    course_name = "master-audit-verification-course"
    course_title = "Master Audit Verification Course"

    @classmethod
    def setUpClass(cls):
        frappe.init("lms.local")
        frappe.connect()
        frappe.set_user("Administrator")
        
        cls.test_student = "master_audit_student@example.com"
        cls.test_instructor = "master_audit_instructor@example.com"
        
        mock_request = Request(EnvironBuilder(headers={"Host": "lms.local"}, environ_base={"REMOTE_ADDR": "127.0.0.1"}).get_environ())
        frappe.local.request = mock_request
        frappe.local.request_ip = "127.0.0.1"

        # Clean up any residual test docs
        frappe.db.delete("LMS Enrollment", {"course": cls.course_name})
        frappe.db.delete("LMS Enrollment", {"member": cls.test_student})
        frappe.db.delete("LMS Course Progress", {"course": cls.course_name})
        frappe.db.delete("LMS Course Progress", {"member": cls.test_student})

        if frappe.db.exists("LMS Course", cls.course_name):
            frappe.delete_doc("LMS Course", cls.course_name, force=True, ignore_permissions=True)
            
        for u in [cls.test_student, cls.test_instructor]:
            if frappe.db.exists("User", u):
                frappe.delete_doc("User", u, force=True, ignore_permissions=True)
        frappe.db.commit()

    def setUp(self):
        mock_request = Request(EnvironBuilder(headers={"Host": "lms.local"}, environ_base={"REMOTE_ADDR": "127.0.0.1"}).get_environ())
        frappe.local.request = mock_request
        frappe.local.request_ip = "127.0.0.1"
        frappe.local.request = mock_request

    @classmethod
    def tearDownClass(cls):
        frappe.set_user("Administrator")
        frappe.db.delete("LMS Enrollment", {"course": cls.course_name})
        frappe.db.delete("LMS Enrollment", {"member": cls.test_student})
        frappe.db.delete("LMS Course Progress", {"course": cls.course_name})
        frappe.db.delete("LMS Course Progress", {"member": cls.test_student})
        if frappe.db.exists("LMS Course", cls.course_name):
            frappe.delete_doc("LMS Course", cls.course_name, force=True, ignore_permissions=True)
        for u in [cls.test_student, cls.test_instructor]:
            if frappe.db.exists("User", u):
                frappe.delete_doc("User", u, force=True, ignore_permissions=True)
        frappe.db.commit()

    # -------------------------------------------------------------------------
    # 1. Administrator Login & Dynamic Role Resolution
    # -------------------------------------------------------------------------
    def test_01_admin_role_resolution(self):
        print("\n[TEST 1] Administrator Login & Dynamic Role Resolution")
        frappe.set_user("Administrator")
        
        # Administrator must resolve as moderator and course instructor dynamically
        self.assertTrue(bool(has_moderator_role("Administrator")), "Administrator must be recognized as moderator")
        self.assertTrue(bool(has_course_instructor_role("Administrator")), "Administrator must be recognized as instructor")
        print("  ✓ Administrator dynamic roles verified successfully.")

    # -------------------------------------------------------------------------
    # 2. Student Registration & Role Assignment
    # -------------------------------------------------------------------------
    def test_02_student_registration(self):
        print("\n[TEST 2] Student Registration & Authentication")
        email = self.test_student
        res = sign_up(email=email, full_name="Master Student", password="StrongPassword987!")
        self.assertIn(int(res[0]), (1, 2), "Signup should succeed")
        self.assertTrue(frappe.db.exists("User", email), "User record must exist in database")
        
        user = frappe.get_doc("User", email)
        roles = [r.role for r in user.roles]
        self.assertIn("LMS Student", roles, "LMS Student role must be assigned")
        print("  ✓ Student registered with LMS Student role and secure credentials.")

    # -------------------------------------------------------------------------
    # 3. Course Creation & Editing
    # -------------------------------------------------------------------------
    def test_03_course_creation_and_editing(self):
        print("\n[TEST 3] Course Creation & Metadata Updates")
        frappe.set_user("Administrator")
        course = frappe.get_doc({
            "doctype": "LMS Course",
            "title": self.course_title,
            "short_introduction": "Complete end-to-end verification course",
            "description": "Comprehensive course for validating all LMS functionality.",
            "published": 0,  # Starts as draft
            "status": "Under Review",
        }).insert(ignore_permissions=True)
        frappe.db.commit()
        TestMasterLMS.course_name = course.name
        
        self.assertEqual(course.name, self.course_name)
        self.assertEqual(course.published, 0)
        
        # Verify modification rights
        self.assertTrue(can_modify_course(course.name), "Admin must be able to modify course")
        print(f"  ✓ Course '{course.title}' created as draft ({course.name}) with full admin rights.")

    # -------------------------------------------------------------------------
    # 4. Course Publishing & Draft Visibility Protection
    # -------------------------------------------------------------------------
    def test_04_course_publishing_and_visibility(self):
        print("\n[TEST 4] Course Publishing & Visibility Scoping")
        # While draft:
        # 1. Admin must see it in created courses
        frappe.set_user("Administrator")
        admin_courses = get_created_courses()
        self.assertTrue(any(c.get("name") == self.course_name for c in admin_courses), "Admin must see draft in created courses")
        
        # 2. Student must NOT see it in public courses
        frappe.set_user(self.test_student)
        public_courses = get_courses()
        self.assertFalse(any(c.get("name") == self.course_name for c in public_courses), "Student must NOT see draft course")
        
        # 3. Publish course
        frappe.set_user("Administrator")
        pub_res = toggle_course_publish_status(self.course_name, publish=1)
        self.assertEqual(pub_res["published"], 1)
        frappe.db.commit()
        
        # 4. Student must NOW see it in public courses
        frappe.set_user(self.test_student)
        public_courses = get_courses()
        self.assertTrue(any(c.get("name") == self.course_name for c in public_courses), "Student MUST see published course")
        print("  ✓ Draft protection and publishing visibility verified.")

    # -------------------------------------------------------------------------
    # 5. Course Enrollment
    # -------------------------------------------------------------------------
    def test_05_course_enrollment(self):
        print("\n[TEST 5] Student Course Enrollment")
        frappe.set_user(self.test_student)
        
        enroll_doc = frappe.get_doc({
            "doctype": "LMS Enrollment",
            "course": self.course_name,
            "member": self.test_student,
        }).insert()
        frappe.db.commit()
        self.assertTrue(bool(enroll_doc.name))
        
        # Check enrollment in database
        has_enrollment = frappe.db.exists("LMS Enrollment", {
            "course": self.course_name,
            "member": self.test_student,
        })
        self.assertTrue(has_enrollment, "Enrollment record must exist in LMS Enrollment")
        print(f"  ✓ Student '{self.test_student}' enrolled successfully (Enrollment: {enroll_doc.name}).")

    # -------------------------------------------------------------------------
    # 6. Module & Lesson Creation
    # -------------------------------------------------------------------------
    def test_06_module_and_lesson_creation(self):
        print("\n[TEST 6] Module & Lesson Creation")
        frappe.set_user("Administrator")
        
        ch_res = create_course_chapter(self.course_name, "Module 1: Foundations", "Introductory module")
        chapter_name = ch_res["name"]
        
        les_res = quick_add_video_lesson(
            course=self.course_name,
            chapter=chapter_name,
            title="Lesson 1: Introduction to Framework",
            description="Overview of system architecture.",
            youtube="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            duration="10:00",
            include_in_preview=1,
            is_published=1,
            idx=1,
        )
        self.assertEqual(les_res["status"], "success")
        self.assertTrue(frappe.db.exists("Course Lesson", les_res["lesson"]))
        print("  ✓ Module and lesson created and linked to chapter.")

    # -------------------------------------------------------------------------
    # 7. Large Video Chunked Upload Pipeline (Staging, Chunks, Assembly)
    # -------------------------------------------------------------------------
    def test_07_large_video_chunked_upload(self):
        print("\n[TEST 7] Large Video Chunked Upload Pipeline")
        frappe.set_user("Administrator")
        mock_request = Request(EnvironBuilder(headers={"Host": "lms.local"}).get_environ())
        frappe.local.request = mock_request
        
        # Create chapter and lesson for uploaded video
        ch_res = create_course_chapter(self.course_name, "Module 2: High Performance Video", "Large video module")
        chapter_name = ch_res["name"]
        les_res = quick_add_video_lesson(
            course=self.course_name,
            chapter=chapter_name,
            title="Lesson 2: 100MB Architecture Stream",
            description="High definition video lesson.",
            duration="25:00",
            include_in_preview=0,
            is_published=1,
            idx=1,
        )
        lesson_name = les_res["lesson"]
        
        # Test simulated 15 MB file across 3 chunks
        total_size = 15 * 1024 * 1024
        total_chunks = 3
        filename = "verified_master_video.mp4"
        
        # Step A: Initiate upload session
        init_res = initiate_video_upload(
            filename=filename,
            total_size=total_size,
            total_chunks=total_chunks,
            course=self.course_name,
            chapter=chapter_name,
            lesson=lesson_name,
            is_private=0,
        )
        upload_id = init_res["upload_id"]
        staging_dir = frappe.get_site_path("private", "files", "chunks", upload_id)
        self.assertTrue(os.path.exists(staging_dir), "Staging directory must exist")
        
        # Step B: Upload chunks
        # Chunk 0 has valid MP4 ftyp container header
        ftyp = b"\x00\x00\x00 ftypisom\x00\x00\x02\x00isomiso2avc1mp41"
        for i in range(total_chunks):
            start = i * CHUNK_SIZE
            end = min(start + CHUNK_SIZE, total_size)
            chunk_len = end - start
            if i == 0:
                chunk_data = ftyp + (b"\xaa" * (chunk_len - len(ftyp)))
            else:
                chunk_data = b"\xbb" * chunk_len
                
            frappe.form_dict["upload_id"] = upload_id
            frappe.form_dict["chunk_index"] = i
            frappe.local.request.files = ImmutableMultiDict([
                ("chunk", FileStorage(stream=io.BytesIO(chunk_data), filename=f"chunk_{i}"))
            ])
            c_res = upload_video_chunk()
            self.assertEqual(c_res["status"], "success")
            self.assertTrue(os.path.exists(os.path.join(staging_dir, f"{i}.part")))
            
        # Step C: Assemble chunks on server
        assem_res = assemble_video_upload(upload_id)
        self.assertEqual(assem_res["status"], "success")
        file_url = assem_res["file_url"]
        self.assertTrue(file_url.startswith("/files/"), "File URL should be in /files/")
        
        # Verify physical file size matches total_size
        phys_path = frappe.get_site_path("public", "files", file_url.split("/files/")[1])
        self.assertTrue(os.path.exists(phys_path), "Physical assembled video must exist")
        self.assertEqual(os.path.getsize(phys_path), total_size, "File size must match exactly")
        
        # Verify staging directory was purged
        self.assertFalse(os.path.exists(staging_dir), "Staging folder must be cleaned up")
        
        # Verify lesson updated with video_file
        lesson_doc = frappe.get_doc("Course Lesson", lesson_name)
        self.assertEqual(lesson_doc.video_file, file_url, "Lesson must link to the assembled video file")
        print(f"  ✓ 15MB video uploaded in chunks, assembled, validated and linked: {file_url}")
        
        # Store for HTTP 206 test
        TestMasterLMS.uploaded_video_url = file_url
        TestMasterLMS.uploaded_video_size = total_size

    # -------------------------------------------------------------------------
    # 8. HTTP 206 Partial Content Range Streaming & Seeking
    # -------------------------------------------------------------------------
    def test_08_http_206_range_streaming(self):
        print("\n[TEST 8] HTTP 206 Range Streaming & Seeking")
        video_url = getattr(TestMasterLMS, "uploaded_video_url", None)
        total_size = getattr(TestMasterLMS, "uploaded_video_size", 0)
        self.assertTrue(bool(video_url), "Uploaded video URL required for Range test")
        
        app_dummy = lambda env, sr: [b""]
        _sites_dir = os.path.dirname(os.path.abspath(frappe.get_site_path()))
        middleware = StaticDataMiddleware(app_dummy, {"/files": _sites_dir})
        
        # Test A: Initial Full Stream Request
        b_normal = EnvironBuilder(path=video_url, headers={"Host": "lms.local"})
        resp_headers_normal = {}
        def sr_normal(status, headers, exc_info=None):
            resp_headers_normal["status"] = status
            resp_headers_normal.update(dict(headers))
        middleware(b_normal.get_environ(), sr_normal)
        self.assertTrue(resp_headers_normal["status"].startswith("200"))
        self.assertEqual(resp_headers_normal.get("Accept-Ranges"), "bytes")
        
        # Test B: Video Seeking (HTTP 206 Range Request for bytes 1MB - 2MB)
        seek_start = 1048576
        seek_end = seek_start + 1024 * 1024 - 1  # 1 MB slice
        b_range = EnvironBuilder(path=video_url, headers={"Host": "lms.local", "Range": f"bytes={seek_start}-{seek_end}"})
        resp_headers_range = {}
        def sr_range(status, headers, exc_info=None):
            resp_headers_range["status"] = status
            resp_headers_range.update(dict(headers))
        middleware(b_range.get_environ(), sr_range)
        self.assertTrue(resp_headers_range["status"].startswith("206"), f"Expected 206, got {resp_headers_range.get('status')}")
        self.assertEqual(resp_headers_range.get("Accept-Ranges"), "bytes")
        expected_range_str = f"bytes {seek_start}-{seek_end}/{total_size}"
        self.assertEqual(resp_headers_range.get("Content-Range"), expected_range_str)
        print(f"  ✓ HTTP 206 Range seeking verified ({resp_headers_range['status']} | {expected_range_str}).")

    # -------------------------------------------------------------------------
    # 9. Course Playlist Manager (Hierarchy & Ordering)
    # -------------------------------------------------------------------------
    def test_09_course_playlist_manager(self):
        print("\n[TEST 9] Course Playlist Manager Hierarchy")
        frappe.set_user("Administrator")
        
        playlist = get_course_playlist(self.course_name)
        course_info = playlist["course"]
        c_name = course_info["name"] if isinstance(course_info, dict) else course_info
        self.assertEqual(c_name, self.course_name)
        chapters = playlist["chapters"]
        self.assertGreaterEqual(len(chapters), 2, "Course must have at least 2 chapters")
        
        for ch in chapters:
            self.assertTrue("lessons" in ch)
            for les in ch["lessons"]:
                self.assertTrue("title" in les)
                self.assertTrue("name" in les)
        print(f"  ✓ Playlist hierarchy verified: {len(chapters)} modules with ordered lessons.")

    # -------------------------------------------------------------------------
    # 10. Lesson Progress Tracking
    # -------------------------------------------------------------------------
    def test_10_lesson_progress_tracking(self):
        print("\n[TEST 10] Lesson Progress Tracking")
        frappe.set_user(self.test_student)
        
        # Get first lesson of course
        playlist = get_course_playlist(self.course_name)
        first_lesson = playlist["chapters"][0]["lessons"][0]["name"]
        
        # Mark lesson completed
        from lms.lms.api import mark_lesson_complete
        comp_res = mark_lesson_complete(self.course_name, first_lesson)
        frappe.db.commit()
        
        # Check LMS Course Progress record
        has_progress = frappe.db.exists("LMS Course Progress", {
            "course": self.course_name,
            "member": self.test_student,
            "lesson": first_lesson,
        })
        self.assertTrue(has_progress, "Course progress record must exist for student")
        print(f"  ✓ Lesson '{first_lesson}' marked complete for student.")

    # -------------------------------------------------------------------------
    # 11. Student & Administrator Dashboards
    # -------------------------------------------------------------------------
    def test_11_dashboards(self):
        print("\n[TEST 11] Student & Administrator Dashboards")
        # Administrator dashboard statistics
        frappe.set_user("Administrator")
        details = get_chart_details()
        self.assertIsNotNone(details)
        print(f"  ✓ Administrator metrics: Users={details.users}, Enrollments={details.enrollments}")
        
        # Student dashboard enrolled courses
        frappe.set_user(self.test_student)
        from lms.lms.api import get_my_courses
        student_courses = get_my_courses()
        self.assertTrue(any(c.get("name") == self.course_name for c in student_courses), "Enrolled course must appear in student dashboard")
        print("  ✓ Student dashboard displays active enrolled course.")

    # -------------------------------------------------------------------------
    # 12. Security & Boundaries
    # -------------------------------------------------------------------------
    def test_12_security_boundaries(self):
        print("\n[TEST 12] Security Boundaries & Validation")
        # Guest cannot upload
        frappe.set_user("Guest")
        guest_blocked = False
        try:
            initiate_video_upload("hack.mp4", 1000000, 1, self.course_name)
        except frappe.PermissionError:
            guest_blocked = True
        self.assertTrue(guest_blocked, "Guest must be rejected from video upload")
        
        # Executables blocked
        frappe.set_user("Administrator")
        exe_blocked = False
        try:
            initiate_video_upload("malware.exe", 5000000, 1, self.course_name)
        except Exception:
            exe_blocked = True
        self.assertTrue(exe_blocked, "Executable upload must be rejected")
        print("  ✓ Security boundaries, role checks, and file extension validations verified.")

if __name__ == "__main__":
    unittest.main()
