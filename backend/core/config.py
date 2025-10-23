"""Application configuration utilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class RTSPSource:
    """Represents a single RTSP camera stream."""

    name: str
    url: str
    enabled: bool = True


@dataclass
class ModelConfig:
    """Holds runtime configuration for inference models."""

    project: str
    detector_path: Path
    classifier_path: Path
    label_map: Path
    confidence_threshold: float = 0.5
    iou_threshold: float = 0.5


@dataclass
class Settings:
    """Aggregated application settings.

    These settings are intended to be populated from environment variables or YAML
    configuration files to ensure that labels and model parameters remain dynamic
    across deployments.
    """

    environment: str = "development"
    data_dir: Path = Path("data")
    artifact_dir: Path = Path("artifacts")
    rtsp_sources: List[RTSPSource] = field(default_factory=list)
    model: Optional[ModelConfig] = None

    @classmethod
    def from_dict(cls, values: dict[str, object]) -> "Settings":
        """Create settings from a dictionary, performing nested coercion."""

        rtsp_entries = [RTSPSource(**entry) for entry in values.get("rtsp_sources", [])]
        model_entry = values.get("model")
        model = ModelConfig(**model_entry) if model_entry else None
        return cls(
            environment=values.get("environment", "development"),
            data_dir=Path(values.get("data_dir", "data")),
            artifact_dir=Path(values.get("artifact_dir", "artifacts")),
            rtsp_sources=rtsp_entries,
            model=model,
        )
