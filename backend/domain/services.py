"""Domain services encapsulating business rules for inspection results.

This module currently provides a :class:`ThresholdBusinessRulesEngine` that
consolidates detection and classification signals into a domain
``InspectionVerdict``. The engine remains intentionally small so that
alternative strategies (for example, a fuzzy rules engine or model-based
policy) can be introduced without rewriting the surrounding application
workflow.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, FrozenSet, Iterable, Optional

from backend.domain.entities import ClassificationResult, DetectionResult, InspectionVerdict


@dataclass(frozen=True)
class LabelPolicy:
    """Configuration describing how a specific label should be evaluated."""

    label: str
    confidence_threshold: Optional[float] = None
    reason_template: Optional[str] = None

    def get_reason(
        self,
        *,
        default_template: str,
        label: str,
        confidence: float,
        source: str,
    ) -> str:
        """Render the NG reason for the configured label."""

        template = self.reason_template or default_template
        return template.format(label=label, confidence=confidence, source=source)


@dataclass(frozen=True)
class ThresholdBusinessRulesEngine:
    """Evaluate inspection outcomes based on label confidence thresholds.

    The engine marks a frame as ``NG`` when either a detection or classification
    result matches one of the configured ``ng_labels`` with a confidence score
    above ``confidence_threshold``. Per-label overrides can be provided via
    :class:`LabelPolicy` instances to customise thresholds and reason strings.
    Labels that are not present in either the ``ng_labels`` or ``ok_labels``
    collections are treated as unknown and can be flagged as ``NG`` depending on
    ``allow_unknown``.
    """

    ng_labels: FrozenSet[str]
    ok_labels: FrozenSet[str]
    confidence_threshold: float = 0.5
    allow_unknown: bool = True
    ok_reason: str = "All detections passed inspection."
    ng_reason_template: str = (
        "Detected NG label: {label} ({confidence:.2f}) via {source}"
    )
    unknown_reason_template: str = (
        "Unknown label detected: {label} ({confidence:.2f}) via {source}"
    )
    label_policies: Optional[Iterable[LabelPolicy]] = None

    def __post_init__(self) -> None:
        """Normalise label collections to frozen sets for deterministic behaviour."""

        policies = self.label_policies or []
        policy_index: Dict[str, LabelPolicy] = {policy.label: policy for policy in policies}
        combined_ng_labels = set(self.ng_labels) | set(policy_index.keys())

        object.__setattr__(self, "ng_labels", frozenset(combined_ng_labels))
        object.__setattr__(self, "ok_labels", frozenset(self.ok_labels))
        object.__setattr__(self, "_policy_index", policy_index)

    def evaluate(
        self,
        detections: Iterable[DetectionResult],
        classifications: Iterable[ClassificationResult],
    ) -> InspectionVerdict:
        """Combine detection and classification signals into a verdict."""

        sorted_classifications = sorted(
            classifications,
            key=lambda result: result.confidence,
            reverse=True,
        )
        for result in sorted_classifications:
            verdict = self._evaluate_label(
                label=result.label,
                confidence=result.confidence,
                source="classification",
            )
            if verdict is not None:
                return verdict

        sorted_detections = sorted(
            detections,
            key=lambda detection: detection.confidence,
            reverse=True,
        )
        for detection in sorted_detections:
            verdict = self._evaluate_label(
                label=detection.label,
                confidence=detection.confidence,
                source="detection",
            )
            if verdict is not None:
                return verdict

        return InspectionVerdict(status="OK", reason=self.ok_reason)

    def _evaluate_label(
        self,
        *,
        label: str,
        confidence: float,
        source: str,
    ) -> InspectionVerdict | None:
        """Determine if a single label warrants an ``NG`` verdict."""

        policy = self._policy_index.get(label)
        threshold = (
            policy.confidence_threshold
            if policy and policy.confidence_threshold is not None
            else self.confidence_threshold
        )

        if label in self.ng_labels and confidence >= threshold:
            reason = (
                policy.get_reason(
                    default_template=self.ng_reason_template,
                    label=label,
                    confidence=confidence,
                    source=source,
                )
                if policy
                else self.ng_reason_template.format(
                    label=label,
                    confidence=confidence,
                    source=source,
                )
            )
            return InspectionVerdict(status="NG", reason=reason)

        known_labels = self.ng_labels | self.ok_labels
        if (
            label not in known_labels
            and not self.allow_unknown
            and confidence >= self.confidence_threshold
        ):
            return InspectionVerdict(
                status="NG",
                reason=self.unknown_reason_template.format(
                    label=label,
                    confidence=confidence,
                    source=source,
                ),
            )

        return None
