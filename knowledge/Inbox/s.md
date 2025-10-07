
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
