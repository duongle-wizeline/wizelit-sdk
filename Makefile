.PHONY: help setup install install-dev test lint format clean build release tag push publish publish-pypi publish-artifactory check-version

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
	@echo "  make release x.x.x - Create new release (updates version, tags, pushes)"
	@echo "  make tag VERSION=x.x.x - Create and push git tag"
	@echo "  make push           - Push code and tags to remote"
	@echo "  make publish        - Publish package (run checks, build, push to remote)"
	@echo "  make publish-pypi   - Publish package to public PyPI"
	@echo "  make publish-artifactory - Publish package to private Artifactory/PyPI"
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

# Extract version from command line or VERSION variable
# Supports: make release 0.1.0 or make release VERSION=0.1.0
# VERSION variable takes precedence if both are provided
VERSION_ARG := $(word 2, $(MAKECMDGOALS))
ifndef VERSION
  ifdef VERSION_ARG
    # Version provided as positional argument (make release 0.1.0)
    VERSION := $(VERSION_ARG)
    # Prevent Make from trying to build the version as a target
    $(eval $(VERSION_ARG):;@:)
  endif
endif

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
	uv run pytest tests/ -v

# Run code linting
lint:
	@echo "Running linting checks..."
	uv run ruff check src/
	@echo "Running type checks..."
	-uv run mypy src/ 2>/dev/null || echo "mypy not installed, skipping type checks"

# Format code
format:
	@echo "Formatting code..."
	uv run black src/ tests/
	uv run ruff check --fix src/

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
	$(error VERSION is not set. Use: make release 0.1.0 or make release VERSION=0.1.0)
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

# Publish package: verify, build, and push to remote
publish:
	@echo "=== Publishing Package ==="
	@echo ""
	@echo "Step 1: Checking git status..."
	@if [ -n "$$(git status --porcelain)" ]; then \
		echo "Warning: You have uncommitted changes!"; \
		echo "Please commit or stash your changes before publishing."; \
		git status --short; \
		exit 1; \
	fi
	@echo "✓ Working directory is clean"
	@echo ""
	@echo "Step 2: Running tests and linting..."
	@make check || exit 1
	@echo ""
	@echo "Step 3: Building package..."
	@make build || exit 1
	@echo ""
	@echo "Step 4: Checking version and tags..."
	@current_version=$$(grep "^version = " pyproject.toml | sed 's/version = //g' | tr -d '"'); \
	echo "Current version: $$current_version"; \
	tag_name="v$$current_version"; \
	if ! git rev-parse "$$tag_name" >/dev/null 2>&1; then \
		echo "Warning: Tag $$tag_name does not exist!"; \
		echo "Creating tag $$tag_name..."; \
		git tag -a "$$tag_name" -m "Release version $$current_version" || exit 1; \
		echo "✓ Tag $$tag_name created"; \
	else \
		echo "✓ Tag $$tag_name already exists"; \
	fi
	@echo ""
	@echo "Step 5: Pushing to remote..."
	@git push origin $$(git branch --show-current) || exit 1
	@git push origin --tags || exit 1
	@echo ""
	@echo "=== Publishing Complete! ==="
	@echo ""
	@current_version=$$(grep "^version = " pyproject.toml | sed 's/version = //g' | tr -d '"'); \
	git_repo_url=$$(git remote get-url origin 2>/dev/null || echo ""); \
	if echo "$$git_repo_url" | grep -q "^git@"; then \
		repo_path=$$(echo "$$git_repo_url" | sed 's|git@github.com:||' | sed 's|\.git$$||'); \
	elif echo "$$git_repo_url" | grep -q "^https://"; then \
		repo_path=$$(echo "$$git_repo_url" | sed 's|https://github.com/||' | sed 's|\.git$$||'); \
	else \
		repo_path="your-org/wizelit-sdk"; \
	fi; \
	echo "Package v$$current_version has been published!"; \
	echo ""; \
	echo "Team members can now install with:"; \
	echo "  uv pip install git+ssh://git@github.com/$$repo_path.git@v$$current_version"

# Release process - creates tag and pushes to remote
release: check-version
	@echo "=== Release Process ==="
	@echo ""
	@echo "Current version in pyproject.toml:"
	@grep "^version = " pyproject.toml || echo "Version not found!"
	@echo ""
	@echo "Releasing version: $(VERSION)"
	@echo ""
	@if git rev-parse v$(VERSION) >/dev/null 2>&1; then \
		echo "Error: Tag v$(VERSION) already exists!"; \
		exit 1; \
	fi
	@echo "Checking for uncommitted changes in src/..."
	@changed_files=$$(git diff --name-only src/ 2>/dev/null; git diff --cached --name-only src/ 2>/dev/null | grep -v "^$$"); \
	if [ -z "$$changed_files" ]; then \
		echo "✓ No uncommitted changes in src/"; \
	else \
		echo ""; \
		echo "⚠️  WARNING: There are uncommitted changes in src/:"; \
		echo ""; \
		echo "$$changed_files" | sort -u; \
		echo ""; \
		echo "Do you want to proceed with the release? (y/N)"; \
		read -r confirm; \
		if [ "$$confirm" != "y" ] && [ "$$confirm" != "Y" ]; then \
			echo "Release cancelled."; \
			exit 1; \
		fi; \
		echo "✓ Proceeding with release..."; \
	fi
	@echo ""
	@echo "Steps to be performed:"
	@echo "  1. Update version in pyproject.toml to $(VERSION)"
	@echo "  2. Run tests and linting"
	@echo "  3. Commit changes"
	@echo "  4. Create git tag v$(VERSION)"
	@echo "  5. Push to remote"
	@echo ""
	@echo "Updating version in pyproject.toml..."
	@sed -i.bak "s/^version = \".*\"/version = \"$(VERSION)\"/" pyproject.toml && rm pyproject.toml.bak || \
	sed -i "" "s/^version = \".*\"/version = \"$(VERSION)\"/" pyproject.toml
	@echo "✓ Version updated to $(VERSION)"
	@echo ""
	@echo "Running tests and linting..."
	@make check || exit 1
	@echo ""
	@echo "Committing changes..."
	@git add pyproject.toml
	@if [ -f uv.lock ] && ! git diff --quiet uv.lock 2>/dev/null; then \
		echo "✓ uv.lock has changed, adding to commit..."; \
		git add uv.lock; \
	fi
	@if git diff --cached --quiet; then \
		echo "✓ No changes to commit (version already set)"; \
	else \
		git commit -m "Release version $(VERSION)" || exit 1; \
		echo "✓ Changes committed"; \
	fi
	@echo ""
	@echo "Creating tag v$(VERSION)..."
	@git tag -a v$(VERSION) -m "Release version $(VERSION)"
	@echo "✓ Tag v$(VERSION) created"
	@echo ""
	@echo "Pushing to remote..."
	@git push origin $$(git branch --show-current) || exit 1
	@git push origin v$(VERSION) || exit 1
	@echo "✓ Pushed to remote"
	@echo ""
	@echo "=== Release v$(VERSION) complete! ==="
	@echo ""
	@git_repo_url=$$(git remote get-url origin 2>/dev/null || echo ""); \
	if echo "$$git_repo_url" | grep -q "^git@"; then \
		repo_path=$$(echo "$$git_repo_url" | sed 's|git@github.com:||' | sed 's|\.git$$||'); \
	elif echo "$$git_repo_url" | grep -q "^https://"; then \
		repo_path=$$(echo "$$git_repo_url" | sed 's|https://github.com/||' | sed 's|\.git$$||'); \
	else \
		repo_path="your-org/wizelit-sdk"; \
	fi; \
	echo "Team members can now install with:"; \
	echo "  uv pip install git+ssh://git@github.com/$$repo_path.git@v$(VERSION)"

# Publish to public PyPI
publish-pypi:
	@echo "=== Publishing to Public PyPI ==="
	@echo ""
	@echo "Step 1: Checking git status..."
	@if [ -n "$$(git status --porcelain)" ]; then \
		echo "Error: You have uncommitted changes!"; \
		echo "Please commit or stash your changes before publishing."; \
		git status --short; \
		exit 1; \
	fi
	@echo "✓ Working directory is clean"
	@echo ""
	@echo "Step 2: Running tests and linting..."
	@make check || exit 1
	@echo ""
	@echo "Step 3: Building package..."
	@make build || exit 1
	@echo ""
	@echo "Step 4: Uploading to PyPI..."
	@python -m pip install twine 2>/dev/null || echo "twine required"
	@python -m twine upload dist/* --non-interactive || exit 1
	@echo ""
	@echo "=== PyPI Upload Complete! ==="
	@echo ""
	@current_version=$$(grep "^version = " pyproject.toml | sed 's/version = //g' | tr -d '"'); \
	echo "✓ Package v$$current_version published to PyPI!"; \
	echo ""; \
	echo "Team members can now install with:"; \
	echo "  pip install wizelit-sdk==$$current_version"; \
	echo "  or simply: pip install wizelit-sdk"

# Publish to private Artifactory/PyPI
publish-artifactory:
	@echo "=== Publishing to Private Artifactory ==="
	@echo ""
	@echo "Step 1: Checking git status..."
	@if [ -n "$$(git status --porcelain)" ]; then \
		echo "Error: You have uncommitted changes!"; \
		echo "Please commit or stash your changes before publishing."; \
		git status --short; \
		exit 1; \
	fi
	@echo "✓ Working directory is clean"
	@echo ""
	@echo "Step 2: Running tests and linting..."
	@make check || exit 1
	@echo ""
	@echo "Step 3: Building package..."
	@make build || exit 1
	@echo ""
	@echo "Step 4: Uploading to Artifactory..."
	@if [ -z "$${ARTIFACTORY_REPO_URL}" ]; then \
		echo "Error: ARTIFACTORY_REPO_URL environment variable not set!"; \
		echo "Example: export ARTIFACTORY_REPO_URL=https://artifactory.company.com/artifactory/api/pypi/pypi"; \
		exit 1; \
	fi
	@python -m pip install twine 2>/dev/null || echo "twine required"
	@python -m twine upload -r artifactory dist/ --non-interactive || exit 1
	@echo ""
	@echo "=== Artifactory Upload Complete! ==="
	@echo ""
	@current_version=$$(grep "^version = " pyproject.toml | sed 's/version = //g' | tr -d '"'); \
	echo "✓ Package v$$current_version published to Artifactory!"; \
	echo ""; \
	echo "Team members can now install with:"; \
	echo "  pip install wizelit-sdk==$$current_version"

# Show current version
version:
	@grep "^version = " pyproject.toml | sed 's/version = //g' | tr -d '"'

# List all available versions (tags)
versions:
	@echo "Available versions:"
	@git tag -l "v*" | sort -V

