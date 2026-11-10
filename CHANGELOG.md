# Changelog

All notable changes to the `cloud-architect` plugin. Versions follow
[Semantic Versioning](https://semver.org/).

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
