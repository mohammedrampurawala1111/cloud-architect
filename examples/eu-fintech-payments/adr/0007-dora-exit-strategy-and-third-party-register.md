# ADR-0007: DORA exit strategy: portable stack, second-provider backup, register

- **Status:** Proposed
- **Date:** 2026-11-10
- **Deciders:** CTO

## Context
DORA requires financial entities to manage ICT third-party and concentration risk, keep a register of information, and have exit strategies (planned and stressed) for providers supporting critical functions. Single-cloud is permitted, but we must show we could leave or survive losing the provider. Multi-cloud active-active would exceed the team budget (weight 5).

## Decision drivers
- DORA exit and concentration requirements.
- Team fit: no second runtime platform to operate.
- Cost.

## Options considered
1. Single cloud, no second copy: exit is only on paper.
2. Single cloud with portable building blocks, plus an encrypted backup copy at a second EU-headquartered provider and a periodic restore test there.
3. Multi-cloud active-active: rejected, budget.

## Decision
We chose **option 2**: container images, standard PostgreSQL, OIDC, Terraform, and OpenTelemetry are the portable core. A daily encrypted logical backup of the ledger and the vault (client-side encrypted, keys held by us; for the vault, only token-level exports unless PCI scope at the second provider is separately approved) is copied to a second EU provider. Once a year, restore the ledger from that copy into an isolated environment to prove the exit path. A register of ICT third parties (cloud, CI, 3DS provider, alerting, acquirer) is maintained with criticality and exit notes.

## Consequences
- Portability: this ADR is what keeps the Adaptable rating honest; the Locked key service has its own exit note (ADR-0004).
- Second provider costs a small amount for storage (estimate: a few hundred euros per month) plus egress.
- Does not give a hot standby at the second provider: a stressed exit means hours to days, not minutes. Say so in the exit plan.

## Fitness criteria
1. A restore of the ledger backup from the second provider into an isolated environment succeeds at least annually, with recorded duration.
2. The third-party register lists every ICT provider with criticality and exit approach; a CI check fails the build when a new provider appears in Terraform without a register entry.
3. No application module imports a provider-specific SDK outside the adapter packages (queue, secrets, identity, key service, storage).

## Revisit when
BaFin or an audit rejects single-cloud with this exit approach; the cloud provider is designated a critical ICT third-party provider with changes in terms; an exit test takes more than 72 hours.
