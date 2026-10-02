"""
drafter.py — generates a tier-appropriate escalation email.

Two modes:
  - "Template" : no API key, fully free. Deterministic, structured draft.
  - "Anthropic Claude" : bring-your-own-key. Richer, LLM-written draft.

The template mode means the public demo costs nothing to run and always works.
"""

TIER_META = {
    "T1": {"to": "Team Lead", "urgency": "Please review", "sla": "within 2 business days"},
    "T2": {"to": "Operations Manager", "urgency": "Needs attention", "sla": "within 1 business day"},
    "T3": {"to": "Senior Leadership", "urgency": "URGENT — SLA breach risk", "sla": "today"},
}


def _template_draft(case: dict) -> str:
    meta = TIER_META.get(case["tier"], TIER_META["T1"])
    return f"""To: {meta['to']}
Subject: [{case['tier']}] Escalation — Case {case['case_id']} ({meta['urgency']})

Hello,

Escalating the following case for your review ({meta['urgency'].lower()}):

  • Case ID    : {case['case_id']}
  • Subject    : {case.get('subject', 'N/A')}
  • Severity   : {str(case.get('severity', 'N/A')).title()}
  • Age        : {case['age_days']} days open
  • Current owner : {case.get('owner', 'Unassigned')}
  • Status     : {case.get('status', 'Open')}

This case has crossed the {case['tier']} escalation threshold. Requested action: please
review and advise on next steps {meta['sla']} to keep us within SLA.

Thank you,
EscalaFlow (automated escalation agent)
"""


def _claude_draft(case: dict, api_key: str) -> str:
    """Use Anthropic Claude if a key is supplied. Falls back to template on error."""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        meta = TIER_META.get(case["tier"], TIER_META["T1"])
        prompt = (
            f"Write a concise, professional internal escalation email.\n"
            f"Recipient role: {meta['to']}. Urgency: {meta['urgency']}. "
            f"Required response window: {meta['sla']}.\n"
            f"Case details: {case}.\n"
            f"Keep it under 150 words. Plain text. No markdown."
        )
        msg = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text
    except Exception as e:
        return _template_draft(case) + f"\n\n[Note: LLM draft unavailable ({e}); used template.]"


def draft_email(case: dict, provider: str = "Template", api_key: str = "") -> str:
    if provider.startswith("Anthropic") and api_key:
        return _claude_draft(case, api_key)
    return _template_draft(case)
