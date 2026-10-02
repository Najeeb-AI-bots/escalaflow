# 🔀 EscalaFlow — Autonomous Multi-Tier Escalation Agent

> An AI agent that monitors a queue of support cases, scores them by age and severity, decides the correct escalation tier (T1 → T2 → T3), and auto-drafts a tier-appropriate escalation email — running on a schedule, hands-free.

**Live demo:** _https://escalaflow.streamlit.app_· **Built by:** [Mohammed Abdul Najeeb](https://github.com/Najeeb-AI-bots)

> 💡 This is an open-source demonstration of a pattern I built in production at Amazon — an autonomous escalation system serving 7,000+ users that cut manual escalation effort by ~80%. All data here is synthetic.

---

## What it does

1. **Ingests** a queue of cases (synthetic CSV: case ID, age, severity, status, owner)
2. **Scores** each case against configurable rules (age thresholds, severity, SLA breach risk)
3. **Decides** the escalation tier using a transparent rules engine (T1 → T2 → T3)
4. **Drafts** a tier-appropriate escalation email via an LLM (AWS Bedrock / Claude, or bring-your-own-key)
5. **Displays** the live queue + generated drafts in a Streamlit dashboard

## Why it matters

Manual case escalation is slow, inconsistent, and error-prone. EscalaFlow shows how an agent can monitor continuously, apply consistent tier logic, and produce ready-to-send drafts — freeing humans to decide, not draft.

## Architecture

```
cases.csv ──▶ Scoring Engine ──▶ Tier Decision ──▶ LLM Draft Generator ──▶ Streamlit UI
                 (rules.yaml)        (T1/T2/T3)        (Bedrock/Claude)
```

## Tech stack

- **Python** — agent loop + scoring
- **AWS Bedrock → Claude** (or bring-your-own API key) — email drafting
- **YAML** — configurable tier rules
- **Streamlit** — live dashboard UI

## Run locally

```bash
git clone https://github.com/Najeeb-AI-bots/escalaflow
cd escalaflow
pip install -r requirements.txt
streamlit run app.py
```

Set your LLM key as an environment variable (never commit it):
```bash
export ANTHROPIC_API_KEY=your_key_here   # or configure AWS Bedrock creds
```

## Skills demonstrated

Agentic orchestration · Rules-based decisioning · Prompt engineering · Structured LLM output · Scheduled automation · Dashboard UI

## License

MIT — synthetic data only, no proprietary content.
