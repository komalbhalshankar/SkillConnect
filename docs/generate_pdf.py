#!/usr/bin/env python3
"""
Generate a clean, high-resolution, publication-quality printable HTML
and compile it to PDF using headless Chrome/Edge.
"""
import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_OUT = os.path.join(BASE_DIR, "data_dictionary_printable.html")
PDF_OUT = os.path.join(BASE_DIR, "SkillConnect_Data_Dictionary.pdf")

TABLES = [
    {
        "name": "users",
        "num": "1",
        "title": "users",
        "category": "Core / Identity Entity",
        "desc": "Stores student and administrator credentials, profiles, academic institution, and role-based access permissions.",
        "relationships": "One-to-Many: user_skills, sent_requests, received_requests, given_ratings, received_ratings.",
        "columns": [
            ("id", "INTEGER", "PK, AUTOINC", "NO", "None", "Unique primary identifier for user account"),
            ("name", "VARCHAR(120)", "NOT NULL", "NO", "None", "Full legal or display name of student / admin"),
            ("email", "VARCHAR(180)", "UNIQUE, INDEX", "NO", "None", "Institutional email address (login credential)"),
            ("password_hash", "VARCHAR(255)", "NOT NULL", "NO", "None", "Cryptographically salted password hash (pbkdf2:sha256)"),
            ("role", "VARCHAR(20)", "NOT NULL", "NO", "'student'", "Authorization role: 'student' or 'admin'"),
            ("college", "VARCHAR(180)", "NULLABLE", "YES", "None", "Enrolled college / university institution name"),
            ("bio", "TEXT", "NULLABLE", "YES", "None", "Student biography, academic interests & background"),
            ("availability", "VARCHAR(120)", "NULLABLE", "YES", "None", "Preferred study hours (e.g. 'Weekends & Evenings')"),
            ("created_at", "DATETIME", "NOT NULL", "NO", "UTC_NOW", "Account creation timestamp (UTC)"),
            ("updated_at", "DATETIME", "NOT NULL", "NO", "UTC_NOW", "Profile last updated timestamp (UTC, onupdate)")
        ]
    },
    {
        "name": "skill_categories",
        "num": "2",
        "title": "skill_categories",
        "category": "Taxonomy Entity",
        "desc": "Standardized academic and technical taxonomy groupings for classifying platform skills into subject disciplines.",
        "relationships": "One-to-Many: skills (cascade all, delete-orphan). Pre-seeded with 8 standard MCA disciplines.",
        "columns": [
            ("id", "INTEGER", "PK, AUTOINC", "NO", "None", "Unique category primary identifier"),
            ("name", "VARCHAR(80)", "UNIQUE, NOT NULL", "NO", "None", "Standardized category name (e.g. 'Programming & Tech', 'Database')"),
            ("description", "VARCHAR(255)", "NULLABLE", "YES", "None", "Overview of domain competencies covered in this category"),
            ("icon", "VARCHAR(50)", "NOT NULL", "NO", "'bi-tag'", "Bootstrap Icons CSS class for UI visual badge"),
            ("created_at", "DATETIME", "NOT NULL", "NO", "UTC_NOW", "Taxonomy creation timestamp (UTC)")
        ]
    },
    {
        "name": "skills",
        "num": "3",
        "title": "skills",
        "category": "Catalogue Entity",
        "desc": "Canonical catalogue of predefined and student-proposed skills available for peer exchange.",
        "relationships": "Many-to-One: skill_categories (category_id). One-to-Many: user_skills (cascade all, delete-orphan).",
        "columns": [
            ("id", "INTEGER", "PK, AUTOINC", "NO", "None", "Unique skill primary identifier"),
            ("category_id", "INTEGER", "FK, NOT NULL", "NO", "None", "Parent category ID referencing skill_categories(id)"),
            ("name", "VARCHAR(100)", "UNIQUE, INDEX", "NO", "None", "Canonical skill name (e.g. 'Python', 'SQL', 'Figma', 'Docker')"),
            ("description", "VARCHAR(255)", "NULLABLE", "YES", "None", "Summary curriculum or domain details"),
            ("created_at", "DATETIME", "NOT NULL", "NO", "UTC_NOW", "Skill registration timestamp (UTC)")
        ]
    },
    {
        "name": "user_skills",
        "num": "4",
        "title": "user_skills",
        "category": "Associative / Junction Entity",
        "desc": "Junction table mapping student profiles to skills with teaching/learning intent and proficiency levels.",
        "relationships": "Foreign Keys: user_id -> users(id), skill_id -> skills(id). Table Unique Constraint: uq_user_skill_type.",
        "columns": [
            ("id", "INTEGER", "PK, AUTOINC", "NO", "None", "Unique junction record identifier"),
            ("user_id", "INTEGER", "FK, INDEX", "NO", "None", "Student ID referencing users(id)"),
            ("skill_id", "INTEGER", "FK, INDEX", "NO", "None", "Skill ID referencing skills(id)"),
            ("skill_type", "VARCHAR(10)", "NOT NULL", "NO", "None", "Intent type: 'teach' (offering) or 'learn' (seeking)"),
            ("proficiency", "VARCHAR(20)", "NOT NULL", "NO", "'intermediate'", "Proficiency: 'beginner', 'intermediate', 'advanced'"),
            ("notes", "VARCHAR(255)", "NULLABLE", "YES", "None", "Custom student notes, target frameworks, or topic focus"),
            ("created_at", "DATETIME", "NOT NULL", "NO", "UTC_NOW", "Record addition timestamp (UTC)"),
            ("updated_at", "DATETIME", "NOT NULL", "NO", "UTC_NOW", "Record last modified timestamp (UTC, onupdate)")
        ]
    },
    {
        "name": "exchange_requests",
        "num": "5",
        "title": "exchange_requests",
        "category": "Proposal / Workflow Entity",
        "desc": "Bilateral skill swap proposals initiated by one student to another with offered and requested skills.",
        "relationships": "Foreign Keys: sender_id, receiver_id -> users(id); offered_skill_id, requested_skill_id -> skills(id).",
        "columns": [
            ("id", "INTEGER", "PK, AUTOINC", "NO", "None", "Unique exchange proposal identifier"),
            ("sender_id", "INTEGER", "FK, INDEX", "NO", "None", "Initiating student ID referencing users(id)"),
            ("receiver_id", "INTEGER", "FK, INDEX", "NO", "None", "Recipient peer student ID referencing users(id)"),
            ("offered_skill_id", "INTEGER", "FK, NOT NULL", "NO", "None", "Skill sender teaches, referencing skills(id)"),
            ("requested_skill_id", "INTEGER", "FK, NOT NULL", "NO", "None", "Skill sender wants to learn, referencing skills(id)"),
            ("status", "VARCHAR(20)", "NOT NULL", "NO", "'pending'", "State: 'pending', 'accepted', 'rejected', 'cancelled'"),
            ("message", "TEXT", "NULLABLE", "YES", "None", "Introductory proposal message and schedule preferences"),
            ("created_at", "DATETIME", "NOT NULL", "NO", "UTC_NOW", "Proposal sent timestamp (UTC)"),
            ("updated_at", "DATETIME", "NOT NULL", "NO", "UTC_NOW", "Status transition timestamp (UTC, onupdate)")
        ]
    },
    {
        "name": "exchange_sessions",
        "num": "6",
        "title": "exchange_sessions",
        "category": "Operational / Schedule Entity",
        "desc": "Scheduled learning meetings originating from accepted exchange requests.",
        "relationships": "Foreign Key: request_id -> exchange_requests(id) [UNIQUE 1-to-1]. One-to-Many: ratings.",
        "columns": [
            ("id", "INTEGER", "PK, AUTOINC", "NO", "None", "Unique session identifier"),
            ("request_id", "INTEGER", "FK, UNIQUE", "NO", "None", "Parent accepted request ID referencing exchange_requests(id)"),
            ("scheduled_at", "DATETIME", "NOT NULL", "NO", "None", "Date and time of meeting"),
            ("duration_minutes", "INTEGER", "NOT NULL", "NO", "60", "Planned meeting length in minutes (default 60)"),
            ("mode", "VARCHAR(20)", "NOT NULL", "NO", "'online'", "Delivery format: 'online', 'in_person', 'hybrid'"),
            ("meeting_details", "VARCHAR(255)", "NULLABLE", "YES", "None", "Video call URL (Meet/Zoom) or physical campus room"),
            ("notes", "TEXT", "NULLABLE", "YES", "None", "Session agenda, study materials, or preparation topics"),
            ("status", "VARCHAR(20)", "NOT NULL", "NO", "'scheduled'", "Session state: 'scheduled', 'completed', 'cancelled'"),
            ("created_at", "DATETIME", "NOT NULL", "NO", "UTC_NOW", "Session booking timestamp (UTC)"),
            ("updated_at", "DATETIME", "NOT NULL", "NO", "UTC_NOW", "Session modification timestamp (UTC, onupdate)")
        ]
    },
    {
        "name": "ratings",
        "num": "7",
        "title": "ratings",
        "category": "Evaluation / Review Entity",
        "desc": "Mutual post-session peer ratings and qualitative feedback submitted after completed learning sessions.",
        "relationships": "Foreign Keys: session_id -> exchange_sessions(id), reviewer_id, reviewee_id -> users(id).",
        "columns": [
            ("id", "INTEGER", "PK, AUTOINC", "NO", "None", "Unique evaluation record identifier"),
            ("session_id", "INTEGER", "FK, INDEX", "NO", "None", "Completed session ID referencing exchange_sessions(id)"),
            ("reviewer_id", "INTEGER", "FK, INDEX", "NO", "None", "Student submitting review, referencing users(id)"),
            ("reviewee_id", "INTEGER", "FK, INDEX", "NO", "None", "Student receiving review, referencing users(id)"),
            ("score", "INTEGER", "CHECK 1..5", "NO", "None", "Integer rating between 1 and 5 stars (inclusive)"),
            ("feedback", "TEXT", "NULLABLE", "YES", "None", "Qualitative peer feedback, testimonials & remarks"),
            ("created_at", "DATETIME", "NOT NULL", "NO", "UTC_NOW", "Rating submission timestamp (UTC)")
        ]
    }
]

def badge_html(constraint_str):
    parts = [p.strip() for p in constraint_str.split(',')]
    badges = []
    for p in parts:
        pu = p.upper()
        if "PK" in pu or "PRIMARY" in pu:
            badges.append('<span class="badge badge-pk">PK</span>')
        elif "FK" in pu or "FOREIGN" in pu:
            badges.append('<span class="badge badge-fk">FK</span>')
        elif "UNIQUE" in pu or "UK" in pu:
            badges.append('<span class="badge badge-uk">UNIQUE</span>')
        elif "INDEX" in pu:
            badges.append('<span class="badge badge-idx">INDEX</span>')
        elif "NOT NULL" in pu:
            badges.append('<span class="badge badge-nn">NOT NULL</span>')
        elif "CHECK" in pu:
            badges.append('<span class="badge badge-chk">CHECK 1..5</span>')
        elif "AUTOINC" in pu:
            badges.append('<span class="badge badge-auto">AUTOINC</span>')
        elif "NULLABLE" in pu:
            badges.append('<span class="badge badge-null">NULLABLE</span>')
        else:
            badges.append(f'<span class="badge badge-other">{p}</span>')
    return " ".join(badges)

def generate_html():
    rows_matrix = ""
    for t in TABLES:
        pk = "id"
        fks = []
        uks = []
        for c in t["columns"]:
            if "FK" in c[2]:
                fks.append(c[0])
            if "UNIQUE" in c[2] and c[0] != "id":
                uks.append(c[0])
        fk_str = ", ".join(fks) if fks else "—"
        uk_str = ", ".join(uks) if uks else "—"
        if t["name"] == "user_skills":
            uk_str = "(user_id, skill_id, skill_type)"
        elif t["name"] == "ratings":
            uk_str = "(session_id, reviewer_id)"

        rows_matrix += f"""
        <tr>
            <td style="font-weight: 700; color: #0284c7; text-align: center;">{t["num"]}</td>
            <td><code class="code-pill">{t["name"]}</code></td>
            <td><span class="entity-tag">{t["category"]}</span></td>
            <td><code>{pk}</code></td>
            <td><small>{fk_str}</small></td>
            <td><small>{uk_str}</small></td>
            <td style="font-size: 8.5pt;">{t["desc"]}</td>
        </tr>
        """

    sections_html = ""
    for t in TABLES:
        col_rows = ""
        for col_name, col_type, constraints, nullable, default_val, desc in t["columns"]:
            nullable_badge = '<span class="status-no">NO</span>' if nullable == "NO" else '<span class="status-yes">YES</span>'
            default_display = f"<code>{default_val}</code>" if default_val != "None" else '<span class="text-muted">—</span>'
            constraints_badges = badge_html(constraints)
            col_rows += f"""
            <tr>
                <td><code class="col-name">{col_name}</code></td>
                <td><code class="col-type">{col_type}</code></td>
                <td>{constraints_badges}</td>
                <td style="text-align: center;">{nullable_badge}</td>
                <td>{default_display}</td>
                <td>{desc}</td>
            </tr>
            """

        sections_html += f"""
        <div class="table-card">
            <div class="table-card-header">
                <div>
                    <h3 class="table-title"><code>{t["num"]}. {t["name"]}</code></h3>
                    <div class="table-subtitle">{t["desc"]}</div>
                </div>
                <div class="table-header-meta">
                    <span class="count-badge">{len(t["columns"])} Attributes</span>
                    <span class="category-badge">{t["category"]}</span>
                </div>
            </div>
            <table class="data-table">
                <thead>
                    <tr>
                        <th style="width: 16%;">Column</th>
                        <th style="width: 15%;">Data Type</th>
                        <th style="width: 22%;">Constraints &amp; Keys</th>
                        <th style="width: 8%; text-align: center;">Null</th>
                        <th style="width: 10%;">Default</th>
                        <th style="width: 29%;">Description &amp; Domain Rules</th>
                    </tr>
                </thead>
                <tbody>
                    {col_rows}
                </tbody>
            </table>
            <div class="table-card-footer">
                <span class="footer-label">Integrity &amp; Relationships:</span> {t["relationships"]}
            </div>
        </div>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>SkillConnect — Database Data Dictionary Specification</title>
<style>
    @page {{
        size: A4 portrait;
        margin: 12mm 12mm 14mm 12mm;
        @bottom-right {{
            content: "Page " counter(page) " of " counter(pages);
            font-size: 8pt;
            color: #64748b;
            font-family: 'Segoe UI', system-ui, sans-serif;
        }}
    }}
    
    * {{
        box-sizing: border-box;
        margin: 0;
        padding: 0;
    }}

    body {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        color: #1e293b;
        background: #ffffff;
        font-size: 9pt;
        line-height: 1.45;
        padding: 0;
    }}

    /* Cover / Header Section */
    .header-banner {{
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #ffffff;
        padding: 20px 24px;
        border-radius: 8px;
        margin-bottom: 18px;
        border-left: 6px solid #38bdf8;
    }}

    .header-top {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }}

    .pills-container {{
        display: flex;
        gap: 6px;
    }}

    .pill {{
        background: rgba(56, 189, 248, 0.2);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.4);
        font-size: 7.5pt;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 4px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    .pill-secondary {{
        background: rgba(148, 163, 184, 0.15);
        color: #cbd5e1;
        border-color: rgba(148, 163, 184, 0.3);
    }}

    .main-title {{
        font-size: 20pt;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #ffffff;
        margin-bottom: 4px;
    }}

    .main-title span {{
        color: #38bdf8;
    }}

    .project-subtitle {{
        font-size: 10pt;
        color: #94a3b8;
        font-weight: 400;
        margin-bottom: 12px;
    }}

    .meta-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 10px;
        background: rgba(15, 23, 42, 0.6);
        padding: 10px 14px;
        border-radius: 6px;
        border: 1px solid #334155;
    }}

    .meta-item {{
        display: flex;
        flex-direction: column;
    }}

    .meta-label {{
        font-size: 7.5pt;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    .meta-value {{
        font-size: 9.5pt;
        font-weight: 700;
        color: #f8fafc;
    }}

    /* Section Titles */
    .section-heading {{
        font-size: 12pt;
        font-weight: 700;
        color: #0f172a;
        margin: 16px 0 10px 0;
        padding-bottom: 4px;
        border-bottom: 2px solid #e2e8f0;
        display: flex;
        align-items: center;
        gap: 8px;
    }}

    .section-heading .num-dot {{
        background: #0284c7;
        color: white;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 8pt;
        font-weight: 800;
    }}

    /* Matrix Table */
    .matrix-table {{
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 20px;
        font-size: 8pt;
    }}

    .matrix-table th {{
        background: #f1f5f9;
        color: #334155;
        font-weight: 700;
        text-align: left;
        padding: 6px 8px;
        border: 1px solid #cbd5e1;
        text-transform: uppercase;
        font-size: 7pt;
        letter-spacing: 0.5px;
    }}

    .matrix-table td {{
        padding: 6px 8px;
        border: 1px solid #e2e8f0;
        vertical-align: middle;
    }}

    .matrix-table tr:nth-child(even) {{
        background: #f8fafc;
    }}

    /* Table Card */
    .table-card {{
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        margin-bottom: 16px;
        background: #ffffff;
        page-break-inside: avoid;
        break-inside: avoid;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}

    .table-card-header {{
        background: #f8fafc;
        border-bottom: 1px solid #cbd5e1;
        padding: 8px 12px;
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
    }}

    .table-title {{
        font-size: 11pt;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 2px;
    }}

    .table-subtitle {{
        font-size: 8pt;
        color: #64748b;
    }}

    .table-header-meta {{
        display: flex;
        gap: 6px;
        align-items: center;
    }}

    .count-badge {{
        background: #e2e8f0;
        color: #334155;
        font-weight: 600;
        font-size: 7.5pt;
        padding: 2px 6px;
        border-radius: 4px;
        white-space: nowrap;
    }}

    .category-badge {{
        background: #e0f2fe;
        color: #0369a1;
        font-weight: 600;
        font-size: 7.5pt;
        padding: 2px 6px;
        border-radius: 4px;
        white-space: nowrap;
    }}

    /* Detailed Data Table */
    .data-table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 8pt;
    }}

    .data-table th {{
        background: #ffffff;
        color: #475569;
        font-weight: 700;
        text-align: left;
        padding: 5px 8px;
        border-bottom: 2px solid #cbd5e1;
        border-top: none;
        border-left: none;
        border-right: none;
        font-size: 7pt;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    .data-table td {{
        padding: 5px 8px;
        border-bottom: 1px solid #f1f5f9;
        border-top: none;
        border-left: none;
        border-right: none;
        vertical-align: middle;
        line-height: 1.35;
    }}

    .data-table tr:last-child td {{
        border-bottom: none;
    }}

    .data-table tr:nth-child(even) {{
        background: #fafbfc;
    }}

    .col-name {{
        font-weight: 700;
        color: #0284c7;
        font-family: 'JetBrains Mono', Consolas, monospace;
        font-size: 8.5pt;
    }}

    .col-type {{
        color: #475569;
        font-family: 'JetBrains Mono', Consolas, monospace;
        font-size: 8pt;
    }}

    .code-pill {{
        background: #f1f5f9;
        color: #0369a1;
        padding: 1px 4px;
        border-radius: 3px;
        font-family: Consolas, monospace;
        font-size: 8pt;
    }}

    /* Badges */
    .badge {{
        display: inline-block;
        padding: 2px 5px;
        font-size: 6.5pt;
        font-weight: 700;
        border-radius: 3px;
        text-transform: uppercase;
        letter-spacing: 0.3px;
        margin-right: 2px;
        line-height: 1.1;
    }}

    .badge-pk {{ background: #f59e0b; color: #ffffff; }}
    .badge-fk {{ background: #4f46e5; color: #ffffff; }}
    .badge-uk {{ background: #10b981; color: #ffffff; }}
    .badge-idx {{ background: #8b5cf6; color: #ffffff; }}
    .badge-nn {{ background: #e11d48; color: #ffffff; }}
    .badge-chk {{ background: #06b6d4; color: #ffffff; }}
    .badge-auto {{ background: #64748b; color: #ffffff; }}
    .badge-null {{ background: #94a3b8; color: #ffffff; }}
    .badge-other {{ background: #64748b; color: #ffffff; }}

    .status-no {{
        color: #e11d48;
        font-weight: 700;
        font-size: 7.5pt;
    }}

    .status-yes {{
        color: #10b981;
        font-weight: 700;
        font-size: 7.5pt;
    }}

    .text-muted {{
        color: #94a3b8;
    }}

    .entity-tag {{
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 2px 5px;
        border-radius: 4px;
        font-size: 7pt;
        color: #475569;
    }}

    .table-card-footer {{
        background: #f8fafc;
        border-top: 1px solid #f1f5f9;
        padding: 5px 12px;
        font-size: 7.5pt;
        color: #64748b;
    }}

    .footer-label {{
        font-weight: 700;
        color: #334155;
    }}

    /* Integrity Rules Box */
    .rules-card {{
        background: #f8fafc;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        padding: 12px 14px;
        margin-top: 10px;
        page-break-inside: avoid;
        break-inside: avoid;
    }}

    .rules-grid {{
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
        margin-top: 8px;
    }}

    .rule-item {{
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 4px;
        padding: 8px 10px;
    }}

    .rule-title {{
        font-weight: 700;
        color: #0f172a;
        font-size: 8.5pt;
        margin-bottom: 2px;
        display: flex;
        align-items: center;
        gap: 5px;
    }}

    .rule-desc {{
        font-size: 7.5pt;
        color: #475569;
        line-height: 1.35;
    }}

    /* Print optimizations */
    @media print {{
        body {{
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }}
        .table-card {{
            page-break-inside: avoid !important;
            break-inside: avoid !important;
        }}
    }}
</style>
</head>
<body>

    <!-- Header / Cover Banner -->
    <div class="header-banner">
        <div class="header-top">
            <div class="pills-container">
                <span class="pill">Database Specification</span>
                <span class="pill pill-secondary">MCA Semester 1 Mini Project</span>
                <span class="pill pill-secondary">3NF Strict Relational Model</span>
            </div>
            <div style="font-size: 8pt; color: #94a3b8;">
                v1.0 &bull; Lossless Document
            </div>
        </div>
        <h1 class="main-title">SkillConnect <span>Data Dictionary</span></h1>
        <div class="project-subtitle">
            Relational Database Schema &amp; Data Dictionary for Peer-to-Peer Student Skill Exchange Platform
        </div>
        <div class="meta-grid">
            <div class="meta-item">
                <span class="meta-label">RDBMS Engine</span>
                <span class="meta-value">SQLite 3 (WAL Mode)</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">ORM Framework</span>
                <span class="meta-value">SQLAlchemy 2.0+ / Flask</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">Schema Coverage</span>
                <span class="meta-value">7 Tables &bull; 54 Attributes</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">Automated Tests</span>
                <span class="meta-value">89 / 89 Test Cases Passed</span>
            </div>
        </div>
    </div>

    <!-- Section 1: Relational Summary Matrix -->
    <div class="section-heading">
        <span class="num-dot">1</span> Relational Schema Summary Matrix
    </div>
    <table class="matrix-table">
        <thead>
            <tr>
                <th style="width: 4%; text-align: center;">#</th>
                <th style="width: 17%;">Table Name</th>
                <th style="width: 16%;">Entity Classification</th>
                <th style="width: 8%;">PK</th>
                <th style="width: 15%;">Foreign Keys</th>
                <th style="width: 18%;">Unique Constraints</th>
                <th style="width: 22%;">System Purpose</th>
            </tr>
        </thead>
        <tbody>
            {rows_matrix}
        </tbody>
    </table>

    <!-- Section 2: Detailed Data Dictionary -->
    <div class="section-heading">
        <span class="num-dot">2</span> Normalized Table Specifications
    </div>

    {sections_html}

    <!-- Section 3: Relational Integrity & Business Rules -->
    <div class="section-heading">
        <span class="num-dot">3</span> Relational Integrity, Cascade &amp; Business Rules
    </div>
    <div class="rules-card">
        <div class="rules-grid">
            <div class="rule-item">
                <div class="rule-title">
                    <span class="badge badge-uk">Constraint</span> Unique Intent Constraint
                </div>
                <div class="rule-desc">
                    <code>UNIQUE(user_id, skill_id, skill_type)</code> on <code>user_skills</code> guarantees a student cannot create duplicate portfolio records for the same skill and intent combination.
                </div>
            </div>
            <div class="rule-item">
                <div class="rule-title">
                    <span class="badge badge-fk">1-to-1</span> Strict Session 1-to-1 Mapping
                </div>
                <div class="rule-desc">
                    <code>UNIQUE(request_id)</code> on <code>exchange_sessions</code> enforces that each accepted proposal generates exactly one scheduled learning meeting.
                </div>
            </div>
            <div class="rule-item">
                <div class="rule-title">
                    <span class="badge badge-chk">Check</span> Star Rating Boundaries &amp; Uniqueness
                </div>
                <div class="rule-desc">
                    <code>CHECK(score BETWEEN 1 AND 5)</code> enforces valid 1-to-5 star ratings, while <code>UNIQUE(session_id, reviewer_id)</code> prevents duplicate evaluations from the same participant.
                </div>
            </div>
            <div class="rule-item">
                <div class="rule-title">
                    <span class="badge badge-nn">Integrity</span> Referential Cascades &amp; Self-Check
                </div>
                <div class="rule-desc">
                    Deleting a <code>User</code> cascades across related skills, proposals, and reviews. Business logic enforces <code>sender_id != receiver_id</code> to forbid self-swaps.
                </div>
            </div>
        </div>
    </div>

    <!-- Print Footer -->
    <div style="margin-top: 18px; padding-top: 10px; border-top: 1px solid #cbd5e1; text-align: center; color: #94a3b8; font-size: 7.5pt;">
        SkillConnect &bull; Peer-to-Peer Student Skill Exchange Platform &bull; Master of Computer Applications (MCA) Semester 1 &bull; Technical Documentation
    </div>

</body>
</html>
"""
    with open(HTML_OUT, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated HTML template at: {HTML_OUT}")

def compile_pdf():
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ]
    browser_exe = None
    for p in chrome_paths:
        if os.path.exists(p):
            browser_exe = p
            break
            
    if not browser_exe:
        print("Error: Neither Chrome nor Edge executable was found.")
        sys.exit(1)
        
    print(f"Compiling PDF using: {browser_exe}")
    cmd = [
        browser_exe,
        "--headless=new",
        "--disable-gpu",
        "--run-all-compositor-stages-before-draw",
        "--no-pdf-header-footer",
        f"--print-to-pdf={PDF_OUT}",
        f"file:///{HTML_OUT.replace(os.sep, '/')}"
    ]
    
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(PDF_OUT) and os.path.getsize(PDF_OUT) > 0:
        size_kb = os.path.getsize(PDF_OUT) / 1024
        print(f"SUCCESS: Created PDF at {PDF_OUT} ({size_kb:.1f} KB)")
    else:
        print("Error generating PDF:", proc.stderr)
        sys.exit(1)

if __name__ == "__main__":
    generate_html()
    compile_pdf()
