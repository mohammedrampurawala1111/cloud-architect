---
type: llm
focus: last_message
weight: 1
---
PASS if the response explicitly assesses what this team can operate (size, skills, on-call) and the recommended option respects it: 4 people without Kubernetes or on-call. FAIL if it recommends self-managed GPU clusters on Kubernetes without flagging that the team cannot run it.
