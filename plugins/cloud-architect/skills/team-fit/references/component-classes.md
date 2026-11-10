# Component classes and complexity weights

Use these `class` names when scoring options with `scoring.md`. If nothing
fits, give an explicit weight (1-5) and say why in the design.

| Weight | Class | Typical products |
|---|---|---|
| 1 | `serverless_functions` | Lambda, Azure Functions, Cloud Run functions |
| 1 | `paas` | App Service, Elastic Beanstalk, App Engine |
| 1 | `managed_database` | RDS/Aurora, Azure Database for PostgreSQL, Cloud SQL |
| 1 | `object_storage` | S3, Blob Storage, Cloud Storage, any S3-compatible store |
| 1 | `managed_queue` | SQS, Service Bus, Cloud Tasks / Pub/Sub |
| 1 | `managed_auth` | Cognito, Entra External ID, Identity Platform, SaaS IdP |
| 1 | `cdn` | CloudFront, Front Door, Cloud CDN |
| 1 | `static_site` | S3 + CDN, Static Web Apps, Firebase Hosting |
| 1 | `managed_secrets` | Secrets Manager, Key Vault, Secret Manager |
| 1 | `managed_scheduler` | EventBridge Scheduler, Cloud Scheduler |
| 1 | `managed_dns` | Route 53, Azure DNS, Cloud DNS |
| 1 | `managed_registry` | ECR, ACR, Artifact Registry |
| 1 | `managed_observability` | CloudWatch, Azure Monitor, Cloud Logging/Monitoring, SaaS APM |
| 1 | `managed_ci_cd` | GitHub Actions, GitLab CI, Azure Pipelines (mark `runtime: false`) |
| 1 | `managed_llm_api` | Bedrock, Microsoft Foundry models, Gemini Enterprise Agent Platform models |
| 2 | `managed_containers` | ECS on Fargate, Container Apps, Cloud Run |
| 2 | `managed_cache` | ElastiCache, Azure Managed Redis, Memorystore |
| 2 | `api_gateway_custom_auth` | API Gateway / APIM / Apigee with custom authorisers |
| 2 | `managed_search` | OpenSearch Service, Azure AI Search |
| 2 | `event_bus` | EventBridge, Event Grid, Eventarc |
| 2 | `managed_workflow` | Step Functions, Durable Functions, Workflows |
| 2 | `managed_warehouse` | BigQuery, Redshift Serverless, Fabric Warehouse |
| 2 | `managed_stream` | Kinesis, Event Hubs, Pub/Sub, MSK Serverless (consumption only) |
| 2 | `managed_ml_endpoint` | SageMaker AI endpoints, Azure ML online endpoints, Agent Platform Endpoints (GCP) |
| 2 | `vm` | A small number of VMs with managed images and patching |
| 2 | `waf` | AWS WAF, Front Door WAF, Cloud Armor |
| 2 | `private_networking` | VPC/VNet design, private endpoints, NAT |
| 3 | `managed_kubernetes` | EKS, AKS, GKE, managed K8s on EU providers |
| 3 | `self_run_broker` | RabbitMQ, Kafka (Strimzi), NATS run by the team |
| 3 | `stream_processing` | Flink, Kafka Streams, Spark Structured Streaming |
| 3 | `multiple_db_engines` | Two or more different database engines to operate |
| 3 | `vpn_hybrid_networking` | Site-to-site VPN, Direct Connect / ExpressRoute / Interconnect |
| 3 | `gpu_serving_self_managed` | vLLM / TGI / Triton on GPU nodes the team runs |
| 3 | `gitops` | Argo CD / Flux operated by the team |
| 4 | `service_mesh` | Istio, Linkerd, Cilium service mesh |
| 4 | `self_hosted_database` | PostgreSQL/MySQL/MongoDB run by the team (incl. operators) |
| 4 | `multi_region_active_active` | Active-active across regions |
| 4 | `custom_autoscaling` | Custom scalers, KEDA tuning, bespoke capacity logic |
| 4 | `own_observability_stack` | Self-run Prometheus/Grafana/Loki/Tempo |
| 5 | `multi_cloud_active_active` | Active-active across providers |
| 5 | `self_run_kubernetes_control_plane` | kubeadm, k3s, RKE2, Talos clusters the team runs |
| 5 | `on_prem_cloud_federation` | On-prem + cloud federation |

Weights 1-5 follow the table in the `team-fit` skill. Classes beyond those examples
(e.g. `vm`, `waf`, `gitops`) were placed at the weight of their closest example.
