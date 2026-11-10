# ML inference API: document classification with a fine-tuned 8B model

> Starting design for human review, not a production sign-off. Status: **Proposed**, decision by the CTO.

## Requirements summary
**What it does:** A public, synchronous HTTP API that classifies a document with a fine-tuned 8B-parameter open-weight language model and returns a label and a confidence score.
**Users & traffic:** External API customers in the US. 50 requests/s at peak, mostly in US business hours (about 08:00-19:00 across US time zones, weekdays). Overnight and weekend traffic is low.
**Data:** Document text in the request. Not stored by the service. Per-customer API keys, quotas and usage counters are stored. Model weights (about 16 GB at bf16) are stored as versioned artifacts.
**Latency / availability:** p95 under 1.5 s end to end. Availability target is 99.5%, assumed (see Quality attributes). RPO is about 0 (stateless, artifacts versioned). RTO is hours, assumed.
**Integrations:** None. The model is self-hosted, with no third-party LLM API.
**Constraints:** US users, so one US region. Likely regulations are inferred, not given: none named. Documents could contain personal data, so see "Data handling".
**Team:** 3 ML engineers (Python, PyTorch) and 1 backend developer. Some GCP, no Kubernetes, no on-call, prefer managed.
**Assumptions I made** (you couldn't answer questions, so please check these; the sizing ones move cost the most):
1. Average document is about 1,000 tokens, p95 about 4,000, hard limit 8,000 (longer inputs are rejected with 413 or truncated, per customer setting).
2. Output is a single label from a fixed set, so decode is about 5-10 tokens. Latency and cost are dominated by prefill (reading the document).
3. One model, one fine-tune version live at a time, updated at most monthly.
4. Synchronous request/response only. No streaming and no batch endpoint at launch.
5. "50 req/s peak" is sustained for minutes at a time, not a single-second spike.
6. Customers authenticate with API keys. No end-user login, no billing system in scope.
7. No regulated data (HIPAA, PCI) at launch, and no customer has contractually required SOC 2 yet. Both flagged below.
8. The 3 ML engineers can build and package a vLLM (or equivalent) container. Team skill self-reported as containers 2/3, IaC 1/3.
9. GCP is the cloud, because the team has "some GCP". No org profile or guardrails were provided.
10. GPU quota in a US region can be obtained before launch. This is not yet verified.

## Recommendation
**Option A: managed ML endpoint on GCP (us-central1).** A thin API facade on Cloud Run sits behind a load balancer with Cloud Armor. It calls a managed model endpoint (Vertex AI custom container running vLLM) over private networking. Firestore holds API keys and quotas.

Because:
- It is the only option the team-fit check rates **Within** the budget (2/5). B and C are At limit.
- No Kubernetes and no on-call: GPU nodes, drivers, health replacement and zone spreading are the provider's job. A failed replica is replaced automatically.
- It lets ML engineers do what they know: package the model, register versions, split traffic for canary of a new fine-tune.
- GPU type is a free choice (L4, A100, H100), which matters because the right one depends on a benchmark we haven't run.

Fallback: **B (Cloud Run with GPU)** if the nightly always-on cost of A matters more than GPU choice. Both use the same container, so switching is small. **C (Kubernetes)** is rejected for now.

## Rationale in brief
| Decision | Because | ADR |
|---|---|---|
| GCP, us-central1 | Team has some GCP; users are in the US; GPU availability | [0001](adr/0001-cloud-and-region.md) |
| Managed model endpoint, not Kubernetes | Budget 2/5, no Kubernetes skills, no on-call | [0002](adr/0002-managed-gpu-serving-not-kubernetes.md) |
| vLLM in an OCI container; label-only output | Portable; classification is prefill-bound | [0003](adr/0003-model-container-and-artifacts.md) |
| Thin Cloud Run facade behind LB and Cloud Armor | Public API needs auth, quotas, load shedding; backend dev owns it | [0004](adr/0004-api-facade-and-edge.md) |
| Fixed headroom plus load shedding, no scale-to-zero | GPU replicas take minutes to start; p95 1.5 s cannot absorb cold starts | [0005](adr/0005-capacity-and-load-shedding.md) |
| 99.5% single region | No on-call, business-hours traffic | [0006](adr/0006-availability-single-region.md) |
| Separate projects, managed secrets, managed observability | Baseline hygiene with no operations capacity | [0007](adr/0007-environments-secrets-observability.md) |

Team-fit output (verbatim from the check; all 5 factors are self-reported, so the verdict is only as good as that input):

```
Operational complexity budget: 2 / 5
Reasoning: start 1; operators = 2 (+1); on_call = false (0); containers = 2 (solid), IaC = 1 (some) (0); kubernetes = 0 (none), platform_team = false (0); preference = managed (-0.5) → 1.5 → 2.
Evidence: none; all 5 factors are self-reported.

| Option | Complexity | Verdict |
| A. Managed ML endpoint | 2 | Within |
| B. Serverless GPU containers | 3 | At limit |
| C. Kubernetes GPU serving | 3 | At limit |
```

My note next to the numbers: I rate C as **rejected** despite "At limit". The check only counts component classes, and the team has zero Kubernetes experience and nobody on call for GPU node problems. B's "At limit" has a named mitigation: it is the same container as A, and its extra part is a scheduled capacity change.

## Quality attributes
- **Latency (assumed target):** p95 < 1.5 s measured at the load balancer, at 50 req/s. Internal budget: edge and facade 50-100 ms, model queue plus prefill up to about 1.0 s at p95, 300 ms margin.
- **Availability (assumed):** 99.5% monthly for successful responses during US business hours; this is what business-hours-only response supports. Error budget: 99.5% ≈ 3 h 36 min per 30 days. A 99.9% target (43 min) would need on-call and a second region, so it is not set. Raise it only with that precondition.
- **RPO / RTO:** No user data is stored by the service, so RPO is about 0 for the service. Model artifacts and images are versioned and kept in a multi-region US bucket and registry. Recovery approach: **backup and restore** (redeploy the container and model into another US region). RTO is hours, not minutes, and mainly bounded by GPU quota and capacity in the second region. Firestore (keys, quotas) has managed backups, and the key data can be rebuilt.
- **Scaling limits to watch:** (1) GPU quota and stock in us-central1, the hard ceiling; (2) endpoint max replicas; (3) the per-request payload limit of the managed endpoint (the facade enforces the 8k-token cap well under it); (4) Firestore write rate if usage counters are written per request (aggregate in memory, flush every few seconds). Revisit the design above about 100 req/s sustained, or if average document length passes about 3,000 tokens.
- **Consistency with the team:** every target above is one the team can back without a pager. The service sheds load (429/503) rather than degrading latency, so failure is visible and short.

## Data handling (no regulation named)
Documents may contain personal or confidential data. Design position: self-hosted model, so document text never goes to a third-party model provider; no document text in logs or Firestore (log length, token count, label, request id only); TLS everywhere; encryption at rest by default. If a customer needs HIPAA, SOC 2 or a data-processing agreement, say so and the full residency and compliance check should be run: it would add controls and could constrain product choice (verify each GCP product's coverage first).

## Rough cost per option (monthly, estimate)
| Option | Range | Main drivers |
|---|---|---|
| A. Managed ML endpoint | $4k-12k | GPU type and replica-hours; always-on minimum replicas overnight; average document length |
| B. Serverless GPU containers | $3k-9k | GPU-hours (scale to zero off-hours); average document length; L4-only GPU choice means more instances |
| C. Kubernetes GPU serving | $3k-9k plus cluster fee | GPU node-hours; idle node headroom; same model drivers |

Non-GPU parts (Cloud Run facade, load balancer, Cloud Armor, Firestore, logging, storage) add roughly $300-800 in all options. The GPU line could move 2-3x either way, depending on measured throughput per GPU (not yet measured) and on committed-use discounts. Rough estimates — verify with each provider's pricing calculator.

## Risks
| Risk | Impact | Mitigation in the design |
|---|---|---|
| GPU quota or capacity is not available at peak | 429s at peak hours | Request quota early; reserve baseline capacity; shed load explicitly (ADR 0005) |
| Throughput per GPU is lower than assumed | Cost 2x+ or p95 miss | Load test with real documents before commit; fitness criteria in ADR 0002 |
| Quantisation (for cost) lowers classification accuracy | Quality regression | Accept only after an offline eval on the held-out set (ADR 0003) |
| Long documents blow latency | p95 miss | Hard token cap at the facade (ADR 0004) |
| An 8B LLM is more model than the task needs | Over-spend | Revisit: a distilled smaller classifier could cost 10x less (see Revisit in ADR 0002) |
| Single region outage | Hours of downtime | Accepted at 99.5% (ADR 0006) |

## Files
[options.md](options.md) · [diagrams.md](diagrams.md) · [adr/README.md](adr/README.md) · [decision-brief.md](decision-brief.md)
