"""
Phase 4 examples for testing Round-Trip Validation and Context Mapper Integration
"""

# Complete example for round-trip validation testing
COMPLETE_SYSTEM_EXAMPLE = {
    "domainName": "ECommerceDomain",
    "contextMap": {
        "name": "ECommerceSystem",
        "type": "SYSTEM_LANDSCAPE",
        "state": "TO_BE",
        "contains": ["OrderManagement", "PaymentService", "ProductCatalog", "CustomerService"],
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
                "upstream": "ProductCatalog",
                "downstream": "OrderManagement",
                "upstreamRoles": ["OHS"],
                "downstreamRoles": ["CF"],
                "implementationTechnology": "GraphQL API"
            },
            {
                "type": "Partnership",
                "upstream": "OrderManagement",
                "downstream": "CustomerService"
            },
            {
                "type": "SharedKernel",
                "upstream": "CustomerService",
                "downstream": "OrderManagement",
                "implementationTechnology": "Shared Database"
            }
        ]
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
            "name": "PaymentProcessing",
            "type": "SUPPORTING_DOMAIN",
            "domainVisionStatement": "Supporting capability for payment processing",
            "entities": ["Payment", "Transaction", "PaymentMethod"],
            "services": ["PaymentService", "FraudDetectionService"]
        },
        {
            "name": "ProductManagement",
            "type": "SUPPORTING_DOMAIN",
            "domainVisionStatement": "Product catalog and inventory management",
            "entities": ["Product", "Category", "Inventory"],
            "services": ["ProductService", "InventoryService"]
        }
    ],
    "boundedContexts": [
        {
            "name": "OrderManagement",
            "type": "FEATURE",
            "implements": ["OrderProcessing"],
            "domainVisionStatement": "Manages customer orders and order lifecycle",
            "implementationTechnology": "Java Spring Boot",
            "knowledgeLevel": "CONCRETE",
            "businessModel": "REVENUE",
            "evolution": "CUSTOM_BUILT",
            "aggregates": [
                {
                    "name": "Order",
                    "owner": "OrderTeam",
                    "knowledgeLevel": "CONCRETE",
                    "likelihoodForChange": "OFTEN",
                    "entities": [
                        {
                            "name": "Order",
                            "aggregateRoot": True,
                            "attributes": [
                                {"name": "orderId", "type": "OrderId", "key": True},
                                {"name": "customerId", "type": "CustomerId"},
                                {"name": "orderDate", "type": "Date"},
                                {"name": "status", "type": "OrderStatus"},
                                {"name": "totalAmount", "type": "Money"}
                            ],
                            "operations": [
                                {
                                    "name": "placeOrder",
                                    "parameters": [
                                        {"name": "customerId", "type": "CustomerId"},
                                        {"name": "items", "type": "List<OrderItem>"}
                                    ],
                                    "returnType": "void",
                                    "visibility": "PUBLIC"
                                },
                                {
                                    "name": "confirmOrder",
                                    "parameters": [],
                                    "returnType": "void",
                                    "visibility": "PUBLIC"
                                },
                                {
                                    "name": "cancelOrder",
                                    "parameters": [{"name": "reason", "type": "String"}],
                                    "returnType": "void",
                                    "visibility": "PUBLIC"
                                }
                            ]
                        },
                        {
                            "name": "OrderItem",
                            "aggregateRoot": False,
                            "attributes": [
                                {"name": "productId", "type": "ProductId"},
                                {"name": "quantity", "type": "int"},
                                {"name": "unitPrice", "type": "Money"},
                                {"name": "lineTotal", "type": "Money"}
                            ]
                        }
                    ],
                    "valueObjects": [
                        {
                            "name": "OrderId",
                            "attributes": [
                                {"name": "value", "type": "String"}
                            ]
                        },
                        {
                            "name": "Money",
                            "attributes": [
                                {"name": "amount", "type": "BigDecimal"},
                                {"name": "currency", "type": "Currency"}
                            ],
                            "operations": [
                                {
                                    "name": "add",
                                    "parameters": [{"name": "other", "type": "Money"}],
                                    "returnType": "Money"
                                },
                                {
                                    "name": "multiply",
                                    "parameters": [{"name": "factor", "type": "BigDecimal"}],
                                    "returnType": "Money"
                                }
                            ]
                        }
                    ],
                    "domainEvents": [
                        {
                            "name": "OrderPlaced",
                            "attributes": [
                                {"name": "orderId", "type": "OrderId"},
                                {"name": "customerId", "type": "CustomerId"},
                                {"name": "timestamp", "type": "DateTime"},
                                {"name": "totalAmount", "type": "Money"}
                            ]
                        },
                        {
                            "name": "OrderConfirmed",
                            "attributes": [
                                {"name": "orderId", "type": "OrderId"},
                                {"name": "timestamp", "type": "DateTime"}
                            ]
                        },
                        {
                            "name": "OrderCancelled",
                            "attributes": [
                                {"name": "orderId", "type": "OrderId"},
                                {"name": "reason", "type": "String"},
                                {"name": "timestamp", "type": "DateTime"}
                            ]
                        }
                    ],
                    "commands": [
                        {
                            "name": "PlaceOrderCommand",
                            "attributes": [
                                {"name": "customerId", "type": "CustomerId"},
                                {"name": "items", "type": "List<OrderItem>"}
                            ]
                        },
                        {
                            "name": "ConfirmOrderCommand",
                            "attributes": [
                                {"name": "orderId", "type": "OrderId"}
                            ]
                        },
                        {
                            "name": "CancelOrderCommand",
                            "attributes": [
                                {"name": "orderId", "type": "OrderId"},
                                {"name": "reason", "type": "String"}
                            ]
                        }
                    ],
                    "services": [
                        {
                            "name": "OrderPricingService",
                            "operations": [
                                {
                                    "name": "calculateTotal",
                                    "parameters": [{"name": "items", "type": "List<OrderItem>"}],
                                    "returnType": "Money"
                                },
                                {
                                    "name": "applyDiscounts",
                                    "parameters": [
                                        {"name": "customerId", "type": "CustomerId"},
                                        {"name": "total", "type": "Money"}
                                    ],
                                    "returnType": "Money"
                                }
                            ]
                        }
                    ],
                    "repositories": [
                        {
                            "name": "OrderRepository",
                            "operations": [
                                {
                                    "name": "save",
                                    "parameters": [{"name": "order", "type": "Order"}],
                                    "returnType": "void"
                                },
                                {
                                    "name": "findById",
                                    "parameters": [{"name": "id", "type": "OrderId"}],
                                    "returnType": "Order"
                                },
                                {
                                    "name": "findByCustomerId",
                                    "parameters": [{"name": "customerId", "type": "CustomerId"}],
                                    "returnType": "List<Order>"
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "name": "PaymentService",
            "type": "SYSTEM",
            "implements": ["PaymentProcessing"],
            "domainVisionStatement": "Handles payment processing and fraud detection",
            "implementationTechnology": "Python FastAPI",
            "knowledgeLevel": "CONCRETE",
            "businessModel": "COMPLIANCE",
            "evolution": "PRODUCT",
            "aggregates": [
                {
                    "name": "Payment",
                    "knowledgeLevel": "CONCRETE",
                    "likelihoodForChange": "NORMAL",
                    "entities": [
                        {
                            "name": "Payment",
                            "aggregateRoot": True,
                            "attributes": [
                                {"name": "paymentId", "type": "PaymentId", "key": True},
                                {"name": "orderId", "type": "OrderId"},
                                {"name": "amount", "type": "Money"},
                                {"name": "status", "type": "PaymentStatus"}
                            ]
                        }
                    ],
                    "domainEvents": [
                        {
                            "name": "PaymentProcessed",
                            "attributes": [
                                {"name": "paymentId", "type": "PaymentId"},
                                {"name": "orderId", "type": "OrderId"},
                                {"name": "amount", "type": "Money"}
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "name": "ProductCatalog",
            "type": "APPLICATION",
            "implements": ["ProductManagement"],
            "domainVisionStatement": "Manages product catalog and inventory",
            "implementationTechnology": "Node.js Express",
            "aggregates": [
                {
                    "name": "Product",
                    "entities": [
                        {
                            "name": "Product",
                            "aggregateRoot": True,
                            "attributes": [
                                {"name": "productId", "type": "ProductId", "key": True},
                                {"name": "name", "type": "String"},
                                {"name": "price", "type": "Money"},
                                {"name": "category", "type": "Category"}
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "name": "CustomerService",
            "type": "APPLICATION",
            "domainVisionStatement": "Customer support and service management",
            "implementationTechnology": "React + Node.js"
        }
    ]
}

# Minimal example for testing basic round-trip
MINIMAL_ROUND_TRIP_EXAMPLE = {
    "contextMap": {
        "name": "SimpleSystem",
        "type": "SYSTEM_LANDSCAPE",
        "contains": ["SimpleContext"]
    },
    "boundedContexts": [
        {
            "name": "SimpleContext",
            "type": "FEATURE",
            "domainVisionStatement": "Simple context for testing"
        }
    ]
}