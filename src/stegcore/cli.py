from __future__ import annotations

import json
import argparse

from .state_engine import StateEngine


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Simple StegCore CLI demo (in-memory)."
    )
    parser.add_argument(
        "--list-nodes",
        action="store_true",
        help="List current nodes and their states.",
    )
    args = parser.parse_args()

    engine = StateEngine()
    # Demo seed data
    engine.mark_healthy(
        node="CosDenOS",
        version="0.1.0",
        metadata={"endpoint": "https://cosden.stegverse.internal"},
    )
    engine.mark_degraded(node="SCW", version="4.0.0", metadata={"reason": "WIP"})

    if args.list_nodes:
        nodes = engine.list_nodes()
        out = {k: v.to_dict() for k, v in nodes.items()}
        print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
