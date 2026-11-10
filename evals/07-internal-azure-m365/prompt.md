---
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Skill, "Bash(python3:*)"]
runs: 3
---
Architect an internal expense-approval tool for a 3,000-employee company that runs on Microsoft 365 and Entra ID, with an existing Azure enterprise agreement. Employees submit receipts (photos/PDFs), managers approve in Teams, finance exports to the ERP nightly. Team: 2 .NET developers, solid Azure DevOps, some Bicep, no Kubernetes, no on-call (business-hours support only). Offices in the US.

I can't answer follow-up questions right now, so don't ask: make reasonable assumptions, list them, and finish. Don't write any files; put the complete design in your reply: requirements summary, an assessment of what my team can run, 2-3 options with trade-offs, your recommendation, the mapping to concrete cloud products, Mermaid diagrams (context and containers), the key decisions, a rough monthly cost per option, the availability and recovery targets the design must meet, and how someone could check that the built system follows each key decision.
