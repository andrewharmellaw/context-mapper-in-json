# Context Mapper JSON Converter

A comprehensive system for converting JSON definitions to Context Mapper DSL (CML) code with full validation and Context Mapper ecosystem integration.

[![CI](https://github.com/ContextMapper/context-mapper-json-converter/workflows/CI/badge.svg)](https://github.com/ContextMapper/context-mapper-json-converter/actions)
[![codecov](https://codecov.io/gh/ContextMapper/context-mapper-json-converter/branch/main/graph/badge.svg)](https://codecov.io/gh/ContextMapper/context-mapper-json-converter)
[![PyPI version](https://badge.fury.io/py/context-mapper-json-converter.svg)](https://badge.fury.io/py/context-mapper-json-converter)
[![Python versions](https://img.shields.io/pypi/pyversions/context-mapper-json-converter.svg)](https://pypi.org/project/context-mapper-json-converter/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Overview

The Context Mapper JSON Converter enables teams to define Domain-Driven Design (DDD) models using JSON format and convert them to valid Context Mapper DSL (CML) code. This approach provides:

- **Structured modeling** with JSON schema validation
- **Tool integration** with existing JSON-based workflows  
- **Comprehensive validation** at every step
- **Round-trip integrity** ensuring no information loss
- **Context Mapper ecosystem integration** for artifact generation

## ✨ Features

### Core Capabilities
- ✅ **Complete DDD Support** - Strategic and tactical patterns
- ✅ **Multi-Layer Validation** - JSON schema, semantic rules, CML syntax
- ✅ **Round-Trip Validation** - Ensures information preservation
- ✅ **Context Mapper Integration** - CLI tools and artifact generation
- ✅ **Production-Ready CLI** - Comprehensive command-line interface
- ✅ **Error Handling** - Detailed error reporting with suggestions

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

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI (when published)
pip install context-mapper-json-converter

# Or install from source
git clone https://github.com/ContextMapper/context-mapper-json-converter.git
cd context-mapper-json-converter
pip install -e .
```

### Basic Usage

1. **Create a JSON definition** (`my-system.json`):

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

2. **Convert to CML**:

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

3. **Generated CML output**:

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

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run property-based tests
pytest tests/test_properties.py

# Run specific test file
pytest tests/test_validation.py
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## Project Structure

```
context-mapper-json-converter/
├── src/                    # Source code
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── validation.py      # JSON validation engine
│   ├── converter.py       # JSON to CML converter
│   ├── cml_validator.py   # CML output validator
│   ├── error_handler.py   # Error handling and reporting
│   └── cli.py            # Command-line interface
├── schemas/               # JSON schema definitions
│   ├── context_map.json
│   ├── bounded_context.json
│   └── relationships.json
├── examples/              # Example JSON and CML files
├── tests/                 # Test suite
│   ├── test_validation.py
│   ├── test_converter.py
│   ├── test_properties.py
│   └── test_integration.py
├── pyproject.toml         # Project configuration
├── requirements.txt       # Dependencies
└── README.md             # This file
```

## Roadmap

Add an Issue, or submit a PR if there is a feature you want to see added.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Context Mapper](https://contextmapper.org/) - The original Context Mapper DSL and tooling
- [Domain-Driven Design](https://domainlanguage.com/ddd/) - The foundational concepts and patterns