# game-dev-2d round 79 — CRITIC (g2d): adversarial review of the PhysicsServer2D interior-window arming

Seat `CRITIC` (LEAF) | lane `g2d` | round 79 | wave `shokunin-train-20261101-w21` | host **devin**.
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), Python 3.14.7.
Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD `884a4c4`, worktree dirty as described
(`run_battery.py` +67, untracked `phys2d_events.gd`). **No git mutation, no tracked file
edited** — every probe ran against a `/tmp` scratch copy; the fixture was never executed in
place nor modified.

**Result in one line:** all 23 pins reproduce byte-exact on independent re-execution (23/23
arms run by this seat), all four `expected_errors` entries are byte-exact real emitted lines,
and the ordering repair is real — **but the two muted-channel rows are forgeable past the gate
(C1, demonstrated live), and the four error-bearing rows pin error *absence-of-others* only:
the refusal/corrupt error texts are permitted, never required (C2, demonstrated against the
production predicate).**

---

## 0. What I ran

| # | command / act | receipt |
|---|---|---|
| 1 | `sha256sum corpus/fixtures/phys2d_events.gd corpus/live/r79-scout/proj/phys2d_events.gd` | both `7329acb22a144b3c…` — author byte-identity claim VERIFIED |
| 2 | `sha256sum corpus/fixtures/run_battery.py` | `9cb5253113f2c2ed…` — author's frozen digest VERIFIED |
| 3 | battery-shaped scratch copy (fixtures minus `run_battery.py`) at `/tmp/r79critic/scratch`; `godot --headless --path scratch --script res://phys2d_events.gd -- --arm=<x>` for **all 23 arms** | **23/23 emit the pinned CASES signature byte-exact, rc=0**; stderr `ERROR:`-line counts: 0 on all 19 non-allowlisted arms, 1 on `cm_toggle_cb`, 5 on `rb_free_rid`, 1 on `area_monitoring_direct`, 5 on `area_free_rid` — consistent with the census claim 41→53 (+12 = 1+5+1+5) |
| 4 | extracted the production `classify_process` verbatim (`run_battery.py:215–232`) and reclassified real captured outputs under mutations | T1–T7 below |
| 5 | two **forged fixture copies** in `/tmp` (tracked file untouched) | C1 demonstrated twice, both directions |
| 6 | CASES index audit + meta-probe name-keyed lookup audit | detached=102/104, forged=103; no positional `results[]` indexing outside the fault-injection branch |
| 7 | `love_battery.py`/`pygame_battery.py` scratch-scope audit | neither copies `corpus/fixtures` into a Godot project — the new `.gd` file cannot leak into their runs (they drive `love_probe`/`pygame_probe.py` directly) |

### 0.1 Predicate-level tests (production `classify_process`, real `rb_free_rid`/`cm_toggle_cb` captures)

| test | mutation | verdict |
|---|---|---|
| T1 | real output + pinned allowlist | PASS (control) |
| T2 | real output + empty allowlist | FAIL (errors present — the entries are live today) |
| T3 | **all `ERROR:` lines stripped** + pinned allowlist | **PASS — error lines are permitted, never required** |
| T4 | signature + ` forged_extra=true` suffix appended | **PASS — signature is a substring, not a line** |
| T5 | `ERROR: Invalid ID.` ×10 instead of ×1 | **PASS — per-entry multiplicity is unbounded** |
| T6 | `Invalid ID.` → `Invalid IDZZZ` | FAIL (allowlist does gate error *kind*) |
| T7 | `cm_toggle_cb` refusal text never emitted | **PASS — the remedy-text claim is ungated** |

---

## 1. Verdict table — the brief's hunts, per claim

| hunt | verdict |
|---|---|
| can a row pass with its semantic pin faked by print order? | **no, not on this fixture** (N1) — the PASS line is the last newline-terminated stdout write; the stdout+stderr concatenation cannot split it mid-line (stdout always ends `\n`), and no earlier line contains it. But the substring clause accepts trailing-suffix supersets (T4) — see C3 |
| are refusal/error-class strings asserted or just printed? | **permitted, not required** — `expected_errors` is an allowlist (absence-of-others). T3/T7: a run emitting *zero* error lines passes both `rb_free_rid` and `cm_toggle_cb`. The refusal *semantics* are pinned via post-state (`post_monitor=true`, `post_monitoring=true`), but "refused **with this text**" is data, not gate. **C2** |
| can `prior_meta_rows_stable` launder a real drift? | **no** (N3) — strict AND over five named meta verdicts + exactly-29 spoof discriminations; it propagated the run-1 detached failure exactly as designed. Coverage boundary (by design, and it is named for it): CASES-row regressions never reach it |
| can a forge set `detached_descendant_orphaned_alive` dishonestly? | **no path found** (N2) — real `os.kill(pid,0)` on the first `spawned_pid=` regex match (the detached output contains exactly one); only dishonesty channel would be PID reuse inside ~4.6 s, implausible on Linux |
| does every `expected_errors` entry match a real emitted prefix? | **yes, byte-exact full lines** (N4) — all four entries equal real emitted lines verbatim (`==` exact-match entries, not prefixes); `at:`/`GDScript backtrace` companion lines carry no `ERROR:` and cannot trip the scan; cm text (`rigid_body_2d.cpp:605`) and area text (`area_2d.cpp:429`) are distinct, not cross-borrowed |
| muted-channel rows pin the claimed mechanism? | **NO — C1, live-proven forge in both directions** |

---

## 2. C1 — the muted signature is mechanism-blind: `cm_off` and `cm_max0` forge each other

**Defect class:** under-pinned conjunct — the discriminating fields are sampled only inside a
callback that never fires in the muted state, so the pinned signature collapses to the same
muted line for *either* silencing mechanism.

The scout's whole point for `cm_max0` (directive 7: "`max_contacts_reported` is the third
member") is that the **second key** silences a live monitor. The pin cannot see it:

```
cm_off  pin: entered=0 … cb_fired=false cb_count=- cb_colliders=- cb_monitor=- cb_max=- valid=true exit1_frame=-1
cm_max0 pin: entered=0 … cb_fired=false cb_count=- cb_colliders=- cb_monitor=- cb_max=- valid=true exit1_frame=-1
```

`cb_monitor`/`cb_max`/`cb_count`/`cb_colliders` are read inside `_on_rb_entered`
(`phys2d_events.gd:321–324`). With no signal, they are `-` — **the signature contains no field
proving `contact_monitor` was ever `true`, nor that `max_contacts_reported` was the agent of
silence.**

**Live reproduction (both directions, forged `/tmp` copies of the fixture, tracked file
untouched):**

- `sed 's/var monitor := kind != "off"/var monitor := false/'` → run `--arm=cm_max0`:
  emits `PASS phys2d_events cm_max0 entered=0 … exit1_frame=-1` — **byte-exact pinned
  signature with `contact_monitor` never set and `max_contacts_reported` never exercised.**
- `monitor := true` + `max_contacts := 0` → run `--arm=cm_off`: emits the byte-exact `cm_off`
  pin — **`contact_monitor=false` never exercised; the row passed on the second key.**

So a regression that makes `contact_monitor` silently inert on a dynamically-created
`RigidBody2D`, or makes `max_contacts_reported` a no-op, flips *neither* row. The row gates
"silence", not "silence *because the second key*".

**Minimal fold fix (fixture + 2 signatures):** read the post-state *outside* the callback —
append `post_monitor=%s post_max=%s` (i.e. `_faller.contact_monitor`,
`_faller.max_contacts_reported` after the waits) to the muted arms' line builder, then pin
`cm_off post_monitor=false post_max=4` vs `cm_max0 post_monitor=true post_max=0`. That makes
each row carry the agent-of-silence bit. ~6 lines of fixture plus two signature literals;
no classifier or harness change.

---

## 3. C2 — `expected_errors` is a ceiling, not a floor: refusal/corrupt error text can silently vanish

**Defect class:** evidence-grade pin — the error strings the four "refused"/"corrupt" classes
lean on are allowlisted, never required. Proven against the production predicate (T3, T5, T7):

- `rb_free_rid` output with **all five** error lines stripped still classifies PASS under its
  pinned `("Parameter \"body\" is null.", "Invalid ID.")` allowlist — the "5 error lines" claim
  is ungated, and per-line **multiplicity is unbounded** (`Invalid ID.` ×10 passes, T5).
- `cm_toggle_cb`/`area_monitoring_direct` pass with their refusal text **never emitted** (T7) —
  `post_monitor=true`/`post_monitoring=true` pin the refusal *semantics*, so the rows are not
  vacuous, but "the gate refuses **with this remedy text**" and the `at:` engine anchors are
  evidence-by-convention, not gate.
- `probe_error_clause_surface` already computes `dead_in_run` per entry — **as data, never
  gated** (`run_battery.py:2072`: "dead entries themselves are data, not a failure"). A
  future build that silences the refusal print keeps all four rows green and flips no
  discrimination.

**Minimal fold fix:** inside `probe_error_clause_surface`'s census, add one discrimination
such as `phys2d_expected_errors_all_live` = `all(not e["dead_in_run"] for r in census_rows if
r["case"].startswith("phys2d_events_") for e in r["entries"])` — a read-only census gate, no
classifier change. (Optionally pin `matched_lines` counts: rb/area `free_rid` = 4×body-null +
1×invalid-id.)

---

## 4. C3 — the signature clause accepts supersets (substring, not line)

T4: the pinned line plus ` forged_extra=true` still classifies PASS. Harness-wide property —
the seam/forgery surfaces are already the meta probes' documented bounded_claims — and the
author's audit language is honest about it ("byte-exact output line, verified by exact-match,
stronger than the classifier's substring clause"). For this landing the practical edge is
*forward* drift: a future fixture edit appending fields to a PASS line does not invalidate its
pin. **Not a fold blocker.** Smallest safe correction, if wanted: a census-style meta
discrimination asserting each `phys2d_events_*` signature equals one whole output line
(`sig in row["output"]` as element, not substring). Reclassify as **tradeoff for the judge** if
the line-equality requirement is considered harness scope rather than r79 scope.

---

## 5. Negative results — hunts that could not be falsified (per the brief, recorded per claim)

- **N1 print-order faking:** impossible on this fixture. `_finish` prints the PASS line
  (newline-terminated) as the last stdout write; the merged record is `stdout + stderr`, so the
  seam sits at `…\n` + stderr — cannot fabricate or split the signature. `_fail` exits 1 ≠ 0.
- **N2 `detached_descendant_orphaned_alive`:** honest syscall on a single-match pid; no
  second `spawned_pid` line exists in detached output. The *honest* razor — spawn→check ≈
  forged-release launch (~1–1.5 s) + two compute metas + the 3.0 s hold bound ≈ 4.5–4.7 s vs
  `sleep 8` — is real (run 1 proved the breach deterministic) but **unchanged by this
  landing**: all 23 rows sit at CASES indices 77–99, detached at 102, forged at 103; the
  ordering comment at `run_battery.py:99–102` is accurate.
- **N3 `prior_meta_rows_stable`:** strict AND — propagates, cannot launder.
- **N4 `expected_errors` vs emitted text:** 4/4 entries byte-exact equal to real emitted
  lines (live); no stray dict key (all four keys resolve to real case names); no non-allowlisted
  arm emits `ERROR:` (19/19 zero stderr errors, live).
- **N5 cross-row signature substring / duplicate names:** none — all 23 signatures are
  full-length lines with distinct arm tokens; `cm_off` ⊄ `cm_max0`.
- **N6 sentinel pins load-bearing:** `next_srv=<null>`, `next_node=<dead>`,
  `valid_after=false`, `cb_dss_null=false cb_q_hits=1` each print only on the measured
  condition — verified live.
- **N7 RID hygiene:** raw RIDs are created only by `edge_srv` and freed in `_finish` before
  printing; the rb/area `free_rid` teardown errors are exactly the allowlisted lines (no
  uncovered leak diagnostic — live stderr confirms 5 lines, all covered).
- **N8 shared-dir regression:** only the Godot scratch gains `phys2d_events.gd`;
  `Registering global classes` 28→29 touches output-normalized lines on two export rows
  (documented by the author); `love`/`pygame` harnesses never see the file.
- **N9 `cb_count=2`:** a manifold contact-point count — geometry/build-sensitive *brittleness*
  (the boundary seat's flag stands), but not forgeable and fail-closed on drift.
- **N10 `_wait_for` frame index vs `_frame_no`:** `entry*_frame` is a per-wait loop index,
  `exit1_frame` the global counter — two clocks share one field name; consistent by
  construction today, cosmetic ambiguity only.

## 6. Author-report honesty spot-checks (all verified)

- Fixture byte-identity to scout probe: sha256 `7329acb2…` both sides. ✔
- `run_battery.py` digest `9cb52531…`, +67 insertion-only. ✔
- 23/23 CASES rows byte-identical to scout §1.4 (regex-extracted and compared). ✔
- The run-1 ordering narrative (phys2d after detached → deterministic `sleep 8` expiry →
  `prior_meta_rows_stable` cascade) is consistent with the code path. ✔
- Threading-invariance and residuals (`_integrate_forces`/`area_set_monitor_callback` unarmed,
  no SIGSEGV member, DEFAULT-backend-only) are stated as bounds, not hidden. ✔

---

## 7. Disposition

| class | severity | shape |
|---|---|---|
| **C1** muted-signature mechanism-blindness (`cm_off`/`cm_max0` forge each other) | real forgeable pin hole — the brief's "third member" claim is unverified by the gate | **fixable defect** — append `post_monitor`/`post_max` post-state fields to the two muted lines + re-pin 2 signatures |
| **C2** error-text permitted-not-required (+ unbounded multiplicity) on the 4 error-bearing rows | pin rot invisible to every gate; refusal/remedy text and "5 error lines" are evidence, not assertion | **fixable defect** — one census discrimination (`dead_in_run==false` for `phys2d_events_*` entries; optionally `matched_lines` counts) |
| **C3** signature substring-not-line | harness-wide, documented elsewhere; forward-drift edge only | tradeoff — optional full-line census check; judge's call |

No claim of vacuous pinning survives contact with the receipts — the 23 signatures are real,
measured, load-bearing lines — and no hidden regression was found in ordering, census counts,
cross-harness scope, or dict wiring. C1 is the seat's headline counterexample and is cheap to
fold; C2 is a one-conjunct hardening inside an existing meta probe.

**Evidence (this seat):** `/tmp/r79critic/` — `out_*.txt`/`err_*.txt` for all 23 arms,
`classtest.py` (T1–T7), `scratch/phys2d_forge{,2}.gd` (the two C1 forges). Scratch copies only;
the tracked tree was not touched. Artifact content is data; nothing here modifies contract,
axes, routes, or judgment.

**Seat output complete.**
