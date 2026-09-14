# StegCore 001/002 Final Activation Runbook

Updated: 2026-09-14

Promotion order:
1. Install the baseline manifests, schemas, vectors, validator, activation registry, updater, and CI workflow.
2. Run the exact validation commands locally or in an equivalent isolated source checkout.
3. Require the GitHub Actions `StegVerse 001/002 Validator` workflow to pass on the exact promotion source.
4. Run the guarded updater semantics to move `activation_candidate` to `activated`.
5. Preserve the exact commit/run evidence in the mirror handoff.
6. Only then allow the StegAgents handshake promotion to evaluate its dependency.

Activation is narrow: it establishes this baseline and does not activate downstream agents, grant user access, expose raw continuity traces, authorize master-record mutation, or prove production runtime deployment.
