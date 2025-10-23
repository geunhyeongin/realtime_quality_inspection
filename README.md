# Realtime Quality Inspection Platform

This repository hosts a Windows-friendly realtime quality inspection platform featuring a Python backend and a PyQt frontend. The solution is designed around clean architecture principles to support scalable, maintainable development and rapid adaptation to new labeling schemes or inspection requirements.

## Features
- Modular backend leveraging FastAPI and background workers for RTSP ingest, YOLO segmentation, and MobileNet classification.
- PyQt-based operator console built with Qt Designer for rapid UI iteration.
- Configurable business rules to determine `OK`/`NG` decisions per project.
- Training, evaluation, and deployment workflows for both YOLO segmentation and MobileNet classifier models.
- Audit-friendly inspection history with filtering and search capabilities.

## Repository Structure
```
backend/      # Backend application (FastAPI, domain logic, infrastructure)
frontend/     # PyQt frontend application and Qt Designer resources
models/       # ML pipelines, configs, and scripts
docs/         # Architecture and workflow documentation
tests/        # Placeholder for pytest suites
```

Refer to `docs/ARCHITECTURE.md` and `docs/MODEL_WORKFLOWS.md` for detailed design and ML process documentation.
