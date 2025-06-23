# Web Scout MCP Client Makefile

.PHONY: help install install-dev test lint format clean run examples

# Default target
help:
	@echo "Web Scout MCP Client - Development Commands"
	@echo "==========================================="
	@echo ""
	@echo "Available commands:"
	@echo "  install      - Install the client package"
	@echo "  install-dev  - Install in development mode with dev dependencies"
	@echo "  test         - Run tests"
	@echo "  lint         - Run linting (flake8)"
	@echo "  format       - Format code (black)"
	@echo "  clean        - Clean build artifacts"
	@echo "  run          - Run the client CLI"
	@echo "  examples     - Run example scripts"
	@echo "  check        - Run all checks (lint, format, test)"
	@echo ""

# Installation
install:
	pip install -e .

install-dev:
	pip install -r requirements.txt
	pip install -e .

# Testing
test:
	python -m pytest tests/ -v

test-coverage:
	python -m pytest tests/ --cov=client --cov-report=html --cov-report=term

# Code quality
lint:
	python -m flake8 client.py tests/ examples/

format:
	python -m black client.py tests/ examples/

format-check:
	python -m black --check client.py tests/ examples/

type-check:
	python -m mypy client.py

# Comprehensive check
check: format-check lint type-check test
	@echo "All checks passed!"

# Clean up
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Running
run:
	python client.py --help

connect:
	python client.py connect

tools:
	python client.py tools

resources:
	python client.py resources

# Examples
examples:
	@echo "Running CLI examples..."
	bash examples/cli_examples.sh

examples-python:
	@echo "Running Python examples..."
	python examples/basic_usage.py

# Development setup
setup-dev: install-dev
	@echo "Development environment setup complete!"
	@echo "You can now run: make check"

# Build distribution
build:
	python setup.py sdist bdist_wheel

upload-test:
	python -m twine upload --repository testpypi dist/*

upload:
	python -m twine upload dist/*

# Documentation
docs:
	@echo "Opening README.md..."
	@if command -v code >/dev/null 2>&1; then \
		code README.md; \
	else \
		echo "Please open README.md in your preferred editor"; \
	fi

# Quick development workflow
dev: format lint test
	@echo "Development checks completed!"

# Server management (if server is in parent directory)
start-server:
	@echo "Starting Web Scout MCP Server..."
	cd ../Web-Scout-MCP-Server && python -m src.server

# Full workflow test
workflow-test: install-dev
	@echo "Testing full workflow..."
	@echo "1. Starting server in background..."
	@cd ../Web-Scout-MCP-Server && python -m src.server &
	@sleep 5
	@echo "2. Running client tests..."
	@python client.py connect
	@python client.py tools
	@echo "3. Workflow test completed!"

# Git operations
git-setup:
	git add .
	git status

commit:
	git add .
	git commit -m "Update Web Scout MCP Client implementation"

push:
	git push origin main

# Project info
info:
	@echo "Web Scout MCP Client"
	@echo "==================="
	@echo "Version: 0.1.0"
	@echo "Python: $(shell python --version)"
	@echo "Pip: $(shell pip --version)"
	@echo ""
	@echo "Project structure:"
	@find . -name "*.py" -o -name "*.md" -o -name "*.txt" -o -name "*.sh" | head -20

# Dependencies
deps:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

deps-update:
	@echo "Updating dependencies..."
	pip list --outdated

# Release preparation
release-prep: clean format lint test build
	@echo "Release preparation completed!"
	@echo "Ready to upload to PyPI"

# Performance test
perf-test:
	@echo "Running performance tests..."
	time python client.py connect
	time python client.py tools