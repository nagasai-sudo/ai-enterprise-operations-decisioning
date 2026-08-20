
from __future__ import annotations

import json
import urllib.request
from typing import Dict, Any


def build_grounded_prompt(payload: Dict[str, Any]) -> str:
    """
    Build a prompt that tells a language model to summarize ONLY structured facts
    already produced by the predictive/anomaly/rules layers.

    The LLM is not allowed to invent a root cause or claim that an action will
    definitely solve the problem.
    """
    return f"""
You are assisting an enterprise operations analyst.

Use ONLY the structured evidence below. Do not invent causes, metrics, or facts.
Do not claim certainty. Do not automatically authorize any operational action.
Your job is to:
1. explain the risk in concise business language;
2. summarize the evidence;
3. present the recommended actions as options for human review;
4. explicitly state that a human should validate the recommendation.

Structured evidence:
{json.dumps(payload, indent=2)}

Return:
- 2-3 sentence explanation
- 3-5 concise recommended actions
- one sentence stating that human validation is required
""".strip()


def generate_with_ollama(prompt: str, model: str = "llama3.1:8b", host: str = "http://localhost:11434") -> str:
    """
    Optional local GenAI integration using an Ollama-compatible local endpoint.
    If you do not run a local model, the Streamlit app falls back to the
    deterministic grounded explanation from decision_support.py.
    """
    body = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{host}/api/generate",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=60) as response:
        data = json.loads(response.read().decode("utf-8"))

    return data.get("response", "").strip()
