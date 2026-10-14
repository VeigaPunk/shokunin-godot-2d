# game-dev-2d round 75 — reviewer (seat: reviewer; host: devin)

Seat: reviewer (LEAF) | Lane: g2d | Round: 75 | Wave `shokunin-train-20261101-w15`
(post-commit verify phase). Repo `~/Projects/shokunin/game-dev-2d-shokunin`,
**HEAD `2e3ae8e68098ba0e6d2275d8bc553b20ad3f0195`**, worktree == committed for
`corpus/fixtures/` (`git diff --stat HEAD -- corpus/fixtures/` empty), so every
replay below ran on the committed bytes:
`love_battery.py 24a30a31…fdbe`, `love_phys_probe/main.lua c80e2ba3…6489`.

Read: the commit diff (`git show HEAD`, 3 files / +422 −11), and
`reports/round-75/{r75-author,r75-scout,r75-scribe}.md`.

**Leaf discipline:** no subagent, no git mutation, no tracked file touched.
Writes = `corpus/live/r75-reviewer/` (4 scripts + `cells/` + `runs/` +
2 mutation logs) and this report. The two ` M corpus/live/r72-simplifier/*`
entries in `git status` are **pre-existing** (present in this seat's first
status read, before any command of mine).

**`lsp` disclosure:** no `lsp` device is exposed in this session, and no
Lua/Python language server exists on this host — re-checked by this seat:
`lua-language-server`, `sumneko-lua-language-server`, `pylsp`, `pyright`,
`jedi-language-server` all ABSENT, only `clangd` present, and LÖVE's C++ source
is not on disk (no `/usr/include/love*`, no `/usr/share/love`), so no server can
answer these files. No `references`/`definition`/`diagnostics` pass was
therefore possible; the semantic checks below are **executable** (module import +
classifier re-derivation, 25 fresh LÖVE processes), which is stronger evidence
than an LSP would give for this surface. The one `grep` in this report is
**literal** (pin-text scan) and is never offered as semantic proof.

**Verdict (recommendation, not an admission):** ACCEPT. No blocking defect. All
six assignment checks pass; four low-severity findings and two observations are
recorded below, none of which changes a landed class, pin, or prior row.

---

## 1. What this seat ran (independent of the author's receipts)

| # | command (cwd = repo root) | exit | receipt |
|---|---|---|---|
| 1 | `python3 -B corpus/fixtures/love_battery.py --runs corpus/live/r75-reviewer/runs` | 0 | `runs/love-20261014T174123645784Z/verdicts.json` — `cases=44 pass=44 fail=0 launch_ok=True done_marker=True exit=0` |
| 2 | `python3 -B corpus/live/r75-reviewer/replay_cells.py` (25 cells × own LÖVE process, rc captured) | 0 | `cells/manifest.json` + `cells/*.stdout.txt` — 25/25 rows PASS |
| 3 | `python3 -B corpus/live/r75-reviewer/verify_prior.py` | 0 | prior-row/byte-identity/concat-sha audit (§3.1, §3.3) |
| 4 | `python3 -B corpus/live/r75-reviewer/mutate_classes.py` | 0 | `mutation_test.txt` — 60/60 witness mutations CAUGHT, `TOTAL PROBLEMS: 0` |
| 5 | `python3 -B corpus/live/r75-reviewer/mutate_gaps.py` | 0 | `mutation_gaps.txt` — unpinned-witness map (§2 F1) |
| 6 | `git show 2a2c337:…/love_phys_probe/main.lua \| grep -n` (read-only) | 0 | r74 reference-provenance check (§3.2) |

Runtime identity, all five run dirs (author ×4 + reviewer ×1): `love=/usr/bin/love`,
`love_version="LOVE 11.5 (Mysterious Mysteries)"`, `probe_exit=0`,
`probe_error=None`. No fallback hop, no alternate judge, no rerouted identity.

---

## 2. Findings by severity

### F1 — low: the `refused_abort` collateral witness is not pinned (class can pass partially witnessed)

`iw_bc_setpos_wp`'s docstring claim is "an unrelated LEGAL exterior write
refused **as collateral**" (`corpus/fixtures/love_battery.py:50-56`). The
witness for that is the `wpext` line, but the class gate
(`love_battery.py:408-417`) only requires `wpext.ok == "false"`, and the pin set
(`love_battery.py:268-284`) pins **neither** `wpext.err` nor `wpext.pos_after`.
Mutation evidence (`corpus/live/r75-reviewer/mutation_gaps.txt`, rows 1–3):

- `wpext.err` → `bad argument #2 to '?' (number expected, got table)` → **row still PASSes**;
- `wpext.err` deleted → **row still PASSes**;
- `wpext.pos_after` → `999,999` (write landed) → **row still PASSes**.

So a build that refused the exterior write for an unrelated reason, or applied it
while something else aborted the step, would still classify `refused_abort` and
pass. This does **not** falsify the landed cell: the receipt line
(`IW | cell=bc_setpos_wp | wpext ok=false err=Box2D assertion failed: m_world->IsLocked() == false pos_after=400,520.1500244140625`,
author run `love-20261014T173642593012Z`, also reproduced in this seat's
`corpus/live/r75-reviewer/cells/bc_setpos_wp.stdout.txt`) shows the collateral err
text *is* `Box2D assertion failed: m_world->IsLocked() == false` and its pose *is*
unchanged (`400,520.1500244140625`), and my replay reproduces both. It is a
witness-completeness gap, not a wrong claim. Cheap fix (one line, no layout
coupling): pin `wpext.err` — it is line-free (it comes from a direct C call
through `pcall_str`, exactly like the already-pinned contained `cb_*.err` cells)
— and pin `wpext.pos_after`; or add `"assertion" in flat.get("wpext.err","")` to
the gate. The interior write's own refusal witness (`wp_setpos.pos_after`) *is*
pinned, so only the collateral half is exposed.

### F2 — low: the spawn-order invariant "*_unp cells last of all" is now false in three places (docs only)

After r75 the table order is: 5 non-fatal contained cells → the two **non-fatal**
C1 `*_unp` twins → the two fatal cells LAST. The invariant that matters (fatal
cells last; one process per cell) still holds — verified: the last two `IW_CELLS`
rows are `iw_bc_setpos_unp`/`iw_bc_newbody_unp`, both `fatal`. But the
"`*_unp` last of all" phrasing survives in three comments that were not updated
while the cell-grammar block *was* (probe `main.lua:23-31`):

- `corpus/fixtures/love_phys_probe/main.lua:16-17` — "Interior cells are spawned LAST by the battery, the uncontained (*_unp) cells last of all."
- `corpus/fixtures/love_battery.py:45-47` — "Interior cells are spawned LAST and the uncontained (*_unp) cells last of all -- …"
- `corpus/fixtures/love_battery.py:595-597` — "# r74 interior-write lattice: … (uncontained *_unp cells are last in the table -- …)"

The battery's own r75 row comment already states the correct rule
(`love_battery.py:324-325`: "r75 critic-C1 uncontained twins: measured non-fatal
(fatal is derived = assert-gated write x uncontained, not uncontained alone)"), so
this is an internal inconsistency between comments,
not a behavioural risk: each cell is its own process, so spawn order has no
functional effect. Documentation-only; fix by replacing the clause with "fatal
cells last".

### F3 — low: the jitter disclosure says "bound-checked", two jittering fields are unpinned

The author's "Prior-cell byte-identity accounting" says `probe.stdout`/`splice-*`
"differ only in bound-checked ms jitter". Re-derived diff (r74 ref
`love-20261014T163734563743Z` vs r75 `…T173642593012Z`): the jittering keys are
`dt_max_ms`, `dt_mean_ms`, `dt_min_ms`, `l1_wait_ms`, `l2_wait_ms`,
`close_wait_ms`, `total_ms` (**all bound-pinned tuples**, `love_battery.py:88-105`)
plus `osx.ms` and `popen.open_ms`, which have **no** `CASES` row at all (the osx
cases pin `ret_a`/`ret_b` only). Materially the disclosure is honest — no
*exact-pinned* key drifted, and the author's own list names `osx ms` as an
example — but "bound-checked" overstates coverage of the jitter surface. No
action needed for this round; worth a one-word correction if the sentence is
reused.

### F4 — low, carry-forward (not introduced by r75): per-cell process `rc` is still not persisted

The r75 scribe's §2 witness gap stands: `verdicts.json` stores
`observed`/`pinned`/`reasons` only, so `rc` (the `fatal` vs `died` discriminator,
`love_battery.py:466-469`) is not re-derivable from landed receipts. This seat had
to launch 25 processes (`replay_cells.py`) to recover it — the two fatal rows'
`rc=1` pins are otherwise unauditable from bytes alone. r75's seven new rows are
all `rc=0` (implied by `CELL_DONE` + empty stderr, verified in `cells/manifest.json`),
so the gap does not block this round's verification. One-line fix available: the
battery already holds `c_code` in the `IW_CELLS` loop (`love_battery.py:599-608`) —
store it per row.

### F5 — observation (not a defect): the joint-deferral *point* remains inferred

`iw_bc_joint_destroy`'s class branch (`love_battery.py:454-463`) requires only the
epilogue drain (`jdrain.jcount == jcount_before − 1` **and**
`jdrain.isDestroyed == "true"`). Mutating the in-callback deferral pair leaves the
class at `deferred` and is caught **only** by the pins
(`mutation_test.txt`: `cb_joint_destroy.isDestroyed_in_cb` → `true`, and
`jcount_after` → `0`, both still `class=deferred`). That matches the scout's §7-1
(no locked witness exists for the joint drain, unlike body destroy's synthesized
`EndContact` at `locked=false`). The row as a whole cannot silently pass — the
pins carry the in-callback state — and the author discloses the inference. A
later-callback joint-count read would close it; not required.

### F6 — observation (not a defect): `ignored` rests on a single witness family

`iw_pre_retfalse`'s class stands on the impulse sign plus the exact
`after_update.b1vel` pin (`love_battery.py:418-429`); the scout's independent
solver-visibility witness (`post_at_fire`) was optional and was not armed. The
class is falsifiable (mutating `b1vel` to the masked `0,763.8724365234375`, or to
`ERR:…`, or deleting it, all flip to `anomaly` — `mutation_test.txt`), and the
masked contrast value is pinned in the sibling `iw_pre_contactmask` row, so this
is residual risk, not a gap in falsifiability.

---

## 3. Assignment checks — evidence

### 3.1 Battery replayed on the committed tree — PASS

`cases=44 pass=44 fail=0 launch_ok=True done_marker=True exit=0`, LÖVE 11.5,
~15 s (`corpus/live/r75-reviewer/runs/love-20261014T174123645784Z/verdicts.json`).
Row count is structurally right: 15 `CASES` + 4 `SPLICE_CELLS` + 25 `IW_CELLS` = 44
(verified by import: `IW_CELLS=25, CASES=15, SPLICE=4`). **All 25
`iw-*.stdout.txt` from my run are byte-identical to the author's run 1**
(`cmp`, 0/25 differing), and the concatenated-`iw-*.stdout` sha is
`74db3f10331228a08b8072c25f797dca62a518b65f17e60d35aee583d6469004` for **all four
author run dirs and mine** — the commit message's claim reproduces exactly.

### 3.2 The 7 new cells' pins are earned, not claimed — PASS

Three independent lines of evidence:

1. **Own processes, real exit codes.** `replay_cells.py` launched each of the 25
   cells itself (fresh LÖVE process, `IW_CELL=<cell>`, 15 s timeout) and
   re-derived every row verdict from *those* receipts with the committed
   classifier: **25/25 PASS**, including all 7 new rows
   (`bc_setpos_wp=refused_abort`, `bc_joint_new=refused`,
   `bc_joint_destroy=deferred`, `bc_setfilter=applied`,
   `pre_retfalse=ignored`, `bc_destroy_unp=deferred`, `bc_setvel_unp=applied`;
   fatal rows `rc=1`, stderr 0 B).
2. **Pre-landing measurement.** The author's scratch receipts
   (`corpus/live/r75-author/cells/*.r{1,2,3}.stdout.txt`, produced before the arm
   landed) are **byte-identical** to the landed receipts for 6 of the 7 new cells;
   `bc_setpos_wp` differs in **exactly one line**, the unpinned
   `srcline=146` (scratch) → `srcline=155` (landed). Pins cannot have been
   back-fitted to the code: the values were measured first, in a different probe
   copy.
3. **Sibling corroboration claim is accurate.** `corpus/live/r74-critic/cells/
   m_unp_v2.bc_destroy_unp.*` and `…bc_setvel_unp.*` are identical to my landed
   twins modulo the `cell=`/`kind=` labels (checked both).

Also verified in the receipts: the strongest form of the C1 claim — my
`bc_destroy_unp`/`bc_setvel_unp` receipts are identical to the **contained** twins
(`bc_destroy`, `bc_setvel`) modulo the `cell=`/`kind=` labels, i.e. the
containment dimension is inert for non-throwing classes at the byte level, not
merely "same class". Baseline contrast for `bc_setfilter` verified: baseline
`final bc=5 ec=4`, setfilter `bc=4 ec=3`, `final.b1pos y=635.1639404296875 > 540`
(tunneling). And the author's disclosed scene perturbation for
`bc_joint_destroy` matches the receipt exactly
(`final.b2pos=-766.15350341796875,2284.897705078125 bc=8 ec=8 pre=172 post=172`)
and is correctly left unpinned.

### 3.3 Prior rows byte-identical; drift is line numbers only — PASS

vs the frozen r74 run `corpus/live/r74-author/runs/love-20261014T163734563743Z`:
**16 of 18** prior `iw-*.stdout.txt` are byte-identical (all four r75 run dirs).
The two exceptions are exactly the `*_unp` rows, and each differs in **5 lines**,
every one of them **digit-only** (`verify_prior.py` normalises digits and re-diffs):

```
bc_setpos_unp.stdout  L7  Error: main.lua:91:  -> main.lua:104:
                      L11 main.lua:91:  in function 'do_mutation' -> :104:
                      L12 main.lua:174: in function 'on_event'    -> :237:
                      L13 main.lua:179: in function <main.lua:179> -> :242:
                      L15 main.lua:220: in function 'update'      -> :294:
bc_newbody_unp.stdout same five sites, 95->108 etc.
```

These are the raw `Error:`/traceback lines, i.e. **not** `IW |` lines: every
`IW | cell=… | …` line is byte-identical between r74 and r75, so **every parsed
key and every prior pinned value is unchanged** (the only pin-line edit is the
declared `esc_fn` addition). The reference is genuine: `git show
2a2c337:corpus/fixtures/love_phys_probe/main.lua` puts the `setpos_unp` escape at
line 91 and the `newbody_unp` escape at line 95 — exactly the r74 receipts'
numbers — and the r74 receipts' mtimes (13:37) predate the r75 author run (14:36),
so they were not edited to fit. stderr files identical throughout.

### 3.4 Insertion-only discipline — PASS

`git show HEAD` removed lines, enumerated: the battery's **8** = the 6 declared
`IW_CELLS`-header comment lines + the two `*_unp` closing pin lines re-added with
`esc_fn` appended (no prior pinned value removed or altered); the probe's **3** =
the declared anchors (`c_pre` one-liner, `world:update(FIXED)`, the `fired`
guard). `--numstat` 153/8 and 100/3 match the report's claim. Every other change
is a pure insertion. The three anchors are behaviour-preserving for non-wp /
non-retfalse cells: `c_pre` returns `nil` when `retfalse_mode` is false,
`world:update(FIXED)` runs identically when `wp_mode` is false, and `uok` is
`true` outside `wp_mode` — confirmed empirically by the 16 byte-identical prior
receipts. `love_probe/`, `pygame_*` untouched (commit touches 3 files).

### 3.5 The new classes' assertions cannot silently pass — PASS

Two-layer check with the committed classifier, driven from my own receipts
(`mutation_test.txt`): every new class is reached only through its full witness
set, and any incomplete witness falls to `anomaly`, never to a neighbouring
class:

- `refused_abort` (gate `love_battery.py:403-417`): all 7 conjuncts load-bearing —
  mutating `wpcall.locked_after`, `wpcall.update_ok`, `wp_setpos.ok`, `wpext.ok`,
  `wpcall_next.update_ok`, `wpcall_next.locked_after`, or the `wp_setpos.err`
  assertion text → `anomaly`; **deleting `wpcall.update_ok` entirely** (i.e. no
  abort at all) → `anomaly` "CELL_DONE but no mutation line" — it can never
  degrade into a plain `refused`.
- `ignored` (`:418-429`): masked velocity (`0,763.87…`), `ERR:` velocity, missing
  velocity, or `returned=true` → `anomaly`; only the landed impulse lands the class.
- `cb_joint_destroy` deferred (`:454-463`): no-drain / not-destroyed / missing
  `jdrain` → `anomaly`; the in-callback deferral pair is enforced by pins.
- `cb_joint_new` (`:438-441, 464`): `ok=true` → `applied` (honest opposite bucket),
  non-assertion err → `anomaly`.
- `bc_setfilter`, `bc_setvel_unp`, `bc_destroy_unp`: every discriminating pin
  mutation flips the row to FAIL (incl. `filter_after`, `final.b1pos/bc/ec`,
  `evpin_ec_lck`, `after_update.count`, `after_update.bpos`, `vel_after`).

**60/60 mutations caught, 0 silent passes.** No `IW_CELLS` pin is a tuple/bound
(all exact-match; the bound form exists only in `CASES`), so no row has slack.

### 3.6 Scout's caution respected: no raw `Error:` line pinned — PASS

Literal scan of the committed battery finds no pin carrying `main.lua:`/`Error:`
(the only hits are the module docstring's prose at `love_battery.py:37` and three
`except ValueError:` clauses — no pin line). The fatal rows pin `assert_txt` (a
substring-derived bucket label), `esc_fn`, `rc`, `done`, `err_on` — all
line-free. `srcline` **is** emitted on the wp row and is **not** pinned anywhere
(verified by import: `srcline` pinned on 0 rows), and it demonstrably drifts
(146 → 155) — exactly why it must stay unpinned. `esc_fn` is pinned on **only**
the two fatal `*_unp` rows, and the rule is the first quoted
`in function '<name>'` frame: in the receipts the first quoted frame is
`[C]: in function 'setPosition'` / `'newBody'`, and LÖVE's boot frames use the
`<…>` form and cannot match — verified on my own receipts, not just the author's.
The interior-error strip (`gsub("^[^:]+:%d+: ")`) is genuinely required: the raw
escaped err carries `main.lua:155:`, while the pcall'd direct-C-call errs
(`cb_*.err`, `wpext.err`) do not — so the pinned stripped text is line-free and
the pin is stable.

### 3.7 One canonical runtime, identity, honest saturation — PASS

All five run dirs resolve to `/usr/bin/love` / LOVE 11.5 (Mysterious Mysteries) /
`probe_exit=0` / `probe_error=None`; nothing in the diff adds a route, fallback,
or second judge. The saturation claim ("44/44 ×4 reps", commit message and
report) is honest and stronger than claimed: the four author reps are
byte-identical to each other **and** to a fifth independent rep from this seat
(50/50 `iw-*` files identical across reps; concat sha `74db3f10…9004`).

### 3.8 Scope note

`resume_continuity_v1` / resume-path preflight is **N/A** to this diff: no
continuity, preflight, or resume surface exists in `love_battery.py` /
`love_phys_probe` (no resume code path touched; the battery's only entry points
are `main()` and the module's parse/classify helpers). Likewise no
authority-boundary or contract surface is touched by this commit.

---

## 4. Residual risk

- **Class-vs-pins asymmetry (F5)** is the only structural soft spot in the new
  rows: for `bc_joint_destroy` the *class* carries the epilogue drain while the
  *pins* carry the in-callback deferral. A future refactor that drops pins (or a
  future row that reuses the `cb_joint_destroy` tag without them) would weaken
  the deferral claim to "count dropped by the end of the step".
- **Witness asymmetry (F1)**: the wp row's interior-write refusal is pinned
  (`wp_setpos.pos_after` = the unchanged fire pose) but the collateral half is
  not; the docstring's "as collateral" reading is therefore one pin short of
  being fully enforced.
- **Build-scoped values**: every pose/step/count pin is a LOVE-11.5 value. The
  classes and the level-relative shapes are the load-bearing part (as the scout
  states); a build change is expected to be caught by the pins, which is the
  design intent (e.g. `bc_setfilter` → `ok=false` ⇒ FAIL).
- **Single-witness class (F6)**: `ignored` has one witness family (velocity).

## 5. Verification gaps (what I did not establish)

- No `lsp` semantic pass (no device, no server on this host — see the header
  disclosure); name/behaviour claims rest on executable evidence, and the one
  text scan is literal.
- **Not re-derived from bytes alone**: per-cell `rc` (F4) — required re-running.
- **Not measured by me**: the joint drain *point* (scout §7-1); L1 shapes for
  joint/filter writes (scout §7-2); whether the wp abort's transient lock affects
  a later in-step callback (scout §7-3); `pre_retfalse` with a per-contact-only
  return (scout §7-4). All are disclosed as open in the scout's §7.
- **Mechanism, not fact**: I verified from receipts *that* callback-escaped errors
  carry `main.lua:NN:` while pcall'd direct C calls do not; I did not trace the
  mechanism (no LÖVE source on disk). The pin-stability conclusion does not depend
  on the mechanism.
- **Out of scope / not used as evidence**: the other in-flight r75 seats'
  untracked scratch trees (`r75-critic`, `r75-boundary`, `r75-baseline`,
  `r75-simplifier`, incl. their private copies of `love_battery.py`) are visible in
  `git status` but were not read as evidence for this review — the committed diff
  is the object under review, and the r74-critic receipts used in §3.2 are a
  *corroboration cross-check* of a claim the author makes, not a source of pins.
