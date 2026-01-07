#!/usr/bin/env python3
import sys, yaml

def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def status(d):
    # Simple, explicit scoring (conservative by design):
    # - Missing/empty lists => DENIED
    # - Renewal required + long assumptions list or weak signals => CONSTRAINED
    # - Otherwise => GRANTED
    def nonempty_list(path):
        cur = d
        for p in path.split("."):
            cur = cur.get(p, None) if isinstance(cur, dict) else None
        return isinstance(cur, list) and len(cur) > 0 and all(isinstance(x, str) and x.strip() for x in cur)

    required_lists = [
        "trust_continuity.assumptions",
        "trust_continuity.continuity_signals",
        "trust_continuity.break_conditions",
        "boundary_conditions.operational",
        "boundary_conditions.temporal",
        "boundary_conditions.contextual",
    ]
    if not all(nonempty_list(p) for p in required_lists):
        return "DENIED"

    renewal = d.get("authority", {}).get("renewal_required", True)
    assumptions_len = len(d["trust_continuity"]["assumptions"])
    signals_len = len(d["trust_continuity"]["continuity_signals"])

    if renewal and (assumptions_len >= 6 or signals_len <= 1):
        return "CONSTRAINED"

    return "GRANTED"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: scripts/bcat_status.py <bcat.yaml>")
        sys.exit(2)
    d = load(sys.argv[1])
    s = status(d)
    print(s)
