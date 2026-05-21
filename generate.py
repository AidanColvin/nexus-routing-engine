"""
CLI entry point for the Nexus Routing Engine.

Usage:
    python generate.py --company sanofi

Reads:   backend/data/raw/<company>.md
Outputs: backend/data/processed/md/<company>_unc.md
         backend/data/processed/pdf/<company>_unc.pdf
"""
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
