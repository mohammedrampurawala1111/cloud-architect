# ADR-0002: Keep regulated data in Canada on AWS `ca-central-1`

- **Status:** Proposed
- **Date:** 2026-11-10
- **Deciders:** CTO

## Context
Customers are in the US and Canada. Canada's PIPEDA and provincial laws (for example Quebec Law 25) allow transfers with accountability, but some Canadian customers (public sector, Quebec-heavy) may require Canadian storage (verify). The US has no general residency rule for this kind of B2B data (no federal-government, defence or health workloads assumed). The team has some AWS experience. Residency level assumed **R1 (in-region)**.

## Decision drivers
- Canadian storage is the stricter requirement and can serve both countries.
- Single region keeps the design inside the team's budget.
- Team knows AWS.

## Options considered
1. **One region in Canada (`ca-central-1`) for all customers.**
2. One region in the US for all customers: simpler for US customers, but fails any Canadian customer that requires Canadian storage.
3. Two regional stacks (US and Canada): satisfies both, doubles operations; exceeds the budget with no stated requirement.
4. A Canadian-headquartered provider (R3): not required at R1; managed-service gaps would raise operations burden (verify what exists).

## Decision
We chose **`ca-central-1` for all production data, with backup copies in `ca-west-1`**, because it meets the stricter Canadian expectation with one stack, and a three-person team cannot run two. US-only storage for a US customer is **not** met; if one is signed, a second stack becomes a new decision.

## Consequences
- Pros: one stack; Canadian data stays in Canada; backups stay in Canada.
- Cons: about 20-40 ms extra latency for US West customers (assumed acceptable); `ca-central-1` pricing is slightly higher than `us-east-1`; AWS is a US-parent provider (jurisdiction rating 🟡, see [controls](../controls.md)).
- **Portability: Adaptable.** The app has no hard-coded region, so a second region stack can be deployed by changing configuration, but the data split (per-tenant region) would need design.

## Fitness criteria
1. All data stores (database, object storage, queue, user pool, secrets, logs) are in `ca-central-1`; backups are in `ca-central-1` or `ca-west-1` only. An organization policy denies other regions except the global services listed in controls.md.
2. The API is served by a regional API Gateway endpoint, not by the CDN; the CDN serves static assets only, with no personal data in them.
3. No third-party SaaS in the production data path (telemetry, error tracking) receives personal data; the sub-processor list in `controls.md` is complete.

## Revisit when
- A customer contractually requires US-only storage or a federal/defence workload appears.
- Canada-heavy customers ask for sovereign controls (R2): move to customer-managed keys with external key store.
- Check with counsel before signing the first Quebec customer (Law 25 assessment).
