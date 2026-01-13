# Publishing wizelit-sdk - Complete Guide

This comprehensive guide shows you how to create and publish your `wizelit-sdk` utility code internally via private Git repository for your team to install into their projects, using `uv` for virtual environment management.

---

## Table of Contents

1. [Project Structure](#1-project-structure)
2. [Install Tools](#2-install-tools)
3. [Create Project Files](#3-create-project-files)
4. [Initialize Git Repository](#4-initialize-git-repository)
5. [Publishing Workflow](#5-publishing-workflow)
6. [Team Installation Guide](#6-team-installation-guide)
7. [Development Workflow](#7-development-workflow)
8. [Troubleshooting](#8-troubleshooting)
9. [Quick Reference](#9-quick-reference)

---

## 1. Project Structure

Set up your project with this structure:

```
wizelit-sdk/
├── Makefile                    # Build and publish automation
├── pyproject.toml              # Package configuration
├── README.md                   # Package documentation
├── CHANGELOG.md                # Version history
├── .gitignore                  # Git ignore rules
├── src/
│   └── wizelit_agent_wrapper/
│       ├── __init__.py
│       └── your_code.py
└── tests/
    └── test_your_code.py
```

---

## 2. Install Tools

### Install uv

```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip
pip install uv
```

### Verify Installation

```bash
uv --version
```

---

## 3. Create Project Files

### 3.1 Create Directory Structure

```bash
mkdir -p wizelit-sdk/src/wizelit_agent_wrapper
mkdir -p wizelit-sdk/tests
cd wizelit-sdk
```

### 3.2 Create `pyproject.toml`

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "wizelit-sdk"
version = "0.1.0"
description = "Wizelit Agent Wrapper - Internal utility package"
readme = "README.md"
requires-python = ">=3.8"
authors = [
    {name = "Your Name", email = "your.email@company.com"}
]
dependencies = [
    # Add your dependencies here
    # "requests>=2.28.0",
    # "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "black>=22.0.0",
    "ruff>=0.1.0",
    "build>=1.0.0",
]

[tool.hatch.build.targets.wheel]
packages = ["src/wizelit_agent_wrapper"]

[tool.black]
line-length = 88
target-version = ['py38']

[tool.ruff]
line-length = 88
target-version = "py38"
```

### 3.3 Create `.gitignore`

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
.venv/
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Testing
.pytest_cache/
.coverage
htmlcov/

# OS
.DS_Store
Thumbs.db
```

### 3.4 Create `README.md`

```markdown
# wizelit-sdk

Internal utility package for Wizelit Agent operations.

## Installation

### Install from Git Repository

```bash
# Install latest version from main branch
uv pip install git+https://github.com/your-org/wizelit-sdk.git

# Install specific version
uv pip install git+https://github.com/your-org/wizelit-sdk.git@v0.1.0

# Install with SSH (Recommended for Private Repos)
uv pip install git+ssh://git@github.com/your-org/wizelit-sdk.git@v0.1.0
```

### Add to pyproject.toml

```toml
[project]
dependencies = [
    "wizelit-sdk @ git+ssh://git@github.com/your-org/wizelit-sdk.git@v0.1.0"
]
```

## Usage

```python
from wizelit_agent_wrapper import your_module

# Use the wrapper
result = your_module.function()
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/your-org/wizelit-sdk.git
cd wizelit-sdk

# Set up environment
make setup

# Activate virtual environment
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install in development mode
make install-dev
```

### Available Make Commands

```bash
make setup          # Set up development environment
make install-dev    # Install in development mode
make test           # Run tests
make format         # Format code with black
make lint           # Lint code with ruff
make check          # Run tests and linting
make clean          # Clean build artifacts
make build          # Build package
make release        # Create new release (interactive)
make tag VERSION=x.x.x  # Create specific version tag
make push           # Push code and tags
make version        # Show current version
make versions       # List all available versions
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and linting: `make check`
4. Commit your changes
5. Push and create a pull request

## Versioning

We use [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality (backward compatible)
- **PATCH** version for bug fixes

See [CHANGELOG.md](CHANGELOG.md) for version history.
```

### 3.5 Create `CHANGELOG.md`

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release

## [0.1.0] - 2025-01-13

### Added
- Initial package structure
- Core wrapper functionality

[Unreleased]: https://github.com/your-org/wizelit-sdk/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/your-org/wizelit-sdk/releases/tag/v0.1.0
```

### 3.6 Create `Makefile`

```makefile
.PHONY: help setup install install-dev test lint format clean build release tag push check-version

# Default target
help:
	@echo "Available commands:"
	@echo "  make setup          - Set up development environment"
	@echo "  make install        - Install package in production mode"
	@echo "  make install-dev    - Install package in development mode"
	@echo "  make test           - Run tests"
	@echo "  make lint           - Run code linting"
	@echo "  make format         - Format code with black"
	@echo "  make check          - Run tests and linting"
	@echo "  make clean          - Remove build artifacts"
	@echo "  make build          - Build package"
	@echo "  make release        - Create new release (updates version, changelog, tags)"
	@echo "  make tag VERSION=x.x.x - Create and push git tag"
	@echo "  make push           - Push code and tags to remote"
	@echo "  make version        - Show current version"
	@echo "  make versions       - List all available versions"

# Set up development environment
setup:
	@echo "Setting up development environment..."
	uv venv
	@echo "Virtual environment created. Activate it with:"
	@echo "  source .venv/bin/activate  (Linux/Mac)"
	@echo "  .venv\\Scripts\\activate     (Windows)"
	@echo ""
	@echo "Then run: make install-dev"

# Install package in production mode
install:
	@echo "Installing package..."
	uv pip install .

# Install package in development mode with dev dependencies
install-dev:
	@echo "Installing package in development mode..."
	uv pip install -e ".[dev]"

# Run tests
test:
	@echo "Running tests..."
	pytest tests/ -v

# Run code linting
lint:
	@echo "Running linting checks..."
	ruff check src/
	@echo "Running type checks..."
	-mypy src/ 2>/dev/null || echo "mypy not installed, skipping type checks"

# Format code
format:
	@echo "Formatting code..."
	black src/ tests/
	ruff check --fix src/

# Run all checks
check: test lint
	@echo "All checks passed!"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	@echo "Clean complete!"

# Build package
build: clean
	@echo "Building package..."
	python -m build
	@echo "Build complete! Files in dist/"

# Check if VERSION is provided
check-version:
ifndef VERSION
	$(error VERSION is not set. Use: make tag VERSION=0.1.0)
endif

# Create git tag
tag: check-version
	@echo "Creating tag v$(VERSION)..."
	@if git rev-parse v$(VERSION) >/dev/null 2>&1; then \
		echo "Error: Tag v$(VERSION) already exists!"; \
		exit 1; \
	fi
	git tag -a v$(VERSION) -m "Release version $(VERSION)"
	@echo "Tag v$(VERSION) created successfully!"
	@echo "Push with: make push"

# Push code and tags to remote
push:
	@echo "Pushing code and tags to remote..."
	git push origin $$(git branch --show-current)
	git push origin --tags
	@echo "Push complete!"

# Interactive release process
release:
	@echo "=== Release Process ==="
	@echo ""
	@echo "Current version in pyproject.toml:"
	@grep "^version = " pyproject.toml || echo "Version not found!"
	@echo ""
	@read -p "Enter new version (e.g., 0.2.0): " version; \
	if [ -z "$$version" ]; then \
		echo "Error: Version cannot be empty"; \
		exit 1; \
	fi; \
	echo ""; \
	echo "Steps to be performed:"; \
	echo "  1. Update version in pyproject.toml to $$version"; \
	echo "  2. You must manually update CHANGELOG.md"; \
	echo "  3. Run tests and linting"; \
	echo "  4. Commit changes"; \
	echo "  5. Create git tag v$$version"; \
	echo "  6. Push to remote"; \
	echo ""; \
	read -p "Continue? [y/N] " confirm; \
	if [ "$$confirm" != "y" ] && [ "$$confirm" != "Y" ]; then \
		echo "Release cancelled."; \
		exit 0; \
	fi; \
	echo ""; \
	echo "Updating version in pyproject.toml..."; \
	sed -i.bak "s/^version = \".*\"/version = \"$$version\"/" pyproject.toml && rm pyproject.toml.bak || \
	sed -i "" "s/^version = \".*\"/version = \"$$version\"/" pyproject.toml; \
	echo "Version updated to $$version"; \
	echo ""; \
	echo "IMPORTANT: Please update CHANGELOG.md now!"; \
	echo "Press Enter when you've updated CHANGELOG.md..."; \
	read; \
	echo ""; \
	echo "Running tests and linting..."; \
	make check || exit 1; \
	echo ""; \
	echo "Committing changes..."; \
	git add pyproject.toml CHANGELOG.md; \
	git commit -m "Release version $$version" || exit 1; \
	echo ""; \
	echo "Creating tag v$$version..."; \
	git tag -a v$$version -m "Release version $$version"; \
	echo ""; \
	echo "Pushing to remote..."; \
	git push origin $$(git branch --show-current); \
	git push origin v$$version; \
	echo ""; \
	echo "=== Release $$version complete! ==="; \
	echo ""; \
	echo "Team members can now install with:"; \
	echo "  uv pip install git+ssh://git@github.com/your-org/wizelit-sdk.git@v$$version"

# Show current version
version:
	@grep "^version = " pyproject.toml | sed 's/version = //g' | tr -d '"'

# List all available versions (tags)
versions:
	@echo "Available versions:"
	@git tag -l "v*" | sort -V
```

### 3.7 Create `src/wizelit_agent_wrapper/__init__.py`

```python
"""Wizelit Agent Wrapper - Internal utility package."""

__version__ = "0.1.0"

# Import your main modules here
# from .your_module import your_function
```

### 3.8 Create a Sample Test `tests/test_example.py`

```python
"""Example test file."""

import pytest
from wizelit_agent_wrapper import __version__


def test_version():
    """Test that version is defined."""
    assert __version__ == "0.1.0"


def test_example():
    """Example test case."""
    assert True
```

---

## 4. Initialize Git Repository

### 4.1 Local Git Setup

```bash
# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Project structure"
```

### 4.2 Configure SSH for Private Repository

```bash
# Generate SSH key if you don't have one
ssh-keygen -t ed25519 -C "your.email@company.com"

# Start ssh-agent
eval "$(ssh-agent -s)"

# Add SSH key to agent
ssh-add ~/.ssh/id_ed25519

# Copy public key to clipboard (add to GitHub/GitLab)
cat ~/.ssh/id_ed25519.pub
```

**Add your SSH public key to:**
- GitHub: Settings → SSH and GPG keys → New SSH key
- GitLab: Preferences → SSH Keys → Add new key

### 4.3 Connect to Remote Repository

```bash
# Create repository on GitHub/GitLab first, then:

# Add remote repository
git remote add origin git@github.com:your-org/wizelit-sdk.git

# Push to remote
git push -u origin main
```

---

## 5. Publishing Workflow

### 5.1 Initial Setup

```bash
# Set up development environment
make setup

# Activate virtual environment
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install in development mode
make install-dev
```

### 5.2 Development Process

```bash
# Make your changes to code...

# Run tests
make test

# Format code
make format

# Run linting
make lint

# Or run everything at once
make check
```

### 5.3 Create First Release

```bash
# Interactive release (recommended)
make release

# This will:
# 1. Prompt for new version number
# 2. Update pyproject.toml
# 3. Prompt you to update CHANGELOG.md
# 4. Run tests and linting
# 5. Commit changes
# 6. Create git tag
# 7. Push everything to remote
```

### 5.4 Manual Release (Alternative)

```bash
# 1. Update version in pyproject.toml
# version = "0.1.0"

# 2. Update CHANGELOG.md with changes

# 3. Run tests and linting
make check

# 4. Commit changes
git add pyproject.toml CHANGELOG.md
git commit -m "Release version 0.1.0"

# 5. Create and push tag
make tag VERSION=0.1.0
make push
```

### 5.5 Subsequent Releases

```bash
# For version 0.2.0
make release
# Enter: 0.2.0
# Update CHANGELOG.md when prompted
# Confirm to proceed

# Done! Team can now install v0.2.0
```

---

## 6. Team Installation Guide

Share this section with your team members.

### 6.1 Prerequisites

**Install uv:**
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Configure SSH (for private repositories):**
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your.email@company.com"

# Add to ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Add public key to GitHub/GitLab
cat ~/.ssh/id_ed25519.pub
```

### 6.2 Install Package in Your Project

**Method 1: Direct Installation**
```bash
# Create project directory
mkdir my-project
cd my-project

# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install wizelit-sdk
uv pip install git+ssh://git@github.com/your-org/wizelit-sdk.git@v0.1.0
```

**Method 2: Add to pyproject.toml**
```toml
[project]
name = "my-project"
version = "0.1.0"
dependencies = [
    "wizelit-sdk @ git+ssh://git@github.com/your-org/wizelit-sdk.git@v0.1.0",
]
```

Then install:
```bash
uv pip install -e .
```

### 6.3 Using the Package

```python
from wizelit_agent_wrapper import your_module

# Use the functionality
result = your_module.function()
print(result)
```

### 6.4 Updating to New Version

```bash
# Check available versions
git ls-remote --tags git@github.com:your-org/wizelit-sdk.git

# Update to specific version
uv pip install --upgrade git+ssh://git@github.com:your-org/wizelit-sdk.git@v0.2.0

# Or update to latest
uv pip install --upgrade git+ssh://git@github.com:your-org/wizelit-sdk.git
```

---

## 7. Development Workflow

### 7.1 Working on Features

```bash
# Create feature branch
git checkout -b feature/new-functionality

# Make changes to code
# ...

# Run tests and linting
make check

# Commit changes
git add .
git commit -m "Add new functionality"

# Push branch
git push origin feature/new-functionality

# Create pull request on GitHub/GitLab
```

### 7.2 Review and Merge

```bash
# After PR approval, merge to main
git checkout main
git pull origin main

# Create new release
make release
```

### 7.3 Hotfix Process

```bash
# Create hotfix branch from main
git checkout main
git checkout -b hotfix/critical-bug

# Fix the bug
# ...

# Test the fix
make check

# Commit and push
git add .
git commit -m "Fix critical bug"
git push origin hotfix/critical-bug

# After PR approval, create patch release
git checkout main
git pull origin main
make release  # Enter patch version, e.g., 0.1.1
```

---

## 8. Troubleshooting

### 8.1 Authentication Issues

**Problem: Permission denied (publickey)**
```bash
# Test SSH connection
ssh -T git@github.com

# If failed, add SSH key
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Verify key is added
ssh-add -l
```

**Problem: HTTPS authentication failing**
```bash
# Solution: Switch to SSH
uv pip install git+ssh://git@github.com/your-org/wizelit-sdk.git@v0.1.0
```

### 8.2 Import Errors

**Problem: Module not found after installation**
```bash
# Check if installed
uv pip list | grep wizelit-sdk

# Verify installation location
uv pip show wizelit-sdk

# Reinstall
uv pip install --force-reinstall git+ssh://git@github.com/your-org/wizelit-sdk.git@v0.1.0
```

**Problem: Wrong module imported**
```bash
# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Verify virtual environment is activated
which python  # Should point to .venv/bin/python
```

### 8.3 Version Conflicts

**Problem: Wrong version installed**
```bash
# Check installed version
uv pip show wizelit-sdk

# Uninstall and reinstall specific version
uv pip uninstall wizelit-sdk
uv pip install git+ssh://git@github.com/your-org/wizelit-sdk.git@v0.1.0
```

**Problem: Dependency conflicts**
```bash
# Create fresh virtual environment
deactivate
rm -rf .venv
uv venv
source .venv/bin/activate
uv pip install git+ssh://git@github.com/your-org/wizelit-sdk.git@v0.1.0
```

### 8.4 Build Issues

**Problem: Build fails**
```bash
# Clean and rebuild
make clean
make build

# Check for syntax errors
python -m py_compile src/wizelit_agent_wrapper/*.py
```

**Problem: Tests fail**
```bash
# Run tests with verbose output
pytest tests/ -v -s

# Run specific test
pytest tests/test_example.py::test_version -v
```

---

## 9. Quick Reference

### 9.1 Common Commands

```bash
# Development
make setup              # Set up environment
make install-dev        # Install for development
make test               # Run tests
make lint               # Check code quality
make format             # Format code
make check              # Run tests + linting

# Publishing
make release            # Interactive release
make tag VERSION=0.1.0  # Create version tag
make push               # Push code and tags

# Information
make version            # Show current version
make versions           # List all versions
make help               # Show all commands
```

### 9.2 Installation Commands for Team

```bash
# Install specific version
uv pip install git+ssh://git@github.com/your-org/wizelit-sdk.git@v0.1.0

# Install latest from main
uv pip install git+ssh://git@github.com/your-org/wizelit-sdk.git

# Update to new version
uv pip install --upgrade git+ssh://git@github.com/your-org/wizelit-sdk.git@v0.2.0
```

### 9.3 Version Management

**Semantic Versioning:**
- `MAJOR.MINOR.PATCH` (e.g., 1.2.3)
- **MAJOR**: Breaking changes (1.0.0 → 2.0.0)
- **MINOR**: New features, backward compatible (1.0.0 → 1.1.0)
- **PATCH**: Bug fixes (1.0.0 → 1.0.1)

**Release Checklist:**
- [ ] Update version in `pyproject.toml`
- [ ] Update `CHANGELOG.md`
- [ ] Run `make check`
- [ ] Commit changes
- [ ] Create git tag
- [ ] Push code and tags

### 9.4 Useful Git Commands

```bash
# View tags
git tag -l

# View remote tags
git ls-remote --tags origin

# Delete local tag
git tag -d v0.1.0

# Delete remote tag
git push origin :refs/tags/v0.1.0

# View commit history
git log --oneline --graph --decorate
```

---

## Additional Resources

- **uv Documentation**: https://github.com/astral-sh/uv
- **Python Packaging Guide**: https://packaging.python.org/
- **Semantic Versioning**: https://semver.org/
- **Keep a Changelog**: https://keepachangelog.com/
- **Git Documentation**: https://git-scm.com/doc

---

## Summary

You now have a complete, production-ready setup for publishing Python packages internally! 

**Key Points:**
- ✅ Automated release process with `make release`
- ✅ Team can install via Git with version pinning
- ✅ Proper testing and linting setup
- ✅ Semantic versioning and changelog tracking
- ✅ SSH authentication for private repositories

**Next Steps:**
1. Create your package following this guide
2. Push to your private Git repository
3. Share the "Team Installation Guide" section with your team
4. Start using `make release` for new versions

Good luck with your `wizelit-sdk` package! 🚀