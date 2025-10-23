"""Tests for interface-level inspection verdict DTOs."""

from __future__ import annotations

from backend.domain.entities import InspectionVerdict
from backend.interfaces import InspectionVerdictDTO


def test_inspection_verdict_dto_from_domain_populates_optional_fields() -> None:
    """DTO should mirror the domain verdict including optional metadata."""

    verdict = InspectionVerdict(
        status="NG",
        reason="Detected NG label: defect_a (0.92) via detection",
        label="defect_a",
        confidence=0.92,
        source="detection",
    )

    dto = InspectionVerdictDTO.from_domain(verdict)

    assert dto.status == verdict.status
    assert dto.reason == verdict.reason
    assert dto.label == verdict.label
    assert dto.confidence == verdict.confidence
    assert dto.source == verdict.source
    assert dto.model_dump() == {
        "status": verdict.status,
        "reason": verdict.reason,
        "label": verdict.label,
        "confidence": verdict.confidence,
        "source": verdict.source,
    }


def test_inspection_verdict_dto_supports_missing_metadata() -> None:
    """Optional metadata should be absent when the domain verdict omits it."""

    verdict = InspectionVerdict(status="OK", reason="All detections passed inspection.")

    dto = InspectionVerdictDTO.from_domain(verdict)

    assert dto.status == "OK"
    assert dto.reason == verdict.reason
    assert dto.label is None
    assert dto.confidence is None
    assert dto.source is None
    assert dto.model_dump() == {
        "status": "OK",
        "reason": verdict.reason,
        "label": None,
        "confidence": None,
        "source": None,
    }


def test_inspection_verdict_dto_model_dump_can_exclude_none_fields() -> None:
    """DTO serialization should support omitting ``None`` values."""

    verdict = InspectionVerdict(status="OK", reason="All detections passed inspection.")

    dto = InspectionVerdictDTO.from_domain(verdict)

    assert dto.model_dump(exclude_none=True) == {
        "status": "OK",
        "reason": verdict.reason,
    }
