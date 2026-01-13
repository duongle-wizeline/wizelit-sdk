.PHONY: help setup install install-dev test lint format clean build release tag push publish check-version

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
	@echo "  make release VERSION=x.x.x - Create new release (updates version, tags, pushes)"
	@echo "  make tag VERSION=x.x.x - Create and push git tag"
	@echo "  make push           - Push code and tags to remote"
	@echo "  make publish        - Publish package (run checks, build, push to remote)"
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
	$(error VERSION is not set. Use: make release VERSION=0.1.0 or make tag VERSION=0.1.0)
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
	echo "Package v$$current_version has been published!"; \
	echo ""; \
	echo "Team members can now install with:"; \
	echo "  uv pip install git+ssh://git@github.com/your-org/wizelit-sdk.git@v$$current_version"

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
	@git commit -m "Release version $(VERSION)" || exit 1
	@echo "✓ Changes committed"
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
	@echo "Team members can now install with:"
	@echo "  uv pip install git+ssh://git@github.com/your-org/wizelit-sdk.git@v$(VERSION)"

# Show current version
version:
	@grep "^version = " pyproject.toml | sed 's/version = //g' | tr -d '"'

# List all available versions (tags)
versions:
	@echo "Available versions:"
	@git tag -l "v*" | sort -V

