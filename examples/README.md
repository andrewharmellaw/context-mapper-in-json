# Context Mapper JSON Converter Examples

This directory contains comprehensive examples demonstrating how to use the Context Mapper JSON Converter for various Domain-Driven Design scenarios.

## 📋 Table of Contents

- [Basic Examples](#basic-examples)
- [Strategic Patterns](#strategic-patterns)
- [Tactical Patterns](#tactical-patterns)
- [Advanced Examples](#advanced-examples)
- [Tutorials](#tutorials)
- [Running Examples](#running-examples)

## 🎯 Basic Examples

Start here if you're new to the Context Mapper JSON Converter.

### [`basic/simple-context-map.json`](basic/simple-context-map.json)
A minimal Context Map with two Bounded Contexts and a simple relationship.

**Use case:** Getting started with Context Mapping
**Patterns:** Basic Context Map, Bounded Contexts, Partnership relationship

### [`basic/insurance-system.json`](basic/insurance-system.json)
A simple insurance system demonstrating core concepts.

**Use case:** Understanding basic DDD modeling
**Patterns:** Context Map, Bounded Contexts with domain vision statements

## 🗺️ Strategic Patterns

Examples focusing on strategic Domain-Driven Design patterns.

### [`strategic/customer-supplier.json`](strategic/customer-supplier.json)
Demonstrates Customer/Supplier relationships with upstream and downstream roles.

**Use case:** Modeling service dependencies and integration patterns
**Patterns:** Customer/Supplier, Upstream/Downstream roles, Implementation technology

### [`strategic/subdomains.json`](strategic/subdomains.json)
Shows how to model subdomains and their relationships to Bounded Contexts.

**Use case:** Strategic domain modeling and subdomain classification
**Patterns:** Core Domain, Supporting Domain, Generic Subdomain

## 🎯 Tactical Patterns

Examples demonstrating tactical DDD patterns within Bounded Contexts.

### [`tactical/aggregates-entities.json`](tactical/aggregates-entities.json)
Complete example with Aggregates, Entities, Value Objects, and Domain Events.

**Use case:** Detailed modeling of domain logic and data structures
**Patterns:** Aggregates, Entities, Value Objects, Domain Events, Commands, Services

## 🚀 Advanced Examples

Complex scenarios combining multiple patterns and advanced features.

### [`advanced/complete-system.json`](advanced/complete-system.json)
Comprehensive e-commerce system with all supported patterns.

**Use case:** Production-ready system modeling
**Patterns:** All strategic and tactical patterns combined

### [`advanced/microservices.json`](advanced/microservices.json)
Microservices architecture with multiple integration patterns.

**Use case:** Modern distributed system architecture
**Patterns:** Multiple relationship types, service boundaries, integration patterns

## 📚 Tutorials

Step-by-step tutorials for learning Context Mapping with JSON.

### [`tutorials/getting-started/`](tutorials/getting-started/)
Complete beginner tutorial with progressive examples.

### [`tutorials/e-commerce-system/`](tutorials/e-commerce-system/)
Build a complete e-commerce system step by step.

## 🏃‍♂️ Running Examples

### Convert Single Example

```bash
# Convert a basic example
cml-convert convert examples/basic/simple-context-map.json output.cml

# Convert with validation
cml-convert convert examples/strategic/customer-supplier.json output.cml \
  --enable-round-trip \
  --use-context-mapper-cli
```

### Validate Examples

```bash
# Validate single example
cml-convert validate examples/basic/simple-context-map.json

# Validate all examples
for file in examples/**/*.json; do
  echo "Validating $file"
  cml-convert validate "$file"
done
```

### Generate Artifacts

```bash
# Generate PlantUML diagrams
cml-convert generate examples/advanced/complete-system.json plantuml \
  --output-dir ./diagrams

# Generate MDSL specifications
cml-convert generate examples/tactical/aggregates-entities.json mdsl \
  --output-dir ./specifications
```

### Batch Processing

```bash
# Convert all examples
mkdir -p output/cml
for file in examples/**/*.json; do
  output="output/cml/$(basename "$file" .json).cml"
  echo "Converting $file -> $output"
  cml-convert convert "$file" "$output" --pretty
done
```

## 📖 Example Categories

### By Complexity

| Level | Examples | Description |
|-------|----------|-------------|
| **Beginner** | `basic/` | Simple Context Maps and Bounded Contexts |
| **Intermediate** | `strategic/`, `tactical/` | Strategic and tactical DDD patterns |
| **Advanced** | `advanced/` | Complex systems with multiple patterns |

### By Domain

| Domain | Examples | Description |
|--------|----------|-------------|
| **E-commerce** | `advanced/complete-system.json` | Online shopping system |
| **Insurance** | `basic/insurance-system.json` | Insurance policy management |
| **Generic** | `basic/simple-context-map.json` | Domain-agnostic examples |

### By Pattern Focus

| Pattern Category | Examples | Key Concepts |
|------------------|----------|--------------|
| **Context Mapping** | `basic/`, `strategic/` | Context boundaries, relationships |
| **Strategic DDD** | `strategic/` | Subdomains, team organization |
| **Tactical DDD** | `tactical/` | Aggregates, entities, domain events |
| **Integration** | `strategic/customer-supplier.json` | Service integration patterns |

## 🔍 Example Structure

Each example follows this structure:

```json
{
  "contextMap": {
    "name": "SystemName",
    "type": "SYSTEM_LANDSCAPE",
    "contains": ["Context1", "Context2"],
    "relationships": [
      // Relationship definitions
    ]
  },
  "boundedContexts": [
    // Bounded Context definitions
  ],
  "subdomains": [
    // Subdomain definitions (optional)
  ]
}
```

## 🎯 Learning Path

### 1. Start with Basics
- `basic/simple-context-map.json`
- `basic/insurance-system.json`

### 2. Learn Strategic Patterns
- `strategic/customer-supplier.json`
- `strategic/subdomains.json`

### 3. Explore Tactical Patterns
- `tactical/aggregates-entities.json`

### 4. Study Advanced Systems
- `advanced/complete-system.json`
- `advanced/microservices.json`

### 5. Follow Tutorials
- `tutorials/getting-started/`
- `tutorials/e-commerce-system/`

## 🤝 Contributing Examples

We welcome contributions of new examples! Please follow these guidelines:

1. **Clear Use Case**: Each example should demonstrate a specific use case or pattern
2. **Documentation**: Include comments and README files explaining the example
3. **Validation**: Ensure examples validate successfully
4. **Realistic**: Use realistic domain names and scenarios
5. **Progressive**: Build complexity gradually

### Example Contribution Template

```json
{
  "// Description": "Brief description of what this example demonstrates",
  "// Use Case": "Specific use case or scenario",
  "// Patterns": "List of DDD patterns demonstrated",
  
  "contextMap": {
    // Your Context Map definition
  },
  "boundedContexts": [
    // Your Bounded Context definitions
  ]
}
```

## 📞 Getting Help

- **Documentation**: See [docs/README.md](../docs/README.md) for complete documentation
- **Issues**: Report problems or request new examples in GitHub Issues
- **Discussions**: Ask questions in GitHub Discussions

## 🔗 See Also

- [JSON Schema Reference](../docs/json-schema-reference.md) - Complete schema documentation
- [CLI Reference](../docs/cli-reference.md) - Command-line usage
- [Validation Guide](../docs/validation-guide.md) - Understanding validation
- [Integration Guide](../docs/integration-guide.md) - Context Mapper integration