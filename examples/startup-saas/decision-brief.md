# Decision brief: Technician scheduling SaaS

**From:** Principal architect · **To:** CTO · **Date:** 2026-11-10
**Decision needed:** Which architecture to build for year one (serverless, managed containers, or Kubernetes). **By:** before infrastructure work starts.

## Context
- A multi-tenant web app, REST API, nightly reports and email notifications for 200 field-service companies in the US and Canada, about 30 requests/s at peak.
- The constraint that shapes the decision: three TypeScript developers, no Kubernetes experience, **no on-call**, and a wish to run as little infrastructure as possible.
- Team: 3 people, no on-call; operational complexity budget **2/5**. Some inputs were assumed, not confirmed.

## Options at a glance
| | A. Serverless | B. Managed containers | C. Kubernetes |
|---|---|---|---|
| Fits the team? | Within | At limit | At limit (Exceeds in practice) |
| Rough cost / month (estimate) | $300-600 | $350-700 | $600-1,200+ |
| Ops burden (highest component) | Low | Medium | High |
| Time to first release | Shortest | Slightly longer | Longest |
| Lock-in | Medium | Low | Low |
| Meets residency and compliance needs? | Yes, Canadian region ([controls](controls.md)) | Yes | Yes |
| Main risk | 15-minute report limit; cold starts | Always-on cost; image patching | Cluster upkeep with nobody on call |

## Recommendation
I recommend **A** because it is the only option Within the team's budget, 30 requests/s needs very little compute so pay-per-use fits, and nothing needs patching with nobody on call. B is the fallback if reports regularly approach the 15-minute function limit or cold starts hurt latency; the app is built so that move is a repackaging, not a rewrite. C becomes right only if the team gains a platform function or a requirement forces multi-cloud or many services.

## What approving A commits us to
- **Spend:** roughly $300-600/month infrastructure (estimate; detailed costing is yours). Not included: support plan, SOC 2 audit.
- **Team:** TypeScript and basic AWS skills; infrastructure as code; no on-call. **Availability target is 99.5% (about 3.6 hours per 30 days)**. Do not promise 99.9% in contracts until someone is paged.
- **Data location:** everything in AWS Canada (`ca-central-1`), backups in Calgary. A customer requiring US-only storage is not met.
- **Reversibility:** mostly easy (standard PostgreSQL, standard HTTP app). Hardest to undo: the managed user pool, because passwords can't be exported (users must reset).

## Top risks
| Risk | Impact | Mitigation |
|---|---|---|
| Cross-tenant data leak | Severe | Row-level security plus automated cross-tenant tests |
| Night-time outage with no on-call | Hours of downtime | 99.5% target; Multi-AZ self-healing; managed services |
| US-only residency demand | Lost deal or second stack | Ask in sales early; second stack is a new decision |
| Reports exceed time limit | Failed reports for the largest customer | Per-company jobs; fall back to a scheduled container task |
| Team-fit inputs are self-reported | Wrong verdict | CTO to check skill ratings; if containers are stronger than stated, B is acceptable |

## Decision
- [ ] A. Serverless (recommended)
- [ ] B. Managed containers
- [ ] C. Kubernetes
- [ ] Not yet: need more information, a spike or a pilot

Decided by: ________ Date: ________ Conditions: ________

Details: [README](README.md) · [options](options.md) · [diagrams](diagrams.md) · [ADRs](adr/README.md) · [controls](controls.md)

*Rough estimates, verify with each provider's pricing calculator. Controls are requirements, not legal advice.*
