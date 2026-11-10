# ADR-0003: PostgreSQL double-entry ledger, 3-zone synchronous, EU pilot-light DR

- **Status:** Proposed
- **Date:** 2026-11-10
- **Deciders:** CTO

## Context
The ledger needs ACID transactions, auditability, RPO 0, and 99.95% availability. 500 TPS peak with about 3 entries per payment is roughly 1,500-2,000 inserts per second at peak.

## Decision drivers
- Requirement: RPO 0 for the ledger; 21.6 min monthly error budget.
- Team fit: managed database only (a self-hosted database scores 4 by itself).
- Portability: standard PostgreSQL.

## Options considered
1. Managed PostgreSQL-compatible database with storage replicated synchronously across 3 zones, one writer, readers, plus an asynchronous cross-region replica (Aurora PostgreSQL with Global Database in the mapping).
2. Managed PostgreSQL with synchronous standby in another zone (RDS Multi-AZ): similar RPO 0 for zone loss, slower failover and fewer readers.
3. Self-run PostgreSQL with synchronous replication across two regions: true RPO 0 for region loss, but adds latency of tens of milliseconds to every payment and a self-hosted database (weight 4): rejected.
4. Event-sourced ledger on a streaming platform: more moving parts, rejected.

## Decision
We chose **option 1**. Ledger design rules:
- Double-entry, append-only journal. Entries are never updated; corrections are reversing entries.
- Every payment state change, its journal entries and its outbox row (ADR-0006) are written in one database transaction.
- Idempotency key unique per merchant, enforced by a database constraint.
- Balances derive from entries plus periodic snapshots; merchant balance rows are not updated in the hot path (avoids a single hot row).
- Only standard PostgreSQL features in application code (so we can leave Aurora).
- **RPO 0 applies to instance and zone failure.** For loss of a whole region, the cross-region replica lags by about a second; the gap is closed by reconciling against acquirer and scheme settlement files and merchant webhooks. **The CTO must accept this explicitly (README, assumption 5).**
- DR is pilot light in the second EU region; the failover is a decision taken by a person, not automatic, to avoid split-brain.

## Consequences
- Portability: Adaptable for the database (standard PostgreSQL); the Global Database feature is Locked but used only for DR.
- Single writer is the scaling ceiling (README).
- A regional outage can exceed the monthly error budget; the SLO wording excludes declared regional disasters.

## Fitness criteria
1. The ledger database cluster has storage in 3 zones and at least one reader in a different zone from the writer; an annual failover test shows no lost acknowledged transactions and recovery under 2 minutes.
2. A schema check in CI forbids UPDATE and DELETE grants on the journal table for the application role.
3. A restore from point-in-time backup into a clean environment succeeds at least every 6 months and is recorded; a DR region failover exercise runs at least annually with RTO ≤ 2 h.

## Revisit when
Sustained 1,000 TPS; the ledger writer CPU above 60% at peak; the CTO requires RPO 0 against region loss (then reconsider option 3 and the team budget).
