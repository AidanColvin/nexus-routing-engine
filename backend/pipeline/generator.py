"""Ollama-powered report generator — 100% local, zero cost."""

import yaml
import ollama
from pathlib import Path
from typing import Iterator

ROOT = Path(__file__).resolve().parent.parent.parent  # repo root

# Preferred models in priority order (first available wins)
PREFERRED_MODELS = [
    "llama3.1:8b",
    "llama3.2:3b",
    "mistral:7b",
    "qwen2.5-coder:14b",
    "qwen2.5:7b",
]


def _load_yaml(rel_path: str) -> dict:
    with open(ROOT / rel_path) as f:
        return yaml.safe_load(f)


def get_available_model() -> str | None:
    """Return the best available local model, or None if Ollama has no models."""
    try:
        models = ollama.list()
        names = [m.model for m in models.models]
        if not names:
            return None
        # Return first preferred model that is available
        for preferred in PREFERRED_MODELS:
            if preferred in names:
                return preferred
        # Fall back to whatever is available
        return names[0]
    except Exception:
        return None


def list_local_models() -> list[str]:
    try:
        return [m.model for m in ollama.list().models]
    except Exception:
        return []


def _build_prompt(company_name: str) -> str:
    unc_map = _load_yaml("config/university_map.yaml")
    sources = _load_yaml("config/sources.yaml")
    sectors = _load_yaml("config/sectors.yaml")
    example = (ROOT / "backend" / "data" / "raw" / "sanofi.md").read_text()

    unc_yaml = yaml.dump(unc_map, default_flow_style=False)
    src_yaml = yaml.dump(sources, default_flow_style=False)
    sec_yaml = yaml.dump(sectors, default_flow_style=False)

    return f"""You are a senior research analyst at UNC-Chapel Hill's Office of Corporate and Foundation Relations. Produce a comprehensive, verified, citation-backed partnership intelligence report for a target company.

VERIFICATION RULES (enforce strictly):
{src_yaml}
- Every factual claim MUST have an inline citation [N].
- Primary sources (SEC filings, earnings releases, NIH RePORTER, ClinicalTrials.gov, PubMed, official company / .edu pages) get confidence 1.0.
- Secondary sources (career aggregators, third-party bios, market research) get confidence 0.5 and must be cross-validated by a primary source.
- If a claim cannot be sourced, omit it entirely. A shorter truthful report beats a longer speculative one.

SECTOR ROUTING CONFIG:
{sec_yaml}

UNC-CHAPEL HILL UNIT MAP:
{unc_yaml}

FORMAT TEMPLATE — replicate this structure and writing style exactly:
{example}
END TEMPLATE

Now generate the equivalent report for: {company_name}

Requirements:
- Replace all Sanofi details with accurate, verified information about {company_name}
- Find real UNC alumni or connections at {company_name}
- Map {company_name}'s research or technology priorities to specific named UNC faculty and centers
- Each UNC faculty mention must include their actual research focus
- Financial data must come from real filings or earnings releases
- Pipeline or product data must come from ClinicalTrials.gov, investor decks, or peer-reviewed sources
- Number all citations [1], [2] ... [N]; References section must list real verifiable URLs
- Talking points must be specific and pairing actual company programs with named UNC strengths

Output ONLY the markdown report starting with "# COMPANY OVERVIEW". No preamble."""


def generate_report_stream(company_name: str) -> Iterator[str]:
    """Yield raw text chunks from the local Ollama model."""
    model = get_available_model()
    if not model:
        raise RuntimeError(
            "Ollama is running but has no models downloaded. "
            "Run: ollama pull llama3.1:8b"
        )

    prompt = _build_prompt(company_name)

    stream = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
        options={
            "num_ctx":    16384,   # large context for the template + output
            "temperature": 0.3,   # focused, factual output
            "num_predict": 6000,  # max output tokens
        },
    )

    for chunk in stream:
        text = chunk.message.content
        if text:
            yield text
