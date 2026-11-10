# ADR-0008: Account structure, identity, secrets and observability baseline

- **Status:** Proposed
- **Date:** 2026-11-10
- **Deciders:** CTO

## Context
We need environment separation, strong identity for staff and merchant users, secret rotation, and logs and metrics that support DORA incident classification and PCI logging, without building an observability platform.

## Decision drivers
- PCI DSS segmentation and logging; DORA incident reporting inputs.
- Team fit: managed identity, secrets and observability (weight 1 each) rather than a self-run stack (weight 4).
- Residency: logs and telemetry stay in the EU.

## Options considered
1. Single account with namespaces/tags: cheap, weak isolation.
2. Separate accounts: non-production, production, CDE, security/log-archive.
3. Self-run observability stack: more control and portability, more on-call: rejected.

## Decision
We chose **option 2 with managed services**:
- **Accounts:** four, with organisation policy limiting regions to the EU and denying disabling of logging. Non-production has synthetic data only.
- **Staff identity:** single sign-on with MFA, short-lived role sessions, no standing production access, a documented break-glass path; every production and CDE session is logged.
- **Merchant identity:** managed identity service with MFA required for dashboard users, roles stored in our own tables.
- **Secrets:** managed secret store; database credentials and API signing keys rotate automatically (at most every 90 days; database passwords more often); no secrets in images or environment files; CI authenticates to the cloud by short-lived federation, with no long-lived keys.
- **Observability:** managed metrics and logs in Frankfurt, OpenTelemetry instrumentation, structured logs with PAN masking, immutable archive in the security account with write-once lock; alert on SLO burn rate for the payment API.
- **CI/CD:** hosted build; signed images pushed to the registry; two-person review for production changes; Terraform plan reviewed in the pipeline.

## Consequences
- Portability: Adaptable; OpenTelemetry and OIDC keep the backends replaceable.
- Cost driver: log ingestion; sample debug logs, keep audit logs complete.
- Four accounts mean cross-account roles to manage in Terraform (a team strength).

## Fitness criteria
1. Exactly four accounts exist with the named purposes; no IAM user with long-lived access keys exists (report shows zero).
2. Every secret in the store has a rotation schedule of 90 days or less; a report lists exceptions with zero.
3. Production and CDE logs are in an archive bucket with Object Lock in compliance mode and retention set by policy; log pipelines contain no non-EU endpoints.

## Revisit when
A SIEM becomes necessary for auditors; log cost exceeds 10% of infrastructure spend; non-EU staff need access.
