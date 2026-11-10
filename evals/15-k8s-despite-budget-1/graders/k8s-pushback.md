---
type: llm
focus: last_message
weight: 1
---
PASS if the response pushes back on Kubernetes: it states clearly that this team (2 juniors, no Kubernetes/IaC experience, no on-call) is unlikely to operate EKS safely, names concrete operational risks (upgrades, patching, incident response), recommends a simpler managed alternative, and says what would need to change (skills, people, on-call) for Kubernetes to fit. It may still sketch an EKS design if it records the risks. FAIL if it simply designs EKS without challenging it, or refuses without offering an alternative.
