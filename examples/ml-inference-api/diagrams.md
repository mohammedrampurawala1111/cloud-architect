# Diagrams: ML inference API (recommended option A)

## 1. System context (neutral)
```mermaid
flowchart LR
    U["API customer systems"] -->|"classify document, HTTPS"| S["Document classification API"]
    ML["ML engineers"] -->|"publish model versions"| S
    S -->|"label and confidence"| U
```

## 2. System context (mapped to GCP)
```mermaid
flowchart LR
    U["API customer systems"] -->|"HTTPS, API key"| S["Classification API on GCP us-central1"]
    ML["ML engineers"] -->|"push weights and image"| S
    S -->|"label and confidence"| U
```

## 3. Containers (neutral)
```mermaid
flowchart TB
    C["API customers"] --> E["Edge: load balancer and WAF"]
    E --> F["API facade: auth, quota, validation, load shedding"]
    F --> K["Key and quota store"]
    F --> SEC["Secret store"]
    F --> M["Managed GPU model endpoint: inference server"]
    ART["Object storage: versioned model weights"] --> M
    REG["Container registry"] --> F
    REG --> M
    F -.-> OBS["Metrics, logs, traces"]
    M -.-> OBS
```

## 4. Containers (mapped to GCP)
```mermaid
flowchart TB
    C["API customers"] --> E["Cloud Load Balancing + Cloud Armor"]
    E --> F["Cloud Run: API facade"]
    F --> K["Firestore: keys and quotas"]
    F --> SEC["Secret Manager"]
    F -->|"private access"| M["Vertex AI endpoint: vLLM on GPU replicas"]
    ART["Cloud Storage: model weights"] --> M
    REG["Artifact Registry"] --> F
    REG --> M
    F -.-> OBS["Cloud Monitoring and Logging"]
    M -.-> OBS
```

## 5. Request flow
```mermaid
sequenceDiagram
    participant C as Customer
    participant E as Edge and WAF
    participant F as API facade
    participant M as Model endpoint
    C->>E: POST /v1/classify with API key
    E->>F: forward, after rate limit check
    F->>F: check key (cached), quota, token count
    alt over quota or too many in flight
        F-->>C: 429 with Retry-After
    else accepted
        F->>M: document text, 1 s timeout budget
        M-->>F: label and confidence
        F-->>C: 200 label, confidence, model version
    end
```
