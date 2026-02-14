# InnerOS Zettelkasten — Development Test Targets
# Usage: make -C development <target>  (from project root)
#    or: make <target>                 (from development/)
#
# Requires: .venv activated or PYTEST set to venv pytest path

PYTEST ?= python -m pytest

.PHONY: test-fast test-unit test-integration test-all test-network help

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

test-fast: ## Fast pre-commit subset (<30s) — no slow, network, or wip tests
	$(PYTEST) tests/unit -m "fast and not slow and not network and not wip"

test-unit: ## All unit tests (excludes wip)
	$(PYTEST) tests/unit -m "not wip"

test-integration: ## Integration tests without network/Ollama (excludes wip)
	$(PYTEST) tests/integration -m "not network and not wip"

test-all: ## Full suite excluding wip
	$(PYTEST) -m "not wip"

test-network: ## Ollama/network tests only (opt-in)
	$(PYTEST) -m "network"
