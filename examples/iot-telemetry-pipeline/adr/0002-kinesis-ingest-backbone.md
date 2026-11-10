# ADR-0002: Use Kinesis Data Streams as the single ingest backbone

- **Status:** Proposed
- **Date:** 2026-11-10
- **Deciders:** CTO

## Context
The same readings feed real-time alerting (seconds) and the archive (minutes). A failure or slowdown in one must not affect the other, and after an incident we need to replay recent data.

## Decision drivers
- Independent failure of alerting and archiving.
- 2,000 records/s, bursts of 3-5x after reconnects.
- Team-fit: managed, no brokers to run (self-run Kafka is weight 3).

## Options considered
- **Kinesis Data Streams**, provisioned shards with enhanced fan-out.
- **IoT rule with two actions** (Lambda and Firehose directly): no replay, pays rule actions twice, one slow target can hold back the other.
- **MSK (Kafka):** more features than we need and more to size.

## Decision
We chose Kinesis because it decouples the two consumers, gives a 24 h replay window, and costs little at this size (hundreds of dollars at most). We provision 6 shards (3x headroom over the 2-shard minimum) and give the alert consumer enhanced fan-out so a slow archive reader cannot delay alerts.

## Consequences
- Shard count is a capacity setting to monitor (1 MB/s or 1,000 records/s per shard).
- Retention beyond 24 h costs extra; we keep the default and alarm on iterator age.
- Portability: **Adaptable** (Kafka-compatible replacements need producer and consumer changes).

## Fitness criteria
1. The alert consumer is its own enhanced fan-out consumer, separate from Firehose (check: two registered consumers on the stream).
2. Alarms on `IteratorAgeMilliseconds` above 2,000 ms for the alert consumer and on write throughput above 60% of provisioned.
3. Shard count is at least 3x the steady-state need (at least 6 shards at 20,000 devices).

## Revisit when
- Sustained write above 60% of provisioned capacity, or the fleet exceeds 100,000 devices.
