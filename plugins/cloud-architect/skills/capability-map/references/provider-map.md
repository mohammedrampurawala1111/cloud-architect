# Provider map

Last reviewed: 9 November 2026; EU provider rows re-checked the same day (rows checked against provider docs and
announcements; see "Review notes" at the end). Product names and availability
change — verify before committing to a design. "Self-hosted" means open-source components you run
on any Kubernetes cluster (cloud, on-prem or a smaller provider such as Hetzner,
OVHcloud, DigitalOcean, Scaleway).

Portability: **P** portable · **A** adaptable · **L** locked (see SKILL.md).

## Compute

| Capability | AWS | Azure | GCP | Self-hosted / K8s | Port. |
|---|---|---|---|---|---|
| compute.functions | Lambda | Azure Functions | Cloud Run functions | Knative, OpenFaaS | A |
| compute.containers.managed | ECS on Fargate | Container Apps | Cloud Run | Knative on K8s | P (OCI images) |
| compute.paas | Elastic Beanstalk | App Service | App Engine | — | A |
| compute.kubernetes | EKS | AKS | GKE | k3s, RKE2, Talos, kubeadm | P |
| compute.vm | EC2 / Auto Scaling groups | Virtual Machines / VM Scale Sets | Compute Engine / MIGs | Proxmox, KubeVirt | P |
| compute.batch | AWS Batch | Azure Batch / Container Apps jobs | Batch / Cloud Run jobs | Kubernetes Jobs, Argo Workflows | A |
| compute.workflow | Step Functions | Durable Functions / Logic Apps | Workflows | Temporal, Argo Workflows | L (managed) / P (Temporal) |

## Data

| Capability | AWS | Azure | GCP | Self-hosted / K8s | Port. |
|---|---|---|---|---|---|
| data.relational | RDS / Aurora (PostgreSQL, MySQL) | Azure Database for PostgreSQL / MySQL (Flexible Server), Azure SQL | Cloud SQL, AlloyDB | CloudNativePG, Percona operators | P (engine) |
| data.relational.global | Aurora DSQL | Azure Database for PostgreSQL elastic clusters (Citus) | Spanner | CockroachDB, YugabyteDB | L / P |
| data.document | DynamoDB, DocumentDB | Cosmos DB | Firestore, Bigtable | MongoDB, ScyllaDB | L (managed) |
| data.cache | ElastiCache / MemoryDB (Valkey/Redis) | Azure Managed Redis (Azure Cache for Redis is retiring) | Memorystore (Valkey/Redis) | Valkey, Redis | P |
| data.object | S3 | Blob Storage | Cloud Storage | Ceph RGW, SeaweedFS, Garage (avoid MinIO community edition for new designs: maintenance mode, source-only) | P (S3 API) / A |
| data.search | OpenSearch Service | Azure AI Search | Agent Search (formerly Vertex AI Search) / self-run | OpenSearch, Elasticsearch, Meilisearch | A |
| data.vector | OpenSearch, Aurora/RDS pgvector, S3 Vectors | Azure AI Search, Cosmos DB vector search, PostgreSQL pgvector | AlloyDB/Cloud SQL pgvector, Vector Search in Agent Platform (formerly Vertex AI Vector Search; verify current name) | pgvector, Qdrant, Weaviate | P (pgvector) |
| data.warehouse | Redshift | Fabric Data Warehouse (Synapse for existing workloads only) | BigQuery | ClickHouse, DuckDB | L / P |
| data.timeseries | Timestream for InfluxDB (Timestream for LiveAnalytics closed to new customers) | Azure Data Explorer / Fabric Eventhouse | Bigtable / BigQuery | TimescaleDB, VictoriaMetrics, InfluxDB | A |

## Messaging & integration

| Capability | AWS | Azure | GCP | Self-hosted / K8s | Port. |
|---|---|---|---|---|---|
| msg.queue | SQS | Service Bus queues / Storage Queues | Cloud Tasks / Pub/Sub | RabbitMQ, NATS JetStream | A |
| msg.pubsub | SNS | Service Bus topics | Pub/Sub | NATS, RabbitMQ | A |
| msg.eventbus | EventBridge | Event Grid | Eventarc | Knative Eventing | A |
| msg.stream | Kinesis, MSK (Kafka) | Event Hubs (Kafka API) | Pub/Sub, Managed Service for Apache Kafka | Kafka (Strimzi), Redpanda | P (Kafka API) |
| int.scheduler | EventBridge Scheduler | Functions timer / Logic Apps | Cloud Scheduler | Kubernetes CronJob | A |

## Edge & networking

| Capability | AWS | Azure | GCP | Self-hosted / K8s | Port. |
|---|---|---|---|---|---|
| net.cdn | CloudFront | Front Door | Cloud CDN | Cloudflare / Fastly / Bunny (third-party) | A |
| net.lb | ALB / NLB | Application Gateway / Load Balancer | Cloud Load Balancing | Gateway API (Envoy Gateway, Traefik, Cilium) | P (Gateway API) |
| net.apigw | API Gateway | API Management | API Gateway / Apigee | Kong, Envoy Gateway | A |
| net.waf | AWS WAF | Front Door / App Gateway WAF | Cloud Armor | Coraza, ModSecurity | A |
| net.dns | Route 53 | Azure DNS | Cloud DNS | ExternalDNS + any DNS provider | P |
| net.private | VPC, PrivateLink, NAT Gateway | VNet, Private Link, NAT Gateway | VPC, Private Service Connect, Cloud NAT | CNI (Cilium, Calico), WireGuard | A |

Note: the community ingress-nginx controller was retired by Kubernetes in March
2026 (no further releases or security fixes). Use a Gateway API implementation
for new self-hosted designs.

## Identity & security

| Capability | AWS | Azure | GCP | Self-hosted / K8s | Port. |
|---|---|---|---|---|---|
| sec.user-auth | Cognito | Entra External ID | Identity Platform / Firebase Auth | Keycloak, Zitadel, Authentik (or SaaS: Auth0, WorkOS, Clerk) | P (OIDC) |
| sec.workload-identity | IAM roles, IRSA / EKS Pod Identity | Managed identities, Workload Identity | Service accounts, Workload Identity | SPIFFE/SPIRE, K8s service accounts | A |
| sec.secrets | Secrets Manager / SSM Parameter Store | Key Vault | Secret Manager | OpenBao / Vault, External Secrets Operator | A |
| sec.kms | KMS | Key Vault keys / Managed HSM | Cloud KMS | OpenBao / Vault transit | A |

## Operations

| Capability | AWS | Azure | GCP | Self-hosted / K8s | Port. |
|---|---|---|---|---|---|
| ops.logs / metrics / traces | CloudWatch, X-Ray, Managed Prometheus/Grafana | Azure Monitor, Application Insights, Managed Prometheus/Grafana | Cloud Logging, Monitoring, Trace | OpenTelemetry Collector + Prometheus, Grafana, Loki, Tempo | P (OTel) |
| ops.ci-cd | CodePipeline / CodeBuild | Azure DevOps Pipelines | Cloud Build / Cloud Deploy | GitHub Actions, GitLab CI, Argo CD, Flux, Jenkins | A |
| ops.iac | CloudFormation, CDK | Bicep / ARM | Infrastructure Manager (Terraform) | Terraform, OpenTofu, Pulumi, Crossplane | P (Terraform/OpenTofu/Pulumi) |
| ops.registry | ECR | Azure Container Registry | Artifact Registry | Harbor, Zot | P (OCI) |
| ops.backup | AWS Backup, DB snapshots/PITR | Azure Backup, DB PITR | Backup and DR, DB PITR | Velero, pgBackRest, Barman | A |

## AI

| Capability | AWS | Azure | GCP | Self-hosted / K8s | Port. |
|---|---|---|---|---|---|
| ai.llm | Bedrock | Microsoft Foundry (formerly Azure AI Foundry; includes Azure OpenAI models) | Gemini Enterprise Agent Platform (formerly Vertex AI) | vLLM, Ollama, TGI on GPU nodes | A |
| ai.ml-platform | SageMaker AI | Azure Machine Learning / Microsoft Foundry | Gemini Enterprise Agent Platform (training, Agent Platform Endpoints) | Kubeflow, MLflow, KServe | L / P |

## Regional and sovereign providers

Use for residency designs (see the `data-residency` skill). For any target
region, start with the hyperscalers' local regions; add a provider headquartered
in the jurisdiction where one fits. This map details the EU; for other
jurisdictions name local providers only when sure they exist and offer the
service (verify).

### EU providers

EU-headquartered providers for EU-only designs. "—" means no managed product: self-run it on VMs or
Kubernetes (raise the team-fit weight) or use another provider. Product names
marked (verify) could not be confirmed against current provider pages.

| Capability | Hetzner (DE) | OVHcloud (FR) | Scaleway (FR) | STACKIT (DE) | IONOS (DE) |
|---|---|---|---|---|---|
| compute.vm | Cloud servers, dedicated servers | Public Cloud Instances, Bare Metal | Instances, Elastic Metal | Compute Engine | Compute Engine / Cloud Cubes |
| compute.containers.managed | — | — | Serverless Containers | — | — |
| compute.functions | — | — | Serverless Functions | — | — |
| compute.batch | — | — | Serverless Jobs | — | — |
| compute.paas | — | — | — | Cloud Foundry | — |
| compute.kubernetes | — (self-run k3s/Talos, or a third-party control plane) | Managed Kubernetes Service | Kubernetes Kapsule | Kubernetes Engine (SKE) | Managed Kubernetes |
| data.relational | — | Public Cloud Databases (PostgreSQL, MySQL) | Managed Database for PostgreSQL and MySQL; Serverless SQL Database | PostgreSQL Flex | DBaaS PostgreSQL, MariaDB |
| data.document | — | Public Cloud Databases (MongoDB) | Managed MongoDB | MongoDB Flex | DBaaS MongoDB |
| data.cache | — | Public Cloud Databases (Valkey) | Managed Database for Redis | Key Value Store (Valkey; Redis offering deprecated from Aug 2026) | In-Memory DB (Redis-compatible) |
| data.search | — | Public Cloud Databases (OpenSearch) | — (verify) | OpenSearch | — |
| data.object | Object Storage (S3-compatible) | Object Storage (S3-compatible) | Object Storage (S3-compatible) | Object Storage (S3-compatible) | Object Storage (S3-compatible) |
| data.vector | — (pgvector self-run) | pgvector on managed PostgreSQL (verify) | pgvector on managed PostgreSQL | pgvector on PostgreSQL Flex (verify) | pgvector on DBaaS PostgreSQL; AI Model Hub vector DB |
| msg.queue / pubsub | — | — (verify) | Queues, Topics and Events (SQS/SNS-compatible), NATS | RabbitMQ | — |
| net.lb | Load Balancers | Load Balancer | Load Balancer | Load Balancer (verify) | Managed Application / Network Load Balancer |
| net.private | Networks, Firewalls | vRack, Private Network | VPC, Private Networks | Network & Security (verify) | Private LANs (verify) |
| net.dns | DNS (verify) | DNS | Domains and DNS | DNS (verify) | Cloud DNS |
| net.cdn | — | CDN (verify) | Edge Services | — | CDN |
| sec.secrets / kms | — | Key Management Service (KMS; KMS on HSM) | Secret Manager, Key Manager | Secrets Manager, Key Management Service | — (none found) |
| ops.registry | — | Managed Private Registry | Container Registry | Container Registry | Private Container Registry |
| ops.logs / metrics | — | Logs Data Platform | Cockpit | Observability | Logging Service |
| ai.llm | — | AI Endpoints | Generative APIs, Managed Inference | AI Model Serving | AI Model Hub |

Notes:
- **Hetzner** is the cheapest per vCPU but offers infrastructure only (servers,
  load balancers, networks, volumes, object storage). Plan to self-run
  databases and Kubernetes, which usually needs a team-fit budget of 4+.
- **OVHcloud** sells SecNumCloud-qualified offerings (Hosted Private Cloud and
  an SNC cloud platform). Check which services sit inside the qualified
  perimeter before relying on it (verify).
- **Scaleway** has the broadest serverless/managed set among EU providers;
  **STACKIT** (Schwarz Group) and **IONOS** focus on managed Kubernetes,
  databases and AI inference from German data centres.
- Always confirm region availability (e.g. Paris, Amsterdam, Warsaw,
  Frankfurt, Nuremberg, Falkenstein, Helsinki) per product.

### Hyperscaler EU and sovereign offerings

Other jurisdictions: check region lists per provider, and dedicated
government or sovereign regions (e.g. AWS GovCloud (US), Azure Government,
Google Cloud dedicated/partner offerings) where the rules require them (verify).

| Provider | EU regions + controls (R1) | Sovereign offerings (R2) |
|---|---|---|
| AWS | EU regions (Frankfurt, Ireland, Paris, Stockholm, Milan, Spain); data residency controls | **AWS European Sovereign Cloud**: separate partition, first region in Brandenburg (DE), GA January 2026, EU-resident operations. Service list is smaller than commercial regions, so check each service. Sovereign Local Zones announced for Belgium, the Netherlands, Portugal (verify status) |
| Azure | EU regions; **EU Data Boundary** for Microsoft Cloud | **Microsoft Sovereign Cloud**: Sovereign Public Cloud (EU controls, Sovereign Control Panel (verify GA), External Key Management with Managed HSM), Sovereign Private Cloud (Azure Local, Microsoft 365 Local), national partner clouds Bleu (FR) and Delos Cloud (DE) |
| GCP | EU regions; **Google Cloud Data Boundary** (residency and access controls, down to country level) | **Google Cloud Dedicated** run by local partners: S3NS (Thales, FR; PREMI3NS SecNumCloud-qualified Dec 2025), T-Systems (DE, tiered offering (verify)); **Google Cloud Air-Gapped** |

Switzerland (e.g. AWS Zurich, Azure Switzerland North, GCP Zurich), the UK and
Norway are outside the EU: allowed only if the user's policy accepts them.

## Common cost traps by provider (name them as cost drivers)
- **All:** egress to the internet, cross-zone traffic, log ingestion volume,
  idle minimum capacity, managed Kubernetes control-plane fees, NAT data
  processing.
- **AWS:** NAT Gateway hourly + per-GB; public IPv4 address charges; CloudWatch
  Logs ingestion.
- **Azure:** Premium tiers needed for private networking on some PaaS services;
  Log Analytics ingestion.
- **GCP:** Cloud NAT and inter-region egress; Cloud Logging volume beyond free tier.

## Review notes (9 November 2026)
Changes since the previous review, from provider documentation and announcements:
- GCP: Vertex AI became **Gemini Enterprise Agent Platform** (April 2026);
  Vertex AI Search → Agent Search, Endpoints → Agent Platform Endpoints.
  Vector Search's new name not confirmed (verify).
- Azure: Azure AI Foundry → **Microsoft Foundry**; Cosmos DB for PostgreSQL is
  closed to new deployments (retires March 2029), replaced by Azure Database
  for PostgreSQL elastic clusters; Azure Cache for Redis retires (Enterprise
  tiers 2027, Basic/Standard/Premium September 2028) in favour of Azure Managed
  Redis; Synapse remains supported but Fabric is the path for new warehouses.
- AWS: Aurora DSQL and S3 Vectors are generally available; Timestream for
  LiveAnalytics closed to new customers (June 2025), use Timestream for InfluxDB;
  AWS European Sovereign Cloud generally available (January 2026).
- Self-hosted: ingress-nginx retired (March 2026); MinIO community edition in
  maintenance mode and distributed as source only.
- EU providers: confirmed against provider docs — STACKIT Compute Engine, Cloud
  Foundry, OpenSearch, RabbitMQ, Container Registry, Observability (Redis offering
  deprecated from August 2026 for a Valkey-based Key Value Store); IONOS MariaDB,
  In-Memory DB, Managed Application/Network Load Balancer, Cloud DNS, CDN,
  Private Container Registry, Logging Service; Scaleway Managed MongoDB, Managed
  Database for Redis, Queues, Topics and Events, NATS, Edge Services, Key Manager;
  OVHcloud KMS. Remaining (verify) marks could not be confirmed.
- Rows not listed above were checked and are unchanged.
