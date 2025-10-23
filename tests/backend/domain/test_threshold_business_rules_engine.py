"""Unit tests for the threshold-based business rules engine."""

from __future__ import annotations

import pytest

from backend.domain.entities import ClassificationResult, DetectionResult
from backend.domain.services import ThresholdBusinessRulesEngine


@pytest.fixture()
def engine() -> ThresholdBusinessRulesEngine:
    """Instantiate the engine with simple OK/NG label sets."""

    return ThresholdBusinessRulesEngine(
        ng_labels=frozenset({"ng", "defect"}),
        ok_labels=frozenset({"ok"}),
        confidence_threshold=0.6,
        allow_unknown=False,
    )


def test_engine_returns_ng_for_high_confidence_ng_label(engine: ThresholdBusinessRulesEngine) -> None:
    """A high-confidence NG label should immediately trigger an NG verdict."""

    detections = [DetectionResult(label="defect", confidence=0.95, mask=b"mask", crop=None)]
    classifications: list[ClassificationResult] = []

    verdict = engine.evaluate(detections=detections, classifications=classifications)

    assert verdict.status == "NG"
    assert "defect" in verdict.reason


def test_engine_treats_unknown_labels_as_ng_when_disallowed(engine: ThresholdBusinessRulesEngine) -> None:
    """Unknown labels should trigger NG when ``allow_unknown`` is False."""

    detections = [DetectionResult(label="mystery", confidence=0.9, mask=b"mask", crop=None)]
    classifications: list[ClassificationResult] = []

    verdict = engine.evaluate(detections=detections, classifications=classifications)

    assert verdict.status == "NG"
    assert "Unknown label" in verdict.reason


def test_engine_returns_ok_when_all_labels_are_known_and_safe(engine: ThresholdBusinessRulesEngine) -> None:
    """Known OK labels should result in an OK verdict."""

    detections = [DetectionResult(label="ok", confidence=0.8, mask=b"mask", crop=None)]
    classifications = [ClassificationResult(label="ok", confidence=0.9, crop_id="crop-1")]

    verdict = engine.evaluate(detections=detections, classifications=classifications)

    assert verdict.status == "OK"
    assert verdict.reason == engine.ok_reason
