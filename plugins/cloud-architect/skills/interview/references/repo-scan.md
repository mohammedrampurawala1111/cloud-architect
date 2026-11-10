# Repository scan (read-only)

How to find what an existing codebase is built from, with Claude Code's Glob,
Grep and Read tools only. Two turns: **all Glob calls in parallel in one turn**,
then **all manifests you found in parallel in the next** (skip lockfiles and
generated files). Skip dependency, build and cache
folders (`node_modules`, `vendor`, `.venv`, `venv`, `dist`, `build`, `target`,
`.terraform`, `.next`, `__pycache__`) and anything over ~256 KB.

## 1. Find

| Glob | Tells you |
|---|---|
| `**/package.json`, `**/requirements*.txt`, `**/pyproject.toml`, `**/go.mod`, `**/pom.xml`, `**/build.gradle*`, `**/*.csproj`, `**/Gemfile`, `**/composer.json`, `**/Cargo.toml` | Languages and dependencies (read them) |
| `**/schema.prisma`, `**/migrations/**`, `**/db/migrate/**`, `**/alembic/**`, `**/V*__*.sql` | Database and migration tool |
| `**/openapi*.{yaml,yml,json}`, `**/swagger*`, `**/*.proto`, `**/*.graphql` | API contracts |
| `**/Dockerfile*`, `**/compose*.y*ml`, `**/docker-compose*.y*ml` | Containers (count them) |
| `**/Chart.yaml`, `**/kustomization.y*ml`, YAML files with `apiVersion:` and `kind:` | Kubernetes (count them) |
| `**/*.tf`, `**/*.bicep`, `**/Pulumi.yaml`, `**/cdk.json`, `**/serverless.y*ml`, `**/template.yaml` | IaC (for Terraform, Grep `resource "` to list resource types) |
| `.github/workflows/*`, `.gitlab-ci.yml`, `azure-pipelines.yml`, `Jenkinsfile`, `bitbucket-pipelines.yml` | CI/CD tool |
| `**/runbook*`, `**/RUNBOOK*`, `CODEOWNERS`, docs mentioning PagerDuty or Opsgenie | On-call, ownership |

## 2. Read the dependencies by role

From the manifests, sort dependencies into roles (examples, not a full list):

| Role | Typical dependencies |
|---|---|
| Web framework | express, fastify, @nestjs/core, next, django, flask, fastapi, spring-boot-starter-web, gin, echo, ASP.NET Core, rails, laravel |
| Data store | pg, postgres, psycopg, pgx, npgsql, mysql2, mongodb, mongoose, @aws-sdk/client-dynamodb, @azure/cosmos, oracledb, ojdbc, elasticsearch |
| ORM / migrations | prisma, typeorm, sequelize, drizzle-orm, knex, sqlalchemy, alembic, hibernate, JPA, Entity Framework, gorm |
| Cache | redis, ioredis, go-redis, memcached |
| Messaging / jobs | @aws-sdk/client-sqs, -sns, -eventbridge, -kinesis, kafkajs, confluent-kafka, spring-kafka, amqplib, pika, bullmq, celery, @google-cloud/pubsub, @azure/service-bus, nats |
| Object storage | @aws-sdk/client-s3, @google-cloud/storage, @azure/storage-blob |
| Cloud | @aws-sdk/*, boto3, aws-sdk-go → AWS · @azure/*, azure-* → Azure · @google-cloud/*, google-cloud-* → GCP |
| Auth | passport, next-auth, jose, auth0, Clerk, Keycloak, Spring Security, Cognito clients |
| Integrations | SES, SendGrid, nodemailer, Postmark, Twilio, Stripe, Slack |
| Observability | @opentelemetry/*, dd-trace, prom-client, Sentry, New Relic, pino, winston |

## 3. Report

Write a short inventory with the file that shows each item, then confirm the
parts that matter by reading the code (entry points, data access, async work,
auth). Detection by file names and dependencies can miss unusual stacks: say
what you couldn't find.

**Team-profile evidence** for team fit, as plain text (no quotes, braces or
colons): containers ← "6 Dockerfiles in the repo"; kubernetes ← "4 Kubernetes
manifests and 1 Helm chart in the repo"; iac ← "23 Terraform files in the repo".
Counts are evidence; a guess ("they probably use Kubernetes") is not.
