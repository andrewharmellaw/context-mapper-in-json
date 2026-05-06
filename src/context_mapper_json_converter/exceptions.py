"""
Domain-specific exception classes for the Context Mapper JSON Converter.

Using custom exceptions lets callers catch specific failure modes without
catching everything, and makes error handling intent explicit.
"""


class ContextMapperError(Exception):
    """Base exception for all Context Mapper JSON Converter errors."""


class ConversionError(ContextMapperError):
    """Raised when JSON-to-CML conversion fails.

    This wraps lower-level errors (template rendering, missing fields, etc.)
    into a single catchable type for library consumers.
    """


class SchemaLoadError(ContextMapperError):
    """Raised when a JSON Schema file cannot be loaded or parsed.

    Typically indicates a packaging problem (missing package data) or a
    corrupt schema file.
    """


class CMLParseError(ContextMapperError):
    """Raised when CML code cannot be parsed back into a JSON structure.

    Used by the round-trip validator when the generated CML is structurally
    invalid.
    """
