---
max_turns: 30
timeout_seconds: 900
fixture: ../../tools/fixtures/fieldservice
allowed_tools: [Read, Glob, Grep, Skill, "Bash(python3:*)"]
runs: 3
---
This repository is our field-service scheduling API (multi-tenant SaaS, about 200 customer companies, 2,000 jobs a day). We want to add a feature: when a technician sets a job to 'on the way', the customer gets an SMS with a link to a live ETA page they can open without logging in, and the ETA updates as the technician moves. Design how to add this to the existing system. Our team is the 3 TypeScript developers in the README, no on-call rotation; customers are in the US.

I can't answer follow-up questions right now, so don't ask: make reasonable assumptions, list them, and finish. Don't write or change any files; put the design in your reply: how the existing system is built (with file references), 2-3 options with trade-offs, your recommendation, what changes where, data and API changes, how it rolls out safely, Mermaid diagrams (as-is and to-be), a rough monthly cost delta, and the key decisions with how someone could check each one is followed.
