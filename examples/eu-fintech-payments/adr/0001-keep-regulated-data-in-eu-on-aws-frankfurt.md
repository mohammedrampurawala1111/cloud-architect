# ADR-0001: Keep regulated data in the EU, on AWS eu-central-1

- **Status:** Proposed
- **Date:** 2026-11-10
- **Deciders:** CTO

## Context
We are a BaFin-supervised financial entity under DORA; customer data must stay in the EU. No provider is named, no existing cloud contract is known. We need synchronous multi-zone database replication, a payment key service, write-once storage, and strong certifications (PCI DSS, ISO 27001, C5; verify).

## Decision drivers
- Residency: EU only (assumed level R1 plus customer-managed keys).
- Team fit: 4 of 4 for every option; managed services keep us there.
- Portability for the DORA exit plan.
- Cost: option B €10,000-€20,000/month (estimate).

## Options considered
1. AWS eu-central-1 with a second EU region for DR (option B).
2. Other hyperscaler EU region (Azure Germany West Central, Google europe-west3): comparable, no decisive advantage found, no existing account.
3. EU-headquartered provider (option C): removes the foreign-parent flag, but adds Kubernetes, self-run identity and an external HSM.

## Decision
We chose **AWS eu-central-1 (Frankfurt) with a second EU region for disaster recovery** because the managed services we need exist in one place, and it keeps the team at 4 of 4 without Kubernetes. We accept the 🟡 foreign-parent rating and mitigate it with customer-managed keys, an EU-only region policy and the exit plan in ADR-0007. Option C is the fallback if R3 is required.

## Consequences
- Portability: Adaptable overall; the key service is Locked (ADR-0004).
- Residual risk: US legal reach (CLOUD Act) over the provider, which counsel must assess.
- Global services (IAM control plane, support access, DNS) are flagged in [controls](../controls.md).

## Fitness criteria
1. An organisation-level policy denies all regions outside the chosen EU regions; verified by an attempted resource creation in us-east-1 failing.
2. All data stores, backups and log archives are in eu-central-1 or the named second EU region, checked by an inventory report with zero non-EU resources.
3. Customer-managed keys encrypt the ledger, the vault, backups and the audit archive.

## Revisit when
BaFin or counsel requires R3; the AWS European Sovereign Cloud is evaluated; a provider incident or concentration review fails.
