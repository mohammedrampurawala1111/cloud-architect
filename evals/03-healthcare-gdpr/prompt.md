---
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Skill, "Bash(python3:*)"]
runs: 3
---
We're building a telehealth app in the Netherlands: patients book video consultations, upload photos of symptoms, and doctors write notes. This is GDPR special-category health data. Around 20k patients in year one. Team: 4 developers (Python, React), one has solid Azure experience, nobody has Kubernetes, no on-call. Video calls can use a third-party video API.

I can't answer follow-up questions right now, so don't ask: make reasonable assumptions, list them, and finish. Don't write any files; put the complete design in your reply: requirements summary, an assessment of what my team can run, 2-3 options with trade-offs, your recommendation, the mapping to concrete cloud products, Mermaid diagrams (context and containers), the key decisions, a rough monthly cost per option, the availability and recovery targets the design must meet, and how someone could check that the built system follows each key decision.
