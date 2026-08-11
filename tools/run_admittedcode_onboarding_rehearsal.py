#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str], *, cwd: Path) -> tuple[int, float, str, str]:
    start = time.perf_counter()
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False, timeout=180)
    return proc.returncode, (time.perf_counter() - start) * 1000, proc.stdout, proc.stderr


def main() -> int:
    parser = argparse.ArgumentParser(description="Mechanical fresh-environment onboarding rehearsal for AdmittedCode.")
    parser.add_argument("--output", default="artifacts/admittedcode-onboarding-rehearsal.json")
    args = parser.parse_args()

    start_total = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="admittedcode-onboarding-") as td:
        venv = Path(td) / "venv"
        rc, venv_ms, _, err = run([sys.executable, "-m", "venv", str(venv)], cwd=ROOT)
        if rc != 0:
            print(err, file=sys.stderr)
            return 2
        python = venv / "bin" / "python"
        steggate = venv / "bin" / "steggate"
        rc, install_ms, _, err = run([str(python), "-m", "pip", "install", "--disable-pip-version-check", "-e", str(ROOT)], cwd=ROOT)
        if rc != 0:
            print(err, file=sys.stderr)
            return 3

        rc, identity_ms, identity_out, identity_err = run([str(steggate), "identity"], cwd=ROOT)
        if rc != 0:
            print(identity_err, file=sys.stderr)
            return 4
        identity = json.loads(identity_out)

        rc, allow_ms, allow_out, allow_err = run([str(steggate), "evaluate", "examples/steggate_allow_request.json"], cwd=ROOT)
        if rc != 0:
            print(allow_err, file=sys.stderr)
            return 5
        allow = json.loads(allow_out)

        deny_payload = json.loads((ROOT / "examples/steggate_allow_request.json").read_text(encoding="utf-8"))
        deny_payload["execution"]["policy_current"] = False
        deny_path = Path(td) / "deny.json"
        deny_path.write_text(json.dumps(deny_payload), encoding="utf-8")
        rc, deny_ms, deny_out, deny_err = run([str(steggate), "evaluate", str(deny_path)], cwd=ROOT)
        if rc != 0:
            print(deny_err, file=sys.stderr)
            return 6
        deny = json.loads(deny_out)

    receipt = {
        "schema_version": "stegverse.admittedcode.onboarding-rehearsal.v1",
        "measured_at": datetime.now(timezone.utc).isoformat(),
        "measurement_type": "AUTOMATED_MECHANICAL_REHEARSAL_NOT_HUMAN_USABILITY",
        "venv_create_ms": round(venv_ms, 3),
        "editable_install_ms": round(install_ms, 3),
        "identity_ms": round(identity_ms, 3),
        "first_allow_ms": round(allow_ms, 3),
        "induced_deny_ms": round(deny_ms, 3),
        "total_rehearsal_ms": round((time.perf_counter() - start_total) * 1000, 3),
        "runtime_identity_correct": identity.get("runtime_identity") == "stegverse:steggate:canonical:three-layer:v1",
        "allow_correct": allow.get("disposition") == "ALLOW",
        "deny_correct": deny.get("disposition") == "DENY",
        "deny_reasons_present": bool(deny.get("reasons")),
        "human_install_to_first_allow_minutes": None,
        "human_failed_request_diagnosis_minutes": None,
        "human_measurement_status": "REQUIRES_UNFAMILIAR_OPERATOR",
    }
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if all((receipt["runtime_identity_correct"], receipt["allow_correct"], receipt["deny_correct"], receipt["deny_reasons_present"])) else 7


if __name__ == "__main__":
    sys.exit(main())
