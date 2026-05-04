"""
JSON Schema definition for Context Map
"""

CONTEXT_MAP_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Context Map Schema",
    "description": "JSON schema for Context Mapper DSL Context Map definitions",
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "pattern": "^[A-Za-z][A-Za-z0-9_]*$",
            "minLength": 1,
            "maxLength": 100,
            "description": "Name of the Context Map. Must start with a letter and contain only letters, numbers, and underscores."
        },
        "type": {
            "type": "string",
            "enum": ["SYSTEM_LANDSCAPE", "ORGANIZATIONAL"],
            "description": "Type of the Context Map. SYSTEM_LANDSCAPE focuses on technical systems, ORGANIZATIONAL focuses on team structures."
        },
        "state": {
            "type": "string", 
            "enum": ["AS_IS", "TO_BE"],
            "description": "State of the Context Map. AS_IS represents current state, TO_BE represents future desired state."
        },
        "contains": {
            "type": "array",
            "items": {
                "type": "string",
                "pattern": "^[A-Za-z][A-Za-z0-9_]*$",
                "minLength": 1,
                "maxLength": 100
            },
            "uniqueItems": True,
            "minItems": 1,
            "description": "List of Bounded Context names contained in this Context Map. Each name must be unique and reference a defined Bounded Context."
        },
        "relationships": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["Partnership", "SharedKernel", "CustomerSupplier", "UpstreamDownstream"],
                        "description": "Type of relationship between Bounded Contexts"
                    },
                    "upstream": {
                        "type": "string",
                        "pattern": "^[A-Za-z][A-Za-z0-9_]*$",
                        "description": "Name of the upstream Bounded Context in the relationship"
                    },
                    "downstream": {
                        "type": "string", 
                        "pattern": "^[A-Za-z][A-Za-z0-9_]*$",
                        "description": "Name of the downstream Bounded Context in the relationship"
                    },
                    "implementationTechnology": {
                        "type": "string",
                        "maxLength": 200,
                        "description": "Technology used to implement the relationship (e.g., REST API, Message Queue)"
                    },
                    "upstreamRoles": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["OHS", "PL", "SK"]
                        },
                        "uniqueItems": True,
                        "description": "Roles of the upstream context: OHS (Open Host Service), PL (Published Language), SK (Shared Kernel)"
                    },
                    "downstreamRoles": {
                        "type": "array", 
                        "items": {
                            "type": "string",
                            "enum": ["ACL", "CF", "SK"]
                        },
                        "uniqueItems": True,
                        "description": "Roles of the downstream context: ACL (Anti-Corruption Layer), CF (Conformist), SK (Shared Kernel)"
                    },
                    "exposedAggregates": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "pattern": "^[A-Za-z][A-Za-z0-9_]*$"
                        },
                        "uniqueItems": True,
                        "description": "List of Aggregate names exposed through this relationship"
                    }
                },
                "required": ["type", "upstream", "downstream"],
                "additionalProperties": False
            },
            "description": "List of relationships between Bounded Contexts in this Context Map."
        }
    },
    "required": ["type", "contains"],
    "additionalProperties": False
}

# Validation rules for semantic constraints
CONTEXT_MAP_SEMANTIC_RULES = {
    "unique_context_names": "All Bounded Context names in 'contains' must be unique",
    "valid_relationship_participants": "All relationship upstream/downstream must reference contexts in 'contains'",
    "no_self_relationships": "A Bounded Context cannot have a relationship with itself",
    "partnership_symmetry": "Partnership relationships should be symmetric (both directions or neither)",
}