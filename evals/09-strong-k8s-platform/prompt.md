---
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Skill, "Bash(python3:*)"]
runs: 3
---
Design a multi-service logistics platform (route optimisation, tracking, partner APIs) for a company that already runs 40 services on Kubernetes. Team: 30 engineers, a 6-person platform team (expert Kubernetes 3/3, Argo CD, Terraform 3/3), 24/7 on-call, preference for control and portability across clouds. 2,000 requests/second peak. Customers are in the US and Mexico.

I can't answer follow-up questions right now, so don't ask: make reasonable assumptions, list them, and finish. Don't write any files; put the complete design in your reply: requirements summary, an assessment of what my team can run, 2-3 options with trade-offs, your recommendation, the mapping to concrete cloud products, Mermaid diagrams (context and containers), the key decisions, a rough monthly cost per option, the availability and recovery targets the design must meet, and how someone could check that the built system follows each key decision.
