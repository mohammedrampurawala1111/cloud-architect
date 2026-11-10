---
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Skill, "Bash(python3:*)"]
runs: 3
---
I'm a DevOps engineer and I have to present an architecture plan to our CTO, who will make the final call. We're building a customer-support ticketing system for our SaaS: web app, email ingestion, file attachments, full-text search, about 40 requests/second at peak. Team: 5 developers (Python, Django), solid AWS and Terraform, containers 2/3, no Kubernetes, an on-call rotation of 2. Customers are in the US. Put the decision brief for the CTO in your reply too.

I can't answer follow-up questions right now, so don't ask: make reasonable assumptions, list them, and finish. Don't write any files; put the complete design in your reply: requirements summary, an assessment of what my team can run, 2-3 options with trade-offs, your recommendation, the mapping to concrete cloud products, Mermaid diagrams (context and containers), the key decisions, a rough monthly cost per option, the availability and recovery targets the design must meet, and how someone could check that the built system follows each key decision.
