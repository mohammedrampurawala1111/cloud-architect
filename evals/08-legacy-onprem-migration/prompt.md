---
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Skill, "Bash(python3:*)"]
runs: 3
---
We need to move a 15-year-old on-prem order-management system to the cloud: a Java monolith on two VMs, Oracle database (800 GB), nightly batch jobs, and a file share used by partners via SFTP. We have 18 months and must keep the business running. Team: 6 developers, 2 sysadmins with VMware experience, an on-call rotation, no cloud experience yet, no Kubernetes. Customers are in the US.

I can't answer follow-up questions right now, so don't ask: make reasonable assumptions, list them, and finish. Don't write any files; put the complete design in your reply: requirements summary, an assessment of what my team can run, 2-3 options with trade-offs, your recommendation, the mapping to concrete cloud products, Mermaid diagrams (context and containers), the key decisions, a rough monthly cost per option, the availability and recovery targets the design must meet, and how someone could check that the built system follows each key decision.
