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
        font-size: 28px;
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
        ["Above cloud", "Mixed / inside cloud", "Below cloud"]
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
st.subheader("Trade Journal Notes")
journal_notes = st.text_area("Write your trade notes here", height=150)
st.markdown('</div>', unsafe_allow_html=True)


def grade_trade(vx_4h, vx_15m, sox_status, es_rejection):
    if sox_status == "Strong":
        return "F", "Avoid short", "SOX is strong, which does not confirm the short thesis.", 15

    if es_rejection in ["Above trend and holding", "Forced / anticipatory short"]:
        return "F", "Avoid short", "ES is not giving a clean rejection. The short looks forced or price is still holding above trend.", 10

    if (
        vx_4h == "Above cloud"
        and vx_15m == "Above cloud"
        and sox_status == "Weak"
        and es_rejection == "Rejecting key level / trend"
    ):
        return "A+", "Best short environment", "4H VX/VIX supports the broader short regime, 15m VX/VIX confirms immediate volatility pressure, SOX is weak, and ES is rejecting a key level cleanly.", 98

    if (
        vx_4h == "Above cloud"
        and vx_15m in ["Mixed / inside cloud", "Rolling over / turning up"]
        and sox_status == "Weak"
        and es_rejection == "Rejecting key level / trend"
    ):
        return "A", "Strong short setup", "4H VX/VIX supports the short thesis, 15m VX/VIX is not perfect but still acceptable, SOX is weak, and ES is rejecting a key level.", 88

    if (
        vx_4h == "Below cloud"
        and vx_15m == "Above cloud"
        and sox_status == "Weak"
        and es_rejection == "Rejecting key level / trend"
    ):
        return "B", "Tradable, but less supported", "15m VX/VIX is helping the immediate short idea, but the broader 4H regime is not fully aligned. SOX is weak and ES is rejecting well, so the trade is still tradable.", 75

    if (
        vx_4h == "Mixed / inside cloud"
        and vx_15m == "Above cloud"
        and sox_status == "Weak"
        and es_rejection == "Rejecting key level / trend"
    ):
        return "B", "Tradable, neutral higher timeframe regime", "4H VX/VIX is mixed inside the cloud, so the broader regime is not fully clear. However, 15m VX/VIX is above cloud, SOX is weak, and ES is rejecting cleanly, which makes the setup tradable but not high quality.", 70

    if (
        vx_4h == "Above cloud"
        and vx_15m == "Below cloud"
        and sox_status == "Weak"
        and es_rejection == "Rejecting key level / trend"
    ):
        return "C", "Possible, but trigger is weak", "The broader 4H regime supports the short thesis, but 15m VX/VIX is below cloud, so the immediate trigger is missing. SOX is weak and ES is rejecting, but follow-through may be less reliable.", 62

    if (
        vx_4h == "Mixed / inside cloud"
        and vx_15m in ["Mixed / inside cloud", "Rolling over / turning up", "Below cloud"]
        and sox_status == "Weak"
        and es_rejection == "Rejecting key level / trend"
    ):
        return "C", "Possible, but broader regime is unclear", "4H VX/VIX is mixed inside the cloud, so the higher timeframe regime is not clearly supporting the short. The setup may still work, but cleaner alignment is missing.", 58

    if (
        vx_4h == "Below cloud"
        and vx_15m == "Below cloud"
        and sox_status == "Weak"
        and es_rejection == "Rejecting key level / trend"
    ):
        return "C", "Possible, but weaker short", "Both 4H and 15m VX/VIX are below cloud, so volatility is not strongly supporting the short thesis. SOX is weak and ES is rejecting, but follow-through may be slower or less reliable.", 55

    reasons = []
    score = 50

    if vx_4h == "Above cloud":
        score += 15
        reasons.append("4H VX/VIX supports the broader short regime.")
    elif vx_4h == "Mixed / inside cloud":
        score += 7
        reasons.append("4H VX/VIX is mixed inside the cloud, so the broader regime is neutral.")
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


def management_playbook(grade):
    if grade == "A+":
        return {
            "Suggested Size": "Full Size",
            "Trade Type": "High-conviction trend short",
            "Patience Level": "High",
            "Tolerance for Chop": "High",
            "Management Style": "Be patient and let the trade work. Avoid reacting to normal noise too early.",
            "Exit Playbook": "Stay in until there is a true direction change. A meaningful loss of 15m VX/VIX strength or ES reclaiming the rejection area is a stronger exit signal.",
            "Breakeven Rule": "Do not move to breakeven too early. Let price get about +10 points in your favor and hold before moving stop to entry."
        }
    if grade == "A":
        return {
            "Suggested Size": "Near Full Size",
            "Trade Type": "Strong short setup",
            "Patience Level": "Medium-High",
            "Tolerance for Chop": "Medium",
            "Management Style": "Give the trade room, but be more alert than with A+ setups.",
            "Exit Playbook": "Hold for follow-through, but tighten attention if 15m VX/VIX loses support or ES starts reclaiming the rejected level.",
            "Breakeven Rule": "Move to breakeven after solid follow-through, not immediately on the first small push."
        }
    if grade == "B":
        return {
            "Suggested Size": "Size Down",
            "Trade Type": "Tactical short / quick scalp",
            "Patience Level": "Medium-Low",
            "Tolerance for Chop": "Low",
            "Management Style": "Treat this as a more tactical trade. If price stalls and does not move in your favor, tighten risk faster.",
            "Exit Playbook": "Take quicker trims. If VX starts to weaken even slightly or ES cannot extend lower, reduce or exit.",
            "Breakeven Rule": "Move stops closer sooner than an A setup. Do not give it too much room if momentum is not there."
        }
    if grade == "C":
        return {
            "Suggested Size": "Very Small Size or Pass",
            "Trade Type": "Scalp only",
            "Patience Level": "Low",
            "Tolerance for Chop": "Very Low",
            "Management Style": "Little tolerance for hesitation. This is not a trade to sit through if it does not move quickly.",
            "Exit Playbook": "Exit fast if there is no immediate downside response. Treat it like a scalp, not a swing idea.",
            "Breakeven Rule": "Use tight management. Consider getting risk reduced quickly if price hesitates."
        }
    return {
        "Suggested Size": "No Size",
        "Trade Type": "No trade",
        "Patience Level": "None",
        "Tolerance for Chop": "None",
        "Management Style": "Stand aside.",
        "Exit Playbook": "No trade should be taken.",
        "Breakeven Rule": "Not applicable."
    }


if st.button("Grade Trade Setup"):
    grade, verdict, explanation, confidence = grade_trade(vx_4h, vx_15m, sox_status, es_rejection)
    take_signal, take_reason = take_decision(grade, confidence)
    playbook = management_playbook(grade)

    st.session_state.current_log_entry = {
        "4H VX/VIX": vx_4h,
        "15m VX/VIX": vx_15m,
        "SOX": sox_status,
        "ES Rejection": es_rejection,
        "Grade": grade,
        "Confidence": confidence,
        "Take Signal": take_signal,
        "Suggested Size": playbook["Suggested Size"],
        "Trade Type": playbook["Trade Type"],
        "Journal Notes": journal_notes
    }

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

    m1, m2, m3, m4 = st.columns(4)

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
                <div class="metric-value" style="font-size:20px;">{take_signal}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with m4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Suggested Size</div>
                <div class="metric-value" style="font-size:20px;">{playbook["Suggested Size"]}</div>
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

    p1, p2 = st.columns(2)

    with p1:
        st.markdown(
            f"""
            <div class="summary-box">
                <div class="summary-title">Management Playbook</div>
                <div class="summary-text">
                    <strong>Trade Type:</strong> {playbook["Trade Type"]}<br><br>
                    <strong>Management Style:</strong> {playbook["Management Style"]}<br><br>
                    <strong>Patience Level:</strong> {playbook["Patience Level"]}<br><br>
                    <strong>Tolerance for Chop:</strong> {playbook["Tolerance for Chop"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with p2:
        st.markdown(
            f"""
            <div class="summary-box">
                <div class="summary-title">Exit and Risk Playbook</div>
                <div class="summary-text">
                    <strong>Exit Playbook:</strong> {playbook["Exit Playbook"]}<br><br>
                    <strong>Breakeven Rule:</strong> {playbook["Breakeven Rule"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

if "current_log_entry" in st.session_state:
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Save Trade Log"):
            st.session_state.trade_log.append(st.session_state.current_log_entry.copy())
            st.success("Trade log saved.")

    with col2:
        if st.session_state.trade_log:
            log_df = pd.DataFrame(st.session_state.trade_log)
            csv = log_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Export Trade Log to CSV",
                data=csv,
                file_name="sitco_trade_log.csv",
                mime="text/csv"
            )

if st.session_state.trade_log:
    st.markdown("### Saved Trade Log")
    log_df = pd.DataFrame(st.session_state.trade_log)
    st.dataframe(log_df, use_container_width=True)