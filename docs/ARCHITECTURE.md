# System Architecture Overview

This document provides a high-level blueprint for the realtime quality inspection platform. The architecture enforces a clean separation between the Python backend, the PyQt frontend, and the machine-learning workflows used for segmentation, classification, and deployment.

## Domain Overview
- **Inspection Session**: Represents a monitoring context that aggregates frames from RTSP streams, maintains detector/classifier states, and yields inspection results.
- **Detection Result**: Output of the YOLO segmentation model including instance masks and metadata.
- **Classification Result**: Output of the MobileNet classifier for cropped detections.
- **Inspection Verdict**: Business rule evaluation that consolidates detection and classification signals into `OK` or `NG` outcomes. The default implementation is the `ThresholdBusinessRulesEngine`, which evaluates confidence thresholds and label allow-lists to determine the final verdict and supports per-label `LabelPolicy` overrides for bespoke messaging and thresholds.

## Clean Architecture Layers

```
┌────────────────────────────────────────────────────────────────┐
│                            Frontend                            │
│                   (PyQt Presentation Layer)                    │
└───────────────────────▲──────────────────────┬─────────────────┘
                        │                      │
                        │ Commands/Queries     │ Signals/Events
                        │                      │
┌───────────────────────┴──────────────────────▼─────────────────┐
│                       Backend Interfaces                       │
│      (REST/WebSocket API, gRPC, CLI, background workers)       │
└───────────────────────▲──────────────────────┬─────────────────┘
                        │                      │
                        │ Use Cases            │ Events/DTOs
                        │                      │
┌───────────────────────┴──────────────────────▼─────────────────┐
│                    Application / Use Cases                     │
│ (Orchestrate domain services, implement business workflows)    │
└───────────────────────▲──────────────────────┬─────────────────┘
                        │                      │
                        │ Entities/Value Obj   │ Repository Ports
                        │                      │
┌───────────────────────┴──────────────────────▼─────────────────┐
│                           Domain                               │
│ (Entities, value objects, domain services, business policies)  │
└───────────────────────▲──────────────────────┬─────────────────┘
                        │                      │
                        │ Implementations      │ Infra Events
                        │                      │
┌───────────────────────┴──────────────────────▼─────────────────┐
│                        Infrastructure                          │
│ (Model runners, RTSP adapters, persistence, configuration)     │
└────────────────────────────────────────────────────────────────┘
```

## Key Components

### Backend (`backend/`)
- **`backend/app`**: Entry points for FastAPI and background workers. Exposes REST/WebSocket APIs consumed by the frontend.
- **`backend/application`**: Use-case orchestrators encapsulating inspection workflows, retraining pipelines, and inference scheduling.
- **`backend/domain`**: Pure business logic, entities, and service interfaces (ports).
- **`backend/infrastructure`**: Adapters for ML models, storage, RTSP streams, and deployment targets.
- **`backend/interfaces`**: Interface layer for API schemas, DTOs, and CLI commands.
- **`backend/core`**: Shared utilities (configuration, logging, dependency injection containers).

### Frontend (`frontend/`)
- **`frontend/app`**: PyQt application entry point, view models, and controllers.
- **`frontend/ui`**: Auto-generated Qt Designer `.ui` files and the compiled Python bindings.
- **`frontend/resources`**: Icons, stylesheets, localization bundles.

### Machine Learning (`models/`)
- **`models/pipelines`**: Training scripts and pipeline definitions for YOLO segmentation and MobileNet classification.
- **`models/configs`**: YAML configuration templates for data paths, hyperparameters, and experiment metadata.
- **`models/scripts`**: Utilities for dataset preparation, evaluation, and deployment packaging.

## Data Flow
1. **RTSP ingest**: Infrastructure service connects to configured RTSP endpoints and emits frames.
2. **Segmentation**: YOLO segmentation runner detects objects and returns bounding boxes/masks.
3. **Cropping & Classification**: Crops are passed to the MobileNet classifier to obtain class probabilities.
4. **Business Rules**: Application layer aggregates results, evaluates configurable rules, and produces inspection verdicts.
5. **Presentation**: Backend publishes results via WebSocket/REST. Frontend subscribes and renders status dashboards.
6. **Persistence**: Inspection history, model metadata, and parameter configurations are stored in the persistence layer.

## Extensibility Guidelines
- Use plugin-style registries for model runners to support different architectures or custom labels.
- Provide configuration-driven label definitions. Labels are not hardcoded and must be dynamic per project.
- Ensure inference and training pipelines share serializable experiment manifests for reproducibility.

## Deployment
- Package backend as a FastAPI application with optional Celery workers for long-running training tasks.
- Frontend is distributed as a PyInstaller bundle communicating with the backend via secure channels.
- Model artifacts are versioned and stored in `models/checkpoints/` with metadata tracked in the database.
