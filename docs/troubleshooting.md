# Troubleshooting Guide

Comprehensive troubleshooting guide for common issues with the Context Mapper JSON Converter.

## 📋 Table of Contents

- [Quick Diagnostics](#quick-diagnostics)
- [Installation Issues](#installation-issues)
- [Validation Errors](#validation-errors)
- [Conversion Problems](#conversion-problems)
- [Integration Issues](#integration-issues)
- [Performance Problems](#performance-problems)
- [CLI Issues](#cli-issues)
- [Configuration Problems](#configuration-problems)
- [Error Reference](#error-reference)
- [Getting Help](#getting-help)

## 🔍 Quick Diagnostics

### System Check

Run this comprehensive system check to identify common issues:

```bash
# Check system status
cml-convert integration-status --detailed

# Check Python environment
python --version
pip list | grep -E "(jsonschema|pydantic|click)"

# Check Java environment
java -version
echo $JAVA_HOME

# Check file permissions
ls -la models/
ls -la generated/
```

### Health Check Script

```bash
#!/bin/bash
# health-check.sh - Comprehensive system health check

echo "🔍 Context Mapper JSON Converter Health Check"
echo "=============================================="

# Python environment
echo "📍 Python Environment:"
python --version
pip show context-mapper-json-converter 2>/dev/null || echo "  Package not installed"

# Java environment
echo "📍 Java Environment:"
if command -v java &> /dev/null; then
    java -version
    echo "  JAVA_HOME: ${JAVA_HOME:-"Not set"}"
else
    echo "  ❌ Java not found"
fi

# Context Mapper CLI
echo "📍 Context Mapper CLI:"
if command -v context-mapper-cli &> /dev/null; then
    context-mapper-cli --version 2>/dev/null || echo "  ❌ CLI not working"
else
    echo "  ❌ CLI not found"
fi

# File system
echo "📍 File System:"
echo "  Current directory: $(pwd)"
echo "  Write permissions: $(test -w . && echo "✅ OK" || echo "❌ No write access")"

# Integration status
echo "📍 Integration Status:"
cml-convert integration-status 2>/dev/null || echo "  ❌ Integration check failed"

echo "=============================================="
echo "Health check completed"
```

## 🚀 Installation Issues

### Package Installation Problems

#### Issue: `pip install` fails

**Symptoms:**
```
ERROR: Could not find a version that satisfies the requirement context-mapper-json-converter
```

**Solutions:**

1. **Update pip:**
```bash
pip install --upgrade pip
```

2. **Install in development mode:**
```bash
git clone <repository-url>
cd context-mapper-json-converter
pip install -e .
```

3. **Use virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

4. **Check Python version:**
```bash
python --version  # Should be 3.8 or higher
```

#### Issue: Missing dependencies

**Symptoms:**
```
ModuleNotFoundError: No module named 'jsonschema'
```

**Solutions:**

1. **Install missing dependencies:**
```bash
pip install -r requirements.txt
```

2. **Reinstall package:**
```bash
pip uninstall context-mapper-json-converter
pip install -e .
```

3. **Check requirements file:**
```bash
cat requirements.txt
pip check
```

### Command Not Found

#### Issue: `cml-convert` command not found

**Symptoms:**
```
bash: cml-convert: command not found
```

**Solutions:**

1. **Check installation:**
```bash
pip show context-mapper-json-converter
```

2. **Check PATH:**
```bash
echo $PATH
which python
which pip
```

3. **Reinstall in development mode:**
```bash
pip install -e .
```

4. **Use Python module directly:**
```bash
python -m src.cli convert input.json output.cml
```

## ✅ Validation Errors

### JSON Schema Validation

#### Issue: Required property missing

**Error:**
```
ValidationError: Property 'type' is required but missing at contextMap
```

**Solution:**
```json
{
  "contextMap": {
    "name": "MySystem",
    "type": "SYSTEM_LANDSCAPE",  // Add missing type
    "contains": ["ServiceA", "ServiceB"]
  }
}
```

#### Issue: Invalid enum value

**Error:**
```
ValidationError: 'INVALID_TYPE' is not a valid value for contextMap.type
```

**Solution:**
Use valid enum values:
```json
{
  "contextMap": {
    "type": "SYSTEM_LANDSCAPE"  // or "ORGANIZATIONAL"
  }
}
```

#### Issue: Pattern mismatch

**Error:**
```
ValidationError: 'invalid-name' does not match pattern '^[A-Za-z][A-Za-z0-9_]*$'
```

**Solution:**
Use valid naming convention:
```json
{
  "name": "ValidName"  // Start with letter, use only letters, numbers, underscores
}
```

### Semantic Validation

#### Issue: Duplicate context names

**Error:**
```
SemanticError: Context name 'OrderService' is not unique
```

**Solution:**
```json
{
  "boundedContexts": [
    {"name": "OrderManagementService", "type": "FEATURE"},
    {"name": "OrderProcessingService", "type": "SYSTEM"}  // Use unique names
  ]
}
```

#### Issue: Invalid relationship

**Error:**
```
ReferenceError: Upstream context 'PaymentService' not found in Context Map
```

**Solution:**
```json
{
  "contextMap": {
    "contains": ["OrderService", "PaymentService"],  // Include all referenced contexts
    "relationships": [
      {
        "type": "CustomerSupplier",
        "upstream": "PaymentService",
        "downstream": "OrderService"
      }
    ]
  }
}
```

### Reference Validation

#### Issue: Missing context definition

**Error:**
```
ReferenceError: Context 'PaymentService' in contains not defined in boundedContexts
```

**Solution:**
```json
{
  "contextMap": {
    "contains": ["OrderService", "PaymentService"]
  },
  "boundedContexts": [
    {"name": "OrderService", "type": "FEATURE"},
    {"name": "PaymentService", "type": "SYSTEM"}  // Add missing definition
  ]
}
```

## 🔄 Conversion Problems

### CML Generation Issues

#### Issue: Invalid CML syntax generated

**Error:**
```
CMLSyntaxError: Unexpected token at line 5, column 12
```

**Diagnosis:**
```bash
# Check generated CML
cml-convert convert input.json output.cml --debug

# Validate CML syntax
cml-convert validate-cml output.cml
```

**Solutions:**

1. **Check input JSON:**
```bash
# Validate JSON first
cml-convert validate input.json --detailed
```

2. **Use pretty formatting:**
```bash
cml-convert convert input.json output.cml --pretty
```

3. **Enable debug mode:**
```bash
cml-convert convert input.json output.cml --debug --log-file debug.log
```

#### Issue: Missing CML elements

**Problem:** Generated CML is incomplete or missing expected elements.

**Diagnosis:**
```bash
# Compare input and output
echo "Input JSON structure:"
jq 'keys' input.json

echo "Generated CML:"
cat output.cml
```

**Solutions:**

1. **Check JSON completeness:**
```json
{
  "contextMap": { /* required */ },
  "boundedContexts": [ /* required */ ],
  "subdomains": [ /* optional */ ]
}
```

2. **Validate conversion step by step:**
```python
from src.converter import ConverterEngine

converter = ConverterEngine()

# Test individual components
context_map_cml = converter.convert_context_map(json_data["contextMap"])
print("Context Map CML:", context_map_cml)

contexts_cml = converter.convert_bounded_contexts(json_data["boundedContexts"])
print("Bounded Contexts CML:", contexts_cml)
```

### Round-Trip Validation Failures

#### Issue: Round-trip validation fails

**Error:**
```
RoundTripError: Information loss detected during conversion
```

**Diagnosis:**
```bash
# Enable round-trip validation with details
cml-convert convert input.json output.cml \
  --enable-round-trip \
  --save-intermediate \
  --compare-detailed
```

**Solutions:**

1. **Check for unsupported features:**
```json
// Remove or simplify complex structures
{
  "boundedContexts": [
    {
      "name": "SimpleContext",
      "type": "FEATURE"
      // Remove complex aggregates temporarily
    }
  ]
}
```

2. **Use tolerance settings:**
```bash
cml-convert round-trip input.json --tolerance loose
```

## 🔧 Integration Issues

### Java Runtime Problems

#### Issue: Java not found

**Error:**
```
IntegrationError: Java runtime not available
```

**Solutions:**

1. **Install Java:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install openjdk-11-jdk

# macOS
brew install openjdk@11

# Windows
# Download from https://adoptium.net/
```

2. **Set JAVA_HOME:**
```bash
# Linux/macOS
export JAVA_HOME="/usr/lib/jvm/java-11-openjdk-amd64"
echo 'export JAVA_HOME="/usr/lib/jvm/java-11-openjdk-amd64"' >> ~/.bashrc

# Windows
setx JAVA_HOME "C:\Program Files\Eclipse Adoptium\jdk-11.0.x.x-hotspot"
```

3. **Verify installation:**
```bash
java -version
javac -version
echo $JAVA_HOME
```

#### Issue: Wrong Java version

**Error:**
```
IntegrationError: Java version 8 is not supported, requires Java 11+
```

**Solutions:**

1. **Check Java version:**
```bash
java -version
```

2. **Install correct version:**
```bash
# Ubuntu/Debian
sudo apt install openjdk-11-jdk

# Update alternatives
sudo update-alternatives --config java
```

3. **Use specific Java version:**
```bash
export JAVA_HOME="/usr/lib/jvm/java-11-openjdk-amd64"
export PATH="$JAVA_HOME/bin:$PATH"
```

### Context Mapper CLI Issues

#### Issue: CLI not found

**Error:**
```
IntegrationError: Context Mapper CLI not available
```

**Solutions:**

1. **Install CLI:**
```bash
# Download latest release
wget https://github.com/ContextMapper/context-mapper-cli/releases/latest/download/context-mapper-cli.jar

# Create executable script
sudo tee /usr/local/bin/context-mapper-cli << 'EOF'
#!/bin/bash
java -jar /usr/local/bin/context-mapper-cli.jar "$@"
EOF

sudo chmod +x /usr/local/bin/context-mapper-cli
```

2. **Test installation:**
```bash
context-mapper-cli --version
```

3. **Configure path:**
```bash
export CONTEXT_MAPPER_CLI_PATH="/usr/local/bin/context-mapper-cli"
```

#### Issue: CLI execution fails

**Error:**
```
IntegrationError: Context Mapper CLI execution failed
```

**Diagnosis:**
```bash
# Test CLI directly
context-mapper-cli --help

# Check Java classpath
java -cp /usr/local/bin/context-mapper-cli.jar --help

# Enable debug logging
cml-convert convert input.json output.cml \
  --use-context-mapper-cli \
  --debug \
  --log-file cli-debug.log
```

**Solutions:**

1. **Check CLI permissions:**
```bash
ls -la /usr/local/bin/context-mapper-cli
chmod +x /usr/local/bin/context-mapper-cli
```

2. **Update CLI:**
```bash
# Download latest version
wget https://github.com/ContextMapper/context-mapper-cli/releases/latest/download/context-mapper-cli.jar -O /usr/local/bin/context-mapper-cli.jar
```

3. **Use alternative path:**
```bash
cml-convert convert input.json output.cml \
  --context-mapper-cli-path "/path/to/context-mapper-cli"
```

## ⚡ Performance Problems

### Slow Conversion

#### Issue: Conversion takes too long

**Symptoms:**
- Conversion hangs or takes minutes for small files
- High CPU or memory usage

**Diagnosis:**
```bash
# Monitor resource usage
top -p $(pgrep -f cml-convert)

# Enable performance logging
cml-convert convert input.json output.cml \
  --debug \
  --log-file performance.log

# Check file size
ls -lh input.json
```

**Solutions:**

1. **Increase memory limit:**
```bash
cml-convert convert input.json output.cml --memory-limit 1024
```

2. **Disable expensive features:**
```bash
cml-convert convert input.json output.cml \
  --no-round-trip \
  --no-context-mapper-cli
```

3. **Use parallel processing:**
```bash
cml-convert convert input.json output.cml --parallel
```

4. **Simplify input:**
```json
// Temporarily remove complex structures
{
  "contextMap": {
    "name": "SimpleSystem",
    "type": "SYSTEM_LANDSCAPE",
    "contains": ["ServiceA"]
    // Remove complex relationships
  }
}
```

### Memory Issues

#### Issue: Out of memory errors

**Error:**
```
MemoryError: Unable to allocate memory for conversion
```

**Solutions:**

1. **Increase system memory:**
```bash
# Check available memory
free -h

# Increase swap space (Linux)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

2. **Optimize conversion:**
```bash
# Process in smaller chunks
cml-convert convert input.json output.cml \
  --memory-limit 512 \
  --chunk-size 100
```

3. **Use streaming mode:**
```python
from src.converter import ConverterEngine

converter = ConverterEngine()
# Process large files in streaming mode
with converter.stream_convert('large-input.json') as stream:
    for chunk in stream:
        process_chunk(chunk)
```

## 💻 CLI Issues

### Command Line Problems

#### Issue: Invalid command syntax

**Error:**
```
Usage: cml-convert [OPTIONS] COMMAND [ARGS]...
Error: No such option: --invalid-option
```

**Solutions:**

1. **Check available options:**
```bash
cml-convert --help
cml-convert convert --help
```

2. **Use correct syntax:**
```bash
# Correct
cml-convert convert input.json output.cml --enable-round-trip

# Incorrect
cml-convert --enable-round-trip convert input.json output.cml
```

#### Issue: File path problems

**Error:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'input.json'
```

**Solutions:**

1. **Check file existence:**
```bash
ls -la input.json
pwd
```

2. **Use absolute paths:**
```bash
cml-convert convert /full/path/to/input.json /full/path/to/output.cml
```

3. **Check permissions:**
```bash
ls -la input.json
chmod 644 input.json
```

### Output Issues

#### Issue: No output generated

**Problem:** Command completes but no output file is created.

**Diagnosis:**
```bash
# Check exit code
cml-convert convert input.json output.cml
echo "Exit code: $?"

# Enable verbose output
cml-convert convert input.json output.cml --verbose

# Check output directory permissions
ls -la $(dirname output.cml)
```

**Solutions:**

1. **Check output directory:**
```bash
mkdir -p $(dirname output.cml)
chmod 755 $(dirname output.cml)
```

2. **Use different output location:**
```bash
cml-convert convert input.json ./output.cml
```

3. **Check for validation errors:**
```bash
cml-convert validate input.json --detailed
```

## ⚙️ Configuration Problems

### Configuration File Issues

#### Issue: Configuration not loaded

**Problem:** Settings in `.cml-convert.json` are ignored.

**Diagnosis:**
```bash
# Check configuration file location
ls -la .cml-convert.json
ls -la ~/.cml-convert.json

# Validate JSON syntax
python -m json.tool .cml-convert.json
```

**Solutions:**

1. **Fix JSON syntax:**
```json
{
  "validation": {
    "enableRoundTrip": true,
    "useContextMapperCli": false
  }
}
```

2. **Check file location:**
```bash
# Project-specific config
touch .cml-convert.json

# User-specific config
touch ~/.cml-convert.json
```

3. **Use explicit config:**
```bash
cml-convert convert input.json output.cml --config custom-config.json
```

#### Issue: Invalid configuration values

**Error:**
```
ConfigurationError: Invalid value 'invalid' for validation.strictMode
```

**Solutions:**

1. **Check valid values:**
```json
{
  "validation": {
    "strictMode": true,  // boolean, not string
    "enableRoundTrip": false,
    "useContextMapperCli": true
  }
}
```

2. **Validate configuration:**
```python
from src.config import Config

try:
    config = Config.from_file('.cml-convert.json')
    print("Configuration valid")
except Exception as e:
    print(f"Configuration error: {e}")
```

## 📚 Error Reference

### Error Codes

| Code | Category | Description | Solution |
|------|----------|-------------|----------|
| E001 | Schema | Missing required property | Add required property |
| E002 | Schema | Invalid data type | Check data type |
| E003 | Schema | Invalid enum value | Use valid enum value |
| E004 | Schema | Pattern mismatch | Follow naming conventions |
| E005 | Semantic | Duplicate names | Use unique names |
| E006 | Semantic | Invalid relationship | Check relationship rules |
| E007 | Reference | Missing context | Define referenced context |
| E008 | Reference | Invalid reference | Check cross-references |
| E009 | Conversion | CML syntax error | Check generated CML |
| E010 | Integration | Java not found | Install Java runtime |
| E011 | Integration | CLI not available | Install Context Mapper CLI |
| E012 | Performance | Memory limit exceeded | Increase memory limit |
| E013 | File | File not found | Check file path |
| E014 | File | Permission denied | Check file permissions |
| E015 | Configuration | Invalid config | Fix configuration file |

### Common Error Patterns

#### Pattern: Missing Dependencies

**Errors:**
- `ModuleNotFoundError`
- `ImportError`
- `Command not found`

**General Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt
pip install -e .

# Check installation
pip check
```

#### Pattern: Permission Issues

**Errors:**
- `Permission denied`
- `Access denied`
- `Cannot write to directory`

**General Solution:**
```bash
# Fix permissions
chmod 755 directory/
chmod 644 file.json

# Check ownership
ls -la
chown $USER:$USER file.json
```

#### Pattern: Path Issues

**Errors:**
- `File not found`
- `No such file or directory`
- `Invalid path`

**General Solution:**
```bash
# Use absolute paths
realpath input.json

# Check current directory
pwd
ls -la

# Create missing directories
mkdir -p output/directory/
```

## 🆘 Getting Help

### Self-Help Resources

1. **Documentation:**
   - [JSON Schema Reference](json-schema-reference.md)
   - [CLI Reference](cli-reference.md)
   - [API Documentation](api-documentation.md)
   - [Validation Guide](validation-guide.md)
   - [Integration Guide](integration-guide.md)

2. **Examples:**
   - Check `examples/` directory
   - Review test files in `tests/`

3. **Logs and Debug Information:**
```bash
# Enable debug logging
cml-convert convert input.json output.cml \
  --debug \
  --log-file debug.log \
  --verbose

# Check system status
cml-convert integration-status --detailed
```

### Community Support

1. **GitHub Issues:**
   - Search existing issues
   - Create detailed bug reports
   - Include system information and logs

2. **Bug Report Template:**
```markdown
## Bug Report

### Environment
- OS: [e.g., Ubuntu 20.04]
- Python: [e.g., 3.9.7]
- Java: [e.g., OpenJDK 11.0.16]
- Package Version: [e.g., 1.0.0]

### Command
```bash
cml-convert convert input.json output.cml --enable-round-trip
```

### Expected Behavior
[Describe what should happen]

### Actual Behavior
[Describe what actually happens]

### Error Output
```
[Paste error messages here]
```

### Input File
```json
[Minimal example that reproduces the issue]
```

### Additional Context
[Any other relevant information]
```

3. **Feature Requests:**
   - Describe the use case
   - Explain the expected behavior
   - Provide examples if possible

### Professional Support

For enterprise users requiring professional support:

1. **Consulting Services:**
   - Architecture review
   - Custom implementation
   - Training and workshops

2. **Priority Support:**
   - Dedicated support channel
   - Faster response times
   - Custom feature development

3. **Contact Information:**
   - Email: support@context-mapper-converter.com
   - Documentation: [Professional Support Guide]

## 🔗 See Also

- [CLI Reference](cli-reference.md) - Command-line troubleshooting
- [API Documentation](api-documentation.md) - Python API troubleshooting
- [Validation Guide](validation-guide.md) - Validation error solutions
- [Integration Guide](integration-guide.md) - Integration troubleshooting
- [JSON Schema Reference](json-schema-reference.md) - Schema validation help