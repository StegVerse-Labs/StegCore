#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
DEFAULT_REGISTRY=Path('registry/stegverse-001-002.activation.json')
def main(argv):
    path=Path(argv[1]) if len(argv)>1 else DEFAULT_REGISTRY
    if not path.exists(): print(json.dumps({'passed':False,'reason':'registry_not_found','registry':str(path)},indent=2)); return 2
    registry=json.loads(path.read_text()); required=registry.get('required_paths',[]); missing=[p for p in required if not Path(p).exists()]; passed=not missing
    print(json.dumps({'passed':passed,'registry':str(path),'activation_target':registry.get('activation_target'),'required_paths_checked':len(required),'missing_paths':missing,'status':'ACTIVATION_PATHS_PRESENT' if passed else 'ACTIVATION_PATHS_MISSING'},indent=2)); return 0 if passed else 1
if __name__=='__main__': raise SystemExit(main(sys.argv))
