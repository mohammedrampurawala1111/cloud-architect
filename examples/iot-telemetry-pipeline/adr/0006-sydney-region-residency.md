# ADR-0006: Keep all data in Sydney, with backups in Melbourne

- **Status:** Proposed
- **Date:** 2026-11-10
- **Deciders:** CTO

## Context
Customers are in Australia. Telemetry linked to customer sites or people may be personal information under the Privacy Act 1988 (APP 8 keeps the sender accountable for cross-border disclosure). No other residency rule was given, so the level is assumed R1 (in-region, any provider). See [controls](../controls.md).

## Decision drivers
- Privacy Act exposure and customer expectations.
- Latency from devices to broker (Sydney is closest).
- Team-fit: one provider and one region pair.

## Options considered
- **Sydney (ap-southeast-2) primary, Melbourne (ap-southeast-4) backup.**
- **Sydney only, no cross-region copy:** cheaper, weaker recovery.
- **Backups outside Australia:** a cross-border disclosure; rejected.

## Decision
We chose Sydney for all processing and storage and Melbourne for replicated backups, because both stay in Australia. No telemetry, logs or backups leave Australia. Alert messages carry device IDs only, so third-party delivery channels do not receive personal information.

## Consequences
- Some services may not be available in Melbourne, which affects recovery (verify).
- Global AWS services (IAM, Route 53) have control planes outside Australia but hold no telemetry.
- Portability: **Portable** (region is configuration).

## Fitness criteria
1. A Service Control Policy denies resource creation outside ap-southeast-2 and ap-southeast-4 in the workload accounts.
2. All S3 buckets, DynamoDB tables, Kinesis streams and log groups are in ap-southeast-2; replicas and backups only in ap-southeast-4.
3. Alert payloads contain device ID, alert type and value only (unit test on the message schema).

## Revisit when
- Government or critical-infrastructure customers appear (IRAP or sovereign controls, R2) (verify).
- Legal review concludes telemetry is not personal information.
