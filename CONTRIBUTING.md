# Contributing to Context Mapper JSON Converter

We welcome contributions to the Context Mapper JSON Converter! This guide will help you get started with contributing to the project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Documentation](#documentation)
- [Code Style](#code-style)
- [Submitting Changes](#submitting-changes)
- [Release Process](#release-process)

## 🤝 Code of Conduct

This project adheres to a code of conduct that we expect all contributors to follow. Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) to help us maintain a welcoming and inclusive community.

### Our Standards

- **Be respectful**: Treat everyone with respect and kindness
- **Be inclusive**: Welcome newcomers and help them get started
- **Be collaborative**: Work together to solve problems and improve the project
- **Be constructive**: Provide helpful feedback and suggestions
- **Be patient**: Remember that everyone has different experience levels

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Java 11 or higher (for Context Mapper integration)
- Basic understanding of Domain-Driven Design (DDD) concepts

### Areas for Contribution

We welcome contributions in several areas:

1. **Core Features**
   - JSON schema enhancements
   - CML conversion improvements
   - New DDD pattern support

2. **Validation**
   - Additional validation rules
   - Better error messages
   - Performance improvements

3. **Integration**
   - Context Mapper ecosystem integration
   - CI/CD pipeline improvements
   - IDE plugin development

4. **Documentation**
   - User guides and tutorials
   - API documentation
   - Example improvements

5. **Testing**
   - Unit test coverage
   - Integration tests
   - Property-based testing

6. **Performance**
   - Optimization improvements
   - Memory usage reduction
   - Large file handling

## 💻 Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/context-mapper-json-converter.git
cd context-mapper-json-converter

# Add upstream remote
git remote add upstream https://github.com/ContextMapper/context-mapper-json-converter.git
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt
pip install -e .

# Install pre-commit hooks
pre-commit install
```

### 3. Verify Setup

```bash
# Run tests
pytest

# Check code style
black --check src/ tests/
flake8 src/ tests/

# Type checking
mypy src/

# Integration status
cml-convert integration-status
```

### 4. Development Dependencies

The `requirements-dev.txt` includes additional tools for development:

```txt
# Testing
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0
hypothesis>=6.70.0

# Code Quality
black>=23.0.0
flake8>=6.0.0
mypy>=1.0.0
isort>=5.12.0

# Documentation
sphinx>=6.0.0
sphinx-rtd-theme>=1.2.0
myst-parser>=1.0.0

# Development Tools
pre-commit>=3.0.0
tox>=4.0.0
```

## 📝 Contributing Guidelines

### Types of Contributions

#### Bug Reports

When reporting bugs, please include:

1. **Clear description** of the issue
2. **Steps to reproduce** the problem
3. **Expected vs actual behavior**
4. **Environment information** (OS, Python version, etc.)
5. **Minimal example** that demonstrates the issue
6. **Error messages** and stack traces

**Bug Report Template:**
```markdown
## Bug Description
[Clear description of the bug]

## Steps to Reproduce
1. [First step]
2. [Second step]
3. [Third step]

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## Environment
- OS: [e.g., Ubuntu 20.04]
- Python: [e.g., 3.9.7]
- Package Version: [e.g., 1.0.0]

## Minimal Example
```json
{
  "contextMap": {
    // Minimal JSON that reproduces the issue
  }
}
```

## Error Output
```
[Paste error messages here]
```
```

#### Feature Requests

When requesting features, please include:

1. **Use case description** - Why is this feature needed?
2. **Proposed solution** - How should it work?
3. **Alternative solutions** - What other approaches were considered?
4. **Examples** - Provide concrete examples if possible

#### Documentation Improvements

Documentation contributions are highly valued:

1. **Fix typos and errors**
2. **Improve clarity and examples**
3. **Add missing documentation**
4. **Translate documentation**

#### Code Contributions

Code contributions should:

1. **Solve a real problem** or implement a requested feature
2. **Include tests** for new functionality
3. **Follow code style** guidelines
4. **Include documentation** updates
5. **Be backward compatible** when possible

## 🔄 Development Workflow

### 1. Create a Branch

```bash
# Update your fork
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/issue-description
```

### 2. Make Changes

Follow these practices:

1. **Write tests first** (TDD approach recommended)
2. **Make small, focused commits**
3. **Write clear commit messages**
4. **Update documentation** as needed

### 3. Commit Guidelines

Use conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
git commit -m "feat(converter): add support for tactical DDD patterns"
git commit -m "fix(validation): handle empty context map gracefully"
git commit -m "docs(api): add examples for ConverterEngine class"
```

### 4. Keep Your Branch Updated

```bash
# Regularly sync with upstream
git fetch upstream
git rebase upstream/main

# Or merge if you prefer
git merge upstream/main
```

## 🧪 Testing

### Test Structure

```
tests/
├── unit/                   # Unit tests
│   ├── test_converter.py
│   ├── test_validation.py
│   └── test_cml_validator.py
├── integration/            # Integration tests
│   ├── test_cli.py
│   └── test_context_mapper.py
├── property/              # Property-based tests
│   └── test_properties.py
├── fixtures/              # Test data
│   ├── valid/
│   └── invalid/
└── conftest.py           # Pytest configuration
```

### Running Tests

```bash
# Run all tests (coverage collected but not enforced)
pytest

# Run all tests with coverage enforcement (recommended before committing)
pytest --cov-fail-under=85

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test file (coverage not enforced for individual files)
pytest tests/unit/test_converter.py

# Run specific test
pytest tests/unit/test_converter.py::test_convert_context_map

# Run tests matching pattern
pytest -k "test_validation"

# Run property-based tests
pytest tests/property/

# Run integration tests (requires Context Mapper CLI)
pytest tests/integration/ --integration
```

**Note on Coverage:** Coverage is always collected, but the 85% threshold is only enforced when you explicitly add `--cov-fail-under=85`. This allows you to run individual test files or specific tests during development without failing due to incomplete coverage. The CI pipeline enforces coverage thresholds automatically.

### Writing Tests

#### Unit Tests

```python
import pytest
from src.converter import ConverterEngine
from src.validation import ValidationEngine

class TestConverterEngine:
    def setup_method(self):
        self.converter = ConverterEngine()
    
    def test_convert_simple_context_map(self):
        # Arrange
        json_data = {
            "contextMap": {
                "name": "TestSystem",
                "type": "SYSTEM_LANDSCAPE",
                "contains": ["ServiceA"]
            },
            "boundedContexts": [
                {"name": "ServiceA", "type": "FEATURE"}
            ]
        }
        
        # Act
        result = self.converter.convert(json_data)
        
        # Assert
        assert "ContextMap TestSystem" in result
        assert "BoundedContext ServiceA" in result
    
    def test_convert_invalid_json_raises_error(self):
        # Arrange
        invalid_json = {"invalid": "data"}
        
        # Act & Assert
        with pytest.raises(ValidationError):
            self.converter.convert(invalid_json)
```

#### Property-Based Tests

```python
from hypothesis import given, strategies as st
from src.converter import ConverterEngine

class TestConverterProperties:
    @given(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))))
    def test_context_name_roundtrip(self, context_name):
        """Property: Context names should survive round-trip conversion"""
        # Assume valid context name
        assume(context_name[0].isalpha())
        
        json_data = {
            "contextMap": {
                "name": context_name,
                "type": "SYSTEM_LANDSCAPE",
                "contains": ["TestContext"]
            },
            "boundedContexts": [
                {"name": "TestContext", "type": "FEATURE"}
            ]
        }
        
        converter = ConverterEngine()
        cml_output = converter.convert(json_data)
        
        # Property: Generated CML should contain the context name
        assert context_name in cml_output
```

#### Integration Tests

```python
import subprocess
import tempfile
import json

class TestCLIIntegration:
    def test_cli_convert_command(self):
        """Test CLI convert command end-to-end"""
        json_data = {
            "contextMap": {
                "name": "CLITest",
                "type": "SYSTEM_LANDSCAPE",
                "contains": ["TestService"]
            },
            "boundedContexts": [
                {"name": "TestService", "type": "FEATURE"}
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as json_file:
            json.dump(json_data, json_file)
            json_file.flush()
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.cml', delete=False) as cml_file:
                # Run CLI command
                result = subprocess.run([
                    'cml-convert', 'convert', 
                    json_file.name, cml_file.name
                ], capture_output=True, text=True)
                
                assert result.returncode == 0
                
                # Check output file
                with open(cml_file.name, 'r') as f:
                    cml_content = f.read()
                    assert "ContextMap CLITest" in cml_content
```

### Test Data Management

Create reusable test fixtures:

```python
# tests/conftest.py
import pytest
import json
from pathlib import Path

@pytest.fixture
def valid_context_map():
    return {
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

@pytest.fixture
def test_data_dir():
    return Path(__file__).parent / "fixtures"

@pytest.fixture
def load_test_json():
    def _load(filename):
        test_dir = Path(__file__).parent / "fixtures"
        with open(test_dir / filename) as f:
            return json.load(f)
    return _load
```

## 📚 Documentation

### Documentation Structure

```
docs/
├── README.md                    # Main documentation
├── json-schema-reference.md     # Schema documentation
├── cli-reference.md            # CLI documentation
├── api-documentation.md        # Python API docs
├── validation-guide.md         # Validation guide
├── integration-guide.md        # Integration guide
├── troubleshooting.md          # Troubleshooting
└── examples/                   # Example files
```

### Writing Documentation

#### Guidelines

1. **Use clear, simple language**
2. **Provide concrete examples**
3. **Include code snippets**
4. **Add cross-references**
5. **Keep it up-to-date**

#### Documentation Standards

```markdown
# Title (H1 - only one per document)

Brief description of what this document covers.

## 📋 Table of Contents (H2)

- [Section 1](#section-1)
- [Section 2](#section-2)

## 🎯 Section 1 (H2)

Content with emoji icons for visual appeal.

### Subsection (H3)

More detailed content.

#### Code Examples (H4)

```python
# Always include complete, runnable examples
from src.converter import ConverterEngine

converter = ConverterEngine()
result = converter.convert(json_data)
```

#### Command Examples

```bash
# Show complete commands with expected output
cml-convert convert input.json output.cml
# Expected output: Conversion completed successfully
```
```

#### API Documentation

Use docstrings for all public APIs:

```python
def convert(self, json_data: Dict[str, Any]) -> str:
    """Convert JSON definition to CML code.
    
    Args:
        json_data: Complete JSON definition containing contextMap,
                  boundedContexts, and optionally subdomains.
    
    Returns:
        Generated CML code as a string.
    
    Raises:
        ValidationError: If JSON validation fails.
        ConversionError: If CML generation fails.
    
    Example:
        >>> converter = ConverterEngine()
        >>> json_data = {
        ...     "contextMap": {
        ...         "name": "ECommerceSystem",
        ...         "type": "SYSTEM_LANDSCAPE",
        ...         "contains": ["OrderService"]
        ...     },
        ...     "boundedContexts": [
        ...         {"name": "OrderService", "type": "FEATURE"}
        ...     ]
        ... }
        >>> cml_output = converter.convert(json_data)
        >>> print(cml_output)
        ContextMap ECommerceSystem type = SYSTEM_LANDSCAPE {
          contains OrderService
        }
        
        BoundedContext OrderService type = FEATURE {
        }
    """
```

### Building Documentation

```bash
# Install documentation dependencies
pip install -r requirements-docs.txt

# Build Sphinx documentation
cd docs/
make html

# Serve documentation locally
python -m http.server 8000 -d _build/html/
```

## 🎨 Code Style

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:

#### Formatting

```python
# Use Black for automatic formatting
black src/ tests/

# Configuration in pyproject.toml
[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'
```

#### Import Organization

```python
# Use isort for import sorting
isort src/ tests/

# Standard library imports
import json
import os
from pathlib import Path
from typing import Dict, List, Optional

# Third-party imports
import click
import jsonschema
from pydantic import BaseModel

# Local imports
from src.config import Config
from src.validation import ValidationEngine
```

#### Naming Conventions

```python
# Classes: PascalCase
class ConverterEngine:
    pass

# Functions and variables: snake_case
def convert_context_map(context_map_data):
    validation_result = validate_input(context_map_data)
    return validation_result

# Constants: UPPER_SNAKE_CASE
DEFAULT_TIMEOUT = 300
MAX_RETRY_ATTEMPTS = 3

# Private methods: _leading_underscore
def _internal_helper_method(self):
    pass
```

#### Type Hints

```python
from typing import Dict, List, Optional, Union, Any

def convert(self, json_data: Dict[str, Any]) -> str:
    """Always use type hints for public APIs."""
    pass

def validate_references(
    self, 
    json_data: Dict[str, Any]
) -> ValidationResult:
    """Use type hints for complex return types."""
    pass

# Use Union for multiple types
def process_input(data: Union[str, Dict[str, Any]]) -> bool:
    pass

# Use Optional for nullable values
def get_config(config_path: Optional[str] = None) -> Config:
    pass
```

### Code Quality Tools

#### Linting

```bash
# Flake8 for linting
flake8 src/ tests/

# Configuration in setup.cfg
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = .git,__pycache__,build,dist
```

#### Type Checking

```bash
# MyPy for type checking
mypy src/

# Configuration in mypy.ini
[mypy]
python_version = 3.8
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
```

#### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3.8

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

## 📤 Submitting Changes

### Pull Request Process

#### 1. Prepare Your Changes

```bash
# Ensure your branch is up-to-date
git fetch upstream
git rebase upstream/main

# Run all checks
pytest
black --check src/ tests/
flake8 src/ tests/
mypy src/

# Update documentation if needed
```

#### 2. Create Pull Request

**Pull Request Template:**
```markdown
## Description
[Brief description of changes]

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Related Issues
Fixes #[issue number]

## Changes Made
- [List of changes]
- [Another change]

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass (if applicable)
- [ ] Property-based tests pass
- [ ] Manual testing completed

## Documentation
- [ ] Code comments updated
- [ ] API documentation updated
- [ ] User documentation updated
- [ ] Examples updated (if applicable)

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Tests added for new functionality
- [ ] All tests pass
- [ ] Documentation updated
- [ ] No breaking changes (or breaking changes documented)
```

#### 3. Review Process

1. **Automated Checks**: CI/CD pipeline runs automatically
2. **Code Review**: Maintainers review your changes
3. **Feedback**: Address any requested changes
4. **Approval**: Once approved, changes will be merged

### Review Guidelines

#### For Contributors

- **Respond promptly** to review feedback
- **Ask questions** if feedback is unclear
- **Make requested changes** in separate commits
- **Test thoroughly** after making changes

#### For Reviewers

- **Be constructive** and helpful
- **Explain reasoning** behind suggestions
- **Approve quickly** when changes look good
- **Test locally** for complex changes

## 🚀 Release Process

### Versioning

We use [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Workflow

#### 1. Prepare Release

```bash
# Create release branch
git checkout -b release/v1.2.0

# Update version numbers
# Update CHANGELOG.md
# Update documentation
```

#### 2. Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version numbers updated
- [ ] Integration tests with Context Mapper CLI
- [ ] Performance benchmarks run
- [ ] Security scan completed

#### 3. Create Release

```bash
# Tag release
git tag -a v1.2.0 -m "Release version 1.2.0"

# Push tag
git push upstream v1.2.0

# Create GitHub release with release notes
```

### Changelog Format

```markdown
# Changelog

## [1.2.0] - 2024-01-15

### Added
- New tactical DDD pattern support
- Round-trip validation improvements
- CLI batch processing mode

### Changed
- Improved error messages for validation failures
- Updated Context Mapper CLI integration

### Fixed
- Memory leak in large file processing
- CML syntax generation edge cases

### Deprecated
- Old configuration format (will be removed in v2.0.0)

### Security
- Updated dependencies to address security vulnerabilities
```

## 🏆 Recognition

### Contributors

We recognize contributors in several ways:

1. **Contributors file**: Listed in CONTRIBUTORS.md
2. **Release notes**: Mentioned in release announcements
3. **Documentation**: Author attribution in documentation
4. **Special recognition**: Outstanding contributions highlighted

### Contribution Types

We value all types of contributions:

- **Code**: New features, bug fixes, performance improvements
- **Documentation**: Writing, editing, translating
- **Testing**: Writing tests, reporting bugs, testing releases
- **Design**: UI/UX improvements, documentation design
- **Community**: Helping users, moderating discussions
- **Infrastructure**: CI/CD improvements, tooling

## 📞 Getting Help

### Communication Channels

1. **GitHub Discussions**: General questions and discussions
2. **GitHub Issues**: Bug reports and feature requests
3. **Email**: maintainers@context-mapper-converter.com
4. **Documentation**: Comprehensive guides and references

### Mentorship

New contributors can get help from experienced maintainers:

1. **Good First Issues**: Labeled issues suitable for beginners
2. **Mentorship Program**: Pairing with experienced contributors
3. **Office Hours**: Regular sessions for questions and help

### Resources

- [Python Development Guide](https://devguide.python.org/)
- [Domain-Driven Design Resources](https://domainlanguage.com/ddd/)
- [Context Mapper Documentation](https://contextmapper.org/docs/)
- [Git Workflow Guide](https://www.atlassian.com/git/tutorials/comparing-workflows)

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

Thank you for contributing to the Context Mapper JSON Converter! Your contributions help make Domain-Driven Design more accessible to developers worldwide. 🎉