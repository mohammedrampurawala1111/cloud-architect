# ADR-0005: Send email through a queue and a managed email service

- **Status:** Proposed
- **Date:** 2026-11-10
- **Deciders:** CTO

## Context
Email notifications cover job assignment, schedule changes, and report links. Volume is modest (assumed under 100,000 per month). Deliverability and not losing messages matter more than speed. Messages contain names and service addresses, which are personal data.

## Decision drivers
- No servers to run (team-fit).
- Do not block API requests on email.
- Personal data stays with in-region providers where possible ([ADR-0002](0002-canadian-region-residency.md)).

## Options considered
1. **Queue + worker + the cloud provider's email service (SES in `ca-central-1`).**
2. Third-party email API (SendGrid, Postmark and similar): good tooling, but a US sub-processor receiving personal data (🔴 jurisdiction rating).
3. Send directly from the API function: simple, but ties request latency to email and loses messages on failure.

## Decision
We chose **a queue feeding a worker that sends through SES in `ca-central-1`**, because it decouples sending from requests, retries automatically, and keeps the provider in the same region and account as the rest of the platform. Emails carry a minimum of personal data and use time-limited links for reports, not attachments. Bounces and complaints come back through a notification topic into a suppression table.

## Consequences
- Pros: cheap; retries; no extra vendor.
- Cons: fewer analytics and template tools than dedicated providers; production access needs a one-time request to leave the sandbox; the sending domain needs SPF, DKIM and DMARC set up.
- **Portability: Adaptable** (SMTP or another API behind one `Mailer` interface).

## Fitness criteria
1. The API never calls the email service directly; only the worker does, via the `Mailer` interface (lint or import rule).
2. The sending domain passes SPF, DKIM and DMARC (`p=quarantine` or stricter), and bounce/complaint rates are tracked with an alarm at 2% bounce.
3. Report emails contain a pre-signed link that expires within 7 days and no attachment.

## Revisit when
- Bounce or complaint rates threaten the sender reputation, or marketing email is added (CASL consent rules apply; check with counsel).
- SMS or push notifications are added (new sub-processor review).
