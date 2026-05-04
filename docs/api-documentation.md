# API Documentation

Complete Python API reference for the Context Mapper JSON Converter.

## 📋 Table of Contents

- [Overview](#overview)
- [Core Classes](#core-classes)
- [Validation Engine](#validation-engine)
- [Converter Engine](#converter-engine)
- [CML Validator](#cml-validator)
- [Error Handling](#error-handling)
- [Configuration](#configuration)
- [Integration Classes](#integration-classes)
- [Usage Examples](#usage-examples)
- [Type Definitions](#type-definitions)

## 🎯 Overview

The Context Mapper JSON Converter provides a comprehensive Python API for converting JSON definitions to Context Mapper DSL (CML) code with full validation support.

### Quick Start

```python
from src import ConverterEngine, ValidationEngine

# Basic usage
validator = ValidationEngine()
converter = ConverterEngine()

# Validate JSON
result = validator.validate_json_schema(json_data)
if result.is_valid:
    # Convert to CML
    cml_output = converter.convert(json_data)
    print(cml_output)
```

## 🏗️ Core Classes

### ConverterEngine

Main conversion engine for transforming JSON to CML.

```python
class ConverterEngine:
    def __init__(self, config: Optional[Config] = None)
    def convert(self, json_data: Dict[str, Any]) -> str
    def convert_context_map(self, context_map: Dict[str, Any]) -> str
    def convert_bounded_contexts(self, contexts: List[Dict[str, Any]]) -> str
    def convert_subdomains(self, subdomains: List[Dict[str, Any]], domain_name: str) -> str
```

#### Methods

**`__init__(config: Optional[Config] = None)`**
- Initialize converter with optional configuration
- **Parameters:**
  - `config`: Configuration object (uses default if None)

**`convert(json_data: Dict[str, Any]) -> str`**
- Convert complete JSON definition to CML
- **Parameters:**
  - `json_data`: Complete JSON definition
- **Returns:** Generated CML code as string
- **Raises:** `ValidationError`, `ConversionError`

**`convert_context_map(context_map: Dict[str, Any]) -> str`**
- Convert Context Map definition to CML
- **Parameters:**
  - `context_map`: Context Map JSON object
- **Returns:** CML Context Map definition

**`convert_bounded_contexts(contexts: List[Dict[str, Any]]) -> str`**
- Convert Bounded Context definitions to CML
- **Parameters:**
  - `contexts`: List of Bounded Context JSON objects
- **Returns:** CML Bounded Context definitions

**`convert_subdomains(subdomains: List[Dict[str, Any]], domain_name: str) -> str`**
- Convert Subdomain definitions to CML
- **Parameters:**
  - `subdomains`: List of Subdomain JSON objects
  - `domain_name`: Name of the domain
- **Returns:** CML Subdomain definitions

#### Example Usage

```python
from src.converter import ConverterEngine
from src.config import Config

# Initialize with custom config
config = Config(
    enable_pretty_formatting=True,
    validate_cml_output=True
)
converter = ConverterEngine(config)

# Convert JSON to CML
json_data = {
    "contextMap": {
        "name": "ECommerceSystem",
        "type": "SYSTEM_LANDSCAPE",
        "contains": ["OrderManagement", "PaymentService"]
    },
    "boundedContexts": [
        {
            "name": "OrderManagement",
            "type": "FEATURE",
            "domainVisionStatement": "Manages customer orders"
        }
    ]
}

cml_output = converter.convert(json_data)
print(cml_output)
```

## ✅ Validation Engine

Comprehensive validation system with multiple validation layers.

```python
class ValidationEngine:
    def __init__(self, config: Optional[Config] = None)
    def validate_json_schema(self, json_data: Dict[str, Any]) -> ValidationResult
    def validate_semantic_rules(self, json_data: Dict[str, Any]) -> ValidationResult
    def validate_references(self, json_data: Dict[str, Any]) -> ValidationResult
    def validate_complete(self, json_data: Dict[str, Any]) -> ValidationResult
```

#### Methods

**`validate_json_schema(json_data: Dict[str, Any]) -> ValidationResult`**
- Validate JSON against schema definitions
- **Parameters:**
  - `json_data`: JSON data to validate
- **Returns:** ValidationResult with schema validation results

**`validate_semantic_rules(json_data: Dict[str, Any]) -> ValidationResult`**
- Validate business rules and semantic constraints
- **Parameters:**
  - `json_data`: JSON data to validate
- **Returns:** ValidationResult with semantic validation results

**`validate_references(json_data: Dict[str, Any]) -> ValidationResult`**
- Validate cross-references and integrity constraints
- **Parameters:**
  - `json_data`: JSON data to validate
- **Returns:** ValidationResult with reference validation results

**`validate_complete(json_data: Dict[str, Any]) -> ValidationResult`**
- Perform complete validation (schema + semantic + references)
- **Parameters:**
  - `json_data`: JSON data to validate
- **Returns:** Combined ValidationResult

#### ValidationResult

```python
class ValidationResult:
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationWarning]
    info: List[ValidationInfo]
    
    def add_error(self, error: ValidationError) -> None
    def add_warning(self, warning: ValidationWarning) -> None
    def add_info(self, info: ValidationInfo) -> None
    def to_dict(self) -> Dict[str, Any]
```

#### Example Usage

```python
from src.validation import ValidationEngine

validator = ValidationEngine()

# Validate JSON schema
result = validator.validate_json_schema(json_data)
if not result.is_valid:
    for error in result.errors:
        print(f"Error: {error.message} at {error.path}")

# Complete validation
result = validator.validate_complete(json_data)
print(f"Validation result: {'PASS' if result.is_valid else 'FAIL'}")
print(f"Errors: {len(result.errors)}")
print(f"Warnings: {len(result.warnings)}")
```

## 🔍 CML Validator

Validates generated CML syntax and semantics.

```python
class CMLValidator:
    def __init__(self, config: Optional[Config] = None)
    def validate_cml_syntax(self, cml_code: str) -> ValidationResult
    def validate_cml_semantics(self, cml_code: str) -> ValidationResult
    def validate_with_context_mapper(self, cml_code: str) -> ValidationResult
```

#### Methods

**`validate_cml_syntax(cml_code: str) -> ValidationResult`**
- Validate CML syntax using internal parser
- **Parameters:**
  - `cml_code`: CML code to validate
- **Returns:** ValidationResult with syntax validation results

**`validate_cml_semantics(cml_code: str) -> ValidationResult`**
- Validate CML semantic rules
- **Parameters:**
  - `cml_code`: CML code to validate
- **Returns:** ValidationResult with semantic validation results

**`validate_with_context_mapper(cml_code: str) -> ValidationResult`**
- Validate using Context Mapper CLI (if available)
- **Parameters:**
  - `cml_code`: CML code to validate
- **Returns:** ValidationResult from Context Mapper validation

#### Example Usage

```python
from src.cml_validator import CMLValidator

validator = CMLValidator()

# Validate CML syntax
result = validator.validate_cml_syntax(cml_code)
if result.is_valid:
    print("CML syntax is valid")
else:
    for error in result.errors:
        print(f"Syntax error: {error.message}")

# Validate with Context Mapper CLI
result = validator.validate_with_context_mapper(cml_code)
```

## 🚨 Error Handling

Comprehensive error handling with detailed error information.

### Exception Hierarchy

```python
class ConverterError(Exception):
    """Base exception for converter errors"""
    pass

class ValidationError(ConverterError):
    """Validation-related errors"""
    def __init__(self, message: str, path: str = "", code: str = "")

class ConversionError(ConverterError):
    """Conversion-related errors"""
    def __init__(self, message: str, context: str = "")

class ConfigurationError(ConverterError):
    """Configuration-related errors"""
    pass

class IntegrationError(ConverterError):
    """Context Mapper integration errors"""
    pass
```

### Error Details

```python
class ErrorDetail:
    message: str
    path: str
    code: str
    severity: str  # "error", "warning", "info"
    suggestions: List[str]
    
    def to_dict(self) -> Dict[str, Any]
```

#### Example Usage

```python
from src.error_handler import ErrorHandler
from src.validation import ValidationError

try:
    result = converter.convert(json_data)
except ValidationError as e:
    print(f"Validation failed: {e.message}")
    print(f"Path: {e.path}")
    print(f"Code: {e.code}")
except ConversionError as e:
    print(f"Conversion failed: {e.message}")
    print(f"Context: {e.context}")
```

## ⚙️ Configuration

Configuration management for the converter system.

```python
class Config:
    def __init__(self,
                 enable_pretty_formatting: bool = True,
                 validate_cml_output: bool = True,
                 enable_round_trip_validation: bool = False,
                 use_context_mapper_cli: bool = False,
                 strict_validation: bool = False,
                 parallel_processing: bool = False,
                 memory_limit_mb: int = 512,
                 timeout_seconds: int = 300)
    
    @classmethod
    def from_file(cls, config_path: str) -> 'Config'
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'Config'
    
    def to_dict(self) -> Dict[str, Any]
    def merge(self, other: 'Config') -> 'Config'
```

#### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enable_pretty_formatting` | bool | True | Format CML output with indentation |
| `validate_cml_output` | bool | True | Validate generated CML syntax |
| `enable_round_trip_validation` | bool | False | Enable round-trip validation |
| `use_context_mapper_cli` | bool | False | Use Context Mapper CLI for validation |
| `strict_validation` | bool | False | Enable strict validation mode |
| `parallel_processing` | bool | False | Enable parallel processing |
| `memory_limit_mb` | int | 512 | Memory limit for processing |
| `timeout_seconds` | int | 300 | Operation timeout |

#### Example Usage

```python
from src.config import Config

# Create configuration
config = Config(
    enable_pretty_formatting=True,
    validate_cml_output=True,
    enable_round_trip_validation=True,
    use_context_mapper_cli=True
)

# Load from file
config = Config.from_file('.cml-convert.json')

# Load from dictionary
config_dict = {
    "validation": {
        "enableRoundTrip": True,
        "useContextMapperCli": False
    }
}
config = Config.from_dict(config_dict)
```

## 🔧 Integration Classes

### Context Mapper Integration

```python
class ContextMapperIntegration:
    def __init__(self, config: Optional[Config] = None)
    def check_java_availability(self) -> bool
    def check_cli_availability(self) -> bool
    def get_integration_status(self) -> IntegrationStatus
    def validate_with_cli(self, cml_code: str) -> ValidationResult
    def generate_artifacts(self, cml_code: str, artifact_type: str, output_dir: str) -> List[str]
```

### Round-Trip Validator

```python
class RoundTripValidator:
    def __init__(self, config: Optional[Config] = None)
    def validate_round_trip(self, json_data: Dict[str, Any]) -> RoundTripResult
    def compare_json(self, original: Dict[str, Any], reconstructed: Dict[str, Any]) -> ComparisonResult
```

#### Example Usage

```python
from src.context_mapper_integration import ContextMapperIntegration
from src.round_trip_validator import RoundTripValidator

# Check integration status
integration = ContextMapperIntegration()
status = integration.get_integration_status()
print(f"Java available: {status.java_available}")
print(f"CLI available: {status.cli_available}")

# Round-trip validation
round_trip = RoundTripValidator()
result = round_trip.validate_round_trip(json_data)
if result.is_valid:
    print("Round-trip validation passed")
else:
    print(f"Round-trip validation failed: {result.differences}")
```

## 📚 Usage Examples

### Basic Conversion

```python
from src import ConverterEngine, ValidationEngine

def convert_json_to_cml(json_file_path: str, cml_file_path: str):
    """Convert JSON file to CML file with validation."""
    
    # Load JSON data
    with open(json_file_path, 'r') as f:
        json_data = json.load(f)
    
    # Validate JSON
    validator = ValidationEngine()
    result = validator.validate_complete(json_data)
    
    if not result.is_valid:
        print("Validation failed:")
        for error in result.errors:
            print(f"  - {error.message}")
        return False
    
    # Convert to CML
    converter = ConverterEngine()
    cml_output = converter.convert(json_data)
    
    # Save CML output
    with open(cml_file_path, 'w') as f:
        f.write(cml_output)
    
    print(f"Successfully converted {json_file_path} to {cml_file_path}")
    return True
```

### Advanced Validation

```python
from src import ValidationEngine, CMLValidator, Config

def advanced_validation(json_data: Dict[str, Any]) -> bool:
    """Perform comprehensive validation with detailed reporting."""
    
    config = Config(
        strict_validation=True,
        use_context_mapper_cli=True
    )
    
    # JSON validation
    validator = ValidationEngine(config)
    json_result = validator.validate_complete(json_data)
    
    if not json_result.is_valid:
        print("JSON validation failed")
        return False
    
    # Convert to CML
    converter = ConverterEngine(config)
    cml_code = converter.convert(json_data)
    
    # CML validation
    cml_validator = CMLValidator(config)
    cml_result = cml_validator.validate_with_context_mapper(cml_code)
    
    if not cml_result.is_valid:
        print("CML validation failed")
        return False
    
    print("All validations passed")
    return True
```

### Batch Processing

```python
import os
from pathlib import Path
from src import ConverterEngine, ValidationEngine

def batch_convert(input_dir: str, output_dir: str):
    """Convert all JSON files in a directory to CML."""
    
    validator = ValidationEngine()
    converter = ConverterEngine()
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    for json_file in input_path.glob("*.json"):
        print(f"Processing {json_file.name}...")
        
        try:
            # Load and validate JSON
            with open(json_file, 'r') as f:
                json_data = json.load(f)
            
            result = validator.validate_complete(json_data)
            if not result.is_valid:
                print(f"  Validation failed for {json_file.name}")
                continue
            
            # Convert to CML
            cml_output = converter.convert(json_data)
            
            # Save CML file
            cml_file = output_path / f"{json_file.stem}.cml"
            with open(cml_file, 'w') as f:
                f.write(cml_output)
            
            print(f"  Successfully converted to {cml_file.name}")
            
        except Exception as e:
            print(f"  Error processing {json_file.name}: {e}")
```

### Integration with Context Mapper

```python
from src import ConverterEngine, ContextMapperIntegration

def convert_and_generate_artifacts(json_data: Dict[str, Any], output_dir: str):
    """Convert JSON to CML and generate Context Mapper artifacts."""
    
    # Convert to CML
    converter = ConverterEngine()
    cml_code = converter.convert(json_data)
    
    # Check Context Mapper integration
    integration = ContextMapperIntegration()
    status = integration.get_integration_status()
    
    if not status.cli_available:
        print("Context Mapper CLI not available")
        return
    
    # Generate artifacts
    artifacts = integration.generate_artifacts(
        cml_code, 
        "plantuml", 
        output_dir
    )
    
    print(f"Generated {len(artifacts)} artifacts:")
    for artifact in artifacts:
        print(f"  - {artifact}")
```

## 📊 Type Definitions

### Core Types

```python
from typing import Dict, List, Any, Optional, Union

# JSON data types
JsonData = Dict[str, Any]
ContextMapData = Dict[str, Any]
BoundedContextData = Dict[str, Any]
SubdomainData = Dict[str, Any]

# Validation types
ValidationLevel = Literal["error", "warning", "info"]
ValidationCode = str
ValidationPath = str

# Configuration types
ConfigDict = Dict[str, Any]
```

### Result Types

```python
class ValidationResult:
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationWarning]
    info: List[ValidationInfo]

class ConversionResult:
    success: bool
    cml_output: Optional[str]
    errors: List[ConversionError]

class RoundTripResult:
    is_valid: bool
    differences: List[str]
    similarity_score: float

class IntegrationStatus:
    java_available: bool
    cli_available: bool
    tools_available: Dict[str, bool]
    setup_instructions: List[str]
```

## 🔗 See Also

- [CLI Reference](cli-reference.md) - Command-line interface guide
- [JSON Schema Reference](json-schema-reference.md) - Complete schema documentation
- [Validation Guide](validation-guide.md) - Validation layers and error handling
- [Integration Guide](integration-guide.md) - Context Mapper ecosystem integration
- [Troubleshooting](troubleshooting.md) - Common issues and solutions