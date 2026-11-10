---
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Skill, "Bash(python3:*)"]
runs: 3
---
Design a public API that serves a fine-tuned 8B-parameter open-weight language model for document classification: 50 requests/second at peak, p95 under 1.5 s, traffic mostly in business hours. Team: 3 ML engineers (Python, PyTorch) and 1 backend developer, some GCP, no Kubernetes, no on-call. Users are in the US.

I can't answer follow-up questions right now, so don't ask: make reasonable assumptions, list them, and finish. Don't write any files; put the complete design in your reply: requirements summary, an assessment of what my team can run, 2-3 options with trade-offs, your recommendation, the mapping to concrete cloud products, Mermaid diagrams (context and containers), the key decisions, a rough monthly cost per option, the availability and recovery targets the design must meet, and how someone could check that the built system follows each key decision.
