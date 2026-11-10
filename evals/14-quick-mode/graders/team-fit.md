---
type: llm
focus: last_message
weight: 1
---
PASS if the response explicitly assesses what this team can operate (size, skills, on-call) and the recommended option respects it: the team is unknown; the response must state an assumption about the team and keep the design simple (managed/serverless). FAIL if it recommends Kubernetes or microservices.
