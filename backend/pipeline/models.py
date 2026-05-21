"""Pydantic data models for the Nexus Routing Engine."""
from pydantic import BaseModel
from typing import List, Optional


class CorporatePriority(BaseModel):
    """A verified corporate focus area extracted from source documents."""
    theme: str
    evidence: str
    source_url: str
    confidence: float


class UniversityMatch(BaseModel):
    """A validated alignment between a corporate priority and a UNC unit."""
    unit_name: str
    level: str  # "university" | "school"
    rationale: str
    source_url: str
    confidence: float


class CompanyProfile(BaseModel):
    """Root object holding all extracted priorities and UNC matches."""
    company_name: str
    sector: str
    headquarters: Optional[str] = None
    priorities: List[CorporatePriority] = []
    matches: List[UniversityMatch] = []
