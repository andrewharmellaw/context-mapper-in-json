# CLI Reference Guide

Complete command-line interface reference for the Context Mapper JSON Converter.

## 📋 Table of Contents

- [Installation](#installation)
- [Basic Commands](#basic-commands)
- [Advanced Commands](#advanced-commands)
- [Global Options](#global-options)
- [Configuration](#configuration)
- [Examples](#examples)
- [Exit Codes](#exit-codes)

## 🚀 Installation

The CLI is available after installing the package:

```bash
pip install -e .
```

Verify installation:
```bash
cml-convert --version
```

## 🔧 Basic Commands

### convert

Convert JSON definition to CML code.

```bash
cml-convert convert <input.json> <output.cml> [options]
```

**Arguments:**
- `input.json` - Path to JSON definition file
- `output.cml` - Path for generated CML output file

**Options:**
- `--validate-only` - Only validate, don't write output
- `--pretty` - Format output with indentation
- `--verbose` - Show detailed conversion progress

**Examples:**
```bash
# Basic conversion
cml-convert convert my-system.json my-system.cml

# Validate only
cml-convert convert my-system.json --validate-only

# Pretty formatted output
cml-convert convert my-system.json my-system.cml --pretty
```

### validate

Validate JSON definition without conversion.

```bash
cml-convert validate <input.json> [options]
```

**Arguments:**
- `input.json` - Path to JSON definition file

**Options:**
- `--schema-only` - Only JSON schema validation
- `--semantic-only` - Only semantic validation
- `--cml-syntax` - Include CML syntax validation
- `--detailed` - Show detailed validation results

**Examples:**
```bash
# Full validation
cml-convert validate my-system.json

# Schema validation only
cml-convert validate my-system.json --schema-only

# Detailed validation report
cml-convert validate my-system.json --detailed
```

## 🚀 Advanced Commands

### round-trip

Perform round-trip validation (JSON → CML → JSON).

```bash
cml-convert round-trip <input.json> [options]
```

**Arguments:**
- `input.json` - Path to JSON definition file

**Options:**
- `--save-intermediate` - Save intermediate CML file
- `--compare-detailed` - Show detailed comparison results
- `--tolerance <level>` - Set comparison tolerance (strict|normal|loose)

**Examples:**
```bash
# Basic round-trip validation
cml-convert round-trip my-system.json

# Save intermediate files
cml-convert round-trip my-system.json --save-intermediate

# Detailed comparison
cml-convert round-trip my-system.json --compare-detailed
```

### integration-status

Check Context Mapper ecosystem integration status.

```bash
cml-convert integration-status [options]
```

**Options:**
- `--check-java` - Check Java runtime availability
- `--check-cli` - Check Context Mapper CLI installation
- `--check-tools` - Check additional Context Mapper tools
- `--setup-help` - Show setup instructions

**Examples:**
```bash
# Check all integrations
cml-convert integration-status

# Check specific components
cml-convert integration-status --check-java --check-cli

# Get setup help
cml-convert integration-status --setup-help
```

### generate

Generate artifacts using Context Mapper tools.

```bash
cml-convert generate <input.json> <artifact-type> [options]
```

**Arguments:**
- `input.json` - Path to JSON definition file
- `artifact-type` - Type of artifact to generate (plantuml|mdsl|generic)

**Options:**
- `--output-dir <dir>` - Output directory for artifacts
- `--format <format>` - Specific format for artifact type
- `--context-mapper-cli` - Use Context Mapper CLI for generation

**Examples:**
```bash
# Generate PlantUML diagrams
cml-convert generate my-system.json plantuml --output-dir ./diagrams

# Generate MDSL specifications
cml-convert generate my-system.json mdsl --output-dir ./specs

# Use Context Mapper CLI
cml-convert generate my-system.json plantuml --context-mapper-cli
```

## ⚙️ Global Options

These options are available for all commands:

### Verbosity
- `--verbose, -v` - Increase output verbosity
- `--quiet, -q` - Suppress non-error output
- `--debug` - Enable debug logging

### Output Control
- `--no-color` - Disable colored output
- `--json-output` - Format output as JSON
- `--log-file <file>` - Write logs to file

### Validation Control
- `--enable-round-trip` - Enable round-trip validation for convert command
- `--use-context-mapper-cli` - Use Context Mapper CLI for validation
- `--strict-validation` - Enable strict validation mode
- `--skip-warnings` - Skip warning-level validation issues

### Performance
- `--parallel` - Enable parallel processing for large files
- `--memory-limit <mb>` - Set memory limit for processing
- `--timeout <seconds>` - Set operation timeout

## 📁 Configuration

### Configuration File

Create `.cml-convert.json` in your project root:

```json
{
  "validation": {
    "enableRoundTrip": true,
    "useContextMapperCli": false,
    "strictMode": false,
    "skipWarnings": false
  },
  "output": {
    "prettyFormat": true,
    "colorOutput": true,
    "verboseLogging": false
  },
  "integration": {
    "contextMapperCliPath": "/usr/local/bin/context-mapper-cli",
    "javaHome": "/usr/lib/jvm/java-11-openjdk",
    "artifactOutputDir": "./generated"
  },
  "performance": {
    "enableParallel": false,
    "memoryLimitMb": 512,
    "timeoutSeconds": 300
  }
}
```

### Environment Variables

- `CML_CONVERT_CONFIG` - Path to configuration file
- `CML_CONVERT_VERBOSE` - Enable verbose output (true/false)
- `CML_CONVERT_NO_COLOR` - Disable colored output (true/false)
- `CONTEXT_MAPPER_CLI_PATH` - Path to Context Mapper CLI
- `JAVA_HOME` - Java runtime location

### Configuration Precedence

1. Command-line options (highest priority)
2. Environment variables
3. Configuration file
4. Default values (lowest priority)

## 📚 Examples

### Basic Workflow

```bash
# 1. Validate your JSON definition
cml-convert validate ecommerce-system.json

# 2. Convert to CML with validation
cml-convert convert ecommerce-system.json ecommerce-system.cml \
  --enable-round-trip \
  --pretty

# 3. Generate artifacts
cml-convert generate ecommerce-system.json plantuml \
  --output-dir ./diagrams
```

### Advanced Validation Workflow

```bash
# 1. Schema validation only
cml-convert validate system.json --schema-only

# 2. Full validation with Context Mapper CLI
cml-convert validate system.json \
  --use-context-mapper-cli \
  --detailed

# 3. Round-trip validation
cml-convert round-trip system.json \
  --save-intermediate \
  --compare-detailed
```

### CI/CD Integration

```bash
# Validation in CI pipeline
cml-convert validate *.json --quiet --json-output > validation-results.json

# Convert with strict validation
cml-convert convert system.json system.cml \
  --strict-validation \
  --enable-round-trip \
  --use-context-mapper-cli

# Generate all artifacts
for file in *.json; do
  cml-convert generate "$file" plantuml --output-dir ./artifacts/plantuml
  cml-convert generate "$file" mdsl --output-dir ./artifacts/mdsl
done
```

### Batch Processing

```bash
# Process multiple files
for json_file in models/*.json; do
  cml_file="${json_file%.json}.cml"
  echo "Processing $json_file -> $cml_file"
  
  cml-convert convert "$json_file" "$cml_file" \
    --enable-round-trip \
    --verbose
done
```

### Integration Status Check

```bash
# Check integration status
cml-convert integration-status

# Setup Context Mapper CLI if needed
if ! cml-convert integration-status --check-cli --quiet; then
  echo "Context Mapper CLI not found"
  cml-convert integration-status --setup-help
fi
```

## 🚨 Exit Codes

The CLI uses standard exit codes:

| Code | Meaning | Description |
|------|---------|-------------|
| 0 | Success | Operation completed successfully |
| 1 | General Error | Unspecified error occurred |
| 2 | Validation Error | JSON validation failed |
| 3 | Conversion Error | CML conversion failed |
| 4 | File Error | File I/O error (not found, permissions, etc.) |
| 5 | Configuration Error | Invalid configuration or options |
| 6 | Integration Error | Context Mapper integration issue |
| 7 | Round-Trip Error | Round-trip validation failed |
| 8 | Timeout Error | Operation timed out |

### Error Handling Examples

```bash
# Check exit code in scripts
cml-convert validate system.json
case $? in
  0) echo "Validation successful" ;;
  2) echo "Validation failed" ;;
  4) echo "File not found" ;;
  *) echo "Unexpected error" ;;
esac

# Use in CI/CD
cml-convert convert system.json system.cml || exit 1
```

## 🔍 Troubleshooting

### Common Issues

**Command not found:**
```bash
# Ensure package is installed
pip install -e .

# Check PATH
which cml-convert
```

**Java not found:**
```bash
# Check Java installation
cml-convert integration-status --check-java

# Set JAVA_HOME
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk
```

**Context Mapper CLI issues:**
```bash
# Check CLI status
cml-convert integration-status --check-cli

# Get setup instructions
cml-convert integration-status --setup-help
```

**Memory issues with large files:**
```bash
# Increase memory limit
cml-convert convert large-system.json large-system.cml \
  --memory-limit 1024

# Enable parallel processing
cml-convert convert large-system.json large-system.cml \
  --parallel
```

### Debug Mode

Enable debug logging for troubleshooting:

```bash
# Debug mode
cml-convert convert system.json system.cml --debug

# Debug with log file
cml-convert convert system.json system.cml \
  --debug \
  --log-file debug.log
```

## 📖 See Also

- [JSON Schema Reference](json-schema-reference.md) - Complete schema documentation
- [API Documentation](api-documentation.md) - Python API reference
- [Validation Guide](validation-guide.md) - Validation layers and error handling
- [Integration Guide](integration-guide.md) - Context Mapper ecosystem integration
- [Troubleshooting](troubleshooting.md) - Common issues and solutions