# Diagrams

Each view appears first in neutral terms, then mapped to the recommended Option A on AWS `ca-central-1`.

## 1. System context

### Neutral

```mermaid
flowchart LR
  D["Dispatcher (customer company)"] --> SYS["Technician scheduling platform"]
  T["Technician (customer company)"] --> SYS
  A["Customer admin"] --> SYS
  SYS --> M["Email recipients"]
  SYS --> G["Geocoding service"]
  O["Our staff (support, engineering)"] --> SYS
```

### Mapped (AWS)

```mermaid
flowchart LR
  D["Dispatcher (customer company)"] --> SYS["Scheduling platform on AWS ca-central-1"]
  T["Technician (customer company)"] --> SYS
  A["Customer admin"] --> SYS
  SYS -->|"SES"| M["Email recipients"]
  SYS -->|"Amazon Location Service"| G["Geocoding"]
  O["Our staff"] -->|"SSO + MFA, least privilege"| SYS
```

## 2. Container view

### Neutral

```mermaid
flowchart TB
  subgraph Clients
    B["Browser (SPA, also on phones)"]
  end
  subgraph Platform
    ST["Static site + CDN"]
    GW["HTTP API gateway (JWT check, throttling)"]
    API["API function: modular monolith"]
    WK["Worker function: reports and emails"]
    SCH["Scheduler (hourly)"]
    Q["Job queue + dead-letter queue"]
    DB[("Relational database, Multi-AZ")]
    OBJ[("Object storage")]
    AUTH["Managed auth"]
    MAIL["Email service"]
    SEC["Secrets store"]
  end
  B --> ST
  B --> AUTH
  B --> GW
  GW --> API
  API --> DB
  API --> Q
  SCH --> Q
  Q --> WK
  WK --> DB
  WK --> OBJ
  WK --> MAIL
  API --> SEC
```

### Mapped (AWS)

```mermaid
flowchart TB
  subgraph Clients
    B["Browser (React SPA)"]
  end
  subgraph AWS_ca_central_1["AWS ca-central-1 (2 AZs)"]
    ST["S3 + CloudFront (static assets only)"]
    GW["API Gateway HTTP API (JWT authorizer)"]
    API["Lambda: API (Node.js monolith)"]
    WK["Lambda: worker"]
    SCH["EventBridge Scheduler (hourly)"]
    Q["SQS + DLQ"]
    DB[("RDS PostgreSQL 16 Multi-AZ")]
    OBJ[("S3: reports, exports")]
    AUTH["Cognito user pool"]
    MAIL["SES"]
    SEC["Secrets Manager"]
  end
  B --> ST
  B --> AUTH
  B --> GW
  GW --> API
  API --> DB
  API --> Q
  SCH --> Q
  Q --> WK
  WK --> DB
  WK --> OBJ
  WK --> MAIL
  API --> SEC
```

## 3. Nightly report flow

```mermaid
sequenceDiagram
  participant S as Scheduler (hourly)
  participant P as Planner (worker function)
  participant Q as Job queue
  participant W as Worker function
  participant DB as Database
  participant O as Object storage
  participant M as Email service
  S->>P: trigger at top of each hour
  P->>DB: companies whose local time is 01:00 and no report yet today
  P->>Q: one message per company (idempotency key: company + date)
  Q->>W: deliver job
  W->>DB: read-only queries for that company
  W->>O: write report file
  W->>Q: enqueue email job with link
  Q->>W: email job
  W->>M: send message with time-limited link
```

## 4. Deployment view

```mermaid
flowchart TB
  subgraph PROD["AWS account: production"]
    subgraph R1["ca-central-1"]
      subgraph AZA["AZ a"]
        FA["Functions (VPC subnet a)"]
        DBP[("Database primary")]
        NA["NAT or endpoints a"]
      end
      subgraph AZB["AZ b"]
        FB["Functions (VPC subnet b)"]
        DBS[("Database standby")]
        NB["NAT or endpoints b"]
      end
      REG["Regional services: gateway, queue, object storage, user pool, email"]
    end
    subgraph R2["ca-west-1"]
      BK[("Backup copies")]
    end
  end
  subgraph NONPROD["AWS account: non-production"]
    DEV["Dev and staging: same shape, single AZ database, synthetic data only"]
  end
  DBP -->|"synchronous"| DBS
  DBP -->|"daily backup copy"| BK
  CI["Hosted CI/CD"] -->|"deploy role, reviewed PRs"| PROD
  CI --> NONPROD
```

Two NAT gateways or two sets of interface endpoints (one per AZ) avoid a single NAT being a single point of failure on the API path.
