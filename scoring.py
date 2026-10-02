"""
scoring.py — transparent rules engine for EscalaFlow.
Scores each case by age and severity, then assigns an escalation tier.
No LLM involved here — the tier decision is fully explainable.
"""

from datetime import datetime
import pandas as pd
import yaml
import os

DEFAULT_RULES = {
    "t1_days": 7,     # escalate to Tier 1 (team lead) after N days open
    "t2_days": 14,    # escalate to Tier 2 (manager) after N days
    "t3_days": 30,    # escalate to Tier 3 (senior leadership) after N days
    "severity_weights": {"low": 1, "medium": 2, "high": 3, "critical": 4},
}


def load_rules(path: str = "rules.yaml") -> dict:
    """Load tier rules from YAML, falling back to sensible defaults."""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            loaded = yaml.safe_load(f) or {}
        rules = {**DEFAULT_RULES, **loaded}
    else:
        rules = dict(DEFAULT_RULES)
    return rules


def _age_days(opened_date: str, today: datetime | None = None) -> int:
    today = today or datetime.now()
    try:
        opened = pd.to_datetime(opened_date)
        return max(0, (today - opened).days)
    except Exception:
        return 0


def _tier_for(age: int, severity: str, rules: dict) -> tuple[str, int]:
    """Return (tier, score). Score blends age and severity for ranking."""
    sev_w = rules["severity_weights"].get(str(severity).lower(), 1)
    # severity accelerates escalation: effective age = age * severity multiplier
    effective = age * (1 + 0.25 * (sev_w - 1))
    score = round(effective + sev_w * 5, 1)

    if effective >= rules["t3_days"]:
        tier = "T3"
    elif effective >= rules["t2_days"]:
        tier = "T2"
    elif effective >= rules["t1_days"]:
        tier = "T1"
    else:
        tier = "OK"
    return tier, score


def score_cases(df: pd.DataFrame, rules: dict, today: datetime | None = None) -> pd.DataFrame:
    """Add age_days, tier, and score columns to the case queue."""
    out = df.copy()
    out["age_days"] = out["opened_date"].apply(lambda d: _age_days(d, today))
    tiers, scores = [], []
    for _, row in out.iterrows():
        tier, score = _tier_for(row["age_days"], row.get("severity", "low"), rules)
        tiers.append(tier)
        scores.append(score)
    out["tier"] = tiers
    out["score"] = scores
    return out
