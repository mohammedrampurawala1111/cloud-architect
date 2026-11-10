# 0005. Fixed headroom and explicit load shedding, no scale-to-zero

- **Status:** Proposed
- **Date:** 2026-11-10
- **Deciders:** CTO

## Context
A new GPU replica takes minutes to start (pull the image, load about 16 GB of weights, warm up), so autoscaling cannot absorb a spike inside a 1.5 s request. Traffic is mostly business hours, so there is a daily pattern but no way to forecast spikes.

## Decision drivers
- p95 < 1.5 s must hold at 50 req/s
- No on-call: overload must degrade safely by itself
- Cost: GPUs are the largest line

## Options considered
1. **Headroom plus load shedding (chosen).** Autoscale on load between a minimum and a maximum; keep about 40% spare at the expected peak; when full, fail fast with 429/503 and Retry-After.
2. **Queue everything.** No errors, but latency blows through the 1.5 s target, so the SLO is lost silently.
3. **Scale to zero overnight.** Lowest cost, but the first morning requests wait minutes. Possible only in option B with a scheduled minimum.

## Decision
We chose a minimum replica count that is never below 2 (covers a replica or zone loss), a maximum equal to the approved GPU quota, a target utilisation near 60%, and a hard cap on in-flight requests in the facade sized from the benchmark. Above the cap the facade returns 429 or 503 with `Retry-After` rather than queueing. We did not choose scale-to-zero because cold starts cannot meet p95 1.5 s.

## Consequences
- Portability: **Portable** concept; the autoscaling settings are **Adaptable**.
- Spend has a floor (overnight minimum replicas). Customers see explicit errors at overload and must retry.
- Sizing numbers come from the ADR 0002 benchmark; until then they are placeholders.

## Fitness criteria
1. Production minimum replicas ≥ 2 and maximum ≤ approved quota, recorded in the deployment config in this repo.
2. In a load test at 1.3× peak (65 req/s), the share of rejected requests is under 5% and p95 of accepted requests stays under 1.5 s.
3. The facade has a configured in-flight cap and no unbounded queue.

## Revisit when
- Overnight idle cost exceeds 25% of total GPU spend (consider B with a scheduled minimum).
- Customers ask for bulk submissions: add an asynchronous batch path (queue plus workers) rather than raising the synchronous cap.
