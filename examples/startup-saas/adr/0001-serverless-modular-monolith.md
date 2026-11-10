# ADR-0001: Run a modular monolith on serverless functions

- **Status:** Proposed
- **Date:** 2026-11-10
- **Deciders:** CTO

## Context
Three TypeScript developers, no Kubernetes experience, no on-call rotation, and a wish to run as little infrastructure as possible. Peak load is about 30 requests/s from 200 companies. Team-fit budget is 2/5; the script rates serverless **Within**, managed containers **At limit**, Kubernetes **At limit** (Exceeds in practice).

## Decision drivers
- Team-fit budget 2/5 and no on-call: nothing should need patching or paging.
- Load is low and spiky (business hours): pay-per-use fits.
- A team of 3 does not need service boundaries (microservices rejected).
- Keep a cheap way out to containers.

## Options considered
1. **Serverless functions + managed database** (A).
2. **Managed containers + load balancer** (B): no time limits or cold starts, but always-on cost, image patching, and At limit.
3. **Managed Kubernetes** (C): Exceeds the team's skills and on-call capacity.
4. **Microservices** on any of the above: rejected, no requirement and 3 developers.

## Decision
We chose **a modular monolith (one TypeScript codebase, modules by folder) deployed as an API function and a worker function on serverless functions**, because the team-fit check puts it Within budget, 30 requests/s needs only about 6 concurrent executions, and no one is on call to patch or scale servers. The HTTP app is written against a standard framework with a thin adapter so it also runs as a plain Node server, which keeps option B open.

## Consequences
- Pros: no servers or images to patch; scales down outside business hours; fastest path to a first deploy.
- Cons: cold starts; 15-minute limit per invocation; database connections need a concurrency cap; VPC networking costs.
- **Portability: Adaptable.** Moving to containers means building an image and replacing the adapter entry point.

## Fitness criteria
1. The repository has one deployable application with `/src/modules/*` boundaries; no module imports another module's internals (checked by a lint rule or dependency check in CI).
2. `npm run start:server` runs the same HTTP app locally as a plain Node server with no cloud SDK required for startup.
3. Reserved concurrency on the API function is set to at most 100, and p95 API latency is under 500 ms in the monthly dashboard.

## Revisit when
- Any report job runs longer than 8 minutes, or cold-start p95 exceeds 500 ms after provisioned concurrency is tried.
- Sustained traffic exceeds 150 requests/s, or the team adds an on-call rotation and wants steady-state economics (then compare B).
