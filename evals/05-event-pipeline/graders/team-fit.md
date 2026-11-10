---
type: llm
focus: last_message
weight: 1
---
PASS if the response explicitly assesses what this team can operate (size, skills, on-call) and the recommended option respects it: 5 engineers with on-call and solid AWS/Terraform but no Kubernetes. FAIL if it recommends self-run Kafka/Flink or Kubernetes without flagging the gap.
