.PHONY: setup lint type test unit integ cov run ui up down status review fleeting

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

# ============================================
# DEV COMMANDS (for development only)
# ============================================

setup:
	python3 -m pip install -r requirements.txt
	python3 -m pip install ruff black pyright pytest pytest-cov pytest-timeout

lint:
	python3 -m ruff check development/src development/tests --select E,F,W --ignore E402,E501,E712,W291,W293,F401,F841
	python3 -m black --check development/src development/tests

type:
	python3 -m pyright development/src || true

unit:
	PYTHONPATH=development python3 -m pytest -q --timeout=300 -m "not slow" development/tests/unit

unit-all:
	PYTHONPATH=development python3 -m pytest -q --timeout=300 development/tests/unit

integ:
	PYTHONPATH=development python3 -m pytest -q development/tests/integration

cov:
	PYTHONPATH=development python3 -m pytest --cov=development/src --cov-report=term-missing

test: lint type unit

run:
	PYTHONPATH=development python3 development/src/cli/weekly_review_cli.py weekly-review

ui:
	python3 web_ui/app.py
