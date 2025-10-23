"""Infrastructure for managing model artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Optional


class ModelRegistry:
    """Simple in-memory registry placeholder.

    Replace with a real persistence layer (database or file-based metadata store).
    """

    def __init__(self) -> None:
        self._detector: Optional[Path] = None
        self._classifier: Optional[Path] = None

    def register_detector(self, path: Path) -> None:
        """Register a detector checkpoint."""

        self._detector = path

    def register_classifier(self, path: Path) -> None:
        """Register a classifier checkpoint."""

        self._classifier = path

    def get_detector(self) -> Optional[Path]:
        """Retrieve the current detector path."""

        return self._detector

    def get_classifier(self) -> Optional[Path]:
        """Retrieve the current classifier path."""

        return self._classifier
