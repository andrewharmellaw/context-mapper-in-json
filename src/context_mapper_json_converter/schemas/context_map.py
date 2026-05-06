"""
JSON Schema definition for Context Map.

The canonical schema lives at schemas/context-map.json in the repository root
and is mirrored here as package data so it is available after installation.
This module loads it at import time so the rest of the package can use it as a
Python dict, exactly as before.
"""

import json
from pathlib import Path
from typing import Any, Dict

# Co-located with this file inside the installed package
_SCHEMA_PATH = Path(__file__).parent / "context-map.json"

with open(_SCHEMA_PATH, encoding="utf-8") as _f:
    CONTEXT_MAP_SCHEMA: Dict[str, Any] = json.load(_f)

# Semantic validation rules (business constraints not expressible in JSON Schema)
CONTEXT_MAP_SEMANTIC_RULES: Dict[str, str] = {
    "unique_context_names": "All Bounded Context names in 'contains' must be unique",
    "valid_relationship_participants": "All relationship upstream/downstream must reference contexts in 'contains'",
    "no_self_relationships": "A Bounded Context cannot have a relationship with itself",
    "partnership_symmetry": "Partnership relationships should be symmetric (both directions or neither)",
}
