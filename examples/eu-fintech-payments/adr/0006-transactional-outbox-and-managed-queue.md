# ADR-0006: Transactional outbox and a managed queue; no Kafka

- **Status:** Proposed
- **Date:** 2026-11-10
- **Deciders:** CTO

## Context
Webhooks to merchants, settlement, reports and the dashboard need events from the ledger without risking lost or phantom events. Volume is moderate (a few events per payment at 500 TPS peak).

## Decision drivers
- Correctness: no event without a committed ledger change, and no committed change without an event.
- Team fit: a streaming platform or self-run broker adds weight 2-3 each.
- Portability.

## Options considered
1. Outbox table written in the same database transaction, relayed by the worker to a managed queue/topic.
2. Dual write (database then queue): can lose events: rejected.
3. Kafka-style stream (managed or self-run): replay and many consumers, but more operations, and no requirement for replay beyond the database itself.

## Decision
We chose **transactional outbox plus a managed queue and topic**. Consumers are idempotent; ordering is per payment. Merchant webhooks are retried with backoff and a dead-letter queue. The queue never carries PANs.

## Consequences
- Portability: Adaptable (behind an interface; swap to RabbitMQ or Kafka).
- At-least-once delivery; consumers must deduplicate.
- Dashboard reporting reads from a database reader and pre-aggregates through the worker, not through a stream.

## Fitness criteria
1. No code path publishes to the queue outside the outbox relay (checked by a lint/architecture test).
2. A chaos test killing the worker mid-relay results in no lost and no duplicated side effects after recovery (duplicates are deduplicated).
3. Dead-letter queue depth is alarmed at greater than 0 for 15 minutes.

## Revisit when
More than five independent consumers need replayable history; sustained event rates above 5,000 per second; a requirement for event replay by regulators.
