# test-scarp

```mermaid
gitGraph
    branch work
    checkout work
    commit id: "Initial commit"
    commit id: "UDN crawler update"
    commit id: "Flat workflow permissions"
```

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Requesting: CLI invoked
    Idle --> Scheduled: Flat workflow triggers
    Scheduled --> Syncing: Fetch latest headlines
    Requesting --> Parsing: Response received
    Syncing --> Parsing: Response received
    Parsing --> Persisting: Writing JSON output
    Persisting --> Idle
```

```mermaid
sequenceDiagram
    participant User
    participant Actions as GitHub Actions
    participant CLI
    participant UDN as UDN API
    User->>CLI: python udn_crawler.py --pages N
    CLI->>UDN: GET /api/more?page=1
    UDN-->>CLI: JSON headlines
    loop Additional pages
        CLI->>UDN: GET /api/more?page=pageNumber
        UDN-->>CLI: JSON page payload
    end
    CLI-->>User: Normalised headline list
    Actions->>UDN: GET /api/more?page=1
    UDN-->>Actions: JSON headlines
    Actions-->>Actions: Commit data with contents: write
```

```mermaid
graph TD
    A[User] --> B[CLI]
    B --> C[Requests Session]
    C --> D[UDN API]
    B --> E[JSON Serializer]
    E --> F[File Output]
    G[GitHub Actions] --> H[Flat Action]
    H --> D
    H --> I[Repository Commit]
```

```mermaid
decision-tree
    root((Start))
    root --> a{"Pages > 0?"}
    a -- No --> a0[Raise ValueError]
    a -- Yes --> b{"Triggered by Actions?"}
    b -- Yes --> e[Ensure contents: write permission]
    b -- No --> f{"Delay > 0?"}
    e --> f
    f -- No --> c[Fetch pages without waiting]
    f -- Yes --> d[Sleep between requests]
```

```mermaid
flowchart LR
    subgraph User
        U1[Run CLI]
    end
    subgraph Frontend
        F1[Terminal]
        F2[GitHub UI]
    end
    subgraph Backend
        B1[udn_crawler.crawl_breaking_news]
        B2[fetch_page]
        B3[Flat workflow]
    end

    U1 --> F1 --> B1 --> B2 --> B1
    B1 --> F1 --> U1
    F2 --> B3 --> B2
    B3 --> F2
```

A lightweight utility for downloading the latest breaking news headlines from UDN.

## Features

- Normalises responses from the official UDN breaking news endpoint.
- Supports configurable pagination and request throttling.
- Writes prettified JSON to disk for downstream processing.
- Provides a scheduled GitHub Actions workflow with the permissions required for Flat commits.

## Usage

```bash
python udn_crawler.py --pages 1 --delay 0 --output /tmp/udn.json
```

## Development

- Requires Python 3.10+.
- Install dependencies with `pip install -r requirements.txt` if you maintain a separate environment.
- Scheduled runs need repository contents write access enabled for the Flat workflow token.
