---
type: llm
focus: last_message
weight: 1
---
PASS if the recommended design follows the patterns already in this repository: sends the SMS asynchronously through the existing SQS queue and worker (not in the request path), follows the existing routes/service/repository module layout, keeps row-level tenancy (tenantId on any new table and in every query), and changes the schema through the existing Prisma migrations. FAIL if two or more of these are ignored.
