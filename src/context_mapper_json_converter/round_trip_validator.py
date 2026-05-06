"""
Round-Trip Validator for Context Mapper JSON Converter

Validates that JSON → CML → JSON conversion preserves all information.
"""

import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, cast

from .cml_validator import CMLValidator
from .converter import ConverterEngine
from .enums import ValidationErrorType
from .exceptions import CMLParseError
from .validation import ValidationError, ValidationResult

logger = logging.getLogger(__name__)


@dataclass
class Discrepancy:
    """Represents a discrepancy found during round-trip validation."""

    property_path: str
    original_value: Any
    converted_value: Any
    discrepancy_type: str
    description: str

    def __str__(self) -> str:
        return f"{self.discrepancy_type}: {self.description} at {self.property_path}"


class CMLParser:
    """
    Parses CML code back into JSON-like structure for comparison.

    This is a simplified parser focused on extracting the key information
    needed for round-trip validation.
    """

    # Regex patterns compiled once at class level
    _CONTEXT_MAP_PATTERN = re.compile(
        r"ContextMap\s+(?:(\w+)\s+)?type\s*=\s*(\w+)(?:\s+state\s*=\s*(\w+))?\s*\{"
    )
    _CONTAINS_PATTERN = re.compile(r"contains\s+([\w\s,]+)")
    _BOUNDED_CONTEXT_PATTERN = re.compile(
        r"BoundedContext\s+(\w+)\s+type\s*=\s*(\w+)(?:\s+realizes\s+(\w+))?\s*\{"
    )
    _AGGREGATE_PATTERN = re.compile(r"Aggregate\s+(\w+)(?:\s+owned\s+by\s+(\w+))?\s*\{")
    _ENTITY_PATTERN = re.compile(r"Entity\s+(\w+)(?:\s+aggregateRoot)?\s*\{")
    _VALUE_OBJECT_PATTERN = re.compile(r"ValueObject\s+(\w+)\s*\{")
    _DOMAIN_EVENT_PATTERN = re.compile(r"DomainEvent\s+(\w+)\s*\{")
    _COMMAND_PATTERN = re.compile(r"Command\s+(\w+)\s*\{")
    _SERVICE_PATTERN = re.compile(r"Service\s+(\w+)\s*\{")
    _REPOSITORY_PATTERN = re.compile(r"Repository\s+(\w+)\s*\{")
    _PROPERTY_PATTERN = re.compile(r'(\w+)\s*=\s*"([^"]*)"')
    _ENUM_PROPERTY_PATTERN = re.compile(r"(\w+)\s*=\s*(\w+)")
    _ATTRIBUTE_PATTERN = re.compile(r"(\w+)\s+(\w+)(?:\s+(key|nullable))*")
    _OPERATION_PATTERN = re.compile(
        r"(?:(public|private|protected)\s+)?(\w+)\s+(\w+)\(([^)]*)\)"
    )
    _PARTNERSHIP_PATTERN = re.compile(r"(\w+)\s+Partnership\s+(\w+)")
    _SHARED_KERNEL_PATTERN = re.compile(
        r"(\w+)\s+\[SK\]\s+<->\s+\[SK\]\s+(\w+)(?:\s*:\s*(.+))?"
    )
    _CUSTOMER_SUPPLIER_PATTERN = re.compile(
        r"(\w+)\s+\[([^\]]+)\]->\[([^\]]+)\]\s+(\w+)(?:\s*:\s*([^{]+))?(?:\s*\{\s*([^}]+)\s*\})?"
    )

    def __init__(self) -> None:
        """Initialize the CML parser."""
        # Expose class-level patterns as instance attributes for backward compatibility
        self.context_map_pattern = self._CONTEXT_MAP_PATTERN
        self.contains_pattern = self._CONTAINS_PATTERN
        self.bounded_context_pattern = self._BOUNDED_CONTEXT_PATTERN
        self.aggregate_pattern = self._AGGREGATE_PATTERN
        self.entity_pattern = self._ENTITY_PATTERN
        self.value_object_pattern = self._VALUE_OBJECT_PATTERN
        self.domain_event_pattern = self._DOMAIN_EVENT_PATTERN
        self.command_pattern = self._COMMAND_PATTERN
        self.service_pattern = self._SERVICE_PATTERN
        self.repository_pattern = self._REPOSITORY_PATTERN
        self.property_pattern = self._PROPERTY_PATTERN
        self.enum_property_pattern = self._ENUM_PROPERTY_PATTERN
        self.attribute_pattern = self._ATTRIBUTE_PATTERN
        self.operation_pattern = self._OPERATION_PATTERN
        self.partnership_pattern = self._PARTNERSHIP_PATTERN
        self.shared_kernel_pattern = self._SHARED_KERNEL_PATTERN
        self.customer_supplier_pattern = self._CUSTOMER_SUPPLIER_PATTERN

    def parse_cml(self, cml_code: str) -> Dict[str, Any]:
        """
        Parse CML code into a JSON-like structure.

        Args:
            cml_code: The CML code to parse

        Returns:
            Dictionary representing the parsed CML structure
        """
        try:
            result: Dict[str, Any] = {}
            lines = cml_code.split("\n")

            # Parse Context Map
            context_map = self._parse_context_map(lines)
            if context_map:
                result["contextMap"] = context_map

            # Parse Bounded Contexts
            bounded_contexts = self._parse_bounded_contexts(lines)
            if bounded_contexts:
                result["boundedContexts"] = bounded_contexts

            # Parse Domain (if present)
            domain = self._parse_domain(lines)
            if domain:
                result.update(domain)

            return result

        except Exception as e:
            logger.error(f"CML parsing failed: {e}")
            raise CMLParseError(f"Failed to parse CML: {str(e)}") from e

    def _parse_context_map(self, lines: List[str]) -> Optional[Dict[str, Any]]:
        """Parse Context Map from CML lines."""
        context_map = None
        in_context_map = False

        for line in lines:
            line = line.strip()

            # Check for Context Map start
            cm_match = self.context_map_pattern.match(line)
            if cm_match:
                name, cm_type, state = cm_match.groups()
                context_map = {"type": cm_type}
                if name:
                    context_map["name"] = name
                if state:
                    context_map["state"] = state
                in_context_map = True
                continue

            if in_context_map and line == "}":
                in_context_map = False
                break

            if in_context_map:
                # context_map is always set when in_context_map is True
                assert context_map is not None

                # Parse contains
                contains_match = self.contains_pattern.match(line)
                if contains_match:
                    contexts = [
                        ctx.strip() for ctx in contains_match.group(1).split(",")
                    ]
                    context_map["contains"] = contexts

                # Parse relationships
                if "relationships" not in context_map:
                    context_map["relationships"] = []
                relationships: List[Dict[str, Any]] = cast(
                    List[Dict[str, Any]], context_map["relationships"]
                )

                # Partnership
                partnership_match = self.partnership_pattern.match(line)
                if partnership_match:
                    upstream, downstream = partnership_match.groups()
                    relationships.append(
                        {
                            "type": "Partnership",
                            "upstream": upstream,
                            "downstream": downstream,
                        }
                    )

                # Shared Kernel
                sk_match = self.shared_kernel_pattern.match(line)
                if sk_match:
                    upstream, downstream, tech = sk_match.groups()
                    rel: Dict[str, Any] = {
                        "type": "SharedKernel",
                        "upstream": upstream,
                        "downstream": downstream,
                    }
                    if tech:
                        rel["implementationTechnology"] = tech.strip()
                    relationships.append(rel)

                # Customer/Supplier and Upstream/Downstream
                cs_match = self.customer_supplier_pattern.match(line)
                if cs_match:
                    (
                        upstream,
                        upstream_roles,
                        downstream_roles,
                        downstream,
                        tech,
                        aggregates,
                    ) = cs_match.groups()
                    cs_rel: Dict[str, Any] = {
                        "type": "CustomerSupplier",  # Default, could be UpstreamDownstream
                        "upstream": upstream,
                        "downstream": downstream,
                    }
                    if upstream_roles:
                        cs_rel["upstreamRoles"] = [
                            r.strip() for r in upstream_roles.split(",")
                        ]
                    if downstream_roles:
                        cs_rel["downstreamRoles"] = [
                            r.strip() for r in downstream_roles.split(",")
                        ]
                    if tech:
                        cs_rel["implementationTechnology"] = tech.strip()
                    if aggregates:
                        cs_rel["exposedAggregates"] = [
                            a.strip() for a in aggregates.split(",")
                        ]
                    relationships.append(cs_rel)

        return context_map

    def _parse_bounded_contexts(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Parse Bounded Contexts from CML lines."""
        bounded_contexts = []
        current_bc = None
        in_bc = False
        brace_count = 0

        for line in lines:
            line = line.strip()

            # Check for Bounded Context start
            bc_match = self.bounded_context_pattern.match(line)
            if bc_match:
                name, bc_type, realizes = bc_match.groups()
                current_bc = {"name": name, "type": bc_type}
                if realizes:
                    current_bc["realizes"] = realizes
                in_bc = True
                brace_count = 1
                continue

            if in_bc:
                # Count braces
                brace_count += line.count("{") - line.count("}")

                # current_bc is always set when in_bc is True
                assert current_bc is not None

                # Parse properties
                prop_match = self.property_pattern.match(line)
                if prop_match:
                    prop_name, prop_value = prop_match.groups()
                    current_bc[prop_name] = prop_value

                enum_match = self.enum_property_pattern.match(line)
                if enum_match:
                    prop_name, prop_value = enum_match.groups()
                    if prop_name not in ["type"]:  # Skip type as it's already parsed
                        current_bc[prop_name] = prop_value

                # Parse aggregates
                agg_match = self.aggregate_pattern.match(line)
                if agg_match:
                    if "aggregates" not in current_bc:
                        current_bc["aggregates"] = []
                    # Note: Full aggregate parsing would be complex,
                    # for round-trip validation we focus on key elements
                    agg_name, owner = agg_match.groups()
                    aggregate: Dict[str, Any] = {"name": agg_name}
                    if owner:
                        aggregate["owner"] = owner
                    cast(List[Dict[str, Any]], current_bc["aggregates"]).append(
                        aggregate
                    )

                # Check if BC is complete
                if brace_count == 0:
                    bounded_contexts.append(current_bc)
                    current_bc = None
                    in_bc = False

        return bounded_contexts

    def _parse_domain(self, lines: List[str]) -> Dict[str, Any]:
        """Parse Domain and Subdomains from CML lines."""
        result: Dict[str, Any] = {}
        in_domain = False
        domain_name = None
        subdomains: List[Dict[str, str]] = []

        for line in lines:
            line = line.strip()

            # Check for Domain start
            if line.startswith("Domain ") and line.endswith(" {"):
                domain_name = line.replace("Domain ", "").replace(" {", "").strip()
                in_domain = True
                continue

            if in_domain and line == "}":
                in_domain = False
                break

            if in_domain and line.startswith("Subdomain "):
                # Simple subdomain parsing - extract name and type
                subdomain_line = line.replace("Subdomain ", "").replace(" {", "")
                subdomain = {"name": subdomain_line}
                subdomains.append(subdomain)

        if domain_name:
            result["domainName"] = domain_name
        if subdomains:
            result["subdomains"] = subdomains

        return result


class RoundTripValidator:
    """
    Validates round-trip conversion: JSON → CML → JSON.

    Ensures that no information is lost during the conversion process
    and that the semantic meaning is preserved.
    """

    def __init__(self) -> None:
        """Initialize the round-trip validator."""
        self.converter = ConverterEngine()
        self.cml_validator = CMLValidator()
        self.cml_parser = CMLParser()

    def validate_round_trip(
        self, original_json: Dict[str, Any], generated_cml: str
    ) -> ValidationResult:
        """
        Validate round-trip conversion from JSON to CML and back.

        Args:
            original_json: The original JSON data
            generated_cml: The generated CML code

        Returns:
            ValidationResult with round-trip validation outcome
        """
        result = ValidationResult(is_valid=True, errors=[], warnings=[])

        try:
            # Step 1: Parse the generated CML back to JSON-like structure
            logger.info("Parsing generated CML back to JSON structure")
            parsed_json = self.cml_parser.parse_cml(generated_cml)

            # Step 2: Compare semantic equivalence
            logger.info("Comparing semantic equivalence")
            discrepancies = self.compare_semantic_equivalence(
                original_json, parsed_json
            )

            # Step 3: Convert discrepancies to validation errors
            for discrepancy in discrepancies:
                if discrepancy.discrepancy_type in [
                    "MISSING_PROPERTY",
                    "TYPE_MISMATCH",
                    "VALUE_MISMATCH",
                ]:
                    result.add_error(
                        ValidationError(
                            message=discrepancy.description,
                            property_path=discrepancy.property_path,
                            error_type=ValidationErrorType.ROUND_TRIP_ERROR,
                            suggestion="Check the conversion logic for this property",
                        )
                    )
                else:
                    result.add_warning(
                        ValidationError(
                            message=discrepancy.description,
                            property_path=discrepancy.property_path,
                            error_type=ValidationErrorType.ROUND_TRIP_WARNING,
                        )
                    )

            # Step 4: Validate that generated CML is parseable by Context Mapper
            cml_validation = self.validate_with_context_mapper(generated_cml)
            if not cml_validation.is_valid:
                for error in cml_validation.errors:
                    result.add_error(error)

            logger.info(
                f"Round-trip validation completed with {len(result.errors)} errors and {len(result.warnings)} warnings"
            )

        except Exception as e:  # Safety net for unexpected round-trip failures
            logger.error(f"Round-trip validation failed: {e}", exc_info=True)
            result.add_error(
                ValidationError(
                    message=f"Round-trip validation error: {str(e)}",
                    property_path="",
                    error_type=ValidationErrorType.ROUND_TRIP_ERROR,
                )
            )

        return result

    def compare_semantic_equivalence(
        self, original: Dict[str, Any], parsed: Dict[str, Any]
    ) -> List[Discrepancy]:
        """
        Compare two JSON structures for semantic equivalence.

        Args:
            original: Original JSON data
            parsed: Parsed JSON data from CML

        Returns:
            List of discrepancies found
        """
        discrepancies = []

        # Compare Context Map
        if "contextMap" in original:
            if "contextMap" not in parsed:
                discrepancies.append(
                    Discrepancy(
                        property_path="contextMap",
                        original_value=original["contextMap"],
                        converted_value=None,
                        discrepancy_type="MISSING_PROPERTY",
                        description="Context Map missing in parsed CML",
                    )
                )
            else:
                discrepancies.extend(
                    self._compare_context_map(
                        original["contextMap"], parsed["contextMap"]
                    )
                )

        # Compare Bounded Contexts
        if "boundedContexts" in original:
            if "boundedContexts" not in parsed:
                discrepancies.append(
                    Discrepancy(
                        property_path="boundedContexts",
                        original_value=original["boundedContexts"],
                        converted_value=None,
                        discrepancy_type="MISSING_PROPERTY",
                        description="Bounded Contexts missing in parsed CML",
                    )
                )
            else:
                discrepancies.extend(
                    self._compare_bounded_contexts(
                        original["boundedContexts"], parsed["boundedContexts"]
                    )
                )

        # Compare Subdomains
        if "subdomains" in original:
            if "subdomains" not in parsed:
                discrepancies.append(
                    Discrepancy(
                        property_path="subdomains",
                        original_value=original["subdomains"],
                        converted_value=None,
                        discrepancy_type="MISSING_PROPERTY",
                        description="Subdomains missing in parsed CML",
                    )
                )

        return discrepancies

    def _compare_context_map(
        self, original: Dict[str, Any], parsed: Dict[str, Any]
    ) -> List[Discrepancy]:
        """Compare Context Map structures."""
        discrepancies = []

        # Compare basic properties
        for prop in ["name", "type", "state"]:
            if prop in original:
                if prop not in parsed:
                    discrepancies.append(
                        Discrepancy(
                            property_path=f"contextMap.{prop}",
                            original_value=original[prop],
                            converted_value=None,
                            discrepancy_type="MISSING_PROPERTY",
                            description=f"Context Map {prop} missing in parsed CML",
                        )
                    )
                elif original[prop] != parsed[prop]:
                    discrepancies.append(
                        Discrepancy(
                            property_path=f"contextMap.{prop}",
                            original_value=original[prop],
                            converted_value=parsed[prop],
                            discrepancy_type="VALUE_MISMATCH",
                            description=f"Context Map {prop} value mismatch",
                        )
                    )

        # Compare contains
        if "contains" in original:
            if "contains" not in parsed:
                discrepancies.append(
                    Discrepancy(
                        property_path="contextMap.contains",
                        original_value=original["contains"],
                        converted_value=None,
                        discrepancy_type="MISSING_PROPERTY",
                        description="Context Map contains missing in parsed CML",
                    )
                )
            else:
                orig_contains = set(original["contains"])
                parsed_contains = set(parsed["contains"])
                if orig_contains != parsed_contains:
                    discrepancies.append(
                        Discrepancy(
                            property_path="contextMap.contains",
                            original_value=original["contains"],
                            converted_value=parsed["contains"],
                            discrepancy_type="VALUE_MISMATCH",
                            description="Context Map contains mismatch",
                        )
                    )

        # Compare relationships (simplified)
        orig_rel_count = len(original.get("relationships", []))
        parsed_rel_count = len(parsed.get("relationships", []))
        if orig_rel_count != parsed_rel_count:
            discrepancies.append(
                Discrepancy(
                    property_path="contextMap.relationships",
                    original_value=orig_rel_count,
                    converted_value=parsed_rel_count,
                    discrepancy_type="COUNT_MISMATCH",
                    description=f"Relationship count mismatch: {orig_rel_count} vs {parsed_rel_count}",
                )
            )

        return discrepancies

    def _compare_bounded_contexts(
        self, original: List[Dict[str, Any]], parsed: List[Dict[str, Any]]
    ) -> List[Discrepancy]:
        """Compare Bounded Context structures."""
        discrepancies = []

        # Compare counts
        if len(original) != len(parsed):
            discrepancies.append(
                Discrepancy(
                    property_path="boundedContexts",
                    original_value=len(original),
                    converted_value=len(parsed),
                    discrepancy_type="COUNT_MISMATCH",
                    description=f"Bounded Context count mismatch: {len(original)} vs {len(parsed)}",
                )
            )

        # Compare by name (create lookup)
        orig_by_name = {bc.get("name"): bc for bc in original}
        parsed_by_name = {bc.get("name"): bc for bc in parsed}

        for name, orig_bc in orig_by_name.items():
            if name not in parsed_by_name:
                discrepancies.append(
                    Discrepancy(
                        property_path=f"boundedContexts[{name}]",
                        original_value=orig_bc,
                        converted_value=None,
                        discrepancy_type="MISSING_PROPERTY",
                        description=f"Bounded Context {name} missing in parsed CML",
                    )
                )
            else:
                parsed_bc = parsed_by_name[name]

                # Compare basic properties
                for prop in ["type", "realizes", "domainVisionStatement"]:
                    if prop in orig_bc:
                        if prop not in parsed_bc:
                            discrepancies.append(
                                Discrepancy(
                                    property_path=f"boundedContexts[{name}].{prop}",
                                    original_value=orig_bc[prop],
                                    converted_value=None,
                                    discrepancy_type="MISSING_PROPERTY",
                                    description=f"Bounded Context {name} {prop} missing",
                                )
                            )
                        elif orig_bc[prop] != parsed_bc[prop]:
                            discrepancies.append(
                                Discrepancy(
                                    property_path=f"boundedContexts[{name}].{prop}",
                                    original_value=orig_bc[prop],
                                    converted_value=parsed_bc[prop],
                                    discrepancy_type="VALUE_MISMATCH",
                                    description=f"Bounded Context {name} {prop} mismatch",
                                )
                            )

                # Compare aggregates (simplified - just count)
                orig_agg_count = len(orig_bc.get("aggregates", []))
                parsed_agg_count = len(parsed_bc.get("aggregates", []))
                if orig_agg_count != parsed_agg_count:
                    discrepancies.append(
                        Discrepancy(
                            property_path=f"boundedContexts[{name}].aggregates",
                            original_value=orig_agg_count,
                            converted_value=parsed_agg_count,
                            discrepancy_type="COUNT_MISMATCH",
                            description=f"Aggregate count mismatch in {name}: {orig_agg_count} vs {parsed_agg_count}",
                        )
                    )

        return discrepancies

    def identify_discrepancies(
        self, json_data: Dict[str, Any], cml_data: Dict[str, Any]
    ) -> List[Discrepancy]:
        """
        Identify specific discrepancies between JSON and CML data.

        Args:
            json_data: Original JSON data
            cml_data: Parsed CML data

        Returns:
            List of identified discrepancies
        """
        return self.compare_semantic_equivalence(json_data, cml_data)

    def validate_with_context_mapper(self, cml_code: str) -> ValidationResult:
        """
        Validate CML code with Context Mapper tools (if available).

        Args:
            cml_code: The CML code to validate

        Returns:
            ValidationResult with Context Mapper tool validation outcome
        """
        result = ValidationResult(is_valid=True, errors=[], warnings=[])

        try:
            # For Phase 4, we implement basic CML structure validation
            # In a production environment, this could integrate with actual Context Mapper CLI

            # Check for basic CML structure requirements
            if "ContextMap" not in cml_code and "BoundedContext" not in cml_code:
                result.add_error(
                    ValidationError(
                        message="CML must contain at least a ContextMap or BoundedContext",
                        property_path="",
                        error_type=ValidationErrorType.CML_STRUCTURE_ERROR,
                    )
                )

            # Check for balanced braces
            open_braces = cml_code.count("{")
            close_braces = cml_code.count("}")
            if open_braces != close_braces:
                result.add_error(
                    ValidationError(
                        message=f"Unbalanced braces: {open_braces} open, {close_braces} close",
                        property_path="",
                        error_type=ValidationErrorType.CML_SYNTAX_ERROR,
                    )
                )

            # Check for valid keywords
            valid_keywords = [
                "ContextMap",
                "BoundedContext",
                "Aggregate",
                "Entity",
                "ValueObject",
                "DomainEvent",
                "Command",
                "Service",
                "Repository",
                "Domain",
                "Subdomain",
            ]

            lines = cml_code.split("\n")
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if line and not line.startswith("//"):
                    # Check if line starts with a keyword or property
                    words = line.split()
                    if (
                        words
                        and words[0] not in valid_keywords
                        and "=" not in line
                        and not line.endswith("{")
                        and not line.endswith("}")
                    ):
                        # This might be an invalid line, but we'll be lenient for Phase 4
                        pass

            # Add integration note
            result.add_warning(
                ValidationError(
                    message="Context Mapper CLI integration not available - using basic validation",
                    property_path="",
                    error_type=ValidationErrorType.INTEGRATION_WARNING,
                    suggestion="Install Context Mapper CLI for full validation",
                )
            )

        except Exception as e:  # Safety net for unexpected validation failures
            logger.error(f"Context Mapper validation failed: {e}", exc_info=True)
            result.add_error(
                ValidationError(
                    message=f"Context Mapper validation error: {str(e)}",
                    property_path="",
                    error_type=ValidationErrorType.INTEGRATION_ERROR,
                )
            )

        return result
