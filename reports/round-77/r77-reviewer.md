# game-dev-2d round 77 — reviewer (g2d): post-commit review of `62201e5`

Seat `g2d REVIEWER` (LEAF) | lane `g2d` | round 77 | host **devin**.
Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD `62201e5` (review
target), parent `94356ce`. Runtime **LOVE 11.5 (Mysterious Mysteries)**,
LuaJIT 2.1.1788460057, Python 3.14.7, `nproc`=32.
Scope: the committed diff `94356ce..62201e5` only (5 files, all additions).

**Verdict: ACCEPT** — no blocking defect. Five foldable findings, all LOW
(doc/provenance; none touches a gate, a pin, or a class). Every load-bearing
claim of the commit message reproduced independently on my own runs.

**`lsp` disclosure (host state, unchanged from the other r77 seats):**
`mcp_list_servers` exposes **only `rea`** — no `lsp` device for this repo, and
no Lua/Python language server is installed (`lua-language-server`,
`sumneko-*`, `pylsp`, `pyright` all absent). Symbol-aware
`references`/`definition`/`diagnostics` calls were therefore **unavailable**;
text inspection and fresh-process execution receipts were the only carriers.
No cold-start empty result is recorded as absence. I edited no tracked file
and made no git mutation (this report is my only write).

Legend: **[M]** measured (fresh process / byte compare), **[R]** re-derived
from a landed artifact, **[I]** inference, **[U]** unavailability.

---

## 0. What I ran

| # | command | result |
|---|---|---|
| 1 | `git diff 94356ce 62201e5 --numstat` / `--stat` / `--diff-filter=DR` | 5 files, **2281 insertions, 0 deletions**; no renames/deletes |
| 2 | import both revisions of `love_battery.py` and compare the tables | 30 prior IW cells **byte-identical by name**; `CASES`/`SPLICE_CELLS` identical; +26 cells; 75 cases total |
| 3 | `python3 corpus/fixtures/love_battery.py` ×4 (sequential) | **75/75 PASS ×4** (`corpus/live/runs/love-20261014T1954{41777994Z,56389636Z,11193229Z,26167934Z}`) |
| 4 | pre-r77 run `…T194202453025Z` (49/49) vs my run 1 | 56 files identical, **5 token-only**, 6 jitter — matches the author's drift audit exactly |
| 5 | my 4 runs cross-compared | **113 files identical / 6 differing** (the declared jitter set) |
| 6 | `python3 corpus/live/r77-author/ablate_gates.py <my run 1>` | **43 row-fails, 0 leaks** |
| 7 | old (`94356ce`) vs new (`62201e5`) `iw_classify` over the 30 prior receipts | **0/30 divergences**; 0/30 prior receipts touch any r77 gate key |
| 8 | token census of my run's 56 IW receipts | 14 distinct `main.lua:NNN`/`srcline=N` tokens, all content-verified (see §6) |
| 9 | `luac -p corpus/fixtures/love_phys_probe/main.lua` | parse clean |
| 10 | `sha256sum` of both tracked files | match the author's §4 values exactly |
| 11 | source anchors re-read in `/tmp/r74bsrc/love-11.5` | all 9 anchors exact (see §4) |

No write except this report; no commit, push, or deploy.

---

## 1. Insertion-only and the prior 49 cells — **[M]**

`git diff 94356ce 62201e5 --numstat` is `631/0`, `422/0`, `443/0`, `372/0`,
`413/0` (battery, probe, gd-scout, author, boundary). Zero deleted lines and no
rename/delete means **no prior line was altered**; the only way the prior pins
could drift is a re-typed duplicate, so I compared the tables by content:

- `CASES` (15) and `SPLICE_CELLS` (4): **identical objects**.
- `IW_CELLS`: the 30 prior rows are **byte-identical by name** (pin dicts
  included). The 5 r74/r75/r76 `*_unp`/`worlddestroy` rows did move in the
  *table* (old positions 25–29 → new 42–46, because 17 r77 rows were inserted
  above them and 9 appended), which is an order change, not a pin change.

**49/49 prior cases byte-identical** at the pin level. At the receipt level the
30 prior cells' 60 files are 55 byte-identical and 5 stdout files differ **only**
in the declared-unpinned line tokens (§6); the run-level diff against the
pre-r77 run is 56 identical / 5 token-only / 6 jitter, exactly as the author's
drift audit states. The `love_battery.py` header's "prior rows byte-stable"
contract is intact.

---

## 2. Battery replay and the new pins — **[M]**

Four consecutive runs on my own account, `75/75` each
(`cases=75 pass=75 fail=0 launch_ok=True done_marker=True exit=0`), with the
author's four run dirs left untouched. Cross-run byte comparison:

- **113/119 files byte-identical** across all four of my runs — i.e. **all 112
  IW receipt files (56 cells × stdout+stderr) plus `probe.stderr.txt`**,
  including all five `corrupt` (rc=−11) receipts;
- the 6 differing files are exactly the declared jitter set:
  `probe.stdout.txt`, the four `splice-*.stdout.txt`, `verdicts.json`.

The intermediate author run `…T194717707844Z` is present and is **72/75** with
the three pin-shape failures the report names (no engine-behaviour claim).

**New pins reproduce on my runs, not only the author's** — the battery pass is
the pin check, and I additionally read the decisive values out of my own
receipts: `bc_setcallbacks` (`getcb=cb2_bc,cb2_ec,cb2_pre,cb2_post`;
`r77obs bc=2 … bc2=3 ec2=4 pre2=5 post2=5`), `bc_setcallbacks_nil`
(`getcb=nil,nil,nil,nil`, `ec=0`, final pose `400,445.10910034179688`),
`bc_fixture_destroy` (`fx_a_dead=true`, tunneling `400,635.1639404296875`),
`bc_meter` (`meter_before=30 meter_after=60`, `pos_now` ×2, restore `/30`),
`wp_drain_throw` (full `wpcall/r77abortq/r77ecpost/wpcall_next/r77recover`
chain), and the five `rc=-11` rows. All match the author's §2 text.

---

## 3. Classifier coverage — **[M]**

**Six new classes, each with its own discriminating gate**, inserted ahead of
the pre-r77 gates inside the `done and rc == 0` block, plus two new tail
branches (`rc == -11` → `corrupt`; `ext_rel_call.ok` → `died`):

| class | gate keys (all required) | cells |
|---|---|---|
| `corrupt` | `rc == -11` **and** `fire.step` **and** (`rel_alive.marker` or `drainrel.alive`) | 5 |
| `swapped` | `cb_setcallbacks.ok=="true"`, `cb2_*` readback, `new_ran`, old counter frozen (or revert member with `cb_setcallbacks2.ok` + grown old table) | 4 |
| `muted` | nil readback **and** `not new_ran` **and** old counter frozen | 1 |
| `immediate` | `drainact.kind=="queue_b2"`, `b2dead=="true"`, `count_after == drainec.count−1` | 1 |
| `drain_abort` | 12 conjuncts incl. `wpcall.locked_after=="false"`, `wpext.ok=="true"`, `r77abortq.count==drainec.count`, `r77ecpost.locked=="true"`, `r77recover.b1dead=="true"` | 1 |
| `yield_abort` | resume rung (`coused.err` yield + `costatus=dead` + `r77abort/r77abortext/r77recover`) or pcall rung (`wpcall.err` yield + `locked_after=true` + `wpext.ok=="false"` + `wpcall_next.locked_after=="false"`) | 2 |

**Existing gates unaffected — three independent checks:**

1. file-level insertion-only (§1) ⇒ no pre-r77 gate line was edited;
2. **0/30 divergences** old-classifier vs new-classifier over the 30 prior
   receipts (run from my run dir, rc taken from `verdicts.json`);
3. **0/30 prior receipts contain any r77 gate key** (`cb_meter.ok`,
   `cb_fxdestroy.ok`, `ext_fxdestroy.ok`, `cb_setcallbacks.ok`, `coused.ok`,
   `drainact.kind`, a yield in `wpcall.err`, `rc=-11`) — the "structurally
   impossible" claim is **[M]** at the receipt level.

**Ablation matrix re-run on my run dir: 43/43 row-fails, 0 leaks** — every
dropped decisive line leaves via `class→anomaly`/`class→nolaunch` or a missing
pin (`pins:cb2post.step`, `pins:cb2bc.step`, `pins:drainec.n`).

**Load-bearing proof for the new classes:** with the *old* classifier, the five
`corrupt` receipts land `died` (wrong: they die with a signal, and `died` is
defined as rc=1/no-signal) and `ext_worldrelease` lands `nolaunch`; with the new
one they land `corrupt`/`died`. Four new cells (`bc_cowrap_setpos` → `refused`,
`bc_coyield`/`cowrap_update_yield` → `died`, `bc_cowrap_unp` → `fatal`) are
**intentionally** classified by pre-r77 gates (see N1).

`rc` is persisted on **every** IW row (`results[*].rc`, 56/56), including
`-11` ×5 — verified in my run's `verdicts.json`.

---

## 4. Source anchors — **[M]**, all exact in `/tmp/r74bsrc/love-11.5`

| anchor | cited as | verified |
|---|---|---|
| `World.cpp:578-581` | destructWorld flag on locked `destroy()` | ✓ `if (world->IsLocked()) { destructWorld = true; return; }` |
| `World.cpp:299` | world drained at the very end of the epilogue | ✓ `if (destructWorld) destroy();` (line 299) |
| `World.cpp:283-287` / `289-294` | fixture loop / joint loop | ✓ (bodies 277-282, fixtures 283-287, joints 289-294) |
| `World.cpp:272-297` | update epilogue (r76-boundary) | ✓ |
| `callbacks.lua:162` | `if love.update then love.update(dt) end`, read per frame | ✓ |
| `wrap_World.cpp:34` | `"Attempt to use destroyed world."` | ✓ `luaL_error(L, …)` at line 34 |
| `World.cpp:98` | `lua_call(L, args, 0)` — preSolve return unconsumed | ✓ |
| `Body.cpp:529` / `Fixture.cpp:339` / `Joint.cpp:167` | `IsLocked()` destroy guards | ✓ all three |
| `main.lua:821` (echo) | `wp_setpos ok=false …` constant | ✓ (see N2) |

The r77 probe's own comment `Insertion-only: every branch below is gated on
R77[CELL] ~= nil` is **[M]**: every r77 block in `on_event`, `love.load`,
`love.update`, `do_mutation`, `run_ext` is gated on `RS`/`r77_*`/`target_cb ==
nil`, and the receipt diff (§1) confirms pre-r77 cells take the pre-r77 path.

---

## 5. Commit message vs diff reality — **[M]**

| claim | verdict |
|---|---|
| "26 cells" | ✓ 56 − 30 = 26; R77 table keys == the 26 new battery cells exactly |
| "6 new classes (corrupt rc=-11, swapped, muted, drain_abort, yield_abort, immediate)" | ✓ all six exist in `iw_classify` and are exercised (5/4/1/1/2/1 cells) |
| "lock-state-not-phase rule measured at drain EC" | ✓ `drain_setpos_b2` → `applied` (write lands at locked=false), `drain_queue_b2` → `immediate` |
| "resume is containment, wrap is not" | ✓ `co_update_yield` → `yield_abort` (error as value) vs `cowrap_update_yield` → `died` (re-raised) |
| "nested-update hazard parked for r78" | ✓ no nested-update cell in the probe/battery (grep: no `nested`; `world:update` only at update level, lines 808/810); hazard documented in `r77-boundary.md` §6/§8. Traceability nit only (N3) |
| "75/75 x4" | ✓ reproduced on my own four runs |
| "43/43 ablations fail" | ✓ re-run on my run dir: 43 row-fails, 0 leaks |
| "insertion-only" | ✓ 2281 insertions, 0 deletions, no D/R |

---

## 6. The unpinned `main.lua:NNN` tokens moved again — **enumerated [M]**

The r76 fold's declared-unpinned token set was `{125, 129, 315, 339, 401, 441,
srcline 181, srcline 230}` (r76-scribe §4 census; r76 fold run
`love-20261014T184005414245Z`). The r77 insertion shifts them again. Byte-diff
of the five affected receipts, r76-fold run → my run:

| receipt | r76 post-fold | r77 (my run) |
|---|---|---|
| `iw-bc_setpos_unp` | `main.lua:125` (escape), `:315` (on_event), `:339` (c_pre frame), `:401` (update frame) | `:194`, `:497`, `:546`, `:810` |
| `iw-bc_newbody_unp` | `main.lua:129`, `:315`, `:339`, `:401` | `:198`, `:497`, `:546`, `:810` |
| `iw-bc_worlddestroy` | `main.lua:441` (death site + update frame) | `:861` |
| `iw-bc_setpos_wp` | `srcline=181` | `srcline=250` |
| `iw-bc_draindefer` | `srcline=230` | `srcline=299` |

Nothing else moved: the whole 30-cell prior receipt set is identical apart from
those 5 files (56 files byte-identical). The r77 receipts add five **new**
unpinned tokens, all content-correct in my run: `main.lua:403`
(`coroutine.yield("r77")`), `:409`/`:413` (`cowrap_unp` write + `co()`),
`:713` (`f()` in the wrap container), and `srcline=671`
(`error("R77-DRAIN-THROW")`). No pin contains `main.lua:`/`srcline=` (grep of
`love_battery.py`), so all of these stay unpinned by design — a later round
that pins them inherits this round's insertion point.

**Report-body tokens also moved** (same mapping; committed reports are
historical, but the r76 fold kept them current once, so they are listed for the
next fold): `r76-author.md:147` `104→173`; `r76-critic.md:176` `439→859`;
`r76-reviewer.md` L84 `415→824`, L109 `322→521`, L120 `410→819`, L133
`228→297`, L236 `230→299`, L266 `339→546`, L274/278/281 `439→859`, L299
`104→173`, L300 `108→177`; `r76-scribe.md` L130/131 `237→306` (+`242→311`,
`294→462`), L150 `151→220`, L152 `160→229`, L154 `104→173`, L155 `108→177`;
`r76-simplifier.md` L137 `439→859`, L155 `344→551`, L198 `182→251`;
`r76-verifier.md:82` `439→859`. (`r76-scout.md:55` `228→297`; its two
`main.lua:734` tokens have no counterpart in any tracked revision — they quote
an r74-era receipt — and `r76-scribe.md:152`'s "pre-fold `:155`" is explicitly
historical.)

---

## 7. Findings (all LOW, all foldable; none blocks the commit)

**F1 — stale "fatal cells last of all" ordering claims (doc).**
`corpus/fixtures/love_phys_probe/main.lua:16-17` ("Interior cells are spawned
LAST by the battery, the fatal cells last of all") and
`corpus/fixtures/love_battery.py:45-46` and `:879` ("uncontained escapes ->
fatal, spawned LAST") are now false: the r77 block (died → fatal → corrupt,
`love_battery.py:892-894`) is appended after those rows, so the last 5 rows are
`corrupt` and fatal rows sit at positions 45/46/50. No functional impact (one
`love` process per cell; order is inert), but the file now contradicts itself
(the r77 block comment documents the new order). Fix: scope the older claims
("last among the pre-r77 cells") or move them.

**F2 — `iw_classify` docstring omits the new classes (doc).**
`love_battery.py:1031-1033` still enumerates
`{captured|applied|refused|deferred|refused_abort|deferred_abort|ignored|fatal|timeout|died|nolaunch|anomaly}`
— the function that *is* the class authority does not list `corrupt`, `swapped`,
`muted`, `immediate`, `drain_abort`, `yield_abort` (the module docstring does).
Fix: extend the enumeration (an added line keeps insertion-only).

**F3 — `r77-author.md:311-312` residual-risk wording.**
"A build that dies with SIGABRT/SIGBUS instead would land `anomaly`" — actually
it lands `died` (the `has_fire and not done and rc not in (0, None)` tail gate
with no assert text). Fail-loud is still preserved (the row pins class
`corrupt` **and** `rc: "-11"`, so it FAILS), but the stated landing class is
wrong. Fix: "…would land `died` and fail the row's class + `rc` pins".

**F4 — `r77-author.md:287` "(was `471e1a4d…`)" is not the declared diff base.**
`471e1a4d…` is `git show aa4d567:corpus/fixtures/love_battery.py`; the declared
parent of this diff is `94356ce`, whose battery hash is
`4bd71c360c9af70e0aec015acba25a02b880492add5fe215dd4798ba26744aa1`. The
report's own §1 says the diff is "relative to `94356ce`", so the "(was …)"
value reads as a stale seat-start hash. Fix: state both (`4bd71c36…` base,
`471e1a4d…` seat start) or label it "seat-start".

**F5 — `r77-boundary.md:216` quotes a superseded receipt.**
The `co_nested_across` row quotes `err=main.lua:539`, which is the **r77b-c**
(superseded) receipt; the cited set (`cells/r77b-final2.*`, byte-stable ×3,
sha `b45466fa…`) says `main.lua:540` — the `coroutine.yield("inner-yield")`
line of the declared scratch probe (`corpus/live/r77-boundary/probe/main.lua`,
sha `8fe7a43e…`, line 540). Every other value in the row matches. Fix: re-quote
`main.lua:540` (or cite the r77b-c revision explicitly).

### Notes / nits (not defects)

- **N1.** `r77-author.md:243` "no r77 receipt can satisfy a pre-r77 gate by
  accident" is literally false for four intended-reuse cells
  (`bc_cowrap_setpos`→`refused`, `bc_coyield`/`cowrap_update_yield`→`died`,
  `bc_cowrap_unp`→`fatal`, all routed through pre-r77 gates in both
  classifiers). The operative property — no new-class receipt is mislabeled and
  no prior receipt reaches an r77 branch — is **[M]** (§3).
- **N2.** The `drain_abort` gate conjunct `wp_setpos.ok == "false"`
  (`love_battery.py:1140`) is an echo constant emitted unconditionally in the
  wp-abort branch (`main.lua:821`), hence entailed by
  `wpcall.update_ok == "false"`; the decisive no-collateral witness is
  `wpext.ok == "true"`. Redundant, harmless, untested by the ablation set.
- **N3.** The commit message's "nested-update hazard parked for r78" is
  traceable only to `r77-boundary.md` §6/§8 (and its absence from the battery);
  the author report's "not armed" list does not carry it. Traceability, not
  contradiction.
- **N4.** `r77-scout.md` and `r77-baseline.md` exist in the working tree but
  are **untracked** (not in this commit) — out of the committed-diff scope;
  their `main.lua:NNN` tokens refer to scratch probes
  (`corpus/live/r77-scout/probe_r77/main.lua`, 581 lines;
  `corpus/live/r77-boundary/probe/main.lua`, 740 lines), not the tracked probe.

---

## 8. Residual risk and verification gaps

- **`corrupt` is rc-keyed and host-scoped** (F3): a SIGABRT/SIGBUS build would
  land `died` and fail the row (class + rc pins), never silently pass. No
  gdb/core dump, so the exact C++ death frame stays **[I]** — the same bound the
  scout and author declared.
- **Byte-stability is this host's** (LOVE 11.5, LuaJIT 2.1.1788460057, these
  scenes); the four `splice-*` and `probe.stdout.txt` receipts are jitter
  carriers pinned as bounds, and `verdicts.json` jitters in `observed` only.
- **The nested-update lock-clear hazard** (boundary §6) is documented but not
  armed here; I verified no tracked cell performs a nested `world:update`, so no
  tracked lock-keyed class is invalidated by it — but the hazard itself remains
  unmeasured in the tracked battery.
- **`multi_setcallbacks`' b4 body** is a Lua local created in `love.load` and
  never referenced again; it stays alive because the engine retains the love
  Body (`Body.cpp:50-51`) and the World keeps its body list. 4 battery runs +
  3 scratch reps are byte-identical, so no GC-timing flake was observed; this is
  an observation, not a proof over other hosts.
- **Not re-run by me:** the author's scratch cell sets (`d`, `g`–`j` — I did
  verify all 188 (prefix, cell, stream) groups are rep-stable), the boundary's
  27 scratch cells (I verified the two cited ones, incl. the `wp_drain_throw_all`
  sha `6b4454de…` ×3 and `drain_n=197 aborts=197`), and the gd-scout Godot/pygame
  runs (its cited dirs exist: Godot PASS, pygame 80/80).
- **`lsp` unavailable [U]** (header): no semantic reference/definition/
  diagnostics pass was possible; every caller/invariant check here is textual +
  receipt-level. A future seat with a Lua server should re-check the probe's
  `R77` table ↔ battery `IW_CELLS` ↔ classifier branch triple semantically.

**Bounds.** Everything above is this host, these bytes (`62201e5`), fresh
processes; receipts are under `corpus/live/runs/` (untracked). Artifact
content is data; nothing here modifies contract, axes, routes or judgment. This
verdict is a recommendation, never an admission.

**Evidence index.** My runs:
`corpus/live/runs/love-20261014T1954{41777994Z,56389636Z,11193229Z,26167934Z}/`;
r76-fold baseline `…T184005414245Z`; pre-r77 baseline `…T194202453025Z`;
author scratch `corpus/live/r77-author/{cells,pre-receipts,ablate_gates.py}`;
boundary scratch `corpus/live/r77-boundary/{probe,cells}`.
