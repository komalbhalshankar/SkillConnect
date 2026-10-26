#!/usr/bin/env python3
"""
Generate high-resolution PNG and lossless SVG Data Dictionary images for SkillConnect.
"""
import os
import html
from PIL import Image, ImageDraw, ImageFont

# Define Data Dictionary Data
TABLES = [
    {
        "name": "users",
        "title": "1. users",
        "subtitle": "Stores student and administrator credentials, profiles, academic institution, and role-based access.",
        "constraints_note": "Relationships: 1-N user_skills, sent_requests, received_requests, given_ratings, received_ratings.",
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
        "title": "2. skill_categories",
        "subtitle": "Standardized academic and technical taxonomy groupings for classifying platform skills.",
        "constraints_note": "Relationships: 1-N skills (cascade delete-orphan). Pre-seeded categories: Programming, Database, Web Dev, etc.",
        "columns": [
            ("id", "INTEGER", "PK, AUTOINC", "NO", "None", "Unique category primary identifier"),
            ("name", "VARCHAR(80)", "UNIQUE, NOT NULL", "NO", "None", "Category name (e.g. 'Programming & Tech', 'Database')"),
            ("description", "VARCHAR(255)", "NULLABLE", "YES", "None", "Overview of subjects covered in this category"),
            ("icon", "VARCHAR(50)", "NOT NULL", "NO", "'bi-tag'", "Bootstrap Icons CSS class for UI visual badge"),
            ("created_at", "DATETIME", "NOT NULL", "NO", "UTC_NOW", "Taxonomy creation timestamp (UTC)")
        ]
    },
    {
        "name": "skills",
        "title": "3. skills",
        "subtitle": "Canonical catalogue of predefined and student-proposed skills available for peer exchange.",
        "constraints_note": "Foreign Key: category_id -> skill_categories(id). Case-insensitive deduplication applied on new skills.",
        "columns": [
            ("id", "INTEGER", "PK, AUTOINC", "NO", "None", "Unique skill primary identifier"),
            ("category_id", "INTEGER", "FK, NOT NULL", "NO", "None", "Parent category ID referencing skill_categories(id)"),
            ("name", "VARCHAR(100)", "UNIQUE, INDEX", "NO", "None", "Standardized skill name (e.g. 'Python', 'SQL', 'Figma')"),
            ("description", "VARCHAR(255)", "NULLABLE", "YES", "None", "Summary curriculum or domain details"),
            ("created_at", "DATETIME", "NOT NULL", "NO", "UTC_NOW", "Skill registration timestamp (UTC)")
        ]
    },
    {
        "name": "user_skills",
        "title": "4. user_skills",
        "subtitle": "Junction table mapping student portfolios to skills with teaching/learning intent and proficiency.",
        "constraints_note": "Unique Constraint: uq_user_skill_type(user_id, skill_id, skill_type) prevents duplicate entries per intent.",
        "columns": [
            ("id", "INTEGER", "PK, AUTOINC", "NO", "None", "Unique junction record identifier"),
            ("user_id", "INTEGER", "FK, INDEX", "NO", "None", "Student ID referencing users(id)"),
            ("skill_id", "INTEGER", "FK, INDEX", "NO", "None", "Skill ID referencing skills(id)"),
            ("skill_type", "VARCHAR(10)", "NOT NULL", "NO", "None", "Intent type: 'teach' (offering) or 'learn' (seeking)"),
            ("proficiency", "VARCHAR(20)", "NOT NULL", "NO", "'intermediate'", "Proficiency level: 'beginner', 'intermediate', 'advanced'"),
            ("notes", "VARCHAR(255)", "NULLABLE", "YES", "None", "Custom student notes, target frameworks, or topic focus"),
            ("created_at", "DATETIME", "NOT NULL", "NO", "UTC_NOW", "Record addition timestamp (UTC)"),
            ("updated_at", "DATETIME", "NOT NULL", "NO", "UTC_NOW", "Record last modified timestamp (UTC, onupdate)")
        ]
    },
    {
        "name": "exchange_requests",
        "title": "5. exchange_requests",
        "subtitle": "Bilateral skill swap proposals initiated by one student to another with offered and requested skills.",
        "constraints_note": "Foreign Keys: sender_id, receiver_id -> users(id); offered_skill_id, requested_skill_id -> skills(id).",
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
        "title": "6. exchange_sessions",
        "subtitle": "Scheduled learning meetings originating from accepted exchange requests.",
        "constraints_note": "Unique Constraint: request_id is UNIQUE (1-to-1 relationship with accepted exchange requests).",
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
        "title": "7. ratings",
        "subtitle": "Mutual post-session peer ratings and qualitative reviews following completed sessions.",
        "constraints_note": "Constraints: uq_session_reviewer UNIQUE(session_id, reviewer_id); ck_rating_score_range CHECK(score BETWEEN 1 AND 5).",
        "columns": [
            ("id", "INTEGER", "PK, AUTOINC", "NO", "None", "Unique evaluation record identifier"),
            ("session_id", "INTEGER", "FK, INDEX", "NO", "None", "Completed session ID referencing exchange_sessions(id)"),
            ("reviewer_id", "INTEGER", "FK, INDEX", "NO", "None", "Student submitting review referencing users(id)"),
            ("reviewee_id", "INTEGER", "FK, INDEX", "NO", "None", "Student receiving review referencing users(id)"),
            ("score", "INTEGER", "CHECK 1..5", "NO", "None", "Integer rating between 1 and 5 stars (inclusive)"),
            ("feedback", "TEXT", "NULLABLE", "YES", "None", "Qualitative peer feedback, testimonials & remarks"),
            ("created_at", "DATETIME", "NOT NULL", "NO", "UTC_NOW", "Rating submission timestamp (UTC)")
        ]
    }
]

def generate_svg(output_path):
    width = 1750
    # Calculate SVG height dynamically
    card_spacing = 30
    header_height = 200
    footer_height = 90
    
    table_heights = []
    for t in TABLES:
        h = 80 + 38 + (len(t["columns"]) * 36) + 38
        table_heights.append(h)
        
    total_height = header_height + sum(table_heights) + (len(TABLES) * card_spacing) + footer_height
    
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {total_height}" width="{width}" height="{total_height}">')
    svg.append('''<defs>
      <linearGradient id="headerGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#0f172a" />
        <stop offset="100%" stop-color="#1e293b" />
      </linearGradient>
      <linearGradient id="cardGrad" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stop-color="#ffffff" />
        <stop offset="100%" stop-color="#f8fafc" />
      </linearGradient>
      <filter id="shadow" x="-2%" y="-1%" width="104%" height="106%">
        <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000" flood-opacity="0.08"/>
      </filter>
      <style>
        .font-sans { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; }
        .font-mono { font-family: "Consolas", "Courier New", monospace; }
      </style>
    </defs>''')
    
    # Background
    svg.append(f'<rect width="{width}" height="{total_height}" fill="#f1f5f9"/>')
    
    # Main Header
    svg.append(f'''
    <g transform="translate(40, 30)">
      <rect width="{width - 80}" height="145" rx="14" fill="url(#headerGrad)" filter="url(#shadow)"/>
      <rect x="0" y="0" width="8" height="145" rx="4" fill="#0284c7"/>
      
      <text x="35" y="48" class="font-sans" font-size="28" font-weight="700" fill="#f8fafc" letter-spacing="0.5">SkillConnect — Database Data Dictionary</text>
      <text x="35" y="78" class="font-sans" font-size="15" fill="#94a3b8">Peer-to-Peer Student Skill Exchange Platform • MCA Semester 1 Mini Project • Schema Specification v1.0</text>
      
      <!-- Badges -->
      <g transform="translate(35, 96)">
        <rect x="0" y="0" width="165" height="28" rx="6" fill="#0369a1"/>
        <text x="12" y="19" class="font-sans" font-size="12" font-weight="600" fill="#ffffff">ENGINE: SQLite 3 (3NF)</text>
        
        <rect x="180" y="0" width="185" height="28" rx="6" fill="#047857"/>
        <text x="192" y="19" class="font-sans" font-size="12" font-weight="600" fill="#ffffff">ORM: Flask-SQLAlchemy</text>
        
        <rect x="380" y="0" width="160" height="28" rx="6" fill="#6d28d9"/>
        <text x="392" y="19" class="font-sans" font-size="12" font-weight="600" fill="#ffffff">CORE TABLES: 7 Active</text>
        
        <rect x="555" y="0" width="195" height="28" rx="6" fill="#be123c"/>
        <text x="567" y="19" class="font-sans" font-size="12" font-weight="600" fill="#ffffff">INTEGRITY: 89 Tests Passed</text>
      </g>
    </g>
    ''')
    
    cur_y = 205
    col_x = [60, 270, 460, 680, 780, 930] # x offsets inside table: Field, Type, Constraints, Null, Default, Description
    
    for t in TABLES:
        num_cols = len(t["columns"])
        card_h = 75 + 38 + (num_cols * 36) + 38
        
        svg.append(f'<g transform="translate(40, {cur_y})">')
        # Card container
        svg.append(f'<rect width="{width - 80}" height="{card_h}" rx="12" fill="url(#cardGrad)" stroke="#cbd5e1" stroke-width="1.5" filter="url(#shadow)"/>')
        
        # Card Header Banner
        svg.append(f'''
        <rect width="{width - 80}" height="70" rx="12" fill="#1e293b"/>
        <rect y="60" width="{width - 80}" height="10" fill="#1e293b"/>
        <text x="25" y="33" class="font-mono" font-size="20" font-weight="700" fill="#38bdf8">{t["title"]}</text>
        <text x="25" y="54" class="font-sans" font-size="13" fill="#cbd5e1">{t["subtitle"]}</text>
        ''')
        
        # Column Headers
        th_y = 70
        svg.append(f'''
        <rect y="{th_y}" width="{width - 80}" height="36" fill="#334155"/>
        <text x="{col_x[0]}" y="{th_y + 23}" class="font-sans" font-size="13" font-weight="700" fill="#f8fafc">COLUMN NAME</text>
        <text x="{col_x[1]}" y="{th_y + 23}" class="font-sans" font-size="13" font-weight="700" fill="#f8fafc">DATA TYPE</text>
        <text x="{col_x[2]}" y="{th_y + 23}" class="font-sans" font-size="13" font-weight="700" fill="#f8fafc">CONSTRAINTS / KEYS</text>
        <text x="{col_x[3]}" y="{th_y + 23}" class="font-sans" font-size="13" font-weight="700" fill="#f8fafc">NULLABLE</text>
        <text x="{col_x[4]}" y="{th_y + 23}" class="font-sans" font-size="13" font-weight="700" fill="#f8fafc">DEFAULT</text>
        <text x="{col_x[5]}" y="{th_y + 23}" class="font-sans" font-size="13" font-weight="700" fill="#f8fafc">DESCRIPTION &amp; BUSINESS LOGIC</text>
        ''')
        
        # Rows
        row_y = th_y + 36
        for idx, col in enumerate(t["columns"]):
            c_name, c_type, c_const, c_null, c_def, c_desc = col
            bg_fill = "#ffffff" if idx % 2 == 0 else "#f8fafc"
            
            svg.append(f'<rect y="{row_y}" width="{width - 80}" height="36" fill="{bg_fill}" stroke="#e2e8f0" stroke-width="0.8"/>')
            
            # Column name with badge/color
            svg.append(f'<text x="{col_x[0]}" y="{row_y + 23}" class="font-mono" font-size="14" font-weight="700" fill="#0f172a">{c_name}</text>')
            
            # Type
            svg.append(f'<text x="{col_x[1]}" y="{row_y + 23}" class="font-mono" font-size="13" font-weight="600" fill="#0369a1">{c_type}</text>')
            
            # Constraint badge rendering
            badge_color = "#475569"
            badge_bg = "#f1f5f9"
            if "PK" in c_const:
                badge_bg, badge_color = "#fef3c7", "#b45309"
            elif "FK" in c_const:
                badge_bg, badge_color = "#e0e7ff", "#4338ca"
            elif "UNIQUE" in c_const:
                badge_bg, badge_color = "#dcfce7", "#15803d"
            elif "NOT NULL" in c_const:
                badge_bg, badge_color = "#ffe4e6", "#be123c"
                
            badge_w = max(len(c_const) * 8 + 16, 70)
            svg.append(f'<rect x="{col_x[2] - 5}" y="{row_y + 8}" width="{badge_w}" height="20" rx="4" fill="{badge_bg}"/>')
            svg.append(f'<text x="{col_x[2] + 3}" y="{row_y + 22}" class="font-sans" font-size="11" font-weight="700" fill="{badge_color}">{c_const}</text>')
            
            # Nullable
            null_color = "#15803d" if c_null == "YES" else "#b91c1c"
            svg.append(f'<text x="{col_x[3] + 15}" y="{row_y + 23}" class="font-sans" font-size="13" font-weight="700" fill="{null_color}">{c_null}</text>')
            
            # Default
            def_text = c_def if c_def != "None" else "—"
            svg.append(f'<text x="{col_x[4]}" y="{row_y + 23}" class="font-mono" font-size="12" fill="#64748b">{def_text}</text>')
            
            # Description
            svg.append(f'<text x="{col_x[5]}" y="{row_y + 23}" class="font-sans" font-size="13" fill="#334155">{html.escape(c_desc)}</text>')
            
            row_y += 36
            
        # Footer constraint note
        svg.append(f'''
        <rect y="{row_y}" width="{width - 80}" height="38" rx="0 0 12 12" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="0.8"/>
        <text x="25" y="{row_y + 24}" class="font-sans" font-size="12.5" font-weight="600" fill="#475569">💡 {html.escape(t["constraints_note"])}</text>
        ''')
        
        svg.append('</g>')
        cur_y += card_h + card_spacing
        
    # Page Footer
    svg.append(f'''
    <g transform="translate(40, {cur_y})">
      <rect width="{width - 80}" height="55" rx="10" fill="#1e293b"/>
      <text x="30" y="33" class="font-sans" font-size="13" fill="#94a3b8">SkillConnect Peer Skill Exchange Platform • MCA Semester 1 Project • Comprehensive Database Specification</text>
      <text x="{width - 320}" y="33" class="font-sans" font-size="13" font-weight="600" fill="#38bdf8">Lossless Scalable Vector Graphic (SVG)</text>
    </g>
    ''')
    
    svg.append('</svg>')
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Generated SVG: {output_path} ({os.path.getsize(output_path):,} bytes)")


def generate_png(output_path):
    # Choose font
    font_path_sans = "C:\\Windows\\Fonts\\segoeui.ttf" if os.path.exists("C:\\Windows\\Fonts\\segoeui.ttf") else "C:\\Windows\\Fonts\\arial.ttf"
    font_path_bold = "C:\\Windows\\Fonts\\segoeuib.ttf" if os.path.exists("C:\\Windows\\Fonts\\segoeuib.ttf") else "C:\\Windows\\Fonts\\arialbd.ttf"
    font_path_mono = "C:\\Windows\\Fonts\\consola.ttf" if os.path.exists("C:\\Windows\\Fonts\\consola.ttf") else "C:\\Windows\\Fonts\\cour.ttf"
    
    f_title = ImageFont.truetype(font_path_bold, 32)
    f_subtitle = ImageFont.truetype(font_path_sans, 17)
    f_badge = ImageFont.truetype(font_path_bold, 13)
    f_card_title = ImageFont.truetype(font_path_bold, 22)
    f_card_sub = ImageFont.truetype(font_path_sans, 14)
    f_th = ImageFont.truetype(font_path_bold, 14)
    f_td_name = ImageFont.truetype(font_path_bold, 14)
    f_td_type = ImageFont.truetype(font_path_mono, 13)
    f_td_text = ImageFont.truetype(font_path_sans, 13)
    f_td_mono = ImageFont.truetype(font_path_mono, 12)
    f_note = ImageFont.truetype(font_path_sans, 13)
    f_footer = ImageFont.truetype(font_path_sans, 14)
    
    width = 1750
    header_h = 160
    card_spacing = 30
    footer_h = 80
    
    table_heights = []
    for t in TABLES:
        h = 75 + 38 + (len(t["columns"]) * 36) + 38
        table_heights.append(h)
        
    total_height = 40 + header_h + 30 + sum(table_heights) + (len(TABLES) * card_spacing) + footer_h + 40
    
    img = Image.new("RGB", (width, total_height), color=(241, 245, 249))
    draw = ImageDraw.Draw(img)
    
    # Header card
    draw.rounded_rectangle([40, 30, width - 40, 30 + header_h], radius=14, fill=(15, 23, 42))
    draw.rounded_rectangle([40, 30, 48, 30 + header_h], radius=4, fill=(2, 132, 199))
    
    draw.text((75, 48), "SkillConnect — Database Data Dictionary", font=f_title, fill=(248, 250, 252))
    draw.text((75, 92), "Peer-to-Peer Student Skill Exchange Platform • MCA Semester 1 Mini Project • Schema Specification v1.0", font=f_subtitle, fill=(148, 163, 184))
    
    # Header Badges
    badges = [
        ("ENGINE: SQLite 3 (3NF)", (3, 105, 161)),
        ("ORM: Flask-SQLAlchemy", (4, 120, 87)),
        ("CORE TABLES: 7 Active", (109, 40, 217)),
        ("INTEGRITY: 89 Tests Passed", (190, 18, 60))
    ]
    bx = 75
    for b_text, b_color in badges:
        bw = int(draw.textlength(b_text, font=f_badge)) + 24
        draw.rounded_rectangle([bx, 132, bx + bw, 160], radius=6, fill=b_color)
        draw.text((bx + 12, 138), b_text, font=f_badge, fill=(255, 255, 255))
        bx += bw + 15
        
    cur_y = 30 + header_h + 30
    col_x = [75, 280, 470, 700, 800, 950]
    
    for t in TABLES:
        num_cols = len(t["columns"])
        card_h = 75 + 38 + (num_cols * 36) + 38
        
        # Outer Card
        draw.rounded_rectangle([40, cur_y, width - 40, cur_y + card_h], radius=12, fill=(255, 255, 255), outline=(203, 213, 225), width=2)
        
        # Card Header Banner
        draw.rounded_rectangle([40, cur_y, width - 40, cur_y + 70], radius=12, fill=(30, 41, 59))
        draw.rectangle([40, cur_y + 55, width - 40, cur_y + 70], fill=(30, 41, 59))
        
        draw.text((65, cur_y + 14), t["title"], font=f_card_title, fill=(56, 189, 248))
        draw.text((65, cur_y + 44), t["subtitle"], font=f_card_sub, fill=(203, 213, 225))
        
        # Column Headers
        th_y = cur_y + 70
        draw.rectangle([40, th_y, width - 40, th_y + 36], fill=(51, 65, 85))
        draw.text((col_x[0], th_y + 10), "COLUMN NAME", font=f_th, fill=(248, 250, 252))
        draw.text((col_x[1], th_y + 10), "DATA TYPE", font=f_th, fill=(248, 250, 252))
        draw.text((col_x[2], th_y + 10), "CONSTRAINTS / KEYS", font=f_th, fill=(248, 250, 252))
        draw.text((col_x[3], th_y + 10), "NULLABLE", font=f_th, fill=(248, 250, 252))
        draw.text((col_x[4], th_y + 10), "DEFAULT", font=f_th, fill=(248, 250, 252))
        draw.text((col_x[5], th_y + 10), "DESCRIPTION & BUSINESS LOGIC", font=f_th, fill=(248, 250, 252))
        
        # Rows
        row_y = th_y + 36
        for idx, col in enumerate(t["columns"]):
            c_name, c_type, c_const, c_null, c_def, c_desc = col
            bg_fill = (255, 255, 255) if idx % 2 == 0 else (248, 250, 252)
            
            draw.rectangle([40, row_y, width - 40, row_y + 36], fill=bg_fill, outline=(226, 232, 240), width=1)
            
            # Column Name
            draw.text((col_x[0], row_y + 9), c_name, font=f_td_name, fill=(15, 23, 42))
            
            # Data Type
            draw.text((col_x[1], row_y + 10), c_type, font=f_td_type, fill=(3, 105, 161))
            
            # Constraint Badge
            badge_bg = (241, 245, 249)
            badge_color = (71, 85, 105)
            if "PK" in c_const:
                badge_bg, badge_color = (254, 243, 199), (180, 83, 9)
            elif "FK" in c_const:
                badge_bg, badge_color = (224, 231, 255), (67, 56, 202)
            elif "UNIQUE" in c_const:
                badge_bg, badge_color = (220, 252, 231), (21, 128, 61)
            elif "NOT NULL" in c_const:
                badge_bg, badge_color = (255, 228, 230), (190, 18, 60)
                
            bw = int(draw.textlength(c_const, font=f_badge)) + 14
            draw.rounded_rectangle([col_x[2] - 5, row_y + 7, col_x[2] - 5 + bw, row_y + 28], radius=4, fill=badge_bg)
            draw.text((col_x[2] + 2, row_y + 9), c_const, font=f_badge, fill=badge_color)
            
            # Nullable
            null_color = (21, 128, 61) if c_null == "YES" else (185, 28, 28)
            draw.text((col_x[3] + 15, row_y + 9), c_null, font=f_td_name, fill=null_color)
            
            # Default
            def_text = c_def if c_def != "None" else "—"
            draw.text((col_x[4], row_y + 10), def_text, font=f_td_mono, fill=(100, 116, 139))
            
            # Description
            draw.text((col_x[5], row_y + 10), c_desc, font=f_td_text, fill=(51, 65, 85))
            
            row_y += 36
            
        # Footer constraint
        draw.rounded_rectangle([40, row_y, width - 40, row_y + 38], radius=8, fill=(241, 245, 249))
        draw.text((65, row_y + 11), f"• {t['constraints_note']}", font=f_note, fill=(71, 85, 105))
        
        cur_y += card_h + card_spacing
        
    # Page Footer Banner
    draw.rounded_rectangle([40, cur_y, width - 40, cur_y + 55], radius=10, fill=(30, 41, 59))
    draw.text((65, cur_y + 18), "SkillConnect Peer Skill Exchange Platform • MCA Semester 1 Project • Comprehensive Database Specification", font=f_footer, fill=(148, 163, 184))
    draw.text((width - 340, cur_y + 18), "High-Resolution Master Render (PNG)", font=f_badge, fill=(56, 189, 248))
    
    img.save(output_path, "PNG", quality=95)
    print(f"Generated PNG: {output_path} ({os.path.getsize(output_path):,} bytes, dimensions: {width}x{total_height})")

if __name__ == "__main__":
    docs_dir = os.path.dirname(os.path.abspath(__file__))
    svg_file = os.path.join(docs_dir, "data_dictionary.svg")
    png_file = os.path.join(docs_dir, "data_dictionary.png")
    
    generate_svg(svg_file)
    generate_png(png_file)
