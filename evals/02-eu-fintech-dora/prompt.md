---
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Skill, "Bash(python3:*)"]
runs: 3
---
Design the platform for a German payments startup: card-payment processing API, ledger, merchant dashboard, fraud scoring. 500 TPS peak, 99.95% availability, RPO 0 for the ledger. We are a regulated financial entity under DORA and BaFin supervision, and customer data must stay in the EU. Team: 10 engineers, 3 of them do ops with an on-call rotation, solid Terraform and containers, some Kubernetes (1 on a 0-3 scale), mostly Java/Kotlin; no dedicated platform team.

I can't answer follow-up questions right now, so don't ask: make reasonable assumptions, list them, and finish. Don't write any files; put the complete design in your reply: requirements summary, an assessment of what my team can run, 2-3 options with trade-offs, your recommendation, the mapping to concrete cloud products, Mermaid diagrams (context and containers), the key decisions, a rough monthly cost per option, the availability and recovery targets the design must meet, and how someone could check that the built system follows each key decision.
