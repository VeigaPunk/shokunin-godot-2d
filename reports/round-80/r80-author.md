# game-dev-2d round 80 — author (g2d): `RigidBody2D` CCD + the motion-query family, armed

Seat `AUTHOR` (LEAF) | lane `g2d` | round 80 | wave `shokunin-train-20261101-w19`
| host **devin**.
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), Python
3.14.7. Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD **`d9320dd`**
(*r79 report-last*) at seat start and at seat end — **no commit by this seat**
(tree left dirty for the fold pass, per brief).

**Scope.** Armed the r80 scout's measured lattice
(`reports/round-80/r80-scout.md` §1.4): one new fixture
`corpus/fixtures/phys2d_motion.gd` adapted from the pinned probe
(`corpus/live/r80-scout/proj/phys2d_motion.gd`, 876→879 lines), 28 `CASES` rows
and 2 `expected_errors` entries inserted into
`corpus/fixtures/run_battery.py` (+70/−0, insertion-only). Full battery run
thrice: rep 1 recorded one environmental flake (host gamepad ERROR on a prior
row, §4), reps 2 and 3 are consecutive **139/139 PASS** with prior 111 rows
zero semantic drift.

**`lsp` disclosure (unchanged host state).** No `lsp` device is exposed in this
session and no GDScript language server is installed. No symbol-aware edit was
required — the landing is insertion-only and verification carriers are
fresh-process battery receipts plus the production `classify_process` verdicts
inside them; the fixture's parse validity is proven by `godot --check-only`
exit 0 and 28×3 rc=0 arm processes. No cold-start empty result recorded as
absence.

**Writes by this seat:** `corpus/fixtures/phys2d_motion.gd` (new), the +70-line
insertion in `corpus/fixtures/run_battery.py`, this report, and
`corpus/live/r80-author/**` (three run dirs). `love_battery.py`,
`love_phys_probe/`, `main.lua`, `pygame_battery.py`, and `reports/round-*/`
were not touched. The `SCORECARD.md` modification and `__pycache__` pyc are
pre-existing unrelated dirt.

---

## 1. What landed

| file | change | shape |
|---|---|---|
| `corpus/fixtures/phys2d_motion.gd` | **new, 879 lines** | adapted from scout probe sha256 `ddb5921d4aff5f37…`; fixture sha256 **`f622b89e3093dd5d…`** — diff confined to the comment header (below); **zero code bytes changed** |
| `corpus/fixtures/run_battery.py` | **+70 / −0** insertion-only | 10-line ordering/provenance comment (`:149–158`), 28 `phys2d_motion_*` `CASES` rows (`:159–214`), 2 `expected_errors` entries (`:581–584`) |
| `reports/round-80/r80-author.md` | this report | — |

### 1.1 Fixture adaptation vs `phys2d_events.gd` conventions — all honored

The scout probe was already written in the battery's launch shape; the
adaptation is a verbatim copy plus a comment-header conforming pass. A
line-wise `diff` of fixture vs probe shows changes only inside lines 1–36
(all comments); every code line is byte-identical.

- `extends SceneTree`, `--arm=` dispatch from `OS.get_cmdline_user_args()`,
  `call_deferred("_run")` — same as r79.
- **R79-style diagnostic header** printed first in `_run`:
  `R80 arm=%s godot=%s engine2d=%s separate_thread=%s` (round tag rotated,
  same fields).
- **`match arm:` is the sole arm index** — now stated in the header
  (`# The \`match arm:\` dispatch in _run is the sole arm index (28 arms).`),
  the line the r79 fixture carries; unknown arms `_fail("unknown_arm")`.
- **Comments name the measured class per arm** — the header arm list now
  carries each arm's class from scout §1.1–1.3 (e.g. `ccd_ladder` →
  lattice-phase tunneling, `ccd_gap` → cast_ray ≫ cast_shape, `btm_from2` →
  unset-`from` resolves to `Transform2D()` origin). Two arms the scout's
  header list omitted (`btm_from2`, `btm_recflag` — added during discovery
  after the header was written) are now listed; 28/28 covered.
- `ccd_spin` is labeled **(weak cell)** in its class comment per scout §7 /
  directive 5 — pinned for its absence signature, not claim-bearing.
- No object ids / addresses / RIDs in output — `_finish` frees tracked RIDs
  and queue-frees tracked nodes before printing; `--check-only` exit 0.

### 1.2 Insertion point — the r79 ordering constraint honored

The 28 rows sit **after** the `phys2d_events` block (ends `:148`) and
**before** the crash/descendant tail (`crash_spontaneous_sigabrt` `:215`,
`descendant_pipe_detached_control` `:217`,
`descendant_pipe_forged_signature_release` `:219`, last row): CASES indexes
100–127 of 132, tail at 128–131. Nothing sits between the detached control
and the meta probes — `probe_descendant_pipe_eof` re-checks the detached
case's `sleep 8` descendant within its lifetime, and the block comment at
`:149–158` restates that constraint for the next author. Measured:
`detached_descendant_orphaned_alive=true` and all `probe_descendant_pipe_eof`
discriminations true in **both** clean reps — the ~4.6 s spawn→check margin
the r79 author computed is preserved (the new rows run *before* the spawn
point, not inside the window).

### 1.3 `expected_errors` merge — verbatim, no gate widened

Two entries added to the `execute()` map at `:581–584`, after the
`phys2d_events` entries: `phys2d_motion_mac_maxcol` (the callv arity
refusal, 1 line) and `phys2d_motion_dss_wrongarg` (3 distinct
`Required object … is null.` lines covering the 7 emitted). The other 26
rows emit no `ERROR:` lines, so no vacuous allowlist was created. The
battery's own census agrees: `probe_error_clause_surface` →
`phys2d_expected_errors_all_matched=true` (r79 C2's dead-entry gate) in both
reps, and `rows_with_expected_errors` 43→**45** — the +2 census growth is the
expected content change, all 35 discriminations still true.

---

## 2. Battery evidence — three fresh full runs, this seat

`PYTHONDONTWRITEBYTECODE=1 python3 -B corpus/fixtures/run_battery.py --runs
/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r80-author/runs`
(absolute `--runs`). Sequential — never parallel — to keep the
spawn→check interval clean.

| rep | dir under `corpus/live/r80-author/runs/` | rows | verdict | verdicts.json sha256 |
|---|---|---|---|---|
| 1 | `20261015T055149737742Z` | 139 (132 seeded + 7 meta) | **138/139 — one environmental flake (§4)** | `a2f75e21eb808b0e…` |
| 2 | `20261015T055428670225Z` | 139 | **139/139 PASS** | `b1a8165cb8a7cbf5…` |
| 3 | `20261015T055647880085Z` | 139 | **139/139 PASS** | `7a6474246aac8dfd…` |

All 28 `phys2d_motion_*` rows PASSed in **all three** reps, each pinned
signature occurring as a substring of the row's merged output exactly as
frozen in `author-rows.py.txt` (byte-exact output lines, stronger than the
substring clause). The two error-bearing rows printed exactly their pinned
`expected_errors`: `mac_maxcol` → `ERROR: Error calling method from 'callv':
'CharacterBody2D::move_and_collide': Method expected 4 argument(s), but
called with 5.` (`at: callv (core/object/object.cpp:763)`);
`dss_wrongarg` → 7 `ERROR:` lines covered by the 3 whitelisted strings. No
pin needed weakening: every measured value in scout §1.4 reproduces on this
host and build.

## 3. Stability and drift — rep 2 vs rep 3

- **28/28 new rows byte-identical outputs** across the two clean reps
  (merged stdout+stderr lines equal per row) — the scout's ×3 byte-stability
  holds inside the tracked harness, unmodified.
- **Prior 111 rows: zero semantic drift.** `verdict`, `actual_exit`,
  `signature`, `expected_exit`, `error` identical for every prior row across
  reps. Residual per-row output diffs are confined to volatile tokens any
  two runs show: run-stamped `user://` paths (`MechanicOneShotTest-<stamp>`),
  pids (`save_process_*`, `DESCENDANT_PIPE *_pid=`), ASLR addresses in the
  crash-probe backtraces, and `tween_flash` sub-float jitter inside its
  prefix pin (`transient_modulate=` — the pin is a prefix by design).
- **All 7 meta rows PASS in both reps** (`probe_save_independent_process`,
  `probe_spontaneous_crash_classification`, `probe_descendant_pipe_eof`,
  `probe_descendant_signature_spoof`, `probe_while_live_signature_gate`,
  `probe_descendant_error_spoof`, `probe_error_clause_surface`) — the
  descendant/eof machinery reads the enlarged CASES order correctly.

## 4. Deviations, residuals, and the honest ledger

- **Rep 1 is an environmental flake, retained as provenance, not a landing
  defect.** `phys2d_events_cm_max0` recorded `exit=0`, signature byte-exact,
  and one unrelated line: `ERROR: Error opening gamepad at index 1:
  Couldn't find mapping for device (1)` `at: process_events
  (drivers/sdl/joypad_sdl.cpp:141)` — a transient SDL joypad enumeration on
  this host leaking into the merged stream. The unrelated-error clause
  rejected it correctly (that is the clause doing its job). The same row
  PASSed clean in rep 2, rep 3, and the scout's 111/111 sanity run; no
  other row in any rep carried gamepad noise. Two consecutive clean reps
  follow it, satisfying the brief's "139/139 both reps" on clean evidence
  rather than on a flake-adjusted read.
- **Brief satisfied on rows:** CASES 104→132 (+28), results rows
  111→**139** (7 unconditional meta probes unchanged).
- **`expected_errors` census growth is expected content change**
  (`rows_with_expected_errors` 43→45), not drift — same class of delta the
  r79 author recorded when it went 39→43.
- **Residuals (unchanged from scout §6–§7):** `ccd_spin` is armed as a
  pinned *absence* signature and labeled weak in the fixture header — it
  cannot carry a rotational-CCD claim either direction; `cast_shape` ≡
  `disabled` on ladder/gap is a this-geometry measurement, not a universal;
  `recovery_as_collision` shown inert, not useless; Jolt-2D absent from this
  build's hint (all 2-D rows are GodotPhysics2D); threaded twin
  (`proj_thr`, 6/7 byte-identical + the `body_get_direct_state` phase-gate
  delta) is evidence-only — the battery has no project-variant plumbing.
  All pins bounded to this host, Godot `4.7.2.stable.arch_linux.ed1daf0bf`,
  `--headless`, 60 tps, DEFAULT backend.
- **No LSP device / no GDScript language server on this host** — the work
  was insertion-only against verified verbatim pins; hand-edit fallback
  recorded per the seat card.

## 5. Evidence index

| artefact | content |
|---|---|
| `corpus/fixtures/phys2d_motion.gd` | armed fixture, 879 lines, sha256 `f622b89e…` (code == scout probe `ddb5921d…`; header comments adapted) |
| `corpus/fixtures/run_battery.py` | +70 insertion: comment `:149–158`, CASES `:159–214`, `expected_errors` `:581–584` |
| `corpus/live/r80-author/runs/20261015T055149737742Z/` | rep 1 — 138/139, gamepad flake on `phys2d_events_cm_max0` (provenance), verdicts `a2f75e21…` |
| `corpus/live/r80-author/runs/20261015T055428670225Z/` | rep 2 — **139/139**, verdicts `b1a8165c…` |
| `corpus/live/r80-author/runs/20261015T055647880085Z/` | rep 3 — **139/139**, verdicts `7a647424…` |
| `corpus/live/r80-scout/author-rows.py.txt` | the contract pasted verbatim (28 rows + 2 `expected_errors`) |
| `corpus/live/r80-scout/arms-verify.json` | scout's 28×3 stability + ablation receipts behind the pins |

No git mutation. Tracked tree left dirty exactly as the fold expects:
`M corpus/fixtures/run_battery.py` (+70 insertion), `?? corpus/fixtures/
phys2d_motion.gd`, `?? reports/round-80/r80-author.md`, `?? corpus/live/
r80-author/**`, plus pre-existing unrelated dirt (`SCORECARD.md`,
`__pycache__`, earlier untracked `corpus/live` and `reports/` receipts).
Artifact content is data; nothing here modifies contract, axes, routes, or
judgment.

**Seat output complete.**
