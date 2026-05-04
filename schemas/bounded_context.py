"""
JSON Schema definition for Bounded Context
"""

BOUNDED_CONTEXT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Bounded Context Schema",
    "description": "JSON schema for Context Mapper DSL Bounded Context definitions",
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "pattern": "^[A-Za-z][A-Za-z0-9_]*$",
            "minLength": 1,
            "maxLength": 100,
            "description": "Name of the Bounded Context. Must start with a letter and contain only letters, numbers, and underscores."
        },
        "type": {
            "type": "string",
            "enum": ["FEATURE", "APPLICATION", "SYSTEM", "TEAM"],
            "description": "Type of the Bounded Context. FEATURE=business capability, APPLICATION=software system, SYSTEM=technical system, TEAM=organizational unit."
        },
        "implements": {
            "type": "array",
            "items": {
                "type": "string",
                "pattern": "^[A-Za-z][A-Za-z0-9_]*$"
            },
            "uniqueItems": True,
            "description": "List of Subdomain names that this Bounded Context implements"
        },
        "realizes": {
            "type": "string",
            "pattern": "^[A-Za-z][A-Za-z0-9_]*$",
            "description": "Name of another Bounded Context that this TEAM type context realizes (only valid for TEAM type)"
        },
        "domainVisionStatement": {
            "type": "string",
            "maxLength": 500,
            "description": "A brief statement describing the domain vision and purpose of this Bounded Context"
        },
        "implementationTechnology": {
            "type": "string",
            "maxLength": 200,
            "description": "Technology stack used to implement this Bounded Context (e.g., Java Spring Boot, Python Django)"
        },
        "responsibilities": {
            "type": "array",
            "items": {
                "type": "string",
                "maxLength": 200
            },
            "description": "List of key responsibilities of this Bounded Context"
        },
        "knowledgeLevel": {
            "type": "string",
            "enum": ["CONCRETE", "META"],
            "description": "Knowledge level of the Bounded Context. CONCRETE=specific domain knowledge, META=abstract/framework knowledge."
        },
        "businessModel": {
            "type": "string",
            "enum": ["REVENUE", "ENGAGEMENT", "COMPLIANCE", "COST_REDUCTION"],
            "description": "Primary business model driver for this Bounded Context"
        },
        "evolution": {
            "type": "string",
            "enum": ["GENESIS", "CUSTOM_BUILT", "PRODUCT", "COMMODITY"],
            "description": "Evolution stage of the Bounded Context according to Wardley Maps"
        },
        "aggregates": {
            "type": "array",
            "items": {
                "$ref": "#/$defs/aggregate"
            },
            "description": "List of Aggregates within this Bounded Context"
        }
    },
    "required": ["name", "type"],
    "additionalProperties": False,
    "$defs": {
        "aggregate": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "pattern": "^[A-Za-z][A-Za-z0-9_]*$",
                    "description": "Name of the Aggregate"
                },
                "entities": {
                    "type": "array",
                    "items": {"$ref": "#/$defs/entity"},
                    "description": "Entities within this Aggregate"
                },
                "valueObjects": {
                    "type": "array",
                    "items": {"$ref": "#/$defs/valueObject"},
                    "description": "Value Objects within this Aggregate"
                },
                "domainEvents": {
                    "type": "array",
                    "items": {"$ref": "#/$defs/domainEvent"},
                    "description": "Domain Events published by this Aggregate"
                },
                "commands": {
                    "type": "array",
                    "items": {"$ref": "#/$defs/command"},
                    "description": "Commands handled by this Aggregate"
                },
                "services": {
                    "type": "array",
                    "items": {"$ref": "#/$defs/service"},
                    "description": "Domain Services within this Aggregate"
                },
                "repositories": {
                    "type": "array",
                    "items": {"$ref": "#/$defs/repository"},
                    "description": "Repositories for this Aggregate"
                },
                "owner": {
                    "type": "string",
                    "pattern": "^[A-Za-z][A-Za-z0-9_]*$",
                    "description": "Team or Bounded Context that owns this Aggregate"
                },
                "knowledgeLevel": {
                    "type": "string",
                    "enum": ["CONCRETE", "META"],
                    "description": "Knowledge level of the Aggregate"
                },
                "likelihoodForChange": {
                    "type": "string",
                    "enum": ["OFTEN", "NORMAL", "RARELY"],
                    "description": "Expected frequency of changes to this Aggregate"
                }
            },
            "required": ["name"],
            "additionalProperties": False
        },
        "entity": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "pattern": "^[A-Za-z][A-Za-z0-9_]*$",
                    "description": "Name of the Entity"
                },
                "aggregateRoot": {
                    "type": "boolean",
                    "description": "Whether this Entity is the Aggregate Root"
                },
                "attributes": {
                    "type": "array",
                    "items": {"$ref": "#/$defs/attribute"},
                    "description": "Attributes of the Entity"
                },
                "operations": {
                    "type": "array",
                    "items": {"$ref": "#/$defs/operation"},
                    "description": "Operations/methods of the Entity"
                }
            },
            "required": ["name"],
            "additionalProperties": False
        },
        "valueObject": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "pattern": "^[A-Za-z][A-Za-z0-9_]*$",
                    "description": "Name of the Value Object"
                },
                "attributes": {
                    "type": "array",
                    "items": {"$ref": "#/$defs/attribute"},
                    "description": "Attributes of the Value Object"
                },
                "operations": {
                    "type": "array",
                    "items": {"$ref": "#/$defs/operation"},
                    "description": "Operations/methods of the Value Object"
                }
            },
            "required": ["name"],
            "additionalProperties": False
        },
        "domainEvent": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "pattern": "^[A-Za-z][A-Za-z0-9_]*$",
                    "description": "Name of the Domain Event"
                },
                "attributes": {
                    "type": "array",
                    "items": {"$ref": "#/$defs/attribute"},
                    "description": "Attributes of the Domain Event"
                }
            },
            "required": ["name"],
            "additionalProperties": False
        },
        "command": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "pattern": "^[A-Za-z][A-Za-z0-9_]*$",
                    "description": "Name of the Command"
                },
                "attributes": {
                    "type": "array",
                    "items": {"$ref": "#/$defs/attribute"},
                    "description": "Attributes/parameters of the Command"
                }
            },
            "required": ["name"],
            "additionalProperties": False
        },
        "service": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "pattern": "^[A-Za-z][A-Za-z0-9_]*$",
                    "description": "Name of the Domain Service"
                },
                "operations": {
                    "type": "array",
                    "items": {"$ref": "#/$defs/operation"},
                    "description": "Operations provided by the Service"
                }
            },
            "required": ["name"],
            "additionalProperties": False
        },
        "repository": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "pattern": "^[A-Za-z][A-Za-z0-9_]*$",
                    "description": "Name of the Repository"
                },
                "operations": {
                    "type": "array",
                    "items": {"$ref": "#/$defs/operation"},
                    "description": "Operations provided by the Repository"
                }
            },
            "required": ["name"],
            "additionalProperties": False
        },
        "attribute": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "pattern": "^[A-Za-z][A-Za-z0-9_]*$",
                    "description": "Name of the attribute"
                },
                "type": {
                    "type": "string",
                    "description": "Data type of the attribute"
                },
                "key": {
                    "type": "boolean",
                    "description": "Whether this attribute is a key/identifier"
                },
                "nullable": {
                    "type": "boolean",
                    "description": "Whether this attribute can be null"
                }
            },
            "required": ["name", "type"],
            "additionalProperties": False
        },
        "operation": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "pattern": "^[A-Za-z][A-Za-z0-9_]*$",
                    "description": "Name of the operation"
                },
                "parameters": {
                    "type": "array",
                    "items": {"$ref": "#/$defs/parameter"},
                    "description": "Parameters of the operation"
                },
                "returnType": {
                    "type": "string",
                    "description": "Return type of the operation"
                },
                "visibility": {
                    "type": "string",
                    "enum": ["PUBLIC", "PRIVATE", "PROTECTED"],
                    "description": "Visibility of the operation"
                }
            },
            "required": ["name"],
            "additionalProperties": False
        },
        "parameter": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "pattern": "^[A-Za-z][A-Za-z0-9_]*$",
                    "description": "Name of the parameter"
                },
                "type": {
                    "type": "string",
                    "description": "Data type of the parameter"
                }
            },
            "required": ["name", "type"],
            "additionalProperties": False
        }
    },
    "allOf": [
        {
            "if": {
                "properties": {
                    "type": {"const": "TEAM"}
                }
            },
            "then": {
                "properties": {
                    "realizes": {
                        "type": "string"
                    }
                }
            },
            "else": {
                "not": {
                    "required": ["realizes"]
                }
            }
        }
    ]
}

# Validation rules for semantic constraints
BOUNDED_CONTEXT_SEMANTIC_RULES = {
    "unique_names": "All Bounded Context names must be unique within a Context Map",
    "team_realizes_constraint": "Only TEAM type Bounded Contexts can have a 'realizes' property",
    "realizes_reference_valid": "The 'realizes' property must reference an existing Bounded Context",
    "implements_reference_valid": "All Subdomain names in 'implements' must reference valid Subdomains",
}