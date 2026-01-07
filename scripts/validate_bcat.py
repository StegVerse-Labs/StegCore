import sys
import yaml

REQUIRED_TOP_LEVEL_KEYS = [
    "bcat_version",
    "module",
    "authority",
    "trust_continuity",
    "boundary_conditions",
    "degradation_behavior",
    "human_accountability",
    "non_action_policy",
]

def fail(msg):
    print(f"BCAT VALIDATION FAILED: {msg}")
    sys.exit(1)

def main(path):
    try:
        with open(path, "r") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        fail(f"Unable to read BCAT declaration: {e}")

    for key in REQUIRED_TOP_LEVEL_KEYS:
        if key not in data:
            fail(f"Missing required section: {key}")

    if not data["non_action_policy"].get("refusal_is_success", False):
        fail("BCAT requires refusal to be treated as a valid success outcome")

    if not data["degradation_behavior"].get("explanation_required", False):
        fail("BCAT requires explainable degradation behavior")

    print("BCAT VALIDATION PASSED")
    sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        fail("Usage: validate_bcat.py <bcat_declaration.yaml>")
    main(sys.argv[1])
