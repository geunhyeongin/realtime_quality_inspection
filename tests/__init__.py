"""Test package configuration."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the repository root is available for absolute imports such as ``backend.*``.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
