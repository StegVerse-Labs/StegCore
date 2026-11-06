"""Ruling StegVerse-org/.github#167 c6393224851 (3): KV <-> SKAP is the in-KV gate, never an InTr hop.

The vendored StegOS registry must not carry the retired intra-organisation profiles, under any alias.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "contracts" / "stegos_universal_intr_snapshot"
RETIRED = {"kv-skap", "kv-skap-custody", "kv-skap-account-metadata"}


def test_snapshot_registry_carries_no_kv_skap_intr_profile():
    registry = json.loads((SNAP / "specs" / "universal-intr-connector-profiles.v1.json").read_text(encoding="utf-8"))
    ids = {p["profile_id"] for p in registry["profiles"]}
    assert not RETIRED & ids
    for p in registry["profiles"]:
        assert {p["source"]["boundary"], p["destination"]["boundary"]} != {"KV", "SKAP_VAULT"}, p["profile_id"]
    assert "governance-external-action" in ids


def test_snapshot_is_linked_by_hash_to_one_stegos_commit():
    manifest = json.loads((SNAP / "manifest.json").read_text(encoding="utf-8"))
    commit = manifest["stegos_source_commit"]
    assert len(commit) == 40 and int(commit, 16) >= 0
    verifier = (ROOT / "scripts" / "verify_stegos_universal_intr_snapshot.py").read_text(encoding="utf-8")
    assert verifier.count(commit) == 2
