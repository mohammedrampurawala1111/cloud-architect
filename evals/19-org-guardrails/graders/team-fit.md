---
type: llm
focus: last_message
weight: 1
---
PASS if the response explicitly assesses what this team can operate (size, skills, on-call) and the recommended option respects it: 4 engineers with on-call, solid AWS/Terraform, no Kubernetes. FAIL if it recommends Kubernetes or self-run search clusters without flagging the gap.
