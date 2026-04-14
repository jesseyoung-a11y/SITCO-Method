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
       padding: 22px;
       border-radius: 14px;
       box-shadow: 0 4px 12px rgba(31, 41, 55, 0.08);
       margin-bottom: 20px;
       color: white;
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


GRADE_COLORS = {
    "A+": "#16A34A",
    "A": "#16A34A",
    "B": "#F59E0B",
    "C": "#DC2626",
    "D": "#DC2626",
    "F": "#DC2626",
}


GRADE_TO_CONFIDENCE = {
    "A+": 96,
    "A": 88,
    "B": 74,
    "C": 58,
    "D": 40,
    "F": 20,
}


SHORT_RULES = {
    "A+": {
        "stop": "5-point hard stop",
        "size": "Full size",
        "framework": "Give room, trust thesis, exit early only if confirmation truly breaks.",
        "management": "Allow normal noise. Can hold through minor pops if SOX / VX / VIX still agree.",
        "time_rule": "Can give it normal time to work. Do not overreact to early noise if internals still agree.",
    },
    "A": {
        "stop": "4-point hard stop",
        "size": "Moderate size or near full size",
        "framework": "Needs to work reasonably soon.",
        "management": "Less tolerance for chop than A+. If no downside progress soon, tighten mentally.",
        "time_rule": "Should start showing downside progress reasonably soon.",
    },
    "B": {
        "stop": "4-point hard stop, sometimes 5 only if structure truly needs it",
        "size": "Reduced size",
        "framework": "Needs to work almost immediately, or reduce risk.",
        "management": "Smaller size + faster proof requirement. If price stalls or VX flips, scratch, cut partial, or tighten aggressively.",
        "time_rule": "Must work quickly. If it stalls, reduce risk fast.",
    },
    "C": {
        "stop": "No trade preferred",
        "size": "Very small size or pass",
        "framework": "Weak short setup. Usually pass.",
        "management": "Little tolerance for hesitation. Not a trade to sit through.",
        "time_rule": "No patience. This is usually a pass.",
    },
    "D": {
        "stop": "Avoid",
        "size": "No size",
        "framework": "Poor short setup.",
        "management": "Stand aside and wait for better alignment.",
        "time_rule": "Pass.",
    },
    "F": {
        "stop": "Do not short",
        "size": "No size",
        "framework": "Short thesis is invalid.",
        "management": "Look for long conditions or stay out.",
        "time_rule": "Pass.",
    },
}


LONG_RULES = {
    "A+": {
        "stop": "5-point hard stop",
        "size": "Full size",
        "framework": "Give room, trust thesis, exit early only if confirmation truly breaks.",
        "management": "Allow normal noise. Can hold through minor dips if internals still agree.",
        "time_rule": "Can give it normal time to work. Do not overreact to early noise if internals still agree.",
    },
    "A": {
        "stop": "4-point hard stop",
        "size": "Moderate size or near full size",
        "framework": "Needs to work reasonably soon.",
        "management": "Less tolerance for chop than A+. If no upside progress soon, tighten mentally.",
        "time_rule": "Should start showing upside progress reasonably soon.",
    },
    "B": {
        "stop": "4-point hard stop, sometimes 5 only if structure truly needs it",
        "size": "Reduced size",
        "framework": "Needs to work almost immediately, or reduce risk.",
        "management": "Smaller size + faster proof requirement. If price stalls or internals flip, scratch, cut partial, or tighten aggressively.",
        "time_rule": "Must work quickly. If it stalls, reduce risk fast.",
    },
    "C": {
        "stop": "No trade preferred",
        "size": "Very small size or pass",
        "framework": "Weak long setup. Usually pass.",
        "management": "Little tolerance for hesitation. Not a trade to sit through.",
        "time_rule": "No patience. This is usually a pass.",
    },
    "D": {
        "stop": "Avoid",
        "size": "No size",
        "framework": "Poor long setup.",
        "management": "Stand aside and wait for better alignment.",
        "time_rule": "Pass.",
    },
    "F": {
        "stop": "Do not go long",
        "size": "No size",
        "framework": "Long thesis is invalid.",
        "management": "Look for short conditions or stay out.",
        "time_rule": "Pass.",
    },
}


def get_best_side(short_grade, long_grade):
    short_conf = GRADE_TO_CONFIDENCE[short_grade]
    long_conf = GRADE_TO_CONFIDENCE[long_grade]

    if short_conf > long_conf:
        strength = "Strong" if short_conf - long_conf >= 20 else "Moderate"
        return "Short", strength
    if long_conf > short_conf:
        strength = "Strong" if long_conf - short_conf >= 20 else "Moderate"
        return "Long", strength
    return "Balanced / No Clear Edge", "Neutral"



def get_downgrade_reasons(side, vx_4h, vx_15m, sox_status, es_behavior, price_stalling, vx_flipping):
    reasons = []

    if side == "Short":
        if sox_status != "Weak":
            reasons.append("SOX is not weak enough for a clean short thesis")
        if vx_4h != "Above cloud":
            reasons.append("4H VX/VIX is not fully supporting the broader short regime")
        if vx_15m not in ["Above cloud", "Rolling over / turning up"]:
            reasons.append("15m VX/VIX is not strongly confirming immediate downside pressure")
        if es_behavior != "Rejecting key level / trend":
            reasons.append("ES is not rejecting trend cleanly")
        if price_stalling:
            reasons.append("price is stalling instead of moving down")
        if vx_flipping:
            reasons.append("VX / VIX is flipping against the short thesis")
        if not reasons:
            reasons.append("A stronger SOX reversal, weaker VX confirmation, or ES reclaiming trend would downgrade the short")
    else:
        if sox_status != "Strong":
            reasons.append("SOX is not strong enough for a clean long thesis")
        if vx_4h != "Below cloud":
            reasons.append("4H VX/VIX is not fully supporting the broader long regime")
        if vx_15m != "Below cloud":
            reasons.append("15m VX/VIX is not strongly confirming immediate long conditions")
        if es_behavior != "Above trend and holding":
            reasons.append("ES is not holding above trend cleanly")
        if price_stalling:
            reasons.append("price is stalling instead of moving up")
        if vx_flipping:
            reasons.append("VX / VIX pressure is rising against the long thesis")
        if not reasons:
            reasons.append("Weaker SOX strength, rising VX pressure, or loss of trend support would downgrade the long")

    return reasons



def get_pass_reason(side, grade):
    if grade in ["A+", "A", "B"]:
        return "This side is still tradable if execution is clean and management matches the grade."

    if side == "Short":
        if grade == "C":
            return "Pass or use very small size because the short setup is only partially aligned and follow-through may be unreliable."
        if grade == "D":
            return "Pass because too many short conditions are weak or mixed."
        return "Pass because the short thesis is invalid or strongly opposed by the current inputs."

    if grade == "C":
        return "Pass or use very small size because the long setup is only partially aligned and follow-through may be unreliable."
    if grade == "D":
        return "Pass because too many long conditions are weak or mixed."
    return "Pass because the long thesis is invalid or strongly opposed by the current inputs."


st.markdown('<div class="main-title">SITCO Method</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Trade grading dashboard for long and short MES / ES setups using VX/VIX, SOX, and trend behavior.</div>',
    unsafe_allow_html=True,
)


left_col, right_col = st.columns(2)


with left_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Regime Inputs")

    vx_4h = st.selectbox(
        "4H VX/VIX status",
        ["Above cloud", "Mixed / inside cloud", "Below cloud"],
    )

    vx_15m = st.selectbox(
        "15m VX/VIX status",
        ["Above cloud", "Mixed / inside cloud", "Rolling over / turning up", "Below cloud"],
    )

    sox_status = st.selectbox(
        "SOX status",
        ["Weak", "Mixed", "Strong"],
    )
    st.markdown('</div>', unsafe_allow_html=True)


with right_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Price Action Inputs")

    es_behavior = st.selectbox(
        "ES trend behavior",
        ["Rejecting key level / trend", "Chopping at level", "Above trend and holding", "Forced / anticipatory entry"],
    )

    price_stalling = st.checkbox("Price is stalling / not moving in desired direction")
    vx_flipping = st.checkbox("VX / VIX is flipping against thesis")
    st.markdown('</div>', unsafe_allow_html=True)


st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("Trade Journal Notes")
journal_notes = st.text_area("Write your trade notes here", height=150)
st.markdown('</div>', unsafe_allow_html=True)



def score_short_trade(vx_4h, vx_15m, sox_status, es_behavior, price_stalling, vx_flipping):
    score = 0
    reasons = []

    if vx_4h == "Above cloud":
        score += 2
        reasons.append("4H VX/VIX supports the broader short regime")
    elif vx_4h == "Mixed / inside cloud":
        score += 1
        reasons.append("4H VX/VIX is neutral")
    else:
        reasons.append("4H VX/VIX is below cloud and not helping shorts")

    if vx_15m == "Above cloud":
        score += 2
        reasons.append("15m VX/VIX confirms immediate volatility pressure")
    elif vx_15m in ["Mixed / inside cloud", "Rolling over / turning up"]:
        score += 1
        reasons.append("15m VX/VIX is partially supportive")
    else:
        reasons.append("15m VX/VIX is below cloud and weak for shorts")

    if sox_status == "Weak":
        score += 2
        reasons.append("SOX is weak")
    elif sox_status == "Mixed":
        score += 1
        reasons.append("SOX is mixed")
    else:
        score -= 2
        reasons.append("SOX is strong against the short thesis")

    if es_behavior == "Rejecting key level / trend":
        score += 2
        reasons.append("ES is rejecting key trend")
    elif es_behavior == "Chopping at level":
        score += 0
        reasons.append("ES is chopping at the level")
    elif es_behavior == "Above trend and holding":
        score -= 2
        reasons.append("ES is above trend and holding")
    else:
        score -= 2
        reasons.append("Short is forced / anticipatory")

    if price_stalling:
        score -= 1
        reasons.append("price is stalling")

    if vx_flipping:
        score -= 1
        reasons.append("VX/VIX is flipping against the short thesis")

    if score >= 7:
        grade = "A+"
    elif score == 6:
        grade = "A"
    elif score in [4, 5]:
        grade = "B"
    elif score == 3:
        grade = "C"
    elif score == 2:
        grade = "D"
    else:
        grade = "F"

    return grade, score, ". ".join(reasons) + "."



def score_long_trade(vx_4h, vx_15m, sox_status, es_behavior, price_stalling, vx_flipping):
    score = 0
    reasons = []

    if vx_4h == "Below cloud":
        score += 2
        reasons.append("4H VX/VIX supports the broader long regime")
    elif vx_4h == "Mixed / inside cloud":
        score += 1
        reasons.append("4H VX/VIX is neutral")
    else:
        reasons.append("4H VX/VIX is above cloud and pressures longs")

    if vx_15m == "Below cloud":
        score += 2
        reasons.append("15m VX/VIX supports immediate long conditions")
    elif vx_15m == "Mixed / inside cloud":
        score += 1
        reasons.append("15m VX/VIX is partially supportive")
    else:
        reasons.append("15m VX/VIX is not helping longs")

    if sox_status == "Strong":
        score += 2
        reasons.append("SOX is strong")
    elif sox_status == "Mixed":
        score += 1
        reasons.append("SOX is mixed")
    else:
        score -= 2
        reasons.append("SOX is weak against the long thesis")

    if es_behavior == "Above trend and holding":
        score += 2
        reasons.append("ES is above trend and holding")
    elif es_behavior == "Chopping at level":
        score += 0
        reasons.append("ES is chopping at the level")
    elif es_behavior == "Rejecting key level / trend":
        score -= 2
        reasons.append("ES is rejecting trend, which hurts longs")
    else:
        score -= 2
        reasons.append("Long is forced / anticipatory")

    if price_stalling:
        score -= 1
        reasons.append("price is stalling")

    if vx_flipping:
        score -= 1
        reasons.append("VX/VIX is flipping against the long thesis")

    if score >= 7:
        grade = "A+"
    elif score == 6:
        grade = "A"
    elif score in [4, 5]:
        grade = "B"
    elif score == 3:
        grade = "C"
    elif score == 2:
        grade = "D"
    else:
        grade = "F"

    return grade, score, ". ".join(reasons) + "."



def take_decision(grade):
    if grade in ["A+", "A"]:
        return "Take"
    if grade == "B":
        return "Conditional Take"
    if grade == "C":
        return "Small Size Only / Pass"
    return "No-Take"



def grade_html(title, grade, score):
    color = GRADE_COLORS[grade]
    return f"""
    <div class="grade-box" style="background-color:{color};">
        <div style="font-size:22px;font-weight:700;margin-bottom:8px;">{title}</div>
        <div style="font-size:34px;font-weight:800;">{grade}</div>
        <div style="font-size:16px;margin-top:6px;">Score: {score}</div>
    </div>
    """


if st.button("Grade Trade Setup"):
    short_grade, short_score, short_explanation = score_short_trade(
        vx_4h, vx_15m, sox_status, es_behavior, price_stalling, vx_flipping
    )
    long_grade, long_score, long_explanation = score_long_trade(
        vx_4h, vx_15m, sox_status, es_behavior, price_stalling, vx_flipping
    )

    short_plan = SHORT_RULES[short_grade]
    long_plan = LONG_RULES[long_grade]
    short_conf = GRADE_TO_CONFIDENCE[short_grade]
    long_conf = GRADE_TO_CONFIDENCE[long_grade]
    best_side, bias_strength = get_best_side(short_grade, long_grade)
    short_downgrade = get_downgrade_reasons("Short", vx_4h, vx_15m, sox_status, es_behavior, price_stalling, vx_flipping)
    long_downgrade = get_downgrade_reasons("Long", vx_4h, vx_15m, sox_status, es_behavior, price_stalling, vx_flipping)
    short_pass_reason = get_pass_reason("Short", short_grade)
    long_pass_reason = get_pass_reason("Long", long_grade)

    if best_side == "Short":
        best_side_reason = short_explanation
        best_side_conf = short_conf
    elif best_side == "Long":
        best_side_reason = long_explanation
        best_side_conf = long_conf
    else:
        best_side_reason = "Both sides are grading similarly, so there is no clear directional edge right now."
        best_side_conf = max(short_conf, long_conf)

    st.session_state.current_log_entry = {
        "4H VX/VIX": vx_4h,
        "15m VX/VIX": vx_15m,
        "SOX": sox_status,
        "ES Behavior": es_behavior,
        "Price Stalling": price_stalling,
        "VX Flipping": vx_flipping,
        "Short Grade": short_grade,
        "Long Grade": long_grade,
        "Short Score": short_score,
        "Long Score": long_score,
        "Short Confidence": short_conf,
        "Long Confidence": long_conf,
        "Best Side": best_side,
        "Bias Strength": bias_strength,
        "Short Take Signal": take_decision(short_grade),
        "Long Take Signal": take_decision(long_grade),
        "Journal Notes": journal_notes,
    }

    st.markdown("---")
    st.markdown("## Best Side Today")
    st.markdown(
        f"""
        <div class="summary-box">
            <div class="summary-title">Best Side: {best_side}</div>
            <div class="summary-text">
                <strong>Bias Strength:</strong> {bias_strength}<br><br>
                <strong>Confidence:</strong> {best_side_conf}/100<br><br>
                <strong>Why:</strong> {best_side_reason}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("## Trade Grades")
    g1, g2 = st.columns(2)
    with g1:
        st.markdown(grade_html("Short Setup", short_grade, short_score), unsafe_allow_html=True)
        st.progress(short_conf / 100)
        st.caption(f"Short confidence: {short_conf}/100")
    with g2:
        st.markdown(grade_html("Long Setup", long_grade, long_score), unsafe_allow_html=True)
        st.progress(long_conf / 100)
        st.caption(f"Long confidence: {long_conf}/100")

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Short Take / No-Take</div>
                <div class="metric-value" style="font-size:20px;">{take_decision(short_grade)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Long Take / No-Take</div>
                <div class="metric-value" style="font-size:20px;">{take_decision(long_grade)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Short Stop</div>
                <div class="metric-value" style="font-size:20px;">{short_plan['stop']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Long Stop</div>
                <div class="metric-value" style="font-size:20px;">{long_plan['stop']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("## Why These Grades")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            f"""
            <div class="summary-box">
                <div class="summary-title">Why Short Grade = {short_grade}</div>
                <div class="summary-text">{short_explanation}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div class="summary-box">
                <div class="summary-title">Why Long Grade = {long_grade}</div>
                <div class="summary-text">{long_explanation}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("## What Would Downgrade This Trade?")
    d1, d2 = st.columns(2)
    with d1:
        st.markdown(
            f"""
            <div class="summary-box">
                <div class="summary-title">Short Downgrade Triggers</div>
                <div class="summary-text">{'<br><br>'.join([f'• {r}' for r in short_downgrade])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with d2:
        st.markdown(
            f"""
            <div class="summary-box">
                <div class="summary-title">Long Downgrade Triggers</div>
                <div class="summary-text">{'<br><br>'.join([f'• {r}' for r in long_downgrade])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("## Time-Based Management")
    t1, t2 = st.columns(2)
    with t1:
        st.markdown(
            f"""
            <div class="summary-box">
                <div class="summary-title">Short Time Rule</div>
                <div class="summary-text">{short_plan['time_rule']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with t2:
        st.markdown(
            f"""
            <div class="summary-box">
                <div class="summary-title">Long Time Rule</div>
                <div class="summary-text">{long_plan['time_rule']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("## Trade Framework")
    p1, p2 = st.columns(2)
    with p1:
        st.markdown(
            f"""
            <div class="summary-box">
                <div class="summary-title">Short Setup Framework</div>
                <div class="summary-text">
                    <strong>Grade:</strong> {short_grade}<br><br>
                    <strong>Suggested Size:</strong> {short_plan['size']}<br><br>
                    <strong>Stop Suggestion:</strong> {short_plan['stop']}<br><br>
                    <strong>Framework:</strong> {short_plan['framework']}<br><br>
                    <strong>Management:</strong> {short_plan['management']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with p2:
        st.markdown(
            f"""
            <div class="summary-box">
                <div class="summary-title">Long Setup Framework</div>
                <div class="summary-text">
                    <strong>Grade:</strong> {long_grade}<br><br>
                    <strong>Suggested Size:</strong> {long_plan['size']}<br><br>
                    <strong>Stop Suggestion:</strong> {long_plan['stop']}<br><br>
                    <strong>Framework:</strong> {long_plan['framework']}<br><br>
                    <strong>Management:</strong> {long_plan['management']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("## Reason for Pass")
    r1, r2 = st.columns(2)
    with r1:
        st.markdown(
            f"""
            <div class="summary-box">
                <div class="summary-title">Short Pass Reason</div>
                <div class="summary-text">{short_pass_reason}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with r2:
        st.markdown(
            f"""
            <div class="summary-box">
                <div class="summary-title">Long Pass Reason</div>
                <div class="summary-text">{long_pass_reason}</div>
            </div>
            """,
            unsafe_allow_html=True,
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
                mime="text/csv",
            )


if st.session_state.trade_log:
    st.markdown("### Saved Trade Log")
    log_df = pd.DataFrame(st.session_state.trade_log)
    st.dataframe(log_df, use_container_width=True)
