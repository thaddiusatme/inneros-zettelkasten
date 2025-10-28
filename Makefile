.PHONY: setup lint type test unit integ cov run ui

setup:
	python3 -m pip install -r requirements.txt
	python3 -m pip install ruff black pyright pytest pytest-cov

lint:
	python3 -m ruff check development/src development/tests --select E,F,W --ignore E402,E501,E712,W291,W293,F401,F841
	python3 -m black --check development/src development/tests

type:
	python3 -m pyright development/src || true

unit:
	PYTHONPATH=development python3 -m pytest -q development/tests/unit

integ:
	PYTHONPATH=development python3 -m pytest -q development/tests/integration

cov:
	PYTHONPATH=development python3 -m pytest --cov=development/src --cov-report=term-missing

test: lint type unit

run:
	PYTHONPATH=development python3 development/src/cli/weekly_review_cli.py weekly-review

ui:
	python3 web_ui/app.py
