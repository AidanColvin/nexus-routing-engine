"""Test data models and extraction rules."""
from src.models import CorporatePriority, CompanyProfile

def test_corporate_priority_creation():
    """Test that a priority object stores data correctly."""
    priority = CorporatePriority(
        theme="AI",
        evidence="Testing data",
        source_url="http://test.com",
        confidence=0.9
    )
    assert priority.theme == "AI"
    assert priority.confidence == 0.9

def test_company_profile_lists():
    """Test that a new profile starts with empty lists."""
    profile = CompanyProfile(company_name="TestCo", sector="tech")
    assert profile.priorities == []
    assert profile.matches == []
