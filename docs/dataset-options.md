# Dataset Options

Shortlist for the ITDS 1471 final project. The course needs:

- a CSV or Excel file with **at least 50 rows and 5 columns**
- analysis in **Pandas**, multiple labeled charts (**bar, line, pie**) in Matplotlib/Seaborn
- the data file goes in the submission ZIP

Size, license, and last-updated values come from the Kaggle API (pulled 2026-11-18).
Row and column counts come from each dataset's docs and are **not yet verified**. Check them with `df.shape` after download.

## Summary

| # | Dataset | Rows × Cols | Size | License | Updated | Time axis? |
|---|---------|-------------|------|---------|---------|-----------|
| 1 | Superstore Sales | ~9,994 × 21 | 2.3 MB | Other (Tableau sample) | 2022-02-17 | Yes, 2014–2017 |
| 2 | Netflix Movies & TV Shows | ~8,807 × 12 | 3.4 MB | CC0 | 2021-09-27 | Yes, 2008–2021 |
| 3 | Video Game Sales | ~16,598 × 11 | 0.4 MB | Unknown | 2016-10-26 | Yes, 1980–2016 |
| 4 | Most Streamed Spotify Songs 2023 | ~953 × 24 | 0.1 MB | Other | 2023-08-26 | Release year only |
| 5 | Hotel Booking Demand | ~119,390 × 32 | 16.9 MB | CC BY 4.0 | 2020-02-13 | Yes, 2015–2017 |
| 6 | Coffee Shop Sales | ~149,116 × 11 | 9.0 MB (.xlsx) | LGPL 3.0 | 2023-12-01 | Yes, Jan–Jun 2023 |
| 7 | World Happiness Report | ~155 × 10–12 per year (5 files) | 0.1 MB | CC0 | 2019-11-27 | Yes, 2015–2019 |

---

## 1. Superstore Sales
<https://www.kaggle.com/datasets/vivek468/superstore-dataset-final>
One CSV, `Sample - Superstore.csv`.

**Why it fits:** It's a retail sales dataset, the kind a junior analyst would get handed. It has dates for line charts, Category/Segment/Region for pie and bar charts, and Sales/Profit/Discount as numbers to analyze.

**Questions:**
- How did monthly sales and profit trend from 2014 to 2017, and is there a seasonal pattern?
- Which categories and sub-categories make money, and which lose it?
- Do bigger discounts lead to lower profit?

**Concerns:** Very clean, with almost no cleaning needed, so there's little to show in a "data prep" section. It's widely used, so classmates may pick it too. The license is "Other" because it's Tableau sample data. That's fine for coursework.

## 2. Netflix Movies & TV Shows
<https://www.kaggle.com/datasets/shivamb/netflix-shows>
One CSV, `netflix_titles.csv`.

**Why it fits:** Real, messy data, so the report gets a meaningful cleaning section. `type` (Movie/TV Show) works well as a pie chart, `date_added` gives a line chart, and `country`, `rating`, and `listed_in` give bar charts. CC0 license.

**Questions:**
- How has the number of titles Netflix adds each year changed, for movies vs. TV shows?
- Which countries produce the most Netflix content?
- What ratings and genres dominate the catalog?

**Concerns:** Lots of missing values: `director` is about 30% empty, and `cast` and `country` have gaps. `duration` mixes "90 min" and "2 Seasons". `country` and `listed_in` hold comma-separated lists that need to be split. The data stops in 2021. It's mostly categorical, with few true numeric columns.

## 3. Video Game Sales
<https://www.kaggle.com/datasets/gregorut/videogamesales>
One CSV, `vgsales.csv`.

**Why it fits:** Sales in millions broken down by region (NA/EU/JP/Other) make good pie and stacked-bar charts. `Year` gives a line chart, and `Genre`, `Platform`, and `Publisher` give categories to group by.

**Questions:**
- Which genres sell best in North America vs. Japan?
- How did total game sales change from 1980 to 2016?
- Which platforms and publishers lead in global sales?

**Concerns:** About 270 rows have `Year` = N/A, and some have no Publisher. Years after 2016 are sparse, so cut them off. The license is listed as Unknown. The data is scraped from VGChartz, so the figures are estimates.

## 4. Most Streamed Spotify Songs 2023
<https://www.kaggle.com/datasets/nelgiriyewithana/top-spotify-songs-2023>
One CSV, `spotify-2023.csv`.

**Why it fits:** Fun, easy-to-present topic with many numeric columns (streams, BPM, danceability, energy, and more) for scatter plots and correlations. Mode and key work as pie charts.

**Questions:**
- Do danceability or energy relate to stream counts?
- Which artists have the most songs in the top list?
- Which release years are most common among the top songs?

**Concerns:** Small, at about 950 rows, but still well over 50. The file needs `encoding="latin-1"`. One `streams` value is corrupted text, and some numeric columns have commas in them. `key` has about 95 missing values. There's no real time series.

## 5. Hotel Booking Demand
<https://www.kaggle.com/datasets/jessemostipak/hotel-booking-demand>
One CSV, `hotel_bookings.csv`.

**Why it fits:** Large and realistic, with a clear business question about cancellations. Arrival dates give monthly trends, hotel type and market segment give pie and bar charts, and `adr` (average daily rate) is a strong numeric column. CC BY 4.0.

**Questions:**
- Which months are busiest, and how do prices (ADR) change across the year?
- What share of bookings are canceled, and does lead time predict cancellation?
- How do city and resort hotels compare?

**Concerns:** 32 columns is a lot to explain in a 10–12 slide deck. `company` is about 94% empty and `agent` about 14%. There are ADR outliers, including negative values and one around 5,400. The 17 MB CSV makes the ZIP larger, which is still fine.

## 6. Coffee Shop Sales
<https://www.kaggle.com/datasets/ahmedabbas757/coffee-sales>
One Excel file, `Coffee Shop Sales.xlsx`.

**Why it fits:** Transaction-level sales across 3 store locations, with date and time, product category, and price. Good for daily and hourly line charts, and pie charts by store or category. It's an Excel file, which the assignment allows.

**Questions:**
- What hours and weekdays are busiest?
- Which store and product category bring in the most revenue?
- How did monthly revenue grow from January to June 2023?

**Concerns:** Synthetic (it's a Maven Analytics practice set) and too clean, so there are no real cleaning steps. It covers only 6 months. Reading .xlsx needs `openpyxl`. With 149k rows, `read_excel` is slow.

## 7. World Happiness Report
<https://www.kaggle.com/datasets/unsdsn/world-happiness>
Five CSVs, one per year from 2015 to 2019.

**Why it fits:** Country-level data with score, GDP, social support, life expectancy, and freedom. Good for correlations, regional bar charts, and year-over-year line charts. CC0.

**Questions:**
- Which factors (GDP, social support, health) relate most strongly to happiness?
- How do regions compare?
- Which countries rose or fell the most from 2015 to 2019?

**Concerns:** Only about 155 rows per year. Column names change between years, for example `Happiness Score` vs. `Score`, and 2018–2019 drop the `Region` column, so the 5 files need careful merging. Pie charts don't fit this data naturally.

---

## Top 2 Picks

**1. Superstore Sales.** It's the best fit for the assignment as written. It covers every required chart type (line over time, pie by category, bar by region, scatter of discount vs. profit). The analyst framing works on its own, and the conclusions turn into business recommendations, which suit a professional report. Main downside: it's clean and common.

**2. Netflix Movies & TV Shows.** The best choice if you want the project to stand out. The messy columns give you a real cleaning story to put in the report and slides. It still supports a line chart (titles added per year), a pie chart (Movie vs. TV), and bar charts (countries, genres, ratings), and the license is clean (CC0). Main downside: few numeric columns, so the analysis leans on counts and groupbys.

**Tie-breaker:** Superstore is safer and faster to finish. Netflix shows more skill.
