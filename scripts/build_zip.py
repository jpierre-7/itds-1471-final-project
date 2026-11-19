"""Build the Canvas submission ZIP. Run from anywhere: python scripts/build_zip.py"""
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "ITDS1471_FinalProject_JohnPierre.zip"
FILES = [
    "data/raw/Sample - Superstore.csv",
    "src/analysis.py",
    "reports/report.docx",
    "reports/presentation.pptx",
    "requirements.txt",
    "README.md",
    *sorted(str(p.relative_to(ROOT)) for p in (ROOT / "reports" / "figures").glob("*.png")),
]

missing = [f for f in FILES if not (ROOT / f).exists()]
assert not missing, f"missing files: {missing}"

# Keep folder structure so `python src/analysis.py` runs right after unzipping.
with ZipFile(OUT, "w", ZIP_DEFLATED) as z:
    for f in FILES:
        z.write(ROOT / f, f)
print(f"Wrote {OUT.name} ({OUT.stat().st_size / 1e6:.1f} MB, {len(FILES)} files)")
