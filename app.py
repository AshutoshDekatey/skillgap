from __future__ import annotations

import hmac
import html
from pathlib import Path

import streamlit as st

from engine import (
    SKILL_LABELS,
    TRACK_LABELS,
    build_practice_queue,
    diagnostic_question_ids,
    get_mastery,
    get_question,
    readiness_summary,
)
from storage import create_or_get_user, get_attempted_question_ids, get_attempts, init_db, record_attempt


APP_DIR = Path(__file__).parent
DB_PATH = APP_DIR / ".data" / "progress.db"
DEMO_USERS = {
    "Ashutosh": {"password": "Ashutosh", "track": "pandas"},
    "Aakash": {"password": "Aakash", "track": "terraform"},
    "Neeraj": {"password": "Neeraj", "track": "capital_markets"},
}

st.set_page_config(page_title="SkillGap", page_icon="✦", layout="wide", initial_sidebar_state="expanded")


def inject_css() -> None:
    st.markdown(
        """
        <style>
        :root {--blue:#2563eb; --violet:#7c3aed; --ink:#172033; --muted:#667085; --line:#e7eaf2;}
        .stApp {background:linear-gradient(180deg,#f8faff 0%,#ffffff 48%); color:var(--ink);}
        [data-testid="stSidebar"] {background:#11152a;}
        [data-testid="stSidebar"] * {color:#f8f9ff;}
        .block-container {max-width:1080px; padding-top:2rem;}
        .hero {padding:2.5rem; border:1px solid #dfe4ff; border-radius:26px; margin-bottom:1.4rem;
          background:radial-gradient(circle at 88% 20%,rgba(124,58,237,.18),transparent 28%),
                     linear-gradient(135deg,#ffffff,#f3f5ff); box-shadow:0 18px 50px rgba(57,48,135,.09);}
        .hero h1 {font-size:2.65rem; letter-spacing:-.045em; color:#151932; margin:.15rem 0 .5rem;}
        .hero p {color:#586174; font-size:1.06rem; max-width:720px; margin:0; line-height:1.65;}
        .eyebrow {font-size:.74rem; letter-spacing:.13em; font-weight:800; color:var(--violet);}
        .question-card {background:white; border:1px solid var(--line); border-radius:20px;
          padding:1.5rem; box-shadow:0 10px 32px rgba(39,45,87,.07); margin:.8rem 0 1rem;}
        .skill-pill {display:inline-block; padding:.32rem .72rem; border-radius:999px;
          background:#eef2ff; color:#5145cd; font-size:.78rem; font-weight:750;}
        .question-context {color:#59637a; font-size:.98rem; line-height:1.6; margin:.75rem 0;}
        .codebox {background:#171a31; color:#f3f4ff; border-radius:13px; padding:1rem 1.1rem;
          font-family:ui-monospace,SFMono-Regular,Menlo,monospace; white-space:pre-wrap; margin:.9rem 0;}
        .metric-card {background:white; border:1px solid var(--line); border-radius:18px;
          padding:1.1rem 1.2rem; min-height:118px; box-shadow:0 7px 22px rgba(37,50,105,.05);}
        .metric-label {font-size:.75rem; color:#7a8499; text-transform:uppercase; letter-spacing:.08em; font-weight:700;}
        .metric-value {font-size:1.65rem; font-weight:780; color:#19213a; margin-top:.45rem; line-height:1.15;}
        .map-shell {background:white; border:1px solid var(--line); border-radius:22px; padding:1.5rem 1.6rem;
          box-shadow:0 10px 32px rgba(37,50,105,.055); margin:1.2rem 0;}
        .skill-row {margin:0 0 1.18rem;}
        .skill-head {display:flex; justify-content:space-between; gap:1rem; margin-bottom:.45rem;
          color:#26304a; font-size:.93rem; font-weight:650;}
        .skill-score {color:#5e6680; font-variant-numeric:tabular-nums;}
        .bar-track {height:10px; background:#eef0f7; border-radius:999px; overflow:hidden;}
        .bar-fill {height:100%; border-radius:999px; width:var(--score);
          background:linear-gradient(90deg,#2563eb 0%,#5b5ce2 52%,#8b5cf6 100%);
          animation:growBar 1.15s cubic-bezier(.2,.75,.25,1) both;}
        @keyframes growBar {from{width:0} to{width:var(--score)}}
        .practice-card {border-radius:22px; padding:1.5rem 1.6rem; color:white;
          background:linear-gradient(125deg,#2457d6 0%,#6545d8 56%,#803ed1 100%);
          box-shadow:0 16px 38px rgba(85,65,201,.2); margin-top:1.2rem;}
        .practice-card h3 {margin:.2rem 0 .45rem; color:white;}
        .practice-card p {margin:0; color:#ebeaff; line-height:1.55;}
        div[data-testid="stMetric"] {background:white; border:1px solid var(--line); border-radius:17px; padding:1rem;}
        .stButton > button[kind="primary"] {background:linear-gradient(90deg,#2563eb,#7c3aed); border:0;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    st.markdown(
        """<div class="hero"><div class="eyebrow">PERSONALIZED LEARNING</div>
        <h1>SkillGap</h1><p>One focused learning path for each person. Diagnose what is weak, practise what matters, and watch the skill map respond.</p></div>""",
        unsafe_allow_html=True,
    )


def clear_question_state() -> None:
    st.session_state.pop("active_question_id", None)
    st.session_state.pop("feedback", None)


def begin_practice() -> None:
    track = st.session_state.track
    attempts = get_attempts(DB_PATH, st.session_state.user_id, track)
    mastery = get_mastery(attempts, track)
    st.session_state.practice_queue = build_practice_queue(track, attempts, mastery, count=5)
    st.session_state.practice_index = 0
    st.session_state.practice_correct = 0
    st.session_state.readiness_before = readiness_summary(mastery)["readiness"]
    st.session_state.session_complete = False
    st.session_state.page = "Practice"
    clear_question_state()


def render_question(question: dict, mode: str) -> None:
    label = SKILL_LABELS[st.session_state.track][question["skill"]]
    st.markdown(f'<span class="skill-pill">{html.escape(label)}</span>', unsafe_allow_html=True)
    if question.get("context"):
        st.markdown(f'<div class="question-context">{html.escape(question["context"])}</div>', unsafe_allow_html=True)
    st.markdown(f"### {question['prompt']}")
    if question.get("code"):
        st.markdown(f'<div class="codebox">{html.escape(question["code"])}</div>', unsafe_allow_html=True)

    feedback = st.session_state.get("feedback")
    if feedback and feedback["question_id"] == question["id"]:
        if feedback["correct"]:
            st.success("Correct — this answer now contributes to your mastery score.")
        else:
            st.error(f"Correct answer: {question['options'][question['answer']]}")
        st.info(question["explanation"])
        if st.button("Continue →", type="primary", use_container_width=True):
            if mode == "practice":
                st.session_state.practice_index += 1
                if st.session_state.practice_index >= len(st.session_state.practice_queue):
                    st.session_state.session_complete = True
            clear_question_state()
            st.rerun()
        return

    with st.form(f"answer_{question['id']}_{mode}"):
        answer = st.radio("Choose one answer", list(question["options"]),
                          format_func=lambda key: question["options"][key], index=None)
        confidence = st.select_slider("Confidence", ["Guessing", "Unsure", "Fairly sure", "Certain"], value="Fairly sure")
        submitted = st.form_submit_button("Check answer", type="primary", use_container_width=True)
    if submitted:
        if answer is None:
            st.warning("Choose an answer before submitting.")
            return
        correct = answer == question["answer"]
        record_attempt(DB_PATH, st.session_state.user_id, question["id"], st.session_state.track,
                       question["skill"], correct, confidence, mode)
        if mode == "practice" and correct:
            st.session_state.practice_correct += 1
        st.session_state.feedback = {"question_id": question["id"], "correct": correct}
        st.rerun()


def diagnostic_page() -> None:
    track = st.session_state.track
    st.title("Diagnostic")
    st.caption(f"12 readable questions across the six skills in {TRACK_LABELS[track]}.")
    question_ids = diagnostic_question_ids(track)
    attempted = get_attempted_question_ids(DB_PATH, st.session_state.user_id, track, "diagnostic")
    remaining = [qid for qid in question_ids if qid not in attempted]
    st.progress((len(question_ids) - len(remaining)) / len(question_ids),
                text=f"{len(question_ids) - len(remaining)} of {len(question_ids)} complete")
    if not remaining:
        st.success("Diagnostic complete. Your dashboard is ready.")
        if st.button("View skill map", type="primary"):
            st.session_state.page = "Dashboard"
            clear_question_state()
            st.rerun()
        return
    if st.session_state.get("active_question_id") not in remaining:
        st.session_state.active_question_id = remaining[0]
    render_question(get_question(st.session_state.active_question_id), "diagnostic")


def skill_map_html(mastery: dict, track: str) -> str:
    rows = []
    for skill, values in mastery.items():
        score = max(0.0, min(100.0, float(values["score"])))
        rows.append(
            f"""<div class="skill-row"><div class="skill-head">
            <span>{html.escape(SKILL_LABELS[track][skill])}</span>
            <span class="skill-score">{score:.0f}% · {values['attempts']} attempts</span></div>
            <div class="bar-track"><div class="bar-fill" style="--score:{score}%"></div></div></div>"""
        )
    return '<div class="map-shell"><div class="eyebrow">MASTERY BY SKILL</div><br>' + "".join(rows) + "</div>"


def dashboard_page() -> None:
    track = st.session_state.track
    attempts = get_attempts(DB_PATH, st.session_state.user_id, track)
    mastery = get_mastery(attempts, track)
    summary = readiness_summary(mastery)
    labels = SKILL_LABELS[track]

    st.title(f"{st.session_state.user_name}'s skill map")
    st.caption(TRACK_LABELS[track])
    metrics = [
        ("Readiness index", f"{summary['readiness']}%"),
        ("Questions answered", str(len(attempts))),
        ("Strongest", labels[summary["strongest"]]),
        ("Focus next", labels[summary["weakest"]]),
    ]
    columns = st.columns(4)
    for column, (label, value) in zip(columns, metrics):
        column.markdown(f'<div class="metric-card"><div class="metric-label">{html.escape(label)}</div><div class="metric-value">{html.escape(value)}</div></div>', unsafe_allow_html=True)

    st.markdown(skill_map_html(mastery, track), unsafe_allow_html=True)
    focus = labels[summary["weakest"]]
    st.markdown(
        f"""<div class="practice-card"><div class="eyebrow" style="color:#d9dcff">RECOMMENDED SESSION</div>
        <h3>Strengthen {html.escape(focus)}</h3>
        <p>Five questions selected from your weakest and least-tested areas. Your skill map recalculates when the session is complete.</p></div>""",
        unsafe_allow_html=True,
    )
    if st.button("Start recommended practice →", type="primary", use_container_width=True):
        begin_practice()
        st.rerun()
    st.caption("The readiness index is a learning-progress indicator, not a certification or employment score.")


def practice_page() -> None:
    st.title("Recommended practice")
    if not st.session_state.get("practice_queue"):
        st.info("Start a recommended session from your dashboard.")
        if st.button("Return to dashboard"):
            st.session_state.page = "Dashboard"
            st.rerun()
        return

    if st.session_state.get("session_complete"):
        attempts = get_attempts(DB_PATH, st.session_state.user_id, st.session_state.track)
        new_score = readiness_summary(get_mastery(attempts, st.session_state.track))["readiness"]
        old_score = st.session_state.readiness_before
        delta = new_score - old_score
        st.success(f"Session complete: {st.session_state.practice_correct}/5 correct.")
        a, b, c = st.columns(3)
        a.metric("Before", f"{old_score}%")
        b.metric("Now", f"{new_score}%")
        c.metric("Change", f"{delta:+d} points")
        st.write("Your dashboard has been recalculated using these five new attempts.")
        if st.button("See updated skill map", type="primary", use_container_width=True):
            for key in ["practice_queue", "practice_index", "practice_correct", "readiness_before", "session_complete"]:
                st.session_state.pop(key, None)
            st.session_state.page = "Dashboard"
            st.rerun()
        return

    index = st.session_state.practice_index
    queue = st.session_state.practice_queue
    st.progress(index / len(queue), text=f"Question {index + 1} of {len(queue)}")
    render_question(get_question(queue[index]), "practice")


def login_page() -> None:
    render_hero()
    left, right = st.columns([1.25, 1])
    with left:
        st.subheader("Three people. Three learning paths.")
        st.markdown("**Ashutosh** · Pandas & Data Cleaning  \n**Aakash** · Terraform Foundations  \n**Neeraj** · Capital Markets")
        st.write("Each learner receives an independent diagnostic, mastery map and recommended practice queue.")
    with right:
        with st.form("login"):
            name = st.selectbox("Learner", list(DEMO_USERS))
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign in →", type="primary", use_container_width=True)
        st.caption("Demo password: the learner's displayed name.")
        if submitted:
            profile = DEMO_USERS[name]
            if not hmac.compare_digest(password, profile["password"]):
                st.error("Incorrect password.")
            else:
                st.session_state.user_id = create_or_get_user(DB_PATH, name, profile["track"])
                st.session_state.user_name = name
                st.session_state.track = profile["track"]
                st.session_state.page = "Dashboard"
                st.rerun()


def main() -> None:
    init_db(DB_PATH)
    inject_css()
    if "user_id" not in st.session_state:
        login_page()
        return

    with st.sidebar:
        st.markdown("## ✦ SkillGap")
        st.caption(st.session_state.user_name)
        st.caption(TRACK_LABELS[st.session_state.track])
        pages = ["Dashboard", "Diagnostic", "Practice"]
        selected = st.radio("Navigate", pages, index=pages.index(st.session_state.get("page", "Dashboard")), label_visibility="collapsed")
        if selected != st.session_state.get("page"):
            st.session_state.page = selected
            clear_question_state()
            st.rerun()
        st.divider()
        if st.button("Sign out", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    page = st.session_state.get("page", "Dashboard")
    if page == "Dashboard":
        dashboard_page()
    elif page == "Diagnostic":
        diagnostic_page()
    else:
        practice_page()


if __name__ == "__main__":
    main()
