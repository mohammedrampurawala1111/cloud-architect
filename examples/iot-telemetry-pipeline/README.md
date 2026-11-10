# IoT telemetry pipeline: architecture

> Starting design for human review, not a production sign-off. Prices, quotas and regional availability are estimates to verify. The CTO decides; every ADR is **Proposed**.

Contents: [options](options.md) · [diagrams](diagrams.md) · [ADRs](adr/README.md) · [controls (residency)](controls.md) · [decision brief](decision-brief.md)

## Requirements summary: IoT telemetry pipeline
**What it does:** ingests one JSON reading per device every 10 seconds, raises threshold alerts within 5 seconds, keeps 13 months of history for dashboards, and sends finance a daily export.
**Users & traffic:** 20,000 devices, so 2,000 readings/s steady (about 173 M/day, 5.2 B/month). Assumed payload about 300 bytes (about 0.6 MB/s, about 52 GB/day raw JSON). Traffic is flat (every device on a fixed timer), but devices may reconnect together after an outage, so ingest must absorb a 3-5x burst.
**Data:** time-series readings, about 67 B rows over 13 months (about 3-4 TB as compressed Parquet, estimate). Small relational-style data: device registry, thresholds, alert state.
**Latency / availability:** alert path p99 under 5 s, device publish to notification handed to the delivery provider. Availability assumed 99.9% for the alert path (error budget about 43 min per 30 days) and 99.5% for dashboards and export. RPO and RTO are assumed (see Quality attributes).
**Integrations:** alert delivery (email, SMS, on-call tool), finance team (daily file), dashboard users.
**Constraints:** customers in Australia; AWS; no Kubernetes; Terraform; Python and Go. No budget figure given.
**Team:** 5 engineers, on-call rotation exists, containers 2/3, Terraform 2/3, Kubernetes none, AWS solid. Preference assumed managed.
**Assumptions I made:** (no follow-up questions were possible)
1. Devices speak MQTT over TLS and hold per-device X.509 certificates, or their firmware can be updated to. If they only speak HTTPS, Option B becomes the fit.
2. Alert rules are static thresholds per device type or device (min/max, "N of last M readings"). No ML, no cross-device correlation. "Within 5 s" means device publish to notification handed to the delivery provider.
3. "Device offline" detection is needed but not at 5 s; a once-a-minute last-seen check is enough.
4. Dashboards serve staff and customers, at most about 50 concurrent users, multi-second query latency acceptable. Fine resolution (raw or 1-5 min) is needed for recent data, hourly or daily for older data. Raw drill-down across all 13 months is rare.
5. The finance export is a daily CSV usage summary per customer and device (reading counts, uptime, billable units), ready by 06:00 Sydney time. It contains no raw readings.
6. Telemetry linked to a customer site or person may be personal information under the Privacy Act, so it is treated as personal. Alert messages carry device IDs only, no names or addresses.
7. Telemetry is one-way (no commands to devices). Devices buffer readings while disconnected; if they don't, gaps in history are accepted.
8. Production and non-production run in separate AWS accounts, all infrastructure in Terraform, GitHub Actions for CI/CD.
9. Growth of up to 2x devices in 24 months.

## Recommendation
**Option A: managed device broker and serverless pipeline**, in AWS Sydney (ap-southeast-2) with backups in Melbourne (ap-southeast-4).

IoT Core (Basic Ingest) → Kinesis Data Streams → two consumers: a Lambda alert evaluator (thresholds and alert state in DynamoDB, notifications via SNS) and Firehose writing Parquet to S3. History is S3 plus Athena with scheduled rollups, Managed Grafana for dashboards, and a scheduled Athena job for the finance export.

Why:
1. **It meets the 5-second target with margin and no always-on servers of ours.** Expected p99 is about 2-3 s ([ADR-0003](adr/0003-lambda-alert-evaluator.md)).
2. **It costs about the same as building our own ingest.** Option B saves nothing at this volume once certificate-authority fees are counted, and adds a service the team must patch, scale and be paged for ([ADR-0001](adr/0001-managed-device-broker.md)).
3. **It fits the team.** Complexity 3 against a budget of 4, with no Kubernetes, no self-run brokers or databases; the pieces are standard AWS managed services the team already knows.
4. **History is cheap and portable.** S3 Parquet queried by Athena handles 67 B rows for hundreds of dollars a month ([ADR-0004](adr/0004-s3-parquet-athena-history.md)).

Option B is the fallback if devices cannot speak MQTT. Option C is not recommended; it uses the whole complexity budget for no requirement we have.

## Team fit (from `plan.py`)

**Operational complexity budget: 4 / 5**
Reasoning: start 1; operators = 5 (+1); on_call = true (+1); containers = 2 (solid), IaC = 2 (solid) (+1); kubernetes = 0 (none), platform_team = false (0); preference = managed (-0.5) → 3.5 → 4.
Evidence: none; all 5 factors are self-reported.

| Option | Complexity | Verdict |
|---|---|---|
| A. Managed device broker and serverless | 3 | Within |
| B. Own ingest service on managed containers | 3 | Within |
| C. Self-run broker, Kafka and time-series database | 4 | Within |

My comment next to the numbers: C is "Within" only because it sits exactly at the budget; there is no headroom, and it would put a self-run MQTT cluster and a self-hosted time-series database on a 5-person team. The factors are all self-reported, and the verdict does not separate A from B, so the A-versus-B choice rests on the reasoning above rather than on the score.

## Quality attributes (for Option A)
| Attribute | Target (assumed) | Design basis |
|---|---|---|
| Alert latency | p99 under 5 s, design aim p95 under 2.5 s | Basic Ingest, Kinesis with enhanced fan-out consumer, Lambda with provisioned concurrency (no cold start), batch window 0 |
| Alert path availability | 99.9% (about 43 min per 30 days). Assumes the existing on-call rotation; without it, target 99.5% | Multi-AZ managed services, no single instance on the path |
| Dashboards and export availability | 99.5% (about 3.6 h per 30 days) | Business-hours response is enough |
| Dashboard query latency | p95 under 10 s for rollups, under 30 s for raw drill-down | Athena over partitioned Parquet |
| RPO | Alert config and state: 5 min (DynamoDB PITR). History: 15 min (S3 replication to Melbourne) | |
| RTO | Single-AZ failure: none (multi-AZ). Whole-region loss: 4 h, **alerting is down until recovery** | Pilot light: Terraform for ap-southeast-4, replicated S3 data, DynamoDB backup copy ([ADR-0007](adr/0007-single-region-pilot-light.md)) |
| Data retention | 13 months, then deleted | S3 lifecycle expiry at 400 days |

**Scaling limits to watch** (verify current quotas):
- Kinesis: one shard takes 1 MB/s or 1,000 records/s. 2,000 rec/s needs at least 2 shards; plan 6 for burst headroom.
- IoT Core: account limits for connections, inbound publish rate and rule-trigger rate (verify defaults for ap-southeast-2; raise by support request before launch).
- Lambda: concurrency equals shards × parallelization factor, well under the default account limit at this size.
- Athena: concurrent query quota is the likely first wall as dashboard users grow.
- Revisit the design at about 100,000 devices, 1-second reporting, or more than about 50 concurrent dashboard users.

## Rough monthly cost (USD, estimate, ap-southeast-2)
| Option | Range | Main drivers |
|---|---|---|
| A. Managed broker and serverless (recommended) | $3,000-5,000 | IoT Core rule and action fees on 5.2 B messages; Lambda invocations; Athena and S3 |
| B. Own ingest on Fargate | $2,500-4,500 | ALB and always-on Fargate tasks; private CA certificates; same data tier as A |
| C. Self-run broker, Kafka, time-series DB | $3,500-7,000 | Always-on broker and database nodes (multi-AZ); MSK; replicated storage |

Option A depends on devices publishing to Basic Ingest topics (`$aws/rules/...`). With ordinary publish and subscribe, IoT Core messaging fees would add roughly $4,000-5,000 per month. Details in [options](options.md). Rough estimates — verify with each provider's pricing calculator.

## Top risks
| Risk | Impact | Mitigation |
|---|---|---|
| Devices cannot use MQTT or Basic Ingest topics | Cost rises or Option A is not buildable | Confirm firmware capability first (the cheapest check in the project); fall back to B |
| IoT Core message fees grow faster than expected (more devices, faster reporting) | Cost | Cost alarm on message count; revisit when above 50,000 devices ([ADR-0001](adr/0001-managed-device-broker.md)) |
| Regional outage stops alerting | Missed alerts for up to the RTO | Accepted explicitly ([ADR-0007](adr/0007-single-region-pilot-light.md)); CTO to confirm |
| Reconnect storm after an outage | Throttling at the broker or stream | Device-side jittered backoff; Kinesis headroom; quotas raised in advance |
| Athena too slow for customer dashboards | Poor dashboard experience | Rollup tables; documented trigger to add a serving database |
| Alert noise or silent failure (rule bug) | Alerts missed or ignored | Synthetic heartbeat device with a known breach, alarmed end to end |
| Residency interpretation (telemetry as personal information) | Compliance rework | Legal review of [controls](controls.md) |
