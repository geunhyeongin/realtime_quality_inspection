"""Tests for the inspection application service."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Optional

import pytest

from backend.application.inspection_service import InspectionService
from backend.domain.entities import ClassificationResult, DetectionResult
from backend.domain.services import ThresholdBusinessRulesEngine


@dataclass
class StubDetector:
    """Detector stub returning a predefined list of detections."""

    detections: List[DetectionResult]

    def detect(self, frame: bytes) -> Iterable[DetectionResult]:  # pragma: no cover - interface compliance
        self.last_frame = frame
        return list(self.detections)


@dataclass
class StubClassifier:
    """Classifier stub returning a predefined list of classifications."""

    results: List[ClassificationResult]
    received_crops: Optional[List[bytes]] = field(default=None, init=False)

    def classify(self, crops: Iterable[bytes]) -> Iterable[ClassificationResult]:  # pragma: no cover - interface compliance
        self.received_crops = list(crops)
        return list(self.results)


@pytest.fixture()
def engine() -> ThresholdBusinessRulesEngine:
    """Provide a business rules engine with simple NG/OK semantics."""

    return ThresholdBusinessRulesEngine(
        ng_labels=frozenset({"ng", "defect_a"}),
        ok_labels=frozenset({"ok"}),
        confidence_threshold=0.5,
        allow_unknown=True,
    )


def test_inspection_service_returns_ok_when_no_detections(engine: ThresholdBusinessRulesEngine) -> None:
    """Inspection service should report OK when nothing is detected."""

    detector = StubDetector(detections=[])
    classifier = StubClassifier(results=[])
    service = InspectionService(detector=detector, classifier=classifier, rules_engine=engine)

    verdict = service.run(b"frame-bytes")

    assert verdict.status == "OK"
    assert classifier.received_crops == [] or classifier.received_crops is None


def test_inspection_service_flags_ng_from_classifier(engine: ThresholdBusinessRulesEngine) -> None:
    """NG classification results should trigger an NG verdict."""

    detections = [DetectionResult(label="ok", confidence=0.9, mask=b"mask", crop=b"crop-1")]
    detector = StubDetector(detections=detections)
    classifier = StubClassifier(
        results=[ClassificationResult(label="defect_a", confidence=0.9, crop_id="crop-1")]
    )
    service = InspectionService(detector=detector, classifier=classifier, rules_engine=engine)

    verdict = service.run(b"frame-bytes")

    assert verdict.status == "NG"
    assert verdict.reason.startswith("Detected NG label")
    assert "classification" in verdict.reason
    assert classifier.received_crops == [b"crop-1"]


def test_inspection_service_flags_ng_from_detection(engine: ThresholdBusinessRulesEngine) -> None:
    """NG detections should trigger an NG verdict even without classifications."""

    detections = [DetectionResult(label="defect_a", confidence=0.8, mask=b"mask", crop=None)]
    detector = StubDetector(detections=detections)
    classifier = StubClassifier(results=[])
    service = InspectionService(detector=detector, classifier=classifier, rules_engine=engine)

    verdict = service.run(b"frame-bytes")

    assert verdict.status == "NG"
    assert verdict.reason.startswith("Detected NG label")
    assert "detection" in verdict.reason
    assert classifier.received_crops == [] or classifier.received_crops is None
