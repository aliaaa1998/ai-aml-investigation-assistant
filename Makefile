.PHONY: up down logs test lint format migrate seed-demo analyze-demo clean

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f api

test:
	pytest

lint:
	ruff check app tests

format:
	ruff format app tests

migrate:
	alembic upgrade head

seed-demo:
	python scripts/seed_demo.py

analyze-demo:
	python scripts/analyze_demo.py

clean:
	rm -rf .pytest_cache .ruff_cache artifacts/reports/*.md
