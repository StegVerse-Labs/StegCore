#!/usr/bin/env python3
import sys
import yaml

REQUIRED_TOP_LEVEL = [
    "bcat_version",
    "module",
    "authority",
    "trust_continuity",
    "boundary_conditions",
    "degradation_behavior",
    "human_accountability",
    "non_action_policy",
]

ALLOWED_MODULE_TYPES = {"agent","service","workflow","automation","infrastructure","machinery"}
ALLOWED_DEGRADE_MODES = {"constrain","suspend","refuse"}

def die(msg: str, code: int = 1):
    print(f"BCAT VALIDATION FAILED: {msg}")
    sys.exit(code)

def require(d, path: str):
    cur = d
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            die(f"Missing required field: {path}")
        cur = cur[part]
    return cur

def main():
    if len(sys.argv) != 2:
        die("Usage: scripts/validate_bcat.py <bcat.yaml>")

    path = sys.argv[1]
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        die(f"Unable to read YAML: {e}")

    if not isinstance(data, dict):
        die("BCAT declaration must be a YAML mapping/object")

    for key in REQUIRED_TOP_LEVEL:
        if key not in data:
            die(f"Missing required section: {key}")

    # Version
    if str(data["bcat_version"]) not in {"1.0", "1"}:
        die("Unsupported bcat_version (expected 1.0)")

    # Module
    require(data, "module.name")
    require(data, "module.owner")
    mtype = require(data, "module.type")
    if mtype not in ALLOWED_MODULE_TYPES:
        die(f"module.type must be one of: {sorted(ALLOWED_MODULE_TYPES)}")

    # Authority
    require(data, "authority.source")
    require(data, "authority.scope")
    rr = require(data, "authority.renewal_required")
    if not isinstance(rr, bool):
        die("authority.renewal_required must be boolean")

    # Trust continuity
    assumptions = require(data, "trust_continuity.assumptions")
    signals = require(data, "trust_continuity.continuity_signals")
    breaks = require(data, "trust_continuity.break_conditions")
    for k, v in [("assumptions", assumptions), ("continuity_signals", signals), ("break_conditions", breaks)]:
        if not isinstance(v, list) or not v or not all(isinstance(x, str) and x.strip() for x in v):
            die(f"trust_continuity.{k} must be a non-empty list of non-empty strings")

    # Boundary conditions
    for k in ["operational", "temporal", "contextual"]:
        v = require(data, f"boundary_conditions.{k}")
        if not isinstance(v, list) or not v or not all(isinstance(x, str) and x.strip() for x in v):
            die(f"boundary_conditions.{k} must be a non-empty list of non-empty strings")

    # Degradation behavior
    modes = require(data, "degradation_behavior.modes")
    if not isinstance(modes, list) or not modes:
        die("degradation_behavior.modes must be a non-empty list")
    bad = [m for m in modes if m not in ALLOWED_DEGRADE_MODES]
    if bad:
        die(f"Invalid degradation modes: {bad}. Allowed: {sorted(ALLOWED_DEGRADE_MODES)}")
    if require(data, "degradation_behavior.explanation_required") is not True:
        die("degradation_behavior.explanation_required must be true")

    # Human accountability
    require(data, "human_accountability.custodian")
    require(data, "human_accountability.escalation_path")

    # Non-action policy (core BCAT invariant)
    if require(data, "non_action_policy.refusal_is_success") is not True:
        die("non_action_policy.refusal_is_success must be true (BCAT invariant)")
    if require(data, "non_action_policy.explanation_required") is not True:
        die("non_action_policy.explanation_required must be true (BCAT invariant)")

    print("BCAT VALIDATION PASSED")
    sys.exit(0)

if __name__ == "__main__":
    main()
