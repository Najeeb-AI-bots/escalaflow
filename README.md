"""
EscalaFlow — Autonomous Multi-Tier Escalation Agent
A Streamlit demo: monitors a queue of support cases, scores them by age &
severity, decides an escalation tier (T1 -> T2 -> T3), and auto-drafts a
tier-appropriate escalation email via an LLM.

All data is synthetic. No proprietary content.
"""

import os
import io
import pandas as pd
import streamlit as st

from scoring import score_cases, load_rules
from drafter import draft_email

st.set_page_config(page_title="EscalaFlow", page_icon="🔀", layout="wide")

# ---------- Header ----------
st.title("🔀 EscalaFlow — Autonomous Multi-Tier Escalation Agent")
st.caption(
    "Monitors a case queue, scores by age & severity, decides escalation tier "
    "(T1 → T2 → T3), and auto-drafts a tier-appropriate escalation email. "
    "Open-source demo · synthetic data only."
)

# ---------- Sidebar: config & data ----------
with st.sidebar:
    st.header("⚙️ Configuration")
    rules = load_rules()
    st.subheader("Tier thresholds (days)")
    rules["t1_days"] = st.number_input("Tier 1 after (days)", 1, 90, rules["t1_days"])
    rules["t2_days"] = st.number_input("Tier 2 after (days)", 1, 120, rules["t2_days"])
    rules["t3_days"] = st.number_input("Tier 3 after (days)", 1, 180, rules["t3_days"])

    st.subheader("LLM for drafting")
    provider = st.selectbox(
        "Provider",
        ["Template (no key, free)", "Anthropic Claude (bring your own key)"],
    )
    api_key = ""
    if provider.startswith("Anthropic"):
        api_key = st.text_input("Anthropic API key", type="password",
                                help="Your key is used only in this session and never stored.")

    st.markdown("---")
    uploaded = st.file_uploader("Upload a case queue CSV", type=["csv"],
                                help="Columns: case_id, opened_date, severity, status, owner, subject")
    use_sample = st.button("Load sample queue")

# ---------- Load data ----------
if uploaded is not None:
    df = pd.read_csv(uploaded)
elif use_sample or "df" not in st.session_state:
    df = pd.read_csv("sample_cases.csv")
else:
    df = st.session_state.get("df")

st.session_state["df"] = df

# ---------- Score ----------
scored = score_cases(df, rules)

# ---------- Summary metrics ----------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total cases", len(scored))
c2.metric("Tier 1", int((scored["tier"] == "T1").sum()))
c3.metric("Tier 2", int((scored["tier"] == "T2").sum()))
c4.metric("Tier 3", int((scored["tier"] == "T3").sum()))

# ---------- Queue table ----------
st.subheader("📋 Scored Case Queue")
tier_filter = st.multiselect("Filter by tier", ["T1", "T2", "T3", "OK"],
                             default=["T1", "T2", "T3"])
view = scored[scored["tier"].isin(tier_filter)].sort_values("score", ascending=False)


def _row_style(row):
    colors = {"T3": "#ffebe6", "T2": "#fff0e0", "T1": "#fffae6", "OK": "#e3fcef"}
    return [f"background-color: {colors.get(row['tier'], 'white')}"] * len(row)


st.dataframe(view.style.apply(_row_style, axis=1), use_container_width=True, hide_index=True)

# ---------- Draft generation ----------
st.subheader("✉️ Auto-Drafted Escalation Emails")
escalations = view[view["tier"].isin(["T1", "T2", "T3"])]
if escalations.empty:
    st.info("No cases currently require escalation under the configured thresholds.")
else:
    pick = st.selectbox(
        "Select a case to draft an escalation for",
        escalations["case_id"].tolist(),
    )
    case = escalations[escalations["case_id"] == pick].iloc[0].to_dict()
    if st.button("Generate escalation draft"):
        with st.spinner("Drafting…"):
            draft = draft_email(case, provider=provider, api_key=api_key)
        st.text_area("Draft email", draft, height=320)
        st.download_button("Download draft (.txt)", draft,
                           file_name=f"escalation_{pick}.txt")

st.markdown("---")
st.caption(
    "Built by Mohammed Abdul Najeeb · open-source demonstration of a production "
    "pattern (escalation automation serving 7,000+ users, ~80% manual-effort "
    "reduction). Synthetic data only."
)
