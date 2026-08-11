from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .service import runtime_identity, self_test
from .steggate import AdmissibilityRequest, evaluate_admissibility
from .version import __version__


def _print(value: object) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def _evaluate(path: str) -> int:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    request = AdmissibilityRequest.model_validate(payload)
    result = evaluate_admissibility(request)
    _print(result.model_dump(mode="json"))
    return 0


def _self_test() -> int:
    result = self_test()
    _print(result)
    return 0 if result["state"] == "PASS" else 1


def _identity() -> int:
    _print(runtime_identity())
    return 0


def _serve(host: str, port: int) -> int:
    import uvicorn

    uvicorn.run("stegcore.service:app", host=host, port=port)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="steggate",
        description="Portable CLI for the canonical StegGate admissibility runtime.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    evaluate_parser = subparsers.add_parser(
        "evaluate", help="Evaluate one JSON commitment candidate through canonical StegGate."
    )
    evaluate_parser.add_argument("request", help="Path to an AdmissibilityRequest JSON file.")

    subparsers.add_parser(
        "self-test", help="Run deterministic ALLOW/DENY/REVIEW/FAIL_CLOSED contract checks."
    )
    subparsers.add_parser(
        "identity", help="Print the transport-independent canonical runtime identity."
    )

    serve_parser = subparsers.add_parser("serve", help="Run the StegGate HTTP service locally.")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", default=8000, type=int)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "evaluate":
        return _evaluate(args.request)
    if args.command == "self-test":
        return _self_test()
    if args.command == "identity":
        return _identity()
    if args.command == "serve":
        return _serve(args.host, args.port)
    raise AssertionError(f"unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
