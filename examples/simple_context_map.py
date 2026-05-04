"""
Example JSON definitions for testing Context Mapper JSON Converter
"""

# Simple valid Context Map with two Bounded Contexts and a Partnership
SIMPLE_CONTEXT_MAP = {
    "contextMap": {
        "name": "InsuranceContextMap",
        "type": "SYSTEM_LANDSCAPE",
        "contains": ["PolicyManagement", "ClaimsProcessing"],
        "relationships": [
            {
                "type": "Partnership",
                "upstream": "PolicyManagement",
                "downstream": "ClaimsProcessing"
            }
        ]
    },
    "boundedContexts": [
        {
            "name": "PolicyManagement",
            "type": "FEATURE",
            "domainVisionStatement": "Manages insurance policies and customer data"
        },
        {
            "name": "ClaimsProcessing", 
            "type": "FEATURE",
            "domainVisionStatement": "Processes insurance claims and settlements"
        }
    ]
}

# Context Map with SharedKernel relationship
SHARED_KERNEL_EXAMPLE = {
    "contextMap": {
        "name": "ECommerceSystem",
        "type": "SYSTEM_LANDSCAPE", 
        "contains": ["ProductCatalog", "OrderManagement"],
        "relationships": [
            {
                "type": "SharedKernel",
                "upstream": "ProductCatalog",
                "downstream": "OrderManagement",
                "implementationTechnology": "Shared Database"
            }
        ]
    },
    "boundedContexts": [
        {
            "name": "ProductCatalog",
            "type": "APPLICATION",
            "domainVisionStatement": "Manages product information and catalog",
            "implementationTechnology": "Java Spring Boot"
        },
        {
            "name": "OrderManagement",
            "type": "APPLICATION", 
            "domainVisionStatement": "Handles order processing and fulfillment",
            "implementationTechnology": "Python Django"
        }
    ]
}

# Example with TEAM type Bounded Context
TEAM_CONTEXT_EXAMPLE = {
    "contextMap": {
        "name": "OrganizationalMap",
        "type": "ORGANIZATIONAL",
        "contains": ["PaymentService", "PaymentTeam"]
    },
    "boundedContexts": [
        {
            "name": "PaymentService",
            "type": "SYSTEM",
            "domainVisionStatement": "Handles payment processing"
        },
        {
            "name": "PaymentTeam",
            "type": "TEAM",
            "realizes": "PaymentService",
            "domainVisionStatement": "Team responsible for payment system"
        }
    ]
}

# Invalid example - missing required fields
INVALID_MISSING_FIELDS = {
    "contextMap": {
        "name": "InvalidMap"
        # Missing required 'type' and 'contains'
    },
    "boundedContexts": [
        {
            "name": "SomeContext"
            # Missing required 'type'
        }
    ]
}

# Invalid example - reference errors
INVALID_REFERENCES = {
    "contextMap": {
        "name": "InvalidReferences",
        "type": "SYSTEM_LANDSCAPE",
        "contains": ["ExistingContext"],
        "relationships": [
            {
                "type": "Partnership",
                "upstream": "NonExistentContext1",  # Not in contains
                "downstream": "NonExistentContext2"  # Not in contains
            }
        ]
    },
    "boundedContexts": [
        {
            "name": "ExistingContext",
            "type": "FEATURE"
        }
    ]
}

# Invalid example - semantic errors
INVALID_SEMANTICS = {
    "contextMap": {
        "name": "InvalidSemantics",
        "type": "SYSTEM_LANDSCAPE",
        "contains": ["SelfRelated"],
        "relationships": [
            {
                "type": "Partnership",
                "upstream": "SelfRelated",
                "downstream": "SelfRelated"  # Self-relationship
            }
        ]
    },
    "boundedContexts": [
        {
            "name": "SelfRelated",
            "type": "FEATURE"
        },
        {
            "name": "SelfRelated",  # Duplicate name
            "type": "APPLICATION"
        }
    ]
}

# Expected CML output for SIMPLE_CONTEXT_MAP
SIMPLE_CONTEXT_MAP_CML = '''ContextMap InsuranceContextMap type = SYSTEM_LANDSCAPE {
  contains PolicyManagement, ClaimsProcessing
  
  PolicyManagement Partnership ClaimsProcessing
}

BoundedContext PolicyManagement type = FEATURE {
  domainVisionStatement = "Manages insurance policies and customer data"
}

BoundedContext ClaimsProcessing type = FEATURE {
  domainVisionStatement = "Processes insurance claims and settlements"
}'''

# Expected CML output for SHARED_KERNEL_EXAMPLE
SHARED_KERNEL_EXAMPLE_CML = '''ContextMap ECommerceSystem type = SYSTEM_LANDSCAPE {
  contains ProductCatalog, OrderManagement
  
  ProductCatalog [SK] <-> [SK] OrderManagement : Shared Database
}

BoundedContext ProductCatalog type = APPLICATION {
  domainVisionStatement = "Manages product information and catalog"
  implementationTechnology = "Java Spring Boot"
}

BoundedContext OrderManagement type = APPLICATION {
  domainVisionStatement = "Handles order processing and fulfillment"
  implementationTechnology = "Python Django"
}'''