.PHONY: help install test build publish-test publish tag bump-patch bump-minor bump-major

# Default target
help:
	@echo "Agent Notes Development Commands:"
	@echo "  make install      - Install dependencies using uv"
	@echo "  make test         - Run tests (if any)"
	@echo "  make build        - Build source and wheel distributions"
	@echo "  make publish      - Build and publish to PyPI"
	@echo "  make tag          - Create and push a git tag for the current version"
	@echo "  make bump-patch   - Bump patch version (0.0.x)"
	@echo "  make bump-minor   - Bump minor version (0.x.0)"
	@echo "  make bump-major   - Bump major version (x.0.0)"

install:
	uv sync

test:
	uv run pytest

build:
	uv build

publish: build
	uv publish

tag:
	@VERSION=$$(grep -m 1 version pyproject.toml | tr -d '"' | tr -d ' ' | cut -d'=' -f2); \
	echo "Tagging version v$$VERSION..."; \
	git tag -a v$$VERSION -m "Release v$$VERSION"; \
	git push origin v$$VERSION

bump-patch:
	uv version patch
	@echo "Don't forget to commit and 'make tag'"

bump-minor:
	uv version minor
	@echo "Don't forget to commit and 'make tag'"

bump-major:
	uv version major
	@echo "Don't forget to commit and 'make tag'"
