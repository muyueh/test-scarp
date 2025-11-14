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
    commit id: "Flat dataset update (13:42)"
    commit id: "Flat dataset update (14:02)"
    branch codex/update-github-actions-for-normalized-array
    checkout codex/update-github-actions-for-normalized-array
    commit id: "Normalize dataset workflow"
    merge main id: "Sync workflow branch"
    checkout main
    merge codex/update-github-actions-for-normalized-array id: "Merge PR #4"
    branch work
    checkout work
    commit id: "Update breaking news dataset"
    commit id: "Configurable request timeout"
```

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Configuring: CLI invoked
    Idle --> Scheduled: Cron triggers workflow
    Scheduled --> Preparing: Checkout & install deps
    Preparing --> Configuring: Parse args & validate timeout
    Configuring --> Fetching: Fetch requested pages with timeout
    Fetching --> Normalising: Build headline array
    Fetching --> Failing: Timeout or HTTP error
    Normalising --> Persisting: Write JSON output
    Persisting --> Validating: Load & sanity check
    Validating --> Idle
    Failing --> Idle
```

```mermaid
sequenceDiagram
    participant User
    participant Actions as GitHub Actions
    participant CLI
    participant AutoCommit as Auto Commit Action
    participant UDN as UDN API
    User->>CLI: python udn_crawler.py --pages N --delay D --timeout T --output file
    CLI->>CLI: Validate args & timeout constraint
    CLI->>UDN: GET /api/more?page=1 (timeout=T)
    UDN-->>CLI: JSON headlines
    loop Remaining pages
        CLI->>UDN: GET /api/more?page=pageNumber (timeout=T)
        UDN-->>CLI: JSON payload
    end
    CLI-->>User: Normalized headline list
    Actions->>Actions: Checkout & setup python
    Actions->>CLI: python udn_crawler.py --pages 3 --delay 0 --timeout 10 --output udn_breaking_news.json
    CLI-->>Actions: Normalized headline list
    Actions->>AutoCommit: Stage udn_breaking_news.json
    AutoCommit->>GitHub: Push updated dataset
```

```mermaid
graph TD
    User[User CLI] --> Parser[Argument parser]
    Parser --> Timeout[Timeout validator]
    Timeout --> Crawler[crawl_breaking_news]
    Crawler --> Requests[requests Session]
    Requests --> API[UDN API]
    Crawler --> Normaliser[Normaliser]
    Normaliser --> Validator[Structure validator]
    Validator --> Output[udn_breaking_news.json]
    Actions[GitHub Actions] --> Setup[setup-python]
    Setup --> Installer[pip install requirements]
    Installer --> Parser
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
    a -- Yes --> t{"Timeout > 0?"}
    t -- No --> t0[Raise ValueError]
    t -- Yes --> b{"Workflow run?"}
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
        U1[Run CLI with pages/delay/timeout]
        U2[Review Flat View dashboard]
    end
    subgraph Frontend
        F1[Terminal / CLI]
        F2[GitHub UI]
        F3[Flat Viewer]
    end
    subgraph Backend
        B1[Argument parser validates timeout]
        B2[crawl_breaking_news]
        B3[fetch_page (requests with timeout)]
        B4[Normaliser & validator]
        B5[GitHub Actions workflow]
        B6[Auto commit action]
    end

    U1 --> F1 --> B1 --> B2 --> B3 --> B2
    B2 --> B4 --> F1 --> U1
    F2 --> B5 --> B1
    B5 --> B4 --> B6 --> F2
    B6 --> F3 --> U2
```

A lightweight utility for downloading the latest breaking news headlines from UDN.

## Features

- Normalises responses from the official UDN breaking news endpoint.
- Supports configurable pagination and request throttling.
- Allows configuring HTTP timeouts to better handle slow responses.
- Writes prettified JSON to disk for downstream processing.
- Provides a scheduled GitHub Actions workflow with the permissions required for Flat commits.

## Usage

```bash
python udn_crawler.py --pages 1 --delay 0 --timeout 10 --output /tmp/udn.json
```

## Development

- Requires Python 3.10+.
- Install dependencies with `pip install -r requirements.txt` if you maintain a separate environment.
- Scheduled runs need repository contents write access enabled for the Flat workflow token.
