"""Unit tests for the threshold-based business rules engine."""

from __future__ import annotations

import pytest

from backend.domain.entities import ClassificationResult, DetectionResult
from backend.domain.services import LabelPolicy, ThresholdBusinessRulesEngine


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
    assert "detection" in verdict.reason


def test_engine_treats_unknown_labels_as_ng_when_disallowed(engine: ThresholdBusinessRulesEngine) -> None:
    """Unknown labels should trigger NG when ``allow_unknown`` is False."""

    detections = [DetectionResult(label="mystery", confidence=0.9, mask=b"mask", crop=None)]
    classifications: list[ClassificationResult] = []

    verdict = engine.evaluate(detections=detections, classifications=classifications)

    assert verdict.status == "NG"
    assert "Unknown label" in verdict.reason
    assert "detection" in verdict.reason


def test_engine_returns_ok_when_all_labels_are_known_and_safe(engine: ThresholdBusinessRulesEngine) -> None:
    """Known OK labels should result in an OK verdict."""

    detections = [DetectionResult(label="ok", confidence=0.8, mask=b"mask", crop=None)]
    classifications = [ClassificationResult(label="ok", confidence=0.9, crop_id="crop-1")]

    verdict = engine.evaluate(detections=detections, classifications=classifications)

    assert verdict.status == "OK"
    assert verdict.reason == engine.ok_reason


def test_engine_prioritises_highest_confidence_result(engine: ThresholdBusinessRulesEngine) -> None:
    """The engine should consider the highest-confidence NG label first."""

    low_conf_ng = DetectionResult(label="defect", confidence=0.61, mask=b"mask", crop=None)
    high_conf_ok = DetectionResult(label="ok", confidence=0.99, mask=b"mask", crop=None)
    # Classification list is intentionally unsorted to ensure internal ordering.
    classifications = [
        ClassificationResult(label="ok", confidence=0.95, crop_id="crop-1"),
        ClassificationResult(label="defect", confidence=0.88, crop_id="crop-2"),
    ]

    verdict = engine.evaluate(
        detections=[high_conf_ok, low_conf_ng],
        classifications=classifications,
    )

    assert verdict.status == "NG"
    assert "classification" in verdict.reason


def test_engine_ignores_unknown_labels_below_threshold(engine: ThresholdBusinessRulesEngine) -> None:
    """Unknown labels should not trigger NG when confidence is below the threshold."""

    detections = [DetectionResult(label="mystery", confidence=0.4, mask=b"mask", crop=None)]

    verdict = engine.evaluate(detections=detections, classifications=[])

    assert verdict.status == "OK"


def test_engine_honours_label_specific_thresholds() -> None:
    """Label policies should override the default NG confidence threshold."""

    engine = ThresholdBusinessRulesEngine(
        ng_labels=frozenset({"scratch"}),
        ok_labels=frozenset({"ok"}),
        confidence_threshold=0.5,
        allow_unknown=True,
        label_policies=[LabelPolicy(label="scratch", confidence_threshold=0.85)],
    )
    low_confidence_detection = DetectionResult(label="scratch", confidence=0.7, mask=b"mask", crop=None)
    high_confidence_detection = DetectionResult(label="scratch", confidence=0.9, mask=b"mask", crop=None)

    verdict = engine.evaluate(detections=[low_confidence_detection], classifications=[])
    assert verdict.status == "OK"

    verdict = engine.evaluate(detections=[high_confidence_detection], classifications=[])
    assert verdict.status == "NG"


def test_engine_renders_custom_reason_from_policy() -> None:
    """Custom reason templates should be used when supplied via label policies."""

    engine = ThresholdBusinessRulesEngine(
        ng_labels=frozenset(),
        ok_labels=frozenset({"ok"}),
        confidence_threshold=0.6,
        allow_unknown=True,
        label_policies=[
            LabelPolicy(
                label="overheat",
                confidence_threshold=0.6,
                reason_template="Thermal limit exceeded by {label} via {source}",
            )
        ],
    )
    detection = DetectionResult(label="overheat", confidence=0.75, mask=b"mask", crop=None)

    verdict = engine.evaluate(detections=[detection], classifications=[])

    assert verdict.status == "NG"
    assert verdict.reason == "Thermal limit exceeded by overheat via detection"


def test_engine_allows_source_specific_thresholds() -> None:
    """Policies should select thresholds based on the originating signal."""

    engine = ThresholdBusinessRulesEngine(
        ng_labels=frozenset({"scratch"}),
        ok_labels=frozenset({"ok"}),
        confidence_threshold=0.5,
        allow_unknown=True,
        label_policies=[
            LabelPolicy(
                label="scratch",
                per_source_thresholds={"detection": 0.85, "classification": 0.65},
            )
        ],
    )
    detection = DetectionResult(label="scratch", confidence=0.8, mask=b"mask", crop=None)
    classification = ClassificationResult(label="scratch", confidence=0.7, crop_id="crop-1")

    verdict = engine.evaluate(detections=[detection], classifications=[classification])

    assert verdict.status == "NG"
    assert verdict.reason.endswith("classification")


def test_engine_uses_source_specific_reason_templates() -> None:
    """Policies should prefer per-source reason templates when provided."""

    engine = ThresholdBusinessRulesEngine(
        ng_labels=frozenset({"scratch"}),
        ok_labels=frozenset({"ok"}),
        confidence_threshold=0.5,
        allow_unknown=True,
        label_policies=[
            LabelPolicy(
                label="scratch",
                per_source_thresholds={"detection": 0.6},
                per_source_reason_templates={
                    "detection": "Scratch detected on conveyor via {source}",
                },
            )
        ],
    )
    detection = DetectionResult(label="scratch", confidence=0.75, mask=b"mask", crop=None)

    verdict = engine.evaluate(detections=[detection], classifications=[])

    assert verdict.status == "NG"
    assert verdict.reason == "Scratch detected on conveyor via detection"
