---
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Skill, "Bash(python3:*)"]
runs: 3
---
Design a multi-tenant B2B SaaS for HR performance reviews: 300 tenant companies, largest has 20,000 employees, tenants want SSO (SAML/OIDC), strict tenant isolation, and a few large tenants want a dedicated database. All customers are in the EU and contracts require EU data residency. Team: 7 engineers (TypeScript, Go), on-call rotation, solid containers and Terraform, no Kubernetes.

I can't answer follow-up questions right now, so don't ask: make reasonable assumptions, list them, and finish. Don't write any files; put the complete design in your reply: requirements summary, an assessment of what my team can run, 2-3 options with trade-offs, your recommendation, the mapping to concrete cloud products, Mermaid diagrams (context and containers), the key decisions, a rough monthly cost per option, the availability and recovery targets the design must meet, and how someone could check that the built system follows each key decision.
