#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib

from stegcore.render_provider_state import evaluate_render_provider_state


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    source = pathlib.Path(args.source)
    if source.exists():
        report = json.loads(source.read_text())
    else:
        report = {
            "schema": "stegverse.governance.render_provider_state.v1",
            "provider_id": "render",
            "state": "BLOCKED_PARTIAL_RENDER_STATE",
            "api_state": "BLOCKED_SOURCE_UNAVAILABLE",
            "repository_configs": [],
            "services": [],
            "environment_values_retained": False,
            "deploy_hooks_retained": False,
            "credentials_retained": False,
            "raw_secret_material_retained": False,
            "manual_action_required": False,
            "production_mutation_allowed": False,
            "execution_authority": False,
            "traffic_cutover_authority": False,
            "cancellation_authority": False,
            "provider_retirement_authority": False,
            "continuity_receipt_minted": False,
            "report_sha256": None,
        }
    result = evaluate_render_provider_state(report)
    output = pathlib.Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
