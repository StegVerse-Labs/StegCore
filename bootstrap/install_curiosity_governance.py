from __future__ import annotations

import base64
import hashlib
import io
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_B64 = ROOT / "bootstrap" / "curiosity-governance-v1.tar.gz.b64"
EXPECTED_SHA256 = "f9d56e25b4e261ded95b64f300342221ab900136b3f319c07cca089317218aee"

raw = base64.b64decode(ARCHIVE_B64.read_text(encoding="ascii"), validate=True)
actual_sha256 = hashlib.sha256(raw).hexdigest()
if actual_sha256 != EXPECTED_SHA256:
    raise SystemExit(
        f"bootstrap archive digest mismatch: expected {EXPECTED_SHA256}, got {actual_sha256}"
    )

root_resolved = ROOT.resolve()
with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as archive:
    members = archive.getmembers()
    for member in members:
        target = (ROOT / member.name).resolve()
        if target != root_resolved and root_resolved not in target.parents:
            raise SystemExit(f"unsafe archive member: {member.name}")
        if member.islnk() or member.issym():
            raise SystemExit(f"links are not allowed: {member.name}")
    archive.extractall(ROOT, members=members)

for path in (
    ROOT / "bootstrap" / "curiosity-governance-v1.tar.gz.b64",
    ROOT / "bootstrap" / "install_curiosity_governance.py",
    ROOT / ".github" / "workflows" / "install-curiosity-governance.yml",
):
    path.unlink(missing_ok=True)

bootstrap_dir = ROOT / "bootstrap"
if bootstrap_dir.exists() and not any(bootstrap_dir.iterdir()):
    bootstrap_dir.rmdir()

print("curiosity/motive governance implementation extracted")
