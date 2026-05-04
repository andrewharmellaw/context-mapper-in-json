"""
CML Output Validator for Context Mapper JSON Converter

Validates generated Context Mapper DSL (CML) code for syntax and semantic correctness.
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from .validation import ValidationResult, ValidationError

logger = logging.getLogger(__name__)


@dataclass
class CMLElement:
    """Represents a parsed CML element."""

    element_type: str  # "ContextMap", "BoundedContext", "Relationship"
    name: Optional[str]
    properties: Dict[str, Any]
    line_number: int


class CMLValidator:
    """
    Validates Context Mapper DSL (CML) code for syntax and semantic correctness.

    Provides validation for:
    1. Basic CML syntax parsing
    2. Semantic rule validation
    3. Reference integrity checking
    """

    def __init__(self):
        """Initialize the CML validator with parsing patterns."""
        self._setup_patterns()

    def _setup_patterns(self) -> None:
        """Set up regex patterns for CML parsing."""

        # Context Map pattern: ContextMap [name] type = TYPE [state = STATE] {
        self.context_map_pattern = re.compile(
            r"ContextMap\s+(?:(\w+)\s+)?type\s*=\s*(\w+)(?:\s+state\s*=\s*(\w+))?\s*\{"
        )

        # Bounded Context pattern: BoundedContext name type = TYPE [realizes context] {
        self.bounded_context_pattern = re.compile(
            r"BoundedContext\s+(\w+)\s+type\s*=\s*(\w+)(?:\s+realizes\s+(\w+))?\s*\{"
        )

        # Contains pattern: contains context1, context2, ...
        self.contains_pattern = re.compile(r"contains\s+([\w\s,]+)")

        # Relationship patterns
        self.partnership_pattern = re.compile(r"(\w+)\s+Partnership\s+(\w+)")
        self.shared_kernel_pattern = re.compile(
            r"(\w+)\s+\[SK\]\s+<->\s+\[SK\]\s+(\w+)(?:\s*:\s*(.+))?"
        )

        # Property patterns
        self.property_pattern = re.compile(r'(\w+)\s*=\s*"([^"]*)"')
        self.enum_property_pattern = re.compile(r"(\w+)\s*=\s*(\w+)")

        # Valid enum values
        self.valid_context_map_types = {"SYSTEM_LANDSCAPE", "ORGANIZATIONAL"}
        self.valid_context_map_states = {"AS_IS", "TO_BE"}
        self.valid_bounded_context_types = {"FEATURE", "APPLICATION", "SYSTEM", "TEAM"}
        self.valid_knowledge_levels = {"CONCRETE", "META"}
        self.valid_business_models = {
            "REVENUE",
            "ENGAGEMENT",
            "COMPLIANCE",
            "COST_REDUCTION",
        }
        self.valid_evolutions = {"GENESIS", "CUSTOM_BUILT", "PRODUCT", "COMMODITY"}

    def validate_syntax(self, cml_code: str) -> ValidationResult:
        """
        Validate CML code syntax.

        Args:
            cml_code: The CML code to validate

        Returns:
            ValidationResult with syntax validation outcome
        """
        result = ValidationResult(is_valid=True, errors=[], warnings=[])

        try:
            # Parse the CML code
            elements = self._parse_cml(cml_code, result)

            if result.is_valid:
                # Validate parsed elements
                self._validate_parsed_elements(elements, result)

        except Exception as e:
            logger.error(f"Unexpected error during CML syntax validation: {e}")
            result.add_error(
                ValidationError(
                    message=f"Unexpected CML validation error: {str(e)}",
                    property_path="",
                    error_type="CML_SYNTAX_ERROR",
                )
            )

        return result

    def _parse_cml(self, cml_code: str, result: ValidationResult) -> List[CMLElement]:
        """Parse CML code into structured elements."""
        elements = []
        lines = cml_code.split("\n")
        current_element = None
        brace_count = 0

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith("//"):
                continue

            try:
                # Check for Context Map
                context_map_match = self.context_map_pattern.match(line)
                if context_map_match:
                    name, cm_type, state = context_map_match.groups()

                    # Validate Context Map type
                    if cm_type not in self.valid_context_map_types:
                        result.add_error(
                            ValidationError(
                                message=f"Invalid Context Map type: {cm_type}",
                                property_path=f"line {line_num}",
                                error_type="CML_SYNTAX_ERROR",
                                line_number=line_num,
                                suggestion=f"Use one of: {', '.join(self.valid_context_map_types)}",
                            )
                        )

                    # Validate state if present
                    if state and state not in self.valid_context_map_states:
                        result.add_error(
                            ValidationError(
                                message=f"Invalid Context Map state: {state}",
                                property_path=f"line {line_num}",
                                error_type="CML_SYNTAX_ERROR",
                                line_number=line_num,
                                suggestion=f"Use one of: {', '.join(self.valid_context_map_states)}",
                            )
                        )

                    current_element = CMLElement(
                        element_type="ContextMap",
                        name=name,
                        properties={"type": cm_type, "state": state},
                        line_number=line_num,
                    )
                    brace_count = 1
                    continue

                # Check for Bounded Context
                bounded_context_match = self.bounded_context_pattern.match(line)
                if bounded_context_match:
                    name, bc_type, realizes = bounded_context_match.groups()

                    # Validate Bounded Context type
                    if bc_type not in self.valid_bounded_context_types:
                        result.add_error(
                            ValidationError(
                                message=f"Invalid Bounded Context type: {bc_type}",
                                property_path=f"line {line_num}",
                                error_type="CML_SYNTAX_ERROR",
                                line_number=line_num,
                                suggestion=f"Use one of: {', '.join(self.valid_bounded_context_types)}",
                            )
                        )

                    current_element = CMLElement(
                        element_type="BoundedContext",
                        name=name,
                        properties={"type": bc_type, "realizes": realizes},
                        line_number=line_num,
                    )
                    brace_count = 1
                    continue

                # Handle content within braces
                if current_element and brace_count > 0:
                    # Count braces
                    brace_count += line.count("{") - line.count("}")

                    # Parse contains statement
                    contains_match = self.contains_pattern.match(line)
                    if contains_match:
                        contexts = [
                            ctx.strip() for ctx in contains_match.group(1).split(",")
                        ]
                        current_element.properties["contains"] = contexts

                    # Parse relationships
                    partnership_match = self.partnership_pattern.match(line)
                    if partnership_match:
                        upstream, downstream = partnership_match.groups()
                        if "relationships" not in current_element.properties:
                            current_element.properties["relationships"] = []
                        current_element.properties["relationships"].append(
                            {
                                "type": "Partnership",
                                "upstream": upstream,
                                "downstream": downstream,
                            }
                        )

                    shared_kernel_match = self.shared_kernel_pattern.match(line)
                    if shared_kernel_match:
                        upstream, downstream, tech = shared_kernel_match.groups()
                        if "relationships" not in current_element.properties:
                            current_element.properties["relationships"] = []
                        rel = {
                            "type": "SharedKernel",
                            "upstream": upstream,
                            "downstream": downstream,
                        }
                        if tech:
                            rel["implementationTechnology"] = tech.strip()
                        current_element.properties["relationships"].append(rel)

                    # Parse properties
                    property_match = self.property_pattern.match(line)
                    if property_match:
                        prop_name, prop_value = property_match.groups()
                        current_element.properties[prop_name] = prop_value

                    enum_property_match = self.enum_property_pattern.match(line)
                    if enum_property_match:
                        prop_name, prop_value = enum_property_match.groups()
                        # Validate enum properties
                        if (
                            prop_name == "knowledgeLevel"
                            and prop_value not in self.valid_knowledge_levels
                        ):
                            result.add_error(
                                ValidationError(
                                    message=f"Invalid knowledgeLevel: {prop_value}",
                                    property_path=f"line {line_num}",
                                    error_type="CML_SYNTAX_ERROR",
                                    line_number=line_num,
                                )
                            )
                        current_element.properties[prop_name] = prop_value

                    # Check if element is complete
                    if brace_count == 0:
                        elements.append(current_element)
                        current_element = None

            except Exception as e:
                result.add_error(
                    ValidationError(
                        message=f"Parse error on line {line_num}: {str(e)}",
                        property_path=f"line {line_num}",
                        error_type="CML_PARSE_ERROR",
                        line_number=line_num,
                    )
                )

        # Check for unclosed braces
        if current_element and brace_count > 0:
            result.add_error(
                ValidationError(
                    message=f"Unclosed braces in {current_element.element_type} {current_element.name}",
                    property_path=f"line {current_element.line_number}",
                    error_type="CML_SYNTAX_ERROR",
                    line_number=current_element.line_number,
                    suggestion="Add missing closing brace '}'",
                )
            )

        return elements

    def _validate_parsed_elements(
        self, elements: List[CMLElement], result: ValidationResult
    ) -> None:
        """Validate the parsed CML elements for consistency."""
        context_maps = [e for e in elements if e.element_type == "ContextMap"]
        bounded_contexts = [e for e in elements if e.element_type == "BoundedContext"]

        # Validate that we have at most one Context Map
        if len(context_maps) > 1:
            result.add_error(
                ValidationError(
                    message="Multiple Context Maps found - only one is allowed",
                    property_path="",
                    error_type="CML_SEMANTIC_ERROR",
                    suggestion="Combine into a single Context Map",
                )
            )

        # Validate Context Map references
        if context_maps:
            context_map = context_maps[0]
            contains = context_map.properties.get("contains", [])
            bc_names = {bc.name for bc in bounded_contexts}

            # Check that all contained contexts are defined
            for context_name in contains:
                if context_name not in bc_names:
                    result.add_error(
                        ValidationError(
                            message=f"Context Map references undefined Bounded Context: {context_name}",
                            property_path=f"ContextMap contains",
                            error_type="CML_REFERENCE_ERROR",
                            line_number=context_map.line_number,
                            suggestion=f"Define BoundedContext {context_name} or remove from contains",
                        )
                    )

            # Validate relationships
            relationships = context_map.properties.get("relationships", [])
            for rel in relationships:
                upstream = rel.get("upstream")
                downstream = rel.get("downstream")

                if upstream not in contains:
                    result.add_error(
                        ValidationError(
                            message=f"Relationship references undefined upstream context: {upstream}",
                            property_path="ContextMap relationships",
                            error_type="CML_REFERENCE_ERROR",
                            suggestion=f"Add {upstream} to contains or fix relationship",
                        )
                    )

                if downstream not in contains:
                    result.add_error(
                        ValidationError(
                            message=f"Relationship references undefined downstream context: {downstream}",
                            property_path="ContextMap relationships",
                            error_type="CML_REFERENCE_ERROR",
                            suggestion=f"Add {downstream} to contains or fix relationship",
                        )
                    )

        # Validate Bounded Context names are unique
        bc_names_list = [bc.name for bc in bounded_contexts]
        if len(bc_names_list) != len(set(bc_names_list)):
            duplicates = [
                name for name in bc_names_list if bc_names_list.count(name) > 1
            ]
            result.add_error(
                ValidationError(
                    message=f"Duplicate Bounded Context names: {', '.join(set(duplicates))}",
                    property_path="BoundedContext names",
                    error_type="CML_SEMANTIC_ERROR",
                    suggestion="Use unique names for all Bounded Contexts",
                )
            )

    def validate_semantics(self, cml_code: str) -> ValidationResult:
        """
        Validate CML semantic rules.

        Args:
            cml_code: The CML code to validate

        Returns:
            ValidationResult with semantic validation outcome
        """
        # For Phase 1, semantic validation is included in syntax validation
        return self.validate_syntax(cml_code)

    def validate_with_context_mapper(self, cml_code: str) -> ValidationResult:
        """
        Validate CML code with Context Mapper tools (if available).

        Args:
            cml_code: The CML code to validate

        Returns:
            ValidationResult with Context Mapper tool validation outcome
        """
        result = ValidationResult(is_valid=True, errors=[], warnings=[])

        # For Phase 1, we'll implement a basic validation
        # In later phases, this could integrate with actual Context Mapper CLI tools

        result.add_warning(
            ValidationError(
                message="Context Mapper tool integration not yet implemented",
                property_path="",
                error_type="CML_TOOL_WARNING",
                suggestion="Validate manually with Context Mapper tools for now",
            )
        )

        return result
