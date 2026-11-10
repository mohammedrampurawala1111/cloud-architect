# cloud-architect scripts

Small, deterministic helpers the skills call so that team scores, guardrail
checks and diagram checks don't depend on the model's judgement on the day. All scripts:

- use the **Python 3 standard library only** (3.8+), no third-party packages;
- make **no network calls**, read only the files you pass (or, for
  `inventory.py`, the repository folder you point it at), and write only to
  stdout;
- have `--help`, exit `0` on success and `2` on invalid input;
- accept JSON or a small YAML subset (block maps and lists, inline `{}`/`[]`,
  comments, plain scalars; no `|`/`>` blocks or anchors; use JSON for anything else).

Skills call them as `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/<name>.py"`. When
Claude passes input on stdin it uses block-style YAML in a quoted heredoc
(`<<'EOF'`, no braces, brackets or quotes in the body): Claude Code's Bash
safety check blocks heredocs that mix braces and quotes, which rules out JSON.
JSON files passed by path work normally.

| Script | Purpose | Sample |
|---|---|---|
| `plan.py` | **One call** for team fit + guardrails (what the skills use) | `samples/plan.yaml` (+ `samples/org.yaml`) |
| `team_score.py` | Operational complexity budget (1-5) + option verdicts | `samples/team.yaml` |
| `guardrails.py` | Options vs the org profile: components needing an exception ADR | `samples/org.yaml`, `samples/guardrail_options.yaml` |
| `inventory.py` | Read-only inventory of an existing codebase (stack, data, messaging, IaC, CI/CD) + team-profile evidence | any repo |
| `check_mermaid.py` | Basic syntax checks for ```mermaid blocks in Markdown | `samples/diagrams.md` |

Run the tests from this folder: `python3 -m unittest discover -s tests`.

## plan.py

Runs `team_score.py` and (when there is an org profile) `guardrails.py` on one
document and prints their Markdown in that order, so a design needs one tool
call instead of two. Same rules, same output.

```bash
python3 plan.py samples/plan.yaml --org samples/org.yaml   # or an inline org: block
python3 plan.py - <<'EOF'
team:
  ...
options:
  ...
EOF
```

Keys: `team` (as for `team_score.py`), `options` (components need `class` or
`weight`; `product` and `provider`/`region` per option or component when
guardrails apply), optional `org`. Other keys are ignored. Errors name the step
that failed (`team fit:`, `guardrails:`). Exit 0 ok, 2 invalid input.

## team_score.py

```bash
python3 team_score.py samples/team.yaml --format markdown
python3 team_score.py profile.json --options options.json
python3 team_score.py --list-classes
```

Input: the interview's team profile, with or without a top-level `team:` key.

| Field | Type | Missing → |
|---|---|---|
| `team.operators` | number of people operating it after launch | `builders`, else 1 |
| `team.on_call` | bool | false |
| `team.platform_team` | bool | false |
| `team.skills.containers` / `.kubernetes` | 0-3 | 0 |
| `team.skills.iac` | 0-3, or `{tool: 0-3}` (best tool counts) | 0 |
| `team.preference` | `managed` \| `balanced` \| `control` | balanced |
| `team.evidence` | `{field: source text}` for `operators`, `on_call`, `platform_team`, `containers`, `iac`, `kubernetes`, `preference` | every factor self-reported |
| `options[].name` | string | "Option N" |
| `options[].components[]` | `{name, class}` or `{name, weight: 1-5}`; `runtime: false` excludes it from the >8 count | — |
| `options[].complexity` | integer, instead of `components` | — |

Every assumed value is listed in `warnings` (JSON) or "Assumptions" (Markdown).
Evidence never changes the score; Markdown adds an "Evidence:" line saying how
many factors are backed by evidence and which are self-reported.

Output (JSON): `budget`, `raw_score`, `breakdown[]` (factor, points, applied,
evidence, `source`: the `team.evidence` text or "self-reported"), `known_tools` (skills rated ≥ 2, strongest cloud), `options[]`
(`complexity`, `verdict`: `within` | `at_limit` | `exceeds`, `basis`), `warnings`.

The rules are those in `skills/team-fit/SKILL.md`: start 1; +1 for ≥ 2
operators; +1 on-call; +1 solid containers and IaC; +1 solid Kubernetes or a
platform team; ±0.5 for control/managed; round half up; clamp 1-5. Option level =
highest component weight, +1 for more than 8 runtime components.

## guardrails.py

```bash
python3 guardrails.py samples/org.yaml --options samples/guardrail_options.yaml
python3 guardrails.py .cloud-architect/org.yaml --options - --format json   # options on stdin
```

Input: the org profile (`org:` with any of `clouds`, `regions`,
`approved_services`, `approved_classes`, `forbidden_classes`, plus free-form
`name`, `platform` and `policies`), and `options[]` with `components[]`
(`name`, `product`, `class`, optional `provider`, `region`, `global: true` for
edge services with no region). `provider` and `region` can be set per option and
overridden per component. Names match case-insensitively, ignoring `-` and `_`.

A component needs an exception when its cloud or region isn't approved (or not
given), its class is forbidden, or neither its product nor its class is on an
approved list. Output: a verdict per option (fits guardrails / needs N exception
ADRs) and one row per finding. Exceptions are reported, not errors: exit `0`;
`2` for invalid input.

## inventory.py

```bash
python3 inventory.py .                    # Markdown summary of the repo
python3 inventory.py path/to/repo --format json
```

Walks the folder (skipping `.git`, `node_modules`, `vendor`, virtualenvs, build
output, `.terraform` and other dependency or cache folders), opens text files up
to 256 KiB, and reports, each with the files that show it:

- languages and likely entry points;
- declared dependencies by role: web framework, data stores, ORM / migrations,
  cache, messaging and jobs, object storage, cloud SDKs, auth, third-party
  integrations (email, SMS, payments), observability, testing. Manifests read:
  `package.json`, `requirements*.txt`, `pyproject.toml`, `go.mod`, `pom.xml`,
  `build.gradle(.kts)`, `*.csproj`, `Gemfile`, `composer.json`, `Cargo.toml`,
  and Prisma schemas;
- API contracts (OpenAPI, protobuf, GraphQL), database migration folders;
- Dockerfiles and base images, compose files, Kubernetes manifests by kind,
  Helm charts, Kustomize, Terraform resource types, other IaC, CI/CD files.

It ends with "Team-profile evidence" lines in the plain-text form `team.evidence`
expects. Detection is by file names and declared dependencies only; the skills
read the code to confirm how each part is used. Exit `0`, or `2` if the folder
doesn't exist or has more than `--max-files` files.
