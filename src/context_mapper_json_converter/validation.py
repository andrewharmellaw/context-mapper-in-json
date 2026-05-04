"""
JSON Validation Engine for Context Mapper JSON Converter
"""

import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from jsonschema import (
    validate,
    ValidationError as JsonSchemaValidationError,
    Draft7Validator,
)
from .schemas.context_map import CONTEXT_MAP_SCHEMA, CONTEXT_MAP_SEMANTIC_RULES
from .schemas.bounded_context import (
    BOUNDED_CONTEXT_SCHEMA,
    BOUNDED_CONTEXT_SEMANTIC_RULES,
)
from .schemas.subdomain import SUBDOMAIN_SCHEMA, SUBDOMAIN_SEMANTIC_RULES

logger = logging.getLogger(__name__)


@dataclass
class ValidationError:
    """Represents a validation error with detailed information."""

    message: str
    property_path: str
    error_type: str
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    suggestion: Optional[str] = None

    def __str__(self) -> str:
        """String representation of the validation error."""
        location = f" at {self.property_path}" if self.property_path else ""
        line_info = f" (line {self.line_number})" if self.line_number else ""
        return f"{self.error_type}: {self.message}{location}{line_info}"


@dataclass
class ValidationResult:
    """Result of validation operation."""

    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]

    def __post_init__(self):
        """Ensure errors and warnings are lists."""
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []

    @property
    def has_errors(self) -> bool:
        """Check if there are any validation errors."""
        return len(self.errors) > 0

    @property
    def has_warnings(self) -> bool:
        """Check if there are any validation warnings."""
        return len(self.warnings) > 0

    def add_error(self, error: ValidationError) -> None:
        """Add a validation error."""
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: ValidationError) -> None:
        """Add a validation warning."""
        self.warnings.append(warning)


class ValidationEngine:
    """
    Comprehensive validation engine for Context Mapper JSON definitions.

    Provides multi-layered validation:
    1. JSON Schema validation - structural and type validation
    2. Semantic validation - business rule validation
    3. Reference validation - cross-reference integrity
    """

    def __init__(self):
        """Initialize the validation engine with schemas."""
        self.context_map_validator = Draft7Validator(CONTEXT_MAP_SCHEMA)
        self.bounded_context_validator = Draft7Validator(BOUNDED_CONTEXT_SCHEMA)
        self.subdomain_validator = Draft7Validator(SUBDOMAIN_SCHEMA)

    def validate_json_schema(self, json_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate JSON data against the appropriate schema.

        Args:
            json_data: The JSON data to validate

        Returns:
            ValidationResult with validation outcome and any errors
        """
        result = ValidationResult(is_valid=True, errors=[], warnings=[])

        try:
            # Determine what type of data we're validating
            if "contextMap" in json_data:
                self._validate_context_map_schema(json_data["contextMap"], result)

            if "boundedContexts" in json_data:
                self._validate_bounded_contexts_schema(
                    json_data["boundedContexts"], result
                )

            if "subdomains" in json_data:
                self._validate_subdomains_schema(json_data["subdomains"], result)

            # If we have both, validate the complete structure
            if "contextMap" in json_data and "boundedContexts" in json_data:
                self._validate_complete_structure_schema(json_data, result)

        except Exception as e:
            logger.error(f"Unexpected error during schema validation: {e}")
            result.add_error(
                ValidationError(
                    message=f"Unexpected validation error: {str(e)}",
                    property_path="",
                    error_type="VALIDATION_ERROR",
                )
            )

        return result

    def _validate_context_map_schema(
        self, context_map_data: Dict[str, Any], result: ValidationResult
    ) -> None:
        """Validate Context Map against schema."""
        try:
            self.context_map_validator.validate(context_map_data)
            logger.debug("Context Map schema validation passed")
        except JsonSchemaValidationError as e:
            error = ValidationError(
                message=e.message,
                property_path=".".join(str(p) for p in e.absolute_path),
                error_type="SCHEMA_ERROR",
                suggestion=self._get_schema_error_suggestion(e),
            )
            result.add_error(error)
            logger.warning(f"Context Map schema validation failed: {error}")

    def _validate_bounded_contexts_schema(
        self, bounded_contexts_data: List[Dict[str, Any]], result: ValidationResult
    ) -> None:
        """Validate Bounded Contexts against schema."""
        if not isinstance(bounded_contexts_data, list):
            result.add_error(
                ValidationError(
                    message="boundedContexts must be an array",
                    property_path="boundedContexts",
                    error_type="SCHEMA_ERROR",
                )
            )
            return

        for i, context_data in enumerate(bounded_contexts_data):
            try:
                self.bounded_context_validator.validate(context_data)
                logger.debug(f"Bounded Context {i} schema validation passed")
            except JsonSchemaValidationError as e:
                error = ValidationError(
                    message=e.message,
                    property_path=f"boundedContexts[{i}].{'.'.join(str(p) for p in e.absolute_path)}",
                    error_type="SCHEMA_ERROR",
                    suggestion=self._get_schema_error_suggestion(e),
                )
                result.add_error(error)
                logger.warning(f"Bounded Context {i} schema validation failed: {error}")

    def _validate_subdomains_schema(
        self, subdomains_data: List[Dict[str, Any]], result: ValidationResult
    ) -> None:
        """Validate Subdomains against schema."""
        if not isinstance(subdomains_data, list):
            result.add_error(
                ValidationError(
                    message="subdomains must be an array",
                    property_path="subdomains",
                    error_type="SCHEMA_ERROR",
                )
            )
            return

        for i, subdomain_data in enumerate(subdomains_data):
            try:
                self.subdomain_validator.validate(subdomain_data)
                logger.debug(f"Subdomain {i} schema validation passed")
            except JsonSchemaValidationError as e:
                error = ValidationError(
                    message=e.message,
                    property_path=f"subdomains[{i}].{'.'.join(str(p) for p in e.absolute_path)}",
                    error_type="SCHEMA_ERROR",
                    suggestion=self._get_schema_error_suggestion(e),
                )
                result.add_error(error)
                logger.warning(f"Subdomain {i} schema validation failed: {error}")

    def _validate_complete_structure_schema(
        self, json_data: Dict[str, Any], result: ValidationResult
    ) -> None:
        """Validate the complete JSON structure."""
        # Check that the root structure is valid
        required_properties = ["contextMap", "boundedContexts"]
        for prop in required_properties:
            if prop not in json_data:
                result.add_error(
                    ValidationError(
                        message=f"Missing required property: {prop}",
                        property_path="",
                        error_type="SCHEMA_ERROR",
                        suggestion=f"Add the '{prop}' property to the root object",
                    )
                )

    def validate_semantic_rules(self, json_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate semantic rules and business constraints.

        Args:
            json_data: The JSON data to validate

        Returns:
            ValidationResult with semantic validation outcome
        """
        result = ValidationResult(is_valid=True, errors=[], warnings=[])

        try:
            if "contextMap" in json_data and "boundedContexts" in json_data:
                self._validate_context_map_semantics(
                    json_data["contextMap"], json_data["boundedContexts"], result
                )
                self._validate_bounded_context_semantics(
                    json_data["boundedContexts"], result
                )

        except Exception as e:
            logger.error(f"Unexpected error during semantic validation: {e}")
            result.add_error(
                ValidationError(
                    message=f"Unexpected semantic validation error: {str(e)}",
                    property_path="",
                    error_type="SEMANTIC_ERROR",
                )
            )

        return result

    def _validate_context_map_semantics(
        self,
        context_map: Dict[str, Any],
        bounded_contexts: List[Dict[str, Any]],
        result: ValidationResult,
    ) -> None:
        """Validate Context Map semantic rules."""
        # Get bounded context names for reference validation
        context_names = {ctx.get("name") for ctx in bounded_contexts if ctx.get("name")}

        # Validate that all contexts in 'contains' exist
        contains = context_map.get("contains", [])
        for context_name in contains:
            if context_name not in context_names:
                result.add_error(
                    ValidationError(
                        message=f"Context Map references undefined Bounded Context: {context_name}",
                        property_path="contextMap.contains",
                        error_type="REFERENCE_ERROR",
                        suggestion=f"Add a Bounded Context with name '{context_name}' or remove it from contains",
                    )
                )

        # Validate relationships
        relationships = context_map.get("relationships", [])
        for i, rel in enumerate(relationships):
            upstream = rel.get("upstream")
            downstream = rel.get("downstream")

            # Check that relationship participants exist in contains
            if upstream and upstream not in contains:
                result.add_error(
                    ValidationError(
                        message=f"Relationship upstream '{upstream}' not found in Context Map contains",
                        property_path=f"contextMap.relationships[{i}].upstream",
                        error_type="REFERENCE_ERROR",
                        suggestion=f"Add '{upstream}' to contextMap.contains or change the upstream reference",
                    )
                )

            if downstream and downstream not in contains:
                result.add_error(
                    ValidationError(
                        message=f"Relationship downstream '{downstream}' not found in Context Map contains",
                        property_path=f"contextMap.relationships[{i}].downstream",
                        error_type="REFERENCE_ERROR",
                        suggestion=f"Add '{downstream}' to contextMap.contains or change the downstream reference",
                    )
                )

            # Check for self-relationships
            if upstream == downstream:
                result.add_error(
                    ValidationError(
                        message=f"Bounded Context cannot have a relationship with itself: {upstream}",
                        property_path=f"contextMap.relationships[{i}]",
                        error_type="SEMANTIC_ERROR",
                        suggestion="Use different Bounded Contexts for upstream and downstream",
                    )
                )

    def _validate_bounded_context_semantics(
        self, bounded_contexts: List[Dict[str, Any]], result: ValidationResult
    ) -> None:
        """Validate Bounded Context semantic rules."""
        context_names = []

        for i, context in enumerate(bounded_contexts):
            name = context.get("name")
            context_type = context.get("type")

            # Check for unique names
            if name in context_names:
                result.add_error(
                    ValidationError(
                        message=f"Duplicate Bounded Context name: {name}",
                        property_path=f"boundedContexts[{i}].name",
                        error_type="SEMANTIC_ERROR",
                        suggestion=f"Use a unique name for this Bounded Context",
                    )
                )
            else:
                context_names.append(name)

            # Validate TEAM type constraints
            if context_type == "TEAM":
                realizes = context.get("realizes")
                if realizes and realizes not in context_names and realizes != name:
                    # Note: This is a forward reference check - we'll validate it exists later
                    pass
            else:
                # Non-TEAM contexts should not have 'realizes'
                if "realizes" in context:
                    result.add_warning(
                        ValidationError(
                            message=f"Only TEAM type Bounded Contexts should have 'realizes' property",
                            property_path=f"boundedContexts[{i}].realizes",
                            error_type="SEMANTIC_WARNING",
                            suggestion="Remove the 'realizes' property or change the type to TEAM",
                        )
                    )

    def validate_references(self, json_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate cross-reference integrity.

        Args:
            json_data: The JSON data to validate

        Returns:
            ValidationResult with reference validation outcome
        """
        result = ValidationResult(is_valid=True, errors=[], warnings=[])

        try:
            if "contextMap" in json_data and "boundedContexts" in json_data:
                self._validate_cross_references(
                    json_data["contextMap"], json_data["boundedContexts"], result
                )

        except Exception as e:
            logger.error(f"Unexpected error during reference validation: {e}")
            result.add_error(
                ValidationError(
                    message=f"Unexpected reference validation error: {str(e)}",
                    property_path="",
                    error_type="REFERENCE_ERROR",
                )
            )

        return result

    def _validate_cross_references(
        self,
        context_map: Dict[str, Any],
        bounded_contexts: List[Dict[str, Any]],
        result: ValidationResult,
    ) -> None:
        """Validate cross-references between Context Map and Bounded Contexts."""
        context_names = {ctx.get("name") for ctx in bounded_contexts if ctx.get("name")}

        # Validate TEAM realizes references
        for i, context in enumerate(bounded_contexts):
            if context.get("type") == "TEAM":
                realizes = context.get("realizes")
                if realizes and realizes not in context_names:
                    result.add_error(
                        ValidationError(
                            message=f"TEAM Bounded Context realizes undefined context: {realizes}",
                            property_path=f"boundedContexts[{i}].realizes",
                            error_type="REFERENCE_ERROR",
                            suggestion=f"Add a Bounded Context with name '{realizes}' or change the realizes reference",
                        )
                    )

    def _get_schema_error_suggestion(
        self, error: JsonSchemaValidationError
    ) -> Optional[str]:
        """Generate helpful suggestions for schema validation errors."""
        if "is not of type" in error.message:
            return (
                f"Check the data type - expected {error.schema.get('type', 'unknown')}"
            )
        elif "is not one of" in error.message:
            enum_values = error.schema.get("enum", [])
            return f"Use one of the allowed values: {', '.join(enum_values)}"
        elif "does not match" in error.message:
            pattern = error.schema.get("pattern", "")
            return f"Value must match pattern: {pattern}"
        elif "is a required property" in error.message:
            return "Add the missing required property"
        elif "Additional properties are not allowed" in error.message:
            return "Remove the extra property or check for typos"
        return None

    def get_validation_suggestions(self, errors: List[ValidationError]) -> List[str]:
        """
        Generate actionable suggestions for validation errors.

        Args:
            errors: List of validation errors

        Returns:
            List of suggestion strings
        """
        suggestions = []

        for error in errors:
            if error.suggestion:
                suggestions.append(error.suggestion)
            else:
                # Generate generic suggestions based on error type
                if error.error_type == "SCHEMA_ERROR":
                    suggestions.append("Check the JSON structure and data types")
                elif error.error_type == "REFERENCE_ERROR":
                    suggestions.append(
                        "Verify that all referenced elements are defined"
                    )
                elif error.error_type == "SEMANTIC_ERROR":
                    suggestions.append("Review the business rules and constraints")

        return list(set(suggestions))  # Remove duplicates
