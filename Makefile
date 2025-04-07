.PHONY: setup-all test-all image-all deploy-all

# Core service targets
setup-core:
	cd core && pip install -e ".[dev]"

test-core:
	cd core && pytest

image-core:
	docker build -t ghcr.io/yourusername/pill-checker-core:latest -f core/Dockerfile core

# Model service targets
setup-model:
	cd model && pip install -e ".[dev]"

test-model:
	cd model && pytest

image-model:
	docker build -t ghcr.io/yourusername/pill-checker-model:latest -f model/Dockerfile model

# Combined targets
setup-all: setup-core setup-model

test-all: test-core test-model

image-all: image-core image-model

# Deployment target using docker-compose
deploy:
	docker-compose up -d

# CI target that runs all tests
test_ci: test-all