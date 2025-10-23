"""Interface schemas for inspection verdict responses."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional

from backend.domain.entities import InspectionVerdict


@dataclass(frozen=True)
class InspectionVerdictDTO:
    """Data transfer object representing an inspection verdict."""

    status: str
    reason: str
    label: Optional[str] = None
    confidence: Optional[float] = None
    source: Optional[str] = None

    @classmethod
    def from_domain(cls, verdict: InspectionVerdict) -> "InspectionVerdictDTO":
        """Build a DTO from the domain inspection verdict."""

        return cls(
            status=verdict.status,
            reason=verdict.reason,
            label=verdict.label,
            confidence=verdict.confidence,
            source=verdict.source,
        )

    def model_dump(self) -> Dict[str, Any]:
        """Serialize the DTO to a plain dictionary for API responses."""

        return asdict(self)
