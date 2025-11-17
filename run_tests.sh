#!/bin/bash
# Test runner script for BiomedNER integration tests

set -e

echo "====================================="
echo "Running BiomedNER Integration Tests"
echo "====================================="

# Activate virtual environment
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
else
    echo "Virtual environment not found. Creating..."
    python3.12 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -e ".[dev]"
fi

echo ""
echo "Running Unit Tests for NER Client..."
python -m pytest tests/services/test_biomed_ner_client.py -v --tb=short

echo ""
echo "Running Unit Tests for Medication Processing..."
python -m pytest tests/services/test_medication_processing.py -v --tb=short

echo ""
echo "Running Integration Tests for Medication Upload..."
python -m pytest tests/api/test_medication_upload.py -v --tb=short

echo ""
echo "Running All NER-Related Tests..."
python -m pytest tests/services/test_biomed_ner_client.py tests/services/test_medication_processing.py tests/api/test_medication_upload.py -v --cov=pill_checker.services.biomed_ner_client --cov=pill_checker.services.medication_processing --cov=pill_checker.api.v1.medications --cov-report=term-missing

echo ""
echo "====================================="
echo "All tests completed!"
echo "====================================="
