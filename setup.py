#!/usr/bin/env python3
"""Setup script for Context Mapper JSON Converter."""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# Get version from package
def get_version():
    version_file = os.path.join("src", "__init__.py")
    with open(version_file, "r", encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    return "0.1.0"

setup(
    name="context-mapper-json-converter",
    version=get_version(),
    author="Context Mapper JSON Converter Contributors",
    author_email="maintainers@context-mapper-converter.com",
    description="Convert JSON definitions to Context Mapper DSL (CML) code with comprehensive validation",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/ContextMapper/context-mapper-json-converter",
    project_urls={
        "Bug Reports": "https://github.com/ContextMapper/context-mapper-json-converter/issues",
        "Source": "https://github.com/ContextMapper/context-mapper-json-converter",
        "Documentation": "https://github.com/ContextMapper/context-mapper-json-converter/blob/main/docs/README.md",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "isort>=5.12.0",
            "pre-commit>=3.0.0",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.2.0",
            "myst-parser>=1.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "hypothesis>=6.70.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "cml-convert=src.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.yaml", "*.yml"],
    },
    keywords=[
        "context-mapper",
        "domain-driven-design",
        "ddd",
        "json",
        "cml",
        "converter",
        "validation",
        "bounded-context",
        "context-map",
    ],
    zip_safe=False,
)