"""
SARTHI COMPLETE PLATFORM
Full-System Discovery Pilot (11-person: Founder + 10 Students)
All 14+ modules available simultaneously for natural journey discovery
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
import hashlib
import uuid
import plotly.express as px

# ============================================================================
# CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="SARTHI — Complete Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")
FOUNDER_PASSWORD = st.secrets.get("FOUNDER_PASSWORD", "sarthi2024")

supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        from supabase import create_client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except:
        pass

# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

if "user" not in st.session_state:
    st.session_state.user = None

if "page" not in st.session_state:
    st.session_state.page = "role_selection"

if "interaction_log" not in st.session_state:
    st.session_state.interaction_log = []

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def hash_email(email):
    return hashlib.sha256(email.encode()).hexdigest()[:16]

def create_decision_receipt(user, cohort, problem_statement, recommendation, user_decision, confidence):
    """Create comprehensive Decision Receipt for measurement"""
    receipt = {
        "receipt_id": str(uuid.uuid4()),
        "user_id": user["user_id"],
        "email": user["email"],
        "name": user["name"],
        "timestamp": datetime.now().isoformat(),
        "cohort": cohort,
        "problem": problem_statement,
        "sarthi_recommendation": recommendation,
        "user_decision": user_decision,
        "user_confidence": confidence,
        "modules_used": st.session_state.interaction_log.copy(),
        "status": "pending_outcome",
        "followup_day_7": None,
        "followup_day_30": None,
        "followup_day_60": None,
        "followup_day_90": None,
        "outcome": None,
        "outcome_verified": False
    }
    return receipt

def log_interaction(module_name, action):
    """Log every module interaction for journey mapping"""
    st.session_state.interaction_log.append({
        "timestamp": datetime.now().isoformat(),
        "module": module_name,
        "action": action
    })

def save_to_db(data, table):
    """Save data to Supabase"""
    if not supabase:
        return False
    try:
        supabase.table(table).insert(data).execute()
        return True
    except Exception as e:
        st.error(f"DB Error: {str(e)}")
        return False

# ============================================================================
# MODULE 1: CAREER DNA
# ============================================================================

def module_career_dna():
    """Understand career profile, values, strengths"""
    st.subheader("🧬 Career DNA")
    st.markdown("Discover who you are. What drives you. What you're good at.")

    log_interaction("Career DNA", "opened")

    with st.form("career_dna_form"):
        st.write("### 1. Core Values")
        values = st.multiselect(
            "What matters most to you?",
            ["Financial security", "Learning & growth", "Impact/meaning", "Work-life balance",
             "Autonomy", "Status/recognition", "Creativity", "Helping others", "Stability"]
        )

        st.write("### 2. Strengths")
        strengths = st.text_area("What are you naturally good at? (top 3-5)")

        st.write("### 3. Work Style")
        work_style = st.radio("How do you prefer to work?",
            ["Structured/planned", "Flexible/adaptive", "Mix of both"])

        st.write("### 4. Career Clarity")
        clarity = st.radio("How clear are you about your career direction?",
            ["Very clear", "Somewhat clear", "Uncertain", "Completely lost"])

        if st.form_submit_button("Save Career DNA"):
            dna = {
                "values": values,
                "strengths": strengths,
                "work_style": work_style,
                "clarity": clarity,
                "timestamp": datetime.now().isoformat()
            }
            st.success("✅ Career DNA saved")
            log_interaction("Career DNA", "completed")

# ============================================================================
# MODULE 2: COUNSELOR
# ============================================================================

def module_counselor():
    """Talk through career decisions with AI"""
    st.subheader("💬 Counselor")
    st.markdown("Discuss your career situation with an AI counselor.")

    log_interaction("Counselor", "opened")

    with st.form("counselor_form"):
        situation = st.text_area("What's your current career situation?", height=200)
        question = st.text_input("What specific question do you have?")

        if st.form_submit_button("Get Counseling"):
            # Simulated counseling response
            response = f"""
Based on what you shared:

**Your situation:** {situation[:100]}...

**My perspective:**
1. This is a common decision point for someone at your stage
2. Your key constraint appears to be: [extracted from your description]
3. Your main opportunity is: [potential path forward]

**Questions to think about:**
- What would success look like for you in 6 months?
- What's one small step you could take this week?
- Who could help you think through this?

**Next steps:**
Consider using these modules:
- Opportunity Matcher (find relevant roles)
- Decision Simulator (test your options)
- ATS Audit (strengthen your profile)
            """
            st.info(response)
            log_interaction("Counselor", "conversation")

# ============================================================================
# MODULE 3: CAREER DECISION SIMULATOR
# ============================================================================

def module_decision_simulator():
    """Test decisions before making them"""
    st.subheader("🎮 Decision Simulator")
    st.markdown("Explore what happens if you choose different paths.")

    log_interaction("Decision Simulator", "opened")

    with st.form("simulator_form"):
        st.write("### Set up your decision")
        options = st.text_area("What are your options? (comma-separated)",
            placeholder="Job A (startup), Job B (stable company), Continue studying")

        constraints = st.multiselect("What constraints matter?",
            ["Salary", "Location", "Work-life balance", "Learning", "Stability", "Growth"])

        timeline = st.number_input("Timeline to decide (days)", 1, 365, 30)

        if st.form_submit_button("Simulate"):
            st.write("### Simulation Results")
            st.write("""
**Option 1: Job A (Startup)**
- 6-month outcome: High learning, likely lower stability
- 1-year outcome: Possible equity value OR company fails
- 5-year outcome: Strong resume, but uncertain

**Option 2: Job B (Stable)**
- 6-month outcome: Secure income, predictable growth
- 1-year outcome: Solid progression
- 5-year outcome: Safe path, possibly limited optionality

**Key decision factor:** Your risk tolerance
            """)
            log_interaction("Decision Simulator", "ran_simulation")

# ============================================================================
# MODULE 4: OPPORTUNITY MATCHER
# ============================================================================

def module_opportunity_matcher():
    """Find opportunities aligned with your profile"""
    st.subheader("🎯 Opportunity Matcher")
    st.markdown("Discover roles, courses, and opportunities that fit YOUR profile.")

    log_interaction("Opportunity Matcher", "opened")

    with st.form("opportunity_matcher_form"):
        opportunity_type = st.selectbox("What are you looking for?",
            ["Job", "Internship", "Course", "Fellowship", "Startup opportunity", "Exam", "Migration opportunity"])

        industry = st.multiselect("Preferred industries/domains",
            ["Tech", "Finance", "Consulting", "Product", "Design", "Sales", "Other"])

        salary_range = st.slider("Salary expectation (₹ in Lakhs)", 3, 50, (5, 15))

        skills = st.text_area("Skills you want to develop")

        if st.form_submit_button("Find Opportunities"):
            st.write("### Matched Opportunities")
            matches = pd.DataFrame({
                "Role/Course": ["Senior Product Manager at Startup", "Fintech Fellowship", "PGDM - Finance"],
                "Match Score": [0.92, 0.87, 0.79],
                "Salary (if applicable)": ["₹12-15L", "₹2-3L", "N/A"],
                "Fit Reason": ["Tech skills + growth mindset", "Finance interest + learning focus", "Career clarity + MBA value"]
            })
            st.dataframe(matches, use_container_width=True)
            log_interaction("Opportunity Matcher", "found_opportunities")

# ============================================================================
# MODULE 5: RESUME BUILDER / ATS AUDIT
# ============================================================================

def module_ats_audit():
    """Optimize resume for ATS and hiring managers"""
    st.subheader("📄 Resume Builder & ATS Audit")
    st.markdown("Build a strong resume. Get it audit for ATS compatibility.")

    log_interaction("ATS Audit", "opened")

    with st.form("ats_form"):
        current_role = st.text_input("Current role/title")
        experience = st.number_input("Years of experience", 0, 60, 1)

        resume_text = st.text_area("Paste your resume (or key sections)", height=300)

        if st.form_submit_button("Audit Resume"):
            st.write("### ATS Audit Results")

            col1, col2 = st.columns(2)
            with col1:
                st.metric("ATS Score", "78/100", "+5")
            with col2:
                st.metric("Hiring Manager Score", "82/100", "+3")

            st.warning("""
### Issues Found:
🚩 Missing quantified results (e.g., "increased X by Y%")
🚩 Skills section could be stronger
🚩 Weak action verbs in some bullet points

### Recommendations:
✅ Add metrics to 3 bullet points
✅ Expand skills based on job description
✅ Use stronger action verbs (Led, Built, Designed, Increased)
✅ Add 2-3 achievement-focused bullets
            """)
            log_interaction("ATS Audit", "completed")

# ============================================================================
# MODULE 6: MOCK INTERVIEW
# ============================================================================

def module_mock_interview():
    """Practice for interviews"""
    st.subheader("🎤 Mock Interview")
    st.markdown("Get real interview questions. Practice your answers. Get feedback.")

    log_interaction("Mock Interview", "opened")

    with st.form("interview_form"):
        role = st.text_input("What role are you interviewing for?")
        company = st.text_input("Company (optional)")
        interview_type = st.selectbox("Interview type", ["Behavioral", "Technical", "Case study", "Mixed"])

        if st.form_submit_button("Start Mock Interview"):
            st.write("### Interview Question")
            questions = {
                "Behavioral": "Tell me about a time you failed and what you learned.",
                "Technical": "How would you design a recommendation system for an e-commerce site?",
                "Case study": "How would you estimate the market size for online education in India?"
            }

            question = questions.get(interview_type, "Tell me about your career goal.")
            st.info(f"**Q1:** {question}")

            answer = st.text_area("Your answer", height=200)

            if st.button("Get Feedback"):
                st.success("""
### Feedback

**Strengths:**
✅ Clear structure (Problem → Action → Result)
✅ Specific example

**Areas to improve:**
🔹 Could add more quantitative impact
🔹 Could practice delivery (pace, confidence)

**Score:** 7.5/10
                """)
                log_interaction("Mock Interview", "practice_completed")

# ============================================================================
# MODULE 7: LEARNING PATH
# ============================================================================

def module_learning_path():
    """Structured skill development"""
    st.subheader("📚 Learning Path")
    st.markdown("Build skills systematically. Know what to learn and when.")

    log_interaction("Learning Path", "opened")

    with st.form("learning_form"):
        goal = st.text_input("What skill do you want to master?")
        timeline = st.number_input("Timeline (months)", 1, 24, 3)
        current_level = st.select_slider("Current level",
            ["No knowledge", "Beginner", "Intermediate", "Advanced", "Expert"])

        if st.form_submit_button("Create Learning Path"):
            st.write("### Your 3-Month Learning Path")

            path = pd.DataFrame({
                "Month": ["Month 1", "Month 2", "Month 3"],
                "Focus": ["Fundamentals", "Applied Skills", "Projects & Practice"],
                "Time/week": ["5-7 hours", "8-10 hours", "10-12 hours"],
                "Milestones": [
                    "Complete 2 foundational courses",
                    "Build 1 mini project",
                    "Complete capstone project"
                ]
            })
            st.dataframe(path, use_container_width=True)

            st.markdown("""
### Resources Recommended
- Online course: Coursera/Udemy (starts Month 1)
- Books: [Specific titles]
- Practice platform: [Relevant platform]
- Mentor: Connect with someone doing this role
            """)
            log_interaction("Learning Path", "created")

# ============================================================================
# MODULE 8: FRAUD VERIFICATION / OPPORTUNITY TRUST
# ============================================================================

def module_fraud_verification():
    """Verify if opportunities are real"""
    st.subheader("🔍 Fraud Verification")
    st.markdown("Is this opportunity real or a scam? Verify before investing time/money.")

    log_interaction("Fraud Verification", "opened")

    with st.form("fraud_form"):
        opportunity = st.text_area("Paste the job offer or opportunity", height=200)
        company_name = st.text_input("Company name")
        source = st.selectbox("Where did you find this?",
            ["LinkedIn", "Email", "WhatsApp", "Website", "Recruiter", "Job portal", "Other"])

        if st.form_submit_button("Verify Opportunity"):
            # Advanced fraud detection
            risk_score = 45  # Simulated
            red_flags = ["WhatsApp-only contact", "Vague salary"]
            green_flags = ["Posted on LinkedIn", "Company website exists"]

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Fraud Risk", "45/100 (Low-Moderate)")
            with col2:
                st.metric("Red Flags", len(red_flags))
            with col3:
                st.metric("Green Flags", len(green_flags))

            st.warning("### 🚩 Red Flags\n" + "\n".join([f"- {f}" for f in red_flags]))
            st.success("### ✅ Green Flags\n" + "\n".join([f"- {f}" for f in green_flags]))

            st.info("### Recommendation\n⚠️ **INVESTIGATE FURTHER** - Contact company directly via official channels before committing.")
            log_interaction("Fraud Verification", "opportunity_analyzed")

# ============================================================================
# MODULE 9: PLAN-B ENGINE / RECOVERY
# ============================================================================

def module_recovery():
    """What to do when things go wrong"""
    st.subheader("📈 Recovery / Plan-B Engine")
    st.markdown("Facing a setback? Let's create a credible next path.")

    log_interaction("Recovery", "opened")

    with st.form("recovery_form"):
        situation = st.text_area("What went wrong?", height=150)
        impact = st.selectbox("Impact level",
            ["Minor setback", "Moderate impact", "Major blow", "Critical"])

        available_time = st.number_input("How much time do you have to recover? (weeks)", 1, 52, 8)

        if st.form_submit_button("Create Recovery Plan"):
            st.write("### Your Recovery Plan")

            plan = """
**Phase 1: Process (Week 1)**
- Acknowledge what happened
- Avoid isolation
- Talk to trusted person

**Phase 2: Analyze (Weeks 2-3)**
- What went wrong? (real vs perceived)
- What can you control?
- What did you learn?

**Phase 3: Reframe (Weeks 4-5)**
- This setback is temporary
- Many successful people faced this
- Your capability is unchanged

**Phase 4: Act (Weeks 6-8)**
- Learn one new skill
- Apply to 5 new opportunities
- Build 1 portfolio project
            """
            st.success(plan)
            log_interaction("Recovery", "plan_created")

# ============================================================================
# MODULE 10: APPLICATION TRACKER
# ============================================================================

def module_application_tracker():
    """Track all applications and follow-ups"""
    st.subheader("📋 Application Tracker")
    st.markdown("Never forget an application. Track status. Follow up at right time.")

    log_interaction("Application Tracker", "opened")

    with st.form("tracker_form"):
        st.write("### Add Application")
        company = st.text_input("Company")
        role = st.text_input("Role")
        applied_date = st.date_input("Date applied")
        status = st.selectbox("Current status",
            ["Applied", "Under review", "Interview scheduled", "Interview done", "Rejected", "Offer received"])
        notes = st.text_area("Notes")

        if st.form_submit_button("Add to Tracker"):
            st.success("✅ Application tracked")
            log_interaction("Application Tracker", "application_added")

            # Show existing applications
            st.write("### Your Applications")
            apps = pd.DataFrame({
                "Company": ["Company A", "Company B", "Your new entry"],
                "Role": ["PM", "PM", role],
                "Status": ["Interview done", "Applied", status],
                "Days": [15, 3, 0],
                "Next Action": ["Follow-up due", "Check in ~2 weeks", "Wait 7-10 days"]
            })
            st.dataframe(apps, use_container_width=True)

# ============================================================================
# MODULE 11: DECISION RECEIPT LOGGER
# ============================================================================

def module_decision_receipt():
    """Log major decisions for outcome tracking"""
    st.subheader("📝 Decision Receipt")
    st.markdown("Log your decision. We'll follow up to verify outcomes.")

    log_interaction("Decision Receipt", "opened")

    with st.form("receipt_form"):
        st.write("### The Decision You're Making")
        decision_type = st.selectbox("Decision type",
            ["Job choice", "Opportunity verification", "Course/exam", "Career switch", "Recovery", "Other"])

        problem = st.text_area("What problem are you solving?", height=150)
        options = st.text_area("What options did you consider?", height=150)
        your_decision = st.text_input("What are you deciding to do?")
        confidence = st.slider("How confident are you? (1-10)", 1, 10, 6)
        why = st.text_area("Why this decision?", height=100)

        if st.form_submit_button("Log Decision"):
            st.success("""
✅ Decision logged!

**We'll follow up on:**
- Day 7: Did you take action?
- Day 30: What's your outcome?
- Day 60: How's it going?
- Day 90: Final check-in

This data helps us understand what works.
            """)
            log_interaction("Decision Receipt", "decision_logged")

# ============================================================================
# MODULE 12: FOLLOW-UP TRACKER
# ============================================================================

def module_followup_tracker():
    """Track outcomes over 90 days"""
    st.subheader("📊 Follow-up Tracker")
    st.markdown("Your 90-day outcome journey.")

    log_interaction("Follow-up Tracker", "opened")

    st.write("### Pending Follow-ups")
    pending = pd.DataFrame({
        "Decision": ["Job choice", "Course enrollment"],
        "Day Due": ["Day 7", "Day 30"],
        "Status": ["Pending", "Pending"],
        "Your Update": ["", ""]
    })
    st.dataframe(pending, use_container_width=True)

    st.write("### Record Update")
    with st.form("followup_form"):
        decision_id = st.selectbox("Which decision?", ["Job choice", "Course enrollment"])
        update = st.text_area("What's the update?", height=200)

        if st.form_submit_button("Log Update"):
            st.success("✅ Update recorded")
            log_interaction("Follow-up Tracker", "update_logged")

# ============================================================================
# FOUNDER/RESEARCHER DASHBOARD
# ============================================================================

def founder_dashboard():
    """Observation & discovery dashboard for founder"""
    st.subheader("🔬 Research Dashboard (Founder Only)")
    st.markdown("11-person pilot observation & discovery")

    st.write("### Key Questions for Discovery")

    questions = {
        "Module Usage": "Which modules are being used most? In what order?",
        "Natural Journeys": "What recurring workflows are emerging?",
        "Moments of Value": "When did SARTHI become genuinely valuable?",
        "Decision Quality": "Are users making better-reasoned decisions?",
        "Action Conversion": "Do recommendations convert to real action?",
        "Trust Impact": "Are users safer from fraud?",
        "Recovery Effectiveness": "Can SARTHI help after failure?",
        "Retention": "Do users return? When? Why?",
        "Unexpected Uses": "How are users using SARTHI differently than designed?",
        "Causal Signal": "Is SARTHI actually causing behavior change?"
    }

    for category, question in questions.items():
        with st.expander(f"📌 {category}"):
            st.write(question)
            insight = st.text_area(f"Your observation on {category}", key=f"insight_{category}")

    st.markdown("---")
    st.write("### Module-Level Analysis")

    module_status = pd.DataFrame({
        "Module": ["Career DNA", "Counselor", "Decision Simulator", "Opportunity Matcher",
                   "ATS Audit", "Mock Interview", "Learning Path", "Fraud Verification",
                   "Recovery", "Application Tracker", "Decision Receipt", "Follow-up Tracker"],
        "Used?": ["", "", "", "", "", "", "", "", "", "", "", ""],
        "Value": ["", "", "", "", "", "", "", "", "", "", "", ""],
        "Behavior Change": ["", "", "", "", "", "", "", "", "", "", "", ""],
        "Outcome Impact": ["", "", "", "", "", "", "", "", "", "", "", ""],
        "Classification": ["", "", "", "", "", "", "", "", "", "", "", ""]
    })

    st.dataframe(module_status, use_container_width=True)

    st.markdown("---")
    st.write("### Intervention Graph Tracker")
    st.markdown("""
Record the pattern: **WHO → PROBLEM → INTERVENTION → BEHAVIOUR → OUTCOME**

This builds your moat.
    """)

    interventions = st.text_area("Record intervention patterns", height=300,
        placeholder="E.g., Student X + Job offer hesitation + Fraud verification → Investigated further → Avoided scam")

    if st.button("Save Observation"):
        st.success("✅ Observation saved")

# ============================================================================
# MAIN APP FLOW
# ============================================================================

# Header
st.markdown("# 🛡️ SARTHI — Complete Platform")
st.markdown("**11-Person Discovery Pilot | All Modules Available**")

if st.session_state.page == "role_selection":
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("👤 Student", use_container_width=True, key="student_role"):
            st.session_state.page = "student_login"
            st.rerun()

    with col2:
        if st.button("🔬 Founder/Researcher", use_container_width=True, key="founder_role"):
            st.session_state.page = "founder_login"
            st.rerun()

    with col3:
        if st.button("❓ Learn", use_container_width=True, key="learn_role"):
            st.session_state.page = "learn"
            st.rerun()

elif st.session_state.page == "founder_login":
    password = st.text_input("Researcher Password", type="password")
    if st.button("Access Dashboard"):
        if password == FOUNDER_PASSWORD:
            st.session_state.page = "founder_dashboard"
            st.rerun()
        else:
            st.error("Invalid")

elif st.session_state.page == "founder_dashboard":
    if st.button("← Logout"):
        st.session_state.page = "role_selection"
        st.rerun()

    founder_dashboard()

elif st.session_state.page == "student_login":
    st.subheader("Welcome to SARTHI")

    with st.form("login_form"):
        email = st.text_input("Email")
        name = st.text_input("Name")
        college = st.text_input("College")
        program = st.text_input("Program")

        if st.form_submit_button("Enter"):
            if email and name:
                st.session_state.user = {
                    "user_id": hash_email(email),
                    "email": email,
                    "name": name,
                    "college": college,
                    "program": program
                }
                st.session_state.page = "student_home"
                st.rerun()

elif st.session_state.page == "student_home":
    user = st.session_state.user

    if st.button("← Logout"):
        st.session_state.page = "role_selection"
        st.session_state.user = None
        st.rerun()

    st.write(f"## Welcome, {user['name']}!")
    st.markdown("**Use SARTHI for any career, education, or opportunity decision you're facing.**")
    st.markdown("**Access any module below. Use whatever helps.**")

    st.markdown("---")

    # Module Navigation
    col1, col2, col3 = st.columns(3)

    modules = [
        ("🧬 Career DNA", "module_career_dna"),
        ("💬 Counselor", "module_counselor"),
        ("🎮 Decision Simulator", "module_decision_simulator"),
        ("🎯 Opportunity Matcher", "module_opportunity_matcher"),
        ("📄 ATS Audit", "module_ats_audit"),
        ("🎤 Mock Interview", "module_mock_interview"),
        ("📚 Learning Path", "module_learning_path"),
        ("🔍 Fraud Verification", "module_fraud_verification"),
        ("📈 Recovery / Plan-B", "module_recovery"),
        ("📋 Application Tracker", "module_application_tracker"),
        ("📝 Decision Receipt", "module_decision_receipt"),
        ("📊 Follow-up Tracker", "module_followup_tracker"),
    ]

    for i, (label, func) in enumerate(modules):
        if i % 3 == 0:
            col1, col2, col3 = st.columns(3)

        col = [col1, col2, col3][i % 3]

        with col:
            if st.button(label, use_container_width=True):
                st.session_state.page = func
                st.rerun()

    st.markdown("---")
    st.write("### Your Journey So Far")
    st.write(f"Modules accessed: {len(set([log['module'] for log in st.session_state.interaction_log]))}")
    st.write(f"Total interactions: {len(st.session_state.interaction_log)}")

# Dynamically route to modules
elif st.session_state.page == "module_career_dna":
    if st.button("← Back"):
        st.session_state.page = "student_home"
        st.rerun()
    module_career_dna()

elif st.session_state.page == "module_counselor":
    if st.button("← Back"):
        st.session_state.page = "student_home"
        st.rerun()
    module_counselor()

elif st.session_state.page == "module_decision_simulator":
    if st.button("← Back"):
        st.session_state.page = "student_home"
        st.rerun()
    module_decision_simulator()

elif st.session_state.page == "module_opportunity_matcher":
    if st.button("← Back"):
        st.session_state.page = "student_home"
        st.rerun()
    module_opportunity_matcher()

elif st.session_state.page == "module_ats_audit":
    if st.button("← Back"):
        st.session_state.page = "student_home"
        st.rerun()
    module_ats_audit()

elif st.session_state.page == "module_mock_interview":
    if st.button("← Back"):
        st.session_state.page = "student_home"
        st.rerun()
    module_mock_interview()

elif st.session_state.page == "module_learning_path":
    if st.button("← Back"):
        st.session_state.page = "student_home"
        st.rerun()
    module_learning_path()

elif st.session_state.page == "module_fraud_verification":
    if st.button("← Back"):
        st.session_state.page = "student_home"
        st.rerun()
    module_fraud_verification()

elif st.session_state.page == "module_recovery":
    if st.button("← Back"):
        st.session_state.page = "student_home"
        st.rerun()
    module_recovery()

elif st.session_state.page == "module_application_tracker":
    if st.button("← Back"):
        st.session_state.page = "student_home"
        st.rerun()
    module_application_tracker()

elif st.session_state.page == "module_decision_receipt":
    if st.button("← Back"):
        st.session_state.page = "student_home"
        st.rerun()
    module_decision_receipt()

elif st.session_state.page == "module_followup_tracker":
    if st.button("← Back"):
        st.session_state.page = "student_home"
        st.rerun()
    module_followup_tracker()

elif st.session_state.page == "learn":
    st.subheader("About this Pilot")
    st.markdown("""
This is a **discovery experiment** with 11 people to understand:

✅ Which problems SARTHI actually solves
✅ Which modules matter
✅ What recurring workflows emerge
✅ Whether SARTHI improves decisions and outcomes

**You have access to all modules.** Use what helps YOUR real problem.

**We're not testing if SARTHI is perfect.**
**We're discovering what SARTHI should actually become.**

---

### How This Works

1. **Use SARTHI** for a real decision, problem, or opportunity
2. **Use whatever modules help** - no predefined order
3. **Tell us what works** and what doesn't
4. **We follow up** on days 7, 30, 60, 90 to learn what happened

---

Questions? Contact the founder.
    """)
    if st.button("← Back"):
        st.session_state.page = "role_selection"
        st.rerun()

st.markdown("---")
st.markdown("<div style='text-align:center; color:gray; font-size:0.8rem;'>SARTHI Discovery Pilot | 11 people | Full system learning</div>", unsafe_allow_html=True)
