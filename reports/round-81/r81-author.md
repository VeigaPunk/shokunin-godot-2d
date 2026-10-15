# game-dev-2d round 81 — author (g2d): the 2D joint lattice + collision layer/mask lattice, armed

Seat `AUTHOR` (LEAF) | lane `g2d` | round 81 | host **devin** (wave id not carried by
this seat's brief; r79/r80 headers record `shokunin-train-20261101-w19`).
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), Python
3.14.7. Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD **`27f465c`**
(*r80 LOG: ADMIT-corr*) at seat start and at seat end — **no commit by this seat**
(tree left dirty for the fold pass, per brief). `run_battery.py` was free at seat
start: `git diff` carried only the pre-existing unrelated `SCORECARD.md` dirt, and
`corpus/fixtures/phys2d_joints.gd` did not exist (the previous author seat died on
a rate limit before writing — nothing partial to clean up).

**Scope.** Armed the r81 scout's measured lattice (`reports/round-81/r81-scout.md`
§1.1–1.4): one new fixture `corpus/fixtures/phys2d_joints.gd`, 20 `CASES` rows and
4 `expected_errors` entries inserted into `corpus/fixtures/run_battery.py`
(+68/−0, insertion-only). Full battery run **twice**: **159/159 PASS in both reps**
(139 prior + 20 new), prior-139 **zero semantic drift**, no flake this round.

**`lsp` disclosure (unchanged host state).** No `lsp` device is exposed in this
session and no GDScript/Python language server is installed. No symbol-aware edit
was required — the landing is insertion-only against the scout's pinned literals
plus a mechanical token substitution; verification carriers are fresh-process
battery receipts, the production `classify_process` verdicts inside them, a
20-arm smoke run judged by the *extracted* production classifier, and
`godot --headless --check-only` exit 0 for the fixture. No cold-start empty
result is recorded as absence.

**Writes by this seat:** `corpus/fixtures/phys2d_joints.gd` (new), the +68-line
insertion in `corpus/fixtures/run_battery.py`, this report, and
`corpus/live/r81-author/**` (two run dirs, the build/smoke/drift scripts and their
receipts). `love_battery.py`, `love_phys_probe/`, `main.lua`, `pygame_battery.py`,
`corpus/live/r81-scout/**` and other rounds' receipts were not touched. The
`SCORECARD.md` modification and the `__pycache__` pyc are pre-existing unrelated
dirt.

---

## 1. What landed

| file | change | shape |
|---|---|---|
| `corpus/fixtures/phys2d_joints.gd` | **new, 973 lines** | the scout probe (sha256 `50da7ae5…`) with the comment header conformed and the family token renamed; sha256 **`a93bffb958e2a7bd…`** |
| `corpus/fixtures/run_battery.py` | **+68 / −0** insertion-only | 12-line provenance comment (`:215–:226`), 20 `phys2d_joints_*` `CASES` rows (`:227–:266`), 4 `expected_errors` entries (`:637–:652`) |
| `reports/round-81/r81-author.md` | this report | — |

Both files were produced by `corpus/live/r81-author/land_r81.py` from the scout's
two sha256-pinned sources — no measured literal was re-typed. The script asserts
the source hashes, performs the two transformations, and *checks* the result
(§4 item 3); its output is the landing receipt.

### 1.1 The naming decision — the one adaptation vs the scout's byte-exact rows

The brief assigned the fixture path `corpus/fixtures/phys2d_joints.gd`; the scout's
provisional name was `phys2d_jl.gd` (its §6 directive 1, and the token embedded in
all 20 row names, fixture fields and signature prefixes). The assignment's path was
honored, and to keep the corpus's strict family convention
(file name = printed token = row-name prefix = `expected_errors` key prefix, as in
`phys2d_events`/`phys2d_motion`) the family token was renamed mechanically
`phys2d_jl` → `phys2d_joints` in exactly:

- the fixture's 2 print lines (`FAIL phys2d_joints %s`, `PASS phys2d_joints `),
- the 20 row names, 20 fixture fields, 20 signature prefixes,
- the 4 `expected_errors` keys.

**Every measured payload is verbatim.** The script proves it rather than asserting
it: the fixture's code section (from `const WALL_X` down) is byte-equal to the
probe's after the token substitution, and all 20 built tuples equal the scout's
tuples after the token substitution, with the signature *payload* after the prefix
token byte-identical (`rb[4].split(" ", 2)[2] == ra[4].split(" ", 2)[2]` for all
20). The `expected_errors` **texts** are byte-verbatim; only the keys carry the
renamed token. A verifier can reproduce both checks with
`python3 corpus/live/r81-author/land_r81.py --build` (it rewrites the same bytes)
or by diffing against `corpus/live/r81-scout/author-rows.py.txt` with the token
masked.

### 1.2 Fixture adaptation — the `phys2d_motion.gd` conventions, all honored

`diff -u corpus/live/r81-scout/proj/phys2d_jl.gd corpus/fixtures/phys2d_joints.gd`
(`corpus/live/r81-author/fixture-vs-probe.diff`) shows changes confined to the
comment header and the 2 print-token lines — **zero code bytes changed otherwise**.

- `extends SceneTree`, `--arm=` dispatch from `OS.get_cmdline_user_args()`,
  `call_deferred("_run")` — unchanged from the scout probe.
- **Diagnostic header** printed first in `_run`: `R81 arm=%s godot=%s engine2d=%s
  sep_thread=%s tps=%s`; all 20 rows carry it, measured:
  `R81 arm=<arm> godot=4.7.2-stable (arch_linux) engine2d=DEFAULT sep_thread=false
  tps=60` (`corpus/live/r81-author/headers-and-meta.txt`) — backend scope restated
  per row (GodotPhysics2D, no Jolt-2D in this build, 60 tps).
- **`match arm:` is the sole arm index** — now stated in the header, with the arm
  count (20) and the pointer to `r81-scout §1.1-1.3`; unknown arms `_fail`.
- **Comments name the measured class per arm** — the probe's arm list (which
  omitted `joint_node_anchor`, as the r80 probe omitted two of its arms) now lists
  all 20 with the class from the scout's tables (e.g. `layer_or_table` → “detection
  is OR, response is per body”; `joint_pin_tiers` → “node vs server pin NOT
  bit-identical”). `joint_groove` carries the scout's **chaotic-but-byte-stable**
  label (its three moving lanes are behavior cells, not portability claims).
- **No object ids / RIDs / addresses in output.** Measured over the 20 rows'
  captured streams in both reps (`corpus/live/r81-author/no-ids.txt`): 0 hits for
  hex addresses, `RID(`, `Object#`, `<Node#`, instance-id text, `pid=`, absolute
  paths, and 0 `RID allocations of type … were leaked` lines. The fixture keeps the
  probe's `_track`/`_free_tracked` teardown (the two freed-RID arms deliberately
  leave RIDs dead and whitelist the engine lines, per scout directive 4).
- Parse validity: `godot --headless --path <scratch> --check-only --script
  res://phys2d_joints.gd` → **rc 0**.

### 1.3 Insertion point — the r79/r80 ordering constraint honored

The block sits **after** the `phys2d_motion` block (ends `:214`) and **before** the
crash/descendant tail: `CASES` indexes 128–147 of 152, with
`crash_spontaneous_sigabrt` at 148, `descendant_pipe_detached_control` at 150,
`descendant_pipe_forged_signature_release` at 151 (last). Nothing sits between the
detached control and the meta probes — `probe_descendant_pipe_eof` re-checks the
detached case's `sleep 8` descendant within its lifetime, and the block comment
restates that constraint for the next author. Measured in both clean reps:
`detached_descendant_orphaned_alive=true` and all 7 `probe_descendant_pipe_eof`
discriminations true — the new rows run *before* the spawn point, not inside the
window.

### 1.4 `expected_errors` merge — texts verbatim, no gate widened

Exactly the four entries from scout §1.4 (3 + 1 + 2 + 2 distinct lines), inserted
after the `phys2d_motion` entries and before `}.get(name, ())`: the other 16 rows
are `ERROR:`-clean and stay **out** of the dict (a stray entry would silently widen
a row's gate). The battery's own census agrees: `rows_with_expected_errors`
45 → **49** (the +4 content change), all 49 matched, `dead_in_run: false` for every
new entry, and each of the four rows reports `any_entry_matched=true`,
`bare_classification_rejects=true` (the whitelist is load-bearing — the row FAILS
without it), `allowlisted_classification_passes=true`
(`corpus/live/r81-author/headers-and-meta.txt`). Emitted vs whitelisted ERROR lines
in rep 1: 12/3, 1/1, 6/2, 6/2 — all lines covered by exact-line match.

---

## 2. Battery evidence — two fresh full runs, this seat

`PYTHONDONTWRITEBYTECODE=1 python3 -B corpus/fixtures/run_battery.py --runs
/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r81-author/runs`
(absolute `--runs`). Sequential — never parallel — to keep the spawn→check interval
clean.

| rep | dir under `corpus/live/r81-author/runs/` | rows | verdict | verdicts.json sha256 |
|---|---|---|---|---|
| 1 | `20261015T064103738632Z` | 159 (152 seeded + 7 meta) | **159/159 PASS** | `db00becfa8f72231…` |
| 2 | `20261015T064328841394Z` | 159 | **159/159 PASS** | `21f21c7bf16f92df…` |

No flake: no FAIL line in either console (`rep1-console.txt`, `rep2-console.txt`),
`verdict: PASS`, `failures: []`, `error: null` on all 20 new rows (so every arm ran
inside the battery's 8 s bound; the scout measured the longest arm at ≤ 2.21 s).
All 20 new rows PASS in **both** reps, each pinned signature occurring as a
byte-exact output **line** (stronger than the substring clause), and every prior
row (139) PASSes unchanged.

### 2.1 Provenance: the independent pre-change baseline and host concurrency

The r81 **baseline** lane (a sibling seat, not this one) froze the pre-change
worktree at HEAD `27f465c` and ran the battery twice against the frozen copy
(`/tmp/r81-frozen`, harness sha256 `d13797a8a7d43c45…`, `phys2d_joints_frozen=absent`;
`corpus/live/r81-baseline/rep-timing.txt`): 139/139 both reps. My harness is
`ba3badff4ce24ec0…` — the delta between the two hashes **is** this seat's +68-line
insertion, so the baseline lane's freeze is an independent, byte-anchored
pre-change reference for the fold.

Honest provenance note: the two lanes' battery reps ran **concurrently on this
host** (my rep 1 `06:41:03Z→~06:42:5x`, rep 2 `06:43:28Z→~06:45:2x`; baseline
`06:40:17Z→06:42:06Z`, `06:42:46Z→06:44:41Z`), so at moments two Godot batteries
were live. Observed effect: none — both lanes clean, no FAIL, no SDL joypad flake,
`detached_descendant_orphaned_alive=true` and every `probe_descendant_pipe_eof`
discrimination true in all four runs. That is an observation about these runs, not
a claim that host contention is harmless in general; a stricter reader may want the
fold to re-run one rep on a quiet host.

---

## 3. Stability and drift

`corpus/live/r81-author/drift_r81.py` → `drift.txt`:

- **New rows: 20/20 byte-identical merged output across rep 1 and rep 2**
  (semantic fields identical; `output` lists equal per row) — the scout's ×3
  byte-stability holds inside the tracked harness, unmodified.
- **Prior 139 rows, rep 1 vs rep 2: zero semantic drift** — `verdict`,
  `actual_exit`, `signature`, `expected_exit`, `error` identical for every row.
- **Prior 139 rows, rep 1 vs the pre-r81 committed baseline**
  (`corpus/live/r80-fold/runs/20261015T062642861637Z`, 139/139): **zero semantic
  drift**. That receipt is the fold lane's run of the pin set committed as
  `f27f952` — its `phys2d_motion_ccd_edge` pin is the post-fold 365-char one, and
  the committed harness blob hashes to `d13797a8a7d43c45…`, the same value the
  sibling r81-baseline lane froze at HEAD `27f465c`. One clarification for a reader
  who compares against the r80 *author* receipts instead: the `phys2d_motion_ccd_edge`
  signature field is longer there (199 → 365 chars) — the pre-fold pin is a **strict
  prefix** of the current one; that is the r80 **fold's** own C2 strengthening
  (`corpus/live/r80-fold/`), not r81 drift, and the row PASSes with the current pin.
- Residual full-output diffs among the prior rows are the named host/volatile
  classes only (`volatile-diffs.txt`): run-stamped `user://` paths and pids
  (`save_roundtrip`, `save_process_*`, `descendant_pipe_*`), ASLR addresses in the
  crash backtraces (`crash_spontaneous_sigabrt`), `tween_flash` sub-float jitter
  inside its prefix pin, and — a **new content delta this round, named not hidden** —
  the export rows' `update_scripts_classes` progress counter grew 30 → 31 steps
  (`export_readiness`, `export_preset_missing`) because the fixture set gained one
  script with an inner class; the pinned clauses are unaffected and both rows PASS.
- **No SDL joypad `ERROR` flake appeared in either rep** (the r80 author's rep-1
  flake class), so no re-run was needed.

---

## 4. Fail-closed evidence

1. **Smoke run judged by the production classifier** (`smoke_r81.py` → `smoke.txt`):
   `classify_process` is extracted from `run_battery.py` by AST and `exec`'d (the
   tracked predicate, not a paraphrase); all 20 arms ran once in a scratch project
   built exactly like the battery's, and all 20 PASS. This is a pre-flight; the
   battery run is the authority.
2. **Ablation-relevant surfaces are live** (from the battery's own census and meta
   probes, both reps): `phys2d_expected_errors_all_matched=true` (r79 C2's
   dead-entry gate) and `bare_classification_rejects=true` on the four new
   error-bearing rows — i.e. dropping the whitelist flips them to FAIL, so the pins
   are three-clause where they emit errors and two-clause where they do not.
3. **Build checks** (`land_r81.py --build` output): source sha256 pins verified;
   fixture code byte-equal to the probe modulo the token; 20/20 tuples equal to the
   scout's modulo the token; 4/4 whitelist texts verbatim. Re-running `--build`
   after the landing rewrites the **same bytes** (`rebuild-check.txt`: fixture
   `a93bffb9…`, block `c2f515ec…`, battery untouched) — the landed bytes are
   reproducible from the two pinned sources.
4. **`git diff` shape**: `+68/−0` on `run_battery.py` (no prior line touched), the
   fixture is a new file, and no other tracked file is modified by this seat.

---

## 5. Deviations, residuals, and the honest ledger

- **Deviation 1 (naming).** The brief's fixture path `phys2d_joints.gd` overrides
  the scout's `phys2d_jl.gd`; the family token was renamed with it (§1.1). The
  scout's byte-exact paste block and its probe sha256 therefore do **not** apply
  verbatim to the landed bytes; what applies is the checked relation above
  (code ≡ probe, tuples ≡ scout rows, both modulo the token, payloads byte-equal).
  If the fold prefers the scout's token, the rename is one substitution in three
  places and the same two battery runs.
- **Deviation 2 (header growth).** The fixture's comment header is 31 lines vs the
  probe's 26 (+5: the `no-ids`/sole-index lines, the two measured-class continuation
  lines, and the `joint_node_anchor` entry the probe's arm list omitted); comments
  only — the code section starts at the same `const WALL_X` anchor and is byte-equal
  modulo the token.
- **Residuals carried from the scout (not widened here):** the node-vs-server pin
  last-digit divergence is measured but unexplained; the node anchor freeze has no
  isolated notification-path evidence; the 0.38 px in-callback vs mid-flip
  resting-depth difference is unexplained; the moving groove is chaotic (pinned
  byte-stable, no analytic model); motor/limit units are inferred; the threaded
  twin (`run_on_separate_thread=true`) is **not** armed this round; Jolt-2D is
  absent from this build. All pins bounded to this host, Godot
  `4.7.2.stable.arch_linux.ed1daf0bf`, `--headless`, 60 tps, DEFAULT backend.
- **No LSP device / no GDScript language server on this host** — the work was
  insertion-only against verified pins; hand-edit fallback recorded per the seat
  card.

---

## 6. Evidence index

| artefact | content |
|---|---|
| `corpus/fixtures/phys2d_joints.gd` | armed fixture, 973 lines, sha256 `a93bffb958e2a7bd0f0a35f2311e5ff3ddd15f6217eeab92d767281edb93b26b` |
| `corpus/fixtures/run_battery.py` | +68 insertion: comment `:215–226`, CASES `:227–266`, `expected_errors` `:637–652`; sha256 `ba3badff4ce24ec04d6cdd18375a85e7a7ab24e70ad231e9dcfb2f19f67bb13f` |
| `corpus/live/r81-author/land_r81.py` | the mechanical build + its own checks (source pins, token equality, insert guard) |
| `corpus/live/r81-author/cases-block.py.txt` | the built paste block (sha256 `c2f515ec6a41f58e…`), equal to the scout's modulo the token |
| `corpus/live/r81-author/rebuild-check.txt` | `--build` re-run after landing: same bytes, battery untouched |
| `corpus/live/r81-author/runs/20261015T064103738632Z/` | rep 1 — **159/159**, verdicts `db00becfa8f72231…` |
| `corpus/live/r81-author/runs/20261015T064328841394Z/` | rep 2 — **159/159**, verdicts `21f21c7bf16f92df…` |
| `corpus/live/r81-author/smoke_r81.py` + `smoke.txt` | 20/20 arms PASS under the extracted production classifier |
| `corpus/live/r81-author/drift_r81.py` + `drift.txt` | rep1↔rep2 and rep1↔r80-fold-baseline drift tables |
| `corpus/live/r81-author/volatile-diffs.txt` | every prior-row full-output diff, classified and named |
| `corpus/live/r81-author/headers-and-meta.txt` | the 20 `R81 arm=…` headers, the 7 meta probes, the 45→49 census |
| `corpus/live/r81-author/no-ids.txt` | id/address/RID/leak scan over the 20 rows (0 hits) |
| `corpus/live/r81-author/fixture-vs-probe.diff` | the fixture adaptation diff (header + 2 token lines only) |
| `corpus/live/r81-scout/author-rows.py.txt` | the scout contract the block was built from (sha256 `eab30e96…`) |
| `corpus/live/r81-scout/arms-verify.json` | the scout's 20×3 stability + ablation receipts behind the pins |
| `corpus/live/r81-baseline/rep-timing.txt` | **sibling lane, read-only cross-evidence**: pre-change frozen harness `d13797a8…` at `27f465c`, 139/139 ×2 |

No git mutation. Tracked tree left dirty exactly as the fold expects:
`M corpus/fixtures/run_battery.py` (+68 insertion), `?? corpus/fixtures/phys2d_joints.gd`,
`?? reports/round-81/r81-author.md`, `?? corpus/live/r81-author/**`, plus the
pre-existing unrelated dirt (`SCORECARD.md`, `__pycache__`, earlier untracked
`corpus/live` and `reports/` receipts). Artifact content is data; nothing here
modifies contract, axes, routes, or judgment.

**Seat output complete.**
