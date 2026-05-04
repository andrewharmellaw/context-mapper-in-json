# Validation Guide

Comprehensive guide to the multi-layer validation system in the Context Mapper JSON Converter.

## 📋 Table of Contents

- [Overview](#overview)
- [Validation Layers](#validation-layers)
- [JSON Schema Validation](#json-schema-validation)
- [Semantic Validation](#semantic-validation)
- [Reference Validation](#reference-validation)
- [CML Syntax Validation](#cml-syntax-validation)
- [Round-Trip Validation](#round-trip-validation)
- [Context Mapper Integration](#context-mapper-integration)
- [Error Handling](#error-handling)
- [Validation Configuration](#validation-configuration)
- [Best Practices](#best-practices)

## 🎯 Overview

The Context Mapper JSON Converter implements a comprehensive multi-layer validation system to ensure the integrity and correctness of JSON definitions and generated CML code.

### Validation Philosophy

- **Fail Fast**: Detect errors as early as possible in the conversion pipeline
- **Comprehensive Coverage**: Validate structure, semantics, and cross-references
- **Clear Feedback**: Provide actionable error messages with suggestions
- **Configurable Strictness**: Support different validation levels for different use cases
- **Integration Ready**: Leverage Context Mapper tooling for authoritative validation

### Validation Pipeline

```
JSON Input
    ↓
1. JSON Schema Validation
    ↓
2. Semantic Validation
    ↓
3. Reference Validation
    ↓
4. CML Generation
    ↓
5. CML Syntax Validation
    ↓
6. Context Mapper Validation (optional)
    ↓
7. Round-Trip Validation (optional)
    ↓
Final Output
```

## 🏗️ Validation Layers

### Layer 1: JSON Schema Validation

Validates the structure and data types of the JSON input against predefined schemas.

**What it checks:**
- Required properties are present
- Data types match schema definitions
- Enum values are valid
- String lengths and patterns
- Array constraints

**Example:**
```python
from src.validation import ValidationEngine

validator = ValidationEngine()
result = validator.validate_json_schema(json_data)

if not result.is_valid:
    for error in result.errors:
        print(f"Schema error: {error.message} at {error.path}")
```

### Layer 2: Semantic Validation

Validates business rules and domain-specific constraints.

**What it checks:**
- Context names are unique within a Context Map
- Aggregate names are unique within a Bounded Context
- TEAM contexts can only realize other contexts
- Relationship types are appropriate for context types
- Domain vision statements meet length requirements

### Layer 3: Reference Validation

Validates cross-references and referential integrity.

**What it checks:**
- All contexts in `contains` exist in `boundedContexts`
- Relationship participants exist in the Context Map
- Subdomain implementations reference valid subdomains
- Aggregate owners reference valid TEAM contexts
- Exposed aggregates exist in the upstream context

### Layer 4: CML Syntax Validation

Validates the generated CML code for syntax correctness.

**What it checks:**
- CML grammar compliance
- Keyword usage
- Identifier validity
- Block structure
- Relationship syntax

### Layer 5: Context Mapper Integration (Optional)

Uses the official Context Mapper CLI for authoritative validation.

**What it checks:**
- Complete CML semantic validation
- Advanced constraint checking
- Context Mapper-specific rules
- Integration with Context Mapper ecosystem

### Layer 6: Round-Trip Validation (Optional)

Validates information preservation through the conversion process.

**What it checks:**
- JSON → CML → JSON consistency
- No information loss during conversion
- Semantic equivalence of original and reconstructed data

## 📝 JSON Schema Validation

### Schema Structure

The JSON schema validation uses a modular schema design:

```
schemas/
├── context_map.py      # Context Map schema
├── bounded_context.py  # Bounded Context schema
├── subdomain.py        # Subdomain schema
└── __init__.py        # Schema registry
```

### Validation Rules

#### Context Map Validation

```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "pattern": "^[A-Za-z][A-Za-z0-9_]*$",
      "minLength": 1,
      "maxLength": 100
    },
    "type": {
      "type": "string",
      "enum": ["SYSTEM_LANDSCAPE", "ORGANIZATIONAL"]
    },
    "contains": {
      "type": "array",
      "items": {"type": "string"},
      "minItems": 1,
      "uniqueItems": true
    }
  },
  "required": ["type", "contains"]
}
```

#### Bounded Context Validation

```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "pattern": "^[A-Za-z][A-Za-z0-9_]*$"
    },
    "type": {
      "type": "string",
      "enum": ["FEATURE", "APPLICATION", "SYSTEM", "TEAM"]
    },
    "domainVisionStatement": {
      "type": "string",
      "maxLength": 500
    }
  },
  "required": ["name", "type"]
}
```

### Common Schema Errors

| Error | Description | Solution |
|-------|-------------|----------|
| `missing_required_property` | Required property not provided | Add the missing property |
| `invalid_type` | Property has wrong data type | Check data type requirements |
| `invalid_enum_value` | Value not in allowed enum list | Use one of the allowed values |
| `pattern_mismatch` | String doesn't match required pattern | Follow naming conventions |
| `length_constraint` | String too long or too short | Adjust string length |

### Example Validation

```python
# Valid JSON
valid_json = {
    "contextMap": {
        "name": "ECommerceSystem",
        "type": "SYSTEM_LANDSCAPE",
        "contains": ["OrderManagement", "PaymentService"]
    }
}

# Invalid JSON - missing required property
invalid_json = {
    "contextMap": {
        "name": "ECommerceSystem"
        # Missing "type" and "contains"
    }
}

validator = ValidationEngine()
result = validator.validate_json_schema(invalid_json)
# Result will contain errors for missing properties
```

## 🧠 Semantic Validation

### Business Rules

#### Context Map Rules

1. **Unique Context Names**: All contexts in a Context Map must have unique names
2. **Valid Relationships**: Relationships must reference contexts that exist in the map
3. **No Self-Relationships**: A context cannot have a relationship with itself
4. **Consistent Types**: Relationship types must be appropriate for the context types

#### Bounded Context Rules

1. **TEAM Context Constraints**: Only TEAM contexts can have a `realizes` property
2. **Implementation Constraints**: `implements` must reference valid subdomains
3. **Aggregate Ownership**: Aggregate `owner` must reference a valid TEAM context
4. **Unique Aggregate Names**: Aggregate names must be unique within a context

#### Relationship Rules

1. **Participant Existence**: Both upstream and downstream contexts must exist
2. **Role Compatibility**: Upstream and downstream roles must be compatible
3. **Exposed Aggregates**: Must reference aggregates that exist in the upstream context
4. **Implementation Technology**: Must be reasonable for the relationship type

### Semantic Validation Examples

```python
# Example: Duplicate context names (invalid)
invalid_semantic = {
    "contextMap": {
        "type": "SYSTEM_LANDSCAPE",
        "contains": ["OrderService", "OrderService"]  # Duplicate!
    },
    "boundedContexts": [
        {"name": "OrderService", "type": "FEATURE"},
        {"name": "OrderService", "type": "SYSTEM"}  # Duplicate name!
    ]
}

# Example: Invalid relationship (invalid)
invalid_relationship = {
    "contextMap": {
        "type": "SYSTEM_LANDSCAPE",
        "contains": ["OrderService"],
        "relationships": [
            {
                "type": "Partnership",
                "upstream": "OrderService",
                "downstream": "PaymentService"  # PaymentService not in contains!
            }
        ]
    }
}

# Validation will catch these semantic errors
validator = ValidationEngine()
result = validator.validate_semantic_rules(invalid_semantic)
```

## 🔗 Reference Validation

### Cross-Reference Integrity

Reference validation ensures that all references between objects are valid and consistent.

#### Validation Checks

1. **Context Map Contains**: All contexts in `contains` must be defined in `boundedContexts`
2. **Relationship Participants**: All relationship upstream/downstream must exist in `contains`
3. **Subdomain Implementation**: All `implements` references must point to valid subdomains
4. **Team Realization**: All `realizes` references must point to valid contexts
5. **Aggregate Ownership**: All aggregate `owner` references must point to valid TEAM contexts
6. **Exposed Aggregates**: All `exposedAggregates` must exist in the upstream context

#### Reference Validation Algorithm

```python
def validate_references(self, json_data: Dict[str, Any]) -> ValidationResult:
    result = ValidationResult()
    
    # Extract all defined contexts
    defined_contexts = {ctx["name"] for ctx in json_data.get("boundedContexts", [])}
    
    # Validate Context Map contains
    if "contextMap" in json_data:
        contains = json_data["contextMap"].get("contains", [])
        for context_name in contains:
            if context_name not in defined_contexts:
                result.add_error(ValidationError(
                    f"Context '{context_name}' in contains not defined in boundedContexts",
                    path="contextMap.contains"
                ))
    
    # Validate relationships
    relationships = json_data.get("contextMap", {}).get("relationships", [])
    for i, rel in enumerate(relationships):
        upstream = rel.get("upstream")
        downstream = rel.get("downstream")
        
        if upstream not in contains:
            result.add_error(ValidationError(
                f"Upstream context '{upstream}' not in Context Map",
                path=f"contextMap.relationships[{i}].upstream"
            ))
        
        if downstream not in contains:
            result.add_error(ValidationError(
                f"Downstream context '{downstream}' not in Context Map",
                path=f"contextMap.relationships[{i}].downstream"
            ))
    
    return result
```

### Reference Validation Examples

```python
# Example: Missing context definition
missing_context = {
    "contextMap": {
        "type": "SYSTEM_LANDSCAPE",
        "contains": ["OrderService", "PaymentService"]  # PaymentService not defined
    },
    "boundedContexts": [
        {"name": "OrderService", "type": "FEATURE"}
        # PaymentService missing!
    ]
}

# Example: Invalid subdomain reference
invalid_subdomain_ref = {
    "boundedContexts": [
        {
            "name": "OrderService",
            "type": "FEATURE",
            "implements": ["OrderProcessing"]  # Subdomain not defined
        }
    ]
    # No subdomains defined
}

validator = ValidationEngine()
result = validator.validate_references(missing_context)
# Will report missing context definition error
```

## 🔍 CML Syntax Validation

### CML Grammar Validation

The CML syntax validator checks the generated CML code against the Context Mapper DSL grammar.

#### Validation Components

1. **Lexical Analysis**: Token recognition and validation
2. **Syntax Analysis**: Grammar rule compliance
3. **Semantic Analysis**: Context-aware validation
4. **Error Recovery**: Meaningful error messages

#### CML Syntax Rules

```cml
// Valid Context Map syntax
ContextMap ECommerceSystem type = SYSTEM_LANDSCAPE {
  contains OrderManagement, PaymentService
  
  PaymentService [OHS,PL]->[ACL] OrderManagement : REST API
}

// Valid Bounded Context syntax
BoundedContext OrderManagement type = FEATURE {
  domainVisionStatement = "Manages customer orders and order lifecycle"
  
  Aggregate Order {
    Entity Order {
      aggregateRoot
      - OrderId orderId key
      - CustomerId customerId
    }
  }
}
```

#### Common CML Syntax Errors

| Error | Description | Example |
|-------|-------------|---------|
| `missing_semicolon` | Statement not properly terminated | `contains OrderService PaymentService` |
| `invalid_identifier` | Invalid naming convention | `Context-Map` (hyphens not allowed) |
| `missing_braces` | Block not properly enclosed | `ContextMap Test {` (missing closing brace) |
| `invalid_relationship` | Malformed relationship syntax | `A -> B` (missing roles) |
| `unknown_keyword` | Unrecognized CML keyword | `InvalidKeyword Test` |

### CML Validation Examples

```python
from src.cml_validator import CMLValidator

# Valid CML
valid_cml = """
ContextMap ECommerceSystem type = SYSTEM_LANDSCAPE {
  contains OrderManagement, PaymentService
}

BoundedContext OrderManagement type = FEATURE {
  domainVisionStatement = "Manages orders"
}
"""

# Invalid CML - syntax error
invalid_cml = """
ContextMap ECommerceSystem type = SYSTEM_LANDSCAPE {
  contains OrderManagement PaymentService  // Missing comma
}
"""

validator = CMLValidator()
result = validator.validate_cml_syntax(invalid_cml)
if not result.is_valid:
    for error in result.errors:
        print(f"CML syntax error: {error.message}")
```

## 🔄 Round-Trip Validation

### Round-Trip Process

Round-trip validation ensures information preservation through the complete conversion cycle:

1. **Original JSON** → Convert to CML
2. **Generated CML** → Parse back to internal representation
3. **Internal Representation** → Convert back to JSON
4. **Reconstructed JSON** → Compare with original

### Comparison Algorithm

```python
def validate_round_trip(self, json_data: Dict[str, Any]) -> RoundTripResult:
    # Step 1: Convert JSON to CML
    converter = ConverterEngine()
    cml_code = converter.convert(json_data)
    
    # Step 2: Parse CML back to internal representation
    parser = CMLParser()
    parsed_data = parser.parse(cml_code)
    
    # Step 3: Convert internal representation back to JSON
    reconstructed_json = converter.to_json(parsed_data)
    
    # Step 4: Compare original and reconstructed JSON
    comparison = self.compare_json(json_data, reconstructed_json)
    
    return RoundTripResult(
        is_valid=comparison.is_equivalent,
        differences=comparison.differences,
        similarity_score=comparison.similarity_score
    )
```

### Comparison Tolerance Levels

#### Strict Mode
- Exact match required for all properties
- Property order must be preserved
- No additional or missing properties allowed

#### Normal Mode (Default)
- Semantic equivalence required
- Property order can differ
- Optional properties with default values can be omitted

#### Loose Mode
- Core properties must match
- Additional metadata properties can differ
- Minor formatting differences allowed

### Round-Trip Validation Examples

```python
from src.round_trip_validator import RoundTripValidator

validator = RoundTripValidator()

# Test round-trip validation
original_json = {
    "contextMap": {
        "name": "TestSystem",
        "type": "SYSTEM_LANDSCAPE",
        "contains": ["ServiceA", "ServiceB"]
    },
    "boundedContexts": [
        {"name": "ServiceA", "type": "FEATURE"},
        {"name": "ServiceB", "type": "SYSTEM"}
    ]
}

result = validator.validate_round_trip(original_json)
if result.is_valid:
    print("Round-trip validation passed")
    print(f"Similarity score: {result.similarity_score}")
else:
    print("Round-trip validation failed")
    for diff in result.differences:
        print(f"  - {diff}")
```

## 🔧 Context Mapper Integration

### Integration Validation

When Context Mapper CLI is available, the system can perform authoritative validation using the official tooling.

#### Integration Setup

```python
from src.context_mapper_integration import ContextMapperIntegration

integration = ContextMapperIntegration()

# Check integration status
status = integration.get_integration_status()
print(f"Java available: {status.java_available}")
print(f"CLI available: {status.cli_available}")

if status.cli_available:
    # Use Context Mapper for validation
    result = integration.validate_with_cli(cml_code)
else:
    print("Context Mapper CLI not available")
    print("Setup instructions:")
    for instruction in status.setup_instructions:
        print(f"  - {instruction}")
```

#### Context Mapper Validation Benefits

1. **Authoritative Validation**: Uses the official Context Mapper parser
2. **Complete Rule Coverage**: Includes all Context Mapper validation rules
3. **Future Compatibility**: Automatically supports new CML features
4. **Ecosystem Integration**: Validates compatibility with Context Mapper tools

### Integration Validation Examples

```python
# Validate with Context Mapper CLI
integration = ContextMapperIntegration()
if integration.check_cli_availability():
    result = integration.validate_with_cli(cml_code)
    if result.is_valid:
        print("Context Mapper validation passed")
    else:
        print("Context Mapper validation failed:")
        for error in result.errors:
            print(f"  - {error.message}")
else:
    print("Context Mapper CLI not available - using internal validation")
```

## 🚨 Error Handling

### Error Categories

#### Validation Errors
- **Schema Errors**: JSON structure violations
- **Semantic Errors**: Business rule violations
- **Reference Errors**: Cross-reference integrity violations
- **Syntax Errors**: CML grammar violations

#### Error Severity Levels

1. **Error**: Prevents successful conversion
2. **Warning**: Potential issues that don't prevent conversion
3. **Info**: Informational messages and suggestions

### Error Message Format

```python
class ValidationError:
    message: str          # Human-readable error description
    path: str            # JSON path to the error location
    code: str            # Error code for programmatic handling
    severity: str        # "error", "warning", or "info"
    suggestions: List[str]  # Actionable suggestions for fixing
```

### Error Examples

```python
# Schema validation error
ValidationError(
    message="Property 'type' is required but missing",
    path="contextMap",
    code="MISSING_REQUIRED_PROPERTY",
    severity="error",
    suggestions=[
        "Add 'type' property with value 'SYSTEM_LANDSCAPE' or 'ORGANIZATIONAL'",
        "See JSON Schema Reference for required properties"
    ]
)

# Semantic validation error
ValidationError(
    message="Context name 'OrderService' is not unique",
    path="boundedContexts[1].name",
    code="DUPLICATE_CONTEXT_NAME",
    severity="error",
    suggestions=[
        "Use unique names for all bounded contexts",
        "Consider renaming to 'OrderManagementService' or 'OrderProcessingService'"
    ]
)

# Reference validation warning
ValidationWarning(
    message="Aggregate owner 'OrderTeam' not found in TEAM contexts",
    path="boundedContexts[0].aggregates[0].owner",
    code="MISSING_TEAM_REFERENCE",
    severity="warning",
    suggestions=[
        "Define 'OrderTeam' as a TEAM bounded context",
        "Remove the owner property if team ownership is not needed"
    ]
)
```

## ⚙️ Validation Configuration

### Configuration Options

```python
class ValidationConfig:
    # Validation levels
    enable_schema_validation: bool = True
    enable_semantic_validation: bool = True
    enable_reference_validation: bool = True
    enable_cml_validation: bool = True
    enable_round_trip_validation: bool = False
    
    # Strictness levels
    strict_mode: bool = False
    fail_on_warnings: bool = False
    skip_info_messages: bool = False
    
    # Integration options
    use_context_mapper_cli: bool = False
    context_mapper_cli_path: Optional[str] = None
    
    # Performance options
    parallel_validation: bool = False
    validation_timeout: int = 300
```

### Configuration Examples

```python
# Strict validation configuration
strict_config = ValidationConfig(
    strict_mode=True,
    fail_on_warnings=True,
    enable_round_trip_validation=True,
    use_context_mapper_cli=True
)

# Lenient validation configuration
lenient_config = ValidationConfig(
    strict_mode=False,
    fail_on_warnings=False,
    skip_info_messages=True,
    enable_round_trip_validation=False
)

# Performance-optimized configuration
performance_config = ValidationConfig(
    parallel_validation=True,
    validation_timeout=60,
    enable_cml_validation=False  # Skip for faster processing
)
```

## 🎯 Best Practices

### Validation Strategy

1. **Start with Schema Validation**: Always validate JSON structure first
2. **Use Incremental Validation**: Validate at each step of the pipeline
3. **Enable Context Mapper Integration**: Use official tooling when available
4. **Configure Appropriately**: Match validation strictness to your use case
5. **Handle Errors Gracefully**: Provide clear feedback and suggestions

### Development Workflow

```python
def development_validation_workflow(json_data: Dict[str, Any]):
    """Recommended validation workflow for development."""
    
    validator = ValidationEngine()
    
    # Step 1: Quick schema validation
    schema_result = validator.validate_json_schema(json_data)
    if not schema_result.is_valid:
        print("Fix schema errors first:")
        for error in schema_result.errors:
            print(f"  - {error.message} at {error.path}")
        return False
    
    # Step 2: Semantic validation
    semantic_result = validator.validate_semantic_rules(json_data)
    if not semantic_result.is_valid:
        print("Fix semantic errors:")
        for error in semantic_result.errors:
            print(f"  - {error.message}")
        return False
    
    # Step 3: Reference validation
    reference_result = validator.validate_references(json_data)
    if not reference_result.is_valid:
        print("Fix reference errors:")
        for error in reference_result.errors:
            print(f"  - {error.message}")
        return False
    
    # Step 4: Full conversion with CML validation
    try:
        converter = ConverterEngine()
        cml_output = converter.convert(json_data)
        
        cml_validator = CMLValidator()
        cml_result = cml_validator.validate_cml_syntax(cml_output)
        
        if not cml_result.is_valid:
            print("CML generation issues:")
            for error in cml_result.errors:
                print(f"  - {error.message}")
            return False
        
        print("All validations passed!")
        return True
        
    except Exception as e:
        print(f"Conversion failed: {e}")
        return False
```

### Production Workflow

```python
def production_validation_workflow(json_data: Dict[str, Any]):
    """Recommended validation workflow for production."""
    
    config = ValidationConfig(
        strict_mode=True,
        enable_round_trip_validation=True,
        use_context_mapper_cli=True,
        fail_on_warnings=True
    )
    
    validator = ValidationEngine(config)
    
    # Complete validation
    result = validator.validate_complete(json_data)
    
    if not result.is_valid:
        # Log all errors and warnings
        for error in result.errors:
            logger.error(f"Validation error: {error.message} at {error.path}")
        
        for warning in result.warnings:
            logger.warning(f"Validation warning: {warning.message} at {warning.path}")
        
        return False
    
    # Round-trip validation
    round_trip_validator = RoundTripValidator(config)
    round_trip_result = round_trip_validator.validate_round_trip(json_data)
    
    if not round_trip_result.is_valid:
        logger.error("Round-trip validation failed")
        for diff in round_trip_result.differences:
            logger.error(f"  - {diff}")
        return False
    
    logger.info("All production validations passed")
    return True
```

### Testing Validation

```python
def test_validation_scenarios():
    """Test various validation scenarios."""
    
    # Test valid input
    valid_json = {...}  # Valid JSON definition
    assert validator.validate_complete(valid_json).is_valid
    
    # Test schema errors
    invalid_schema = {...}  # Missing required properties
    result = validator.validate_json_schema(invalid_schema)
    assert not result.is_valid
    assert any("required" in error.code for error in result.errors)
    
    # Test semantic errors
    invalid_semantic = {...}  # Duplicate names
    result = validator.validate_semantic_rules(invalid_semantic)
    assert not result.is_valid
    assert any("DUPLICATE" in error.code for error in result.errors)
    
    # Test reference errors
    invalid_references = {...}  # Missing context definitions
    result = validator.validate_references(invalid_references)
    assert not result.is_valid
    assert any("NOT_FOUND" in error.code for error in result.errors)
```

## 🔗 See Also

- [JSON Schema Reference](json-schema-reference.md) - Complete schema documentation
- [CLI Reference](cli-reference.md) - Command-line validation options
- [API Documentation](api-documentation.md) - Python validation API
- [Integration Guide](integration-guide.md) - Context Mapper integration setup
- [Troubleshooting](troubleshooting.md) - Common validation issues and solutions