"""
restructure.py — Run once from inside nexus-routing-engine/

  python restructure.py

What it does:
  1. Deletes all junk/temp write scripts and stale files
  2. Builds a clean backend / tests / data layout
  3. Writes correct, final versions of every source file
  4. Moves your existing data/raw content into the right place
  5. Runs the tests to confirm everything works
"""

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent

# ──────────────────────────────────────────────────────────────────────────────
# 1.  DELETE JUNK
# ──────────────────────────────────────────────────────────────────────────────

JUNK = [
    "write_report.py",
    "write_sanofi.py",
    "write_sanofi_full.py",
    "fix_nexus.py",
    "main.py",
    "example-profile-sanofi.md",
    "workflow-v1.md",
    "reports",          # old reports/ dir
    "src",              # will be replaced by backend/
]

print("── Step 1: removing junk files ──")
for name in JUNK:
    target = ROOT / name
    if target.exists():
        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink()
        print(f"  deleted  {name}")

# ──────────────────────────────────────────────────────────────────────────────
# 2.  CREATE DIRECTORY TREE
# ──────────────────────────────────────────────────────────────────────────────

print("\n── Step 2: creating directory structure ──")

dirs = [
    "backend/pipeline",
    "backend/config",
    "backend/data/raw",
    "backend/data/processed/md",
    "backend/data/processed/pdf",
    "tests",
]

for d in dirs:
    (ROOT / d).mkdir(parents=True, exist_ok=True)
    print(f"  ok  {d}/")

# ──────────────────────────────────────────────────────────────────────────────
# 3.  MIGRATE EXISTING DATA/RAW  →  backend/data/raw
# ──────────────────────────────────────────────────────────────────────────────

old_raw = ROOT / "data" / "raw"
new_raw = ROOT / "backend" / "data" / "raw"

if old_raw.exists():
    for f in old_raw.glob("*.md"):
        dest = new_raw / f.name
        shutil.copy2(f, dest)
        print(f"\n── Step 3: copied {f.name} → backend/data/raw/ ──")

# Remove old data/ directory
old_data = ROOT / "data"
if old_data.exists():
    shutil.rmtree(old_data)
    print("  removed old data/")

# ──────────────────────────────────────────────────────────────────────────────
# 4.  WRITE BACKEND SOURCE FILES
# ──────────────────────────────────────────────────────────────────────────────

print("\n── Step 4: writing backend source files ──")

# backend/__init__.py
(ROOT / "backend" / "__init__.py").write_text("", encoding="utf-8")

# backend/pipeline/__init__.py
(ROOT / "backend" / "pipeline" / "__init__.py").write_text("", encoding="utf-8")

# ── backend/pipeline/models.py ────────────────────────────────────────────────
(ROOT / "backend" / "pipeline" / "models.py").write_text("""\
\"\"\"Pydantic data models for the Nexus Routing Engine.\"\"\"
from pydantic import BaseModel
from typing import List, Optional


class CorporatePriority(BaseModel):
    \"\"\"A verified corporate focus area extracted from source documents.\"\"\"
    theme: str
    evidence: str
    source_url: str
    confidence: float


class UniversityMatch(BaseModel):
    \"\"\"A validated alignment between a corporate priority and a UNC unit.\"\"\"
    unit_name: str
    level: str  # "university" | "school"
    rationale: str
    source_url: str
    confidence: float


class CompanyProfile(BaseModel):
    \"\"\"Root object holding all extracted priorities and UNC matches.\"\"\"
    company_name: str
    sector: str
    headquarters: Optional[str] = None
    priorities: List[CorporatePriority] = []
    matches: List[UniversityMatch] = []
""", encoding="utf-8")

# ── backend/pipeline/verifier.py ──────────────────────────────────────────────
(ROOT / "backend" / "pipeline" / "verifier.py").write_text("""\
\"\"\"Source-tier verification logic for the Nexus Routing Engine.\"\"\"


def verify_source_tier(source_type: str, sources_config: dict) -> float:
    \"\"\"
    Return a confidence score based on source priority hierarchy.

    Primary sources  → 1.0
    Secondary sources → 0.5
    Unknown sources  → 0.0
    \"\"\"
    if source_type in sources_config.get("primary", []):
        return 1.0
    if source_type in sources_config.get("secondary", []):
        return 0.5
    return 0.0
""", encoding="utf-8")

# ── backend/pipeline/renderer.py ──────────────────────────────────────────────
(ROOT / "backend" / "pipeline" / "renderer.py").write_text("""\
\"\"\"Markdown → PDF renderer for the Nexus Routing Engine.\"\"\"
import markdown
from weasyprint import HTML
from pathlib import Path

CSS = \"\"\"
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
\"\"\"

BASE_DIR = Path(__file__).resolve().parent.parent  # backend/


def save_reports(company: str, content: str) -> tuple[Path, Path]:
    \"\"\"
    Write *content* as both a raw Markdown file and a styled PDF.

    Outputs land in:
      backend/data/processed/md/<company>_unc.md
      backend/data/processed/pdf/<company>_unc.pdf
    \"\"\"
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
""", encoding="utf-8")

# ──────────────────────────────────────────────────────────────────────────────
# 5.  WRITE CONFIG FILES
# ──────────────────────────────────────────────────────────────────────────────

print("  writing config files …")

(ROOT / "backend" / "config" / "sectors.yaml").write_text("""\
biopharma:
  routes: [oncology, immunology, vaccines, neurology, rare_disease]

public_health:
  routes: [epidemiology, health_equity, outcomes_research]

digital_health:
  routes: [ehr, clinical_decision_support, remote_monitoring]

ai_data:
  routes: [machine_learning, nlp, computer_vision, bioinformatics]
""", encoding="utf-8")

(ROOT / "backend" / "config" / "sources.yaml").write_text("""\
primary:
  - sec
  - nih_reporter
  - clinicaltrials
  - pubmed
  - official_company
  - official_unc

secondary:
  - linkedin
  - third_party_bios
  - market_research
""", encoding="utf-8")

(ROOT / "backend" / "config" / "university_map.yaml").write_text("""\
unc_chapel_hill:
  campus_wide:
    - renci
    - biomedical_informatics
    - data_science

  pharmacy:
    - medicinal_chemistry
    - structural_biology
    - chemical_biology

  medicine:
    - translational_research
    - disease_models
    - clinical_trials

  gillings:
    - epidemiology
    - biostatistics
    - public_health_policy

  data_science_society:
    - machine_learning
    - data_engineering
    - health_informatics
""", encoding="utf-8")

# ──────────────────────────────────────────────────────────────────────────────
# 6.  WRITE TESTS
# ──────────────────────────────────────────────────────────────────────────────

print("  writing test files …")

(ROOT / "tests" / "__init__.py").write_text("", encoding="utf-8")

(ROOT / "tests" / "test_models.py").write_text("""\
from backend.pipeline.models import CompanyProfile, CorporatePriority, UniversityMatch


def test_company_profile_defaults():
    p = CompanyProfile(company_name="TestCo", sector="biopharma")
    assert p.priorities == []
    assert p.matches == []


def test_corporate_priority():
    cp = CorporatePriority(
        theme="oncology", evidence="test", source_url="http://x.com", confidence=0.9
    )
    assert cp.theme == "oncology"
    assert cp.confidence == 0.9


def test_university_match():
    m = UniversityMatch(
        unit_name="renci", level="university",
        rationale="theme match", source_url="http://x.com", confidence=1.0,
    )
    assert m.level == "university"
""", encoding="utf-8")

(ROOT / "tests" / "test_verifier.py").write_text("""\
from backend.pipeline.verifier import verify_source_tier

CFG = {"primary": ["pubmed", "sec"], "secondary": ["linkedin"]}


def test_primary_source():
    assert verify_source_tier("pubmed", CFG) == 1.0


def test_secondary_source():
    assert verify_source_tier("linkedin", CFG) == 0.5


def test_unknown_source():
    assert verify_source_tier("random_blog", CFG) == 0.0
""", encoding="utf-8")

(ROOT / "tests" / "test_renderer.py").write_text("""\
from backend.pipeline.renderer import save_reports


def test_save_reports_creates_files(tmp_path, monkeypatch):
    # Redirect output to tmp_path so we don't pollute the real data dir
    import backend.pipeline.renderer as r
    monkeypatch.setattr(r, "BASE_DIR", tmp_path)

    md_path, pdf_path = save_reports("test_company", "# Hello World")

    assert md_path.exists()
    assert pdf_path.exists()
    assert "# Hello World" in md_path.read_text(encoding="utf-8")
    assert pdf_path.stat().st_size > 0
""", encoding="utf-8")

# ──────────────────────────────────────────────────────────────────────────────
# 7.  WRITE generate.py  (CLI entry point, replaces nexus_route.py)
# ──────────────────────────────────────────────────────────────────────────────

(ROOT / "generate.py").write_text("""\
\"\"\"
CLI entry point for the Nexus Routing Engine.

Usage:
    python generate.py --company sanofi

Reads:   backend/data/raw/<company>.md
Outputs: backend/data/processed/md/<company>_unc.md
         backend/data/processed/pdf/<company>_unc.pdf
\"\"\"
import argparse
from pathlib import Path

from backend.pipeline.renderer import save_reports


def main() -> None:
    parser = argparse.ArgumentParser(description="Nexus Routing Engine")
    parser.add_argument(
        "--company", required=True,
        help="Filename stem inside backend/data/raw/  (no .md extension)",
    )
    args = parser.parse_args()

    raw_path = Path(__file__).parent / "backend" / "data" / "raw" / f"{args.company}.md"

    if not raw_path.exists():
        print(f"ERROR: source file not found → {raw_path}")
        raise SystemExit(1)

    content = raw_path.read_text(encoding="utf-8")
    print(f"Loaded {len(content):,} chars from {raw_path.name}")

    md_path, pdf_path = save_reports(args.company, content)

    print(f"✓  MD  → {md_path}  ({md_path.stat().st_size:,} bytes)")
    print(f"✓  PDF → {pdf_path}  ({pdf_path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
""", encoding="utf-8")

# ──────────────────────────────────────────────────────────────────────────────
# 8.  WRITE requirements.txt
# ──────────────────────────────────────────────────────────────────────────────

(ROOT / "requirements.txt").write_text("""\
pydantic>=2.0
PyYAML>=6.0
requests>=2.31
beautifulsoup4>=4.12
pandas>=2.0
jinja2>=3.1
markdown>=3.5
weasyprint>=60.0
pytest>=9.0
""", encoding="utf-8")

# ──────────────────────────────────────────────────────────────────────────────
# 9.  WRITE .gitignore
# ──────────────────────────────────────────────────────────────────────────────

(ROOT / ".gitignore").write_text("""\
venv/
__pycache__/
*.pyc
*.pyo
.DS_Store
.pytest_cache/
backend/data/processed/
""", encoding="utf-8")

# ──────────────────────────────────────────────────────────────────────────────
# 10. REMOVE OLD nexus_route.py (replaced by generate.py)
# ──────────────────────────────────────────────────────────────────────────────

old_nr = ROOT / "nexus_route.py"
if old_nr.exists():
    old_nr.unlink()
    print("\n── Step 5: removed old nexus_route.py (replaced by generate.py) ──")

# ──────────────────────────────────────────────────────────────────────────────
# 11. RUN TESTS
# ──────────────────────────────────────────────────────────────────────────────

print("\n── Step 6: running tests ──")
result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/", "-v"],
    cwd=ROOT,
)

# ──────────────────────────────────────────────────────────────────────────────
# 12. PRINT FINAL TREE
# ──────────────────────────────────────────────────────────────────────────────

print("\n── Final structure ──")
subprocess.run(
    ["tree", "-I", "venv|__pycache__|*.pyc|*.dist-info|*.egg-info", "-L", "4"],
    cwd=ROOT,
)

print("""
═══════════════════════════════════════════════════════
  Done.  To generate a report:

    python generate.py --company sanofi

  To add a new company:
    1. Create  backend/data/raw/<company>.md
    2. Run     python generate.py --company <company>
═══════════════════════════════════════════════════════
""")