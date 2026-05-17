#!/usr/bin/env python3
"""
Script to merge the three separate JSON schemas into one unified schema.
This creates context-mapper.json from context-map.json, bounded-context.json, and subdomain.json.
"""

import json
from pathlib import Path

# Paths
SCHEMA_DIR = Path(__file__).parent.parent / "src" / "context_mapper_json_converter" / "schemas"
CONTEXT_MAP_SCHEMA = SCHEMA_DIR / "context-map.json"
BOUNDED_CONTEXT_SCHEMA = SCHEMA_DIR / "bounded-context.json"
SUBDOMAIN_SCHEMA = SCHEMA_DIR / "subdomain.json"
OUTPUT_SCHEMA = SCHEMA_DIR / "context-mapper.json"

def load_schema(path):
    """Load a JSON schema file."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def merge_schemas():
    """Merge the three schemas into one unified schema."""
    
    # Load all three schemas
    context_map = load_schema(CONTEXT_MAP_SCHEMA)
    bounded_context = load_schema(BOUNDED_CONTEXT_SCHEMA)
    subdomain = load_schema(SUBDOMAIN_SCHEMA)
    
    # Create the unified schema structure
    unified = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "Context Mapper Document Schema",
        "description": "Unified JSON schema for complete Context Mapper DSL documents including Context Maps, Bounded Contexts, and Domains",
        "type": "object",
        "properties": {
            "contextMap": {
                "$ref": "#/$defs/contextMap",
                "description": "The Context Map defining the system landscape and relationships between Bounded Contexts"
            },
            "boundedContexts": {
                "type": "array",
                "items": {
                    "$ref": "#/$defs/boundedContext"
                },
                "description": "List of Bounded Contexts in the system"
            },
            "domains": {
                "type": "array",
                "items": {
                    "$ref": "#/$defs/domain"
                },
                "description": "List of Domains containing Subdomains"
            }
        },
        "additionalProperties": False,
        "$defs": {}
    }
    
    # Add contextMap definition (from context-map.json root)
    unified["$defs"]["contextMap"] = {
        "type": context_map["type"],
        "properties": context_map["properties"],
        "required": context_map["required"],
        "additionalProperties": context_map.get("additionalProperties", False)
    }
    
    # Extract relationship definition from contextMap
    if "relationships" in context_map["properties"]:
        rel_items = context_map["properties"]["relationships"]["items"]
        unified["$defs"]["relationship"] = rel_items
        # Update contextMap to reference the relationship definition
        unified["$defs"]["contextMap"]["properties"]["relationships"] = {
            "type": "array",
            "items": {"$ref": "#/$defs/relationship"},
            "description": context_map["properties"]["relationships"].get("description", "")
        }
    
    # Add boundedContext definition (from bounded-context.json root)
    unified["$defs"]["boundedContext"] = {
        "type": bounded_context["type"],
        "properties": bounded_context["properties"],
        "required": bounded_context["required"],
        "additionalProperties": bounded_context.get("additionalProperties", False)
    }
    
    # Add allOf constraint for TEAM type if it exists
    if "allOf" in bounded_context:
        unified["$defs"]["boundedContext"]["allOf"] = bounded_context["allOf"]
    
    # Add all $defs from bounded-context.json
    if "$defs" in bounded_context:
        for key, value in bounded_context["$defs"].items():
            unified["$defs"][key] = value
    
    # Add domain definition (wrapper for subdomains)
    unified["$defs"]["domain"] = {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "pattern": "^[A-Za-z][A-Za-z0-9_]*$",
                "minLength": 1,
                "maxLength": 100,
                "description": "Name of the Domain"
            },
            "subdomains": {
                "type": "array",
                "items": {
                    "$ref": "#/$defs/subdomain"
                },
                "description": "List of Subdomains within this Domain"
            }
        },
        "required": ["name"],
        "additionalProperties": False
    }
    
    # Add subdomain definition (from subdomain.json root)
    unified["$defs"]["subdomain"] = {
        "type": subdomain["type"],
        "properties": subdomain["properties"],
        "required": subdomain["required"],
        "additionalProperties": subdomain.get("additionalProperties", False)
    }
    
    return unified

def main():
    """Main function to merge schemas and write output."""
    print("Merging JSON schemas...")
    print(f"  - {CONTEXT_MAP_SCHEMA.name}")
    print(f"  - {BOUNDED_CONTEXT_SCHEMA.name}")
    print(f"  - {SUBDOMAIN_SCHEMA.name}")
    
    unified = merge_schemas()
    
    # Write the unified schema
    with open(OUTPUT_SCHEMA, 'w', encoding='utf-8') as f:
        json.dump(unified, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Created unified schema: {OUTPUT_SCHEMA.name}")
    print(f"   Total definitions: {len(unified['$defs'])}")
    print(f"   Root properties: {', '.join(unified['properties'].keys())}")

if __name__ == "__main__":
    main()
