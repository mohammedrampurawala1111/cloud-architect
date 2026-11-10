---
type: llm
focus: last_message
weight: 2
---
Judge as a senior SRE in a production-readiness review of this design. PASS if you would let it proceed to build with at most minor comments: it is operable by the stated team, has no single point of failure that contradicts the stated availability need, covers backups, secrets, monitoring and environment separation, and does not add components the requirements don't need. FAIL if you would send it back for rework.
