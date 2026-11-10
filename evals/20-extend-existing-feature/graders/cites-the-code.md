---
type: llm
focus: last_message
weight: 1
---
PASS if the response describes the existing system with references to actual files in the repository (for example src/lib/queue.ts, src/worker/handlers.ts, src/modules/jobs/service.ts, prisma/schema.prisma, infra/sqs.tf) for at least four distinct files. FAIL if it describes the system generically or cites fewer than four real files.
