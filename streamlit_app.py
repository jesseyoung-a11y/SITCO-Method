import streamlit as st
import pandas as pd

st.set_page_config(page_title="SITCO Method", layout="wide")

if "trade_log" not in st.session_state:
    st.session_state.trade_log = []

st.markdown("""
<style>
    .stApp {
        background-color: #F5F7FA;
        color: #1F2937;
    }
    .main-title {
        font-size: 42px;
        font-weight: 700;
        color: #1F2937;
        margin-bottom: 6px;
    }
    .subtitle {
        font-size: 18px;
        color: #4B5563;
        margin-bottom: 24px;
    }
    .card {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 14px rgba(31, 41, 55, 0.08);
        margin-bottom: 20px;
    }
    .summary-box {
        background-color: #FFFFFF;
        padding: 22px;
        border-left: 6px solid #1D4ED8;
        border-radius: 14px;
        box-shadow: 0 4px 12px rgba(31, 41, 55, 0.08);
        margin-bottom: 20px;
    }
    .grade-box {
        background-color: #DBEAFE;
        padding: 22px;
        border-left: 6px solid #1E3A8A;
        border-radius: 14px;
        box-shadow: 0 4px 12px rgba(31, 41, 55, 0.08);
        margin-bottom: 20px;
    }
    .summary-title {
        font-size: 22px;
        font-weight: 700;
        color: #1F2937;
        margin-bottom: 8px;
    }
    .summary-text {
        font-size: 16px;
        color: #374151;
        line-height: 1.6;
    }
    .metric-card {
        background-color: #FFFFFF;
        padding: 16px;
        border-radius: 14px;
        box-shadow: 0 4px 12px rgba(31, 41, 55, 0.08);
        text-align: center;
        margin-bottom: 20px;
    }
    .metric-title {
        font-size: 16px;
        color: #6B7280;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 32px;
        font-weight: 700;
        color: #1D4ED8;
    }
    div.stButton > button {
        background-color: #1D4ED8;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.7em 1.4em;
        font-weight: 600;
    }
    div.stButton > button:hover {
        background-color: #1E3A8A;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">SITCO Method</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Trade grading dashboard for ES short setups using VX/VIX, SOX, and ES rejection quality.</div>',
    unsafe_allow_html=True
)

left_col, right_col = st.columns(2)

with left_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Regime and Trigger Inputs")

    vx_4h = st.selectbox(
        "4H VX/VIX status",
        ["Above cloud", "Below cloud"]
    )

    vx_15m = st.selectbox(
        "15m VX/VIX status",
        ["Above cloud", "Mixed / inside cloud", "Rolling over / turning up", "Below cloud"]
    )
    st.markdown('</div>', unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Confirmation and Entry Inputs")

    sox_status = st.selectbox(
        "SOX status",
        ["Weak", "Mixed", "Strong"]
    )

    es_rejection = st.selectbox(
        "ES rejection quality",
        ["Rejecting key level / trend", "Chopping at level", "Above trend and holding", "Forced / anticipatory short"]
    )
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("Screenshot Checklist")
s1 = st.checkbox("4H VX/VIX screenshot captured")
s2 = st.checkbox("15m VX/VIX screenshot captured")
s3 = st.checkbox("SOX screenshot captured")
s4 = st.checkbox("ES setup screenshot captured")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("Trade Journal Notes")
journal_notes = st.text_area("Write your trade notes here", height=150)
st.markdown('</div>', unsafe_allow_html=True)


def grade_trade(vx_4h, vx_15m, sox_status, es_rejection):
    # Hard fail conditions
    if sox_status == "Strong":
        return "F", "Avoid short", "SOX is strong, which does not confirm the short thesis.", 15

    if es_rejection in ["Above trend and holding", "Forced / anticipatory short"]:
        return "F", "Avoid short", "ES is not giving a clean rejection. The short looks forced or price is still holding above trend.", 10

    # A+
    if (
        vx_4h == "Above cloud"
        and vx_15m == "Above cloud"
        and sox_status == "Weak"
        and es_rejection == "Rejecting key level / trend"
    ):
        return "A+", "Best short environment", "4H VX/VIX supports the broader short regime, 15m VX/VIX confirms immediate volatility pressure, SOX is weak, and ES is rejecting a key level cleanly.", 98

    # A
    if (
        vx_4h == "Above cloud"
        and vx_15m in ["Mixed / inside cloud", "Rolling over / turning up"]
        and sox_status == "Weak"
        and es_rejection == "Rejecting key level / trend"
    ):
        return "A", "Strong short setup", "4H VX/VIX supports the short thesis, 15m VX/VIX is not perfect but still acceptable, SOX is weak, and ES is rejecting a key level.", 88

    # B
    if (
        vx_4h == "Below cloud"
        and vx_15m == "Above cloud"
        and sox_status == "Weak"
        and es_rejection == "Rejecting key level / trend"
    ):
        return "B", "Tradable, but less supported", "15m VX/VIX is helping the immediate short idea, but the broader 4H regime is not fully aligned. SOX is weak and ES is rejecting well, so the trade is still tradable.", 75

    # C - your explicit rule
    if (
        vx_4h == "Above cloud"
        and vx_15m == "Below cloud"
        and sox_status == "Weak"
        and es_rejection == "Rejecting key level / trend"
    ):
        return "C", "Possible, but trigger is weak", "The broader 4H regime supports the short thesis, but 15m VX/VIX is below cloud, so the immediate trigger is missing. SOX is weak and ES is rejecting, but follow-through may be less reliable.", 62

    # C
    if (
        vx_4h == "Below cloud"
        and vx_15m == "Below cloud"
        and sox_status == "Weak"
        and es_rejection == "Rejecting key level / trend"
    ):
        return "C", "Possible, but weaker short", "Both 4H and 15m VX/VIX are below cloud, so volatility is not strongly supporting the short thesis. SOX is weak and ES is rejecting, but follow-through may be slower or less reliable.", 55

    # Mixed / fallback logic
    reasons = []
    score = 50

    if vx_4h == "Above cloud":
        score += 15
        reasons.append("4H VX/VIX supports the broader short regime.")
    else:
        reasons.append("4H VX/VIX does not strongly support the broader short regime.")

    if vx_15m == "Above cloud":
        score += 15
        reasons.append("15m VX/VIX supports immediate volatility pressure.")
    elif vx_15m in ["Mixed / inside cloud", "Rolling over / turning up"]:
        score += 8
        reasons.append("15m VX/VIX is somewhat supportive, but not fully confirmed.")
    else:
        reasons.append("15m VX/VIX is below cloud, so immediate support is weak.")

    if sox_status == "Weak":
        score += 10
        reasons.append("SOX is weak and confirms downside pressure.")
    elif sox_status == "Mixed":
        reasons.append("SOX is mixed and only partially confirms downside.")

    if es_rejection == "Rejecting key level / trend":
        score += 10
        reasons.append("ES is rejecting a key level cleanly.")
    elif es_rejection == "Chopping at level":
        reasons.append("ES is chopping instead of rejecting cleanly.")

    if score >= 80:
        grade = "B"
        verdict = "Tradable setup"
    elif score >= 60:
        grade = "C"
        verdict = "Caution / weaker setup"
    else:
        grade = "F"
        verdict = "Avoid short"

    return grade, verdict, " ".join(reasons), score


def take_decision(grade, confidence):
    if grade in ["A+", "A"] and confidence >= 85:
        return "Take", "This setup has strong alignment and meets high-quality short criteria."
    if grade == "B" and confidence >= 70:
        return "Conditional Take", "This setup is tradable, but broader alignment is not perfect. Use caution and tighter selectivity."
    if grade == "C":
        return "No-Take or Small Size Only", "This setup is weaker. Consider passing unless other strong context supports it."
    return "No-Take", "This setup does not have enough alignment to justify a short."


if st.button("Grade Trade Setup"):
    grade, verdict, explanation, confidence = grade_trade(vx_4h, vx_15m, sox_status, es_rejection)
    take_signal, take_reason = take_decision(grade, confidence)

    st.markdown("---")

    st.markdown(
        f"""
        <div class="grade-box">
            <div class="summary-title">Trade Grade</div>
            <div class="summary-text">This setup receives a grade of <strong>{grade}</strong>.</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    m1, m2, m3 = st.columns(3)

    with m1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Grade</div>
                <div class="metric-value">{grade}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with m2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Confidence Score</div>
                <div class="metric-value">{confidence}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with m3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Take / No-Take</div>
                <div class="metric-value" style="font-size:22px;">{take_signal}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        f"""
        <div class="summary-box">
            <div class="summary-title">Verdict</div>
            <div class="summary-text">{verdict}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="summary-box">
            <div class="summary-title">Why</div>
            <div class="summary-text">{explanation}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="summary-box">
            <div class="summary-title">Take / No-Take Reasoning</div>
            <div class="summary-text">{take_reason}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    checklist_complete = all([s1, s2, s3, s4])

    log_entry = {
        "4H VX/VIX": vx_4h,
        "15m VX/VIX": vx_15m,
        "SOX": sox_status,
        "ES Rejection": es_rejection,
        "Grade": grade,
        "Confidence": confidence,
        "Take Signal": take_signal,
        "Checklist Complete": "Yes" if checklist_complete else "No",
        "Journal Notes": journal_notes
    }

    if st.button("Save Trade Log"):
        st.session_state.trade_log.append(log_entry)
        st.success("Trade log saved.")

if st.session_state.trade_log:
    st.markdown("### Saved Trade Log")
    log_df = pd.DataFrame(st.session_state.trade_log)
    st.dataframe(log_df, use_container_width=True)
