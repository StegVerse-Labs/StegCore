#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def main() -> int:
    source = Path(sys.argv[1] if len(sys.argv) > 1 else "evidence/pytest-results.xml")
    output = Path(sys.argv[2] if len(sys.argv) > 2 else "evidence/pytest-failure-status.json")
    output.parent.mkdir(parents=True, exist_ok=True)

    if not source.exists():
        record = {
            "status": "blocked",
            "reason": "pytest_report_missing",
            "failed_tests": [],
            "error_tests": [],
            "manual_action_required": False,
        }
    else:
        root = ET.parse(source).getroot()
        suites = [root] if root.tag == "testsuite" else list(root.findall("testsuite"))
        failed: list[str] = []
        errored: list[str] = []
        totals = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
        for suite in suites:
            for key in totals:
                totals[key] += int(suite.attrib.get(key, 0))
            for case in suite.findall("testcase"):
                ident = f"{case.attrib.get('classname', '')}::{case.attrib.get('name', '')}".strip(":")
                if case.find("failure") is not None:
                    failed.append(ident)
                if case.find("error") is not None:
                    errored.append(ident)
        record = {
            "status": "pass" if not failed and not errored else "fail",
            "totals": totals,
            "failed_tests": sorted(failed),
            "error_tests": sorted(errored),
            "manual_action_required": False,
        }

    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
