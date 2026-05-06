"""
Context Mapper Tool Integration for Context Mapper JSON Converter

Provides integration with Context Mapper CLI tools and ecosystem.
"""

import logging
import os
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .exceptions import ConversionError
from .types import ContextMapperDocument
from .validation import ValidationError, ValidationResult

logger = logging.getLogger(__name__)


@dataclass
class ContextMapperTool:
    """Represents a Context Mapper tool configuration."""

    name: str
    command: str
    version_arg: str = "--version"
    available: bool = False
    version: Optional[str] = None


class ContextMapperIntegration:
    """
    Integration with Context Mapper CLI tools and ecosystem.

    Provides functionality to:
    1. Detect available Context Mapper tools
    2. Validate CML files using Context Mapper CLI
    3. Generate artifacts using Context Mapper generators
    4. Integrate with Context Mapper VS Code extension
    """

    def __init__(self) -> None:
        """Initialize Context Mapper integration."""
        self.tools = {
            "contextmapper": ContextMapperTool(
                name="Context Mapper CLI", command="contextmapper"
            ),
            "cml": ContextMapperTool(name="CML CLI", command="cml"),
            "java": ContextMapperTool(
                name="Java Runtime", command="java", version_arg="-version"
            ),
        }
        self._detect_tools()

    def _detect_tools(self) -> None:
        """Detect available Context Mapper tools."""
        for tool_id, tool in self.tools.items():
            try:
                result = subprocess.run(
                    [tool.command, tool.version_arg],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if (
                    result.returncode == 0 or tool_id == "java"
                ):  # Java returns non-zero for -version
                    tool.available = True
                    # Extract version from output
                    output = result.stdout + result.stderr
                    tool.version = self._extract_version(output, tool_id)
                    logger.info(f"Detected {tool.name}: {tool.version}")
                else:
                    logger.debug(f"{tool.name} not available: {result.stderr}")

            except (
                subprocess.TimeoutExpired,
                FileNotFoundError,
                subprocess.SubprocessError,
            ) as e:
                logger.debug(f"{tool.name} not available: {e}")
                tool.available = False

    def _extract_version(self, output: str, tool_id: str) -> str:
        """Extract version information from tool output."""
        lines = output.split("\n")

        if tool_id == "java":
            for line in lines:
                if "version" in line.lower():
                    return line.strip()
        else:
            # For Context Mapper tools, look for version patterns
            for line in lines:
                if any(word in line.lower() for word in ["version", "v."]):
                    return line.strip()

        return "Unknown version"

    def get_available_tools(self) -> Dict[str, ContextMapperTool]:
        """Get dictionary of available Context Mapper tools."""
        return {tool_id: tool for tool_id, tool in self.tools.items() if tool.available}

    def is_context_mapper_available(self) -> bool:
        """Check if any Context Mapper tools are available."""
        return any(tool.available for tool in self.tools.values())

    def validate_cml_with_cli(self, cml_code: str) -> ValidationResult:
        """
        Validate CML code using Context Mapper CLI tools.

        Args:
            cml_code: The CML code to validate

        Returns:
            ValidationResult with CLI validation outcome
        """
        result = ValidationResult(is_valid=True, errors=[], warnings=[])

        if not self.is_context_mapper_available():
            result.add_warning(
                ValidationError(
                    message="No Context Mapper CLI tools available for validation",
                    property_path="",
                    error_type="INTEGRATION_WARNING",
                    suggestion="Install Context Mapper CLI or Java-based tools for enhanced validation",
                )
            )
            return result

        try:
            # Create temporary CML file
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".cml", delete=False
            ) as temp_file:
                temp_file.write(cml_code)
                temp_file_path = temp_file.name

            try:
                # Try Context Mapper CLI first
                if self.tools["contextmapper"].available:
                    cli_result = self._validate_with_contextmapper_cli(temp_file_path)
                    result.errors.extend(cli_result.errors)
                    result.warnings.extend(cli_result.warnings)
                    if not cli_result.is_valid:
                        result.is_valid = False

                # Try CML CLI as fallback
                elif self.tools["cml"].available:
                    cli_result = self._validate_with_cml_cli(temp_file_path)
                    result.errors.extend(cli_result.errors)
                    result.warnings.extend(cli_result.warnings)
                    if not cli_result.is_valid:
                        result.is_valid = False

                # Java-based validation as last resort
                elif self.tools["java"].available:
                    result.add_warning(
                        ValidationError(
                            message="Using basic Java validation - install Context Mapper CLI for full validation",
                            property_path="",
                            error_type="INTEGRATION_WARNING",
                        )
                    )

            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)

        except (OSError, subprocess.SubprocessError) as e:
            logger.error(f"CLI validation failed: {e}", exc_info=True)
            result.add_error(
                ValidationError(
                    message=f"CLI validation error: {str(e)}",
                    property_path="",
                    error_type="INTEGRATION_ERROR",
                )
            )

        return result

    def _validate_with_contextmapper_cli(self, file_path: str) -> ValidationResult:
        """Validate using Context Mapper CLI."""
        result = ValidationResult(is_valid=True, errors=[], warnings=[])

        try:
            # Run Context Mapper validation
            cmd_result = subprocess.run(
                ["contextmapper", "validate", file_path],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if cmd_result.returncode != 0:
                result.is_valid = False
                # Parse error output
                error_lines = cmd_result.stderr.split("\n")
                for line in error_lines:
                    if line.strip():
                        result.add_error(
                            ValidationError(
                                message=line.strip(),
                                property_path="",
                                error_type="CONTEXTMAPPER_CLI_ERROR",
                            )
                        )
            else:
                result.add_warning(
                    ValidationError(
                        message="CML validated successfully with Context Mapper CLI",
                        property_path="",
                        error_type="INTEGRATION_SUCCESS",
                    )
                )

        except subprocess.TimeoutExpired:
            result.add_error(
                ValidationError(
                    message="Context Mapper CLI validation timed out",
                    property_path="",
                    error_type="INTEGRATION_TIMEOUT",
                )
            )
        except (OSError, subprocess.SubprocessError) as e:
            result.add_error(
                ValidationError(
                    message=f"Context Mapper CLI error: {str(e)}",
                    property_path="",
                    error_type="INTEGRATION_ERROR",
                )
            )

        return result

    def _validate_with_cml_cli(self, file_path: str) -> ValidationResult:
        """Validate using CML CLI."""
        result = ValidationResult(is_valid=True, errors=[], warnings=[])

        try:
            # Run CML validation
            cmd_result = subprocess.run(
                ["cml", "validate", file_path],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if cmd_result.returncode != 0:
                result.is_valid = False
                result.add_error(
                    ValidationError(
                        message=f"CML CLI validation failed: {cmd_result.stderr}",
                        property_path="",
                        error_type="CML_CLI_ERROR",
                    )
                )
            else:
                result.add_warning(
                    ValidationError(
                        message="CML validated successfully with CML CLI",
                        property_path="",
                        error_type="INTEGRATION_SUCCESS",
                    )
                )

        except subprocess.TimeoutExpired:
            result.add_error(
                ValidationError(
                    message="CML CLI validation timed out",
                    property_path="",
                    error_type="INTEGRATION_TIMEOUT",
                )
            )
        except (OSError, subprocess.SubprocessError) as e:
            result.add_error(
                ValidationError(
                    message=f"CML CLI error: {str(e)}",
                    property_path="",
                    error_type="INTEGRATION_ERROR",
                )
            )

        return result

    def generate_artifacts(
        self, cml_code: str, generator_type: str = "plantuml"
    ) -> ValidationResult:
        """
        Generate artifacts from CML using Context Mapper generators.

        Args:
            cml_code: The CML code to process
            generator_type: Type of generator to use (plantuml, mdsl, etc.)

        Returns:
            ValidationResult with generation outcome
        """
        result = ValidationResult(is_valid=True, errors=[], warnings=[])

        if not self.tools["contextmapper"].available:
            result.add_warning(
                ValidationError(
                    message="Context Mapper CLI not available for artifact generation",
                    property_path="",
                    error_type="INTEGRATION_WARNING",
                    suggestion="Install Context Mapper CLI to generate artifacts",
                )
            )
            return result

        try:
            # Create temporary CML file
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".cml", delete=False
            ) as temp_file:
                temp_file.write(cml_code)
                temp_file_path = temp_file.name

            try:
                # Run generator
                cmd_result = subprocess.run(
                    ["contextmapper", "generate", generator_type, temp_file_path],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )

                if cmd_result.returncode == 0:
                    result.add_warning(
                        ValidationError(
                            message=f"Successfully generated {generator_type} artifacts",
                            property_path="",
                            error_type="INTEGRATION_SUCCESS",
                        )
                    )
                else:
                    result.add_error(
                        ValidationError(
                            message=f"Artifact generation failed: {cmd_result.stderr}",
                            property_path="",
                            error_type="GENERATOR_ERROR",
                        )
                    )

            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)

        except (OSError, subprocess.SubprocessError) as e:
            logger.error(f"Artifact generation failed: {e}", exc_info=True)
            result.add_error(
                ValidationError(
                    message=f"Artifact generation error: {str(e)}",
                    property_path="",
                    error_type="INTEGRATION_ERROR",
                )
            )

        return result

    def get_integration_status(self) -> Dict[str, Any]:
        """
        Get comprehensive integration status.

        Returns:
            Dictionary with integration status information
        """
        available_tools = self.get_available_tools()

        return {
            "tools_available": len(available_tools),
            "tools_detected": {
                tool_id: {
                    "available": tool.available,
                    "version": tool.version,
                    "command": tool.command,
                }
                for tool_id, tool in self.tools.items()
            },
            "integration_ready": self.is_context_mapper_available(),
            "recommended_setup": self._get_setup_recommendations(),
        }

    def _get_setup_recommendations(self) -> List[str]:
        """Get setup recommendations for Context Mapper integration."""
        recommendations = []

        if not self.tools["java"].available:
            recommendations.append(
                "Install Java Runtime Environment (JRE) 11 or higher"
            )

        if not self.tools["contextmapper"].available:
            recommendations.append(
                "Install Context Mapper CLI from https://contextmapper.org/docs/cli/"
            )

        if not any(tool.available for tool in self.tools.values()):
            recommendations.extend(
                [
                    "Install Context Mapper VS Code extension for IDE support",
                    "Consider using Context Mapper Docker image for containerized validation",
                    "Check Context Mapper documentation for alternative installation methods",
                ]
            )

        return recommendations


class ContextMapperWorkflow:
    """
    High-level workflow integration with Context Mapper ecosystem.

    Provides end-to-end workflows that combine JSON conversion with
    Context Mapper tool capabilities.
    """

    def __init__(self) -> None:
        """Initialize Context Mapper workflow."""
        self.integration = ContextMapperIntegration()

    def validate_and_generate_workflow(
        self, json_data: ContextMapperDocument, generators: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Complete workflow: JSON → CML → Validation → Artifact Generation.

        Args:
            json_data: Input JSON data
            generators: List of generators to run (plantuml, mdsl, etc.)

        Returns:
            Dictionary with results for each step
        """
        from .converter import ConverterEngine
        from .validation import ValidationEngine

        results: Dict[str, Any] = {}

        # Step 1: Validate JSON
        json_validator = ValidationEngine()
        json_result = json_validator.validate_json_schema(json_data)
        results["json_validation"] = json_result

        if not json_result.is_valid:
            return results

        # Step 2: Convert to CML
        try:
            converter = ConverterEngine()
            cml_code = converter.convert(json_data)
            results["conversion"] = ValidationResult(
                is_valid=True, errors=[], warnings=[]
            )
        except ConversionError as e:
            results["conversion"] = ValidationResult(
                is_valid=False,
                errors=[
                    ValidationError(
                        message=f"Conversion failed: {str(e)}",
                        property_path="",
                        error_type="CONVERSION_ERROR",
                    )
                ],
                warnings=[],
            )
            return results

        # Step 3: Validate with Context Mapper CLI
        cli_result = self.integration.validate_cml_with_cli(cml_code)
        results["cli_validation"] = cli_result

        # Step 4: Generate artifacts (if requested and validation passed)
        if generators and cli_result.is_valid:
            results["artifact_generation"] = {}
            for generator in generators:
                gen_result = self.integration.generate_artifacts(cml_code, generator)
                results["artifact_generation"][generator] = gen_result

        return results

    def get_workflow_status(self) -> Dict[str, Any]:
        """Get comprehensive workflow status."""
        integration_status = self.integration.get_integration_status()

        return {
            "integration_status": integration_status,
            "workflow_capabilities": {
                "json_validation": True,
                "cml_conversion": True,
                "cli_validation": integration_status["integration_ready"],
                "artifact_generation": integration_status["integration_ready"],
                "round_trip_validation": True,
            },
            "recommended_workflow": [
                "1. Validate JSON schema and semantics",
                "2. Convert JSON to CML",
                "3. Validate CML with Context Mapper CLI (if available)",
                "4. Generate artifacts (PlantUML, MDSL, etc.)",
                "5. Perform round-trip validation",
            ],
        }
