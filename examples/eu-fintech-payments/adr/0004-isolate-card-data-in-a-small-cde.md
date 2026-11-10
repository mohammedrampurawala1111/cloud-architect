# ADR-0004: Isolate card data in a small CDE with tokenisation and a key service

- **Status:** Proposed
- **Date:** 2026-11-10
- **Deciders:** CTO

## Context
We process and store PANs and so fall under PCI DSS as a service provider (assumption). Every system that can touch PANs is in scope for audit, hardening and logging. Our ten engineers cannot afford a platform-wide cardholder data environment.

## Decision drivers
- PCI DSS scope and audit cost.
- Security: PAN leakage through logs, queues or analytics.
- Team fit: managed key service, not a self-run HSM cluster.

## Options considered
1. Everything in scope: simplest to build, largest audit and breach surface.
2. Small isolated vault: PAN enters and leaves only through the vault, other services handle tokens.
3. Outsource tokenisation to a third-party vault: smallest scope, but a new critical ICT provider and likely PAN outside our control; possible later.

## Decision
We chose **a small card vault in a separate cloud account (the CDE)**: it receives PANs over TLS, encrypts them with keys in the payment key service, stores them in its own database, returns tokens, and is the only component that sends authorisation messages to acquirers. The core service sees tokens and masked data only. Non-production has no network path to the CDE and uses test PANs.

## Consequences
- Portability: the vault code is portable; the key service is **Locked**. A move needs a key ceremony and wrapped key export; design keys as exportable key blocks where the product allows (verify).
- One extra network hop (vault) on the authorisation path: budget about 10 ms.
- PCI scope is limited to the vault, the CDE account, its network and the people with access.

## Fitness criteria
1. A scan of the ledger database, queues, logs and analytics exports for PAN patterns (Luhn-valid 13-19 digits) returns zero hits; run daily.
2. Only the vault's role can use the PAN encryption keys, shown by the key policy.
3. Security groups in the production account have no rule reaching the CDE database; non-production has no route to the CDE.

## Revisit when
Terminals, PIN or P2PE are added; outsourced tokenisation becomes cheaper than a PCI assessment; PAN storage is no longer needed (network tokens only).
