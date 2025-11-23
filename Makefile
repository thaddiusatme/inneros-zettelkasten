.PHONY: setup lint type test unit integ cov run ui

setup:
	python3 -m pip install -r requirements.txt
	python3 -m pip install ruff black pyright pytest pytest-cov pytest-timeout

lint:
	python3 -m ruff check development/src development/tests --select E,F,W --ignore E402,E501,E712,W291,W293,F401,F841
	python3 -m black --check development/src development/tests

type:
	python3 -m pyright development/src || true

unit:
	cd development && PYTHONPATH=. python3 -m pytest -q -m "not slow" tests/unit

unit-all:
	cd development && PYTHONPATH=. python3 -m pytest -q tests/unit

integ:
	cd development && PYTHONPATH=. python3 -m pytest -q tests/integration

cov:
	cd development && PYTHONPATH=. python3 -m pytest --cov=src --cov-report=term-missing

test: lint type unit

run:
	PYTHONPATH=development python3 development/src/cli/weekly_review_cli.py weekly-review

ui:
	python3 web_ui/app.py
