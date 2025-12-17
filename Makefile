.PHONY: setup lint format type test unit integ cov run ui up down status review fleeting clean-venv smoke

# Venv configuration - ensures reproducible tooling
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
SYSTEM_PYTHON ?= python3

# ============================================
# USER COMMANDS (what you use daily)
# ============================================

up:
	@echo "🚀 Starting InnerOS automation daemon..."
	PYTHONPATH=development python3 development/src/cli/inneros_automation_cli.py daemon start

down:
	@echo "🛑 Stopping InnerOS automation daemon..."
	PYTHONPATH=development python3 development/src/cli/inneros_automation_cli.py daemon stop

status:
	@PYTHONPATH=development python3 development/src/cli/inneros_status_cli.py

review:
	@echo "📋 Generating weekly review..."
	PYTHONPATH=development python3 development/src/cli/weekly_review_cli.py --vault knowledge weekly-review --preview

fleeting:
	@echo "📊 Checking fleeting notes health..."
	PYTHONPATH=development python3 development/src/cli/fleeting_cli.py --vault knowledge fleeting-health

smoke:
	@echo "🔥 Running usability smoke test..."
	@echo "--- Step 1/3: Status check ---"
	@$(MAKE) status
	@echo "--- Step 2/3: Review (preview) ---"
	@$(MAKE) review
	@echo "--- Step 3/3: Fleeting health ---"
	@$(MAKE) fleeting
	@echo "✅ Smoke test complete. All core commands working."

# ============================================
# DEV COMMANDS (for development only)
# ============================================

# Bootstrap venv (idempotent - only creates if missing)
$(VENV)/bin/activate:
	@echo "📦 Creating virtual environment..."
	$(SYSTEM_PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install -r dev-requirements.txt
	@echo "✅ Virtual environment ready at $(VENV)"

setup: $(VENV)/bin/activate
	@echo "✅ Setup complete. Use 'make lint' to check code."

lint: $(VENV)/bin/activate
	$(PYTHON) -m ruff check development/src development/tests --select E,F,W --ignore E402,E501,E712,W291,W293,F401,F841
	$(PYTHON) -m black --check development/src development/tests

format: $(VENV)/bin/activate
	@echo "🔧 Auto-formatting code..."
	$(PYTHON) -m ruff check --fix development/src development/tests --select E,F,W --ignore E402,E501,E712,W291,W293,F401,F841
	$(PYTHON) -m black development/src development/tests
	@echo "✅ Formatting complete."

type: $(VENV)/bin/activate
	$(PYTHON) -m pyright development/src || true

clean-venv:
	@echo "🧹 Removing virtual environment..."
	rm -rf $(VENV)
	@echo "✅ Virtual environment removed. Run 'make setup' to recreate."

unit: $(VENV)/bin/activate
	PYTHONPATH=development $(PYTHON) -m pytest -q --timeout=300 -m "not slow" development/tests/unit

unit-all: $(VENV)/bin/activate
	PYTHONPATH=development $(PYTHON) -m pytest -q --timeout=300 development/tests/unit

integ: $(VENV)/bin/activate
	PYTHONPATH=development $(PYTHON) -m pytest -q development/tests/integration

cov: $(VENV)/bin/activate
	PYTHONPATH=development $(PYTHON) -m pytest --cov=development/src --cov-report=term-missing

test: lint type unit

run:
	PYTHONPATH=development python3 development/src/cli/weekly_review_cli.py weekly-review

ui:
	python3 web_ui/app.py
