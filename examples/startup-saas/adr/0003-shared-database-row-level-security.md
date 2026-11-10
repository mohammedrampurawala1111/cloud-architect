# ADR-0003: One PostgreSQL database with row-level security for tenants

- **Status:** Proposed
- **Date:** 2026-11-10
- **Deciders:** CTO

## Context
200 companies, each with modest data, in a multi-tenant SaaS. A cross-tenant leak is the worst failure. The team can run one database; it cannot run hundreds.

## Decision drivers
- Team-fit budget 2/5: one database engine, one schema to migrate.
- Strong tenant isolation requirement (customer contracts, SOC 2 buyers).
- Per-tenant export and deletion on request.

## Options considered
1. **Shared database, shared schema, `company_id` column, row-level security (RLS).**
2. Schema per tenant: stronger separation, but 200 schemas to migrate and monitor.
3. Database per tenant: strongest isolation, highest cost and operations; exceeds budget.

## Decision
We chose **one Multi-AZ PostgreSQL 16 database with a `company_id` on every tenant table and RLS policies**, because it is the simplest thing the team can run and RLS gives a second layer of defence beyond application code. The application sets the tenant in the session for each request, inside a transaction, through one data-access wrapper; code outside the wrapper cannot query tenant tables.

## Consequences
- Pros: one migration path; lowest cost; easy cross-tenant admin metrics for us (through a separate role).
- Cons: noisy-neighbour risk; a mistake in the wrapper affects all tenants; per-tenant restore means exporting rows, not restoring a database.
- **Portability: Portable** (standard PostgreSQL features).

## Fitness criteria
1. Every table with a `company_id` column has RLS enabled and forced; the application role is not a superuser and does not have `BYPASSRLS` (checked by a CI query against the schema).
2. An automated test suite asserts that a request authenticated as tenant A cannot read or write tenant B rows on every endpoint.
3. A documented export-and-delete procedure for one company completes within 30 days; the audit log records privileged access to tenant data and is retained 1 year.

## Revisit when
- One tenant exceeds 20% of database load or storage.
- A customer requires dedicated infrastructure or customer-managed keys (move that tenant to its own database).
