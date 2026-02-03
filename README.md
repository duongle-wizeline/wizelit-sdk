# wizelit-sdk

Internal utility package for Wizelit Agent operations.

## Installation

### Install from PyPI

```bash
uv pip install wizelit-sdk
```

### Add to pyproject.toml

```toml
[project]
dependencies = [
    "wizelit-sdk"
]
```

## Quickstart

1. Install the package (see above).
2. Configure environment variables (see Configuration).
3. Import and use the SDK from your app.

### CLI

The package also installs a small command-line tool named `wizelit-sdk` which helps scaffold and manage agent projects.

Install and run the CLI:

```bash
# Install package (global or in virtualenv)
pip install wizelit-sdk

# Create a new project using a template (fast|slow|hybrid)
wizelit-sdk init "My Agent" --template hybrid

# Alternative (without wrapper):
python -m wizelit_sdk.cli init "My Agent" --template hybrid
```

Useful commands:

- `wizelit-sdk init <name> [--template fast|slow|hybrid]` — scaffold a new agent project
- `wizelit-sdk scaffold <name>` — basic scaffold (older command)
- `wizelit-sdk validate [path]` — validate project structure
- `wizelit-sdk list-tools [path]` — list functions decorated with `@mcp.ingest`

If you are developing locally, install editable and use the wrapper from your virtualenv:

```bash
# from repo root
pip install -e .
source .venv/bin/activate
wizelit-sdk init "My Agent"
```

## Usage

```python
from wizelit_agent_wrapper import your_module

# Use the wrapper
result = your_module.function()
```

## SDK Guide

### Basic import patterns

```python
from wizelit_sdk import database, exceptions
from wizelit_sdk.agent_wrapper import agent_wrapper
```

### Initialize and call

```python
# Example: create a wrapper and call a method
wrapper = agent_wrapper.WizelitAgentWrapper()
result = wrapper.run()
```

### Error handling

```python
from wizelit_sdk.exceptions import WizelitError

try:
    wrapper.run()
except WizelitError as exc:
    # handle SDK-specific errors
    print(exc)
```

## Configuration

The SDK reads database configuration from the hosting application's environment. Provide these variables in the consuming project (e.g., via your app's .env or deployment secrets):

- POSTGRES_USER
- POSTGRES_PASSWORD
- POSTGRES_HOST
- POSTGRES_PORT
- POSTGRES_DB

You can also supply a full connection string via `DATABASE_URL` (overrides the individual fields). If using streaming/logging with Redis, set `REDIS_HOST`, `REDIS_PORT`, and optionally `REDIS_PASSWORD`.

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
make setup                  # Set up development environment
make install                # Install package (production mode)
make install-dev            # Install in development mode
make test                   # Run tests
make lint                   # Run code linting
make format                 # Format code with black
make check                  # Run tests and linting
make clean                  # Clean build artifacts
make build                  # Build package
make release x.x.x          # Create new release (updates version, tags, pushes)
make tag VERSION=x.x.x      # Create and push git tag
make push                   # Push code and tags to remote
make publish                # Publish package (run checks, build, push to remote)
make publish-pypi           # Publish package to public PyPI
make publish-artifactory    # Publish package to private Artifactory/PyPI
make version                # Show current version
make versions               # List all available versions
```

### Deploy to PyPI

Use the built-in Makefile target (recommended):

```bash
make publish-pypi
```

This target will:

1. Verify the git working tree is clean.
2. Run tests and linting (`make check`).
3. Build the package (`make build`).
4. Upload the artifacts in `dist/` to PyPI via `twine`.

Optional release/tag flow (before publishing):

```bash
# Interactive release flow (updates version, tags, pushes)
make release x.x.x

# Or tag a specific version
make tag VERSION=x.x.x
```

Notes:

- Ensure your PyPI credentials are configured locally (e.g., via $HOME/.pypirc or your preferred environment variables).
- The package version must be unique on PyPI; if a version already exists, bump it and rebuild.

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
