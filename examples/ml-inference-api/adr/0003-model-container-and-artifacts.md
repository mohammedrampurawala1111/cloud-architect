# 0003. vLLM in an OCI container, label-only output, versioned artifacts

- **Status:** Proposed
- **Date:** 2026-11-10
- **Deciders:** CTO

## Context
The fine-tuned 8B model is classification only. The cost and latency of an LLM here come from reading the document (prefill), not from generating text. The ML engineers work in Python and PyTorch.

## Decision drivers
- Throughput per GPU, which sets cost
- Portability between the serving options (ADR 0002)
- Reproducible, reversible model releases
- Team skills

## Options considered
1. **vLLM (or a similar open inference server) in a container (chosen).** Continuous batching, prefix caching, constrained decoding; widely used; portable.
2. **Hand-written PyTorch/Transformers server.** Familiar to the team but much lower throughput, so several times the GPU cost.
3. **Provider's prebuilt serving container.** Faster start, less control; use only if it matches option 1's throughput in the benchmark.

## Decision
We chose an open inference server in our own container, with output constrained to the fixed label set (max 8 new tokens), because classification is dominated by prefill and batching, and because the same container then runs on any of the three options. Weights are stored in versioned object storage in standard Hugging Face format; each release is an immutable (weights version, image digest) pair.

Quantisation (for example 8-bit) may be used to cut cost, but only after an offline evaluation on the held-out set shows no meaningful accuracy loss (threshold set by the ML team).

## Consequences
- Portability: **Portable** (OCI image, standard weights format).
- The ML team owns the container and its dependency updates (an upgrade burden that is theirs to schedule).
- Model version is returned in every API response, so customers can trace results.

## Fitness criteria
1. The production deployment references an image by digest and a weights path with a version suffix; no `latest` tags.
2. API responses include `model_version`.
3. Any quantised model in production has an eval report in this repo showing accuracy against the bf16 baseline.

## Revisit when
- The inference server cannot meet the throughput measured in ADR 0002.
- A model update changes the output from fixed labels to free text.
