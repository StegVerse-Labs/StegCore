import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "validate_permission_admissibility_boundary.py"
spec = importlib.util.spec_from_file_location("pa_validator", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_permission_present_is_not_sufficient():
    result = module.evaluate_case({
        "consequence_bearing": True,
        "permission_present": True,
        "authority_current": False,
        "consent_or_standing_required": False,
        "consent_or_standing_current": None,
        "continuity_current": True,
        "governing_conditions_current": True,
        "consequence_attributable": True,
        "consequence_reconstructable": True,
    })
    assert result["decision"] == "DENY"
    assert result["admissible"] is False


def test_permission_absence_is_not_automatic_denial():
    result = module.evaluate_case({
        "consequence_bearing": True,
        "permission_present": False,
        "authority_current": True,
        "consent_or_standing_required": False,
        "consent_or_standing_current": None,
        "continuity_current": True,
        "governing_conditions_current": True,
        "consequence_attributable": True,
        "consequence_reconstructable": True,
    })
    assert result["decision"] == "ALLOW"
    assert result["admissible"] is True


def test_required_consent_or_standing_fails_closed():
    result = module.evaluate_case({
        "consequence_bearing": True,
        "permission_present": True,
        "authority_current": True,
        "consent_or_standing_required": True,
        "consent_or_standing_current": False,
        "continuity_current": True,
        "governing_conditions_current": True,
        "consequence_attributable": True,
        "consequence_reconstructable": True,
    })
    assert result["decision"] == "DENY"


def test_missing_current_evidence_defers():
    result = module.evaluate_case({
        "consequence_bearing": True,
        "permission_present": True,
        "authority_current": True,
        "consent_or_standing_required": False,
        "consent_or_standing_current": None,
        "continuity_current": None,
        "governing_conditions_current": True,
        "consequence_attributable": True,
        "consequence_reconstructable": True,
    })
    assert result["decision"] == "DEFER"
    assert result["admissible"] is False


def test_coordination_does_not_become_execution_authority():
    result = module.evaluate_case({
        "consequence_bearing": False,
        "permission_present": False,
    })
    assert result["decision"] == "ALLOW"
    assert result["execution_authority"] is False


def test_contract_semantic_suite():
    import json
    contract = json.loads(module.CONTRACT.read_text(encoding="utf-8"))
    assert module.validate_contract(contract) == []
