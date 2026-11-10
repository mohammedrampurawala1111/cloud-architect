# ADR-0007: Multi-AZ database, point-in-time recovery and in-Canada backup copy

- **Status:** Proposed
- **Date:** 2026-11-10
- **Deciders:** CTO

## Context
No on-call, so recovery from common failures must be automatic, and recovery from rare ones must be possible without specialist skills. Target availability is 99.5%. Residency rules apply to backups ([ADR-0002](0002-canadian-region-residency.md)).

## Decision drivers
- RPO 5 minutes for data corruption; RTO 4 hours (assumed).
- Region-level loss is rare; a second live region exceeds the team-fit budget.
- Backups must stay in Canada.

## Options considered
1. **Multi-AZ + point-in-time recovery + backup copy in a second Canadian region** (backup and restore).
2. Single AZ with backups only: AZ failure becomes an outage that needs manual work.
3. Warm standby or active-active in a second region: no requirement for it, and it would exceed the budget.

## Decision
We chose **Multi-AZ PostgreSQL with 14-day point-in-time recovery, a daily copy of backups to `ca-west-1`, and object-storage versioning with a cross-region copy of reports**, because it self-heals for AZ failure, covers bad deploys and data errors, and gives a region-loss path inside Canada at low cost. Region loss means a slower restore (RTO 1-2 days, RPO up to 24 hours).

## Consequences
- Pros: automatic AZ failover; low cost; Canadian data stays in Canada.
- Cons: region loss is a long outage; the team must exercise a restore (a process task, not in this design).
- **Portability: Portable** (PostgreSQL backups restore anywhere).

## Fitness criteria
1. The production database is Multi-AZ with automated backups retained 14 days; encryption at rest uses a customer-managed key.
2. Backup copies exist only in `ca-central-1` and `ca-west-1`.
3. A restore into a new instance has been completed at least once before launch, with the elapsed time recorded and below 4 hours for point-in-time recovery.

## Revisit when
- A customer contract requires an RTO under 4 hours for region loss (consider warm standby) or availability above 99.5% (requires on-call first).
- Database size exceeds 500 GB (restore time grows).
