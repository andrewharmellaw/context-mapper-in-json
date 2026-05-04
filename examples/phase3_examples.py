"""
Phase 3 examples with Tactical DDD patterns: Aggregates, Entities, Value Objects, Domain Events, Commands, Services
"""

# Simple Aggregate example
SIMPLE_AGGREGATE_EXAMPLE = {
    "contextMap": {
        "name": "OrderManagementSystem",
        "type": "SYSTEM_LANDSCAPE",
        "contains": ["OrderManagement"]
    },
    "boundedContexts": [
        {
            "name": "OrderManagement",
            "type": "FEATURE",
            "domainVisionStatement": "Manages customer orders and order processing",
            "aggregates": [
                {
                    "name": "Order",
                    "knowledgeLevel": "CONCRETE",
                    "likelihoodForChange": "NORMAL",
                    "entities": [
                        {
                            "name": "Order",
                            "aggregateRoot": True,
                            "attributes": [
                                {
                                    "name": "orderId",
                                    "type": "OrderId",
                                    "key": True
                                },
                                {
                                    "name": "customerId",
                                    "type": "CustomerId"
                                },
                                {
                                    "name": "orderDate",
                                    "type": "Date"
                                },
                                {
                                    "name": "status",
                                    "type": "OrderStatus"
                                }
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
                                    "name": "cancelOrder",
                                    "parameters": [],
                                    "returnType": "void",
                                    "visibility": "PUBLIC"
                                }
                            ]
                        },
                        {
                            "name": "OrderItem",
                            "aggregateRoot": False,
                            "attributes": [
                                {
                                    "name": "productId",
                                    "type": "ProductId"
                                },
                                {
                                    "name": "quantity",
                                    "type": "int"
                                },
                                {
                                    "name": "unitPrice",
                                    "type": "Money"
                                }
                            ]
                        }
                    ],
                    "valueObjects": [
                        {
                            "name": "OrderId",
                            "attributes": [
                                {
                                    "name": "value",
                                    "type": "String"
                                }
                            ]
                        },
                        {
                            "name": "Money",
                            "attributes": [
                                {
                                    "name": "amount",
                                    "type": "BigDecimal"
                                },
                                {
                                    "name": "currency",
                                    "type": "Currency"
                                }
                            ],
                            "operations": [
                                {
                                    "name": "add",
                                    "parameters": [{"name": "other", "type": "Money"}],
                                    "returnType": "Money"
                                }
                            ]
                        }
                    ],
                    "domainEvents": [
                        {
                            "name": "OrderPlaced",
                            "attributes": [
                                {
                                    "name": "orderId",
                                    "type": "OrderId"
                                },
                                {
                                    "name": "customerId",
                                    "type": "CustomerId"
                                },
                                {
                                    "name": "timestamp",
                                    "type": "DateTime"
                                }
                            ]
                        },
                        {
                            "name": "OrderCancelled",
                            "attributes": [
                                {
                                    "name": "orderId",
                                    "type": "OrderId"
                                },
                                {
                                    "name": "reason",
                                    "type": "String"
                                }
                            ]
                        }
                    ],
                    "commands": [
                        {
                            "name": "PlaceOrderCommand",
                            "attributes": [
                                {
                                    "name": "customerId",
                                    "type": "CustomerId"
                                },
                                {
                                    "name": "items",
                                    "type": "List<OrderItem>"
                                }
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
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ]
}

# Complex example with multiple aggregates
COMPLEX_TACTICAL_EXAMPLE = {
    "contextMap": {
        "name": "ECommerceSystem",
        "type": "SYSTEM_LANDSCAPE",
        "contains": ["OrderManagement", "ProductCatalog"]
    },
    "boundedContexts": [
        {
            "name": "OrderManagement",
            "type": "FEATURE",
            "domainVisionStatement": "Handles order processing and fulfillment",
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
                                {"name": "id", "type": "OrderId", "key": True},
                                {"name": "customerId", "type": "CustomerId"},
                                {"name": "status", "type": "OrderStatus"}
                            ],
                            "operations": [
                                {
                                    "name": "confirm",
                                    "returnType": "void",
                                    "visibility": "PUBLIC"
                                }
                            ]
                        }
                    ],
                    "domainEvents": [
                        {
                            "name": "OrderConfirmed",
                            "attributes": [
                                {"name": "orderId", "type": "OrderId"},
                                {"name": "timestamp", "type": "DateTime"}
                            ]
                        }
                    ]
                },
                {
                    "name": "Customer",
                    "knowledgeLevel": "CONCRETE",
                    "entities": [
                        {
                            "name": "Customer",
                            "aggregateRoot": True,
                            "attributes": [
                                {"name": "id", "type": "CustomerId", "key": True},
                                {"name": "email", "type": "Email"},
                                {"name": "name", "type": "String"}
                            ]
                        }
                    ],
                    "valueObjects": [
                        {
                            "name": "Email",
                            "attributes": [
                                {"name": "value", "type": "String"}
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "name": "ProductCatalog",
            "type": "APPLICATION",
            "domainVisionStatement": "Manages product information and catalog",
            "aggregates": [
                {
                    "name": "Product",
                    "entities": [
                        {
                            "name": "Product",
                            "aggregateRoot": True,
                            "attributes": [
                                {"name": "id", "type": "ProductId", "key": True},
                                {"name": "name", "type": "String"},
                                {"name": "price", "type": "Money"}
                            ]
                        }
                    ],
                    "services": [
                        {
                            "name": "ProductSearchService",
                            "operations": [
                                {
                                    "name": "searchByName",
                                    "parameters": [{"name": "query", "type": "String"}],
                                    "returnType": "List<Product>"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ]
}

# Expected CML output for SIMPLE_AGGREGATE_EXAMPLE
SIMPLE_AGGREGATE_EXAMPLE_CML = '''ContextMap OrderManagementSystem type = SYSTEM_LANDSCAPE {
  contains OrderManagement
}

BoundedContext OrderManagement type = FEATURE {
  domainVisionStatement = "Manages customer orders and order processing"

  Aggregate Order {
    knowledgeLevel = CONCRETE
    likelihoodForChange = NORMAL

    Entity Order aggregateRoot {
      OrderId orderId key
      CustomerId customerId
      Date orderDate
      OrderStatus status
      public void placeOrder(CustomerId customerId, List<OrderItem> items)
      public void cancelOrder()
    }

    Entity OrderItem {
      ProductId productId
      int quantity
      Money unitPrice
    }

    ValueObject OrderId {
      String value
    }

    ValueObject Money {
      BigDecimal amount
      Currency currency
      Money add(Money other)
    }

    DomainEvent OrderPlaced {
      OrderId orderId
      CustomerId customerId
      DateTime timestamp
    }

    DomainEvent OrderCancelled {
      OrderId orderId
      String reason
    }

    Command PlaceOrderCommand {
      CustomerId customerId
      List<OrderItem> items
    }

    Service OrderPricingService {
      Money calculateTotal(List<OrderItem> items)
    }

    Repository OrderRepository {
      void save(Order order)
      Order findById(OrderId id)
    }
  }
}'''