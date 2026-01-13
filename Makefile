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

