#!/usr/bin/env python3
"""
Command-line interface for Context Mapper JSON Converter
"""

import json
import logging
import sys
from pathlib import Path
from typing import Optional

import click

from .cml_validator import CMLValidator
from .config import setup_logging
from .context_mapper_integration import ContextMapperIntegration, ContextMapperWorkflow
from .converter import ConverterEngine
from .round_trip_validator import RoundTripValidator
from .validation import ValidationEngine


@click.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.argument("output_file", type=click.Path(path_type=Path), required=False)
@click.option(
    "--validate-only", "-v", is_flag=True, help="Only validate JSON, do not convert"
)
@click.option("--skip-cml-validation", is_flag=True, help="Skip CML output validation")
@click.option(
    "--enable-round-trip", is_flag=True, help="Enable round-trip validation (Phase 4)"
)
@click.option(
    "--use-context-mapper-cli",
    is_flag=True,
    help="Use Context Mapper CLI for validation (Phase 4)",
)
@click.option(
    "--generate-artifacts",
    multiple=True,
    help="Generate artifacts using Context Mapper (plantuml, mdsl, etc.)",
)
@click.option("--verbose", is_flag=True, help="Enable verbose logging")
@click.option(
    "--format-output",
    is_flag=True,
    default=True,
    help="Format CML output (default: True)",
)
def convert(
    input_file: Path,
    output_file: Optional[Path],
    validate_only: bool,
    skip_cml_validation: bool,
    enable_round_trip: bool,
    use_context_mapper_cli: bool,
    generate_artifacts: tuple,
    verbose: bool,
    format_output: bool,
) -> None:
    """
    Convert JSON definitions to Context Mapper DSL (CML) code.

    INPUT_FILE: Path to JSON file containing Context Map and Bounded Context definitions
    OUTPUT_FILE: Path to output CML file (optional, defaults to stdout)
    """

    # Set up logging
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(log_level)
    logger = logging.getLogger(__name__)

    try:
        # Read and parse JSON input
        logger.info(f"Reading JSON input from {input_file}")
        with open(input_file, "r", encoding="utf-8") as f:
            json_data = json.load(f)

        # Initialize validation engine
        validator = ValidationEngine()

        # Initialize Phase 4 components if needed
        round_trip_validator = None
        context_mapper_integration = None

        if enable_round_trip:
            round_trip_validator = RoundTripValidator()
            logger.info("Round-trip validation enabled")

        if use_context_mapper_cli or generate_artifacts:
            context_mapper_integration = ContextMapperIntegration()
            logger.info("Context Mapper CLI integration enabled")

        # Validate JSON schema
        logger.info("Validating JSON schema...")
        schema_result = validator.validate_json_schema(json_data)

        if not schema_result.is_valid:
            click.echo("❌ JSON Schema Validation Failed:", err=True)
            for error in schema_result.errors:
                click.echo(f"  • {error}", err=True)

            # Show suggestions
            suggestions = validator.get_validation_suggestions(schema_result.errors)
            if suggestions:
                click.echo("\n💡 Suggestions:", err=True)
                for suggestion in suggestions:
                    click.echo(f"  • {suggestion}", err=True)

            sys.exit(1)

        logger.info("JSON schema validation passed")

        # Validate semantic rules
        logger.info("Validating semantic rules...")
        semantic_result = validator.validate_semantic_rules(json_data)

        if not semantic_result.is_valid:
            click.echo("❌ Semantic Validation Failed:", err=True)
            for error in semantic_result.errors:
                click.echo(f"  • {error}", err=True)
            sys.exit(1)

        logger.info("Semantic validation passed")

        # Show warnings if any
        all_warnings = schema_result.warnings + semantic_result.warnings
        if all_warnings:
            click.echo("⚠️  Warnings:", err=True)
            for warning in all_warnings:
                click.echo(f"  • {warning}", err=True)

        # If validate-only mode, stop here
        if validate_only:
            click.echo("✅ JSON validation completed successfully")
            return

        # Convert to CML
        logger.info("Converting JSON to CML...")
        converter = ConverterEngine()
        cml_output = converter.convert(json_data)

        logger.info("JSON to CML conversion completed")

        # Validate generated CML (unless skipped)
        if not skip_cml_validation:
            logger.info("Validating generated CML...")
            cml_validator = CMLValidator()
            cml_result = cml_validator.validate_syntax(cml_output)

            if not cml_result.is_valid:
                click.echo("❌ Generated CML Validation Failed:", err=True)
                for error in cml_result.errors:
                    click.echo(f"  • {error}", err=True)
                sys.exit(1)

            if cml_result.warnings:
                click.echo("⚠️  CML Warnings:", err=True)
                for warning in cml_result.warnings:
                    click.echo(f"  • {warning}", err=True)

            logger.info("CML validation passed")

        # Phase 4: Context Mapper CLI validation (if enabled)
        if use_context_mapper_cli and context_mapper_integration:
            logger.info("Validating with Context Mapper CLI...")
            cli_result = context_mapper_integration.validate_cml_with_cli(cml_output)

            if not cli_result.is_valid:
                click.echo("❌ Context Mapper CLI Validation Failed:", err=True)
                for error in cli_result.errors:
                    click.echo(f"  • {error}", err=True)
            else:
                click.echo("✅ Context Mapper CLI validation passed")

            if cli_result.warnings:
                click.echo("⚠️  Context Mapper CLI Warnings:", err=True)
                for warning in cli_result.warnings:
                    click.echo(f"  • {warning}", err=True)

        # Phase 4: Round-trip validation (if enabled)
        if enable_round_trip and round_trip_validator:
            logger.info("Performing round-trip validation...")
            round_trip_result = round_trip_validator.validate_round_trip(
                json_data, cml_output
            )

            if not round_trip_result.is_valid:
                click.echo("❌ Round-Trip Validation Failed:", err=True)
                for error in round_trip_result.errors:
                    click.echo(f"  • {error}", err=True)
            else:
                click.echo("✅ Round-trip validation passed")

            if round_trip_result.warnings:
                click.echo("⚠️  Round-Trip Warnings:", err=True)
                for warning in round_trip_result.warnings:
                    click.echo(f"  • {warning}", err=True)

        # Output CML
        if output_file:
            logger.info(f"Writing CML output to {output_file}")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(cml_output)
            click.echo(f"✅ CML output written to {output_file}")
        else:
            click.echo("Generated CML:")
            click.echo("=" * 50)
            click.echo(cml_output)
            click.echo("=" * 50)

        # Phase 4: Generate artifacts (if requested)
        if generate_artifacts and context_mapper_integration:
            click.echo(f"\n🔧 Generating artifacts...")
            for generator in generate_artifacts:
                logger.info(f"Generating {generator} artifacts...")
                gen_result = context_mapper_integration.generate_artifacts(
                    cml_output, generator
                )

                if gen_result.is_valid:
                    click.echo(f"✅ {generator} artifacts generated successfully")
                else:
                    click.echo(f"❌ {generator} artifact generation failed:", err=True)
                    for error in gen_result.errors:
                        click.echo(f"  • {error}", err=True)

                if gen_result.warnings:
                    for warning in gen_result.warnings:
                        click.echo(f"  ℹ️  {warning}")

        # Show summary
        context_map_count = 1 if "contextMap" in json_data else 0
        bounded_context_count = len(json_data.get("boundedContexts", []))
        relationship_count = len(
            json_data.get("contextMap", {}).get("relationships", [])
        )
        aggregate_count = sum(
            len(bc.get("aggregates", [])) for bc in json_data.get("boundedContexts", [])
        )

        click.echo(f"\n📊 Conversion Summary:")
        click.echo(f"  • Context Maps: {context_map_count}")
        click.echo(f"  • Bounded Contexts: {bounded_context_count}")
        click.echo(f"  • Relationships: {relationship_count}")
        if aggregate_count > 0:
            click.echo(f"  • Aggregates: {aggregate_count}")

        # Phase 4 summary
        if enable_round_trip:
            click.echo(f"  • Round-trip validation: ✅")
        if use_context_mapper_cli:
            click.echo(f"  • Context Mapper CLI: ✅")
        if generate_artifacts:
            click.echo(f"  • Generated artifacts: {', '.join(generate_artifacts)}")

    except json.JSONDecodeError as e:
        click.echo(f"❌ Invalid JSON in {input_file}: {e}", err=True)
        sys.exit(1)
    except FileNotFoundError:
        click.echo(f"❌ File not found: {input_file}", err=True)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        click.echo(f"❌ Unexpected error: {e}", err=True)
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


@click.group()
def main() -> None:
    """Context Mapper JSON Converter - Convert JSON definitions to CML code."""
    pass


@main.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
def validate(input_file: Path) -> None:
    """Validate JSON file without conversion."""
    convert.callback(input_file, None, True, False, False, True, (), False, True)  # type: ignore[misc]


@main.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
def round_trip(input_file: Path) -> None:
    """Test round-trip validation: JSON → CML → JSON comparison."""
    setup_logging("INFO")
    logger = logging.getLogger(__name__)

    try:
        # Read JSON
        with open(input_file, "r", encoding="utf-8") as f:
            json_data = json.load(f)

        # Convert to CML
        converter = ConverterEngine()
        cml_output = converter.convert(json_data)

        # Perform round-trip validation
        round_trip_validator = RoundTripValidator()
        result = round_trip_validator.validate_round_trip(json_data, cml_output)

        if result.is_valid:
            click.echo("✅ Round-trip validation PASSED")
        else:
            click.echo("❌ Round-trip validation FAILED")
            for error in result.errors:
                click.echo(f"  • {error}")

        if result.warnings:
            click.echo("⚠️  Warnings:")
            for warning in result.warnings:
                click.echo(f"  • {warning}")

    except Exception as e:
        click.echo(f"❌ Round-trip validation error: {e}", err=True)


@main.command()
def integration_status() -> None:
    """Show Context Mapper integration status."""
    integration = ContextMapperIntegration()
    status = integration.get_integration_status()

    click.echo("🔧 Context Mapper Integration Status\n")

    click.echo(f"Tools Available: {status['tools_available']}")
    click.echo(f"Integration Ready: {'✅' if status['integration_ready'] else '❌'}")

    click.echo("\nDetected Tools:")
    for tool_id, tool_info in status["tools_detected"].items():
        status_icon = "✅" if tool_info["available"] else "❌"
        version = tool_info["version"] if tool_info["available"] else "Not available"
        click.echo(f"  {status_icon} {tool_id}: {version}")

    if status["recommended_setup"]:
        click.echo("\nRecommended Setup:")
        for recommendation in status["recommended_setup"]:
            click.echo(f"  • {recommendation}")


@main.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--generator",
    "-g",
    multiple=True,
    default=["plantuml"],
    help="Artifact generators to run (plantuml, mdsl, etc.)",
)
def generate(input_file: Path, generator: tuple) -> None:
    """Generate artifacts from JSON using Context Mapper tools."""
    setup_logging("INFO")

    try:
        # Read JSON
        with open(input_file, "r", encoding="utf-8") as f:
            json_data = json.load(f)

        # Use workflow for complete generation
        workflow = ContextMapperWorkflow()
        results = workflow.validate_and_generate_workflow(json_data, list(generator))

        # Report results
        for step, result in results.items():
            if step == "artifact_generation":
                for gen_type, gen_result in result.items():
                    if gen_result.is_valid:
                        click.echo(f"✅ {gen_type} artifacts generated")
                    else:
                        click.echo(f"❌ {gen_type} generation failed")
                        for error in gen_result.errors:
                            click.echo(f"  • {error}")
            elif not result.is_valid:
                click.echo(f"❌ {step} failed")
                for error in result.errors:
                    click.echo(f"  • {error}")
                return

    except Exception as e:
        click.echo(f"❌ Generation error: {e}", err=True)


@main.command()
def version() -> None:
    """Show version information."""
    from . import __version__

    click.echo(f"Context Mapper JSON Converter v{__version__}")


# Add the convert command to the main group
main.add_command(convert)


if __name__ == "__main__":
    main()
