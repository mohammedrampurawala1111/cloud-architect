# ADR-0002: Modular monolith on managed containers; no Kubernetes

- **Status:** Proposed
- **Date:** 2026-11-10
- **Deciders:** CTO

## Context
10 engineers, 3 of them ops, no platform team, Kubernetes skill 1 of 3, strong containers and Terraform. 500 TPS peak is modest. Fraud scoring and ledger writes are on the same authorisation path with a tight latency budget.

## Decision drivers
- Team-fit budget 4 of 4: nothing beyond managed services.
- Latency and availability: every network hop on the authorisation path costs both.
- PCI scope: card handling must be isolated.
- Portability: standard OCI images.

## Options considered
1. Serverless functions (A): fast to start, but cold starts for Java, connection storms, lowest portability.
2. Managed containers, modular monolith (B).
3. Kubernetes with microservices (C): control and portability, but patching, upgrades and cluster on-call for a team at level 1.

## Decision
We chose **managed containers with a modular monolith in Kotlin**, deployed as four runtime units from at most three code bases: card vault (isolated, ADR-0004), core service (payments, ledger, fraud module), async worker (same code as core, different entry point), dashboard backend. We left Kubernetes, a service mesh and microservices out because the team has Kubernetes skill 1 and no requirement needs them.

## Consequences
- Module boundaries inside the core (payments, ledger, fraud, settlement, merchants) are enforced with build-time rules, so a later split is possible.
- Portability: Adaptable (task definitions rewritten for another runtime; images unchanged).
- One deploy affects payments, ledger and fraud together; use progressive rollout.

## Fitness criteria
1. No more than four deployable units in production, listed in the architecture repo; no Kubernetes cluster exists in the production account.
2. A build check fails if a module imports another module's internal package (for example an architecture-test suite in CI).
3. Every service runs at least 3 tasks spread over 3 zones.

## Revisit when
Sustained load above 1,000 TPS; more than 25 engineers or independent release needs; a requirement for a portable runtime beyond containers.
