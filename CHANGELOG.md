# Changelog

All notable changes to the `cloud-architect` plugin. Versions follow
[Semantic Versioning](https://semver.org/).

## [1.1.0] — 2026-11-11

Instructions and reference data only, and measured end to end against plain
Claude.

### Changed
- **No scripts or programs.** The plugin directory accepts scripts only from
  Verified organizations, so team scoring, guardrail checks, the repository scan
  and the diagram check are now exact written procedures with fixed output
  formats. The plugin is 21 Markdown, JSON and image files.
- **Team fit by lookup.** The budget and verdicts come from lookup tables
  generated from the original scoring rules (all 48 budget rows match);
  components are counted as building blocks; a class list with example
  products keeps classification consistent.
- **Never recommend an At limit option** while a Within option meets the
  requirements; it's offered as a conditional alternative.
- **Design consistency check** (Standard and Full modes): recovery per failure
  scope with the mechanism behind each RPO/RTO and every stateful component,
  numbers stated once, capacity vs peak, cost vs sizing (including NAT or
  private endpoints), one component list, required building blocks.
- Compact rules live inside `design`, so a new-system design reads no extra
  files; `extend` reads the repository in parallel batches.
- **No credentials, MCP servers or network use.** Cost ranges come from the
  model's knowledge and are labelled as estimates; uncertain products are
  marked "(verify)".
- The `design` description is narrower and no longer asks to be loaded before
  every architecture question.
- Development tools and eval scenarios moved to the `dev` branch; `main` holds
  the plugin, examples and results.

### Added
- `PRIVACY.md`, and privacy policy, support and documentation URLs in
  `plugin.json`.
- README: troubleshooting section and results from a full comparison: senior
  SRE review 98% vs 35% for plain Claude, principal DevOps review 82% vs 14%,
  mean score 0.97 vs 0.65 over 20 scenarios (`evals/RESULTS.md`).

## [1.0.0] — 2026-11-10

First public release. Right-sized cloud architecture your team can actually
run, for new systems, features in an existing codebase, and migrations.
Architecture only: it reads code but never writes code, IaC or pipelines, and
never deploys.

- **New systems** (`design`): interview, team-fit budget from a script, 2-3
  provider-neutral options with a rough monthly cost range and its drivers,
  provider mapping with a portability rating per component, quality attributes
  consistent with the team's on-call, Mermaid diagrams, and ADRs with a
  "because" and fitness criteria. Quick / Standard / Full modes.
- **Features in an existing codebase** (`extend`): reads the repository
  read-only, records its patterns with file references, and designs the feature
  to fit them first.
- **Migrations** (`migrate`): strategy per workload, target architecture, and
  phases with coexistence, data migration method, cut-over, rollback, point of
  no return and exit criteria.
- **Data residency and controls** (`data-residency`): regions per data
  category, data-flow map, jurisdiction flags, regional and sovereign
  providers, control requirements. Not legal advice.
- **CTO decision brief** (`decision-brief`), **org guardrails** with exception
  ADRs, and supporting skills `interview`, `team-fit`, `capability-map`,
  `diagram`, `adr`.
- **No scripts or programs:** instructions and reference data only. Team
  scoring, guardrail checks, the repository scan and the diagram check are
  exact written procedures with fixed output formats.
- **Evidence:** eval suite of 20 scenarios against plain Claude; results in
  `evals/RESULTS.md`, scenarios and tooling on the `dev` branch.
