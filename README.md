# Template Project

A modern Python template project following industry best practices for professional Python development.

## Features

- **Modern Python Setup**: Supports Python 3.11+
- **Configuration Management**: Pydantic-based settings with environment variable support
- **Structured Logging**: Advanced logging with structlog, color support, JSON output, and Rich integration
- **Testing**: Comprehensive test suite with pytest and coverage reporting
- **CLI Interface**: Built-in command-line interface using Typer
- **Type Safety**: Full type hints and mypy configuration

## Quick Start

### Installation

```bash
# Clone repository
git clone <your-repo-url>
cd template-project

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install with development dependencies
pip install -e ".[dev]"
```

### Basic Usage

```python
from template_project import get_settings, get_logger, setup_logging

# Get application settings
settings = get_settings()
print(f"Running {settings.app_name} v{settings.app_version}")

# Setup logging
setup_logging()

# Use logging
logger = get_logger(__name__)
logger.info("Hello, Template Project!", extra_key="extra_value")
```

### Command Line Interface

```bash
# Show help
template-project --help

# Say hello
template-project hello

# Display project information
template-project info

# Initialize project directories
template-project init
```

## Project Structure

```
template-project/
├── config/                      # Configuration and logging package
│   ├── __init__.py
│   ├── settings.py              # Pydantic settings
│   └── logger.py               # Structlog logging
├── src/
│   └── template_project/          # Main package
│       ├── cli.py                 # Command-line interface
│       └── __init__.py
├── tests/                         # Test suite
│   ├── conftest.py               # Pytest configuration
│   ├── test_config.py            # Configuration tests
│   └── test_logging.py           # Logging tests
├── docs/                         # Documentation (MkDocs)
├── notebooks/                    # Jupyter notebooks
├── scripts/                      # Utility scripts
├── data/                         # Data directory
├── logs/                         # Log files
├── models/                       # Model files
├── pyproject.toml               # Project configuration
├── README.md                     # This file
├── LICENSE                       # MIT License
├── .gitignore                    # Git ignore patterns
├── .cursorignore                 # Cursor AI ignore patterns
```

## Configuration

### Environment Variables

Create a `.env` file in project root:

```env
# Application
APP_NAME=My App
DEBUG=False
ENVIRONMENT=development

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Paths (optional)
DATA_DIR=data
LOGS_DIR=logs
MODELS_DIR=models
```

### Settings Class

The `Settings` class uses Pydantic for validation and environment variable loading:

```python
from config import Settings, get_settings

# Create custom settings
settings = Settings(
    app_name="Custom App",
    debug=True,
    log_level="DEBUG"
)

# Or load from environment
settings = get_settings()
```

## Logging

### Setup

```python
from template_project import setup_logging

# Basic setup (uses defaults)
setup_logging()

# Custom setup with file logging
setup_logging(
    log_level="DEBUG",
    log_file="logs/custom.log",
)

# Production setup with JSON output
setup_logging(
    log_level="INFO",
    json_output=True
)
```

### Usage

```python
from template_project import get_logger, LoggerMixin, log_exception

# Standard usage with context
logger = get_logger(__name__)
logger.info("Info message", user_id=123, action="login")
logger.error("Error message", error_code=500)

# Using LoggerMixin in classes
class MyClass(LoggerMixin):
    def process_data(self, data):
        self.logger.debug("Processing data", count=len(data))
        try:
            result = [x * 2 for x in data]
            return result
        except Exception as e:
            log_exception(self.logger, e, data_length=len(data))
            raise

# Using utility functions
try:
    risky_operation()
except Exception as e:
    log_exception(logger, e, operation="risky_operation")
```

### Structlog Features

- **Contextual Logging**: Add structured context to all log messages
- **Rich Integration**: Beautiful colored console output with Rich
- **JSON Output**: Machine-readable logs for production/automation
- **File Logging**: Separate file and console output
- **Performance**: More efficient than standard logging
- **Type Safety**: Full type hints for bound loggers

## Development

### Code Quality Tools

```bash
# Format code with Black
black src/ tests/

# Lint with Ruff
ruff check src/ tests/

# Type checking with mypy
mypy src/

# Type checking with ty (faster alternative)
ty src/

# Run all quality checks
black src/ tests/ && ruff check src/ tests/ && mypy src/
```

### Testing

```bash
# Run tests
pytest

# Run specific test file
pytest tests/test_config.py
```

## CLI Development

The CLI is built using Typer. Add new commands in `cli.py`:

```python
@main.command()
def mycommand(name: str = typer.Option("World", help="Name to greet")):
    """Description of my command."""
    typer.echo(f"Hello, {name}!")
```

Run with:

```bash
template-project mycommand
template-project mycommand --name Alice
```

## Best Practices Followed

1. **Type Hints**: All functions and classes include type annotations
2. **Documentation**: Docstrings follow Google style guide
3. **Error Handling**: Proper exception handling and structured logging
4. **Configuration**: Environment-based configuration with validation
5. **Testing**: Unit tests with high coverage
6. **Code Style**: Consistent formatting and linting
7. **Separation of Concerns**: Modular, maintainable structure
8. **Security**: Proper handling of secrets and sensitive data
9. **Structured Logging**: Context-rich logging with structlog
10. **Modern Dependencies**: Latest versions of well-maintained libraries

## Dependencies

### Core Dependencies

- **typer**: Modern CLI framework with type hints
- **structlog**: Structured logging with Rich integration
- **rich**: Terminal formatting and colored output
- **pydantic**: Data validation and settings management
- **pydantic-settings**: Environment variable loading
- **python-dotenv**: Environment file support

### Development Dependencies

- **pytest**: Modern testing framework
- **pytest-cov**: Coverage reporting
- **black**: Code formatting
- **ruff**: Fast Python linter
- **mypy**: Static type checking
- **ty**: Fast type checking alternative to mypy
- **pre-commit**: Git hooks automation

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
