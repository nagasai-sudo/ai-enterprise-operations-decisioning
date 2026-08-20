
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

from decision_support import build_decision_support
from genai import build_grounded_prompt, generate_with_ollama

BASE = Path(__file__).resolve().parent

st.set_page_config(
    page_title="AI-Assisted Enterprise Operations Decisioning",
    page_icon="📊",
    layout="wide",
)

st.title("AI-Assisted Enterprise Operations Decisioning")
st.caption(
    "Independent proof of concept using synthetic data. "
    "Predictions and recommendations are for demonstration only."
)

@st.cache_data
def load_results():
    df = pd.read_csv(BASE / "step3_test_results.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    return df

@st.cache_resource
def load_model():
    return joblib.load(BASE / "step3_best_sla_model.joblib")

df = load_results()
_ = load_model()  # loaded so the app package includes the trained predictive artifact

# Threshold chosen during Step 3 using validation data only.
HIGH_THRESHOLD = 0.46

with st.sidebar:
    st.header("Select operating context")
    units = sorted(df["Business_Unit"].dropna().unique())
    unit = st.selectbox("Business unit", units)

    unit_df = df[df["Business_Unit"] == unit].sort_values("Date")
    selected_date = st.selectbox(
        "Reporting date",
        list(unit_df["Date"].dt.strftime("%Y-%m-%d")),
        index=len(unit_df) - 1,
    )

    st.divider()
    use_local_llm = st.checkbox("Use local GenAI summary (optional)")
    local_model = st.text_input("Local model name", value="llama3.1:8b")

row = unit_df[unit_df["Date"].dt.strftime("%Y-%m-%d") == selected_date].iloc[0]

prob = float(row["SLA_Breach_Probability"])
anomaly = bool(row["Anomaly_Flag"])

result = build_decision_support(
    row=row,
    breach_probability=prob,
    anomaly_detected=anomaly,
    high_threshold=HIGH_THRESHOLD,
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Risk Level", result.risk_level)
col2.metric("Next-Period Breach Probability", f"{result.breach_probability:.1%}")
col3.metric("Current SLA", f"{row['SLA_Compliance_Pct']:.1f}%")
col4.metric("Anomaly Detected", "Yes" if result.anomaly_detected else "No")

st.subheader("Operational context")
context_cols = st.columns(4)
context_cols[0].metric("Transaction Volume", f"{int(row['Transaction_Volume']):,}")
context_cols[1].metric("Backlog", f"{int(row['Backlog']):,}")
context_cols[2].metric("Processing Time", f"{row['Average_Processing_Time_Min']:.2f} min")
context_cols[3].metric("Error Rate", f"{row['Error_Rate_Pct']:.2f}%")

st.subheader("Why this condition was flagged")
for factor in result.contributing_factors:
    st.write(f"- {factor}")

payload = result.to_dict()
payload["business_unit"] = unit
payload["date"] = selected_date
payload["current_sla_pct"] = float(row["SLA_Compliance_Pct"])

st.subheader("Decision-support explanation")
if use_local_llm:
    try:
        prompt = build_grounded_prompt(payload)
        ai_text = generate_with_ollama(prompt, model=local_model)
        if ai_text:
            st.info(ai_text)
        else:
            st.info(result.explanation)
            st.caption("Local model returned no text; showing deterministic grounded explanation.")
    except Exception as exc:
        st.info(result.explanation)
        st.caption(
            "Local GenAI was unavailable, so the app used the deterministic grounded explanation. "
            f"Technical detail: {exc}"
        )
else:
    st.info(result.explanation)

st.subheader("Recommended actions for human review")
for i, action in enumerate(result.recommended_actions, start=1):
    st.write(f"{i}. {action}")

st.subheader("Human decision")
decision = st.radio(
    "Select the analyst response",
    ["Investigate", "Accept recommendation", "Dismiss / no action"],
    horizontal=True,
)

notes = st.text_area("Reviewer notes", placeholder="Document why this decision was made...")

if st.button("Record review decision"):
    st.success(
        f"Review recorded for demonstration: {decision}. "
        "This prototype does not execute downstream operational actions."
    )

st.divider()
with st.expander("Responsible-AI design notes"):
    st.markdown(
        """
- The dataset is synthetic and contains no employer or client data.
- The prediction is probabilistic, not a statement of certainty.
- The anomaly detector is a separate signal from the supervised SLA-risk model.
- Explanations are grounded in structured evidence produced by the data/model layer.
- The optional language-model layer is instructed not to invent causes or authorize action.
- A human reviewer remains responsible for the final decision.
- Prototype model metrics must not be represented as real-world business impact.
        """
    )

with st.expander("Model limitations"):
    st.markdown(
        """
This is a proof of concept built on synthetic data. The current test set is small,
especially for the positive SLA-breach class. Model performance should therefore
be interpreted only as a demonstration of the architecture and evaluation process,
not as evidence of production readiness.
        """
    )
