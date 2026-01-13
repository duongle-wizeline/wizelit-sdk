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

