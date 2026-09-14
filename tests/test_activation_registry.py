from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]; REGISTRY=ROOT/'registry'/'stegverse-001-002.activation.json'
def load(): return json.loads(REGISTRY.read_text())
def test_activation_registry_is_valid_json():
    d=load(); assert d['registry_id']=='stegverse_001_002_activation_registry'; assert d['status'] in {'activation_candidate','activated'}
def test_activation_registry_result_matches_status():
    d=load(); expected='ACTIVATED' if d['status']=='activated' else 'ACTIVATION_CANDIDATE'; assert d['current_registry_result']['status']==expected
def test_activation_registry_declares_required_entities():
    ids={e['id'] for e in load()['entities']}; assert {'StegVerse-001','StegVerse-002'}<=ids
def test_activation_registry_declares_required_paths():
    paths=set(load()['required_paths']); assert {'entities/stegverse-001.dc.yml','entities/stegverse-002.mr.yml','tools/evaluate_admissibility.py','.github/workflows/stegverse-001-002-validator.yml'}<=paths
