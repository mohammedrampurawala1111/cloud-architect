# Decision brief: IoT telemetry pipeline

**From:** Principal architect · **To:** CTO · **Date:** 2026-11-10
**Decision needed:** which architecture to build for ingesting, alerting on, storing and exporting data from 20,000 devices · **By:** before build kickoff

## Context
- We are building a pipeline for 20,000 devices reporting every 10 s: alerts within 5 s, 13 months of history for dashboards, a daily file for finance. Customers are in Australia.
- The constraint that shapes the decision is team capacity: 5 engineers, no Kubernetes, but an on-call rotation and solid AWS skills.
- Team: 5, on-call exists, operational complexity budget 4 / 5 (all factors self-reported).

## Options at a glance
| | A. Managed broker and serverless | B. Own ingest on Fargate | C. Self-run broker, Kafka, time-series DB |
|---|---|---|---|
| Fits the team? | Within (3 / 4) | Within (3 / 4) | Within (4 / 4, no headroom) |
| Meets residency and compliance needs? | Yes, Sydney with Melbourne backups ([controls](controls.md)) | Yes | Yes |
| Rough cost / month (estimate) | $3,000-5,000 | $2,500-4,500 | $3,500-7,000 |
| Ops burden (highest component) | Low | Medium (ingest service, certificate authority) | High (broker, database, stream processor) |
| Time to first release | 6-8 weeks | 8-10 weeks | 14+ weeks |
| Lock-in | Medium | Medium | Low |
| Main risk | Devices must speak MQTT; per-message cost scales with fleet | Certificate lifecycle for 20,000 devices; ingest scaling | Operating four stateful systems |

Rough estimates — verify with each provider's pricing calculator.

## Recommendation
I recommend **A** because:
1. It meets the 5-second target (expected p99 about 2-3 s) using managed services we do not patch or scale.
2. It costs about the same as B, so owning ingest buys nothing at this volume.
3. It leaves the most headroom in the team's complexity budget.

B is the fallback if devices cannot speak MQTT. C becomes right only if we need to leave AWS or require Australian-owned providers (R3).

## What approving A commits us to
- Spend: roughly $3,000-5,000/month infrastructure (estimate), growing linearly with device count; $4,000-5,000/month more if devices cannot use Basic Ingest topics.
- Team: the existing on-call rotation covers the alert path (99.9% target assumes it); Terraform and AWS skills already present.
- Reversibility: history (S3 Parquet) and the device protocol are portable; Step Functions and DynamoDB code are AWS-specific but small.
- Acceptance: a regional outage stops alerting until recovery (RTO 4 h). Please confirm.

## Top risks
| Risk | Impact | Mitigation |
|---|---|---|
| Firmware cannot use MQTT or Basic Ingest | Option A unbuildable or costlier | Verify in week 1; fall back to B |
| Regional outage stops alerts | Missed alerts up to 4 h | Accept explicitly, or fund active-active (ADR-0007) |
| Athena too slow for customer dashboards | Poor experience | Rollups now; add a serving database past 50 concurrent users |
| Telemetry is personal information | Compliance rework | Legal review of controls.md |

## Decision
- [ ] A. Managed broker and serverless (recommended)
- [ ] B. Own ingest on Fargate
- [ ] C. Self-run broker, Kafka, time-series DB
- [ ] Not yet: need more information (for example device capability check)

Decided by: ________ Date: ________ Conditions: ________

Details: [README](README.md) · [options](options.md) · [diagrams](diagrams.md) · [ADRs](adr/README.md) · [controls](controls.md)
