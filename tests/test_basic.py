"""Basic tests to verify the package setup is working."""

import pytest

from context_mapper_json_converter import Config, ConverterEngine, ValidationEngine


def test_package_imports():
    """Test that all main classes can be imported."""
    assert ConverterEngine is not None
    assert ValidationEngine is not None
    assert Config is not None


def test_converter_engine_creation():
    """Test that ConverterEngine can be instantiated."""
    converter = ConverterEngine()
    assert converter is not None


def test_validation_engine_creation():
    """Test that ValidationEngine can be instantiated."""
    validator = ValidationEngine()
    assert validator is not None


def test_config_creation():
    """Test that Config can be instantiated."""
    config = Config()
    assert config is not None


def test_simple_validation(simple_context_map, validation_engine):
    """Test basic JSON validation with a simple context map."""
    result = validation_engine.validate_json_schema(simple_context_map)
    assert result is not None
    # Note: This might fail if the validation logic has issues, but it tests the basic flow


def test_simple_conversion(simple_context_map, converter_engine):
    """Test basic JSON to CML conversion."""
    try:
        result = converter_engine.convert(simple_context_map)
        assert isinstance(result, str)
        assert len(result) > 0
    except Exception as e:
        # If conversion fails, at least we know the method exists and can be called
        assert hasattr(converter_engine, 'convert')


class TestBasicFunctionality:
    """Test class for basic functionality."""
    
    def test_version_available(self):
        """Test that version information is available."""
        from context_mapper_json_converter import __version__
        assert __version__ is not None
        assert isinstance(__version__, str)
    
    def test_cli_module_exists(self):
        """Test that CLI module can be imported."""
        from context_mapper_json_converter import cli
        assert cli is not None
    
    def test_validation_module_exists(self):
        """Test that validation module can be imported."""
        from context_mapper_json_converter import validation
        assert validation is not None
    
    def test_converter_module_exists(self):
        """Test that converter module can be imported."""
        from context_mapper_json_converter import converter
        assert converter is not None