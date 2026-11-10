"""Generate evals/ cases (repo root, outside the plugin folder: prompt.md + graders/*.md)."""
import os
import shutil
import sys

ROOT = sys.argv[1]
# Eval cases live at the repo root, outside the plugin folder, so they never ship.
EVALS = os.path.join(ROOT, "evals")

SUFFIX = (
    "\n\nI can't answer follow-up questions right now, so don't ask: make reasonable "
    "assumptions, list them, and finish. Don't write any files; put the complete design "
    "in your reply: requirements summary, an assessment of what my team can run, 2-3 "
    "options with trade-offs, your recommendation, the mapping to concrete cloud "
    "products, Mermaid diagrams (context and containers), the key decisions, a rough "
    "monthly cost per option, the availability and recovery targets the design must "
    "meet, and how someone could check that the built system follows each key "
    "decision.\n"
)
QUICK_SUFFIX = (
    "\n\nI can't answer follow-up questions right now, so don't ask: make reasonable "
    "assumptions, list them, and finish. Don't write any files; put the design in your "
    "reply.\n"
)
EXTEND_SUFFIX = (
    "\n\nI can't answer follow-up questions right now, so don't ask: make reasonable "
    "assumptions, list them, and finish. Don't write or change any files; put the design in "
    "your reply: how the existing system is built (with file references), 2-3 options with "
    "trade-offs, your recommendation, what changes where, data and API changes, how it rolls "
    "out safely, Mermaid diagrams (as-is and to-be), a rough monthly cost delta, and the key "
    "decisions with how someone could check each one is followed.\n"
)
# The sample repository lives outside the plugin folder (tools/fixtures/), so the
# plugin never ships it; the path is relative to the case directory.
EXTEND_FRONT = (
    "---\nmax_turns: 30\ntimeout_seconds: 900\nfixture: ../../tools/fixtures/fieldservice\n"
    'allowed_tools: [Read, Glob, Grep, Skill, "Bash(python3:*)"]\nruns: 3\n---\n'
)
FRONT = (
    "---\nmax_turns: 30\ntimeout_seconds: 900\n"
    'allowed_tools: [Read, Skill, "Bash(python3:*)"]\nruns: 3\n---\n'
)

REAL_NAMES = (
    "Treat these 2025-2026 product names as real: Gemini Enterprise Agent Platform "
    "(formerly Vertex AI), Agent Search, Agent Platform Endpoints, Microsoft Foundry "
    "(formerly Azure AI Foundry), Azure Managed Redis, Azure Database for PostgreSQL "
    "elastic clusters, Fabric Data Warehouse, Aurora DSQL, Amazon S3 Vectors, Timestream "
    "for InfluxDB, AWS European Sovereign Cloud, EU Data Boundary, Google Cloud Data "
    "Boundary, Google Cloud Dedicated, S3NS, Delos Cloud, Bleu, Cloud Run functions, "
    "Memorystore for Valkey, Managed Service for Apache Kafka, Hetzner Object Storage, "
    "OVHcloud Managed Kubernetes Service / Public Cloud Databases / AI Endpoints, "
    "Scaleway Kubernetes Kapsule / Serverless Containers / Serverless Functions / "
    "Generative APIs, STACKIT Kubernetes Engine (SKE) / PostgreSQL Flex / AI Model "
    "Serving, IONOS Managed Kubernetes / DBaaS / AI Model Hub."
)


def llm(criteria, weight=1, focus="last_message"):
    return "---\ntype: llm\nfocus: %s\nweight: %s\n---\n%s\n" % (focus, weight, criteria.strip())


def regex(pattern, match="contains", flags=None, target="last_message"):
    fm = "---\ntype: regex\ntarget: %s\nmatch: %s\n" % (target, match)
    if flags:
        fm += "flags: %s\n" % flags
    return fm + "---\n" + pattern + "\n"


COMMON = {
    "decisions-have-because": llm(
        "PASS if every major component or decision in the recommended design (compute, "
        "primary data store, messaging, identity, provider/region choice) is justified "
        "with a reason tied to a stated requirement or a fact about the team, written "
        "as an explicit 'because …' or an equivalent explicit justification next to the "
        "choice. FAIL if two or more major choices are stated without any reason, or the "
        "reasons are generic ('it is scalable') rather than tied to this scenario."),
    "portability-ratings": llm(
        "PASS if the recommended design gives a per-component portability or lock-in "
        "rating for the mapped cloud products (for example Portable / Adaptable / Locked, "
        "or an explicit lock-in level per component in a table). FAIL if lock-in is only "
        "discussed in general terms or for fewer than half of the mapped components."),
    "cost-estimate": llm(
        "PASS if the response gives a rough monthly infrastructure cost (a figure or "
        "range) for at least two options, with the sizing assumptions or main cost "
        "drivers behind it. FAIL if cost is only described qualitatively or given for one "
        "option only."),
    "no-invented-services": llm(
        "FAIL only if the response names a cloud product or managed service that clearly "
        "does not exist under that name, or attributes a managed service to a provider "
        "that does not offer it (e.g. 'Hetzner Managed PostgreSQL', 'AWS Kubernetes "
        "Lite'). Renamed or recently launched products are fine. If unsure whether a "
        "product exists, PASS. " + REAL_NAMES),
    "mermaid-present": regex(r"```mermaid"),
    "mermaid-labels-quoted": regex(
        r"\w\[[^\"(\[\n\]][^\"\n\]]*[()][^\"\n\]]*\]", match="not_contains"),
    # Graders below are written from the reader's side (engineer, SRE, principal
    # DevOps architect), not from the plugin's output format, so both arms can pass.
    "buildable-design": llm(
        "Judge as an engineer who must build this without the architect in the room. "
        "PASS if you could start building without re-deciding the major choices: the "
        "response names specific products, regions and numeric targets or limits; gives "
        "concrete, checkable conditions for the key decisions (not 'scalable' or "
        "'secure'); and names the risky assumptions to verify first. FAIL if two of "
        "these are missing or vague."),
    "quality-attributes": llm(
        "PASS if the response states, for the recommended design: availability or "
        "latency targets for the main user-facing paths, a backup/recovery approach "
        "consistent with the stated (or assumed) data-loss and recovery-time needs, and "
        "an availability target that is consistent with the team's on-call situation "
        "(or explicitly conditional on on-call). FAIL if two or more of these are "
        "missing."),
    "senior-sre-review": llm(
        "Judge as a senior SRE in a production-readiness review of this design. PASS if "
        "you would let it proceed to build with at most minor comments: it is operable "
        "by the stated team, has no single point of failure that contradicts the stated "
        "availability need, covers backups, secrets, monitoring and environment "
        "separation, and does not add components the requirements don't need. FAIL if "
        "you would send it back for rework.", weight=2),
    "principal-devops-review": llm(
        "Judge as a principal DevOps architect reviewing the DESIGN before a platform "
        "team builds it. Judge architecture decisions, not implementation detail: do not "
        "require product or tool names for secrets, CI/CD or monitoring, pipeline steps, "
        "deploy or rollback mechanics, runbooks or configuration; leaving those to the "
        "platform team is correct. PASS only if all hold: (1) right-sized: nothing "
        "heavier than the team, traffic and availability need justify, and no essential "
        "building block missing; (2) failure modes fit the targets: no single point of "
        "failure that breaks the stated availability, and the recovery tier matches "
        "RPO/RTO; (3) sound boundaries: where traffic enters, what is private, and where "
        "sensitive data lives and flows are clear and defensible; (4) operable by the "
        "stated team: what must be monitored and recovered is stated, and the "
        "availability target is reconciled with their on-call situation; (5) environments "
        "are separated and isolated as a requirement; (6) internally consistent: figures, "
        "verdicts and criteria agree across sections, and cost is plausible for the "
        "sizing with the big traps named; (7) the hard trade-offs are stated honestly, "
        "with what would change the decision. FAIL only for a design flaw that would make "
        "you send it back, never for detail that belongs to the platform team.", weight=2),
    "plugin-skill-fired": "---\ntype: tool_used\ntool: Skill\ninput_match: cloud-architect\narm: with-only\n---\n",
}

EU = {
    "eu-data-stays-in-eu": llm(
        "PASS if every data store, backup/DR copy and processing component that handles "
        "personal data is placed in an EU region (EU member state; not UK, Switzerland "
        "or US), and the response explicitly flags any component or third-party "
        "sub-processor that is outside the EU or subject to non-EU jurisdiction (e.g. a "
        "US-parent provider, a global CDN/DNS/IdP, an email or monitoring SaaS). FAIL if "
        "any personal-data store or processing is placed outside the EU or if no such "
        "flags/analysis appear."),
    "eu-provider-alternative": llm(
        "PASS if the response offers at least one EU-headquartered provider option "
        "(e.g. Hetzner, OVHcloud, Scaleway, STACKIT, IONOS) alongside the hyperscaler "
        "EU-region or sovereign-cloud mapping, with at least one concrete trade-off. FAIL "
        "otherwise."),
    "data-flow-map": llm(
        "PASS if the response includes a data-flow map (table or diagram) showing where "
        "personal data is stored and processed (by component, provider and region). "
        "FAIL if there is no such map."),
    "not-legal-advice": regex(r"not legal advice", flags="i"),
}


def team_fit(text):
    return llm("PASS if the response explicitly assesses what this team can operate "
               "(size, skills, on-call) and the recommended option respects it: " + text)


CASES = [
    ("01-startup-saas",
     "Help me architect a B2B SaaS for scheduling field-service technicians: web app, "
     "REST API, nightly report generation, email notifications. Expect 200 customer "
     "companies and about 30 requests/second at peak in year one. We are 3 developers "
     "(TypeScript, some AWS experience, no Kubernetes, no on-call rotation) and want to "
     "run as little infrastructure as possible. Customers are in the US and Canada.",
     {"team-fit": team_fit(
         "a 3-person team with no Kubernetes experience and no on-call. FAIL if the "
         "recommendation is Kubernetes, self-managed servers or microservices.")}),
    ("02-eu-fintech-dora",
     "Design the platform for a German payments startup: card-payment processing API, "
     "ledger, merchant dashboard, fraud scoring. 500 TPS peak, 99.95% availability, "
     "RPO 0 for the ledger. We are a regulated financial entity under DORA and BaFin "
     "supervision, and customer data must stay in the EU. Team: 10 engineers, 3 of them "
     "do ops with an on-call rotation, solid Terraform and containers, some Kubernetes "
     "(1 on a 0-3 scale), mostly Java/Kotlin; no dedicated platform team.",
     {"team-fit": team_fit(
         "10 engineers with on-call and solid Terraform/containers but limited "
         "Kubernetes. FAIL if it recommends self-run databases, a service mesh or a "
         "self-managed Kubernetes control plane without flagging the team gap."),
      "dora-considerations": llm(
          "PASS if the response addresses DORA-specific needs with concrete design "
          "consequences: at least three of exit strategy/portability for critical "
          "providers, ICT third-party register, concentration risk, major-incident "
          "reporting, resilience/threat-led testing. FAIL if DORA is only named.")}),
    ("03-healthcare-gdpr",
     "We're building a telehealth app in the Netherlands: patients book video "
     "consultations, upload photos of symptoms, and doctors write notes. This is GDPR "
     "special-category health data. Around 20k patients in year one. Team: 4 developers "
     "(Python, React), one has solid Azure experience, nobody has Kubernetes, no on-call. "
     "Video calls can use a third-party video API.",
     {"team-fit": team_fit(
         "4 developers, no Kubernetes, no on-call. FAIL if it recommends Kubernetes or "
         "self-run infrastructure."),
      "health-data-controls": llm(
          "PASS if the response specifies concrete controls for special-category health "
          "data: encryption with customer-managed keys or equivalent, access logging, "
          "and a recommendation to do a DPIA, and it checks the third-party video API "
          "for EU processing. FAIL if two of these are missing.")}),
    ("04-ecommerce-high-traffic",
     "Design an e-commerce platform for a fashion retailer: catalogue, search, cart, "
     "checkout, order management. Normal load 300 requests/second, flash sales up to "
     "8,000 requests/second for 30 minutes. Team: 25 engineers, a 4-person platform "
     "team with solid Kubernetes and Terraform, 24/7 on-call. We're on GCP today. "
     "Customers are in the US.",
     {"team-fit": team_fit(
         "a large team with a platform team, solid Kubernetes and on-call; Kubernetes "
         "or managed containers are both acceptable. FAIL if the team's capability is "
         "ignored entirely or the design has no plan for the flash-sale peak.")}),
    ("05-event-pipeline",
     "Architect an IoT telemetry pipeline: 20,000 devices send a JSON reading every 10 "
     "seconds; we need real-time alerting on thresholds within 5 seconds, a 13-month "
     "history for dashboards, and a daily export to the finance team. Team: 5 engineers "
     "(Python, Go), solid AWS, containers 2/3, Terraform 2/3, no Kubernetes, an on-call "
     "rotation exists. Customers are in Australia.",
     {"team-fit": team_fit(
         "5 engineers with on-call and solid AWS/Terraform but no Kubernetes. FAIL if it "
         "recommends self-run Kafka/Flink or Kubernetes without flagging the gap.")}),
    ("06-ml-inference-api",
     "Design a public API that serves a fine-tuned 8B-parameter open-weight language "
     "model for document classification: 50 requests/second at peak, p95 under 1.5 s, "
     "traffic mostly in business hours. Team: 3 ML engineers (Python, PyTorch) and 1 "
     "backend developer, some GCP, no Kubernetes, no on-call. Users are in the US.",
     {"team-fit": team_fit(
         "4 people without Kubernetes or on-call. FAIL if it recommends self-managed "
         "GPU clusters on Kubernetes without flagging that the team cannot run it."),
      "gpu-capacity": llm(
          "PASS if the response addresses GPU serving concretely (managed endpoint or "
          "serverless GPU option, scale-to-zero or minimum capacity trade-off, and cost "
          "of idle GPUs). FAIL if GPU capacity and cost are not discussed.")}),
    ("07-internal-azure-m365",
     "Architect an internal expense-approval tool for a 3,000-employee company that "
     "runs on Microsoft 365 and Entra ID, with an existing Azure enterprise agreement. "
     "Employees submit receipts (photos/PDFs), managers approve in Teams, finance "
     "exports to the ERP nightly. Team: 2 .NET developers, solid Azure DevOps, some "
     "Bicep, no Kubernetes, no on-call (business-hours support only). Offices in the US.",
     {"team-fit": team_fit(
         "2 .NET developers without on-call. FAIL if it recommends Kubernetes or a "
         "non-Azure provider without a strong reason."),
      "uses-existing-estate": llm(
          "PASS if the design reuses the existing Microsoft estate: Entra ID for "
          "sign-in, Teams integration for approvals, Azure under the existing agreement, "
          "and Azure DevOps/Bicep (or justified alternative) for delivery. FAIL if two "
          "of these are ignored.")}),
    ("08-legacy-onprem-migration",
     "We need to move a 15-year-old on-prem order-management system to the cloud: a "
     "Java monolith on two VMs, Oracle database (800 GB), nightly batch jobs, and a "
     "file share used by partners via SFTP. We have 18 months and must keep the "
     "business running. Team: 6 developers, 2 sysadmins with VMware experience, an "
     "on-call rotation, no cloud experience yet, no Kubernetes. Customers are in the US.",
     {"team-fit": team_fit(
         "a team with no cloud experience and no Kubernetes but with on-call and "
         "sysadmins. FAIL if the first step is a rewrite to microservices or Kubernetes."),
      "migration-path": llm(
          "PASS if the response gives a phased migration path (e.g. rehost/replatform "
          "first, then modernise) with how to handle the Oracle database and the SFTP "
          "partner interface, and a cut-over/rollback approach. FAIL otherwise.")}),
    ("09-strong-k8s-platform",
     "Design a multi-service logistics platform (route optimisation, tracking, "
     "partner APIs) for a company that already runs 40 services on Kubernetes. Team: "
     "30 engineers, a 6-person platform team (expert Kubernetes 3/3, Argo CD, "
     "Terraform 3/3), 24/7 on-call, preference for control and portability across "
     "clouds. 2,000 requests/second peak. Customers are in the US and Mexico.",
     {"team-fit": team_fit(
         "a team with an expert platform team and on-call; Kubernetes is appropriate "
         "here. FAIL if it rejects Kubernetes for lack of team skills or ignores the "
         "existing platform.")}),
    ("10-solo-side-project",
     "I'm a solo developer building a side project: a recipe-sharing site with user "
     "accounts, photo uploads and comments. Maybe 1,000 users. I know Python and a bit "
     "of AWS, I have no time for operations, and my budget is under $50/month. I live "
     "in the US.",
     {"team-fit": team_fit(
         "one person with no time for operations and a $50/month budget. FAIL if it "
         "recommends Kubernetes, multiple services or anything needing on-call, or if "
         "the recommended option's estimated infra cost exceeds $50/month.")}),
    ("11-global-low-latency-api",
     "Design a public pricing API for a travel-booking marketplace used worldwide: "
     "reads must return in under 50 ms p95 in North America, Europe and Asia; prices "
     "change every few minutes; 10,000 requests/second at peak. Team: 12 engineers, "
     "on-call, solid containers and Terraform, some Kubernetes. No data-residency "
     "requirements: prices are not personal data.",
     {"team-fit": team_fit(
         "12 engineers with on-call and solid containers/Terraform. FAIL if it recommends "
         "multi-region active-active self-run databases without flagging operational "
         "burden."),
      "no-eu-only-restriction": llm(
          "PASS if the design is multi-region for latency and does NOT restrict "
          "deployment to EU regions or add an EU data-sovereignty analysis, since the "
          "user said there are no residency requirements. FAIL if it confines the design "
          "to the EU or spends a section on EU sovereignty."),
      "latency-plan": llm(
          "PASS if the response explains how 50 ms p95 is met globally (edge caching or "
          "regional read replicas, cache invalidation for price changes). FAIL otherwise.")}),
    ("12-batch-analytics",
     "Architect a batch-heavy analytics platform for a retail chain: 2 TB of sales and "
     "inventory data lands nightly as CSV/Parquet from 400 stores; analysts run SQL and "
     "dashboards in the morning; a weekly demand-forecast model runs for 3 hours. "
     "Team: 4 data engineers (SQL, Python, dbt), some AWS and some GCP, no Kubernetes, "
     "no on-call (failures can wait until morning). The company is in the US.",
     {"team-fit": team_fit(
         "4 data engineers without Kubernetes or on-call. FAIL if it recommends "
         "self-run Spark/Kubernetes clusters without flagging the gap.")}),
    ("13-multitenant-b2b-saas",
     "Design a multi-tenant B2B SaaS for HR performance reviews: 300 tenant companies, "
     "largest has 20,000 employees, tenants want SSO (SAML/OIDC), strict tenant "
     "isolation, and a few large tenants want a dedicated database. All customers are "
     "in the EU and contracts require EU data residency. Team: 7 engineers (TypeScript, "
     "Go), on-call rotation, solid containers and Terraform, no Kubernetes.",
     {"team-fit": team_fit(
         "7 engineers with on-call, solid containers/Terraform, no Kubernetes. FAIL if it "
         "recommends Kubernetes without flagging the skills gap."),
      "tenant-isolation": llm(
          "PASS if the response compares tenant-isolation models (shared schema with "
          "row-level security, schema/database per tenant, dedicated stacks) and supports "
          "dedicated databases for large tenants. FAIL otherwise.")}),
    ("14-quick-mode",
     "quick: architecture for a URL shortener with click analytics. Just give me "
     "something sensible.",
     {"quick-mode": llm(
         "PASS if the response goes straight to one recommended design plus at most one "
         "alternative, lists the assumptions it made (traffic, team, budget), and does "
         "not ask the user a list of questions. FAIL if it presents three or more full "
         "options or stops to ask questions."),
      "team-fit": team_fit(
          "the team is unknown; the response must state an assumption about the team "
          "and keep the design simple (managed/serverless). FAIL if it recommends "
          "Kubernetes or microservices.")}),
    ("15-k8s-despite-budget-1",
     "We want Kubernetes for our new booking API. We are 2 junior developers (Node.js), "
     "nobody has used Kubernetes or Terraform, there is no on-call, and we prefer "
     "managed services in general — but our CTO read that Kubernetes is the industry "
     "standard, so design it on Kubernetes (EKS). Traffic: 20 requests/second. "
     "Customers are in the US.",
     {"k8s-pushback": llm(
         "PASS if the response pushes back on Kubernetes: it states clearly that this "
         "team (2 juniors, no Kubernetes/IaC experience, no on-call) is unlikely to "
         "operate EKS safely, names concrete operational risks (upgrades, patching, "
         "incident response), recommends a simpler managed alternative, and says what "
         "would need to change (skills, people, on-call) for Kubernetes to fit. It may "
         "still sketch an EKS design if it records the risks. FAIL if it simply designs "
         "EKS without challenging it, or refuses without offering an alternative."),
      "team-fit": team_fit(
          "2 junior developers with no Kubernetes/IaC and no on-call; the recommended "
          "option must be managed containers, PaaS or serverless, not EKS.")}),
]

CASES.append(
    ("17-cto-decision-brief",
     "I'm a DevOps engineer and I have to present an architecture plan to our CTO, who "
     "will make the final call. We're building a customer-support ticketing system for "
     "our SaaS: web app, email ingestion, file attachments, full-text search, about 40 "
     "requests/second at peak. Team: 5 developers (Python, Django), solid AWS and "
     "Terraform, containers 2/3, no Kubernetes, an on-call rotation of 2. Customers are "
     "in the US. Put the decision brief for the CTO in your reply too.",
     {"team-fit": team_fit(
         "5 developers with on-call, solid AWS/Terraform, no Kubernetes. FAIL if it "
         "recommends Kubernetes without flagging the skills gap."),
      "cto-decides": llm(
          "PASS if the response is framed as a recommendation for the CTO to decide: it "
          "recommends one option with reasons but explicitly leaves the decision to the "
          "CTO (e.g. a decision/sign-off section with the options to choose from), and "
          "never states that the architecture has been decided or approved. FAIL if it "
          "presents the choice as already made or gives no decision section."),
      "options-at-a-glance": llm(
          "PASS if the brief compares the options side by side in one table covering at "
          "least team fit, monthly cost and main risk or lock-in for each option. "
          "FAIL otherwise."),
      "decision-unticked": regex(r"- \[ \]"),
      "no-ticked-decision": regex(r"- \[[xX]\]", match="not_contains"),
      "cto-questions": llm(
          "PASS if the response anticipates questions the CTO is likely to ask (cost "
          "certainty, risks, lock-in, team capacity or similar) and gives short answers. "
          "FAIL otherwise.")}))

CASES.append(
    ("18-india-payments-residency",
     "Design a UPI and card payments gateway for Indian merchants: payment API, "
     "merchant dashboard, settlement batch jobs, fraud rules. 300 TPS peak, 99.95% "
     "availability. We must follow RBI rules on payment data and PCI DSS, and we plan "
     "to add customers in Singapore next year. Team: 8 engineers (Java, Go), on-call "
     "rotation, solid AWS and Terraform, some Kubernetes (1 on a 0-3 scale).",
     {"team-fit": team_fit(
         "8 engineers with on-call and solid AWS/Terraform, limited Kubernetes. FAIL if it "
         "recommends self-run databases or a self-managed control plane without flagging "
         "the gap."),
      "data-in-jurisdiction": llm(
          "PASS if payment system data (stores, backups, processing) is placed in Indian "
          "regions, citing the RBI payment-data storage requirement, and the response says "
          "how Singapore customers' data would be handled (separate region or documented "
          "transfers) without moving Indian payment data out of India. FAIL if Indian payment "
          "data is stored or replicated outside India, or residency is not addressed."),
      "frameworks-to-controls": llm(
          "PASS if PCI DSS is translated into concrete design controls (e.g. tokenisation or "
          "hosted payment fields to reduce scope, segmented cardholder data environment, "
          "encryption and key management, logging and monitoring). FAIL if PCI DSS is only "
          "named."),
      "data-flow-map": EU["data-flow-map"],
      "not-legal-advice": EU["not-legal-advice"]}))

CASES.append(
    ("19-org-guardrails",
     "Design a document-search service for our internal knowledge base: employees "
     "upload PDFs and Word files, we extract text, and they search it with keyword and "
     "semantic search. 2,000 employees, about 5 searches/second at peak, 400 GB of "
     "documents. Team: 4 engineers (Python), solid AWS, Terraform 2/3, containers 2/3, "
     "no Kubernetes, an on-call rotation of 2. Our platform team's guardrails, which "
     "every design must follow or get an explicit exception for: AWS only; regions "
     "eu-west-1 and eu-central-1 only; approved services ECS on Fargate, Lambda, "
     "RDS for PostgreSQL, S3, SQS, CloudFront and Cognito; no self-hosted databases. "
     "Offices are in Ireland and Germany.",
     {"team-fit": team_fit(
         "4 engineers with on-call, solid AWS/Terraform, no Kubernetes. FAIL if it "
         "recommends Kubernetes or self-run search clusters without flagging the gap."),
      "respects-guardrails": llm(
          "PASS if every component in the recommended design is on AWS in eu-west-1 or "
          "eu-central-1 (edge services like CloudFront excepted) and uses an approved "
          "service, OR is explicitly called out as an exception to the guardrails with a "
          "reason and an approval or sign-off step (e.g. a search service such as "
          "OpenSearch or Bedrock, which is not on the list). FAIL if a non-approved "
          "service, region or self-hosted database is used without being flagged as an "
          "exception."),
      "approved-alternative-considered": llm(
          "PASS if, for any component outside the approved list, the response says why "
          "an approved alternative (e.g. PostgreSQL full-text search plus pgvector on RDS) "
          "does or does not meet the requirement. FAIL if a non-approved service is "
          "chosen without comparing it to an approved one.")}))

CASES.append(
    ("20-extend-existing-feature",
     "This repository is our field-service scheduling API (multi-tenant SaaS, about 200 "
     "customer companies, 2,000 jobs a day). We want to add a feature: when a technician sets "
     "a job to 'on the way', the customer gets an SMS with a link to a live ETA page they can "
     "open without logging in, and the ETA updates as the technician moves. Design how to add "
     "this to the existing system. Our team is the 3 TypeScript developers in the README, no "
     "on-call rotation; customers are in the US.",
     {"team-fit": team_fit(
         "3 developers with no on-call working on the existing ECS/PostgreSQL/SQS system. FAIL if "
         "it recommends Kubernetes, a new database, Kafka or splitting into microservices without "
         "a requirement that needs it."),
      "fits-existing-patterns": llm(
          "PASS if the recommended design follows the patterns already in this repository: sends "
          "the SMS asynchronously through the existing SQS queue and worker (not in the request "
          "path), follows the existing routes/service/repository module layout, keeps row-level "
          "tenancy (tenantId on any new table and in every query), and changes the schema through "
          "the existing Prisma migrations. FAIL if two or more of these are ignored."),
      "cites-the-code": llm(
          "PASS if the response describes the existing system with references to actual files in "
          "the repository (for example src/lib/queue.ts, src/worker/handlers.ts, "
          "src/modules/jobs/service.ts, prisma/schema.prisma, infra/sqs.tf) for at least four "
          "distinct files. FAIL if it describes the system generically or cites fewer than four "
          "real files."),
      "public-link-safety": llm(
          "PASS if the unauthenticated ETA page is designed safely: an unguessable, expiring "
          "token scoped to one job (or equivalent), minimal data exposed (no customer details "
          "beyond what is needed), and it does not weaken the existing tenant isolation for the "
          "authenticated API. FAIL otherwise.")},
     "extend"))

NEGATIVE = (
    "16-neg-unrelated",
    "---\nmax_turns: 5\ntimeout_seconds: 180\nallowed_tools: [Read, Skill]\nruns: 3\n---\n"
    "What's the difference between TCP and UDP? Two short paragraphs, please.\n",
    {"no-design-skill": "---\ntype: tool_used\ntool: Skill\ninput_match: cloud-architect\nmin: 0\nmax: 0\narm: both\n---\n",
     "answers-question": llm(
         "PASS if the response explains that TCP is connection-oriented and reliable/"
         "ordered while UDP is connectionless and best-effort, in about two paragraphs, "
         "without turning it into an architecture design. FAIL otherwise.")},
)

EU_CASES = {"02-eu-fintech-dora", "03-healthcare-gdpr", "13-multitenant-b2b-saas"}


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


if os.path.isdir(EVALS):
    for name in os.listdir(EVALS):
        if name[:2].isdigit():
            shutil.rmtree(os.path.join(EVALS, name))
for case in CASES:
    slug, prompt, extra = case[:3]
    kind = case[3] if len(case) > 3 else None
    d = os.path.join(EVALS, slug)
    if kind == "extend":
        write(os.path.join(d, "prompt.md"), EXTEND_FRONT + prompt + EXTEND_SUFFIX)
        graders = dict(COMMON)
        graders.update(extra)
        for g, body in graders.items():
            write(os.path.join(d, "graders", g + ".md"), body)
        continue
    # Quick mode must not get the full checklist: it asks for 2-3 options, which
    # contradicts the quick-mode grader (one recommendation, at most one alternative).
    write(os.path.join(d, "prompt.md"), FRONT + prompt + (QUICK_SUFFIX if slug == "14-quick-mode" else SUFFIX))
    graders = dict(COMMON)
    if slug in EU_CASES:
        graders.update(EU)
    graders.update(extra)
    for g, body in graders.items():
        write(os.path.join(d, "graders", g + ".md"), body)
slug, prompt, graders = NEGATIVE
for g, body in graders.items():
    write(os.path.join(EVALS, slug, "graders", g + ".md"), body)
write(os.path.join(EVALS, slug, "prompt.md"), prompt)
print("wrote", len(CASES) + 1, "cases to", EVALS)
