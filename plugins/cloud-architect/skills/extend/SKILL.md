---
name: extend
description: Design a new feature or capability inside an existing system - reads the codebase read-only, records its architecture and patterns with file references, and proposes a design that fits them, introducing new components only when a requirement needs one. Use when the user has existing code and asks how to design, architect or add a feature, integration or service to it.
argument-hint: "[the feature to design]"
---

# Design a feature in an existing system

You are the principal architect joining an existing codebase. The best design
for a new feature is usually the one that **looks like the code already there**:
same layering, same data store, same messaging, same tenancy and auth model.
A new component is a cost the team carries forever, so it needs a requirement
that the existing ones can't meet.

**Scope: architecture only, read-only.** Read with Read, Glob and Grep only. Never edit or create code, migrations, IaC or pipelines, and
never run builds, tests, package managers or anything that contacts an
environment. The output is a design the team builds from.

**No repository or project folder (e.g. Claude chat, Cowork).** If there is
no repository or writable project folder available (for example in Claude chat
or Cowork without a folder), do not try to write files: deliver every document
in the conversation as Markdown sections with the same headings, and say once
that files weren't written. Skip repo scanning and say the team profile is
self-reported.

**No codebase?** This skill needs an existing codebase to read. If there is
none, say so and offer the `design` workflow instead.

## 1. The feature
From `$ARGUMENTS` and the conversation: what the feature does, who uses it,
expected load and data, latency or availability needs, and constraints
(deadline, regulation, provider limits). Ask only what changes the design; if
the user can't answer, assume and list the assumptions.

## 2. The existing system (as-is), with evidence
Scan the repository as described in
`${CLAUDE_PLUGIN_ROOT}/skills/interview/references/repo-scan.md` (Glob calls in
one turn, then the manifests in the next).

Then read the code that matters for this feature in **one batch of parallel
Read calls** (about 10 files at most): the entry points, the module closest to
the feature, how it reaches the data store, how async work is done, and the
auth / tenancy middleware. Read only what the feature touches; don't survey
the whole repo, and don't read files one at a time.

Record the **patterns** as facts with `file:line` references:

| Concern | What the code does | Evidence |
|---|---|---|
| Structure | e.g. modules with routes → service → repository | `src/modules/jobs/service.ts:4` |
| Data | store, ORM, migration tool, tenancy filter | |
| Async work | queue / bus, how jobs are dispatched, retries, dead-letter | |
| Auth and tenancy | how identity and tenant are derived and enforced | |
| API style | REST / GraphQL / gRPC, validation, versioning | |
| Integrations | email, SMS, payments, third-party APIs | |
| Deployment | runtime, IaC, CI/CD, environments, regions | |
| Observability | logging, tracing, metrics | |

Only claim what you read. Mark anything inferred from names alone as
"(inferred)". If the scan finds little (no manifests, IaC or CI), say so
and ask the user how the system is built and run.

Use the scan's team-profile evidence as the sources of the team facts in
step 4.

**Gaps the feature depends on.** Note what the existing system lacks that the
feature relies on: no non-production environment, no backups for a store the
feature writes to, secrets in plain config, a single zone on a path the feature
makes critical. Don't adopt a gap as the design: name it, say what it risks
for this feature, and make closing it a precondition or a separate
recommendation. **Environment separation is always a requirement:** if there is
no non-production environment, the recommendation includes one as a
precondition for shipping the feature. Feature flags, allow-lists or dry-run
modes in production limit exposure; they don't replace a separate environment.

## 3. Options that fit first
- **A. Fits the existing patterns:** the feature built only from what the
  system already has (same store, same queue and worker, same module layout).
  Always present it, even if you don't recommend it.
- **B. Adds a component** (a new data store, queue, service, third-party
  provider) only when a requirement can't be met by A. Name the requirement.
- At most one more option if there is a real trade-off.

For each option: what changes, why, and trade-offs (fit with existing code,
new things to run, risk, time to deliver, rough monthly cost delta and its
drivers), and for every **new** component its product and a **Portability**
rating (Portable / Adaptable / Locked, plus what it would take to move). A new
third-party provider or managed service counts as a new component: check residency (use `data-residency` rules if the user's data must
stay in a region) and the org guardrails if there is a profile.

## 4. Team fit and guardrails
Apply the team-fit rules (step 4 of `design` if it is loaded; otherwise Read
`${CLAUDE_PLUGIN_ROOT}/skills/team-fit/references/scoring.md`)
with one option per design, listing the **existing components plus the new
ones**, so the verdict reflects the whole system the team will run after the
change. Show the team-fit block in its exact format. With an org profile or stated
platform rules, include guardrails as in `design`.

## 5. The design (to-be)
For the recommended option:
- **Change map:** each module, component or file area that changes, and how
  (new module / new handler / new table / new endpoint). Paths, not code.
- **Component mapping (to-be):** one table of every runtime component after the
  change, existing and new, with its product, whether it is new, and its
  **Portability** rating.
- **Data changes:** new tables or fields, indexes, the migration approach for
  live data (expand → backfill → contract when columns change), and tenancy
  on every new table.
- **API and event contracts:** new or changed endpoints and messages, and how
  existing clients keep working (additive change, versioning).
- **Rollout approach:** how the change reaches production safely as an
  architecture choice (feature flag, dark launch, per-tenant enablement), and
  what can be turned off without a deploy.
- **Quality attributes:** the feature's availability target with its error
  budget, and its latency or freshness need; whether the existing components
  already meet them (queue delay, provider rate limits, provider SLA); and how
  the target fits the team's on-call (with no on-call, a business-hours target
  or a stated precondition, as in `design`). Don't promise more than the
  existing system delivers.
- **Data protection:** for every new store or table, its backup and recovery
  (RPO, RTO, retention), whether it is personal data, and how long it is kept.
- **Risks:** what could break existing behaviour.

## 6. Deliverables
Write to `docs/architecture/<feature-slug>/` (ask if unclear), in one turn, or
give the same content in chat if the user wants no files:

| File | Contents |
|---|---|
| `README.md` | The feature, assumptions, as-is patterns table with evidence, gaps the feature depends on, options (new components with portability), recommendation and why, change map, data and contract changes, rollout approach, quality attributes and data protection, rough cost delta, risks |
| `diagrams.md` | Container view **as-is** and **to-be**, with new or changed parts marked, plus a sequence diagram of the feature's main flow |
| `adr/NNNN-*.md` | One ADR per significant decision (continue an existing `adr/` folder's numbering), each with a "because" tied to a requirement or an existing pattern, and fitness criteria |

Then check every Mermaid block against the self-check in the `diagram` skill
(`${CLAUDE_PLUGIN_ROOT}/skills/diagram/SKILL.md`, "Check before finishing") and fix
anything that fails.

**Fitness criteria** for a feature check that it follows the system's rules,
e.g. "Every new table has a `tenantId` column and every query on it filters by
it", "Notifications are sent only from the worker, never in the request path",
"No new data store".

State the rough cost delta once (in the options) and refer to it elsewhere,
so the figures can't disagree.

Before finishing, run the consistency check (step 6 of `design` if it is
loaded; otherwise Read `${CLAUDE_PLUGIN_ROOT}/skills/design/references/consistency.md`, section 5)
on the to-be design, with the recovery table covering every store the feature
adds or changes. Then check: every pattern claim has a file reference or
"(inferred)"; option A is present; every new component names the requirement
that needs it; the to-be mapping rates **every** runtime component, existing
ones included, for portability; the feature has an availability
target consistent with on-call and every new store has backup and recovery;
gaps the feature depends on are named, not adopted; every decision has a "because" and fitness criteria; nothing
was written outside `docs/architecture/`.
