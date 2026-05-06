"""Context Mapper JSON Converter.

A comprehensive system for converting JSON definitions to Context Mapper DSL (CML) code
with full validation and Context Mapper ecosystem integration.
"""

__version__ = "1.0.0"
__author__ = "Context Mapper JSON Converter Contributors"
__email__ = "maintainers@context-mapper-converter.com"

from .cml_validator import CMLValidator
from .config import Config
from .context_mapper_integration import ContextMapperIntegration, ContextMapperWorkflow
from .converter import ConverterEngine
from .enums import (
    BoundedContextType,
    BusinessModel,
    ContextMapState,
    ContextMapType,
    Evolution,
    KnowledgeLevel,
    LikelihoodForChange,
    OperationVisibility,
    RelationshipType,
    SubdomainType,
)
from .error_handler import ErrorHandler
from .exceptions import (
    CMLParseError,
    ContextMapperError,
    ConversionError,
    SchemaLoadError,
)
from .round_trip_validator import RoundTripValidator
from .validation import ValidationEngine, ValidationResult

__all__ = [
    "ValidationEngine",
    "ValidationResult",
    "ConverterEngine",
    "CMLValidator",
    "ErrorHandler",
    "RoundTripValidator",
    "ContextMapperIntegration",
    "ContextMapperWorkflow",
    "Config",
    # Enums
    "RelationshipType",
    "BoundedContextType",
    "ContextMapType",
    "ContextMapState",
    "KnowledgeLevel",
    "BusinessModel",
    "Evolution",
    "SubdomainType",
    "LikelihoodForChange",
    "OperationVisibility",
    # Exceptions
    "ContextMapperError",
    "ConversionError",
    "SchemaLoadError",
    "CMLParseError",
]
