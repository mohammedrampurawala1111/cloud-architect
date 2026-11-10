# ADR-0006: Use a managed user pool for authentication

- **Status:** Proposed
- **Date:** 2026-11-10
- **Deciders:** CTO

## Context
B2B product with company-scoped users. Passwords, MFA, reset flows and token issuing are risky to build. A year-two request for customer SSO (SAML or OIDC) is likely. SOC 2 buyers expect MFA.

## Decision drivers
- No time or on-call capacity to run an identity server.
- In-region, in the same provider (no extra sub-processor).
- Standard tokens, so the app is not tied to one issuer.

## Options considered
1. **Managed user pool from the cloud provider (Cognito in `ca-central-1`).**
2. Third-party identity SaaS (Auth0, Clerk, etc.): richer B2B features (organisations, SSO), higher cost at scale, and a foreign sub-processor.
3. Self-run identity server (Keycloak): flexible, but a server to patch and back up; exceeds the budget.

## Decision
We chose **the provider's managed user pool with email+password and MFA**, because it needs no servers, stays in region, and issues standard OIDC tokens that the API gateway validates. Company membership and roles live in our database, not in token claims beyond `company_id` and role. Customer SSO is added later through the pool's federation.

## Consequences
- Pros: no auth servers; MFA built in; federation available.
- Cons: limited UI customisation; user export does not include password hashes, so leaving requires a password reset for all users; some B2B features (per-company SSO policies) are manual.
- **Portability: Adaptable** (standard OIDC at the API; the user store is the lock-in).

## Fitness criteria
1. The API validates tokens by issuer and audience through a standard JWT verifier; no handler calls the user pool SDK directly except the `identity` module.
2. MFA is enforced for all users with the dispatcher or admin role, and for all of our own staff accessing production.
3. Authorisation (company and role) is checked in the application and RLS ([ADR-0003](0003-shared-database-row-level-security.md)), never inferred from the client.

## Revisit when
- More than 10 customers ask for SSO with per-company policies, or the pool's limits (users, federation) are reached: evaluate a B2B identity SaaS.
