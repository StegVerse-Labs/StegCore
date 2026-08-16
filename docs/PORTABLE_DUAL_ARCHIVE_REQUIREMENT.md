# Portable Dual-Archive Requirement

All StegVerse portable SDK package releases, including StegVerse S Ecosystem, StegVerse NS Ecosystem, and future StegOS packages, must provide both `.zip` and `.tar.gz` archive forms from the same declared payload.

Each format must have its own SHA-256 and immutable locator in the governed SDK catalog. The package receipt inside each archive must describe the same source commit, deployment class, payload file manifest, authority boundaries, and Node Sovereign non-self-accreditation posture.

```text
same canonical source + same payload
-> deterministic .zip
-> deterministic .tar.gz
-> independent archive SHA-256 values
-> governed catalog binding
-> SDK user selects preferred format
```

The archive format is a transport/tooling choice and carries no governance authority.

For StegOS, boot/install image formats may additionally be published, but they remain separate governed artifacts and do not erase the `.zip` + `.tar.gz` SDK distribution pair.
