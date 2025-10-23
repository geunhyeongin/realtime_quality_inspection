"""Domain entities for inspection workflows."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class DetectionResult:
    """Represents a YOLO segmentation detection with an optional crop."""

    label: str
    confidence: float
    mask: bytes
    crop: Optional[bytes] = None


@dataclass(frozen=True)
class ClassificationResult:
    """Represents a classification output for a cropped detection."""

    label: str
    confidence: float
    crop_id: str


@dataclass(frozen=True)
class InspectionVerdict:
    """Represents the consolidated decision for a frame or item.

    The verdict always includes the overall ``status`` and a human-readable
    ``reason``. When the verdict is triggered by a specific detection or
    classification result, optional metadata is populated to enable structured
    downstream handling without having to parse the textual message.
    """

    status: str  # e.g. "OK" or "NG"
    reason: str
    label: Optional[str] = None
    confidence: Optional[float] = None
    source: Optional[str] = None
