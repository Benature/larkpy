"""Common utility helpers for larkpy."""

from __future__ import annotations
from typing import Dict, Any

__all__ = ["clean_params"]


def clean_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """Return a copy of params with entries whose value is None removed."""
    return {k: v for k, v in params.items() if v is not None}

