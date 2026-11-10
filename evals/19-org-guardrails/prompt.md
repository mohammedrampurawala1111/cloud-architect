---
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Skill, "Bash(python3:*)"]
runs: 3
---
Design a document-search service for our internal knowledge base: employees upload PDFs and Word files, we extract text, and they search it with keyword and semantic search. 2,000 employees, about 5 searches/second at peak, 400 GB of documents. Team: 4 engineers (Python), solid AWS, Terraform 2/3, containers 2/3, no Kubernetes, an on-call rotation of 2. Our platform team's guardrails, which every design must follow or get an explicit exception for: AWS only; regions eu-west-1 and eu-central-1 only; approved services ECS on Fargate, Lambda, RDS for PostgreSQL, S3, SQS, CloudFront and Cognito; no self-hosted databases. Offices are in Ireland and Germany.

I can't answer follow-up questions right now, so don't ask: make reasonable assumptions, list them, and finish. Don't write any files; put the complete design in your reply: requirements summary, an assessment of what my team can run, 2-3 options with trade-offs, your recommendation, the mapping to concrete cloud products, Mermaid diagrams (context and containers), the key decisions, a rough monthly cost per option, the availability and recovery targets the design must meet, and how someone could check that the built system follows each key decision.
