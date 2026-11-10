# Team fit and guardrails: exact procedure

Apply these rules mechanically and show the work, so the same team and options
always give the same result. Don't round, skip or adjust anything except as
written here. If you disagree with a result, say why next to it; never change it.

## 1. Team facts

Collect six facts. For each, note its source: the repository or org profile
("evidence", e.g. "12 Helm charts in deploy/") or the user ("self-reported").
A fact nobody gave gets the default and goes in the Assumptions line.

| Fact | Values | Default if unknown |
|---|---|---|
| operators | people who operate it after launch | builders, else 1 |
| on_call | true / false | false |
| platform_team | true / false | false |
| containers, iac, kubernetes | 0 none · 1 some · 2 solid · 3 expert (for several IaC tools, the best one counts) | 0 |
| preference | managed / balanced / control | balanced |

## 2. Budget (1-5): look it up, don't calculate

Answer four yes/no questions, then read the budget from the row that matches,
in the column for the team's preference. Don't add or round anything yourself:
the table already applies the rules.

- **Operators ≥ 2:** two or more people will operate it after launch.
- **On-call:** an on-call rotation exists, or will before launch.
- **Containers ≥ 2 and IaC ≥ 2:** both rated solid or expert.
- **Kubernetes ≥ 2 or platform team:** either one is true.

| Operators ≥ 2 | On-call | Containers ≥ 2 and IaC ≥ 2 | Kubernetes ≥ 2 or platform team | managed | balanced | control |
|---|---|---|---|---|---|---|
| no | no | no | no | 1 | 1 | 2 |
| no | no | no | yes | 2 | 2 | 3 |
| no | no | yes | no | 2 | 2 | 3 |
| no | no | yes | yes | 3 | 3 | 4 |
| no | yes | no | no | 2 | 2 | 3 |
| no | yes | no | yes | 3 | 3 | 4 |
| no | yes | yes | no | 3 | 3 | 4 |
| no | yes | yes | yes | 4 | 4 | 5 |
| yes | no | no | no | 2 | 2 | 3 |
| yes | no | no | yes | 3 | 3 | 4 |
| yes | no | yes | no | 3 | 3 | 4 |
| yes | no | yes | yes | 4 | 4 | 5 |
| yes | yes | no | no | 3 | 3 | 4 |
| yes | yes | no | yes | 4 | 4 | 5 |
| yes | yes | yes | no | 4 | 4 | 5 |
| yes | yes | yes | yes | 5 | 5 | 5 |

## 3. Option complexity

**Components are building blocks, not resources.** List each option the way
its options table does: one entry per distinct building block. Several
functions are one `serverless_functions`; three queues are one
`managed_queue`; networking, a WAF or a NAT gateway count only when the team
designs and runs them itself, not when the platform provides them. CI/CD and
other build-time parts aren't runtime components.

**Class:** give each building block the class of its product from this list
(closest class if the product isn't listed; say why):

**Weight 1**
- `cdn`: Amazon CloudFront, Azure Front Door, Cloud CDN, Cloudflare CDN
- `managed_auth`: Amazon Cognito, Entra External ID, Firebase Authentication, Auth0, Microsoft Entra ID, Clerk
- `managed_ci_cd`: AWS CodePipeline, Azure Pipelines, Cloud Build, GitHub Actions, GitLab CI
- `managed_database`: Amazon Aurora, Azure Cosmos DB, AlloyDB, IONOS DBaaS, Amazon DynamoDB, Azure Database for PostgreSQL, Cloud SQL, MongoDB Atlas
- `managed_dns`: Amazon Route 53, Azure DNS, Cloud DNS
- `managed_llm_api`: Amazon Bedrock, Azure OpenAI in Microsoft Foundry, Gemini API, Anthropic API
- `managed_observability`: Amazon CloudWatch, Azure Monitor, Google Cloud Observability, Datadog, Grafana Cloud, New Relic, Sentry
- `managed_queue`: Amazon SNS, Azure Service Bus, Google Pub/Sub, Amazon SQS, Azure Storage Queues
- `managed_registry`: Amazon ECR, Azure Container Registry, Artifact Registry
- `managed_scheduler`: Amazon EventBridge Scheduler, Cloud Scheduler
- `managed_secrets`: AWS KMS, Azure Key Vault, Google Secret Manager, AWS Secrets Manager, AWS Systems Manager Parameter Store
- `object_storage`: Amazon EFS, Azure Blob Storage, Google Cloud Storage, Cloudflare R2, Amazon S3, Hetzner Object Storage
- `paas`: AWS App Runner, Azure App Service, Google App Engine, Fly.io, AWS Elastic Beanstalk, Heroku, AWS Transfer Family, Render
- `serverless_functions`: AWS Lambda, Azure Functions, Cloud Run functions, Cloudflare Workers, Scaleway Serverless Functions
- `static_site`: AWS Amplify Hosting, Azure Static Web Apps, Firebase Hosting, Netlify

**Weight 2**
- `api_gateway_custom_auth`: Amazon API Gateway with a Lambda authorizer, Azure API Management, Apigee
- `event_bus`: Amazon EventBridge, Azure Event Grid, Eventarc
- `managed_cache`: Amazon ElastiCache, Azure Managed Redis, Memorystore for Valkey, Upstash Redis, Amazon MemoryDB
- `managed_containers`: Amazon ECS, Azure Container Apps, Google Cloud Run, Scaleway Serverless Containers, Amazon ECS on Fargate, Azure Container Instances
- `managed_ml_endpoint`: Amazon SageMaker endpoints, Microsoft Foundry managed endpoints, Agent Platform Endpoints, Cloud Run with GPUs
- `managed_search`: Amazon OpenSearch Service, Azure AI Search, Algolia, Elastic Cloud
- `managed_stream`: Amazon Kinesis Data Streams, Azure Event Hubs, Managed Service for Apache Kafka, Confluent Cloud, Amazon MSK
- `managed_warehouse`: Amazon Athena, Azure Synapse, BigQuery, Fabric Data Warehouse, Amazon Redshift, Snowflake
- `managed_workflow`: AWS Step Functions, Azure Durable Functions, Google Workflows, Temporal Cloud, Azure Logic Apps
- `private_networking`: Amazon VPC with private subnets and NAT, Azure Private Link, Private Service Connect, AWS PrivateLink
- `vm`: Amazon EC2, Azure Virtual Machines, Google Compute Engine, Hetzner Cloud servers
- `waf`: AWS WAF, Azure Web Application Firewall, Cloud Armor

**Weight 3**
- `gitops`: Argo CD, Flux
- `gpu_serving_self_managed`: Self-managed GPU serving (vLLM on VMs or Kubernetes)
- `managed_kubernetes`: Amazon EKS, Azure Kubernetes Service (AKS), GKE Autopilot, IONOS Managed Kubernetes, EKS Auto Mode, Google Kubernetes Engine (GKE), OVHcloud Managed Kubernetes Service, Scaleway Kubernetes Kapsule
- `multiple_db_engines`
- `self_run_broker`: Self-run Kafka, Self-run RabbitMQ, Strimzi (Kafka on Kubernetes)
- `stream_processing`: Amazon Managed Service for Apache Flink, Azure Stream Analytics, Google Dataflow, Self-run Apache Flink, Self-run Apache Spark
- `vpn_hybrid_networking`: AWS Direct Connect, Azure ExpressRoute, Cloud Interconnect, AWS Site-to-Site VPN

**Weight 4**
- `custom_autoscaling`: Karpenter, KEDA
- `multi_region_active_active`: Multi-region active-active database
- `own_observability_stack`: Self-run Prometheus, Grafana and Loki
- `self_hosted_database`: Self-hosted Keycloak, Self-hosted MongoDB, Self-hosted MySQL, Self-hosted OpenSearch or Elasticsearch, Self-hosted Oracle, Self-hosted PostgreSQL
- `service_mesh`: Istio, Linkerd

**Weight 5**
- `multi_cloud_active_active`: Active-active across two clouds
- `on_prem_cloud_federation`: On-prem and cloud federation
- `self_run_kubernetes_control_plane`: Self-managed Kubernetes (kubeadm, k3s, RKE)

**Complexity** = the highest weight in the option, **+1** if it has more than 8
runtime building blocks.

**Verdict:** look it up; don't work it out.

| Complexity ↓ / Budget → | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| 1 | Within | Within | Within | Within | Within |
| 2 | At limit | Within | Within | Within | Within |
| 3 | Exceeds | At limit | Within | Within | Within |
| 4 | Exceeds | Exceeds | At limit | Within | Within |
| 5 | Exceeds | Exceeds | Exceeds | At limit | Within |
| 6 | Exceeds | Exceeds | Exceeds | Exceeds | At limit |

## 4. Output (paste this block, filled in, every time)

```markdown
**Operational complexity budget: 2 / 5**
Reasoning: operators = 2 (yes); on_call = false (no); containers = 2 (solid), IaC = 1 (some) (no); kubernetes = 0 (none), platform_team = false (no); preference = managed → row yes-no-no-no, managed → 2.
Evidence: 1 of 5 factors backed (containers ← 6 Dockerfiles in services/), the rest self-reported.
Assumptions: platform_team not given; assumed false.

| Option | Complexity | Basis | Verdict |
|---|---|---|---|
| A. Serverless | 1 | highest: managed_database (1), 5 building blocks | Within |
| B. Managed containers | 2 | highest: managed_containers (2), 6 building blocks | Within |
| C. Kubernetes + GitOps | 3 | highest: managed_kubernetes (3), 7 building blocks | At limit |
```

Leave out the Evidence line's backed list when nothing is backed ("Evidence:
none; all 5 factors are self-reported."), and the Assumptions line when nothing
was assumed. When most factors are self-reported and a verdict decides between
options, say so and name the fact that would change it.

**Recommending:** recommend a **Within** option whenever one meets the stated
requirements. An **At limit** option is never the recommendation in that case,
even if the user or a CTO asks for it: offer it as the conditional alternative,
with its mitigation and what must be true first (skills, people, on-call).
Recommend an At limit option only when no Within option meets a stated
requirement, and name that requirement. Never recommend an Exceeds option.

**One verdict, one word.** Everywhere else (summary, recommendation, options,
ADRs, decision brief) use the exact verdict word from this table for each
option: never "exceeds" for an option the table says is At limit, and never a
softer or stronger paraphrase.

**Check before answering:** look the budget up again from the four answers and
the preference, recount each option's building blocks, look each verdict up
again, and search your answer for every place an option's verdict is
mentioned. If anything differs from the table, fix the text, not the table.

## 5. Org guardrails (only with an org profile or stated platform rules)

Rules come from `.cloud-architect/org.yaml` or the conversation: allowed
`clouds`, `regions`, `approved_services` (product names), `approved_classes`,
`forbidden_classes`. Compare names ignoring case, `-` and `_`. For each
component of each option (provider and region per option unless the component
says otherwise):

1. **Cloud:** with an allowed list, the provider must be on it; no provider
   given counts as an exception.
2. **Region:** with an allowed list, the region must be on it, except edge
   services with no region (CDN, DNS); no region given counts as an exception.
3. **Forbidden class:** a component of a forbidden class is an exception.
4. **Approved:** with an approved list, the product or the class must be on it
   (a forbidden component is reported once, under rule 3).

A component with any failing rule needs one exception. Output:

```markdown
**Org guardrails: Acme**

| Option | Exceptions | Verdict |
|---|---|---|
| A. Managed containers | 0 | fits guardrails |
| B. Kubernetes | 2 | needs 2 exception ADRs |

| Option | Component | Product | Rule | Why it needs an exception |
|---|---|---|---|---|
| B. Kubernetes | Cluster | EKS | approved services | EKS is not on the approved list |
| B. Kubernetes | Queue | SQS | region | us-east-1 is not an approved region |
```

Each exception needs an exception ADR signed off by the org owner, or a change
to the design (see `design` → `references/guardrails.md`).
