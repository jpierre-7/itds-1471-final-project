"""Build reports/presentation.pptx (11 slides, 16:9) from the charts and top-10 rows.

Run from the repo root:
    uvx --with python-pptx,pandas python -I scripts/build_slides.py
Numbers on the slides are copied from the output of src/analysis.py; re-check them if the data changes.
"""
import hashlib
from pathlib import Path

import pandas as pd
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_SHAPE_TYPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

ROOT = Path(__file__).resolve().parent.parent
FIGS = ROOT / "reports" / "figures"
OUT = ROOT / "reports" / "presentation.pptx"

FONT = "Calibri"
INK = RGBColor(0x1F, 0x1F, 0x1F)
MUTED = RGBColor(0x52, 0x51, 0x4E)
ACCENT = RGBColor(0x2A, 0x78, 0xD6)  # same blue as the charts
TINT = RGBColor(0xEC, 0xF3, 0xFC)  # light blue card fill
RED = RGBColor(0xE3, 0x49, 0x48)  # same red as the loss bars
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

SLIDE_W, SLIDE_H = 13.333, 7.5
M = 0.6  # side margin
CONTENT_W = SLIDE_W - 2 * M

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(SLIDE_W), Inches(SLIDE_H)
BLANK = prs.slide_layouts[6]


def text(slide, x, y, w, h, paras, size=16, color=INK, bold=False, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, bullets=False, space_after=6):
    """Add a text box. paras: list of strings, or (string, {run overrides}) tuples."""
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, para in enumerate([paras] if isinstance(paras, (str, tuple)) else paras):
        s, opts = para if isinstance(para, tuple) else (para, {})
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(space_after)
        if bullets:
            pPr = p._p.get_or_add_pPr()
            pPr.set("marL", str(Inches(0.25)))
            pPr.set("indent", str(-Inches(0.25)))
            bu = pPr.makeelement(qn("a:buChar"), {"char": "•"})
            pPr.append(bu)
        r = p.add_run()
        r.text = s
        f = r.font
        f.name, f.size, f.bold = FONT, Pt(opts.get("size", size)), opts.get("bold", bold)
        f.color.rgb = opts.get("color", color)
        if "link" in opts:
            r.hyperlink.address = opts["link"]
    return box


def title(slide, s):
    text(slide, M, 0.45, CONTENT_W, 0.9, s, size=32, bold=True, anchor=MSO_ANCHOR.MIDDLE)


def card(slide, x, y, w, h, fill=TINT):
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shp.adjustments[0] = 0.08
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    shp.line.fill.background()
    shp.shadow.inherit = False
    return shp


def stat(slide, x, y, w, value, label, color=ACCENT, size=40):
    text(slide, x, y, w, 0.8, value, size=size, bold=True, color=color)
    text(slide, x, y + 0.8, w, 0.7, label, size=14, color=MUTED)


def number_dot(slide, x, y, n, d=0.5):
    dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(d), Inches(d))
    dot.fill.solid()
    dot.fill.fore_color.rgb = ACCENT
    dot.line.fill.background()
    dot.shadow.inherit = False
    tf = dot.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = str(n)
    r.font.name, r.font.size, r.font.bold, r.font.color.rgb = FONT, Pt(18), True, WHITE


def image(slide, path, x, y, max_w, max_h):
    """Place an image as large as fits in the box, keeping its aspect ratio; top-aligned, centred across."""
    pic = slide.shapes.add_picture(str(path), Inches(x), Inches(y))
    scale = min(Inches(max_w) / pic.width, Inches(max_h) / pic.height)
    pic.width, pic.height = int(pic.width * scale), int(pic.height * scale)
    pic.left = Inches(x) + (Inches(max_w) - pic.width) // 2
    return pic


def chart_slide(headline, fig, value, label, points, value_color=ACCENT):
    """Chart left (large), one stat callout and 1-2 bullets right."""
    s = prs.slides.add_slide(BLANK)
    title(s, headline)
    image(s, FIGS / fig, M, 1.55, 8.4, 5.4)
    side_x, side_w = 9.4, SLIDE_W - M - 9.4
    stat(s, side_x, 1.9, side_w, value, label, color=value_color)
    text(s, side_x, 3.75, side_w, 3.0, points, size=16, bullets=True, space_after=12)
    return s


# ---------- 1. Title ----------
s = prs.slides.add_slide(BLANK)
text(s, M, 1.3, CONTENT_W, 1.1, "Superstore Sales Analysis, 2014–2017", size=44, bold=True)
text(s, M, 2.4, CONTENT_W, 0.6, "Sales trends, profit drivers, and the cost of discounts", size=22, color=MUTED)
text(s, M, 3.3, CONTENT_W, 1.0, [
    ("John Pierre", {"bold": True, "size": 20}),
    "ITDS 1471 Data Analysis with Python  ·  Houston Community College  ·  December 5, 2026",
], size=16, color=INK)
for i, (v, lab) in enumerate([("$2.30M", "total sales"), ("$286K", "total profit"),
                              ("12.5%", "profit margin"), ("18.7%", "of order lines lose money")]):
    x = M + i * (CONTENT_W + 0.3) / 4
    card(s, x, 4.9, (CONTENT_W + 0.3) / 4 - 0.3, 1.7)
    stat(s, x + 0.3, 5.05, (CONTENT_W + 0.3) / 4 - 0.9, v, lab)

# ---------- 2. Overview & questions ----------
s = prs.slides.add_slide(BLANK)
title(s, "Project overview: three questions about a retail store")
text(s, M, 1.7, 4.9, 4.8, [
    ("Role", {"bold": True, "color": ACCENT}),
    "Junior data analyst handed four years of a US office-supply store's orders.",
    ("Goal", {"bold": True, "color": ACCENT}),
    "Load a real public dataset into Python, analyze it with Pandas, and show the trends "
    "in labeled Matplotlib and Seaborn charts.",
    ("Deliverables", {"bold": True, "color": ACCENT}),
    "Analysis script, 6 charts, written report, and this deck.",
], size=16, space_after=8)
questions = [
    "How did sales and profit trend from 2014 to 2017, and is there a seasonal pattern?",
    "Which categories and sub-categories make money, and which lose it?",
    "Do bigger discounts lead to lower profit?",
]
for i, q in enumerate(questions):
    y = 1.7 + i * 1.65
    card(s, 6.0, y, SLIDE_W - M - 6.0, 1.35)
    number_dot(s, 6.3, y + 0.42, i + 1)
    text(s, 7.1, y, SLIDE_W - M - 7.4, 1.35, q, size=18, anchor=MSO_ANCHOR.MIDDLE)

# ---------- 3. Dataset ----------
s = prs.slides.add_slide(BLANK)
title(s, "Dataset: Superstore Sales from Kaggle")
for i, (v, lab) in enumerate([("9,994", "rows (order lines)"), ("21", "columns"),
                              ("5,009", "orders"), ("793", "customers")]):
    x = M + i * (CONTENT_W + 0.3) / 4
    card(s, x, 1.6, (CONTENT_W + 0.3) / 4 - 0.3, 1.6)
    stat(s, x + 0.3, 1.75, (CONTENT_W + 0.3) / 4 - 0.9, v, lab)
text(s, M, 3.6, 5.6, 3.4, [
    ("Source", {"bold": True, "color": ACCENT}),
    ("kaggle.com/datasets/vivek468/superstore-dataset-final",
     {"link": "https://www.kaggle.com/datasets/vivek468/superstore-dataset-final", "color": ACCENT}),
    "Sample - Superstore.csv, 2.3 MB, latin-1 encoding",
    "US retail orders, 2014-01-03 to 2017-12-30",
    "No missing values, no duplicate rows",
    "Tableau sample data (license “Other”), fine for coursework",
], size=16, space_after=6)
text(s, 6.8, 3.6, SLIDE_W - M - 6.8, 3.4, [
    ("Columns", {"bold": True, "color": ACCENT}),
    "Order: Row ID, Order ID, Order Date, Ship Date, Ship Mode",
    "Customer: Customer ID, Customer Name, Segment",
    "Location: Country, City, State, Postal Code, Region",
    "Product: Product ID, Category, Sub-Category, Product Name",
    "Numbers: Sales, Quantity, Discount, Profit",
], size=16, space_after=6)

# ---------- 4. Top 10 rows ----------
s = prs.slides.add_slide(BLANK)
title(s, "First 10 rows of the dataset")
cols = {  # column -> (width in inches, formatter)
    "Order ID": (1.6, str), "Order Date": (1.1, str), "Customer Name": (1.5, str),
    "Segment": (1.0, str), "Region": (0.85, str), "Category": (1.35, str),
    "Sub-Category": (1.25, str), "Sales": (0.95, "${:,.2f}".format),
    "Quantity": (0.85, str), "Discount": (0.85, "{:.0%}".format),
    "Profit": (0.95, lambda v: f"-${-v:,.2f}" if v < 0 else f"${v:,.2f}"),
}
rows = pd.read_csv(ROOT / "reports" / "top10_rows.csv")[list(cols)]
scale = CONTENT_W / sum(w for w, _ in cols.values())
tbl = s.shapes.add_table(len(rows) + 1, len(cols), Inches(M), Inches(1.6),
                         Inches(CONTENT_W), Inches(0.42 * (len(rows) + 1))).table
for j, (name, (w, fmt)) in enumerate(cols.items()):
    tbl.columns[j].width = Inches(w * scale)
    numeric = name in ("Sales", "Quantity", "Discount", "Profit")
    for i in range(len(rows) + 1):
        cell = tbl.cell(i, j)
        cell.margin_left = cell.margin_right = Inches(0.08)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        cell.fill.solid()
        cell.fill.fore_color.rgb = ACCENT if i == 0 else (TINT if i % 2 == 0 else WHITE)
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.RIGHT if numeric else PP_ALIGN.LEFT
        r = p.add_run()
        r.text = name if i == 0 else fmt(rows.iloc[i - 1][name])
        r.font.name, r.font.size, r.font.bold = FONT, Pt(12), i == 0
        r.font.color.rgb = WHITE if i == 0 else (RED if name == "Profit" and rows.iloc[i - 1][name] < 0 else INK)
for i in range(len(rows) + 1):
    tbl.rows[i].height = Inches(0.42)
text(s, M, 6.4, CONTENT_W, 0.6,
     "Showing 11 of the 21 columns. Not shown: Row ID, Ship Date, Ship Mode, Customer ID, Country, "
     "City, State, Postal Code, Product ID, Product Name.", size=12, color=MUTED)

# ---------- 5. Data prep & methods ----------
s = prs.slides.add_slide(BLANK)
title(s, "Data prep and methods")
steps = [
    ("Load", "pd.read_csv with encoding=\"latin-1\". Check shape (9,994 × 21), missing values, duplicates."),
    ("Prepare", "Parse Order Date and Ship Date to datetimes. Add Year and Ship Days columns."),
    ("Aggregate", "groupby, resample, and pivot_table by month, year, category, region, and discount."),
    ("Visualize", "6 Matplotlib/Seaborn charts: line, pie, bar, grouped bar. Each has a title, axis labels, and a legend where needed."),
]
step_w = (CONTENT_W - 3 * 0.3) / 4
for i, (head, body) in enumerate(steps):
    x = M + i * (step_w + 0.3)
    card(s, x, 1.7, step_w, 3.6)
    number_dot(s, x + 0.3, 2.0, i + 1)
    text(s, x + 0.3, 2.7, step_w - 0.6, 0.5, head, size=20, bold=True)
    text(s, x + 0.3, 3.3, step_w - 0.6, 1.9, body, size=15)
text(s, M, 5.7, CONTENT_W, 1.2, [
    "The data was already clean (0 missing values, 0 duplicate rows), so prep focused on dates and derived columns.",
    "The script asserts the shape, no nulls, no duplicates, and no ship date before its order date.",
], size=16, bullets=True)

# ---------- 6-10. Charts ----------
chart_slide("Sales grew 51% from 2014 to 2017, peaking every fall",
            "01_monthly_sales_profit.png", "+51%", "sales growth, $484K (2014) to $733K (2017)", [
                "Every year peaks in Sep–Dec and dips in Jan–Feb",
                "Best calendar month: November. Worst: February",
            ])

s = prs.slides.add_slide(BLANK)
title(s, "Sales are split evenly, and all three categories grew")
image(s, FIGS / "02_sales_share_by_category.png", M, 1.5, 4.6, 4.0)
image(s, FIGS / "06_yearly_sales_by_category.png", M + 4.9, 1.5, CONTENT_W - 4.9, 4.0)
text(s, M, 5.85, CONTENT_W, 1.2, [
    "Share of sales: Technology 36%, Furniture 32%, Office Supplies 31%",
    "All three grew in 2016–2017, but Furniture earns only a 2.5% margin (Technology 17.4%, Office Supplies 17.0%)",
], size=16, bullets=True, space_after=8)

chart_slide("Tables, Bookcases, and Supplies lose money",
            "03_profit_by_subcategory.png", "-$17.7K", "total profit on Tables, the biggest loss", [
                "Bookcases -$3.5K, Supplies -$1.2K",
                "Top earners: Copiers $55.6K, Phones $44.5K, Accessories $41.9K",
            ], value_color=RED)

chart_slide("West earns the best margin, Central the worst",
            "04_sales_profit_by_region.png", "14.9%", "profit margin in the West", [
                "East 13.5%, South 11.9%, Central 7.9%",
                "Central outsells South ($501K vs $392K) but earns less profit ($40K vs $47K)",
            ])

chart_slide("Discounts of 30% or more turn orders unprofitable",
            "05_profit_by_discount.png", "30%", "discount where average profit per order line turns negative", [
                "0–20% discounts: +$25 to +$96 per line",
                "50% discount: -$311 per line, the worst level",
            ])

# ---------- 11. Conclusions ----------
s = prs.slides.add_slide(BLANK)
title(s, "Conclusions and recommendations")
half = (CONTENT_W - 0.3) / 2
for x, head, points in [
    (M, "What the data shows", [
        "Sales grew 51% in four years, with a strong Sep–Dec peak",
        "Technology and Office Supplies earn ~17% margins; Furniture earns 2.5%",
        "Tables (-$17.7K), Bookcases, and Supplies lose money",
        "Average profit per line turns negative at 30%+ discounts",
    ]),
    (M + half + 0.3, "What to do next", [
        "Cap discounts at 20%; require approval above that",
        "Reprice or cut discounts on Tables and Bookcases",
        "Stock up and staff for the Sep–Dec rush",
        "Study Central's 7.9% margin, the lowest region",
    ]),
]:
    card(s, x, 1.6, half, 4.3)
    text(s, x + 0.4, 1.9, half - 0.8, 0.5, head, size=22, bold=True, color=ACCENT)
    text(s, x + 0.4, 2.6, half - 0.8, 3.1, points, size=17, bullets=True, space_after=14)
text(s, M, 6.25, CONTENT_W, 0.6, "Bottom line: sales are growing, but deep discounts and Furniture eat the profit.",
     size=20, bold=True)

prs.save(OUT)

# ---------- Self-check: reopen and verify ----------
chk = Presentation(OUT)
slides = list(chk.slides)
assert 10 <= len(slides) <= 12, f"{len(slides)} slides"
embedded = {sh.image.sha1 for sl in slides for sh in sl.shapes if sh.shape_type == MSO_SHAPE_TYPE.PICTURE}
figs = {hashlib.sha1(p.read_bytes()).hexdigest(): p.name for p in FIGS.glob("*.png")}
assert len(figs) == 6 and set(figs) <= embedded, f"missing charts: {[n for h, n in figs.items() if h not in embedded]}"
tables = [sh.table for sl in slides for sh in sl.shapes if sh.has_table]
assert len(tables) == 1 and len(tables[0].rows) == 11, "table must have header + 10 data rows"
for n, sl in enumerate(slides, 1):
    for sh in sl.shapes:
        h = sum(r.height for r in sh.table.rows) if sh.has_table else sh.height
        assert sh.left >= 0 and sh.top >= 0 and sh.left + sh.width <= chk.slide_width \
            and sh.top + h <= chk.slide_height, f"slide {n}: {sh.name} out of bounds"
print(f"OK: {OUT.relative_to(ROOT)} has {len(slides)} slides, all 6 charts embedded, 10-row table, all shapes in bounds")
