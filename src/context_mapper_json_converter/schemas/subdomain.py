"""
JSON Schema definition for Subdomain.

The canonical schema lives at schemas/subdomain.json in the repository root
and is mirrored here as package data so it is available after installation.
This module loads it at import time so the rest of the package can use it as a
Python dict, exactly as before.
"""

import json
from pathlib import Path
from typing import Any, Dict

from ..exceptions import SchemaLoadError

# Co-located with this file inside the installed package
_SCHEMA_PATH = Path(__file__).parent / "subdomain.json"

try:
    with open(_SCHEMA_PATH, encoding="utf-8") as _f:
        SUBDOMAIN_SCHEMA: Dict[str, Any] = json.load(_f)
except (OSError, json.JSONDecodeError) as _e:
    raise SchemaLoadError(
        f"Failed to load subdomain schema from {_SCHEMA_PATH}: {_e}"
    ) from _e

# Semantic validation rules (business constraints not expressible in JSON Schema)
SUBDOMAIN_SEMANTIC_RULES: Dict[str, str] = {
    "unique_names": "All Subdomain names must be unique within a domain",
    "core_domain_limit": "Typically only one CORE_DOMAIN should exist per business domain",
    "entity_reference_valid": "All entity names should follow naming conventions",
    "service_reference_valid": "All service names should follow naming conventions",
}
