---
name: team-fit
description: Score a team's operational complexity budget (1-5) from size, skills, on-call and preference, and check architecture options against it. Use when choosing between architectures or judging whether a team can run Kubernetes or microservices.
---

# Team fit: operational complexity budget

Architecture fails more often because the team can't operate it than because the
technology was wrong. This skill turns the team profile into a budget and checks
each option against it. **The score is computed by a script, never in prose**, so
the same team always gets the same budget.

## 1. Run the scorer

Inside `design`, `plan.py` runs this scorer together with the guardrails check
in one call; use the steps below for standalone team-fit questions.

Put the team profile (the YAML the `interview` skill emits) and **all** options
into one document and pipe it to the script in a single call:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/team_score.py" - --format markdown <<'EOF'
team:
  operators: 2
  on_call: false
  platform_team: false
  skills:
    containers: 2
    kubernetes: 0
    iac: 1
  preference: managed
options:
  - name: A. Serverless
    components:
      - name: API
        class: serverless_functions
      - name: Primary DB
        class: managed_database
  - name: B. Managed containers
    components:
      - name: API
        class: managed_containers
      - name: Primary DB
        class: managed_database
EOF
```

**Input format rule:** write the heredoc as block-style YAML exactly like this:
quoted delimiter `<<'EOF'`, one `key: value` per line, no `{ }`, no `[ ]` and no
quote characters in the body. Claude Code's Bash safety check blocks heredocs
that mix braces and quotes (so JSON is blocked) and unquoted `<<EOF`
delimiters. If a command is blocked anyway, write the YAML to a file and pass
its path; don't retry variations.

- Use `--format json` when you need the breakdown or per-option detail.
- Component `class` names and weights: `references/component-classes.md`
  (or `--list-classes`). If nothing fits, pass `weight: N` and say why.
- Mark build-time-only components (CI/CD) with `runtime: false`.
- If Python or Bash is unavailable, apply the rules below by hand and say that
  you did.
- Copy the script's **budget, reasoning line and verdict table verbatim**. Never
  adjust its numbers; if you disagree, say why next to them.
- Report its "Assumptions" line: those inputs were missing from the profile.
- Report its "Evidence" line. When most factors are self-reported and the
  budget decides between options (an option is *At limit* or *Exceeds*), say
  that the verdict rests on self-reported skills and name the fact that would
  change it.

## 2. Rules the script implements

Start at **1** and add:

| Factor | Points |
|---|---|
| ≥ 2 people who will operate the system after launch | +1 |
| An on-call rotation exists (or will before launch) | +1 |
| Solid (2+) container **and** IaC experience | +1 |
| Solid (2+) Kubernetes experience **or** a platform/SRE team | +1 |
| Preference = `control` | +0.5 |
| Preference = `managed` | −0.5 |

Round half up, clamp to 1-5.

| Budget | What it can carry |
|---|---|
| 1 | Fully managed / serverless / PaaS only. Managed DB. No servers, no clusters. |
| 2 | Managed containers (Cloud Run, Container Apps, ECS on Fargate), managed DB/queue/cache, simple IaC. |
| 3 | Several services, event-driven pieces, a few self-managed components, full IaC + CI/CD, basic SLOs. |
| 4 | Managed Kubernetes with GitOps, multiple environments, autoscaling tuning, on-call with runbooks. |
| 5 | Multi-region, service mesh, self-hosted data stores, multi-cloud — with a dedicated platform team. |

Component weights: **1** serverless, PaaS, managed DB, object storage, managed
queue/auth, CDN · **2** managed containers, cache, API gateway with custom auth,
managed search, event bus · **3** managed Kubernetes, self-run brokers, stream
processing, multiple DB engines, hybrid networking · **4** service mesh,
self-hosted databases, multi-region active-active, own observability stack ·
**5** multi-cloud active-active, self-run control plane, on-prem federation.

An option's **complexity level** = its highest component weight, +1 if it has
more than 8 distinct runtime components.

## 3. Verdicts
- **Within** (level ≤ budget): fine.
- **At limit** (level = budget + 1): allowed only with a named mitigation —
  training, a managed alternative later, or a support contract.
- **Exceeds** (level ≥ budget + 2): reject, or keep only as the "if you grow
  into it" option and say what would have to change (hires, skills, on-call).

If the user insists on an option that exceeds the budget, don't silently comply:
state the verdict, the concrete operational risks (who patches, who is paged,
upgrade cadence), and the smallest change that would make it fit. If they still
want it, design it with those risks recorded in an ADR.

## 4. Prefer what the team knows
The script's `known_tools` lists skills rated solid or better and the
`strongest_cloud`. When two choices are otherwise close, pick the one matching
(the org profile's platform, when there is one, comes first; tooling itself is
the builders' choice, so these are inputs to the architecture, not
decisions about how to build it):
- Cloud with the highest skill score, unless constraints say otherwise.
- IaC tool already in use; else match the team's language (Pulumi/CDK for
  TypeScript/Python/Go/C# teams; Terraform/OpenTofu as the neutral default;
  Bicep for Azure-only .NET shops).
- CI/CD where the code already lives (GitHub Actions, GitLab CI, Azure DevOps,
  Bitbucket Pipelines, Jenkins).
- Observability tool already paid for; else the provider's native tooling or
  OpenTelemetry + a managed backend.
- Runtime languages the team already writes.

## 5. Output
The script's Markdown, then one line per *At limit* option naming its
mitigation, then the tool preferences from step 4:

```markdown
**Operational complexity budget: 2 / 5**
Reasoning: start 1; operators = 2 (+1); on_call = false (0); containers = 2 (solid), IaC = 1 (some) via terraform (0); kubernetes = 0 (none), platform_team = false (0); preference = managed (-0.5) → 1.5 → 2.

| Option | Complexity | Verdict |
|---|---|---|
| A. Serverless | 1 | Within |
| B. Managed containers | 2 | Within |
| C. Kubernetes + GitOps | 3 | At limit |

C needs Kubernetes training for both operators and an on-call rotation first.
```
