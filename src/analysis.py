"""ITDS 1471 Final Project: Superstore Sales analysis.

Run from the repo root:  python src/analysis.py
Reads data/raw/Sample - Superstore.csv, prints key findings,
saves charts to reports/figures/ and the top 10 rows to reports/top10_rows.csv.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "raw" / "Sample - Superstore.csv"
FIGS = ROOT / "reports" / "figures"

# Colorblind-safe palette (first 3 slots validated as a set) + text inks
BLUE, ORANGE, AQUA, RED = "#2a78d6", "#eb6834", "#1baf7a", "#e34948"
INK, INK_2 = "#0b0b0b", "#52514e"

plt.rcParams.update({
    "figure.dpi": 150,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": INK_2,
    "axes.labelcolor": INK,
    "axes.titleweight": "bold",
    "axes.grid": True,
    "grid.color": "#e4e3df",
    "grid.linewidth": 0.8,
    "axes.axisbelow": True,
    "xtick.color": INK_2,
    "ytick.color": INK_2,
    "font.size": 10,
})


def dollars(x, _pos=None):
    sign = "-" if x < 0 else ""
    return f"{sign}${abs(x) / 1000:,.0f}K" if abs(x) >= 1000 else f"{sign}${abs(x):,.0f}"


def money(v):
    return f"-${-v:,.0f}" if v < 0 else f"${v:,.0f}"


def save(fig, name):
    fig.tight_layout()
    fig.savefig(FIGS / name, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved reports/figures/{name}")


# ---------- 1. Load & clean ----------
df = pd.read_csv(DATA, encoding="latin-1")  # file is not UTF-8
assert df.shape == (9994, 21), f"unexpected shape {df.shape}"
assert df.isna().sum().sum() == 0, "unexpected missing values"
assert not df.duplicated().any(), "unexpected duplicate rows"

print(f"Rows: {len(df):,}  Columns: {df.shape[1]}")

df["Order Date"] = pd.to_datetime(df["Order Date"], format="%m/%d/%Y")
df["Ship Date"] = pd.to_datetime(df["Ship Date"], format="%m/%d/%Y")
df["Year"] = df["Order Date"].dt.year
df["Ship Days"] = (df["Ship Date"] - df["Order Date"]).dt.days
assert (df["Ship Days"] >= 0).all(), "ship date before order date"

FIGS.mkdir(parents=True, exist_ok=True)
df.head(10).to_csv(ROOT / "reports" / "top10_rows.csv", index=False)

print(f"Orders: {df['Order ID'].nunique():,}  Customers: {df['Customer ID'].nunique():,}")
print(f"Date range: {df['Order Date'].min():%Y-%m-%d} to {df['Order Date'].max():%Y-%m-%d}")
print(f"Total sales: ${df['Sales'].sum():,.0f}  Total profit: ${df['Profit'].sum():,.0f}"
      f"  Margin: {df['Profit'].sum() / df['Sales'].sum():.1%}")
print(f"Loss-making order lines: {(df['Profit'] < 0).mean():.1%}")

print("\nCharts:")

# ---------- Chart 1: monthly sales & profit trend (two panels, shared x) ----------
monthly = df.set_index("Order Date").resample("MS")[["Sales", "Profit"]].sum()
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
ax1.plot(monthly.index, monthly["Sales"], color=BLUE, lw=2, marker="o", ms=3)
ax1.set_title("Monthly Sales, 2014–2017")
ax1.set_ylabel("Sales")
ax1.yaxis.set_major_formatter(dollars)
ax2.plot(monthly.index, monthly["Profit"], color=BLUE, lw=2, marker="o", ms=3)
ax2.axhline(0, color=INK_2, lw=0.8)
ax2.set_title("Monthly Profit, 2014–2017")
ax2.set_ylabel("Profit")
ax2.set_xlabel("Order month")
ax2.yaxis.set_major_formatter(dollars)
save(fig, "01_monthly_sales_profit.png")

yearly = df.groupby("Year")[["Sales", "Profit"]].sum()
yearly["Growth"] = yearly["Sales"].pct_change()
print("\n  Yearly totals:\n" + yearly.to_string(formatters={
    "Sales": "${:,.0f}".format, "Profit": "${:,.0f}".format, "Growth": "{:.1%}".format}))
by_month = df.groupby(df["Order Date"].dt.month)["Sales"].sum()
print(f"  Best month overall: {by_month.idxmax()}  Worst: {by_month.idxmin()}")

# ---------- Chart 2: share of sales by category (pie) ----------
cat = df.groupby("Category")[["Sales", "Profit"]].sum().sort_values("Sales", ascending=False)
fig, ax = plt.subplots(figsize=(6, 6))
ax.pie(cat["Sales"], labels=cat.index, autopct="%1.1f%%", startangle=90, counterclock=False,
       colors=[BLUE, ORANGE, AQUA], wedgeprops={"edgecolor": "white", "linewidth": 2},
       textprops={"color": INK})
ax.set_title("Share of Total Sales by Category")
ax.legend(cat.index, title="Category", loc="upper left", bbox_to_anchor=(0.85, 1))
save(fig, "02_sales_share_by_category.png")
cat["Margin"] = cat["Profit"] / cat["Sales"]
print("\n  By category:\n" + cat.to_string(formatters={
    "Sales": "${:,.0f}".format, "Profit": "${:,.0f}".format, "Margin": "{:.1%}".format}))

# ---------- Chart 3: profit by sub-category (seaborn, diverging color) ----------
sub = df.groupby("Sub-Category")["Profit"].sum().sort_values()
fig, ax = plt.subplots(figsize=(9, 6))
sns.barplot(x=sub.values, y=sub.index, hue=sub.index, legend=False, ax=ax, saturation=1,
            palette=[RED if v < 0 else BLUE for v in sub.values])
ax.axvline(0, color=INK_2, lw=0.8)
ax.set_title("Total Profit by Sub-Category (red = loss)")
ax.set_xlabel("Profit")
ax.set_ylabel("Sub-category")
ax.xaxis.set_major_formatter(dollars)
ax.grid(axis="y", visible=False)
save(fig, "03_profit_by_subcategory.png")
print("\n  Loss-making sub-categories: " + ", ".join(f"{k} ({money(v)})" for k, v in sub[sub < 0].items()))
print("  Top 3 profit sub-categories: " + ", ".join(f"{k} ({money(v)})" for k, v in sub.tail(3)[::-1].items()))

# ---------- Chart 4: sales and profit by region (grouped bars, same $ axis) ----------
region = df.groupby("Region")[["Sales", "Profit"]].sum().sort_values("Sales", ascending=False)
fig, ax = plt.subplots(figsize=(9, 5))
region.plot.bar(ax=ax, color=[BLUE, ORANGE], width=0.75, edgecolor="white", linewidth=2, rot=0)
ax.set_title("Sales and Profit by Region")
ax.set_xlabel("Region")
ax.set_ylabel("US dollars")
ax.yaxis.set_major_formatter(dollars)
ax.legend(title="Measure")
ax.grid(axis="x", visible=False)
save(fig, "04_sales_profit_by_region.png")
region["Margin"] = region["Profit"] / region["Sales"]
print("\n  By region:\n" + region.to_string(formatters={
    "Sales": "${:,.0f}".format, "Profit": "${:,.0f}".format, "Margin": "{:.1%}".format}))

# ---------- Chart 5: average profit per order line by discount level ----------
disc = df.groupby("Discount").agg(avg_profit=("Profit", "mean"), lines=("Profit", "size"))
fig, ax = plt.subplots(figsize=(9, 5))
labels = [f"{d:.0%}" for d in disc.index]
ax.bar(labels, disc["avg_profit"], color=[RED if v < 0 else BLUE for v in disc["avg_profit"]],
       edgecolor="white", linewidth=2)
ax.axhline(0, color=INK_2, lw=0.8)
ax.set_title("Average Profit per Order Line by Discount Level (red = loss)")
ax.set_xlabel("Discount")
ax.set_ylabel("Average profit")
ax.yaxis.set_major_formatter(dollars)
ax.grid(axis="x", visible=False)
save(fig, "05_profit_by_discount.png")
corr = df["Discount"].corr(df["Profit"])
breakeven = disc[disc["avg_profit"] < 0].index.min()
print(f"\n  Discount vs profit correlation: {corr:.2f}")
print(f"  Average profit turns negative at discount >= {breakeven:.0%}")
print("  Avg profit by discount: " + ", ".join(f"{d:.0%}: {money(v)}" for d, v in disc["avg_profit"].items()))

# ---------- Chart 6: yearly sales by category (grouped bars) ----------
yc = df.pivot_table(index="Year", columns="Category", values="Sales", aggfunc="sum")[cat.index]
fig, ax = plt.subplots(figsize=(9, 5))
yc.plot.bar(ax=ax, color=[BLUE, ORANGE, AQUA], width=0.8, edgecolor="white", linewidth=2, rot=0)
ax.set_title("Yearly Sales by Category")
ax.set_xlabel("Year")
ax.set_ylabel("Sales")
ax.yaxis.set_major_formatter(dollars)
ax.legend(title="Category")
ax.grid(axis="x", visible=False)
for bars in ax.containers:
    ax.bar_label(bars, labels=[f"${b.get_height() / 1000:.0f}K" for b in bars], fontsize=8, color=INK_2)
save(fig, "06_yearly_sales_by_category.png")

seg = df.groupby("Segment")["Sales"].sum()
print("\n  Sales share by segment: " + ", ".join(f"{k} {v / seg.sum():.1%}" for k, v in seg.items()))
print(f"  Average days to ship: {df['Ship Days'].mean():.1f}")
