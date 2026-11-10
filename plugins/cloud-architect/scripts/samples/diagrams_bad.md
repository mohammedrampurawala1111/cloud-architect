# Sample diagrams (each block has a deliberate error)

```mermaid
flowchart LR
  api[API service (Cloud Run)]
  db[(Primary DB]
  api --> db
```

```mermaid
flowchart sideways
  a --> b
```

```mermaid
flowhcart LR
  a --> b
```

```mermaid
flowchart TB
  subgraph vpc[Private network]
    end[Finish]
```

```mermaid
sequenceDiagram
  A->>B: hello
  alt ok
    B-->>A: hi
```
