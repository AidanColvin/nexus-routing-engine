import pytest
from pathlib import Path
from src.models import CompanyProfile
from src.renderer import generate_html, save_reports
from src.verifier import verify_source_tier

def test_models_functionality():
    p = CompanyProfile(company_name="Test", sector="tech")
    assert p.company_name == "Test"

def test_verifier_functionality():
    cfg = {"primary": ["test"]}
    assert verify_source_tier("test", cfg) == 1.0

def test_renderer_functionality():
    html = generate_html("# Title")
    assert "h1" in html

def test_pipeline_integration():
    # Execute full pipeline
    md_content = "# Integration Test"
    md_path, pdf_path = save_reports("integration_test", md_content)
    
    # Verify file paths
    assert md_path.exists()
    assert pdf_path.exists()
    
    # Verify folder structure
    assert md_path.parent.name == "md"
    assert pdf_path.parent.name == "pdf"
    
    print(f"\nPipeline successfully saved files to: {md_path.parent.parent}")
