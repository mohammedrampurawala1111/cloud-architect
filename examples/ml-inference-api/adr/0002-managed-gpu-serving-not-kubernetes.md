# 0002. Managed GPU model endpoint, not Kubernetes

- **Status:** Proposed
- **Date:** 2026-11-10
- **Deciders:** CTO

## Context
The model must run on GPUs, at about 50 req/s peak with p95 < 1.5 s. The team is 3 ML engineers and 1 backend developer, with no Kubernetes experience and no on-call. The team-fit budget is 2/5.

## Decision drivers
- Team-fit: A is Within, B and C At limit
- No on-call: GPU node failures must self-heal
- Time to first release
- GPU choice, because the right GPU depends on an unrun benchmark
- Cost and portability

## Options considered
- **A. Managed ML endpoint (chosen).** Provider runs GPU machines and replacement. Free GPU choice. Always-on minimum replicas.
- **B. Serverless GPU containers.** Cheaper overnight (scale to zero) but L4-class GPUs only (verify), and the team owns a capacity schedule. Same container as A, so it is the fallback.
- **C. Kubernetes with GPU node pools.** Best tuning and portability, but the team has no Kubernetes skills and no one is on call. Rejected for now.

## Decision
We chose a managed model endpoint running our own vLLM container because it is the only option within the team's operational budget, it keeps GPU nodes off the team's plate, and it gives GPU choice (L4, A100, H100) that we need to settle by benchmark. We did not choose Kubernetes because the team has no Kubernetes experience and no on-call rotation.

## Consequences
- Portability: **Adaptable**. The container moves to B or C with deployment config rewritten.
- Minimum replicas run around the clock, so overnight cost is not zero. Accepted at first.
- The endpoint's limits (payload size, request timeout, scaling speed) are the provider's; they must be checked in a benchmark before commit.

## Fitness criteria
1. A load test with production-like documents (average about 1,000 tokens, p95 about 4,000) sustains 50 req/s for 30 minutes with p95 < 1.5 s and under 0.5% errors, at or below the planned max replica count.
2. The measured cost per 1M input tokens is recorded in this repo and the monthly estimate at peak profile stays inside the range in README.md (or the README is updated).
3. No Kubernetes cluster exists in the production project.

## Revisit when
- Measured GPU spend exceeds $12k/month for two months, or overnight idle spend exceeds 25% of the total: consider B.
- The team gains a Kubernetes engineer or a second model must be served: consider C.
- An evaluation shows a distilled smaller classifier matches quality; it could cost roughly 10x less and run on CPU or a single small GPU.
