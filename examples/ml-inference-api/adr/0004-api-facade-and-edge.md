# 0004. Thin API facade on managed containers, behind load balancer and WAF

- **Status:** Proposed
- **Date:** 2026-11-10
- **Deciders:** CTO

## Context
The API is public. It needs authentication, per-customer quotas, input limits, abuse protection and a place to shed load. The backend developer is the natural owner. The model endpoint should not be exposed directly.

## Decision drivers
- Public exposure and abuse risk
- Small team: one deployable, not several services
- Keep GPU capacity for legitimate, valid requests
- Cost and portability

## Options considered
1. **One stateless facade (modular monolith) on managed containers, behind LB and WAF (chosen).** One codebase for auth, quotas, validation, metrics.
2. **Full API management product.** More features (developer portal, billing hooks), but heavier than needed and more to learn.
3. **Expose the model endpoint directly.** Fewest parts, but no per-customer quota, no input limits, and the endpoint is not built for public traffic.

## Decision
We chose a single stateless facade service on managed containers (Python, same language as the team) behind a load balancer with a WAF, because it keeps one owner (the backend developer) and one deployable, and puts rate limiting, token caps and load shedding before the GPUs. Design points:
- API keys are stored hashed in a serverless document store, cached in memory in the facade for about 60 s; key revocation takes effect within that time.
- Per-customer quotas and rate limits: coarse per-IP/per-key limits at the WAF, precise per-key limits in the facade. Usage counters are aggregated in memory and flushed every few seconds.
- Requests above 8,000 tokens are rejected (413) or truncated by explicit customer setting.
- The facade calls the model endpoint over private access with a service identity, and a 1 s upstream timeout.
- Document text is never logged.

## Consequences
- Portability: facade **Portable** (container); key store **Adaptable** (small schema behind one module); edge **Adaptable**.
- Adds about 20-50 ms for one hop, accepted within the latency budget.
- No developer portal or self-service key management at launch.

## Fitness criteria
1. The model endpoint has no public ingress: only the facade's service identity can call it.
2. Requests with a missing or invalid key never reach the model endpoint (checked by the endpoint's request count against facade logs).
3. Logs from the facade contain no field holding document text (checked by a log-schema test in CI).

## Revisit when
- Customers need self-service keys, billing or a developer portal.
- The facade exceeds about 20 instances at peak or starts needing its own team.
