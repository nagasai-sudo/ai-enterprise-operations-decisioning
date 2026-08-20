
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List, Dict, Any


@dataclass
class DecisionSupportResult:
    risk_level: str
    breach_probability: float
    anomaly_detected: bool
    contributing_factors: List[str]
    recommended_actions: List[str]
    explanation: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def derive_risk_level(probability: float, high_threshold: float, medium_ratio: float = 0.60) -> str:
    medium_threshold = high_threshold * medium_ratio
    if probability >= high_threshold:
        return "High"
    if probability >= medium_threshold:
        return "Medium"
    return "Low"


def extract_contributing_factors(row) -> List[str]:
    factors: List[str] = []

    if row.get("SLA_Change_1D", 0) < -1:
        factors.append("SLA performance declined from the prior period")
    if row.get("Backlog_Change_1D", 0) > 100:
        factors.append("Backlog is increasing")
    if row.get("Processing_Time_Change_1D", 0) > 0.5:
        factors.append("Average processing time is increasing")
    if row.get("Error_Rate_Change_1D", 0) > 0.5:
        factors.append("Error rate is increasing")
    if row.get("SLA_Compliance_Pct", 100) < 96:
        factors.append("Current SLA performance is below the preferred operating range")
    if row.get("Error_Rate_Pct", 0) > 3:
        factors.append("Current error rate is elevated")
    if row.get("Average_Processing_Time_Min", 0) > 8:
        factors.append("Current processing time is elevated")
    if row.get("Backlog", 0) > 1500:
        factors.append("Current backlog is elevated")

    if not factors:
        factors.append("No major rule-based contributing factor was detected")

    return factors


def recommend_actions(factors: List[str], risk_level: str, anomaly_detected: bool) -> List[str]:
    actions: List[str] = []

    joined = " ".join(factors).lower()

    if "backlog" in joined:
        actions.append("Review the affected work queue and identify the largest backlog contributors")
    if "processing time" in joined:
        actions.append("Investigate recent processing delays, bottlenecks, or unusually slow work types")
    if "error rate" in joined:
        actions.append("Review recent exceptions and error categories for a potential quality or process issue")
    if "sla" in joined:
        actions.append("Prioritize near-term work that has the greatest potential to affect SLA performance")

    if anomaly_detected:
        actions.append("Compare the current period with recent historical patterns to validate the anomaly")

    if risk_level == "High":
        actions.append("Escalate the condition for human review before taking operational action")
    elif risk_level == "Medium":
        actions.append("Monitor the next reporting period closely and investigate if deterioration continues")
    else:
        actions.append("Continue routine monitoring; no immediate intervention is recommended")

    # preserve order while removing duplicates
    return list(dict.fromkeys(actions))


def build_explanation(
    business_unit: str,
    risk_level: str,
    breach_probability: float,
    anomaly_detected: bool,
    factors: List[str],
) -> str:
    probability_pct = breach_probability * 100
    factor_text = "; ".join(factors)

    if risk_level == "High":
        opening = (
            f"{business_unit} is currently classified as high risk, with an estimated "
            f"{probability_pct:.1f}% probability of an SLA breach in the next reporting period."
        )
    elif risk_level == "Medium":
        opening = (
            f"{business_unit} shows a moderate level of operational risk, with an estimated "
            f"{probability_pct:.1f}% probability of an SLA breach in the next reporting period."
        )
    else:
        opening = (
            f"{business_unit} is currently classified as low risk, with an estimated "
            f"{probability_pct:.1f}% probability of an SLA breach in the next reporting period."
        )

    anomaly_text = (
        " The anomaly detector also flagged the current observation as unusual."
        if anomaly_detected
        else " The anomaly detector did not flag the current observation as unusual."
    )

    return f"{opening}{anomaly_text} Key contributing evidence: {factor_text}."


def build_decision_support(
    row,
    breach_probability: float,
    anomaly_detected: bool,
    high_threshold: float,
) -> DecisionSupportResult:
    business_unit = str(row.get("Business_Unit", "Selected business unit"))
    risk_level = derive_risk_level(breach_probability, high_threshold)
    factors = extract_contributing_factors(row)
    actions = recommend_actions(factors, risk_level, anomaly_detected)
    explanation = build_explanation(
        business_unit=business_unit,
        risk_level=risk_level,
        breach_probability=breach_probability,
        anomaly_detected=anomaly_detected,
        factors=factors,
    )

    return DecisionSupportResult(
        risk_level=risk_level,
        breach_probability=breach_probability,
        anomaly_detected=anomaly_detected,
        contributing_factors=factors,
        recommended_actions=actions,
        explanation=explanation,
    )
