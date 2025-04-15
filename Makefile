.PHONY: run
run:
	@ZK_DIR=. uv run mcp dev server.py

.PHONY: format
format:
	@uv run ruff check . --select I --fix-only --exit-zero
	@uv run ruff format .

.PHONY: lint
lint:
	@uv run ruff check .
	@uv run mypy --show-error-codes .

.PHONY: pre-commit
pre-commit: format lint
