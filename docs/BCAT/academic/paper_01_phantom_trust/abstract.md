# Abstract — Phantom Trust

Modern automated and autonomous systems increasingly rely on long-lived,
non-human credentials to perform actions without continuous human oversight.
While existing security models emphasize authentication and authorization,
they largely assume that credential validity implies ongoing legitimacy.

This paper introduces **phantom trust**, a failure condition in which credentials
and actors remain technically valid and policy-authorized, yet are no longer
semantically legitimate in operational context. Unlike traditional security incidents,
phantom trust does not require credential compromise, misconfiguration, or policy
violation, and therefore often evades detection.

We present **trust continuity** as a first-class system property, distinct from identity
and permission, and show how breaks in continuity can silently undermine system
legitimacy. We develop a taxonomy of phantom trust states observed in automated
systems, including orphaned automation, context-drifted authority, and temporal
desynchronization.

Finally, we discuss detection signals based on continuity breaks, context mismatch,
and operational anomalies, and argue that autonomous and AI-mediated systems
require boundary-conditioned trust models to remain governable, explainable,
and accountable at scale.
