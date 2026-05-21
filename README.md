# Nexus Routing Engine

Evidence-first workflow engine for generating UNC-Chapel Hill partnership reports from company and university sources.

The system ingests company and institutional materials, extracts structured entities, routes them through sector-specific alignment logic, verifies each claim against prioritized sources, and renders a citation-backed report with confidence annotations [cite:5].

## Overview

Nexus Routing Engine is designed to produce highly specific, source-grounded reports that map corporate strategy to UNC-Chapel Hill’s overall research ecosystem and to school-level units such as Pharmacy, Medicine, and Gillings. The system is optimized for accuracy, traceability, and repeatability rather than broad qualitative matching [cite:5].

Each report is built from a standardized evidence pipeline so that every claim can be traced to a source category and every alignment can be justified with structured metadata. The workflow is intentionally modular so new sectors, new universities, or new source connectors can be added without rewriting the core engine [cite:5].

## Features

- Company profile ingestion from filings, press releases, investor decks, websites, and public databases.
- Corporate priority extraction for therapeutic areas, technology platforms, business strategy, and partnership signals.
- UNC-CH mapping at two levels: campus-wide capabilities and school-specific alignment.
- Source-ranking and verification to prevent unsupported claims.
- Structured markdown output with inline citations and confidence labels.
- Configurable sector routing for life sciences, public health, AI, business, and other domains [cite:5].

## Architecture

The pipeline is organized into five stages:

1. **Ingestion**  
   Collects company profiles, filings, press releases, university pages, grant records, and research database outputs.

2. **Extraction**  
   Identifies entities such as executives, therapeutic programs, research themes, grants, labs, centers, and institutional units.

3. **Routing**  
   Maps the company into a sector-specific alignment path, such as biopharma, digital health, public health, or AI.

4. **Verification**  
   Validates each claim against prioritized sources, including official corporate materials, `.edu` domains, `.gov` databases, and peer-reviewed literature.

5. **Report Rendering**  
   Produces a structured report in markdown or PDF with inline citations and confidence annotations [cite:5].

The architecture is intentionally deterministic at the verification layer so that the system does not overstate relationships between a company and UNC-Chapel Hill. That makes the output suitable for research, partnership development, and executive-facing materials [cite:5][cite:8].

## Data Model

The engine uses typed entities rather than free-form text wherever possible.

### Core objects

- `CompanyProfile`
- `CorporatePriority`
- `SectorCategory`
- `UniversityMatch`
- `VerificationResult`
- `ReportSection`

### Example schema

```python
from pydantic import BaseModel
from typing import List, Optional

class CorporatePriority(BaseModel):
    theme: str
    evidence: str
    source_url: str
    confidence: float

class UniversityMatch(BaseModel):
    unit_name: str
    level: str  # "university" or "school"
    rationale: str
    source_url: str
    confidence: float

class CompanyProfile(BaseModel):
    company_name: str
    sector: str
    headquarters: Optional[str]
    priorities: List[CorporatePriority] = []
    matches: List[UniversityMatch] = []
```

Using typed schemas makes the workflow easier to test and makes report generation more reproducible across companies [cite:5].

## Verification Strategy

All extracted claims pass through a source-ranking layer before they can appear in the final report.

### Priority order

1. **Primary sources**  
   SEC filings, earnings releases, investor presentations, NIH RePORTER, ClinicalTrials.gov, PubMed, and official UNC pages.

2. **Institutional sources**  
   `.edu`, `.gov`, and official corporate domains.

3. **Secondary sources**  
   Career aggregators, market research sites, and third-party bios, only when cross-validated by a higher-tier source [cite:5].

A claim is included in the final report only if it can be supported by an acceptable source tier. If the evidence is incomplete, the engine should either downgrade the confidence or omit the claim entirely [cite:5]. That policy is central to keeping the output factual and defensible [cite:8].

## Installation

```bash
git clone https://github.com/your-org/nexus-routing-engine.git
cd nexus-routing-engine
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Requirements

```txt
pydantic>=2.0
PyYAML>=6.0
requests>=2.31
beautifulsoup4>=4.12
pandas>=2.0
jinja2>=3.1
```

You can add NLP or search tooling later, but the initial version should stay lightweight and validation-focused [cite:5].

## Configuration

The system is controlled by YAML configuration files.

### `config/sectors.yaml`

```yaml
biopharma:
  routes:
    - oncology
    - immunology
    - vaccines
    - neurology
    - rare_disease

public_health:
  routes:
    - epidemiology
    - health_equity
    - outcomes_research
```

### `config/sources.yaml`

```yaml
primary:
  - sec
  - nih_reporter
  - clinicaltrials
  - pubmed
  - official_company
  - official_unc

secondary:
  - linkedin
  - third_party_bios
  - market_research
```

### `config/university_map.yaml`

```yaml
unc_chapel_hill:
  campus_wide:
    - renci
    - biomedical_informatics
    - data_science
  pharmacy:
    - medicinal_chemistry
    - structural_biology
    - chemical_biology
  medicine:
    - translational_research
    - disease_models
    - clinical_trials
  gillings:
    - epidemiology
    - biostatistics
    - public_health_policy
```

This keeps the mapping logic editable without changing application code [cite:5].

## Usage

```bash
python -m nexus_route \
  --company "Sanofi" \
  --sector "biopharma" \
  --output reports/sanofi_unc.md
```

The command performs extraction, sector routing, UNC mapping, claim verification, and markdown rendering in one pass [cite:5].

### Expected flow

1. Load company input.
2. Extract company priorities.
3. Load UNC campus and school mapping.
4. Match the two datasets.
5. Verify each match.
6. Render the final report.

## Output Format

The generated report should follow a fixed structure.

```md
# Company Name × UNC-Chapel Hill

## Company Overview
## Corporate Priorities
## UNC-Chapel Hill Alignment
### Campus-Wide Opportunities
### School-Specific Opportunities
## Evidence Table
## Confidence Notes
## References
```

This structure makes it easy to compare companies side by side and keeps UNC-wide opportunities separate from school-specific ones [cite:5].

## Example Logic

```python
def align_company_to_unc(profile, unc_map):
    matches = []
    for priority in profile.priorities:
        for unit in unc_map.get(profile.sector, []):
            if semantic_overlap(priority.theme, unit):
                matches.append(unit)
    return matches
```

In practice, semantic overlap should never be the only criterion. The match must still be verified with source evidence before it reaches the final report [cite:5].

## Testing

The test suite should cover extraction, routing, and verification independently.

### Recommended tests

- `test_extract_priorities.py`
- `test_sector_router.py`
- `test_verifier.py`
- `test_report_rendering.py`

### Example assertions

- Extracted priorities are stable across multiple source formats.
- The sector router selects the correct UNC track.
- Unsupported claims are rejected.
- Report output always includes citations for factual statements [cite:5].

A good testing rule is that no report should be considered valid unless every included claim has passed verification [cite:5][cite:8].

## Extending the System

To add a new company sector:

1. Add the sector to `config/sectors.yaml`.
2. Define relevant UNC units in `config/university_map.yaml`.
3. Add source types required for that sector.
4. Add tests for extraction and verification.
5. Update the report template if the section structure changes [cite:5].

To add a new university, create a new mapping file and reuse the same verification and rendering layers. The architecture should stay university-agnostic so the same engine can support other institutions later [cite:5].

## Limitations

This system is only as good as its source coverage and source quality. If the company or university does not publish enough authoritative information, the report should remain conservative rather than speculative [cite:5].

The system should not infer faculty expertise, pipeline priorities, or partnership intent without support from verifiable sources. That discipline is what keeps the workflow credible in executive, academic, and partnership contexts [cite:5][cite:8].

## Roadmap

- Add automated source ingestion connectors.
- Add vector search for evidence retrieval.
- Add confidence scoring per claim.
- Add PDF export.
- Add a dashboard for reviewing pending matches.
- Add audit logs for every verification decision [cite:5].

## License

Specify your preferred license here, such as MIT or Apache 2.0.

---

If you want, I can turn this into a **repo-specific README** with your exact project name, Python package layout, and a more polished `Usage` + `Configuration` section.