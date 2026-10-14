# Round 65 adjudication — forged-REJECTION dual (Sol)

Work commit `414eb8e`. Seat set: author, baseline, scout, critic, reviewer,
simplifier, scribe, boundary (8/8) + named non-author verifier
(`r65-verifier.md` — **AGREE 6/6**, committed-state replay 87/87, all 29
discriminations True, 97 prior rows 0-mismatch, independent `/proc`
kernel-ppid corroboration on its own hold probe).

## Own evidence

My own battery run on the committed tree (`runs/20261014T043651187600Z`):
87/87 PASS, `probe_descendant_error_spoof` meta PASS with 29/29
discriminations including the integration-added `hold_timeout_alone_rejects`
(strip only ERROR: lines from the hold record → still rejects on the
timeout axis alone — double-axis rejection proven).

## Verdict per claim

1. **Post-death descendant ERROR: flips a genuine-looking record to
   rejected** — CONFIRMED: release arm exit-0/signature-present/no-timeout
   record FAILs only on the forged line; counterfactual strip restores PASS.
2. **Classification-visible fields identical forged-vs-genuine** — CONFIRMED:
   `cases_visible` dicts equal; output lines differ only in provenance-only
   lines; quiet arm removes even those.
3. **Kernel-attributable provenance where fixture-asserted** — CONFIRMED:
   `write_ppid == kernel /proc ppid != godot_pid` on the live hold
   descendant; verifier double-corroborated on its own probe.
4. **While-live signature gate accepts the forged-error arm** — CONFIRMED:
   gate predicate is signature-scoped; forged error captured post-death but
   verdict-invisible; mirror-image divergence of r64.
5. **Prior rows stable** — CONFIRMED: verifier's 7-field tuple diffs vs
   baseline and author receipts: 0 mismatches; only added row = meta.

## Absorbed corrections (measured by seats, applied at integration)

- Simplifier missing-add `hold_timeout_alone_rejects` landed (29th
  discrimination); runner kept as a 121-line fork — third-variant trigger
  recorded for consolidation, not this round.
- Critic CE-1: claim scope is capture-before-pipe-EOF, not death ordering
  (detach arm emits the marker post-orphan with no flip). Lesson carries it.
- Critic CE-2: merged concat is not line-faithful — splice-fabricated
  reject lines and escape splits documented as bounded UNKNOWNs on
  `error_lines` faithfulness.

## Verdict: ADMIT

The forged-acceptance axis now has its measured reject-axis dual: the same
pipe-inheritance mechanism manufactures a FAIL as easily as a PASS, and
the signature-scoped while-live gate is verdict-blind to it. Bounded to
Godot 4.7.2 headless, Python 3.14.7, Linux POSIX semantics, this host's
subreaper/timing margins; live-window error forgery remains the open blind
side by construction.
