import streamlit as st

from src.config import STREAMLIT_PAGE_CONFIG, APP_NAME, CLINICIAN_PASSWORD
from src.db import (
    init_db,
    create_case,
    list_cases,
    save_screening_result,
    get_latest_screening,
    save_therapy_plan,
    get_latest_therapy_plan,
    add_progress_log,
    get_progress_history,
    save_dtfe_forecast,
    get_latest_dtfe_forecast,
)
from src.utils import generate_case_id
from src.consent import grant_consent, get_consent_status, require_consent
from src.screening import compute_risk
from src.therapy import generate_therapy_plan, summarize_plan
from src.progress import compute_trend, needs_attention, prepare_dtfe_timeseries
from src.dtfe import run_dtfe

# ============================
# INITIALIZATION
# ============================

st.set_page_config(**STREAMLIT_PAGE_CONFIG)
st.title(APP_NAME)

init_db()

# ============================
# SIDEBAR: CLINICIAN LOGIN
# ============================

st.sidebar.header("Clinician Login")

password = st.sidebar.text_input("Password", type="password")

is_clinician = password == CLINICIAN_PASSWORD

if not is_clinician:
    st.sidebar.warning("Clinician access required.")
    st.stop()

st.sidebar.success("Authenticated")

# ============================
# CASE SELECTION
# ============================

st.header("📁 Case Management")

cases = list_cases()
case_ids = [c["case_id"] for c in cases]

selected_case = st.selectbox(
    "Select existing case",
    [""] + case_ids
)

if st.button("➕ Create New Case"):
    new_case_id = generate_case_id()
    age = st.number_input(
        "Child age (months)",
        min_value=6,
        max_value=72,
        step=1
    )
    create_case(new_case_id, age)
    st.success(f"Case created: {new_case_id}")
    st.experimental_rerun()

if not selected_case:
    st.stop()

st.divider()

# ============================
# CONSENT MANAGEMENT
# ============================

st.header("🛡️ Consent")

consents = get_consent_status(selected_case)

for ctype, granted in consents.items():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(ctype)
    with col2:
        if granted:
            st.success("Granted")
        else:
            if st.button(f"Grant {ctype}"):
                grant_consent(selected_case, ctype)
                st.experimental_rerun()

st.divider()

# ============================
# SCREENING
# ============================

st.header("🧠 Screening (Decision Support)")

require_consent(selected_case, "QUESTIONNAIRE")

with st.form("screening_form"):
    st.subheader("Questionnaire")

    questionnaire = {
        "eye_contact": st.checkbox("Reduced eye contact"),
        "response_to_name": st.checkbox("Does not respond to name"),
        "joint_attention": st.checkbox("Limited joint attention"),
        "gestures": st.checkbox("Limited gestures"),
        "sensory_sensitivity": st.checkbox("Sensory sensitivities"),
        "language_delay": st.checkbox("Language delay"),
    }

    submitted = st.form_submit_button("Run Screening")

if submitted:
    prob, level, evidence = compute_risk(
        {k: int(v) for k, v in questionnaire.items()}
    )
    save_screening_result(selected_case, prob, level, evidence)
    st.success("Screening completed.")

latest_screen = get_latest_screening(selected_case)

if latest_screen:
    st.metric("Risk Level", latest_screen["risk_level"])
    st.json(latest_screen["evidence"])

st.divider()

# ============================
# THERAPY PLANNING
# ============================

st.header("🧩 Therapy Planning")

if latest_screen:
    plan = generate_therapy_plan(
        latest_screen["risk_level"],
        latest_screen["evidence"]
    )

    st.subheader("Proposed Plan")
    st.json(plan)

    if st.button("Approve Therapy Plan"):
        save_therapy_plan(selected_case, plan, approved=True)
        st.success("Therapy plan approved.")

latest_plan = get_latest_therapy_plan(selected_case)
if latest_plan:
    st.subheader("Approved Therapy Summary")
    st.write(summarize_plan(latest_plan))

st.divider()

# ============================
# PROGRESS TRACKING
# ============================

st.header("📈 Weekly Progress Tracking")

require_consent(selected_case, "LONGITUDINAL")

week = st.number_input("Week number", min_value=1, step=1)
score = st.slider("Progress score", 0.0, 100.0, 50.0)
notes = st.text_area("Notes")

if st.button("Add Progress Entry"):
    add_progress_log(selected_case, week, score, notes)
    st.success("Progress logged.")

history = get_progress_history(selected_case)

if len(history) >= 2:
    trend = compute_trend(history)
    st.subheader("Trend Analysis")
    st.json(trend)

    if needs_attention(history):
        st.warning("⚠️ Plateau or regression risk detected.")

st.divider()

# ============================
# DTFE FORECASTING
# ============================

st.header("🔮 Developmental Trajectory Forecasting (DTFE)")

if len(history) >= 4:
    ts = prepare_dtfe_timeseries(history)
    dtfe_result = run_dtfe(ts)

    save_dtfe_forecast(selected_case, dtfe_result)

    st.subheader("DTFE Output")
    st.json(dtfe_result)
else:
    st.info("At least 4 weeks of data required for DTFE.")
