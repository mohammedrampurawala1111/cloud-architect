# Decision brief: ML inference API

**From:** Principal architect · **To:** CTO · **Date:** 2026-11-10
**Decision needed:** Which architecture to build for serving the fine-tuned 8B document-classification model as a public API · **By:** before GPU quota requests and the first build sprint

## Context
- A public API for US customers: 50 requests/s at peak, p95 under 1.5 s, mostly business hours.
- The shaping constraint is team capacity: 3 ML engineers and 1 backend developer, no Kubernetes experience, no on-call.
- Team operational complexity budget: **2 / 5** (self-reported inputs).

## Options at a glance
| | A. Managed ML endpoint | B. Serverless GPU containers | C. Kubernetes GPU serving |
|---|---|---|---|
| Fits the team? | Within | At limit | At limit (I rate it rejected: no Kubernetes skills, no on-call) |
| Rough cost / month (estimate) | $4k-12k | $3k-9k | $3k-9k plus cluster fee |
| Ops burden (highest component) | Low | Medium | High |
| Time to first release | about 4-6 weeks | about 4-6 weeks | about 8-12 weeks |
| Lock-in | Low to medium | Low | Low |
| Main risk | Always-on GPUs overnight | Team owns the capacity schedule; fewer GPU choices | Operations the team cannot staff |

## Recommendation
I recommend **A** because:
1. It is the only option within the team's operating budget, and it needs no on-call: the provider replaces failed GPU machines.
2. It gets the team to a first release fastest and lets ML engineers use familiar model-deployment workflows.
3. It leaves the GPU type open, which matters because we have not yet measured throughput per GPU.

B is the fallback if overnight GPU cost proves too high (same container, small change). C becomes right if the company hires Kubernetes expertise or serves several models.

## What approving A commits us to
- **Spend:** about $4k-12k/month infrastructure, mostly GPUs (estimate; the biggest uncertainty is average document length and measured throughput). Rough estimates — verify with each provider's pricing calculator.
- **Team:** no on-call, so the design sets **99.5%** availability (about 3 h 36 min allowed downtime per month), not 99.9%. Customers must not be promised more.
- **Reversibility:** high. The model runs in a standard container with standard weights; moving to B or C is a configuration change, not a rewrite.
- **Quality of the sizing:** based on assumptions listed in the README (document size around 1,000 tokens, label-only output). A benchmark in the first sprint replaces them.

## Top risks
| Risk | Impact | Mitigation |
|---|---|---|
| GPU quota or stock is missing at peak | Errors (429) at peak hours | Request quota now; reserve baseline; explicit load shedding |
| Throughput per GPU is below assumption | Cost 2x or higher, or p95 missed | Benchmark with real documents before commit |
| An 8B LLM is more than the task needs | Overspend | Compare against a distilled smaller classifier |
| Regional outage | Hours of downtime | Accepted at 99.5%; artifacts replicated to a second region |
| Documents contain regulated data | Compliance gap | Not in scope today; run a full compliance check if a customer requires HIPAA or SOC 2 |

## Decision
- [ ] A. Managed ML endpoint (recommended)
- [ ] B. Serverless GPU containers
- [ ] C. Kubernetes GPU serving
- [ ] Not yet: need a benchmark or pilot first

Decided by: ________ Date: ________ Conditions: ________

Details: [README](README.md) · [options](options.md) · [diagrams](diagrams.md) · [ADRs](adr/README.md)
