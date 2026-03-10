# Parent Entity Classification

![Model Workflow](model-workflow.png)

Three-stage cascade: Rule-Based, LLM API, XLM-RoBERTa. Each stage runs only when the previous cannot classify with confidence.

## Overview

Classification of parent entities in vertical ownership chains across global markets. ~1.4M entities from 120+ countries, four categories:

- **Individual** – Personal names
- **Company** – Corporate entities (Inc., Ltd., GMBH, etc.)
- **Family Firm** – Family-owned (e.g. Smith & Sons Ltd)
- **Government** – Government agencies and public institutions

## Tech stack

| Layer | Stack |
|-------|-------|
| Pipeline | Python 3.10+, pandas, Anthropic API, PyTorch, transformers |
| Rule engine | Regex, keyword matching, suffix lists |
| LLM | Claude Haiku 3.5 via Batches API |
| ML | XLM-RoBERTa fine-tuned (Hugging Face) |
| Web | HTML, CSS, JavaScript, Chart.js |

## Pipeline scripts

| Script | Purpose |
|--------|---------|
| `01_validate_claude_on_train.py` | Accuracy vs manual labels |
| `02_rule_based_filter.py` | Deterministic rules, ~56% coverage |
| `03_submit_claude_batches.py` | Submit to Anthropic Batches |
| `04_collect_and_merge.py` | Merge rule + API results |
| `05_train_xlmr.py` | Fine-tune XLM-RoBERTa |

Run from project root. Paths in scripts assume `output/` and source `.dta`; adjust for your setup.

```bash
pip install -r requirements.txt
python scripts/02_rule_based_filter.py   # example
```

## Data

### File structure

```
August/
├── done_processed_{CC}_data.csv      # Per-country CSV
├── done_processed_{CC}_data_stats.txt
└── ... (120+ countries)
```

### CSV columns

| Column       | Description          |
|--------------|----------------------|
| parent_name  | Entity name          |
| parent_id    | Orbis ID             |
| parent_city  | City                 |
| language     | Detected language    |
| entity_type  | individual, company, family_firm, government |

## Web interface

- **Report** – Metrics, workflow diagram, classification results
- **Simulation** – Entity classification walkthrough
- **Data by Country** – Browse by country, CSV, stats, charts

Hosted at [puneethkotha.github.io/Research-Data](https://puneethkotha.github.io/Research-Data/).

Built with `build_report.py`; outputs `index.html`.

## Contact

Puneeth Kotha · NYU Stern
