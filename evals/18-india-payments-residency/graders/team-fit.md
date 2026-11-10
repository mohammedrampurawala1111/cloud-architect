---
type: llm
focus: last_message
weight: 1
---
PASS if the response explicitly assesses what this team can operate (size, skills, on-call) and the recommended option respects it: 8 engineers with on-call and solid AWS/Terraform, limited Kubernetes. FAIL if it recommends self-run databases or a self-managed control plane without flagging the gap.
