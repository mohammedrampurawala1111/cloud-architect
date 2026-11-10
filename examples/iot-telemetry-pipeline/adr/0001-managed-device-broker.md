# ADR-0001: Use a managed device broker (IoT Core, Basic Ingest) for ingestion

- **Status:** Proposed
- **Date:** 2026-11-10
- **Deciders:** CTO

## Context
20,000 devices each send a JSON reading every 10 s (2,000 messages/s, 5.2 B/month). Each device needs its own identity, and the team must run this with 5 engineers and an existing on-call rotation.

## Decision drivers
- Team-fit: budget 4 / 5; avoid owning a broker or a certificate authority.
- Per-device identity and revocation for 20,000 devices.
- Cost: roughly equal to building our own ingest (see options.md).
- Portability: devices keep a standard protocol (MQTT over TLS).

## Options considered
- **A. IoT Core with Basic Ingest** (complexity 3 overall).
- **B. Own Go ingest on Fargate with mutual TLS and a private CA** (complexity 3, more to run, roughly the same cost).
- **C. Self-run MQTT cluster** (complexity 4).

## Decision
We chose IoT Core with Basic Ingest because it gives per-device certificate identity and revocation with nothing to patch or scale, because B saves nothing measurable at this volume while adding a service and a CA to operate, and because C uses the whole complexity budget for no requirement. Devices publish to `$aws/rules/...` topics so that messaging fees are not charged on top of rule fees (verify current pricing).

## Consequences
- Cost grows linearly with message count (about $0.30 per million messages through rule plus action, estimate).
- Devices must support MQTT and publish to Basic Ingest topics. This is an assumption to verify first.
- Nothing else can subscribe to device messages through the broker; consumers read from Kinesis.
- Portability: **Adaptable** (standard MQTT and X.509; registry, certificates and rules need migrating).

## Fitness criteria
1. Every device connects with its own X.509 certificate; no shared credentials (check: the IoT registry has one certificate per device).
2. Devices publish only to Basic Ingest topics (check: IoT Core usage shows no billed publish-subscribe messaging beyond a documented allowance).
3. A cost alarm fires if monthly IoT Core message volume exceeds 6.5 B.

## Revisit when
- Devices cannot use MQTT or Basic Ingest: choose B.
- Fleet exceeds about 50,000 devices or reporting is faster than every 5 s, and IoT Core cost exceeds about $8,000/month: re-cost B.
