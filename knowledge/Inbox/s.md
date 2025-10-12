---
created: 2025-10-07 14:37
tags: [accuracy-evaluation, data-pipeline, data-preprocessing, data-science, data-visualization,
  jupyter-notebook, machine-learning, model-training]
quality_score: 0.2
ai_processed: '2025-10-12T12:54:08.657989'
---

``` mermaid
flowchart LR
  subgraph P[prepare]
  end
  subgraph T[train]
  end
  subgraph E[evaluate]
  end

  prep_py[prepare.py]:::plain --> P
  raw[(data/raw/)]:::file --> P

  P --> train_csv[(train.csv)]:::file
  P --> test_csv[(test.csv)]:::file
  train_py[train.py]:::plain --> T
  train_csv --> T
  test_csv --> T

  T --> model[(model.joblib)]:::file
  model --> E
  T --> E
  eval_py[evaluate.py]:::plain --> E
  E --> acc[(accuracy.json)]:::file

  classDef file fill:#fff,stroke:#999,stroke-width:1px;
  classDef plain stroke:none,fill:none;

```
