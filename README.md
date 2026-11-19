# ITDS 1471 Final Project

**Course:** ITDS 1471 – Data Analysis with Python
**Due:** December 5, 2026

As a junior data analyst, I take a real-world dataset from a free public source (CSV or Excel, at least 50 rows and 5 columns), load it into Python, and analyze it with Pandas. I visualize the main relationships and trends with Matplotlib and Seaborn, using charts with titles, axis labels, and legends, and I explain what each chart shows. The results go into a written report (`.docx`) and a 10–12 slide PowerPoint deck.

## Dataset

**Superstore Sales** by Vivek Chowdhury on Kaggle: <https://www.kaggle.com/datasets/vivek468/superstore-dataset-final>
(chosen from the shortlist in [`docs/dataset-options.md`](docs/dataset-options.md))

- File: `Sample - Superstore.csv`, 2.3 MB, **9,994 rows × 21 columns**
- One row per order line: US retail orders from 2014-01-03 to 2017-12-30
- Columns: order/ship dates, ship mode, customer segment, location (city, state, region), product category/sub-category, Sales, Quantity, Discount, Profit
- No missing values, no duplicate rows
- Encoding is **latin-1**, not UTF-8: use `pd.read_csv(..., encoding="latin-1")`
- License: "Other". Originally Tableau sample data; used here for coursework

## Questions

_TBD_

## Methods

_TBD_

## Results

_TBD_

## How to Run

1. Install dependencies: `pip install -r requirements.txt`
2. Download the dataset ZIP and unzip it into `data/raw/`:
   ```bash
   curl -L -o superstore.zip https://www.kaggle.com/api/v1/datasets/download/vivek468/superstore-dataset-final
   unzip superstore.zip -d data/raw/
   ```
   This should create `data/raw/Sample - Superstore.csv`.
3. Analysis script: _TBD_

## Project Layout

```
data/raw/        original downloaded dataset (git-ignored)
data/processed/  cleaned data used by the analysis
notebooks/       exploratory Jupyter notebooks
src/             final analysis script (.py — submitted)
reports/         report (.docx) and slides (.pptx)
reports/figures/ exported chart images
docs/            planning notes (dataset options, etc.)
```
