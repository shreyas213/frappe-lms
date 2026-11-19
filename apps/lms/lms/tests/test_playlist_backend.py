import os
import frappe
from lms.lms.api import (
    get_course_playlist,
    quick_add_video_lesson,
    delete_video_lesson,
    reorder_playlist_lessons,
    mark_lesson_complete,
    update_last_accessed_lesson,
    create_course_chapter,
    toggle_course_publish_status,
)

def run_tests():
    os.chdir("/home/shrey/frappe/frappe-bench/sites")
    frappe.init("lms.local")
    frappe.connect()

    frappe.set_user("Administrator")
    print("Testing Playlist Manager Backend APIs...")

    # 1. Create or get test course
    course_name = "test-video-playlist-course"
    if frappe.db.exists("LMS Course", course_name):
        frappe.delete_doc("LMS Course", course_name, force=True)

    course_doc = frappe.get_doc({
        "doctype": "LMS Course",
        "title": "Test Video Playlist Course",
        "name": course_name,
        "short_introduction": "Complete masterclass with video playlist.",
        "description": "<p>A comprehensive course with multiple video lessons.</p>",
        "published": 1,
    })
    course_doc.insert(ignore_permissions=True)
    frappe.db.commit()
    print("✓ Created test course:", course_doc.name)

    # 2. Create Module 1
    ch1 = create_course_chapter(course_name, "Module 1: Introduction")
    ch1_name = ch1["chapter"]
    print("✓ Created Chapter 1:", ch1_name)

    # 3. Add video lessons
    # Lesson 1: YouTube
    l1 = quick_add_video_lesson(
        course=course_name,
        chapter=ch1_name,
        title="Intro to Vue.js",
        description="Getting started with Vue 3 and modern web development.",
        youtube="https://www.youtube.com/watch?v=b0IZo2Aho2Y",
        duration="10:15",
        include_in_preview=1,
    )
    print("✓ Added YouTube lesson:", l1["lesson"])

    # Lesson 2: Vimeo
    l2 = quick_add_video_lesson(
        course=course_name,
        chapter=ch1_name,
        title="Component Architecture",
        description="Understanding single file components and reactivity.",
        vimeo_url="https://vimeo.com/76979871",
        duration="15:30",
        include_in_preview=0,
    )
    print("✓ Added Vimeo lesson:", l2["lesson"])

    # Lesson 3: MP4 direct upload
    l3 = quick_add_video_lesson(
        course=course_name,
        chapter=ch1_name,
        title="Direct Video Upload",
        description="HTML5 direct video playback test.",
        video_file="/files/sample_video.mp4",
        duration="08:45",
        attachment="/files/sample_notes.pdf",
        include_in_preview=0,
    )
    print("✓ Added MP4 video lesson:", l3["lesson"])

    # 4. Create Module 2
    ch2 = create_course_chapter(course_name, "Module 2: Advanced Topics")
    ch2_name = ch2["chapter"]
    print("✓ Created Chapter 2:", ch2_name)

    l4 = quick_add_video_lesson(
        course=course_name,
        chapter=ch2_name,
        title="State Management",
        description="Pinia and centralized stores.",
        youtube="https://www.youtube.com/watch?v=2BpwXq1v0lA",
        duration="22:10",
        include_in_preview=0,
    )
    print("✓ Added lesson in Chapter 2:", l4["lesson"])

    # 5. Fetch playlist
    playlist = get_course_playlist(course_name)
    assert playlist["course"]["title"] == "Test Video Playlist Course"
    assert playlist["course"]["total_lessons"] == 4
    assert len(playlist["chapters"]) == 2
    assert len(playlist["chapters"][0]["lessons"]) == 3
    assert len(playlist["chapters"][1]["lessons"]) == 1
    assert playlist["chapters"][0]["lessons"][0]["youtube"] == "https://www.youtube.com/watch?v=b0IZo2Aho2Y"
    assert playlist["chapters"][0]["lessons"][1]["vimeo_url"] == "https://vimeo.com/76979871"
    assert playlist["chapters"][0]["lessons"][2]["video_file"] == "/files/sample_video.mp4"
    assert playlist["chapters"][0]["lessons"][2]["attachment"] == "/files/sample_notes.pdf"
    print("✓ Verified get_course_playlist returns complete hierarchy and metadata")

    # 6. Test reordering
    reorder_res = reorder_playlist_lessons(ch1_name, [l3["lesson"], l1["lesson"], l2["lesson"]])
    assert reorder_res["status"] == "success"
    print("✓ Verified reorder_playlist_lessons")

    # 7. Test Student progress tracking
    # Create or use a student user
    student_user = "test_student@example.com"
    if not frappe.db.exists("User", student_user):
        u = frappe.get_doc({
            "doctype": "User",
            "email": student_user,
            "first_name": "Test",
            "last_name": "Student",
            "send_welcome_email": 0,
        })
        u.insert(ignore_permissions=True)

    frappe.set_user(student_user)

    # Mark lesson 1 complete
    prog = mark_lesson_complete(course_name, l1["lesson"])
    assert prog["status"] == "success"
    assert prog["completed"] is True
    assert prog["completed_lessons"] == 1
    assert prog["total_lessons"] == 4
    assert prog["progress"] == 25.0
    print("✓ Verified mark_lesson_complete updates LMS Course Progress & LMS Enrollment: 25% complete")

    # Mark lesson 2 complete
    prog2 = mark_lesson_complete(course_name, l2["lesson"])
    assert prog2["completed_lessons"] == 2
    assert prog2["progress"] == 50.0
    print("✓ Verified progress updates dynamically: 50% complete")

    # Update last accessed lesson
    acc = update_last_accessed_lesson(course_name, l3["lesson"])
    assert acc["status"] == "success"
    print("✓ Verified update_last_accessed_lesson")

    # Fetch playlist as student
    student_playlist = get_course_playlist(course_name)
    assert student_playlist["course"]["is_enrolled"] is True
    assert student_playlist["course"]["completed_lessons"] == 2
    assert student_playlist["course"]["progress"] == 50.0
    assert student_playlist["course"]["current_lesson"] == l3["lesson"]
    print("✓ Verified student playlist matches real database state and resume point!")

    # 8. Test publish / draft toggle
    frappe.set_user("Administrator")
    toggle_course_publish_status(course_name, 0)
    assert frappe.db.get_value("LMS Course", course_name, "published") == 0
    toggle_course_publish_status(course_name, 1)
    assert frappe.db.get_value("LMS Course", course_name, "published") == 1
    print("✓ Verified toggle_course_publish_status (draft/publish)")

    # 9. Test delete video lesson
    del_res = delete_video_lesson(l4["lesson"])
    assert del_res["status"] == "success"
    assert not frappe.db.exists("Course Lesson", l4["lesson"])
    print("✓ Verified delete_video_lesson")

    print("\nALL 9 BACKEND API TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
