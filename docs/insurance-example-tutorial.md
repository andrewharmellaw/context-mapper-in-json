# Insurance Example Tutorial: Staged Context Mapping

This tutorial demonstrates how to progressively build a Context Map for an insurance domain using JSON format. The example is based on the [Context Mapper Insurance Example](https://github.com/ContextMapper/context-mapper-examples/tree/master/src/main/cml/insurance-example) and shows how to evolve your model through five stages, from basic structure to fully detailed domain models.

## Overview

The insurance domain example models a typical insurance company system with the following bounded contexts:

- **CustomerManagementContext**: Manages customer data and addresses
- **CustomerSelfServiceContext**: Web application for customer self-service
- **PrintingContext**: External printing service for documents
- **PolicyManagementContext**: Manages insurance contracts and policies
- **RiskManagementContext**: Calculates customer risk factors
- **DebtCollection**: Handles financial debts and dunning

## Stage 1: Basic Context Map Structure

**File**: [`examples/insurance-stage-1.json`](../examples/insurance-stage-1.json)

**What's included**:
- Context Map with type and state
- List of bounded contexts
- Basic relationships between contexts
- Domain and subdomain definitions

**Key concepts**:
- `SYSTEM_LANDSCAPE`: Focuses on technical systems
- `TO_BE`: Represents future desired state
- Basic relationship types: `UpstreamDownstream`, `Partnership`, `SharedKernel`

```json
{
  "contextMap": {
    "name": "InsuranceContextMap",
    "type": "SYSTEM_LANDSCAPE",
    "state": "TO_BE",
    "contains": [
      "CustomerManagementContext",
      "CustomerSelfServiceContext",
      "PrintingContext",
      "PolicyManagementContext",
      "RiskManagementContext",
      "DebtCollection"
    ],
    "relationships": [
      {
        "type": "UpstreamDownstream",
        "upstream": "CustomerManagementContext",
        "downstream": "CustomerSelfServiceContext"
      }
      // ... more relationships
    ]
  }
}
```

**Validation**:
```bash
python -m context_mapper_json_converter.cli validate examples/insurance-stage-1.json
```

---

## Stage 2: Adding Relationship Patterns

**File**: [`examples/insurance-stage-2.json`](../examples/insurance-stage-2.json)

**What's new**:
- Detailed relationship patterns with roles
- `CustomerSupplier` relationships with upstream/downstream roles
- Strategic patterns: OHS (Open Host Service), PL (Published Language), ACL (Anti-Corruption Layer), CF (Conformist)

**Key concepts**:
- **Upstream roles**: `OHS`, `PL`, `SK` (Shared Kernel)
- **Downstream roles**: `ACL`, `CF`, `SK`
- **CustomerSupplier**: Explicit customer-supplier relationship

```json
{
  "type": "CustomerSupplier",
  "upstream": "PrintingContext",
  "downstream": "CustomerManagementContext",
  "upstreamRoles": ["OHS", "PL"],
  "downstreamRoles": ["ACL"]
}
```

**Pattern explanation**:
- **OHS (Open Host Service)**: Upstream provides a well-defined service interface
- **PL (Published Language)**: Upstream publishes a formal language/protocol
- **ACL (Anti-Corruption Layer)**: Downstream protects itself from upstream changes
- **CF (Conformist)**: Downstream conforms to upstream's model

---

## Stage 3: Bounded Context Details

**File**: [`examples/insurance-stage-3.json`](../examples/insurance-stage-3.json)

**What's new**:
- Bounded context types: `FEATURE`, `APPLICATION`, `SYSTEM`, `TEAM`
- Domain vision statements
- Implementation technologies
- Responsibilities
- Aggregate definitions (names only)

**Key concepts**:
- **FEATURE**: Business capability or feature
- **APPLICATION**: Software application
- **SYSTEM**: External or technical system
- **TEAM**: Organizational team

```json
{
  "name": "CustomerManagementContext",
  "type": "FEATURE",
  "implements": ["CustomerManagementDomain"],
  "domainVisionStatement": "The customer management context is responsible for managing all the data of the insurance companies customers.",
  "implementationTechnology": "Java, JEE Application",
  "responsibilities": ["Customers", "Addresses"],
  "aggregates": [
    {
      "name": "Customers"
    }
  ]
}
```

---

## Stage 4: Aggregate Structure with Entities and Value Objects

**File**: [`examples/insurance-stage-4.json`](../examples/insurance-stage-4.json)

**What's new**:
- Entities within aggregates
- Value Objects within aggregates
- Basic domain model structure

**Key concepts**:
- **Entity**: Object with identity that persists over time
- **Value Object**: Immutable object defined by its attributes
- **Aggregate**: Cluster of entities and value objects with a root entity

```json
{
  "name": "Customers",
  "entities": [
    {
      "name": "Customer"
    },
    {
      "name": "Address"
    }
  ],
  "valueObjects": [
    {
      "name": "SocialInsuranceNumber"
    }
  ]
}
```

---

## Stage 5: Complete Domain Model

**File**: [`examples/insurance-stage-5.json`](../examples/insurance-stage-5.json)

**What's new**:
- Entity attributes with types
- Aggregate roots marked
- Operations/methods on entities
- Relationship implementation technologies
- Exposed aggregates in relationships
- Team ownership of aggregates
- Complete domain model details

**Key concepts**:
- **Aggregate Root**: Entry point entity for the aggregate
- **Attributes**: Properties with data types
- **Operations**: Methods/functions on entities
- **Owner**: Team responsible for the aggregate

```json
{
  "name": "Customers",
  "owner": "ContractsTeam",
  "entities": [
    {
      "name": "Customer",
      "aggregateRoot": true,
      "attributes": [
        {
          "name": "firstname",
          "type": "String"
        },
        {
          "name": "lastname",
          "type": "String"
        },
        {
          "name": "addresses",
          "type": "List<Address>"
        }
      ]
    },
    {
      "name": "Address",
      "attributes": [
        {
          "name": "street",
          "type": "String"
        },
        {
          "name": "city",
          "type": "String"
        }
      ]
    }
  ]
}
```

**Relationship with implementation details**:
```json
{
  "type": "CustomerSupplier",
  "upstream": "CustomerManagementContext",
  "downstream": "CustomerSelfServiceContext",
  "upstreamRoles": ["OHS"],
  "downstreamRoles": [],
  "exposedAggregates": ["Customers"]
}
```

**Team definitions**:
```json
{
  "name": "ContractsTeam",
  "type": "TEAM"
}
```

---

## Validation Results

All five stages have been validated successfully using the context-mapper-json-converter:

```bash
# Stage 1
✅ JSON validation completed successfully

# Stage 2
✅ JSON validation completed successfully

# Stage 3
✅ JSON validation completed successfully

# Stage 4
✅ JSON validation completed successfully

# Stage 5
✅ JSON validation completed successfully
```

---

## Progressive Development Approach

This staged approach demonstrates best practices for developing Context Maps:

### 1. **Start Simple** (Stage 1)
   - Identify bounded contexts
   - Define basic relationships
   - Establish domain structure

### 2. **Add Strategic Patterns** (Stage 2)
   - Define relationship types
   - Add upstream/downstream roles
   - Apply DDD strategic patterns

### 3. **Document Context Details** (Stage 3)
   - Add vision statements
   - Specify technologies
   - Define responsibilities
   - Identify aggregates

### 4. **Model Domain Structure** (Stage 4)
   - Define entities and value objects
   - Structure aggregates
   - Establish domain model

### 5. **Complete the Model** (Stage 5)
   - Add attributes and types
   - Define operations
   - Specify ownership
   - Document implementation details

---

## Key JSON Schema Requirements

### Context Map
- **Required**: `type`, `contains`
- **Optional**: `name`, `state`, `relationships`

### Relationships
- **Required**: `type`, `upstream`, `downstream`
- **Optional**: `upstreamRoles`, `downstreamRoles`, `implementationTechnology`, `exposedAggregates`

### Bounded Context
- **Required**: `name`, `type`
- **Optional**: `implements`, `domainVisionStatement`, `implementationTechnology`, `responsibilities`, `aggregates`

### Aggregate
- **Required**: `name`
- **Optional**: `owner`, `entities`, `valueObjects`, `domainEvents`, `commands`, `services`, `repositories`

### Entity
- **Required**: `name`
- **Optional**: `aggregateRoot`, `attributes`, `operations`

### Attribute
- **Required**: `name`, `type`
- **Optional**: `key`, `nullable`

---

## Converting to CML

You can convert any of these JSON files to Context Mapper DSL (CML) format:

```bash
python -m context_mapper_json_converter.cli convert examples/insurance-stage-5.json -o output.cml
```

---

## Next Steps

1. **Experiment**: Modify the examples to match your domain
2. **Validate**: Use the CLI to validate your JSON
3. **Iterate**: Start with Stage 1 and progressively add details
4. **Convert**: Generate CML files for use with Context Mapper tools

---

## References

- [Context Mapper Official Examples](https://github.com/ContextMapper/context-mapper-examples)
- [Context Mapper DSL Documentation](https://contextmapper.org/docs/language-reference/)
- [Domain-Driven Design Patterns](https://contextmapper.org/docs/strategic-ddd/)
- [JSON Schema Documentation](../src/context_mapper_json_converter/schemas/)

---

## License

This example is based on the Context Mapper Insurance Example, which is licensed under Apache License 2.0.
