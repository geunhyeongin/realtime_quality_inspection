"""Domain services encapsulating business rules for inspection results."""

from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet, Iterable

from backend.domain.entities import ClassificationResult, DetectionResult, InspectionVerdict


@dataclass(frozen=True)
class ThresholdBusinessRulesEngine:
    """Evaluate inspection outcomes based on label confidence thresholds.

    The engine marks a frame as ``NG`` when either a detection or classification
    result matches one of the configured ``ng_labels`` with a confidence score
    above ``confidence_threshold``. Labels that are not present in either the
    ``ng_labels`` or ``ok_labels`` collections are treated as unknown and can be
    flagged as ``NG`` depending on ``allow_unknown``.
    """

    ng_labels: FrozenSet[str]
    ok_labels: FrozenSet[str]
    confidence_threshold: float = 0.5
    allow_unknown: bool = True
    ok_reason: str = "All detections passed inspection."
    ng_reason_template: str = "Detected NG label: {label} ({confidence:.2f})"
    unknown_reason_template: str = "Unknown label detected: {label}"

    def evaluate(
        self,
        detections: Iterable[DetectionResult],
        classifications: Iterable[ClassificationResult],
    ) -> InspectionVerdict:
        """Combine detection and classification signals into a verdict."""

        for result in classifications:
            verdict = self._evaluate_label(
                label=result.label,
                confidence=result.confidence,
                source="classification",
            )
            if verdict is not None:
                return verdict

        for detection in detections:
            verdict = self._evaluate_label(
                label=detection.label,
                confidence=detection.confidence,
                source="detection",
            )
            if verdict is not None:
                return verdict

        return InspectionVerdict(status="OK", reason=self.ok_reason)

    def _evaluate_label(
        self, label: str, confidence: float, source: str
    ) -> InspectionVerdict | None:
        """Determine if a single label warrants an ``NG`` verdict."""

        if label in self.ng_labels and confidence >= self.confidence_threshold:
            return InspectionVerdict(
                status="NG",
                reason=self.ng_reason_template.format(
                    label=label, confidence=confidence, source=source
                ),
                label=label,
                confidence=confidence,
                source=source,
            )

        known_labels = self.ng_labels | self.ok_labels
        if label not in known_labels and not self.allow_unknown:
            return InspectionVerdict(
                status="NG",
                reason=self.unknown_reason_template.format(label=label, source=source),
                label=label,
                confidence=confidence,
                source=source,
            )

        return None
