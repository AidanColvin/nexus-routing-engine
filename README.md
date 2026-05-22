# Nexus Routing Engine

Evidence-first AI pipeline for generating UNC-Chapel Hill partnership reports from any company name. Type a company, press Enter, get a fully structured, citation-backed intelligence brief in minutes — free, local, no API costs.

---

## What It Does

Nexus takes a company name as its only input and produces a complete partnership intelligence report mapping that company's research priorities, pipeline programs, and key personnel to specific UNC-Chapel Hill schools, institutes, faculty, and research centers.

Every claim in the report is tied to a source. Every UNC match is paired with a named faculty member or center and their real research focus. The output is ready for executive briefings, partnership development meetings, and internal research.

---

## Features

- **Single-input web UI** — type a company name, press Enter, get a report
- **Live streaming output** — watch the report write itself token by token in real time
- **100% free and local** — runs on Ollama with open-source models, no API keys, no usage costs
- **Full pipeline automation** — sector routing, UNC unit mapping, source verification, and report rendering in one pass
- **Structured report format** — Company Overview, Basic Info, UNC Connections, Talking Points, Pipeline Alignment, and numbered References every time
- **Dual export** — download the finished report as Markdown or styled PDF
- **Source verification hierarchy** — primary sources (SEC, NIH, ClinicalTrials, PubMed) outrank secondary sources (bios, aggregators); unsupported claims are dropped
- **YAML-configured routing** — sectors, UNC units, and source tiers are all editable without touching code
- **Model auto-selection** — uses the best available local model automatically

---

## Architecture

The pipeline runs in five stages every time a company name is submitted.

```
Company Name
     │
     ▼
1. Sector Routing          config/sectors.yaml
     │                     Maps company to biopharma / public_health / AI / etc.
     ▼
2. UNC Unit Mapping        config/university_map.yaml
     │                     Identifies relevant schools, centers, and institutes
     ▼
3. Source Verification     config/sources.yaml
     │                     Enforces primary > secondary source hierarchy
     ▼
4. AI Report Generation    backend/pipeline/generator.py
     │                     Ollama LLM writes structured markdown with citations
     ▼
5. Rendering               backend/pipeline/renderer.py
                           Markdown → styled HTML (browser) + PDF (download)
```

The web layer streams the generation output token by token using Server-Sent Events so you see the report being written in real time.

---

## Project Structure

```
nexus-routing-engine/
├── app.py                          Flask web server and SSE streaming endpoint
├── run.sh                          One-command startup script
├── requirements.txt
├── config/
│   ├── sectors.yaml                Sector-to-route mapping
│   ├── sources.yaml                Source tier definitions
│   └── university_map.yaml         UNC schools, centers, and research units
├── backend/
│   ├── pipeline/
│   │   ├── generator.py            Ollama-powered report generator
│   │   ├── renderer.py             Markdown → HTML + PDF renderer (WeasyPrint)
│   │   └── verifier.py             Source-tier confidence scoring
│   └── data/
│       ├── raw/                    Example reports (sanofi.md used as format template)
│       └── processed/
│           ├── md/                 Generated markdown reports
│           └── pdf/                Generated PDF reports
└── templates/
    └── index.html                  Single-page web UI
```

---

## Installation

### 1. Install Ollama

Ollama runs AI models locally on your machine.

```bash
# macOS
brew install ollama
```

Or download from [ollama.com](https://ollama.com).

### 2. Pull a model

```bash
ollama pull llama3.1:8b
```

This downloads once (~5 GB) and runs free forever. The engine also supports `llama3.2:3b`, `mistral:7b`, and `qwen2.5-coder:14b` — it picks the best available model automatically.

### 3. Clone and install dependencies

```bash
git clone https://github.com/your-org/nexus-routing-engine.git
cd nexus-routing-engine
pip install -r requirements.txt
```

### Requirements

```
flask>=3.0
ollama>=0.4
markdown>=3.5
weasyprint>=60.0
pydantic>=2.0
PyYAML>=6.0
python-dotenv>=1.0
```

---

## Usage

```bash
./run.sh
```

Then open **http://localhost:5050** in your browser.

The startup script automatically launches Ollama if it is not already running, checks that a model is available, and starts the Flask server.

### What happens when you submit a company name

1. The sector router classifies the company using `config/sectors.yaml`
2. The UNC unit map (`config/university_map.yaml`) identifies relevant schools and centers
3. The source verification hierarchy (`config/sources.yaml`) is encoded into the generation prompt
4. The local LLM writes the full report, streaming each token to the browser
5. The dark terminal panel shows raw markdown in real time
6. On completion the panel transitions to the fully rendered report
7. Download buttons appear for Markdown and PDF

---

## Output Format

Every report follows this fixed section structure regardless of company.

```
# COMPANY OVERVIEW
One-paragraph summary with inline citations explaining what the company does
and why it is a strong UNC partnership candidate.

## BASIC COMPANY INFORMATION
Name, location, website, company type, IPO status, headcount.

## UNC CONNECTION
Named individuals at the company with UNC degrees or affiliations,
their roles, board positions, and why they are partnership entry points.

## TALKING POINTS

### SECTION 1: [Company] Organizational Context
Financial momentum, key products, AI or technology strategy,
external partnership signals — all cited.

### SECTION 2: Pipeline Alignment with UNC Research
Each subsection pairs a specific company program with a named UNC
faculty member or center and their real research focus.

## REFERENCES
Numbered list of all cited sources with full URLs.
```

---

## Configuration

All routing logic is controlled by three YAML files. Edit them without touching any code.

### `config/sectors.yaml`

Maps sector keywords to alignment routes.

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

Defines the source tier hierarchy used during generation. Primary sources get confidence 1.0, secondary get 0.5, and unsupported claims are dropped.

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

Maps UNC schools and institutes to their research domains.

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

---

## Local Models

The engine selects the best available model automatically in this priority order:

| Model | Size | Best for |
|---|---|---|
| `llama3.1:8b` | 5 GB | General reports, strong instruction following |
| `llama3.2:3b` | 2 GB | Faster generation, smaller footprint |
| `mistral:7b` | 4 GB | Analytical writing |
| `qwen2.5-coder:14b` | 9 GB | Technical companies, AI/software sectors |

To pull any model:

```bash
ollama pull llama3.1:8b
```

For maximum quality on a capable machine:

```bash
ollama pull llama3.3:70b
```

---

## API Reference

| Method | Route | Description |
|---|---|---|
| `GET` | `/` | Web UI |
| `POST` | `/api/generate` | Start streaming report generation |
| `GET` | `/api/status` | Returns active model and available models |
| `GET` | `/download/<company>/md` | Download saved Markdown report |
| `GET` | `/download/<company>/pdf` | Download styled PDF report |

### `/api/generate` request

```json
{ "company": "Pfizer" }
```

### `/api/generate` SSE event types

```
{ "type": "model",  "model": "llama3.1:8b" }
{ "type": "chunk",  "text": "..." }
{ "type": "done",   "html": "...", "md_url": "...", "pdf_url": "..." }
{ "type": "error",  "message": "..." }
```

---

## Verification Strategy

The generation prompt strictly enforces the following rules before a claim can appear in the final report.

- Every factual claim must carry an inline citation `[N]`
- Primary sources (SEC filings, NIH RePORTER, ClinicalTrials.gov, PubMed, official `.edu` and company pages) receive confidence 1.0
- Secondary sources (career aggregators, third-party bios, market research) receive confidence 0.5 and must be cross-validated by a primary source
- Claims that cannot be sourced are omitted entirely — the engine never speculates
- A shorter truthful report is always preferred over a longer speculative one

---

## Extending the System

### Add a new sector

1. Add the sector and its routes to `config/sectors.yaml`
2. Add relevant UNC units to `config/university_map.yaml`
3. No code changes required

### Swap the AI model

```bash
ollama pull <model-name>
```

The engine picks it up automatically on the next request if it ranks higher in the preference list in `backend/pipeline/generator.py`.

### Change the report format

Edit `backend/data/raw/sanofi.md`. This file is the format template the LLM is shown for every generation. Changing its structure changes the output structure for all future reports.

---

## Roadmap

- [ ] Automated source ingestion connectors (SEC EDGAR, NIH RePORTER, ClinicalTrials.gov)
- [ ] Vector search over UNC faculty pages for better alignment matching
- [ ] Per-claim confidence scores displayed inline in the UI
- [ ] Report history and comparison dashboard
- [ ] Audit log of every generation and source decision
- [ ] Multi-university support beyond UNC-Chapel Hill

---

## License

MIT
