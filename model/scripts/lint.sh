# scripts/lint.sh
#!/bin/bash
set -e

echo "Running linters..."
isort src tests
black src tests
ruff src tests

echo "Linting completed successfully!"