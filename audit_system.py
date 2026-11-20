import os
import sys
import frappe
from frappe.utils import cint

def run_audit():
    print("=" * 80)
    print("FRAPPE LMS COMPREHENSIVE SYSTEM AUDIT")
    print("=" * 80)
    
    os.chdir("/home/shrey/frappe/frappe-bench/sites")
    frappe.init(site="lms.local")
    frappe.connect()
    
    # 1. Error Logs
    print("\n--- 1. RECENT ERROR LOGS ---")
    logs = frappe.db.sql("""
        SELECT name, method, LEFT(error, 250) as err_snippet, seen, creation 
        FROM `tabError Log` 
        ORDER BY creation DESC 
        LIMIT 15
    """, as_dict=True)
    
    print(f"Total error logs retrieved: {len(logs)}")
    for l in logs:
        print(f"[{l.creation}] {l.name} | Method: {l.method}")
        print(f"   Snippet: {l.err_snippet.strip().replace(chr(10), ' ')[:160]}...\n")
        
    # 2. Site Configuration & Limits
    print("\n--- 2. SITE CONFIGURATION & LIMITS ---")
    conf = frappe.conf
    print(f"Site name: {frappe.local.site}")
    print(f"Developer mode: {conf.get('developer_mode')}")
    print(f"max_file_size in conf: {conf.get('max_file_size')}")
    print(f"max_video_size_mb in conf: {conf.get('max_video_size_mb')}")
    sys_max_file = frappe.get_system_settings('max_file_size')
    print(f"System settings max_file_size: {sys_max_file}")
    
    # 3. LMS App Modules & DocTypes
    print("\n--- 3. LMS DOCTYPE & MODULE VALIDATION ---")
    doctypes = frappe.get_all("DocType", filters={"module": "LMS"}, fields=["name"])
    print(f"Total LMS DocTypes: {len(doctypes)}")
    doctype_errors = []
    for dt in doctypes:
        dt_name = dt.name
        try:
            meta = frappe.get_meta(dt_name)
            doc_class = frappe.get_doc(dt_name)
        except Exception as e:
            doctype_errors.append((dt_name, str(e)))
            
    if doctype_errors:
        print(f"FAILED DocTypes ({len(doctype_errors)}):")
        for dt_name, err in doctype_errors:
            print(f"  {dt_name}: {err}")
    else:
        print("All LMS DocTypes loaded and verified with 0 errors.")
        
    # 4. Hooks validation
    print("\n--- 4. HOOKS VALIDATION ---")
    try:
        app_hooks = frappe.get_hooks(app_name="lms")
        print(f"LMS app hooks found. Total hook keys: {len(app_hooks)}")
        for k in ["doc_events", "scheduler_events", "override_whitelisted_methods", "website_route_rules"]:
            if k in app_hooks:
                print(f"  Hook '{k}': {app_hooks[k]}")
    except Exception as e:
        print(f"Error inspecting hooks: {e}")
        
    # 5. Database Statistics
    print("\n--- 5. DATABASE INTEGRITY & COUNTS ---")
    counts = {
        "User": frappe.db.count("User"),
        "LMS Course": frappe.db.count("LMS Course"),
        "Course Chapter": frappe.db.count("Course Chapter"),
        "Course Lesson": frappe.db.count("Course Lesson"),
        "LMS Enrollment": frappe.db.count("LMS Enrollment"),
        "LMS Batch": frappe.db.count("LMS Batch"),
        "Course Instructor": frappe.db.count("Course Instructor"),
        "File": frappe.db.count("File"),
    }
    for k, v in counts.items():
        print(f"  {k}: {v}")
        
    # Check published vs draft courses
    published_courses = frappe.get_all("LMS Course", filters={"published": 1}, fields=["name", "title"])
    draft_courses = frappe.get_all("LMS Course", filters={"published": 0}, fields=["name", "title"])
    print(f"  Published Courses ({len(published_courses)}): {[c.name for c in published_courses]}")
    print(f"  Draft Courses ({len(draft_courses)}): {[c.name for c in draft_courses]}")
    
    # 6. File & Video Storage Check
    print("\n--- 6. STORAGE & STAGING CHECKS ---")
    site_path = frappe.get_site_path()
    public_files = frappe.get_site_path("public", "files")
    private_files = frappe.get_site_path("private", "files")
    staging_chunks = frappe.get_site_path("private", "chunks")
    print(f"Site path: {site_path}")
    print(f"Public files path exists: {os.path.exists(public_files)} ({public_files})")
    print(f"Private files path exists: {os.path.exists(private_files)} ({private_files})")
    print(f"Staging chunks path exists: {os.path.exists(staging_chunks)} ({staging_chunks})")
    
    # 7. Check for broken file links in Course Lesson
    print("\n--- 7. COURSE LESSON VIDEO & FILE AUDIT ---")
    lessons = frappe.get_all("Course Lesson", fields=["name", "title", "course", "chapter", "video_file", "youtube", "vimeo_url", "attachment"])
    print(f"Total lessons: {len(lessons)}")
    video_upload_lessons = [l for l in lessons if l.video_file]
    youtube_lessons = [l for l in lessons if l.youtube]
    vimeo_lessons = [l for l in lessons if l.vimeo_url]
    print(f"  Lessons with uploaded video: {len(video_upload_lessons)}")
    print(f"  Lessons with YouTube: {len(youtube_lessons)}")
    print(f"  Lessons with Vimeo: {len(vimeo_lessons)}")
    
    broken_files = []
    for l in video_upload_lessons:
        v_url = l.video_file
        if v_url.startswith("/files/"):
            phys_path = frappe.get_site_path("public", "files", v_url.split("/files/")[1])
            if not os.path.exists(phys_path):
                broken_files.append((l.name, l.title, v_url, phys_path))
    if broken_files:
        print(f"WARNING: Found {len(broken_files)} lessons with missing video files on disk:")
        for name, title, url, path in broken_files[:10]:
            print(f"  Lesson {name} ('{title}'): {url} -> not found at {path}")
    else:
        print("All uploaded video lesson files exist on disk.")

    print("\n" + "=" * 80)
    print("AUDIT COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    run_audit()
