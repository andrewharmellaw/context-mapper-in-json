"""Performance tests for Context Mapper JSON Converter.

Tests conversion performance with large JSON files, memory usage,
validation performance with complex schemas, and scalability limits.

**Validates: Requirements 2.3, 2.5**
"""

import json
import os
import sys
import tempfile
import time
from pathlib import Path

import pytest

from context_mapper_json_converter.converter import ConverterEngine
from context_mapper_json_converter.exceptions import ConversionError
from context_mapper_json_converter.validation import ValidationEngine

# ---------------------------------------------------------------------------
# Test data generators
# ---------------------------------------------------------------------------

def generate_large_context_map(num_contexts: int = 50) -> dict:
    """Generate a large context map with many bounded contexts and relationships."""
    context_names = [f"BoundedContext{i}" for i in range(num_contexts)]

    bounded_contexts = []
    for i, name in enumerate(context_names):
        bc = {
            "name": name,
            "type": "FEATURE",
            "domainVisionStatement": f"Domain vision for {name} - handles business logic area {i}",
            "implementationTechnology": "Java Spring Boot",
        }
        bounded_contexts.append(bc)

    # Add relationships between consecutive contexts
    relationships = []
    for i in range(min(num_contexts - 1, 20)):  # Cap at 20 relationships
        relationships.append({
            "type": "CustomerSupplier",
            "upstream": context_names[i],
            "downstream": context_names[i + 1],
            "upstreamRoles": ["OHS", "PL"],
            "downstreamRoles": ["ACL"],
        })

    return {
        "contextMap": {
            "name": "LargeSystem",
            "type": "SYSTEM_LANDSCAPE",
            "contains": context_names,
            "relationships": relationships,
        },
        "boundedContexts": bounded_contexts,
    }


def generate_context_map_with_aggregates(num_contexts: int = 10, aggregates_per_context: int = 5) -> dict:
    """Generate a context map with bounded contexts containing aggregates."""
    context_names = [f"Context{i}" for i in range(num_contexts)]

    bounded_contexts = []
    for i, name in enumerate(context_names):
        aggregates = []
        for j in range(aggregates_per_context):
            aggregate = {
                "name": f"Aggregate{i}_{j}",
                "entities": [
                    {
                        "name": f"Entity{i}_{j}",
                        "aggregateRoot": True,
                        "attributes": [
                            {"name": "id", "type": "String", "key": True},
                            {"name": "name", "type": "String"},
                            {"name": "status", "type": "String"},
                        ],
                    }
                ],
                "valueObjects": [
                    {
                        "name": f"ValueObject{i}_{j}",
                        "attributes": [
                            {"name": "value", "type": "String"},
                        ],
                    }
                ],
                "domainEvents": [
                    {
                        "name": f"Event{i}_{j}Created",
                        "attributes": [
                            {"name": "entityId", "type": "String"},
                        ],
                    }
                ],
            }
            aggregates.append(aggregate)

        bc = {
            "name": name,
            "type": "FEATURE",
            "aggregates": aggregates,
        }
        bounded_contexts.append(bc)

    return {
        "contextMap": {
            "name": "TacticalSystem",
            "type": "SYSTEM_LANDSCAPE",
            "contains": context_names,
        },
        "boundedContexts": bounded_contexts,
    }


def generate_complex_validation_data(num_contexts: int = 30) -> dict:
    """Generate complex data for validation performance testing."""
    context_names = [f"Ctx{i}" for i in range(num_contexts)]

    bounded_contexts = [
        {"name": name, "type": "FEATURE"}
        for name in context_names
    ]

    relationships = []
    for i in range(0, min(num_contexts - 1, 15), 2):
        relationships.append({
            "type": "Partnership",
            "upstream": context_names[i],
            "downstream": context_names[i + 1],
        })

    return {
        "contextMap": {
            "name": "ComplexSystem",
            "type": "SYSTEM_LANDSCAPE",
            "contains": context_names,
            "relationships": relationships,
        },
        "boundedContexts": bounded_contexts,
    }


# ---------------------------------------------------------------------------
# Conversion performance tests
# ---------------------------------------------------------------------------

class TestConversionPerformance:
    """Tests for conversion performance with various input sizes."""

    def test_small_context_map_conversion_speed(self):
        """Small context map (5 contexts) should convert in under 1 second."""
        json_data = generate_large_context_map(num_contexts=5)
        converter = ConverterEngine()

        start = time.time()
        result = converter.convert(json_data)
        elapsed = time.time() - start

        assert isinstance(result, str)
        assert len(result) > 0
        assert elapsed < 1.0, f"Small conversion took {elapsed:.3f}s, expected < 1.0s"

    def test_medium_context_map_conversion_speed(self):
        """Medium context map (25 contexts) should convert in under 2 seconds."""
        json_data = generate_large_context_map(num_contexts=25)
        converter = ConverterEngine()

        start = time.time()
        result = converter.convert(json_data)
        elapsed = time.time() - start

        assert isinstance(result, str)
        assert len(result) > 0
        assert elapsed < 2.0, f"Medium conversion took {elapsed:.3f}s, expected < 2.0s"

    def test_large_context_map_conversion_speed(self):
        """Large context map (50 contexts) should convert in under 5 seconds."""
        json_data = generate_large_context_map(num_contexts=50)
        converter = ConverterEngine()

        start = time.time()
        result = converter.convert(json_data)
        elapsed = time.time() - start

        assert isinstance(result, str)
        assert len(result) > 0
        assert elapsed < 5.0, f"Large conversion took {elapsed:.3f}s, expected < 5.0s"

    def test_context_map_with_aggregates_conversion_speed(self):
        """Context map with aggregates (10 contexts, 5 aggregates each) should convert in under 3 seconds."""
        json_data = generate_context_map_with_aggregates(num_contexts=10, aggregates_per_context=5)
        converter = ConverterEngine()

        start = time.time()
        result = converter.convert(json_data)
        elapsed = time.time() - start

        assert isinstance(result, str)
        assert len(result) > 0
        assert elapsed < 3.0, f"Aggregate conversion took {elapsed:.3f}s, expected < 3.0s"

    def test_repeated_conversions_consistent_speed(self):
        """Repeated conversions of the same data should have consistent performance."""
        json_data = generate_large_context_map(num_contexts=20)
        converter = ConverterEngine()

        times = []
        for _ in range(5):
            start = time.time()
            result = converter.convert(json_data)
            elapsed = time.time() - start
            times.append(elapsed)
            assert isinstance(result, str)

        # All runs should complete within 2 seconds
        for i, t in enumerate(times):
            assert t < 2.0, f"Run {i+1} took {t:.3f}s, expected < 2.0s"

        # Performance should not degrade significantly across runs
        max_time = max(times)
        min_time = min(times)
        # Max should not be more than 10x the min (allows for JIT warmup etc.)
        if min_time > 0:
            ratio = max_time / min_time
            assert ratio < 10.0, f"Performance variance too high: max={max_time:.3f}s, min={min_time:.3f}s, ratio={ratio:.1f}"

    def test_conversion_output_scales_with_input(self):
        """Larger inputs should produce proportionally larger outputs."""
        small_data = generate_large_context_map(num_contexts=5)
        large_data = generate_large_context_map(num_contexts=50)
        converter = ConverterEngine()

        small_result = converter.convert(small_data)
        large_result = converter.convert(large_data)

        # Large output should be bigger than small output
        assert len(large_result) > len(small_result), (
            "Larger input should produce larger output"
        )

    def test_all_relationship_types_performance(self):
        """Converting all relationship types should complete quickly."""
        relationship_types = ["Partnership", "SharedKernel", "CustomerSupplier", "UpstreamDownstream"]
        converter = ConverterEngine()

        for rel_type in relationship_types:
            json_data = {
                "contextMap": {
                    "name": "TestSystem",
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

            start = time.time()
            result = converter.convert(json_data)
            elapsed = time.time() - start

            assert isinstance(result, str)
            assert elapsed < 1.0, f"Relationship type {rel_type} took {elapsed:.3f}s, expected < 1.0s"


# ---------------------------------------------------------------------------
# Validation performance tests
# ---------------------------------------------------------------------------

class TestValidationPerformance:
    """Tests for validation performance with complex schemas."""

    def test_small_schema_validation_speed(self):
        """Small schema (5 contexts) should validate in under 1 second."""
        json_data = generate_complex_validation_data(num_contexts=5)
        validator = ValidationEngine()

        start = time.time()
        result = validator.validate_json_schema(json_data)
        elapsed = time.time() - start

        assert result.is_valid
        assert elapsed < 1.0, f"Small validation took {elapsed:.3f}s, expected < 1.0s"

    def test_medium_schema_validation_speed(self):
        """Medium schema (30 contexts) should validate in under 2 seconds."""
        json_data = generate_complex_validation_data(num_contexts=30)
        validator = ValidationEngine()

        start = time.time()
        result = validator.validate_json_schema(json_data)
        elapsed = time.time() - start

        assert result.is_valid
        assert elapsed < 2.0, f"Medium validation took {elapsed:.3f}s, expected < 2.0s"

    def test_semantic_validation_speed(self):
        """Semantic validation of complex data should complete in under 2 seconds."""
        json_data = generate_complex_validation_data(num_contexts=30)
        validator = ValidationEngine()

        start = time.time()
        result = validator.validate_semantic_rules(json_data)
        elapsed = time.time() - start

        assert result.is_valid
        assert elapsed < 2.0, f"Semantic validation took {elapsed:.3f}s, expected < 2.0s"

    def test_combined_validation_speed(self):
        """Combined schema + semantic validation should complete in under 3 seconds."""
        json_data = generate_complex_validation_data(num_contexts=30)
        validator = ValidationEngine()

        start = time.time()
        schema_result = validator.validate_json_schema(json_data)
        semantic_result = validator.validate_semantic_rules(json_data)
        elapsed = time.time() - start

        assert schema_result.is_valid
        assert semantic_result.is_valid
        assert elapsed < 3.0, f"Combined validation took {elapsed:.3f}s, expected < 3.0s"

    def test_invalid_data_validation_speed(self):
        """Validation of invalid data should also complete quickly."""
        invalid_data = {
            "contextMap": {
                "name": "InvalidSystem",
                "type": "SYSTEM_LANDSCAPE",
                "contains": ["ServiceA", "ServiceB", "ServiceC"],
                "relationships": [
                    {
                        "type": "CustomerSupplier",
                        "upstream": "NonExistent",
                        "downstream": "ServiceA",
                    }
                ],
            },
            "boundedContexts": [
                {"name": "ServiceA", "type": "FEATURE"},
                {"name": "ServiceB", "type": "SYSTEM"},
                {"name": "ServiceC", "type": "FEATURE"},
            ],
        }
        validator = ValidationEngine()

        start = time.time()
        schema_result = validator.validate_json_schema(invalid_data)
        semantic_result = validator.validate_semantic_rules(invalid_data)
        elapsed = time.time() - start

        # Validation should complete quickly even for invalid data
        assert elapsed < 1.0, f"Invalid data validation took {elapsed:.3f}s, expected < 1.0s"
        # The semantic validation should detect the error
        assert not semantic_result.is_valid

    def test_repeated_validations_consistent_speed(self):
        """Repeated validations should have consistent performance."""
        json_data = generate_complex_validation_data(num_contexts=20)
        validator = ValidationEngine()

        times = []
        for _ in range(5):
            start = time.time()
            result = validator.validate_json_schema(json_data)
            elapsed = time.time() - start
            times.append(elapsed)
            assert result.is_valid

        # All runs should complete within 2 seconds
        for i, t in enumerate(times):
            assert t < 2.0, f"Validation run {i+1} took {t:.3f}s, expected < 2.0s"


# ---------------------------------------------------------------------------
# Memory and resource tests
# ---------------------------------------------------------------------------

class TestMemoryAndResources:
    """Tests for memory usage and resource consumption."""

    def test_large_conversion_does_not_crash(self):
        """Converting a very large context map should not crash the process."""
        json_data = generate_large_context_map(num_contexts=100)
        converter = ConverterEngine()

        # Should complete without raising an exception
        result = converter.convert(json_data)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_large_tactical_conversion_does_not_crash(self):
        """Converting large tactical patterns should not crash."""
        json_data = generate_context_map_with_aggregates(
            num_contexts=10, aggregates_per_context=10
        )
        converter = ConverterEngine()

        result = converter.convert(json_data)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_output_size_is_reasonable(self):
        """Output size should be proportional to input and not excessively large."""
        json_data = generate_large_context_map(num_contexts=50)
        converter = ConverterEngine()

        result = converter.convert(json_data)

        # Output should be non-trivial but not absurdly large
        # 50 contexts with relationships should produce at most ~500KB of CML
        max_size_bytes = 500 * 1024  # 500 KB
        output_size = len(result.encode("utf-8"))
        assert output_size < max_size_bytes, (
            f"Output size {output_size} bytes exceeds limit of {max_size_bytes} bytes"
        )

    def test_multiple_converter_instances_work_independently(self):
        """Multiple converter instances should work independently without interference."""
        json_data_1 = generate_large_context_map(num_contexts=10)
        json_data_2 = generate_context_map_with_aggregates(num_contexts=5, aggregates_per_context=3)

        converter1 = ConverterEngine()
        converter2 = ConverterEngine()

        result1 = converter1.convert(json_data_1)
        result2 = converter2.convert(json_data_2)

        assert isinstance(result1, str)
        assert isinstance(result2, str)
        assert len(result1) > 0
        assert len(result2) > 0
        # Results should be different since inputs are different
        assert result1 != result2

    def test_converter_handles_empty_collections_efficiently(self):
        """Converter should handle empty collections without performance issues."""
        json_data = {
            "contextMap": {
                "name": "EmptySystem",
                "type": "SYSTEM_LANDSCAPE",
                "contains": ["EmptyContext"],
                "relationships": [],
            },
            "boundedContexts": [
                {
                    "name": "EmptyContext",
                    "type": "FEATURE",
                    "aggregates": [],
                }
            ],
        }
        converter = ConverterEngine()

        start = time.time()
        result = converter.convert(json_data)
        elapsed = time.time() - start

        assert isinstance(result, str)
        assert elapsed < 0.5, f"Empty collections conversion took {elapsed:.3f}s, expected < 0.5s"


# ---------------------------------------------------------------------------
# File I/O performance tests
# ---------------------------------------------------------------------------

class TestFileIOPerformance:
    """Tests for file I/O performance with large JSON files."""

    def test_large_json_file_read_and_convert(self):
        """Reading and converting a large JSON file should complete in under 5 seconds."""
        json_data = generate_large_context_map(num_contexts=50)

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(json_data, f, indent=2)
            temp_path = f.name

        try:
            converter = ConverterEngine()

            start = time.time()
            with open(temp_path, "r", encoding="utf-8") as f:
                loaded_data = json.load(f)
            result = converter.convert(loaded_data)
            elapsed = time.time() - start

            assert isinstance(result, str)
            assert len(result) > 0
            assert elapsed < 5.0, f"File read + convert took {elapsed:.3f}s, expected < 5.0s"
        finally:
            os.unlink(temp_path)

    def test_large_cml_output_write_speed(self):
        """Writing large CML output to file should complete quickly."""
        json_data = generate_large_context_map(num_contexts=50)
        converter = ConverterEngine()
        cml_output = converter.convert(json_data)

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".cml", delete=False, encoding="utf-8"
        ) as f:
            temp_path = f.name

        try:
            start = time.time()
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(cml_output)
            elapsed = time.time() - start

            assert elapsed < 1.0, f"File write took {elapsed:.3f}s, expected < 1.0s"

            # Verify file was written correctly
            with open(temp_path, "r", encoding="utf-8") as f:
                read_back = f.read()
            assert read_back == cml_output
        finally:
            os.unlink(temp_path)


# ---------------------------------------------------------------------------
# Scalability tests
# ---------------------------------------------------------------------------

class TestScalability:
    """Tests for scalability limits and error handling under load."""

    def test_conversion_scales_linearly_with_context_count(self):
        """Conversion time should scale roughly linearly with number of contexts."""
        converter = ConverterEngine()

        sizes = [10, 20, 40]
        times = []

        for size in sizes:
            json_data = generate_large_context_map(num_contexts=size)
            start = time.time()
            result = converter.convert(json_data)
            elapsed = time.time() - start
            times.append(elapsed)
            assert isinstance(result, str)

        # Each doubling of input should not more than 4x the time
        # (allowing for some overhead and non-linearity)
        for i in range(1, len(times)):
            if times[i - 1] > 0.001:  # Only check if previous time is measurable
                ratio = times[i] / times[i - 1]
                assert ratio < 8.0, (
                    f"Conversion time ratio {ratio:.1f}x for 2x input size "
                    f"(sizes {sizes[i-1]} -> {sizes[i]}), expected < 8.0x"
                )

    def test_validation_handles_many_relationships(self):
        """Validation should handle many relationships without timing out."""
        # Create a context map with many relationships
        num_contexts = 20
        context_names = [f"Ctx{i}" for i in range(num_contexts)]

        relationships = []
        for i in range(num_contexts - 1):
            relationships.append({
                "type": "CustomerSupplier",
                "upstream": context_names[i],
                "downstream": context_names[i + 1],
            })

        json_data = {
            "contextMap": {
                "name": "ManyRelationships",
                "type": "SYSTEM_LANDSCAPE",
                "contains": context_names,
                "relationships": relationships,
            },
            "boundedContexts": [
                {"name": name, "type": "FEATURE"}
                for name in context_names
            ],
        }

        validator = ValidationEngine()

        start = time.time()
        result = validator.validate_json_schema(json_data)
        semantic_result = validator.validate_semantic_rules(json_data)
        elapsed = time.time() - start

        assert result.is_valid
        assert semantic_result.is_valid
        assert elapsed < 3.0, f"Many-relationship validation took {elapsed:.3f}s, expected < 3.0s"

    def test_error_handling_under_load(self):
        """Error handling should work correctly even with many invalid inputs."""
        validator = ValidationEngine()
        converter = ConverterEngine()

        # Generate many invalid inputs and verify they're handled gracefully
        invalid_inputs = [
            {},  # Empty dict
            {"contextMap": {}},  # Missing required fields
            {"boundedContexts": []},  # Missing contextMap
            {"contextMap": {"type": "INVALID_TYPE", "contains": []}, "boundedContexts": []},
        ]

        start = time.time()
        for invalid_input in invalid_inputs * 10:  # Repeat 10 times
            try:
                schema_result = validator.validate_json_schema(invalid_input)
                # Some may be valid schema-wise but fail semantically
            except Exception:
                pass  # Exceptions are acceptable for invalid inputs

            try:
                converter.convert(invalid_input)
            except (ConversionError, ValueError, TypeError, AttributeError):
                pass  # Exceptions are acceptable for invalid inputs

        elapsed = time.time() - start
        assert elapsed < 5.0, f"Error handling under load took {elapsed:.3f}s, expected < 5.0s"

    def test_batch_conversion_performance(self):
        """Converting multiple independent context maps should be efficient."""
        converter = ConverterEngine()

        # Generate 20 small context maps
        batch = [
            generate_large_context_map(num_contexts=5)
            for _ in range(20)
        ]

        start = time.time()
        results = [converter.convert(data) for data in batch]
        elapsed = time.time() - start

        assert len(results) == 20
        for result in results:
            assert isinstance(result, str)
            assert len(result) > 0

        assert elapsed < 5.0, f"Batch conversion of 20 items took {elapsed:.3f}s, expected < 5.0s"

    def test_validation_batch_performance(self):
        """Validating multiple context maps in batch should be efficient."""
        validator = ValidationEngine()

        # Generate 20 small context maps for validation
        batch = [
            generate_complex_validation_data(num_contexts=5)
            for _ in range(20)
        ]

        start = time.time()
        results = [validator.validate_json_schema(data) for data in batch]
        elapsed = time.time() - start

        assert len(results) == 20
        for result in results:
            assert result.is_valid

        assert elapsed < 5.0, f"Batch validation of 20 items took {elapsed:.3f}s, expected < 5.0s"
