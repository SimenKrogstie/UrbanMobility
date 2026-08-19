# Show available commands
default:
    @just --list

# Run the complete development check 
check:
    just lint
    just typecheck
    just test

# Fix formatting and auto-fix lint issues
fix:
    uv run ruff check . --fix
    just format

# Format source code
format:
    uv run ruff format .

# Check lint rules 
lint:
    uv run ruff check .

# Static type checking
typecheck:
    uv run pyright

# Run test suite
test:
    uv run pytest

# Run tests with verbose output
testv:
    uv run pytest -v

# Run tests and show missing coverage
coverage:
    uv run pytest --cov=urbanmobility --cov-report=term-missing

# Prepare branch before commit
ready:
    just fix
    just typecheck
    just test

# Update virtual environment
sync:
    uv sync

# Clean Python cache files
clean:
    find . -type d -name "__pycache__" -exec rm -rf {} +
    find . -name "*.pyc" -delete

