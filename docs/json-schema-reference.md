# JSON Schema Reference

Quick reference guide for the Context Mapper JSON format.

## Table of Contents
- [Context Map](#context-map)
- [Bounded Context](#bounded-context)
- [Relationships](#relationships)
- [Aggregates](#aggregates)
- [Entities and Value Objects](#entities-and-value-objects)
- [Domain and Subdomains](#domain-and-subdomains)
- [Complete Example](#complete-example)

---

## Context Map

The top-level container for your system architecture.

### Required Fields
- `type`: `"SYSTEM_LANDSCAPE"` or `"ORGANIZATIONAL"`
- `contains`: Array of bounded context names

### Optional Fields
- `name`: String (context map name)
- `state`: `"AS_IS"` or `"TO_BE"`
- `relationships`: Array of relationship objects

### Example
```json
{
  "contextMap": {
    "name": "MySystem",
    "type": "SYSTEM_LANDSCAPE",
    "state": "TO_BE",
    "contains": ["ContextA", "ContextB"],
    "relationships": [...]
  }
}
```

---

## Bounded Context

Represents a bounded context in your domain.

### Required Fields
- `name`: String (must match pattern `^[A-Za-z][A-Za-z0-9_]*$`)
- `type`: `"FEATURE"`, `"APPLICATION"`, `"SYSTEM"`, or `"TEAM"`

### Optional Fields
- `implements`: Array of subdomain names
- `realizes`: String (for TEAM type only)
- `domainVisionStatement`: String (max 500 chars)
- `implementationTechnology`: String (max 200 chars)
- `responsibilities`: Array of strings
- `knowledgeLevel`: `"CONCRETE"` or `"META"`
- `businessModel`: `"REVENUE"`, `"ENGAGEMENT"`, `"COMPLIANCE"`, or `"COST_REDUCTION"`
- `evolution`: `"GENESIS"`, `"CUSTOM_BUILT"`, `"PRODUCT"`, or `"COMMODITY"`
- `aggregates`: Array of aggregate objects

### Example
```json
{
  "name": "OrderManagement",
  "type": "FEATURE",
  "implements": ["OrderDomain"],
  "domainVisionStatement": "Manages customer orders",
  "implementationTechnology": "Java Spring Boot",
  "responsibilities": ["Order Processing", "Order Tracking"],
  "aggregates": [...]
}
```

---

## Relationships

Defines relationships between bounded contexts.

### Required Fields
- `type`: `"Partnership"`, `"SharedKernel"`, `"CustomerSupplier"`, or `"UpstreamDownstream"`
- `upstream`: String (upstream context name)
- `downstream`: String (downstream context name)

### Optional Fields
- `implementationTechnology`: String (max 200 chars)
- `upstreamRoles`: Array of `"OHS"`, `"PL"`, or `"SK"`
- `downstreamRoles`: Array of `"ACL"`, `"CF"`, or `"SK"`
- `exposedAggregates`: Array of aggregate names

### Relationship Types

#### UpstreamDownstream
Basic upstream-downstream relationship.
```json
{
  "type": "UpstreamDownstream",
  "upstream": "ServiceA",
  "downstream": "ServiceB"
}
```

#### CustomerSupplier
Customer-supplier relationship with roles.
```json
{
  "type": "CustomerSupplier",
  "upstream": "ServiceA",
  "downstream": "ServiceB",
  "upstreamRoles": ["OHS", "PL"],
  "downstreamRoles": ["ACL"]
}
```

#### Partnership
Equal partnership between contexts.
```json
{
  "type": "Partnership",
  "upstream": "ServiceA",
  "downstream": "ServiceB",
  "implementationTechnology": "RabbitMQ"
}
```

#### SharedKernel
Shared kernel between contexts.
```json
{
  "type": "SharedKernel",
  "upstream": "ServiceA",
  "downstream": "ServiceB"
}
```

### Strategic Patterns

**Upstream Roles:**
- `OHS` (Open Host Service): Provides well-defined service interface
- `PL` (Published Language): Publishes formal language/protocol
- `SK` (Shared Kernel): Shares code/model with downstream

**Downstream Roles:**
- `ACL` (Anti-Corruption Layer): Protects from upstream changes
- `CF` (Conformist): Conforms to upstream's model
- `SK` (Shared Kernel): Shares code/model with upstream

---

## Aggregates

Cluster of domain objects treated as a unit.

### Required Fields
- `name`: String

### Optional Fields
- `owner`: String (team/context name)
- `knowledgeLevel`: `"CONCRETE"` or `"META"`
- `likelihoodForChange`: `"OFTEN"`, `"NORMAL"`, or `"RARELY"`
- `entities`: Array of entity objects
- `valueObjects`: Array of value object objects
- `domainEvents`: Array of domain event objects
- `commands`: Array of command objects
- `services`: Array of service objects
- `repositories`: Array of repository objects

### Example
```json
{
  "name": "Orders",
  "owner": "OrderTeam",
  "likelihoodForChange": "NORMAL",
  "entities": [...],
  "valueObjects": [...]
}
```

---

## Entities and Value Objects

### Entity

Object with identity that persists over time.

**Required Fields:**
- `name`: String

**Optional Fields:**
- `aggregateRoot`: Boolean (marks as aggregate root)
- `attributes`: Array of attribute objects
- `operations`: Array of operation objects

```json
{
  "name": "Order",
  "aggregateRoot": true,
  "attributes": [
    {
      "name": "orderId",
      "type": "String",
      "key": true
    },
    {
      "name": "totalAmount",
      "type": "BigDecimal"
    }
  ],
  "operations": [
    {
      "name": "calculateTotal",
      "returnType": "BigDecimal"
    }
  ]
}
```

### Value Object

Immutable object defined by its attributes.

**Required Fields:**
- `name`: String

**Optional Fields:**
- `attributes`: Array of attribute objects
- `operations`: Array of operation objects

```json
{
  "name": "Money",
  "attributes": [
    {
      "name": "amount",
      "type": "BigDecimal"
    },
    {
      "name": "currency",
      "type": "String"
    }
  ]
}
```

### Attribute

**Required Fields:**
- `name`: String
- `type`: String (data type)

**Optional Fields:**
- `key`: Boolean (marks as identifier)
- `nullable`: Boolean

```json
{
  "name": "email",
  "type": "String",
  "nullable": false
}
```

### Operation

**Required Fields:**
- `name`: String

**Optional Fields:**
- `parameters`: Array of parameter objects
- `returnType`: String
- `visibility`: `"PUBLIC"`, `"PRIVATE"`, or `"PROTECTED"`

```json
{
  "name": "processPayment",
  "parameters": [
    {
      "name": "amount",
      "type": "BigDecimal"
    }
  ],
  "returnType": "PaymentResult",
  "visibility": "PUBLIC"
}
```

---

## Domain and Subdomains

### Domain

**Required Fields:**
- `name`: String

**Optional Fields:**
- `subdomains`: Array of subdomain objects

### Subdomain

**Required Fields:**
- `name`: String
- `type`: `"CORE_DOMAIN"`, `"SUPPORTING_DOMAIN"`, or `"GENERIC_SUBDOMAIN"`

**Optional Fields:**
- `domainVisionStatement`: String

```json
{
  "domains": [
    {
      "name": "ECommerceDomain",
      "subdomains": [
        {
          "name": "OrderManagement",
          "type": "CORE_DOMAIN",
          "domainVisionStatement": "Core business capability for order processing"
        },
        {
          "name": "Shipping",
          "type": "SUPPORTING_DOMAIN",
          "domainVisionStatement": "Supports order fulfillment"
        },
        {
          "name": "Authentication",
          "type": "GENERIC_SUBDOMAIN",
          "domainVisionStatement": "Generic user authentication"
        }
      ]
    }
  ]
}
```

---

## Complete Example

Minimal complete example:

```json
{
  "contextMap": {
    "type": "SYSTEM_LANDSCAPE",
    "contains": ["OrderService", "PaymentService"],
    "relationships": [
      {
        "type": "CustomerSupplier",
        "upstream": "PaymentService",
        "downstream": "OrderService",
        "upstreamRoles": ["OHS"],
        "downstreamRoles": ["ACL"]
      }
    ]
  },
  "boundedContexts": [
    {
      "name": "OrderService",
      "type": "FEATURE",
      "aggregates": [
        {
          "name": "Orders",
          "entities": [
            {
              "name": "Order",
              "aggregateRoot": true,
              "attributes": [
                {
                  "name": "orderId",
                  "type": "String"
                }
              ]
            }
          ]
        }
      ]
    },
    {
      "name": "PaymentService",
      "type": "SYSTEM"
    }
  ]
}
```

---

## Validation

Validate your JSON:

```bash
# Validate JSON schema
cml-convert validate my-model.json

# Validate with semantic rules
cml-convert validate my-model.json --strict

# Convert and validate CML output
cml-convert convert my-model.json output.cml --enable-round-trip
```

---

## Common Patterns

### Microservices Architecture
```json
{
  "contextMap": {
    "type": "SYSTEM_LANDSCAPE",
    "contains": ["ServiceA", "ServiceB", "ServiceC"],
    "relationships": [
      {
        "type": "CustomerSupplier",
        "upstream": "ServiceA",
        "downstream": "ServiceB",
        "upstreamRoles": ["OHS", "PL"],
        "downstreamRoles": ["ACL"],
        "implementationTechnology": "REST API"
      }
    ]
  }
}
```

### Team Topology
```json
{
  "boundedContexts": [
    {
      "name": "OrderTeam",
      "type": "TEAM"
    },
    {
      "name": "OrderService",
      "type": "FEATURE",
      "aggregates": [
        {
          "name": "Orders",
          "owner": "OrderTeam"
        }
      ]
    }
  ]
}
```

### Domain Events
```json
{
  "aggregates": [
    {
      "name": "Orders",
      "domainEvents": [
        {
          "name": "OrderPlaced",
          "attributes": [
            {
              "name": "orderId",
              "type": "String"
            },
            {
              "name": "timestamp",
              "type": "DateTime"
            }
          ]
        }
      ]
    }
  ]
}
```

---

## See Also

- [Insurance Example Tutorial](insurance-example-tutorial.md) - Complete staged example
- [JSON Schema Files](../src/context_mapper_json_converter/schemas/) - Full schema definitions
- [Context Mapper Documentation](https://contextmapper.org/docs/) - CML language reference
