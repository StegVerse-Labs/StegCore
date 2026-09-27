import hashlib
import json
import unittest
from benchmarks.svg_governance_cycle import STAGES, benchmark, evaluate_trace, specimen


def rebind(t):
    t["evidence"] = {}
    t["evidence"]["synthetic_predecessor_hash"] = hashlib.sha256(json.dumps(
        [t[s] if s != 'evidence' else {} for s in STAGES[:-1]], sort_keys=True, separators=(",", ":")
    ).encode()).hexdigest()
    return t


class SVGTraceTests(unittest.TestCase):
    def test_allow_deny_fail_closed(self):
        for d in ("ALLOW", "DENY", "FAIL_CLOSED"):
            self.assertEqual(evaluate_trace(specimen(d))["disposition"], d)

    def test_stale_revoked_replay(self):
        for key in ("stale_constraint", "revoked", "replay"):
            t = specimen()
            t[key] = True
            self.assertEqual(evaluate_trace(t)["disposition"], "DENY")

    def test_missing_partial_interrupted(self):
        t = specimen()
        del t["evidence"]
        self.assertEqual(evaluate_trace(t)["disposition"], "FAIL_CLOSED")
        for key in ("partial_recording", "interrupted"):
            t = specimen()
            t[key] = True
            self.assertEqual(evaluate_trace(t)["disposition"], "FAIL_CLOSED")

    def test_lineage_and_consequence(self):
        t = specimen()
        t["observation"] = "changed"
        self.assertEqual(evaluate_trace(t)["reason"], "LINEAGE_MISMATCH")
        t = specimen("DENY")
        t["consequence"] = "SIMULATED"
        self.assertEqual(evaluate_trace(rebind(t))["reason"], "UNAUTHORIZED_CONSEQUENCE")

    def test_benchmark(self):
        r = benchmark(8)
        self.assertEqual(r["evidence_class"], "SYNTHETIC_SOURCE_ONLY")
        self.assertEqual(r["iterations"], 8)


if __name__ == "__main__":
    unittest.main()
