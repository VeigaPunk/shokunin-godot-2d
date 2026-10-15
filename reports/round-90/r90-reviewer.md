# r90 reviewer — independent verification of the r90 diff (commit `ee20575`)

Seat `REVIEWER` (g2d lane r90) | host **devin** | Godot `4.7.2.stable.arch_linux.ed1daf0bf`
(`/usr/bin/godot`, `--headless`, 60 tps, GodotPhysics2D), Python 3.14.7.
Reviewed commit `ee20575` (HEAD at review time; parent `a08a190`). Diff scope:
`corpus/fixtures/{rb_lattice.gd,rb_watch.gd}` (+707/+9), `corpus/fixtures/run_battery.py`
(+74/−0, 3 pure-insertion hunks), `reports/round-90/r90-author.md` (+214). **No tracked
file was modified by this seat; no commits.** (Concurrent-worktree note: at review start
`git status` showed no modified tracked file; during the review — 19:16–19:17Z — an
in-flight sibling r89-fold seat edited `corpus/fixtures/{run_battery.py,geo2d_lattice.gd}`
in the same worktree. That is not this seat's work, not part of `ee20575`, and I left it
untouched. Every check below reads the **committed** bytes via `git show ee20575:…`, and my
launch project was extracted from the commit, so none of the review is affected.) Seat-owned
untracked scratch/receipts:
`corpus/live/r90-reviewer/**` (57 fresh Godot launches + run driver + classifier harness,
`manifest.sha256` 174/174 OK) and this report.

**`lsp` disclosure.** No `lsp` device and no GDScript/Python language server is exposed to
this seat (MCP servers visible here: `rea` only). Every check below is a textual/AST read of
the committed sources plus fresh-process execution receipts — the literal fallback, recorded
so it is never presented as semantic proof. The diff contains no renames (fixture landing +
literal `CASES`/allowlist/gate inserts), so no symbol-aware operation was possible or required.

**probeParent disclosure.** Exactly one read-only `ufo-labrat` was dispatched (bounded
hypothesis H1: envelope-free pins are load-proof under 8-way concurrency). It returned
**without executing** — its environment exposed only read-only filesystem tools, no shell —
so it contributed a static audit of this seat's own `.par` receipts (12/12 PASS lines equal
to the pins by text comparison) and **no new empirical evidence**; it was not re-dispatched.
All empirical evidence below is this seat's own fresh execution.

**Verdict: PASS on the landed bytes.** All five assigned axes — row shape correctness,
tuple-envelope semantics vs classifier, `expected_errors` exactness (byte-compared against
engine output), floor-gate coverage, pin arithmetic — verify clean, plus the three boundary
folds the dispatch names (tps-qualified pins, `eng=` Dummy precondition, typed refusal
ladder). Findings F1–F6 are evidence-integrity / report-precision / by-design items; none
changes a pinned byte or a verdict.

---

## 1. What was verified clean

**V1 — additive, scoped diff; prior rows untouched.**
`git show --numstat ee20575`: `rb_lattice.gd` +707, `rb_watch.gd` +9, `run_battery.py`
**+74/−0**, report +214; `--diff-filter=D` empty, no modified tracked file inside the commit
(the two worktree-only sibling edits noted in the header are not in it). The `run_battery.py`
diff is exactly
**3 hunks, all pure insertions**: CASES block (file lines 474–531), the two
`expected_errors` entries (952), the one discrimination key (2583). AST row-diff of `CASES`
parent `a08a190` → commit: 228 → 240 entries, **pure insertion of 12 rows at index 224**;
the 4-row tail (`crash_spontaneous_sigabrt`, `crash_self_sigkill`,
`descendant_pipe_detached_control`, `descendant_pipe_forged_signature_release`) keeps its
order, so the detached-control row stays adjacent to the meta probes (guarded `sleep 8` gap
intact). Fixture shas match the report and the commit: `rb_lattice.gd`
`10da2291295c55dd7074cb226f6c7caf74530d3925885c9d6f7064285f5a951c`, `rb_watch.gd`
`e349faa0715421d727165717a8fe9333f4536faee8e6c28da84e694cb94272de` (sha-equal to
`corpus/live/r90-scout/proj/rb_watch.gd` — the verbatim forwarder), `project.godot`
`8de8b3af…` unchanged. `rb_lattice.gd` vs the scout probe (`4f201e85…`, 287 diff lines):
header/fold comments, `PASS r90_lattice` prefix, `_eng/_guard/_dh/_pair`, per-arm pairing
fields, the new `impedge` arm — **experiment bodies unchanged** (fold is additive).

**V2 — row shape correctness.** All 240 CASES entries are 5-tuples; case names unique. The
12 new rows: script `rb_lattice.gd`, a single `--arm=<arm>` flag whose token matches the row
name suffix, rc `0`, plain-string signature (no tuple), and a full PASS-line pin whose
`PASS r90_lattice <arm>` token matches. The 12 probe arms are covered exactly once, and the
probe's `match` covers exactly those 12 (the `_arm_fallback` path is unreachable from
CASES — every row prints its own arm name). `freezelock` carries `--frames=120` and `lag`
`--frames=30`; no other row passes `--frames`. Every arm calls `_guard()` first, so `eng=`
and `tps=` lead every PASS line. The committed rows are byte-identical to the generator
block `corpus/live/r90-author/author-rows.py.txt` (12/12, parsed and compared).

**V3 — fresh independent execution (this seat).** `corpus/live/r90-reviewer/run_arms.sh`
(same launch shape: `timeout -s KILL 25 godot --headless --path proj --script
res://rb_lattice.gd -- --arm=<a> [--frames=N]`), 12 arms × 3 reps sequential + 12 arms × 1
rep 8-way concurrent, under host load ~70: **48/48 classify PASS** with the production
classifier AST-extracted from the committed harness (segment sha
`749fa0607e7707e614c1ab157a6f8e756dfc2f460746e6d218e6734ad8fa72c3` — the same segment sha
r89 recorded). Every emitted PASS line is **byte-equal to the committed pin as a whole line**
(not merely substring-present), `out_uniq=1`/`err_uniq=1` per row, rc=0, and stderr
byte-identical to the author's receipts. The author's own 12×6 fresh receipts re-classified
with the same classifier: **72/72 PASS, out_uniq=err_uniq=1** (report claim verified).

**V4 — tuple-envelope semantics vs classifier.** None of the 12 rows is an envelope — all
signatures are single strings, so no r90 row reaches the `any(classifier(…) for sig in
evidence)` path; the two entry-carrying rows (`comrefuse`, `impedge`) are single-string rows
too, so no r90 row can route a tuple into `classify_process` (the r89 F6 latent hazard is not
touched by this landing). Envelope-free is *justified*, not merely unexercised: the folded
surface was byte-stable over 6 author arm reps, 14 battery reps, 3 sequential + 1
8-way-concurrent rep of mine — **no second mode observed**. The classifier's tuple path is
unchanged from r89.

**V5 — `expected_errors` exactness (byte-compare vs engine output).** Fresh and committed
receipts agree exactly: `r90_lattice_comrefuse` emits **exactly 1** ERROR line, byte-equal
(after strip) to `ERROR: Condition "center_of_mass_mode != CENTER_OF_MASS_MODE_CUSTOM" is
true.`; `r90_lattice_impedge` emits **exactly 3** — `ERROR: Condition "p_inertia < 0" is
true.` ×1 and `ERROR: Condition "p_mass <= 0" is true.` ×2 (the `mass0` + `massneg` lanes) —
one exact entry covers both mass lines. The accompanying `at:` lines
(`set_center_of_mass …rigid_body_2d.cpp:376`, `set_inertia …:334`, `set_mass …:324`) carry
no `ERROR:` token and are correctly outside the whitelist. Both rows are load-bearing:
`bare_rejects=True` / `allowlisted_passes=True` (re-derived from my fresh receipts, and in
the committed census).

**V6 — floor-gate coverage.** `r90_expected_errors_all_matched` (run_battery.py:2583–2591)
covers `case.startswith("r90_")`; both entry-bearing rows are inside the prefix and the ten
entry-less siblings are inert-but-covered — the same named-by-round / covers-round-prefixes
shape as the r87/r88/r89 gates. It is not a dead key: it participates in
`sf_meta_ok = all(sf_discriminations.values())` (39 discriminations, all true in the green
runs → meta row PASS). Green-run census: gate `true`, `dead_entry_count=0`,
`rows_with_expected_errors` **55→57** (+2), `comrefuse matched_lines=1`, `impedge`
`p_inertia<0` ×1 + `p_mass<=0` ×2, both `bare_classification_rejects=true` /
`allowlisted_classification_passes=true`. Discrimination demonstrated in-memory on the
committed census data: marking the impedge entries dead flips the gate to `False`.

**V7 — pin arithmetic (every pinned value recomputed).** A float32 recurrence
`v ← v·(1−d·dt) + g·dt`, `y ← y + v·dt` (`d` = effective linear damp, `dt` = 1/60) reproduces
**every pinned 4-dp value exactly**: gravity `g0/g05/g1/g2/gm1/zv/zv0/cf` at f30 and f60
(e.g. `g1 f60 = 482.2250, 933.3325`; `zv` damped `−14.6187/−28.5357`; `zv0 = −30·n·dt`);
damp `default/rep0/rep05/comb05` at f30/f60 and the `tld=0.1/0.0/0.5/0.6` oracle;
order `cb0..cb4/cblast/f1..f60` (e.g. `cb1 ty=0.8162 vy=32.6394`); write
`wzero/whold/wman` (`wman = g·dt²·n(n−1)/2` → `118.4167` at n=30, `481.8333` at n=60);
lag `dy = n·g·dt² = 8.1667`, `gdt=16.3333`, `gdt2=0.272222`, `exp=N=30`,
`apre/bpre/bpost = 490.0001/473.6668/490.0001`. Impulse closed forms: circle r=8 m=1 →
`iI=0.031250`, `ω=480·iI=15.0000`, central `Δv=−60`; off-centre `cross((8,0),(0,−60))·iI
= −15`; rect 20×10 → `I=(400+100)/12=41.6667`, `iI=0.024000`, `ω=11.5200`; impedge all four
lanes `ω=15.0000` with AUTO `iI=0.031250` (refusals leave physics untouched). Freezelock
`f_lock y=−128.0000 = −100 − 28·(60·dt)` (impulse lands at the `f==1` await → 28
post-impulse integrations), `f_static/f_kin` frozen at spawn; contacts rest
`−7.7000 = −8 (r=8) + 0.3` solver penetration. TPS qualification holds both ways: pins
carry `tps=60`, and a real 30-tps boot prints `tps=30` and fails classification (V8).

**V8 — engine precondition and tps qualification (the boundary folds).** Dummy boot
(`physics/2d/physics_engine="Dummy"`): `eng=PhysicsServer2DDummy` is emitted; `gravity`
reproduces the boundary's silent-vacuity shape (all bodies frozen at spawn, `ncb=0`,
`cb0_rel=−1`, `pf_delta=60`, `tick_dh=1:59`, 0 B stderr) and my receipt is **byte-identical
to the author's `dummy_gravity.out`**; `props`/`gravity`/`comrefuse` all **fail**
classification (pin absent). Real 30-tps project boot
(`physics/common/physics_ticks_per_second=30`, the boundary's route): `tps=30`,
`gravity f30 g05=245.1961` (pin 62.2838), `lag exp_dy=32.6667` (pin 8.1667), `freezelock
f_lock=−156.0000` (pin −128.0000) → every tested arm **fails** classification. No
30-tps-only value (`late_body` pairing, `n=29`) is pinned anywhere. (See F2 for the
author's own 30-tps receipt, which does not actually exercise this.)

**V9 — prior-row identity, battery outcome, flake accounting.** Green run
`runs9/20261015T212551992799Z` (247/247) vs the r89 green reference
(`corpus/live/r89-author/runs5/20261015T195521854184Z`): `common=235 new_only=12
old_only=0`, **signature/verdict mismatches = 0** — no prior row changed. The two green runs
(`runs9/…` and `runs12/20261015T220233737605Z`) have identical signatures and verdicts for
all 247 rows; raw-output diffs are confined to 13 documented-volatile rows (F4). The
report's rep table reproduces from the 14 `verdicts.json` on disk: rep1 `r90_lattice_props`
FAIL (author transcription bug — the pin dropped the `Thread Group|` group-header token,
first divergence at char 1110, pin 2633 vs emitted 2646 bytes; probe output itself stable),
reps2–13 r90 12/12 PASS, rep9 + rep12b green 247/247. All non-r90 failures are the
documented pre-existing flake classes (`transition`, `negative_transition`, `overlap`,
`audio_playback`, `audio_bus_route`, `input_lattice_pre_frame`).

**V10 — harness invariants.** 240 CASES all 5-tuples, no duplicate names; every
`expected_errors` key corresponds to a CASES row (no orphan keys); no envelope row carries
entries (no tuple-into-classifier path); the three hunks are pure insertions; the 12 new
rows sit immediately before the crash/descendant tail; result rows 247 = 240 CASES + 7 meta.

---

## 2. Findings (ranked by severity)

**F1 (medium — evidence integrity; the committed tree carries no r90 evidence).**
`git ls-files corpus/live/r90-author` → **0 files**: nothing of the lane's evidence tree is
in `ee20575` (contrast r89: 1317 files committed under `corpus/live/r89-author` in
`8cea888`). The report's evidence index ("`corpus/live/r90-author/` — `manifest.sha256`
covers all") and the commit message's "247/247 x2 green" rest entirely on **untracked
worktree** files. Those files exist and verify here (`sha256sum -c` → 4015/4015 OK, no
self-entry — r89's F1 self-hash defect is absent), and I re-verified the load-bearing claim
by fresh execution, so no verdict changes; but a checkout of `ee20575` cannot reproduce the
green-run claim. Suggested action: fold the evidence tree into the wave commit (as the r89
fold did) or scope the report's evidence index to committed artefacts.

**F2 (medium-low — evidence mislabel: the "30 tps" receipt is a 60-tps run).**
`r90-author.md` cites `corpus/live/r90-author/f_pair_30tps.rep{1,2}.out` as receipts
"under `--physics-ticks-per-second 30`". That CLI option **does not exist in this build**:
`godot --help` lists no physics-ticks option, and running the same arm with and without
`--physics-ticks-per-second 30` produces **byte-identical** output with **empty stderr**
(`corpus/live/r90-reviewer/runs/tps{A,B}.{out,err}`). The receipt itself prints `tps=60`
with `ncb=60 / pf_delta=60 / tick_dh=1:59` and the 60-tps `f_normal y=-7.6969` — i.e. a
plain 60-tps run at default `--frames=60`; the comparison drawn against the pin
(`ncb=120`) is a frames comparison, not a tps comparison. The *claim* the receipt was meant
to support is nonetheless **true**, and I verified it the boundary's way
(`physics/common/physics_ticks_per_second=30` in a project copy): `tps=30` is printed and
the pins fail loudly (V8). Suggested action: replace the receipt/claim with a real 30-tps
project boot, or state explicitly that no CLI tps override exists on this build.

**F3 (low — report arithmetic).** "All 12 r90 rows are PASS in every rep after the rep1
props-pin fix — 13 completed reps × 12 = **156/156** row-instances (rep1 itself had 11/12…)"
is internally inconsistent: over the 13 reps `runs1..runs13` the count is **155/156** (rep1's
props FAIL is the one miss); over all 14 `verdicts.json` on disk (incl. rep12b) it is
**167/168**. No pin affected.

**F4 (low — report precision; repeat of r89's F4 class).** The rep9↔rep12b stability
sentence ("the only output diffs are declared envelope modes (`api_press`, `release_edge`,
`ui_ns`), the volatile `mp_loopback` peer-id token, and `frames=` jitter rows
(`route_toggle`, `tween_flash`)") is incomplete: **13 rows** differ in raw output — those
six plus `save_roundtrip`, `save_process_writer/reader/missing` (pid/path),
`crash_spontaneous_sigabrt` (ASLR/load addresses) and both descendant rows (pids). All are
pre-existing volatile diagnostics whose signatures and verdicts are identical
(mismatches = 0), and the load-bearing claim (247/247 ×2, all 12 r90 rows byte-identical)
is verified true.

**F5 (low — evidence hygiene; r89 F1 class, weaker form).** `manifest.sha256` includes
**216 receipts under `runs/`** that are excluded by `corpus/live/.gitignore` (`runs/`), so
even if the tree were committed the manifest could not verify from a checkout — it only
verifies in the live worktree (4015/4015 OK here). No self-entry this time. Suggested
action: state the gitignore exclusion in the report, or force-add the fresh-arm receipts.

**F6 (low — by-design, noted for the axis).** The exact-entry floor gate checks only
`dead_in_run` (≥1 match); the pinned per-run multiplicities (comrefuse ×1, impedge
`p_mass<=0` ×2) are recorded as census data but not enforced — a future engine emitting the
refusal once or thrice would still PASS. Consistent with the r87/r88/r89 precedent.

---

## 3. Residual risks

- **Envelope absence**: the 12 pins admit exactly one mode; a third mode (r89's lesson)
  would fail loudly rather than be absorbed. Coverage: 6 author arm reps + 14 battery reps
  + 3 sequential + 1 8-way-concurrent rep of mine, plus the delegated labrat's static audit
  — no second mode observed. The labrat could not execute, so heavier-load exhaustiveness
  remains untested by an independent seat.
- **`tps=` is a project-setting pin, not the effective rate**: a run that changed the
  effective step rate without rewriting the project setting is caught only by
  `ncb`/`pf_delta`/`tick_dh`. Those were exercised at 60 tps (all reps) and 30 tps (this
  seat, V8); 120/240 tps were exercised by the boundary on the scout probe, not on the
  folded probe.
- **4-dp/6-dp float32 pins** (`y=482.2250`, `vy=933.3325`, `rest=-7.7000`, `iI=0.031250`):
  reproduced exactly by my float32 model on this build; a solver/backend change moves the
  last decimal (same class as r89 bridge/ring pins).
- **Empirical solver readbacks** not derivable from closed form: contacts
  `cvel=0.0000,16.3333` and `pos=0.0000,0.3000` at rest, contacts `ncb=45` (sleep onset),
  freezelock `f_normal -7.6969` (mid-settle). Stable over 9+ reps, solver-version-sensitive.
- **Build/host tokens**: `nprops=88` + the full ordered `props` list (incl. the `Thread
  Group` header), `methods`, `enum`, `ps_*` defaults — each flips loudly on a build bump
  (intended).
- **The 30-tps `late_body` pairing is deliberately unpinned**; my 30-tps runs showed
  `sync0` (`cb0_rel=1`), so the pin's 30-tps failure is via `tps=`/values, not via the
  pairing shift. Either way it fails loudly; no gap.
- **No full 247-row battery re-run by this seat** (host load ~70; documented flake classes
  make a single run uninformative). Per-row coverage — 12 rows × (14 committed battery reps
  + 6 author arm reps + 3 fresh + 1 concurrent) + the Dummy/30-tps falsification cells — is
  the load-bearing verification and is complete.
- **Concurrent worktree churn**: while this review ran, a sibling r89-fold seat edited
  `corpus/fixtures/{run_battery.py,geo2d_lattice.gd}` in the same worktree (header note).
  The review pins `ee20575`'s bytes; any later commit that folds those sibling edits is a
  new artefact set and would need its own diff-scoped check for the r90 rows.
- **F1**: the lane's receipts can be lost by a worktree clean; the report and this review
  are the only durable pointers until the orchestrator folds the tree.

## 4. Blockers

None. Shipping/admission decisions remain with the operator.

---

## 5. Evidence index / reproduction

| artefact | path |
|---|---|
| fresh 12-arm × 3-rep receipts (this seat, untracked) | `corpus/live/r90-reviewer/runs/**` + `run_arms.sh` |
| 8-way concurrent rep (12 arms) | `corpus/live/r90-reviewer/runs_par/*.par.{out,err,rc}` |
| Dummy-boot falsification cells | `corpus/live/r90-reviewer/runs_dummy/**` + `proj_dummy/` |
| real 30-tps falsification cells | `corpus/live/r90-reviewer/runs_tps30/**` + `proj_tps30/` |
| CLI-flag A/B (no-op proof) | `corpus/live/r90-reviewer/runs/tps{A,B}.{out,err}` |
| classifier extraction (verified sha `749fa0607e7707e6…`) | AST segment of `classify_process`, committed `run_battery.py:595–612`; driver `verify_fresh.py` |
| receipt manifest (this seat) | `corpus/live/r90-reviewer/manifest.sha256` — 174/174 OK, no self-entry |
| committed battery receipts | `corpus/live/r90-author/runs{1..13}/<stamp>/verdicts.json` (+ `runs12/…220233737605Z`); green = `runs9/212551992799Z`, `runs12/220233737605Z` |
| author fresh-arm receipts (re-classified 72/72) | `corpus/live/r90-author/runs/*.rep*.{out,err,rc}` |
| author evidence tree (untracked — see F1) | `corpus/live/r90-author/manifest.sha256` (4015/4015 OK worktree) |
| launch shape | `timeout -s KILL 25 godot --headless --path corpus/live/r90-reviewer/proj --script res://rb_lattice.gd -- --arm=<a> [--frames=N]` |

Reviewed commit `ee20575`; this seat made no tracked modifications and no commits.
