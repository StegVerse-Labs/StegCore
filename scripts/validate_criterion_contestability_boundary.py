from __future__ import annotations

import json
from pathlib import Path

from stegcore.criterion_contestability import evaluate_criterion_contestability

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts" / "criterion-contestability-boundary.v1.json"


def base_candidate(**overrides):
    candidate = {
        "consequence_bearing": True,
        "trajectory_ids": ["trajectory-a", "trajectory-b"],
        "selected_criterion_id": "criterion-1",
        "criterion_provenance_bound": True,
        "criterion_contestable_at_commit": True,
        "criterion_authority_current": True,
        "relation_governed": True,
        "authority_current": True,
        "continuity_current": True,
        "governing_conditions_current": True,
        "consequence_attributable": True,
        "consequence_reconstructable": True,
        "consent_or_standing_required": False,
        "consent_or_standing_current": None,
    }
    candidate.update(overrides)
    return candidate


CASES = (
    ("parallel-visible-unbound-provenance-deny", base_candidate(criterion_provenance_bound=False), "DENY"),
    ("contestability-disabled-deny", base_candidate(criterion_contestable_at_commit=False), "DENY"),
    ("stale-criterion-authority-deny", base_candidate(criterion_authority_current=False), "DENY"),
    ("missing-required-consent-deny", base_candidate(consent_or_standing_required=True, consent_or_standing_current=False), "DENY"),
    ("parallel-contest-with-unresolved-authority-defer", base_candidate(criterion_authority_current=None), "DEFER"),
    ("all-current-allow", base_candidate(), "ALLOW"),
    ("orientation-only-no-execution-authority", base_candidate(consequence_bearing=False), "ALLOW"),
)


def main() -> None:
    contract = json.loads(CONTRACT.read_text())
    assert contract["contract_id"] == "CCB-001"
    assert contract["fail_closed"] is True
    assert contract["execution_authority"] is False
    assert contract["semantic_cases"] == [case[0] for case in CASES]

    for case_id, candidate, expected in CASES:
        result = evaluate_criterion_contestability(candidate)
        assert result["decision"] == expected, (case_id, result)
        assert result["orientation_used_as_authority"] is False
        assert result["contestability_used_as_admissibility"] is False
        assert result["synthetic_consensus_used"] is False
        assert result["execution_authority_conferred"] is False

    print("CRITERION_CONTESTABILITY_BOUNDARY=PASS")
    print(f"cases={len(CASES)}")


if __name__ == "__main__":
    main()
