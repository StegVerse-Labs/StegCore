from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class StegCoreConfig:
    """
    Placeholder for future configuration.

    Later this can hold:
    - persistence backend config
    - security settings
    - cluster/node identifiers
    """
    persistence_backend: Optional[str] = None
