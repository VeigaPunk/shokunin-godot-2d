# game-dev-2d round 78 — reviewer (seat: reviewer; host: devin)

Lane `g2d`, wave `shokunin-train-20261101-w18`. Repo
`/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin` @ HEAD **`1a03b7a`**
("r78 work: nested-update damage surface — 17 cells"; parent `d4aaa95`).
Host: LÖVE 11.5 (Mysterious Mysteries) `/usr/bin/love`, LuaJIT
2.1.1788460057, Python 3.14.7, `luac -p` present.
Leaf discipline: no subagent, no git mutation, **no tracked-file edit**.
Writes: this report + `corpus/live/r78-reviewer/**` (scratch only).
Pre-existing state note: `corpus/live/r72-simplifier/{snapshots/log.txt,watch.log}`
were already `M` in `git status` before this seat's first command and are
untouched by it (they are the only tracked modifications in the tree).

Review target: commit `1a03b7a` — `corpus/fixtures/love_battery.py`
(+560/−5), `corpus/fixtures/love_phys_probe/main.lua` (+479/−0),
`reports/round-78/r78-author.md` (+381). `git diff --stat 1a03b7a^ 1a03b7a`
= exactly those three files.

**`lsp` disclosure (seat-card obligation).** No `lsp` device is exposed in
this session (`mcp_list_servers` → only `rea`; no `lsp` tool in the dispatch
surface) and no Lua/Python language server is installed
(`lua-language-server`, `sumneko-*`, `pylsp`, `pyright`, `luacheck` ABSENT;
only `clangd`, and the LÖVE C++ tree is not in this repo). `references`,
`definition` and `diagnostics` requests were therefore **not available** —
text `grep`/`diff` was the literal fallback and is **never** presented below
as semantic proof. Semantic claims rest on: (a) fresh-process execution
receipts, (b) source-level variants of the tracked classifier built by
`ast`/text surgery and executed in-process, (c) parser diagnostics
(`luac -p`, `ast.parse`, `py_compile`). No cold-start empty result is
recorded as absence.

Artifact-trust: `r78-author.md`, `r78-boundary.md`, `r78-scout.md` and the
author's scratch receipts were read as **data**. The canonical assignment is
the only instruction source.

---

## 0. Verdict summary

The committed diff is what it claims to be. I re-derived every load-bearing
number from my own fresh processes and my own classifier variants:

- **92/92 PASS ×4 consecutive full batteries** on the committed tree (mine,
  fresh processes), all 17 r78 receipts byte-stable across all four runs and
  **byte-identical to the author's final run** (17/17).
- **Insertion-only confirmed twice** (my own parent-revision run and the
  author's cited r77 closeout run): 45 byte-identical + 11 line-token-only +
  **0 semantic diffs** over the 56 prior IW cells; the 11 token-only cells
  are exactly the author's named list. The 5 deletions are all inside
  `iw_classify`, exactly as enumerated. Prior **classes** unchanged (0/56
  under a pre-r78 classifier variant).
- **All 17 new cells replayed ×3 in fresh processes** with my own witness
  predicates (including line-**ordering** witnesses the classifier cannot
  see): 0 failures, byte-stable, class re-derived with the tracked
  classifier, battery pins re-checked.
- **Ablation reproduced independently**: my own 61-mutation matrix
  (conjunct-level, class *and* pins) → **61/61 caught, 0 leaks, 0 targets
  absent**; the author's own `ablate_gates.py` re-run against **my** receipts
  → **37 caught, 0 not caught, 0 absent, 0 base mismatches**.
- **The disclosed r77 D2 fix is real, not cosmetic**: the old conjunct was
  vacuous (0/73 receipts contain a bare `postfire` key; it fired for all five
  r77 members, including the drain member that *has* `postfire.step`), and
  the new per-member form **discriminates** — the two death-site mutants the
  old form still classes `corrupt` are flipped to `anomaly` by the new form.
- **The r78 layer is load-bearing for every new row and inert for every prior
  row**: a pre-r78 classifier variant loses the class on 17/17 r78 receipts
  and changes 0/56 prior receipts.
- **Siblings unaffected (my own runs)**: pygame 80/80, Godot-2D 88/88.

Findings: **one MEDIUM** (F1 — the armed `corrupt` member is keyed on
`depth==2`, which the sibling `r78-boundary` seat measured to be *not* the
variable, and the arm never cites it), **one LOW/MEDIUM** (F2 — a drain-EC
line emitted on the predicate boundary proved forgeable, called a "drain EC"
where the receipt shows an immediate destroy), **two LOW** (F3
structural-trueness family in three conjuncts; F4 the livelock gate's missing
queued-body witness), and **three precision/completeness nits** (F5–F7). No
HIGH finding; **no false-PASS or false-FAIL constructed anywhere**.

---

## 1. Evidence (commands, exits, receipts)

All under `corpus/live/r78-reviewer/` unless noted.

| # | what | command | result |
|---|---|---|---|
| 1 | battery ×4, committed tree | `python3 corpus/fixtures/love_battery.py --runs corpus/live/r78-reviewer/runs` | `totals: cases=92 pass=92 fail=0`, exit 0, ×4 — `runs/love-20261014T211{347279711,426971047,454038377,903490145}Z` |
| 2 | parent-revision battery | scratch copy of `1a03b7a^` battery+probes (`prior/`), same command | `cases=75 pass=75 fail=0` — `prior-runs/love-20261014T211432298275Z` |
| 3 | drift audit ×2 pre-images | `drift_audit_independent.py` (normalises `main.lua:NNN` / `srcline=NNN`) | 45 identical / 11 token-only / **0 semantic** / 17 new — identical numbers vs my parent run *and* vs the author's cited `corpus/live/runs/love-20261014T200810918691Z` |
| 4 | row order | `row_order.py` (regex-parses both revisions' tables) | prior rows preserved in order, 0 content changes, 0 missing |
| 5 | cell replay ×3 | `replay_cells.py` (fresh `love` per cell/rep, my own predicates + ordering) | 17 cells × 3 reps, `failures: 0 []` → `replay.json` |
| 6 | mutation matrix | `gate_ablation_independent.py` §D | **61 applied, 61 caught, 0 not caught, 0 absent** → `gate_ablation.json` |
| 7 | classifier variants | same script, `ast`-extracted `iw_classify` with the r78 layer removed (`pre78`) and the old conjunct restored (`oldcorr`) | §A 0/56 prior class changes; §B 17/17 r78 load-bearing; §C vacuity; §E discrimination |
| 8 | author's ablation, my receipts | `ablate_author_replay.py` (their script, `--runs` pointed at my run) | `ablations: 37 caught, 0 NOT caught, 0 tag absent, 0 base mismatches` |
| 9 | sibling batteries | `pygame_battery.py --runs …/sibling-runs`, `run_battery.py --runs …/sibling-runs` | pygame `80/80` PASS, Godot `88/88` PASS |
| 10 | parser diagnostics | `luac -p corpus/fixtures/love_phys_probe/main.lua`; `ast.parse`/`py_compile` on `love_battery.py` | all OK |
| 11 | tracked-byte check | `sha256sum` of the three files vs `git show 1a03b7a^:` blobs | `ea70c42c…` / `75eb18d2…` / `conf.lua` `85aa6232…` (unchanged) — exactly the author's table |
| 12 | no-side-effect check | `git status --porcelain -- corpus/fixtures reports/round-78` | only untracked `__pycache__/*.pyc` (pre-existing) + other seats' reports; no tracked edit |

662 fresh LÖVE/Godot/pygame processes across the cited runs #1–#9 (plus three
superseded iterations of the replay harness that I fixed and re-ran — their
outputs are not cited).

---

## 2. What I re-derived independently

### 2.1 Battery and stability

`92/92` ×4 on the committed bytes. All 17 r78 cells are byte-stable across
those four runs (`17/17`), and **byte-identical to the author's final run**
`corpus/live/r78-author/runs/love-20261014T210943322605Z` (`17/17`), so the
author's `runs_distinct=1` claim reproduces on foreign receipts. The author's
intermediate-revision claim also reproduces: their three pre-rework runs
(`…T2100{16171220,25788543,47125716}Z`) are byte-identical to the final run
on all 17 r78 cells (51/51 comparisons), and the 91/92 provenance run
`…T205937122136Z` fails exactly one row, `iw_drain_worldrelease`, with
`class anomaly != corrupt (rc=-11 without a release or nested-drain witness)`
— the one-line fix attempt, as disclosed.

### 2.2 Insertion-only

Two independent pre-images agree, and the token-only set matches the author's
§1 list exactly:

```
byte-identical: 45   line-token-only: 11   semantic diffs: 0   new receipts: 17
token-only cells: bc_cowrap_unp bc_coyield bc_draindefer bc_newbody_unp
  bc_setpos_unp bc_setpos_wp bc_worlddestroy cowrap_update_yield
  ext_worldrelease wp_coyield wp_drain_throw
```

No pin contains `main.lua` or `srcline` (0 occurrences in
`love_battery.py`), so the declared-unpinned drift is genuinely unpinned.

**Position claim, precisely.** The prior 75 rows are preserved *in order* with
no edit; index identity holds for IW indices **0–41**. The 14 r78 non-death
rows are inserted at index 42 (as the author discloses: "appended ahead of the
process-death tail"), the r78 uncontained death row at index 65, and the two
r78 corrupt rows at 71–72. Prior tail rows therefore shift: old 42–50 → new
56–64 (+14), old 51–55 → new 66–70 (+15). The binding tail invariant —
**the `rc=-11` band is the final 7 rows** — holds, and each cell is still its
own process. So "prior 75 rows at identical positions" is true for the
non-tail block and for *relative* order everywhere, but the literal index
reading is false for the 14 tail rows; the author's own §1 says the same.

### 2.3 Cell replay (my predicates, not the author's pins)

`replay_cells.py` spawns a fresh `love` per (cell, rep), parses with the
tracked `parse_iw`, re-derives the class with the tracked `iw_classify`,
re-checks every pinned key with the tracked `check`, **and** asserts my own
decisive-witness predicates per cell — including three *ordering* properties
the classifier cannot see:

- `n_queue_inner_drain`: the `r78drainec` line precedes the `r78nest1` line
  (the drain ran *inside* the nested update), and the `r78destroy … dead=true`
  line precedes `postfire` (the target is dead before the outer callback
  returns) — both measured, both true.
- `z_abort_use_after`: `r78zsame` (all five accessors live) precedes
  `r78zlate` (invalidated).
- `n_depth2_drain`: the **last line on the pipe** is the depth-2 nest's own
  receipt, `postfire.step` absent, `stderr` 0 B, `rc=-11` — and the `_wp` twin
  is byte-identical modulo the cell name (`pcall` does not contain a signal).

Result: `replayed 17 cells x 3 reps; failures: 0 []`, every cell
`stable=True`. `livelock_all`'s receipt arithmetic also checks out: the count
of `r78drainec` lines equals `r78obs.drain_n` (197) and
`aborts == drain_n == steps − fire_step + 1`.

### 2.4 Ablation (my mutations; the 37/37 claim)

My matrix targets **individual conjuncts**, not whole tags, and separates the
two layers: class-gate flips (`drainec.depth 1→0`, `queue.dead_in_cb
false→true`, `destroy.dead true→false`, `wpext.err → IsLocked assert`,
`nest1.err → IsLocked text`, `zpost.touch ERR→true`, `aborts 197→196`,
`drainec.n 2→1`, …) and pin-level failures (`r78npre` dropped,
`final.b1pos` altered, `drainec.dyn b3→b1`). **61/61 caught**, including the
three boundary-relevant ones: nothing destroyed (`destroy.count 3→4`),
immediate-destroy EC (`drainec.depth 1→0`), and collateral lock refusal
(`wpext.err` → the `IsLocked` text) each flip the row to `anomaly`.

The author's own harness, pointed at **my** receipts, reports
`37 caught, 0 NOT caught, 0 tag absent, 0 base mismatches` — the claim is
confirmed on independent evidence, not merely re-read.

### 2.5 The disclosed r77 D2 vacuity and its fix

- **Vacuous, confirmed.** No receipt key is ever a bare `postfire`
  (`0/73`), because `parse_iw` emits only `<tag>.<key>`, `done`, `evpin_*`,
  `rc`, `assert_txt`, `err_on`, `esc_fn`. The parent conjunct
  `"postfire" not in flat` therefore fired for all five r77 members —
  including `drain_worldrelease`, which *has* `postfire.step`. I rebuilt the
  parent conjunct and evaluated it directly on the receipts:
  `old_conjunct_fires=True` for all five.
- **The new form discriminates.** `V_oldcorr` (tracked classifier with the
  parent conjunct restored) still returns `corrupt` on the two death-site
  mutants that `V_new` rejects:
  `bc_worldrelease` + a `postfire` line → new `anomaly` / old `corrupt`;
  `drain_worldrelease` − the `postfire` line → new `anomaly` / old `corrupt`.
  That is the test the old form could not pass, and it is why the fix is
  substantive rather than cosmetic.
- **The member clauses are disjoint** (member A needs `rel_post.marker` ∧
  ¬`postfire.step`; member B needs `drainrel.alive` ∧ `postfire.step`), and
  the switch from `rel_alive.marker` to `rel_post.marker` makes member A's
  death-site marker *later* (tighter). Side effect worth recording: a receipt
  with `rel_alive.marker` but no `rel_post.marker` now falls to `anomaly`
  instead of `corrupt` — a fail-closed narrowing, not a hole.

### 2.6 Layer additivity and load-bearing

`pre78` (the whole r78 layer cut out of the tracked `iw_classify` source, no
`flat.get("r78…")` remaining) applied to all receipts:

- **0/56** prior cells change class → the r78 layer moved no prior row.
- **17/17** r78 rows lose their class (`anomaly`, except
  `n_destroy_contacting` → `fatal`) → each new branch is load-bearing; the
  uncontained member would otherwise be swallowed by the pre-existing
  `"Box2D assertion" in stdout → fatal` gate, exactly as the author says.

`rc` is persisted on **all 73 IW rows** (`58×0`, `8×1`, `7×−11`), including
both r78 death classes.

---

## 3. Findings (by severity)

### F1 — MEDIUM: the armed `corrupt` member is keyed on `depth==2`, which the same-round sibling boundary seat measured to be *not* the variable, and the arm never cites it

`corpus/fixtures/love_battery.py` (r78 `corrupt` sub-gate, `1a03b7a`) requires

```python
        if ("fire.step" in flat and "postfire.step" not in flat
                and flat.get("r78drainact.kind") == "nested_update"
                and flat.get("r78nest2.ok") == "true"
                and flat.get("r78nest2.lock_after") == "false"
                and flat.get("r78nest2.depth") == "2"
                and flat.get("r78nest2.in_cb") == "true"
                and flat.get("r78drainec.n") == "2"
                and flat.get("r78drainec.depth") == "2"
                and flat.get("r78drainec.in_cb") == "true"):
```

`reports/round-78/r78-boundary.md` §3.1 measured the same SIGSEGV **at depth 1**
(`b_drain1` nests from a top-level, `depth=0` drain EC; `b_drain1_wp` is also
SIGSEGV) and from the *second* drain EC (`b_drain2_second`), and §8.2 states
the author-facing correction verbatim: *"Key the corrupt class on the drain-EC
origin, not on depth … A gate keyed on `depth==2` will miss the depth-1 members
of this class (mine) and will not be justified by the mechanism."*

`r78-author.md` cites `r77-boundary` (§1/§6 provenance of the lock-clear) but
**never `r78-boundary`** (`grep -n "r78-boundary" reports/round-78/r78-author.md
corpus/fixtures/**` → no hit), so the correction is unaddressed; the commit
subject and §3.3 still frame the class as "depth-2 … SIGSEGV".

Impact is **not** a soundness hole: the gate is fail-closed — a depth-1 member
would classify `anomaly` and the row would FAIL, not silently pass. But (i) the
armed class is narrower than the measured class, (ii) the depth conjunct is a
*cell-shape* pin presented as a decisive witness, and (iii) the arm's §7
"no independent reproduction by another seat" now understates the round: a
sibling measured this exact surface (93 processes) and refuted one framing.
Recommend: keep `depth` as a pinned value but re-key the gate on the drain-EC
origin (`r78drainact.kind == "nested_update"` + the nest returning + `postfire`
absent + `rc=-11`), and record boundary §3 in the report.

### F2 — LOW/MEDIUM: `r78drainec` is emitted on the predicate boundary proved forgeable, and is called a "drain EC" where the receipt shows an immediate destroy

`corpus/fixtures/love_phys_probe/main.lua` (r78 emission point):

```lua
  if R78S ~= nil and ev == "ec" and not world:isLocked() then
    r78_drain_hook(contact, fa, fb, dyn)
  end
```

That is boundary's Q3 predicate (`ev == "ec" and locked() == "false"`), which
§4 shows is passed by two forgeries with *nothing destroyed* and by one
**field-identical** exterior-destroy EC; §8.1's smallest safe correction is a
provenance predicate (`deferred` at the call site, `own ≥ 1` per EC).

Concrete instance **inside the armed corpus**: the three contained escape
cells carry `r78drainec` lines produced by the *immediate* post-nest destroy,
not by a drain loop —

```
n_destroy_contacting_wp: r78nest1 … count=4   →  r78drainec n=1 … depth=0 in_cb=true count=4  →  r78destroy what=b1 … dead=true count=3
n_destroy_ground_wp:     r78nest1 … count=4   →  r78drainec n=1 dyn=b1 / n=2 dyn=b3 (both depth=0 in_cb=true count=4)  →  r78destroy what=g … count=3
n_destroy_fx_wp:         r78nest1 … count=4   →  r78drainec n=1 … depth=0 in_cb=true count=4  →  r78destroy what=fx … fcount 1→0
```

`r78-author.md` §3.4 and the row comment at `love_battery.py:939` call the
ground cell's pair "**two drain ECs**"; they are the ground's two EndContacts
dispatched by the immediate `destroy()` while the world was unlocked in the
outer callback. Under boundary §4.2 this line cannot distinguish a drain EC
from a foreign one.

No false PASS found: every gate that reads `r78drainec` is compensated — the
`inner_drain` gate additionally requires `r78queue.dead_in_cb == "false"`
(the call-site deferred witness boundary §8.1 asks for), `r78destroy.dead`,
`count == bodies−1` and `depth == 1`; the `corrupt` member additionally
requires the `r78nest2.*` return line; the `refused` member requires
`r78nest1`/`r78drainact`. All of those are ablation-caught (61/61), and I could
not construct a receipt that passes a gate on a forged EC alone. Recommend:
add `deferred`/`own`/`pend` to the line (or rename it `r78ecunl`) and correct
§3.4's prose.

### F3 — LOW: three new conjuncts belong to the same "cannot fail once the key exists" family as the r77 defect just fixed

Measured over my four runs: `r78drainec.locked` is `false` in **52/52**
occurrences, `r78inner.locked` is `true` in **44/44**, `r78inner.depth` is
`1` in **44/44** — because the probe emits each line only under exactly that
condition. They are fail-closed on *absence* (an absent key → `None` ≠
`"false"` → `anomaly`), so unlike the r77 bug they cannot admit a receipt with
no evidence; but they carry no discriminating value and read like
measurements. The genuinely measured conjuncts in the same gates are
`r78inner_write.ok == "false"`, `r78queue.dead_in_cb == "false"`,
`r78destroy.dead/count`, `r78nest1.lock_after == "false"` — each
ablation-caught. Recommend a one-line docstring note ("presence of the line is
the witness; the value restates the probe's own predicate") so the next round
does not treat them as evidence.

### F4 — LOW: the `livelock` gate has no queued-body-count witness

Boundary §5 measured a **starvation** shape (`e_live_two`: two queued bodies,
the abort unwinds out of the body loop so the second is never attempted —
`aborts == drain_n == rate`, `count == bodies`, `pend` unchanged) and §8.5
asks for either the starvation corollary or an explicit single-body scope for
the `drain_n == aborts` identity. The author's three livelock cells are
single-body, but the class gate is keyed only on `r78obs.aborts/drain_n`,
`count == built.bodies`, `b1dead/b3dead`, `r78wpcall.locked_after`,
`r78wpext.ok` — a two-body starvation receipt would be admitted under the same
reason string ("nothing destroyed") with the starved body invisible. The
report neither cites the corollary nor scopes the identity to one queued body.

### F5 — LOW (precision): "`rc` is persisted on every row" is arm-scoped

True for the 73 IW rows (measured: `58×0, 8×1, 7×−11`). Not true for the
15 `CASES` + 4 `SPLICE` rows, which never carried `rc` in any round
(pre-existing shape; the probe exit is in the payload's `probe_exit`). The
sentence in `r78-author.md` §1 should say "every IW row".

### F6 — LOW (precision): the `cells/*.summary.json` scratch reps span three battery revisions

`a1–a6` were produced against the **parent** battery hash `829867…` — their
`class` fields read `anomaly`/`fatal` precisely because the r78 branches did
not exist yet — and `b1–b3` carry three *intermediate* hashes
(`83f91ac0…`, `8ff8fa2e…`, `cca65904…`), none equal to the final
`ea70c42c…`. The claim they support (`stable_bytes=true`) holds and I
reproduced byte-stability ×3 on final bytes, but those `class` fields are not
final-revision classes and must not be cited as such.

### F7 — LOW (completeness/attribution): the unarmed zombie's mechanism label repeats a refuted claim

`r78-author.md` §6 describes the deliberately-unarmed non-touching zombie as
"the scout's silent-UAF + block-reuse finding". Boundary §6 corrected the
mechanism: the world hands back the **same Lua userdata** (`same_rawequal=1`)
via address-keyed memoization in `World::getContacts`/`findObject`, with
`Contact::invalidate()` running only from `World::EndContact` — no stale vptr
and no `b2BlockAllocator` reuse required; and the zombie needs no nest, no
drain and no abort (one exterior `setPosition` + the ordinary cadence). The
cell is legitimately out of the brief's scope, but the *label* on the inherited
frontier item is now refuted by a sibling measurement.

### INFO

- **No resume path in scope.** `grep -n "resume|preflight|continuity"` over the
  two touched fixtures finds only `coroutine.resume` (the r77 containment
  rung) — there is no process-resume/preflight machinery, so the seat-card
  `resume_continuity_v1` check is N/A for this diff: nothing to reject, no
  mutation to guard. Likewise there is no specialist-lane dispatch, route or
  identity machinery in the touched files, so same-identity rerouting is N/A;
  the only runtime identity in play is the single tracked battery, and the
  arm neither replaces it nor adds a fallback.
- **One canonical runtime, no rerouting.** The arm extends the single tracked
  battery (`love_battery.py`) and the single tracked probe
  (`love_phys_probe`); no second judge, no fallback path, no route change, no
  new class vocabulary consumed anywhere outside the battery and the reports
  (grepped: no tracked script maps the class names; the only other hits are
  prose in `reports/` and two stale untracked scratch copies of the battery
  under `corpus/live/gd-scout/`). Sibling batteries were verified green by my
  own runs, not just by the author's.
- **Tail discipline preserved.** All 7 `rc=-11` rows are the final 7 IW rows;
  `n_destroy_contacting` (rc=1) sits inside the rc≠0 band, not after it.
- **`assert_txt`/`err_on` non-decisiveness is honest**: the inner-Step bracket
  legitimately puts `Box2D assertion failed: m_world->IsLocked() == false` on
  stdout in every nested cell; the r78 pins do not use those keys (they do use
  `esc_fn`, which is the traceback frame `in function 'update'` — a real
  witness, verified).

---

## 4. Cross-check: boundary's forgery results vs the armed cells

Boundary §4 offers three forgery routes against the *scout's* drain-EC gate.
Against the **armed** r78 gates:

| boundary route | armed-gate consequence | my evidence |
|---|---|---|
| **A** — Collide-phase destroy after a nest, nothing destroyed, `cls=foreign` | cannot pass: `inner_drain` needs `r78destroy.dead=true` **and** `count == bodies−1`; mutating either flips the row to `anomaly` | mutations `destroy.dead true→false`, `destroy.count 3→4` → CAUGHT |
| **B** — exterior `destroy()`, EC field-identical to a real drain EC | cannot pass: the gate needs the call-site deferred witness `r78queue.dead_in_cb=false` (boundary §8.1's `deferred`) plus the count drop; the immediate-destroy variant is also rejected by `r78drainec.depth==1` | mutations `queue.dead_in_cb false→true`, `drainec.depth 1→0` → CAUGHT |
| **immediate re-entrant destroy inside the outer Step** (boundary §8.4) | same as B; and this is exactly the shape the three `_wp` cells carry — hence **F2** | `drainec.depth 1→0` → CAUGHT; receipts cited in F2 |

So the author's gates do **not** rest on the forgeable single-witness predicate;
they carry the destroy-provenance conjuncts boundary §8.1 recommends (call-site
`dead_in_cb` = `deferred`, `destroy.dead`, the count drop) plus the EC's `dyn`
identity in the pins. The residual is F2 (naming/prose + no `own/pend` field),
not a demonstrated admission. Boundary's §3.2 text-precision note (`Box2D
assertion failed: found`, not a lock assert) is independently confirmed by the
armed `refused` member's pinned text — the author found and recorded the same
correction before boundary filed it.

---

## 5. Residual risk and verification gaps

- **I did not reproduce the depth-1 crash myself.** F1 rests on boundary's
  receipts (§3.1, 93 cited processes) plus the author's own gate text; my
  scratch contains no depth-1 probe. I therefore cite it as *their*
  measurement, not mine, and F1's severity is set by the fact that the gate is
  fail-closed.
- **The crashing frame remains inferred** (no core/gdb) — author §7 and
  boundary §9 agree; the measured bound is "after the nested update returns,
  before any further Lua frame", which my replay confirms only in that the
  `r78nest2` line is the last line on the pipe.
- **My mutation matrix is receipt-level, not scenario-level.** It proves the
  gates fail closed when evidence is deleted or poisoned; it does not prove
  the probe cannot be *driven* into a forged shape. Boundary §4 is the
  scenario-level attack; my cross-check of it (§4 above) is by construction
  plus citation.
- **The pre-rework revision is not in git.** The claim "92/92 ×3 on the
  intermediate revision, byte-identical r78 receipts" is corroborated from the
  author's receipts (51/51) but the pre-rework *bytes* exist only in their
  scratch.
- **Non-decisive keys by design**: `assert_txt`/`err_on` for r78 rows, and
  `r78wpcall.srcline` (a probe line number, pinned nowhere — 0 pin
  occurrences, verified).
- **Timing rows jitter** within pinned bounds (6 `dtcadence`/`popen` rows
  differ in raw value between my runs; all PASS on both sides) — the battery's
  bound-pinning design, not drift.
- **Not verified by me**: whether `r78drainec` for the `_wp` cells would be
  classified `own=0`/`cls=foreign` under boundary's provenance predicate (I
  did not rebuild their probe); F2's "not a drain EC" reading is grounded in
  the receipt ordering (`drainec` before `r78destroy`, count still 4) plus the
  probe's emission predicate, which is sufficient to reject the *label* but
  does not itself re-run boundary's classification.

**Verification gap I am leaving named:** no seat has yet armed a **depth-1**
member of the body-drain re-entrancy class, and no seat has yet armed the
two-queued-body starvation corollary. Both are measured shapes with receipts
(boundary `b_drain1*`, `e_live_two`) and are the natural r79 frontier.

---

## 6. Recommendation

**ADMIT the work as measured, with two corrections asked of the author
before the round seals** (or as an explicit adjudicator decision):

1. **F1** — re-key the `corrupt` member's gate on the drain-EC origin rather
   than `depth==2` (or arm a depth-1 member), and record boundary §3 in
   `r78-author.md`. The measured class is wider than the armed one; the gate
   is fail-closed, so this is a coverage/attribution defect, not a soundness
   hole.
2. **F2** — stop calling the `_wp` cells' `r78drainec` lines "drain ECs" (or
   add the provenance fields); the line is emitted on the predicate the
   sibling seat proved forgeable.

F3–F7 are documentation/precision items that do not affect any verdict. The
battery, the insertion-only claim, the ablation claim, the class additivity,
the 17-cell replay and the disclosed r77 D2 fix all reproduce on independent
evidence; the one canonical runtime is untouched; no false PASS or false FAIL
was constructed.

*This is a seat recommendation, never an admission; the canonical runtime
remains the only judge.*
