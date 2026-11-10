---
name: data-residency
description: Data residency, sovereignty and compliance for architecture designs in any region. Use when the user names target countries or regions, data residency or sovereignty, or a regulation or framework (GDPR, HIPAA, PCI DSS, ISO 27001, SOC 2, NIS2, DORA, etc.).
---

# Data residency and compliance

Places the design, and the regulated data in it, where the user's rules require,
and makes any remaining exposure visible. It runs alongside `design`: apply it to
the options (Phase 3), the provider mapping (Phase 4) and the deliverables
(Phase 5). It works for any jurisdiction; nothing defaults to the EU.

> **This is not legal advice.** It is an engineering assessment to support your
> DPO, legal counsel and auditors. Include that exact sentence in `controls.md`
> and in any chat answer that uses this skill.

The output is **control requirements**: what the architecture must provide so
the organisation can comply. It is not evidence of compliance and must not be
filed as such. Evidence (configurations, access reviews, test records, audit
reports) comes from the built system and the organisation's compliance
function. Say this in `controls.md`.

## 1. Pin the scope
From the interview (ask once if missing):
- **Target jurisdictions:** where users are, and where data must be stored and
  processed (countries or blocs, e.g. "India", "US + Canada", "EU/EEA").
- **Regulations and frameworks:** infer them from context (regions, sector,
  data types, customer type) using "Inferring what applies" in
  `references/regulations.md`; present them as "Likely applicable (inferred)"
  with a one-line reason each, plus "Possibly applicable" for ones that depend on
  a fact you don't know. Never require the user to know the list.
- **Residency level:**

| Level | Meaning |
|---|---|
| **R1 — In-region** | Any provider, regions inside the target jurisdiction only |
| **R2 — Sovereign controls** | R1 + operator access and keys under local control (sovereign cloud offerings, customer-managed or external keys) |
| **R3 — Local jurisdiction only** | Only providers headquartered and controlled in the target jurisdiction |

Default to **R1** when the user only names a region or a privacy law, and record
it as an assumption. If no residency rule applies, say so and skip this skill;
don't restrict regions without a reason.

Look up each named law or framework in `references/regulations.md` for its
residency/transfer rules and architecture consequences. If something isn't
there, say what you know with "(verify)"; never invent a requirement.

## 2. Place every component
- Map every component to a region inside the target jurisdiction (provider +
  region name) in the mapped view and the cost table. Check that the provider
  actually has a region there; if not, say so and offer the nearest compliant
  option.
- Multi-jurisdiction systems: decide per data category where it lives (e.g. EU
  users' data in an EU region, Indian payment data in India) and show the split.
- Flag services that are global or run their control plane elsewhere even when
  data sits in-region: CDN edges, DNS, global load balancers, IAM/directory,
  support access, telemetry, cross-region backups, AI APIs routing elsewhere.
- Backups, DR replicas and logs follow the same rules. Say where they go.

## 3. Data-flow map (required)
A table **and** a Mermaid flowchart showing where regulated data is stored and
processed:

| Data category | Regulated? | Stored in (provider, region) | Processed by | Sub-processors | Leaves the jurisdiction? |
|---|---|---|---|---|---|

Categories: account/profile, special or sensitive data (health, biometrics,
financial, children's data), payment card data, logs/telemetry (often personal),
backups, analytics, AI prompts/embeddings. In the diagram use one `subgraph` per
jurisdiction plus `Outside`, and label every arrow that carries regulated data.
Run `check_mermaid.py` on it like any other diagram.

## 4. Jurisdiction flags
For every component **and every third-party SaaS** (auth, email/SMS, payments,
error tracking, APM, CDN, support desk, LLM API, CI runners):

| Rating | Meaning |
|---|---|
| 🟢 **Local** | Provider headquartered in the target jurisdiction, in-region |
| 🟡 **In-region, foreign parent** | In-region, but the provider's parent is subject to another country's law (e.g. US CLOUD Act). Note mitigations: sovereign offering, customer-managed keys, encryption before upload, contracts |
| 🔴 **Leaves the jurisdiction** | Stored or processed outside: needs the transfer mechanism the law allows (adequacy, SCCs, consent, approval) or a replacement |

At R3 every 🟡/🔴 must be replaced or explicitly accepted by the user. At R1/R2
list them as risks with mitigations. Never claim a sovereign offering removes
foreign jurisdiction; say what it changes and that the legal assessment is the
customer's.

## 5. Regional and sovereign providers
For the chosen option show the hyperscaler mapping in the target region (plus
its sovereign offering at R2) and, where they exist, at least one provider
headquartered in the jurisdiction. Use the `capability-map` skill's provider map (`${CLAUDE_PLUGIN_ROOT}/skills/capability-map/references/provider-map.md`)
("Regional and sovereign providers"). For jurisdictions it doesn't cover, name
local providers only if you are sure they exist and offer the service; otherwise
say "check local providers (verify)". **Never invent a service.** If a provider
lacks a managed product, reclassify the component (e.g. `self_hosted_database`)
and include that variant as its own option in the single `plan.py` call (see
`design`, step 4): fewer managed services often push a local-only option over
the team's budget. Record that trade-off in the recommendation and
an ADR.

## 6. Frameworks → control requirements
For each framework in scope (ISO 27001, SOC 2, PCI DSS, HIPAA, NIS2, DORA,
FedRAMP, …) add its architecture consequences from `references/regulations.md`
as numbered control requirements the design must provide (logging, encryption,
key management, segmentation, access reviews, backup and recovery, incident
reporting, exit strategy):

| ID | Control requirement | Law / framework | Design element |
|---|---|---|---|
| CR-01 | Card data never stored; payment page hosted by the PSP | PCI DSS | ADR-0004 |

Frameworks certify the organisation, not the diagram: say which controls the
design enables and which remain process work. Each control requirement that the
design itself must satisfy also appears as a fitness criterion in the ADR it
belongs to (e.g. the residency ADR).

## 7. Deliverable: `controls.md`
In `docs/architecture/<system>/`:
1. Jurisdictions, residency level and why; regions used per data category.
2. Data-flow table and diagram.
3. Jurisdiction table (component, provider, region, rating, mitigation).
4. Provider comparison: hyperscaler in-region vs regional/sovereign provider,
   with gaps, portability ratings and the team-fit verdict for each.
5. Laws and frameworks in scope, with the control requirements table.
6. Open questions for the DPO / legal / compliance team (impact assessment?
   transfer assessments? sub-processor list? certification scope?).
7. The sentences "This is not legal advice." and "These are control
   requirements for the design, not evidence of compliance; evidence comes from
   the built system."

Also add a residency ADR ("Keep regulated data in <region> on <provider>") and
mark anything you could not confirm with "(verify)".
