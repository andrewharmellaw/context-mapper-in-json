"""
Round-trip validation integration tests.

Tests the complete JSON → CML → JSON round-trip process, including
consistency checking, discrepancy detection, and performance characteristics.
"""

import json
import time
from pathlib import Path
from typing import Any, Dict

import pytest

from context_mapper_json_converter.converter import ConverterEngine
from context_mapper_json_converter.round_trip_validator import (
    CMLParser,
    Discrepancy,
    RoundTripValidator,
)
from context_mapper_json_converter.validation import ValidationResult

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
VALID_DIR = FIXTURES_DIR / "valid"


def load_json(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def convert_to_cml(json_data: dict) -> str:
    converter = ConverterEngine()
    return converter.convert(json_data)


# ---------------------------------------------------------------------------
# CMLParser tests
# ---------------------------------------------------------------------------


class TestCMLParser:
    """Test the CMLParser class that parses CML back to JSON-like structure."""

    def setup_method(self):
        self.parser = CMLParser()

    def test_parser_initialises_without_error(self):
        """CMLParser can be instantiated."""
        assert self.parser is not None

    def test_parse_simple_context_map(self):
        """Parser extracts ContextMap from simple CML."""
        cml = (
            "ContextMap SimpleSystem type = SYSTEM_LANDSCAPE {\n"
            "  contains ServiceA, ServiceB\n"
            "}\n"
            "BoundedContext ServiceA type = FEATURE {}\n"
            "BoundedContext ServiceB type = SYSTEM {}\n"
        )
        result = self.parser.parse_cml(cml)
        assert "contextMap" in result
        assert result["contextMap"]["type"] == "SYSTEM_LANDSCAPE"

    def test_parse_context_map_name(self):
        """Parser extracts ContextMap name."""
        cml = (
            "ContextMap MySystem type = SYSTEM_LANDSCAPE {\n"
            "  contains ServiceA\n"
            "}\n"
            "BoundedContext ServiceA type = FEATURE {}\n"
        )
        result = self.parser.parse_cml(cml)
        assert result["contextMap"].get("name") == "MySystem"

    def test_parse_context_map_contains(self):
        """Parser extracts contains list from ContextMap."""
        cml = (
            "ContextMap Test type = SYSTEM_LANDSCAPE {\n"
            "  contains ServiceA, ServiceB\n"
            "}\n"
            "BoundedContext ServiceA type = FEATURE {}\n"
            "BoundedContext ServiceB type = SYSTEM {}\n"
        )
        result = self.parser.parse_cml(cml)
        contains = result["contextMap"].get("contains", [])
        assert "ServiceA" in contains
        assert "ServiceB" in contains

    def test_parse_bounded_contexts(self):
        """Parser extracts BoundedContext definitions."""
        cml = (
            "ContextMap Test type = SYSTEM_LANDSCAPE {\n"
            "  contains ServiceA\n"
            "}\n"
            "BoundedContext ServiceA type = FEATURE {\n"
            "}\n"
        )
        result = self.parser.parse_cml(cml)
        assert "boundedContexts" in result
        assert len(result["boundedContexts"]) == 1
        assert result["boundedContexts"][0]["name"] == "ServiceA"

    def test_parse_bounded_context_type(self):
        """Parser extracts BoundedContext type."""
        cml = (
            "ContextMap Test type = SYSTEM_LANDSCAPE {\n"
            "  contains ServiceA\n"
            "}\n"
            "BoundedContext ServiceA type = FEATURE {\n"
            "}\n"
        )
        result = self.parser.parse_cml(cml)
        assert result["boundedContexts"][0]["type"] == "FEATURE"

    def test_parse_multiple_bounded_contexts(self):
        """Parser extracts multiple BoundedContexts."""
        cml = (
            "ContextMap Test type = SYSTEM_LANDSCAPE {\n"
            "  contains ServiceA, ServiceB, ServiceC\n"
            "}\n"
            "BoundedContext ServiceA type = FEATURE {\n"
            "}\n"
            "BoundedContext ServiceB type = SYSTEM {\n"
            "}\n"
            "BoundedContext ServiceC type = APPLICATION {\n"
            "}\n"
        )
        result = self.parser.parse_cml(cml)
        assert len(result["boundedContexts"]) == 3

    def test_parse_partnership_relationship(self):
        """Parser extracts Partnership relationships."""
        cml = (
            "ContextMap Test type = SYSTEM_LANDSCAPE {\n"
            "  contains ServiceA, ServiceB\n"
            "  ServiceA Partnership ServiceB\n"
            "}\n"
            "BoundedContext ServiceA type = FEATURE {}\n"
            "BoundedContext ServiceB type = SYSTEM {}\n"
        )
        result = self.parser.parse_cml(cml)
        relationships = result["contextMap"].get("relationships", [])
        assert len(relationships) >= 1
        partnership = next(
            (r for r in relationships if r.get("type") == "Partnership"), None
        )
        assert partnership is not None

    def test_parse_shared_kernel_relationship(self):
        """Parser extracts SharedKernel relationships."""
        cml = (
            "ContextMap Test type = SYSTEM_LANDSCAPE {\n"
            "  contains ServiceA, ServiceB\n"
            "  ServiceA [SK] <-> [SK] ServiceB\n"
            "}\n"
            "BoundedContext ServiceA type = FEATURE {}\n"
            "BoundedContext ServiceB type = SYSTEM {}\n"
        )
        result = self.parser.parse_cml(cml)
        relationships = result["contextMap"].get("relationships", [])
        sk = next((r for r in relationships if r.get("type") == "SharedKernel"), None)
        assert sk is not None

    def test_parse_empty_cml_returns_empty_dict(self):
        """Parsing empty CML returns an empty or minimal dict."""
        result = self.parser.parse_cml("")
        assert isinstance(result, dict)

    def test_parse_cml_from_real_fixture(self):
        """Parser can parse CML generated from a real fixture."""
        json_data = load_json(VALID_DIR / "simple-context-map.json")
        cml_output = convert_to_cml(json_data)
        result = self.parser.parse_cml(cml_output)
        assert isinstance(result, dict)
        assert "contextMap" in result or "boundedContexts" in result


# ---------------------------------------------------------------------------
# RoundTripValidator – validate_round_trip
# ---------------------------------------------------------------------------


class TestRoundTripValidation:
    """Test the RoundTripValidator.validate_round_trip method."""

    def setup_method(self):
        self.validator = RoundTripValidator()

    def test_validator_initialises_without_error(self):
        """RoundTripValidator can be instantiated."""
        assert self.validator is not None

    def test_validate_round_trip_returns_validation_result(self):
        """validate_round_trip returns a ValidationResult."""
        json_data = load_json(VALID_DIR / "simple-context-map.json")
        cml_output = convert_to_cml(json_data)
        result = self.validator.validate_round_trip(json_data, cml_output)
        assert isinstance(result, ValidationResult)

    def test_simple_context_map_round_trip_passes(self):
        """Simple context map passes round-trip validation."""
        json_data = load_json(VALID_DIR / "simple-context-map.json")
        cml_output = convert_to_cml(json_data)
        result = self.validator.validate_round_trip(json_data, cml_output)
        assert result.is_valid, f"Round-trip failed: {result.errors}"

    def test_customer_supplier_round_trip(self):
        """Customer-supplier fixture round-trip validation."""
        json_data = load_json(VALID_DIR / "customer-supplier.json")
        cml_output = convert_to_cml(json_data)
        result = self.validator.validate_round_trip(json_data, cml_output)
        assert isinstance(result, ValidationResult)

    def test_partnership_round_trip(self):
        """Partnership fixture round-trip validation."""
        json_data = load_json(VALID_DIR / "partnership.json")
        cml_output = convert_to_cml(json_data)
        result = self.validator.validate_round_trip(json_data, cml_output)
        assert isinstance(result, ValidationResult)

    def test_aggregates_entities_round_trip(self):
        """Aggregates and entities fixture round-trip validation."""
        json_data = load_json(VALID_DIR / "aggregates-entities.json")
        cml_output = convert_to_cml(json_data)
        result = self.validator.validate_round_trip(json_data, cml_output)
        assert isinstance(result, ValidationResult)

    def test_all_valid_fixtures_round_trip(self):
        """All valid fixtures complete round-trip validation without crashing."""
        for json_file in VALID_DIR.glob("*.json"):
            json_data = load_json(json_file)
            cml_output = convert_to_cml(json_data)
            result = self.validator.validate_round_trip(json_data, cml_output)
            assert isinstance(
                result, ValidationResult
            ), f"Round-trip failed for {json_file.name}"

    def test_round_trip_with_empty_cml_produces_errors(self):
        """Round-trip with empty CML produces validation errors."""
        json_data = load_json(VALID_DIR / "simple-context-map.json")
        result = self.validator.validate_round_trip(json_data, "")
        # Empty CML should produce errors or warnings
        assert not result.is_valid or len(result.warnings) > 0

    def test_round_trip_context_map_name_preserved(self):
        """Context Map name is preserved through round-trip."""
        json_data = load_json(VALID_DIR / "simple-context-map.json")
        cml_output = convert_to_cml(json_data)
        original_name = json_data["contextMap"]["name"]
        assert original_name in cml_output

    def test_round_trip_bounded_context_names_preserved(self):
        """Bounded Context names are preserved through round-trip."""
        json_data = load_json(VALID_DIR / "simple-context-map.json")
        cml_output = convert_to_cml(json_data)
        for bc in json_data["boundedContexts"]:
            assert bc["name"] in cml_output


# ---------------------------------------------------------------------------
# RoundTripValidator – compare_semantic_equivalence
# ---------------------------------------------------------------------------


class TestCompareSemanticEquivalence:
    """Test the compare_semantic_equivalence method."""

    def setup_method(self):
        self.validator = RoundTripValidator()

    def test_identical_structures_have_no_discrepancies(self):
        """Identical structures produce no discrepancies."""
        data = {
            "contextMap": {
                "name": "Test",
                "type": "SYSTEM_LANDSCAPE",
                "contains": ["ServiceA"],
            },
            "boundedContexts": [{"name": "ServiceA", "type": "FEATURE"}],
        }
        discrepancies = self.validator.compare_semantic_equivalence(data, data)
        assert len(discrepancies) == 0

    def test_missing_context_map_detected(self):
        """Missing contextMap in parsed data is detected as discrepancy."""
        original = {
            "contextMap": {
                "name": "Test",
                "type": "SYSTEM_LANDSCAPE",
                "contains": ["ServiceA"],
            },
            "boundedContexts": [{"name": "ServiceA", "type": "FEATURE"}],
        }
        parsed = {"boundedContexts": [{"name": "ServiceA", "type": "FEATURE"}]}
        discrepancies = self.validator.compare_semantic_equivalence(original, parsed)
        assert any(d.property_path == "contextMap" for d in discrepancies)

    def test_missing_bounded_contexts_detected(self):
        """Missing boundedContexts in parsed data is detected."""
        original = {
            "contextMap": {
                "name": "Test",
                "type": "SYSTEM_LANDSCAPE",
                "contains": ["ServiceA"],
            },
            "boundedContexts": [{"name": "ServiceA", "type": "FEATURE"}],
        }
        parsed = {
            "contextMap": {
                "name": "Test",
                "type": "SYSTEM_LANDSCAPE",
                "contains": ["ServiceA"],
            }
        }
        discrepancies = self.validator.compare_semantic_equivalence(original, parsed)
        assert any("boundedContexts" in d.property_path for d in discrepancies)

    def test_context_map_type_mismatch_detected(self):
        """Context Map type mismatch is detected."""
        original = {
            "contextMap": {
                "name": "Test",
                "type": "SYSTEM_LANDSCAPE",
                "contains": ["ServiceA"],
            },
            "boundedContexts": [{"name": "ServiceA", "type": "FEATURE"}],
        }
        parsed = {
            "contextMap": {
                "name": "Test",
                "type": "ORGANIZATIONAL",
                "contains": ["ServiceA"],
            },
            "boundedContexts": [{"name": "ServiceA", "type": "FEATURE"}],
        }
        discrepancies = self.validator.compare_semantic_equivalence(original, parsed)
        assert any("type" in d.property_path for d in discrepancies)

    def test_discrepancy_objects_have_required_fields(self):
        """Discrepancy objects have all required fields."""
        original = {
            "contextMap": {
                "name": "Test",
                "type": "SYSTEM_LANDSCAPE",
                "contains": ["ServiceA"],
            },
            "boundedContexts": [{"name": "ServiceA", "type": "FEATURE"}],
        }
        parsed = {"boundedContexts": [{"name": "ServiceA", "type": "FEATURE"}]}
        discrepancies = self.validator.compare_semantic_equivalence(original, parsed)
        for d in discrepancies:
            assert isinstance(d, Discrepancy)
            assert d.property_path is not None
            assert d.discrepancy_type is not None
            assert d.description is not None

    def test_returns_list_of_discrepancies(self):
        """compare_semantic_equivalence returns a list."""
        result = self.validator.compare_semantic_equivalence({}, {})
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# RoundTripValidator – identify_discrepancies
# ---------------------------------------------------------------------------


class TestIdentifyDiscrepancies:
    """Test the identify_discrepancies method."""

    def setup_method(self):
        self.validator = RoundTripValidator()

    def test_identify_discrepancies_returns_list(self):
        """identify_discrepancies returns a list."""
        result = self.validator.identify_discrepancies({}, {})
        assert isinstance(result, list)

    def test_identify_discrepancies_same_as_compare_semantic(self):
        """identify_discrepancies produces same result as compare_semantic_equivalence."""
        original = {
            "contextMap": {
                "name": "Test",
                "type": "SYSTEM_LANDSCAPE",
                "contains": ["ServiceA"],
            },
            "boundedContexts": [{"name": "ServiceA", "type": "FEATURE"}],
        }
        parsed = {"boundedContexts": [{"name": "ServiceA", "type": "FEATURE"}]}
        d1 = self.validator.identify_discrepancies(original, parsed)
        d2 = self.validator.compare_semantic_equivalence(original, parsed)
        assert len(d1) == len(d2)

    def test_no_discrepancies_for_matching_data(self):
        """No discrepancies when data matches."""
        data = {
            "contextMap": {
                "name": "Test",
                "type": "SYSTEM_LANDSCAPE",
                "contains": ["ServiceA"],
            },
            "boundedContexts": [{"name": "ServiceA", "type": "FEATURE"}],
        }
        discrepancies = self.validator.identify_discrepancies(data, data)
        assert len(discrepancies) == 0


# ---------------------------------------------------------------------------
# RoundTripValidator – validate_with_context_mapper
# ---------------------------------------------------------------------------


class TestValidateWithContextMapper:
    """Test the validate_with_context_mapper method."""

    def setup_method(self):
        self.validator = RoundTripValidator()

    def test_validate_with_context_mapper_returns_validation_result(self):
        """validate_with_context_mapper returns a ValidationResult."""
        cml = "ContextMap Test type = SYSTEM_LANDSCAPE {\n  contains ServiceA\n}\nBoundedContext ServiceA type = FEATURE {}"
        result = self.validator.validate_with_context_mapper(cml)
        assert isinstance(result, ValidationResult)

    def test_valid_cml_passes_basic_validation(self):
        """Valid CML passes basic Context Mapper validation."""
        json_data = load_json(VALID_DIR / "simple-context-map.json")
        cml_output = convert_to_cml(json_data)
        result = self.validator.validate_with_context_mapper(cml_output)
        assert result.is_valid

    def test_cml_without_required_elements_fails(self):
        """CML without ContextMap or BoundedContext fails validation."""
        result = self.validator.validate_with_context_mapper("just some text")
        assert not result.is_valid

    def test_cml_with_unbalanced_braces_fails(self):
        """CML with unbalanced braces fails validation."""
        cml = "ContextMap Test type = SYSTEM_LANDSCAPE {\n  contains ServiceA\n"  # missing closing brace
        result = self.validator.validate_with_context_mapper(cml)
        assert not result.is_valid

    def test_validation_adds_integration_warning(self):
        """Validation adds a warning about CLI integration not being available."""
        json_data = load_json(VALID_DIR / "simple-context-map.json")
        cml_output = convert_to_cml(json_data)
        result = self.validator.validate_with_context_mapper(cml_output)
        # Should have a warning about CLI integration
        assert len(result.warnings) > 0


# ---------------------------------------------------------------------------
# Round-trip error detection and reporting
# ---------------------------------------------------------------------------


class TestRoundTripErrorDetection:
    """Test round-trip validation error detection and reporting."""

    def setup_method(self):
        self.validator = RoundTripValidator()

    def test_errors_have_descriptive_messages(self):
        """Round-trip errors include descriptive messages."""
        original = {
            "contextMap": {
                "name": "Test",
                "type": "SYSTEM_LANDSCAPE",
                "contains": ["ServiceA"],
            },
            "boundedContexts": [{"name": "ServiceA", "type": "FEATURE"}],
        }
        # Provide CML that is missing the context map
        cml = "BoundedContext ServiceA type = FEATURE {}"
        result = self.validator.validate_round_trip(original, cml)
        if not result.is_valid:
            for error in result.errors:
                assert error.message, "Error should have a message"
                assert error.error_type, "Error should have an error_type"

    def test_warnings_have_descriptive_messages(self):
        """Round-trip warnings include descriptive messages."""
        json_data = load_json(VALID_DIR / "simple-context-map.json")
        cml_output = convert_to_cml(json_data)
        result = self.validator.validate_round_trip(json_data, cml_output)
        for warning in result.warnings:
            assert warning.message, "Warning should have a message"

    def test_round_trip_result_is_valid_for_good_conversion(self):
        """Round-trip result is valid for a correctly converted fixture."""
        json_data = load_json(VALID_DIR / "simple-context-map.json")
        cml_output = convert_to_cml(json_data)
        result = self.validator.validate_round_trip(json_data, cml_output)
        assert (
            result.is_valid
        ), f"Expected valid round-trip, got errors: {result.errors}"

    def test_discrepancy_str_representation(self):
        """Discrepancy objects have a useful string representation."""
        d = Discrepancy(
            property_path="contextMap.type",
            original_value="SYSTEM_LANDSCAPE",
            converted_value="ORGANIZATIONAL",
            discrepancy_type="VALUE_MISMATCH",
            description="Context Map type value mismatch",
        )
        s = str(d)
        assert "VALUE_MISMATCH" in s or "mismatch" in s.lower()


# ---------------------------------------------------------------------------
# Performance characteristics
# ---------------------------------------------------------------------------


class TestRoundTripPerformance:
    """Test performance characteristics of round-trip validation."""

    def setup_method(self):
        self.validator = RoundTripValidator()

    def test_simple_round_trip_completes_quickly(self):
        """Simple round-trip validation completes within 2 seconds."""
        json_data = load_json(VALID_DIR / "simple-context-map.json")
        cml_output = convert_to_cml(json_data)

        start = time.time()
        result = self.validator.validate_round_trip(json_data, cml_output)
        elapsed = time.time() - start

        assert elapsed < 2.0, f"Round-trip took too long: {elapsed:.2f}s"
        assert isinstance(result, ValidationResult)

    def test_complex_round_trip_completes_within_timeout(self):
        """Complex round-trip validation completes within 5 seconds."""
        json_data = load_json(VALID_DIR / "aggregates-entities.json")
        cml_output = convert_to_cml(json_data)

        start = time.time()
        result = self.validator.validate_round_trip(json_data, cml_output)
        elapsed = time.time() - start

        assert elapsed < 5.0, f"Complex round-trip took too long: {elapsed:.2f}s"

    def test_repeated_round_trips_are_consistent(self):
        """Repeated round-trip validations produce consistent results."""
        json_data = load_json(VALID_DIR / "simple-context-map.json")
        cml_output = convert_to_cml(json_data)

        results = [
            self.validator.validate_round_trip(json_data, cml_output) for _ in range(3)
        ]

        # All results should have the same validity
        validities = [r.is_valid for r in results]
        assert len(set(validities)) == 1, "Round-trip results should be consistent"

    def test_all_fixtures_round_trip_within_timeout(self):
        """All valid fixtures complete round-trip within 10 seconds total."""
        start = time.time()

        for json_file in VALID_DIR.glob("*.json"):
            json_data = load_json(json_file)
            cml_output = convert_to_cml(json_data)
            self.validator.validate_round_trip(json_data, cml_output)

        elapsed = time.time() - start
        assert elapsed < 10.0, f"All fixtures round-trip took too long: {elapsed:.2f}s"

    def test_cml_parser_performance(self):
        """CML parser completes within reasonable time."""
        json_data = load_json(VALID_DIR / "aggregates-entities.json")
        cml_output = convert_to_cml(json_data)

        parser = CMLParser()
        start = time.time()
        result = parser.parse_cml(cml_output)
        elapsed = time.time() - start

        assert elapsed < 1.0, f"CML parsing took too long: {elapsed:.2f}s"
        assert isinstance(result, dict)
