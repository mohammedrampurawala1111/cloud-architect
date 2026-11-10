# Design consistency

Reviewers send designs back most often because the parts don't agree with each
other, not because a choice is wrong. Build the design so they can't disagree,
then check it before answering.

## 1. Recovery per failure scope

For the recommended option, one table. Every stateful component (databases,
object storage, queues holding work, search indexes, key and secret stores,
identity stores, card or token vaults) appears in it.

| Failure scope | RPO | RTO | Mechanism that makes it true | Components covered |
|---|---|---|---|---|
| One instance or zone | e.g. ~0 | 5 min | Multi-AZ synchronous standby | Primary DB, cache |
| Whole region | e.g. 1 h | 4 h | Cross-region backup copy every hour, infrastructure redeployable from code | Primary DB, object storage, secrets |
| Data deleted or corrupted | e.g. 5 min | 2 h | Point-in-time recovery, 14-day window | Primary DB |

Rules:
- **The RPO can't be better than the mechanism.** A daily copy means up to 24 h
  of loss for that scope; replication lag sets the floor for a replica. If the
  stated RPO is tighter than the mechanism allows, change the mechanism or the
  RPO.
- **The RTO includes everything needed to serve again:** data restored, compute
  and networking running in the recovery location, DNS or traffic switched.
- **No stateful component is left out.** If one has no recovery for a scope,
  say so in the table and in the risks.
- **The tier matches the availability target and on-call** (see quality
  attributes in `design`).

## 2. One source for every number

State each figure once and refer to it elsewhere: the sizing assumptions, each
option's rough cost range, the availability target and error budget, the
RPO/RTO table, capacity limits. Anything derived (a ratio such as "twice the
cost", a per-month figure from a per-hour one, a headroom multiple) must be
recomputed from those figures, not restated from memory.

**Capacity:** for each component that scales, its stated capacity is at least
the peak load times the headroom you claim (e.g. "4 shards × 1,000 records/s =
4,000/s ≥ 2,000/s peak × 2"). If a surge is mentioned, the capacity covers it
or the design says what happens instead (queueing, throttling, load shedding).

**Cost vs sizing:** a cost range must be plausible for the sizing stated
(instance sizes, count, hours running, storage, egress). If you size a large
database, its cost appears in the range.

## 3. One component list

The same components, with the same names, in every place they appear: options,
mapping table, diagrams, data-flow and recovery tables, decision brief. A store
named in the data-flow table (e.g. "card vault") must be in the mapping, the
diagrams and the recovery table, or not exist anywhere.

## 4. Always-required building blocks

Each one is in the design, or its absence is a named risk:
- **Environment separation:** production separate from non-production (separate
  accounts, subscriptions or projects at minimum). Feature flags don't replace it.
- **Secrets:** a managed secret store, and how credentials rotate.
- **Identity:** how users and services authenticate.
- **Observability:** logs, metrics and the signals behind the availability target.
- **Backups:** covered by the recovery table above.
- **No single point of failure** that contradicts the availability target
  (one NAT gateway, one zone, one instance on a 99.9% path).

## 5. Check before answering

Go through this list and fix the text wherever it fails:
1. Every stateful component is in the recovery table, and every RPO is
   achievable with its mechanism.
2. Every number appears once and every derived figure is recomputed.
3. Capacity covers peak × headroom, and any surge you mention.
4. Each cost range fits its sizing.
5. The component list matches across all sections and diagrams.
6. Environment separation, secrets, identity, observability and backups are
   present or named as risks; no single point of failure breaks the target.
7. Team-fit verdicts are worded exactly as in the team-fit table everywhere.
