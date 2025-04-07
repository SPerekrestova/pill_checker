.PHONY: setup lint test docker-build docker-run

setup:
    pip install -e ".[dev]"
    pre-commit install

lint:
    ./scripts/lint.sh

test:
    ./scripts/test.sh

docker-build:
    docker build -t medical-ner-service .

docker-run:
    docker run -p 8081:8081 --rm medical-ner-service