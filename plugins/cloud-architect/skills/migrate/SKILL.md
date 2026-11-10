---
name: migrate
description: Design the migration of an existing system to the cloud or to a new platform - current state (from the codebase when available, read-only), target architecture, strategy per workload, phases with exit criteria, data migration method per store, cut-over and rollback approach with the point of no return, and how old and new coexist. Use when the user wants to move, re-platform, modernise or replace a legacy or on-premises system.
argument-hint: "[the system to migrate]"
---

# Migration architecture

A migration design answers two questions: **where are we going** (the target
architecture) and **how do we get there without stopping the business** (the
path). The path is architecture, not project management: the order of moves,
how data moves, how traffic switches, and how each step can be undone are
design decisions with trade-offs. Leave staffing, dates and task plans to the
user.

**Scope: architecture only, read-only.** If there is code, read it with Read,
Glob, Grep and the inventory script; never edit it, never run builds, cloud
CLIs or migration tools. No IaC, pipelines or scripts.

## 1. Current state
- **From the codebase** (when the repo is available): run
  `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/inventory.py" .` once, then read the
  entry points and data access to confirm. Record what you read with `file:line`
  references.
- **From the user** (always): what runs where (servers, VMs, databases with
  engine, version and size), batch jobs and their windows, file transfers and
  partner interfaces, integrations, current availability and the downtime the
  business can accept, licences that constrain choices, the deadline, and the
  team (skills, on-call). Ask in small batches; assume and list what they can't
  answer.

Produce a **workload table**: workload, technology, size, dependencies
(inbound and outbound), how critical, and what's hard to move (licensing,
stateful sessions, hard-coded IPs, shared file systems, tightly coupled batch).

## 2. Strategy per workload
For each workload choose one, with a "because" from the facts above:

| Strategy | Meaning | Typical when |
|---|---|---|
| **Retain** | Leave where it is for now | Not worth moving yet, or blocked |
| **Retire** | Switch it off | Nobody needs it |
| **Rehost** | Same software on cloud VMs | Deadline first, little change capacity |
| **Replatform** | Same code, managed runtime or database | Quick wins with low change, e.g. a managed database |
| **Repurchase** | Replace with SaaS | Commodity function |
| **Refactor** | Change the code to fit the target architecture | A requirement the current design can't meet |

Prefer the least change that meets the requirements and the deadline. Refactor
belongs after the move unless a requirement forces it earlier; say so when you
defer it.

## 3. Target architecture
Design the end state with the `design` skill's rules: neutral capabilities
first, mapping with portability, team fit, residency, guardrails. Run `plan.py`
once (input format in `design`, step 4) with **the target and every
intermediate state** as separate options, because a team often has to run old
and new side by side, which can exceed its budget even when the target fits.
Paste the team-fit block verbatim.

## 4. The path
Order the moves into **phases** (usually 2-5). For each phase:
- **What moves** and what stays.
- **Coexistence:** how old and new talk to each other meanwhile (hybrid
  network, shared identity, interim integration, which side is the source of
  truth for each data set).
- **Data migration method** for each data store, with its downtime:
  - one-off dump and restore (simple; downtime grows with size),
  - replication or change data capture into the target, then switch (short
    downtime; needs a supported tool for the engine pair),
  - dual write (avoid unless nothing else works: hard to keep consistent).
  Name the engine pair and say what to verify (tool support, data types,
  stored procedures, character sets, size vs the downtime window).
- **Cut-over approach:** big bang, per workload, per tenant or partner, or
  gradual traffic shift; how clients and partners are switched (DNS, endpoint
  config, keeping hostnames, credentials and IP allow-lists for partners).
- **Rollback approach:** how to go back if the cut-over fails, how data written
  after the switch gets back to the old side (reverse replication, replay, or
  accept loss), and the **point of no return**: the step after which rollback
  is no longer possible, and what must be true before taking it.
- **Exit criteria:** the measurable conditions to finish the phase (e.g. "7
  days on the new database with p95 within 10% of the old, zero
  reconciliation differences").

Keep the old system recoverable until the point of no return of each phase.
Never plan a phase whose downtime exceeds what the business accepted without
saying so.

## 5. Risks
The top risks of the path (data loss or drift, partner disruption, performance
regression, licensing, running two systems at once), each with the design
mitigation.

## 6. Deliverables
Write to `docs/architecture/<system-slug>/` (ask if unclear) in one turn, or
give the same content in chat if the user wants no files:

| File | Contents |
|---|---|
| `README.md` | Current state summary, assumptions, workload table, strategy per workload, target summary, recommendation and why, risks |
| `migration.md` | The phases (what moves, coexistence, data method, cut-over, rollback, point of no return, exit criteria), the downtime per phase vs what was accepted |
| `options.md`, `adr/` | The target architecture's options, mapping with portability, and ADRs, as in `design` |
| `diagrams.md` | Current state, each intermediate state, and the target (container views), plus the data migration flow |

Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/check_mermaid.py"` on the files
once and fix errors.

ADRs for a migration include the strategy for each critical workload, the data
migration method for each critical store, and the cut-over approach. Their
**fitness criteria** check the result, e.g. "Zero row-count and checksum
differences between source and target before the switch", "Partners keep the
same SFTP hostname and credentials".

Before finishing, check: every workload has a strategy and a "because"; every
data store has a migration method and its downtime; every phase has a rollback
approach, a point of no return and exit criteria; the team-fit verdict covers
the intermediate states.
