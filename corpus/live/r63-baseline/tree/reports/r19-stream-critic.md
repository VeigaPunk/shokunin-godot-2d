# r19 stream-critic leaf

role: critic (read-only except this report)  
axis: calibration (attack stream-attribution pair)  
branch: craft/game-dev-2d-r1 @ fa31bef (uncommitted runner+fixture)  
executor report: `.shokunin/game-dev-2d/reports/r19-stream-executor.md`  
verdict artifact reviewed: `.shokunin/game-dev-2d/corpus/live/runs/20261012T231855322812Z/stream-attribution-verdicts.json`  
parent re-run note: meta PASS; n=34 battery PASS; `FAIL stream_reject` is expected inner print

## Scope respected

- Did not edit runner, fixture, MANIFEST, sibling books, seeded fixtures, or classify_process.
- Only wrote this leaf report.

## Attack answers

### 1) Could a concatenated stdout+stderr check still pass accept and fail to prove attribution?

**Yes — concat fails to prove attribution on the reject half.**

Replayed landed streams through ordinary `classify_process` (concat semantics: signature anywhere, reject only on `ERROR:` / SCRIPT / Parse):

| case | concat `classify_process` |
|------|---------------------------|
| stream_accept | **True** |
| stream_reject | **True** (false admit) |

Reject stderr is exactly `STREAM_STDERR: unrelated attribution diagnostic` with **no** `ERROR:` substring. Concatenated classification therefore treats reject like accept. The pair only separates the cases because probe path uses `run_process_streams` + `classify_streams`, which requires the signature on **stdout** and rejects unallowed `STREAM_STDERR:` / `ERROR:` lines on **stderr**. Ordinary `run_process` still does `proc.stdout + proc.stderr` (unchanged) — r11 lesson remains true for default battery classification.

### 2) Does reject fail for a reason other than stderr attribution?

**No for the landed pair.** Both exits are 0; both carry the stdout signature; neither timed out (`error` null). Accept `inner_classification=True`, reject `False`. Difference is reject stderr line `STREAM_STDERR: unrelated attribution diagnostic` with `allowed_stderr=()`. Exit codes identical → rejection is stream content, not exit-code or missing-signature or timeout.

### 3) Does the new flag change default battery behavior when omitted?

**No.** `--probe-stream-attribution` is `action="store_true"` (default off). Probe block is gated on `if args.probe_stream_attribution`. Ordinary CASES list and existing probe flags untouched per executor + git status (`M run_battery.py`, `?? stream_attribution_probe.gd` only under fixtures).

### 4) Does classify_process or any seeded fixture hash change?

- `classify_process` body still present and still concat-fed via `run_process`; new logic is additive `classify_streams` + probe-local `run_process_streams`.
- Seeded fixtures: no modifications in git status (only new untracked probe + modified runner).
- Critic did not re-hash every seeded file; status is sufficient that no seeded fixture path is dirty.

### 5) Would Godot engine banner or push_error backtrace make accept spuriously fail?

- **Banner:** Landed accept stdout includes `Godot Engine v4.7.2...` then the marker; stderr empty. `classify_streams` only requires `signature in stdout` and scans stderr for `ERROR:` / `STREAM_STDERR:`. Banner on stdout does **not** fail accept (observed PASS).
- **push_error backtrace:** **Not exercised** by this fixture (print / optional printerr only). No claim that accept survives engine `ERROR:` noise or stack lines on stderr. If accept ever emitted unallowed `ERROR:` on stderr, `classify_streams` would fail accept — good for calibration, but unprobed here.

### 6) False-admit paths

**This pair's meta verdict is not a false admit** under the contract markers:
- accept classifies true with marker on stdout only, stderr empty
- reject classifies false with same exit, same stdout marker, stderr diagnostic present
- same `res://stream_attribution_probe.gd`
- meta checks exact line membership on claimed streams

**Residual false-admit / under-reject in `classify_streams` (narrow hole, not this pair's markers):**

```text
run_battery.py  classify_streams  — loop over stderr_lines:
  only returns False for stripped lines that startswith "ERROR:" (unallowed)
  or startswith "STREAM_STDERR:" (unallowed).
  All other non-empty stderr (plain printerr text, push_warning text without ERROR:,
  engine chatter without those prefixes) is **ignored** → would still return True.
```

So a reject variant that `printerr("unrelated")` **without** the `STREAM_STDERR:` / `ERROR:` prefix would **inner-classify True** (false admit of the reject case). The landed fixture deliberately uses `STREAM_STDERR:` so meta PASS is real for this pair only.

**Ordinary battery false-admit (pre-existing, still live):** concat + `classify_process` would admit the landed reject streams as True (see §1). Probe does not fix default classification.

**Console `FAIL stream_reject`:** expected inner print when classification is False; parent confirms not a battery failure. Not a defect.

## Verdict on the pair

**SOUND** — narrow but sound for one Godot 4.7.2 headless stream-attribution pair with the contracted markers and separate-stream classifier.

## Parent follow-up (not authored by this critic)

After this report, the parent closed the residual hole named above: `classify_streams` now rejects any non-empty stderr line that is not in `allowed_stderr`, not only `ERROR:` and `STREAM_STDERR:` prefixes. Parent re-ran `--probe-stream-attribution` after that edit: meta PASS, accept inner True, reject inner False, both exit 0. Artifact: `.shokunin/game-dev-2d/corpus/live/runs/20261012T232054666461Z/stream-attribution-verdicts.json`. The critic did not author that edit.

### Remaining unprobed diagnostics (do not overclaim)

- crash classification
- process-tree timeout
- export reliability / rendered output
- `push_error` / engine `ERROR:` backtrace on accept
- `push_warning` stream placement
- plain `printerr` without `STREAM_STDERR:` / `ERROR:` prefix (classify_streams hole above)
- default `run_process` concatenation still used by ordinary 33 cases (attribution still unproved there)

### Bounded claim (unchanged)

One Godot 4.7.2 headless stream-attribution pair. Not crash, not process-tree timeout, not export reliability, not rendered output.
