# 0001. GCP, us-central1

- **Status:** Proposed
- **Date:** 2026-11-10
- **Deciders:** CTO

## Context
No cloud was named. The team has "some GCP". Users are in the US. The workload needs GPUs, so GPU availability and quota matter more than price differences.

## Decision drivers
- Team skills (some GCP, no other cloud mentioned)
- US users, so latency within one US region is fine for a 1.5 s target
- GPU availability and managed GPU serving options
- Portability (container-based design keeps this reversible)

## Options considered
1. **GCP, us-central1 (chosen).** Existing team knowledge; central US gives about 30-60 ms to either coast; wide GPU offering.
2. **GCP, us-east4 or us-east1.** Slightly closer to East-coast users; GPU offering must be checked. Equivalent otherwise.
3. **AWS or Azure.** Comparable GPU options, but no team experience given and no credits or accounts known.

## Decision
We chose GCP in us-central1 because the team already has some GCP experience and all US users are within one network hop of a central region. Region is confirmed only after checking GPU quota and managed endpoint availability.

## Consequences
- Portability: the container design (ADR 0003) keeps the cloud choice **Portable** for compute; managed wrappers are **Adaptable**.
- If GPU stock in us-central1 is poor, move to another US region before launch. This is a config choice, not a redesign.
- Assumption to confirm: there is no existing org cloud or credits elsewhere.

## Fitness criteria
1. All production resources are in one GCP project in a single US region (us-central1 unless quota check says otherwise); model artifacts bucket is US multi-region.
2. A GPU quota request covering the peak replica count was approved before the first production deploy.

## Revisit when
- Users outside the US are added (latency, residency).
- GPU quota or stock in the region blocks the peak count twice in a month.
- The company standardises on another cloud.
