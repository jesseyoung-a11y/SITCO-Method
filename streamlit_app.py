import streamlit as st

st.set_page_config(page_title="SITCO Method", layout="wide")

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
        font-size: 34px;
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
        [
            "Above cloud",
            "Below cloud"
        ]
    )

    vx_15m = st.selectbox(
        "15m VX/VIX status",
        [
            "Above cloud",
            "Mixed / inside cloud",
            "Rolling over / turning up",
            "Below cloud"
        ]
    )
    st.markdown('</div>', unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Confirmation and Entry Inputs")

    sox_status = st.selectbox(
        "SOX status",
        [
            "Weak",
            "Mixed",
            "Strong"
        ]
    )

    es_rejection = st.selectbox(
        "ES rejection quality",
        [
            "Rejecting key level / trend",
            "Chopping at level",
            "Above trend and holding",
            "Forced / anticipatory short"
        ]
    )
    st.markdown('</div>', unsafe_allow_html=True)


def grade_trade(vx_4h, vx_15m, sox_status, es_rejection):
    reasons = []

    # Hard fail conditions
    if sox_status == "Strong":
        return (
            "F",
            "Avoid short",
            "SOX is strong, which does not confirm the short thesis."
        )

    if es_rejection in ["Above trend and holding", "Forced / anticipatory short"]:
        return (
            "F",
            "Avoid short",
            "ES is not giving a clean rejection. The short looks forced or price is still holding above trend."
        )

    # A+ setup
    if (
        vx_4h == "Above cloud"
        and vx_15m == "Above cloud"
        and sox_status == "Weak"
        and es_rejection == "Rejecting key level / trend"
    ):
        return (
            "A+",
            "Best short environment",
            "4H VX/VIX supports the broader short regime, 15m VX/VIX confirms immediate volatility pressure, SOX is weak, and ES is rejecting a key level cleanly."
        )

    # A setup
    if (
        vx_4h == "Above cloud"
        and vx_15m in ["Mixed / inside cloud", "Rolling over / turning up"]
        and sox_status == "Weak"
        and es_rejection == "Rejecting key level / trend"
    ):
        return (
            "A",
            "Strong short setup",
            "4H VX/VIX supports the short thesis, 15m VX/VIX is not perfect but still acceptable, SOX is weak, and ES is rejecting a key level."
        )

    # B setup
    if (
        vx_4h == "Below cloud"
        and vx_15m == "Above cloud"
        and sox_status == "Weak"
        and es_rejection == "Rejecting key level / trend"
    ):
        return (
            "B",
            "Tradable, but less supported",
            "15m VX/VIX is helping the immediate short idea, but the broader 4H regime is not fully aligned. SOX is weak and ES is rejecting well, so the trade is still tradable."
        )

    # C setup
    if (
        vx_4h == "Below cloud"
        and vx_15m == "Below cloud"
        and sox_status == "Weak"
        and es_rejection == "Rejecting key level / trend"
    ):
        return (
            "C",
            "Possible, but weaker short",
            "Both 4H and 15m VX/VIX are below cloud, so volatility is not strongly supporting the short thesis. SOX is weak and ES is rejecting, but follow-through may be slower or less reliable."
        )

    # Mixed / downgrade logic
    if sox_status == "Mixed":
        reasons.append("SOX is only mixed, not fully confirming downside.")
    if vx_4h == "Below cloud":
        reasons.append("4H VX/VIX is below cloud, so the larger regime is not strongly supporting the short.")
    if vx_15m == "Below cloud":
        reasons.append("15m VX/VIX is below cloud, so there is limited immediate volatility support.")
    if vx_15m in ["Mixed / inside cloud", "Rolling over / turning up"]:
        reasons.append("15m VX/VIX is not fully above cloud, so trigger quality is moderate.")
    if es_rejection == "Chopping at level":
        reasons.append("ES is chopping at the level instead of rejecting cleanly.")

    if reasons:
        return (
            "C",
            "Caution / weaker setup",
            " ".join(reasons)
        )

    return (
        "F",
        "Avoid short",
        "Too much conflict is present in the setup. The short does not have enough alignment."
    )


if st.button("Grade Trade Setup"):
    grade, verdict, explanation = grade_trade(vx_4h, vx_15m, sox_status, es_rejection)

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

    m1, m2 = st.columns(2)

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
                <div class="metric-title">Verdict</div>
                <div class="metric-value" style="font-size:24px;">{verdict}</div>
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
            <div class="summary-title">Method Summary</div>
            <div class="summary-text">
                The SITCO Method grades ES short setups by checking the higher timeframe regime first, then the lower timeframe trigger,
                then SOX confirmation, and finally ES rejection quality. Cleaner alignment produces stronger grades.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
