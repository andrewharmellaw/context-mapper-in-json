"""Bug condition exploration test for test coverage improvement.

This test validates that the current test coverage is below the 85% threshold,
confirming the bug condition exists. This test is EXPECTED TO FAIL on unfixed code.

**Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10**
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st


class TestCoverageBugCondition:
    """Test that demonstrates inadequate test coverage exists."""

    def test_overall_coverage_below_threshold(self):
        """
        **Property 1: Bug Condition** - Test Coverage Below 85% Threshold

        This test validates that current test coverage is below 85% for the project.
        EXPECTED OUTCOME: Test FAILS (this confirms inadequate coverage exists)
        """
        # Get the pytest executable from the current Python environment
        pytest_cmd = [sys.executable, "-m", "pytest"]

        # Run coverage analysis - EXCLUDE this test file to prevent infinite recursion
        result = subprocess.run(
            pytest_cmd
            + [
                "--cov=src",
                "--cov-report=json",
                "--cov-report=term-missing",
                "-q",
                "--ignore=tests/test_bug_condition_exploration.py",
            ],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )

        # Load coverage data
        coverage_file = Path("coverage.json")
        if not coverage_file.exists():
            pytest.fail("Coverage report not generated")

        with open(coverage_file) as f:
            coverage_data = json.load(f)

        total_coverage = coverage_data["totals"]["percent_covered"]

        # This assertion SHOULD FAIL on unfixed code - proving bug exists
        assert total_coverage >= 85, (
            f"EXPECTED FAILURE: Total coverage is {total_coverage:.1f}%, "
            f"which is below the required 85% threshold. "
            f"This confirms the bug condition exists."
        )

    def test_critical_modules_coverage_below_threshold(self):
        """
        Test that critical modules have inadequate coverage.
        EXPECTED OUTCOME: Test FAILS (this confirms module-specific coverage gaps)
        """
        # Get the pytest executable from the current Python environment
        pytest_cmd = [sys.executable, "-m", "pytest"]

        # Run coverage analysis - EXCLUDE this test file to prevent infinite recursion
        result = subprocess.run(
            pytest_cmd
            + [
                "--cov=src",
                "--cov-report=json",
                "-q",
                "--ignore=tests/test_bug_condition_exploration.py",
            ],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )

        # Load coverage data
        coverage_file = Path("coverage.json")
        if not coverage_file.exists():
            pytest.fail("Coverage report not generated")

        with open(coverage_file) as f:
            coverage_data = json.load(f)

        # Critical modules that should have high coverage
        critical_modules = {
            "src/context_mapper_json_converter/converter.py": 80,
            "src/context_mapper_json_converter/validation.py": 80,
            "src/context_mapper_json_converter/cli.py": 80,
            "src/context_mapper_json_converter/round_trip_validator.py": 80,
            "src/context_mapper_json_converter/cml_validator.py": 80,
            "src/context_mapper_json_converter/context_mapper_integration.py": 80,
        }

        coverage_failures = []

        for module_path, min_coverage in critical_modules.items():
            if module_path in coverage_data["files"]:
                module_coverage = coverage_data["files"][module_path]["summary"][
                    "percent_covered"
                ]
                if module_coverage < min_coverage:
                    coverage_failures.append(
                        f"{module_path}: {module_coverage:.1f}% (required: {min_coverage}%)"
                    )

        # This assertion SHOULD FAIL on unfixed code - proving module-specific gaps exist
        assert not coverage_failures, (
            f"EXPECTED FAILURE: Critical modules have inadequate coverage:\n"
            + "\n".join(coverage_failures)
            + "\nThis confirms module-specific coverage gaps exist."
        )

    def test_test_fixture_directories_empty(self):
        """
        Test that test fixture directories are empty or missing.
        EXPECTED OUTCOME: Test FAILS (this confirms missing test infrastructure)
        """
        fixture_dirs = [
            Path("tests/fixtures/valid"),
            Path("tests/fixtures/invalid"),
            Path("tests/fixtures/expected"),
        ]

        missing_or_empty_dirs = []

        for fixture_dir in fixture_dirs:
            if not fixture_dir.exists():
                missing_or_empty_dirs.append(f"{fixture_dir}: Directory does not exist")
            elif not any(fixture_dir.iterdir()):
                missing_or_empty_dirs.append(f"{fixture_dir}: Directory is empty")

        # This assertion SHOULD FAIL on unfixed code - proving missing test infrastructure
        assert not missing_or_empty_dirs, (
            f"EXPECTED FAILURE: Test fixture directories are missing or empty:\n"
            + "\n".join(missing_or_empty_dirs)
            + "\nThis confirms missing test infrastructure."
        )

    def test_comprehensive_test_categories_missing(self):
        """
        Test that comprehensive test categories are missing.
        EXPECTED OUTCOME: Test FAILS (this confirms missing test types)
        """
        test_categories = {
            "tests/unit": "Unit tests directory",
            "tests/integration": "Integration tests directory",
            "tests/property": "Property-based tests directory",
            "tests/performance": "Performance tests directory",
        }

        missing_categories = []

        for test_dir, description in test_categories.items():
            test_path = Path(test_dir)
            if not test_path.exists():
                missing_categories.append(f"{test_dir}: {description} missing")
            elif not any(test_path.glob("test_*.py")):
                missing_categories.append(
                    f"{test_dir}: {description} has no test files"
                )

        # This assertion SHOULD FAIL on unfixed code - proving missing test categories
        assert not missing_categories, (
            f"EXPECTED FAILURE: Comprehensive test categories are missing:\n"
            + "\n".join(missing_categories)
            + "\nThis confirms missing test types."
        )

    @given(st.text(min_size=1, max_size=100))
    @settings(max_examples=5)
    def test_property_based_testing_infrastructure_missing(self, test_input):
        """
        Property-based test to validate that PBT infrastructure is missing.
        EXPECTED OUTCOME: Test FAILS (this confirms missing PBT setup)

        Note: Reduced to 5 examples for faster execution.
        """
        # Check if property-based tests exist for core modules
        pbt_files = [
            Path("tests/property/test_converter_properties.py"),
            Path("tests/property/test_validation_properties.py"),
        ]

        existing_pbt_files = [f for f in pbt_files if f.exists()]

        # This assertion SHOULD FAIL on unfixed code - proving missing PBT infrastructure
        assert len(existing_pbt_files) == len(pbt_files), (
            f"EXPECTED FAILURE: Property-based testing infrastructure missing. "
            f"Found {len(existing_pbt_files)} of {len(pbt_files)} expected PBT files. "
            f"This confirms missing PBT setup."
        )

    def tearDown(self):
        """Clean up coverage files after test."""
        coverage_files = ["coverage.json", ".coverage"]
        for file in coverage_files:
            if Path(file).exists():
                Path(file).unlink()


if __name__ == "__main__":
    # Run the bug condition exploration test
    pytest.main([__file__, "-v"])
