import json
import re
from pathlib import Path

import markdown as md_lib
from flask import (Flask, Response, jsonify,
                   render_template, request, send_file, stream_with_context)

from backend.pipeline.generator import (
    generate_report_stream, get_available_model, list_local_models,
)
from backend.pipeline.renderer import save_reports

app = Flask(__name__)
ROOT = Path(__file__).resolve().parent


def _safe(name: str) -> str:
    return re.sub(r"[^\w\-]", "_", name.strip().lower())


# ── Main UI ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    model  = get_available_model()
    models = list_local_models()
    return render_template("index.html", model=model, models=models)


# ── Status API (lets the frontend know which model is active) ────────────────

@app.route("/api/status")
def status():
    model  = get_available_model()
    models = list_local_models()
    return jsonify({"model": model, "models": models, "ready": bool(model)})


# ── Report generation (Server-Sent Events stream) ────────────────────────────

@app.route("/api/generate", methods=["POST"])
def generate():
    data    = request.get_json(force=True)
    company = (data.get("company") or "").strip()

    if not company:
        return jsonify({"error": "Company name is required."}), 400

    model = get_available_model()
    if not model:
        return jsonify({
            "error": "No local model found. Run:  ollama pull llama3.1:8b"
        }), 503

    safe = _safe(company)

    def event_stream():
        accumulated = []
        try:
            # Tell the client which model is running
            yield f"data: {json.dumps({'type': 'model', 'model': model})}\n\n"

            for chunk in generate_report_stream(company):
                accumulated.append(chunk)
                yield f"data: {json.dumps({'type': 'chunk', 'text': chunk})}\n\n"

            # Save markdown
            content = "".join(accumulated)
            md_path = ROOT / "backend" / "data" / "processed" / "md" / f"{safe}_unc.md"
            md_path.parent.mkdir(parents=True, exist_ok=True)
            md_path.write_text(content, encoding="utf-8")

            # Render to HTML for display
            rendered = md_lib.markdown(content, extensions=["tables", "extra", "toc"])

            yield f"data: {json.dumps({'type': 'done', 'html': rendered, 'company': safe, 'md_url': f'/download/{safe}/md', 'pdf_url': f'/download/{safe}/pdf'})}\n\n"

        except Exception as exc:
            msg = str(exc)
            yield f"data: {json.dumps({'type': 'error', 'message': msg})}\n\n"

    headers = {
        "X-Accel-Buffering": "no",
        "Cache-Control":     "no-cache",
        "Connection":        "keep-alive",
    }
    return Response(
        stream_with_context(event_stream()),
        mimetype="text/event-stream",
        headers=headers,
    )


# ── File downloads ────────────────────────────────────────────────────────────

@app.route("/download/<company>/<fmt>")
def download(company, fmt):
    safe = _safe(company)

    if fmt == "md":
        path = ROOT / "backend" / "data" / "processed" / "md" / f"{safe}_unc.md"
        if not path.exists():
            return "Not found", 404
        return send_file(path, as_attachment=True, download_name=f"{safe}_report.md")

    if fmt == "pdf":
        pdf_path = ROOT / "backend" / "data" / "processed" / "pdf" / f"{safe}_unc.pdf"
        if not pdf_path.exists():
            md_path = ROOT / "backend" / "data" / "processed" / "md" / f"{safe}_unc.md"
            if not md_path.exists():
                return "Not found", 404
            _, pdf_path = save_reports(safe, md_path.read_text(encoding="utf-8"))
        return send_file(pdf_path, as_attachment=True, download_name=f"{safe}_report.pdf")

    return "Unknown format", 400


if __name__ == "__main__":
    app.run(debug=True, port=5050)
