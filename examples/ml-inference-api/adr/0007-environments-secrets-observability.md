# 0007. Separate projects, managed secrets, managed observability

- **Status:** Proposed
- **Date:** 2026-11-10
- **Deciders:** CTO

## Context
A public API serving possibly sensitive documents needs identity, secret handling, environment separation and visibility, with nobody to run extra tooling.

## Decision drivers
- Team-fit budget 2/5: no self-run tools
- Blast radius: test GPUs and keys must not touch production
- Cost: GPU test environments are expensive

## Options considered
1. **Separate cloud projects for production and non-production; managed secret store; managed monitoring and logging (chosen).**
2. **One project with naming conventions.** Cheaper, but one mistake exposes production.
3. **Self-run observability stack.** More flexible, but adds components the team cannot operate.

## Decision
We chose two projects (production, and one shared non-production), each service running under its own service identity with least-privilege roles, no long-lived service account keys; customer API keys and any provider credentials in the managed secret store, with a rotation path that needs no redeploy (facade reads secrets at start and on key refresh); managed monitoring, logging and tracing with the signals: p50/p95/p99 latency, error and 429 rates, in-flight requests, GPU utilisation, replica count, tokens per second. The non-production environment uses the smallest GPU and a minimum of one replica, so its cost stays low.

## Consequences
- Portability: **Adaptable** (dashboards and policies must be rebuilt elsewhere; logs are structured JSON).
- Non-production does not reproduce peak load; load tests for ADR 0002 run in a short-lived scaled-up window.

## Fitness criteria
1. Production and non-production are different projects; no identity in non-production has a role in production.
2. No service account key files exist; no secret appears in container images or environment config checked into the repo.
3. A dashboard with the listed signals exists in the production project.

## Revisit when
- A customer requires audit evidence (SOC 2 or similar): add audit-log retention and access reviews.
- Log volume becomes the largest non-GPU cost line.
