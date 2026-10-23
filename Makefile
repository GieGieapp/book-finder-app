.PHONY: up down restart logs test test-local shell clean help

help:
	@echo "Available commands:"
	@echo "  make up          - Start docker-compose containers in detached mode"
	@echo "  make down        - Stop and remove docker-compose containers"
	@echo "  make restart     - Restart docker-compose services"
	@echo "  make logs        - Tail live logs from all containers"
	@echo "  make test        - Run all 52 unit test suites inside Docker container"
	@echo "  make test-local  - Run all unit tests locally with python3"
	@echo "  make shell       - Open bash shell inside web container"
	@echo "  make clean       - Clean Python bytecode cache directories"

up:
	docker-compose up -d --build

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

test:
	docker-compose run --rm web python test_app.py

test-local:
	python3 test_app.py

shell:
	docker-compose exec web /bin/sh

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
