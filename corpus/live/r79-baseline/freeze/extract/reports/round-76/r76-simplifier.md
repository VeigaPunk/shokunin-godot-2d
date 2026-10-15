# game-dev-2d round 76 — simplifier (seat: simplifier; host: devin)

Lane `g2d`, wave `shokunin-train-20261101-w16`. Repo
`/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin`, HEAD `6ca715d`.
Runtime: LOVE 11.5 (`/usr/bin/love`), Python 3.14.7. Review target: the
committed r76 diff only (`git show 6ca715d`, `corpus/fixtures/love_battery.py`
+174/−1, `corpus/fixtures/love_phys_probe/main.lua` +131/−3).

Leaf discipline: no subagent, no git mutation, **no tracked-file edit**.
Writes = this report + `corpus/live/r76-simplifier/**`. Every candidate was
built and replayed in a scratch tree under that scope.

## Axes (this seat, this round)

- **A1 weight** — duplicated authorities / branch bodies / dead state in the
  r76 delta.
- **A2 evidence** — armed witnesses, pins, and falsifiability-bearing lines.
- **A3 contract** — receipt bytes, pinned keys, classifications, battery
  verdict.
- **A4 replay reproducibility** — can the claim be re-derived by a third party
  from the artifacts alone.

Admission rule applied: a deletion is *proposed* only when A3 and A4 are
byte-for-byte unmoved and A1 improves. A2 is never traded for A1.

## Result

Two deletions replay-proven byte-identical (propose), one deletion candidate
semantically-proven but withheld on the byte-identity bar, two deletions
falsified and rejected with measurements.

| variant | file | change | Δ lines | iw strict | token-only | real div | battery |
|---|---|---|---|---|---|---|---|
| `v0`,`v0b` | — | none (baseline ×2) | 0 | 60/60 | 0 | 0 | 49/49 |
| **`v1`** | battery | **P1** abort-witness single authority | −12/+11 | **60/60** | 0 | 0 | **49/49** |
| **`v4`** | battery | **P2** stale class enumeration → pointer | −2/+1 | **60/60** | 0 | 0 | **49/49** |
| **`v6`** | battery | **P1+P2 composed** | −14/+12 | **60/60** | 0 | 0 | **49/49** |
| `v2` | probe | W1 merge duplicated branch bodies | −20/+4 | 55/60 | 5/60 | 0 | 49/49 |
| `v3` | probe | R1 drop `c_pre` body gate | −9/+6 | 56/60 | 3/60 | 1/60 | **48/49 FAIL** |
| `v5` | probe | R2 drop `jw_prev` guard | −1/+1 | 59/60 | 0 | 1/60 | **48/49 FAIL** |

`iw strict` = the 60 deterministic interior-write receipts (`iw-*.stdout.txt`
+ `iw-*.stderr.txt`, 30 cells) byte-identical to the committed r76-author
reference run. `token-only` = identical after normalizing *only* the unpinned
`main.lua:<N>` / `srcline=<N>` digits. `real div` = anything else moved.

---

## P1 — one authority for the r75 abort witness (PROPOSE)

`corpus/fixtures/love_battery.py`, `iw_classify`, inside the
`wpcall.update_ok == "false"` gate.

The r76 `deferred_abort` branch restates the r75 `refused_abort` six-conjunct
abort witness verbatim (`wpcall.locked_after`, `wp_setpos.ok`,
`wp_setpos.err`, `wpext.ok`, `wpcall_next.update_ok`,
`wpcall_next.locked_after`) and then adds its five deferral witnesses. The
predicate is now authored twice, in two branches of the same gate: a later
conjunct added to the r75 set silently leaves `deferred_abort` on the stale
weaker set. That is a duplicate authority, not merely repeated text.

Proposed shape (`v1.diff`): bind `abort_w` once before the
`cb_destroy.ok == "true"` dispatch and reuse it at both sites —
`if (abort_w and <5 deferral witnesses>)` → `deferred_abort`,
`if abort_w:` → `refused_abort`. The deferral-only conjuncts stay inline and
the `return "anomaly", "deferred-abort witness incomplete"` fall-through is
unchanged, so the r76 class ordering and the reviewer's F1 fail-open
observation are untouched. Named-local hoisting is this file's own idiom
(`late`, `drop`, `dead`, `ec_lck`, `jdrop`, `impulse_landed`), so no second
convention is created.

**Preserved contract (measured).** `corpus/live/r76-simplifier/runs-v1/love-20261014T183503538238Z`:
60/60 iw receipts byte-identical; every `verdicts.json` row identical
including `observed` class and `rc` for all 30 iw cells; 49/49 PASS.

**Stronger than replay.** The replay only exercises 30 receipts. A
differential equivalence fuzz (`corpus/live/r76-simplifier/fuzz_v1_equiv.py`)
loads the HEAD classifier and the v1 classifier side by side and drives both
with the 30 real receipts plus 200,000 randomly assembled `flat` maps over
all 29 keys the file reads (adversarial pool includes missing keys, `""`,
`ERR:`, non-numeric, assert text, `rc∈{0,1}`, `timed_out`). **0 divergences**
on the full `(class, detail)` tuple. Exit 0.

## P2 — collapse the stale duplicated class enumeration (PROPOSE)

`corpus/fixtures/love_battery.py` lines 171–172.

`expected_class` is enumerated twice: once in `iw_classify`'s docstring (r76
updated it) and once in the `IW_CELLS` header (r76 did not). The header
advertises the pinned vocabulary as
`{captured, applied, refused, refused_abort, deferred, ignored, fatal}` —
7 names. The 30 cells actually pin **9** classes.

Measured provenance of the drift: at pre-r76 `ddd455b` the file had 25 cells
pinning exactly `{captured, applied, refused, deferred, refused_abort,
ignored, fatal}` — i.e. the enumeration was *accurate* then, and r76 made it
stale by exactly two names, `deferred_abort` (r76's own new class) and `died`.
This sharpens the reviewer's F2 (`timeout`/`nolaunch`/`anomaly` are classifier
*outcomes*, never pinned expected classes, so their absence is by design).

Proposed shape (`v4.diff`): delete the stale 7-name enumeration, leave a
one-line pointer at the surviving authority. −1 net line, comment-only.

**Preserved contract.** `runs-v4/love-20261014T183537304848Z`: 60/60 strict
byte-identical, all verdict rows identical, 49/49 PASS.

**Tradeoff, named.** The inline enumeration had reader value next to the
cells; the pointer costs one hop. The minimal *defect* fix is instead a
two-name insertion into the existing line — that is an insertion, outside
this seat's propose-deletions remit, and it is the author's/L1's call which
shape lands. Composed `v6` proves P1 and P2 co-apply cleanly (−2 net, 60/60
strict, 49/49).

---

## W1 — duplicated probe branch bodies (CANDIDATE, WITHHELD)

`corpus/fixtures/love_phys_probe/main.lua`. `do_mutation`'s r76 `destroy2`
branch (6 lines) is byte-identical to the r75 `destroy` branch, and the r76
`jwatch` branch (12 lines) is byte-identical to the r75 `joint_destroy`
branch. Merging them behind `mkind == "destroy" or mkind == "destroy2"` /
`mkind == "joint_destroy" or mkind == "jwatch"` deletes 16 net lines and
removes two more duplicate authorities (`v2.diff`).

**It is semantically identity-proven** —
`runs-v2/love-20261014T183514570588Z`: 0 real divergence, every pinned key
and all 30 classifications identical, 49/49 PASS. `destroy2`/`jwatch` still
emit `fire.kind=<their own kind>` (that comes from `kind`, not `mkind`), and
both merged branches emit identical bytes.

**It fails the seat's byte-identity bar by exactly 5 receipts**, and only in
unpinned source-line tokens (raw diffs):

```
iw-bc_draindefer   srcline=230 -> 232
iw-bc_setpos_wp    srcline=181 -> 182
iw-bc_worlddestroy main.lua:439 -> 423  (throw site + traceback frame)
iw-bc_setpos_unp   main.lua:<N>  (traceback frames)
iw-bc_newbody_unp  main.lua:<N>  (traceback frames)
```

The shift is structural: merging rewrites the two prior guard lines
(144, 195) to two lines each (+2 above every throw site) and removes 16 lines
above the `love.update` frames. The r76 author already accepted this exact
drift class for r75 prior cells ("differ ONLY in `main.lua:NNN` source-line
references (structural drift of additive edits, documented since r75)"), so
this is admissible under the *lane's* standard and not under the seat's
stricter one. **Reported, not proposed** — the L1 owns whether the lane's
standard or the seat's standard governs. Two further costs the L1 should
price: it edits two r75 prior lines, against the wave's insertion-only
protocol, and it couples r76 cells to r75 branch bodies.

## R1 — `c_pre` body gate: FALSIFIED, KEEP

`main.lua:344` `if A == b1 or B == b1 then` looks subsumed: `fa == f_mask`
implies `A == b1` because `f_mask` is a fixture on `b1`. Deletion (`v3.diff`,
−3 lines) was built and replayed: `runs-v3/love-20261014T183526115413Z`
→ **48/49, FAIL**
`rf1counts.passes: '32' != pinned '1'`.

The gate is the pair-scope filter for the *passes* arm: without it every
non-b1 `preSolve` contact in the run counts as a pass (32 of them). It is
load-bearing, and the cell's `rf1counts falses=1 passes=1` pin is what makes
that falsifiable. Keep.

## R2 — `jw_prev`: FALSIFIED, KEEP (not dead state)

`jw_prev` is the only new mutable state in the probe, so "dead state" had to
be measured, not asserted. Deletion of the guard
(`jw_prev ~= nil and jw_prev > 0` → `else`), line-count-neutral so no token
drifts, replayed at `runs-v5/love-20261014T183615552924Z` → **48/49, FAIL**
`jwdrop.cb: 'post' != pinned 'ec'`. Raw receipt delta:

```
+ IW | cell=bc_jwatch | jwdrop cb=pre step=74 locked=true jcount=0
+ IW | cell=bc_jwatch | jwdrop cb=post step=74 locked=true jcount=0
```

The guard is what makes `jwdrop` fire *once*, on the first callback after the
drain. `jw_prev` is live, load-bearing state. Keep.

---

## Considered and kept (no replay claim, judgment calls)

- **`try/except ValueError` around `late`** — byte-identity-admissible
  (Python-only), but three sibling guards in the same function (r74 `vy`,
  r74 `after_update.count`, r75 `jdrain.jcount`) carry the identical shape.
  Deleting one instance would create a second convention — the thing this
  seat exists to prevent — and it is the fail-closed path (malformed receipt
  → `anomaly`, not a battery crash). If the lane ever wants it gone it must
  go from all four sites, which touches r74/r75 rows: out of scope here.
- **`late` is *derived* (`drainlate.step == wpcall.step + 1`), not a literal
  `== "74"`.** The literal is shorter and would destroy the falsifiability:
  a build draining two steps late would still match a literal pin. Keep.
- **`EM("cb_draindefer unreached")`** — never read by `iw_classify`, but it is
  a falsifiability marker (a build without the in-callback lock would emit it)
  and it matches the r75 marker at `main.lua:182`
  (`-- unreached if assert fires`). Keep: A2 outranks A1.
- **17 of the r76 pins are never read by the classifier** (`post_destroy2.*`,
  `jwlive.*`, `jwdrop.*`, `rf1counts.*`, `wdrained.*`, `esc_fn`, `err_on`,
  `assert_txt`, `abortq.step`, `cb_destroy.count_after`, …). They are pure
  guards: the cell FAILs if the measured value drifts. Deleting a pin removes
  falsifiability. Keep all.
- **`local jw_prev = nil` / explicit `= nil`** — matches the file's own r75
  convention (`local j_pre = nil`). Keep.
- **Docstring paragraphs in both files** — evidence-bearing (they carry the
  SayGoodbye census result and the class semantics). Keep.
- **`battery.py` module docstring "the measured partition is {refused |
  deferred | fatal | applied}"** — stale since r75, but explicitly
  provenance-marked historical ("r74 lattice (…)"); the seat never deletes
  marked provenance. Untouched.

## Dead-state sweep

Census over every new r76 identifier in both files (definition + uses):
`dd_mode` 5, `d2_mode` 2, `wd_mode` 2, `jw_mode` 3, `rf1_mode` 4, `jw_prev` 3,
`rf1_falses` 3, `rf1_passes` 3, `f_mask` 6+1, `abortq`/`drainlate`/`ecunl`/
`jwlive`/`jwdrop`/`rf1counts`/`wdrained`/`post_destroy2` all ≥1 emission +
≥1 classifier or pin reference. **No dead state found.** The two plausible
dead-state candidates (`jw_prev`, `rf1_passes`' gate) were falsified above by
replay, not argued.

## Stop condition

The remaining weight in the r76 delta is all evidence-bearing: pins, the
`*_unp`/`unreached` witnesses, the mode guards (`dd_mode`/`wd_mode`/`rf1_mode`
gate emissions that would otherwise contaminate prior cells' receipts), and
the two falsified guards. The next deletion would remove falsifiability, so
this seat stops here.

## Evidence

- Reference: `corpus/live/r76-author/runs/love-20261014T182933442897Z`
  (r76-author rep 1, `totals cases=49 pass=49 fail=0`).
- Scratch trees (byte-copies of HEAD fixtures, battery + both probes):
  `corpus/live/r76-simplifier/{scratch,v1,v2,v3,v4,v5,v6}/`, built by
  `build_variants.py` (every replacement asserts its occurrence count and
  refuses on drift); diffs `v1.diff` … `v6.diff`.
- Runs: `runs-v0/love-20261014T183349105552Z`, `runs-v0b/…183547609885Z`,
  `runs-v1/…183503538238Z`, `runs-v2/…183514570588Z`,
  `runs-v3/…183526115413Z`, `runs-v4/…183537304848Z`,
  `runs-v5/…183615552924Z`, `runs-v6/…183625856575Z` (each with
  `verdicts.json` + per-cell receipts). Runs were serialized so the
  timing-measured lattice (`dt`/`popen`/`splice`) was not perturbed.
- Comparator: `compare.py` (read-only; separates the deterministic `iw-*`
  carrier from the timing-measured `probe.stdout`/`splice-*` carrier, which is
  **never** byte-comparable — two runs of identical bytes differ there:
  `dt_max_ms=1.097` vs `1.093`).
- Equivalence fuzz: `fuzz_v1_equiv.py` → `30 real + 200000 fuzzed;
  divergences: 0`, exit 0.
- Baseline control: two independent runs of the unmodified bytes gave 60/60
  strict and identical verdict rows, so the reference run is a valid
  comparator for the deterministic carrier.

## Device disclosures

- **`lsp` unavailable — recorded, not worked around.** No LSP server on PATH
  (`which lua-language-server lua-ls emmylua-ls pyright pylsp
  jedi-language-server` → none, exit 7) and the only MCP server configured
  for this session is a binary-analysis (Ghidra) provider exposing no
  `references`/`lsp` tool. The `references` device therefore could not answer
  any file, and there was no cold-start/empty-result state to mis-read. No
  grep output is presented as semantic proof anywhere in this report; the
  caller/equivalence claims rest on the replay receipts, the falsification
  runs, and the 200k differential fuzz.
- **Shared-tree check.** `git diff --numstat` for
  `corpus/fixtures/love_battery.py` and
  `corpus/fixtures/love_phys_probe/main.lua` is **empty** — the two files the
  r76 diff touched are byte-identical to HEAD, and I edited no tracked file.
  `git status --porcelain` shows my artifacts only as untracked entries under
  `corpus/live/r76-simplifier/`. Two pre-existing tracked modifications
  (`corpus/live/r72-simplifier/snapshots/log.txt`, mtime 12:35;
  `corpus/live/r72-simplifier/watch.log`, mtime 11:57) predate this seat and
  are not mine. Observed drift outside my scope: the untracked residue file
  `corpus/fixtures/__pycache__/love_battery.cpython-314.pyc` was present at
  seat start and absent at seat end (sibling r76 seats were writing
  concurrently — `r76-critic.md` 15:36:28, `r76-reviewer.md` 15:36:19,
  `r76-baseline.md` 15:37:01). I did not touch it; every command I ran used
  `python3 -B`, so I neither created nor removed bytecode caches.

## Cross-seat relation (context, not authority)

Reviewer F2 flagged the same two-enumeration disagreement; this report adds
the pre-r76 measurement that dates the drift to r76 and supplies a
replay-proven deletion shape for it. The critic's knockout table (§2.1,
`abortq`/`drainlate`/`ecunl` emission blocks → `anomaly`) proves the
classifier's conjuncts bite; P1 changes no conjunct, so that table still
holds under P1 and was re-derived by the 200k fuzz.

## Bounded claims

This host, LOVE 11.5, Python 3.14.7, HEAD `6ca715d`. Byte-identity is claimed
against the named reference run, on the deterministic `iw-*` carrier only.
P1's generality is claimed for the 29-key input space the fuzz sampled, not
for all conceivable receipts. W1 is claimed semantically identical, not
byte-identical. No claim is made about pygame/other probes (untouched
controls) or about any build other than the pinned one.
