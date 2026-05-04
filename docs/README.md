# Context Mapper JSON Converter

A comprehensive system for converting JSON definitions to Context Mapper DSL (CML) code with full validation and Context Mapper ecosystem integration.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [JSON Schema Reference](#json-schema-reference)
- [CLI Reference](#cli-reference)
- [Examples](#examples)
- [Validation](#validation)
- [Integration](#integration)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## 🎯 Overview

The Context Mapper JSON Converter enables teams to define Domain-Driven Design (DDD) models using JSON format and convert them to valid Context Mapper DSL (CML) code. This approach provides:

- **Structured modeling** with JSON schema validation
- **Tool integration** with existing JSON-based workflows
- **Comprehensive validation** at every step
- **Round-trip integrity** ensuring no information loss
- **Context Mapper ecosystem integration** for artifact generation

### Supported DDD Patterns

**Strategic Patterns:**
- Context Maps with all relationship types
- Bounded Contexts with full attribute support
- Subdomains (Core, Supporting, Generic)
- Team ownership and organizational modeling

**Tactical Patterns:**
- Aggregates with lifecycle management
- Entities and Value Objects
- Domain Events and Commands
- Services and Repositories
- Complete attribute and operation modeling

## ✨ Features

### Core Capabilities
- ✅ **Complete DDD Support** - Strategic and tactical patterns
- ✅ **Multi-Layer Validation** - JSON schema, semantic rules, CML syntax
- ✅ **Round-Trip Validation** - Ensures information preservation
- ✅ **Context Mapper Integration** - CLI tools and artifact generation
- ✅ **Production-Ready CLI** - Comprehensive command-line interface
- ✅ **Error Handling** - Detailed error reporting with suggestions

### Advanced Features
- 🔄 **Round-trip validation** (JSON → CML → JSON comparison)
- 🔧 **Context Mapper CLI integration** with tool detection
- 📊 **Artifact generation** (PlantUML, MDSL, etc.)
- 🚀 **Workflow orchestration** for complete processing pipelines
- 📈 **Performance optimization** for large models
- 🔍 **Integration status monitoring** with setup recommendations

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Basic Installation

```bash
# Clone the repository
git clone <repository-url>
cd context-mapper-json-converter

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Optional: Context Mapper Integration

For full Context Mapper integration, install:

```bash
# Java Runtime (required for Context Mapper tools)
# Install Java 11+ from https://adoptium.net/

# Context Mapper CLI (optional but recommended)
# Follow instructions at https://contextmapper.org/docs/cli/
```

Check integration status:
```bash
cml-convert integration-status
```

## 🏃‍♂️ Quick Start

### 1. Create a JSON Definition

Create `my-system.json`:

```json
{
  "contextMap": {
    "name": "ECommerceSystem",
    "type": "SYSTEM_LANDSCAPE",
    "contains": ["OrderManagement", "PaymentService"],
    "relationships": [
      {
        "type": "CustomerSupplier",
        "upstream": "PaymentService",
        "downstream": "OrderManagement",
        "upstreamRoles": ["OHS", "PL"],
        "downstreamRoles": ["ACL"],
        "implementationTechnology": "REST API"
      }
    ]
  },
  "boundedContexts": [
    {
      "name": "OrderManagement",
      "type": "FEATURE",
      "domainVisionStatement": "Manages customer orders and order lifecycle"
    },
    {
      "name": "PaymentService",
      "type": "SYSTEM",
      "domainVisionStatement": "Handles payment processing and transactions"
    }
  ]
}
```

### 2. Convert to CML

```bash
# Basic conversion
cml-convert convert my-system.json my-system.cml

# With advanced validation
cml-convert convert my-system.json my-system.cml \
  --enable-round-trip \
  --use-context-mapper-cli

# Validation only
cml-convert validate my-system.json
```

### 3. Generated CML Output

```cml
ContextMap ECommerceSystem type = SYSTEM_LANDSCAPE {
  contains OrderManagement, PaymentService
  
  PaymentService [OHS,PL]->[ACL] OrderManagement : REST API
}

BoundedContext OrderManagement type = FEATURE {
  domainVisionStatement = "Manages customer orders and order lifecycle"
}

BoundedContext PaymentService type = SYSTEM {
  domainVisionStatement = "Handles payment processing and transactions"
}
```

## 📚 Documentation Structure

- **[JSON Schema Reference](json-schema-reference.md)** - Complete schema documentation
- **[CLI Reference](cli-reference.md)** - Command-line interface guide
- **[Examples](examples/)** - Comprehensive example library
- **[API Documentation](api-documentation.md)** - Python API reference
- **[Validation Guide](validation-guide.md)** - Validation layers and error handling
- **[Integration Guide](integration-guide.md)** - Context Mapper ecosystem integration
- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions

## 🎯 Next Steps

1. **Explore Examples** - Check the [examples directory](examples/) for comprehensive samples
2. **Read the Schema Reference** - Understand the [JSON schema structure](json-schema-reference.md)
3. **Try Advanced Features** - Test [round-trip validation and CLI integration](cli-reference.md)
4. **Integrate with Your Workflow** - See the [integration guide](integration-guide.md)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Context Mapper](https://contextmapper.org/) - The original Context Mapper DSL and tooling
- [Domain-Driven Design](https://domainlanguage.com/ddd/) - The foundational concepts and patterns