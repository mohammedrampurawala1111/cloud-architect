---
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Skill, "Bash(python3:*)"]
runs: 3
---
Design a public pricing API for a travel-booking marketplace used worldwide: reads must return in under 50 ms p95 in North America, Europe and Asia; prices change every few minutes; 10,000 requests/second at peak. Team: 12 engineers, on-call, solid containers and Terraform, some Kubernetes. No data-residency requirements: prices are not personal data.

I can't answer follow-up questions right now, so don't ask: make reasonable assumptions, list them, and finish. Don't write any files; put the complete design in your reply: requirements summary, an assessment of what my team can run, 2-3 options with trade-offs, your recommendation, the mapping to concrete cloud products, Mermaid diagrams (context and containers), the key decisions, a rough monthly cost per option, the availability and recovery targets the design must meet, and how someone could check that the built system follows each key decision.
