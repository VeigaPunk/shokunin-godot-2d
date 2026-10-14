# Round 66 — scout: rejection-clause SURFACE map (host: devin)

Recon only; no tracked edits. Scope kept: this report +
`corpus/live/r66-scout/` (scratch). Tree state at map time: HEAD
`2efaae2e554e` (r66-baseline frozen there), `corpus/fixtures/` clean —
`run_battery.py` sha256 `cd4824cc1a01…`, `descendant_pipe_probe.gd` sha256
`37cf50156839…`, both identical to the r66-baseline frozen blobs.

**Provenance note — mid-flight landing.** During this session the r66
author's uncommitted fixture diff appeared in the working tree:
`descendant_pipe_probe.gd` +65/−1 → sha `9ff5a9ae5757…`, adding exactly
the four arm shapes this map prescribes — `--spawn-allowforge`
(allowlist preemptor, echoes `save_corrupt_negative`'s byte-exact string
post-death), `--spawn-splitforge` (`ERR\n` + `OR: …` newline-split
evasion), `--spawn-seamforge` (descendant-authored stdout-tail
`…ends in ERROR` unterminated + stderr-head `: SEAMFORGE phantom
fabricated line` — the concat-seam fabrication), `--spawn-midlineforge`
(pre-death fixed-offset mid-signature splice, dual-clause corruption) —
plus `ALLOWFORGE/SPLITFORGE/SEAMFORGE/MIDLINE` consts and the docstring
arm map naming `probe_error_clause_surface`. `run_battery.py` was still
`cd4824cc` at report-write. The map below was made against the HEAD bytes
(correct: the seat maps the pre-author surface); the in-flight diff
confirms arms (a), (c-evasion), and (c-fabrication) verbatim. I did not
re-run anything against the modified fixture.

**Tooling note:** no `lsp` device is exposed to this seat — text search +
targeted reads used (documented fallback per seat card). `run_battery.py`
was read in full (2006 lines); every symbol cited below is direct source
evidence, not grep sampling. The verbatim classifier was executed for all
synthetic arms via `ast.get_source_segment` extraction (r65-boundary
method — zero re-implementation drift).

**Bottom line:** all four declared edges were already *measured* at r65
(critic + boundary seats, scratch-only) but none is *tracked*. The surface
map below localizes each clause to exact `run_battery.py` lines, enumerates
the allowlist census against the real 87-row receipt, names the arms that
discriminate each clause (the r65-boundary `proj_edge` fixture already
carries most of them, measured), and pins the insertion points. One new
runner-side gap surfaced during mapping: `run_process` propagates
`UnicodeDecodeError` on invalid-UTF-8 child bytes — a descendant `\xff`
write crashes the whole battery mid-run (observed, synthetic `sh` child,
this host).

## (1) The error path, exactly — `run_battery.py:160-177`

```python
def classify_process(code, error, output, expected_exit, signature, allowed_errors=()):
    lines = output.splitlines()                       # :161 — Python splitlines
    def allowed_error(line, allowed):                 # :162 — per-line preemptor
        stripped = line.strip()                       # :163 — strip before ALL match forms
        if stripped == allowed: return True           # :164 — exact form
        if allowed.endswith(","):                     # :166 — ","-prefix form
            return stripped.startswith(allowed) and stripped.count("ERROR:") == 1
        if allowed == "ERROR: chain incomplete":      # :168 — structured form
            return (stripped.startswith("ERROR: chain incomplete collections=")
                    and "scene=SceneB:<Node#" in stripped
                    and "old_alive=false" in stripped
                    and stripped.count("ERROR:") == 1)
        return False                                  # :172
    unrelated_errors = [line for line in lines if "ERROR:" in line        # :174
                        and not any(allowed_error(line, allowed) for allowed in allowed_errors)]
    return (code == expected_exit and error is None and signature in output    # :176
            and not unrelated_errors and "SCRIPT ERROR:" not in output         # :177
            and "Parse Error:" not in output)
```

Observed facts:

- **Line geometry is mixed.** The `ERROR:` scan is *line-local* substring
  (`"ERROR:" in line` over `output.splitlines()`); `SCRIPT ERROR:` and
  `Parse Error:` are *blob-global* substrings over the raw merged text, as
  is `signature in output`. Newline-split defeats the line-local clause;
  non-contiguity defeats the blob clauses; seam-contiguity fools both.
- **Allowlist match forms (hcom-shaped, three forms, checked in order):**
  (i) `stripped == allowed` exact — `strip()` makes it whitespace-pad
  insensitive (measured `b_exact_whitespace_pad` → absorbed); (ii)
  `allowed.endswith(",")` → `startswith(allowed) and count("ERROR:")==1`
  — admits an **arbitrary suffix** provided it contains no second
  `ERROR:` token; (iii) `allowed == "ERROR: chain incomplete"` → three
  substrings + `count==1`. Entry evaluation is per-line, any-match
  (`any(...)` at :175).
- **`count("ERROR:")==1` counts the whole line**, not the tail: an
  allowlisted line with *any* second `ERROR:` anywhere rejects
  (`b_prefix_tail_second_ERROR`, `b_exact_tail_second_ERROR`,
  `b_chain_two_errors` all → reject; the r65 critic measured the same on
  real output — "tail-forge defeats the allowlist"). Conversely a
  `,`-prefix entry absorbs arbitrary non-`ERROR:` suffixes
  (`b_prefix_forged_tail` → absorbed).
- **Redundant post-override:** `:449-450` re-checks
  `"SCRIPT ERROR:" in output or "Parse Error:" in output` after classify
  — strictly redundant: every caller passes the same `output` through a
  `classify_process` that already contains those conjuncts. Dead-redundant
  belt-and-suspenders, not a distinct surface.
- **`classify_streams`** (`:179-208`) is a different shape — stderr-lines
  only, any non-empty un-allowlisted stderr line rejects; **stdout is not
  scanned at all** (r65 boundary measured a stdout-carried forged error
  EVADE under it, `st_err_stdout` → True while merged cls → False).
  Its `line_allowed` has only exact + `,`-prefix forms — no structured form.
- **Universal funnel:** `classify_process` backs every verdict — CASES rows
  (`:447`), exports (`:312`,`:345`,`:1580`,`:1599`), mutants (`:367-377`),
  fault probes (`:234`), and every meta `inner_classification`
  (`:524`,`:644`,`:778`,`:1007`,`:1214`,`:1220`,`:1342`,`:1375`,`:1652`,
  `:1800`,`:1857`,`:1959`).
- **Merge shape:** `run_process` (`:149-158`) returns
  `proc.stdout + proc.stderr` — a pure concat with exactly ONE seam
  (stdout-tail → stderr-head), never interleaved. `errforge_run` `:1162`
  same. The gated reads (`:920-948`,`:1282`) instead append per-selector-
  event in **arrival order** — a different seam geometry (seams can occur
  anywhere). TimeoutExpired merges the same out-then-err (`:154-156`).

## (2) Dead-entry census — 43-key `expected_errors` dict vs the real receipt

Computed against `corpus/live/runs/20261014T043948860752Z/verdicts.json`
(87 rows, PASS — the r66-baseline-era battery) replaying `allowed_error`
verbatim per entry:

- **43 dict keys, all present in CASES (81 rows)**; `.get(name, ())` covers
  the 38 non-dict rows.
- **All 40 non-empty entries are TRIPPED by their row's captured output**
  (both `negative_transition` entries hit). Zero dead entries on the
  ordinary path.
- **`,`-prefix census (7 entries):** six are load-bearing prefixes — the
  child's emitted line continues past the comma with varying data
  (`button_activation_*` ` got focused=true receipts=0 text=Ready`,
  `animation_stuck` ` got 0.0`, `tween_no_start` ` transient_seen=…`,
  `contact_no_collision` ` start=(40.0, 36.0)…`, `audio_no_play`
  ` in_tree=true playing=false…`, `audio_bus_route_invalid_control`
  ` requested=NoSuchFixtureBus…`). The seventh, `save_process_missing`'s
  `"…signature=FILE_NOT_FOUND,"`, is emitted **ending exactly at the
  comma** (`save_process.gd:33` literal text) — it matches via the
  *exact* branch; its prefix semantics are dead-but-loaded: the entry
  still silently admits any `,…`-suffix forged continuation (prefix
  surface without prefix need).
- **3 dict keys map to `()`** — `slider_adjust_repeat_right_focus_restore`
  (:423), `…_second_focus_restore` (:425),
  `…_press_after_late_reconnect` (:429): documentation-only entries,
  semantically identical to the `.get` default. Dead entries, harmless.
- **`"ERROR: chain incomplete"` structured branch (:168-171) is unreachable
  on the 87-row path** — its only caller is `classify_mutant` for
  `mutant_broken_scene_route` (`:371-373`), exercised solely under
  `--probe-failing`. A live-shape / ordinary-path-dead clause.
- **`crash_self_sigkill` deliberately has no entry** — `OS.kill(own pid)`
  (`spontaneous_crash_probe.gd:18`) dies before any engine error line;
  captured output carries zero `ERROR:` lines. The allowlist-absent path
  is exercised by this row every run.
- **`SCRIPT ERROR:` / `Parse Error:` blob clauses are never tripped by any
  reachable fixture output** — no fixture script produces a script/parse
  error by design; the r65 critic noted they are exercised only by forgery.
  Live-but-unexercised scan clauses — prime census targets for
  forge-arm discriminations (measured `c_script_error_forged`,
  `c_parse_error_forged` → reject).
- **Adjacent dead surface:** stdin/ffmpeg-style notes N/A here; the only
  other allowlist consumer is `fault_injection`'s
  `fault_clean_expected_negative` (Python-subprocess arm, `--fault-injection`
  mode only) — the preemptor IS exercised there, on non-Godot output.

## (3) Line-faithfulness primitives

- The scan operates on **`str.splitlines()`** of the merged text — Python's
  11 boundary characters, not just `\n`. Scratch census (verbatim
  classifier, `ERR<x>OR:` token splits): `\n \r \r\n \x0b \x0c \x1c \x1d
  \x1e \x85 \u2028 \u2029` **all** split the token into two lines → all
  evade identically. A descendant has a wide evasion alphabet — e.g.
  `ERR\x0c`+`OR:` needs no newline at all (FF is a byte-level boundary).
  (`\x1f`, `\t` trivially evade by breaking the substring without
  splitting — different mechanism, same verdict.)
- **Fabricated lines land at two seams:** (i) the concat seam —
  `stdout` tail unterminated + `stderr` head, e.g. child prints
  `ending in ERROR` then `: PHANTOM …` reaches stderr — merged contains
  `ending in ERROR: PHANTOM …`, a line present in **neither** stream
  (r65-critic CE-2, real-pipe measured → reject; my `c_seam_splice_fabricated`
  → reject with `stdout_error_lines=[]`, `stderr_error_lines=[]`,
  `error_lines=[1 phantom]`); (ii) same-pipe interleave — two writers
  `<PIPE_BUF` chunks reassemble contiguously in-stream (boundary measured
  `--spawn-errforge-split` → detected; `--spawn-errforge-midline` corrupts
  the signature too). Symmetric blob fabrication: a signature or
  `SCRIPT ERROR:` split exactly across the seam completes and
  accepts/rejects (`c_seam_signature_splice` → PASS fabricated;
  `c_script_error_seam_splice` → reject fabricated).
- **Split markers land as evasion:** `ERR\n`+`OR:` leaves both halves as
  separate captured lines, neither containing `ERROR:` → record PASSes
  with the forged bytes in-capture (boundary `comm_err_newlinesplit` →
  True on real pipes; my `c_newline_split_evasion` → True). Blob clauses
  split the same way (`c_script_error_newline_split` → True).
- **NEW observed gap:** `run_process` catches only `TimeoutExpired` and
  `OSError` (`:153-158`). `subprocess.run(text=True)` strict-decodes —
  a child/descendant writing `\xff` raises `UnicodeDecodeError` **through**
  `run_process` → `execute` → `main` → battery dies mid-run (measured,
  `sh -c 'printf "\xff\xfe"'` this host). Same hole in every bounded-Popen
  `text=True` runner (`errforge_run` `:1157-1158`, gated captures use
  `errors="replace"` and are immune). A post-death descendant can kill
  the runner, not just the row.
- `output.strip().splitlines()` in records is presentation-only; verdicts
  read the raw merged string.

## (4) Fixture arms that discriminate each clause

Existing machinery to reuse: the stock reparenting gate
(`descendant_pipe_probe.gd:87-100` pattern), `errforge_run`-shaped bounded
Popen (`:1137`), `split_errforge_run` per-stream capture (`:1348`),
`reclassify_crash`-pattern captured-byte reclassification (`:523-526`).
The r65-boundary `proj_edge/descendant_pipe_probe.gd` (sha `dded5056…`)
already carries most arm shapes, measured on real pipes:

| declared edge | discriminating arm(s) | source of shape |
|---|---|---|
| (a) allowlist preemptor | `--spawn-errforge-allowlisted`: descendant echoes `save_corrupt_negative`'s exact string post-death → reclassify captured bytes under `()` → reject, under the matching tuple → absorbed; `write_ppid≠godot_pid` proves post-death authorship. Boundary-measured: `comm_err_allowlisted` False / `comm_err_allowlisted_allowed` True | boundary `:145-147` |
| (b) match-shape gates | same arm emitted as `"ERROR: <marker>,"`-prefix + forged tail; reclassify under `(prefix,)` → absorbed (arbitrary suffix), under `()` → reject; captured line + ` ERROR: x` appended → `count==2` → reject. Structured form: synthetic `chain incomplete` bytes under `(CHAIN,)` with/without `scene=SceneB:<Node#` | measured rows `b_*` in `surface-probe-results.json` |
| (c) newline-split evasion | `--spawn-errforge-newlinesplit`: post-death `printf 'ERR\n'` + `printf 'OR: …\n'` → captured bytes contain the forged token, no line contains `ERROR:` → inner cls **True**; pair with `--spawn-errforge-split` (no newline → contiguous → False) as the line-locality control | boundary `:142-144`, `:126-128`; measured `comm_err_newlinesplit` True / `comm_err_split` False |
| (c) splice fabrication | merge-seam: child `printraw("…ending in ERROR")` unterminated + post-death descendant `echo ': SPLICE…' >&2` → per-stream capture (`split_errforge_run` shape) proves the `ERROR:` line exists in neither stream, merged cls False. Same-pipe interleave variant already exists (`--spawn-errforge-split`) | r65-critic `splice_real.py` (real pipes, measured) |
| (c′) blob-clause twins | `--spawn-scriptforge-release` / parse twin: descendant writes `SCRIPT ERROR:` / `Parse Error:` post-death → rejects through the two never-exercised clauses; newline-split twins evade | measured `c_script_error_*` rows; r65-critic matrix |
| (d) dead-entry census | meta-side only: replay `allowed_error` over each row's captured output → `entries_tripped` / `entries_dead` lists + `()→3`, chain-incomplete-unreachable, `crash_self_sigkill` none-needed | this report §2; computable in-run at meta time |

No CASES-row additions needed — an expected-FAIL record stays
inexpressible (r62/r65 precedent); all arms are meta-driven bounded Popens
or pure captured-byte reclassification.

## (5) Insertion map

- **`corpus/fixtures/descendant_pipe_probe.gd`** (additive, mirrors r65
  `+35`): new consts after `ERRFORGE_ERROR` (`:67`) — e.g. a
  comma-bearing `ERRFORGE_PREEMPTOR` line, `SCRIPT/PARSE` forge texts;
  new arm flags in the docstring map (`:42-61`) and new `elif` branches in
  the spawn chain after `errforge_hold or errforge_release` (`:97-100`),
  reusing the stock reparenting gate verbatim. Boundary `proj_edge` is the
  drop-in template (its header comment must be rewritten — it's a scratch
  disclosure, not tracked-fitting).
- **`corpus/fixtures/run_battery.py`** (additive, mirrors r65 `+431`):
  new unconditional meta block `probe_error_clause_surface` inserted
  **after** the r65 error-spoof block ends (`print` at `:1541`) and
  **before** `if args.probe_failing:` (`:1542`) — the established
  append-only meta slot. Everything it needs is already in scope inside
  `main()`: `classify_process`, `pid_alive` (`:629`), `kernel_ppid`
  (`:781`), `gate_poll_tick` (`:895`), `scratch`, `args.godot`,
  `run_dir`, `detached` (r62 control), and the `errforge_run` /
  `gated_errforge_run` / `split_errforge_run` helpers defined at
  `:1137`/`:1226`/`:1348` (reusable directly or cloned to keep the r65
  record shape). Append one `results.append({"case":
  "probe_error_clause_surface", …})` row → 88 rows total; the 87 prior
  rows are untouched by construction.
- Expected discriminations to land (all already measured True on this
  host): allowlist-preempts-forged-error; prefix-admits-arbitrary-suffix;
  second-`ERROR:`-tail-defeats-allowlist; newline-split-evades /
  contiguous-split-detects; seam-splice-fabricates-reject (per-stream
  absence proven); script/parse blob clauses fire on forged writes;
  census counts (`tripped`, `empty-tuple=3`, chain-incomplete
  ordinary-dead); forged vs genuine `cases_visible` equality preserved.
- Watchpoint for the author: `errforge_run`/`split_errforge_run` are
  nested inside the r65 block and reference `errforge_signature` /
  `errforge_error` constants (`:1133-1134`) — a new probe can reuse the
  functions with new markers only if the marker constants are
  parameterized or the record fields renamed; cleanest is to clone the
  runner shape (the blocks are already near-identical three times over).
- Claim-wording watchpoint (from r65-critic CE-1, still true): the flip
  boundary is *capture-before-pipe-EOF*, not death-ordering — the same
  caveat must ride any r66 headline ("line presence" = *captured* merged-
  output line presence).

## Confidence and remaining unknowns

- Clause locations, match-order, merge geometry, census: **high** — direct
  source + verbatim-exec receipt
  (`corpus/live/r66-scout/surface-probe-results.json`, 22/22 discriminations
  hold under the production classifier) + the r66-baseline-era 87-row
  verdicts replay.
- Live-pipe truth of every arm shape: **high for most** — r65-boundary
  measured `newlinesplit`/`split`/`allowlisted`/`glue`/`midline`/`stderr`/
  `flood` on real Godot 4.7.2 pipes; merge-seam splice measured by
  r65-critic. Arms not yet run on real pipes: comma-prefix forgery,
  `SCRIPT ERROR:`/`Parse Error:` descendant arms (synthetic-only so far —
  blob-substring geometry makes outcome near-certain but unmeasured live).
- Unknowns retained: whether the author lands one combined
  `probe_error_clause_surface` row vs several; whether the decode-crash
  gap (`\xff` child bytes → `UnicodeDecodeError` mid-battery) is in scope
  for r66 — it is adjacent to, not inside, the declared four edges;
  multi-line `splitlines` behaviors under `\r\n`-mixed Godot output on
  non-Linux hosts remain unmeasured (Linux-only claim stands per r62-r65
  convention).

## Files written (inside brief scope only)

- report: `reports/round-66/r66-scout.md` (this file)
- scratch: `corpus/live/r66-scout/{surface_probe.py,
  surface-probe-results.json}`
