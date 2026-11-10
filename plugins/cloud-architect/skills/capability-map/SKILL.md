---
name: capability-map
description: Provider-neutral vocabulary of architecture building blocks (compute, data, messaging, networking, identity, observability) and their equivalents on AWS, Azure, GCP and self-hosted Kubernetes. Use when translating a neutral design into a specific cloud, comparing providers, assessing lock-in, or planning a migration between clouds.
---

# Capability map

Design with **capabilities**, then map to **products**. This keeps the design
portable and makes lock-in visible.

## How to use
1. Describe each component as a capability from the list below
   (e.g. `compute.containers.managed`, `data.relational`).
2. When the provider is chosen, look the capability up in
   `references/provider-map.md` and pick the product.
3. For each mapped component, record a **portability rating**:
   - **Portable** — open standard or protocol (PostgreSQL, S3 API, OCI
     containers, Kubernetes, OpenTelemetry, OIDC, AMQP/Kafka protocol).
   - **Adaptable** — provider-specific product but a common pattern with
     equivalents elsewhere; moving means config and some code (queues, functions,
     API gateways, secret stores).
   - **Locked** — proprietary data model or API with no direct equivalent;
     moving means a rewrite or data migration (DynamoDB, Cosmos DB, Spanner,
     Firestore, Step Functions, Logic Apps, proprietary ML services).
4. Prefer *Portable* when cost and effort are similar. Allow *Locked* when it
   clearly saves the team effort, and record that trade-off in an ADR.

## Capability vocabulary

**Compute**
- `compute.functions` — event-driven serverless functions
- `compute.containers.managed` — run containers without managing a cluster
- `compute.paas` — managed web app platform (push code, platform runs it)
- `compute.kubernetes` — managed Kubernetes cluster
- `compute.vm` — virtual machines / VM scale sets
- `compute.batch` — batch / long-running jobs
- `compute.workflow` — orchestration of multi-step processes / sagas

**Data**
- `data.relational` — SQL database (PostgreSQL / MySQL / SQL Server)
- `data.relational.global` — horizontally scalable / globally distributed SQL
- `data.document` — document / key-value NoSQL
- `data.cache` — in-memory cache (Redis-compatible)
- `data.object` — object / blob storage
- `data.search` — full-text search
- `data.vector` — vector search for embeddings
- `data.warehouse` — analytical warehouse
- `data.timeseries` — time-series storage

**Messaging & integration**
- `msg.queue` — point-to-point queue
- `msg.pubsub` — publish/subscribe topics, fan-out
- `msg.eventbus` — event routing with rules/filters
- `msg.stream` — ordered, replayable event stream (Kafka-style)
- `int.scheduler` — cron / scheduled triggers

**Edge & networking**
- `net.cdn` — content delivery
- `net.lb` — L7 load balancer / ingress
- `net.apigw` — API gateway (auth, rate limiting, keys)
- `net.waf` — web application firewall
- `net.dns` — managed DNS
- `net.private` — private networking (VPC/VNet, private endpoints, NAT)

**Identity & security**
- `sec.user-auth` — end-user authentication (sign-up, social, SSO)
- `sec.workload-identity` — service identities, roles, least privilege
- `sec.secrets` — secrets store
- `sec.kms` — key management / encryption keys

**Operations**
- `ops.logs`, `ops.metrics`, `ops.traces` — observability (prefer OpenTelemetry)
- `ops.ci-cd` — build and deploy pipelines
- `ops.iac` — infrastructure as code
- `ops.registry` — container / artifact registry
- `ops.backup` — backups and point-in-time restore

**AI**
- `ai.llm` — hosted foundation models
- `ai.ml-platform` — training / hosting custom models

## Before finalising
Product names, features and regional availability change. If a docs or search
tool is available, verify any product you're not certain about, especially
anything marked "verify" in the reference table. Connected MCP servers count:
a provider docs server (e.g. Microsoft Docs, AWS docs), a Terraform registry
server, or a cloud provider's read-only server can confirm a service exists in
the target region. Use only read/lookup tools, never ones that create or change
resources, and say which tool confirmed what.
