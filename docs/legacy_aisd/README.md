# Multi-Crop Sell-Timing Advisor for Rwanda

**Course:** 04-652 Artificial Intelligence System Design<br>
**Assignment:** Assignment 2 - Phase 1: Preprocessing and Feature Engineering Strategy<br>
**Author:** Jean Gabriel Mpuhwezimana

## Project Overview

Smallholder farmers must decide whether to sell harvested crops immediately or wait for potentially higher prices. Waiting can increase revenue, but storage costs and crop deterioration may offset the price gain.

This project develops a decision-support system that combines short-term crop price forecasts with crop-specific storage-loss estimates and costs to compare selling opportunities.

## Machine Learning Task

The prediction task is **regression**. The model will predict crop prices in **Rwandan francs per kilogram (RWF/kg)** at horizons of **1, 2 and 3 calendar days**.

A shared XGBoost model is proposed, using crop identity, market, historical prices, calendar features and forecast horizon. Its performance will be compared with:

- **Persistence baseline:** the future price equals the latest observed price.
- **Histogram gradient boosting:** an alternative tree-based regression model.

Training targets will come from observed market prices. Storage losses will be represented separately through crop-specific assumptions in the revenue calculation.

## Dataset

The dataset contains historical farmgate price observations for agricultural products sold in Rwandan markets. Each row represents the reported price of one product at one market on one observation date. The current project includes tomato and carrot exports from [TangaBid](https://tangabid.com/data-access/), with **Esoko Rwanda** identified as the source. Prices are recorded in Rwandan francs per kilogram (RWF/kg).

| Column | Meaning |
| --- | --- |
| `observed_date` | Date on which the market price was observed. |
| `product` | Crop/product name, such as Tomato or Carrot. |
| `unit` | Measurement unit for the price, expected to be kilograms. |
| `variety` | Crop variety; currently missing in the available exports. |
| `grade` | Product quality grade; currently missing in the available exports. |
| `channel` | Market channel for the reported price, such as farmgate. |
| `location` | Name of the market location. |
| `region` | District or wider region containing the location. |
| `currency` | Currency of the price, expected to be RWF. |
| `source` | Organisation identified as the source of the observation. |
| `scraped_at` | Timestamp when the record was collected from the source. |
| `price` | Observed selling price in RWF per unit. |

The `price` column is the target feature: the model predicts its future value for each crop and market.

### Example records

The table below shows four observations in a simplified form. Each row is one reported crop price at a particular market and date.

| Observed date | Product | Market location | Region | Price (RWF/kg) |
| --- | --- | --- | --- | ---: |
| 2026-10-14 | Tomato | Kirambo | BURERA | 833.00 |
| 2026-10-14 | Tomato | Kibuye | KARONGI | 800.00 |
| 2026-10-14 | Tomato | Nyagahinga | BURERA | 600.00 |
| 2026-10-13 | Tomato | Birambo | KARONGI | 567.00 |

The initial audit covers tomatoes and carrots. Cabbage, red onions and Irish potato Kinigi Grade 2 are planned extensions, subject to historical data availability and quality.

| Crop | Raw observations | Raw columns | Observations after duplicate and conflict handling | Scope |
| --- | ---: | ---: | ---: | --- |
| Tomatoes | 3,524 | 12 | 3,106 | Initial dataset |
| Carrots | 3,552 | 12 | 3,160 | Initial dataset |
| Cabbage | - | - | - | Planned extension |
| Red onions | - | - | - | Planned extension |
| Irish potato Kinigi Grade 2 | - | - | - | Planned extension |

### Initial Audit Findings

- **Combined raw dataset:** 7,076 rows and 12 columns.
- **Date range:** 1 January 2025 to 14 October 2026.
- **Missing metadata:** `variety` and `grade` are entirely missing in both exports; all other columns contain no missing values.
- **Overall missingness:** 16.67% of cells.
- **Reporting gap:** no observations from August through October 2025.
- **Retained observations:** 6,266 after duplicate removal and isolation of conflicting records.
- **Forecast examples:** 6,329 observed origin-target pairs across the three horizons, before eligibility filtering and temporal boundary exclusions.

The 12 raw columns include price, date, product, market and provenance fields. They are distinct from the engineered model inputs.

The target variable is the price observed on the exact future date for the same crop and market. Missing future prices will not be interpolated.

## Preprocessing and Feature Engineering Strategy

1. **Validate records:** check dates, product identities, units, currency, market identifiers and positive numerical prices.
2. **Resolve duplicates:** collapse repeated equal-price records and isolate conflicting prices for review.
3. **Construct historical features:** calculate lagged prices, observation ages, rolling statistics and price changes separately for each crop-market series.
4. **Create targets:** match each forecast origin with an observed price exactly 1, 2 or 3 calendar days later.
5. **Partition chronologically:** allocate distinct forecast-origin dates into 70% training, 15% validation and 15% test periods.
6. **Prevent leakage:** exclude examples whose target dates cross partition boundaries and fit preprocessing transformations only on training data.
7. **Evaluate models:** compare MAE and RMSE by crop and forecast horizon, with observation counts reported alongside the metrics.

Three expanding-window folds within the training period are planned for model selection. Numerical imputation will use training-derived medians, while crop and market identifiers will be one-hot encoded. Tree-model inputs will remain unscaled.

Preliminary tomato experiments have already examined part of the available evaluation period. Results that reuse this period will be treated as exploratory; independent confirmation will require new future observations.

## Repository Contents

| Path | Purpose |
| --- | --- |
| `data/raw/` | Original tomato and carrot CSV exports |
| `data/processed/` | Output location for processed datasets |
| `phase1_strategy/Phase1_Strategy_Report.pdf` | Phase 1 audit and preprocessing strategy |
| `phase1_strategy/Phase1_Strategy_Report.tex` | Editable LaTeX report source |
| `phase1_strategy/audit_raw.py` | Reproducible dataset audit |
| `phase1_strategy/audit/` | Audit summaries, missingness tables and conflicting records |
| `phase2_implementation/notebooks/` | Location for the Phase 2 execution notebook |
| `src/` | Reserved modules for preprocessing implementation |
| `figures/` | Location for diagnostic figures |
| `requirements.txt` | Python dependencies |
| `.gitignore` | Exclusions for environments, caches and generated files |

## Running the Phase 1 Audit

Use **Python 3.11 or 3.12**. Run the following commands from the repository root.

### 1. Create a virtual environment

```bash
python -m venv .venv
```

### 2. Activate the environment

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**

```bat
.venv\Scripts\activate.bat
```

**Linux or macOS:**

```bash
source .venv/bin/activate
```

### 3. Install dependencies and run the audit

```bash
python -m pip install -r requirements.txt
python phase1_strategy/audit_raw.py
```

Audit results are written to `phase1_strategy/audit/`. The script preserves the original CSV files and reports dataset dimensions, missingness, duplicate records, conflicts and available forecast pairs.

## Compiling the Strategy Report

The report is written in LaTeX and uses black-and-white formatting. Compile it with pdfLaTeX through TeX Live, MiKTeX or Overleaf.

```bash
cd phase1_strategy
pdflatex -interaction=nonstopmode -halt-on-error Phase1_Strategy_Report.tex
```

The LaTeX source requires no external figures or bibliography files.

## Planned Crop Expansion

Additional crop histories will be assessed using the same audit procedure:

- [Cabbage](https://www.tangabid.com/market/prices/?product=62)
- [Red onions](https://www.tangabid.com/market/prices/?product=5)
- [Irish potato Kinigi Grade 2](https://www.tangabid.com/market/prices/?product=3)

Crop inclusion will depend on reporting frequency, historical coverage, record consistency and sufficient observed forecast pairs. Potato varieties and grades will remain separate product categories.

## Current Project Stage

Phase 1 establishes the dataset audit, preprocessing decisions, feature engineering plan and validation strategy.

Phase 2 will implement the preprocessing pipeline, produce diagnostic figures and evaluate forecasting performance. Revenue comparisons will use documented storage-loss scenarios because the price datasets do not contain measured spoilage outcomes.
