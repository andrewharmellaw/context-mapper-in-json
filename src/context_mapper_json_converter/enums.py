"""
Enumerations for fixed value sets used across the Context Mapper JSON Converter.

Using enums instead of bare strings eliminates typo bugs, makes valid values
discoverable, and lets mypy catch misuse at type-check time.
"""

from enum import Enum


class RelationshipType(str, Enum):
    """Valid relationship types between Bounded Contexts."""

    PARTNERSHIP = "Partnership"
    SHARED_KERNEL = "SharedKernel"
    CUSTOMER_SUPPLIER = "CustomerSupplier"
    UPSTREAM_DOWNSTREAM = "UpstreamDownstream"


class BoundedContextType(str, Enum):
    """Valid Bounded Context types."""

    FEATURE = "FEATURE"
    APPLICATION = "APPLICATION"
    SYSTEM = "SYSTEM"
    TEAM = "TEAM"


class ContextMapType(str, Enum):
    """Valid Context Map types."""

    SYSTEM_LANDSCAPE = "SYSTEM_LANDSCAPE"
    ORGANIZATIONAL = "ORGANIZATIONAL"


class ContextMapState(str, Enum):
    """Valid Context Map states."""

    AS_IS = "AS_IS"
    TO_BE = "TO_BE"


class KnowledgeLevel(str, Enum):
    """Valid knowledge levels for Bounded Contexts and Aggregates."""

    CONCRETE = "CONCRETE"
    META = "META"


class BusinessModel(str, Enum):
    """Valid business model drivers for Bounded Contexts."""

    REVENUE = "REVENUE"
    ENGAGEMENT = "ENGAGEMENT"
    COMPLIANCE = "COMPLIANCE"
    COST_REDUCTION = "COST_REDUCTION"


class Evolution(str, Enum):
    """Valid evolution stages (Wardley Maps) for Bounded Contexts."""

    GENESIS = "GENESIS"
    CUSTOM_BUILT = "CUSTOM_BUILT"
    PRODUCT = "PRODUCT"
    COMMODITY = "COMMODITY"


class SubdomainType(str, Enum):
    """Valid subdomain types."""

    CORE_DOMAIN = "CORE_DOMAIN"
    SUPPORTING_DOMAIN = "SUPPORTING_DOMAIN"
    GENERIC_SUBDOMAIN = "GENERIC_SUBDOMAIN"


class LikelihoodForChange(str, Enum):
    """Valid likelihood-for-change values for Aggregates."""

    OFTEN = "OFTEN"
    NORMAL = "NORMAL"
    RARELY = "RARELY"


class OperationVisibility(str, Enum):
    """Valid visibility modifiers for operations."""

    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"
    PROTECTED = "PROTECTED"
