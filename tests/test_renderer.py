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
