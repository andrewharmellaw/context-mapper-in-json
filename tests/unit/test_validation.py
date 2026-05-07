"""
Comprehensive unit tests for ValidationEngine.

Tests JSON schema validation, semantic rule validation, cross-reference validation,
and validation error reporting.
"""

import pytest

from context_mapper_json_converter.validation import (
    ValidationEngine,
    ValidationError,
    ValidationResult,
)


@pytest.fixture
def validator():
    return ValidationEngine()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _simple_valid():
    return {
        "contextMap": {"type": "SYSTEM_LANDSCAPE", "contains": ["A", "B"]},
        "boundedContexts": [
            {"name": "A", "type": "FEATURE"},
            {"name": "B", "type": "SYSTEM"},
        ],
    }


# ---------------------------------------------------------------------------
# Instantiation
# ---------------------------------------------------------------------------


class TestValidationEngineInit:
    def test_instantiation(self, validator):
        assert validator is not None

    def test_has_validators(self, validator):
        assert validator.context_map_validator is not None
        assert validator.bounded_context_validator is not None
        assert validator.subdomain_validator is not None


# ---------------------------------------------------------------------------
# validate_json_schema() – valid inputs
# ---------------------------------------------------------------------------


class TestValidateJsonSchemaValid:
    def test_simple_valid_data(self, validator):
        result = validator.validate_json_schema(_simple_valid())
        assert isinstance(result, ValidationResult)
        assert result.is_valid

    def test_valid_with_name(self, validator):
        data = {
            "contextMap": {
                "name": "MyMap",
                "type": "SYSTEM_LANDSCAPE",
                "contains": ["A"],
            },
            "boundedContexts": [{"name": "A", "type": "FEATURE"}],
        }
        result = validator.validate_json_schema(data)
        assert result.is_valid

    def test_valid_with_state(self, validator):
        data = {
            "contextMap": {
                "type": "SYSTEM_LANDSCAPE",
                "state": "AS_IS",
                "contains": ["A"],
            },
            "boundedContexts": [{"name": "A", "type": "FEATURE"}],
        }
        result = validator.validate_json_schema(data)
        assert result.is_valid

    def test_valid_organizational_type(self, validator):
        data = {
            "contextMap": {"type": "ORGANIZATIONAL", "contains": ["TeamA"]},
            "boundedContexts": [{"name": "TeamA", "type": "TEAM"}],
        }
        result = validator.validate_json_schema(data)
        assert result.is_valid

    def test_valid_all_bounded_context_types(self, validator):
        for bc_type in ["FEATURE", "APPLICATION", "SYSTEM", "TEAM"]:
            data = {
                "contextMap": {"type": "SYSTEM_LANDSCAPE", "contains": ["Ctx"]},
                "boundedContexts": [{"name": "Ctx", "type": bc_type}],
            }
            result = validator.validate_json_schema(data)
            assert result.is_valid, f"Expected valid for type {bc_type}"

    def test_valid_with_domain_vision_statement(self, validator):
        data = {
            "contextMap": {"type": "SYSTEM_LANDSCAPE", "contains": ["A"]},
            "boundedContexts": [
                {
                    "name": "A",
                    "type": "FEATURE",
                    "domainVisionStatement": "Handles orders",
                }
            ],
        }
        result = validator.validate_json_schema(data)
        assert result.is_valid

    def test_valid_with_relationships(self, validator):
        data = {
            "contextMap": {
                "type": "SYSTEM_LANDSCAPE",
                "contains": ["A", "B"],
                "relationships": [
                    {"type": "Partnership", "upstream": "A", "downstream": "B"}
                ],
            },
            "boundedContexts": [
                {"name": "A", "type": "FEATURE"},
                {"name": "B", "type": "SYSTEM"},
            ],
        }
        result = validator.validate_json_schema(data)
        assert result.is_valid

    def test_valid_with_subdomains(self, validator):
        data = {
            "subdomains": [{"name": "CoreSub", "type": "CORE_DOMAIN"}],
        }
        result = validator.validate_json_schema(data)
        assert result.is_valid

    def test_valid_with_aggregates(self, validator):
        data = {
            "contextMap": {"type": "SYSTEM_LANDSCAPE", "contains": ["A"]},
            "boundedContexts": [
                {
                    "name": "A",
                    "type": "FEATURE",
                    "aggregates": [{"name": "MyAggregate"}],
                }
            ],
        }
        result = validator.validate_json_schema(data)
        assert result.is_valid

    def test_valid_with_entities(self, validator):
        data = {
            "contextMap": {"type": "SYSTEM_LANDSCAPE", "contains": ["A"]},
            "boundedContexts": [
                {
                    "name": "A",
                    "type": "FEATURE",
                    "aggregates": [
                        {
                            "name": "Agg",
                            "entities": [
                                {
                                    "name": "MyEntity",
                                    "aggregateRoot": True,
                                    "attributes": [
                                        {"name": "id", "type": "String", "key": True}
                                    ],
                                }
                            ],
                        }
                    ],
                }
            ],
        }
        result = validator.validate_json_schema(data)
        assert result.is_valid

    def test_returns_validation_result_type(self, validator):
        result = validator.validate_json_schema(_simple_valid())
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")
        assert hasattr(result, "warnings")


# ---------------------------------------------------------------------------
# validate_json_schema() – invalid inputs
# ---------------------------------------------------------------------------


class TestValidateJsonSchemaInvalid:
    def test_missing_context_map_type(self, validator):
        data = {
            "contextMap": {"name": "X"},  # missing type and contains
            "boundedContexts": [],
        }
        result = validator.validate_json_schema(data)
        assert not result.is_valid
        assert len(result.errors) > 0

    def test_missing_context_map_contains(self, validator):
        data = {
            "contextMap": {"type": "SYSTEM_LANDSCAPE"},  # missing contains
            "boundedContexts": [],
        }
        result = validator.validate_json_schema(data)
        assert not result.is_valid

    def test_invalid_context_map_type(self, validator):
        data = {
            "contextMap": {"type": "INVALID_TYPE", "contains": ["A"]},
            "boundedContexts": [{"name": "A", "type": "FEATURE"}],
        }
        result = validator.validate_json_schema(data)
        assert not result.is_valid

    def test_invalid_context_map_state(self, validator):
        data = {
            "contextMap": {
                "type": "SYSTEM_LANDSCAPE",
                "state": "INVALID",
                "contains": ["A"],
            },
            "boundedContexts": [{"name": "A", "type": "FEATURE"}],
        }
        result = validator.validate_json_schema(data)
        assert not result.is_valid

    def test_missing_bounded_context_name(self, validator):
        data = {
            "contextMap": {"type": "SYSTEM_LANDSCAPE", "contains": ["A"]},
            "boundedContexts": [{"type": "FEATURE"}],  # missing name
        }
        result = validator.validate_json_schema(data)
        assert not result.is_valid

    def test_missing_bounded_context_type(self, validator):
        data = {
            "contextMap": {"type": "SYSTEM_LANDSCAPE", "contains": ["A"]},
            "boundedContexts": [{"name": "A"}],  # missing type
        }
        result = validator.validate_json_schema(data)
        assert not result.is_valid

    def test_invalid_bounded_context_type(self, validator):
        data = {
            "contextMap": {"type": "SYSTEM_LANDSCAPE", "contains": ["A"]},
            "boundedContexts": [{"name": "A", "type": "INVALID"}],
        }
        result = validator.validate_json_schema(data)
        assert not result.is_valid

    def test_invalid_relationship_type(self, validator):
        data = {
            "contextMap": {
                "type": "SYSTEM_LANDSCAPE",
                "contains": ["A", "B"],
                "relationships": [
                    {"type": "INVALID", "upstream": "A", "downstream": "B"}
                ],
            },
            "boundedContexts": [
                {"name": "A", "type": "FEATURE"},
                {"name": "B", "type": "SYSTEM"},
            ],
        }
        result = validator.validate_json_schema(data)
        assert not result.is_valid

    def test_missing_relationship_upstream(self, validator):
        data = {
            "contextMap": {
                "type": "SYSTEM_LANDSCAPE",
                "contains": ["A", "B"],
                "relationships": [{"type": "Partnership", "downstream": "B"}],
            },
            "boundedContexts": [
                {"name": "A", "type": "FEATURE"},
                {"name": "B", "type": "SYSTEM"},
            ],
        }
        result = validator.validate_json_schema(data)
        assert not result.is_valid

    def test_invalid_upstream_role(self, validator):
        data = {
            "contextMap": {
                "type": "SYSTEM_LANDSCAPE",
                "contains": ["A", "B"],
                "relationships": [
                    {
                        "type": "CustomerSupplier",
                        "upstream": "A",
                        "downstream": "B",
                        "upstreamRoles": ["INVALID_ROLE"],
                    }
                ],
            },
            "boundedContexts": [
                {"name": "A", "type": "FEATURE"},
                {"name": "B", "type": "SYSTEM"},
            ],
        }
        result = validator.validate_json_schema(data)
        assert not result.is_valid

    def test_errors_list_populated_on_failure(self, validator):
        data = {"contextMap": {"name": "X"}, "boundedContexts": []}
        result = validator.validate_json_schema(data)
        assert not result.is_valid
        assert isinstance(result.errors, list)
        assert len(result.errors) > 0

    def test_error_has_message(self, validator):
        data = {"contextMap": {"name": "X"}, "boundedContexts": []}
        result = validator.validate_json_schema(data)
        for error in result.errors:
            assert hasattr(error, "message")
            assert len(error.message) > 0

    def test_fixture_missing_required_fields(self, validator, load_invalid_json):
        data = load_invalid_json("missing-required-fields.json")
        result = validator.validate_json_schema(data)
        assert not result.is_valid

    def test_fixture_invalid_types(self, validator, load_invalid_json):
        data = load_invalid_json("invalid-types.json")
        result = validator.validate_json_schema(data)
        assert not result.is_valid


# ---------------------------------------------------------------------------
# validate_semantic_rules()
# ---------------------------------------------------------------------------


class TestValidateSemanticRules:
    def test_valid_data_passes_semantic_rules(self, validator):
        result = validator.validate_semantic_rules(_simple_valid())
        assert result.is_valid

    def test_duplicate_bounded_context_names(self, validator):
        data = {
            "contextMap": {"type": "SYSTEM_LANDSCAPE", "contains": ["A", "B"]},
            "boundedContexts": [
                {"name": "A", "type": "FEATURE"},
                {"name": "A", "type": "SYSTEM"},  # duplicate
            ],
        }
        result = validator.validate_semantic_rules(data)
        assert not result.is_valid
        assert any(
            "Duplicate" in e.message or "duplicate" in e.message.lower()
            for e in result.errors
        )

    def test_context_map_references_undefined_context(self, validator):
        data = {
            "contextMap": {"type": "SYSTEM_LANDSCAPE", "contains": ["A", "Missing"]},
            "boundedContexts": [{"name": "A", "type": "FEATURE"}],
        }
        result = validator.validate_semantic_rules(data)
        assert not result.is_valid

    def test_relationship_upstream_not_in_contains(self, validator):
        data = {
            "contextMap": {
                "type": "SYSTEM_LANDSCAPE",
                "contains": ["A", "B"],
                "relationships": [
                    {"type": "Partnership", "upstream": "C", "downstream": "B"}
                ],
            },
            "boundedContexts": [
                {"name": "A", "type": "FEATURE"},
                {"name": "B", "type": "SYSTEM"},
            ],
        }
        result = validator.validate_semantic_rules(data)
        assert not result.is_valid

    def test_relationship_downstream_not_in_contains(self, validator):
        data = {
            "contextMap": {
                "type": "SYSTEM_LANDSCAPE",
                "contains": ["A", "B"],
                "relationships": [
                    {"type": "Partnership", "upstream": "A", "downstream": "C"}
                ],
            },
            "boundedContexts": [
                {"name": "A", "type": "FEATURE"},
                {"name": "B", "type": "SYSTEM"},
            ],
        }
        result = validator.validate_semantic_rules(data)
        assert not result.is_valid

    def test_self_relationship_is_invalid(self, validator):
        data = {
            "contextMap": {
                "type": "SYSTEM_LANDSCAPE",
                "contains": ["A"],
                "relationships": [
                    {"type": "Partnership", "upstream": "A", "downstream": "A"}
                ],
            },
            "boundedContexts": [{"name": "A", "type": "FEATURE"}],
        }
        result = validator.validate_semantic_rules(data)
        assert not result.is_valid

    def test_non_team_with_realizes_generates_warning(self, validator):
        data = {
            "contextMap": {"type": "SYSTEM_LANDSCAPE", "contains": ["A"]},
            "boundedContexts": [
                {"name": "A", "type": "FEATURE", "realizes": "SomeCtx"}
            ],
        }
        result = validator.validate_semantic_rules(data)
        # Should produce a warning (not necessarily an error)
        assert result.has_warnings or not result.is_valid

    def test_fixture_duplicate_names(self, validator, load_invalid_json):
        data = load_invalid_json("duplicate-names.json")
        result = validator.validate_semantic_rules(data)
        assert not result.is_valid

    def test_fixture_missing_references(self, validator, load_invalid_json):
        data = load_invalid_json("missing-references.json")
        result = validator.validate_semantic_rules(data)
        assert not result.is_valid

    def test_returns_validation_result(self, validator):
        result = validator.validate_semantic_rules(_simple_valid())
        assert isinstance(result, ValidationResult)


# ---------------------------------------------------------------------------
# validate_references()
# ---------------------------------------------------------------------------


class TestValidateReferences:
    def test_valid_references(self, validator):
        result = validator.validate_references(_simple_valid())
        assert result.is_valid

    def test_team_realizes_valid_context(self, validator):
        data = {
            "contextMap": {
                "type": "SYSTEM_LANDSCAPE",
                "contains": ["TeamA", "OrderCtx"],
            },
            "boundedContexts": [
                {"name": "TeamA", "type": "TEAM", "realizes": "OrderCtx"},
                {"name": "OrderCtx", "type": "FEATURE"},
            ],
        }
        result = validator.validate_references(data)
        assert result.is_valid

    def test_team_realizes_undefined_context(self, validator):
        data = {
            "contextMap": {"type": "SYSTEM_LANDSCAPE", "contains": ["TeamA"]},
            "boundedContexts": [
                {"name": "TeamA", "type": "TEAM", "realizes": "NonExistent"},
            ],
        }
        result = validator.validate_references(data)
        assert not result.is_valid

    def test_no_context_map_returns_valid(self, validator):
        data = {"boundedContexts": [{"name": "A", "type": "FEATURE"}]}
        result = validator.validate_references(data)
        assert result.is_valid

    def test_returns_validation_result(self, validator):
        result = validator.validate_references(_simple_valid())
        assert isinstance(result, ValidationResult)


# ---------------------------------------------------------------------------
# get_validation_suggestions()
# ---------------------------------------------------------------------------


class TestGetValidationSuggestions:
    def test_returns_list(self, validator):
        errors = [
            ValidationError(message="test", property_path="", error_type="SCHEMA_ERROR")
        ]
        result = validator.get_validation_suggestions(errors)
        assert isinstance(result, list)

    def test_returns_suggestions_for_schema_errors(self, validator):
        errors = [
            ValidationError(message="test", property_path="", error_type="SCHEMA_ERROR")
        ]
        result = validator.get_validation_suggestions(errors)
        assert len(result) > 0

    def test_returns_suggestions_for_reference_errors(self, validator):
        errors = [
            ValidationError(
                message="test", property_path="", error_type="REFERENCE_ERROR"
            )
        ]
        result = validator.get_validation_suggestions(errors)
        assert len(result) > 0

    def test_uses_error_suggestion_when_available(self, validator):
        errors = [
            ValidationError(
                message="test",
                property_path="",
                error_type="SCHEMA_ERROR",
                suggestion="Fix this",
            )
        ]
        result = validator.get_validation_suggestions(errors)
        assert "Fix this" in result

    def test_deduplicates_suggestions(self, validator):
        errors = [
            ValidationError(
                message="t1",
                property_path="",
                error_type="SCHEMA_ERROR",
                suggestion="Same suggestion",
            ),
            ValidationError(
                message="t2",
                property_path="",
                error_type="SCHEMA_ERROR",
                suggestion="Same suggestion",
            ),
        ]
        result = validator.get_validation_suggestions(errors)
        assert result.count("Same suggestion") == 1

    def test_empty_errors_returns_empty_list(self, validator):
        result = validator.get_validation_suggestions([])
        assert result == []


# ---------------------------------------------------------------------------
# ValidationResult dataclass
# ---------------------------------------------------------------------------


class TestValidationResult:
    def test_initial_state_valid(self):
        result = ValidationResult(is_valid=True, errors=[], warnings=[])
        assert result.is_valid
        assert not result.has_errors
        assert not result.has_warnings

    def test_add_error_sets_invalid(self):
        result = ValidationResult(is_valid=True, errors=[], warnings=[])
        result.add_error(
            ValidationError(message="err", property_path="", error_type="TEST")
        )
        assert not result.is_valid
        assert result.has_errors

    def test_add_warning_keeps_valid(self):
        result = ValidationResult(is_valid=True, errors=[], warnings=[])
        result.add_warning(
            ValidationError(message="warn", property_path="", error_type="TEST")
        )
        assert result.is_valid
        assert result.has_warnings

    def test_multiple_errors(self):
        result = ValidationResult(is_valid=True, errors=[], warnings=[])
        result.add_error(
            ValidationError(message="e1", property_path="", error_type="T")
        )
        result.add_error(
            ValidationError(message="e2", property_path="", error_type="T")
        )
        assert len(result.errors) == 2


# ---------------------------------------------------------------------------
# ValidationError dataclass
# ---------------------------------------------------------------------------


class TestValidationError:
    def test_str_representation(self):
        error = ValidationError(
            message="Something wrong",
            property_path="contextMap.type",
            error_type="SCHEMA_ERROR",
        )
        s = str(error)
        assert "SCHEMA_ERROR" in s
        assert "Something wrong" in s

    def test_str_with_line_number(self):
        error = ValidationError(
            message="err", property_path="", error_type="T", line_number=42
        )
        s = str(error)
        assert "42" in s

    def test_optional_fields_default_none(self):
        error = ValidationError(message="err", property_path="", error_type="T")
        assert error.line_number is None
        assert error.column_number is None
        assert error.suggestion is None
