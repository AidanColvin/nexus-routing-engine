from flask import Flask, render_template, request, jsonify, send_file
from pathlib import Path
import markdown as md_lib
import re

from src.renderer import save_reports

app = Flask(__name__)


def _safe_company_name(name: str) -> str:
    return re.sub(r"[^\w\-]", "_", name.strip().lower())


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.get_json(force=True)
    company = (data.get("company") or "").strip()
    content = (data.get("content") or "").strip()

    if not company:
        return jsonify({"error": "Company name is required."}), 400
    if not content:
        return jsonify({"error": "Report content is required."}), 400

    safe = _safe_company_name(company)

    try:
        save_reports(safe, content)
        rendered_html = md_lib.markdown(
            content, extensions=["tables", "extra", "toc"]
        )
        return jsonify(
            {
                "html": rendered_html,
                "company": safe,
                "md_url": f"/download/{safe}/md",
                "pdf_url": f"/download/{safe}/pdf",
            }
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/download/<company>/<fmt>")
def download(company, fmt):
    safe = _safe_company_name(company)
    if fmt == "md":
        path = Path(f"data/processed/md/{safe}_unc.md")
        if not path.exists():
            return "Not found", 404
        return send_file(path.resolve(), as_attachment=True, download_name=f"{safe}_report.md")
    if fmt == "pdf":
        path = Path(f"data/processed/pdf/{safe}_unc.pdf")
        if not path.exists():
            return "Not found", 404
        return send_file(path.resolve(), as_attachment=True, download_name=f"{safe}_report.pdf")
    return "Unknown format", 400


if __name__ == "__main__":
    app.run(debug=True, port=5050)
