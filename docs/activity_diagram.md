# SkillConnect — UML Activity Diagram Specification
**Academic Level:** MCA Semester 1 — Python Mini Project  
**System Boundary:** `SkillConnect Platform`  
**Pattern:** UML 2.5 Activity Diagrams with Partitions (Swimlanes), Decision Nodes, and State Progression  
**Current Baseline:** Fully implemented & verified (91/91 unit/integration tests passing)

---

## 1. Overview
An **Activity Diagram** describes the dynamic flow of control and data between actors and system components. In SkillConnect, the two primary business workflows modeled are:

1. **Primary Workflow: End-to-End Skill Exchange Lifecycle**  
   From candidate discovery, proposal validation, and recipient decision, to session scheduling, completion, and reciprocal peer review submission.
2. **Algorithmic Workflow: Deterministic Reciprocal Matching Engine**  
   Step-by-step mathematical evaluation of complementary portfolios, scoring rules, proficiency bonuses, and ranking.

- **High-Resolution PNG:** [activity_diagram.png](activity_diagram.png) (Swimlane Activity Diagram)
- **Scalable Vector Graphic:** [activity_diagram.svg](activity_diagram.svg)
- **PlantUML Source:** [activity_diagram.puml](activity_diagram.puml)

![SkillConnect UML Activity Diagram](activity_diagram.png)

---

## 2. Primary Activity Diagram: End-to-End Skill Exchange Lifecycle

This diagram uses **Swimlanes (Partitions)** to clearly separate responsibilities between:
- **Student A (Sender / Learner / Teacher)**
- **SkillConnect System & Database**
- **Student B (Receiver / Partner)**

```mermaid
sequenceDiagram
    autonumber
    actor A as Student A (Sender)
    participant S as SkillConnect System & DB
    actor B as Student B (Receiver)

    Note over A, B: Phase 1: Discovery & Request Formulation
    A->>S: Search or Discover Compatible Peers
    S-->>A: Display Matched Candidates with Compatibility Score (0-100%)
    A->>S: Select Candidate B & Choose Offered & Requested Skills
    A->>S: Submit Exchange Proposal (Message + Skill Pair)

    Note over S: Phase 2: System Validation Checks
    alt Validation Failure (Self-exchange, skill not in Teach/Learn, or Duplicate)
        S-->>A: Flash Error Message (Keep Draft)
    else Validation Success
        S->>S: Insert ExchangeRequest (status = 'pending')
        S-->>B: Notify Incoming Request in Inbox / Dashboard
    end

    Note over B: Phase 3: Recipient Evaluation
    B->>S: Open Request Details & Review Proposed Exchange
    alt Recipient Rejects
        B->>S: Click "Reject"
        S->>S: Update ExchangeRequest (status = 'rejected')
        S-->>A: Request marked Rejected (Terminal State)
    else Recipient Accepts
        B->>S: Click "Accept"
        S->>S: Update ExchangeRequest (status = 'accepted')
        S-->>A: Notify Acceptance (Session Scheduling Unlocked)
    end

    Note over A, B: Phase 4: Session Scheduling
    rect rgb(240, 248, 255)
        Note over A, B: Either Participant Can Schedule
        A->>S: Fill Scheduling Form (Date, Time, Duration, Mode, Meeting Link)
        alt Schedule Invalid (Past date or Duration < 15 or > 300 min)
            S-->>A: Show Form Error
        else Schedule Valid
            S->>S: Insert ExchangeSession (status = 'scheduled')
            S-->>A: Confirmation (Added to Dashboard)
            S-->>B: Notification (Session Confirmed)
        end
    end

    Note over A, B: Phase 5: Execution & Completion
    A->>B: Attend & Conduct Peer Learning Session (Online/In-Person)
    A->>S: Click "Mark as Completed"
    S->>S: Update ExchangeSession (status = 'completed')
    S-->>A: Unlock Post-Session Rating Form
    S-->>B: Unlock Post-Session Rating Form

    Note over A, B: Phase 6: Bilateral Evaluation & Feedback
    par Student A Rates B
        A->>S: Submit Rating (1-5 Stars + Feedback)
        S->>S: Validate: Completed? Participant? Score 1-5? No prior review?
        S->>S: Insert Rating Record
        S->>S: Recalculate Student B's Average Rating
    and Student B Rates A
        B->>S: Submit Rating (1-5 Stars + Feedback)
        S->>S: Validate: Completed? Participant? Score 1-5? No prior review?
        S->>S: Insert Rating Record
        S->>S: Recalculate Student A's Average Rating
    end

    Note over A, B: Terminal State: Exchange Successfully Completed & Metrics Updated
```

---

## 3. Detailed Swimlane Activity Flow (Flowchart Format)

```mermaid
flowchart TD
    %% Initial Node
    StartNode((● Start)) --> A_Browse[Student A: Browse Discovery / Student Search]

    %% Swimlane Partition 1: Student A
    subgraph Swimlane_A ["Partition: Student A (Sender)"]
        A_Browse --> A_Select[Select Compatible Peer Student B]
        A_Select --> A_FillForm[Choose Offered Skill from Teach Portfolio<br/>& Requested Skill from Candidate's Teach Portfolio]
        A_FillForm --> A_Submit[Submit Exchange Proposal]
    end

    %% Swimlane Partition 2: System Validation
    subgraph Swimlane_System ["Partition: SkillConnect Platform & Engine"]
        A_Submit --> Sys_Validate{System: Validate Proposal Prerequisites}
        Sys_Validate -- "Invalid (Self-req / Skill mismatch / Duplicate)" --> Sys_Err[Display Validation Error]
        Sys_Err --> A_FillForm
        
        Sys_Validate -- "Valid" --> Sys_SavePending[Save ExchangeRequest with status='pending']
        Sys_SavePending --> Sys_NotifyB[Dispatch Notification / Update Receiver Inbox]
    end

    %% Swimlane Partition 3: Student B
    subgraph Swimlane_B ["Partition: Student B (Receiver)"]
        Sys_NotifyB --> B_Review[Student B: Review Exchange Request Details]
        B_Review --> B_Decision{Student B Decision}
        
        B_Decision -- "Reject" --> B_RejectAction[Click 'Reject Request']
        B_Decision -- "Accept" --> B_AcceptAction[Click 'Accept Request']
    end

    %% Resolution Paths
    B_RejectAction --> Sys_SetRejected[System: Update ExchangeRequest status='rejected']
    Sys_SetRejected --> End_Rejected((◉ End Rejected))

    B_AcceptAction --> Sys_SetAccepted[System: Update ExchangeRequest status='accepted']
    
    %% Session Scheduling
    Sys_SetAccepted --> AB_Schedule[Either Participant: Fill Session Schedule Form<br/>Date, Time, Duration 15-300m, Mode, Link]
    AB_Schedule --> Sys_ValidSess{System: Validate Date & Duration}
    Sys_ValidSess -- "Past Date / Invalid Duration" --> AB_Schedule
    Sys_ValidSess -- "Valid" --> Sys_SaveSess[Save ExchangeSession with status='scheduled']

    %% Execution
    Sys_SaveSess --> AB_Conduct[Participants: Conduct Peer Learning Session]
    AB_Conduct --> AB_Complete[Participant: Click 'Mark Completed']
    AB_Complete --> Sys_SetCompleted[System: Update ExchangeSession status='completed']

    %% Rating Phase (Parallel / Concurrent)
    Sys_SetCompleted --> Fork_Rating{Fork}
    
    Fork_Rating --> Rate_A[Student A: Submit 1-5 Star Review for B]
    Fork_Rating --> Rate_B[Student B: Submit 1-5 Star Review for A]

    Rate_A --> Sys_SaveRatingA[System: Verify & Save Rating<br/>Recalculate B's Average Rating]
    Rate_B --> Sys_SaveRatingB[System: Verify & Save Rating<br/>Recalculate A's Average Rating]

    Sys_SaveRatingA --> Join_Rating{Join}
    Sys_SaveRatingB --> Join_Rating

    Join_Rating --> Sys_UpdateStats[System: Update Activity Summaries & Badges]
    Sys_UpdateStats --> End_Success((◉ End Completed))
```

---

## 4. Secondary Activity Diagram: Reciprocal Matching Engine Workflow

```mermaid
flowchart TD
    M_Start((● Start Engine)) --> M_Load[Load Active Student A's Teach and Learn Portfolios]
    M_Load --> M_Query[Query All Candidate Students B where B != A and role='student']
    
    M_Query --> M_Loop[Iterate Through Each Candidate B]
    
    subgraph Candidate_Evaluation ["Candidate Evaluation Loop"]
        M_Loop --> M_Fwd["Compute Forward Match Set: M_fwd = L_A ∩ T_B"]
        M_Fwd --> M_Rev["Compute Reverse Match Set: M_rev = T_A ∩ L_B"]
        
        M_Rev --> M_CheckMatch{"|M_fwd| + |M_rev| > 0 ?"}
        
        M_CheckMatch -- "No" --> M_Discard[Discard Candidate - Score = 0]
        
        M_CheckMatch -- "Yes" --> M_Points["Assign Directional Base Points:<br/>• If |M_fwd| > 0: +40 pts<br/>• If |M_rev| > 0: +40 pts"]
        
        M_Points --> M_Cat["Category Bonus Check:<br/>If category overlap exists: +10 pts"]
        
        M_Cat --> M_Prof["Proficiency Differential Check:<br/>If Teacher Level >= Learner Level: +10 pts"]
        
        M_Prof --> M_Score["Compute Total Score:<br/>Score = min(100, S_fwd + S_rev + S_cat + S_prof)"]
        
        M_Score --> M_Collect[Collect Candidate with Itemized Breakdown]
    end

    M_Discard --> M_NextCandidate{More Candidates?}
    M_Collect --> M_NextCandidate
    
    M_NextCandidate -- "Yes" --> M_Loop
    M_NextCandidate -- "No" --> M_Sort[Sort Candidates by Compatibility Score Descending]
    
    M_Sort --> M_Render[Render Recommendations on Student Discovery Dashboard]
    M_Render --> M_End((◉ End Engine))
```

---

## 5. Formal UML Element Mapping for Viva Presentation

| UML Element | Representation in SkillConnect | Function in Workflow |
|---|---|---|
| **Initial Node (`●`)** | User initiates discovery or clicks "Request Exchange". | Starting point of the activity. |
| **Activity States (Rectangles)** | `Browse Directory`, `Fill Form`, `Validate Proposal`, `Conduct Session`. | Unit of work or operation performed by actor or system. |
| **Partitions / Swimlanes** | `Student A`, `SkillConnect System`, `Student B`. | Clarifies who owns each action. |
| **Decision Nodes (Diamonds)** | `Valid Proposal?`, `Recipient Accept/Reject?`, `Date Valid?`. | Evaluates boolean guard conditions to branch execution. |
| **Fork Node (Horizontal Bar)** | After session marked `completed`. | Splits single control flow into concurrent paths (both users can rate independently). |
| **Join Node (Horizontal Bar)** | Synchronizes independent rating submissions. | Merges parallel streams before final profile and dashboard metrics recalculation. |
| **Final State Node (`◉`)** | Exchange completed and rated, or request rejected. | Terminates the activity lifecycle. |
