# Eval results — cloud-architect

Run on 10–11 November 2026 on the released plugin (instructions and reference
data only, no scripts): **plugin vs plain Claude**, 20 scenarios, 3 runs per
side (120 runs), same prompts and tools, blind LLM judge.

## Headline

| | With plugin | Plain Claude |
|---|---|---|
| **Senior-SRE rubric (Opus judge)** (reader-side) | **56 / 57 (98%)** | 20 / 57 (35%) |
| **Principal-DevOps rubric (Opus judge)** (reader-side, strictest) | **47 / 57 (82%)** | 8 / 57 (14%) |
| Team fit respected | **57 / 57** | 51 / 57 |
| Kubernetes pushback when the CTO asks for EKS (case 15) | **3 / 3** | 0 / 3 |
| Every decision has a "because" | **55 / 57** | 39 / 57 |
| Availability and recovery targets (reader-side) | **57 / 57** | 51 / 57 |
| Buildable design (reader-side) | **57 / 57** | 54 / 57 |
| Residency: data-flow map (regulated cases) | **12 / 12** | 3 / 12 |
| Fits the existing code / cites real files (case 20) | 3 / 3 | 3 / 3 |
| Migration path with cut-over and rollback (case 08) | 3 / 3 | 3 / 3 |
| Mean score, all graders | **0.97** | 0.65 |
| Mean score, without graders that reward the plugin's own format¹ | **0.97** | 0.71 |
| Scenarios better / tie / worse | 19 / 1 / 0 | — |
| Mean cost per design (USD) | 0.27 | 0.16 |
| Mean time per design (s) | 150 | 106 |

Scored by an LLM judge (Opus) with rubrics written by the author; not a human review. Method and caveats in evals/RESULTS.md.

¹ Excludes `portability-ratings`, `not-legal-advice`, `decision-unticked`,
`no-ticked-decision` and `options-at-a-glance`.

**What this says.** The Opus judge, using the senior-SRE rubric, approves the
plugin's design 56 times in 57, against 20 for plain Claude; using the
principal-DevOps rubric, it approves 47 against 8.
Both sides read code equally well and both give a buildable design with a cost
estimate; the plugin wins on what the rubrics check next: team fit that holds
under pressure, recovery that covers every stateful component, consistent
figures, and residency analysis. It costs about 1.7× as much per design.

## How it was run (read before quoting numbers)

- **Runner:** `tools/eval_harness.py` on the [`dev` branch](https://github.com/mohammedrampurawala1111/cloud-architect/tree/dev),
  a stand-in for `claude plugin eval`. Scenarios and graders are in `evals/` on
  that branch; the sample repository for case 20 is in `tools/fixtures/`.
- **Agent model:** Sonnet. **Judge:** Opus, blind to the side, one call per run.
- **Runs:** 3 per side per case. Differences under ~0.1 on one case are noise.
- **Isolation:** fresh directory per run; user settings, plugins and MCP servers
  excluded; both sides allowed `Read`, `Skill` and `Bash(python3:*)` (and
  `Glob`, `Grep` in case 20).
- **Chat-only answers;** file deliverables are not graded.
- **Prompts end with a checklist** (options, rough cost, targets, how to check
  each decision). That helps plain Claude; real prompts are usually shorter.
- **Reader-side graders** are written from an engineer's, SRE's or principal
  DevOps architect's point of view, not from the plugin's format.
- **The plugin loaded in 57 of 57 design requests**, and in none of the 3
  unrelated-question runs (case 16).
- **Usage limit:** 16 runs failed on an account session limit and some judging
  returned no verdict; all affected cases (13, 15, 17-20) were rerun in full
  and the failed runs replaced.
- **Spend:** USD 40.18 for the final result set.

## Known weak spots

- **The principal-DevOps rubric still rejects 10 of 57** plugin designs, mostly
  for a cost or recovery figure that doesn't match its mechanism.
- **Feature in an existing repo is the most expensive case** (USD 0.53 per
  design): the repository is read with Claude's own tools.
- **Judge error:** one case 09 run was failed for rating complexity 6 against
  budget 5 as "At limit", which is correct under the plugin's rules.

## Results

| Scenario | With plugin | Baseline | Δ | Plugin failed | Baseline failed |
|---|---|---|---|---|---|
| 01-startup-saas | 1.00 | 0.77 | +0.23 | — | portability-ratings, principal-devops-review, senior-sre-review |
| 02-eu-fintech-dora | 0.93 | 0.72 | +0.20 | decisions-have-because, eu-provider-alternative, principal-devops-review | data-flow-map, decisions-have-because, eu-data-stays-in-eu, not-legal-advice, portability-ratings, principal-devops-review, senior-sre-review |
| 03-healthcare-gdpr | 0.94 | 0.57 | +0.37 | eu-provider-alternative, principal-devops-review | data-flow-map, decisions-have-because, eu-data-stays-in-eu, eu-provider-alternative, not-legal-advice, portability-ratings, principal-devops-review, senior-sre-review |
| 04-ecommerce-high-traffic | 1.00 | 0.56 | +0.44 | — | decisions-have-because, portability-ratings, principal-devops-review, senior-sre-review |
| 05-event-pipeline | 0.95 | 0.61 | +0.33 | principal-devops-review | portability-ratings, principal-devops-review, senior-sre-review |
| 06-ml-inference-api | 1.00 | 0.62 | +0.38 | — | decisions-have-because, portability-ratings, principal-devops-review, senior-sre-review |
| 07-internal-azure-m365 | 1.00 | 0.88 | +0.12 | — | portability-ratings, principal-devops-review |
| 08-legacy-onprem-migration | 0.95 | 0.79 | +0.17 | principal-devops-review | decisions-have-because, portability-ratings, principal-devops-review |
| 09-strong-k8s-platform | 0.90 | 0.61 | +0.28 | principal-devops-review | portability-ratings, principal-devops-review, senior-sre-review |
| 10-solo-side-project | 1.00 | 0.61 | +0.39 | — | portability-ratings, principal-devops-review, senior-sre-review |
| 11-global-low-latency-api | 1.00 | 0.64 | +0.36 | — | decisions-have-because, portability-ratings, principal-devops-review, senior-sre-review |
| 12-batch-analytics | 1.00 | 0.67 | +0.33 | — | portability-ratings, principal-devops-review, senior-sre-review |
| 13-multitenant-b2b-saas | 1.00 | 0.65 | +0.35 | — | data-flow-map, decisions-have-because, eu-provider-alternative, not-legal-advice, portability-ratings, principal-devops-review, senior-sre-review |
| 14-quick-mode | 0.90 | 0.14 | +0.76 | principal-devops-review, senior-sre-review | buildable-design, cost-estimate, decisions-have-because, mermaid-present, portability-ratings, principal-devops-review, quality-attributes, quick-mode, senior-sre-review, team-fit |
| 15-k8s-despite-budget-1 | 0.95 | 0.48 | +0.48 | principal-devops-review | decisions-have-because, k8s-pushback, portability-ratings, principal-devops-review, senior-sre-review, team-fit |
| 16-neg-unrelated | 1.00 | 1.00 | +0.00 | — | — |
| 17-cto-decision-brief | 0.94 | 0.63 | +0.31 | decisions-have-because, principal-devops-review | cto-questions, decision-unticked, decisions-have-because, options-at-a-glance, portability-ratings, principal-devops-review, senior-sre-review |
| 18-india-payments-residency | 1.00 | 0.78 | +0.22 | — | data-flow-map, decisions-have-because, not-legal-advice, portability-ratings, principal-devops-review |
| 19-org-guardrails | 0.96 | 0.69 | +0.27 | principal-devops-review | decisions-have-because, portability-ratings, principal-devops-review, senior-sre-review |
| 20-extend-existing-feature | 1.00 | 0.58 | +0.42 | — | cost-estimate, decisions-have-because, portability-ratings, principal-devops-review, quality-attributes, senior-sre-review |

**Mean score:** plugin 0.97 · baseline 0.65 · Δ +0.32  
**Scenarios:** plugin better 19 · tie 1 · baseline better 0

Scored by an LLM judge (Opus) with rubrics written by the author; not a human review. Method and caveats in evals/RESULTS.md.

| Grader | Plugin pass | Baseline pass |
|---|---|---|
| answers-question | 3/3 | 3/3 |
| approved-alternative-considered | 3/3 | 3/3 |
| buildable-design | 57/57 | 54/57 |
| cites-the-code | 3/3 | 3/3 |
| cost-estimate | 57/57 | 53/57 |
| cto-decides | 3/3 | 3/3 |
| cto-questions | 3/3 | 0/3 |
| data-flow-map | 12/12 | 3/12 |
| data-in-jurisdiction | 3/3 | 3/3 |
| decision-unticked | 3/3 | 0/3 |
| decisions-have-because | 55/57 | 39/57 |
| dora-considerations | 3/3 | 3/3 |
| eu-data-stays-in-eu | 9/9 | 5/9 |
| eu-provider-alternative | 7/9 | 5/9 |
| fits-existing-patterns | 3/3 | 3/3 |
| frameworks-to-controls | 3/3 | 3/3 |
| gpu-capacity | 3/3 | 3/3 |
| health-data-controls | 3/3 | 3/3 |
| k8s-pushback | 3/3 | 0/3 |
| latency-plan | 3/3 | 3/3 |
| mermaid-labels-quoted | 57/57 | 57/57 |
| mermaid-present | 57/57 | 54/57 |
| migration-path | 3/3 | 3/3 |
| no-design-skill | 3/3 | 3/3 |
| no-eu-only-restriction | 3/3 | 3/3 |
| no-invented-services | 57/57 | 57/57 |
| no-ticked-decision | 3/3 | 3/3 |
| not-legal-advice | 12/12 | 2/12 |
| options-at-a-glance | 3/3 | 1/3 |
| portability-ratings | 57/57 | 0/57 |
| principal-devops-review | 47/57 | 8/57 |
| public-link-safety | 3/3 | 3/3 |
| quality-attributes | 57/57 | 51/57 |
| quick-mode | 3/3 | 0/3 |
| respects-guardrails | 3/3 | 3/3 |
| senior-sre-review | 56/57 | 20/57 |
| team-fit | 57/57 | 51/57 |
| tenant-isolation | 3/3 | 3/3 |
| uses-existing-estate | 3/3 | 3/3 |

Scored by an LLM judge (Opus) with rubrics written by the author; not a human review. Method and caveats in evals/RESULTS.md.

| Arm | Runs | Mean cost (USD) | Mean time (s) | Replies with Mermaid lint errors |
|---|---|---|---|---|
| with | 60 | 0.27 | 150 | 1 of 57 |
| without | 60 | 0.16 | 106 | 0 of 54 |

## Reproduce

```bash
git checkout dev   # merge main first to test the latest plugin
python3 tools/gen_evals.py .
python3 tools/eval_harness.py plugins/cloud-architect --runs 3 --max-cost 80 --jobs 6
python3 tools/build_results.py out.md evals/results/<dir>
```
