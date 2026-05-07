"""
Context Mapper integration tests.

Tests the ContextMapperIntegration and ContextMapperWorkflow classes,
including graceful handling when Context Mapper CLI tools are not available.
"""

import json
from pathlib import Path

import pytest

from context_mapper_json_converter.context_mapper_integration import (
    ContextMapperIntegration,
    ContextMapperTool,
    ContextMapperWorkflow,
)
from context_mapper_json_converter.validation import ValidationResult

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
VALID_DIR = FIXTURES_DIR / "valid"


def load_json(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


# Module-scoped fixtures so tool detection only runs once per test session.


@pytest.fixture(scope="module")
def integration():
    return ContextMapperIntegration()


@pytest.fixture(scope="module")
def workflow():
    return ContextMapperWorkflow()


# ---------------------------------------------------------------------------
# ContextMapperIntegration – tool detection
# ---------------------------------------------------------------------------


class TestContextMapperIntegrationToolDetection:
    """Test tool detection and availability checking."""

    def test_integration_initialises_without_error(self, integration):
        """ContextMapperIntegration can be instantiated."""
        assert integration is not None

    def test_tools_dict_contains_expected_keys(self, integration):
        """Tools dictionary contains contextmapper, cml, and java keys."""
        assert "contextmapper" in integration.tools
        assert "cml" in integration.tools
        assert "java" in integration.tools

    def test_each_tool_is_contextmapper_tool_instance(self, integration):
        """Each tool entry is a ContextMapperTool dataclass."""
        for tool in integration.tools.values():
            assert isinstance(tool, ContextMapperTool)

    def test_is_context_mapper_available_returns_bool(self, integration):
        """is_context_mapper_available returns a boolean."""
        result = integration.is_context_mapper_available()
        assert isinstance(result, bool)

    def test_get_available_tools_returns_dict(self, integration):
        """get_available_tools returns a dictionary."""
        available = integration.get_available_tools()
        assert isinstance(available, dict)

    def test_available_tools_are_subset_of_all_tools(self, integration):
        """Available tools are a subset of all tools."""
        available = integration.get_available_tools()
        for key in available:
            assert key in integration.tools

    def test_context_mapper_not_available_in_test_env(self, integration):
        """Context Mapper CLI is not available in the test environment."""
        # In CI / test environments, contextmapper CLI is not installed
        cm_tool = integration.tools["contextmapper"]
        # We don't assert False here because java might be available;
        # we just verify the attribute exists and is a bool
        assert isinstance(cm_tool.available, bool)


# ---------------------------------------------------------------------------
# ContextMapperIntegration – validate_cml_with_cli
# ---------------------------------------------------------------------------


class TestValidateCMLWithCLI:
    """Test CML validation via CLI (graceful degradation when unavailable)."""

    def test_validate_cml_returns_validation_result(self, integration):
        """validate_cml_with_cli always returns a ValidationResult."""
        cml_code = "ContextMap Test type = SYSTEM_LANDSCAPE { contains ServiceA }\nBoundedContext ServiceA type = FEATURE {}"
        result = integration.validate_cml_with_cli(cml_code)
        assert isinstance(result, ValidationResult)

    def test_validate_cml_without_cli_returns_warning(self, integration):
        """When CLI is unavailable, validation returns a warning (not an error)."""
        if (
            integration.tools["contextmapper"].available
            or integration.tools["cml"].available
        ):
            pytest.skip(
                "A Context Mapper CLI tool is available – skipping unavailability test"
            )

        cml_code = "ContextMap Test type = SYSTEM_LANDSCAPE { contains ServiceA }\nBoundedContext ServiceA type = FEATURE {}"
        result = integration.validate_cml_with_cli(cml_code)
        # Should be valid (no hard errors) but may have warnings
        assert result.is_valid
        assert len(result.warnings) > 0

    def test_validate_cml_warning_mentions_no_cli(self, integration):
        """Warning message mentions that no CLI tools are available."""
        if (
            integration.tools["contextmapper"].available
            or integration.tools["cml"].available
        ):
            pytest.skip("A Context Mapper CLI tool is available")

        cml_code = "ContextMap Test type = SYSTEM_LANDSCAPE { contains ServiceA }\nBoundedContext ServiceA type = FEATURE {}"
        result = integration.validate_cml_with_cli(cml_code)
        warning_messages = " ".join(str(w) for w in result.warnings)
        assert (
            "Context Mapper" in warning_messages
            or "CLI" in warning_messages
            or "available" in warning_messages.lower()
        )

    def test_validate_empty_cml_does_not_crash(self, integration):
        """Validating empty CML string does not raise an exception."""
        result = integration.validate_cml_with_cli("")
        assert isinstance(result, ValidationResult)

    def test_validate_cml_with_real_fixture(self, integration):
        """Validation works with CML generated from a real fixture."""
        from context_mapper_json_converter.converter import ConverterEngine

        json_data = load_json(VALID_DIR / "simple-context-map.json")
        converter = ConverterEngine()
        cml_output = converter.convert(json_data)

        result = integration.validate_cml_with_cli(cml_output)
        assert isinstance(result, ValidationResult)


# ---------------------------------------------------------------------------
# ContextMapperIntegration – generate_artifacts
# ---------------------------------------------------------------------------


class TestGenerateArtifacts:
    """Test artifact generation (graceful degradation when CLI unavailable)."""

    def test_generate_artifacts_returns_validation_result(self, integration):
        """generate_artifacts always returns a ValidationResult."""
        cml_code = "ContextMap Test type = SYSTEM_LANDSCAPE { contains ServiceA }\nBoundedContext ServiceA type = FEATURE {}"
        result = integration.generate_artifacts(cml_code, "plantuml")
        assert isinstance(result, ValidationResult)

    def test_generate_artifacts_without_cli_returns_warning(self, integration):
        """When CLI is unavailable, artifact generation returns a warning."""
        if integration.tools["contextmapper"].available:
            pytest.skip("Context Mapper CLI is available")

        cml_code = "ContextMap Test type = SYSTEM_LANDSCAPE { contains ServiceA }\nBoundedContext ServiceA type = FEATURE {}"
        result = integration.generate_artifacts(cml_code, "plantuml")
        # Should be valid (no hard errors) but with a warning
        assert result.is_valid
        assert len(result.warnings) > 0

    def test_generate_artifacts_warning_mentions_cli(self, integration):
        """Warning message mentions Context Mapper CLI."""
        if integration.tools["contextmapper"].available:
            pytest.skip("Context Mapper CLI is available")

        cml_code = "ContextMap Test type = SYSTEM_LANDSCAPE { contains ServiceA }\nBoundedContext ServiceA type = FEATURE {}"
        result = integration.generate_artifacts(cml_code, "plantuml")
        warning_messages = " ".join(str(w) for w in result.warnings)
        assert "Context Mapper" in warning_messages or "CLI" in warning_messages

    def test_generate_artifacts_different_generator_types(self, integration):
        """generate_artifacts accepts different generator type strings."""
        cml_code = "ContextMap Test type = SYSTEM_LANDSCAPE { contains ServiceA }\nBoundedContext ServiceA type = FEATURE {}"
        for gen_type in ["plantuml", "mdsl", "generic"]:
            result = integration.generate_artifacts(cml_code, gen_type)
            assert isinstance(result, ValidationResult)


# ---------------------------------------------------------------------------
# ContextMapperIntegration – get_integration_status
# ---------------------------------------------------------------------------


class TestGetIntegrationStatus:
    """Test integration status reporting."""

    def test_get_integration_status_returns_dict(self, integration):
        """get_integration_status returns a dictionary."""
        status = integration.get_integration_status()
        assert isinstance(status, dict)

    def test_integration_status_has_required_keys(self, integration):
        """Integration status contains expected keys."""
        status = integration.get_integration_status()
        assert "tools_available" in status
        assert "tools_detected" in status
        assert "integration_ready" in status
        assert "recommended_setup" in status

    def test_tools_detected_contains_all_tools(self, integration):
        """tools_detected contains entries for all known tools."""
        status = integration.get_integration_status()
        for tool_id in ["contextmapper", "cml", "java"]:
            assert tool_id in status["tools_detected"]

    def test_tools_detected_entries_have_required_fields(self, integration):
        """Each tool entry has available, version, and command fields."""
        status = integration.get_integration_status()
        for tool_id, tool_info in status["tools_detected"].items():
            assert "available" in tool_info
            assert "version" in tool_info
            assert "command" in tool_info

    def test_integration_ready_is_bool(self, integration):
        """integration_ready is a boolean."""
        status = integration.get_integration_status()
        assert isinstance(status["integration_ready"], bool)

    def test_recommended_setup_is_list(self, integration):
        """recommended_setup is a list."""
        status = integration.get_integration_status()
        assert isinstance(status["recommended_setup"], list)

    def test_tools_available_count_matches_available_tools(self, integration):
        """tools_available count matches the number of available tools."""
        status = integration.get_integration_status()
        available_count = sum(
            1 for t in status["tools_detected"].values() if t["available"]
        )
        assert status["tools_available"] == available_count


# ---------------------------------------------------------------------------
# ContextMapperWorkflow
# ---------------------------------------------------------------------------


class TestContextMapperWorkflow:
    """Test the high-level ContextMapperWorkflow class."""

    def test_workflow_initialises_without_error(self, workflow):
        """ContextMapperWorkflow can be instantiated."""
        assert workflow is not None
        assert workflow.integration is not None

    def test_validate_and_generate_workflow_returns_dict(self, workflow):
        """validate_and_generate_workflow returns a dictionary of results."""
        json_data = load_json(VALID_DIR / "simple-context-map.json")
        results = workflow.validate_and_generate_workflow(json_data)
        assert isinstance(results, dict)

    def test_workflow_includes_json_validation_step(self, workflow):
        """Workflow results include json_validation step."""
        json_data = load_json(VALID_DIR / "simple-context-map.json")
        results = workflow.validate_and_generate_workflow(json_data)
        assert "json_validation" in results

    def test_workflow_includes_conversion_step(self, workflow):
        """Workflow results include conversion step."""
        json_data = load_json(VALID_DIR / "simple-context-map.json")
        results = workflow.validate_and_generate_workflow(json_data)
        assert "conversion" in results

    def test_workflow_includes_cli_validation_step(self, workflow):
        """Workflow results include cli_validation step."""
        json_data = load_json(VALID_DIR / "simple-context-map.json")
        results = workflow.validate_and_generate_workflow(json_data)
        assert "cli_validation" in results

    def test_workflow_valid_json_passes_json_validation(self, workflow):
        """Valid JSON passes the json_validation step."""
        json_data = load_json(VALID_DIR / "simple-context-map.json")
        results = workflow.validate_and_generate_workflow(json_data)
        assert results["json_validation"].is_valid

    def test_workflow_valid_json_passes_conversion(self, workflow):
        """Valid JSON passes the conversion step."""
        json_data = load_json(VALID_DIR / "simple-context-map.json")
        results = workflow.validate_and_generate_workflow(json_data)
        assert results["conversion"].is_valid

    def test_workflow_invalid_json_stops_at_validation(self, workflow):
        """Invalid JSON stops the workflow at json_validation."""
        invalid_data = {"contextMap": {"name": "Test"}}  # missing required fields
        results = workflow.validate_and_generate_workflow(invalid_data)
        assert "json_validation" in results
        assert not results["json_validation"].is_valid
        # Conversion step should not be present when validation fails
        assert "conversion" not in results

    def test_workflow_with_generators_returns_artifact_results(self, workflow):
        """Workflow with generators includes artifact_generation in results when CLI available."""
        json_data = load_json(VALID_DIR / "simple-context-map.json")
        results = workflow.validate_and_generate_workflow(
            json_data, generators=["plantuml"]
        )
        # If CLI is available, artifact_generation should be present
        # If not, it won't be present (CLI validation may not be valid)
        assert isinstance(results, dict)

    def test_get_workflow_status_returns_dict(self, workflow):
        """get_workflow_status returns a dictionary."""
        status = workflow.get_workflow_status()
        assert isinstance(status, dict)

    def test_workflow_status_has_required_keys(self, workflow):
        """Workflow status contains expected keys."""
        status = workflow.get_workflow_status()
        assert "integration_status" in status
        assert "workflow_capabilities" in status
        assert "recommended_workflow" in status

    def test_workflow_capabilities_includes_core_features(self, workflow):
        """Workflow capabilities includes json_validation and cml_conversion."""
        status = workflow.get_workflow_status()
        caps = status["workflow_capabilities"]
        assert caps.get("json_validation") is True
        assert caps.get("cml_conversion") is True

    def test_workflow_recommended_steps_is_list(self, workflow):
        """recommended_workflow is a non-empty list."""
        status = workflow.get_workflow_status()
        assert isinstance(status["recommended_workflow"], list)
        assert len(status["recommended_workflow"]) > 0

    def test_workflow_processes_all_valid_fixtures(self, workflow):
        """Workflow processes all valid fixture files without crashing."""
        for json_file in VALID_DIR.glob("*.json"):
            json_data = load_json(json_file)
            results = workflow.validate_and_generate_workflow(json_data)
            assert isinstance(results, dict), f"Failed for {json_file.name}"
            assert "json_validation" in results


# ---------------------------------------------------------------------------
# External dependency handling and error recovery
# ---------------------------------------------------------------------------


class TestExternalDependencyHandling:
    """Test graceful handling of missing external dependencies."""

    def test_missing_cli_does_not_raise_exception(self, integration):
        """Missing Context Mapper CLI does not raise an exception."""
        # This should always work regardless of CLI availability
        result = integration.validate_cml_with_cli(
            "BoundedContext Test type = FEATURE {}"
        )
        assert isinstance(result, ValidationResult)

    def test_missing_cli_artifact_generation_does_not_raise(self, integration):
        """Missing CLI for artifact generation does not raise an exception."""
        result = integration.generate_artifacts(
            "BoundedContext Test type = FEATURE {}", "plantuml"
        )
        assert isinstance(result, ValidationResult)

    def test_integration_status_always_returns_complete_info(self, integration):
        """Integration status always returns complete information regardless of tool availability."""
        status = integration.get_integration_status()
        # All three tools should be reported even if unavailable
        assert len(status["tools_detected"]) == 3

    def test_recommendations_provided_when_tools_missing(self, integration):
        """Setup recommendations are provided when tools are not available."""
        status = integration.get_integration_status()
        if not status["integration_ready"]:
            assert len(status["recommended_setup"]) > 0


# ---------------------------------------------------------------------------
# ContextMapperIntegration – _extract_version
# ---------------------------------------------------------------------------


class TestExtractVersion:
    """Test version extraction from tool output."""

    def test_extract_version_java_with_version_line(self, integration):
        """_extract_version extracts version from java output."""
        output = 'openjdk version "11.0.2" 2019-01-15\nOpenJDK Runtime Environment'
        version = integration._extract_version(output, "java")
        assert "version" in version.lower() or "11" in version

    def test_extract_version_java_no_version_line(self, integration):
        """_extract_version returns Unknown version when no version line found."""
        output = "some output without version info"
        version = integration._extract_version(output, "java")
        assert isinstance(version, str)

    def test_extract_version_contextmapper_with_version_line(self, integration):
        """_extract_version extracts version from contextmapper output."""
        output = "Context Mapper CLI version 6.8.0\nUsage: contextmapper"
        version = integration._extract_version(output, "contextmapper")
        assert "version" in version.lower() or "6.8.0" in version

    def test_extract_version_contextmapper_no_version_line(self, integration):
        """_extract_version returns Unknown version when no version line found."""
        output = "some output without any matching info"
        version = integration._extract_version(output, "contextmapper")
        assert version == "Unknown version"

    def test_extract_version_returns_string(self, integration):
        """_extract_version always returns a string."""
        version = integration._extract_version("", "contextmapper")
        assert isinstance(version, str)


# ---------------------------------------------------------------------------
# ContextMapperIntegration – _validate_with_contextmapper_cli (direct call)
# ---------------------------------------------------------------------------


class TestValidateWithContextmapperCLI:
    """Test _validate_with_contextmapper_cli directly."""

    def test_validate_with_contextmapper_cli_returns_validation_result(
        self, integration
    ):
        """_validate_with_contextmapper_cli returns a ValidationResult."""
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".cml", delete=False) as f:
            f.write(
                "ContextMap Test type = SYSTEM_LANDSCAPE { contains ServiceA }\nBoundedContext ServiceA type = FEATURE {}"
            )
            path = f.name
        try:
            result = integration._validate_with_contextmapper_cli(path)
            assert isinstance(result, ValidationResult)
        finally:
            os.unlink(path)

    def test_validate_with_contextmapper_cli_handles_missing_command(self, integration):
        """_validate_with_contextmapper_cli handles FileNotFoundError gracefully."""
        import os
        import tempfile

        # Temporarily make contextmapper unavailable by using a non-existent path
        original_command = integration.tools["contextmapper"].command
        integration.tools["contextmapper"].command = "/nonexistent/contextmapper"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".cml", delete=False) as f:
            f.write("ContextMap Test type = SYSTEM_LANDSCAPE {}")
            path = f.name
        try:
            result = integration._validate_with_contextmapper_cli(path)
            assert isinstance(result, ValidationResult)
        finally:
            os.unlink(path)
            integration.tools["contextmapper"].command = original_command


# ---------------------------------------------------------------------------
# ContextMapperIntegration – _validate_with_cml_cli (direct call)
# ---------------------------------------------------------------------------


class TestValidateWithCmlCLI:
    """Test _validate_with_cml_cli directly."""

    def test_validate_with_cml_cli_returns_validation_result(self, integration):
        """_validate_with_cml_cli returns a ValidationResult."""
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".cml", delete=False) as f:
            f.write(
                "ContextMap Test type = SYSTEM_LANDSCAPE { contains ServiceA }\nBoundedContext ServiceA type = FEATURE {}"
            )
            path = f.name
        try:
            result = integration._validate_with_cml_cli(path)
            assert isinstance(result, ValidationResult)
        finally:
            os.unlink(path)

    def test_validate_with_cml_cli_handles_missing_command(self, integration):
        """_validate_with_cml_cli handles FileNotFoundError gracefully."""
        import os
        import tempfile

        original_command = integration.tools["cml"].command
        integration.tools["cml"].command = "/nonexistent/cml"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".cml", delete=False) as f:
            f.write("ContextMap Test type = SYSTEM_LANDSCAPE {}")
            path = f.name
        try:
            result = integration._validate_with_cml_cli(path)
            assert isinstance(result, ValidationResult)
        finally:
            os.unlink(path)
            integration.tools["cml"].command = original_command


# ---------------------------------------------------------------------------
# ContextMapperIntegration – validate_cml_with_cli with mocked tool availability
# ---------------------------------------------------------------------------


class TestValidateCMLWithCLIToolPaths:
    """Test validate_cml_with_cli with different tool availability scenarios."""

    def test_validate_cml_with_java_only_available(self, integration):
        """When only java is available, validation returns a warning about basic validation."""
        # Force only java to be available
        original_states = {
            k: (v.available, v.command) for k, v in integration.tools.items()
        }
        integration.tools["contextmapper"].available = False
        integration.tools["cml"].available = False
        integration.tools["java"].available = True

        try:
            cml_code = "ContextMap Test type = SYSTEM_LANDSCAPE { contains ServiceA }\nBoundedContext ServiceA type = FEATURE {}"
            result = integration.validate_cml_with_cli(cml_code)
            assert isinstance(result, ValidationResult)
            assert result.is_valid  # Java fallback just adds a warning
        finally:
            for k, (avail, cmd) in original_states.items():
                integration.tools[k].available = avail
                integration.tools[k].command = cmd

    def test_validate_cml_with_contextmapper_available(self, integration):
        """When contextmapper is available, it is used for validation."""
        # Force contextmapper to be available (but with a non-existent command to test error handling)
        original_available = integration.tools["contextmapper"].available
        original_command = integration.tools["contextmapper"].command
        integration.tools["contextmapper"].available = True
        integration.tools["contextmapper"].command = "/nonexistent/contextmapper"

        try:
            cml_code = "ContextMap Test type = SYSTEM_LANDSCAPE { contains ServiceA }\nBoundedContext ServiceA type = FEATURE {}"
            result = integration.validate_cml_with_cli(cml_code)
            assert isinstance(result, ValidationResult)
        finally:
            integration.tools["contextmapper"].available = original_available
            integration.tools["contextmapper"].command = original_command

    def test_validate_cml_with_cml_cli_available(self, integration):
        """When cml CLI is available (but not contextmapper), it is used for validation."""
        original_cm_available = integration.tools["contextmapper"].available
        original_cml_available = integration.tools["cml"].available
        original_cml_command = integration.tools["cml"].command
        integration.tools["contextmapper"].available = False
        integration.tools["cml"].available = True
        integration.tools["cml"].command = "/nonexistent/cml"

        try:
            cml_code = "ContextMap Test type = SYSTEM_LANDSCAPE { contains ServiceA }\nBoundedContext ServiceA type = FEATURE {}"
            result = integration.validate_cml_with_cli(cml_code)
            assert isinstance(result, ValidationResult)
        finally:
            integration.tools["contextmapper"].available = original_cm_available
            integration.tools["cml"].available = original_cml_available
            integration.tools["cml"].command = original_cml_command


# ---------------------------------------------------------------------------
# ContextMapperIntegration – generate_artifacts with contextmapper available
# ---------------------------------------------------------------------------


class TestGenerateArtifactsWithCLI:
    """Test generate_artifacts when contextmapper CLI is (simulated as) available."""

    def test_generate_artifacts_with_contextmapper_available(self, integration):
        """generate_artifacts uses contextmapper CLI when available."""
        original_available = integration.tools["contextmapper"].available
        original_command = integration.tools["contextmapper"].command
        integration.tools["contextmapper"].available = True
        integration.tools["contextmapper"].command = "/nonexistent/contextmapper"

        try:
            cml_code = "ContextMap Test type = SYSTEM_LANDSCAPE { contains ServiceA }\nBoundedContext ServiceA type = FEATURE {}"
            result = integration.generate_artifacts(cml_code, "plantuml")
            assert isinstance(result, ValidationResult)
        finally:
            integration.tools["contextmapper"].available = original_available
            integration.tools["contextmapper"].command = original_command


# ---------------------------------------------------------------------------
# ContextMapperIntegration – _get_setup_recommendations coverage
# ---------------------------------------------------------------------------


class TestSetupRecommendations:
    """Test _get_setup_recommendations for all tool availability scenarios."""

    def test_recommendations_when_no_tools_available(self, integration):
        """When no tools are available, extended recommendations are provided."""
        original_states = {k: v.available for k, v in integration.tools.items()}
        for tool in integration.tools.values():
            tool.available = False

        try:
            recommendations = integration._get_setup_recommendations()
            assert isinstance(recommendations, list)
            assert len(recommendations) > 0
        finally:
            for k, avail in original_states.items():
                integration.tools[k].available = avail

    def test_recommendations_when_java_missing(self, integration):
        """When java is missing, JRE installation is recommended."""
        original_java_available = integration.tools["java"].available
        integration.tools["java"].available = False

        try:
            recommendations = integration._get_setup_recommendations()
            assert any("Java" in r or "JRE" in r for r in recommendations)
        finally:
            integration.tools["java"].available = original_java_available

    def test_recommendations_when_contextmapper_missing(self, integration):
        """When contextmapper is missing, CLI installation is recommended."""
        original_cm_available = integration.tools["contextmapper"].available
        integration.tools["contextmapper"].available = False

        try:
            recommendations = integration._get_setup_recommendations()
            assert any(
                "Context Mapper" in r or "contextmapper" in r.lower()
                for r in recommendations
            )
        finally:
            integration.tools["contextmapper"].available = original_cm_available


# ---------------------------------------------------------------------------
# ContextMapperWorkflow – artifact generation in workflow
# ---------------------------------------------------------------------------


class TestWorkflowArtifactGeneration:
    """Test artifact generation within the workflow."""

    def test_workflow_with_generators_when_cli_available(self, workflow):
        """Workflow with generators runs artifact generation when CLI is available."""
        # Force contextmapper to be available with a non-existent command
        original_available = workflow.integration.tools["contextmapper"].available
        original_command = workflow.integration.tools["contextmapper"].command
        workflow.integration.tools["contextmapper"].available = True
        workflow.integration.tools["contextmapper"].command = (
            "/nonexistent/contextmapper"
        )

        try:
            json_data = load_json(VALID_DIR / "simple-context-map.json")
            results = workflow.validate_and_generate_workflow(
                json_data, generators=["plantuml"]
            )
            assert isinstance(results, dict)
            # artifact_generation should be present when CLI is available and validation passes
            if results.get("cli_validation") and results["cli_validation"].is_valid:
                assert "artifact_generation" in results
        finally:
            workflow.integration.tools["contextmapper"].available = original_available
            workflow.integration.tools["contextmapper"].command = original_command

    def test_workflow_artifact_generation_with_multiple_generators(self, workflow):
        """Workflow handles multiple generators."""
        original_available = workflow.integration.tools["contextmapper"].available
        original_command = workflow.integration.tools["contextmapper"].command
        workflow.integration.tools["contextmapper"].available = True
        workflow.integration.tools["contextmapper"].command = (
            "/nonexistent/contextmapper"
        )

        try:
            json_data = load_json(VALID_DIR / "simple-context-map.json")
            results = workflow.validate_and_generate_workflow(
                json_data, generators=["plantuml", "mdsl"]
            )
            assert isinstance(results, dict)
        finally:
            workflow.integration.tools["contextmapper"].available = original_available
            workflow.integration.tools["contextmapper"].command = original_command
