"""Application service orchestrating inspection workflows."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol

from backend.domain.entities import ClassificationResult, DetectionResult, InspectionVerdict


class Detector(Protocol):
    """Protocol for segmentation detectors."""

    def detect(self, frame: bytes) -> Iterable[DetectionResult]:
        """Run segmentation on a frame and yield detection results."""


class Classifier(Protocol):
    """Protocol for cropped object classifiers."""

    def classify(self, crops: Iterable[bytes]) -> Iterable[ClassificationResult]:
        """Classify cropped detections and yield predictions."""


class BusinessRulesEngine(Protocol):
    """Protocol for computing inspection verdicts."""

    def evaluate(
        self,
        detections: Iterable[DetectionResult],
        classifications: Iterable[ClassificationResult],
    ) -> InspectionVerdict:
        """Combine detection and classification results into a final verdict."""


@dataclass
class InspectionService:
    """Coordinates detection, classification, and business logic."""

    detector: Detector
    classifier: Classifier
    rules_engine: BusinessRulesEngine

    def run(self, frame: bytes) -> InspectionVerdict:
        """Execute the inspection pipeline for a single frame."""

        detections = list(self.detector.detect(frame))
        crops = [detection.crop for detection in detections if detection.crop is not None]
        classifications = list(self.classifier.classify(crops)) if crops else []
        return self.rules_engine.evaluate(detections, classifications)
