---
type: llm
focus: last_message
weight: 1
---
PASS if the response states, for the recommended design: availability or latency targets for the main user-facing paths, a backup/recovery approach consistent with the stated (or assumed) data-loss and recovery-time needs, and an availability target that is consistent with the team's on-call situation (or explicitly conditional on on-call). FAIL if two or more of these are missing.
