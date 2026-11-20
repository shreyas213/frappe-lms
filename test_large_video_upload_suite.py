import os
import io
import time
import shutil
import frappe
from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request
from werkzeug.datastructures import FileStorage, ImmutableMultiDict
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
)
from lms.lms.utils import get_lesson

CHUNK_SIZE = 5 * 1024 * 1024 # 5 MB

def run_tests():
    if not os.path.exists("lms.local") and os.path.exists("sites/lms.local"):
        os.chdir("sites")
    frappe.init("lms.local")
    frappe.connect()

    print("=" * 80)
    print("STARTING LARGE VIDEO UPLOAD AND STREAMING VERIFICATION SUITE")
    print("=" * 80)

    course_name = "test-video-playlist-course"
    frappe.set_user("Administrator")

    # Ensure test course exists
    if not frappe.db.exists("LMS Course", course_name):
        course = frappe.get_doc({
            "doctype": "LMS Course",
            "title": "Large Video Test Course",
            "name": course_name,
            "published": 1,
        }).insert(ignore_permissions=True)
        print("Created test course:", course.name)
    else:
        print("Using existing test course:", course_name)

    # ------------------------------------------------------------------------
    # TEST 1: Configurable Limits
    # ------------------------------------------------------------------------
    print("\n--- TEST 1: Configurable Limits Verification ---")
    config = get_video_upload_config()
    print("Active upload config:", config)
    assert config["max_size_mb"] >= 2048, f"Expected at least 2048 MB, got {config['max_size_mb']}"
    assert config["chunk_size_bytes"] == CHUNK_SIZE
    print("✓ Test 1 Passed: Limits configurable and verified at", config["max_size_mb"], "MB")

    # ------------------------------------------------------------------------
    # TEST 2: Security & Permissions
    # ------------------------------------------------------------------------
    print("\n--- TEST 2: Security & Permissions Verification ---")
    frappe.set_user("Guest")
    guest_failed = False
    try:
        initiate_video_upload("hack.mp4", 1000000, 1, course_name)
    except frappe.PermissionError:
        guest_failed = True
    assert guest_failed, "Guest upload must be rejected"
    print("✓ Guest access properly blocked with PermissionError")

    # Create / verify a test student user without instructor/admin role
    test_student = "student_tester@example.com"
    if not frappe.db.exists("User", test_student):
        frappe.get_doc({
            "doctype": "User",
            "email": test_student,
            "first_name": "Student",
            "last_name": "Tester",
            "enabled": 1,
            "roles": [{"role": "All"}],
        }).insert(ignore_permissions=True)

    frappe.set_user(test_student)
    student_failed = False
    try:
        initiate_video_upload("unauthorized.mp4", 1000000, 1, course_name)
    except frappe.PermissionError:
        student_failed = True
    assert student_failed, "Non-instructor student upload must be rejected"
    print("✓ Unauthorized user blocked with PermissionError")

    # Administrator switch
    frappe.set_user("Administrator")
    print("✓ Test 2 Passed: Role-based upload security verified")

    # ------------------------------------------------------------------------
    # TEST 3: Validation (Invalid format, file size, malicious container)
    # ------------------------------------------------------------------------
    print("\n--- TEST 3: Format & Container Validation ---")
    # Unsupported extension
    exe_blocked = False
    try:
        initiate_video_upload("malicious.exe", 5000000, 1, course_name)
    except Exception as e:
        exe_blocked = True
        print("✓ Executable blocked:", str(e))
    assert exe_blocked, "Executable upload must be rejected"

    # Exceeding configured maximum size
    oversize_blocked = False
    try:
        initiate_video_upload("too_big.mp4", 3000 * 1024 * 1024, 600, course_name) # 3000 MB
    except Exception as e:
        oversize_blocked = True
        print("✓ Oversized file blocked:", str(e))
    assert oversize_blocked, "Oversized upload must be rejected"

    print("✓ Test 3 Passed: Extension and size boundaries verified")

    # ------------------------------------------------------------------------
    # TEST 4: Interrupted Upload & Cancellation Cleanup
    # ------------------------------------------------------------------------
    print("\n--- TEST 4: Interrupted Upload & Staging Cleanup ---")
    mock_request = Request(EnvironBuilder(headers={"Host": "lms.local"}).get_environ())
    frappe.local.request = mock_request

    interrupted_init = initiate_video_upload(
        "interrupted_test.mp4",
        15 * 1024 * 1024, # 15 MB
        3,
        course_name,
        is_private=0
    )
    i_upload_id = interrupted_init["upload_id"]
    staging_path = frappe.get_site_path("private", "files", "chunks", i_upload_id)
    assert os.path.exists(staging_path)

    # Upload chunk 0
    frappe.form_dict["upload_id"] = i_upload_id
    frappe.form_dict["chunk_index"] = 0
    c0_bytes = b"\x00\x00\x00 ftypisom\x00\x00\x02\x00isomiso2avc1mp41" + b"A" * (5 * 1024 * 1024 - 32)
    frappe.local.request.files = ImmutableMultiDict([("chunk", FileStorage(stream=io.BytesIO(c0_bytes), filename="chunk_0"))])
    upload_video_chunk()
    assert os.path.exists(os.path.join(staging_path, "0.part"))

    # User cancels upload
    cancel_res = cancel_video_upload(i_upload_id)
    print("Cancellation result:", cancel_res)
    assert not os.path.exists(staging_path), "Staging chunk folder must be completely purged upon cancellation"
    print("✓ Staging chunks purged cleanly upon cancellation")
    print("✓ Test 4 Passed: Upload cancellation & cleanup verified")

    # ------------------------------------------------------------------------
    # Helper to run complete upload & verify student playback/seeking
    # ------------------------------------------------------------------------
    def execute_video_test(target_size_bytes, label, chapter_title, lesson_title):
        print(f"\n" + "=" * 50)
        print(f"RUNNING TEST: {label} ({target_size_bytes / (1024 * 1024):.1f} MB)")
        print(f"=" * 50)

        # 1. Create chapter
        ch_res = create_course_chapter(course_name, chapter_title, f"Module for {label}")
        chapter_name = ch_res["name"]
        print(f"1. Created module: {chapter_title} ({chapter_name})")

        # 2. Pre-create lesson
        les_res = quick_add_video_lesson(
            course=course_name,
            chapter=chapter_name,
            title=lesson_title,
            description=f"Lesson containing {label} video.",
            duration="15:00",
            include_in_preview=1,
            is_published=1,
            idx=1,
        )
        lesson_name = les_res["lesson"]
        print(f"2. Created video lesson record: {lesson_title} ({lesson_name})")

        # 3. Calculate chunks
        total_chunks = (target_size_bytes + CHUNK_SIZE - 1) // CHUNK_SIZE
        filename = f"video_{label.lower().replace(' ', '_')}.mp4"

        print(f"3. Initiating upload for {filename}: {target_size_bytes} bytes across {total_chunks} chunks...")
        t0 = time.time()
        init_res = initiate_video_upload(
            filename=filename,
            total_size=target_size_bytes,
            total_chunks=total_chunks,
            course=course_name,
            chapter=chapter_name,
            lesson=lesson_name,
            is_private=0
        )
        upload_id = init_res["upload_id"]

        # 4. Stream upload chunks
        # Chunk 0 has MP4 ftyp box
        ftyp_header = b"\x00\x00\x00 ftypisom\x00\x00\x02\x00isomiso2avc1mp41"
        for i in range(total_chunks):
            start = i * CHUNK_SIZE
            end = min(start + CHUNK_SIZE, target_size_bytes)
            chunk_len = end - start

            if i == 0:
                payload = ftyp_header + (b"\x00" * (chunk_len - len(ftyp_header)))
            else:
                # Repeated pattern for fast memory allocation
                payload = b"V" * chunk_len

            frappe.form_dict["upload_id"] = upload_id
            frappe.form_dict["chunk_index"] = i
            frappe.local.request.files = ImmutableMultiDict([("chunk", FileStorage(stream=io.BytesIO(payload), filename=f"chunk_{i}"))])
            c_res = upload_video_chunk()
            assert c_res["part_size"] == chunk_len
            if (i + 1) % 20 == 0 or (i + 1) == total_chunks:
                pct = ((i + 1) / total_chunks) * 100
                print(f"   Chunk {i + 1}/{total_chunks} uploaded ({pct:.0f}%)")

        upload_time = time.time() - t0
        print(f"4. All {total_chunks} chunks transferred in {upload_time:.2f}s ({target_size_bytes / (1024*1024*upload_time):.1f} MB/s)")

        # 5. Assemble video on server
        t_assem = time.time()
        assem_res = assemble_video_upload(upload_id)
        assem_time = time.time() - t_assem
        print(f"5. Assembled on server in {assem_time:.2f}s. Result:", assem_res)
        file_url = assem_res["file_url"]

        # 6. Verify file exists in physical storage
        disk_path = frappe.get_site_path("public", file_url.lstrip("/"))
        assert os.path.exists(disk_path), f"File missing at {disk_path}"
        actual_disk_size = os.path.getsize(disk_path)
        assert actual_disk_size == target_size_bytes, f"Size mismatch: expected {target_size_bytes}, got {actual_disk_size}"
        print(f"6. Verified file in storage: {disk_path} ({actual_disk_size / (1024*1024):.2f} MB)")

        # 7. Verify Frappe File record
        file_doc = frappe.get_doc("File", {"file_url": file_url})
        assert file_doc.file_size == target_size_bytes
        print(f"7. Verified File Doctype record: {file_doc.name} (file_size={file_doc.file_size})")

        # 8. Verify LMS Lesson record contains the correct URL
        lesson_doc = frappe.get_doc("Course Lesson", lesson_name)
        assert lesson_doc.video_file == file_url, f"Lesson video_file mismatch: {lesson_doc.video_file} != {file_url}"
        print(f"8. Verified Course Lesson '{lesson_doc.title}' has video_file: {lesson_doc.video_file}")

        # 9. Verify Playlist tree returns video under the correct module
        playlist = get_course_playlist(course_name)
        found_in_playlist = False
        for ch in playlist["chapters"]:
            if ch["name"] == chapter_name:
                for les in ch["lessons"]:
                    if les["name"] == lesson_name:
                        assert les["video_file"] == file_url
                        found_in_playlist = True
        assert found_in_playlist, f"Lesson not found in playlist under module {chapter_name}"
        print(f"9. Verified Playlist tree returns video lesson under module: {chapter_title}")

        # 10. Verify Student can play and seek through video via HTTP Range requests
        # Test Normal GET
        app_dummy = lambda env, sr: [b""]
        _sites_dir = os.path.dirname(os.path.abspath(frappe.get_site_path()))
        middleware = StaticDataMiddleware(app_dummy, {"/files": _sites_dir})

        # Test A: Standard Initial Stream Request
        b_normal = EnvironBuilder(path=file_url, headers={"Host": "lms.local"})
        resp_headers_normal = {}
        def sr_normal(status, headers, exc_info=None):
            resp_headers_normal["status"] = status
            resp_headers_normal.update(dict(headers))
        middleware(b_normal.get_environ(), sr_normal)
        assert resp_headers_normal["status"].startswith("200"), f"Expected 200, got {resp_headers_normal.get('status')}"
        assert resp_headers_normal.get("Accept-Ranges") == "bytes", "Must advertise Accept-Ranges: bytes"
        print(f"10a. Verified Standard Stream: {resp_headers_normal['status']} | Accept-Ranges: bytes")

        # Test B: Student Video Seeking (HTTP Range Request to 50% through video)
        seek_start = target_size_bytes // 2
        seek_end = seek_start + 1024 * 1024 - 1 # 1 MB slice
        b_range = EnvironBuilder(path=file_url, headers={"Host": "lms.local", "Range": f"bytes={seek_start}-{seek_end}"})
        resp_headers_range = {}
        def sr_range(status, headers, exc_info=None):
            resp_headers_range["status"] = status
            resp_headers_range.update(dict(headers))
        middleware(b_range.get_environ(), sr_range)
        assert resp_headers_range["status"].startswith("206"), f"Expected 206 Partial Content, got {resp_headers_range.get('status')}"
        assert resp_headers_range.get("Accept-Ranges") == "bytes"
        expected_range_str = f"bytes {seek_start}-{seek_end}/{target_size_bytes}"
        assert resp_headers_range.get("Content-Range") == expected_range_str, f"Content-Range mismatch: {resp_headers_range.get('Content-Range')} != {expected_range_str}"
        print(f"10b. Verified Video Seeking: {resp_headers_range['status']} | Content-Range: {resp_headers_range['Content-Range']}")

        # 11. Verify Page reload / student lesson retrieval
        frappe.set_user(test_student)
        frappe.local.request_ip = "127.0.0.1"
        # Enroll student in course
        if not frappe.db.exists("LMS Enrollment", {"course": course_name, "member": test_student}):
            frappe.get_doc({
                "doctype": "LMS Enrollment",
                "course": course_name,
                "member": test_student,
            }).insert(ignore_permissions=True)

        student_lesson = get_lesson(course=course_name, chapter=ch_res["idx"], lesson=1)
        assert student_lesson.get("video_file") == file_url
        print(f"11. Verified Student Retrieval ({test_student}): Lesson video URL accessible after reload: {student_lesson['video_file']}")
        frappe.set_user("Administrator")

        print(f"✓✓✓ {label} TEST PASSED WITH 100% SUCCESS ✓✓✓")
        return disk_path, file_doc.name

    # ------------------------------------------------------------------------
    # RUN PROGRESSIVE LARGE VIDEO TESTS: 100MB, 250MB, 500MB, 1GB
    # ------------------------------------------------------------------------
    created_cleanup_list = []

    try:
        # TEST 5: 100 MB Video
        p100, f100 = execute_video_test(100 * 1024 * 1024, "100 MB Video", "Module 1: 100MB Stream", "Lesson 1: Intro 100MB")
        created_cleanup_list.append((p100, f100))

        # TEST 6: 250 MB Video
        p250, f250 = execute_video_test(250 * 1024 * 1024, "250 MB Video", "Module 2: 250MB Stream", "Lesson 2: Core 250MB")
        created_cleanup_list.append((p250, f250))

        # TEST 7: 500 MB Video
        p500, f500 = execute_video_test(500 * 1024 * 1024, "500 MB Video", "Module 3: 500MB Stream", "Lesson 3: Deep Dive 500MB")
        created_cleanup_list.append((p500, f500))

        # TEST 8: 1 GB Video (1024 MB)
        p1000, f1000 = execute_video_test(1024 * 1024 * 1024, "1 GB Video", "Module 4: 1GB Masterclass", "Lesson 4: Masterclass 1GB")
        created_cleanup_list.append((p1000, f1000))

    finally:
        print("\n--- Cleaning up test video files from storage ---")
        for disk_p, file_docname in created_cleanup_list:
            try:
                if os.path.exists(disk_p):
                    os.remove(disk_p)
                frappe.db.delete("File", {"name": file_docname})
            except Exception as e:
                print("Cleanup error for", disk_p, e)
        frappe.db.commit()
        print("✓ Cleanup completed.")

    print("\n" + "=" * 80)
    print("ALL TESTS IN LARGE VIDEO UPLOAD & STREAMING SUITE PASSED 100% SUCCESSFULLY!")
    print("=" * 80)
    frappe.destroy()

if __name__ == "__main__":
    run_tests()
