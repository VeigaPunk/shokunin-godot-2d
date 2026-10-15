# game-dev-2d round 75 — simplifier (seat: simplifier; host: devin)

## Scope, method, disclosure

- Lane repo `/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin` @ HEAD `2e3ae8e`.
  Reviewed the r75 diff only: `corpus/fixtures/love_battery.py` (+153/−8) and
  `corpus/fixtures/love_phys_probe/main.lua` (+100/−3), against
  `reports/round-75/r75-author.md`.
- **Leaf discipline**: no subagents, no git mutation, no tracked file touched.
  Verified before reporting: `git diff --stat -- corpus/fixtures/` empty and
  sha256 of both files **identical to `git show HEAD:<file>`**. All writes are
  under `corpus/live/r75-simplifier/**` plus this report. (Pre-existing dirt
  `corpus/live/r72-simplifier/{snapshots/log.txt,watch.log}` was already
  modified at session start — not mine.)
- **lsp disclosure**: this session has no `lsp` device and no Lua LSP server on
  PATH (`which lua-language-server sumneko lua-lsp emmylua` → all absent;
  unchanged host state). Every "no consumer" claim below is therefore a
  **literal grep** result, never presented as semantic proof.
- **Scratch copy per candidate**: `corpus/live/r75-simplifier/scratch/<cand>/
  fixtures` is a byte copy of `corpus/fixtures` with exactly the candidate's
  named line-range edits applied (`logs/<cand>.diff` = the patch, sha256 in the
  evidence table). The battery script itself is the **unmodified committed
  file** in every run — only the patched file differs.
- **Control** = committed receipt bytes,
  `corpus/live/r75-author/runs/love-20261014T173642593012Z` (rep 1 of 4). All 25
  `iw-*.stdout` are byte-identical across the 4 committed reps; concat sha256
  `74db3f10…9004` reproduced exactly.
  Independent corroboration: the **r75-baseline** lane's post-landing run
  (`corpus/live/r75-baseline/love-runs-postland/love-20261014T174348368669Z`)
  is byte-identical to the control on all 25 stdout + 25 stderr receipts
  (different seat, different run — the receipt set is stable across 6 runs).
- **C0 control-of-the-control**: an unedited byte copy of `corpus/fixtures` run
  through the same harness → 50/50 receipts byte-identical, 25/25 iw result
  rows identical, concat `74db3f10…9004`, 44/44 PASS. The harness adds zero
  drift, so every diff below is attributable to the candidate edit alone.

Axes used: **A1** arm weight (lines/state), **A2** receipt-byte identity vs the
committed control, **A3** verdict/class identity (44/44 + every pinned key),
**A4** falsifiability on the unmeasured branch (witness value if a build
behaves differently), **A5** prior-cell invariance, **A6** convention
singularity.

## Candidates found (proposed, never applied)

| id | site (r75 diff) | delta | A2 receipt identity | A3 | recommendation |
|---|---|---|---|---|---|
| C1 | `main.lua:156` post-assert `EM cb_setpos_wp` | −1 line | 48/50 byte-identical; 2 fatal receipts differ **only** in 3 traceback refs (exact −1 translation) | 25/25 rows identical, 44/44 | **KEEP** — armed witness on the falsifying branch |
| C2 | `main.lua:59/300/308-309` abort latch | net 0 lines, −1 local, −1 conjunct | **50/50 byte-identical ×2 reps** | identical, 44/44 | **OPTIONAL** (lowest priority) |
| C3 | `love_battery.py:393-395` `iw_classify` docstring | 3 lines rewritten | **50/50 byte-identical** | identical, 44/44 | **RECOMMEND** (only clean fold) |
| C4 | `main.lua:169-178` `j_pre == nil` guard | −4 lines | 48/50 byte-identical; same 3-ref translation (−4) | identical, 44/44 | **KEEP** — labeled `api_missing` beats a nil-index `died` |
| C5 | `love_battery.py:408-414` three probe-constant witnesses | −3 lines | **50/50 byte-identical** | identical, 44/44 | **KEEP** — receipt-consistency pins |

### C1 — unreachable post-assert emission (`main.lua:156`)

```lua
    body:setPosition(1234.5, 678.9)
    EM(string.format("cb_setpos_wp pos_after=%s", pos(body)))  -- unreached if assert fires
```

Dead on this build: the assert fires *inside* `setPosition` (line 155), so the
emission cannot run. Proof chain:
1. Literal grep: `cb_setpos_wp` appears nowhere in `love_battery.py` and
   nowhere in tracked code except this emission site — no consumer (no LSP
   available; grep is the literal fallback, recorded above).
2. Literal grep of the committed control receipts: the tag is **absent from all
   25 receipts** (`grep -l` → exit 1). The author's own comment on the line
   says the same.
3. Replay with the line deleted (2 reps): `iw-bc_setpos_wp.stdout.txt` is
   **byte-identical** (including `srcline=155` — the deletion sits *below* the
   emitted reference); 48/50 files byte-identical; the 2 fatal receipts differ
   only in the three traceback refs below the deletion, each translated by
   exactly −1 (237→236, 242→241, 294→293) and verified to resolve to the same
   source lines (`do_mutation(...)`, the `c_bc` one-liner, `world:update(FIXED)`);
   25/25 iw result rows identical; 44/44 PASS; concat `0a6b9e3a…9e22` ×2 reps.

Why keep: the line is not an accident — it is the **only positive witness** on
the falsifying branch (a build where the callback-level write is *not*
asserted): emitted + moved `pos` = applied; emitted + unmoved = silently
ignored; absent = aborted. The classifier returns `anomaly` on that branch
either way, so deletion is verdict-neutral — but it destroys that three-way
evidence for one line. Corroboration: the sibling r75-reviewer's
`mutation_gaps.txt` independently records `cb_setpos_wp.pos_after <absent>` as
an unpinned witness, i.e. two methods agree the witness is not load-bearing for
the verdict — which is exactly why the *evidence* argument is the only one left.
Same defect class at `main.lua:105` (`cb_setpos_unp`) is **r74 provenance, out
of the r75 diff** — recorded, not proposed.

### C2 — collapse the abort latch (`main.lua:59/300/308-309`)

```lua
local wp_aborted, wp_recovered = false, false     →  local wp_pending = false
    wp_aborted = true                             →      wp_pending = true
  elseif wp_aborted and not wp_recovered then     →  elseif wp_pending then
    wp_recovered = true                           →      wp_pending = false
```

Line-count neutral, 50/50 receipts byte-identical on 2 reps, 44/44 PASS,
concat `74db3f10…9004`. Equivalence: `do_mutation` fires at most once per
process (the `fired` guard), so at most one abort → at most one recovery
emission. The only divergence window is a *second, independent* abort inside
`world:update` after a recovery; it is unreachable from the mutation, and if it
ever happened both variants already FAIL the `wpcall.step=73` pin (the second
abort emits its own `wpcall` line, last-wins) — the new variant would merely
also emit a second `wpcall_next`. Value: −1 state variable, −1 conjunct.
Recommendation: optional; it is a rename, so apply only if the round wants the
weight gone.

### C3 — stale duplicate class vocabulary (`love_battery.py:393-395`) — recommended

The r75 diff added `refused_abort` and `ignored` to the `IW_CELLS` header
(hunk at +140…+148) and to the module docstring, but `iw_classify`'s docstring
still enumerates the **r74** vocabulary:

```
"""Map one cell's capture onto {captured|applied|refused|deferred|
fatal|timeout|died|nolaunch|anomaly}. ...
```

Three copies of one vocabulary, one stale — a duplicate authority. Fold: delete
the enumeration and point at the single authority (3 lines rewritten, no
behavior):

```
"""Map one cell's capture onto the class vocabulary declared by the
IW_CELLS header (single authority). Partial-capture detection is built
in: fire-present without CELL_DONE is never a pass shape."""
```

Replay: 50/50 receipts byte-identical (the probe is untouched), 25/25 iw rows
identical, 44/44 PASS, concat `74db3f10…9004`. This is the only candidate I
recommend landing. The r74-scoped sentence "the measured partition is
{refused | deferred | fatal | applied}" (module docstring, line 26) is
**history and stays** per the provenance rule; the C3 pointer makes the live
vocabulary unambiguous.

### C4 — probe-internal `j_pre == nil` guard (`main.lua:169-178`)

Unreachable for this cell: `love.load` assigns `j_pre` for
`kind == "joint_destroy"` before any update, and a missing
`newDistanceJoint` throws at load (`nolaunch`), not at use. Its emission
`cb_joint_destroy api_missing=pre_joint` is unconsumed (no pin; the classifier
would say `anomaly` either way). Deletion proven: 48/50 byte-identical, same
3-ref translation by −4 (237→233, 242→238, 294→290, resolved to the same source
lines), 25/25 rows identical, 44/44 PASS ×2 reps, concat `c3915fd3…a9ea`.
Why keep: it converts a hypothetical nil-index crash (class `died`, no
`CELL_DONE`) into a labeled `anomaly` receipt for 3 lines; the file's
convention is to guard surfaces before dereferencing them (`contactmask`,
`setfilter` do the same). Deleting it buys 4 lines and buys back a worse failure
label.

### C5 — three probe-constant witnesses in the `refused_abort` chain (`love_battery.py:408-414`)

`wpcall.update_ok == "false"`, `wp_setpos.ok == "false"` and
`wpcall_next.update_ok == "true"` re-check **literal text the probe writes**
(`main.lua:303/305/310` hardcode those values); the enclosing
`if "wpcall.update_ok" in flat` already guarantees the first. Deletion proven:
50/50 byte-identical, 25/25 rows identical, 44/44 PASS, concat
`74db3f10…9004`. Why keep: the battery's authority model is **receipt-over-code**
— the classifier validates the receipt text, not the probe's control flow. A
probe bug that emitted `wp_setpos ok=true` inside the abort branch would then be
misread as `refused_abort` instead of `anomaly`. Three lines is the price of the
receipt staying self-consistent; deleting them is where this round's deletions
would start to harm the falsifiability axis.

Also considered and rejected without a run (weight-neutral or worse, no
consumer change): deduplicating the `destroy_unp`/`setvel_unp` emitter strings
with the contained branches (a shared helper costs more lines than the two it
saves); factoring `jdead()` for the two `isDestroyed` probes (net −1 line, adds
an upvalue-coupled helper); inlining `retfalse_mode`/`wp_mode` (breaks the
file's cached-kind-flag convention); `local uok, uerr = true, nil` → `true`
(sub-line noise); dropping the unpinned `srcline=`/`wpcall.err`-vs-`wp_setpos.err`
duplication (both are declared, claim-bearing evidence: the C3 "same write, same
error text" claim and the raw error location).

## Preserved contract

- 44/44 PASS in every candidate run (15 CASES + 4 splice + 25 IW cells);
  `launch_ok=True done_marker=True exit=0`; totals identical to control in all
  9 candidate runs.
- 25/25 `iw` result rows identical to control (class, `observed`, pins,
  reasons) in every candidate run — including the two fatal cells whose
  receipts carry the line-number drift.
- Class partition unchanged: `refused_abort` and `ignored` still the r75
  classes; the two `*_unp` fatal cells still spawned last; per-cell process
  isolation kept; `esc_fn` pins unchanged (they are the drift-immune witness,
  independently demonstrated by C1/C4: only traceback line numbers move).
- No prior cell, pin, or pinned value touched by any candidate; the r74-scoped
  history in both docstrings retained.

## Evidence index

All under `corpus/live/r75-simplifier/` (control copy under `control/`,
manifests under `manifests/`, patches under `logs/`).

| candidate | run dir(s) | iw-stdout concat sha256 (sorted) | patch sha256 |
|---|---|---|---|
| C0 copy | `runs/c0_control_copy/love-20261014T174300468334Z` | `74db3f10331228a08b8072c25f797dca62a518b65f17e60d35aee583d6469004` | — (byte copy) |
| C1 | `…T174240423499Z`, `…T174335917407Z` | `0a6b9e3a9b30b7c6548238911579b6988fd0836318c3508702b12b884c209e22` | `caed3b81…4219` |
| C2 | `…T174240421799Z`, `…T174335917090Z` | `74db3f10…9004` | `83ebd429…57d7` |
| C3 | `…T174240423912Z` | `74db3f10…9004` | `9763be61…eb29` |
| C4 | `…T174240421944Z`, `…T174335918376Z` | `c3915fd348faecbb266b45192294059122385876126ae38b323b5c67f387a9ea` | `460c3eec…e33a` |
| C5 | `…T174240421776Z` | `74db3f10…9004` | `72eab18e…475c` |

Control concat: `74db3f10…9004` (all 4 committed reps + r75-baseline
post-landing run + C0 + C2 + C3 + C5).

Reproduce:

```
cd corpus/live/r75-simplifier
python3 simplifier.py apply  <cand>          # copy + patch scratch fixtures, emit logs/<cand>.diff
python3 scratch/<cand>/fixtures/love_battery.py --runs "$PWD/runs/<cand>"
python3 simplifier.py compare <cand>         # per-file cmp vs control + result-row diff
```

## Tradeoffs and stop point

- The lane's strongest artifact is the receipt bytes; the r75 diff is already
  tight, so the honest simplification yield is **one comment-only fold (C3)**
  plus one optional state merge (C2). Everything else that is deletable is
  deletable only by spending evidence (C1's armed witness, C4's guard label,
  C5's receipt-consistency pins).
- Structural cost of *any* edit above the fatal escape sites: the two `*_unp`
  tracebacks embed absolute source lines, so a deletion anywhere above them
  shifts 3 refs per receipt. That drift is mechanical and exactly measurable
  (proved above by resolving the shifted refs), but it is why C2/C3/C5 —
  line-neutral or battery-side — are the only candidates whose receipts are
  **strictly** byte-identical.
- Stop point reached: the next deletion (C1/C4/C5) would trade arm weight for
  falsifiability, which is an axis this lane does not spend. C3 is the one fold
  I recommend; C2 only if the round wants the state variable gone.
