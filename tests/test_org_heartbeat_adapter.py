from __future__ import annotations
import json,subprocess,sys
from pathlib import Path

def test_heartbeat_return_echoes_authority_bound_fields(tmp_path: Path):
    root=Path(__file__).resolve().parents[1]
    assertion={
        'schema':'stegverse.org-heartbeat/v1','claimant_id':'TASK-TEST-0001',
        'repository':'StegVerse-Labs/StegCore','epoch':4,'nonce':'abc123',
        'claims':[],'fencing_token':7,'scope':{'contracts':[],'release_surfaces':[]},
        'policy_version':'stegverse.org-state/v0.2','evidence_pointer':None
    }
    source=tmp_path/'assertion.json'; output=tmp_path/'return.json'
    source.write_text(json.dumps(assertion))
    subprocess.run([sys.executable,str(root/'scripts/produce_org_heartbeat_return.py'),str(source),str(output)],cwd=root,check=True)
    result=json.loads(output.read_text())
    assert result['nonce']=='abc123'
    assert result['epoch']==4
    assert result['fencing_token']==7
    assert result['repository']=='StegVerse-Labs/StegCore'
    assert result['authority_effect']=='none'
    assert result['execution_authority'] is False
    assert result['release_authority'] is False
    assert result['continuity_receipt_minted'] is False
