# cloud-architect

**Right-sized architecture your team can actually run — in the regions and under the rules you need.**

A Claude plugin that does one job: produce architecture, with its reasoning,
for a new system, a new feature in an existing codebase, or a migration. It
interviews you about what you're building and who will run it, reads your org's guardrails and what the repo shows about your team,
scores how much operational complexity the team can carry, proposes 2-3
provider-neutral options, maps the chosen one to AWS, Azure, GCP, Kubernetes or
regional providers, and writes the architecture documents.

**Architecture only.** It decides *what* and *why*. How you build, run, staff
and budget it is yours: the plugin never writes IaC or pipelines, never deploys
anything, doesn't plan your team's work, and gives cost only as a rough range
per option so you can compare them.

## Why not just ask Claude?

Plain Claude gives good architecture advice. What it usually leaves out is what
makes a design survivable for a small team and buildable by someone else:

- **Team fit computed, not guessed.** A script scores the team's operational
  complexity budget from size, on-call and skills (backed by repo evidence where
  there is some) and rejects options the team can't run, Kubernetes included.
- **Fits the platform you already have.** An org profile lists approved clouds,
  regions and services; every component outside it gets an exception ADR
  instead of slipping through.
- **Checkable decisions.** Every ADR has a "because" and fitness criteria:
  concrete conditions anyone can check against the built system.
- **Residency done properly.** Regions per data category, a data-flow map,
  foreign-jurisdiction flags and control requirements for the laws in scope.

Measured against plain Claude with the same prompts, Sonnet as the model and a
blind Opus judge, 3 runs per scenario: 18 new-system design scenarios, and one
scenario each for a migration and a feature in an existing repo. [`evals/RESULTS.md`](https://github.com/mohammedrampurawala1111/cloud-architect/blob/main/evals/RESULTS.md) has the method and caveats.

| | With cloud-architect | Plain Claude |
|---|---|---|
| Senior SRE production-readiness review | **48 / 54** | 22 / 54 |
| Principal DevOps architect design review | **34 / 54** | 8 / 54 |
| Every decision has a "because" | **51 / 54** | 39 / 54 |
| Holds Kubernetes pushback when the CTO asks for EKS | **3 / 3** | 0 / 3 |
| Residency data-flow map (regulated cases) | **12 / 12** | 2 / 12 |
| Legacy migration (`migrate`) | **1.00** | 0.81 |
| Feature in an existing repo (`extend`) | **0.98** | 0.60 |
| Cost per design (Sonnet, chat answer) | USD 0.22 | USD 0.15 |

Senior reviewers approve its designs about twice as often. The strictest
review still sends back 20 of 54 new-system designs, mostly for capacity
figures that don't add up or recovery that misses a stateful component.

## Install

From the Claude plugin directory once it's listed, or from GitHub in Claude Code:

```bash
/plugin marketplace add mohammedrampurawala1111/cloud-architect
/plugin install cloud-architect@cloud-architect-marketplace
```

Try it without installing, from a clone of the repository:

```bash
claude --plugin-dir ./plugins/cloud-architect
```

**Where it works:** built and tested in Claude Code (CLI, desktop and IDE
extensions). Its scripts need Python 3.8+ (standard library only), and Claude
Code asks before running them. Where Python can't run, the skills apply the
same rules by hand and say so; other surfaces haven't been tested yet.

## How to use

Just ask in Claude Code, or start a skill directly with its command. The
plugin picks the workflow, asks what it needs, and writes the design.

| You want | Say, for example | You get |
|---|---|---|
| Architecture for a new system | "Help me architect a booking API for 200 clinics. We're 4 Python developers, no on-call." or `/cloud-architect:design booking API` | `docs/architecture/<system>/`: `README.md`, `options.md`, `diagrams.md`, `adr/` |
| A quick sketch | "quick: architecture for a URL shortener" | One recommendation and one alternative, in chat |
| A plan your CTO decides on | "…and my CTO makes the final call" | Also `decision-brief.md`, a one-page brief with a sign-off block |
| A regulated or region-bound system | Name the countries or the rules: "customers in Germany, health data", "PCI DSS" | Also `controls.md`: regions per data category, data-flow map, control requirements |
| A feature in your existing code | Open the repo, then "Design how to add SMS notifications to this codebase" or `/cloud-architect:extend SMS notifications` | `docs/architecture/<feature>/`: as-is and to-be, what changes where, ADRs |
| A migration | "Design the migration of our on-prem Java app and Oracle database to AWS" or `/cloud-architect:migrate` | Also `migration.md`: phases, data method, cut-over, rollback |
| To record the decision | "The CTO chose B, on condition we hire a platform engineer by Q3" | The brief is ticked, ADRs become Accepted, conditions become fitness criteria |
| Just the team check | `/cloud-architect:team-fit` | Your team's complexity budget and a verdict per option |

**What happens after you ask**

1. **Questions.** About 10 in small batches: what it does, load, data,
   regions, and your team (size, skills, on-call). Say "don't ask, assume" to
   skip them; the assumptions are listed in the answer.
2. **Mode.** It says which one it uses: *Quick*, *Standard* (the default), or
   *Full* when residency rules or a decision-maker are involved.
3. **Checks.** It runs a local script for the team score (and org guardrails if
   you have a profile). Claude Code asks before running it.
4. **The design.** Options with trade-offs and a rough cost range, a
   recommendation, the mapping to products with portability, diagrams and
   ADRs. It asks where to write the files (default
   `docs/architecture/<name>/`) and changes nothing else in your repo.

**Tips**

- **Describe your team.** Size, skills on a 0-3 scale (none / some / solid /
  expert) and whether anyone is on call. The recommendation depends on it.
- **Want it in chat only?** Say "don't write any files".
- **Have platform rules?** Add `.cloud-architect/org.yaml` (below), or state
  them in the request ("AWS only, eu-west-1, no self-hosted databases").
- **Want to change something?** Ask: "use Azure instead", "drop option C",
  "make it EU-only". It updates the design and the ADRs.

## Features

| Feature | What it does |
|---|---|
| Team-aware budget | `team_score.py` scores the team's operational complexity budget (1-5) and checks each option: within / at limit / exceeds. Each factor shows its evidence (e.g. "12 Helm charts in `deploy/`") or is marked self-reported. |
| Kubernetes pushback | Options above the budget are rejected or flagged with what would have to change (hires, skills, on-call). |
| Org guardrails | `guardrails.py` checks every option against `.cloud-architect/org.yaml` (approved clouds, regions, services, forbidden component classes). Each exception needs an exception ADR signed off by the org owner. |
| Capabilities first | Designs in neutral building blocks, then maps them to products with a portability rating per component. |
| Quality attributes | Availability and latency targets with error budgets, RPO/RTO and the recovery approach they imply, scaling limits, all consistent with the team's on-call. Properties of the design, not an operating plan. |
| Rough cost | A monthly range per option with its main cost drivers, enough to compare options. No cost tables; detailed costing is yours. |
| Data residency and controls | For any target region: regions pinned per data category, a data-flow map, foreign-jurisdiction flags, regional and sovereign providers, and laws and frameworks (GDPR, HIPAA, PCI DSS, ISO 27001, SOC 2, NIS2, DORA, …) turned into numbered control requirements. Not legal advice, and not evidence of compliance. |
| Validated diagrams | Mermaid C4 context, container and deployment views and sequence diagrams, linted by `check_mermaid.py`. |
| Feature design in an existing codebase | `extend` reads the repo (read-only) with `inventory.py`, records its patterns with `file:line` evidence, and designs the feature to fit them first, adding a component only when a requirement needs one. As-is and to-be views, change map, data and API changes, rollout approach, ADRs. |
| Migration design | `migrate`: workload table, strategy per workload (retain, retire, rehost, replatform, repurchase, refactor), target architecture, and phases with coexistence, data migration method, cut-over, rollback, point of no return and exit criteria. |
| CTO decision brief | One page written as the principal architect's recommendation: options at a glance with cost, team fit and guardrail exceptions, what approving commits you to, top risks and a sign-off block. The CTO decides; the plugin then records the decision in the brief and ADRs. |
| ADRs | MADR records for the hard-to-reverse decisions, each with a "because" and fitness criteria, Proposed until the decision-maker signs off. |

Three modes keep simple requests cheap: **Quick** (one recommendation, no
extra skills), **Standard** (the default: options, mapping, diagrams, ADRs,
rough cost) and **Full**, which adds data residency or the decision brief only
when the request calls for them.

Output goes to `docs/architecture/<system>/`: `README.md`, `options.md`,
`diagrams.md`, `adr/`, and when needed `decision-brief.md`, `controls.md` and,
for migrations, `migration.md`. A feature design goes to
`docs/architecture/<feature>/`.

### Skills

| Skill | Command | Purpose |
|---|---|---|
| design | `/cloud-architect:design [what you're building]` | Full workflow; also starts on "help me architect X" |
| extend | `/cloud-architect:extend [the feature]` | Design a feature that fits an existing codebase |
| migrate | `/cloud-architect:migrate [the system]` | Migration architecture: phases, data, cut-over, rollback |
| interview | `/cloud-architect:interview` | Requirements, org profile, repo evidence and team profile |
| team-fit | `/cloud-architect:team-fit` | Budget and option verdicts |
| decision-brief | `/cloud-architect:decision-brief` | One-page brief for the CTO; records the decision afterwards |
| data-residency | `/cloud-architect:data-residency` | Residency, sovereignty and control requirements for any region |
| capability-map | `/cloud-architect:capability-map` | Neutral blocks ↔ AWS / Azure / GCP / Kubernetes / regional providers |
| diagram | `/cloud-architect:diagram` | Mermaid diagrams, validated |
| adr | `/cloud-architect:adr` | Architecture Decision Records, including exception ADRs |

It adds an estimated 1,100 tokens to each session (skill descriptions).

## Org profile (optional)

Put your platform's guardrails in `.cloud-architect/org.yaml` in your repo
and every design stays inside them:

```yaml
org:
  name: Acme
  clouds: [aws]
  regions: [eu-central-1, eu-west-1]
  approved_services: [ECS on Fargate, Lambda, RDS for PostgreSQL, SQS, S3, CloudFront]
  forbidden_classes: [self_hosted_database]
  platform:
    landing_zone: AWS Control Tower, one account per environment
    iac: terraform
    ci_cd: github_actions
    observability: datadog
```

Full example: [`scripts/samples/org.yaml`](scripts/samples/org.yaml). Without a
profile the plugin designs freely and says so.

## Examples

Complete runs of this release, each the `docs/architecture/<system>/` folder it
wrote, unedited. The prompts are eval scenarios 01, 02, 05 and 06, with a CTO
making the final decision:

| Example | Scenario |
|---|---|
| [startup-saas](https://github.com/mohammedrampurawala1111/cloud-architect/tree/main/examples/startup-saas/) | 3-person TypeScript team, B2B scheduling SaaS |
| [eu-fintech-payments](https://github.com/mohammedrampurawala1111/cloud-architect/tree/main/examples/eu-fintech-payments/) | German payments platform under DORA, EU-only |
| [iot-telemetry-pipeline](https://github.com/mohammedrampurawala1111/cloud-architect/tree/main/examples/iot-telemetry-pipeline/) | 20k devices, real-time alerting, 13-month history |
| [ml-inference-api](https://github.com/mohammedrampurawala1111/cloud-architect/tree/main/examples/ml-inference-api/) | Fine-tuned 8B model behind a public API |

## What it reads and runs

- **Reads**, with Claude Code's Read, Glob and Grep tools only:
  `.cloud-architect/org.yaml`, and file names and contents in your repository,
  to find the tools your team uses (IaC, containers, Kubernetes, CI/CD,
  runbooks) and, for `extend` and `migrate`, how the existing code is built.
- **Runs** local Python scripts that read their input and print a result:
  `plan.py` (team fit and guardrails in one call, built on `team_score.py`
  and `guardrails.py`), `inventory.py` (a read-only scan that opens only your repository's
  dependency manifests, Dockerfiles, Kubernetes, IaC and CI files) and
  `check_mermaid.py`.
  Standard library only.
- **Writes** Markdown files only, under `docs/architecture/<name>/` (a system,
  feature or migration), and only where you agree.
- **Uses your MCP servers if you have them** (optional, read-only lookups):
  a connected pricing server makes the rough cost ranges use real prices, and a docs
  or Terraform registry server confirms services exist in your region. The
  plugin bundles none and works fully without them.
- **Never** bundles MCP servers, hooks or telemetry, makes network calls of its
  own, runs cloud CLIs, or writes code, IaC or pipeline files. No `plan`,
  `apply` or deploy.

## Limitations

- Designs new systems, features in existing codebases, and migrations.
  Auditing an existing estate, checking an implementation against the design,
  and planning the build or the team's operations are out of scope.
- `inventory.py` detects by file names and declared dependencies; the skills
  read the code to confirm, but unusual stacks may be missed.
- Output is a design for human review, not a production sign-off.
- Team skills are self-reported unless the repository shows evidence; the
  budget is only as good as its inputs.
- Cost ranges are rough estimates for comparing options, from memory unless a
  pricing tool is connected; verify with each provider's pricing calculator.
  Product names and regional availability change too. The provider map was
  last reviewed on 9 November 2026; items it could not confirm are marked
  "(verify)".
- Residency and controls mode is an engineering assessment, not legal advice,
  and its control requirements are not evidence of compliance.

## Development

From a clone of the [repository](https://github.com/mohammedrampurawala1111/cloud-architect):

```bash
cd plugins/cloud-architect/scripts && python3 -m unittest discover -s tests
claude plugin validate . && claude plugin validate ./plugins/cloud-architect
python3 tools/gen_evals.py . && python3 tools/eval_harness.py plugins/cloud-architect --runs 3 --max-cost 120
```

See [CHANGELOG.md](https://github.com/mohammedrampurawala1111/cloud-architect/blob/main/CHANGELOG.md).

## Licence

MIT, see [LICENSE](LICENSE).
