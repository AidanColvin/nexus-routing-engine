"""Source-tier verification logic for the Nexus Routing Engine."""


def verify_source_tier(source_type: str, sources_config: dict) -> float:
    """
    Return a confidence score based on source priority hierarchy.

    Primary sources  → 1.0
    Secondary sources → 0.5
    Unknown sources  → 0.0
    """
    if source_type in sources_config.get("primary", []):
        return 1.0
    if source_type in sources_config.get("secondary", []):
        return 0.5
    return 0.0
