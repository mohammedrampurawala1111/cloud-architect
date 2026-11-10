# Decision brief: EU card-payments platform

**From:** Principal architect · **To:** CTO · **Date:** 2026-11-10
**Decision needed:** which architecture to build for the payments API, ledger, dashboard and fraud scoring · **By:** before detailed design and the PCI/BaFin planning start

## Context
- A card-payment platform for EU merchants at 500 TPS peak, 99.95% availability, ledger RPO 0, under DORA and BaFin, with customer data in the EU.
- The constraint that shapes the decision: a team of 10 (3 on ops with on-call, no platform team, Kubernetes skill 1 of 3) building a regulated system.
- Team: 10 engineers, on-call exists; operational complexity budget **4 / 5**, and every option scores 4. There is no headroom.

## Options at a glance
| | A. Serverless on AWS | B. Managed containers on AWS | C. EU provider + Kubernetes |
|---|---|---|---|
| Fits the team? | Within | Within | Within (I rate it least comfortable) |
| Rough cost / month (estimate) | €9,000-€18,000 | €10,000-€20,000 | €8,000-€18,000 |
| Ops burden (highest component) | Low (compute); same elsewhere | Low to medium | High (Kubernetes, identity, HSM) |
| Time to first release | Fastest | Moderate | Slowest |
| Lock-in | High (functions, gateway) | Medium | Low to medium |
| Meets residency and compliance needs? | Yes, R1 with mitigations | Yes, R1 with mitigations | Yes, R1 and a candidate for R3 |
| Main risk | Java cold starts, hard exit | Foreign-parent jurisdiction | Team capacity, thinner managed services |

Costs are from memory, no pricing tool: verify with provider calculators. All team-fit inputs are self-reported.

## Recommendation
I recommend **B** because:
1. It is the simplest design that meets 99.95% and RPO 0 across zone failures, with no clusters to run.
2. It uses what the team is strong at (containers, Terraform) and avoids the one thing it is not (Kubernetes).
3. It keeps a credible DORA exit (containers, standard PostgreSQL, OIDC, second-provider backup).

A is the fallback if time to market outweighs exit risk. C becomes right if BaFin, counsel or a key customer requires an EU-headquartered provider (R3).

## What approving B commits us to
- Spend: roughly €10,000-€20,000/month infrastructure (estimate; detailed costing is yours).
- Team: 24/7 on-call across three people is a precondition for 99.95% and is thin; the design assumes the CTO addresses it (hire, rotation size or an on-call partner). I am not planning that here.
- Reversibility: the payment key service and any use of provider-specific database features are the hard-to-undo parts; the code rules in ADR-0003, 0004 and 0007 limit this.

## Decisions I need from you, beyond the option
1. **Region-loss wording.** RPO 0 holds for zone and instance failure. For loss of a whole region the design has a lag of about a second, closed by reconciliation, and a 2-hour RTO that would use about six months of error budget. Do you accept "99.95% excluding declared regional disasters" and "RPO 0 within a region"? Otherwise we need synchronous cross-region writes on a self-run database, which exceeds the team's budget.
2. **Residency level.** Is a US-parented hyperscaler acceptable with customer-managed keys (R1)? If not, choose C.
3. **PCI DSS scope.** Confirm that we store PANs ourselves rather than use a third-party vault.

## Top risks
| Risk | Impact | Mitigation |
|---|---|---|
| Region loss vs RPO 0 / 99.95% | Requirement not literally met | CTO acceptance, reconciliation, annual DR test (ADR-0003) |
| Team at limit with thin on-call | Slow incident response, DORA deadlines missed | Managed-only stack; staffing decision |
| PCI scope creep | Audit cost, breach exposure | Isolated CDE, daily PAN scan (ADR-0004) |
| Foreign-parent jurisdiction, concentration | Supervisory challenge | CMKs, EU-only policy, exit test (ADR-0001, 0007) |

## Decision
- [ ] A. Serverless on AWS
- [ ] B. Managed containers on AWS (recommended)
- [ ] C. EU provider with managed Kubernetes
- [ ] Not yet: need … (more information, a spike, a pilot)

Decided by: ________ Date: ________ Conditions: ________

Details: [README](README.md) · [options](options.md) · [diagrams](diagrams.md) · [ADRs](adr/README.md) · [controls](controls.md)
