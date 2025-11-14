# test-scarp

```mermaid
gitGraph
    commit id: "Initial commit"
    branch main
    checkout main
    commit id: "Grant Flat workflow push permissions"
    branch codex/update-pagination-for-udn_crawler
    checkout codex/update-pagination-for-udn_crawler
    commit id: "Add crawler & diagrams"
    checkout main
    merge codex/update-pagination-for-udn_crawler id: "Merge PR #2"
    checkout codex/update-pagination-for-udn_crawler
    merge main id: "Sync main into feature"
    checkout main
    merge codex/update-pagination-for-udn_crawler id: "Merge PR #3"
    branch work
    checkout work
    commit id: "Flat dataset update"
    commit id: "Normalize dataset workflow"
```

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Requesting: CLI invoked
    Idle --> Scheduled: Cron triggers workflow
    Scheduled --> Preparing: Checkout & install deps
    Preparing --> Fetching: Call UDN API
    Requesting --> Fetching: Fetch requested pages
    Fetching --> Normalising: Build headline array
    Normalising --> Persisting: Write JSON output
    Persisting --> Validating: Load & sanity check
    Validating --> Idle
```

```mermaid
sequenceDiagram
    participant User
    participant Actions as GitHub Actions
    participant CLI
    participant AutoCommit as Auto Commit Action
    participant UDN as UDN API
    User->>CLI: python udn_crawler.py --pages N --output file
    CLI->>UDN: GET /api/more?page=1
    UDN-->>CLI: JSON headlines
    loop Remaining pages
        CLI->>UDN: GET /api/more?page=pageNumber
        UDN-->>CLI: JSON payload
    end
    CLI-->>User: Normalized headline list
    Actions->>Actions: Checkout & setup python
    Actions->>CLI: python udn_crawler.py --pages 3 --output udn_breaking_news.json
    CLI-->>Actions: Normalized headline list
    Actions->>AutoCommit: Stage udn_breaking_news.json
    AutoCommit->>GitHub: Push updated dataset
```

```mermaid
graph TD
    User[User CLI] --> Crawler[crawl_breaking_news]
    Crawler --> Requests[requests Session]
    Requests --> API[UDN API]
    Crawler --> Normaliser[Normaliser]
    Normaliser --> Validator[Structure validator]
    Validator --> Output[udn_breaking_news.json]
    Actions[GitHub Actions] --> Setup[setup-python]
    Setup --> Installer[pip install requirements]
    Installer --> Crawler
    Actions --> AutoCommit[git-auto-commit-action]
    AutoCommit --> Repo[Repository]
    Repo --> Flat[Flat View]
    Output -.-> Flat
```

```mermaid
decision-tree
    root((Start))
    root --> a{"Pages > 0?"}
    a -- No --> a0[Raise ValueError]
    a -- Yes --> b{"Workflow run?"}
    b -- Yes --> c[Install dependencies]
    c --> d{"CLI succeeded?"}
    b -- No --> e{"Delay > 0?"}
    e -- Yes --> f[Sleep between requests]
    e -- No --> g[Fetch pages immediately]
    d -- No --> h[Fail job]
    d -- Yes --> i[Normalise & write JSON]
    g --> i
    i --> j{"Validation passes?"}
    j -- Yes --> k[Commit updated dataset]
    j -- No --> h
```

```mermaid
flowchart LR
    subgraph User
        U1[Run CLI manually]
        U2[Review Flat View dashboard]
    end
    subgraph Frontend
        F1[Terminal / CLI]
        F2[GitHub UI]
        F3[Flat Viewer]
    end
    subgraph Backend
        B1[crawl_breaking_news]
        B2[fetch_page]
        B3[Normaliser & validator]
        B4[GitHub Actions workflow]
        B5[Auto commit action]
    end

    U1 --> F1 --> B1 --> B2 --> B1
    B1 --> B3 --> F1 --> U1
    F2 --> B4 --> B1
    B4 --> B3 --> B5 --> F2
    B5 --> F3 --> U2
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
