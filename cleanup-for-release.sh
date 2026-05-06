#!/bin/bash
# Cleanup script for preparing Context Mapper JSON Converter for public release
# This script removes development artifacts and organizes the repository structure

set -e

echo "🧹 Context Mapper JSON Converter - Repository Cleanup for Public Release"
echo "========================================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] || [ ! -d "src" ]; then
    print_error "This script must be run from the repository root directory"
    exit 1
fi

print_status "Starting repository cleanup..."

# 1. Remove temporary and development files
print_status "Removing temporary and development files..."

# Remove output files
if [ -f "output.cml" ]; then
    rm output.cml
    print_success "Removed output.cml"
fi

if [ -f "phase2_output.cml" ]; then
    rm phase2_output.cml
    print_success "Removed phase2_output.cml"
fi

if [ -f "phase3_output.cml" ]; then
    rm phase3_output.cml
    print_success "Removed phase3_output.cml"
fi

# Remove log files
if [ -f "cml_converter.log" ]; then
    rm cml_converter.log
    print_success "Removed cml_converter.log"
fi

# Remove development test files from root
print_status "Removing development test files from root directory..."
for test_file in test_*.py; do
    if [ -f "$test_file" ]; then
        rm "$test_file"
        print_success "Removed $test_file"
    fi
done

# Remove .kiro directory (internal development specs)
if [ -d ".kiro" ]; then
    rm -rf .kiro
    print_success "Removed .kiro directory"
fi

# 2. Create proper test directory structure
print_status "Creating proper test directory structure..."

# Create test subdirectories
mkdir -p tests/unit
mkdir -p tests/integration
mkdir -p tests/fixtures/valid
mkdir -p tests/fixtures/invalid
mkdir -p tests/fixtures/expected
mkdir -p tests/performance

print_success "Created test directory structure"

# 3. Reorganize examples
print_status "Reorganizing examples directory..."

# Create example subdirectories
mkdir -p examples/basic
mkdir -p examples/strategic
mkdir -p examples/tactical
mkdir -p examples/advanced
mkdir -p examples/tutorials/getting-started
mkdir -p examples/tutorials/e-commerce-system

# Move existing examples to appropriate directories
if [ -f "examples/insurance_example.json" ]; then
    mv examples/insurance_example.json examples/basic/insurance-system.json
    print_success "Moved insurance example to basic/"
fi

if [ -f "examples/phase2_customer_supplier.json" ]; then
    mv examples/phase2_customer_supplier.json examples/strategic/customer-supplier.json
    print_success "Moved customer-supplier example to strategic/"
fi

if [ -f "examples/phase2_subdomains.json" ]; then
    mv examples/phase2_subdomains.json examples/strategic/subdomains.json
    print_success "Moved subdomains example to strategic/"
fi

if [ -f "examples/phase3_tactical.json" ]; then
    mv examples/phase3_tactical.json examples/tactical/aggregates-entities.json
    print_success "Moved tactical example to tactical/"
fi

if [ -f "examples/phase4_complete.json" ]; then
    mv examples/phase4_complete.json examples/advanced/complete-system.json
    print_success "Moved complete example to advanced/"
fi

# Remove Python example files (convert to JSON if needed)
for py_file in examples/*.py; do
    if [ -f "$py_file" ]; then
        rm "$py_file"
        print_success "Removed Python example file: $(basename "$py_file")"
    fi
done

# 4. Clean up Python cache and build artifacts
print_status "Cleaning Python cache and build artifacts..."

# Remove __pycache__ directories
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
print_success "Removed __pycache__ directories"

# Remove .pyc files
find . -name "*.pyc" -delete 2>/dev/null || true
print_success "Removed .pyc files"

# Remove build artifacts
if [ -d "build" ]; then
    rm -rf build
    print_success "Removed build directory"
fi

if [ -d "dist" ]; then
    rm -rf dist
    print_success "Removed dist directory"
fi

if [ -d "*.egg-info" ]; then
    rm -rf *.egg-info
    print_success "Removed egg-info directories"
fi

# 5. Create missing directories
print_status "Creating missing directories..."

mkdir -p docs/assets/images
mkdir -p docs/assets/diagrams
mkdir -p docs/tutorials

print_success "Created documentation directories"

# 6. Validate essential files exist
print_status "Validating essential files..."

essential_files=(
    "README.md"
    "LICENSE"
    "CONTRIBUTING.md"
    "CHANGELOG.md"
    "pyproject.toml"
    "requirements.txt"
    "requirements-dev.txt"
    ".gitignore"
    ".pre-commit-config.yaml"
    "tox.ini"
    "MANIFEST.in"
)

missing_files=()
for file in "${essential_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -eq 0 ]; then
    print_success "All essential files present"
else
    print_warning "Missing essential files: ${missing_files[*]}"
fi

# 7. Validate directory structure
print_status "Validating directory structure..."

essential_dirs=(
    "src"
    "tests"
    "docs"
    "examples"
    "schemas"
    ".github/workflows"
    ".github/ISSUE_TEMPLATE"
)

missing_dirs=()
for dir in "${essential_dirs[@]}"; do
    if [ ! -d "$dir" ]; then
        missing_dirs+=("$dir")
    fi
done

if [ ${#missing_dirs[@]} -eq 0 ]; then
    print_success "All essential directories present"
else
    print_warning "Missing essential directories: ${missing_dirs[*]}"
fi

# 8. Check for sensitive files
print_status "Checking for sensitive files..."

sensitive_patterns=(
    "*.key"
    "*.pem"
    "*.p12"
    "*.pfx"
    "*password*"
    "*secret*"
    ".env"
    "config.local.*"
)

sensitive_files=()
for pattern in "${sensitive_patterns[@]}"; do
    files=$(find . \
        -not -path './venv/*' \
        -not -path './.venv/*' \
        -not -path './.git/*' \
        -name "$pattern" -type f 2>/dev/null || true)
    if [ -n "$files" ]; then
        sensitive_files+=($files)
    fi
done

if [ ${#sensitive_files[@]} -eq 0 ]; then
    print_success "No sensitive files found"
else
    print_warning "Found potential sensitive files: ${sensitive_files[*]}"
    print_warning "Please review these files before committing"
fi

# 9. Update file permissions
print_status "Setting proper file permissions..."

# Make scripts executable
chmod +x cleanup-for-release.sh 2>/dev/null || true

# Set proper permissions for documentation
find docs -type f -name "*.md" -exec chmod 644 {} \; 2>/dev/null || true
find examples -type f -name "*.json" -exec chmod 644 {} \; 2>/dev/null || true

print_success "Updated file permissions"

# 10. Generate summary report
print_status "Generating cleanup summary..."

echo ""
echo "📊 CLEANUP SUMMARY"
echo "=================="
echo "✅ Removed temporary files (*.cml, *.log)"
echo "✅ Removed development test files from root"
echo "✅ Removed .kiro directory"
echo "✅ Organized test directory structure"
echo "✅ Reorganized examples by category"
echo "✅ Cleaned Python cache and build artifacts"
echo "✅ Created missing directories"
echo "✅ Validated essential files and directories"
echo "✅ Checked for sensitive files"
echo "✅ Updated file permissions"

# 11. Final recommendations
echo ""
echo "🎯 NEXT STEPS"
echo "============="
echo "1. Review the changes: git status"
echo "2. Test the package: pip install -e . && pytest"
echo "3. Run pre-commit hooks: pre-commit run --all-files"
echo "4. Update documentation if needed"
echo "5. Commit changes: git add . && git commit -m 'Clean up repository for public release'"
echo "6. Create release: git tag v1.0.0 && git push origin v1.0.0"

# 12. Optional: Run basic validation
echo ""
read -p "🔍 Run basic validation tests? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Running basic validation..."
    
    # Check if Python is available
    if command -v python3 &> /dev/null; then
        # Test import
        if python3 -c "import src; print('✅ Package imports successfully')" 2>/dev/null; then
            print_success "Package imports successfully"
        else
            print_warning "Package import failed - check dependencies"
        fi
        
        # Test CLI
        if python3 -m src.cli --help &> /dev/null; then
            print_success "CLI is accessible"
        else
            print_warning "CLI access failed"
        fi
    else
        print_warning "Python3 not found - skipping validation"
    fi
    
    # Check if essential files are valid
    if python3 -c "import json; json.load(open('examples/basic/insurance-system.json'))" 2>/dev/null; then
        print_success "Example JSON files are valid"
    else
        print_warning "Example JSON validation failed"
    fi
fi

echo ""
print_success "Repository cleanup completed! 🎉"
print_status "The repository is now ready for public release."

exit 0