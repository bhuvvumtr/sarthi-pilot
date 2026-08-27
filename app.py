import streamlit as st
import pandas as pd
import json
from datetime import datetime
import hashlib

# ============================================================================
# SARTHI APP - COMPLETE
# ============================================================================

st.set_page_config(page_title="SARTHI", page_icon="🛡️", layout="wide")

# Try to connect to Supabase
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")
INSTRUCTOR_PASSWORD = st.secrets.get("INSTRUCTOR_PASSWORD", "sarthi2024")

supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        from supabase import create_client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except:
        pass

# ============================================================================
# STYLING
# ============================================================================

st.markdown("""
    <style>
    .main { padding: 2rem; }
    .stButton>button { width: 100%; padding: 0.75rem; }
    .metric-card { padding: 1.5rem; border-radius: 0.5rem; background: #f0f2f6; }
    .risk-high { color: #d32f2f; font-weight: bold; }
    .risk-medium { color: #f57c00; font-weight: bold; }
    .risk-low { color: #388e3c; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def hash_email(email):
    return hashlib.sha256(email.encode()).hexdigest()[:16]

def analyze_opportunity(opportunity_text):
    """Analyze job opportunity for fraud risk"""
    risk_score = 0
    red_flags = []
    green_flags = []

    text_lower = opportunity_text.lower()

    # Red flags
    if any(x in text_lower for x in ["upfront", "advance payment", "registration fee"]):
        red_flags.append("🚩 Asks for upfront payment")
        risk_score += 25

    if "guaranteed" in text_lower and ("salary" in text_lower or "income" in text_lower):
        red_flags.append("🚩 Guarantees unrealistic salary")
        risk_score += 15

    if any(x in text_lower for x in ["urgent", "limited time", "hurry"]):
        red_flags.append("🚩 Artificial urgency")
        risk_score += 10

    if any(x in text_lower for x in ["no experience", "anyone can"]):
        red_flags.append("🚩 No experience required")
        risk_score += 15

    if len(opportunity_text) < 50:
        red_flags.append("🚩 Vague job description")
        risk_score += 20

    if "$" not in text_lower and "salary" in text_lower and "rupee" not in text_lower:
        red_flags.append("🚩 No salary mentioned")
        risk_score += 5

    if any(x in text_lower for x in ["whatsapp", "telegram", "signal"]):
        red_flags.append("🚩 Contact via messaging app only")
        risk_score += 10

    # Green flags
    if any(x in text_lower for x in ["linkedin", "naukri", "indeed"]):
        green_flags.append("✅ Posted on legitimate job board")
        risk_score -= 10

    if "@" in opportunity_text and "." in opportunity_text:
        green_flags.append("✅ Professional email address")
        risk_score -= 5

    if "interview" in text_lower or "process" in text_lower:
        green_flags.append("✅ Formal interview process")
        risk_score -= 10

    if "contract" in text_lower or "offer letter" in text_lower:
        green_flags.append("✅ Formal documentation")
        risk_score -= 5

    risk_score = max(0, min(100, risk_score))

    if risk_score >= 70:
        recommendation = "🚫 DO NOT PROCEED"
        confidence = 0.95
    elif risk_score >= 50:
        recommendation = "🔍 INVESTIGATE FURTHER"
        confidence = 0.75
    else:
        recommendation = "✅ LIKELY LEGITIMATE"
        confidence = 0.85

    return {
        "risk_score": risk_score,
        "recommendation": recommendation,
        "confidence": confidence,
        "red_flags": red_flags,
        "green_flags": green_flags
    }

def save_decision(user, cohort, situation, sarthi_recommendation, user_decision, user_confidence):
    """Save decision to Supabase"""
    if not supabase:
        return False

    try:
        decision_data = {
            "user_id": user["user_id"],
            "email": user["email"],
            "name": user["name"],
            "college": user["college"],
            "program": user["program"],
            "cohort": cohort,
            "situation": situation,
            "sarthi_recommendation": json.dumps(sarthi_recommendation),
            "user_decision": user_decision,
            "user_confidence": user_confidence,
            "timestamp": datetime.now().isoformat(),
            "status": "pending_outcome"
        }

        supabase.table("decisions").insert(decision_data).execute()
        return True
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return False

# ============================================================================
# MAIN APP
# ============================================================================

st.title("🛡️ SARTHI — Career Decision Platform")
st.markdown("**Verify opportunities. Avoid scams. Make confident decisions.**")
st.markdown("---")

if "page" not in st.session_state:
    st.session_state.page = "role"

if "user" not in st.session_state:
    st.session_state.user = None

# Role selection
if st.session_state.page == "role":
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👤 I'm a Student", use_container_width=True):
            st.session_state.page = "student_login"
            st.rerun()
    with col2:
        if st.button("👨‍🏫 I'm an Instructor", use_container_width=True):
            st.session_state.page = "instructor_login"
            st.rerun()

# Student signup
elif st.session_state.page == "student_login":
    st.subheader("Student Sign Up")
    with st.form("signup"):
        email = st.text_input("Email")
        name = st.text_input("Full Name")
        college = st.selectbox("College", ["Ashoka School of Finance", "ICT Academy", "Infosys Academy", "Other"])
        program = st.selectbox("Program", ["BBA", "BCom", "B.Tech", "Other"])

        if st.form_submit_button("✅ Start"):
            if email and name:
                st.session_state.user = {
                    "user_id": hash_email(email),
                    "email": email,
                    "name": name,
                    "college": college,
                    "program": program
                }
                st.session_state.page = "decision_type"
                st.rerun()

# Decision type selection
elif st.session_state.page == "decision_type":
    user = st.session_state.user
    st.subheader(f"Welcome, {user['name']}!")
    st.write("What decision do you need help with?")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🎯 Job Choice", use_container_width=True):
            st.session_state.page = "job_choice"
            st.rerun()
    with col2:
        if st.button("🔍 Verify Opportunity", use_container_width=True):
            st.session_state.page = "verify_opportunity"
            st.rerun()
    with col3:
        if st.button("📈 Recovery", use_container_width=True):
            st.session_state.page = "recovery"
            st.rerun()

# Job choice
elif st.session_state.page == "job_choice":
    user = st.session_state.user
    st.subheader("🎯 Job Choice Decision")

    situation = st.text_area("Describe your job situation", height=150)
    confidence = st.slider("Confidence (1-10)?", 1, 10, 5)

    if st.button("Get Recommendation"):
        rec = {"recommendation": "✅ PURSUE", "confidence": 0.8}
        st.success(f"**{rec['recommendation']}** - Confidence: {rec['confidence']:.0%}")

        if st.button("Log Decision"):
            save_decision(user, "job_choice", situation, rec, "pursuing", confidence)
            st.success("✅ Saved!")

# Verify opportunity (fraud detection)
elif st.session_state.page == "verify_opportunity":
    user = st.session_state.user
    st.subheader("🔍 Opportunity Verification")

    opportunity = st.text_area("Paste job offer details", height=200)

    if st.button("Analyze Risk"):
        analysis = analyze_opportunity(opportunity)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Risk Score", f"{analysis['risk_score']}/100")
        with col2:
            st.metric("Confidence", f"{analysis['confidence']:.0%}")
        with col3:
            st.metric("Recommendation", analysis['recommendation'])

        if analysis['red_flags']:
            st.warning("### Red Flags")
            for flag in analysis['red_flags']:
                st.write(flag)

        if analysis['green_flags']:
            st.success("### Green Flags")
            for flag in analysis['green_flags']:
                st.write(flag)

        if st.button("Log Decision"):
            save_decision(user, "opportunity_trust", opportunity, analysis, "verified", 8)
            st.success("✅ Saved!")

# Recovery
elif st.session_state.page == "recovery":
    user = st.session_state.user
    st.subheader("📈 Failure Recovery")

    situation = st.text_area("What setback did you face?", height=150)

    if st.button("Get Plan"):
        st.success("### Recovery Plan\n1. Acknowledge\n2. Learn\n3. Move forward")

        if st.button("Log Decision"):
            save_decision(user, "failure_recovery", situation, {}, "planning", 7)
            st.success("✅ Saved!")

# Instructor dashboard
elif st.session_state.page == "instructor_login":
    password = st.text_input("Instructor Password", type="password")

    if st.button("Access"):
        if password == INSTRUCTOR_PASSWORD:
            st.session_state.page = "dashboard"
            st.rerun()
        else:
            st.error("Invalid")

elif st.session_state.page == "dashboard":
    if st.button("Logout"):
        st.session_state.page = "role"
        st.rerun()

    st.subheader("📊 Instructor Dashboard")

    if supabase:
        try:
            decisions = supabase.table("decisions").select("*").execute().data
            users = set([d.get('user_id') for d in decisions])

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Students", len(users))
            with col2:
                st.metric("Total Decisions", len(decisions))
            with col3:
                cohort_b = [d for d in decisions if d.get('cohort') == 'opportunity_trust']
                st.metric("Fraud Checks", len(cohort_b))
            with col4:
                if cohort_b:
                    avg_risk = sum([json.loads(d.get('sarthi_recommendation', '{}')).get('risk_score', 0) for d in cohort_b]) / len(cohort_b)
                    st.metric("Avg Risk", f"{avg_risk:.0f}")

            if decisions:
                df = pd.DataFrame([{"Name": d.get('name'), "College": d.get('college'), "Cohort": d.get('cohort'), "Time": d.get('timestamp')[:10]} for d in decisions[-50:]])
                st.dataframe(df, use_container_width=True)

                csv = df.to_csv(index=False)
                st.download_button("📥 Download CSV", csv, "decisions.csv", "text/csv")
        except Exception as e:
            st.error(f"DB Error: {str(e)}")
    else:
        st.warning("Database not connected. Add Supabase secrets.")

st.markdown("---")
st.markdown("<div style='text-align:center; color:gray; font-size:0.8rem;'>SARTHI v1.0 | Career Decision Platform</div>", unsafe_allow_html=True)