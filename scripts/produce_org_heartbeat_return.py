#!/usr/bin/env python3
from __future__ import annotations
import json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def fail(m): print(f'ERROR: {m}',file=sys.stderr); raise SystemExit(1)
def main():
 if len(sys.argv)!=3: fail('usage: produce_org_heartbeat_return.py ASSERTION OUTPUT')
 assertion=Path(sys.argv[1]); output=Path(sys.argv[2]); a=json.loads(assertion.read_text())
 if a.get('schema')!='stegverse.org-heartbeat/v1': fail('unsupported assertion schema')
 repo='StegVerse-Labs/StegCore'
 if a.get('repository')!=repo: fail('assertion repository mismatch')
 commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 r={'schema':'stegverse.org-heartbeat-return/v1','assertion_file':assertion.name,'claimant_id':a['claimant_id'],'repository':repo,'epoch':a['epoch'],'nonce':a['nonce'],'claims':a.get('claims',[]),'fencing_token':a['fencing_token'],'scope':a.get('scope',{}),'policy_version':a['policy_version'],'evidence_pointer':commit,'repository_commit':commit,'authority_effect':'none','continuity_receipt_minted':False,'execution_authority':False,'release_authority':False}
 output.parent.mkdir(parents=True,exist_ok=True); output.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n'); print(output)
if __name__=='__main__': main()
