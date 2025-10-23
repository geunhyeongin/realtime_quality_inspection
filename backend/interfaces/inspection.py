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

    def model_dump(self, *, exclude_none: bool = False) -> Dict[str, Any]:
        """Serialize the DTO to a plain dictionary for API responses.

        Parameters
        ----------
        exclude_none:
            When ``True`` optional fields whose value is ``None`` will be
            omitted from the resulting dictionary. This mirrors the behaviour of
            Pydantic's ``model_dump`` helper and keeps wire responses compact for
            OK verdicts that do not provide trigger metadata.
        """

        payload = asdict(self)
        if not exclude_none:
            return payload
        return {key: value for key, value in payload.items() if value is not None}
