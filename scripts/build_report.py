"""Build reports/report.docx from the charts in reports/figures/.

Run from the repo root:  uvx --with python-docx python -I scripts/build_report.py
Every number below comes from the printed output of src/analysis.py.
"""
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parent.parent
FIGS = ROOT / "reports" / "figures"
OUT = ROOT / "reports" / "report.docx"

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Inches(8.5), Inches(11)
for side in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
    setattr(sec, side, Inches(1))

normal = doc.styles["Normal"]
normal.font.name = "Calibri"
normal.font.size = Pt(11)
normal.paragraph_format.space_after = Pt(8)
normal.paragraph_format.line_spacing = 1.15


def h(text, level=1):
    doc.add_heading(text, level=level)


def p(*parts):
    """Paragraph from plain strings; a ("text", "b"|"code") tuple formats that run."""
    para = doc.add_paragraph()
    for part in parts:
        text, fmt = part if isinstance(part, tuple) else (part, "")
        run = para.add_run(text)
        run.bold = fmt == "b"
        if fmt == "code":
            run.font.name = "Consolas"
    return para


def items(lines, numbered=False):
    for n, line in enumerate(lines, 1):
        para = doc.add_paragraph(style="List Bullet")
        if numbered:  # Word's "List Number" never restarts, so number by hand
            para.style = doc.styles["Normal"]
            para.paragraph_format.left_indent = Inches(0.25)
            para.paragraph_format.first_line_indent = Inches(-0.25)
            para.paragraph_format.space_after = Pt(4)
            para.add_run(f"{n}.\t")
        if isinstance(line, tuple):
            para.add_run(line[0]).bold = True
            para.add_run(line[1])
        else:
            para.add_run(line)


fig_no = 0


def figure(name, caption, width=5.3):
    global fig_no
    fig_no += 1
    pic = doc.add_paragraph()
    pic.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pic.paragraph_format.keep_with_next = True
    pic.add_run().add_picture(str(FIGS / name), width=Inches(width))
    cap = doc.add_paragraph(f"Figure {fig_no}. {caption}", style="Caption")
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER


table_no = 0


def table(caption, header, rows):
    global table_no
    table_no += 1
    cap = doc.add_paragraph(f"Table {table_no}. {caption}", style="Caption")
    cap.paragraph_format.keep_with_next = True
    t = doc.add_table(rows=1, cols=len(header), style="Light List Accent 1")
    for cell, text in zip(t.rows[0].cells, header):
        cell.text = text
    for row in rows:
        for i, (cell, text) in enumerate(zip(t.add_row().cells, row)):
            cell.text = text
            if i:  # numbers right-aligned, first column left
                cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
    for i, cell in enumerate(t.rows[0].cells):
        if i:
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
    for row in t.rows[:-1]:  # keep the table on one page
        for cell in row.cells:
            cell.paragraphs[0].paragraph_format.keep_with_next = True
    doc.add_paragraph()


def page_number_footer(section):
    para = section.footer.paragraphs[0]
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = para.add_run()
    for tag, text in (("begin", None), (None, "PAGE"), ("end", None)):
        if tag:
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), tag)
        else:
            el = OxmlElement("w:instrText")
            el.set(qn("xml:space"), "preserve")
            el.text = text
        run._r.append(el)


# ---------- Title page ----------
for _ in range(6):
    doc.add_paragraph()
title = doc.add_paragraph("Superstore Sales Analysis", style="Title")
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
sub = doc.add_paragraph("Where the profit comes from and where it leaks out, 2014–2017", style="Subtitle")
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
for _ in range(4):
    doc.add_paragraph()
for line in ("John Pierre",
             "ITDS 1471: Data Analysis with Python",
             "Houston Community College",
             "December 5, 2026"):
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    para.paragraph_format.space_after = Pt(2)
    run = para.add_run(line)
    run.font.size = Pt(13)
    run.font.color.rgb = RGBColor(0x40, 0x40, 0x40)

# Body starts on a new section so the title page has no page number.
body = doc.add_section(WD_SECTION.NEW_PAGE)
body.footer.is_linked_to_previous = False
page_number_footer(body)

# ---------- 1. Introduction ----------
h("1. Introduction")
p("A retail company records every product it sells: what it was, who bought it, where it "
  "shipped, what discount it got, and whether the sale made or lost money. For this project I "
  "acted as a junior data analyst handed four years of that kind of data, with one job: find "
  "out where the profit comes from and where it leaks out.")
p("I loaded the data with Pandas, summarized it by time, product, region, and discount, and "
  "built six charts with Matplotlib and Seaborn. Each chart below gets a short explanation of "
  "what it shows and why a manager should care. The report ends with conclusions, four "
  "recommendations, and the limits of what this data can tell us.")

# ---------- 2. Dataset ----------
h("2. Dataset")
p("The data is the Superstore Sales dataset posted on Kaggle by Vivek Chowdhury "
  "(https://www.kaggle.com/datasets/vivek468/superstore-dataset-final). It is a single CSV "
  "file, ", ("Sample - Superstore.csv", "code"), ", about 2.3 MB. Tableau first published "
  "it as sample data, and Kaggle lists the license as \"Other,\" so I'm using it for "
  "coursework only.")
p("Each row is one order line, meaning one product inside one order. The file has ",
  ("9,994 rows and 21 columns", "b"), " covering 5,009 orders from 793 customers. Order "
  "dates run from January 3, 2014 to December 30, 2017, and every sale is in the United "
  "States. The 21 columns fall into five groups:")
items([
    ("Order: ", "Row ID, Order ID, Order Date, Ship Date, Ship Mode"),
    ("Customer: ", "Customer ID, Customer Name, Segment (Consumer, Corporate, Home Office)"),
    ("Location: ", "Country, City, State, Postal Code, Region (Central, East, South, West)"),
    ("Product: ", "Product ID, Category, Sub-Category, Product Name"),
    ("Numbers: ", "Sales, Quantity, Discount, Profit"),
])
p("The file was already clean: no missing values and no duplicate rows. The one problem was "
  "the text encoding. The file is saved as latin-1, not UTF-8, so a plain ",
  ("pd.read_csv()", "code"), " call stops with a UnicodeDecodeError until you pass ",
  ("encoding=\"latin-1\"", "code"), ".")

# ---------- 3. Questions ----------
h("3. Questions")
p("I set out to answer three questions:")
items([
    "How did sales and profit trend from 2014 to 2017, and is there a seasonal pattern?",
    "Which categories and sub-categories make money, and which lose it?",
    "Do bigger discounts lead to lower profit?",
], numbered=True)
p("I also compared the four regions, since a region with good sales and weak profit would "
  "send me back to questions 2 and 3 for the reason.")

# ---------- 4. Data preparation and methods ----------
h("4. Data Preparation and Methods")
p("All of the work is in one script, ", ("analysis.py", "code"), ", which is included with "
  "this report. It runs top to bottom in these steps:")
items([
    ("Load and check. ", "Read the CSV with pd.read_csv(encoding=\"latin-1\"). Assert "
     "statements confirm the shape is 9,994 × 21, that df.isna() finds no missing values, and "
     "that df.duplicated() finds no duplicate rows, so the script stops if the file ever "
     "changes."),
    ("Fix the dates. ", "Convert Order Date and Ship Date from text to datetimes with "
     "pd.to_datetime(format=\"%m/%d/%Y\")."),
    ("Add two columns. ", "Year comes from the order date. Ship Days is the ship date minus "
     "the order date; another assert makes sure no order shipped before it was placed."),
    ("Summarize. ", "resample(\"MS\") gives monthly totals; groupby() gives totals by year, "
     "category, sub-category, region, and discount level; pct_change() gives year-over-year "
     "growth; pivot_table() builds the year-by-category grid; and Series.corr() measures how "
     "discount and profit move together."),
    ("Chart and save. ", "Six charts with Matplotlib and Seaborn, each with a title, axis "
     "labels, and a legend where there is more than one series. Red always marks a loss. The "
     "script saves every chart as a PNG and prints every number used in this report."),
])
p("Throughout the report, ", ("margin", "b"), " means profit divided by sales. A 12.5% margin "
  "means the company kept 12.5 cents of profit from each dollar of sales.")

# ---------- 5. Analysis ----------
h("5. Analysis")
p("Table 1 gives the headline numbers before breaking them down chart by chart.")
table("Headline numbers, 2014–2017", ["Measure", "Value"], [
    ["Total sales", "$2,297,201"],
    ["Total profit", "$286,397"],
    ["Profit margin", "12.5%"],
    ["Order lines that lost money", "18.7%"],
    ["Orders / customers", "5,009 / 793"],
    ["Sales share by segment", "Consumer 50.6%, Corporate 30.7%, Home Office 18.7%"],
    ["Average days from order to ship", "4.0"],
])
p("Almost one order line in five lost money. The rest of this section looks for where those "
  "losses sit.")

h("5.1 Sales and profit over time", 2)
figure("01_monthly_sales_profit.png",
       "Monthly sales (top) and monthly profit (bottom), January 2014 to December 2017.")
p("Yearly sales slipped 2.8% in 2015 (from $484,247 to $470,533), then grew 29.5% in 2016 "
  "to $609,206 and another 20.4% in 2017 to $733,215. Profit went up every year, even in "
  "2015, rising from $49,544 to $93,439. The same seasonal shape repeats each year: sales "
  "jump in September, dip in October, and peak in November and December, while January and "
  "February are the slowest months. Across all four years November is the best month and "
  "February the worst. The profit line is much noisier than sales. It fell below zero twice "
  "(July 2014 and January 2015), and November 2016 brought in about $79K of sales but only "
  "about $4K of profit. For planning, this means stock and staff should be ready for the "
  "fall rush, and a big sales month doesn't automatically mean a good profit month.")

h("5.2 Share of sales by category", 2)
figure("02_sales_share_by_category.png", "Share of total sales by product category.",
       width=3.6)
p("On sales alone, the three categories look evenly matched: Technology brings in 36.4%, "
  "Furniture 32.3%, and Office Supplies 31.3%. Table 2 adds profit, and the picture changes. "
  "Furniture sells almost as much as the other two but keeps only 2.5 cents of each dollar, "
  "so it produces about 6% of total profit from about a third of total sales.")
table("Sales, profit, and margin by category",
      ["Category", "Sales", "Profit", "Margin"], [
          ["Technology", "$836,154", "$145,455", "17.4%"],
          ["Furniture", "$742,000", "$18,451", "2.5%"],
          ["Office Supplies", "$719,047", "$122,491", "17.0%"],
      ])

h("5.3 Profit by sub-category", 2)
figure("03_profit_by_subcategory.png",
       "Total profit for each of the 17 sub-categories, 2014–2017. Red bars lost money.")
p("Three of the 17 sub-categories lost money over the four years: ",
  ("Tables (-$17,725), Bookcases (-$3,473), and Supplies (-$1,189)", "b"),
  ". Tables and Bookcases are both Furniture, which explains most of Furniture's weak "
  "margin; without those two, Furniture's profit would be about $39,600 instead of $18,451. "
  "The top earners all sit in Technology: Copiers ($55,618), Phones ($44,516), and "
  "Accessories ($41,937). The losses are concentrated in a short list of product lines, "
  "which makes them easier to act on than a problem spread across the whole catalog.")

h("5.4 Sales and profit by region", 2)
figure("04_sales_profit_by_region.png", "Total sales and total profit by region.")
p("The West leads on both measures, with $725,458 in sales and $108,418 in profit (14.9% "
  "margin), followed by the East at 13.5%. Central is the weak spot. It sold about $110,000 "
  "more than the South ($501,240 vs. $391,722) yet made about $7,000 less profit ($39,706 "
  "vs. $46,749), for the lowest margin of any region at 7.9%. The South sits at 11.9%. This "
  "chart shows that Central has a problem but not what causes it. Discount levels and "
  "product mix are where I would look first, since those two drive profit everywhere else in "
  "this data.")

h("5.5 Discount and profit", 2)
figure("05_profit_by_discount.png",
       "Average profit per order line at each discount level. Red bars are average losses.")
p("Each bar is the average profit of every order line sold at that discount. Lines with no "
  "discount earn $67 on average, and lines at 10% earn $96. At 15% and 20% the average drops "
  "to about $25. Starting at ", ("30% off, every discount level loses money", "b"),
  " on average, and the worst is 50%, at -$311 per line. The correlation between discount "
  "and profit across all 9,994 lines is -0.22. That is a weak negative relationship: "
  "discount alone doesn't predict whether one particular line makes money, but the averages "
  "show a clear break between 20% and 30%. One caution is that the levels are not equally "
  "common. Most lines sold at 0% or 20%, while levels like 32% and 45% cover only a few dozen "
  "lines or fewer, so their bars can swing more.")

h("5.6 Yearly sales by category", 2)
figure("06_yearly_sales_by_category.png", "Yearly sales for each category, 2014–2017.")
p("All three categories grew in 2016 and again in 2017. 2015 was mixed: Furniture rose from "
  "$157K to $171K while Technology and Office Supplies both fell. Over the full four years, "
  "Technology grew from $175K to $272K (about 55%) and Office Supplies from $152K to $246K "
  "(about 62%), but Furniture only went from $157K to $215K (about 37%). Because Furniture "
  "grew the slowest, the low-margin category is a slightly smaller share of the business in "
  "2017 than it was in 2014. That helps profit, but it is happening by accident rather than "
  "by plan.")

# ---------- 6. Conclusion ----------
h("6. Conclusion")
p("The Superstore is growing and profitable. Sales rose 51% from 2014 to 2017 after a small "
  "dip in 2015, profit rose every year, and the company kept 12.5% of sales as profit. Here "
  "is how the analysis answers the three questions:")
items([
    ("Trend and season. ", "Sales climbed steadily after 2015, with the strongest months from "
     "September through December and the weakest in January and February."),
    ("Winners and losers. ", "Technology (17.4% margin) and Office Supplies (17.0%) carry the "
     "profit. Furniture sells nearly as much but earns a 2.5% margin, mostly because Tables "
     "and Bookcases lose money."),
    ("Discounts. ", "Yes, past a point. Order lines at 20% off or less make money on average, "
     "and every level from 30% up loses money. The correlation is weak (-0.22), so discount is "
     "one cause of losses among several, not the only one."),
], numbered=True)
p("The bigger story is that 18.7% of order lines lose money, and those losses are not random. "
  "They cluster in deep discounts, in two Furniture sub-categories, and in the Central "
  "region, which gives the company specific places to start.")

# ---------- 7. Recommendations ----------
h("7. Recommendations")
items([
    ("Cap standard discounts at 20%. ", "Every level at 20% or below makes money on average "
     "and every level at 30% or above loses it. Any discount over 20% should need a manager's "
     "approval."),
    ("Fix or cut Tables and Bookcases. ", "Together they lost $21,198. Check what discounts "
     "these items usually sell at and whether they lose money even at full price. Reprice the "
     "products that can be saved and drop the ones that can't."),
    ("Find out why Central's margin is 7.9%. ", "Compare Central's discount levels and product "
     "mix against the West (14.9%). If Central discounts more heavily, the 20% cap above "
     "should close part of the gap."),
    ("Build the fall season around Technology. ", "September through December are the biggest "
     "sales months, and Technology has the highest margin and the three most profitable "
     "sub-categories. Stock up on Copiers, Phones, and Accessories for the fall and keep "
     "those promotions at 20% off or less."),
], numbered=True)

# ---------- 8. Limitations ----------
h("8. Limitations")
p(("Sample data. ", "b"), "This is a Tableau demo dataset, so it probably doesn't describe a "
  "real company. The methods carry over to real sales data, but the specific numbers "
  "shouldn't be used for real business decisions.")
p(("Four years only. ", "b"), "The data stops at the end of 2017. Four Novembers is a small "
  "base for a seasonal pattern, and nothing here says what happened after 2017.")
p(("Correlation is not causation. ", "b"), "The discount chart shows that deep discounts and "
  "losses go together. It doesn't prove the discount caused the loss. A store might put its "
  "deepest discounts on products that were already losing money, such as Tables, in which "
  "case the discount is a symptom. Testing a discount cap in one region before rolling it "
  "out would answer that question.")
p(("No cost breakdown. ", "b"), "The file gives one Profit number per line. Product cost, "
  "shipping cost, and returns aren't listed separately, so I can't say which of them makes a "
  "line lose money.")

doc.save(OUT)
print(f"saved {OUT.relative_to(ROOT)}  ({fig_no} figures, {table_no} tables)")
