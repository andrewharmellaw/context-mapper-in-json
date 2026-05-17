# Publishing Guide

This guide explains how to publish the Context Mapper JSON Converter package to PyPI and set up all badges.

## Current Status

✅ **Fixed**:
- CI badge (points to correct repository)
- License badge (working)
- Python version badge (static, shows 3.8+)

⏳ **Pending Setup**:
- Codecov badge (requires account setup)
- PyPI badges (requires package publication)

## Phase 1: Fix Repository Badges (✅ Complete)

The README badges have been updated to point to the correct repository:
- Changed from `ContextMapper/context-mapper-json-converter`
- To `andrewharmellaw/context-mapper-in-json`

## Phase 2: Setup Codecov

### Step 1: Create Codecov Account

1. Go to https://codecov.io
2. Sign in with your GitHub account
3. Authorize Codecov to access your repositories

### Step 2: Add Repository

1. In Codecov dashboard, click "Add new repository"
2. Find and select `andrewharmellaw/context-mapper-in-json`
3. Copy the repository upload token (if shown)

### Step 3: Configure GitHub (if needed)

For public repositories, no token is usually needed. For private repositories:

1. Go to your GitHub repository settings
2. Navigate to Secrets and variables → Actions
3. Add a new secret named `CODECOV_TOKEN`
4. Paste the token from Codecov

### Step 4: Update CI Workflow (if needed)

If using a private repository, update `.github/workflows/ci.yml`:

```yaml
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v4
  with:
    file: ./coverage.xml
    flags: unittests
    name: codecov-umbrella
    fail_ci_if_error: false
    token: ${{ secrets.CODECOV_TOKEN }}  # Add this line for private repos
```

### Step 5: Verify

1. Push changes to trigger CI
2. Check Codecov dashboard for coverage reports
3. Verify badge shows coverage percentage

## Phase 3: Prepare Package for PyPI

### Step 1: Review Package Metadata

Check `pyproject.toml` for:
- ✅ Package name: `context-mapper-json-converter`
- ✅ Version: `1.0.0`
- ✅ Description
- ✅ License: MIT
- ✅ Python version: >=3.8
- ✅ Dependencies
- ✅ Entry points: `cml-convert`

### Step 2: Build Package Locally

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# This creates:
# - dist/context_mapper_json_converter-1.0.0-py3-none-any.whl
# - dist/context-mapper-json-converter-1.0.0.tar.gz
```

### Step 3: Check Package

```bash
# Check package for errors
twine check dist/*

# Should output:
# Checking dist/context_mapper_json_converter-1.0.0-py3-none-any.whl: PASSED
# Checking dist/context-mapper-json-converter-1.0.0.tar.gz: PASSED
```

### Step 4: Test Installation Locally

```bash
# Create a test virtual environment
python -m venv test-env
source test-env/bin/activate  # On Windows: test-env\Scripts\activate

# Install from the built wheel
pip install dist/context_mapper_json_converter-1.0.0-py3-none-any.whl

# Test the CLI
cml-convert --help

# Test validation
cml-convert validate examples/insurance-stage-1.json

# Deactivate and clean up
deactivate
rm -rf test-env
```

## Phase 4: Publish to PyPI

### Step 1: Create PyPI Account

1. Go to https://pypi.org
2. Click "Register" and create an account
3. Verify your email address

### Step 2: Create API Token

1. Log in to PyPI
2. Go to Account Settings → API tokens
3. Click "Add API token"
4. Name: `context-mapper-json-converter-upload`
5. Scope: "Entire account" (or specific project after first upload)
6. Copy the token (starts with `pypi-`)

### Step 3: Add Token to GitHub

1. Go to your GitHub repository
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `PYPI_API_TOKEN`
5. Value: Paste the PyPI token
6. Click "Add secret"

### Step 4: Test Upload to TestPyPI (Optional but Recommended)

```bash
# Create TestPyPI account at https://test.pypi.org
# Create API token for TestPyPI

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ context-mapper-json-converter

# If successful, proceed to real PyPI
```

### Step 5: Manual Upload to PyPI

```bash
# Upload to PyPI
twine upload dist/*

# Enter your PyPI credentials or use token:
# Username: __token__
# Password: <your-pypi-token>
```

### Step 6: Automated Publishing via GitHub Release

The repository includes `.github/workflows/publish-pypi.yml` which automatically publishes to PyPI when you create a GitHub release.

**To publish a new version**:

1. Update version in `pyproject.toml`
2. Commit and push changes
3. Create a new release on GitHub:
   - Go to repository → Releases → "Create a new release"
   - Tag: `v1.0.0` (match version in pyproject.toml)
   - Title: `Release 1.0.0`
   - Description: Release notes
   - Click "Publish release"
4. GitHub Actions will automatically build and publish to PyPI

### Step 7: Add PyPI Badges to README

After successful publication, add these badges back to README.md:

```markdown
[![PyPI version](https://badge.fury.io/py/context-mapper-json-converter.svg)](https://badge.fury.io/py/context-mapper-json-converter)
[![Python versions](https://img.shields.io/pypi/pyversions/context-mapper-json-converter.svg)](https://pypi.org/project/context-mapper-json-converter/)
[![Downloads](https://pepy.tech/badge/context-mapper-json-converter)](https://pepy.tech/project/context-mapper-json-converter)
```

### Step 8: Update Installation Instructions

After publishing, update README.md:

```markdown
### Installation

```bash
# Install from PyPI (recommended)
pip install context-mapper-json-converter

# Or install from source
git clone https://github.com/andrewharmellaw/context-mapper-in-json.git
cd context-mapper-in-json
pip install -e .
```
```

## Phase 5: Verify Everything Works

### Checklist

- [ ] CI badge shows passing status
- [ ] Codecov badge shows coverage percentage
- [ ] PyPI version badge shows current version
- [ ] Python versions badge shows supported versions
- [ ] License badge shows MIT
- [ ] Package installs from PyPI: `pip install context-mapper-json-converter`
- [ ] CLI works: `cml-convert --help`
- [ ] Validation works: `cml-convert validate examples/insurance-stage-1.json`

## Troubleshooting

### CI Badge Shows "Unknown"

- Verify the workflow file is named `ci.yml` (not `CI.yml`)
- Check that the workflow has run at least once
- Ensure the badge URL matches your repository path

### Codecov Badge Shows "Unknown"

- Verify Codecov account is set up
- Check that coverage.xml is being uploaded
- Ensure the repository is added to Codecov
- Wait a few minutes for Codecov to process the upload

### PyPI Upload Fails

**"Invalid or non-existent authentication information"**
- Verify the API token is correct
- Ensure token is added to GitHub Secrets correctly
- Check token hasn't expired

**"File already exists"**
- You cannot re-upload the same version
- Increment version in `pyproject.toml`
- Build and upload again

**"Package name already taken"**
- The package name is already used on PyPI
- Choose a different name in `pyproject.toml`
- Update all references to the new name

### Package Installation Fails

**"No matching distribution found"**
- Verify package was uploaded successfully
- Check PyPI page: https://pypi.org/project/context-mapper-json-converter/
- Wait a few minutes for PyPI to index the package

**"Command 'cml-convert' not found"**
- Verify entry point in `pyproject.toml`
- Reinstall the package: `pip install --force-reinstall context-mapper-json-converter`
- Check PATH includes Python scripts directory

## Version Management

### Semantic Versioning

Follow semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes (e.g., 1.0.0 → 2.0.0)
- **MINOR**: New features, backward compatible (e.g., 1.0.0 → 1.1.0)
- **PATCH**: Bug fixes, backward compatible (e.g., 1.0.0 → 1.0.1)

### Release Process

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md` with changes
3. Commit: `git commit -m "Bump version to X.Y.Z"`
4. Tag: `git tag vX.Y.Z`
5. Push: `git push && git push --tags`
6. Create GitHub release (triggers automatic PyPI upload)

## Maintenance

### Updating the Package

1. Make changes to code
2. Update tests
3. Update documentation
4. Bump version
5. Create release
6. Verify PyPI publication

### Monitoring

- **PyPI Stats**: https://pypistats.org/packages/context-mapper-json-converter
- **GitHub Insights**: Repository → Insights
- **Codecov Reports**: https://codecov.io/gh/andrewharmellaw/context-mapper-in-json

## Resources

- [PyPI Publishing Guide](https://packaging.python.org/tutorials/packaging-projects/)
- [Codecov Documentation](https://docs.codecov.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Semantic Versioning](https://semver.org/)
