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
