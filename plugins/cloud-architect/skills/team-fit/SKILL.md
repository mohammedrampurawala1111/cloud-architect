---
name: team-fit
description: Score a team's operational complexity budget (1-5) from size, skills, on-call and preference, and check architecture options against it. Use when choosing between architectures or judging whether a team can run Kubernetes or microservices.
---

# Team fit: operational complexity budget

Architecture fails more often because the team can't operate it than because the
technology was wrong. This skill turns the team profile into a budget and checks
each option against it. **The score follows fixed rules, worked step by step**, so the same team always
gets the same budget.

## 1. Score the team and the options

Read `references/scoring.md` and apply it exactly: collect the six team facts
with their sources (repository evidence or self-reported), compute the budget,
give every component of **all** options a class and weight, and work out each
option's complexity and verdict. Output the block in the exact format shown
there. Never adjust a result; if you disagree, say why next to it. Report the
Assumptions line (facts that were missing) and the Evidence line. When most
factors are self-reported and an option is *At limit* or *Exceeds*, say the
verdict rests on self-reported skills and name the fact that would change it.

## 2. The rules in brief

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

Recommend a Within option whenever one meets the requirements; At limit only
when none does (see "Recommending" in `references/scoring.md`).

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
Note the skills the team rates solid (2) or better and its strongest cloud.
When two choices are otherwise close, pick the one matching
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
The block from the scoring rules, then one line per *At limit* option naming its
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
