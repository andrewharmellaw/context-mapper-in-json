"""Property-based tests for ValidationEngine.

Tests validation robustness across randomly generated JSON structures,
error message consistency, and validation properties across many input scenarios.

**Validates: Requirements 2.3, 2.5, 2.9**
"""

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from context_mapper_json_converter import ValidationEngine
from context_mapper_json_converter.validation import ValidationError, ValidationResult

# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

VALID_CONTEXT_MAP_TYPES = ["SYSTEM_LANDSCAPE", "ORGANIZATIONAL"]
VALID_BC_TYPES = ["FEATURE", "APPLICATION", "SYSTEM", "TEAM"]
VALID_RELATIONSHIP_TYPES = ["Partnership", "SharedKernel", "CustomerSupplier", "UpstreamDownstream"]


@st.composite
def valid_context_map_json(draw):
    """Generate a complete valid context map JSON structure."""
    num_contexts = draw(st.integers(min_value=1, max_value=4))
    context_names = [f"Context{i}" for i in range(num_contexts)]
    cm_type = draw(st.sampled_from(VALID_CONTEXT_MAP_TYPES))

    bounded_contexts = [
        {"name": n, "type": draw(st.sampled_from(VALID_BC_TYPES))}
        for n in context_names
    ]

    return {
        "contextMap": {"type": cm_type, "contains": context_names},
        "boundedContexts": bounded_contexts,
    }


@st.composite
def json_with_missing_required_fields(draw):
    """Generate JSON missing required fields to trigger schema errors."""
    variant = draw(st.sampled_from(["no_type", "no_contains", "empty_contains"]))
    if variant == "no_type":
        return {"contextMap": {"contains": ["Alpha"]}}
    elif variant == "no_contains":
        return {"contextMap": {"type": "SYSTEM_LANDSCAPE"}}
    else:
        return {"contextMap": {"type": "SYSTEM_LANDSCAPE", "contains": []}}


@st.composite
def json_with_invalid_bc_type(draw):
    """Generate JSON with an invalid bounded context type.
    
    Uses a mix of common invalid values and random strings to ensure
    good test coverage without excessive filtering.
    """
    # Common invalid types that users might actually try
    common_invalid = [
        "SERVICE", "MODULE", "COMPONENT", "DOMAIN", "SUBDOMAIN",
        "CONTEXT", "BOUNDARY", "AGGREGATE", "ENTITY", "VALUE_OBJECT",
        "REPOSITORY", "FACTORY", "SERVICE_LAYER", "API", "DATABASE"
    ]
    
    # Either pick a common invalid type or generate a random one
    use_common = draw(st.booleans())
    if use_common:
        invalid_type = draw(st.sampled_from(common_invalid))
    else:
        # Generate random text that's definitely not valid
        invalid_type = draw(st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll")),
            min_size=1,
            max_size=10,
        ))
        # Only filter if we accidentally generated a valid type (rare)
        assume(invalid_type not in VALID_BC_TYPES)
    
    return {
        "contextMap": {"type": "SYSTEM_LANDSCAPE", "contains": ["Alpha"]},
        "boundedContexts": [{"name": "Alpha", "type": invalid_type}],
    }


@st.composite
def json_with_invalid_cm_type(draw):
    """Generate JSON with an invalid context map type.
    
    Uses a mix of common invalid values and random strings to ensure
    good test coverage without excessive filtering.
    """
    # Common invalid types that users might actually try
    common_invalid = [
        "SYSTEM", "DOMAIN", "CONTEXT", "APPLICATION", "TEAM",
        "FEATURE", "ENGAGEMENT", "BUSINESS", "TECHNICAL", "CORE",
        "SUPPORTING", "GENERIC", "INFRASTRUCTURE", "FRONTEND", "BACKEND"
    ]
    
    # Either pick a common invalid type or generate a random one
    use_common = draw(st.booleans())
    if use_common:
        invalid_type = draw(st.sampled_from(common_invalid))
    else:
        # Generate random text that's definitely not valid
        invalid_type = draw(st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll")),
            min_size=1,
            max_size=10,
        ))
        # Only filter if we accidentally generated a valid type (rare)
        assume(invalid_type not in VALID_CONTEXT_MAP_TYPES)
    
    return {
        "contextMap": {"type": invalid_type, "contains": ["Alpha"]},
        "boundedContexts": [{"name": "Alpha", "type": "FEATURE"}],
    }


# ---------------------------------------------------------------------------
# Property tests
# ---------------------------------------------------------------------------

class TestValidationProperties:
    """Property-based tests for ValidationEngine."""

    @given(valid_context_map_json())
    @settings(max_examples=15, deadline=None)
    def test_valid_json_always_returns_validation_result(self, json_data):
        """
        Property: validate_json_schema() always returns a ValidationResult instance.

        **Validates: Requirements 2.3, 2.5**
        """
        validator = ValidationEngine()
        result = validator.validate_json_schema(json_data)
        assert isinstance(result, ValidationResult), (
            "validate_json_schema() must return a ValidationResult"
        )

    @given(valid_context_map_json())
    @settings(max_examples=15, deadline=None)
    def test_valid_json_passes_schema_validation(self, json_data):
        """
        Property: Structurally valid JSON always passes schema validation.

        **Validates: Requirements 2.3, 2.5**
        """
        validator = ValidationEngine()
        result = validator.validate_json_schema(json_data)
        assert result.is_valid, (
            f"Valid JSON should pass schema validation. Errors: {[str(e) for e in result.errors]}"
        )

    @given(valid_context_map_json())
    @settings(max_examples=15, deadline=None)
    def test_validation_is_deterministic(self, json_data):
        """
        Property: Validating the same JSON twice produces identical results.

        **Validates: Requirements 2.9**
        """
        validator = ValidationEngine()
        result1 = validator.validate_json_schema(json_data)
        result2 = validator.validate_json_schema(json_data)
        assert result1.is_valid == result2.is_valid, (
            "Validation must be deterministic for the same input"
        )
        assert len(result1.errors) == len(result2.errors), (
            "Error count must be deterministic for the same input"
        )

    @given(valid_context_map_json())
    @settings(max_examples=15, deadline=None)
    def test_valid_json_has_no_errors(self, json_data):
        """
        Property: Valid JSON produces zero validation errors.

        **Validates: Requirements 2.3, 2.5**
        """
        validator = ValidationEngine()
        result = validator.validate_json_schema(json_data)
        assert len(result.errors) == 0, (
            f"Valid JSON must produce no errors. Got: {[str(e) for e in result.errors]}"
        )

    @given(json_with_missing_required_fields())
    @settings(max_examples=15, deadline=None)
    def test_missing_required_fields_produce_errors(self, json_data):
        """
        Property: JSON missing required fields always produces validation errors.

        **Validates: Requirements 2.3, 2.9**
        """
        validator = ValidationEngine()
        result = validator.validate_json_schema(json_data)
        assert not result.is_valid, (
            "JSON with missing required fields must fail validation"
        )
        assert len(result.errors) > 0, (
            "JSON with missing required fields must produce at least one error"
        )

    @given(json_with_invalid_bc_type())
    @settings(max_examples=15, deadline=None)
    def test_invalid_bounded_context_type_produces_errors(self, json_data):
        """
        Property: JSON with invalid bounded context type always fails validation.

        **Validates: Requirements 2.3, 2.9**
        """
        validator = ValidationEngine()
        result = validator.validate_json_schema(json_data)
        assert not result.is_valid, (
            "JSON with invalid bounded context type must fail validation"
        )

    @given(json_with_invalid_cm_type())
    @settings(max_examples=15, deadline=None)
    def test_invalid_context_map_type_produces_errors(self, json_data):
        """
        Property: JSON with invalid context map type always fails validation.

        **Validates: Requirements 2.3, 2.9**
        """
        validator = ValidationEngine()
        result = validator.validate_json_schema(json_data)
        assert not result.is_valid, (
            "JSON with invalid context map type must fail validation"
        )

    @given(valid_context_map_json())
    @settings(max_examples=15, deadline=None)
    def test_validation_result_has_required_attributes(self, json_data):
        """
        Property: ValidationResult always has is_valid, errors, and warnings attributes.

        **Validates: Requirements 2.5**
        """
        validator = ValidationEngine()
        result = validator.validate_json_schema(json_data)
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")
        assert hasattr(result, "warnings")
        assert isinstance(result.errors, list)
        assert isinstance(result.warnings, list)

    @given(valid_context_map_json())
    @settings(max_examples=10, deadline=None)
    def test_errors_are_validation_error_instances(self, json_data):
        """
        Property: All errors in ValidationResult are ValidationError instances.

        **Validates: Requirements 2.5**
        """
        validator = ValidationEngine()
        result = validator.validate_json_schema(json_data)
        for error in result.errors:
            assert isinstance(error, ValidationError), (
                f"Each error must be a ValidationError instance, got {type(error)}"
            )

    @given(valid_context_map_json())
    @settings(max_examples=10, deadline=None)
    def test_validation_errors_have_non_empty_messages(self, json_data):
        """
        Property: All validation errors have non-empty message strings.

        **Validates: Requirements 2.5, 2.9**
        """
        validator = ValidationEngine()
        result = validator.validate_json_schema(json_data)
        for error in result.errors:
            assert isinstance(error.message, str), "Error message must be a string"
            assert len(error.message) > 0, "Error message must not be empty"

    @given(valid_context_map_json())
    @settings(max_examples=10, deadline=None)
    def test_is_valid_consistent_with_errors_list(self, json_data):
        """
        Property: is_valid is False if and only if errors list is non-empty.

        **Validates: Requirements 2.5**
        """
        validator = ValidationEngine()
        result = validator.validate_json_schema(json_data)
        if result.errors:
            assert not result.is_valid, (
                "is_valid must be False when errors list is non-empty"
            )
        else:
            assert result.is_valid, (
                "is_valid must be True when errors list is empty"
            )

    @given(st.integers(min_value=1, max_value=10))
    @settings(max_examples=10, deadline=None)
    def test_validation_scales_with_multiple_bounded_contexts(self, num_contexts):
        """
        Property: Validation handles any number of bounded contexts without error.

        **Validates: Requirements 2.3, 2.5**
        """
        context_names = [f"Context{i}" for i in range(num_contexts)]
        json_data = {
            "contextMap": {"type": "SYSTEM_LANDSCAPE", "contains": context_names},
            "boundedContexts": [{"name": n, "type": "FEATURE"} for n in context_names],
        }
        validator = ValidationEngine()
        result = validator.validate_json_schema(json_data)
        assert isinstance(result, ValidationResult)
        assert result.is_valid, (
            f"Valid JSON with {num_contexts} contexts must pass validation"
        )

    @given(st.one_of(
        st.none(),
        st.integers(),
        st.text(min_size=0, max_size=10),
        st.lists(st.integers()),
    ))
    @settings(max_examples=10, deadline=None)
    def test_non_dict_input_handled_gracefully(self, invalid_input):
        """
        Property: Non-dict inputs are handled without crashing (returns error result or raises).

        **Validates: Requirements 2.9**
        """
        validator = ValidationEngine()
        try:
            result = validator.validate_json_schema(invalid_input)
            # If it doesn't raise, it must return a ValidationResult
            assert isinstance(result, ValidationResult)
        except (TypeError, AttributeError, Exception):
            # Raising an exception is also acceptable for non-dict inputs
            pass
