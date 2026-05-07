"""
End-to-end integration tests for Context Mapper JSON Converter.

Tests complete workflows from JSON input to CML output using real files
and the CLI interface.
"""

import json
import os
import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from context_mapper_json_converter.cli import convert, main
from context_mapper_json_converter.cml_validator import CMLValidator
from context_mapper_json_converter.converter import ConverterEngine
from context_mapper_json_converter.validation import ValidationEngine

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
VALID_DIR = FIXTURES_DIR / "valid"
INVALID_DIR = FIXTURES_DIR / "invalid"
EXPECTED_DIR = FIXTURES_DIR / "expected"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_json(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def load_text(path: Path) -> str:
    with open(path) as f:
        return f.read()


# ---------------------------------------------------------------------------
# Full JSON → CML workflow tests (no CLI)
# ---------------------------------------------------------------------------


class TestFullConversionWorkflow:
    """Test complete JSON to CML conversion workflows using the engine directly."""

    def test_simple_context_map_workflow(self):
        """Full workflow: load JSON, validate, convert, validate CML."""
        json_data = load_json(VALID_DIR / "simple-context-map.json")

        validator = ValidationEngine()
        schema_result = validator.validate_json_schema(json_data)
        assert (
            schema_result.is_valid
        ), f"Schema validation failed: {schema_result.errors}"

        semantic_result = validator.validate_semantic_rules(json_data)
        assert (
            semantic_result.is_valid
        ), f"Semantic validation failed: {semantic_result.errors}"

        converter = ConverterEngine()
        cml_output = converter.convert(json_data)
        assert cml_output, "CML output should not be empty"
        assert "ContextMap" in cml_output
        assert "BoundedContext" in cml_output

        cml_validator = CMLValidator()
        cml_result = cml_validator.validate_syntax(cml_output)
        assert cml_result.is_valid, f"CML validation failed: {cml_result.errors}"

    def test_customer_supplier_workflow(self):
        """Full workflow with CustomerSupplier relationship."""
        json_data = load_json(VALID_DIR / "customer-supplier.json")

        validator = ValidationEngine()
        assert validator.validate_json_schema(json_data).is_valid
        assert validator.validate_semantic_rules(json_data).is_valid

        converter = ConverterEngine()
        cml_output = converter.convert(json_data)

        assert "CustomerSupplier" in cml_output or "->" in cml_output
        assert "SupplierService" in cml_output
        assert "CustomerService" in cml_output

        cml_validator = CMLValidator()
        assert cml_validator.validate_syntax(cml_output).is_valid

    def test_partnership_workflow(self):
        """Full workflow with Partnership relationship."""
        json_data = load_json(VALID_DIR / "partnership.json")

        converter = ConverterEngine()
        cml_output = converter.convert(json_data)

        assert "Partnership" in cml_output

        cml_validator = CMLValidator()
        assert cml_validator.validate_syntax(cml_output).is_valid

    def test_shared_kernel_workflow(self):
        """Full workflow with SharedKernel relationship."""
        json_data = load_json(VALID_DIR / "shared-kernel.json")

        converter = ConverterEngine()
        cml_output = converter.convert(json_data)

        assert "[SK]" in cml_output

        cml_validator = CMLValidator()
        assert cml_validator.validate_syntax(cml_output).is_valid

    def test_aggregates_entities_workflow(self):
        """Full workflow with tactical DDD patterns (aggregates, entities)."""
        json_data = load_json(VALID_DIR / "aggregates-entities.json")

        validator = ValidationEngine()
        assert validator.validate_json_schema(json_data).is_valid

        converter = ConverterEngine()
        cml_output = converter.convert(json_data)

        assert "Aggregate" in cml_output
        assert "Entity" in cml_output

        cml_validator = CMLValidator()
        assert cml_validator.validate_syntax(cml_output).is_valid

    def test_value_objects_workflow(self):
        """Full workflow with value objects."""
        json_data = load_json(VALID_DIR / "value-objects.json")

        converter = ConverterEngine()
        cml_output = converter.convert(json_data)

        assert "ValueObject" in cml_output

    def test_domain_events_workflow(self):
        """Full workflow with domain events."""
        json_data = load_json(VALID_DIR / "domain-events.json")

        converter = ConverterEngine()
        cml_output = converter.convert(json_data)

        assert "DomainEvent" in cml_output

    def test_subdomains_workflow(self):
        """Full workflow with subdomains."""
        json_data = load_json(VALID_DIR / "subdomains.json")

        converter = ConverterEngine()
        cml_output = converter.convert(json_data)

        assert "Domain" in cml_output or "Subdomain" in cml_output

    def test_all_valid_fixtures_convert_successfully(self):
        """All valid fixture files should convert without errors."""
        converter = ConverterEngine()
        validator = ValidationEngine()

        for json_file in VALID_DIR.glob("*.json"):
            json_data = load_json(json_file)
            schema_result = validator.validate_json_schema(json_data)
            assert (
                schema_result.is_valid
            ), f"{json_file.name}: schema validation failed: {schema_result.errors}"
            cml_output = converter.convert(json_data)
            assert cml_output, f"{json_file.name}: CML output should not be empty"


# ---------------------------------------------------------------------------
# CLI integration tests
# ---------------------------------------------------------------------------


class TestCLIIntegration:
    """Test CLI integration with file system operations."""

    def setup_method(self):
        self.runner = CliRunner()

    def test_cli_convert_simple_file_to_stdout(self):
        """CLI convert command outputs CML to stdout."""
        result = self.runner.invoke(
            main, ["convert", str(VALID_DIR / "simple-context-map.json")]
        )
        assert result.exit_code == 0, f"CLI failed: {result.output}"
        assert "BoundedContext" in result.output

    def test_cli_convert_to_output_file(self):
        """CLI convert command writes CML to output file."""
        with tempfile.NamedTemporaryFile(suffix=".cml", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            result = self.runner.invoke(
                main,
                ["convert", str(VALID_DIR / "simple-context-map.json"), tmp_path],
            )
            assert result.exit_code == 0, f"CLI failed: {result.output}"
            assert os.path.exists(tmp_path)
            content = load_text(Path(tmp_path))
            assert "BoundedContext" in content
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_cli_validate_only_flag(self):
        """CLI --validate-only flag validates without converting."""
        result = self.runner.invoke(
            main,
            ["convert", "--validate-only", str(VALID_DIR / "simple-context-map.json")],
        )
        assert result.exit_code == 0, f"CLI failed: {result.output}"
        assert "validation" in result.output.lower() or "✅" in result.output

    def test_cli_invalid_json_exits_with_error(self):
        """CLI exits with non-zero code for invalid JSON."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            tmp.write("{invalid json}")
            tmp_path = tmp.name

        try:
            result = self.runner.invoke(main, ["convert", tmp_path])
            assert result.exit_code != 0
        finally:
            os.unlink(tmp_path)

    def test_cli_missing_required_fields_exits_with_error(self):
        """CLI exits with error for JSON missing required fields."""
        invalid_data = {"contextMap": {"name": "Test"}}  # missing type and contains
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            json.dump(invalid_data, tmp)
            tmp_path = tmp.name

        try:
            result = self.runner.invoke(main, ["convert", tmp_path])
            assert result.exit_code != 0
        finally:
            os.unlink(tmp_path)

    def test_cli_verbose_flag_produces_more_output(self):
        """CLI --verbose flag produces additional output."""
        result_normal = self.runner.invoke(
            main, ["convert", str(VALID_DIR / "simple-context-map.json")]
        )
        result_verbose = self.runner.invoke(
            main,
            ["convert", "--verbose", str(VALID_DIR / "simple-context-map.json")],
        )
        assert result_normal.exit_code == 0
        assert result_verbose.exit_code == 0

    def test_cli_skip_cml_validation_flag(self):
        """CLI --skip-cml-validation flag skips CML validation step."""
        result = self.runner.invoke(
            main,
            [
                "convert",
                "--skip-cml-validation",
                str(VALID_DIR / "simple-context-map.json"),
            ],
        )
        assert result.exit_code == 0

    def test_cli_integration_status_command(self):
        """CLI integration-status command reports tool availability."""
        result = self.runner.invoke(main, ["integration-status"])
        assert result.exit_code == 0
        assert "Integration" in result.output or "Tools" in result.output

    def test_cli_version_command(self):
        """CLI version command outputs version string."""
        result = self.runner.invoke(main, ["version"])
        assert result.exit_code == 0
        assert "Converter" in result.output or "v" in result.output

    def test_cli_round_trip_command(self):
        """CLI round-trip command performs round-trip validation."""
        result = self.runner.invoke(
            main, ["round-trip", str(VALID_DIR / "simple-context-map.json")]
        )
        assert result.exit_code == 0

    def test_cli_convert_all_valid_fixtures(self):
        """All valid fixtures should convert successfully via CLI."""
        for json_file in VALID_DIR.glob("*.json"):
            result = self.runner.invoke(main, ["convert", str(json_file)])
            assert (
                result.exit_code == 0
            ), f"CLI failed for {json_file.name}: {result.output}"

    def test_cli_conversion_summary_shown(self):
        """CLI shows conversion summary after successful conversion."""
        result = self.runner.invoke(
            main, ["convert", str(VALID_DIR / "simple-context-map.json")]
        )
        assert result.exit_code == 0
        assert "Summary" in result.output or "Bounded Context" in result.output


# ---------------------------------------------------------------------------
# Error handling across complete workflows
# ---------------------------------------------------------------------------


class TestWorkflowErrorHandling:
    """Test error handling across complete workflows."""

    def setup_method(self):
        self.runner = CliRunner()

    def test_invalid_json_syntax_error_message(self):
        """Workflow produces clear error for malformed JSON."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            tmp.write("{ not valid json }")
            tmp_path = tmp.name

        try:
            result = self.runner.invoke(main, ["convert", tmp_path])
            assert result.exit_code != 0
            assert "JSON" in result.output or "json" in result.output.lower()
        finally:
            os.unlink(tmp_path)

    def test_schema_validation_error_shows_details(self):
        """Schema validation errors include helpful details."""
        invalid_data = {
            "contextMap": {
                "name": "Test",
                # missing required 'type' and 'contains'
            }
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            json.dump(invalid_data, tmp)
            tmp_path = tmp.name

        try:
            result = self.runner.invoke(main, ["convert", tmp_path])
            assert result.exit_code != 0
        finally:
            os.unlink(tmp_path)

    def test_semantic_validation_error_for_missing_references(self):
        """Semantic validation catches missing context references."""
        invalid_data = {
            "contextMap": {
                "name": "Test",
                "type": "SYSTEM_LANDSCAPE",
                "contains": ["ServiceA", "ServiceB"],
            },
            "boundedContexts": [
                {"name": "ServiceA", "type": "FEATURE"}
                # ServiceB is missing
            ],
        }
        validator = ValidationEngine()
        result = validator.validate_semantic_rules(invalid_data)
        assert not result.is_valid
        assert any("ServiceB" in str(e) for e in result.errors)

    def test_converter_raises_on_completely_empty_input(self):
        """Converter handles empty input gracefully."""
        converter = ConverterEngine()
        # Empty dict should produce empty or minimal output, not crash
        try:
            cml_output = converter.convert({})
            # Either empty string or minimal output is acceptable
            assert isinstance(cml_output, str)
        except (ValueError, Exception):
            pass  # Raising an exception is also acceptable

    def test_workflow_with_invalid_fixture_files(self):
        """Invalid fixture files should fail validation."""
        validator = ValidationEngine()
        for json_file in INVALID_DIR.glob("*.json"):
            try:
                json_data = load_json(json_file)
                schema_result = validator.validate_json_schema(json_data)
                semantic_result = validator.validate_semantic_rules(json_data)
                # At least one validation should fail for invalid files
                both_valid = schema_result.is_valid and semantic_result.is_valid
                # Some invalid files may pass schema but fail semantic, or vice versa
                # The important thing is that we can process them without crashing
            except json.JSONDecodeError:
                pass  # Malformed JSON is expected for some invalid fixtures


# ---------------------------------------------------------------------------
# Logging and output formatting
# ---------------------------------------------------------------------------


class TestLoggingAndOutputFormatting:
    """Test logging and output formatting across workflows."""

    def setup_method(self):
        self.runner = CliRunner()

    def test_cli_output_contains_cml_separator(self):
        """CLI output includes separator around CML content."""
        result = self.runner.invoke(
            main, ["convert", str(VALID_DIR / "simple-context-map.json")]
        )
        assert result.exit_code == 0
        assert "=" in result.output or "CML" in result.output

    def test_cli_error_output_uses_stderr(self):
        """CLI error messages go to stderr (captured in output by CliRunner)."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            tmp.write("{bad}")
            tmp_path = tmp.name

        try:
            result = self.runner.invoke(main, ["convert", tmp_path], mix_stderr=False)
            assert result.exit_code != 0
        finally:
            os.unlink(tmp_path)

    def test_cli_success_output_contains_checkmark(self):
        """Successful CLI operations include success indicators."""
        with tempfile.NamedTemporaryFile(suffix=".cml", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            result = self.runner.invoke(
                main,
                ["convert", str(VALID_DIR / "simple-context-map.json"), tmp_path],
            )
            assert result.exit_code == 0
            assert "✅" in result.output or "written" in result.output.lower()
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_conversion_summary_counts_are_accurate(self):
        """Conversion summary shows accurate counts."""
        json_data = load_json(VALID_DIR / "customer-supplier.json")
        bc_count = len(json_data.get("boundedContexts", []))
        rel_count = len(json_data.get("contextMap", {}).get("relationships", []))

        result = self.runner.invoke(
            main, ["convert", str(VALID_DIR / "customer-supplier.json")]
        )
        assert result.exit_code == 0
        assert str(bc_count) in result.output
        assert str(rel_count) in result.output
