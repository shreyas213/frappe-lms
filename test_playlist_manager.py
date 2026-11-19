import frappe

def run():
    frappe.init(site="lms.local")
    frappe.connect()

    from lms.lms.api import create_course_chapter, quick_add_video_lesson, get_course_playlist

    course_name = "test-video-playlist-course"

    # Check if course exists
    course_doc = frappe.get_doc("LMS Course", course_name)
    print(f"Found course: {course_doc.title} ({course_doc.name})")

    # Clean existing test chapters for this course to test from scratch (0 -> 1 -> 2)
    ch_names = frappe.get_all("Course Chapter", filters={"course": course_name}, pluck="name")
    for ch in ch_names:
        frappe.db.delete("Lesson Reference", {"parent": ch})
    frappe.db.delete("Course Chapter", {"course": course_name})
    frappe.db.delete("Chapter Reference", {"parent": course_name})
    frappe.db.commit()

    # Verify initial count
    init_playlist = get_course_playlist(course_name)
    print("Initial count:", init_playlist.get("stats"))
    assert init_playlist["stats"]["total_modules"] == 0
    assert init_playlist["stats"]["total_lessons"] == 0

    # Test 1: Add Module 1
    res_ch1 = create_course_chapter(
        course=course_name,
        title="Module 1: Java Fundamentals",
        description="Core concepts of Java programming language."
    )
    print("Created Chapter 1:", res_ch1)
    assert res_ch1.get("title") == "Module 1: Java Fundamentals"
    assert res_ch1.get("description") == "Core concepts of Java programming language."

    # Check stats after Module 1
    stats1 = get_course_playlist(course_name)["stats"]
    print("Stats after Module 1:", stats1)
    assert stats1["total_modules"] == 1
    assert stats1["total_lessons"] == 0

    # Test 2: Add Lesson 1 under Module 1 (with YouTube URL & duration)
    res_les1 = quick_add_video_lesson(
        course=course_name,
        chapter=res_ch1["name"],
        title="Lesson 1: Introduction to Java",
        description="Getting started with Java syntax and OOP.",
        youtube="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        duration=600,
        include_in_preview=1,
        is_published=1,
        idx=1
    )
    print("Created Lesson 1:", res_les1)

    stats2 = get_course_playlist(course_name)["stats"]
    print("Stats after Lesson 1:", stats2)
    assert stats2["total_modules"] == 1
    assert stats2["total_lessons"] == 1

    # Test 3: Add Module 2 and Lesson 2 (with MP4 & PDF attachment)
    res_ch2 = create_course_chapter(
        course=course_name,
        title="Module 2: Advanced Java",
        description="Advanced functional programming and concurrency."
    )
    print("Created Chapter 2:", res_ch2)

    res_les2 = quick_add_video_lesson(
        course=course_name,
        chapter=res_ch2["name"],
        title="Lesson 2: Java Streams",
        description="Mastering map, filter, reduce.",
        video_file="/files/sample_stream.mp4",
        attachment="/files/streams_cheatsheet.pdf",
        duration=900,
        include_in_preview=0,
        is_published=1,
        idx=2
    )
    print("Created Lesson 2:", res_les2)

    stats3 = get_course_playlist(course_name)["stats"]
    print("Stats after Lesson 2:", stats3)
    assert stats3["total_modules"] == 2
    assert stats3["total_lessons"] == 2

    # Verify full playlist structure returned
    full_playlist = get_course_playlist(course_name)
    print("Full playlist chapters count:", len(full_playlist["chapters"]))
    for ch in full_playlist["chapters"]:
        print(f"Chapter: {ch['title']} | Description: {ch.get('description')} | Lessons count: {len(ch['lessons'])}")
        for les in ch["lessons"]:
            print(f"  - Lesson: {les['title']} | idx: {les.get('idx')} | video: {les.get('youtube') or les.get('video_file')} | preview: {les.get('include_in_preview')}")

    print("ALL PLAYLIST MANAGER VERIFICATION TESTS PASSED SUCCESSFULLY!")
    frappe.destroy()

if __name__ == "__main__":
    run()
