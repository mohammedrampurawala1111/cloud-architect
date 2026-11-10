# ADR-0007: Run in one region with a pilot-light recovery approach

- **Status:** Proposed
- **Date:** 2026-11-10
- **Deciders:** CTO

## Context
The alert path target is 99.9% (assumed). A multi-AZ design handles zone failure. A whole-region loss is rare but would stop alerting.

## Decision drivers
- Availability target and error budget (about 43 min per 30 days).
- Team-fit: multi-region active-active (weight 4 in the team-fit scale) is not required by any stated requirement.
- Cost.

## Options considered
- **Single region, multi-AZ, pilot light in Melbourne.**
- **Active-active across Sydney and Melbourne:** devices need failover endpoints and state must replicate; heavy for this team.
- **Single region with no recovery approach:** leaves backups and recovery unplanned.

## Decision
We chose one active region with a pilot light: all infrastructure parameterised by region, S3 history replicated to Melbourne, DynamoDB backups copied to Melbourne, no running pipeline there. Targets: RTO 4 h; RPO 15 min for history and 5 min for configuration and state. **We accept that alerting stops during a regional outage; the CTO should confirm this.**

## Consequences
- A regional outage longer than the error budget breaches the 99.9% target.
- Devices must reach a new endpoint after failover, so they use a custom broker domain that DNS can repoint. This is a firmware requirement.
- Portability: **Portable** (the approach is provider-neutral).

## Fitness criteria
1. Devices connect through a custom IoT Core domain, not the default endpoint.
2. S3 replication lag is alarmed at 15 min; DynamoDB backup copies in ap-southeast-4 are at most 24 h old, and point-in-time recovery is on in Sydney.
3. A restore into Melbourne from code plus replicated data has been rehearsed with a recorded time under 4 h.

## Revisit when
- Contractual availability above 99.9%, or a regulator requires regional failover.
