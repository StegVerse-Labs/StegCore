"""The vendored SDK structural validator must stay a byte-for-byte pinned copy."""
import hashlib
import json
import pathlib
import unittest

VENDOR = pathlib.Path(__file__).resolve().parents[1] / "src" / "stegcore" / "_vendor"
MODULE = VENDOR / "structural_validator.py"
PROVENANCE = VENDOR / "structural_validator.provenance.json"
PINNED_BLOB_SHA1 = "2622031c0317afc7a41b1f95e6570d5e8bf62d5c"


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


class VendoredStructuralValidatorTest(unittest.TestCase):
    def test_blob_hash_matches_pin(self):
        self.assertEqual(git_blob_sha1(MODULE.read_bytes()), PINNED_BLOB_SHA1)

    def test_provenance_matches_pin(self):
        provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        data = MODULE.read_bytes()
        self.assertEqual(provenance["git_blob_sha1"], PINNED_BLOB_SHA1)
        self.assertEqual(provenance["sha256"], hashlib.sha256(data).hexdigest())
        self.assertEqual(provenance["contract_version"], "1.6")

    def test_contract_version_and_stdlib_only(self):
        from stegcore._vendor import structural_validator as sv

        self.assertEqual(sv.CONTRACT["contract_version"], "1.6")
        imports = [line for line in MODULE.read_text(encoding="utf-8").splitlines()
                   if line.startswith(("import ", "from "))]
        self.assertEqual(imports, ["import calendar", "import hashlib", "import json", "import re"])


if __name__ == "__main__":
    unittest.main()
