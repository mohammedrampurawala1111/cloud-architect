---
name: adr
description: Write Architecture Decision Records (MADR format) for significant design choices, including options considered, team-fit and lock-in. Use when the user wants to document an architecture decision, record why a cloud, database or platform was chosen, or after the design skill picks an option.
---

# Architecture Decision Records

Write one ADR per **significant, hard-to-reverse** decision. Typical set for a
new system (3-8 total):
- Cloud provider (or self-hosted) choice
- Compute model (functions vs managed containers vs Kubernetes)
- Primary data store(s)
- Sync vs async integration / messaging choice
- Identity & authentication approach
- Monolith vs services split
- Region / availability strategy and DR tier
- **Exception ADRs:** one per component outside the org profile's guardrails
  (see `design` → Phase 4b)

Tooling (IaC, CI/CD, observability products) is the builders' decision; write
an ADR about it only when the architecture depends on it.

Don't write ADRs for trivial or easily reversed choices.

**No repository or project folder (e.g. Claude chat, Cowork).** If there is
no repository or writable project folder available (for example in Claude chat
or Cowork without a folder), do not try to write files: deliver every document
in the conversation as Markdown sections with the same headings, and say once
that files weren't written. Skip repo scanning and say the team profile is
self-reported.

## Files
- Path: `docs/architecture/<system-slug>/adr/NNNN-kebab-title.md`, numbered
  from `0001`. If an `adr/` folder already exists in the repo, continue its
  numbering and match its format instead.
- Also write `adr/README.md` with an index table: number, title, status, date.

## Template

```markdown
# NNNN. <Decision title in active voice, e.g. "Use managed containers for the API">

- **Status:** Proposed | Accepted | Superseded by NNNN
- **Date:** YYYY-MM-DD
- **Deciders:** <the decision-maker, e.g. CTO; filled in when they decide>

## Context
What problem, which requirements (link to the requirement summary items), which
team facts matter. 3-6 sentences.

## Decision drivers
- Requirement or constraint 1
- Team fit (complexity budget N/5, relevant skills)
- Cost / time-to-market / portability as relevant

## Options considered
1. **Option A** — one line
2. **Option B** — one line
3. **Option C** — one line

## Decision
We chose **Option X** because … (tie back to the drivers).

## Consequences
- ✅ Positive …
- ⚠️ Negative / risks …
- 🔒 Lock-in: Portable | Adaptable | Locked — what it would take to move.

## Fitness criteria
1-3 conditions anyone can check against the built system to see that it follows
this decision. Use numbers, names and places ("All data stores are managed
PostgreSQL 16 in eu-central-1 with point-in-time recovery", "No component
outside eu-central-1 and eu-west-1 except the CDN"); never "scalable",
"secure" or "robust". Say what must be true, not which tool checks it.

## Revisit when
Concrete triggers: "traffic > 2k RPS sustained", "team gains a platform
engineer", "multi-region becomes a requirement".
```

For an **exception ADR**, title it "Exception: <what> outside <guardrail>",
and in Context name the guardrail and the approved alternative; in Decision
drivers say why the alternative doesn't meet the requirement; in Consequences
state what supporting it adds (skills, upgrades, a second tool to run). `Deciders:` is the org
owner from the org profile, or the decision-maker.

## Rules
- Status is **Proposed** until the decision-maker (e.g. the CTO) has decided and
  the user tells you so; then follow `decision-brief` → "Recording the decision".
  Never mark an ADR Accepted on your own judgement.
- Keep each ADR to about one page.
- Use neutral capability names in the Context and Options, product names in the
  Decision.
