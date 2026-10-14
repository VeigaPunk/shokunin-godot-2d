# Round 61 simplifier report — minimal-design critique of the crash-row diff (host: devin)

Seat: simplifier (report-only). Lane axis: **coverage** — tracked
spontaneous-crash classification row per r60. I polled
`git -C ~/Projects/shokunin/game-dev-2d-shokunin diff` until the author's CASES
diff existed, then judged it against the production classifier. No tracked
edit, no commit, no sibling-scope write. Scratch under
`corpus/live/r61-simplifier/`; this report is my only tracked-path write.

## Poll evidence

- `git status --short` / `git diff` empty of tracked changes through
  22:03:06Z (only untracked `corpus/live/r61-*` scratch and my report dir).
- First tracked diff observed 22:04:40Z: `M corpus/fixtures/run_battery.py`
  (+42 lines, 0 deletions) plus untracked `corpus/fixtures/spontaneous_crash_probe.gd`.
  Re-polled 22:05:10Z and 22:05:40Z — stable, still additive-only.

## The diff as landed (verbatim inventory)

1. **CASES += 2 tuples** (`run_battery.py:96-97`):
   - `("crash_spontaneous_sigabrt", "spontaneous_crash_probe.gd", ["--spontaneous-crash"], -6, "SPONTANEOUS_CRASH_PROBE: expected signature")`
   - `("crash_self_sigkill", "spontaneous_crash_probe.gd", ["--spontaneous-sigkill"], -9, "SPONTANEOUS_CRASH_PROBE: expected signature")`
   → CASES count 77 → **79** (ast-verified).
2. **`expected_errors` += 1 exact-match entry** (`run_battery.py:437`):
   `"crash_spontaneous_sigabrt": ("ERROR: r60 spontaneous crash probe",)` —
   uses the pre-existing per-name allowlist dict shared by ~30 cases.
3. **Unconditional meta block** (`run_battery.py:508-546`, ~39 lines):
   `probe_spontaneous_crash_classification` re-classifies the two new rows'
   already-captured outputs under mismatched expectations — zero extra Godot
   invocations; four discriminations + row-PASS guards.
4. **New fixture** `corpus/fixtures/spontaneous_crash_probe.gd` (15 lines):
   byte-identical executable content to the r60 scratch probe measured twice
   (`diff` vs `corpus/live/r60-verifier/scratch-probe/proj/spontaneous_crash_probe.gd`
   → only the comment block changed, r60→r61 provenance note). Same MARKER,
   same `OS.crash("r60 spontaneous crash probe")`, same arms.

## Verdict: minimal expression — YES, with named deletables

### The briefed question: can the signature field already carry it?

**No — measured.** I `ast`-extracted `classify_process` verbatim from the
tracked runner (sha256 `42104d95…`, same as r59/r60) and fed it the r60
verifier's real captured outputs
(`corpus/live/r61-simplifier/signature_cannot_carry.py` →
`classify_matrix.json`):

```
False  crash exp=-6 sig=marker allowlist=none          # today's behavior
True   crash exp=-6 sig=marker allowlist=exact         # the landed row
False  crash exp=-6 sig=ERROR-line allowlist=none      # signature CANNOT carry it
False  crash exp=-6 sig=marker allowlist=prefix-comma  # comma form FAILS here
False  crash exp=-9 sig=marker allowlist=exact         # mismatch still rejects
False  crash exp=1  sig=marker allowlist=exact         # mismatch still rejects
True   sigkill exp=-9 sig=marker allowlist=none        # zero-cost second row
False  sigkill exp=-6 sig=marker allowlist=none        # mismatch still rejects
False  crash exp=-6 sig=absent-marker allowlist=exact  # spoof still rejects
```

`signature in output` passes trivially (the `ERROR:` line is in the merged
output), but `unrelated_errors` rejection is orthogonal — the CASES signature
field provably cannot express this row. The **existing** `expected_errors`
dict is the one carrier; the author added one data entry, not a new allowlist
concept. This is exactly the r60-identified zero-runner-change path.

**Correctness nuance worth recording**: the allowlist entry *must* be
exact-match. The `allowed.endswith(",")` prefix convention (used by e.g.
`save_process_missing` for a varying `pid=` tail) fails on this line — the
real line has no trailing comma, so `stripped.startswith(allowed)` is False
(measured above). The author used the correct exact form; any later
"harmonization" to the comma form silently breaks the row.

### Row shape

Literal `-6`/`-9` expected exits match house style (CASES carries bare ints);
marker reuse is honest — the fixture's own MARKER doubles as the signature.
The `-9` row needs **zero** allowlist entry (self-SIGKILL emits empty stderr;
measured True unmodified) — it is the cheapest possible second row and
expresses r60's "expected -9 arm matches True unmodified" finding as tracked
evidence. Both rows justified; nothing padded.

### Meta block — kept, not deletable

39 lines for `probe_spontaneous_crash_classification` follows the lane's
`probe_save_independent_process` convention (unconditional in-band meta row).
It operationalizes the move's own clause — "expected-mismatch rejection
untouched" — as a per-run check at zero extra process cost. I re-derived all
four discriminations plus both row verdicts against real captured output; all
six hold (see `classify_matrix.json`). Leaner encodings exist (~15 lines) but
the verbose record payload is house style. **Not deletable.**

### Fixture choice: new file vs folding into `crash_exit_probe.gd`

The strictly lighter alternative — adding `--spontaneous-crash` /
`--spontaneous-sigkill` arms to the existing `crash_exit_probe.gd` (~4 lines,
no new file) — exists and would be viable: its `--hold-open`/no-flag arms are
flag-gated, so the opt-in `--probe-crash-exit` leg is unaffected. The author
instead promoted the r60 scratch fixture byte-exact. I judge this
**admissible, not a second convention**: it preserves the r60-measured marker
and `ERROR:` strings verbatim (the allowlist entry literally cites the r60
message) and leaves `crash_exit_probe.gd`'s sha256 untouched — the lane's
hash-stability citations across r59/r60 verifications depend on that.
Marginal cost ≈ 10 lines of marker/arg-dispatch boilerplate. Not a required
deletion; noted for completeness.

### Prior behavior untouched — structural

The diff is 100% additive: `classify_process`, `run_process`, the
`--probe-crash-exit` (harness SIGTERM -15) and `--probe-timeout` legs are
byte-untouched. Expected-mismatch rejection is preserved and now *tracked*
(the meta's `-9`-expected-on-`-6` and `-6`-expected-on-`-9` arms both reject —
measured). `python3 -m py_compile` (to /tmp, not in-tree) and `ast.parse` both
clean.

### Deletion candidates named

1. **`corpus/fixtures/__pycache__/`** — stray untracked pycache inside the
   tracked fixtures dir, left by the author's scratch import.
   `git check-ignore` rc=1 (NOT ignored); zero `.pyc` files tracked. It will
   appear in `git status` and risks an accidental commit. **Remove before the
   work commit, or ignore it.** (Not mine to delete — outside my write scope.)
2. **Pre-existing dead weight, outside this diff**: three explicit empty-tuple
   `expected_errors` entries — `slider_adjust_repeat_right_focus_restore: ()`,
   `slider_adjust_repeat_right_second_focus_restore: ()`,
   `slider_adjust_repeat_right_second_focus_restore_press_after_late_reconnect: ()`
   (`run_battery.py:416/418/422`) — are semantically identical to the
   `.get(name, ())` default: 3 lines, zero behavior change if deleted. They
   arguably document "deliberately none"; at most a comment's worth of value.
3. **Avoided non-minimalism (confirmed absent, keep it that way)**: no 6th
   CASES tuple field, no new classifier, no `--probe-spontaneous-crash` opt-in
   leg — any of those would be a second convention over the one-carrier
   mechanism. Flag preemptively for the verifier's eyes.
4. **Kept deliberately**: the fixture's no-flag `quit(1)` accept arm is
   unexercised by tracked rows but preserves the r60 probe shape (~2 lines,
   honest comment) — not flagged. The `"r60 spontaneous crash probe"` message
   literal is *provenance*, not a stale name — renaming it to r61 would desync
   the allowlist entry from the measured string.

### Expected after-state

Before: 89 rows (77 CASES + 2 mutants + 10 probe/meta — r61-baseline receipt,
89/89 PASS, 0 field deltas vs r59 non-author). After: **79 CASES + 2 mutants +
11 probe/meta = 92 rows**; the two new rows classify PASS (measured on real
captured output above), meta PASS iff all four discriminations hold.

### Inherited caveats (not introduced by this diff)

- `returncode` carries the signal number, not its origin — self-SIGKILL vs
  external SIGKILL remain indistinguishable to the classifier; the meta's
  `bounded_claim` states this honestly.
- The -6 shape is `OS.crash`-specific (SIGILL→handler→SIGABRT), deterministic
  ×2 per r60 on this host; cross-host stability unprobed — same caveat r60
  recorded.

## Artifact inventory (my scope)

- `corpus/live/r61-simplifier/signature_cannot_carry.py` — verbatim-`ast`
  classifier extractor + 9-arm matrix.
- `corpus/live/r61-simplifier/classify_matrix.json` — matrix results + runner
  sha256.
- This report. No commit, no tracked-fixture mutation, no LOG/SCORECARD write.

**Bottom line**: the landed diff is the minimal expression of the declared
move — one CASES tuple + one existing-dict entry carry the -6 row (the
signature field provably cannot), one extra tuple carries the -9 row at zero
cost, and the meta block is the in-convention guard, not weight. Nothing in
the diff is dead on arrival; deletables named are the stray `__pycache__/` and
the three pre-existing empty-tuple allowlist entries.
