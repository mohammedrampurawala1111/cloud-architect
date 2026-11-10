# Regulations and frameworks: architecture consequences

Engineering checklists, **not legal advice**. Summaries as of November 2026;
laws change and many have sector or regional add-ons. Confirm with counsel.
"(verify)" marks points to check before relying on them.

## Inferring what applies

Users rarely know which rules apply. Infer from context, show the reasoning, and
let them correct it. Mark each **Likely** (a stated fact triggers it) or
**Possibly** (depends on something unknown; say what).

| If the context says… | Likely applicable | Possibly (ask only if it changes the design) |
|---|---|---|
| Users or customers in the EU/EEA | GDPR | NIS2 (if in a listed sector and medium or large), EU Cyber Resilience Act (if you ship a product with software) |
| Users in the UK | UK GDPR | Cyber Essentials (UK public-sector customers) |
| US consumers | State privacy laws (e.g. CCPA/CPRA for California residents) | COPPA (children under 13) |
| Health data | HIPAA (US), GDPR special-category data (EU), My Health Records Act (AU, for My Health Record data) | HITRUST (if US enterprise health customers ask) |
| Card payments | PCI DSS | Reduced scope if a hosted payment page or tokenisation provider is used |
| Payments or fintech in India | RBI payment-data storage rule, DPDP Act | PCI DSS |
| Banks, insurers, investment firms in the EU | DORA, GDPR | NIS2 |
| Selling to enterprises (B2B SaaS) | SOC 2 (mainly US buyers) or ISO 27001 (EU/global buyers) are usually asked for in procurement | ISO 27701 / 27018 (privacy-focused buyers) |
| US federal government customers | FedRAMP | CMMC (defence supply chain), CJIS (law enforcement), ITAR (defence articles) |
| Government customers elsewhere | Local schemes: C5 (DE), SecNumCloud (FR), ENS (ES), IRAP (AU), MTCS (SG), Cyber Essentials (UK) | Residency in country, often with sovereign controls (R2) |
| Energy, transport, water, health providers, digital infrastructure, managed IT services in the EU | NIS2 | Sector rules from the national transposition |
| Users in Brazil / China / India / other listed countries | The local law in the table below | Its residency or transfer rule for your data categories |
| Children's data, biometrics, location tracking | The privacy law of each user region, with stricter consent and impact-assessment duties | Age verification |
| No personal data at all (e.g. public prices, telemetry without identifiers) | None for residency | Frameworks still asked by customers (SOC 2, ISO 27001) |

Default for a B2B SaaS with no other signal: the privacy law of each user region
plus "Possibly SOC 2 / ISO 27001 (customer procurement)".

## Privacy and residency laws by jurisdiction

| Jurisdiction | Main law(s) | Residency / transfer rule (summary) | Design consequence |
|---|---|---|---|
| EU / EEA | GDPR | No general localisation; transfers outside the EEA need an adequacy decision, SCCs or BCRs plus a transfer assessment | Keep personal data in EEA regions unless a transfer mechanism is in place; remote support access from outside counts as a transfer |
| United Kingdom | UK GDPR, Data Protection Act 2018 | Like GDPR; UK adequacy regulations, IDTA or the UK Addendum to SCCs | UK or adequate-country regions; treat EU↔UK flows as transfers to document |
| Switzerland | revFADP (2023) | Transfers to countries without adequate protection need safeguards | Swiss or adequate-country regions |
| United States | No general federal law; sector laws (HIPAA health, GLBA finance, COPPA children); state laws (e.g. California CCPA/CPRA and other state privacy acts) | Few residency rules; public-sector and defence workloads can require US-only, US-person-operated environments (FedRAMP, ITAR, CJIS) | Pick US regions; GovCloud-type regions for federal/defence; per-state consent and deletion features |
| Canada | PIPEDA; provincial laws (e.g. Quebec Law 25) | Transfers allowed with accountability; Quebec requires an assessment before personal data leaves the province (verify details); some public-sector bodies require local storage (verify) | Canadian regions for public sector and Quebec-heavy data |
| Brazil | LGPD | Transfers need an adequacy decision, standard clauses or other listed mechanisms | São Paulo regions or documented transfers |
| India | DPDP Act 2023 (rules notified 2025, phased in (verify)); RBI payment-data directive | DPDP allows transfers except to countries the government restricts; **payment system data must be stored only in India** (RBI) | Indian regions for payments data; keep the transfer-restriction list in review |
| China | PIPL, Data Security Law, Cybersecurity Law | Critical information infrastructure operators and large processors must store data in China; exports need a security assessment, standard contract or certification | Separate China deployment with a local operator; no shared global control plane (verify current thresholds) |
| Russia | Federal Law 152-FZ / 242-FZ | Personal data of Russian citizens must be recorded and stored initially in databases in Russia | Local primary database; replication outward only as the law allows |
| Australia | Privacy Act 1988 (APP 8); My Health Records Act; IRAP for government | Cross-border disclosure keeps the discloser accountable; My Health Record data must stay in Australia | Australian regions for health and government workloads |
| New Zealand | Privacy Act 2020 (IPP 12) | Cross-border disclosure needs comparable safeguards | NZ or Australian regions, documented safeguards |
| Japan | APPI | Transfers abroad need consent or equivalent-system safeguards | Japanese regions or documented consent |
| South Korea | PIPA | Transfers need consent or listed exceptions | Korean regions for sensitive data |
| Singapore | PDPA | Transfer obligation: comparable protection abroad | Singapore regions or contractual safeguards; MTCS for government |
| Indonesia | PDP Law 2022; sector rules | Transfers need adequate protection or consent; public-sector and financial data have local rules (verify) | Jakarta regions for public-sector and financial workloads |
| Vietnam | Decree 53 (Cybersecurity Law), PDP Decree 13 | Some service providers must store certain data locally (verify scope) | Local hosting where the decree applies |
| Saudi Arabia | PDPL; NCA cloud controls | Transfers restricted to listed conditions; government data often must stay in KSA (verify) | KSA regions for government and regulated sectors |
| UAE | Federal PDPL; DIFC and ADGM regimes; sector rules | Transfers to adequate countries or with safeguards; health data has local storage rules (verify) | UAE regions for health and government |
| South Africa | POPIA | Transfers need adequate protection, consent or contract | South African regions or documented safeguards |
| Nigeria | NDPA 2023 | Transfers need adequacy or listed safeguards; some government data localisation (verify) | Local or documented transfers |
| Turkey | KVKK | Transfers need adequacy, safeguards or authority approval | Turkish regions or approved transfers |

Common to almost all: data-subject rights (access, deletion), breach
notification within short deadlines, records of processing, impact assessments
for high-risk processing, and processor contracts covering the regions used.

## Frameworks and sector rules

| Framework | Scope | Architecture consequences |
|---|---|---|
| ISO/IEC 27001:2022 (+ 27017 cloud, 27018 PII in cloud, 27701 privacy) | Any organisation; certifies the ISMS | Asset inventory (IaC), access control and reviews, encryption, logging and monitoring, backup and restore tests, supplier management. The design enables controls; certification is process work |
| SOC 2 (Type I/II) | Service organisations, mainly US customers | Change management via CI/CD, least privilege, audit logs with retention, encryption, availability monitoring, vendor list |
| PCI DSS v4.0.x | Anyone storing, processing or transmitting card data | Minimise scope (hosted payment pages or tokenisation), segment the cardholder data environment, strong cryptography, quarterly scans, file-integrity and log monitoring |
| HIPAA (+ HITRUST) | US health data (PHI) | Business associate agreements with every provider and SaaS, encryption, audit logging, access controls, backup/contingency plan |
| NIS2 | EU essential and important entities (energy, transport, banking, health, digital infrastructure, managed ICT services, public administration, others) | Risk management measures (incident handling, continuity and backups, supply-chain security, secure development, MFA, encryption); incident reporting: early warning within 24 h, notification within 72 h. Transposition varies by member state (verify the national law) |
| DORA | EU financial entities (applies since 17 Jan 2025) | ICT third-party register; tested exit strategy per critical provider (prefer Portable components); concentration-risk analysis; major-incident reporting; resilience and threat-led testing. Critical ICT providers (incl. major hyperscalers) are under direct EU oversight since Nov 2025, which does not move the entity's own duties |
| EU Cyber Resilience Act | Products with digital elements sold in the EU (phased in to 2027 (verify)) | Secure-by-default configuration, vulnerability handling, SBOMs, security updates for the support period |
| FedRAMP (Low / Moderate / High) | Cloud services sold to US federal agencies | Use FedRAMP-authorised services and regions (often GovCloud-type), NIST SP 800-53 controls, continuous monitoring |
| NIST CSF 2.0 / SP 800-53 | US-origin control frameworks, widely used | Map controls to the design: identify, protect, detect, respond, recover, govern |
| CMMC 2.0 | US defence supply chain | Controlled unclassified information in compliant environments (often GovCloud-type), NIST SP 800-171 controls |
| C5 (Germany, BSI) | Cloud providers serving German public sector and others | Choose C5-attested services; same control themes as ISO 27001 |
| SecNumCloud (France, ANSSI) | French public sector and sensitive data | Qualified offerings only (e.g. S3NS PREMI3NS, OVHcloud qualified offers); check which services are in scope (verify) |
| ENS (Spain) | Spanish public sector | ENS-certified services at the required category |
| IRAP / Essential Eight (Australia) | Australian government | IRAP-assessed services; Essential Eight hardening (patching, MFA, backups, application control) |
| Cyber Essentials (UK) | UK public-sector suppliers | Baseline controls: firewalls, secure configuration, access control, malware protection, patching |
| MTCS (Singapore) | Singapore government and regulated sectors | MTCS-certified services at the required level |

## Designing for these rules

| Need | Architecture response |
|---|---|
| Residency | Region pinning per data category, region-restricted policies (e.g. organisation policies / SCPs), no global default services for regulated data |
| Transfers | Data-flow map, encryption with customer-managed keys, documented transfer mechanism per flow |
| Exit / portability | Portable components for critical paths; IaC for everything; tested data export |
| Incident reporting | Centralised logs with retention, alert routing to on-call, runbooks with reporting steps and deadlines |
| Backup and continuity | Point-in-time recovery, cross-zone (and if required cross-region, in-jurisdiction) backups, restore drills |
| Supply chain | Provider and SaaS register, SBOMs, pinned dependencies, signed images |
| Key control (R2/R3) | Customer-managed or external keys (HSM) held in the jurisdiction |
| Card data | Keep it out of your systems where possible (tokenisation, hosted fields) |
