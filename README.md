
# AI-Assisted Enterprise Operations Decisioning

An independent proof-of-concept demonstrating how predictive analytics, anomaly detection,
structured decision logic, optional generative AI, and human review can be combined in an
enterprise-style workflow.

## Why this project exists

Traditional automation often stops after data collection, transformation, validation, and reporting.
This project explores the next layer:

**Data → Validation → Prediction → Anomaly Detection → Explanation → Recommendation → Human Review**

The prototype uses **synthetic data only**. It contains no employer or client information.

## Core use case

Predict whether a synthetic business unit is likely to breach a 95% SLA threshold in the next
reporting period and surface the result to a human analyst with supporting evidence and recommended actions.

## Components

- Synthetic enterprise operations dataset
- Chronological train / validation / test split
- Time-based feature engineering
- SLA-breach prediction model
- Isolation Forest anomaly detector
- Structured contributing-factor logic
- Human-review recommendations
- Optional locally hosted generative-AI summary
- Streamlit demonstration interface

## Current model evaluation

The threshold was selected using the validation set only. The test set was then used for final evaluation.

See:
- `step3_model_comparison.csv`
- `step3_anomaly_evaluation.csv`

Because this is synthetic proof-of-concept data and the positive test class is small,
the metrics must not be interpreted as production performance.

## Run locally

1. Create and activate a Python environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the app:

```bash
streamlit run app.py
```

## Optional local GenAI

The app works without a language model by using a deterministic, grounded explanation.

If you have a local Ollama-compatible model running, enable the "Use local GenAI summary" option in the sidebar.
The LLM receives only structured evidence that was already produced by the prediction/anomaly/rules layer.

## Responsible-AI design

This prototype intentionally keeps a human in the loop:

- predictions are probabilistic;
- anomaly detection is treated as a supporting signal;
- explanations are grounded in structured evidence;
- recommended actions are options, not automatic commands;
- no downstream operational action is executed by the app;
- the human reviewer records the final decision.

## Repository purpose

This project is intended as a technical learning and demonstration artifact for AI-assisted
enterprise workflow decisioning using non-confidential data.
