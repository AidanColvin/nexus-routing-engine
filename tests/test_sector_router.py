"""Test sector routing and matching models."""
from src.models import UniversityMatch

def test_university_match_creation():
    """Test that a match object stores unit and level data."""
    match = UniversityMatch(
        unit_name="renci",
        level="university",
        rationale="theme match",
        source_url="http://test.com",
        confidence=1.0
    )
    assert match.unit_name == "renci"
    assert match.level == "university"
