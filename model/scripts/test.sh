# scripts/test.sh
#!/bin/bash
set -e

echo "Running tests..."
pytest tests -v --cov=src --cov-report=term-missing

echo "Tests completed successfully!"