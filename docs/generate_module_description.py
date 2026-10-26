#!/usr/bin/env python3
"""
Generate a high-resolution, publication-quality Module Description Graphic
in both SVG and PNG formats for SkillConnect.
"""
import os
import subprocess
import sys
import html

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SVG_OUT = os.path.join(BASE_DIR, "module_description.svg")
PNG_OUT = os.path.join(BASE_DIR, "module_description.png")

MODULES = [
    {
        "num": "MODULE 01",
        "title": "User Authentication & Profile",
        "accent": "#38bdf8",
        "accent_bg": "rgba(56, 189, 248, 0.15)",
        "accent_border": "rgba(56, 189, 248, 0.4)",
        "badge": "Identity Tier",
        "endpoint": "/auth • /profile",
        "service": "AuthService",
        "models": "User",
        "desc": "Manages student and administrator onboarding, identity verification, access controls, and academic portfolio profiles.",
        "features": [
            "Secure student registration with institutional validation",
            "PBKDF2:SHA256 salted password cryptographic hashing",
            "Flask-Login session management with persistent cookies",
            "Role-Based Access Control (RBAC: Student vs. Admin roles)",
            "Profile customization (college, bio, schedule availability)"
        ],
        "test_status": "100% Tested (14 Unit/Integ Tests)"
    },
    {
        "num": "MODULE 02",
        "title": "Skill Portfolio & Taxonomy",
        "accent": "#818cf8",
        "accent_bg": "rgba(129, 140, 248, 0.15)",
        "accent_border": "rgba(129, 140, 248, 0.4)",
        "badge": "Portfolio Tier",
        "endpoint": "/skills • /skills/add",
        "service": "SkillService",
        "models": "SkillCategory, Skill, UserSkill",
        "desc": "Structures technical and academic skill catalogs into standardized disciplines with bilateral student intent mappings.",
        "features": [
            "8 pre-seeded MCA academic & technical subject categories",
            "Dual-intent mapping: Teach (offering) vs. Learn (seeking)",
            "3-tier proficiency rating (Beginner, Intermediate, Advanced)",
            "Case-insensitive skill deduplication on custom user input",
            "Strict table constraint preventing duplicate user skill intents"
        ],
        "test_status": "100% Tested (19 Unit/Integ Tests)"
    },
    {
        "num": "MODULE 03",
        "title": "Discovery & Matching Engine",
        "accent": "#34d399",
        "accent_bg": "rgba(52, 211, 153, 0.15)",
        "accent_border": "rgba(52, 211, 153, 0.4)",
        "badge": "Algorithm Tier",
        "endpoint": "/matching • /directory",
        "service": "MatchingEngine",
        "models": "User, UserSkill, Skill",
        "desc": "Delivers intelligent discovery and transparent two-way reciprocal compatibility recommendations between peer students.",
        "features": [
            "Global searchable student directory with multi-criteria filters",
            "Deterministic 0–100% two-way reciprocal synergy scoring",
            "Reciprocal Need-Offer matching (40% teach ∩ learn synergy)",
            "Bonus points for category affinity (+10%) & proficiency (+10%)",
            "Itemized compatibility breakdowns and strict self-exclusion"
        ],
        "test_status": "100% Tested (12 Unit/Integ Tests)"
    },
    {
        "num": "MODULE 04",
        "title": "Exchange & Session Lifecycle",
        "accent": "#fbbf24",
        "accent_bg": "rgba(251, 191, 36, 0.15)",
        "accent_border": "rgba(251, 191, 36, 0.4)",
        "badge": "Workflow Tier",
        "endpoint": "/exchanges • /sessions",
        "service": "ExchangeService",
        "models": "ExchangeRequest, ExchangeSession",
        "desc": "Orchestrates bilateral skill swap proposals, proposal status transitions, and scheduled peer learning meetings.",
        "features": [
            "Bilateral proposals with offered and requested skill bindings",
            "Strict validation ensuring sender ≠ receiver (no self-swaps)",
            "4-state proposal machine (pending, accepted, rejected, cancelled)",
            "1-to-1 operational session booking for accepted proposals",
            "Flexible session delivery modes: Online, In-Person, or Hybrid"
        ],
        "test_status": "100% Tested (23 Unit/Integ Tests)"
    },
    {
        "num": "MODULE 05",
        "title": "Rating, Feedback & Dashboard",
        "accent": "#c084fc",
        "accent_bg": "rgba(192, 132, 252, 0.15)",
        "accent_border": "rgba(192, 132, 252, 0.4)",
        "badge": "Analytics Tier",
        "endpoint": "/dashboard • /reviews",
        "service": "RatingService, StatsService",
        "models": "Rating, ExchangeSession, User",
        "desc": "Facilitates mutual peer accountability through post-session evaluations and live performance telemetry dashboards.",
        "features": [
            "Bilateral 1-to-5 star quantitative evaluations with CHECK bound",
            "Qualitative testimonials & written peer learning remarks",
            "Unique constraint (session_id, reviewer_id) prevents duplicates",
            "Real-time computed student average ratings & review counts",
            "Interactive student dashboard powered by Chart.js data feeds"
        ],
        "test_status": "100% Tested (17 Unit/Integ Tests)"
    },
    {
        "num": "MODULE 06",
        "title": "Administration & Governance",
        "accent": "#fb7185",
        "accent_bg": "rgba(251, 113, 133, 0.15)",
        "accent_border": "rgba(251, 113, 133, 0.4)",
        "badge": "Governance Tier",
        "endpoint": "/admin • CLI Tooling",
        "service": "AdminController, CLI Commands",
        "models": "All Database Entities",
        "desc": "Provides administrative control, platform-wide audit metrics, taxonomy curation, and automated system management.",
        "features": [
            "Restricted administrative dashboard with @admin_required RBAC",
            "System-wide telemetry: user counts, active swaps, ratings",
            "Skill taxonomy curation (create, update, view categories)",
            "Platform skill catalog moderation & quality control",
            "Automated CLI management: seed-skills, create-admin, reset-db"
        ],
        "test_status": "100% Tested (CLI & RBAC Tests)"
    }
]

def wrap_text_lines(text, max_chars=54):
    words = text.split()
    lines = []
    current = []
    cur_len = 0
    for w in words:
        if cur_len + len(w) + 1 > max_chars and current:
            lines.append(" ".join(current))
            current = [w]
            cur_len = len(w)
        else:
            current.append(w)
            cur_len += len(w) + 1
    if current:
        lines.append(" ".join(current))
    return lines

def generate_svg():
    width = 1760
    height = 1270
    
    col_w = 540
    col_gap = 30
    start_x = 45
    
    row_h = 495
    start_y = 135
    row_gap = 25
    
    cards_svg = ""
    for idx, m in enumerate(MODULES):
        col_idx = idx % 3
        row_idx = idx // 3
        
        x = start_x + col_idx * (col_w + col_gap)
        y = start_y + row_idx * (row_h + row_gap)
        
        feature_items = ""
        feat_y = 265
        for f in m["features"]:
            f_esc = html.escape(f)
            feature_items += f"""
            <g transform="translate(24, {feat_y})">
              <circle cx="5" cy="5" r="3" fill="{m['accent']}" />
              <text x="16" y="9" font-size="11.5" fill="#e2e8f0" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif">{f_esc}</text>
            </g>
            """
            feat_y += 28
            
        title_esc = html.escape(m['title'])
        endpoint_esc = html.escape(m['endpoint'])
        service_esc = html.escape(m['service'])
        models_esc = html.escape(m['models'])
        badge_esc = html.escape(m['badge'])
        num_esc = html.escape(m['num'])
        test_status_esc = html.escape(m['test_status'])

        desc_lines = wrap_text_lines(m['desc'], max_chars=54)
        desc_tspans = ""
        for line_i, line_text in enumerate(desc_lines):
            dy = "0" if line_i == 0 else "18"
            desc_tspans += f'<tspan x="0" dy="{dy}">{html.escape(line_text)}</tspan>'

        cards_svg += f"""
        <!-- Card {idx+1}: {title_esc} -->
        <g transform="translate({x}, {y})" filter="url(#card-shadow)">
          <!-- Card Base -->
          <rect width="{col_w}" height="{row_h}" rx="12" fill="#1e293b" stroke="{m['accent_border']}" stroke-width="1.5"/>
          
          <!-- Card Header Top Accent Line -->
          <rect width="{col_w}" height="4" rx="2" fill="{m['accent']}"/>
          
          <!-- Header Area -->
          <g transform="translate(24, 26)">
            <!-- Pill and Number -->
            <rect x="0" y="0" width="85" height="22" rx="4" fill="{m['accent_bg']}" stroke="{m['accent']}" stroke-width="1"/>
            <text x="42.5" y="15" text-anchor="middle" font-size="9.5" font-weight="800" fill="{m['accent']}" letter-spacing="0.5">{num_esc}</text>
            
            <rect x="95" y="0" width="105" height="22" rx="4" fill="#0f172a" stroke="#334155" stroke-width="1"/>
            <text x="147.5" y="15" text-anchor="middle" font-size="9.5" font-weight="700" fill="#94a3b8">{badge_esc}</text>
            
            <!-- Title -->
            <text x="0" y="52" font-size="19" font-weight="800" fill="#ffffff" letter-spacing="-0.3">{title_esc}</text>
            
            <!-- Description with clean line wrapping -->
            <text x="0" y="76" font-size="11.5" fill="#94a3b8" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif">
              {desc_tspans}
            </text>
          </g>
          
          <!-- Meta Specs Box -->
          <g transform="translate(24, 146)">
            <rect width="{col_w - 48}" height="76" rx="6" fill="#0f172a" stroke="#334155" stroke-width="1"/>
            
            <g transform="translate(14, 24)">
              <text font-size="8.5" font-weight="700" fill="#64748b" text-transform="uppercase" letter-spacing="0.5">BLUEPRINT / ROUTES</text>
              <text y="18" font-size="11" font-weight="600" fill="{m['accent']}" font-family="'JetBrains Mono', Consolas, monospace">{endpoint_esc}</text>
            </g>
            
            <g transform="translate(250, 24)">
              <text font-size="8.5" font-weight="700" fill="#64748b" text-transform="uppercase" letter-spacing="0.5">SERVICE &amp; LOGIC</text>
              <text y="18" font-size="11" font-weight="600" fill="#38bdf8" font-family="'JetBrains Mono', Consolas, monospace">{service_esc}</text>
            </g>
            
            <g transform="translate(14, 58)">
              <text font-size="8.5" font-weight="700" fill="#64748b" text-transform="uppercase" letter-spacing="0.5">ENTITIES:</text>
              <text x="56" y="0" font-size="10.5" font-weight="500" fill="#cbd5e1" font-family="'JetBrains Mono', Consolas, monospace">{models_esc}</text>
            </g>
          </g>
          
          <!-- Feature Header -->
          <text x="24" y="248" font-size="9" font-weight="800" fill="#94a3b8" text-transform="uppercase" letter-spacing="0.5">CORE CAPABILITIES &amp; FUNCTIONAL LOGIC</text>
          
          <!-- Features List -->
          {feature_items}
          
          <!-- Footer Card Status -->
          <g transform="translate(24, {row_h - 38})">
            <line x1="0" y1="0" x2="{col_w - 48}" y2="0" stroke="#334155" stroke-width="1"/>
            <circle cx="6" cy="20" r="4" fill="#34d399"/>
            <text x="16" y="24" font-size="10" font-weight="700" fill="#34d399">VERIFIED</text>
            <text x="80" y="24" font-size="10.5" fill="#94a3b8">• {test_status_esc}</text>
          </g>
        </g>
        """

    svg_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background:#0b1120; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
  <defs>
    <filter id="card-shadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="8" stdDeviation="10" flood-color="#000000" flood-opacity="0.45"/>
    </filter>
    <linearGradient id="header-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1e293b"/>
      <stop offset="100%" stop-color="#0f172a"/>
    </linearGradient>
    <linearGradient id="title-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38bdf8"/>
      <stop offset="50%" stop-color="#818cf8"/>
      <stop offset="100%" stop-color="#c084fc"/>
    </linearGradient>
  </defs>

  <!-- Background Grid Accent -->
  <g opacity="0.06">
    <pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse">
      <path d="M 30 0 L 0 0 0 30" fill="none" stroke="#94a3b8" stroke-width="0.8"/>
    </pattern>
    <rect width="100%" height="100%" fill="url(#grid)" />
  </g>

  <!-- TOP HEADER BANNER -->
  <g transform="translate(45, 20)">
    <rect width="{width - 90}" height="88" rx="10" fill="url(#header-grad)" stroke="#334155" stroke-width="1.5" filter="url(#card-shadow)"/>
    
    <g transform="translate(28, 22)">
      <rect x="0" y="0" width="270" height="20" rx="4" fill="rgba(56, 189, 248, 0.15)" stroke="#38bdf8" stroke-width="1"/>
      <text x="135" y="14" text-anchor="middle" font-size="8.5" font-weight="800" fill="#38bdf8" letter-spacing="0.5">ARCHITECTURE &amp; MODULE SPECIFICATION</text>
      
      <text y="44" font-size="22" font-weight="800" fill="url(#title-grad)" letter-spacing="-0.5">SkillConnect — System Module Architecture &amp; Descriptions</text>
      <text y="64" font-size="11" font-weight="400" fill="#94a3b8">Comprehensive Specification of the 6 Functional &amp; Governance Modules • Layered MVC with Flask Blueprints, Service Layer &amp; SQLAlchemy ORM</text>
    </g>

    <!-- Header Telemetry Badges -->
    <g transform="translate({width - 490}, 26)">
      <rect x="0" y="0" width="125" height="36" rx="6" fill="#1e293b" stroke="#38bdf8" stroke-width="1"/>
      <text x="62.5" y="15" text-anchor="middle" font-size="8.5" font-weight="700" fill="#38bdf8">ARCHITECTURE</text>
      <text x="62.5" y="29" text-anchor="middle" font-size="11" font-weight="700" fill="#ffffff">Layered MVC</text>

      <rect x="135" y="0" width="125" height="36" rx="6" fill="#1e293b" stroke="#34d399" stroke-width="1"/>
      <text x="197.5" y="15" text-anchor="middle" font-size="8.5" font-weight="700" fill="#34d399">VERIFIED TESTS</text>
      <text x="197.5" y="29" text-anchor="middle" font-size="11" font-weight="700" fill="#ffffff">91 / 91 Passed</text>

      <rect x="270" y="0" width="125" height="36" rx="6" fill="#1e293b" stroke="#c084fc" stroke-width="1"/>
      <text x="332.5" y="15" text-anchor="middle" font-size="8.5" font-weight="700" fill="#c084fc">MODULE COUNT</text>
      <text x="332.5" y="29" text-anchor="middle" font-size="11" font-weight="700" fill="#ffffff">6 Core Modules</text>
    </g>
  </g>

  <!-- MODULE CARDS -->
  {cards_svg}

  <!-- BOTTOM ARCHITECTURE SUMMARY BANNER -->
  <g transform="translate(45, {height - 75})">
    <rect width="{width - 90}" height="55" rx="8" fill="#0f172a" stroke="#334155" stroke-width="1"/>
    
    <g transform="translate(24, 24)">
      <text font-size="9" font-weight="800" fill="#38bdf8" text-transform="uppercase" letter-spacing="0.5">TECHNICAL PIPELINE:</text>
      <text x="150" font-size="11" fill="#cbd5e1">
        Presentation (Jinja2 &amp; Bootstrap 5) <tspan fill="#38bdf8">→</tspan> Controller Tier (Flask Blueprints) <tspan fill="#38bdf8">→</tspan> Business Tier (Service Layer) <tspan fill="#38bdf8">→</tspan> Persistence Tier (SQLAlchemy 3NF on SQLite)
      </text>
    </g>
    
    <g transform="translate({width - 120}, 34)">
      <text text-anchor="end" font-size="10.5" fill="#64748b">SkillConnect • MCA Semester 1 Mini Project • Lossless Technical Graphic</text>
    </g>
  </g>

</svg>
"""
    with open(SVG_OUT, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Generated SVG Module Description: {SVG_OUT}")

def render_png():
    browser_exe = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if not os.path.exists(browser_exe):
        browser_exe = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
        
    cmd = [
        browser_exe,
        "--headless=new",
        "--disable-gpu",
        "--run-all-compositor-stages-before-draw",
        f"--screenshot={PNG_OUT}",
        "--window-size=1760,1270",
        f"file:///{SVG_OUT.replace(os.sep, '/')}"
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
        
    if os.path.exists(PNG_OUT) and os.path.getsize(PNG_OUT) > 0:
        print(f"SUCCESS: Rendered PNG Module Description at: {PNG_OUT} ({os.path.getsize(PNG_OUT):,} bytes)")
    else:
        print("Error rendering PNG:", proc.stderr)

if __name__ == "__main__":
    generate_svg()
    render_png()
