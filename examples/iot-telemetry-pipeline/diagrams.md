# Diagrams

Option A (recommended). Neutral views first, then the AWS-mapped views.

## C4 context (neutral)
```mermaid
flowchart TB
  dev["Devices (20,000)"]
  ops["Operations staff and customers"]
  fin["Finance team"]
  sys["Telemetry pipeline"]
  pager["Alert delivery (email, SMS, on-call tool)"]
  dev -->|"JSON reading every 10 s"| sys
  sys -->|"Threshold alerts within 5 s"| pager
  pager --> ops
  ops -->|"Dashboards, 13 months"| sys
  sys -->|"Daily export file"| fin
```

## C4 container view (neutral)
```mermaid
flowchart LR
  dev["Devices"] --> broker["Managed device broker"]
  broker --> stream["Stream"]
  stream --> alerts["Alert evaluator"]
  alerts <--> state["Config and alert state"]
  alerts --> notify["Notifications"]
  stream --> archive["Archive delivery"]
  archive --> lake["Object storage (Parquet)"]
  lake --> sql["SQL query engine"]
  sched["Scheduler and workflow"] --> sql
  sql --> rollups["Rollup tables"]
  rollups --> lake
  sql --> dash["Dashboards"]
  sql --> export["Export bucket"]
  export --> fin["Finance team"]
```

## C4 context (AWS-mapped)
```mermaid
flowchart TB
  dev["Devices (MQTT over TLS, X.509)"]
  ops["Staff and customers (SSO)"]
  fin["Finance team"]
  sys["Telemetry pipeline in AWS Sydney ap-southeast-2"]
  pager["SNS to email, SMS, on-call tool"]
  dev -->|"JSON every 10 s"| sys
  sys --> pager
  ops -->|"Managed Grafana"| sys
  sys -->|"Daily CSV in S3 export bucket"| fin
```

## C4 container view (AWS-mapped)
```mermaid
flowchart LR
  dev["Devices"] --> iot["AWS IoT Core (Basic Ingest) and rule"]
  iot --> kds["Kinesis Data Streams"]
  kds -->|"enhanced fan-out"| lam["Lambda alert evaluator"]
  lam <--> ddb["DynamoDB: thresholds and alert state"]
  lam --> sns["SNS"]
  kds --> fh["Firehose (Parquet)"]
  fh --> s3["S3 history bucket"]
  s3 --> ath["Athena"]
  evb["EventBridge Scheduler"] --> sf["Step Functions"]
  sf --> ath
  ath --> s3
  ath --> gra["Managed Grafana"]
  sf --> exp["S3 export bucket"]
  exp --> fin["Finance team"]
  s3 -->|"replication"| s3dr["S3 backup bucket, Melbourne ap-southeast-4"]
```

## Alert flow (sequence of steps)
```mermaid
flowchart LR
  a["Device publishes reading"] -->|"under 0.3 s"| b["IoT rule to Kinesis"]
  b -->|"under 1 s"| c["Lambda reads batch"]
  c --> d["Evaluate thresholds, read state"]
  d -->|"breach and not already open"| e["Write alert state, publish to SNS"]
  e -->|"under 1 s"| f["Delivered to provider"]
```

Latency budget (estimate): publish and rule about 0.3 s, stream and consumer push about 0.5-1 s, evaluation and state write about 0.2 s, SNS handoff about 0.2 s. Expected total about 1.5-2.5 s; the target is p99 under 5 s.
