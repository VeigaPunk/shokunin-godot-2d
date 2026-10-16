# r93-scribe receipts — wave-B gate on committed `4b75151` (AnimationPlayer + Tween lattice)

Seat `SCRIBE` (LEAF, frozen `probeParent`) | lane `g2d-r93-scribe` | round 93 | host
**devin** (32 cores, loadavg 74–87, 60 foreign `yes` hogs owned by another lane).

**Zero tracked writes.** `git status --porcelain -uno` empty at audit start, at every
re-check, and at audit end. Only files created: this lane's receipts (untracked) and the
untracked report `reports/round-93/r93-scribe.md`. No commit, no push, no runtime config.

## Run inventory

| artefact | path | what it is |
|---|---|---|
| battery run 1 (worktree = committed bytes) | `battery-runs/20261016T010005212465Z/verdicts.json` | 295 rows, FAIL 293/295 (`transition` exit=1, `audio_playback` exit=2 — pre-existing volatile classes); r93 23/23; `r93_expected_errors_all_matched=true`; `dead_entry_count=0`; `rows_with_expected_errors=68`; log `battery-rep1.log` |
| battery run 2 (`git archive HEAD` extract at `/home/vgpnk/r93-committed-extract`) | `battery-committed/20261016T010554750817Z/verdicts.json` | 295 rows, FAIL 294/295 (`overlap` exit=1 — same volatile class); r93 23/23; gate true; dead 0; log `battery-rep2.log` |
| fresh single-arm receipts (17 arms × 3 reps) | `fresh/<fixture>.<arm>.rep<N>.{out,err,rc}` | battery launch shape (`godot --headless --path <proj> --script res://<fixture>.gd -- --arm=<a>`), isolated `XDG_DATA_HOME` (`fresh/xdg-data/`), 25 s `timeout -s KILL`; **51/51 rc=0, 51/51 stderr 0 B** |
| fresh-arm driver | `fresh_arms.sh` | replay script; project at `/home/vgpnk/r93-fresh-proj` (byte-copies of committed fixtures) |
| static custody + fold audit | `audit/static_audit.py` → `static_audit.json` / `.out` | committed-tree identity, insertion-only diff (239 files, 0 deletions), CASES=288 / r93 rows 261–283 contiguous, allowlists (0 r93 keys), gate presence, manifest verification (scout 304/304, boundary 1049/1049, author 1086/1086, all completeness-exact) |
| receipt census + law re-derivation | `audit/receipts_census.py` → `receipts_census.json` / `.out` | 387 committed r93 receipts; binding 23/23 all-hit; single `phys_delta`→`clock` collision; overshoot / N−1 / crossfade / DEFERRED clauses constant |
| dossier recompute + mutant test | `audit/recompute.py` → `recompute.json` / `.out` | production `classify_process` (segment sha `749fa0607e7707e6…`); 110 mutants (57 value / 7 bool / 46 conjuncts), **110 rejected, 0 accepted** |
| cross-run comparison | `audit/compare_runs.py` → `compare_runs.json` | 263 identical / 16 tail-only / 13 pin-head-diff (signature still verbatim in all) / 3 verdict flips (volatile classes); emitted signature field identical for all 295 rows |
| lane manifest | `manifest.sha256` | 737 entries; every file under this directory except itself and this index |

## Labrat (frozen `probeParent`, exactly one dispatch)

Agent `11415ff9`, read-only, three clauses: (1) every own-arm canonical receipt carries its
pin verbatim — PASS, only misses are intentional critic mutants + `defect/noscript`;
(2) collision census — PASS, sole collision `phys_delta=0.01666666666667` in 30/30 `clock`
receipts (`clock` is not a CASES row); (3) crossfade `w_i=(i−1)/(N−1)` — PASS,
max dev 2.3736e-05 / 3.3730e-05 / 0.0 for N=10/20/5, `interleaved_eq_plain=true` 37/37.

## Headline verdict

**Custody HOLDS** — 4/4 declared law families encoded and load-bearing; both committed-byte
runs green on the r93 surface; floor gate vacuously true and correctly scoped. Findings
A1–A9 in `reports/round-93/r93-scribe.md` §8; none falsifies a landed pin, allowlist entry,
gate key, or verdict.
