"""Training entry point for YOLO segmentation models."""

from __future__ import annotations

from pathlib import Path


def train_detector(config_path: Path) -> None:
    """Placeholder function for detector training pipeline."""

    raise NotImplementedError("Implement YOLO segmentation training pipeline")


if __name__ == "__main__":
    raise SystemExit("Use `python -m models.pipelines.train_detector --config <path>` once implemented")
