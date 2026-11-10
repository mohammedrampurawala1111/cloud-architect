---
type: llm
focus: last_message
weight: 1
---
PASS if the response explicitly assesses what this team can operate (size, skills, on-call) and the recommended option respects it: 3 developers with no on-call working on the existing ECS/PostgreSQL/SQS system. FAIL if it recommends Kubernetes, a new database, Kafka or splitting into microservices without a requirement that needs it.
