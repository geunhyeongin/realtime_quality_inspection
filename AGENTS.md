# Repository Guidelines for Agents

## Scope
These guidelines apply to the entire repository unless a subdirectory defines its own `AGENTS.md`.

## Coding Principles
- Adhere to clean architecture. Keep frameworks (FastAPI, PyQt) at the boundaries.
- Prefer dependency injection via constructors or factories.
- Keep functions focused; avoid side effects unless explicit.
- Type hints are mandatory for public functions and methods.
- Use dataclasses or `pydantic` models for structured data.

## Documentation
- Every new module should include a module-level docstring explaining its responsibilities and external dependencies.
- Update the architecture documentation when introducing new bounded contexts or workflows.

## Testing
- Place automated tests under `tests/` mirroring the package structure.
- Use `pytest` and include fixtures for reusable components.

## Configuration
- Configuration must be defined via `.yaml` or `.env` files under `models/configs` or `backend/core`.
- Avoid hardcoding file paths; use the `backend.core.config.Settings` utilities instead.
