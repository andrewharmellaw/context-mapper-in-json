"""
Comprehensive unit tests for ConverterEngine.

Tests all conversion methods with valid and invalid inputs, covering all DDD patterns
and relationship types.
"""

import pytest

from context_mapper_json_converter.converter import ConverterEngine


@pytest.fixture
def converter():
    return ConverterEngine()


# ---------------------------------------------------------------------------
# Basic instantiation
# ---------------------------------------------------------------------------


class TestConverterEngineInit:
    def test_instantiation(self, converter):
        assert converter is not None

    def test_has_jinja_env(self, converter):
        assert converter.jinja_env is not None

    def test_has_templates(self, converter):
        assert converter.context_map_template is not None
        assert converter.bounded_context_template is not None
        assert converter.aggregate_template is not None


# ---------------------------------------------------------------------------
# convert() – top-level entry point
# ---------------------------------------------------------------------------


class TestConvert:
    def test_convert_simple_context_map(self, converter):
        data = {
            "contextMap": {
                "name": "TestMap",
                "type": "SYSTEM_LANDSCAPE",
                "contains": ["CtxA"],
            },
            "boundedContexts": [{"name": "CtxA", "type": "FEATURE"}],
        }
        result = converter.convert(data)
        assert isinstance(result, str)
        assert "ContextMap" in result
        assert "BoundedContext" in result

    def test_convert_without_context_map(self, converter):
        data = {"boundedContexts": [{"name": "CtxA", "type": "FEATURE"}]}
        result = converter.convert(data)
        assert "BoundedContext CtxA" in result

    def test_convert_without_bounded_contexts(self, converter):
        data = {
            "contextMap": {"type": "SYSTEM_LANDSCAPE", "contains": ["CtxA"]},
        }
        result = converter.convert(data)
        assert "ContextMap" in result

    def test_convert_with_subdomains(self, converter):
        data = {
            "contextMap": {"type": "SYSTEM_LANDSCAPE", "contains": ["CtxA"]},
            "boundedContexts": [{"name": "CtxA", "type": "FEATURE"}],
            "domainName": "MyDomain",
            "subdomains": [{"name": "CoreSub", "type": "CORE_DOMAIN"}],
        }
        result = converter.convert(data)
        assert "Domain MyDomain" in result
        assert "Subdomain CoreSub" in result

    def test_convert_empty_data_returns_empty_string(self, converter):
        result = converter.convert({})
        assert result == ""

    def test_convert_raises_on_invalid_input(self, converter):
        with pytest.raises((ValueError, Exception)):
            converter.convert(None)

    def test_convert_multiple_bounded_contexts(self, converter):
        data = {
            "contextMap": {
                "type": "SYSTEM_LANDSCAPE",
                "contains": ["CtxA", "CtxB"],
            },
            "boundedContexts": [
                {"name": "CtxA", "type": "FEATURE"},
                {"name": "CtxB", "type": "SYSTEM"},
            ],
        }
        result = converter.convert(data)
        assert "BoundedContext CtxA" in result
        assert "BoundedContext CtxB" in result


# ---------------------------------------------------------------------------
# convert_context_map()
# ---------------------------------------------------------------------------


class TestConvertContextMap:
    def test_basic_context_map(self, converter):
        data = {"type": "SYSTEM_LANDSCAPE", "contains": ["A", "B"]}
        result = converter.convert_context_map(data)
        assert "ContextMap" in result
        assert "SYSTEM_LANDSCAPE" in result
        assert "A" in result
        assert "B" in result

    def test_context_map_with_name(self, converter):
        data = {"name": "MyMap", "type": "SYSTEM_LANDSCAPE", "contains": ["A"]}
        result = converter.convert_context_map(data)
        assert "ContextMap MyMap" in result

    def test_context_map_with_state(self, converter):
        data = {"type": "SYSTEM_LANDSCAPE", "state": "AS_IS", "contains": ["A"]}
        result = converter.convert_context_map(data)
        assert "AS_IS" in result

    def test_context_map_organizational_type(self, converter):
        data = {"type": "ORGANIZATIONAL", "contains": ["TeamA"]}
        result = converter.convert_context_map(data)
        assert "ORGANIZATIONAL" in result

    def test_context_map_with_relationships(self, converter):
        data = {
            "type": "SYSTEM_LANDSCAPE",
            "contains": ["A", "B"],
            "relationships": [
                {"type": "Partnership", "upstream": "A", "downstream": "B"}
            ],
        }
        result = converter.convert_context_map(data)
        assert "Partnership" in result

    def test_context_map_contains_joined(self, converter):
        data = {"type": "SYSTEM_LANDSCAPE", "contains": ["X", "Y", "Z"]}
        result = converter.convert_context_map(data)
        assert "X" in result
        assert "Y" in result
        assert "Z" in result


# ---------------------------------------------------------------------------
# convert_bounded_context()
# ---------------------------------------------------------------------------


class TestConvertBoundedContext:
    def test_minimal_bounded_context(self, converter):
        data = {"name": "MyCtx", "type": "FEATURE"}
        result = converter.convert_bounded_context(data)
        assert "BoundedContext MyCtx type = FEATURE" in result

    def test_bounded_context_with_domain_vision(self, converter):
        data = {
            "name": "MyCtx",
            "type": "FEATURE",
            "domainVisionStatement": "Handles orders",
        }
        result = converter.convert_bounded_context(data)
        assert 'domainVisionStatement = "Handles orders"' in result

    def test_bounded_context_with_implementation_technology(self, converter):
        data = {
            "name": "MyCtx",
            "type": "SYSTEM",
            "implementationTechnology": "Java Spring",
        }
        result = converter.convert_bounded_context(data)
        assert 'implementationTechnology = "Java Spring"' in result

    def test_bounded_context_with_knowledge_level(self, converter):
        data = {"name": "MyCtx", "type": "FEATURE", "knowledgeLevel": "CONCRETE"}
        result = converter.convert_bounded_context(data)
        assert "knowledgeLevel = CONCRETE" in result

    def test_bounded_context_with_business_model(self, converter):
        data = {"name": "MyCtx", "type": "FEATURE", "businessModel": "REVENUE"}
        result = converter.convert_bounded_context(data)
        assert "businessModel = REVENUE" in result

    def test_bounded_context_with_evolution(self, converter):
        data = {"name": "MyCtx", "type": "FEATURE", "evolution": "GENESIS"}
        result = converter.convert_bounded_context(data)
        assert "evolution = GENESIS" in result

    def test_bounded_context_with_responsibilities(self, converter):
        data = {
            "name": "MyCtx",
            "type": "FEATURE",
            "responsibilities": ["Order processing", "Billing"],
        }
        result = converter.convert_bounded_context(data)
        assert "responsibilities" in result

    def test_bounded_context_with_realizes(self, converter):
        data = {"name": "TeamCtx", "type": "TEAM", "realizes": "OrderManagement"}
        result = converter.convert_bounded_context(data)
        assert "realizes OrderManagement" in result

    def test_bounded_context_with_aggregates(self, converter):
        data = {
            "name": "MyCtx",
            "type": "FEATURE",
            "aggregates": [{"name": "MyAggregate"}],
        }
        result = converter.convert_bounded_context(data)
        assert "Aggregate MyAggregate" in result

    def test_bounded_context_closes_with_brace(self, converter):
        data = {"name": "MyCtx", "type": "FEATURE"}
        result = converter.convert_bounded_context(data)
        assert result.strip().endswith("}")

    def test_all_bounded_context_types(self, converter):
        for bc_type in ["FEATURE", "APPLICATION", "SYSTEM", "TEAM"]:
            data = {"name": "Ctx", "type": bc_type}
            result = converter.convert_bounded_context(data)
            assert bc_type in result


# ---------------------------------------------------------------------------
# convert_relationships()
# ---------------------------------------------------------------------------


class TestConvertRelationships:
    def test_partnership_relationship(self, converter):
        rels = [{"type": "Partnership", "upstream": "A", "downstream": "B"}]
        result = converter.convert_relationships(rels)
        assert len(result) == 1
        assert "A Partnership B" in result[0]

    def test_shared_kernel_relationship(self, converter):
        rels = [{"type": "SharedKernel", "upstream": "A", "downstream": "B"}]
        result = converter.convert_relationships(rels)
        assert len(result) == 1
        assert "[SK]" in result[0]
        assert "A" in result[0]
        assert "B" in result[0]

    def test_shared_kernel_with_impl_tech(self, converter):
        rels = [
            {
                "type": "SharedKernel",
                "upstream": "A",
                "downstream": "B",
                "implementationTechnology": "REST",
            }
        ]
        result = converter.convert_relationships(rels)
        assert "REST" in result[0]

    def test_customer_supplier_relationship(self, converter):
        rels = [{"type": "CustomerSupplier", "upstream": "A", "downstream": "B"}]
        result = converter.convert_relationships(rels)
        assert len(result) == 1
        assert "A" in result[0]
        assert "B" in result[0]

    def test_customer_supplier_with_roles(self, converter):
        rels = [
            {
                "type": "CustomerSupplier",
                "upstream": "A",
                "downstream": "B",
                "upstreamRoles": ["OHS", "PL"],
                "downstreamRoles": ["ACL"],
            }
        ]
        result = converter.convert_relationships(rels)
        assert "OHS" in result[0]
        assert "PL" in result[0]
        assert "ACL" in result[0]

    def test_customer_supplier_with_impl_tech(self, converter):
        rels = [
            {
                "type": "CustomerSupplier",
                "upstream": "A",
                "downstream": "B",
                "implementationTechnology": "gRPC",
            }
        ]
        result = converter.convert_relationships(rels)
        assert "gRPC" in result[0]

    def test_customer_supplier_with_exposed_aggregates(self, converter):
        rels = [
            {
                "type": "CustomerSupplier",
                "upstream": "A",
                "downstream": "B",
                "exposedAggregates": ["OrderAggregate"],
            }
        ]
        result = converter.convert_relationships(rels)
        assert "OrderAggregate" in result[0]

    def test_upstream_downstream_relationship(self, converter):
        rels = [{"type": "UpstreamDownstream", "upstream": "A", "downstream": "B"}]
        result = converter.convert_relationships(rels)
        assert len(result) == 1
        assert "A" in result[0]
        assert "B" in result[0]

    def test_upstream_downstream_with_roles(self, converter):
        rels = [
            {
                "type": "UpstreamDownstream",
                "upstream": "A",
                "downstream": "B",
                "upstreamRoles": ["OHS"],
                "downstreamRoles": ["CF"],
            }
        ]
        result = converter.convert_relationships(rels)
        assert "OHS" in result[0]
        assert "CF" in result[0]

    def test_multiple_relationships(self, converter):
        rels = [
            {"type": "Partnership", "upstream": "A", "downstream": "B"},
            {"type": "SharedKernel", "upstream": "C", "downstream": "D"},
        ]
        result = converter.convert_relationships(rels)
        assert len(result) == 2

    def test_empty_relationships(self, converter):
        result = converter.convert_relationships([])
        assert result == []

    def test_unknown_relationship_type_fallback(self, converter):
        rels = [{"type": "Unknown", "upstream": "A", "downstream": "B"}]
        result = converter.convert_relationships(rels)
        assert len(result) == 1
        assert "A" in result[0]
        assert "B" in result[0]


# ---------------------------------------------------------------------------
# convert_subdomains()
# ---------------------------------------------------------------------------


class TestConvertSubdomains:
    def test_basic_subdomain(self, converter):
        subdomains = [{"name": "CoreSub", "type": "CORE_DOMAIN"}]
        result = converter.convert_subdomains(subdomains, "MyDomain")
        assert "Domain MyDomain" in result
        assert "Subdomain CoreSub" in result
        assert "CORE_DOMAIN" in result

    def test_subdomain_with_vision_statement(self, converter):
        subdomains = [
            {
                "name": "CoreSub",
                "type": "CORE_DOMAIN",
                "domainVisionStatement": "Core business",
            }
        ]
        result = converter.convert_subdomains(subdomains, "MyDomain")
        assert "Core business" in result

    def test_multiple_subdomains(self, converter):
        subdomains = [
            {"name": "CoreSub", "type": "CORE_DOMAIN"},
            {"name": "SupportSub", "type": "SUPPORTING_DOMAIN"},
        ]
        result = converter.convert_subdomains(subdomains, "MyDomain")
        assert "CoreSub" in result
        assert "SupportSub" in result

    def test_default_domain_name(self, converter):
        subdomains = [{"name": "Sub", "type": "GENERIC_SUBDOMAIN"}]
        result = converter.convert_subdomains(subdomains)
        assert "DefaultDomain" in result

    def test_subdomain_with_entities(self, converter):
        subdomains = [
            {"name": "Sub", "type": "CORE_DOMAIN", "entities": ["Order", "Customer"]}
        ]
        result = converter.convert_subdomains(subdomains, "D")
        assert "Order" in result
        assert "Customer" in result


# ---------------------------------------------------------------------------
# convert_aggregate()
# ---------------------------------------------------------------------------


class TestConvertAggregate:
    def test_minimal_aggregate(self, converter):
        data = {"name": "MyAggregate"}
        result = converter.convert_aggregate(data)
        assert "Aggregate MyAggregate" in result
        assert result.strip().endswith("}")

    def test_aggregate_with_owner(self, converter):
        data = {"name": "MyAggregate", "owner": "TeamA"}
        result = converter.convert_aggregate(data)
        assert "owned by TeamA" in result

    def test_aggregate_with_knowledge_level(self, converter):
        data = {"name": "MyAggregate", "knowledgeLevel": "CONCRETE"}
        result = converter.convert_aggregate(data)
        assert "knowledgeLevel = CONCRETE" in result

    def test_aggregate_with_likelihood_for_change(self, converter):
        data = {"name": "MyAggregate", "likelihoodForChange": "OFTEN"}
        result = converter.convert_aggregate(data)
        assert "likelihoodForChange = OFTEN" in result

    def test_aggregate_with_entities(self, converter):
        data = {
            "name": "MyAggregate",
            "entities": [{"name": "MyEntity", "aggregateRoot": True}],
        }
        result = converter.convert_aggregate(data)
        assert "Entity MyEntity" in result

    def test_aggregate_with_value_objects(self, converter):
        data = {
            "name": "MyAggregate",
            "valueObjects": [{"name": "MyVO"}],
        }
        result = converter.convert_aggregate(data)
        assert "ValueObject MyVO" in result

    def test_aggregate_with_domain_events(self, converter):
        data = {
            "name": "MyAggregate",
            "domainEvents": [{"name": "OrderPlaced"}],
        }
        result = converter.convert_aggregate(data)
        assert "DomainEvent OrderPlaced" in result

    def test_aggregate_with_commands(self, converter):
        data = {
            "name": "MyAggregate",
            "commands": [{"name": "PlaceOrder"}],
        }
        result = converter.convert_aggregate(data)
        assert "Command PlaceOrder" in result

    def test_aggregate_with_services(self, converter):
        data = {
            "name": "MyAggregate",
            "services": [{"name": "OrderService"}],
        }
        result = converter.convert_aggregate(data)
        assert "Service OrderService" in result

    def test_aggregate_with_repositories(self, converter):
        data = {
            "name": "MyAggregate",
            "repositories": [{"name": "OrderRepository"}],
        }
        result = converter.convert_aggregate(data)
        assert "Repository OrderRepository" in result


# ---------------------------------------------------------------------------
# convert_entity()
# ---------------------------------------------------------------------------


class TestConvertEntity:
    def test_minimal_entity(self, converter):
        data = {"name": "MyEntity"}
        result = converter.convert_entity(data)
        assert "Entity MyEntity {" in result
        assert result.strip().endswith("}")

    def test_aggregate_root_entity(self, converter):
        data = {"name": "MyEntity", "aggregateRoot": True}
        result = converter.convert_entity(data)
        assert "aggregateRoot" in result

    def test_non_aggregate_root_entity(self, converter):
        data = {"name": "MyEntity", "aggregateRoot": False}
        result = converter.convert_entity(data)
        assert "aggregateRoot" not in result

    def test_entity_with_attributes(self, converter):
        data = {
            "name": "MyEntity",
            "attributes": [{"name": "id", "type": "String", "key": True}],
        }
        result = converter.convert_entity(data)
        assert "String id" in result
        assert "key" in result

    def test_entity_with_operations(self, converter):
        data = {
            "name": "MyEntity",
            "operations": [{"name": "doSomething", "returnType": "void"}],
        }
        result = converter.convert_entity(data)
        assert "doSomething" in result

    def test_entity_with_nullable_attribute(self, converter):
        data = {
            "name": "MyEntity",
            "attributes": [{"name": "desc", "type": "String", "nullable": True}],
        }
        result = converter.convert_entity(data)
        assert "nullable" in result


# ---------------------------------------------------------------------------
# convert_value_object()
# ---------------------------------------------------------------------------


class TestConvertValueObject:
    def test_minimal_value_object(self, converter):
        data = {"name": "MyVO"}
        result = converter.convert_value_object(data)
        assert "ValueObject MyVO {" in result
        assert result.strip().endswith("}")

    def test_value_object_with_attributes(self, converter):
        data = {
            "name": "Money",
            "attributes": [
                {"name": "amount", "type": "BigDecimal"},
                {"name": "currency", "type": "String"},
            ],
        }
        result = converter.convert_value_object(data)
        assert "BigDecimal amount" in result
        assert "String currency" in result

    def test_value_object_with_operations(self, converter):
        data = {
            "name": "Money",
            "operations": [{"name": "add", "returnType": "Money"}],
        }
        result = converter.convert_value_object(data)
        assert "add" in result


# ---------------------------------------------------------------------------
# convert_domain_event()
# ---------------------------------------------------------------------------


class TestConvertDomainEvent:
    def test_minimal_domain_event(self, converter):
        data = {"name": "OrderPlaced"}
        result = converter.convert_domain_event(data)
        assert "DomainEvent OrderPlaced {" in result
        assert result.strip().endswith("}")

    def test_domain_event_with_attributes(self, converter):
        data = {
            "name": "OrderPlaced",
            "attributes": [{"name": "orderId", "type": "OrderId"}],
        }
        result = converter.convert_domain_event(data)
        assert "OrderId orderId" in result


# ---------------------------------------------------------------------------
# convert_command()
# ---------------------------------------------------------------------------


class TestConvertCommand:
    def test_minimal_command(self, converter):
        data = {"name": "PlaceOrder"}
        result = converter.convert_command(data)
        assert "Command PlaceOrder {" in result
        assert result.strip().endswith("}")

    def test_command_with_attributes(self, converter):
        data = {
            "name": "PlaceOrder",
            "attributes": [{"name": "customerId", "type": "CustomerId"}],
        }
        result = converter.convert_command(data)
        assert "CustomerId customerId" in result


# ---------------------------------------------------------------------------
# convert_service()
# ---------------------------------------------------------------------------


class TestConvertService:
    def test_minimal_service(self, converter):
        data = {"name": "OrderService"}
        result = converter.convert_service(data)
        assert "Service OrderService {" in result
        assert result.strip().endswith("}")

    def test_service_with_operations(self, converter):
        data = {
            "name": "OrderService",
            "operations": [{"name": "processOrder", "returnType": "OrderId"}],
        }
        result = converter.convert_service(data)
        assert "processOrder" in result
        assert "OrderId" in result


# ---------------------------------------------------------------------------
# convert_repository()
# ---------------------------------------------------------------------------


class TestConvertRepository:
    def test_minimal_repository(self, converter):
        data = {"name": "OrderRepository"}
        result = converter.convert_repository(data)
        assert "Repository OrderRepository {" in result
        assert result.strip().endswith("}")

    def test_repository_with_operations(self, converter):
        data = {
            "name": "OrderRepository",
            "operations": [{"name": "findById", "returnType": "Order"}],
        }
        result = converter.convert_repository(data)
        assert "findById" in result
        assert "Order" in result


# ---------------------------------------------------------------------------
# convert_attribute()
# ---------------------------------------------------------------------------


class TestConvertAttribute:
    def test_basic_attribute(self, converter):
        data = {"name": "orderId", "type": "String"}
        result = converter.convert_attribute(data)
        assert "String orderId" in result

    def test_key_attribute(self, converter):
        data = {"name": "id", "type": "Long", "key": True}
        result = converter.convert_attribute(data)
        assert "key" in result

    def test_nullable_attribute(self, converter):
        data = {"name": "desc", "type": "String", "nullable": True}
        result = converter.convert_attribute(data)
        assert "nullable" in result

    def test_key_and_nullable_attribute(self, converter):
        data = {"name": "id", "type": "Long", "key": True, "nullable": True}
        result = converter.convert_attribute(data)
        assert "key" in result
        assert "nullable" in result

    def test_non_key_non_nullable_attribute(self, converter):
        data = {"name": "name", "type": "String", "key": False, "nullable": False}
        result = converter.convert_attribute(data)
        assert "key" not in result
        assert "nullable" not in result


# ---------------------------------------------------------------------------
# convert_operation()
# ---------------------------------------------------------------------------


class TestConvertOperation:
    def test_basic_operation(self, converter):
        data = {"name": "doSomething"}
        result = converter.convert_operation(data)
        assert "doSomething" in result

    def test_operation_with_return_type(self, converter):
        data = {"name": "getOrder", "returnType": "Order"}
        result = converter.convert_operation(data)
        assert "Order getOrder" in result

    def test_operation_with_parameters(self, converter):
        data = {
            "name": "findById",
            "parameters": [{"name": "id", "type": "Long"}],
            "returnType": "Order",
        }
        result = converter.convert_operation(data)
        assert "Long id" in result

    def test_operation_with_multiple_parameters(self, converter):
        data = {
            "name": "search",
            "parameters": [
                {"name": "query", "type": "String"},
                {"name": "limit", "type": "Integer"},
            ],
            "returnType": "List",
        }
        result = converter.convert_operation(data)
        assert "String query" in result
        assert "Integer limit" in result

    def test_operation_with_private_visibility(self, converter):
        data = {"name": "helper", "visibility": "PRIVATE", "returnType": "void"}
        result = converter.convert_operation(data)
        assert "private" in result

    def test_operation_with_protected_visibility(self, converter):
        data = {"name": "helper", "visibility": "PROTECTED", "returnType": "void"}
        result = converter.convert_operation(data)
        assert "protected" in result

    def test_operation_public_visibility_not_prefixed(self, converter):
        data = {"name": "doIt", "visibility": "PUBLIC", "returnType": "void"}
        result = converter.convert_operation(data)
        # PUBLIC visibility should not add a prefix
        assert "public" not in result

    def test_operation_no_return_type_defaults_void(self, converter):
        data = {"name": "doIt"}
        result = converter.convert_operation(data)
        assert "void" in result


# ---------------------------------------------------------------------------
# End-to-end fixture-based tests
# ---------------------------------------------------------------------------


class TestConverterWithFixtures:
    def test_convert_aggregates_entities_fixture(self, converter, load_test_json):
        data = load_test_json("aggregates-entities.json")
        result = converter.convert(data)
        assert "Aggregate Order" in result
        assert "Entity Order" in result

    def test_convert_value_objects_fixture(self, converter, load_test_json):
        data = load_test_json("value-objects.json")
        result = converter.convert(data)
        assert "ValueObject" in result

    def test_convert_domain_events_fixture(self, converter, load_test_json):
        data = load_test_json("domain-events.json")
        result = converter.convert(data)
        assert "DomainEvent" in result

    def test_convert_partnership_fixture(self, converter, load_test_json):
        data = load_test_json("partnership.json")
        result = converter.convert(data)
        assert "Partnership" in result

    def test_convert_customer_supplier_fixture(self, converter, load_test_json):
        data = load_test_json("customer-supplier.json")
        result = converter.convert(data)
        assert "[" in result  # roles notation

    def test_convert_shared_kernel_fixture(self, converter, load_test_json):
        data = load_test_json("shared-kernel.json")
        result = converter.convert(data)
        assert "[SK]" in result

    def test_convert_upstream_downstream_fixture(self, converter, load_test_json):
        data = load_test_json("upstream-downstream.json")
        result = converter.convert(data)
        assert "->" in result

    def test_convert_subdomains_fixture(self, converter, load_test_json):
        data = load_test_json("subdomains.json")
        result = converter.convert(data)
        assert "Subdomain" in result

    def test_convert_simple_context_map_fixture(self, converter, load_test_json):
        data = load_test_json("simple-context-map.json")
        result = converter.convert(data)
        assert "ContextMap" in result

    def test_convert_system_landscape_fixture(self, converter, load_test_json):
        data = load_test_json("system-landscape.json")
        result = converter.convert(data)
        assert "SYSTEM_LANDSCAPE" in result

    def test_convert_bounded_contexts_fixture(self, converter, load_test_json):
        data = load_test_json("bounded-contexts.json")
        result = converter.convert(data)
        assert "BoundedContext" in result
