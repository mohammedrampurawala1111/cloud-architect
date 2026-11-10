---
type: llm
focus: last_message
weight: 1
---
PASS if the response explicitly assesses what this team can operate (size, skills, on-call) and the recommended option respects it: a 3-person team with no Kubernetes experience and no on-call. FAIL if the recommendation is Kubernetes, self-managed servers or microservices.
