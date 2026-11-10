# Field-service technician scheduling SaaS: architecture

> Starting design for human review, not a production sign-off. Prices, quotas and regional availability are estimates; verify before committing.

**Mode:** Full (a CTO decides; Canadian customers trigger a residency and privacy check). Nothing was confirmed with the requester, so every gap is an explicit assumption below.

Files: [options](options.md) · [diagrams](diagrams.md) · [controls (residency/compliance)](controls.md) · [decision brief](decision-brief.md) · [ADRs](adr/README.md)

## Requirements summary: technician scheduling SaaS
**What it does:** Multi-tenant B2B web app where dispatchers at field-service companies schedule technicians against jobs. It has a REST API, nightly per-company report generation, and email notifications.
**Users & traffic:** 200 customer companies in year one. About 30 requests/s at peak, so roughly 5-10 requests/s average over business hours, and far less overnight. Assumed 5,000-10,000 named users. Technicians use the responsive web app on phones.
**Data:** Companies, users, technicians, customers' service addresses, jobs, schedules, time entries, generated reports. Mostly relational. Assumed under 100 GB in year one. Retention 7 years for job records (assumed), reports kept 13 months. Strong consistency within a tenant.
**Latency / availability:** API p95 under 500 ms (assumed). Availability target 99.5% (see quality attributes). RPO 5 minutes, RTO 4 hours.
**Integrations:** Email (transactional notifications and report links). Address geocoding for routing (assumed, via an in-region service). No payments, no native mobile app, no SMS in year one.
**Constraints:** As little infrastructure as possible. Customers in the US and Canada.
**Team:** 3 developers, TypeScript, some AWS experience, no Kubernetes, no on-call, prefer managed.
**Assumptions I made:**
1. AWS is the provider, because the team has some AWS experience and no other cloud is mentioned.
2. No payment card data, no health data. Nothing is processed that triggers HIPAA or PCI DSS.
3. Residency level **R1 (in-region)**. All primary data stays in Canada (`ca-central-1`), which also serves US customers. No US customer is assumed to require US-only storage; verify in sales conversations.
4. Customers are companies (B2B) and will ask for SOC 2 in procurement. The design enables the technical controls; the audit is process work.
5. Login is email and password with MFA in year one. Customer SAML/SSO is a likely year-two ask.
6. "Nightly" means 01:00 in each company's local time. US and Canada span about 5 time zones, so reports run as an hourly sweep, not one global job.
7. Peak growth over year one is at most 3x the stated load. Beyond that, see the scaling limits.
8. No real-time push (live map, websockets) in year one. The UI refreshes by polling.

## Recommendation

**Build Option A: a modular TypeScript monolith on serverless functions with managed PostgreSQL, in AWS `ca-central-1`.**

Why:
- **It's the only option inside the team's budget.** The team-fit check gives a 2/5 budget; A is Within, B (containers) is At limit. With no on-call and no platform skills, nothing to patch or scale is better than something merely managed. See [ADR-0001](adr/0001-serverless-modular-monolith.md).
- **The load is small.** 30 requests/s at about 200 ms each needs roughly 6 concurrent executions, so serverless pay-per-use fits.
- **It keeps B available.** The app is written as one portable HTTP application with a thin Lambda adapter, so moving to containers later is a packaging change.
- **One region covers both countries.** Canadian data stays in Canada ([ADR-0002](adr/0002-canadian-region-residency.md)).

Fall back to B if nightly reports regularly approach the 15-minute function limit or cold starts hurt the p95 target (see ADR-0001 "Revisit when"). Kubernetes (C) is rejected: it exceeds what a three-person team with no Kubernetes experience and no on-call can run.

## Team fit (from `plan.py`, verbatim)

**Operational complexity budget: 2 / 5**
Reasoning: start 1; operators = 3 (+1); on_call = false (0); containers = 1 (some), IaC = 1 (some) (0); kubernetes = 0 (none), platform_team = false (0); preference = managed (-0.5) → 1.5 → 2.
Evidence: none; all 5 factors are self-reported.

| Option | Complexity | Verdict |
|---|---|---|
| A. Serverless | 2 | Within |
| B. Managed containers | 3 | At limit |
| C. Kubernetes | 3 | At limit |

My note next to these numbers: the script scores by component class, so C shows the same 3 as B. I treat C as **Exceeds** in practice, because the team's Kubernetes skill is 0 and there is no on-call for cluster upgrades and node problems. B's mitigation, if chosen, is to keep the single-service shape and use only Fargate (no EC2 nodes). Most inputs are self-reported, and the A-versus-B verdict decides the recommendation, so the CTO should check the skill ratings.

## Architecture in one paragraph

A React single-page app is served from object storage behind a CDN. It calls a REST API (API Gateway HTTP API in front of one TypeScript function containing all domain modules) directly, not through the CDN, so personal data never transits foreign edge locations. State is in one Multi-AZ PostgreSQL database with tenant isolation by row-level security. Email goes through a queue and a managed email service. Nightly reports use an hourly scheduler that finds companies whose local time is 01:00, enqueues one job per company, and a worker function writes the report to object storage and emails a time-limited link. Auth is a managed user pool. Everything runs in two AZs of `ca-central-1`; backups are copied to `ca-west-1` (Calgary).

Modules inside the monolith: `tenants`, `identity`, `scheduling`, `jobs`, `technicians`, `reports`, `notifications`. They are separated by folder and interface, not by network.

## Quality attributes (recommended option)

- **Availability: 99.5% (assumed), about 3.6 hours of error budget per 30 days.** The design is Multi-AZ throughout, and AZ failure should self-heal in minutes. Because there is **no on-call**, the target is deliberately set to what business-hours response supports. A 99.9% target (43 minutes per 30 days) would require someone to be paged, which is a precondition the team does not currently have; do not advertise 99.9% in contracts until it does.
- **Latency:** API p95 under 500 ms for schedule reads and writes (assumed). Cold starts add about 0.3-1 s on a Node function in a VPC (verify). If the p95 target is breached, add provisioned concurrency for the API function (a small fixed cost).
- **RPO / RTO:**
  - AZ failure: Multi-AZ failover, RPO 0, RTO a few minutes.
  - Data corruption or bad deploy: point-in-time recovery, RPO 5 minutes, RTO 4 hours (restore to a new instance).
  - Region loss: restore from the cross-region backup copy in `ca-west-1`, RPO up to 24 hours (daily copy; verify whether continuous replication of automated backups is available for the chosen engine), RTO 1 to 2 days. This is **backup and restore**, not warm standby: a second live region is not justified by any stated requirement and would exceed the team's budget. Backups stay in Canada.
- **Scaling limits to watch:**
  - Database connections (a small instance allows a few hundred): cap function concurrency at 100. Add a connection proxy when connections exceed 70% of `max_connections`.
  - Function account concurrency quota (default 1,000 per region (verify)): about 6-20 are expected at peak.
  - Reports: 15-minute function limit per company job. Revisit if any company's report takes more than 8 minutes.
  - The design needs revisiting at roughly 150 requests/s sustained, about 5x the year-one peak, or roughly 1,000 companies.
- **Identity, secrets, observability, backups, CI/CD, environments:**
  - Identity: managed user pool, MFA, short-lived JWTs verified by the API; service-to-service access by IAM roles only.
  - Secrets: managed secrets store; database credentials use managed rotation every 30 days; no secrets in environment variables of code or images.
  - Observability: structured JSON logs and metrics to the provider's logging service (no third-party APM, so no personal data leaves Canada via telemetry), with an external synthetic health check. Log retention 1 year, with personal data minimised in logs.
  - CI/CD: hosted CI pipeline deploying through pull-request review. Production has no manual console changes (infrastructure as code).
  - Environments: separate AWS accounts for production and non-production (organization with service control policies restricting regions to `ca-central-1` and `ca-west-1`, plus the global services used).

## Rough monthly cost (estimates, USD)

| Option | Range | Main drivers |
|---|---|---|
| A. Serverless (recommended) | $300-600 | Multi-AZ database; network egress to AWS services from VPC (NAT or endpoints in 2 AZs); logs |
| B. Managed containers | $350-700 | Always-on tasks (2 minimum); load balancer; NAT or endpoints in 2 AZs; database |
| C. Kubernetes | $600-1,200+ | Control-plane fee; always-on worker nodes in 2 AZs; the same database and NAT as B |

Rough estimates, verify with each provider's pricing calculator. Not priced: people, support plan, a SOC 2 audit.

## Top risks

| Risk | Impact | Mitigation in the design |
|---|---|---|
| Report job exceeds the function time limit | Reports fail for the largest company | One job per company; chunk by day range; fallback to a scheduled container task (B's component) |
| Tenant data leak via a query bug | Severe, breaches customer contracts | Row-level security in the database, a tenant-scoped connection wrapper, cross-tenant tests ([ADR-0003](adr/0003-shared-database-row-level-security.md)) |
| No on-call, and a night-time outage | Up to hours of downtime | 99.5% target only; Multi-AZ self-healing; managed services; no contractual 99.9% |
| US customer demands US-only data | Lost deal, or a second deployment | Ask early; the app has no hard-coded region, so a second stack in a US region is possible but is extra work ([ADR-0002](adr/0002-canadian-region-residency.md)) |
| Email deliverability and complaints | Missed notifications | Domain authentication (SPF, DKIM, DMARC), bounce and complaint handling ([ADR-0005](adr/0005-email-via-queue-and-ses.md)) |
| Managed auth lock-in | Password hashes cannot be exported | Standard OIDC tokens at the API; migration needs a password reset ([ADR-0006](adr/0006-managed-auth-user-pool.md)) |

## Out of scope
Infrastructure code, pipelines, runbooks, staffing and alert routing. Detailed costing, and an SMS/push notification channel, are the team's to decide.
