# game-dev-2d round 89 — fold (r89-fold): correction queue applied — SP1 dead accumulator + F5 dead arms deleted (−51 lines), F1 stderr-fragment pin closes the demonstrated crash-cause blindness, reviewer custody items landed; 247-row battery green ×2 on final bytes

Seat `EXECUTOR` (fold) | lane `g2d-r89-fold` | host **devin**. Runtime **Godot
`4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`, `--headless`, 60 tps,
GodotPhysics2D), Python 3.14.7. Repo `~/Projects/shokunin/game-dev-2d-shokunin`.
Base HEAD **`ee20575`** (r90 author, 247 rows — custody free per the task card).
**No commit, no push; the only tracked-byte changes are the five files in §2.**

**`lsp` disclosure.** No `lsp` device exposed in this dispatch — the only MCP
server is `rea` (binary analysis); no GDScript/Python language server exists on
this host (same state as all r89 seats). All edits are textual; callers were
audited by complete occurrence enumeration (`bridge_hole`: dispatch lines +
definitions only; `names`: declaration + one append only) plus fresh-process
receipts. No cold empty result is recorded as absence.

**probeParent disclosure.** Zero descendants spawned — the one-labrat licence
was not needed: every queue item was discharged against fresh execution
receipts on this seat.

**Load regime.** Both batteries ran under foreign sibling load (loadavg
**55–104** during the window, 32 cores); run1's four failures are the
documented load-flake classes only (§4).

---

## 1. Queue items applied

| # | item (task card) | disposition |
|---|---|---|
| 1 | simplifier `f535ddb` SP1: remove `names` dead accumulator (−2) | **applied via `git apply`** of `corpus/live/r89-simplifier/r89-simplifier-fold.patch` → `geo2d_lattice.gd` sha `9784716b…` → **`608a322e…` (579 lines) — `cmp` byte-identical to the simplifier's proven `fixtures-after/geo2d_lattice.gd`** (the byte-identical battery was already proven by that seat on the 235-row block; final-bytes proof on 247 rows is §4) |
| 2 | critic F1 (`68756af`): `lineempty` crash-cause-blind — add stderr-fragment pin | **applied**: new `required_stderr` mechanism in `run_battery.py` (`proc_stdout`/`proc_stderr` captured via `run_process_streams`, merged byte-identically; fragments `'Clipper2Lib::Point<double>'`, `"Assertion '__n < this->size()' failed."` must appear on stderr AND the signature is anchored to stdout). Discrimination demonstrated, §3 |
| 3 | critic F5: delete dead arms `bridge_hole`/`bridge_hole2` + falsified comment | **applied**: both dispatch entries and both arm bodies deleted (−49), incl. the falsified *"merge() of a contained square yields TWO contours"* comment (the round's own measurement shows merge collapses containment to k=1; `clip` is the hole-producer — pinned by `contain`/`ring*` rows). Overrides the simplifier's SP2 keep-disposition per the task card; scout `run_cells.sh`/`RECEIPTS.md` evidence untouched (historical receipt drivers now hit the census fallback — disclosed) |
| 4 | reviewer `61355e2`: custody items + A-list where they touch armed rows | **applied in-part, scoped** — see §5 disposition table |

`git diff --stat` (final, uncommitted):

```
 corpus/.gitignore                      |  4 ++
 corpus/fixtures/geo2d_lattice.gd       | 51 -------------------
 corpus/fixtures/run_battery.py         | 91 ++++++++++++++++++++++++++++++----
 corpus/live/.gitignore                 |  6 +++
 corpus/live/r89-author/manifest.sha256 |  1 -
 5 files changed, 90 insertions(+), 63 deletions(-)
```

Fixture shas now: `geo2d_lattice.gd` **`dcce4c74…`** (530 lines, `--check-only`
rc=0), `input89_edges.gd` `601c223e…` (untouched), `project.godot` `8de8b3af…`
(untouched), `run_battery.py` **`2679180a…`**.

## 2. What changed in `run_battery.py` (+77/−14)

| site | change | why |
|---|---|---|
| `:417–441` comment | `9784716b…` → `dcce4c74…` r89-fold variant provenance (r90-comment precedent: *"folded variant of scout sha256 …"*); `23-cell` → `24-cell` (scribe A1b); lineempty block documents the new pin | comments must not falsify after the fold |
| `:604–619` | new `run_process_streams` — identical launch/timeout/OSError shape to `run_process`; merged concatenation reproduces `run_process` output byte-for-byte in all three paths | F1 needs per-stream content |
| `:765–766` | `execute` launches via `run_process_streams`; `output = proc_stdout + proc_stderr` (identical bytes) | single swap keeps all 240 CASES launch semantics unchanged |
| `:997–1014` | `required_stderr` dict keyed by case name (same shape as `expected_errors`): `geo2d_lattice_lineempty` → `('Clipper2Lib::Point<double>', "Assertion '__n < this->size()' failed.")` | the pin |
| `:1025–1033` | pin check: `all(fragment in proc_stderr)` AND `any(sig in proc_stdout)` | closes both demonstrated blind spots (foreign abort w/o the assert; stderr-only signature) |
| `:1043` | `record["required_stderr"]` (data field, `expected_errors` parity) | verdicts carry the pin applied |
| `:2423–2442` | census F6 guard: tuple signatures dispatch via `any(sig)` exactly as `execute()` does — a future envelope row gaining an entry classifies instead of `TypeError`-crashing the census | reviewer F6 (unreachable today — no envelope row has entries) |

CASES untouched: 240 5-tuples, names unique — the pin is harness-side, no row
bytes changed (`V2`-era invariants preserved).

## 3. F1 discrimination — demonstrated, not just asserted

`corpus/live/r89-fold/fp_pin_check.py` runs the production `classify_process`
(AST-extracted from the folded `run_battery.py`, segment sha **`749fa060…`** —
unchanged by this fold) **and** the pin predicate against fresh battery-shape
launches (`subprocess.run`, streams separate):

| probe | pre-fold `classify_process` on merged blob | post-fold (classifier ∧ pin) |
|---|---|---|
| folded `geo2d_lattice.gd --arm=lineempty` (real crash) | PASS | **PASS** (rc −6; both fragments on stderr; sig on stdout) |
| `fp_wrongcause.gd` (critic's probe: exact signature on stdout, then INF-vertex `clip_polygons` abort — `offset_polyline(∅)` never called) | **PASS** (the demonstrated false positive) | **FAIL** (0 B stderr → fragment missing) |
| `fp_stderr_sig.gd` (signature on stderr only, same wrong-cause abort) | **PASS** (false positive) | **FAIL** (signature not stdout-anchored) |

Receipts: `runs/fp_*.out/.err/.rc`, `runs/folded_lineempty.*`,
`runs/fp_pin_check.json` (`ok: true`).

Deliberately **not** pinned: the `c++/16/` header path (compiler-version-pinned;
the fragment pair already binds the Clipper2 assert class). Assert text is
toolchain-pinned — disclosed host-conditional token, same class as
`joys=0`/`nmethods=86`.

## 4. Battery verdicts — final bytes, ×2, sequential

`python3 run_battery.py --runs ../live/r89-fold/runs{1,2}` (sequential, not
parallel; battery launch shape = `subprocess.run`, 8 s bound/row).

| run | stamp | rows | verdict | fails |
|---|---|---|---|---|
| run1 | `20261015T221843471142Z` | 247 | **243 PASS / 4 FAIL** (rc=1) | `overlap`, `negative_transition`, `audio_bus_route_invalid_control` + `probe_error_clause_surface` (census cascade: the two dead rows' 3 allowlist entries went `dead_in_run` → `census_bare_classifier_consistent=false` — the designed cascade) |
| run2 | `20261015T222323179429Z` | 247 | **247/247 PASS — all green** (rc=0) | none |

- **r89 rows: 20/20 PASS in both runs** (18 `geo2d_lattice_*` + 2
  `input89_edges_*`); `lineempty` PASS with `required_stderr` populated in
  `verdicts.json`. **r90 rows: 12/12 PASS in both runs.**
- **run2 vs both r90-author canonical green runs** (`runs9`, `runs12` — the
  `ee20575`-era 247/247 runs): `common=247 new_only=0 old_only=0
  tuple_mismatches=0` — the fold is verdict-tuple-identical to canonical on
  every armed row. Normalized OUT-DIFFs vs greens: only the documented
  volatile classes (`mp_loopback` uids, `frames=` jitter, envelope-payload
  modes on `input_lattice_*`, `tween_flash` float) — tuple-neutral. r89 rows:
  zero tuple mismatches, zero normalized output diffs vs both greens (the
  `polyendpoly` GDScript backtrace `:577/:578` → `:526/:527` shift is
  normalized by the established `.<ext>:<N>` rule — declared at fold time,
  verdict-inert, exactly as the simplifier disclosed).
- **run1 vs run2**: `tuple_mismatches=4` — precisely run1's four flake rows;
  r89/r90 rows identical between the two.
- run1's four fails are exactly the documented load-flake classes: `overlap`
  (probe timing, seen in r90-author runs1/3/7/9/10/12/13 pattern),
  `negative_transition` (null `current_scene` SCRIPT ERROR under load —
  `r69-scribe.md:211`), `audio_bus_route_invalid_control` (audio under load —
  `r88-verifier2`), and the meta cascade that correctly fires when census
  entries die (seen identically in r89-author rep3 / both r89-simplifier runs
  / r90-author runs 3,6,8,10,11,13). **No new flake class appeared; nothing
  r89/r90-flaked.**
- Gate state, run2: `r89_expected_errors_all_matched=true`,
  `r90_expected_errors_all_matched=true`, `dead_entry_count=0`;
  `sf_meta PASS`. Run1: `r89/r90` gates `true` even under the cascade (dead
  entries were the two flaked non-r89/non-r90 rows).

## 5. Reviewer / A-list disposition table (queue item 4)

| id | item | touches armed rows? | disposition |
|---|---|---|---|
| reviewer **F1** | manifest self-entry + gitignored `runs/` make `r89-author/manifest.sha256` unverifiable from commit alone | custody | **applied**: self-entry dropped → `sha256sum -c` = **1712/1712 OK** (the 396 `runs/` receipts verify in-worktree; coverage retained — scout/boundary manifests also exclude themselves). The residual "commit-only checkout lacks `runs/`" is the established live-tree convention (r87/r88 identical); receipts are manifest-covered |
| reviewer **F2** | 1255 regenerable run-tree files + `.pyc`/`.godot/` committed | custody | **applied**: `corpus/live/.gitignore` gains `runs*/`, `**/__pycache__/`, `**/.godot/`; `corpus/.gitignore` gains `**/__pycache__/`, `**/.godot/` (covers the fixtures-side `.pyc` currently dirtying status). Tracked files unaffected; prevents the class recurring |
| reviewer **F3** | `r89-author.md` prose "SQUARE<ROUND<MITER" inverts the measured ROUND<SQUARE<MITER | report prose only — pinned tuple in CASES is correct | **not applied** (outside armed-row scope; noted for the ledger) |
| reviewer **F4** | rep4↔rep5 stability sentence incomplete | report prose only | **not applied** (same scope) |
| reviewer **F5** | `matched_lines` is data not gate | by design, consistent with r87/r88 | no action |
| reviewer **F6** | census `TypeError` on tuple signature | **armed file** | **applied**: envelope-aware `any()` dispatch at the census (§2) |
| scribe **A1/A1b** | "23-cell" count in fixture comment | **armed file** | **applied**: `24-cell` in `run_battery.py` comment |
| scribe **A7** | manifest self-entry | custody | **applied** (same edit as reviewer F1) |
| scribe A2/A5/A8/A9/A10 | scout/boundary wording items | report prose / consistent-as-landed | no action |
| scribe A3/A4 | unreceipted superseded launches; partially unreconstructible frequency table | advisory custody — cannot be retro-receipted | disclosed, no file action |
| scribe A6 | author "no commit" superseded | info/resolved | no action (ledger note) |

## 6. Evidence index (`corpus/live/r89-fold/`, `manifest.sha256` — 574 entries, all OK)

| artefact | path |
|---|---|
| battery run 1+2 (247 rows each) | `runs1/20261015T221843471142Z/`, `runs2/20261015T222323179429Z/` (`verdicts.json` `223d123c…` / `3898a562…`), `battery-run{1,2}.{stdout,stderr}` (stderr 0 B both) |
| green-run comparisons | `compare-run1-vs-greens.txt`, `compare-run2-vs-run1-greens.txt` (`corpus/live/r87-baseline/compare.py godot`, unmodified) |
| F1 discrimination | `fp_pin_check.py`, `runs/fp_pin_check.json`, `runs/fp_*.{out,err,rc}`, `probes/fp_{wrongcause,stderr_sig}.gd` (copied from `r89-critic`) |
| folded-probe arm receipts | `proj/` (folded fixture + byte-identical `project.godot`), `runs/geo_{lineempty,census,polyendpoly,ringhits}.fold1.{out,err,rc}` — all pinned PASS lines byte-exact vs CASES; `polyendpoly` backtrace declared at `:526/:527` |
| byte/sha state | `key-shas.txt`, `diffstat.txt`, `uptime.txt` |

## 7. Remaining risks / blockers

- **`lineempty` stderr pin is toolchain-pinned** (libstdc++ `__n < this->size()`
  + `Clipper2Lib::Point<double>` mangled name): a libstdc++/libc++ migration or
  a fixed empty-polyline path flips the row to loud FAIL — intended (the row
  now means "the Clipper2 empty-polyline assert fires", not merely "−6").
- F1's third gap (sig-class-only `expected_exit=-6` rows generally) is closed
  **only for `lineempty`** — `crash_spontaneous_sigabrt`/`crash_self_sigkill`
  keep the shared merged-blob convention (same shape, by design; no stderr
  assert exists there to pin).
- `polyendpoly` stderr `at:`/backtrace line numbers moved (`:577/:578` →
  `:526/:527`, `_run` → `:108`) — normalized by the compare tool, declared.
- Deleting `bridge_hole`/`bridge_hole2` stales the verbatim-probe sha chain
  (`9784716b…` citations in r89 manifests/reports stay accurate as *history* —
  `run_battery.py`'s comment now records the folded variant, r90-comment
  precedent). The scout's `run_cells.sh` driver, if replayed verbatim, hits
  the `_:` census fallback for the two deleted arms — receipt evidence
  remains valid.
- Reviewer F3/F4 and scribe wording-only A-items left as historical dossier
  prose (armed-row scope per the task card) — listed above for the ledger.
- Foreign uncommitted file `reports/round-90/r90-scribe.md` present in the
  worktree — **not this seat's, untouched** (preserved).
- Blockers: **none**. Commit/integration decision stays with the operator.

Seat output complete.
