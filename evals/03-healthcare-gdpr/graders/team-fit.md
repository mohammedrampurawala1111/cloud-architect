---
type: llm
focus: last_message
weight: 1
---
PASS if the response explicitly assesses what this team can operate (size, skills, on-call) and the recommended option respects it: 4 developers, no Kubernetes, no on-call. FAIL if it recommends Kubernetes or self-run infrastructure.
