#!/usr/bin/env python3
"""CLI wrapper for the installable StegVerse v1.3 conformance module."""
from __future__ import annotations

import argparse
from pathlib import Path

from stegcore.spec_conformance import (
    load_json,
    validate_action_request,
    validate_decision_receipt,
    validate_execution_receipt,
    validate_replay_result,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=("action", "decision", "execution", "replay"))
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    record = load_json(args.path)
    validators = {
        "action": validate_action_request,
        "decision": validate_decision_receipt,
        "execution": validate_execution_receipt,
        "replay": validate_replay_result,
    }
    validators[args.kind](record)
    print(f"PASS: {args.kind} conformance: {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
