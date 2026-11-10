# EU card-payments platform: architecture

Status: **Proposed**, awaiting the CTO's decision. Date: 2026-11-10.
Starting design for human review, not a production sign-off.

Files: [options](options.md) · [diagrams](diagrams.md) · [controls (DORA / PCI / GDPR)](controls.md) · [decision brief](decision-brief.md) · [ADRs](adr/README.md)

## Requirements summary: EU card-payments platform
**What it does:** card-payment processing API for merchants (authorise, capture, refund, webhooks), a double-entry ledger, a merchant dashboard, and real-time fraud scoring.
**Users & traffic:** merchants' servers and browsers via the API (500 TPS peak, given); merchant staff on the dashboard (low volume). Average assumed ~100 TPS, so peak is about 5x average.
**Data:** card data (PAN, expiry; no CVV storage after authorisation), personal data of merchants and cardholders, financial ledger entries, fraud features and decisions, audit logs. Ledger retention assumed 10 years (verify against HGB/AO/GwG with counsel).
**Latency / availability:** 99.95% availability (error budget about 21.6 min per 30 days); RPO 0 for the ledger (given). Latency targets are assumed, see below.
**Integrations:** acquirer(s) and card schemes, a 3-D Secure server provider, merchant webhooks, bank/settlement files.
**Constraints:** regulated financial entity (DORA, BaFin); customer data stays in the EU; PCI DSS because we handle card data.
**Team:** 10 engineers, 3 of them on ops with an on-call rotation, no platform team; strong Terraform and containers, Kubernetes 1 on a 0-3 scale; Java/Kotlin.
**Assumptions I made** (you could not answer questions, so these stand until corrected):
1. We are a licensed payment institution (ZAG) acting as a PSP/gateway towards one or more acquirers. We are not a card-scheme member and do not issue cards.
2. Card-not-present e-commerce only. No terminals, no PIN handling. If PIN or terminal traffic is added, the HSM design changes.
3. We store PANs (needed for capture, refunds, retries), so we are a PCI DSS service provider and need a cardholder data environment (CDE). The design keeps that environment as small as possible.
4. Merchants and cardholders are in the EU/EEA. Residency level **R1** (in-region, EU only), plus customer-managed keys as an extra control. This is not R3: a US-parented hyperscaler is acceptable to the CTO with documented mitigations. This is the biggest assumption; if you need R3, option C is the starting point.
5. "RPO 0" means no acknowledged ledger write is lost on instance or availability-zone failure. For loss of a whole region it is not achievable on a managed database without paying latency on every payment; the design accepts a replication lag of about a second there and closes the gap by reconciliation (see Quality attributes). **The CTO must explicitly accept or reject this.**
6. Greenfield: no existing system, no org profile or platform guardrails, no existing cloud contract or credits.
7. The team prefers managed services, builds in Kotlin/Java, uses Terraform and a hosted Git/CI service.
8. DORA is lex specialis for us; NIS2 is not layered on top (verify with counsel).

## Recommendation
**Option B: a modular monolith on managed containers, with a managed PostgreSQL-compatible ledger database, on AWS eu-central-1 (Frankfurt), with a pilot-light disaster-recovery region in the EU.** Why:
- It is the simplest design that meets 99.95% and RPO 0 for AZ failures: no servers or control planes to run, and the ledger database replicates synchronously across three zones.
- It fits the team: containers and Terraform are strengths, Kubernetes is not (1 of 3).
- Portability for DORA exit: containers plus standard PostgreSQL plus OIDC. Nothing in the critical path requires a proprietary programming model (unlike Lambda-based option A).
- Option C (EU-headquartered provider) is the right answer if the CTO or BaFin requires R3 or sovereign-provider status, but it adds Kubernetes and self-run identity/HSM work to a team that is at its limit.

Rejected because: Kubernetes, service mesh, Kafka, microservices, event sourcing and multi-region active-active are all left out. No requirement demands them and each would push the team beyond its budget (see ADRs 0002, 0003, 0006).

## Team fit (script output, verbatim)
### Team fit

**Operational complexity budget: 4 / 5**
Reasoning: start 1; operators = 3 (+1); on_call = true (+1); containers = 3 (expert), IaC = 3 (expert) (+1); kubernetes = 1 (some), platform_team = false (0); preference = managed (-0.5) → 3.5 → 4.
Evidence: none; all 5 factors are self-reported.

| Option | Complexity | Verdict |
|---|---|---|
| A. Serverless functions on AWS | 4 | Within |
| B. Managed containers on AWS | 4 | Within |
| C. EU-headquartered provider with managed Kubernetes | 4 | Within |

My comments next to the numbers (the numbers are unchanged): all inputs are self-reported, and all three options score the same, so the verdict does not choose between them. Every option sits exactly at the budget (4 of 4), which means no headroom. The score is driven by the regulated-payments extras (acquirer VPN, HSM), not by the compute choice. Option C additionally relies on Kubernetes skill at level 1 and on self-run Keycloak; I rate it the riskiest for this team even though the script says Within.

## Quality attributes (recommended option B)
| Attribute | Target | Basis |
|---|---|---|
| Availability, payment API | 99.95% monthly (about 21.6 min budget) | given |
| Availability, dashboard | 99.9% (about 43 min), assumed | not on the authorisation path |
| Latency, our overhead on authorisation | p95 ≤ 150 ms, p99 ≤ 300 ms, excluding the acquirer round trip | assumed |
| Fraud scoring inside that budget | p99 ≤ 40 ms | assumed |
| RPO, ledger, AZ or instance failure | 0 (synchronous storage replication across 3 AZs) | given |
| RTO, AZ or instance failure | automatic, about 1 min (database failover about 30-60 s) | managed failover, verify |
| RPO, whole-region loss | about 1 s (asynchronous cross-region replica), then reconciled | assumption 5 |
| RTO, whole-region loss | 2 h assumed | pilot light |

- **Recovery approach:** multi-AZ in Frankfurt for everything on the payment path; pilot-light in a second EU region (eu-west-1 Ireland or eu-west-3 Paris, to be chosen; both EU) with a cross-region database replica, images replicated, infrastructure code ready to scale up. Point-in-time recovery on the ledger database; backups stay in the EU, plus an encrypted copy at a second EU provider (ADR-0007).
- **Why a region loss may breach the SLO:** one 2-hour regional outage uses about six months of error budget. The 99.95% target is therefore stated as "excluding declared regional disasters"; the CTO should approve this wording. Active-active across regions would remove it, but needs synchronous cross-region ledger writes (latency on every payment) or self-run databases (budget 4+ for this team). Not recommended.
- **Consistency with the team:** 99.95% requires 24/7 response. Three people doing on-call is thin for 24/7 (a rotation of one in three), and the target assumes this on-call exists and that the 3 ops engineers are not also the only people able to deploy. This is a precondition of the recommendation, not a plan.
- **Scaling limits to watch:** (1) Aurora writer: one writer instance; at roughly 2,000-4,000 ledger inserts/s the writer is the ceiling, and 500 TPS payments x about 3 entries leaves about 2x to 3x headroom; revisit at 1,000 TPS sustained. (2) Hot accounts: a single merchant balance row will serialise writers, so balances are derived from entries with periodic snapshots (ADR-0003). (3) Connection count to the database: use a connection pool (RDS Proxy or in-app pool) and keep task counts bounded. (4) Fargate and API quotas per region: check the service quotas before launch (verify). (5) Fraud cache memory.

## Rough monthly cost per option (estimates, production plus DR plus non-production)
| Option | Range | Main drivers |
|---|---|---|
| A. Serverless on AWS | €9,000-€18,000 | database (three-AZ instances plus DR replica), provisioned concurrency for Java, HSM/Payment Cryptography, log ingestion |
| **B. Managed containers on AWS (recommended)** | **€10,000-€20,000** | database instances and DR replica (about half), always-on Fargate tasks across 3 AZs, HSM/Payment Cryptography, log ingestion and NAT egress |
| C. EU provider with managed Kubernetes | €8,000-€18,000 (high uncertainty) | database nodes, Kubernetes worker nodes, hosted HSM contract, self-run identity |

Rough estimates, from memory, no pricing tool was connected; verify with each provider's pricing calculator. Detail in [options](options.md).

## Top risks
| Risk | Why it matters | Mitigation in the design |
|---|---|---|
| Regional disaster vs RPO 0 and 99.95% | requirement cannot be met literally | explicit CTO acceptance, reconciliation against acquirer settlement files, tested DR (ADR-0003) |
| Team at its complexity limit (4 of 4) and 24/7 on-call with 3 people | burnout, slow incident response, DORA incident-reporting deadlines | managed services only, no Kubernetes; consider hiring or a managed on-call partner (CTO decision) |
| PCI DSS scope creep | cost, audit effort | small isolated CDE account, tokenisation, PAN never in logs (ADR-0004) |
| US-parented provider (CLOUD Act) and DORA concentration risk | regulatory scrutiny | customer-managed keys, EU-only regions, tested exit and second-provider backup (ADR-0001, 0007) |
| Aurora-specific features creeping into the code | exit cost | use only the PostgreSQL feature set; fitness criterion in ADR-0003 |
| Fraud model or cache outage | declines or fraud losses | rules-only fallback with a defined fail policy (ADR-0005) |

## Open items for counsel and compliance
See [controls](controls.md), section 6. Nothing here is legal advice.
