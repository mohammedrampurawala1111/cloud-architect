---
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Skill, "Bash(python3:*)"]
runs: 3
---
Architect an IoT telemetry pipeline: 20,000 devices send a JSON reading every 10 seconds; we need real-time alerting on thresholds within 5 seconds, a 13-month history for dashboards, and a daily export to the finance team. Team: 5 engineers (Python, Go), solid AWS, containers 2/3, Terraform 2/3, no Kubernetes, an on-call rotation exists. Customers are in Australia.

I can't answer follow-up questions right now, so don't ask: make reasonable assumptions, list them, and finish. Don't write any files; put the complete design in your reply: requirements summary, an assessment of what my team can run, 2-3 options with trade-offs, your recommendation, the mapping to concrete cloud products, Mermaid diagrams (context and containers), the key decisions, a rough monthly cost per option, the availability and recovery targets the design must meet, and how someone could check that the built system follows each key decision.
