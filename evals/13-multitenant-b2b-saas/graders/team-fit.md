---
type: llm
focus: last_message
weight: 1
---
PASS if the response explicitly assesses what this team can operate (size, skills, on-call) and the recommended option respects it: 7 engineers with on-call, solid containers/Terraform, no Kubernetes. FAIL if it recommends Kubernetes without flagging the skills gap.
