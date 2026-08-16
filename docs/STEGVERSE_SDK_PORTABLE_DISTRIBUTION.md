# StegVerse SDK Portable Distribution

## Purpose

The first public/community distribution channel for portable StegVerse ecosystems is the SDK/console rather than an app-store or paid-product launch.

This creates an intentional adoption path for:

- ordinary users willing to test portable sovereign deployments;
- developers integrating StegGate/AdmittedCode;
- beta testers;
- researchers;
- Node Sovereign operators;
- future ecosystem service providers.

## Initial channel

```text
channel: SDK_EARLY_ACCESS
console_download_supported: true
console_install_supported: true
app_product: false
paid_product: false
```

The duration of SDK early access is a governed product-lifecycle decision and is not hardcoded into the package.

## User choice

Every portable implementation request must choose:

```text
S  -> StegVerse S Ecosystem / Sovereign
NS -> StegVerse NS Ecosystem / Node Sovereign profile
```

There is no implicit default.

An NS package installs the Node Sovereign profile and activation contract but does not grant ecosystem membership.

## Package requirements

Each distributable archive must:

1. include the canonical micro-ecosystem manifest;
2. include the Node Sovereign definition/profile so S/NS semantics travel with the package;
3. include the canonical runtime source needed by the portable unit;
4. include an inspectable package receipt;
5. hash every packaged file;
6. identify the deployment class;
7. identify the source commit when available;
8. require no provider account;
9. contain no non-TV/TVC secret material;
10. avoid claiming Node Sovereign membership merely because NS was installed.

## Deterministic builder

```bash
python tools/build_portable_ecosystem_package.py \
  --deployment-class S \
  --output-dir dist/sdk

python tools/build_portable_ecosystem_package.py \
  --deployment-class NS \
  --output-dir dist/sdk
```

The generated ZIP is byte-deterministic for identical source contents and contains `PACKAGE_RECEIPT.json`.

## Console contract

A future SDK console needs only a thin distribution surface over the package catalog:

```text
list portable packages
-> user selects S or NS
-> show deployment semantics and authority boundary
-> build/select exact version
-> verify package receipt/hash
-> download OR governed install
-> run local proof
-> for NS: begin separate membership activation process
```

The console must never collapse installation and activation.

## Product lifecycle

The intended progression is:

```text
SDK_EARLY_ACCESS
-> SDK_COMMUNITY
-> APP_PRODUCT_CANDIDATE
-> PAID_PRODUCT_CANDIDATE
```

Promotion depends on real usage evidence, package reliability, recovery, security, governance conformance, community feedback, and support economics.

SDK availability is therefore not merely a development convenience. It is the initial community-development and ecosystem-discovery channel.

## Economic relationship

SDK early adopters may later be eligible for verified contribution accounting through StegFin when they perform useful, authorized, receipt-bearing work such as testing, verification, relay, storage, compute, preservation, documentation, translation, or other governed services.

Installation, enrollment, passive holding, traffic generation, or self-created node identities do not by themselves constitute rewardable contribution.
