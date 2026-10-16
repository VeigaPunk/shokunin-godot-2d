# r96 simplifier — committed-tree audit of `89f85ed8`

**VERDICT: PROVEN-LEAN.** The committed r96 landing carries a verified
**−55-line, 33-site dead-weight fold** across six fixture files: every
proposed deletion was executed head-to-head against committed bytes —
**264 fresh headless Godot launches** (66 launches × 2 reps × committed
vs folded scratch trees) with **0 semantic diffs**, 0 missing PASS/FAIL
lines, identical exit codes. The audit also **caught and rejected one
static-scan false positive**: `var loaded = ResourceLoader.load(p)` in
`_arm_refuse` is *liveness-load-bearing* — folding it flips
`set_path_collision_refused=true→false`. Nothing was landed: this seat
reports candidates only; zero tracked writes, commit nothing.

Seat `SIMPLIFIER` (g2d lane r96) | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, `--headless`,
15 s per-launch bound, 2400 s battery bound), Python 3.14. Audit
target: commit `89f85ed844c27ffb2a1760cc359c334caa92ef1f` (*r96 author:
60 rows (426 total)*). All scratch work under
`corpus/live/r96-simplifier/` (gitignored); committed bytes staged at
`tree/` + `committed-tree/` via `git archive`/hash verification, never
the r97-dirty working tree.

**`lsp` disclosure.** No `lsp` device / no GDScript language server on
this host (unchanged lane state r89–r96, per sibling reports). Call-site
absence is therefore shown by text-grep **as the recorded literal
fallback** — never presented as semantic proof — and every load-bearing
claim is instead proven by fresh-process Godot execution on the
battery's own scratch shape. That choice was vindicated: the single
semantic regression found anywhere in this audit (`loaded`, §4) is
invisible to reference-counting and visible only to execution.

## 1. Audit scope and committed-byte verification

Target is the committed tree only — the working tree carries a foreign
r97 lane's in-flight landing (§7). Fixture snapshot
`tree/corpus/fixtures/` verified sha256-equal to `git show
HEAD:corpus/fixtures/*` for all eight audited files
(`head-check.txt`, `shas-committed.txt`):

| file | committed sha256 (truncated) | HEAD-verified |
|---|---|---|
| `scene_io_lattice.gd` | `8aeab1cb…` | identical |
| `r96b_cache.gd` | `f7d06de3…` | identical |
| `r96b_id.gd` | `53a63d65…` | identical |
| `r96b_phase.gd` | `4bb89614…` | identical |
| `r96b_seed.gd` | `69a6413f…` | identical |
| `r96b_seq.gd` | `3cae3659…` | identical |
| `r96b_var.gd` | `71653a79…` | identical |
| `run_battery.py` | `3118fb5a…` | identical |

Battery shape (`audit-battery.txt`): 419 CASES / 426 results incl. 7
meta rows; r96 block = 60 contiguous rows, indices 355–414; per-fixture
coverage 13/14/5/10/7/10/1 rows mapping 1:1 to arms except
`r96b_var --arm=idstat` which intentionally serves two rows
(`idstat_breadth`, `idstat_u31_gate`). No duplicate r96 case names; no
r96 signature is a prefix/substring of another signature.

## 2. Proven deletion candidates (fold executed in scratch, verified)

All folds preserve every emitted byte of every PASS line, every
diagnostic, every side-effecting call (`_mk_child`, `ResourceSaver.save`,
`_write_grad` all remain invoked), and all 16 expected-error matches.
Deltas measured `folded/` vs `tree/`:

### scene_io_lattice.gd — −12 lines, 8 sites
- `_arm_pack_basic`: `var child := _mk_child(root, "Child", …)` → bare
  call. The binding is never read; the call is load-bearing (packs the
  child) and stays.
- `_arm_det`: `var e2 := ResourceSaver.save(b, p2)` → bare call. `e2`
  never read (the arm pins `e1`/`e3` error codes); the save stays.
- Terminal `= null` cleanup stores after the last read, removable
  because Godot refcount teardown happens at scope exit regardless:
  `l1` (takeover), `cached/stale/repl/ign/ign2/ign3` (cache, −6),
  `spr.texture = null` + `gt` (subres, −2), `loaded` (extres, −1),
  `back` (editstate, −1), `loaded` (refuse, −1). **Note:** the refuse
  `loaded = null` *terminal* store is dead — the `var loaded =`
  *binding* is not (§4).

### r96b_cache.gd — −21 lines, 8 sites
- `_arm_deep`: `var e2 := _write_grad(dep, …)` → bare call (write
  side-effect kept; `e2` never read).
- Terminal `= null` stores removed after last read: deep (5),
  repl_uncached (3), reuse_delete (3), reuse_delay (4), ignoredeep (5),
  threaded (2) = 22 stores.
- Header arm-list comment corrected (comment-only, +1 line).

### r96b_id.gd — −4 lines, 4 sites
- `_sha_str` helper deleted (−6): **zero call sites** in committed
  bytes (grep fallback; corroborated by prior lane scan and by the
  full 264-launch run emitting identical output).
- `_arm_subsame`: `var e1 :=` / `var e2 :=` → bare saves; both
  `ResourceSaver.save` calls remain (the arm pins the resave id-law
  via `id1`/`id2` text diff, not error codes).
- Header arm-list comment corrected to the real 15-arm list
  (comment-only, +2).

### r96b_var.gd — −12 lines, 9 sites
- `_arm_lever`: `ps_ref` bookkeeping removed entirely — `var ps_ref:
  PackedScene = null`, `ps_ref = ps`, `ps_ref = null` (−3); `var e :=
  ResourceSaver.save(ps, p)` → bare call.
- Terminal `= null` stores: rich `ps/ps2/ps3` (−3), conn `ps` (−1),
  groups `ps` (−1), meta `ps` (−1), idstat `ps/ps2/ps3` (−3).

### r96b_seed.gd — −6 lines, 2 sites
- seedcheck `a/b/c/d = null` (−4), fresh2 `d1/d2 = null` (−2),
  all after the final print.

### r96b_seq.gd — net 0 lines, 3 sites
- `_mk_ext_scene` helper: `var e_ext := ResourceSaver.save(grad, ext)`
  → bare call **and** `e_ext` dropped from the returned
  `[mk.call(), mk.call(), loaded, e_ext]` array — the caller never
  reads index 3; the save side-effect stays.
- Header arm-list comment gains the missing `minimal` (comment-only).

### run_battery.py — comment-only (scratch copy)
- The folded copy carries two documentation edits for reviewer
  inspection: provenance noting the simplifier fold, and the stale
  gate comment "two whitelist-bearing cases … 15 entries" →
  "three allowlist-bearing cases … 16 strings" (actual committed state
  is 3 cases / 16 entries — ownership ×2, uid ×1, refuse ×13; the
  comment text was not updated when the uid entry was added).
  **Harness code is untouched; these are proposed comment fixes only.**

## 3. Verification method and results

`verify_folds.py` rebuilds each side's scratch project exactly as
`run_battery.py` does (fixture copy, project-name munge,
`controls/pickup.tscn` staging, causal-chain two-frame fix), then runs
all **60 r96 rows + 6 uncovered instrument arms** (`finger0`, `fresh2`,
`fingerB`-family boundary arms, `lattice_unknown`) × 2 reps per side,
`/usr/bin/godot --headless`, 15 s bound per launch:

```
committed scratch: 132 launches   folded scratch: 132 launches
diffs: []            no_pass_or_fail_line: []
raw byte diffs: 14 — all masked-equal (declared classes only)
```

Declared process-random / line-number masks (none is pinned by any
signature; `instability-probe.txt` documents each as process-random on
committed bytes too):

| mask | fires on | why non-semantic |
|---|---|---|
| `unique_id=\d+` | `twoext`, `extother` | minted ids are process-random by design |
| `res://*.gd:\d+` | `refuse` | backtrace line numbers shift under any deletion |
| `min=/max=/sample=` | `idstat_*` | process-random minted ids; only `n/distinct/gt2p31/pin_found/instantiate_ok` are pinned |
| `vals=/g1=/g2=` | `finger0`, `fresh2` | boundary instruments, not battery rows |

Key result: `set_path_collision_refused=true` on **both** sides after
the §4 fix; all 60 committed signatures emit byte-identically on the
folded tree.

Controls on the committed harness (`runs-control-clean`,
`runs-control`): **426/426 PASS each**, all 60 r96 rows green,
`r96_expected_errors_all_matched` satisfied — the loaded control ran
under 8 CPU hogs against the committed archive
(`committed-tree/…/run_battery.py`, sha `3118fb5a…`) precisely because
the working-tree harness was foreign-modified mid-session (§7).

Receipt census (`pin-census.txt`, 2256 receipts): 58/60 r96 rows have
signature-bearing receipts. The two STEM-ONLY rows (`extres`,
`pack_basic`) are the author's *declared* key folds — no historical
receipt can byte-match them by construction; both were re-verified
byte-exactly on this seat's own launches (PASS lines = CASES bytes).

## 4. Rejected candidate — the `loaded` liveness trap (headline)

`_arm_refuse` (scene_io_lattice.gd:752 committed):

```gdscript
ResourceSaver.save(Gradient.new(), p)
var loaded = ResourceLoader.load(p)   # NOT dead — do not fold
var other := Gradient.new()
other.set_path(p)
var collide_refused := other.resource_path == ""
```

Static scans (mine and the prior lane's) mark `loaded` never-read
after the binding — an apparent textbook dead store. Folding it to a
bare `ResourceLoader.load(p)` was **executed and regressed**:
`set_path_collision_refused` flipped `true→false`. The binding keeps
the cached resource referenced; without it the load's result drops to
refcount 0, the cache entry is collectable, and `other.set_path(p)`
no longer detects the collision the arm exists to pin. **Rejected;
binding restored and re-verified.** This is the load-bearing-liveness
class the seat card warns about: grep-clean is not dead for
cache-mode/RefCounted resources.

Also rejected/kept deliberately:
- `_arm_subextra`'s `_unused` underscore binding — kept; the
  `_`-prefix idiom *documents* an intentional discard, not dead weight.
- All other terminal nulls not listed in §2 (e.g. `pos` loop-carried,
  file-scope `arm/k/use_process`, `_parts` helper state) — false
  positives of the simple scope walk, verified live by inspection.
- `r96b_phase.gd`: **zero proven candidates** — every store is read or
  phase-load-bearing; left untouched in `folded/`.

## 5. Report-only findings (candidates, not folded — signatures pin the bytes)

- **Duplicate `key=` tokens inside emitted PASS lines**
  (`audit-battery.txt`): `no_ext_line` (extres), `header_has_uid`
  (uid), `sha`/`size`/`colors_match` (formats), `signal`/`to`/`method`/
  `from` (conn), `type`/`name`/`groups`/`unique_id`/`parent` (groups),
  `owner`/`name`/`ph`/`ed`/`kids` (editstate). Each pair emits twice
  per line; the first occurrence is dead output weight. **Not folded:**
  the signature pins the whole line, so removal is not byte-neutral —
  flagged for the author/integrator as a future-round convention fix.
- **Stale gate comment** (harness ~L3510): "two whitelist-bearing
  cases … 15 entries" vs actual 3 cases/16 strings — comment-only fix
  shown in the folded harness copy.
- **Stale header arm lists** in `r96b_cache.gd`, `r96b_id.gd`,
  `r96b_seq.gd` — corrected in the fold, comment-only.
- **Pre-existing duplicate signature groups outside r96**
  (`negative_overlap`/`negative_signal`, camera limits, buttons, r95
  celloff rows, crash/descendant-pipe controls): outside this lane's
  remit; recorded, not acted on.
- `audio_playback` wall-clock flake documented by the author: did not
  fire on this seat's runs (both controls 426/426); pre-existing,
  unrelated to r96 simplification.

## 6. Preserved contract

Emissions, exit codes, expected-error census (3 cases / 16 entries,
all live-matched), the `r96_expected_errors_all_matched` gate, all
historical/provenance comments, and every side-effecting call are
preserved. The fold is strictly weight removal: −55 net lines, no
renames, no new conventions, no second authorities.

## 7. Shared-tree state at report time

- `git rev-parse HEAD` = `89f85ed844c27ffb2a1760cc359c334caa92ef1f`.
- All seven r96 fixtures + `run_battery.py`: **byte-identical to HEAD**
  (re-verified sha256 at report time).
- Tracked diff vs HEAD is exactly the **foreign r97 lane's** in-flight
  work — `corpus/fixtures/run_battery.py` +60 lines (the `stree_lattice`
  block, referencing `reports/round-97/r97-author.md`) plus its
  regenerated `__pycache__/run_battery.cpython-314.pyc`, and untracked
  `stree_lattice.gd` / `r97_scene_*` fixtures. Content inspected: pure
  r97 additions, nothing r96-shaped; the block landed mid-session
  (working harness still read committed sha `3118fb5a…` at the 05:16
  clean control) — **not this lane's write**.
- This seat's writes: only under `corpus/live/r96-simplifier/` and this
  report. Zero tracked writes, zero commits, zero staging.

## 8. Evidence index (all under `corpus/live/r96-simplifier/`)

- `fold-verification.json` / `fold-runs/` — 264-launch committed-vs-
  folded diff (0 masked diffs, 14 raw diffs all in declared classes).
- `runs-control-clean/` + `runs-control/` — two independent 426/426
  batteries on committed bytes (one under 8-hog load).
- `deadstore-scan.txt`, `audit-static.txt|json`, `audit-battery.txt` —
  scope-aware store/coverage/duplicate scans.
- `pin-census.txt` — 2256-receipt signature census.
- `instability-probe.txt` — process-random token evidence.
- `fold-proposal.diff`, `folded/` — the proposed fold, reviewable.

## 9. Blockers

**None.** The lane is green end-to-end; the single semantic trap found
(`loaded` liveness) was caught by execution, rejected, and is
documented above as the reusable lesson for any future fold of
cache-adjacent probes.

— r96 simplifier, seat output; the canonical Rust runtime judges.
