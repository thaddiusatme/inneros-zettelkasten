# InnerOS Architecture

## System Overview

```mermaid
flowchart LR
  subgraph CLI
    A[weekly_review_cli] --> B[WorkflowManager]
    C[youtube_cli] --> B
  end
  subgraph Core
    B --> D[AI Engines]
    B --> E[Safety Backup]
    B --> F[Link Suggestions]
  end
  subgraph Storage
    G[knowledge vault md files]
    H[.automation metrics json]
  end
  subgraph Web
    I[Flask app.py] --> J[Metrics API]
  end
  D --> H
  E --> H
  F --> G
  B --> G
  J --> H
```

## Module Map

- development/src/ai — core analytics and AI helpers
- development/src/cli — user facing commands
- development/src/utils — safety and directory helpers
- development/src/monitoring — metrics and health
- web_ui — Flask app and metrics view

## Key Flows

- Weekly review: CLI reads vault, computes metrics, writes JSON; optional UI reads metrics
- Inbox capture: automation script normalizes files, updates vault, records activity
