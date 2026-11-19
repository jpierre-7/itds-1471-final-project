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

1. How did sales and profit trend from 2014 to 2017, and is there a seasonal pattern?
2. Which categories and sub-categories make money, and which lose it?
3. Do bigger discounts lead to lower profit?

## Methods

- Load the CSV with Pandas (`encoding="latin-1"`). Check the shape, missing values, and duplicates.
- Parse order and ship dates into datetimes, then add `Year` and `Ship Days` columns.
- Group and aggregate (`groupby`, `resample`, `pivot_table`) by month, year, category, sub-category, region, and discount level.
- Make 6 charts with Matplotlib and Seaborn (line, pie, bar, grouped bar), each with a title, axis labels, and a legend where needed.

## Results

| Chart | Finding |
|---|---|
| `01_monthly_sales_profit.png` | Sales grew 51% from 2014 ($484K) to 2017 ($733K). Every year peaks in Sep–Dec and dips in Jan–Feb. |
| `02_sales_share_by_category.png` | Sales are split fairly evenly: Technology 36%, Furniture 32%, Office Supplies 31%. |
| `03_profit_by_subcategory.png` | Tables (-$17.7K), Bookcases (-$3.5K), and Supplies (-$1.2K) lose money. Copiers, Phones, and Accessories earn the most. |
| `04_sales_profit_by_region.png` | West leads in sales and margin (14.9%). Central has the weakest margin (7.9%). |
| `05_profit_by_discount.png` | Average profit per order line turns negative at discounts of 30% and above. |
| `06_yearly_sales_by_category.png` | All three categories grew in 2016–2017. Furniture sells well but earns only a 2.5% margin. |

Overall: $2.30M in sales, $286K profit (12.5% margin), and 18.7% of order lines lose money.

## How to Run

1. Install dependencies: `pip install -r requirements.txt`
2. Download the dataset ZIP and unzip it into `data/raw/`:
   ```bash
   curl -L -o superstore.zip https://www.kaggle.com/api/v1/datasets/download/vivek468/superstore-dataset-final
   unzip superstore.zip -d data/raw/
   ```
   This should create `data/raw/Sample - Superstore.csv`.
3. Run the analysis from the repo root: `python src/analysis.py`
   It prints the key numbers, saves the charts to `reports/figures/`, and writes the top 10 rows to `reports/top10_rows.csv` (for the slides).
4. Optional: rebuild the report and slides.
   ```bash
   pip install python-docx python-pptx
   python scripts/build_report.py    # -> reports/report.docx
   python scripts/build_slides.py    # -> reports/presentation.pptx
   ```

## Submission

The deliverables are `reports/report.docx` (written report) and `reports/presentation.pptx` (11 slides). To build the Canvas ZIP from the repo root:

```bash
python scripts/build_zip.py   # -> ITDS1471_FinalProject_JohnPierre.zip (git-ignored)
```

The ZIP keeps the folder structure, so `python src/analysis.py` runs right after unzipping.

## Project Layout

```
data/raw/        original downloaded dataset (git-ignored)
data/processed/  cleaned data used by the analysis
notebooks/       exploratory Jupyter notebooks
src/             final analysis script (.py — submitted)
reports/         report (.docx) and slides (.pptx)
reports/figures/ exported chart images
scripts/         build scripts for the report, slides, and submission ZIP
docs/            planning notes (dataset options, etc.)
```
