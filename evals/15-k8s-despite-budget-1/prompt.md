---
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Skill, "Bash(python3:*)"]
runs: 3
---
We want Kubernetes for our new booking API. We are 2 junior developers (Node.js), nobody has used Kubernetes or Terraform, there is no on-call, and we prefer managed services in general — but our CTO read that Kubernetes is the industry standard, so design it on Kubernetes (EKS). Traffic: 20 requests/second. Customers are in the US.

I can't answer follow-up questions right now, so don't ask: make reasonable assumptions, list them, and finish. Don't write any files; put the complete design in your reply: requirements summary, an assessment of what my team can run, 2-3 options with trade-offs, your recommendation, the mapping to concrete cloud products, Mermaid diagrams (context and containers), the key decisions, a rough monthly cost per option, the availability and recovery targets the design must meet, and how someone could check that the built system follows each key decision.
