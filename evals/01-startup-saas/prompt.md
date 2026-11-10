---
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Skill, "Bash(python3:*)"]
runs: 3
---
Help me architect a B2B SaaS for scheduling field-service technicians: web app, REST API, nightly report generation, email notifications. Expect 200 customer companies and about 30 requests/second at peak in year one. We are 3 developers (TypeScript, some AWS experience, no Kubernetes, no on-call rotation) and want to run as little infrastructure as possible. Customers are in the US and Canada.

I can't answer follow-up questions right now, so don't ask: make reasonable assumptions, list them, and finish. Don't write any files; put the complete design in your reply: requirements summary, an assessment of what my team can run, 2-3 options with trade-offs, your recommendation, the mapping to concrete cloud products, Mermaid diagrams (context and containers), the key decisions, a rough monthly cost per option, the availability and recovery targets the design must meet, and how someone could check that the built system follows each key decision.
