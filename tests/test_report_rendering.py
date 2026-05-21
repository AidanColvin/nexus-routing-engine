"""Test the final markdown and pdf report generation."""
import pytest
from pathlib import Path
from src.renderer import save_reports

def test_pipeline_builds_files(tmp_path):
    """Test that the pipeline writes both MD and PDF files."""
    # Define temp paths
    temp_dir = tmp_path / "processed"
    
    # Run the save_reports function
    md_path, pdf_path = save_reports("TestCorp", "# TestCorp Report", output_dir=str(temp_dir))
    
    assert md_path.exists()
    assert pdf_path.exists()
    assert "# TestCorp Report" in md_path.read_text()
