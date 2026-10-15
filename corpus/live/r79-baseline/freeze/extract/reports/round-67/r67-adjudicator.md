# R67 adjudicator (Sol) — classify_streams ↔ merged per-channel divergence map

Round: 67. Wave: `shokunin-train-20261014-w7`. Work commits: `d44ba86`
("r67: classify_streams per-channel divergence map — 7 probe arms +
dual-classify meta, 20 discriminations") + `9e946c9` (simplifier-derived
`sd_sig_head` load-bearing seam-tail pin).

## Declared move (depth/coverage)

Pin `classify_streams`' per-channel divergence from merged
`classify_process` as a measured axis — opt-in probe only, no default-path
change; stdout-carried `ERROR:` absorbed PASS-shaped where merged rejects;
per-stream records + divergent-verdict pins; prior rows byte-stable.

## Seat convergence

| seat | landing | contribution |
|---|---|---|
| author | yes | `run_battery.py` +~265: `streamdiv_*` meta inside `--probe-stream-attribution` (7 real-Godot arms + 6 allowlist reclasses + pair dual, 20 discriminations, 9-row `divergence_table`); `stream_attribution_probe.gd` +58 per-channel byte placement (`--{stdout,stderr}-error`, `--stderr-structured`, `--sig-on-stderr`, `--seam-{error,script,sig}`). Flagged 89/89, meta PASS |
| scout | yes | claim confirmed; AST-level corroboration of both classifier segments (byte-identical worktree↔HEAD); re-pinned the latent stderr-only strictness |
| critic | yes | wording falsification absorbed: "exactly the stream-attribution axis" → 12/27 arms divergent via ≥4 distinct mechanisms (absorb / strict×4 / seam×allowlist); enumeration replaces "exactly"; e2e receipts converge |
| boundary | yes | seam positionality proven: only stdout-tail→stderr-head fabricates (reverse order unfabricatable — stderr always lands after all stdout); splitlines table identical per path; drain-order insensitive |
| simplifier | yes | minimal bar met; flagged `sd_sig_head` dead binding → integration made it load-bearing (`raw_stdout.endswith(sd_sig_head)` conjunct, `9e946c9`) rather than deleting |
| reviewer | yes | committed-state audit clean |
| scribe | yes | 54 real-pipe records (own extraction driver, sha-convergent, rep-stable); verified author 9-row table row-for-row post-land; lesson+LOG drafts adopted |
| baseline | yes | frozen replay 88/88 + surface 34/34, 0 drift; archive 622MiB (hygiene fix holds) |
| verifier | yes | **AGREE 5/5** on `9e946c9` — flagless 88/88, flagged 89/89, surface 34/34, stream-attribution discriminations 20/20, all 9 divergence rows match author receipts; `endswith` pin confirmed true on real bytes |

## Measured headline (converged across ≥3 seats each)

- **12/27 arms divergent**, rep-stable, four families:
  - ABSORB (streams=T/merged=F): stdout `ERROR:` invisible to streams
    (stdout examined only for signature + 2 blob tokens).
  - STRICT (merged=T/streams=F): every non-empty stderr line must match
    `allowed_stderr` (non-`ERROR:` chatter rejects); signature
    channel-pinned to stdout (stderr-only sig fails; exempting it can't
    redirect the pin); seam-fabricated signature; allowlist+noise; in-
    stderr `ERR\nOR:` evasion; merged-only structured entry.
  - SEAM×ALLOWLIST (merged=F/streams=T): exempted stderr fragment
    completes a phantom `ERROR:`/`SCRIPT ERROR:` line existing only in
    the concat (2 arms).
  - AGREE: stderr `ERROR:` both-reject; allowlisted stderr both-absorb;
    blob tokens both-reject; exit/error short-circuit first.
- **The shipped reject arm itself diverges** (`g_stream_reject`:
  T/F) — `STREAM_STDERR:` diagnostic has no `ERROR:` token; divergence
  was production behavior since r19, un-named until now.
- Seam is **one-position**: stdout-tail|stderr-head only (boundary).

## Adjudicator own reproduction (committed tree)

- Flagless full-battery replay: 88/88 PASS incl. surface meta 34/34.
- Flagged `--probe-stream-attribution` replay: 89/89 PASS, all
  discriminations true, `divergence_table` 9/9 rows match.

## Corrections absorbed this round

- "exactly the stream-attribution axis" → falsified as written; the
  corrected claim is the enumerated four-family map (12/27 divergent).
- `sd_sig_head` dead → kept and pinned (seam tail asserted on real
  stdout bytes), not deleted.

## Bounds

Classifier-level verdicts only; Godot 4.7.2 headless; CPython POSIX
pipes on this host; `classify_streams` divergent behavior is latent for
the default battery (sole call site = opt-in probe). Real captured pipe
bytes throughout — no synthetic strings.

## Verdict — **ADMIT**

- depth: **improved locally** — the per-channel asymmetry is now a
  measured, enumerated map (absorb/strict/seam×allowlist/agree) with
  clause-level mechanism per family; a latent production divergence on a
  shipped arm is pinned.
- coverage: **improved locally** — 20 discriminations, 9-row divergence
  table, seam-position bound, channel-pinned signature rule.
- calibration: **unchanged** — opt-in flag; default path byte-stable;
  classifiers untouched (proven byte-identical across three seats).

Work commits `d44ba86` + `9e946c9`; report-last commit follows.
