.PHONY: install run-local test lint docker-build docker-run

install:
	python -m pip install -e ".[dev]"

run-local:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest

lint:
	ruff check app tests

docker-build:
	docker build -t ctf-cybersec-bot .

docker-run:
	docker run --env-file .env -p 8000:8000 ctf-cybersec-bot

