"""
Python Converter Engine for Context Mapper JSON Converter

Transforms validated JSON definitions into Context Mapper DSL (CML) code.
"""

import logging
from typing import Any, Callable, Dict, List, Optional

from jinja2 import BaseLoader, Environment, TemplateError, UndefinedError

from .enums import RelationshipType
from .exceptions import ConversionError
from .types import (
    AggregateDict,
    AttributeDict,
    BoundedContextDict,
    CommandDict,
    ContextMapDict,
    ContextMapperDocument,
    DomainEventDict,
    EntityDict,
    OperationDict,
    RelationshipDict,
    RepositoryDict,
    ServiceDict,
    SubdomainDict,
    ValueObjectDict,
)

logger = logging.getLogger(__name__)


class ConverterEngine:
    """
    Converts JSON definitions to Context Mapper DSL (CML) code.

    Uses template-based generation for consistent CML formatting and syntax.
    Supports Context Maps, Bounded Contexts, and basic relationships.
    """

    def __init__(self) -> None:
        """Initialize the converter engine with CML templates."""
        # autoescape=False is intentional: this converter generates CML (a DSL text
        # file), not HTML. Autoescaping would corrupt CML syntax characters like
        # < > { }.  nosec B701
        self.jinja_env = Environment(
            loader=BaseLoader(), autoescape=False
        )  # nosec B701
        self._setup_templates()

    def _setup_templates(self) -> None:
        """Set up Jinja2 templates for CML generation."""

        # Context Map template
        self.context_map_template = self.jinja_env.from_string(
            """
{%- if context_map.name %}ContextMap {{ context_map.name }}{% else %}ContextMap{% endif %} type = {{ context_map.type }}{% if context_map.state %} state = {{ context_map.state }}{% endif %} {
  contains {{ context_map.contains | join(', ') }}
  {%- if relationships %}
  
  {%- for rel in relationships %}
  {{ rel }}
  {%- endfor %}
  {%- endif %}
}""".strip()
        )

        # Subdomain template
        self.subdomain_template = self.jinja_env.from_string(
            """
Domain {{ domain_name }} {
  {%- for subdomain in subdomains %}
  Subdomain {{ subdomain.name }} {
    type = {{ subdomain.type }}
    {%- if subdomain.domainVisionStatement %}
    domainVisionStatement = "{{ subdomain.domainVisionStatement }}"
    {%- endif %}
    {%- if subdomain.entities %}
    entities = {{ subdomain.entities | join(', ') }}
    {%- endif %}
    {%- if subdomain.services %}
    services = {{ subdomain.services | join(', ') }}
    {%- endif %}
  }
  {%- endfor %}
}""".strip()
        )

        # Bounded Context template
        self.bounded_context_template = self.jinja_env.from_string(
            """
BoundedContext {{ context.name }} type = {{ context.type }}{% if context.realizes %} realizes {{ context.realizes }}{% endif %} {
  {%- if context.domainVisionStatement %}
  domainVisionStatement = "{{ context.domainVisionStatement }}"
  {%- endif %}
  {%- if context.implementationTechnology %}
  implementationTechnology = "{{ context.implementationTechnology }}"
  {%- endif %}
  {%- if context.responsibilities %}
  responsibilities = "{{ context.responsibilities | join(', ') }}"
  {%- endif %}
  {%- if context.knowledgeLevel %}
  knowledgeLevel = {{ context.knowledgeLevel }}
  {%- endif %}
  {%- if context.businessModel %}
  businessModel = {{ context.businessModel }}
  {%- endif %}
  {%- if context.evolution %}
  evolution = {{ context.evolution }}
  {%- endif %}
  {%- if context.aggregates %}
  
  {%- for aggregate in context.aggregates %}
  {{ aggregate_content(aggregate) }}
  {%- endfor %}
  {%- endif %}
}""".strip()
        )

        # Aggregate template
        self.aggregate_template = self.jinja_env.from_string(
            """
Aggregate {{ aggregate.name }}{% if aggregate.owner %} owned by {{ aggregate.owner }}{% endif %} {
  {%- if aggregate.knowledgeLevel %}
  knowledgeLevel = {{ aggregate.knowledgeLevel }}
  {%- endif %}
  {%- if aggregate.likelihoodForChange %}
  likelihoodForChange = {{ aggregate.likelihoodForChange }}
  {%- endif %}
  {%- if aggregate.entities %}
  
  {%- for entity in aggregate.entities %}
  {{ entity_content(entity) }}
  {%- endfor %}
  {%- endif %}
  {%- if aggregate.valueObjects %}
  
  {%- for vo in aggregate.valueObjects %}
  {{ value_object_content(vo) }}
  {%- endfor %}
  {%- endif %}
  {%- if aggregate.domainEvents %}
  
  {%- for event in aggregate.domainEvents %}
  {{ domain_event_content(event) }}
  {%- endfor %}
  {%- endif %}
  {%- if aggregate.commands %}
  
  {%- for command in aggregate.commands %}
  {{ command_content(command) }}
  {%- endfor %}
  {%- endif %}
  {%- if aggregate.services %}
  
  {%- for service in aggregate.services %}
  {{ service_content(service) }}
  {%- endfor %}
  {%- endif %}
  {%- if aggregate.repositories %}
  
  {%- for repo in aggregate.repositories %}
  {{ repository_content(repo) }}
  {%- endfor %}
  {%- endif %}
}""".strip()
        )

    def _indent(self, text: str, spaces: int = 2) -> str:
        """Indent every line of *text* by *spaces* spaces."""
        pad = " " * spaces
        return "\n".join(f"{pad}{line}" for line in text.split("\n"))

    def _convert_block(
        self,
        items: list,
        converter_fn: Callable[[Any], str],
        parts: list,
    ) -> None:
        """Convert each item with *converter_fn*, indent it, and append to *parts*."""
        for item in items:
            parts.append(f"\n{self._indent(converter_fn(item))}")

    def convert(self, json_data: ContextMapperDocument) -> str:
        """
        Convert complete JSON definition to CML code.

        Args:
            json_data: Validated JSON data containing contextMap and boundedContexts

        Returns:
            Generated CML code as string

        Raises:
            ConversionError: If required data is missing or invalid
        """
        try:
            cml_parts = []

            # Convert Context Map
            if "contextMap" in json_data:
                context_map_cml = self.convert_context_map(
                    json_data["contextMap"], json_data.get("boundedContexts", [])
                )
                cml_parts.append(context_map_cml)

            # Convert Domains/Subdomains (if present)
            # New unified schema structure: domains array with name and subdomains
            if "domains" in json_data:
                for domain in json_data["domains"]:
                    domain_name = domain.get("name", "DefaultDomain")
                    subdomains = domain.get("subdomains", [])
                    if subdomains:
                        subdomain_cml = self.convert_subdomains(subdomains, domain_name)
                        cml_parts.append(subdomain_cml)
            # Backward compatibility: old structure with subdomains at root
            elif "subdomains" in json_data:
                domain_name = json_data.get("domainName", "DefaultDomain")
                subdomain_cml = self.convert_subdomains(
                    json_data["subdomains"], domain_name
                )
                cml_parts.append(subdomain_cml)

            # Convert Bounded Contexts
            if "boundedContexts" in json_data:
                for context in json_data["boundedContexts"]:
                    context_cml = self.convert_bounded_context(context)
                    cml_parts.append(context_cml)

            # Join all parts with double newlines
            return "\n\n".join(cml_parts)

        except (TemplateError, UndefinedError, KeyError, TypeError) as e:
            logger.error(f"Conversion failed: {e}")
            raise ConversionError(f"Failed to convert JSON to CML: {str(e)}") from e

    def convert_context_map(
        self,
        context_map_data: ContextMapDict,
        bounded_contexts: Optional[List[BoundedContextDict]] = None,
    ) -> str:
        """
        Convert Context Map JSON to CML syntax.

        Args:
            context_map_data: Context Map JSON data
            bounded_contexts: List of Bounded Context data for relationship validation

        Returns:
            CML Context Map definition
        """
        try:
            # Generate relationship strings
            relationships = []
            if "relationships" in context_map_data:
                relationships = self.convert_relationships(
                    context_map_data["relationships"]
                )

            # Render Context Map template
            cml_output = self.context_map_template.render(
                context_map=context_map_data, relationships=relationships
            )

            logger.debug(f"Generated Context Map CML: {cml_output}")
            return cml_output

        except (TemplateError, UndefinedError, KeyError, TypeError) as e:
            logger.error(f"Context Map conversion failed: {e}")
            raise ConversionError(f"Failed to convert Context Map: {str(e)}") from e

    def convert_bounded_context(self, context_data: BoundedContextDict) -> str:
        """
        Convert Bounded Context JSON to CML syntax.

        Args:
            context_data: Bounded Context JSON data

        Returns:
            CML Bounded Context definition
        """
        try:
            # Build the bounded context parts
            bc_parts = []

            # Header
            name = context_data.get("name")
            bc_type = context_data.get("type")
            realizes = context_data.get("realizes")

            header = f"BoundedContext {name} type = {bc_type}"
            if realizes:
                header += f" realizes {realizes}"
            header += " {"

            bc_parts.append(header)

            # Add optional string properties (quoted in CML)
            if "domainVisionStatement" in context_data:
                bc_parts.append(
                    f'  domainVisionStatement = "{context_data["domainVisionStatement"]}"'
                )
            if "implementationTechnology" in context_data:
                bc_parts.append(
                    f'  implementationTechnology = "{context_data["implementationTechnology"]}"'
                )

            # Add optional enum properties (unquoted in CML)
            for prop_name in ("knowledgeLevel", "businessModel", "evolution"):
                value = context_data.get(prop_name)
                if value is not None:
                    bc_parts.append(f"  {prop_name} = {value}")

            # Handle responsibilities (array)
            if "responsibilities" in context_data:
                responsibilities = context_data["responsibilities"]
                if responsibilities:
                    resp_str = ", ".join(responsibilities)
                    bc_parts.append(f'  responsibilities = "{resp_str}"')

            # Add aggregates
            self._convert_block(
                context_data.get("aggregates", []), self.convert_aggregate, bc_parts
            )

            bc_parts.append("}")

            cml_output = "\n".join(bc_parts)
            logger.debug(f"Generated Bounded Context CML: {cml_output}")
            return cml_output

        except (KeyError, TypeError) as e:
            logger.error(f"Bounded Context conversion failed: {e}")
            raise ConversionError(f"Failed to convert Bounded Context: {str(e)}") from e

    def convert_relationships(self, relationships: List[RelationshipDict]) -> List[str]:
        """
        Convert relationship JSON to CML relationship syntax.

        Args:
            relationships: List of relationship JSON data

        Returns:
            List of CML relationship strings
        """
        cml_relationships = []

        for rel in relationships:
            try:
                rel_type = rel.get("type")
                upstream = rel.get("upstream")
                downstream = rel.get("downstream")
                impl_tech = rel.get("implementationTechnology")
                upstream_roles = rel.get("upstreamRoles", [])
                downstream_roles = rel.get("downstreamRoles", [])
                exposed_aggregates = rel.get("exposedAggregates", [])

                if rel_type == RelationshipType.PARTNERSHIP:
                    # Partnership: A Partnership B
                    rel_str = f"{upstream} Partnership {downstream}"

                elif rel_type == RelationshipType.SHARED_KERNEL:
                    # Shared Kernel: A [SK] <-> [SK] B
                    rel_str = f"{upstream} [SK] <-> [SK] {downstream}"
                    if impl_tech:
                        rel_str += f" : {impl_tech}"

                elif rel_type == RelationshipType.CUSTOMER_SUPPLIER:
                    # Customer/Supplier: A [U,OHS,PL]->[D,ACL] B
                    upstream_role_str = (
                        ",".join(upstream_roles) if upstream_roles else "U"
                    )
                    downstream_role_str = (
                        ",".join(downstream_roles) if downstream_roles else "D"
                    )
                    rel_str = f"{upstream} [{upstream_role_str}]->[{downstream_role_str}] {downstream}"

                    if impl_tech:
                        rel_str += f" : {impl_tech}"

                    if exposed_aggregates:
                        rel_str += f" {{ {', '.join(exposed_aggregates)} }}"

                elif rel_type == RelationshipType.UPSTREAM_DOWNSTREAM:
                    # Upstream/Downstream: A [U,OHS,PL]->[D,ACL] B (similar to Customer/Supplier)
                    upstream_role_str = (
                        ",".join(upstream_roles) if upstream_roles else "U"
                    )
                    downstream_role_str = (
                        ",".join(downstream_roles) if downstream_roles else "D"
                    )
                    rel_str = f"{upstream} [{upstream_role_str}]->[{downstream_role_str}] {downstream}"

                    if impl_tech:
                        rel_str += f" : {impl_tech}"

                    if exposed_aggregates:
                        rel_str += f" {{ {', '.join(exposed_aggregates)} }}"

                else:
                    # Fallback for unknown relationship types
                    rel_str = f"{upstream} {rel_type} {downstream}"
                    if impl_tech:
                        rel_str += f" : {impl_tech}"

                cml_relationships.append(rel_str)
                logger.debug(f"Generated relationship: {rel_str}")

            except (KeyError, TypeError) as e:
                logger.warning(f"Failed to convert relationship {rel}: {e}")
                continue

        return cml_relationships

    def convert_subdomains(
        self, subdomains: List[SubdomainDict], domain_name: str = "DefaultDomain"
    ) -> str:
        """
        Convert subdomain JSON to CML Domain syntax.

        Args:
            subdomains: List of subdomain JSON data
            domain_name: Name of the domain containing the subdomains

        Returns:
            CML Domain definition with subdomains
        """
        try:
            # Render Subdomain template
            cml_output = self.subdomain_template.render(
                domain_name=domain_name, subdomains=subdomains
            )

            logger.debug(f"Generated Subdomain CML: {cml_output}")
            return cml_output

        except (TemplateError, UndefinedError, KeyError, TypeError) as e:
            logger.error(f"Subdomain conversion failed: {e}")
            raise ConversionError(f"Failed to convert Subdomains: {str(e)}") from e

    def convert_aggregate(self, aggregate_data: AggregateDict) -> str:
        """
        Convert Aggregate JSON to CML syntax.

        Args:
            aggregate_data: Aggregate JSON data

        Returns:
            CML Aggregate definition
        """
        try:
            # Process nested tactical elements
            aggregate_cml_parts = []

            # Add aggregate header
            name = aggregate_data.get("name")
            owner = aggregate_data.get("owner")
            knowledge_level = aggregate_data.get("knowledgeLevel")
            likelihood_for_change = aggregate_data.get("likelihoodForChange")

            header = f"Aggregate {name}"
            if owner:
                header += f" owned by {owner}"
            header += " {"

            aggregate_cml_parts.append(header)

            # Add aggregate properties
            if knowledge_level:
                aggregate_cml_parts.append(f"  knowledgeLevel = {knowledge_level}")
            if likelihood_for_change:
                aggregate_cml_parts.append(
                    f"  likelihoodForChange = {likelihood_for_change}"
                )

            # Add entities
            self._convert_block(
                aggregate_data.get("entities", []),
                self.convert_entity,
                aggregate_cml_parts,
            )

            # Add value objects
            self._convert_block(
                aggregate_data.get("valueObjects", []),
                self.convert_value_object,
                aggregate_cml_parts,
            )

            # Add domain events
            self._convert_block(
                aggregate_data.get("domainEvents", []),
                self.convert_domain_event,
                aggregate_cml_parts,
            )

            # Add commands
            self._convert_block(
                aggregate_data.get("commands", []),
                self.convert_command,
                aggregate_cml_parts,
            )

            # Add services
            self._convert_block(
                aggregate_data.get("services", []),
                self.convert_service,
                aggregate_cml_parts,
            )

            # Add repositories
            self._convert_block(
                aggregate_data.get("repositories", []),
                self.convert_repository,
                aggregate_cml_parts,
            )

            aggregate_cml_parts.append("}")

            cml_output = "\n".join(aggregate_cml_parts)
            logger.debug(f"Generated Aggregate CML: {cml_output}")
            return cml_output

        except (KeyError, TypeError) as e:
            logger.error(f"Aggregate conversion failed: {e}")
            raise ConversionError(f"Failed to convert Aggregate: {str(e)}") from e

    def convert_entity(self, entity_data: EntityDict) -> str:
        """Convert Entity JSON to CML syntax."""
        try:
            name = entity_data.get("name")
            aggregate_root = entity_data.get("aggregateRoot", False)
            attributes = entity_data.get("attributes", [])
            operations = entity_data.get("operations", [])

            entity_parts = []

            # Entity header
            if aggregate_root:
                entity_parts.append(f"Entity {name} aggregateRoot {{")
            else:
                entity_parts.append(f"Entity {name} {{")

            # Add attributes
            for attr in attributes:
                attr_str = self.convert_attribute(attr)
                entity_parts.append(f"  {attr_str}")

            # Add operations
            for op in operations:
                op_str = self.convert_operation(op)
                entity_parts.append(f"  {op_str}")

            entity_parts.append("}")

            return "\n".join(entity_parts)

        except (KeyError, TypeError) as e:
            logger.error(f"Entity conversion failed: {e}")
            raise ConversionError(f"Failed to convert Entity: {str(e)}") from e

    def convert_value_object(self, vo_data: ValueObjectDict) -> str:
        """Convert Value Object JSON to CML syntax."""
        try:
            name = vo_data.get("name")
            attributes = vo_data.get("attributes", [])
            operations = vo_data.get("operations", [])

            vo_parts = [f"ValueObject {name} {{"]

            # Add attributes
            for attr in attributes:
                attr_str = self.convert_attribute(attr)
                vo_parts.append(f"  {attr_str}")

            # Add operations
            for op in operations:
                op_str = self.convert_operation(op)
                vo_parts.append(f"  {op_str}")

            vo_parts.append("}")

            return "\n".join(vo_parts)

        except (KeyError, TypeError) as e:
            logger.error(f"Value Object conversion failed: {e}")
            raise ConversionError(f"Failed to convert Value Object: {str(e)}") from e

    def convert_domain_event(self, event_data: DomainEventDict) -> str:
        """Convert Domain Event JSON to CML syntax."""
        try:
            name = event_data.get("name")
            attributes = event_data.get("attributes", [])

            event_parts = [f"DomainEvent {name} {{"]

            # Add attributes
            for attr in attributes:
                attr_str = self.convert_attribute(attr)
                event_parts.append(f"  {attr_str}")

            event_parts.append("}")

            return "\n".join(event_parts)

        except (KeyError, TypeError) as e:
            logger.error(f"Domain Event conversion failed: {e}")
            raise ConversionError(f"Failed to convert Domain Event: {str(e)}") from e

    def convert_command(self, command_data: CommandDict) -> str:
        """Convert Command JSON to CML syntax."""
        try:
            name = command_data.get("name")
            attributes = command_data.get("attributes", [])

            command_parts = [f"Command {name} {{"]

            # Add attributes
            for attr in attributes:
                attr_str = self.convert_attribute(attr)
                command_parts.append(f"  {attr_str}")

            command_parts.append("}")

            return "\n".join(command_parts)

        except (KeyError, TypeError) as e:
            logger.error(f"Command conversion failed: {e}")
            raise ConversionError(f"Failed to convert Command: {str(e)}") from e

    def convert_service(self, service_data: ServiceDict) -> str:
        """Convert Service JSON to CML syntax."""
        try:
            name = service_data.get("name")
            operations = service_data.get("operations", [])

            service_parts = [f"Service {name} {{"]

            # Add operations
            for op in operations:
                op_str = self.convert_operation(op)
                service_parts.append(f"  {op_str}")

            service_parts.append("}")

            return "\n".join(service_parts)

        except (KeyError, TypeError) as e:
            logger.error(f"Service conversion failed: {e}")
            raise ConversionError(f"Failed to convert Service: {str(e)}") from e

    def convert_repository(self, repo_data: RepositoryDict) -> str:
        """Convert Repository JSON to CML syntax."""
        try:
            name = repo_data.get("name")
            operations = repo_data.get("operations", [])

            repo_parts = [f"Repository {name} {{"]

            # Add operations
            for op in operations:
                op_str = self.convert_operation(op)
                repo_parts.append(f"  {op_str}")

            repo_parts.append("}")

            return "\n".join(repo_parts)

        except (KeyError, TypeError) as e:
            logger.error(f"Repository conversion failed: {e}")
            raise ConversionError(f"Failed to convert Repository: {str(e)}") from e

    def convert_attribute(self, attr_data: AttributeDict) -> str:
        """Convert Attribute JSON to CML syntax."""
        name = attr_data.get("name")
        attr_type = attr_data.get("type")
        key = attr_data.get("key", False)
        nullable = attr_data.get("nullable", False)

        attr_str = f"{attr_type} {name}"

        if key:
            attr_str += " key"
        if nullable:
            attr_str += " nullable"

        return attr_str

    def convert_operation(self, op_data: OperationDict) -> str:
        """Convert Operation JSON to CML syntax."""
        name = op_data.get("name")
        parameters = op_data.get("parameters", [])
        return_type = op_data.get("returnType")
        visibility = op_data.get("visibility")

        # Build parameter string
        param_strs = []
        for param in parameters:
            param_name = param.get("name")
            param_type = param.get("type")
            param_strs.append(f"{param_type} {param_name}")

        param_str = ", ".join(param_strs)

        # Build operation string
        op_str = ""
        if visibility and visibility != "PUBLIC":
            op_str += f"{visibility.lower()} "

        if return_type:
            op_str += f"{return_type} "
        else:
            op_str += "void "

        op_str += f"{name}({param_str})"

        return op_str
