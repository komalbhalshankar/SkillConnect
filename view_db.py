"""
SkillConnect — Live Database Inspector for Project Review & Teacher Demo.
Usage:
  python view_db.py                    (Shows overview summary of all tables)
  python view_db.py users              (Shows all registered users and roles)
  python view_db.py user_skills        (Shows student Teach/Learn skill portfolios)
  python view_db.py requests           (Shows exchange requests and status)
  python view_db.py sessions           (Shows scheduled and completed sessions)
  python view_db.py ratings            (Shows post-session ratings and reviews)
  python view_db.py categories         (Shows standard skill categories)
  python view_db.py all                (Shows full dump of all active tables)
"""
import sys
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "instance" / "skillconnect.db"

def print_table(title, headers, rows):
    print(f"\n{'='*75}")
    print(f"  TABLE: {title} ({len(rows)} records)")
    print(f"{'='*75}")
    if not rows:
        print("  (No records found)")
        return

    # Calculate column widths
    cols = len(headers)
    widths = [len(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            widths[i] = max(widths[i], len(str(val) if val is not None else "NULL"))
    
    # Cap maximum width for readability
    widths = [min(w, 40) for w in widths]

    # Format header
    sep = "+-" + "-+-".join("-" * w for w in widths) + "-+"
    hdr = "| " + " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers)) + " |"
    print(sep)
    print(hdr)
    print(sep)

    # Format rows
    for row in rows:
        formatted = []
        for i, val in enumerate(row):
            s = str(val if val is not None else "")
            if len(s) > widths[i]:
                s = s[:widths[i]-3] + "..."
            formatted.append(s.ljust(widths[i]))
        print("| " + " | ".join(formatted) + " |")
    print(sep)

def view_summary(cur):
    print(f"\n{'='*75}")
    print(f"  SKILLCONNECT — DATABASE OVERVIEW (instance/skillconnect.db)")
    print(f"{'='*75}")
    tables = [
        ("users", "Registered Students & Administrators"),
        ("skill_categories", "Standard Academic Skill Categories"),
        ("skills", "Standard Taxonomy & Custom Added Skills"),
        ("user_skills", "Student Portfolios (Teach vs. Learn)"),
        ("exchange_requests", "Exchange Proposals & Agreement State Machine"),
        ("exchange_sessions", "Scheduled & Completed Learning Sessions"),
        ("ratings", "Bilateral Post-Session Peer Reviews & Ratings")
    ]
    summary_rows = []
    for tbl, desc in tables:
        count = cur.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
        summary_rows.append((tbl, count, desc))
    
    print_table("Database Tables Summary", ["Table Name", "Total Records", "Description"], summary_rows)
    print("\n[Tip] View any table in detail by running: python view_db.py <table_name>")
    print("   Example: python view_db.py users")
    print("   Example: python view_db.py user_skills")
    print("   Example: python view_db.py requests")
    print("   Example: python view_db.py sessions")
    print("   Example: python view_db.py ratings\n")

def view_users(cur):
    query = """
    SELECT id, name, email, role, 
           COALESCE(college, '-') as college,
           substr(password_hash, 1, 20) || '...' as password_hash,
           created_at 
    FROM users 
    ORDER BY id ASC;
    """
    rows = cur.execute(query).fetchall()
    print_table("users (Registered Students & Admins)", 
                ["ID", "Name", "Email", "Role", "College", "Password Hash (Argon2/Salted)", "Created At"], rows)

def view_user_skills(cur):
    query = """
    SELECT us.id, u.name as student, us.skill_type, s.name as skill_name, 
           us.proficiency, COALESCE(us.notes, '-') as notes
    FROM user_skills us
    JOIN users u ON us.user_id = u.id
    JOIN skills s ON us.skill_id = s.id
    ORDER BY us.id ASC;
    """
    rows = cur.execute(query).fetchall()
    print_table("user_skills (Student Portfolios)", 
                ["ID", "Student", "Type", "Skill Name", "Proficiency", "Notes"], rows)

def view_requests(cur):
    query = """
    SELECT r.id, 
           sender.name as sender, 
           receiver.name as receiver, 
           s_off.name as offered_skill, 
           s_req.name as requested_skill, 
           r.status, 
           COALESCE(r.message, '-') as message
    FROM exchange_requests r
    JOIN users sender ON r.sender_id = sender.id
    JOIN users receiver ON r.receiver_id = receiver.id
    JOIN skills s_off ON r.offered_skill_id = s_off.id
    JOIN skills s_req ON r.requested_skill_id = s_req.id
    ORDER BY r.id ASC;
    """
    rows = cur.execute(query).fetchall()
    print_table("exchange_requests (Proposals & States)", 
                ["ID", "Sender", "Receiver", "Offered (Teach)", "Requested (Learn)", "Status", "Message"], rows)

def view_sessions(cur):
    query = """
    SELECT ses.id, 
           ses.request_id,
           sender.name || ' & ' || receiver.name as participants,
           ses.scheduled_at, 
           ses.duration_minutes || ' mins' as duration, 
           ses.mode,
           ses.status,
           COALESCE(ses.meeting_details, '-') as meeting_link
    FROM exchange_sessions ses
    JOIN exchange_requests r ON ses.request_id = r.id
    JOIN users sender ON r.sender_id = sender.id
    JOIN users receiver ON r.receiver_id = receiver.id
    ORDER BY ses.id ASC;
    """
    rows = cur.execute(query).fetchall()
    print_table("exchange_sessions (Learning Sessions)", 
                ["ID", "Req ID", "Participants", "Scheduled At", "Duration", "Mode", "Status", "Meeting Details"], rows)

def view_ratings(cur):
    query = """
    SELECT rat.id, 
           rat.session_id, 
           reviewer.name as reviewer, 
           reviewee.name as reviewee, 
           rat.score || ' / 5 Stars' as score, 
           rat.feedback,
           rat.created_at
    FROM ratings rat
    JOIN users reviewer ON rat.reviewer_id = reviewer.id
    JOIN users reviewee ON rat.reviewee_id = reviewee.id
    ORDER BY rat.id ASC;
    """
    rows = cur.execute(query).fetchall()
    print_table("ratings (Bilateral Post-Session Peer Reviews)", 
                ["ID", "Session", "Reviewer", "Reviewee", "Score", "Feedback", "Timestamp"], rows)

def view_categories(cur):
    query = "SELECT id, name, icon, description FROM skill_categories ORDER BY id ASC;"
    rows = cur.execute(query).fetchall()
    print_table("skill_categories (Taxonomy)", ["ID", "Category Name", "Icon", "Description"], rows)

def main():
    if not DB_PATH.exists():
        print(f"[ERROR] Database file not found at: {DB_PATH}")
        print("Run 'python run.py init-db' and 'python run.py seed-demo' first.")
        sys.exit(1)

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    target = sys.argv[1].lower() if len(sys.argv) > 1 else "summary"

    if target in ["summary", "overview", "info"]:
        view_summary(cur)
    elif target in ["users", "user"]:
        view_users(cur)
    elif target in ["user_skills", "skills_portfolio", "portfolio"]:
        view_user_skills(cur)
    elif target in ["requests", "exchange_requests", "proposals"]:
        view_requests(cur)
    elif target in ["sessions", "exchange_sessions"]:
        view_sessions(cur)
    elif target in ["ratings", "reviews", "feedback"]:
        view_ratings(cur)
    elif target in ["categories", "skill_categories"]:
        view_categories(cur)
    elif target in ["all", "full"]:
        view_summary(cur)
        view_users(cur)
        view_user_skills(cur)
        view_requests(cur)
        view_sessions(cur)
        view_ratings(cur)
    else:
        print(f"[UNKNOWN TABLE] '{target}'. Available tables: users, user_skills, requests, sessions, ratings, categories, all")
    
    con.close()

if __name__ == "__main__":
    main()
