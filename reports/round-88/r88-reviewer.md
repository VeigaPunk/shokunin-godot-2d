# r88 reviewer — independent verification of the r88 diff (work `3c47eee`, report `f9e8a5b`)

Seat `REVIEWER` (r88) | host **devin** | Godot `4.7.2.stable.arch_linux.ed1daf0bf`
(`/usr/bin/godot`, `--headless`, 60 tps, GodotPhysics2D), Python 3.14.7.
Reviewed commit `3c47eee` (parent `d15c54d`) and report `f9e8a5b`; HEAD at review
time `6ce55dd` (r88-scribe custody commit). `git status --porcelain -uno` is
**empty** — no tracked modifications, no commits by this seat.

**`lsp` disclosure.** No `lsp` device and no GDScript/Python language server is
exposed to this seat (no `references`/`definition`/`diagnostics` tooling
available). Every check below is a textual read of the landed sources plus
fresh-process execution receipts — the literal fallback, recorded here so it is
never presented as semantic proof. Seat-owned scratch/receipts:
`corpus/live/r88-reviewer/**` (untracked).

**Verdict: CHANGES-needed.** Two actionable findings (F1, F2) — both already
measured and given verified fixes by this round's own boundary seat — plus
low-severity report precision (F3) and residual risks (F4–F6). Everything else
in the diff checks out; all claim arithmetic reproduces.

---

## 1. What was verified clean

**V1 — additive diff, prior rows untouched.** `git show --numstat 3c47eee`:
`run_battery.py` **+42/−0**, `r88_surfaces.gd` +422, `r88_spawnable.tscn` +4.
The run_battery diff has **0 removed lines**; three insertion sites
(`run_battery.py:385–399` 8 CASES rows, `:811–813` 1 `expected_errors` entry,
`:2414–2421` 1 discrimination key). The literal `CASES` list is 200→208 entries;
verdict rows 207→215. The 8 new rows sit at CASES index 196–203, immediately
before `crash_spontaneous_sigabrt`; `descendant_pipe_detached_control` is
immediately followed by `descendant_pipe_forged_signature_release` — no inserted
row lands inside the descendant `sleep 8` gap the author's comment guards.

**V2 — every pinned evidence string is verbatim in the receipts.** Parsed the 8
CASES pins out of `run_battery.py` and matched them against
`corpus/live/r88-author/arms/<arm>.{0..3}.out`: **8/8 pins present in 4/4 reps**
(uniq PASS payload = 1 each). `mp_loopback` is the only arm whose whole-file
bytes differ across reps (uniq=4); the difference is confined to the declared
volatile `R88S mp_lb … raw_uid=…` diagnostic line — the PASS payload is
byte-identical ×4 (`PASS r88_surfaces mp_loopback …` ×4 uniq=1). The same 8 pins
are present in the recorded outputs of both battery runs.

**V3 — battery runs.** `runs1/20261015T181519396144Z` and
`runs2/20261015T181910437115Z`: **215/215 PASS each**, top-level `verdict=PASS`.
Both runs' scratch copies of the fixture are sha256
`78370a044df10b28c30045aa3cee98798a3e3b45a4b90c5f517e9ee237b331e9` == the
working-tree fixture — the runs exercised the landed bytes.

**V4 — prior-row identity (reproduced).** `corpus/live/r87-baseline/compare.py
godot` against both r87 refs (r87-critic2 `…T175608856719Z`, r87-fold-check
`…T174312754775Z`): `common=207 new_only=8 old_only=0 tuple_mismatches=1
(seeded=0 meta=1)` for each. The single meta delta is exactly
`probe_error_clause_surface`, and the normalized sub-diff is exactly:
census rows 52→53 (+`r88_surfaces_sprite_phys`) and discriminations 36→37
(+`r88_expected_errors_all_matched`), with every other census row and
discrimination value byte-equal. runs1↔runs2: `common=215 … tuple_mismatches=0`.
The author's "1 meta tuple delta = census enumeration" characterization is
accurate.

**V5 — expected_errors / census / gate.** The new entry is exact-shape
(`run_battery.py:811`), and the census row shows `matched_lines=1`,
`dead_in_run=false`, `bare_classification_rejects=true`,
`allowlisted_classification_passes=true` in both runs. The new gate is
non-vacuous: `census_covers_all_allowlisted_rows` (`run_battery.py:2380`)
forces every allowlisted row into the census, so the `r88_` row cannot vanish
and leave `all(...)` trivially true; the r87 gate correctly does not cover the
`r88_` prefix.

**V6 — spawner-refusal correction is real.** Fresh seat-owned probe
(`corpus/live/r88-reviewer/runs/spawncheck.{out,err}`): in 4.7.2 `spawn(0)` and
`spawn()` **both** refuse with `ERROR: Custom spawn requires the
'spawn_function' property to be a valid callable.` at
`spawn (modules/multiplayer/multiplayer_spawner.cpp:325)`; with a valid
`spawn_function`, `spawn(0)` returns a `Node2D` and adds it under `spawn_path`.
The arm's positive control is indeed the registered-scene auto-track
(receipts: `pos[added=SpawnableOne c_got=SpawnableOne c_pos=33.0000,44.0000]`,
`pos_wait=1` ×4). The author's claim is confirmed (the scribe's "unreceipted"
item is now receipted, though in this seat's untracked tree).

**V7 — peer-uid normalization.** The arm normalizes with a **literal**
`String(e).replace(str(auth_uid), "<C>")` (`r88_surfaces.gd:155–160`) — not a
regex, no length assumption, so the boundary's 4–5-digit tail is handled by
construction. The four fresh receipts exercised 9–10-digit ids only
(`734451770`, `1729987873`, `831283327`, `1217620113`), so the tail path is
empirically unexercised but code-correct; `uid_s=1`/`uid_after_dyn=true` are
structural. (Battery-side note in F5.)

**V8 — audio pin sits past the falsified window.** Seat-owned timeline
(`runs/aud.*`, 4 reps): `playing` true f0–f8, first false at f9 (2/4) / f10
(2/4), false f19–f25; peak `-200.00` at *every* frame; `pos=0.000` throughout.
The arm reads `p.playing` after its 20-await loop (≥f20) and samples peaks at
f4/f9/f14/f19 — outside the boundary's falsified early window (f0–f8) and past
the flip band (f6–f13). The negative pin is sound.

**V9 — guards and hazards.** `--arm=` (empty), `--arm=bogus`, and no arm all
exit rc=1 with `FAIL r88_surfaces … reason=empty_arm|unknown_arm`; `arm=` is the
first printed line. Greps: no `offset_polyline`, no `get_global_rect`; the two
`range_height` hits are comments only (`r88_surfaces.gd:14,255`).

**V10 — one canonical runtime / identity.** Every receipt and verdict banner is
`4.7.2.stable.arch_linux.ed1daf0bf`; the battery's scratch project name is
stamped per run (`MechanicOneShotTest-<stamp>`) and both runs carry their own
scratch tree — no cross-run identity leak. Measured wall times reproduce the
report's budget: 0.62–1.57 s/arm, `mp_spawner` 2.76 s.

---

## 2. Findings

### F1 (HIGH, actionable) — two pinned rows carry Case-B startup-race realizations; "Envelopes added: 0" is not established for them

**Where.** `r88_surfaces_sprite_phys` pins `pos=…74.5675` (`run_battery.py:395`);
`r88_surfaces_light_props` pins `body_y=118.4614` (`run_battery.py:391`).

**Why it is a defect.** `r88-boundary` §2/§3.2/§3.3/§4.3 (report lines 58–113,
126–136, 238–243) measured the same code shape landing on two step counts
depending on the first main-loop iteration: Case B = `74.5675` / `118.4614`,
Case A = `66.5952` / `107.9190`, with the mode **flipping run-to-run on this
host** (their mirror: 3/3 Case A in one window, 8/8 Case B under 8-way
concurrency, then B, A, B sequentially). Boundary directive 1 (report lines
249–255) says explicitly *do not pin the fall-distance values as written*, and
offers a v≠0 sync recipe **verified deterministic in both modes**; directive 3
keeps the audio sample point (done), directive 5 is F2.

**Fresh spot-run evidence (this seat, same host/window).**
- The author's exact `_arm_sprite_phys` logic in a smaller script → Case A
  `pos=250.0000,66.5952` **4/4** (`runs/armx.*`) and 3/3 in a warm project dir
  (`runs/armx2.*`) — the pinned `74.5675` is a property of the launch shape, not
  of the arm logic.
- The author's exact `_arm_light_props` logic in a smaller script → Case A
  `body_y=107.9190` **4/4** (`runs/lightx.*`) vs the pinned `118.4614`.
- The landed fixture itself was Case B in **all 29 pristine** spot-runs by this
  seat in this window — 6 sequential `light_props` (`runs/lp.seq*`, `118.4614`),
  12 sequential + 8 concurrent `sprite_phys` (`runs/sp.loop*`, `runs/sp.conc*`,
  `74.5675`), 3 more `sprite_phys` from a fresh project dir (`runs/realcopy*`)
  — plus 16 delay-mutated runs (`runs/lp.delay*`, `runs/sp.delay*`:
  `OS.delay_msec(200)` and 1–100 ms, all still Case B). I.e. currently B-biased
  and delay-insensitive, but the *quantity being pinned is a mode*.

**Impact.** The author's 6 samples (4 fresh + 2 battery) cannot establish mode
stability against a flip the boundary measured on this host, and the report
neither mentions the race nor declares the rows as mode candidates. On a host /
window that lands Case A, both rows fail loudly (`66.5952`/`107.9190` ≠ pins) —
a latent flake in landed rows, and an overclaimed stability record
(author report lines 121–126).

**Fix (cheap, already verified).** Apply the boundary's v≠0 sync recipe (keeps
the current pinned values, deterministic in both modes), or declare the two
rows as mode-envelope candidates with both payloads — the mechanism exists
(`run_battery.py:816–823`: evidence tuple → PASS iff ANY payload appears).

### F2 (MEDIUM, actionable) — `ray_through_occluder=true` is a vacuous pin (boundary directive 5 unfixed)

**Where.** `r88_surfaces.gd:270–281`: the ray is
`PhysicsRayQueryParameters2D.create((-50,-80),(-50,60))` — vertical at x=−50 —
while the occluder polygon (local `[(0,0),(10,0),(10,10)]`, `occ.position=(0,-40)`)
occupies global x∈[0,10], y∈[−40,−30]. The ray can never intersect it, so the
pinned boolean is true regardless of physics. This is the exact ray
`r88-boundary` §3c/§4.3 (lines 48, 198–208) falsified as evidence, with a
sharp-ray control that is empty in the occluder arm and **hits** in a
`StaticBody2D`+`CollisionPolygon2D` control; directive 5 (lines 264–268) asks
for the crossing ray if the boolean is meant to be evidence.

**Impact.** The row's occluder-noncollision claim is still carried — by
`body_y` pass-through (the body crosses the occluder band; the boundary's
collision control stops at −47.7) — but that is exactly F1's mode-dependent
value, so as landed the only *stable* evidence in the row is `occ_is_co=false`
(a class check). The pinned boolean measures nothing.

**Fix.** Use the crossing ray (e.g. y=−35, x −50→50) as the boundary verified,
or remove the boolean from the evidence string and let `body_y` carry the claim.

### F3 (LOW, report precision)

1. Author report line 39 says "**CASES 207 → 215**": the literal `CASES` list is
   200→208 entries; the **result rows** are 207→215 (7 meta rows are appended
   outside `CASES`). The +8 delta and all row-level claims are correct — the
   label conflates CASES entries with verdict rows.
2. Author report line 85 says the client received the `SpawnableOne` twin "in
   ~4 frames": the receipts show `pos_wait=1` and `frames=0` in all 4 fresh
   reps — replication is observed on the next frame, not ~4.
3. Author report line 81 quotes the refusal as `at: spawn
   (multiplayer_spawner.cpp:325)`; the engine emits
   `at: spawn (modules/multiplayer/multiplayer_spawner.cpp:325)` (verified in
   `runs/spawncheck.err`). Substance unaffected.

### F4 (LOW, residual risk) — fixed loopback ports 41777/41778

Boundary directive 7 (lines 271–274) requires MP arms to own their port. Within
one battery run the cases are serial and each port belongs to one case, and the
author disclosed the ports (report lines 130–131) — but two concurrent battery
runs on this host can cross-connect. I traced this arm's contamination
signature: the loser prints `rc=[20,0]` → pin mismatch, and the winner can gain
an extra `peer_connected` entry → the pinned 5-entry `order=[…]` list no longer
matches (the pin requires the closing `]` after `s_disc<C>`). Both directions
fail **loudly**; there is no silent-pass path. Report it as a cross-lane flake
source, not a soundness hole.

### F5 (LOW, residual) — uid-tail coverage on the battery side

The arm's literal-replace normalization is tail-correct (V7), but the receipts
contain only 9–10-digit ids, so the 4–5-digit tail (boundary: 21/600 000) is
unexercised. Additionally `compare.py`'s normalizer
(`\b[0-9a-f]{8,}\b`) does not catch letter-glued tokens, so
`s_conn<uid>`/`s_disc<uid>` stay raw on the declared-volatile `R88S` line (the
runs1↔runs2 `OUT-DIFF` is exactly those two tokens), and a 4–5-digit uid would
also leave `uid_c=`/`raw_uid=` raw. This touches only cross-run normalized
diffs of a declared-volatile diagnostic line — never the pin or the verdict.

### F6 (INFO) — `mp_spawner` worst-case frame budget vs the 8 s case bound

Healthy path measured 2.76 s (~303 frames). With two broken replication legs
(`pos_wait`+`sync_wait` at their 300-frame bounds on top of `neg_wait=300`),
~1200 frames exceed the battery's 8 s per-case bound on a 60 fps host → the
regression surfaces as TIMEOUT rather than pin mismatch. Still loud; noted so
the "comfortably inside the 8 s bound" wording (report line 72) is not read as
covering the multi-leg-broken case.

---

## 3. Residual risk and verification gaps

- **F1 is not reproduced against the landed fixture on this host** (29/29
  pristine Case-B runs, including 8-way concurrency and a fresh project dir,
  plus 16 delay-mutated runs). The finding rests on
  (a) the same arm logic yielding Case A in a different launch shape on this
  host, and (b) the boundary's fixed-file flip measurements. Whether the
  battery's exact launch shape can land Case A on a faster host is unmeasured
  here; the fix is cheap either way.
- **No `lsp` device**: no `references`/`definition`/`diagnostics` queries were
  possible; source reads + fresh-process receipts only (recorded).
- **No fresh full-battery re-run** by this seat (bounded spot-runs only, per
  dispatch). Prior-row identity is verified through the author's recorded
  verdicts with `compare.py`, not by an independent 215-row run.
- **Cross-lane port contention** (F4) was not re-measured with two concurrent
  batteries; the contamination failure mode was derived from the arm's pins and
  the boundary's measured signature.
- Bounded claim: every execution statement above is Linux headless Godot
  `4.7.2.stable.arch_linux.ed1daf0bf`, 60 tps, GodotPhysics2D, this host, this
  window; no Windows/macOS or exported-build claim.

**Recommendation: CHANGES-needed** — land F1 (sync recipe or envelope) and F2
(crossing ray) before this diff is treated as stable; F3 is text-only; F4–F6
are residual risks to carry in the round record.
