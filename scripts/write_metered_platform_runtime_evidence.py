#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from stegcore.metered_platform import REQUIRED_RETIREMENT_GATES, evaluate_metered_platform


def main() -> int:
    cases = {
        "selection": {"scope": "REPLACEMENT_DESIGN_ONLY", "provider": "render", "evidence": {}},
        "retirement_denied": {"scope": "PROVIDER_RETIREMENT", "provider": "render", "evidence": {}},
        "retirement_complete": {
            "scope": "PROVIDER_RETIREMENT",
            "provider": "render",
            "evidence": {gate: True for gate in REQUIRED_RETIREMENT_GATES},
        },
    }
    evaluated = {name: evaluate_metered_platform(case) for name, case in cases.items()}
    evidence = {
        "contract": "metered-platform-replacement@1.0",
        "status": "pass",
        "checks": {
            "selection_allowed": evaluated["selection"]["reason_code"] == "replacement.selection_allowed",
            "incomplete_retirement_denied": evaluated["retirement_denied"]["reason_code"] == "retirement.evidence_incomplete",
            "complete_retirement_evaluated": evaluated["retirement_complete"]["reason_code"] == "retirement.evidence_complete",
            "provider_retirement_authority_false": all(not item["provider_retirement_authority"] for item in evaluated.values()),
            "cancellation_authority_false": all(not item["cancellation_authority"] for item in evaluated.values()),
            "continuity_receipt_minted_false": all(not item["continuity_receipt_minted"] for item in evaluated.values()),
        },
        "receipts": evaluated,
    }
    evidence["status"] = "pass" if all(evidence["checks"].values()) else "fail"
    path = Path("evidence/metered-platform-runtime-validation.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(path)
    return 0 if evidence["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
