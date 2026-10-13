# game-dev-2d — craft-hours ledger

Append-only. One row per round: dispatched lanes, in-domain lane-minutes,
verification, evidence pointer, cumulative hours. A craft-hour is one hour
of verified in-domain lane work; collective time counts — an N-lane wave
spending T in-domain minutes logs N×T craft-minutes. Shokunin rank needs
≥10,000 verified craft-hours AND the SHONEN gate — necessary, never
sufficient. See PROTOCOL.md §Craft-hours.

| round | lanes | in-domain lane-min | verified | evidence | cumulative (h) |
|---|---|---|---|---|---|
| ledger-open | — | 0 | — | instrumentation opens 2026-10-13; pre-ledger rounds creditable only by recomputation from round reports/wave artifacts, marked `[~]` estimate or `[x]` evidenced | 0 |
