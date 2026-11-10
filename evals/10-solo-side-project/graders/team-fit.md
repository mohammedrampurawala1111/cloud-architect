---
type: llm
focus: last_message
weight: 1
---
PASS if the response explicitly assesses what this team can operate (size, skills, on-call) and the recommended option respects it: one person with no time for operations and a $50/month budget. FAIL if it recommends Kubernetes, multiple services or anything needing on-call, or if the recommended option's estimated infra cost exceeds $50/month.
