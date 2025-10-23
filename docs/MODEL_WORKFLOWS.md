# Model Workflows

This document captures the end-to-end lifecycle of YOLO segmentation and MobileNet classification models, including dataset management, training, evaluation, deployment, and monitoring.

## Terminology
- **Project**: A collection of labels, datasets, and models tailored to a specific customer or product line.
- **Experiment**: A single training run bound to configuration files and dataset snapshots.
- **Artifact**: Serialized model weights, label maps, metrics reports, and deployment bundles.

## Configuration
All experiments are configured through YAML manifests stored in `models/configs/`.

```yaml
project: widget_line_a
labels:
  - ok
  - ng
  - scratch
  - dent
models:
  detector:
    name: yolov8-seg
    weights: pretrained/yolov8s-seg.pt
    hyperparameters:
      epochs: 100
      batch_size: 16
  classifier:
    name: mobilenet_v3_small
    weights: imagenet
    hyperparameters:
      epochs: 50
      batch_size: 64
  business_rules:
    max_ng_ratio: 0.1
    allow_unknown: false
```

Label sets are project-specific; avoid hardcoding them in code. Persist label metadata in the database and propagate to both training and inference components.

## Dataset Management
1. **Ingestion**: Use `models/scripts/dataset_ingest.py` to download or copy raw data into project directories.
2. **Annotation**: Store segmentation masks and classification labels in common formats (COCO, Pascal VOC).
3. **Versioning**: Track dataset versions via DVC or Git LFS.

## Training Pipeline
- YOLO segmentation training entry point: `python -m models.pipelines.train_detector --config path/to/config.yaml`
- MobileNet classifier training: `python -m models.pipelines.train_classifier --config path/to/config.yaml`
- Both pipelines emit metrics to `artifacts/experiments/<timestamp>/metrics.json`

## Evaluation
- `python -m models.scripts.evaluate --config path/to/config.yaml --checkpoint artifacts/...`
- Store evaluation reports in `artifacts/reports/` and update the backend via an API endpoint (`POST /models/metrics`).

## Deployment
1. Register a successful checkpoint using `python -m models.scripts.register_model`.
2. Backend fetches the registered artifact and updates runtime inference services.
3. Frontend displays the active model version and confidence metrics.

## Monitoring & Feedback
- Backend logs inference requests/responses to the database.
- Provide a UI module under `frontend/app/history` to query past inference outcomes.
- Enable manual labeling corrections that feed back into dataset versioning.
