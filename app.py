from __future__ import annotations

import hmac
import html
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from engine import (
    SKILL_LABELS,
    build_practice_queue,
    diagnostic_question_ids,
    get_mastery,
    get_question,
    readiness_summary,
)
from storage import (
    create_or_get_user,
    get_attempted_question_ids,
    get_attempts,
    init_db,
    record_attempt,
)


APP_DIR = Path(__file__).parent
DB_PATH = APP_DIR / ".data" / "progress.db"

DEMO_USERS = {
    "Ashutosh": {"password": "Ashutosh", "goal": "Financial data"},
    "Aakash": {"password": "Aakash", "goal": "Data analysis"},
    "Neeraj": {"password": "Neeraj", "goal": "Business reporting"},
}

st.set_page_config(
    page_title="Pandas GapMap",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_css() -> None:
    st.markdown(
        """
        <style>
        .stApp {background: #f5f7fb;}
        [data-testid="stSidebar"] {background: #101828;}
        [data-testid="stSidebar"] * {color: #f8fafc;}
        .hero {
            padding: 2.2rem 2.4rem; border-radius: 24px;
            color: white; margin-bottom: 1.2rem;
            background: linear-gradient(125deg, #14213d 0%, #264653 55%, #2a9d8f 100%);
            box-shadow: 0 16px 40px rgba(16, 24, 40, .16);
        }
        .hero h1 {font-size: 2.45rem; margin: 0 0 .45rem;}
        .hero p {font-size: 1.05rem; opacity: .9; margin: 0; max-width: 760px;}
        .question-card, .soft-card {
            background: white; border: 1px solid #e4e7ec; border-radius: 18px;
            padding: 1.3rem 1.45rem; box-shadow: 0 5px 18px rgba(16,24,40,.05);
        }
        .eyebrow {color: #087f73; font-weight: 750; letter-spacing: .08em; font-size: .76rem;}
        .codebox {
            background: #101828; color: #e6edf3; border-radius: 12px;
            padding: 1rem 1.1rem; font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
            white-space: pre-wrap; margin: .8rem 0;
        }
        .skill-pill {display:inline-block; background:#e8f7f4; color:#087f73; border-radius:999px;
            padding:.28rem .7rem; font-size:.8rem; font-weight:700; margin-bottom:.65rem;}
        div[data-testid="stMetric"] {background:white; border:1px solid #e4e7ec; padding:1rem;
            border-radius:16px; box-shadow:0 4px 14px rgba(16,24,40,.04);}
        .small-note {color:#667085; font-size:.88rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def reset_question_state() -> None:
    st.session_state.pop("active_question_id", None)
    st.session_state.pop("feedback", None)


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero">
          <div class="eyebrow" style="color:#b9f5e9">PERSONALIZED PANDAS PRACTICE</div>
          <h1>Pandas GapMap</h1>
          <p>Find the data-cleaning concepts you have not fully mastered, then practise the right skill next.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_question(question: dict, mode: str) -> None:
    feedback = st.session_state.get("feedback")
    st.markdown(
        f'<span class="skill-pill">{html.escape(SKILL_LABELS[question["skill"]])}</span>',
        unsafe_allow_html=True,
    )
    st.subheader(question["prompt"])
    if question.get("code"):
        st.markdown(
            f'<div class="codebox">{html.escape(question["code"])}</div>',
            unsafe_allow_html=True,
        )

    if feedback and feedback["question_id"] == question["id"]:
        if feedback["correct"]:
            st.success("Correct — your mastery estimate has been updated.")
        else:
            correct_text = question["options"][question["answer"]]
            st.error(f"Not quite. Correct answer: {correct_text}")
        st.info(question["explanation"])
        if st.button("Next question →", type="primary", use_container_width=True):
            reset_question_state()
            st.rerun()
        return

    with st.form(f"question_form_{question['id']}"):
        choice = st.radio(
            "Choose one answer",
            options=list(question["options"].keys()),
            format_func=lambda key: question["options"][key],
            index=None,
        )
        confidence = st.select_slider(
            "How confident are you?",
            options=["Guessing", "Unsure", "Fairly sure", "Certain"],
            value="Fairly sure",
        )
        submitted = st.form_submit_button("Check answer", type="primary", use_container_width=True)

    if submitted:
        if choice is None:
            st.warning("Select an answer before submitting.")
            return
        correct = choice == question["answer"]
        record_attempt(
            DB_PATH,
            user_id=st.session_state.user_id,
            question_id=question["id"],
            skill=question["skill"],
            correct=correct,
            confidence=confidence,
            mode=mode,
        )
        st.session_state.feedback = {
            "question_id": question["id"],
            "correct": correct,
        }
        st.rerun()


def diagnostic_page() -> None:
    st.title("Diagnostic assessment")
    st.caption("16 questions · approximately 10 minutes · one pass is enough for V1")
    all_ids = diagnostic_question_ids()
    attempted = get_attempted_question_ids(DB_PATH, st.session_state.user_id, mode="diagnostic")
    remaining = [qid for qid in all_ids if qid not in attempted]
    progress = (len(all_ids) - len(remaining)) / len(all_ids)
    st.progress(progress, text=f"{len(all_ids) - len(remaining)} of {len(all_ids)} completed")

    if not remaining:
        st.success("Diagnostic complete. Your first personalised skill map is ready.")
        if st.button("Open my dashboard", type="primary"):
            reset_question_state()
            st.session_state.page = "Dashboard"
            st.rerun()
        return

    if "active_question_id" not in st.session_state:
        st.session_state.active_question_id = remaining[0]
    render_question(get_question(st.session_state.active_question_id), "diagnostic")


def practice_page() -> None:
    st.title("Adaptive practice")
    attempts = get_attempts(DB_PATH, st.session_state.user_id)
    mastery = get_mastery(attempts)
    queue = build_practice_queue(attempts, mastery, count=10)

    if not queue:
        st.info("Complete the diagnostic to unlock your personalised practice queue.")
        return

    weakest = min(mastery, key=lambda skill: mastery[skill]["score"])
    st.caption(
        f"Today’s queue prioritises **{SKILL_LABELS[weakest]}**, currently your lowest-confidence skill."
    )

    if "active_question_id" not in st.session_state or st.session_state.active_question_id not in queue:
        st.session_state.active_question_id = queue[0]
    render_question(get_question(st.session_state.active_question_id), "practice")


def dashboard_page() -> None:
    st.title("Your skill map")
    attempts = get_attempts(DB_PATH, st.session_state.user_id)
    mastery = get_mastery(attempts)
    summary = readiness_summary(mastery)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Readiness index", f"{summary['readiness']}%")
    c2.metric("Questions answered", len(attempts))
    c3.metric("Strongest skill", SKILL_LABELS[summary["strongest"]])
    c4.metric("Focus next", SKILL_LABELS[summary["weakest"]])

    chart_df = pd.DataFrame(
        [
            {
                "Skill": SKILL_LABELS[skill],
                "Mastery": values["score"],
                "Attempts": values["attempts"],
            }
            for skill, values in mastery.items()
        ]
    ).sort_values("Mastery")
    fig = px.bar(
        chart_df,
        x="Mastery",
        y="Skill",
        orientation="h",
        color="Mastery",
        color_continuous_scale=["#d92d20", "#fdb022", "#12b76a"],
        range_color=[0, 100],
        text="Mastery",
    )
    fig.update_traces(texttemplate="%{text:.0f}%", textposition="outside")
    fig.update_layout(
        height=470,
        margin=dict(l=10, r=30, t=20, b=10),
        coloraxis_showscale=False,
        xaxis_title="Estimated mastery (%)",
        yaxis_title=None,
        plot_bgcolor="white",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Recommended next step")
    st.info(
        f"Practise **{SKILL_LABELS[summary['weakest']]}** next. "
        "The recommendation changes automatically as you answer more questions."
    )
    st.caption(
        "V1 mastery is an explainable practice indicator based on correctness, confidence and repeated attempts—not a certification or employment score."
    )


def cleaning_lab_page() -> None:
    st.title("CSV cleaning lab")
    st.write("Upload a CSV to profile common quality problems and create a cleaned copy.")
    uploaded = st.file_uploader("Upload a CSV file", type=["csv"])
    if uploaded is None:
        st.markdown(
            '<div class="soft-card">Your file stays within the running app session. V1 does not save uploaded datasets.</div>',
            unsafe_allow_html=True,
        )
        return

    try:
        df = pd.read_csv(uploaded)
    except Exception as exc:
        st.error(f"Pandas could not read this file: {exc}")
        return

    duplicate_count = int(df.duplicated().sum())
    missing_count = int(df.isna().sum().sum())
    text_columns = list(df.select_dtypes(include="object").columns)
    numeric_columns = list(df.select_dtypes(include="number").columns)

    a, b, c, d = st.columns(4)
    a.metric("Rows", f"{len(df):,}")
    b.metric("Columns", len(df.columns))
    c.metric("Missing cells", f"{missing_count:,}")
    d.metric("Duplicate rows", f"{duplicate_count:,}")

    with st.expander("Column quality report", expanded=True):
        report = pd.DataFrame(
            {
                "dtype": df.dtypes.astype(str),
                "missing": df.isna().sum(),
                "missing_%": (df.isna().mean() * 100).round(1),
                "unique": df.nunique(dropna=True),
            }
        )
        st.dataframe(report, use_container_width=True)

    st.subheader("Build a cleaned copy")
    remove_duplicates = st.checkbox("Remove duplicate rows", value=True)
    strip_text = st.checkbox("Strip leading/trailing whitespace from text columns", value=True)
    drop_empty = st.checkbox("Drop completely empty rows and columns", value=True)

    cleaned = df.copy()
    operations: list[str] = []
    if drop_empty:
        cleaned = cleaned.dropna(axis=0, how="all").dropna(axis=1, how="all")
        operations.append("Dropped completely empty rows and columns")
    if remove_duplicates:
        before = len(cleaned)
        cleaned = cleaned.drop_duplicates()
        operations.append(f"Removed {before - len(cleaned)} duplicate rows")
    if strip_text:
        for column in cleaned.select_dtypes(include="object").columns:
            cleaned[column] = cleaned[column].apply(lambda value: value.strip() if isinstance(value, str) else value)
        operations.append(f"Trimmed whitespace in {len(text_columns)} text columns")

    st.dataframe(cleaned.head(25), use_container_width=True)
    st.caption(" · ".join(operations) if operations else "No cleaning operations selected")
    st.download_button(
        "Download cleaned CSV",
        cleaned.to_csv(index=False).encode("utf-8"),
        file_name="cleaned_data.csv",
        mime="text/csv",
        type="primary",
    )
    if numeric_columns:
        st.caption(f"Numeric columns detected: {', '.join(numeric_columns[:8])}")


def login_page() -> None:
    render_hero()
    left, right = st.columns([1.35, 1])
    with left:
        st.subheader("Learn by finding the gaps")
        st.write(
            "This beta does not force you through a linear Pandas course. It measures eight practical "
            "data-cleaning skills, identifies weaker areas, and changes your practice queue accordingly."
        )
        st.markdown(
            """
            - Take a short diagnostic
            - See mastery by skill
            - Practise weak concepts first
            - Audit and clean a real CSV
            """
        )
    with right:
        with st.form("login_form"):
            st.subheader("Sign in")
            name = st.selectbox("Learner", list(DEMO_USERS))
            password = st.text_input("Password", type="password")
            start = st.form_submit_button("Enter GapMap →", type="primary", use_container_width=True)
        st.caption("Demo access: each learner’s password is the same as their displayed name.")
        if start:
            expected = DEMO_USERS[name]["password"]
            if not hmac.compare_digest(password, expected):
                st.error("Incorrect password.")
            else:
                goal = DEMO_USERS[name]["goal"]
                user_id = create_or_get_user(DB_PATH, name, goal)
                st.session_state.user_id = user_id
                st.session_state.user_name = name
                st.session_state.user_goal = goal
                st.session_state.page = "Diagnostic"
                st.rerun()


def main() -> None:
    init_db(DB_PATH)
    inject_css()

    if "user_id" not in st.session_state:
        login_page()
        return

    with st.sidebar:
        st.markdown("## 🧭 GapMap")
        st.caption(f"Learning as {st.session_state.user_name}")
        st.caption(f"Path: {st.session_state.user_goal}")
        pages = ["Diagnostic", "Practice", "Dashboard", "CSV Lab"]
        selected = st.radio(
            "Navigate",
            pages,
            index=pages.index(st.session_state.get("page", "Diagnostic")),
            label_visibility="collapsed",
        )
        if selected != st.session_state.get("page"):
            st.session_state.page = selected
            reset_question_state()
            st.rerun()
        st.divider()
        if st.button("Sign out", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    page = st.session_state.get("page", "Diagnostic")
    if page == "Diagnostic":
        diagnostic_page()
    elif page == "Practice":
        practice_page()
    elif page == "Dashboard":
        dashboard_page()
    else:
        cleaning_lab_page()


if __name__ == "__main__":
    main()
