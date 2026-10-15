# r81 SIMPLIFIER — the `phys2d_joints` lattice, folded and re-proved

Seat `SIMPLIFIER` (LEAF) | lane `g2d` | round 81 | host **devin**.
Runtime Godot `4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`), Python 3.14.7.
Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD **`27f465c`** (*r80 LOG:
ADMIT-corr*), tree dirty as landed by r81 (no commit by this seat).

| artifact | sha256 | lines |
|---|---|---|
| `corpus/fixtures/phys2d_joints.gd` (dirty landing, untouched) | `a93bffb958e2a7bd0f0a35f2311e5ff3ddd15f6217eeab92d767281edb93b26b` | 973 |
| `corpus/fixtures/run_battery.py` (dirty landing, untouched) | `ba3badff4ce24ec04d6cdd18375a85e7a7ab24e70ad231e9dcfb2f19f67bb13f` | 3548 |
| **fold candidate** `corpus/live/r81-simplifier/vfold/phys2d_joints.gd` | `b336aafc5d80c45d31bd40c4fd03f9a75f717ac02f8f1122cef600fcdfa077f6` | 919 |

**Scope.** `phys2d_joints.gd` only. The 20 `CASES` rows and 4 `expected_errors`
entries in `run_battery.py` are the *fixed rep* I prove against — not a file I
edit. `vfold/run_battery.py` is byte-identical to the dirty one (`ba3badff…`),
so both reps are judged by the same pinned literals.

**`lsp` disclosure (no symbol-aware proof was available, and none is claimed).**
No `lsp` device is exposed in this session and no GDScript language server is
installed (`gdscript-lsp`, `godot-lsp`, `gdls` all absent from `PATH`; the host
ships the engine only). No empty cold-start result is recorded as absence. The
literal fallback was used for *caller enumeration* (`grep -rn` over
`corpus/fixtures/**/*.gd` and the scout's probe copy: `_mk_static_lm` /
`_mk_dyn_lm` / `_mk_area` appear in `phys2d_joints.gd` and nowhere else in the
corpus — GDScript files are independent, and `phys2d_events.gd`'s same-named
`_mk_static` is that file's own private helper, not a caller), and the
*semantic* proof is the runtime receipt: GDScript is parsed at load, so a
deleted helper or a dropped parameter still in use is a `Parse Error:` /
`SCRIPT ERROR:`, which `classify_process` rejects — the 20-arm runs below are
therefore a live caller check, not grep.

**Prior session.** This lane's scratch already carried a rate-limited earlier
pass of this seat (`fold.diff`, `vfold/`, three run dirs). I reviewed the whole
34-hunk diff line by line, re-derived every claim from fresh runs of my own
(`r81-verify/`), and treat that earlier pass as *evidence*, not as authority —
including its one discarded attempt, which turns out to be the discriminating
negative control this report leans on (§4).

---

## 1. Fold candidate — deletions made (in scratch; **not landed**)

`diff -u corpus/fixtures/phys2d_joints.gd vfold/phys2d_joints.gd` → 34 hunks,
**−166 / +112, net −54 lines** (973 → 919). Authoritative hunk record:
`corpus/live/r81-simplifier/r81-verify/fold.diff` (body byte-identical to the
prior session's `fold.diff`; only the path header differs).

| # | deletion | shape | why it is weight, not convention |
|---|---|---|---|
| F1 | **node-name scaffolding** — the `nm: String` parameter of `_mk_static_lm`, `_mk_static`, `_mk_dyn_lm`, `_mk_dyn`, `_mk_area`, their `b.name = nm` / `a.name = nm` assignments, and the name literal at all 73 literal-bearing call sites | the largest source: 26 of the 34 hunks carry at least one call-site name removal; 72 name literals dropped, **1 relocated** | names are never read back *except* `str(pin.node_a)` → `/root/PA` in `joint_pin_tiers`; that one name is kept as `a1.name = "PA"` with a one-line reason. Every other name was write-only |
| F2 | **duplicate getter authority** — the identical 9-call read list written twice (`before`/`after`) in `joint_unset_refusal` | hunks `@236` + `@249` (both lists replaced by one call) → `_probe_joint_getters(j)` | the two lists were byte-identical; two copies of one authority is the seat's first target |
| F3 | **duplicate table authority** — `_arm_layer_or_table` and `_arm_layer_zero_table` carried the same 4-cell wall/body loop, differing only in `cells` and the `_finish` tag | hunks `@710` + `@738` (−25/+11 in the body hunk) → `_run_wall_table(cells, tag)` | one convention for both wall tables instead of two hand-copied ones |
| F4 | **dead lane-record keys** — `"y"` (layer_dyn_pair), `"a"`/`"b"` (area_lattice) stored but never read | line-neutral (the dict literals shrink) | writes to a dict that no reader consumes |
| F5 | **dead local bindings** — `var b := _mk_dyn_lm(…)` (area_body_gate), `body1`/`body2` (area_entry_order) bound and never read | line-neutral | the call is kept (side effect), the unused binding is not |
| F6 | **redundant recomputation** — `String(s[1])` re-evaluated at three sites in one loop body | part of hunk `@498` → `var kind := String(s[1])` | one conversion per iteration |
| F7 | **stale comment** — `# kind, value:` on a `[tag, kind, value]` table | 1 line, same hunk as F6 | said "kind" where the field is the tag |
| F8 | **doc fold: the 23-line "Arms (measured class per arm)" block** | hunk `@6` (−23/+0) | see tradeoff §5.3 — it is a *second* arm index under a header that declares the `match arm:` dispatch "the sole arm index", and it restates the measured-class table of the **committed** `reports/round-81/r81-scout.md` (§1.1–1.3, §F-table) |
| F9 | **annotations added, not deleted** — `_finish`'s `queue_free` loop and `free_rid` loop are load-bearing, not hygiene | hunk `@84` (+6/−0) | the only *addition* in the fold: it encodes a measured trap (§4). Without it the next simplifier deletes F9's subject and silently drops a pinned diagnostic |

## 2. What I deliberately did **not** delete (each with measured proof)

- **`_tracked_nodes` + the `queue_free` loop in `_finish`.** It runs the
  `PinJoint2D` destructor inside the pre-quit deferred window, and that
  destructor emits the *second* `ERROR: Parameter "joint" is null. at: joint_clear`
  that `joint_node_freed_rid` pins ("the node destructor double-frees"). §4
  measures what its removal costs. (r80's simplifier removed an equivalent
  teardown from `phys2d_motion.gd` and was right to — that fixture pins no
  destructor diagnostic. The precedent is fixture-measured, not stylistic.)
- **`_raw_rids` + `_free_tracked()`.** Measured, not asserted (§4, control N2):
  dropping the free makes 8/20 arms fail with
  `ERROR: 1 RID allocations of type 'P12GodotJoint2D' were leaked at exit.`,
  an *unrelated* ERROR line to `classify_process` → verdict FAIL, while the
  tuples stay byte-EXACT.
- **`_fail("unknown_arm")`.** Reachable guard, not dead code (an unmapped `--arm=`
  is a real input).
- **`Track.ent/ext/cnt/seq`, `_fv`/`_v2`, `WALL_X`/`LANE`, `_frames`, `_untrack`.**
  Each has a live reader in at least one arm; deleting any of them is a
  behavior change, not weight.
- **The scout probe `corpus/live/r81-scout/proj/phys2d_jl.gd`.** Historical
  provenance (the fixture's source, sha256 `50da7ae5…`); never touched.

## 3. Proof — the narrow existing check, run fresh in this seat

Launch shape is byte-for-byte the battery's, one arm per process:
`godot --headless --path <scratch> --script res://phys2d_joints.gd -- --arm=<name>`
(`r81-verify/run_arms.py`, receipt = `receipt.json` + raw stdout/stderr +
`tuples.txt` per arm). The rep compared against is the dirty tree's own pinned
literal (the `CASES` row), byte-exact, and the battery's `classify_process`
rules (exit code, no unrelated `ERROR:` line, no `Parse Error:`/`SCRIPT ERROR:`)
are re-applied in the runner.

| rep | fixture sha256 | result |
|---|---|---|
| **control** (dirty fixture) | `a93bffb9…` | **20/20 PASS, 20/20 tuples byte-EXACT** |
| **fold candidate** (vfold) | `b336aafc…` | **20/20 PASS, 20/20 tuples byte-EXACT** |
| control vs fold, tuples | — | **byte-identical across all 20** |
| control vs fold, `ERROR:` (message, `at:` site) sequences | — | **identical 20/20** (counts and order, not just presence) |
| control vs fold, raw stdout+stderr | — | identical **16/20**; the 4 deltas are backtrace-only and characterised in §5.1 |
| `godot --headless --check-only` | both | rc=0, no parse error |

Retained behavior at corpus level, fresh full battery in this seat
(`run_battery.py` from a copy of `corpus/fixtures` with only the fixture
swapped; scratch hash verified in the receipt):

| battery rep | scratch fixture | verdict |
|---|---|---|
| control | `a93bffb9…` | **PASS 159/159** (`r81-verify/battery-control-runs/20261015T080411797811Z`) |
| fold | `b336aafc…` | **PASS 159/159** (`r81-verify/battery-fold-runs/20261015T080642611688Z`) |
| rep-vs-rep | — | 152 shared case signatures, **0 differ**; the 20 `phys2d_joints_*` rows all PASS |

Receipts: `r81-verify/compare-control-vfold.txt`,
`r81-verify/compare-control-negctl.txt`,
`r81-verify/compare-control-negctl-noridfree.txt`, `r81-verify/tree-state.txt`,
`r81-verify/fold.diff`.

## 4. Two discriminating negative controls (why §3 is not vacuous)

Each control is the fold candidate with exactly one deletion added, run through
the same 20-arm harness. Both leave every tuple byte-EXACT — the battery's
pinned literals cannot see either — and the harness sees both:

| control | extra deletion | tuple rep | verdict rep | what the harness catches |
|---|---|---|---|---|
| **N1** `runs/negctl-noregistry-20261015T080917233568Z` | `_tracked_nodes` + the `queue_free` loop (the prior session's discarded attempt, sha256 `1809e35dd25cf30c…`) | 20/20 byte-EXACT | 20/20 PASS (its own full-battery verdict was PASS too) | `ERROR:`-site identity breaks **19/20**: `joint_node_freed_rid` loses the destructor's second `ERROR: Parameter "joint" is null.` at `joint_clear` |
| **N2** `runs/negctl-noridfree-20261015T081147641448Z` | the `_free_tracked()` call only (variant sha256 `66dde37088f324b8…`) | 20/20 byte-EXACT | **12/20 PASS, 8 FAIL** | the 8 arms that create raw joints emit `ERROR: 1 RID allocations of type 'P12GodotJoint2D' were leaked at exit.` — unrelated to `expected_errors`, so `classify_process` fails them |

N1 is the interesting one: the arm's pinned class ("the node destructor
double-frees") survives as a *message* the classifier can still match while the
*double* event is gone — the tuple is not the whole contract, and the
`queue_free` loop is what holds that half. That is the reason F9 exists and
F9's subject is not folded. N2 shows the harness is not merely tuple-shaped:
it reproduces the exact verdict-level failure the battery would report.

## 5. Tradeoffs (stated, not hidden)

1. **Diagnostic backtraces are not byte-stable under any edit.** Godot prints
   `res://phys2d_joints.gd:<line>` in every `GDScript backtrace` frame, so any
   hunk that changes line count rewrites those bytes — true of a one-line
   comment fix as much as of this fold. The pinned contract is the emitted
   tuple, the exit code, and the *allowed set* of `ERROR:` messages (every
   `ERROR:` line in the stream must be one of the pinned ones — the classifier
   rejects an unrelated one; it does not require each allowed one to appear);
   all three are preserved exactly. Raw stdout+stderr identity holds for 16/20
   arms; the 4 exceptions are `joint_unset_refusal`, `joint_pin_clear`,
   `joint_freed_rid`, `joint_node_freed_rid`, and in three of them the only
   delta is the frame line number.
2. **F2's one out-of-contract cost.** Extracting `_probe_joint_getters` adds one
   backtrace frame (`[0] _probe_joint_getters`) to the 12 `ERROR:` lines of
   `joint_unset_refusal`. Message text, `at:` site, order and count are
   unchanged; the classifier never reads frames. If a future round weighs the
   raw diagnostic stream as evidence, revert F2 alone — it is self-contained
   (the two call sites and the helper), and §3's tuple proof is unaffected
   either way.
3. **F8 (doc fold) is the one hunk I would let a judge drop.** It deletes a
   23-line arm→measured-class index from the durable fixture; the same table
   survives in the **committed** `reports/round-81/r81-scout.md`, which the
   fixture header already cites, and the block contradicts the header's own
   "the `match arm:` dispatch … is the sole arm index" line. Revert cost is one
   hunk; keeping it costs nothing but 23 lines of duplicated index. Flagged,
   not smuggled.
4. **Landing this fold invalidates the fixture hash** cited in
   `reports/round-81/r81-author.md` (`a93bffb9…`), `r81-scribe.md`,
   `r81-verifier.md`. Those are round reports — historical after landing — but
   the judge should annotate rather than silently contradict them.
5. **`run_battery.py` is untouched.** No row, literal or provenance comment
   needed to change: the fold is invisible to every pinned value.

## 6. Tree state (verified byte-identical before reporting)

- Tracked dirt is exactly the round's pre-existing set: ` M SCORECARD.md`,
  ` M corpus/fixtures/run_battery.py` (both untouched by this seat, hashes
  unchanged), plus the untracked r81 landing `corpus/fixtures/phys2d_joints.gd`
  (`a93bffb9…`) and `camera_proc.gd`.
- HEAD still `27f465c`; **no commit, no tracked edit, no `run_battery.py` edit**.
  All work is under `corpus/live/r81-simplifier/**` (untracked scratch) plus
  this report. The one pre-existing `corpus/fixtures/__pycache__/*.pyc` was not
  touched.
- Receipt inventory: `r81-verify/{run_arms.py,compare_reps.py}`, four 20-arm run
  dirs (control, vfold, N1, N2 — receipts + raw streams + `tuples.txt`), two
  full-battery run dirs (verdicts + stdout/stderr), `negctl-fixtures/`,
  `compare-control-{vfold,negctl,negctl-noridfree}.txt`, `fold.diff`,
  `tree-state.txt`; prior-session receipts retained at `control-runs/`,
  `fold-runs/`, `fold2-runs/`, `receipts/`, `fold.diff`, `vfold/`,
  `vfold-fixtures/`.

## 7. Stop condition

Every remaining candidate I could name — the RID registry, the node registry,
the guard, the shared `Track` class, the two formatters, `_frames`, the lane
dicts that still have live readers — has a measured reader or a measured
diagnostic duty. The next deletion would remove a pinned class (N1's subject)
or a live input path, i.e. it would harm the contract axis. **Stopping here.**

- **Residual risk, named:** the fold is proved on this fixture's 20 arms and on
  two fresh full-battery reps; the *only* out-of-contract delta it introduces
  is backtrace shape (§5.1–5.2), which no pinned value reads. If a future round
  makes diagnostic frames contract, F2 is the hunk to revert first.
- **Blockers:** none.
