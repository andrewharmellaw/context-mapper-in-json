"""
Phase 2 examples with Customer/Supplier, Upstream/Downstream relationships and Subdomains
"""

# Customer/Supplier relationship example
CUSTOMER_SUPPLIER_EXAMPLE = {
    "contextMap": {
        "name": "ECommerceSystem",
        "type": "SYSTEM_LANDSCAPE",
        "contains": ["OrderManagement", "PaymentService", "InventoryService"],
        "relationships": [
            {
                "type": "CustomerSupplier",
                "upstream": "PaymentService",
                "downstream": "OrderManagement",
                "upstreamRoles": ["OHS", "PL"],
                "downstreamRoles": ["ACL"],
                "implementationTechnology": "REST API",
                "exposedAggregates": ["Payment", "Transaction"]
            },
            {
                "type": "UpstreamDownstream", 
                "upstream": "InventoryService",
                "downstream": "OrderManagement",
                "upstreamRoles": ["OHS"],
                "downstreamRoles": ["CF"],
                "implementationTechnology": "Message Queue"
            }
        ]
    },
    "boundedContexts": [
        {
            "name": "OrderManagement",
            "type": "FEATURE",
            "domainVisionStatement": "Manages customer orders and order lifecycle",
            "implementationTechnology": "Java Spring Boot"
        },
        {
            "name": "PaymentService",
            "type": "SYSTEM",
            "domainVisionStatement": "Handles payment processing and transactions",
            "implementationTechnology": "Python FastAPI"
        },
        {
            "name": "InventoryService",
            "type": "SYSTEM", 
            "domainVisionStatement": "Manages product inventory and stock levels",
            "implementationTechnology": "Node.js Express"
        }
    ]
}

# Example with Subdomains
SUBDOMAIN_EXAMPLE = {
    "domainName": "ECommerceDomain",
    "contextMap": {
        "name": "ECommerceContextMap",
        "type": "SYSTEM_LANDSCAPE",
        "contains": ["OrderManagement", "ProductCatalog", "UserManagement"]
    },
    "subdomains": [
        {
            "name": "OrderProcessing",
            "type": "CORE_DOMAIN",
            "domainVisionStatement": "Core business capability for processing customer orders",
            "entities": ["Order", "OrderItem", "Customer"],
            "services": ["OrderService", "PricingService"]
        },
        {
            "name": "ProductManagement",
            "type": "SUPPORTING_DOMAIN",
            "domainVisionStatement": "Supporting capability for managing product catalog",
            "entities": ["Product", "Category", "Brand"],
            "services": ["ProductService", "CategoryService"]
        },
        {
            "name": "Authentication",
            "type": "GENERIC_SUBDOMAIN",
            "domainVisionStatement": "Generic user authentication and authorization",
            "entities": ["User", "Role", "Permission"],
            "services": ["AuthService", "UserService"]
        }
    ],
    "boundedContexts": [
        {
            "name": "OrderManagement",
            "type": "FEATURE",
            "implements": ["OrderProcessing"],
            "domainVisionStatement": "Implements order processing capabilities"
        },
        {
            "name": "ProductCatalog",
            "type": "APPLICATION",
            "implements": ["ProductManagement"],
            "domainVisionStatement": "Implements product catalog management"
        },
        {
            "name": "UserManagement",
            "type": "SYSTEM",
            "implements": ["Authentication"],
            "domainVisionStatement": "Implements user authentication system"
        }
    ]
}

# Complex example with multiple relationship types
COMPLEX_RELATIONSHIPS_EXAMPLE = {
    "contextMap": {
        "name": "InsuranceSystem",
        "type": "SYSTEM_LANDSCAPE",
        "contains": ["PolicyManagement", "ClaimsProcessing", "RiskAssessment", "CustomerService", "Billing"],
        "relationships": [
            {
                "type": "Partnership",
                "upstream": "PolicyManagement",
                "downstream": "CustomerService"
            },
            {
                "type": "SharedKernel",
                "upstream": "PolicyManagement",
                "downstream": "Billing",
                "implementationTechnology": "Shared Database"
            },
            {
                "type": "CustomerSupplier",
                "upstream": "RiskAssessment",
                "downstream": "PolicyManagement",
                "upstreamRoles": ["OHS", "PL"],
                "downstreamRoles": ["ACL"],
                "exposedAggregates": ["RiskProfile", "Assessment"]
            },
            {
                "type": "UpstreamDownstream",
                "upstream": "ClaimsProcessing",
                "downstream": "CustomerService",
                "upstreamRoles": ["OHS"],
                "downstreamRoles": ["CF"],
                "implementationTechnology": "Event Bus"
            }
        ]
    },
    "boundedContexts": [
        {
            "name": "PolicyManagement",
            "type": "FEATURE",
            "domainVisionStatement": "Core policy management and underwriting"
        },
        {
            "name": "ClaimsProcessing",
            "type": "FEATURE", 
            "domainVisionStatement": "Claims intake, processing and settlement"
        },
        {
            "name": "RiskAssessment",
            "type": "SYSTEM",
            "domainVisionStatement": "Risk analysis and assessment engine"
        },
        {
            "name": "CustomerService",
            "type": "APPLICATION",
            "domainVisionStatement": "Customer support and service portal"
        },
        {
            "name": "Billing",
            "type": "SYSTEM",
            "domainVisionStatement": "Billing and payment processing"
        }
    ]
}

# Expected CML output for CUSTOMER_SUPPLIER_EXAMPLE
CUSTOMER_SUPPLIER_EXAMPLE_CML = '''ContextMap ECommerceSystem type = SYSTEM_LANDSCAPE {
  contains OrderManagement, PaymentService, InventoryService
  
  PaymentService [OHS,PL]->[ACL] OrderManagement : REST API { Payment, Transaction }
  InventoryService [OHS]->[CF] OrderManagement : Message Queue
}

BoundedContext OrderManagement type = FEATURE {
  domainVisionStatement = "Manages customer orders and order lifecycle"
  implementationTechnology = "Java Spring Boot"
}

BoundedContext PaymentService type = SYSTEM {
  domainVisionStatement = "Handles payment processing and transactions"
  implementationTechnology = "Python FastAPI"
}

BoundedContext InventoryService type = SYSTEM {
  domainVisionStatement = "Manages product inventory and stock levels"
  implementationTechnology = "Node.js Express"
}'''

# Expected CML output for SUBDOMAIN_EXAMPLE
SUBDOMAIN_EXAMPLE_CML = '''ContextMap ECommerceContextMap type = SYSTEM_LANDSCAPE {
  contains OrderManagement, ProductCatalog, UserManagement
}

Domain ECommerceDomain {
  Subdomain OrderProcessing {
    type = CORE_DOMAIN
    domainVisionStatement = "Core business capability for processing customer orders"
    entities = Order, OrderItem, Customer
    services = OrderService, PricingService
  }
  Subdomain ProductManagement {
    type = SUPPORTING_DOMAIN
    domainVisionStatement = "Supporting capability for managing product catalog"
    entities = Product, Category, Brand
    services = ProductService, CategoryService
  }
  Subdomain Authentication {
    type = GENERIC_SUBDOMAIN
    domainVisionStatement = "Generic user authentication and authorization"
    entities = User, Role, Permission
    services = AuthService, UserService
  }
}

BoundedContext OrderManagement type = FEATURE {
  domainVisionStatement = "Implements order processing capabilities"
}

BoundedContext ProductCatalog type = APPLICATION {
  domainVisionStatement = "Implements product catalog management"
}

BoundedContext UserManagement type = SYSTEM {
  domainVisionStatement = "Implements user authentication system"
}'''