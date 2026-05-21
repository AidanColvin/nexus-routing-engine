"""Markdown → PDF renderer for the Nexus Routing Engine."""
import markdown
from weasyprint import HTML
from pathlib import Path

CSS = """
body {
  font-family: Helvetica, Arial, sans-serif;
  font-size: 11pt;
  line-height: 1.6;
  color: #222;
  margin: 40px 50px;
}
h1 {
  color: #002D72;
  border-bottom: 2px solid #002D72;
  padding-bottom: 6px;
  text-transform: uppercase;
}
h2 {
  color: #1a569d;
  margin-top: 28px;
  border-bottom: 1px solid #ccc;
  padding-bottom: 4px;
}
h3  { color: #333; margin-top: 20px; }
h4  { color: #555; font-style: italic; margin-top: 16px; }
hr  { border: 0; border-top: 1px solid #ddd; margin: 20px 0; }
ul  { padding-left: 20px; }
li  { margin-bottom: 6px; }
table { border-collapse: collapse; width: 100%; margin-top: 16px; }
th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
th  { background: #f5f5f5; font-weight: bold; }
"""

BASE_DIR = Path(__file__).resolve().parent.parent  # backend/


def save_reports(company: str, content: str) -> tuple[Path, Path]:
    """
    Write *content* as both a raw Markdown file and a styled PDF.

    Outputs land in:
      backend/data/processed/md/<company>_unc.md
      backend/data/processed/pdf/<company>_unc.pdf
    """
    md_dir  = BASE_DIR / "data" / "processed" / "md"
    pdf_dir = BASE_DIR / "data" / "processed" / "pdf"
    md_dir.mkdir(parents=True, exist_ok=True)
    pdf_dir.mkdir(parents=True, exist_ok=True)

    md_path  = md_dir  / f"{company}_unc.md"
    pdf_path = pdf_dir / f"{company}_unc.pdf"

    # Raw Markdown
    md_path.write_text(content, encoding="utf-8")

    # Styled PDF
    html_body = markdown.markdown(content, extensions=["tables"])
    full_html = (
        '<!DOCTYPE html><html><head><meta charset="utf-8">'
        f"<style>{CSS}</style></head>"
        f"<body>{html_body}</body></html>"
    )
    HTML(string=full_html).write_pdf(pdf_path)

    return md_path, pdf_path
