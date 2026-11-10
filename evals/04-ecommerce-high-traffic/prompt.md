---
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Skill, "Bash(python3:*)"]
runs: 3
---
Design an e-commerce platform for a fashion retailer: catalogue, search, cart, checkout, order management. Normal load 300 requests/second, flash sales up to 8,000 requests/second for 30 minutes. Team: 25 engineers, a 4-person platform team with solid Kubernetes and Terraform, 24/7 on-call. We're on GCP today. Customers are in the US.

I can't answer follow-up questions right now, so don't ask: make reasonable assumptions, list them, and finish. Don't write any files; put the complete design in your reply: requirements summary, an assessment of what my team can run, 2-3 options with trade-offs, your recommendation, the mapping to concrete cloud products, Mermaid diagrams (context and containers), the key decisions, a rough monthly cost per option, the availability and recovery targets the design must meet, and how someone could check that the built system follows each key decision.
