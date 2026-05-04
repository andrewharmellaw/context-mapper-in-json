"""Pytest configuration and fixtures for Context Mapper JSON Converter tests."""

import json
import tempfile
from pathlib import Path
from typing import Dict, Any

import pytest

from context_mapper_json_converter.config import Config
from context_mapper_json_converter.converter import ConverterEngine
from context_mapper_json_converter.validation import ValidationEngine


@pytest.fixture
def simple_context_map() -> Dict[str, Any]:
    """Simple context map for basic testing."""
    return {
        "contextMap": {
            "name": "TestSystem",
            "type": "SYSTEM_LANDSCAPE",
            "contains": ["ServiceA", "ServiceB"],
        },
        "boundedContexts": [
            {"name": "ServiceA", "type": "FEATURE"},
            {"name": "ServiceB", "type": "SYSTEM"},
        ],
    }


@pytest.fixture
def complex_context_map() -> Dict[str, Any]:
    """Complex context map with relationships for advanced testing."""
    return {
        "contextMap": {
            "name": "ECommerceSystem",
            "type": "SYSTEM_LANDSCAPE",
            "contains": ["OrderManagement", "PaymentService", "InventoryService"],
            "relationships": [
                {
                    "type": "CustomerSupplier",
                    "upstream": "PaymentService",
                    "downstream": "OrderManagement",
                    "upstreamRoles": ["OHS", "PL"],
                    "downstreamRoles": ["ACL"],
                    "implementationTechnology": "REST API",
                },
                {
                    "type": "Partnership",
                    "upstream": "OrderManagement",
                    "downstream": "InventoryService",
                },
            ],
        },
        "boundedContexts": [
            {
                "name": "OrderManagement",
                "type": "FEATURE",
                "domainVisionStatement": "Manages customer orders and order lifecycle",
                "implementationTechnology": "Java Spring Boot",
            },
            {
                "name": "PaymentService",
                "type": "SYSTEM",
                "domainVisionStatement": "Handles payment processing and transactions",
            },
            {
                "name": "InventoryService",
                "type": "FEATURE",
                "domainVisionStatement": "Manages product inventory and stock levels",
            },
        ],
    }


@pytest.fixture
def tactical_patterns_example() -> Dict[str, Any]:
    """Example with tactical DDD patterns."""
    return {
        "contextMap": {
            "name": "OrderSystem",
            "type": "SYSTEM_LANDSCAPE",
            "contains": ["OrderManagement"],
        },
        "boundedContexts": [
            {
                "name": "OrderManagement",
                "type": "FEATURE",
                "aggregates": [
                    {
                        "name": "Order",
                        "entities": [
                            {
                                "name": "Order",
                                "aggregateRoot": True,
                                "attributes": [
                                    {"name": "orderId", "type": "OrderId", "key": True},
                                    {"name": "customerId", "type": "CustomerId"},
                                    {"name": "status", "type": "OrderStatus"},
                                ],
                            }
                        ],
                        "valueObjects": [
                            {
                                "name": "OrderId",
                                "attributes": [{"name": "value", "type": "String"}],
                            }
                        ],
                    }
                ],
            }
        ],
    }


@pytest.fixture
def invalid_json_missing_required() -> Dict[str, Any]:
    """Invalid JSON missing required properties."""
    return {
        "contextMap": {
            "name": "InvalidSystem"
            # Missing "type" and "contains"
        }
    }


@pytest.fixture
def invalid_json_duplicate_names() -> Dict[str, Any]:
    """Invalid JSON with duplicate context names."""
    return {
        "contextMap": {
            "name": "DuplicateSystem",
            "type": "SYSTEM_LANDSCAPE",
            "contains": ["ServiceA", "ServiceA"],  # Duplicate
        },
        "boundedContexts": [
            {"name": "ServiceA", "type": "FEATURE"},
            {"name": "ServiceA", "type": "SYSTEM"},  # Duplicate name
        ],
    }


@pytest.fixture
def invalid_json_missing_references() -> Dict[str, Any]:
    """Invalid JSON with missing context references."""
    return {
        "contextMap": {
            "name": "MissingRefSystem",
            "type": "SYSTEM_LANDSCAPE",
            "contains": ["ServiceA", "ServiceB"],  # ServiceB not defined
        },
        "boundedContexts": [
            {"name": "ServiceA", "type": "FEATURE"}
            # ServiceB missing
        ],
    }


@pytest.fixture
def converter_engine() -> ConverterEngine:
    """Converter engine instance for testing."""
    return ConverterEngine()


@pytest.fixture
def validation_engine() -> ValidationEngine:
    """Validation engine instance for testing."""
    return ValidationEngine()


@pytest.fixture
def test_config() -> Config:
    """Test configuration."""
    return Config(
        enable_pretty_formatting=True,
        validate_cml_output=True,
        enable_round_trip_validation=False,
        use_context_mapper_cli=False,
    )


@pytest.fixture
def temp_json_file():
    """Create a temporary JSON file for testing."""

    def _create_temp_file(data: Dict[str, Any]) -> str:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f, indent=2)
            return f.name

    return _create_temp_file


@pytest.fixture
def temp_cml_file():
    """Create a temporary CML file for testing."""

    def _create_temp_file(content: str = "") -> str:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".cml", delete=False) as f:
            f.write(content)
            return f.name

    return _create_temp_file


@pytest.fixture
def test_data_dir() -> Path:
    """Path to test data directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def load_test_json():
    """Load JSON test data from fixtures."""

    def _load(filename: str) -> Dict[str, Any]:
        test_dir = Path(__file__).parent / "fixtures" / "valid"
        with open(test_dir / filename) as f:
            return json.load(f)

    return _load


@pytest.fixture
def load_invalid_json():
    """Load invalid JSON test data from fixtures."""

    def _load(filename: str) -> Dict[str, Any]:
        test_dir = Path(__file__).parent / "fixtures" / "invalid"
        with open(test_dir / filename) as f:
            return json.load(f)

    return _load


@pytest.fixture
def load_expected_cml():
    """Load expected CML output from fixtures."""

    def _load(filename: str) -> str:
        test_dir = Path(__file__).parent / "fixtures" / "expected"
        with open(test_dir / filename) as f:
            return f.read()

    return _load


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "performance: mark test as a performance test")
    config.addinivalue_line("markers", "slow: mark test as slow running")


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="run integration tests",
    )
    parser.addoption(
        "--performance",
        action="store_true",
        default=False,
        help="run performance tests",
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on command line options."""
    if config.getoption("--integration"):
        # Don't skip integration tests
        return

    if config.getoption("--performance"):
        # Don't skip performance tests
        return

    # Skip integration and performance tests by default
    skip_integration = pytest.mark.skip(reason="need --integration option to run")
    skip_performance = pytest.mark.skip(reason="need --performance option to run")

    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)
        if "performance" in item.keywords:
            item.add_marker(skip_performance)
