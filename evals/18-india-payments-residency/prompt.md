---
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Skill, "Bash(python3:*)"]
runs: 3
---
Design a UPI and card payments gateway for Indian merchants: payment API, merchant dashboard, settlement batch jobs, fraud rules. 300 TPS peak, 99.95% availability. We must follow RBI rules on payment data and PCI DSS, and we plan to add customers in Singapore next year. Team: 8 engineers (Java, Go), on-call rotation, solid AWS and Terraform, some Kubernetes (1 on a 0-3 scale).

I can't answer follow-up questions right now, so don't ask: make reasonable assumptions, list them, and finish. Don't write any files; put the complete design in your reply: requirements summary, an assessment of what my team can run, 2-3 options with trade-offs, your recommendation, the mapping to concrete cloud products, Mermaid diagrams (context and containers), the key decisions, a rough monthly cost per option, the availability and recovery targets the design must meet, and how someone could check that the built system follows each key decision.
