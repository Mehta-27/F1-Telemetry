.PHONY: install lint format typecheck test clean docker docker-run run

PYTHON ?= python3
PIP ?= pip3

install:
	$(PYTHON) -m venv .venv
	.venv/bin/$(PIP) install -r requirements.txt

install-dev: install
	.venv/bin/$(PIP) install ruff mypy pytest pytest-cov pre-commit
	.venv/bin/pre-commit install

lint:
	ruff check .

format:
	ruff format .

typecheck:
	mypy . --ignore-missing-imports

test:
	pytest tests/ --cov=. --cov-report=term-missing

run:
	streamlit run app.py

clean:
	rm -rf __pycache__ .pytest_cache .ruff_cache .mypy_cache
	rm -rf *.egg-info dist build

docker:
	docker build -t f1-intelligence-hub .

docker-run:
	docker run -p 8501:8501 f1-intelligence-hub

pre-commit:
	pre-commit run --all-files
