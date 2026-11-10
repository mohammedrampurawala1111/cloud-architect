---
type: llm
focus: last_message
weight: 1
---
PASS if every component in the recommended design is on AWS in eu-west-1 or eu-central-1 (edge services like CloudFront excepted) and uses an approved service, OR is explicitly called out as an exception to the guardrails with a reason and an approval or sign-off step (e.g. a search service such as OpenSearch or Bedrock, which is not on the list). FAIL if a non-approved service, region or self-hosted database is used without being flagged as an exception.
