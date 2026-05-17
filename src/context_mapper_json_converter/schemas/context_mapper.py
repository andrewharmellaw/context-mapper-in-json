"""
Unified JSON Schema definition for Context Mapper documents.

This module provides a single, unified schema that combines Context Maps,
Bounded Contexts, and Domains/Subdomains into one cohesive schema with
strong typing for all components.

The canonical schema lives at schemas/context-mapper.json and is loaded
at import time so the rest of the package can use it as a Python dict.
"""

import json
from pathlib import Path
from typing import Any, Dict

from ..exceptions import SchemaLoadError

# Co-located with this file inside the installed package
_SCHEMA_PATH = Path(__file__).parent / "context-mapper.json"

try:
    with open(_SCHEMA_PATH, encoding="utf-8") as _f:
        CONTEXT_MAPPER_SCHEMA: Dict[str, Any] = json.load(_f)
except (OSError, json.JSONDecodeError) as _e:
    raise SchemaLoadError(
        f"Failed to load unified context-mapper schema from {_SCHEMA_PATH}: {_e}"
    ) from _e

# Semantic validation rules (business constraints not expressible in JSON Schema)
# These are merged from the individual schema modules
CONTEXT_MAPPER_SEMANTIC_RULES: Dict[str, str] = {
    # Context Map rules
    "unique_context_names": "All Bounded Context names in 'contains' must be unique",
    "valid_relationship_participants": "All relationship upstream/downstream must reference contexts in 'contains'",
    "no_self_relationships": "A Bounded Context cannot have a relationship with itself",
    "partnership_symmetry": "Partnership relationships should be symmetric (both directions or neither)",
    
    # Bounded Context rules
    "unique_bounded_context_names": "All Bounded Context names must be unique within a Context Map",
    "team_realizes_constraint": "Only TEAM type Bounded Contexts can have a 'realizes' property",
    "realizes_reference_valid": "The 'realizes' property must reference an existing Bounded Context",
    "implements_reference_valid": "All Subdomain names in 'implements' must reference valid Subdomains",
    
    # Subdomain rules
    "unique_subdomain_names": "All Subdomain names must be unique within a domain",
    "core_domain_limit": "Typically only one CORE_DOMAIN should exist per business domain",
    "entity_reference_valid": "All entity names should follow naming conventions",
    "service_reference_valid": "All service names should follow naming conventions",
}

__all__ = ["CONTEXT_MAPPER_SCHEMA", "CONTEXT_MAPPER_SEMANTIC_RULES"]
