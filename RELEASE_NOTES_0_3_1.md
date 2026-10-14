# StegCore 0.3.1 release notes (proposed successor release candidate)

Release authority: TV/TVC. This file and `RELEASE_BINDING.json` are the only changes in the release commit.

- Source parent: `244375d2b8d22ecffbae54339789d609f8571296`
- Built on the frozen 0.3.0 release commit `58445bb14642c1889cf9802666c15bd48c6d2e39`; runtime semantics unchanged
  (runtime identity `stegverse:steggate:canonical:three-layer:v1`).
- Public distribution: `stegverse-stegcore==0.3.1`; import namespace `stegcore`.
- Adds the release-triggered Trusted Publishing workflow the frozen commit lacked, fixes stale 0.2.0 test/metadata
  expectations, removes GitHub-token tag creation, and adds a guard against reintroducing it.

Candidate only: no tag, GitHub Release, PyPI publication, grant or custody is created by this commit.
