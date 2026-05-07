"""
Comprehensive unit tests for schema modules.

Tests BoundedContext, ContextMap, and Subdomain schema definitions,
their structure, validation rules, and semantic constraints.
"""

import pytest
from jsonschema import Draft7Validator
from jsonschema import ValidationError as JsonSchemaValidationError

from context_mapper_json_converter.schemas.bounded_context import (
    BOUNDED_CONTEXT_SCHEMA,
    BOUNDED_CONTEXT_SEMANTIC_RULES,
)
from context_mapper_json_converter.schemas.context_map import (
    CONTEXT_MAP_SCHEMA,
    CONTEXT_MAP_SEMANTIC_RULES,
)
from context_mapper_json_converter.schemas.subdomain import (
    SUBDOMAIN_SCHEMA,
    SUBDOMAIN_SEMANTIC_RULES,
)

# ---------------------------------------------------------------------------
# ContextMap Schema
# ---------------------------------------------------------------------------

class TestContextMapSchema:
    @pytest.fixture
    def validator(self):
        return Draft7Validator(CONTEXT_MAP_SCHEMA)

    def test_schema_is_dict(self):
        assert isinstance(CONTEXT_MAP_SCHEMA, dict)

    def test_schema_has_title(self):
        assert "title" in CONTEXT_MAP_SCHEMA

    def test_schema_has_type_object(self):
        assert CONTEXT_MAP_SCHEMA.get("type") == "object"

    def test_schema_has_required_fields(self):
        assert "required" in CONTEXT_MAP_SCHEMA
        assert "type" in CONTEXT_MAP_SCHEMA["required"]
        assert "contains" in CONTEXT_MAP_SCHEMA["required"]

    def test_schema_has_properties(self):
        assert "properties" in CONTEXT_MAP_SCHEMA
        props = CONTEXT_MAP_SCHEMA["properties"]
        assert "name" in props
        assert "type" in props
        assert "state" in props
        assert "contains" in props
        assert "relationships" in props

    def test_valid_minimal_context_map(self, validator):
        data = {"type": "SYSTEM_LANDSCAPE", "contains": ["A"]}
        validator.validate(data)  # Should not raise

    def test_valid_full_context_map(self, validator):
        data = {
            "name": "MyMap",
            "type": "SYSTEM_LANDSCAPE",
            "state": "AS_IS",
            "contains": ["A", "B"],
            "relationships": [{"type": "Partnership", "upstream": "A", "downstream": "B"}],
        }
        validator.validate(data)  # Should not raise

    def test_invalid_missing_type(self, validator):
        with pytest.raises(JsonSchemaValidationError):
            validator.validate({"contains": ["A"]})

    def test_invalid_missing_contains(self, validator):
        with pytest.raises(JsonSchemaValidationError):
            validator.validate({"type": "SYSTEM_LANDSCAPE"})

    def test_invalid_context_map_type(self, validator):
        with pytest.raises(JsonSchemaValidationError):
            validator.validate({"type": "INVALID", "contains": ["A"]})

    def test_invalid_state_value(self, validator):
        with pytest.raises(JsonSchemaValidationError):
            validator.validate({"type": "SYSTEM_LANDSCAPE", "state": "INVALID", "contains": ["A"]})

    def test_valid_organizational_type(self, validator):
        data = {"type": "ORGANIZATIONAL", "contains": ["TeamA"]}
        validator.validate(data)  # Should not raise

    def test_valid_to_be_state(self, validator):
        data = {"type": "SYSTEM_LANDSCAPE", "state": "TO_BE", "contains": ["A"]}
        validator.validate(data)  # Should not raise

    def test_invalid_additional_property(self, validator):
        with pytest.raises(JsonSchemaValidationError):
            validator.validate({"type": "SYSTEM_LANDSCAPE", "contains": ["A"], "extra": "value"})

    def test_contains_must_be_array(self, validator):
        with pytest.raises(JsonSchemaValidationError):
            validator.validate({"type": "SYSTEM_LANDSCAPE", "contains": "A"})

    def test_contains_must_have_min_one_item(self, validator):
        with pytest.raises(JsonSchemaValidationError):
            validator.validate({"type": "SYSTEM_LANDSCAPE", "contains": []})

    def test_contains_items_must_be_strings(self, validator):
        with pytest.raises(JsonSchemaValidationError):
            validator.validate({"type": "SYSTEM_LANDSCAPE", "contains": [123]})

    def test_valid_relationship_types(self, validator):
        for rel_type in ["Partnership", "SharedKernel", "CustomerSupplier", "UpstreamDownstream"]:
            data = {
                "type": "SYSTEM_LANDSCAPE",
                "contains": ["A", "B"],
                "relationships": [{"type": rel_type, "upstream": "A", "downstream": "B"}],
            }
            validator.validate(data)  # Should not raise

    def test_invalid_relationship_type(self, validator):
        with pytest.raises(JsonSchemaValidationError):
            validator.validate({
                "type": "SYSTEM_LANDSCAPE",
                "contains": ["A", "B"],
                "relationships": [{"type": "INVALID", "upstream": "A", "downstream": "B"}],
            })

    def test_relationship_missing_upstream(self, validator):
        with pytest.raises(JsonSchemaValidationError):
            validator.validate({
                "type": "SYSTEM_LANDSCAPE",
                "contains": ["A", "B"],
                "relationships": [{"type": "Partnership", "downstream": "B"}],
            })

    def test_relationship_missing_downstream(self, validator):
        with pytest.raises(JsonSchemaValidationError):
            validator.validate({
                "type": "SYSTEM_LANDSCAPE",
                "contains": ["A", "B"],
                "relationships": [{"type": "Partnership", "upstream": "A"}],
            })

    def test_valid_upstream_roles(self, validator):
        data = {
            "type": "SYSTEM_LANDSCAPE",
            "contains": ["A", "B"],
            "relationships": [{
                "type": "CustomerSupplier",
                "upstream": "A",
                "downstream": "B",
                "upstreamRoles": ["OHS", "PL"],
            }],
        }
        validator.validate(data)  # Should not raise

    def test_invalid_upstream_role(self, validator):
        with pytest.raises(JsonSchemaValidationError):
            validator.validate({
                "type": "SYSTEM_LANDSCAPE",
                "contains": ["A", "B"],
                "relationships": [{
                    "type": "CustomerSupplier",
                    "upstream": "A",
                    "downstream": "B",
                    "upstreamRoles": ["INVALID"],
                }],
            })

    def test_valid_downstream_roles(self, validator):
        data = {
            "type": "SYSTEM_LANDSCAPE",
            "contains": ["A", "B"],
            "relationships": [{
                "type": "CustomerSupplier",
                "upstream": "A",
                "downstream": "B",
                "downstreamRoles": ["ACL", "CF"],
            }],
        }
        validator.validate(data)  # Should not raise

    def test_invalid_downstream_role(self, validator):
        with pytest.raises(JsonSchemaValidationError):
            validator.validate({
                "type": "SYSTEM_LANDSCAPE",
                "contains": ["A", "B"],
                "relationships": [{
                    "type": "CustomerSupplier",
                    "upstream": "A",
                    "downstream": "B",
                    "downstreamRoles": ["INVALID"],
                }],
            })

    def test_name_pattern_valid(self, validator):
        data = {"name": "ValidName123", "type": "SYSTEM_LANDSCAPE", "contains": ["A"]}
        validator.validate(data)  # Should not raise

    def test_name_pattern_invalid_starts_with_number(self, validator):
        with pytest.raises(JsonSchemaValidationError):
            validator.validate({"name": "1Invalid", "type": "SYSTEM_LANDSCAPE", "contains": ["A"]})


class TestContextMapSemanticRules:
    def test_semantic_rules_is_dict(self):
        assert isinstance(CONTEXT_MAP_SEMANTIC_RULES, dict)

    def test_has_unique_context_names_rule(self):
        assert "unique_context_names" in CONTEXT_MAP_SEMANTIC_RULES

    def test_has_valid_relationship_participants_rule(self):
        assert "valid_relationship_participants" in CONTEXT_MAP_SEMANTIC_RULES

    def test_has_no_self_relationships_rule(self):
        assert "no_self_relationships" in CONTEXT_MAP_SEMANTIC_RULES

    def test_rules_are_strings(self):
        for key, value in CONTEXT_MAP_SEMANTIC_RULES.items():
            assert isinstance(value, str), f"Rule {key} should be a string"


# ---------------------------------------------------------------------------
# BoundedContext Schema
# ---------------------------------------------------------------------------

class TestBoundedContextSchema:
    @pytest.fixture
    def validator(self):
        return Draft7Validator(BOUNDED_CONTEXT_SCHEMA)

    def test_schema_is_dict(self):
        assert isinstance(BOUNDED_CONTEXT_SCHEMA, dict)

    def test_schema_has_required_fields(self):
        assert "required" in BOUNDED_CONTEXT_SCHEMA
        assert "name" in BOUNDED_CONTEXT_SCHEMA["required"]
        assert "type" in BOUNDED_CONTEXT_SCHEMA["required"]

    def test_schema_has_properties(self):
        props = BOUNDED_CONTEXT_SCHEMA["properties"]
        assert "name" in props
        assert "type" in props
        assert "aggregates" in props
        assert "domainVisionStatement" in props
        assert "implementationTechnology" in props
        assert "responsibilities" in props
        assert "knowledgeLevel" in props
        assert "businessModel" in props
        assert "evolution" in props

    def test_valid_minimal_bounded_context(self, validator):
        validator.validate({"name": "MyCtx", "type": "FEATURE"})

    def test_valid_all_types(self, validator):
        for bc_type in ["FEATURE", "APPLICATION", "SYSTEM", "TEAM"]:
            validator.validate({"name": "Ctx", "type": bc_type})

    def test_invalid_missing_name(self, validator):
        with pytest.raises(JsonSchemaValidationError):
            validator.validate({"type": "FEATURE"})

    def test_invalid_missing_type(self, validator):
        with pytest.raises(JsonSchemaValidationError):
            validator.validate({"name": "MyCtx"})

    def test_invalid_type_value(self, validator):
        with pytest.raises(JsonSchemaValidationError):
            validator.validate({"name": "MyCtx", "type": "INVALID"})

    def test_invalid_additional_property(self, validator):
        with pytest.raises(JsonSchemaValidationError):
            validator.validate({"name": "MyCtx", "type": "FEATURE", "extra": "value"})

    def test_valid_knowledge_levels(self, validator):
        for level in ["CONCRETE", "META"]:
            validator.validate({"name": "Ctx", "type": "FEATURE", "knowledgeLevel": level})

    def test_invalid_knowledge_level(self, validator):
        with pytest.raises(JsonSchemaValidationError):
            validator.validate({"name": "Ctx", "type": "FEATURE", "knowledgeLevel": "INVALID"})

    def test_valid_business_models(self, validator):
        for model in ["REVENUE", "ENGAGEMENT", "COMPLIANCE", "COST_REDUCTION"]:
            validator.validate({"name": "Ctx", "type": "FEATURE", "businessModel": model})

    def test_invalid_business_model(self, validator):
        with pytest.raises(JsonSchemaValidationError):
            validator.validate({"name": "Ctx", "type": "FEATURE", "businessModel": "INVALID"})

    def test_valid_evolution_stages(self, validator):
        for stage in ["GENESIS", "CUSTOM_BUILT", "PRODUCT", "COMMODITY"]:
            validator.validate({"name": "Ctx", "type": "FEATURE", "evolution": stage})

    def test_invalid_evolution_stage(self, validator):
        with pytest.raises(JsonSchemaValidationError):
            validator.validate({"name": "Ctx", "type": "FEATURE", "evolution": "INVALID"})

    def test_valid_with_aggregate(self, validator):
        data = {
            "name": "Ctx",
            "type": "FEATURE",
            "aggregates": [{"name": "MyAgg"}],
        }
        validator.validate(data)

    def test_valid_aggregate_with_entity(self, validator):
        data = {
            "name": "Ctx",
            "type": "FEATURE",
            "aggregates": [{
                "name": "MyAgg",
                "entities": [{"name": "MyEntity", "aggregateRoot": True}],
            }],
        }
        validator.validate(data)

    def test_valid_aggregate_with_value_object(self, validator):
        data = {
            "name": "Ctx",
            "type": "FEATURE",
            "aggregates": [{
                "name": "MyAgg",
                "valueObjects": [{"name": "MyVO"}],
            }],
        }
        validator.validate(data)

    def test_valid_aggregate_with_domain_event(self, validator):
        data = {
            "name": "Ctx",
            "type": "FEATURE",
            "aggregates": [{
                "name": "MyAgg",
                "domainEvents": [{"name": "OrderPlaced"}],
            }],
        }
        validator.validate(data)

    def test_valid_aggregate_with_command(self, validator):
        data = {
            "name": "Ctx",
            "type": "FEATURE",
            "aggregates": [{
                "name": "MyAgg",
                "commands": [{"name": "PlaceOrder"}],
            }],
        }
        validator.validate(data)

    def test_valid_aggregate_with_service(self, validator):
        data = {
            "name": "Ctx",
            "type": "FEATURE",
            "aggregates": [{
                "name": "MyAgg",
                "services": [{"name": "OrderService"}],
            }],
        }
        validator.validate(data)

    def test_valid_aggregate_with_repository(self, validator):
        data = {
            "name": "Ctx",
            "type": "FEATURE",
            "aggregates": [{
                "name": "MyAgg",
                "repositories": [{"name": "OrderRepo"}],
            }],
        }
        validator.validate(data)

    def test_valid_attribute_with_key(self, validator):
        data = {
            "name": "Ctx",
            "type": "FEATURE",
            "aggregates": [{
                "name": "Agg",
                "entities": [{
                    "name": "E",
                    "attributes": [{"name": "id", "type": "String", "key": True}],
                }],
            }],
        }
        validator.validate(data)

    def test_valid_attribute_nullable(self, validator):
        data = {
            "name": "Ctx",
            "type": "FEATURE",
            "aggregates": [{
                "name": "Agg",
                "entities": [{
                    "name": "E",
                    "attributes": [{"name": "desc", "type": "String", "nullable": True}],
                }],
            }],
        }
        validator.validate(data)

    def test_valid_operation_with_parameters(self, validator):
        data = {
            "name": "Ctx",
            "type": "FEATURE",
            "aggregates": [{
                "name": "Agg",
                "entities": [{
                    "name": "E",
                    "operations": [{
                        "name": "doIt",
                        "parameters": [{"name": "p", "type": "String"}],
                        "returnType": "void",
                        "visibility": "PUBLIC",
                    }],
                }],
            }],
        }
        validator.validate(data)

    def test_invalid_operation_visibility(self, validator):
        with pytest.raises(JsonSchemaValidationError):
            validator.validate({
                "name": "Ctx",
                "type": "FEATURE",
                "aggregates": [{
                    "name": "Agg",
                    "entities": [{
                        "name": "E",
                        "operations": [{"name": "doIt", "visibility": "INVALID"}],
                    }],
                }],
            })

    def test_name_must_start_with_letter(self, validator):
        with pytest.raises(JsonSchemaValidationError):
            validator.validate({"name": "1Invalid", "type": "FEATURE"})

    def test_realizes_only_valid_for_team_type(self, validator):
        # TEAM type with realizes should be valid
        validator.validate({"name": "TeamCtx", "type": "TEAM", "realizes": "OrderCtx"})

    def test_non_team_with_realizes_is_invalid(self, validator):
        # Non-TEAM type with realizes should be invalid per allOf constraint
        with pytest.raises(JsonSchemaValidationError):
            validator.validate({"name": "Ctx", "type": "FEATURE", "realizes": "Other"})


class TestBoundedContextSemanticRules:
    def test_semantic_rules_is_dict(self):
        assert isinstance(BOUNDED_CONTEXT_SEMANTIC_RULES, dict)

    def test_has_unique_names_rule(self):
        assert "unique_names" in BOUNDED_CONTEXT_SEMANTIC_RULES

    def test_has_team_realizes_constraint_rule(self):
        assert "team_realizes_constraint" in BOUNDED_CONTEXT_SEMANTIC_RULES

    def test_rules_are_strings(self):
        for key, value in BOUNDED_CONTEXT_SEMANTIC_RULES.items():
            assert isinstance(value, str)


# ---------------------------------------------------------------------------
# Subdomain Schema
# ---------------------------------------------------------------------------

class TestSubdomainSchema:
    @pytest.fixture
    def validator(self):
        return Draft7Validator(SUBDOMAIN_SCHEMA)

    def test_schema_is_dict(self):
        assert isinstance(SUBDOMAIN_SCHEMA, dict)

    def test_schema_has_required_fields(self):
        assert "required" in SUBDOMAIN_SCHEMA
        assert "name" in SUBDOMAIN_SCHEMA["required"]
        assert "type" in SUBDOMAIN_SCHEMA["required"]

    def test_schema_has_properties(self):
        props = SUBDOMAIN_SCHEMA["properties"]
        assert "name" in props
        assert "type" in props
        assert "domainVisionStatement" in props
        assert "entities" in props
        assert "services" in props

    def test_valid_minimal_subdomain(self, validator):
        validator.validate({"name": "CoreSub", "type": "CORE_DOMAIN"})

    def test_valid_all_types(self, validator):
        for sub_type in ["CORE_DOMAIN", "SUPPORTING_DOMAIN", "GENERIC_SUBDOMAIN"]:
            validator.validate({"name": "Sub", "type": sub_type})

    def test_invalid_missing_name(self, validator):
        with pytest.raises(JsonSchemaValidationError):
            validator.validate({"type": "CORE_DOMAIN"})

    def test_invalid_missing_type(self, validator):
        with pytest.raises(JsonSchemaValidationError):
            validator.validate({"name": "Sub"})

    def test_invalid_type_value(self, validator):
        with pytest.raises(JsonSchemaValidationError):
            validator.validate({"name": "Sub", "type": "INVALID"})

    def test_invalid_additional_property(self, validator):
        with pytest.raises(JsonSchemaValidationError):
            validator.validate({"name": "Sub", "type": "CORE_DOMAIN", "extra": "value"})

    def test_valid_with_domain_vision_statement(self, validator):
        validator.validate({
            "name": "Sub",
            "type": "CORE_DOMAIN",
            "domainVisionStatement": "Core business logic",
        })

    def test_valid_with_entities(self, validator):
        validator.validate({
            "name": "Sub",
            "type": "CORE_DOMAIN",
            "entities": ["Order", "Customer"],
        })

    def test_valid_with_services(self, validator):
        validator.validate({
            "name": "Sub",
            "type": "CORE_DOMAIN",
            "services": ["OrderService"],
        })

    def test_entities_must_be_array(self, validator):
        with pytest.raises(JsonSchemaValidationError):
            validator.validate({"name": "Sub", "type": "CORE_DOMAIN", "entities": "Order"})

    def test_entities_items_must_be_strings(self, validator):
        with pytest.raises(JsonSchemaValidationError):
            validator.validate({"name": "Sub", "type": "CORE_DOMAIN", "entities": [123]})

    def test_entities_must_be_unique(self, validator):
        with pytest.raises(JsonSchemaValidationError):
            validator.validate({
                "name": "Sub",
                "type": "CORE_DOMAIN",
                "entities": ["Order", "Order"],  # duplicate
            })

    def test_name_must_start_with_letter(self, validator):
        with pytest.raises(JsonSchemaValidationError):
            validator.validate({"name": "1Sub", "type": "CORE_DOMAIN"})

    def test_name_max_length(self, validator):
        long_name = "A" * 101
        with pytest.raises(JsonSchemaValidationError):
            validator.validate({"name": long_name, "type": "CORE_DOMAIN"})


class TestSubdomainSemanticRules:
    def test_semantic_rules_is_dict(self):
        assert isinstance(SUBDOMAIN_SEMANTIC_RULES, dict)

    def test_has_unique_names_rule(self):
        assert "unique_names" in SUBDOMAIN_SEMANTIC_RULES

    def test_rules_are_strings(self):
        for key, value in SUBDOMAIN_SEMANTIC_RULES.items():
            assert isinstance(value, str)


# ---------------------------------------------------------------------------
# Schema imports from package
# ---------------------------------------------------------------------------

class TestSchemaImports:
    def test_bounded_context_schema_importable(self):
        from context_mapper_json_converter.schemas.bounded_context import (
            BOUNDED_CONTEXT_SCHEMA,
        )
        assert BOUNDED_CONTEXT_SCHEMA is not None

    def test_context_map_schema_importable(self):
        from context_mapper_json_converter.schemas.context_map import CONTEXT_MAP_SCHEMA
        assert CONTEXT_MAP_SCHEMA is not None

    def test_subdomain_schema_importable(self):
        from context_mapper_json_converter.schemas.subdomain import SUBDOMAIN_SCHEMA
        assert SUBDOMAIN_SCHEMA is not None

    def test_schemas_package_importable(self):
        import context_mapper_json_converter.schemas
        assert context_mapper_json_converter.schemas is not None
