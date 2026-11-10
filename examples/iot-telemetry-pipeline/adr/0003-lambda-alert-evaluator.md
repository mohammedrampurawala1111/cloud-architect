# ADR-0003: Evaluate alerts in Lambda with DynamoDB state, notify through SNS

- **Status:** Proposed
- **Date:** 2026-11-10
- **Deciders:** CTO

## Context
Alerts must reach the delivery provider within 5 s of a device publishing. Rules are static thresholds (min/max, N of the last M readings) per device type or device, with de-duplication state (open, acknowledged, closed).

## Decision drivers
- Latency target: p99 under 5 s.
- Team-fit: Python and Go; no stream-processing framework experience (weight 3).
- Testability: rules are code with unit tests.

## Options considered
- **Lambda consumer with DynamoDB state.**
- **Fargate consumer** (Option B): always-on, more to deploy and scale.
- **Flink or similar stream processor:** windowing we do not need; weight 3.
- **IoT rules engine SQL thresholds:** cannot hold alert state and is hard to test.

## Decision
We chose a Lambda function (Go or Python) fed by a Kinesis enhanced fan-out consumer with batch window 0 and provisioned concurrency to avoid cold starts. Thresholds are cached in memory and refreshed from DynamoDB every 30 s. Alert state uses conditional writes so each breach creates one alert. N-of-M rules keep the last M values per device. Alerts go to SNS, with a dead-letter queue for failed deliveries and an on-failure destination for poison records. Offline detection is a separate once-a-minute check against a last-seen item, outside the 5 s path.

## Consequences
- Rule changes take up to 30 s to apply.
- N-of-M rules add DynamoDB writes (up to 2,000/s if every device uses one); plain min/max rules write only on state changes.
- Portability: **Adaptable** (logic is plain code); the DynamoDB access code is **Locked** but small.

## Fitness criteria
1. A synthetic heartbeat device injects a known breach every 5 minutes; measured publish-to-SNS time has p99 under 5 s over any 24 h (CloudWatch metric and alarm).
2. The evaluator runs with provisioned concurrency and a Kinesis on-failure destination configured.
3. A breach that stays open produces exactly one alert plus configured reminders (integration test in CI).

## Revisit when
- Rules need time windows longer than a few minutes or cross-device correlation (consider a stream processor).
- Evaluator p99 duration exceeds 1 s.
