.PHONY: install sync  test lint format run help

install:
	uv tool install . -e --force

sync:
	uv sync

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .

run:
	uv run main.py

help:
	@echo "Available commands:"
	@echo "  make install  - Install project dependencies"
	@echo "  make sync     - Sync project dependencies"
	@echo "  make clean    - Clean up cache and dependencies"
	@echo "  make test     - Run tests"
	@echo "  make lint     - Run linter"
	@echo "  make format   - Format code"
	@echo "  make run      - Run main application"
