---
type: llm
focus: last_message
weight: 1
---
PASS if, for any component outside the approved list, the response says why an approved alternative (e.g. PostgreSQL full-text search plus pgvector on RDS) does or does not meet the requirement. FAIL if a non-approved service is chosen without comparing it to an approved one.
