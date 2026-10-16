# r100 author — GUI input-routing capstone landed: 25 rows (14 scout cells + 11 boundary rows), 4 fixtures, battery 451/451 on final bytes

Seat `AUTHOR` (g2d lane r100, **capstone**) | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, `--headless`,
`DisplayServer.get_name()=="headless"`, 64×64 root viewport, 60 tps,
`RendererDummy`). Worktree
`~/Projects/shokunin/game-dev-2d-shokunin-wt-r100`, branch `wt-r100`, HEAD
`89f85ed8` (r96 author merge) — **nothing committed, nothing staged**.

Scope per dispatch: read `reports/round-100/r100-scout.md` +
`corpus/live/r100-scout/` and `reports/round-100/r100-boundary.md` +
`corpus/live/r100-boundary/`; **encode only boundary-surviving claims**;
insertion-only `run_battery.py`; new fixtures under `corpus/fixtures/`; full
battery **twice on final bytes**; live receipts under
`corpus/live/r100-author/`; this report. Zero commits. Every Godot launch is
`timeout`-bounded (25 s in the smoke harness, 8 s inside the battery's own
`execute()`), never unbounded.

**`lsp` disclosure.** No `lsp` device in this session and no GDScript language
server on this host — `definition`/`references`/`rename` were **unavailable for
every file**. No rename/symbol work was required: the task is fixture landing +
row encoding + behavioral verification, and every signature below is a
measured full line, not a hand-derived one.

**The host is shared.** loadavg 51–66 for the whole session (concurrent lanes).
"quiet" below never means idle.

---

## 1. Landed files

| file | sha256 | provenance |
|---|---|---|
| `corpus/fixtures/r100_gui.gd` | `dd826f6e7b74ba62fcfd175ab7a1cf0c40fd9712de4b33a18554930cf6dad073` (780 lines) | **byte-copy** of the frozen r100-scout probe `corpus/live/r100-scout/proj/r100_gui.gd` (no folds) |
| `corpus/fixtures/r100b_phase.gd` | `49298e6cc18c4e0de627105b9d95ff28ed2ccfa52bb1cc2da364b76d5430d4b7` (520 lines) | **byte-copy** of `corpus/live/r100-boundary/probes/r100b_phase.gd` |
| `corpus/fixtures/r100b_emul.gd` | `31087e7821eb4d2d5cf4bd28d9e5d8ca11bd52f83057fcd41889ecfecdbd4960` (37 lines) | **byte-copy** of `corpus/live/r100-boundary/probes/r100b_emul.gd` |
| `corpus/fixtures/r100b_seq.gd` | `4718a19e0050f4043613a5a93a13cbd812c811605f7a14d33e000544eafa94dd` (790 lines) | **byte-copy** of `corpus/live/r100-boundary/probes/r100b_seq.gd` |
| `corpus/fixtures/run_battery.py` | tracked, `+132 / −0` | insertion-only: r100 comment header + 25 CASES tuples + 3 `expected_errors` entries + `r100_expected_errors_all_matched` floor gate |
| `reports/round-100/r100-author.md` | this report (new, untracked) | — |
| `corpus/live/r100-author/**` | receipts/tools (new, untracked) | §6 |

`project.godot` untouched. No fixture was folded: **all four are pure copies**
so the hash chain to the frozen probes is exact (independently corroborated by
the read-only labrat audit, §7 H1). The one place the scout's *wording* was
wrong (the drag threshold) is corrected **row-side** and in the battery header,
never by editing a frozen fixture.

## 2. What the boundary let through, and what it did not

The r100-boundary report's verdict table (18 rows) is the encoding contract.
Applied:

| # | scout claim | boundary verdict | encoding consequence |
|---|---|---|---|
| 1–2 | STOP/PASS/IGNORE routing matrix + `set_input_as_handled`; `push_input` is a scene-tree injection (no `Input` state, no cursor) that *does* update hover | CONFIRMED, extended; hover half **synchronous** | `r100_gui_routing` + `r100_gui_hover` shipped verbatim; **new** `r100b_phase_hoverphase` pins the synchronous pick (`h_imm=A ev=[in@0]` before any await) |
| 3 | cursor written only by `Input.parse_input_event`, from `global_position` | observable CONFIRMED, **mechanism REWORDED — the write is FLUSH-GATED** | the scout's `r100_gui_cursor` row survives byte-identical (it samples after `await process_frame`); **new** `r100b_phase_cursorphase` pins the mechanism (`mm_imm=(0.0,0.0)` → `mm_flush=(20.0,20.0)`, `held 0→1`) and `r100b_phase_flushpos` pins the flush position (`sig@1=(20.0,20.0)`, i.e. **before** the `process_frame` signal) |
| 4 | `event.position` is control-local; `get_*_mouse_position()` are cursor-derived | CONFIRMED | `r100_gui_localpos` verbatim |
| 5 | hover clipped to the viewport rect, button routing not | CONFIRMED | `r100_gui_clip` verbatim |
| 6 | drag start = **accumulated `|relative|` > 10** | **REFUTED as worded [A]** — the law is **`|Σ relative| > 10`** | the pinned `r100_gui_drag` row is consistent with *both* models, so it ships unchanged; the **separating sign test** ships as `r100b_phase_dragphase` (`dp_sign_same drag=0` with Σ|rel| = 12; `dp_rel_only drag=1`; `dp_pos_only drag=0`), and the battery header states the corrected law |
| 7–13 | drop target = hover-picked; touch positional/tracked; both emulation directions; SubViewport isolation; warp inertness; focus-owned keys; headless-null render | CONFIRMED | the nine matching `r100_gui_*` rows verbatim; **new** `r100b_emul_state` pins the parsed-touch button state machine (`held 0→1→0→1`) that the scout's one-shot sample could not show |
| 14 | the 14 rows are byte-stable ×6 canonical + ×2 load | CONFIRMED and widened to **7 launch modes** | no envelope/mode split is authored anywhere — the rows are event-driven |
| 17 | is any payload a function of an unmodelled tick phase? | **NO CYCLE FOUND [A]** | no phase row is authored; the phase *probe* arm `startup` is deliberately **excluded** (it prints wall-clock `t=`) |
| 18 | can the 14 cells be replayed in one process? | **REFUTED — single-cell-per-process only [A]** | **new** `r100b_seq_clean` / `r100b_seq_noclean` pin the contamination chain (10/14 and 5/14 reproduction; first divergences pinned) |

Also encoded from the boundary's §6 (new mechanisms, all ×3 byte-stable here):
`r100b_phase_orderin` (`_input` runs **before** `_gui_input`, so a
`_gui_input`-side `set_input_as_handled` cannot suppress the `_input` copy),
`r100b_phase_coalesce` (parse-path motions coalesce at the flush — one event,
summed `relative`, last `position` — while pushed motions stay 1:1),
`r100b_phase_dblclick` (the engine never computes `double_click` for synthetic
events), `r100b_phase_velphase` (`get_last_mouse_velocity()` is `(0.0,0.0)` at
every sampled phase on both paths — the scout's "do not pin" warning was about
the `Input.warp_mouse` path, which no row prints).

## 3. Row inventory (25)

**Scout cells — `r100_gui.gd` (14, verbatim from the scout's
`author-rows.py.txt`, full-line signatures):** `r100_gui_{census, routing,
hover, motion, localpos, cursor, clip, drag, touch, subvp, warp, focus, render,
osmeta}`.

**Boundary rows — 11:** `r100b_phase_{cursorphase, hoverphase, dragphase,
coalesce, velphase, flushpos, orderin, dblclick}` (8 arms of `r100b_phase.gd`;
its 9th arm `startup` is excluded as deliberately unstable),
`r100b_emul_state` (`r100b_emul.gd`), `r100b_seq_clean` (`--clean=1`) and
`r100b_seq_noclean` (`--clean=0`) (`r100b_seq.gd`, each pinning the first
documented divergence line of its variant).

All 25 signatures are **full `PASS` lines** (no prefix cut, no ±1-tick tails),
so `ROWS_PREFIX == ROWS` needs no envelope.

**Deliberately NOT authored:**

- `r100b_phase_startup` — prints wall-clock `t=` and frame counters (the
  boundary's own §7 labels it unstable).
- any **mode-portability row** (`--fixed-fps` / threaded physics / hog load):
  the boundary's 7-mode table is real evidence, but the harness builds the
  engine command line itself and `flags` land *after* `--` as user args, so a
  per-case `--fixed-fps` is **inexpressible** without editing `execute()`
  (out of scope: insertion-only). The mode table is cited as the *reason* no
  envelope is needed, not re-encoded as rows.
- the scout's §7 pre-existing flake family (`negative_transition`, `overlap`,
  `audio_*`) — not this seat's lattice; **not re-attacked** (and not "fixed":
  fixing the harness's one-frame `current_scene` readiness or the meta-gate
  coupling would be a behavior change, not an authoring act — §8).
- every scout §8 unknown still unmeasured (multi-touch `index>0`, drag-preview
  content, `event_index` semantics, `in_local_coords` under a non-identity
  content scale, nested SubViewports, `Input.set_mouse_mode`,
  real-display drag/drop) — no row claims them.
- raw object reprs, `OS.get_thread_caller_id`, processor counts, adapter names,
  `Input.get_last_mouse_velocity` after `warp_mouse` — never pinned (scout
  §6.2; the `osmeta` row pins class existence + method counts only).

## 4. `run_battery.py` changes (insertion-only)

1. **CASES 419 → 444 tuples** (results rows 426 → **451** incl. the 7 meta
   probes): the r100 block (59-line comment header + 50 tuple lines) is
   inserted after `r96b_seed_seedcheck`, ahead of the crash/descendant tail —
   `descendant_pipe_detached_control`'s sleep-8 gap stays adjacent to the meta
   probes, and the final four CASES tuples are untouched.
2. **`expected_errors` += 3 entries / 3 strings** (after the r96 block):
   `r100_gui_render`, `r100b_seq_clean`, `r100b_seq_noclean`, each the exact
   single line `ERROR: Parameter "t" is null.` — the deterministic
   `RendererDummy` backbuffer-readback diagnostic measured in every one of
   these receipts. Each matched exactly 1 line in every run (no dead entries).
3. **Floor gate extended**: `r100_expected_errors_all_matched` over
   `case.startswith(("r100_gui_", "r100b_"))` — same named-by-round /
   covers-round-prefixes shape as r87–r96, so a dead r100 allowlist entry
   cannot pass silently. It lives inside the `sf_discriminations` dict that
   `probe_error_clause_surface` gates on, so it is load-bearing for the meta
   verdict (True in all three runs, including the flaked one).

**Insertion-only proof:** `git diff --stat corpus/fixtures/run_battery.py` →
`132 insertions(+)`, `0 deletions`; the apply script asserts post-hoc that
removing the three inserted regions restores the original file bytes
byte-for-byte; 444 CASES names, 444 distinct; `python3 -m py_compile` clean.

## 5. Evidence

### 5.1 Fresh-process smoke, ×3, production classifier (pre-battery)

`corpus/live/r100-author/make_rows.py` builds a scratch replicating
`run_battery.py`'s staging byte-for-byte (whole-fixture copy, per-run
`config/name` munging, `pickup.tscn` staging, the scratch-only 2-frame
`causal_chain.gd` readiness patch) and runs all 25 arms ×3 fresh processes
(75 launches, `timeout 25`, all `rc=0`), then classifies each row with the
production clause **copied verbatim from `run_battery.py:1310`**
(`classify_process`, merged stdout+stderr):

```
{"rows": 25, "duplicates": [], "failures": [], "all_pass": true}
```

75/75 accepts, 0 rejections, `uniq_sha=1` for every arm.
Receipts: `corpus/live/r100-author/runs/smoke/<case>.rep{1,2,3}.{out,err,rc}`;
per-row classification record: `corpus/live/r100-author/rows.json`.

### 5.2 Full battery, three runs on identical final bytes

| run | run dir | rows | result |
|---|---|---|---|
| rep1 | `corpus/live/r100-author/runs/20261016T084621281967Z` | 451 | **PASS 451/451** — `PASS battery` |
| rep2 | `corpus/live/r100-author/runs/20261016T085506490798Z` | 451 | **449/451** — `FAIL negative_transition` + `FAIL error-clause surface meta` (both the pre-existing class, §8) |
| rep3 | `corpus/live/r100-author/runs/20261016T090315730565Z` | 451 | **PASS 451/451** — `PASS battery` (second green) |

In **every** run: all 25 r100 rows PASS, all 7 meta probes PASS except rep2's
meta (below), and the r100 floor gate is True.

### 5.3 The rep2 failure is the scout's documented pre-existing coupling, not an r100 row

rep2's two FAILs are one event:

- `negative_transition` (exit 1, expected) — its allowlisted diagnostic never
  fired, so the pinned signature missed; the captured output shows the
  scout's §7 root cause verbatim: the probe reads `current_scene` one frame
  after `change_scene_to_packed`
  (`SCRIPT ERROR: … on a null value.` at `controls/scene_transition_negative.gd:22`)
  and then `ERROR: negative transition probe exceeded 120 frames`.
- `probe_error_clause_surface` — its only false discrimination is
  `census_bare_classifier_consistent`, and its only inconsistent census row is
  `negative_transition` (`any_entry_matched=False`,
  `bare_classification_rejects=True`): exactly scout §7 root cause 3, "any
  load-induced row flake fails the battery twice". `dead_entry_count=2` in
  rep2 = that row's own two allowlist entries; **no r100 entry went dead**
  (`matched_lines=[1]`, `dead=[False]` for all three).

Isolated re-runs of that row against rep2's own scratch at the final bytes:
**3/3 PASS** (`rc=1`, signature present, 0 `ERROR:` lines) — the row is
load-sensitive inside the serial battery, not broken, and nothing in the r100
block touches scene transitions (the 4 new fixtures never call
`change_scene_to_*`). The same row family flaked in the r89 author's own
receipts and in the scout's HEAD sweep (`r100-scout.md` §7).

### 5.4 The pinned bytes are the battery's own bytes

`corpus/live/r100-author/crosscheck_receipts.py` compares each r100 row's
captured output **inside the battery** against the author's independent
fresh-process smoke receipt for the same case: **25/25 line-for-line
identical, 0 mismatches in all three runs**. Two different scratch
environments, the same bytes.

### 5.5 rep3

`PASS 451/451` — `PASS battery`, run dir
`corpus/live/r100-author/runs/20261016T090315730565Z`: the **second green on
the identical final bytes**, with `negative_transition` and the
`probe_error_clause_surface` meta both PASS and `dead_entry_count=0`. Across
all three runs the 25 r100 rows are 25/25 PASS and the r100 floor gate is
`True` — including rep2, where only the pre-existing coupling flipped.

### 5.6 Allowlist census (rep1, from the meta row's own census)

`rows_with_expected_errors=74`, `dead_entry_count=0`, `dead_entries=[]`; for
each r100 case: `entries=[ERROR: Parameter "t" is null.]`,
`matched_lines=[1]`, `dead_in_run=[False]`, `bare_classification_rejects=True`,
`allowlisted_classification_passes=True` — i.e. all three rows are
census-consistent and the entries are floor-live, not ceiling.

## 6. Live receipts (all under `corpus/live/r100-author/`)

| path | content |
|---|---|
| `runs/smoke/<case>.rep{1,2,3}.{out,err,rc}` | 75 fresh-process smoke receipts (25 arms × 3) |
| `runs/<stamp>/verdicts.json`, `save-process-verdicts.json` | the three full battery runs |
| `battery-rep{1,2,3}.{out,err}` | battery stdout/stderr per run |
| `runs/isolated-negative_transition/rep{1,2,3}.{out,err}` | the isolated re-run of the pre-existing flake row at final bytes |
| `make_rows.py` | smoke harness + row builder (production classifier copied verbatim) |
| `rows.json`, `rows.py.txt` | per-row classification record + generated tuples |
| `analyze_run.py`, `crosscheck_receipts.py`, `apply_insert.py` | run analysis, battery-vs-smoke byte cross-check, insertion applier |
| `RECEIPTS.md`, `manifest.sha256` | hash summary |

## 7. Independent probe (frozen `probeParent`, exactly one read-only labrat)

One `ufo-labrat` dispatch (agent `374d001d`), read-only, advisory, **wrote
nothing**. It reported 5/6 hypotheses CONFIRMED — fixture byte-identity
(780/520/37/790 lines read end-to-end), 25 distinct `r100_gui_`/`r100b_` cases
in one contiguous block ahead of the crash tail, all four referenced scripts
present, `rows.json` ↔ battery tuples 1:1 verbatim, and the exact
`expected_errors` entries + `r100_expected_errors_all_matched` gate shape.
**H2 (insertion-only via `git diff`) came back NOT-VISIBLE** — that substrate
has no shell/git binary, so the zero-deletion claim is carried by this seat's
`git diff --stat` (§4) and the applier's byte-restore assert. Its one caveat
(H1 compares rendered text, not hashes) is closed by the `sha256sum` table in
§1. It also independently noted the phase probe has 9 arms and 8 were pinned —
consistent with the deliberate `startup` exclusion.

## 8. Remaining risks / blockers

- **The battery's verdict is load-conditional at HEAD, and the r100 block is
  not the cause.** rep2 flaked on `negative_transition` + the
  `census_bare_classifier_consistent` coupling the scout already documented
  (§7 above). Fix candidates remain the harness's own 2-frame readiness pattern
  extended to the transition/overlap fixtures and a longer audio window — a
  behavior change for the operator, **not** made here. Nothing in this seat's
  25 rows interacts with that family.
- **`r100b_seq_*` rows encode stateful contamination by design.** They pin
  first-divergence lines of a single-process replay; if a future engine makes
  the cells composable (or the cursor/emulated-button state resettable), these
  two rows FAIL — the correct, loud failure for a genuinely changed claim. The
  tracked battery launches one fresh process per case, so the *other* 23 rows
  are unaffected either way.
- **Host/engine pinning.** Every value is this host / Godot
  `4.7.2.stable.arch_linux.ed1daf0bf` / `--headless` / 64×64 root viewport /
  identity transform; no off-host claim. The `render`/`seq` allowlist line is
  the dummy-storage diagnostic text, engine-version pinned like the corpus's
  other allowlist entries.
- **`corpus/fixtures/__pycache__/run_battery.cpython-314.pyc` is a tracked
  build artifact** regenerated by any import/compile of the battery; restored
  to HEAD bytes after the final run (r95/r96 handling).
- **The r100 rows are single-cell-per-process by construction** — a future
  probe that batches cells must reset the viewport cursor and the emulated
  button state (no reset API exists headless: `Viewport.warp_mouse` is inert;
  the only reset is a parsed matching release or a fresh process).
- **Blockers: none.** Nothing committed; unrelated lanes' untracked
  `corpus/live/` artifacts untouched; no stray Godot processes left.

## 9. Evidence index (exact run dirs)

- smoke scratch: `corpus/live/r100-author/runs/20261016T084549529755Z-rows/scratch`
- rep1: `corpus/live/r100-author/runs/20261016T084621281967Z` (PASS 451/451)
- rep2: `corpus/live/r100-author/runs/20261016T085506490798Z` (449/451 + meta, pre-existing class)
- rep3: `corpus/live/r100-author/runs/20261016T090315730565Z` (PASS 451/451)
