# JSON Schema Reference

Complete reference for the Context Mapper JSON Converter schema structure.

## 📋 Table of Contents

- [Root Structure](#root-structure)
- [Context Map](#context-map)
- [Bounded Context](#bounded-context)
- [Relationships](#relationships)
- [Subdomains](#subdomains)
- [Tactical DDD Patterns](#tactical-ddd-patterns)
- [Data Types](#data-types)
- [Validation Rules](#validation-rules)

## 🏗️ Root Structure

The root JSON object can contain the following top-level properties:

```json
{
  "domainName": "string (optional)",
  "contextMap": { /* Context Map definition */ },
  "boundedContexts": [ /* Array of Bounded Context definitions */ ],
  "subdomains": [ /* Array of Subdomain definitions */ ]
}
```

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `domainName` | string | No | Name of the domain (used for subdomain organization) |
| `contextMap` | object | No* | Context Map definition |
| `boundedContexts` | array | No* | Array of Bounded Context definitions |
| `subdomains` | array | No | Array of Subdomain definitions |

*At least one of `contextMap` or `boundedContexts` is required.

## 🗺️ Context Map

Defines the strategic view of the system with bounded contexts and their relationships.

```json
{
  "contextMap": {
    "name": "ECommerceSystem",
    "type": "SYSTEM_LANDSCAPE",
    "state": "TO_BE",
    "contains": ["OrderManagement", "PaymentService"],
    "relationships": [
      {
        "type": "CustomerSupplier",
        "upstream": "PaymentService",
        "downstream": "OrderManagement",
        "upstreamRoles": ["OHS", "PL"],
        "downstreamRoles": ["ACL"],
        "implementationTechnology": "REST API",
        "exposedAggregates": ["Payment", "Transaction"]
      }
    ]
  }
}
```

### Context Map Properties

| Property | Type | Required | Values | Description |
|----------|------|----------|--------|-------------|
| `name` | string | No | Valid identifier | Name of the Context Map |
| `type` | string | Yes | `SYSTEM_LANDSCAPE`, `ORGANIZATIONAL` | Type of Context Map |
| `state` | string | No | `AS_IS`, `TO_BE` | Current or future state |
| `contains` | array | Yes | Array of context names | Bounded Contexts in this map |
| `relationships` | array | No | Array of relationship objects | Relationships between contexts |

## 🏢 Bounded Context

Defines a bounded context with its properties and tactical DDD patterns.

```json
{
  "name": "OrderManagement",
  "type": "FEATURE",
  "implements": ["OrderProcessing"],
  "realizes": "OrderTeam",
  "domainVisionStatement": "Manages customer orders and order lifecycle",
  "implementationTechnology": "Java Spring Boot",
  "responsibilities": ["Order creation", "Order tracking", "Order fulfillment"],
  "knowledgeLevel": "CONCRETE",
  "businessModel": "REVENUE",
  "evolution": "CUSTOM_BUILT",
  "aggregates": [
    {
      "name": "Order",
      "owner": "OrderTeam",
      "knowledgeLevel": "CONCRETE",
      "likelihoodForChange": "OFTEN",
      "entities": [ /* Entity definitions */ ],
      "valueObjects": [ /* Value Object definitions */ ],
      "domainEvents": [ /* Domain Event definitions */ ],
      "commands": [ /* Command definitions */ ],
      "services": [ /* Service definitions */ ],
      "repositories": [ /* Repository definitions */ ]
    }
  ]
}
```

### Bounded Context Properties

| Property | Type | Required | Values | Description |
|----------|------|----------|--------|-------------|
| `name` | string | Yes | Valid identifier | Name of the Bounded Context |
| `type` | string | Yes | `FEATURE`, `APPLICATION`, `SYSTEM`, `TEAM` | Type of Bounded Context |
| `implements` | array | No | Array of subdomain names | Subdomains implemented by this context |
| `realizes` | string | No | Context name | Context realized by this TEAM context |
| `domainVisionStatement` | string | No | Text (max 500 chars) | Vision statement for this context |
| `implementationTechnology` | string | No | Text (max 200 chars) | Technology stack used |
| `responsibilities` | array | No | Array of strings | Key responsibilities |
| `knowledgeLevel` | string | No | `CONCRETE`, `META` | Knowledge level |
| `businessModel` | string | No | `REVENUE`, `ENGAGEMENT`, `COMPLIANCE`, `COST_REDUCTION` | Business model driver |
| `evolution` | string | No | `GENESIS`, `CUSTOM_BUILT`, `PRODUCT`, `COMMODITY` | Evolution stage |
| `aggregates` | array | No | Array of aggregate objects | Tactical DDD aggregates |

## 🔗 Relationships

Define relationships between bounded contexts in a Context Map.

### Relationship Types

#### Partnership
```json
{
  "type": "Partnership",
  "upstream": "ContextA",
  "downstream": "ContextB"
}
```

#### Shared Kernel
```json
{
  "type": "SharedKernel",
  "upstream": "ContextA",
  "downstream": "ContextB",
  "implementationTechnology": "Shared Database"
}
```

#### Customer/Supplier
```json
{
  "type": "CustomerSupplier",
  "upstream": "SupplierContext",
  "downstream": "CustomerContext",
  "upstreamRoles": ["OHS", "PL"],
  "downstreamRoles": ["ACL"],
  "implementationTechnology": "REST API",
  "exposedAggregates": ["Product", "Order"]
}
```

#### Upstream/Downstream
```json
{
  "type": "UpstreamDownstream",
  "upstream": "UpstreamContext",
  "downstream": "DownstreamContext",
  "upstreamRoles": ["OHS"],
  "downstreamRoles": ["CF"],
  "implementationTechnology": "Message Queue"
}
```

### Relationship Properties

| Property | Type | Required | Values | Description |
|----------|------|----------|--------|-------------|
| `type` | string | Yes | `Partnership`, `SharedKernel`, `CustomerSupplier`, `UpstreamDownstream` | Relationship type |
| `upstream` | string | Yes | Context name | Upstream context |
| `downstream` | string | Yes | Context name | Downstream context |
| `upstreamRoles` | array | No | `OHS`, `PL`, `SK` | Upstream context roles |
| `downstreamRoles` | array | No | `ACL`, `CF`, `SK` | Downstream context roles |
| `implementationTechnology` | string | No | Text (max 200 chars) | Implementation technology |
| `exposedAggregates` | array | No | Array of aggregate names | Exposed aggregates |

### Role Definitions

**Upstream Roles:**
- `OHS` - Open Host Service
- `PL` - Published Language
- `SK` - Shared Kernel

**Downstream Roles:**
- `ACL` - Anti-Corruption Layer
- `CF` - Conformist
- `SK` - Shared Kernel

## 🏗️ Subdomains

Define domain and subdomain structure for strategic modeling.

```json
{
  "domainName": "ECommerceDomain",
  "subdomains": [
    {
      "name": "OrderProcessing",
      "type": "CORE_DOMAIN",
      "domainVisionStatement": "Core business capability for processing customer orders",
      "entities": ["Order", "OrderItem", "Customer"],
      "services": ["OrderService", "PricingService"]
    },
    {
      "name": "Authentication",
      "type": "GENERIC_SUBDOMAIN",
      "domainVisionStatement": "Generic user authentication and authorization",
      "entities": ["User", "Role", "Permission"],
      "services": ["AuthService", "UserService"]
    }
  ]
}
```

### Subdomain Properties

| Property | Type | Required | Values | Description |
|----------|------|----------|--------|-------------|
| `name` | string | Yes | Valid identifier | Name of the subdomain |
| `type` | string | Yes | `CORE_DOMAIN`, `SUPPORTING_DOMAIN`, `GENERIC_SUBDOMAIN` | Subdomain type |
| `domainVisionStatement` | string | No | Text (max 500 chars) | Vision statement |
| `entities` | array | No | Array of entity names | Main entities |
| `services` | array | No | Array of service names | Domain services |

## 🎯 Tactical DDD Patterns

### Aggregate

```json
{
  "name": "Order",
  "owner": "OrderTeam",
  "knowledgeLevel": "CONCRETE",
  "likelihoodForChange": "OFTEN",
  "entities": [ /* entities */ ],
  "valueObjects": [ /* value objects */ ],
  "domainEvents": [ /* domain events */ ],
  "commands": [ /* commands */ ],
  "services": [ /* services */ ],
  "repositories": [ /* repositories */ ]
}
```

| Property | Type | Required | Values | Description |
|----------|------|----------|--------|-------------|
| `name` | string | Yes | Valid identifier | Aggregate name |
| `owner` | string | No | Context/team name | Owning team or context |
| `knowledgeLevel` | string | No | `CONCRETE`, `META` | Knowledge level |
| `likelihoodForChange` | string | No | `OFTEN`, `NORMAL`, `RARELY` | Change frequency |

### Entity

```json
{
  "name": "Order",
  "aggregateRoot": true,
  "attributes": [
    {
      "name": "orderId",
      "type": "OrderId",
      "key": true
    },
    {
      "name": "customerId",
      "type": "CustomerId",
      "nullable": false
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
    }
  ]
}
```

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `name` | string | Yes | Entity name |
| `aggregateRoot` | boolean | No | Whether this is the aggregate root |
| `attributes` | array | No | Entity attributes |
| `operations` | array | No | Entity operations/methods |

### Value Object

```json
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
    }
  ]
}
```

### Domain Event

```json
{
  "name": "OrderPlaced",
  "attributes": [
    {"name": "orderId", "type": "OrderId"},
    {"name": "customerId", "type": "CustomerId"},
    {"name": "timestamp", "type": "DateTime"}
  ]
}
```

### Command

```json
{
  "name": "PlaceOrderCommand",
  "attributes": [
    {"name": "customerId", "type": "CustomerId"},
    {"name": "items", "type": "List<OrderItem>"}
  ]
}
```

### Service

```json
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
```

### Repository

```json
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
```

## 📊 Data Types

### Attribute

```json
{
  "name": "orderId",
  "type": "OrderId",
  "key": true,
  "nullable": false
}
```

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `name` | string | Yes | Attribute name |
| `type` | string | Yes | Data type |
| `key` | boolean | No | Whether this is a key/identifier |
| `nullable` | boolean | No | Whether this can be null |

### Operation

```json
{
  "name": "placeOrder",
  "parameters": [
    {"name": "customerId", "type": "CustomerId"},
    {"name": "items", "type": "List<OrderItem>"}
  ],
  "returnType": "void",
  "visibility": "PUBLIC"
}
```

| Property | Type | Required | Values | Description |
|----------|------|----------|--------|-------------|
| `name` | string | Yes | Valid identifier | Operation name |
| `parameters` | array | No | Array of parameter objects | Operation parameters |
| `returnType` | string | No | Type name | Return type |
| `visibility` | string | No | `PUBLIC`, `PRIVATE`, `PROTECTED` | Visibility level |

### Parameter

```json
{
  "name": "customerId",
  "type": "CustomerId"
}
```

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `name` | string | Yes | Parameter name |
| `type` | string | Yes | Parameter type |

## ✅ Validation Rules

### Naming Conventions
- All names must start with a letter
- Names can contain letters, numbers, and underscores
- Names must be 1-100 characters long

### Reference Integrity
- All referenced contexts in `contains` must be defined in `boundedContexts`
- All relationship participants must exist in the Context Map `contains`
- TEAM contexts can only `realize` other defined contexts
- Aggregate `owner` must reference a valid TEAM context

### Semantic Rules
- Context names must be unique within a Context Map
- Aggregate names must be unique within a Bounded Context
- No self-relationships allowed (context cannot relate to itself)
- TEAM contexts are the only ones that can have a `realizes` property

### Type Constraints
- Context Map `type` must be `SYSTEM_LANDSCAPE` or `ORGANIZATIONAL`
- Bounded Context `type` must be `FEATURE`, `APPLICATION`, `SYSTEM`, or `TEAM`
- Subdomain `type` must be `CORE_DOMAIN`, `SUPPORTING_DOMAIN`, or `GENERIC_SUBDOMAIN`
- Relationship `type` must be `Partnership`, `SharedKernel`, `CustomerSupplier`, or `UpstreamDownstream`

## 🔍 Schema Validation

The converter performs multi-layer validation:

1. **JSON Schema Validation** - Structure and type checking
2. **Semantic Validation** - Business rule enforcement
3. **Reference Validation** - Cross-reference integrity
4. **CML Validation** - Generated CML syntax checking
5. **Round-Trip Validation** - Information preservation (Phase 4)