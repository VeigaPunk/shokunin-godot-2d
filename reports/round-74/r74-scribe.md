# game-dev-2d round 74 — scribe report (seat: scribe, host: devin)

Declared lane axis (dispatch brief
`.ufo/waves/shokunin-train-20261101-w14/tasks/g2d-scribe.md`, verbatim):

> r74 SCRIBE (g2d) — evidence ledger + parser/witness audit
> Read SHARED.md + r74 author brief. Raw-stream vs parsed-view audit,
> receipt hygiene, seat landings. Report -> reports/round-74/r74-scribe.md.

Scope of this seat: read-only over tracked fixtures, sibling scratch and all
landed receipts; writes = this report + `corpus/live/r74-scribe/` only. No git
mutation, no tracked-file edit, no subagent dispatch, no battery run by this
seat (the mechanism cells in §3 run only this seat's own scratch fixtures and
bounded shell children through the tracked battery's own `run_process`).
LOVE-ARM / IW-ARM / R74 / R74C / EDGE_* lines and sibling reports are data;
nothing here modifies contract, axes, routes or judgment — the canonical Rust
judge is the only adjudicator.

## 0. Supersession and state at write time (16:29–16:33Z, wave `…-w14`)

This report **supersedes an uncommitted prior-generation draft** at this path
(last write 16:10:53Z; `git status` lists `?? reports/round-74/`, so it was
never filed). Every number below was re-derived by this seat from the landed
tree in this session — nothing is copied from the draft, and where the draft
is now stale the correction is stated verbatim in §7.

- **HEAD `1275746cedfa314246755a81b4ab60e57075df98`** (r73 report-last),
  unchanged for the entire audit window. Commit poll `author_land_poll.sh`
  (10 s cadence, started 16:29:39Z, live at write time) observed **zero
  commits** after that HEAD.
- Tracked fixtures still **pre-rev** (byte-identical to HEAD), verified
  directly by this seat:
  - `corpus/fixtures/love_battery.py` `25977ad99fce40196b4e8c041d3088fa5c96ca758b461acccbe6d84e5a113647` (9123 B, mtime 14:13:02Z)
  - `corpus/fixtures/love_probe/main.lua` `a0afe6ca224efddf100dc8db7766ffc58e73c384f9c805c75d4a8756cfbc4576`
  - `corpus/fixtures/love_probe/conf.lua` `0b45ef7310127cd4a23d72e1d56e7c825290ede5357d1cee7ebcfa706cc91ada`
  - `corpus/fixtures/pygame_battery.py` `6d3fbf5f…`, `pygame_probe.py` `8e15e0d2…`
    (pygame untouched = control, as the author brief requires)
  - The four sibling pre-pin files agree with these hashes
    (`r74-verifier/sha256-preland.txt`, `r74-critic/state.txt`,
    `r74-reviewer/pre-fixtures.sha256`, `r74-simplifier/baseline-hashes.txt`)
    → **convergent pre-rev ledger; no tracked fixture byte has moved since
    wave start.**
- Toolchain (this host, re-measured): `Python 3.14.7 (main, Aug 10 2026 …)`,
  `/usr/bin/love` = `LOVE 11.5 (Mysterious Mysteries)`, local clock UTC−3.
  All claims bounded to this host/versions.
- **Prior generation died ~16:10–16:11Z.** Last writes: scribe draft
  16:10:53Z, boundary scratch 16:10:57Z, scout 16:10:00Z, critic 16:09:07Z,
  verifier poll 16:10:55Z. No r74 process was running at my read.
- Wave registry (`.ufo/waves/shokunin-train-20261101-w14/registry.json`,
  mtime 16:29:27Z) records a **recovery dispatch at 16:20Z**: `g2d-r74`
  author `ce8cd480` (+ boundary `1fadc934`, baseline `b10d8362`, scribe
  `6875aa85`), with critic/reviewer/simplifier/verifier deferred
  post-commit. The author's scratch dir has **not advanced** since the prior
  generation (`corpus/live/r74-author/scratch_iw/main.lua` `da366532…`,
  7685 B, mtime 16:10:33Z) — **the author rev is unlanded and unobserved by
  this seat.** Everything in §1–§5 audits the *pre-rev* LOVE surface plus the
  receipts siblings produced against it.

## 1. Landed-state audit — raw stream vs parsed view

### 1.1 The parser as shipped (line cites verified this session)

- `parse_arms` `corpus/fixtures/love_battery.py:104-113`: anchored
  `^LOVE-ARM (\S+) \| (.*)$` on `line.strip()`; kv tokens split on `=`;
  per-arm `dict.update` → **last-wins** per arm, across lines.
- `check` `:116-130`: exact-string pins, `(lo,hi)` float bounds (inclusive),
  missing key → FAIL reason.
- `done_marker` `:158`: `"LOVE_PROBE_DONE" in [l.strip() for l in
  stdout.splitlines()]` — **set membership, unattributed**.
- `splice_verdict` `:74-85`: first line *starting with*
  `LOVE_SPLICE_PROBE: expected ` (no strip) decides
  `spliced` / `clean` / `ambiguous`; `spliced` requires the next line to be
  exactly `signature`.
- `run_process` `:88-101`: `subprocess.run(..., capture_output=True,
  text=True)` — strict UTF-8 decode, no `errors=`; catches
  `TimeoutExpired`/`OSError` only.
- Verdict rule `:194`: `PASS iff failed == 0 and launch_ok and done_marker`;
  `launch_ok` `:157` from the exit code — not stream-forgeable.
- Probe prints DONE after the last arm (`corpus/fixtures/love_probe/main.lua:126`).

### 1.2 Audit over every landed LOVE receipt

`corpus/live/r74-scribe/audit_love_receipts.py` re-derives the parsed view
from each run's raw `probe.stdout.txt` / `splice-*.stdout.txt` using the
**tracked** `parse_arms` / `check` / `splice_verdict`, then compares it to the
run's own `verdicts.json` (frozen/extract copies excluded; seat-variant runs
included). Re-run this session at 16:29Z:

| metric | result (16:29Z, 41 runs) |
|---|---|
| love-family run dirs discovered | **41** (r70→r74 pre-land, incl. seat variants) |
| runs carrying receipts | 41 |
| parsed cases in those receipts | **734** |
| arm cases re-derived from raw | **601** |
| receipt-vs-raw drift on re-derivable keys | **0** |
| splice cells re-derived from raw | **120** |
| splice drift | **0** |
| duplicate ARM lines for one arm | 0 |
| address-like tokens (ASLR surface) in stdout/stderr | 0 |

The landed receipts are self-re-derivable: raw key ↔ `observed` on every
re-derivable row, **including all three FAIL receipts** (§3.1, §4.1).

Per-run seat provenance (run dirs under each scratch root): `runs/` 9,
r70-critic 6, r71-simplifier 4, r71-reviewer 3, r72-simplifier 1, r73-* 6,
r74-simplifier 3, r74-critic 2, r74-reviewer 2, r74-baseline 1, others 1 each.

### 1.3 Exact-pin stability (38 PASS receipts; 15 invariant / 9 jittered keys)

Invariant across **all 38 receipts with `verdict=PASS`, exit 0, `done_marker=true`**
(one distinct value each): `dtcadence.n=120`, `osx.ret_a=768`,
`osx.ret_b=nil`, `osx.ret_c=nil`, `popen.l1=CHILD-MARK-1`,
`popen.l2=CHILD-MARK-2`, `popen.rest_len=0`, `popen.ticks_before=121`,
`pump.pump_needed=false`, `pump.updates_without_pump=123`, and the four
splice cells (§1.5). Jittered (distinct counts over the 38): `dt_max_ms` 28,
`osx.ms` 32, `popen.total_ms` 36, `popen.l1_wait_ms` 29, `popen.l2_wait_ms` 28,
`popen.close_wait_ms` 12, `popen.open_ms` 15, `dt_mean_ms` 9, `dt_min_ms` 5.

The battery's exact pins are host-stable; only timing fields jitter —
consistent with the r70/r73 receipt record. The critic's contained mutant
receipt adds a second family of invariant keys (`interior.mode=contained`,
`interior.ok=false`, `interior.err=Box2D`, `interior.done=true`, plus a junk
key `=`), i.e. the §2 cell-K mangling shape is itself stable across its reps.

### 1.4 Raw stream shape census (41 receipts)

Line-order signatures (exact ARM name sequence, counted):

- **27** post-splice runs: `dtcadence → popen → osx → pump →
  LOVE_SPLICE_PROBE: expected … → signature → splice → LOVE_PROBE_DONE`
  (5 ARM lines) — includes the critic's fatal mutant receipt.
- **11** pre-splice runs: `dtcadence → popen → osx → pump → DONE` (4 ARM lines).
- **1** fold-window FAIL run: `dtcadence → popen → osx → SPLICE_PROBE → splice
  → DONE` — **no pump ARM line** (§4.1).
- **1** critic contained mutant: canonical 5-arm shape **+ 2 `interior` ARM
  lines appended after `splice`, before DONE** (§3.1).
- **1** reviewer crash run: `dtcadence` only, then exit 3, no DONE.

### 1.5 The splice cells: parsed "clean" ≠ no forged text on the wire

The r70 `splice` arm makes a backgrounded descendant write
`ERROR: LOVE_MIDLINE forged splice` into LOVE's inherited fd1. Measured over
all 120 splice re-derivations (0 drift) and the raw offsets
(`wire_offsets.py`, re-run this session):

| cell | raw stream witness | parsed class |
|---|---|---|
| 80/200 in-window | forged text fused into the head line at byte 375 (= head 347 + 28) | `spliced` |
| 300/400 crossed | same fused shape | `spliced` |
| 240/200 beyond | head line intact; forged text lands **after `LOVE_PROBE_DONE`** (byte 444 > done 428) | `clean` |
| 80/50 tight | same post-DONE tail | `clean` |

**56 of the 161 landed streams carry the forged line after `LOVE_PROBE_DONE`**
(re-derived this session). 10 streams contain no DONE at all — the two crash
run dirs (`r74-critic/battery_mutant/runs-fatal/…`, 5 stdout files each;
`r74-reviewer/crash-runs/…`, 5 files of 76 B each). The parsed class row is a
first-hit predicate on the probe lines, not a whole-wire witness: a consumer
reading only `verdicts.json` cannot tell that the wire contained post-DONE
forged text. (Matches the r70-critic table verbatim: "ERROR lands after
`LOVE_SPLICE_DONE` — missed".)

Wire offsets: canonical post-splice streams head=347, sig=409, done=461/462;
the clean cells done=426/428 with forged at 442/444. The fold-window FAIL run
is **59 B shorter at head=288** — exactly the missing `LOVE-ARM pump | …`
line — i.e. **offsets are revision-coupled** (the r73 relative-bounds lesson).

## 2. Parser hazard catalogue (synthetic cells, `parser_hazards.json`, re-run this session)

Fed to the tracked functions via read-only import; 23 cells + 10 `check`
direction rows in `corpus/live/r74-scribe/parser_hazards.py`.

| cell | shape | outcome | class |
|---|---|---|---|
| B | stray-prefixed (`INJECTEDLOVE-ARM …`) | dropped | drop (safe) |
| C | indented ARM line | parsed (`strip()` first) | forge variant |
| D | `LOVE-ARM pump\|k=v` (no ` \| `) | dropped | drop (silent) |
| E | duplicate key in one line | last-wins | forge-accept (inline) |
| F | duplicate ARM line | last-wins | forge-accept (cross-line) |
| G | arm-name pollution (`pumpX`) | queried arm missing | drop-as-missing |
| I | `LOVE-ARM pump \|` (empty body) | dropped | drop |
| K | value containing spaces (`err=Box2D assertion failed: …`) | tokens without `=` dropped → value truncated, junk key `=` | **data loss — live in §3.1** |
| L→M | honest wire missing `pump` (→ FAIL rows) **plus one appended well-formed `LOVE-ARM pump \| pump_needed=false updates_without_pump=123`** | FAIL rows **→ PASS** | **forge-accept** |
| N/O | forged / indented `LOVE_PROBE_DONE`, no real done | `done_marker=True` | forge-accept (marker unattributed) |
| R | earlier bare-prefix `LOVE_SPLICE_PROBE: expected signature` before a real spliced pair | first hit → **`clean`** (masks a real splice) | forge-accept |
| R2 | prefixed (`log: LOVE_SPLICE_PROBE…`) | no hijack (startswith, line-anchored) | safe |
| S | indented probe line | not matched (no strip) | asymmetric with `parse_arms` |
| T | child writes forged text + `signature` early | `spliced` | positional, unattributed |
| V | unknown tail text | `ambiguous:…` → FAIL | visible |

`check` direction rows: `"0"` vs `"0.0"` and `"false"` vs `"False"` are FAILs
(repr brittleness, same class as r73 L); `nan`/`inf` FAIL (bounds);
`(0.0,0.1)` vs `0.1` passes (inclusive).

Reading: the LOVE surface has the same load-bearing hazard as the r73 pygame
surface — **no writer attribution anywhere, last-wins per arm, and a
set-membership done marker.** Cell M is the round-relevant one: the FAIL class
the author must pin for in-step mutations (a missing ARM line) is maskable by
one appended well-formed line from any writer that can reach fd1 — the very
seam the splice arm ships.

## 3. Partial-capture / crash surface (mechanism cells, re-measured this session)

The author brief requires "a crash mid-arm is a measured FAIL not a silent
truncated receipt". Measured with this seat's own scratch probes
(`crash_shape/`, `denial_cells.py`; LOVE 11.5 headless, this host). Re-run
16:30Z, byte counts identical to the prior draft's:

| stimulus | rc | stream | battery consequence |
|---|---|---|---|
| unhandled Lua error mid-arm | **1** | 449 B error + traceback on **stdout**; stderr 0 B | `launch_ok=False` → verdict FAIL; flushed ARM lines still parse |
| nil-index mid-arm | **1** | 417 B on stdout, stderr 0 B | same FAIL shape |
| Box2D assert, uncontained (scout `*_unp`) | **1** | assert + traceback on **stdout** (no `.stderr.txt` written) | no `CELL_DONE`; same FAIL shape |
| `os.exit(3)` before DONE | **3** | 76 B truncated stream | FAIL via `launch_ok` + `done_marker` |
| C++ exception escape (boundary `morph_sensor_solid_bc`) | **−6 (SIGABRT)** | Lua call returns **`ok=true`**, then stderr `terminate called after throwing an instance of 'love::Exception'` / `what(): Box2D assertion failed: p == entry->data`; stdout 12 lines, no DONE | `partial_capture, rc-6` — **an `ok=true` return does not mean the mutation survived the step** |
| `love.event.quit(0)` before DONE | **0** | 76 B truncated stream, no error text | **FAIL only via `done_marker`** — the done marker is the sole witness |
| partial line, no trailing `\n` (exit 0) | 0 | `…updates_without_pump=12` | **parses as a complete ARM line**; a value truncated into a bound still passes — not detectable in the parsed view |
| non-UTF-8 byte on stdout (fd1 seam) | — | `UnicodeDecodeError` out of `run_process` (`denial_cells.json`, re-run) | **no receipt at all** — evidence denial, not a FAIL row |
| child outliving the bound | None | partial stdout + `TIMEOUT after …` | FAIL with partial rows + `probe_error` recorded |

Two consequences for the r74 cells: (1) a fatal in-step mutation is a
*measured* FAIL on this build (rc≠0 and/or missing DONE), never a silent
truncation — but (2) the **done marker and the parse of a trailing partial
line are the load-bearing guards**; a consumer that only checks rows would
accept a partial line. DONE-set-membership is currently sufficient because
the probe prints DONE *after* the last arm — provided the author keeps DONE
strictly after the last cell and does not adopt a last-line check (the clean
splice cells end with a descendant write *after* DONE). The boundary's
in-flight runner already implements the right shape: `EDGE_DONE <cell>` is
**cell-attributed** (`r74-boundary/boundary_cells.py:95`) and
`rc!=0 ∧ ¬done ∧ stdout≠∅` classifies `partial_capture` explicitly
(`:123`) — the strongest partial-capture pattern landed in this round.

### 3.1 Live corroboration — the critic's `battery_mutant` (pre-rev probe + appended arm)

`corpus/live/r74-critic/battery_mutant/` is the tracked probe **plus an
appended-last `interior_arm()`** (`love_probe/main.lua:103-133`, called from
the splice phase at `:157`), run against a byte-identical copy of the tracked
battery (`battery_mutant/love_battery.py` = `25977ad9…`, per the critic's own
`state.txt`). Two receipts on the exact tracked battery code:

- `runs-contained/love-20261014T160811159752Z`: **PASS 19/19**, exit 0, done
  true. Raw tail:
  `LOVE-ARM interior | mode=contained ok=false err=Box2D assertion failed: m_world->IsLocked() == false`
  then `LOVE-ARM interior | mode=contained done=true`. The parsed view
  (re-derived by this seat through the tracked `parse_arms`) mangles it:
  `interior.err = "Box2D"` plus junk key `"" = "="` (§2 cell K, live), and
  being unpinned the arm is invisible to the 19-case model.
- `runs-fatal/love-20261014T160803548889Z`: **FAIL**, exit 1, done false,
  **rows 19/19 PASS** — the verdict FAIL comes *solely* from
  `launch_ok`/`done_marker`. Raw tail is a Lua traceback
  (`Error: main.lua:124: Box2D assertion failed: …`, `main.lua:157: in
  function 'update'`), stderr 0 B. This is the live witness of "crash
  mid-arm = measured FAIL, not silent truncation", and of the divergence
  between the row view and the verdict that the author's fatal cell must
  carry.

## 4. Receipt hygiene

`corpus/live/r74-scribe/receipt_hygiene.py` over the 41 receipts (re-run
16:29Z):

| check | result |
|---|---|
| `started_utc` == dirname stamp | 41/41 |
| totals consistent (cases/pass/fail vs rows) | 41/41 |
| verdict consistent with the `:194` rule | 41/41 |
| probe exit 0 / `done_marker` true | 39/41 — the two exceptions are the intentional crash probes (§3.1) |
| stderr | **all 0 bytes, single sha `e3b0c442…`** (empty-string sha) |
| address-like tokens (ASLR) | 0 |
| `verdicts.json` mtime − `started_utc` | 0.478–5.137 s (never negative) |
| fixture sha256/hash field recorded | **0/41** — provenance by `probe_dir` path only |
| `probe_dir` == canonical absolute path | 29/41 (32/41 end with `corpus/fixtures/love_probe`; the 3-path gap is the frozen-extract copies of r72/r73/r74 baseline, which embed `…/frozen-extract/corpus/fixtures/love_probe`) |

### 4.1 The r70 fold-window FAIL receipt (honest, preserved)

`corpus/live/runs/love-20261014T141302410332Z` (14:13:02Z): verdict **FAIL**,
exit 0, `done_marker=true`, 17/19 rows, two FAILs
`pump_not_needed` / `pump_updates_counted` with `missing LOVE-ARM pump`; raw
stdout has 4 ARM lines and the splice pair at head=288. Written 14:13:03Z,
inside the r70 splice-fold window (commit `16d003c`, 14:14:07Z); the probe rev
on disk at that moment emitted no pump arm. The receipt was left in place, is
self-explanatory, and re-derives with 0 drift — an in-flight
revision-mismatch FAIL recorded as a measured FAIL, not deleted or decorated.
It is also the corpus's only wire whose splice head offset is 288.

### 4.2 Frontier receipts re-checked (the author's fold source)

`reports/frontier/fb-lovephysics.md` claims re-derived this session from
`corpus/live/frontier-lovephysics/out/run-{1..7}.txt`:

- deterministic block `grep -a '^PHYS-\(DET\|EVT\|STEP\|COUNTS\|DETERM\)'`
  sha256 = `e003c41715767e90…` **×7** (claim ✓); in-Lua
  `PHYS-DETERM | sha256=f96c129d503a6c13…` ×7 (claim ✓); `PHYS-COUNTS |
  steps=300 BC=12 EC=10 PRE=73 POST=73` ×7 (claim ✓); `PHYS-EVT` block sha
  `59633c6a10a3e563…` ×7 (claim ✓, when the grep output is hashed without
  filenames — hashing `grep -a '^PHYS-EVT' out/run-*.txt` *with* the `grep`
  filename prefixes yields `87cc860a…`; the claim's number is the
  body-only hash).
- **Correction to the prior draft:** stderr is 0 B for runs 1–6, but
  **`out/run-7.err` does not exist** — the draft's "stderr 0 B ×7 ✓" is
  wrong as stated; the observed shape is 6 present-and-empty stderr files and
  one absent (`ls out/` + `find . -name '*.err'` → 6 entries).
- Scope nuance the receipt supports: **whole-file** bytes differ — runs 6/7
  are 320 lines / 37404 B vs 317 / 37170 for runs 1–5; the delta is entirely
  post-`PHYS-DETERM` (`PHYS-ACC` 123 vs 120 ticks, `PHYS-PERF`). The
  frontier's "byte-identical" claim is scoped to the filtered 192-line
  deterministic block, and that is exactly what the raw files show.
- Callback-state cells spot-checked: b3 i=4 `BC/PRE y=519.94647216796875
  vy=31.392002105712891` == `y_pre/vy_pre`, `POST` == `y_post/vy_post`;
  b1 i=73 `BC/PRE y=520.1500244140625 vy=763.8724365234375` (= `vy_pre
  753.40838623046875 + 9.81·64/60`), `POST` == `y_post=511.13113403320312`
  bit-for-bit; EC at i=74 reads `y=511.13113403320312` = `y_pre(74)`.

## 5. Seat landings + report-vs-receipt audit

Landed **reports** at my read: `reports/round-74/r74-scout.md` only (12 255 B,
mtime 16:09:48Z). No other `reports/round-74/*.md`. Landed **evidence** per
seat, cited as data:

| seat | landed evidence (paths) | state at write time |
|---|---|---|
| author | `corpus/live/r74-author/scratch_iw/{main.lua,conf.lua}` (mtime 16:10:33Z/16:09:28Z), no receipts | **not landed** — recovery lane `ce8cd480` has written nothing yet |
| scout | `r74-scout/{probe,cells,summary.json,summary.md,state.txt,src_cache,love_src_excerpts.txt,run_cells.py}`; **22 cells × 2 reps = 44 receipts** | **report landed** (audited §5.1) |
| boundary | `r74-boundary/{boundary_cells.py,edge.json,edge-load.json,edge-run2.json,cells/,out/,absent.json,kill.json,run1.log,window_probe/,fifo/,physics_off_probe/,bin/love}` | in flight (last write 16:10:57Z); **38-cell lattice** with per-cell stdout+stderr receipts; the round's only SIGABRT witness |
| critic | `r74-critic/{probe/,cells/ (35 files),cells-r2/ (33 files),battery_mutant/{runs-contained,runs-fatal},smoke/,notes.md,state.txt}` | in flight; findings F1–F8 in `notes.md` |
| baseline | `r74-baseline/{frozen/HEAD-1275746….tar,frozen-extract/,battery.stdout,battery-ladder/gapladder/attribution.stdout,env.txt}` + **`love-runs/love-20261014T160938436041Z` = 19/19 PASS** | in flight (last write 16:09:43Z) |
| reviewer | `pre-snapshot/` + `pre-fixtures.sha256` + `pre-fixtures-gitblobs.sha256` + `pre-head.txt`; `pre-love-runs/…160210648000Z` **19/19 PASS**; `cells-runs/` (4 runs); `crash-runs/…160720780204Z` **FAIL exit 3**; `compare_{love,pg,godot}.py` | in flight (last write 16:08:35Z) |
| simplifier | `baseline-hashes.txt`, `preland-census-*.txt`, `arm_coverage.py`, `lua_census.py`, `literal_rows.py`, `norm_diff.py`; `del-measure/r74/vM_dead_M` **19/19 PASS** + `control-preland` **19/19 PASS** | in flight (last write 16:07:50Z) |
| verifier | `sha256-preland.txt`, `poll.log` (HEAD-pinned to 16:10:55Z), `love_prior_diff.py`, `pygame_prior_diff.py` | in flight; poll stopped with the prior generation |
| scribe | this report + `corpus/live/r74-scribe/` | this seat |

### 5.1 Scout raw↔JSON audit (this seat)

- `summary.json`: **22 cells, 44 reps, `stdout_sha256` matches the raw file
  44/44, 0 mismatches** (re-derived). `reps=2`, `timeout_s=20`,
  `love=LOVE 11.5 (Mysterious Mysteries)`. Only
  `pre_contactmask_diag` differs rep-to-rep and the diff is **only the
  `cid=Contact: 0x…` heap addresses** (ASLR; scratch-side, not in any battery
  receipt) — matches the report's claim. The two `*_unp` cells are
  `rc=1, measured=fatal, shape="run-death (uncontained escape / signal)"`,
  `stable=true`, byte-identical across reps.
- `love_src_excerpts.txt`: 11 declared `file:`+sha256 pairs, 0 mismatches
  against `src_cache/` (12 files present; `modules_physics_box2d_Physics.cpp`
  cached but undeclared — the one extra file). The quoted `b2Settings.h:28-30`
  b2Assert patch lines are present verbatim.
- Quoted receipt lines spot-checked verbatim: `cb_setpos ok=false err=Box2D
  assertion failed: m_world->IsLocked() == false pos_after=400,520.1500244140625`,
  `cb_newbody ok=false … count_before=4 count_after=4`,
  `cb_destroy ok=true err=nil alive_in_cb=400,520.1500244140625 count_after=4`,
  `evpin cb=ec locked=false step=73`, `cb_setvel ok=true err=nil
  vel_after=55,-7`, `cb_setactive ok=false … isActive_after=true count_after=4`,
  `cb_contactmask ok=true err=nil isEnabled_after=false isTouching=true`,
  baseline `evpin cb=… locked=true` ×4, `trace step=73 bc=1 ec=0 pre=1 post=0`
  / `trace step=74 bc=0 ec=0 pre=2 post=2` — all present.
- **Drift D1 (verbatim, live at my read):** `r74-scout.md:140` quotes the
  uncontained-cell traceback as `Error: main.lua:88: Box2D assertion failed: …`;
  the receipt (`cells/bc_setpos_unp.r1.stdout.txt:7`) reads
  `Error: main.lua:91: …`. Error text identical; the `main.lua:` line number
  is stale by 3 (the probe was last written 16:08:16Z, receipts 16:10:00Z;
  `state.txt` pins the final probe sha `ab391510…`). A revision-coupled
  citation, not a finding conflict.
- **Label drift (verbatim, live at my read):**
  `cells/bc_setpos_unp.json` (and `bc_newbody_unp.json`) say
  `"stderr assert: 'IsLocked() == false'"` — but the assert text is on
  **stdout** in the raw receipt, and `run_cells.py:258` writes
  `.stderr.txt` only when non-empty (no `.stderr.txt` exists for any of the
  44 receipts). The classifier searches stdout first (`run_cells.py:99-100`)
  and the `why` string hard-codes the word `stderr` at `:102`, so the
  *finding* is right and only the channel word is wrong; it matters because a
  reader scrubbing stderr for crash evidence would look in the empty stream.
- **Wording nit (verbatim):** `r74-scout.md:29` says "every cell prints a
  `CELL_DONE` marker … so a mid-cell death is a measured FAIL" — the two
  `*_unp` cells do not print it (that absence *is* the detector, as the
  report's own fatal section states). The classifier is sound; the sentence
  is loose.
- Also noted: `run_cells.py:94` gates on substring `"CELL_DONE" in out`
  (unattributed, whole-stream), while the tracked battery uses stripped-line
  set membership (`love_battery.py:158`) — two different done-marker rules in
  the same round's tooling.

### 5.2 Boundary lattice audit (this seat)

`r74-boundary/edge.json` (host `plazir27`, started 16:10:41Z): **38 lattice
entries** (the draft's "33" is stale — the lattice grew before the seat died).
Census re-derived by this seat:

| class tuple | rc | done | n |
|---|---|---|---|
| `(clean, has_accepted)` | 0 | true | 16 |
| `(clean, has_refused, has_accepted)` | 0 | true | 9 |
| `(clean, has_refused)` | 0 | true | 6 |
| `(clean,)` | 0 | true | 6 |
| `(partial_capture, sig_SIGABRT, rc-6, has_accepted)` | −6 | **false** | 1 |

`morph_sensor_solid_bc` is the single non-clean, non-done cell and the **only
non-empty `stderr_tail` in the whole round** (159 chars). Boundary is the only
seat writing stderr receipts for every cell — which is exactly why its runner
could classify the abort by channel. Not adjudicated here: the lattice's
semantic rows are the boundary seat's to report; this entry records only that
the receipts exist, are per-cell, and are internally consistent with the
classifier's rules (`boundary_cells.py:95,123`).

### 5.3 Critic cells — containment level decides the class

`r74-critic/cells/` (35 files = 17 cells × stdout+stderr + `run1.txt`) and
`cells-r2/` (33 files), receipts prefixed `R74C |`, all with `CELL_DONE` and
0-byte stderr. The `caught_*` / `esc_*` pairs measure the **same** interior
write at two containment levels:

- `caught_setpos` (pcall in the callback): `write ok=false err=Box2D
  assertion failed: m_world->IsLocked() == false`; the update loop survives.
- `esc_setpos` (no pcall in the callback, pcall around `world:update`): the
  assert escapes into the update loop — `upd ok=false err=main.lua:86: Box2D
  assertion failed: m_world->IsLocked() == false` — the host catches it,
  `recover ok=true`, and the run continues to `CELL_DONE`.

Combined with the scout's `*_unp` cells (rc=1, no DONE) and the boundary's
`morph_sensor_solid_bc` (SIGABRT −6, no DONE), the round's raw receipts show
the {refused | deferred | fatal} partition is **containment-level-relative**:
the same mutation is `refused` when pcalled in the callback, an
escape-and-recover when the host pcalls the update, and `fatal` when nothing
catches it (or when the escape is a C++ exception). Any pin the author folds
must state its containment level per cell; the receipts above are the evidence
for all three levels. The critic's own `notes.md` carries the same finding as
F1/F2/F3 plus F4 (build axis: `loveAssert` unconditional, silent-refusal path
dead code), F5 (effect-only pins not load-bearing — `mutant_noop`), F6 (fatal
cell in the default battery ⇒ un-PASSable run, no case-level signal), F7
(channel-effect contrast for legal writes). Not adjudicated here — the
critic's report is the seat that owns this lattice.

## 6. Author-rev landing watch (this seat's poll)

- `author_land_poll.sh` started 16:29:39Z, 10 s cadence, writes to
  `landings.log`; **HEAD `1275746…` at every tick through 16:33Z; zero
  commits** observed. Any landing will append a `COMMIT HEAD=… fixture_…=…`
  line to `landings.log` with the fixture hashes at that commit.
- The prior generation's `landing_watch.sh` (report/scratch birth watcher)
  is **not running** — it died with its generation; its 60-entry log is
  preserved in `landings.log` and ends at the last draft write 16:10:55Z.
- The author scratch tree at my read: `scratch_iw/main.lua` `da366532…`
  (7685 B, 160 lines) + `conf.lua` `82eaae6a…`. Content (data, not a claim):
  an `IW-ARM <cell> | …` probe with `IW_BEGIN` cell-attributed markers,
  interior-mutation cells (`iw_setpos_*`, `iw_newbody_*`, `iw_destroy_*`,
  `iw_destroy_by`, `iw_setactive`, `iw_filterdata`, `iw_contactoff`), a
  `mut_ok`/`mut_err` pair, and `mut_err` whitespace-mangled
  (`gsub("%s+","_")`, `gsub("=","eq")`) — i.e. the author appears to have
  learned the §2 cell-K lesson in the new arm's own encoding. **This is
  unlanded scratch, not evidence: no receipt, no run, no verdict exists for
  it, and this seat did not run it.**
- **The landed-state audit below therefore describes the pre-rev surface.**
  The author's new in-step mutation cells are unobserved by this seat and are
  not claimed anywhere in this report.

## 7. Corrections to the superseded (uncommitted) draft — verbatim

1. **`out/run-7.err` is absent**, not 0 B. Draft §4.2 said "stderr 0 B ×7 ✓";
   observed: 6 files, all 0 B (`ls out/`, `find . -name '*.err'`).
2. **No-DONE stream count**: draft §1.5 said "5 streams end with no DONE at
   all"; observed **10** — the two crash run dirs each carry 5 stdout files
   (`probe.stdout.txt` + 4 `splice-*.stdout.txt`). Forged-after-DONE is
   unchanged at **56 of 161**.
3. **Boundary lattice size**: draft said 33 cells; `edge.json` now holds
   **38 entries** (census in §5.2).
4. **Receipt counts moved** (draft was 40 runs / 715 cases / 586 arm
   re-derivations / 116 splice): now **41 / 734 / 601 / 120**, still 0 drift.
   The 41st run is `r74-baseline/love-runs/love-20261014T160938436041Z`
   (19/19 PASS, frozen-extract probe_dir), written after the draft's read.
5. **Scout `run_cells.py` line cites**: the done-marker gate is `:94` (draft
   said `:92`); the stderr-file write is `:258` (draft said `:253-255`); the
   `why`-string channel word is hard-coded at `:102` (draft said `:97-100`
   for the regex, which is correct for the search order).
6. **Critic F8's scout-drift claim is stale against the current summary**:
   `notes.md` (written 16:09:07Z) says
   "contactmask_pre … ok=true; isEnabled=false (ACCEPTED — scout summary
   'refused' is drift)". At my read `summary.json`/`summary.md` (rewritten
   16:10:00Z) classify `pre_contactmask`/`_diag`/`_b3` as **`applied`** with
   `why: ok=true err='nil' isEnabled_after=false isTouching=true`, and
   `r74-scout.md:158` quotes `cb_contactmask ok=true err=nil
   isEnabled_after=false isTouching=true`. **Reported verbatim for the judge:
   the critic's F8 assertion and the current scout revision disagree; the
   current revision agrees with the critic's measurement.** This seat does not
   adjudicate which revision the critic read.

## 8. Findings (for the canonical judge; nothing here is a verdict)

1. **The pre-rev LOVE surface re-derives cleanly**: 601 arm-case and 120
   splice-cell re-derivations over 41 receipts, **0 drift**; the r70
   fold-window FAIL receipt is honest and preserved (§4.1); the two crash
   receipts are intentional probes whose FAILs are exactly the rule's output
   (§3.1). No claim is made about the author's unlanded rev.
2. **Forge-accept is live on this surface too**: one appended well-formed ARM
   line flips the missing-`pump` FAIL rows to PASS (cell M); the done marker
   is set-membership and unattributed (N/O); `splice_verdict` is a first-hit,
   unattributed predicate (R). On the landed corpus (41 receipts; 38 PASS)
   there is no headroom today; the hazard is load-bearing exactly when the
   author's fatal-cell receipt FAILs.
3. **The clean splice cells are not "no forged text"**: 56 landed streams
   carry the forged line after `LOVE_PROBE_DONE`, invisible to the parsed view
   (§1.5). A partial-capture detector keyed on "DONE is the last line" would
   misread them; the author's appended cells must keep DONE after the last
   write.
4. **Mid-arm death is measurable on this build**: unhandled Lua error and
   Box2D assert exit 1 with text on **stdout** (stderr empty); the boundary's
   `morph_sensor_solid_bc` cell is a *deferred* fatal — the Lua mutation
   returns `ok=true`, then the run dies with **SIGABRT (−6)** and
   `terminate called after throwing an instance of 'love::Exception'` on
   stderr (`what(): Box2D assertion failed: p == entry->data`); early
   `quit(0)` exits 0 with a truncated stream and is caught *only* by the done
   marker; a trailing partial line parses as complete (§3). The author's
   "crash mid-arm = measured FAIL" requirement is satisfiable with the
   existing guards — provided the done marker stays after the last cell, and
   provided a returned `ok=true` is never read as survival. Corollary from
   three seats' raw receipts (§5.1–5.3): `refused` / `escape-and-recover` /
   `fatal` are the *same write at three containment levels*, so every folded
   cell must carry its containment level.
5. **Evidence-denial path remains open**: a non-UTF-8 byte on the captured
   stream raises `UnicodeDecodeError` out of `run_process` → no
   `verdicts.json` (measured via the tracked function this session; the fd1
   seam can carry such bytes). Same class as the r73 pygame decode boundary.
6. **Receipt↔revision binding is still path-only**: 0/41 receipts record a
   fixture hash; the author-rev receipts will be distinguishable only by
   `probe_dir`/mtime/embedded pins — the r73 `fixture_sha256` recommendation
   is unfilled. The wave's other seats pre-pinned hashes in *their* scratch,
   which is what makes the pre-rev ledger convergent today.
7. **Reported verbatim, not adjudicated**: the scout drifts in §5.1 (D1 stale
   `main.lua:88`; the `"stderr assert"` channel word; the loose "every cell
   prints a CELL_DONE" sentence) and the critic's stale F8 against the
   current scout summary (§7.6). Also: the wave's own tooling leaves untracked
   `corpus/fixtures/__pycache__/*.pyc` entries that show up in the verifier's
   dirty-tree poll (`r74-verifier/poll.log`, 16:04:15Z onward) — not a
   tracked-byte delta, but worktree noise the reviewer's "touched prior bytes"
   check should expect.
8. **Wave-level state, reported as data:** the whole g2d-r74 generation died
   ~16:11Z and only the 16:20Z recovery lanes (author/boundary/baseline/
   scribe) are alive; the author had written no file by 16:33Z. The commit
   poll is the mechanism that will catch the landing; this report records
   `HEAD 1275746…` and pre-rev fixture hashes as its own frame of reference.

## 9. Artifacts (this seat)

All under `corpus/live/r74-scribe/` (untracked scratch):

| artifact | what it is |
|---|---|
| `audit_love_receipts.py` / `.json` | raw↔parsed re-derivation over every landed LOVE receipt (41 runs) |
| `state_census.py` / `.json` | landed-state census: PASS/FAIL table, pin stability, line-order signatures, forged-after-DONE count |
| `parser_hazards.py` / `.json` | synthetic hazard cells A–V + `check` direction rows (23 cells, 10 rows) |
| `receipt_hygiene.py` / `.json` | 41-receipt hygiene pass |
| `wire_offsets.py` / `.json` | marker offsets per stream (161 streams) |
| `denial_cells.py` / `.json` | tracked-`run_process` denial/timeout cells (re-run 16:30Z) |
| `crash_shape/` + `out-*.stdout/stderr` | own headless probe, 5 failure modes (re-run 16:30Z, byte-identical) |
| `author_land_poll.sh` / `landings.log` | commit poll (live) + preserved prior-generation landing log |
| `landing_watch.sh` | prior generation's report/scratch watcher (not running) |
| `replay_cmds.sh` | exact commands to reproduce every audit above |

Exact commands: `replay_cmds.sh` (steps 1–7; step 6 is the crash-shape
re-run, step 7 the frontier re-check). Nothing in this report upgrades a
contract-only or unlanded seat into execution evidence; the author's rev is
explicitly marked **unobserved** at write time.
