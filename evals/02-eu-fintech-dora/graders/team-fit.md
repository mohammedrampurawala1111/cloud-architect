---
type: llm
focus: last_message
weight: 1
---
PASS if the response explicitly assesses what this team can operate (size, skills, on-call) and the recommended option respects it: 10 engineers with on-call and solid Terraform/containers but limited Kubernetes. FAIL if it recommends self-run databases, a service mesh or a self-managed Kubernetes control plane without flagging the team gap.
