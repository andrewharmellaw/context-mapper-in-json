"""
JSON Schema definition for Bounded Context.

The canonical schema lives at schemas/bounded-context.json in the repository root
and is mirrored here as package data so it is available after installation.
This module loads it at import time so the rest of the package can use it as a
Python dict, exactly as before.
"""

import json
from pathlib import Path
from typing import Any, Dict

# Co-located with this file inside the installed package
_SCHEMA_PATH = Path(__file__).parent / "bounded-context.json"

with open(_SCHEMA_PATH, encoding="utf-8") as _f:
    BOUNDED_CONTEXT_SCHEMA: Dict[str, Any] = json.load(_f)

# Semantic validation rules (business constraints not expressible in JSON Schema)
BOUNDED_CONTEXT_SEMANTIC_RULES: Dict[str, str] = {
    "unique_names": "All Bounded Context names must be unique within a Context Map",
    "team_realizes_constraint": "Only TEAM type Bounded Contexts can have a 'realizes' property",
    "realizes_reference_valid": "The 'realizes' property must reference an existing Bounded Context",
    "implements_reference_valid": "All Subdomain names in 'implements' must reference valid Subdomains",
}
