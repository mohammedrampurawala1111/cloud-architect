# Eval results — cloud-architect 1.0.0

> **Measured on a build with local scripts.** In these runs, Python scripts did
> the team scoring, guardrail checks, repository scan and diagram lint. 1.0.0
> ships without scripts (the plugin directory accepts them only from Verified
> organizations) and applies the same rules as written procedures. It hasn't
> been re-measured yet.

Run on 10 November 2026: **plugin arm vs no-plugin baseline**, 19 scenarios,
3 runs per arm per scenario (114 runs), same prompts and tools, blind LLM judge.
The main run measures the new-system workflow. `extend` and `migrate` were
added after it and are measured separately in
[Existing systems](#existing-systems-extend-and-migrate).

## Headline

| | With plugin | Plain Claude |
|---|---|---|
| Senior SRE production-readiness review (reader-side) | **48 / 54** | 22 / 54 |
| Principal DevOps architect design review (reader-side, strictest) | **34 / 54** | 8 / 54 |
| Every decision has a "because" | **51 / 54** | 39 / 54 |
| Kubernetes pushback when the CTO asks for EKS (case 15) | **3 / 3** | 0 / 3 |
| Residency: data-flow map (regulated cases) | **12 / 12** | 2 / 12 |
| Buildable design (reader-side) | 54 / 54 | 51 / 54 |
| Quality attributes (reader-side) | 54 / 54 | 50 / 54 |
| Migration path with cut-over and rollback (case 08, before `migrate`; 3 / 3 after, see below) | 1 / 3 | **3 / 3** |
| Mean score, all graders | **0.93** | 0.66 |
| Mean score, without graders that reward the plugin's own format¹ | **0.92** | 0.72 |
| Scenarios better / tie / worse | 18 / 1 / 0 | — |
| Mean cost per run (USD) | 0.22 | 0.15 |
| Mean time per run (s) | 104 | 98 |

¹ Excludes `portability-ratings`, `not-legal-advice`, `decision-unticked`,
`no-ticked-decision` and `options-at-a-glance`.

**What this says.** With its design rules (no single point of failure against
the availability target, secrets rotation, environment separation, targets
consistent with on-call) and the team-fit budget, a senior SRE approves the
plugin's design 48 times in 54 against 22 for plain Claude. The strictest grader, a principal DevOps design review, still rejects
20 of 54 plugin designs; see below.

## How it was run (read before quoting numbers)

- **Runner:** `tools/eval_harness.py` on the [`dev` branch](https://github.com/mohammedrampurawala1111/cloud-architect/tree/dev), a stand-in for `claude plugin eval`. The scenarios and graders are in `evals/` on that branch.
- **Agent model:** Sonnet. **Judge:** Opus, blind to the arm, one call per run.
- **Runs:** 3 per arm per case. Differences under ~0.1 on one case are noise.
- **Isolation:** fresh empty directory per run; user settings, plugins and MCP
  servers excluded; both arms allowed `Read`, `Skill` and `Bash(python3:*)`.
- **Chat-only answers;** file deliverables are not graded.
- **Prompts end with a checklist** (options, rough cost, availability and
  recovery targets, how to check each decision). That helps plain Claude: it
  ties on `buildable-design` and `quality-attributes` because the prompt asks.
- **The design skill loaded in 54 of 54 plugin runs**, and in none of the 6
  unrelated-question runs.
- **Spend:** USD 34.04 (judge 13.21), plus a USD 0.84 pilot.

## What the evals caught

1. **Inconsistent capacity figures.** Claims the provisioned units can't carry
   (e.g. a 3-5x surge on shards sized for 1x; case 05).
2. **Recovery that misses stateful components.** The DR plan covers the main
   database but not the card vault, keys or identity store (case 02), or photo
   storage (case 03).
3. **Hidden downtime in a scaling step.** A pre-sale database resize that
   restarts the instance, not weighed against the error budget (case 04).
4. **Migration cut-over and rollback dropped (case 08, 1/3 vs 3/3).** "Don't
   plan the team's work" was read as excluding cut-over and rollback, which for
   a migration are architecture decisions. Fixed by the `migrate` skill (3/3,
   see below).

Items 1-3 are internal-consistency errors that a deterministic check of the
design can catch; item 4 is a scope wording fix.

## Results

| Scenario | With plugin | Baseline | Δ | Plugin failed | Baseline failed |
|---|---|---|---|---|---|
| 01-startup-saas | 1.00 | 0.82 | +0.18 | — | portability-ratings, principal-devops-review |
| 02-eu-fintech-dora | 0.93 | 0.56 | +0.37 | principal-devops-review, senior-sre-review | data-flow-map, decisions-have-because, eu-data-stays-in-eu, eu-provider-alternative, not-legal-advice, portability-ratings, principal-devops-review, senior-sre-review |
| 03-healthcare-gdpr | 0.93 | 0.52 | +0.41 | eu-provider-alternative, principal-devops-review | data-flow-map, decisions-have-because, eu-data-stays-in-eu, eu-provider-alternative, not-legal-advice, portability-ratings, principal-devops-review, senior-sre-review |
| 04-ecommerce-high-traffic | 0.95 | 0.64 | +0.31 | principal-devops-review | decisions-have-because, portability-ratings, principal-devops-review, senior-sre-review |
| 05-event-pipeline | 0.90 | 0.77 | +0.13 | principal-devops-review | portability-ratings, principal-devops-review, senior-sre-review |
| 06-ml-inference-api | 1.00 | 0.59 | +0.41 | — | decisions-have-because, portability-ratings, principal-devops-review, senior-sre-review |
| 07-internal-azure-m365 | 0.95 | 0.83 | +0.12 | principal-devops-review | portability-ratings, principal-devops-review |
| 08-legacy-onprem-migration | 0.86 | 0.74 | +0.12 | migration-path, principal-devops-review | decisions-have-because, portability-ratings, principal-devops-review, quality-attributes, senior-sre-review |
| 09-strong-k8s-platform | 1.00 | 0.72 | +0.28 | — | portability-ratings, principal-devops-review, senior-sre-review |
| 10-solo-side-project | 0.90 | 0.67 | +0.23 | principal-devops-review, senior-sre-review | portability-ratings, principal-devops-review, senior-sre-review |
| 11-global-low-latency-api | 0.91 | 0.64 | +0.27 | principal-devops-review | decisions-have-because, portability-ratings, principal-devops-review, senior-sre-review |
| 12-batch-analytics | 0.90 | 0.59 | +0.31 | principal-devops-review | decisions-have-because, portability-ratings, principal-devops-review, senior-sre-review |
| 13-multitenant-b2b-saas | 1.00 | 0.61 | +0.39 | — | data-flow-map, eu-provider-alternative, not-legal-advice, portability-ratings, principal-devops-review, senior-sre-review |
| 14-quick-mode | 0.67 | 0.14 | +0.52 | decisions-have-because, principal-devops-review, senior-sre-review | buildable-design, cost-estimate, decisions-have-because, mermaid-present, portability-ratings, principal-devops-review, quality-attributes, quick-mode, senior-sre-review, team-fit |
| 15-k8s-despite-budget-1 | 0.93 | 0.48 | +0.45 | decisions-have-because, principal-devops-review | decisions-have-because, k8s-pushback, portability-ratings, principal-devops-review, senior-sre-review, team-fit |
| 16-neg-unrelated | 1.00 | 1.00 | +0.00 | — | — |
| 17-cto-decision-brief | 1.00 | 0.69 | +0.31 | — | cto-questions, decision-unticked, decisions-have-because, options-at-a-glance, portability-ratings, principal-devops-review, senior-sre-review |
| 18-india-payments-residency | 0.92 | 0.86 | +0.06 | principal-devops-review | data-flow-map, not-legal-advice, portability-ratings |
| 19-org-guardrails | 0.91 | 0.71 | +0.20 | principal-devops-review, senior-sre-review | portability-ratings, principal-devops-review, senior-sre-review |

**Mean score:** plugin 0.93 · baseline 0.66 · Δ +0.27  
**Scenarios:** plugin better 18 · tie 1 · baseline better 0

| Grader | Plugin pass | Baseline pass |
|---|---|---|
| answers-question | 3/3 | 3/3 |
| approved-alternative-considered | 3/3 | 3/3 |
| buildable-design | 54/54 | 51/54 |
| cost-estimate | 54/54 | 51/54 |
| cto-decides | 3/3 | 3/3 |
| cto-questions | 3/3 | 2/3 |
| data-flow-map | 12/12 | 2/12 |
| data-in-jurisdiction | 3/3 | 3/3 |
| decision-unticked | 3/3 | 0/3 |
| decisions-have-because | 51/54 | 39/54 |
| dora-considerations | 3/3 | 3/3 |
| eu-data-stays-in-eu | 9/9 | 4/9 |
| eu-provider-alternative | 7/9 | 3/9 |
| frameworks-to-controls | 3/3 | 3/3 |
| gpu-capacity | 3/3 | 3/3 |
| health-data-controls | 3/3 | 3/3 |
| k8s-pushback | 3/3 | 0/3 |
| latency-plan | 3/3 | 3/3 |
| mermaid-labels-quoted | 54/54 | 54/54 |
| mermaid-present | 54/54 | 51/54 |
| migration-path | 1/3 | 3/3 |
| no-design-skill | 3/3 | 3/3 |
| no-eu-only-restriction | 3/3 | 3/3 |
| no-invented-services | 54/54 | 54/54 |
| no-ticked-decision | 3/3 | 3/3 |
| not-legal-advice | 12/12 | 2/12 |
| options-at-a-glance | 3/3 | 1/3 |
| portability-ratings | 54/54 | 0/54 |
| principal-devops-review | 34/54 | 8/54 |
| quality-attributes | 54/54 | 50/54 |
| quick-mode | 3/3 | 0/3 |
| respects-guardrails | 3/3 | 3/3 |
| senior-sre-review | 48/54 | 22/54 |
| team-fit | 54/54 | 48/54 |
| tenant-isolation | 3/3 | 3/3 |
| uses-existing-estate | 3/3 | 3/3 |

| Arm | Runs | Mean cost (USD) | Mean time (s) | Replies with Mermaid lint errors |
|---|---|---|---|---|
| with | 57 | 0.22 | 104 | 0 of 54 |
| without | 57 | 0.15 | 98 | 0 of 51 |

## Existing systems: `extend` and `migrate`

`extend` (a feature in an existing codebase) and `migrate`, measured on 10
November 2026 on the two cases they target, 3 runs per arm; the other 18 cases were not
rerun (the new-system workflow only gained a routing step; a spot check of
cases 01 and 15 still routed to `design`).

| Case | With plugin | Plain Claude |
|---|---|---|
| 08 legacy on-prem migration | **1.00** | 0.81 |
| 20 feature in an existing repo (sample repo in `tools/fixtures/` on the `dev` branch) | **0.98** | 0.60 |

| Grader (cases 08 + 20, 6 runs per arm) | With plugin | Plain Claude |
|---|---|---|
| Senior SRE review | **6 / 6** | 2 / 6 |
| Principal DevOps review | **6 / 6** | 2 / 6 |
| Quality attributes | **6 / 6** | 3 / 6 |
| Migration path with cut-over and rollback (08) | 3 / 3 | 3 / 3 |
| Fits the existing code's patterns (20) | 3 / 3 | 3 / 3 |
| Cites real files from the repo (20) | 3 / 3 | 3 / 3 |
| Safe unauthenticated link design (20) | 3 / 3 | 3 / 3 |

Plain Claude reads the code as well as the plugin does (both arms had Read,
Glob and Grep): it ties on fitting the patterns and citing files. The plugin
wins on what a reviewer checks next: availability and recovery for the new
data, environment separation, and consistency. The pilot caught `extend`
adopting "test in production behind flags" because the sample repo has no
staging environment; it now treats environment separation as a precondition.
Spend: USD 4.93 plus USD 2.33 of pilots.

## Reproduce

```bash
git checkout dev
python3 tools/gen_evals.py .
python3 tools/eval_harness.py plugins/cloud-architect --runs 3 --max-cost 80 --jobs 10
python3 tools/build_results.py out.md evals/results/<dir>
```
