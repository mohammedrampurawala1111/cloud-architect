---
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Skill, "Bash(python3:*)"]
runs: 3
---
Architect a batch-heavy analytics platform for a retail chain: 2 TB of sales and inventory data lands nightly as CSV/Parquet from 400 stores; analysts run SQL and dashboards in the morning; a weekly demand-forecast model runs for 3 hours. Team: 4 data engineers (SQL, Python, dbt), some AWS and some GCP, no Kubernetes, no on-call (failures can wait until morning). The company is in the US.

I can't answer follow-up questions right now, so don't ask: make reasonable assumptions, list them, and finish. Don't write any files; put the complete design in your reply: requirements summary, an assessment of what my team can run, 2-3 options with trade-offs, your recommendation, the mapping to concrete cloud products, Mermaid diagrams (context and containers), the key decisions, a rough monthly cost per option, the availability and recovery targets the design must meet, and how someone could check that the built system follows each key decision.
