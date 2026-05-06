"""
TypedDict definitions for the JSON input structures accepted by the converter.

Using TypedDict instead of Dict[str, Any] gives mypy visibility into the shape
of these dicts without changing runtime behaviour. All optional fields use
total=False so callers only need to supply the keys they have.

The hierarchy mirrors the JSON Schema in schemas/:
  ContextMapperDocument
    └── ContextMapDict          (contextMap)
          └── RelationshipDict  (relationships[])
    └── BoundedContextDict      (boundedContexts[])
          └── AggregateDict     (aggregates[])
                ├── EntityDict
                ├── ValueObjectDict
                ├── DomainEventDict
                ├── CommandDict
                ├── ServiceDict
                └── RepositoryDict
    └── SubdomainDict           (subdomains[])
"""

from typing import List, TypedDict

# ---------------------------------------------------------------------------
# Tactical DDD building blocks
# ---------------------------------------------------------------------------


class AttributeDict(TypedDict, total=False):
    """A single attribute on an Entity, ValueObject, DomainEvent, or Command."""

    name: str  # required
    type: str  # required
    key: bool
    nullable: bool


class ParameterDict(TypedDict, total=False):
    """A parameter in an operation signature."""

    name: str  # required
    type: str  # required


class OperationDict(TypedDict, total=False):
    """An operation (method) on an Entity, ValueObject, Service, or Repository."""

    name: str  # required
    parameters: List[ParameterDict]
    returnType: str
    visibility: str  # "PUBLIC" | "PRIVATE" | "PROTECTED"


class EntityDict(TypedDict, total=False):
    """An Entity inside an Aggregate."""

    name: str  # required
    aggregateRoot: bool
    attributes: List[AttributeDict]
    operations: List[OperationDict]


class ValueObjectDict(TypedDict, total=False):
    """A Value Object inside an Aggregate."""

    name: str  # required
    attributes: List[AttributeDict]
    operations: List[OperationDict]


class DomainEventDict(TypedDict, total=False):
    """A Domain Event published by an Aggregate."""

    name: str  # required
    attributes: List[AttributeDict]


class CommandDict(TypedDict, total=False):
    """A Command handled by an Aggregate."""

    name: str  # required
    attributes: List[AttributeDict]


class ServiceDict(TypedDict, total=False):
    """A Domain Service inside an Aggregate."""

    name: str  # required
    operations: List[OperationDict]


class RepositoryDict(TypedDict, total=False):
    """A Repository for an Aggregate."""

    name: str  # required
    operations: List[OperationDict]


class AggregateDict(TypedDict, total=False):
    """An Aggregate inside a Bounded Context."""

    name: str  # required
    owner: str
    knowledgeLevel: str  # "CONCRETE" | "META"
    likelihoodForChange: str  # "OFTEN" | "NORMAL" | "RARELY"
    entities: List[EntityDict]
    valueObjects: List[ValueObjectDict]
    domainEvents: List[DomainEventDict]
    commands: List[CommandDict]
    services: List[ServiceDict]
    repositories: List[RepositoryDict]


# ---------------------------------------------------------------------------
# Strategic DDD structures
# ---------------------------------------------------------------------------


class RelationshipDict(TypedDict, total=False):
    """A relationship between two Bounded Contexts in a Context Map."""

    type: str  # required — "Partnership" | "SharedKernel" | "CustomerSupplier" | "UpstreamDownstream"
    upstream: str  # required
    downstream: str  # required
    implementationTechnology: str
    upstreamRoles: List[str]
    downstreamRoles: List[str]
    exposedAggregates: List[str]


class ContextMapDict(TypedDict, total=False):
    """The contextMap section of a ContextMapperDocument."""

    type: str  # required — "SYSTEM_LANDSCAPE" | "ORGANIZATIONAL"
    contains: List[str]  # required
    name: str
    state: str  # "AS_IS" | "TO_BE"
    relationships: List[RelationshipDict]


class BoundedContextDict(TypedDict, total=False):
    """A single entry in the boundedContexts array."""

    name: str  # required
    type: str  # required — "FEATURE" | "APPLICATION" | "SYSTEM" | "TEAM"
    implements: List[str]
    realizes: str
    domainVisionStatement: str
    implementationTechnology: str
    responsibilities: List[str]
    knowledgeLevel: str  # "CONCRETE" | "META"
    businessModel: str  # "REVENUE" | "ENGAGEMENT" | "COMPLIANCE" | "COST_REDUCTION"
    evolution: str  # "GENESIS" | "CUSTOM_BUILT" | "PRODUCT" | "COMMODITY"
    aggregates: List[AggregateDict]


class SubdomainDict(TypedDict, total=False):
    """A single entry in the subdomains array."""

    name: str  # required
    type: str  # required — "CORE_DOMAIN" | "SUPPORTING_DOMAIN" | "GENERIC_SUBDOMAIN"
    domainVisionStatement: str
    entities: List[str]
    services: List[str]


# ---------------------------------------------------------------------------
# Top-level document
# ---------------------------------------------------------------------------


class ContextMapperDocument(TypedDict, total=False):
    """The top-level JSON document accepted by the converter.

    Only contextMap and boundedContexts are required for a minimal document;
    all other keys are optional.
    """

    contextMap: ContextMapDict  # required for conversion
    boundedContexts: List[BoundedContextDict]  # required for conversion
    subdomains: List[SubdomainDict]
    domainName: str
