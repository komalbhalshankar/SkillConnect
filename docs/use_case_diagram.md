# SkillConnect — UML Use Case Diagram Specification
**Academic Level:** MCA Semester 1 — Python Mini Project  
**System Boundary:** `SkillConnect System`  
**Current Status:** Phase 4 Verified Baseline (Modules 1, 2, 3, and 4 fully implemented and tested)

---

## 1. Overview
This UML Use Case Diagram models the functional interactions between the system actors and the **SkillConnect** platform. It uses clean, standard UML notation without unnecessary numbering prefixes.

- **Visual Vector Diagram:** [use_case_diagram.svg](use_case_diagram.svg)
- **PlantUML Source:** [use_case_diagram.puml](use_case_diagram.puml)
- **Mermaid Source:** [use_case_diagram.mmd](use_case_diagram.mmd)

```mermaid
flowchart LR
    %% Actors
    Student["fa:fa-user-graduate Student<br/>&lt;&lt;Primary Actor&gt;&gt;"]
    Admin["fa:fa-user-shield Administrator<br/>&lt;&lt;Secondary Actor&gt;&gt;"]

    subgraph SkillConnect ["System Boundary: SkillConnect Platform"]
        %% Module 1
        UC_Reg(["Register Account"])
        UC_Auth(["Log In / Log Out"])
        UC_Prof(["View & Update Profile"])

        %% Module 2
        UC_ManageSkills(["Manage Skills (Add, Edit, Remove)"])
        UC_SkillDetails(["Specify Skill Type & Proficiency"])

        %% Module 3
        UC_Search(["Search & Filter Students"])
        UC_ViewProfile(["View Student Profile"])
        UC_Discover(["Discover Compatible Partners"])
        UC_CalculateScore(["Calculate Compatibility Score & Matched Skills"])

        %% Module 4
        UC_SendRequest(["Send Exchange Request"])
        UC_RespondRequest(["Respond to Request (Accept / Reject)"])
        UC_History(["View Exchange History"])
        UC_Schedule(["Schedule Learning Session"])
        UC_SessionDetails(["View Session Details"])
        UC_CompleteSession(["Complete or Cancel Session"])

        %% Module 5
        UC_Rate(["Rate Completed Exchange"])
        UC_Feedback(["Submit Written Feedback"])
        UC_Dashboard(["View Dashboard & Activity Summaries"])

        %% Administration
        UC_AdminLogin(["Log In as Administrator"])
        UC_AdminPortal(["Access Protected Admin Portal"])
        UC_AdminStats(["View Platform Statistics"])
        UC_ManageTaxonomy(["Manage Skill Categories & Skills"])
    end

    %% Student Connections
    Student --> UC_Reg
    Student --> UC_Auth
    Student --> UC_Prof
    Student --> UC_ManageSkills
    Student --> UC_Search
    Student --> UC_ViewProfile
    Student --> UC_Discover
    Student --> UC_SendRequest
    Student --> UC_RespondRequest
    Student --> UC_History
    Student --> UC_Schedule
    Student --> UC_SessionDetails
    Student --> UC_CompleteSession
    Student --> UC_Rate
    Student --> UC_Dashboard

    %% Include / Extend Connections
    UC_ManageSkills -.->|&lt;&lt;include&gt;&gt;| UC_SkillDetails
    UC_Discover -.->|&lt;&lt;include&gt;&gt;| UC_CalculateScore
    UC_Rate -.->|&lt;&lt;include&gt;&gt;| UC_Feedback
    UC_Schedule -.->|&lt;&lt;extend&gt;&gt;| UC_RespondRequest
    UC_Rate -.->|&lt;&lt;extend&gt;&gt;| UC_CompleteSession

    %% Admin Connections
    Admin --> UC_AdminLogin
    Admin --> UC_AdminPortal
    Admin --> UC_AdminStats
    Admin --> UC_ManageTaxonomy
    UC_AdminPortal -.->|&lt;&lt;include&gt;&gt;| UC_AdminLogin
    UC_AdminStats -.->|&lt;&lt;include&gt;&gt;| UC_AdminPortal
    UC_ManageTaxonomy -.->|&lt;&lt;include&gt;&gt;| UC_AdminPortal
```

---

## 2. Actors Description

1. **Student Actor (Primary Actor):**
   The registered peer learner/teacher. Every student can declare skills to teach and skills to learn under a unified profile, search peers, discover bilateral matches, send requests, schedule sessions, and rate peers.
2. **Administrator Actor (Secondary Actor):**
   The college department coordinator or system moderator. Responsible for role-protected oversight, platform usage statistics, and curating official skill categories and skills.

---

## 3. Use Case Descriptions & Implementation Status

| Module | Use Case Name | Actor | Description | Target Phase & Status |
| :--- | :--- | :--- | :--- | :---: |
| **Authentication & Profile** | Register Account | Student | Creates account with name, email, password, and college. | **Phase 2 (Implemented & Tested)** |
| | Log In / Log Out | Student / Admin | Authenticates session via Flask-Login. | **Phase 2 (Implemented & Tested)** |
| | View & Update Profile | Student | Manages bio, college, and availability. | **Phase 2 (Implemented & Tested)** |
| **Skill Management** | Manage Skills | Student | Adds, edits, or deletes skills in personal portfolio. | **Phase 3 (Implemented & Tested)** |
| | Specify Skill Type & Proficiency | Student | *&lt;&lt;include&gt;&gt;* Defines Teach/Learn intent and level. | **Phase 3 (Implemented & Tested)** |
| **Discovery & Matching** | Search & Filter Students | Student | Searches peers by name, category, or proficiency. | **Phase 3 (Implemented & Tested)** |
| | View Student Profile | Student | Inspects a peer's skills, bio, and compatibility overview. | **Phase 3 (Implemented & Tested)** |
| | Discover Compatible Partners | Student | Triggers the rule-based matching engine. | **Phase 3 (Implemented & Tested)** |
| | Calculate Compatibility Score | Student | *&lt;&lt;include&gt;&gt;* Computes 0–100% score and matched skills. | **Phase 3 (Implemented & Tested)** |
| **Exchange & Session** | Send Exchange Request | Student | Proposes a skill exchange to another student. | **Phase 4 (Implemented & Tested)** |
| | Respond to Request | Student | Accepts or rejects incoming requests. | **Phase 4 (Implemented & Tested)** |
| | View Exchange History | Student | Tracks status of incoming and outgoing requests. | **Phase 4 (Implemented & Tested)** |
| | Schedule Learning Session | Student | *&lt;&lt;extend&gt;&gt;* Schedules accepted exchange meetings. | **Phase 4 (Implemented & Tested)** |
| | View Session Details | Student | Reviews meeting link/location and agenda notes. | **Phase 4 (Implemented & Tested)** |
| | Complete or Cancel Session | Student | Concludes, cancels, or reschedules sessions. | **Phase 4 (Implemented & Tested)** |
| **Rating & Dashboard** | Rate Completed Exchange | Student | *&lt;&lt;extend&gt;&gt;* Evaluates completed sessions (1–5 stars). | *Phase 5 (Planned)* |
| | Submit Written Feedback | Student | *&lt;&lt;include&gt;&gt;* Submits review comments. | *Phase 5 (Planned)* |
| | View Dashboard & Analytics | Student | Displays summaries and Chart.js activity charts. | *Phase 5 (Planned)* |
| **Administration** | Log In as Administrator | Admin | Authenticates as admin. | **Phase 2 (Implemented & Tested)** |
| | Access Admin Portal | Admin | Role-protected admin dashboard. | **Phase 2 (Implemented & Tested)** |
| | View Platform Statistics | Admin | Reviews platform-wide usage metrics. | *Phase 5 (Planned)* |
| | Manage Categories & Skills | Admin | Curates official categories and skills taxonomy. | **Phase 3 (Implemented & Tested)** |
