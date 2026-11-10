# 0006. 99.5% target, single region, backup-and-restore recovery

- **Status:** Proposed
- **Date:** 2026-11-10
- **Deciders:** CTO

## Context
No availability target was given. The team has no on-call, and traffic is mostly in business hours. Multi-region GPU serving doubles the largest cost line and needs operations the team cannot staff.

## Decision drivers
- No on-call: the target must be one that business-hours response can back
- Cost: a second region of GPUs is expensive
- The service stores no customer documents, so recovery is mostly redeployment

## Options considered
1. **99.5%, one region, redeploy elsewhere on regional failure (chosen).** Error budget 3 h 36 min per 30 days.
2. **99.9%, warm standby in a second region.** Error budget 43 min; needs on-call and roughly double the GPU spend.
3. **No stated target.** Leaves the CTO and customers guessing.

## Decision
We chose 99.5% in a single region with automatic zone-level healing (minimum 2 replicas), and backup-and-restore as the regional recovery approach: artifacts and images are kept in multi-region US storage so the stack can be redeployed in a second US region. RTO is hours (assumed); RPO is about 0 for the service. Because nobody is on call, a higher target is a precondition on adding on-call and a standby, not something this design promises.

## Consequences
- Portability: **Adaptable**; the recovery plan depends on the provider's cross-region artifact features.
- A regional outage during business hours means hours of downtime. If customers' contracts require more, this ADR must change.
- Customers should not be offered an SLA above 99.5% on this design.

## Fitness criteria
1. Model weights and container images exist in a US multi-region bucket and registry (or a replica in a second US region).
2. A redeploy of the stack into a second US region has been done once from the repo, with the time recorded (target under 4 hours).
3. Monthly availability is reported against 99.5%, measured at the load balancer as non-5xx plus intentional 429s counted separately.

## Revisit when
- A customer contract needs an SLA above 99.5%.
- An on-call rotation exists: consider 99.9% with a warm standby.
- Two regional incidents occur in a year.
