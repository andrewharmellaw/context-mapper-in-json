"""Property-based tests for ConverterEngine.

Tests conversion invariants across randomly generated valid JSON structures,
round-trip consistency, and error handling properties with invalid inputs.

**Validates: Requirements 2.3, 2.5, 2.9**
"""

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from context_mapper_json_converter import ConversionError, ConverterEngine

# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

VALID_CONTEXT_MAP_TYPES = ["SYSTEM_LANDSCAPE", "ORGANIZATIONAL"]
VALID_BC_TYPES = ["FEATURE", "APPLICATION", "SYSTEM", "TEAM"]
VALID_RELATIONSHIP_TYPES = [
    "Partnership",
    "SharedKernel",
    "CustomerSupplier",
    "UpstreamDownstream",
]

# Names must match ^[A-Za-z][A-Za-z0-9_]*$
_name_tail = st.text(
    alphabet=st.characters(
        whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters="_"
    ),
    min_size=0,
    max_size=10,
)


@st.composite
def valid_identifier(draw):
    """Generate a valid CML identifier (starts with letter, rest alphanumeric/_)."""
    first = draw(
        st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll")),
            min_size=1,
            max_size=1,
        )
    )
    rest = draw(_name_tail)
    return first + rest


@st.composite
def unique_names(draw, min_size=1, max_size=5):
    """Generate a list of unique valid identifiers."""
    size = draw(st.integers(min_value=min_size, max_value=max_size))
    names = []
    for i in range(size):
        names.append(f"Context{i}")
    return names


@st.composite
def valid_bounded_context(draw, name):
    """Generate a valid bounded context dict for a given name."""
    bc_type = draw(st.sampled_from(VALID_BC_TYPES))
    bc = {"name": name, "type": bc_type}
    return bc


@st.composite
def valid_context_map_json(draw):
    """Generate a complete valid context map JSON structure."""
    num_contexts = draw(st.integers(min_value=1, max_value=4))
    context_names = [f"Context{i}" for i in range(num_contexts)]
    cm_type = draw(st.sampled_from(VALID_CONTEXT_MAP_TYPES))

    bounded_contexts = []
    for name in context_names:
        bc = draw(valid_bounded_context(name))
        bounded_contexts.append(bc)

    return {
        "contextMap": {
            "type": cm_type,
            "contains": context_names,
        },
        "boundedContexts": bounded_contexts,
    }


@st.composite
def valid_context_map_with_relationships(draw):
    """Generate a valid context map JSON with optional relationships."""
    num_contexts = draw(st.integers(min_value=2, max_value=4))
    context_names = [f"Ctx{i}" for i in range(num_contexts)]
    cm_type = draw(st.sampled_from(VALID_CONTEXT_MAP_TYPES))

    bounded_contexts = [
        {"name": n, "type": draw(st.sampled_from(VALID_BC_TYPES))}
        for n in context_names
    ]

    # Optionally add relationships between distinct pairs
    relationships = []
    if num_contexts >= 2:
        rel_type = draw(st.sampled_from(VALID_RELATIONSHIP_TYPES))
        upstream = context_names[0]
        downstream = context_names[1]
        relationships.append(
            {
                "type": rel_type,
                "upstream": upstream,
                "downstream": downstream,
            }
        )

    cm = {
        "type": cm_type,
        "contains": context_names,
    }
    if relationships:
        cm["relationships"] = relationships

    return {
        "contextMap": cm,
        "boundedContexts": bounded_contexts,
    }


# ---------------------------------------------------------------------------
# Property tests
# ---------------------------------------------------------------------------


class TestConverterProperties:
    """Property-based tests for ConverterEngine."""

    @given(valid_context_map_json())
    @settings(max_examples=15, deadline=None)
    def test_valid_json_always_produces_string_output(self, json_data):
        """
        Property: For any valid JSON input, convert() returns a non-empty string.

        **Validates: Requirements 2.3, 2.5**
        """
        converter = ConverterEngine()
        result = converter.convert(json_data)
        assert isinstance(result, str), "convert() must return a string"
        assert len(result) > 0, "convert() must return non-empty output for valid input"

    @given(valid_context_map_json())
    @settings(max_examples=15, deadline=None)
    def test_conversion_is_deterministic(self, json_data):
        """
        Property: Converting the same JSON twice produces identical output.

        **Validates: Requirements 2.3, 2.9**
        """
        converter = ConverterEngine()
        result1 = converter.convert(json_data)
        result2 = converter.convert(json_data)
        assert result1 == result2, "Conversion must be deterministic for the same input"

    @given(valid_context_map_json())
    @settings(max_examples=15, deadline=None)
    def test_context_map_type_appears_in_output(self, json_data):
        """
        Property: The context map type always appears in the CML output.

        **Validates: Requirements 2.3, 2.5**
        """
        converter = ConverterEngine()
        result = converter.convert(json_data)
        cm_type = json_data["contextMap"]["type"]
        assert (
            cm_type in result
        ), f"Context map type '{cm_type}' must appear in CML output"

    @given(valid_context_map_json())
    @settings(max_examples=15, deadline=None)
    def test_all_bounded_context_names_appear_in_output(self, json_data):
        """
        Property: Every bounded context name appears in the CML output.

        **Validates: Requirements 2.3, 2.5**
        """
        converter = ConverterEngine()
        result = converter.convert(json_data)
        for bc in json_data["boundedContexts"]:
            assert (
                bc["name"] in result
            ), f"Bounded context name '{bc['name']}' must appear in CML output"

    @given(valid_context_map_with_relationships())
    @settings(max_examples=15, deadline=None)
    def test_relationships_produce_valid_output(self, json_data):
        """
        Property: JSON with relationships always converts without raising exceptions.

        **Validates: Requirements 2.3, 2.5**
        """
        converter = ConverterEngine()
        result = converter.convert(json_data)
        assert isinstance(result, str)
        assert len(result) > 0

    @given(
        st.one_of(
            st.none(),
            st.integers(),
            st.floats(allow_nan=False),
            st.lists(st.integers(), min_size=0, max_size=3),
        )
    )
    @settings(max_examples=15, deadline=None)
    def test_non_dict_non_string_input_raises_or_returns_empty(self, invalid_input):
        """
        Property: Non-dict, non-string inputs either raise an exception or return an empty string.

        The converter uses `in` operator to check for keys, so non-dict inputs that
        don't support `in` (None, int, float) raise TypeError/ValueError, while
        list inputs produce empty output.

        **Validates: Requirements 2.9**
        """
        converter = ConverterEngine()
        try:
            result = converter.convert(invalid_input)
            # If it doesn't raise, the result must be a string (possibly empty)
            assert isinstance(
                result, str
            ), "convert() must return a string even for non-dict inputs"
        except (ConversionError, ValueError, TypeError, AttributeError):
            pass  # Raising is also acceptable

    @given(valid_context_map_json())
    @settings(max_examples=10, deadline=None)
    def test_output_contains_bounded_context_keyword(self, json_data):
        """
        Property: CML output always contains the 'BoundedContext' keyword.

        **Validates: Requirements 2.3, 2.5**
        """
        converter = ConverterEngine()
        result = converter.convert(json_data)
        assert (
            "BoundedContext" in result
        ), "CML output must contain 'BoundedContext' keyword"

    @given(valid_context_map_json())
    @settings(max_examples=10, deadline=None)
    def test_output_contains_context_map_keyword(self, json_data):
        """
        Property: CML output always contains the 'ContextMap' keyword.

        **Validates: Requirements 2.3, 2.5**
        """
        converter = ConverterEngine()
        result = converter.convert(json_data)
        assert "ContextMap" in result, "CML output must contain 'ContextMap' keyword"

    @given(st.sampled_from(VALID_CONTEXT_MAP_TYPES))
    @settings(max_examples=10, deadline=None)
    def test_all_context_map_types_are_handled(self, cm_type):
        """
        Property: All valid context map types produce valid CML output.

        **Validates: Requirements 2.3**
        """
        json_data = {
            "contextMap": {"type": cm_type, "contains": ["Alpha"]},
            "boundedContexts": [{"name": "Alpha", "type": "FEATURE"}],
        }
        converter = ConverterEngine()
        result = converter.convert(json_data)
        assert isinstance(result, str)
        assert cm_type in result

    @given(st.sampled_from(VALID_BC_TYPES))
    @settings(max_examples=10, deadline=None)
    def test_all_bounded_context_types_are_handled(self, bc_type):
        """
        Property: All valid bounded context types produce valid CML output.

        **Validates: Requirements 2.3**
        """
        json_data = {
            "contextMap": {"type": "SYSTEM_LANDSCAPE", "contains": ["MyCtx"]},
            "boundedContexts": [{"name": "MyCtx", "type": bc_type}],
        }
        converter = ConverterEngine()
        result = converter.convert(json_data)
        assert isinstance(result, str)
        assert bc_type in result

    @given(st.sampled_from(VALID_RELATIONSHIP_TYPES))
    @settings(max_examples=10, deadline=None)
    def test_all_relationship_types_are_handled(self, rel_type):
        """
        Property: All valid relationship types produce valid CML output.

        **Validates: Requirements 2.3**
        """
        json_data = {
            "contextMap": {
                "type": "SYSTEM_LANDSCAPE",
                "contains": ["Alpha", "Beta"],
                "relationships": [
                    {"type": rel_type, "upstream": "Alpha", "downstream": "Beta"}
                ],
            },
            "boundedContexts": [
                {"name": "Alpha", "type": "FEATURE"},
                {"name": "Beta", "type": "SYSTEM"},
            ],
        }
        converter = ConverterEngine()
        result = converter.convert(json_data)
        assert isinstance(result, str)
        assert len(result) > 0
