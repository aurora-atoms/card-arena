.PHONY: install test smoke hygiene lint

install:
	pip install -e ".[dev]"

test:
	pytest

smoke:
	python -m ptcg_ai_agent.match_runner --games 10 --seed 7

hygiene:
	python scripts/check_public_hygiene.py

lint:
	ruff check src tests scripts
