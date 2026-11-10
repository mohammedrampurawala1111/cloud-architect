# ADR-0005: Inline fraud scoring in the authorisation path with a rules fallback

- **Status:** Proposed
- **Date:** 2026-11-10
- **Deciders:** CTO

## Context
Fraud scoring must decide before the acquirer is called, so it is on the critical path. Assumed budget: p99 ≤ 40 ms. Team writes Java/Kotlin; no data-science platform exists.

## Decision drivers
- Latency and availability of the authorisation path.
- Team fit: no separate model-serving platform.
- GDPR: automated decisions must be reviewable.

## Options considered
1. Scoring as a module inside the core service, model loaded in memory, velocity features from a managed cache.
2. Separate scoring service: independent deployment but an extra hop and failure mode.
3. Third-party fraud SaaS: fast to start, but sends personal data to another provider and adds a critical ICT third party.

## Decision
We chose **option 1**. Rules (velocity, BIN/country mismatch, amount limits) plus a portable model format (for example ONNX) loaded in the JVM. Features come from the cache; if the cache is unavailable, the module falls back to rules computed from the ledger database with a degraded flag. The **failure policy is explicit**: if scoring cannot run at all, payments below a configured amount proceed with a flag and above it go to review/decline. Every decision is stored with its inputs and rule/model version, and the dashboard lets merchants and analysts review flagged payments. Training is offline on pseudonymised exports; models are deployed as versioned artefacts with the application.

## Consequences
- Portability: Portable (JVM, Valkey/Redis protocol, ONNX).
- Fraud logic releases with the core; use feature flags for rule changes.
- Model quality work (labels, retraining) is not designed here.

## Fitness criteria
1. Fraud module p99 ≤ 40 ms at 500 TPS in a load test, with the cache enabled.
2. A game-day test that disables the cache shows the payment API still answers with the degraded flag and no errors above 0.1%.
3. Every payment record has a stored score, decision and model/rule version.

## Revisit when
Rules-only fallback loses material accuracy; model size or feature needs exceed in-process limits; a second consumer of scores appears (then consider a separate service).
