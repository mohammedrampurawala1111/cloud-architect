# Examples

Four complete runs of `cloud-architect` 1.0.0, generated on 10 November 2026
with Claude Sonnet and not edited. Each folder is exactly what the plugin wrote
to `docs/architecture/<system>/`. The prompts are eval scenarios 01, 02, 05 and
06 (in `evals/`), with two additions: the CTO makes the final decision, and the
plugin may not ask questions, so every gap is an assumption listed in the
README.

| Folder | Scenario | Look at |
|---|---|---|
| [startup-saas](startup-saas/) | 3 TypeScript developers, no on-call, B2B scheduling SaaS, US and Canada | Team budget and Kubernetes rejection in `options.md`; Canadian residency in `controls.md` |
| [eu-fintech-payments](eu-fintech-payments/) | German payments platform under DORA, EU-only, RPO 0 for the ledger | `controls.md`: data-flow map, jurisdiction flags, DORA exit strategy; card-data isolation ADR |
| [iot-telemetry-pipeline](iot-telemetry-pipeline/) | 20k devices, alerts within 5 s, 13-month history, Australia | Streaming options for a team without Kubernetes; recovery tier ADR |
| [ml-inference-api](ml-inference-api/) | Fine-tuned 8B model, 50 req/s, p95 < 1.5 s | Managed GPU serving vs Kubernetes; capacity and load-shedding ADR |

Every folder has `README.md` (requirements, recommendation, quality
attributes, risks), `options.md`, `diagrams.md`, `decision-brief.md` (left
undecided for the CTO) and `adr/`, each ADR with a "because" and fitness
criteria. Three include `controls.md` because their scenarios have residency
rules.

Costs are rough estimates from the model's memory as of the generation date:
verify with each provider's pricing calculator. ADRs are Proposed: these are
designs for review, not decisions.
