# Position in the StegVerse LLM Communications Stack

Stack identifier: `STEGVERSE-LLM-COMMS-STACK-v1`

`StegCore` is the commit-time decision engine used by the distributed StegVerse LLM Communications Stack and other consequence-bearing StegVerse transitions.

## This repository owns

- allow, deny, or defer decisions for proposed actions;
- policy-shape evaluation;
- consent, quorum, veto, time-lock, escalation, and constraint interpretation;
- commit-time checks using verified continuity and standing inputs;
- machine-readable decision reasons.

## This repository consumes

- verified continuity and standing evidence;
- structured action intents and transition candidates;
- policy, delegation, consent, and context inputs;
- bounded operational state and audit signals.

## This repository produces

- proceed, pause, deny, allow, deny, or defer decisions as defined by the applicable contract;
- constraints and machine-readable reason codes;
- decision evidence for downstream execution, refusal, return, custody, and reconstruction.

## This repository does not own

- model inference;
- provider-neutral LLM brokerage;
- communication-source normalization;
- receipt minting or verification;
- identity storage;
- continuity truth;
- Master Record custody;
- execution merely because an action is allowed.

## Related stack components

- `StegVerse-org/LLM-adapter` — common governed LLM broker and transition adapter;
- `StegVerse-Labs/governed-llm` — StegVerse-controlled local inference provider;
- `StegVerse-Labs/hybrid-collab-bridge` — internal collaboration adapter;
- `StegVerse-Labs/Comms-Gateway` — communication-event normalization and routing;
- `GCAT-BCAT-Engine/workflows` — deterministic validation and orchestration.

Model output, communication, continuity evidence, validation, and an allow decision remain separate architectural facts. None should be collapsed into another.
