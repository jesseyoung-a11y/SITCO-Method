from dataclasses import dataclass
from typing import Dict, List, Tuple

import streamlit as st


GRADE_COLORS = {
    "A+": "#16a34a",  # green
    "A": "#16a34a",   # green
    "B": "#f59e0b",   # orange
    "C": "#dc2626",   # red
    "D": "#dc2626",   # red
    "F": "#dc2626",   # red
}

GRADE_ORDER = ["F", "D", "C", "B", "A", "A+"]


@dataclass
class TradeInputs:
    vx_4h_above_cloud: bool
    vx_15m_above_cloud: bool
    sox_weak: bool
    sox_strong: bool
    es_rejecting_trend: bool
    es_holding_above_trend: bool
    price_stalling: bool
    vx_flipping_against_thesis: bool


@dataclass
class GradeOutput:
    grade: str
    score: int
    summary: str
    stop_plan: str
    management: List[str]


SHORT_PLAYBOOK: Dict[str, Dict] = {
    "A+": {
        "summary": "Give room, trust thesis, exit early only if confirmation truly breaks.",
        "stop_plan": "5-point max stop, normal size.",
        "management": [
            "Full size.",
            "5-point hard stop.",
            "Thesis-failed early exit.",
            "Allow normal noise.",
            "Can hold through minor pops if SOX / VX still agree.",
        ],
    },
    "A": {
        "summary": "Needs to work reasonably soon.",
        "stop_plan": "4-point max stop, moderate size.",
        "management": [
            "Moderate size or slightly reduced size.",
            "4-point hard stop most of the time.",
            "Needs decent follow-through.",
            "Less tolerance for chop than A+.",
            "If no downside progress soon, start tightening mentally.",
        ],
    },
    "B": {
        "summary": "Needs to work almost immediately, or reduce risk.",
        "stop_plan": "4-point max stop, sometimes 5 only if structure truly needs it.",
        "management": [
            "Reduced size.",
            "Smaller size + faster proof requirement.",
            "Much faster management.",
            "If price stalls or VX flips, scratch, cut partial, or tighten aggressively.",
            "Do not let a B trade become a full A+ loss.",
        ],
    },
    "C": {
        "summary": "Weak short setup. Usually pass.",
        "stop_plan": "No trade preferred.",
        "management": [
            "Usually skip.",
            "Only consider if multiple factors improve quickly.",
            "Do not force mediocre shorts.",
        ],
    },
    "D": {
        "summary": "Poor short setup.",
        "stop_plan": "Avoid.",
        "management": [
            "Do not take.",
            "Wait for better alignment.",
        ],
    },
    "F": {
        "summary": "Short thesis is invalid.",
        "stop_plan": "Do not short.",
        "management": [
            "Stand aside or look for long conditions instead.",
        ],
    },
}

LONG_PLAYBOOK: Dict[str, Dict] = {
    "A+": {
        "summary": "Give room, trust thesis, exit early only if confirmation truly breaks.",
        "stop_plan": "5-point max stop, normal size.",
        "management": [
            "Full size.",
            "5-point hard stop.",
            "Thesis-failed early exit.",
            "Allow normal noise.",
            "Can hold through minor dips if internals still agree.",
        ],
    },
    "A": {
        "summary": "Needs to work reasonably soon.",
        "stop_plan": "4-point max stop, moderate size.",
        "management": [
            "Moderate size or slightly reduced size.",
            "4-point hard stop most of the time.",
            "Needs decent follow-through.",
            "Less tolerance for chop than A+.",
            "If no upside progress soon, start tightening mentally.",
        ],
    },
    "B": {
        "summary": "Needs to work almost immediately, or reduce risk.",
        "stop_plan": "4-point max stop, sometimes 5 only if structure truly needs it.",
        "management": [
            "Reduced size.",
            "Smaller size + faster proof requirement.",
            "Much faster management.",
            "If price stalls or internals flip, scratch, cut partial, or tighten aggressively.",
            "Do not let a B trade become a full A+ loss.",
        ],
    },
    "C": {
        "summary": "Weak long setup. Usually pass.",
        "stop_plan": "No trade preferred.",
        "management": [
            "Usually skip.",
            "Only consider if multiple factors improve quickly.",
            "Do not force mediocre longs.",
        ],
    },
    "D": {
        "summary": "Poor long setup.",
        "stop_plan": "Avoid.",
        "management": [
            "Do not take.",
            "Wait for better alignment.",
        ],
    },
    "F": {
        "summary": "Long thesis is invalid.",
        "stop_plan": "Do not go long.",
        "management": [
            "Stand aside or look for short conditions instead.",
        ],
    },
}


def clamp_grade(score: int) -> str:
    if score >= 5:
        return "A+"
    if score == 4:
        return "A"
    if score == 3:
        return "B"
    if score == 2:
        return "C"
    if score == 1:
        return "D"
    return "F"


def score_short_setup(inputs: TradeInputs) -> GradeOutput:
    score = 0
    reasons = []

    if inputs.vx_4h_above_cloud:
        score += 1
        reasons.append("4H VX above EMA clouds")
    if inputs.vx_15m_above_cloud:
        score += 1
        reasons.append("15m VX above EMA clouds")
    if inputs.sox_weak:
        score += 1
        reasons.append("SOX weak")
    if inputs.es_rejecting_trend:
        score += 2
        reasons.append("ES rejecting trend")

    if inputs.sox_strong:
        score -= 2
        reasons.append("SOX strong against short thesis")
    if inputs.es_holding_above_trend:
        score -= 2
        reasons.append("ES holding above trend")
    if inputs.price_stalling:
        score -= 1
        reasons.append("Price stalling")
    if inputs.vx_flipping_against_thesis:
        score -= 1
        reasons.append("VX flipping against thesis")

    grade = clamp_grade(max(0, min(score, 5)))
    pb = SHORT_PLAYBOOK[grade]
    summary = ", ".join(reasons) if reasons else "No strong short signals yet"

    return GradeOutput(
        grade=grade,
        score=score,
        summary=summary,
        stop_plan=pb["stop_plan"],
        management=pb["management"],
    )



def score_long_setup(inputs: TradeInputs) -> GradeOutput:
    score = 0
    reasons = []

    if not inputs.vx_4h_above_cloud:
        score += 1
        reasons.append("4H VX below EMA clouds")
    if not inputs.vx_15m_above_cloud:
        score += 1
        reasons.append("15m VX below EMA clouds")
    if inputs.sox_strong:
        score += 1
        reasons.append("SOX strong")
    if inputs.es_holding_above_trend:
        score += 2
        reasons.append("ES holding above trend")

    if inputs.sox_weak:
        score -= 2
        reasons.append("SOX weak against long thesis")
    if inputs.es_rejecting_trend:
        score -= 2
        reasons.append("ES rejecting trend")
    if inputs.price_stalling:
        score -= 1
        reasons.append("Price stalling")
    if inputs.vx_flipping_against_thesis:
        score -= 1
        reasons.append("VX pressure rising against long thesis")

    grade = clamp_grade(max(0, min(score, 5)))
    pb = LONG_PLAYBOOK[grade]
    summary = ", ".join(reasons) if reasons else "No strong long signals yet"

    return GradeOutput(
        grade=grade,
        score=score,
        summary=summary,
        stop_plan=pb["stop_plan"],
        management=pb["management"],
    )



def grade_badge(label: str, grade: str) -> str:
    color = GRADE_COLORS.get(grade, "#6b7280")
    return f'''
    <div style="padding:12px 16px;border-radius:14px;background:{color};color:white;font-weight:700;font-size:20px;text-align:center;">
        {label}: {grade}
    </div>
    '''



def render_trade_grade_card(title: str, output: GradeOutput):
    color = GRADE_COLORS.get(output.grade, "#6b7280")
    st.markdown(
        f'''
        <div style="border:1px solid #e5e7eb;border-radius:18px;padding:16px 18px;margin-bottom:14px;">
            <div style="display:inline-block;padding:6px 12px;border-radius:999px;background:{color};color:white;font-weight:700;margin-bottom:10px;">
                {title}: {output.grade}
            </div>
            <div style="font-size:15px;margin-bottom:8px;"><strong>Why:</strong> {output.summary}</div>
            <div style="font-size:15px;margin-bottom:8px;"><strong>Stop suggestion:</strong> {output.stop_plan}</div>
            <div style="font-size:15px;"><strong>Framework:</strong> {SHORT_PLAYBOOK[output.grade]['summary'] if 'Short' in title else LONG_PLAYBOOK[output.grade]['summary']}</div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    for item in output.management:
        st.write(f"• {item}")



def render_trade_grading_panel():
    st.subheader("Trade Grading Framework")
    st.caption("Separate grades for shorts and longs, with color-coded trade quality and stop guidance.")

    col1, col2 = st.columns(2)

    with col1:
        vx_4h_above_cloud = st.toggle("4H VX above EMA clouds", value=True)
        vx_15m_above_cloud = st.toggle("15m VX above EMA clouds", value=True)
        sox_weak = st.toggle("SOX weak", value=True)
        sox_strong = st.toggle("SOX strong", value=False)

    with col2:
        es_rejecting_trend = st.toggle("ES rejecting trend", value=True)
        es_holding_above_trend = st.toggle("ES holding above trend", value=False)
        price_stalling = st.toggle("Price stalling", value=False)
        vx_flipping_against_thesis = st.toggle("VX flipping against thesis", value=False)

    inputs = TradeInputs(
        vx_4h_above_cloud=vx_4h_above_cloud,
        vx_15m_above_cloud=vx_15m_above_cloud,
        sox_weak=sox_weak,
        sox_strong=sox_strong,
        es_rejecting_trend=es_rejecting_trend,
        es_holding_above_trend=es_holding_above_trend,
        price_stalling=price_stalling,
        vx_flipping_against_thesis=vx_flipping_against_thesis,
    )

    short_output = score_short_setup(inputs)
    long_output = score_long_setup(inputs)

    st.markdown("### Grades")
    g1, g2 = st.columns(2)
    with g1:
        st.markdown(grade_badge("Short Setup", short_output.grade), unsafe_allow_html=True)
    with g2:
        st.markdown(grade_badge("Long Setup", long_output.grade), unsafe_allow_html=True)

    st.markdown("### Trade Guidance")
    left, right = st.columns(2)
    with left:
        render_trade_grade_card("Short Setup", short_output)
    with right:
        render_trade_grade_card("Long Setup", long_output)


# Example usage inside your Streamlit app:
# from trade_grading_framework import render_trade_grading_panel
# render_trade_grading_panel()

