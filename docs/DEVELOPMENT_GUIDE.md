# Development Guide

This guide summarizes workflows for local development on Windows, covering backend services, PyQt frontend tooling, and machine-learning pipelines.

## Prerequisites
- Python 3.10+
- Poetry or `pipenv` for dependency management
- Node.js (optional) for bundling static assets
- Qt 6 (Designer + PyQt6 bindings)
- CUDA toolkit (for GPU-accelerated training/inference)

## Repository Layout
Refer to [ARCHITECTURE.md](./ARCHITECTURE.md) for high-level design. Key folders for contributors:

- `backend/`: FastAPI services, use cases, domain, infrastructure adapters.
- `frontend/`: PyQt presentation layer with Qt Designer `.ui` resources.
- `models/`: Training pipelines, experiment configurations, deployment scripts.
- `tests/`: Shared pytest-based test suite.
- `docs/`: Additional documentation.

## Environment Setup (Windows)
1. Create a virtual environment: `python -m venv .venv`
2. Activate: `.venv\\Scripts\\activate`
3. Install dependencies once defined: `pip install -r requirements.txt` or `poetry install`
4. Install Qt tools: `pip install pyqt6 pyqt6-tools`
5. For CUDA support, ensure NVIDIA drivers and the toolkit are installed.

## Running Services
- **Backend API**: `uvicorn backend.app.main:app --reload`
- **Background Worker**: `python -m backend.app.worker`
- **Frontend**: `python -m frontend.app.main`

## Code Generation
- Convert Qt Designer `.ui` files using `pyuic6 frontend/ui/main_window.ui -o frontend/ui/main_window.py`
- Generate pydantic models from JSON schema using `datamodel-codegen`

## Testing
- Run the whole suite: `pytest`
- Linting: `ruff check .`
- Type checking: `mypy backend frontend`

## Continuous Integration
- Add GitHub Actions workflows for lint, type check, tests, and packaging.
- Use pre-commit hooks for formatting and static analysis.

## Documentation
- Update `docs/` when changing architecture decisions.
- Keep changelog entries under `docs/CHANGELOG.md` (to be created with the first release).

## Release Workflow
1. Trigger model evaluation pipeline (see `docs/MODEL_WORKFLOWS.md`).
2. Package backend Docker image and frontend installer.
3. Tag release and upload artifacts.
