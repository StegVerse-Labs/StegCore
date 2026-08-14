from __future__ import annotations

import json
from pathlib import Path

from stegcore.capability_registry import load_capability_registry, validate_capability_registry


DEFAULT_REGISTRY = Path("management/admissible-existence-capability-registry.json")


def main() -> int:
    registry = load_capability_registry(DEFAULT_REGISTRY)
    result = validate_capability_registry(registry)
    print(json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True))
    return 0 if result.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
