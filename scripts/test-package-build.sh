#!/bin/bash
# Script to test package building and installation locally

set -e  # Exit on error

echo "🔨 Testing Package Build and Installation"
echo "=========================================="
echo ""

# Clean previous builds
echo "📦 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info
echo "✅ Cleaned"
echo ""

# Install build tools
echo "🔧 Installing build tools..."
pip install --quiet --upgrade build twine
echo "✅ Build tools installed"
echo ""

# Build the package
echo "🏗️  Building package..."
python -m build
echo "✅ Package built"
echo ""

# Check the package
echo "🔍 Checking package..."
twine check dist/*
echo ""

# List built files
echo "📋 Built files:"
ls -lh dist/
echo ""

# Create test environment
echo "🧪 Creating test environment..."
python -m venv test-env
source test-env/bin/activate

# Install from wheel
echo "📥 Installing from wheel..."
pip install --quiet dist/*.whl

# Test CLI
echo "🧪 Testing CLI..."
echo ""
echo "  Testing --help:"
cml-convert --help
echo ""

echo "  Testing --version:"
cml-convert --version || echo "  (version command not implemented)"
echo ""

echo "  Testing validate:"
cml-convert validate examples/insurance-stage-1.json
echo ""

# Cleanup
echo "🧹 Cleaning up test environment..."
deactivate
rm -rf test-env
echo "✅ Cleaned up"
echo ""

echo "✅ All tests passed!"
echo ""
echo "📦 Package is ready for publication"
echo ""
echo "Next steps:"
echo "  1. Review the built files in dist/"
echo "  2. Test upload to TestPyPI (optional):"
echo "     twine upload --repository testpypi dist/*"
echo "  3. Upload to PyPI:"
echo "     twine upload dist/*"
echo "  4. Or create a GitHub release to trigger automatic upload"
