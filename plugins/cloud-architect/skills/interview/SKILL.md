---
name: interview
description: Adaptive requirements interview for architecture design. Reads the org profile and read-only repository evidence, asks about the service's behaviour, traffic, data, constraints, and the team's size, skills and on-call capacity, then produces a requirements summary. Use on its own when the user wants to capture requirements, or as phase 1 of the design skill.
---

# Architecture requirements interview

Goal: gather just enough to make good architecture decisions, in **about 10
questions**, without exhausting the user.

## Before asking: read what already exists
Read-only, and only with Read, Glob and Grep. Never run cloud CLIs or anything
that contacts an environment.

1. **Org profile.** If `.cloud-architect/org.yaml` exists, read it: approved
   clouds, regions, services, forbidden component classes, the platform (landing
   zone, IaC, CI/CD, observability, golden paths) and policies. Don't ask what it
   answers; list it under **Constraints** as "from the org profile". If it
   doesn't exist and the user mentions a platform team or company standards,
   offer once to write one from their answers (format: `scripts/samples/org.yaml`).
2. **Repository evidence.** If you're in a code repository, run
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/inventory.py" .` once: it lists the
   stack and ends with a "Team-profile evidence" line to use as `team.evidence`.
   Look further only for what it can't see (runbooks, on-call docs). What
   counts as evidence:

   | Look for | Evidence of |
   |---|---|
   | `*.tf`, `*.tofu`, Pulumi, `*.bicep`, CDK, CloudFormation | IaC skill and tool |
   | `Dockerfile`, `compose.yaml` | Containers |
   | Helm `Chart.yaml`, Kubernetes manifests, Kustomize, Argo CD / Flux | Kubernetes |
   | `.github/workflows/`, `.gitlab-ci.yml`, `azure-pipelines.yml`, `Jenkinsfile` | CI/CD tool |
   | Provider SDKs or config in code (`boto3`, `@aws-sdk`, `azure-*`, `google-cloud-*`) | Cloud familiarity |
   | Runbooks, PagerDuty / Opsgenie mentions, `CODEOWNERS`, on-call docs | On-call, platform team |

   Count, don't guess: "14 Helm charts in `deploy/`" is evidence; "they probably
   use Kubernetes" is not. Show what you found and let the user correct it.
   Evidence suggests a level; the user's answer sets it. If nothing is found,
   everything stays self-reported; say so.

## How to ask
- Ask in **small batches of 2-4 questions**, grouped by topic. If a
  multiple-choice question tool (AskUserQuestion) is available, use it with
  concrete options plus "not sure"; otherwise ask in plain text.
- Offer sensible defaults: "If you're not sure, I'll assume ~50 requests/sec at
  peak."
- **Skip** anything already answered or implied. **Only follow up** when the
  answer would change the design (e.g. "real-time" → ask latency target;
  "health data" → ask jurisdiction).
- Accept "don't know" and record it as an assumption.
- Never ask for secrets, credentials or account IDs.

## Question bank (pick, don't recite)

### 1. The service (always)
- What does it do, in one or two sentences? Who uses it (internal staff, public
  consumers, other systems)?
- Main interaction style: web/mobile app, public API, background processing,
  data pipeline, real-time (chat, streaming, live updates), ML inference?
- Key user journeys or operations — the 2-3 that matter most.

### 2. Load & behaviour
- Expected users / requests at launch and in 12 months? Traffic shape: steady,
  business hours, spiky (campaigns, events), batch windows?
- Latency expectations for the critical path (e.g. p95 < 300 ms)?
- Long-running work? (jobs > 30 s, scheduled tasks, file processing)
- Read-heavy or write-heavy?

### 3. Data
- What data is stored: relational records, documents, files/media, time series,
  events, search, vectors?
- Rough volume now and growth; retention requirements.
- Consistency: must every read see the latest write (payments, inventory) or is
  eventual consistency fine?
- Personal or sensitive data? (PII, health, payment card)

### 4. Reliability
- What happens if it's down for an hour? (annoyance / lost revenue / safety)
  → maps to availability target (99.5 / 99.9 / 99.95+).
- How much data can you afford to lose (RPO) and how fast must you recover (RTO)?
- Single region OK, or users spread globally / regulatory need for multiple regions?

### 5. Integrations
- External systems: payment providers, identity providers (SSO), email/SMS,
  third-party APIs, on-prem systems, existing databases.
- Authentication for end users: social login, enterprise SSO, own accounts?

### 6. Constraints
- Monthly budget range for infrastructure (rough is fine).
- **Regions and residency (always ask once):** "Which countries or regions are
  your users in, and where must data be stored and processed?" Accept any
  answer (a country, a bloc such as EU/EEA, several regions, *no constraint*,
  *not sure*). If data must stay somewhere, follow up: "Is a global cloud
  provider's local region acceptable, or must the provider itself be based
  there?"
- **Regulations and frameworks: don't ask the user to name them.** Infer them
  from what you already know (user regions, sector, data types such as health
  or card data, customer type such as government, enterprise or consumers) with
  the table in `data-residency/references/regulations.md` → "Inferring what
  applies". Show the list in the requirements summary as **"Likely applicable
  (inferred)"**, one line each with the reason, and let the user confirm or
  correct it. Ask only about a gap that changes the design (e.g. "Will you sell
  to US federal agencies?", "Do you store card numbers or use a hosted payment
  page?"). If any residency rule or framework applies, use the `data-residency`
  skill.
- Existing cloud accounts, credits, enterprise agreements, or a mandated
  provider? Tools already in use (CI, monitoring, IaC)?
- Deadline for first production release?

### 7. Team (always — this drives the design)
- How many engineers will build it, and how many will operate it after launch?
- Experience level with: each cloud (AWS/Azure/GCP), containers, Kubernetes,
  IaC (Terraform/OpenTofu, Pulumi, Bicep, CDK, CloudFormation), CI/CD,
  observability tooling, databases. A 0-3 scale is fine: none / some / solid /
  expert.
- Main programming languages and frameworks.
- Is there an on-call rotation or a platform/SRE team? Who gets paged at 3am?
- Preference: "we want to run as little infrastructure as possible" vs "we want
  control and portability".

## Output
Produce the **Requirements Summary** using the template in the `design` skill,
including an explicit "Assumptions I made" list. Ask the user to confirm or
correct it. Also emit a compact team profile for the `team-fit` skill:

```yaml
team:
  builders: 4
  operators: 2
  on_call: false
  platform_team: false
  skills:            # 0 none, 1 some, 2 solid, 3 expert
    aws: 1
    azure: 0
    gcp: 2
    containers: 2
    kubernetes: 0
    iac: { terraform: 1 }
    ci_cd: { github_actions: 2 }
    observability: 1
  languages: [typescript, python]
  preference: managed   # managed | balanced | control
  evidence:            # only facts backed by the repo or org profile; omit the rest
    containers: 6 Dockerfiles in services/
    iac: 23 Terraform files in infra/
    on_call: on-call rota in docs/runbooks/README.md
constraints:
  user_regions: [eu, us]      # where users are
  data_residency: [eu]        # where data must stay; [] = no constraint
  residency_level: R1         # R1 in-region | R2 sovereign controls | R3 local providers only
  regulations: [gdpr, ccpa]   # e.g. gdpr, uk_gdpr, hipaa, lgpd, dpdp, pipl
  frameworks: [iso27001, soc2] # e.g. pci_dss, nis2, dora, fedramp
```

Pass the `team:` block unchanged to `scripts/plan.py` (in `design`) or
`scripts/team_score.py` (standalone `team-fit`).
`evidence` keys are `operators`, `on_call`, `platform_team`, `containers`,
`iac`, `kubernetes` and `preference`; write each value as plain text without
quotes, braces or colons.
