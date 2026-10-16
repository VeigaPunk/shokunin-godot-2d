# r92 verifier — independent non-author verification of `5900431`

Seat `VERIFIER` (g2d lane r92, independent non-author) | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, `--headless`, 60 tps,
GodotPhysics2D), Python 3.14.7, 32 cores. Target:
`5900431f4a4a83ac7c38b1a2ce7aad179f7ff72b` (*r92 author: 14 tilemap rows
(272 total) — nav 2-payload envelope (boundary falsification folded), nullts
SIGSEGV armed rc=-6, tombstone encoding; 272/272 x2*). Receipts:
`corpus/live/r92-verifier/` (index in `RECEIPTS.md` there; `manifest.sha256`
342/342 OK, three scratch trees excluded by the manifest's scope header).
Author report: `reports/round-92/r92-author.md`; inputs:
`reports/round-92/r92-scout.md`, `reports/round-92/r92-boundary.md`.

**`lsp` disclosure.** No `lsp` device and no GDScript language server is exposed
to this seat (unchanged lane state); every semantic check below is an AST/static
read of the committed bytes plus fresh-process execution — the recorded
fallback. The change is one new fixture file plus an insertion-only harness
block (no renames, no symbol moves), so no symbol-aware operation was possible
or required.

**Frozen probeParent disclosure.** Exactly one read-only `ufo-labrat` (L2, agent
`9c32ddd9`) was dispatched with one bounded static hypothesis in four clauses:
(A) per-arm `_it` key set == committed signature field set for all 13 PASS arms;
(B) the nav envelope's two payloads differ only in `regions_f1`; (C) the
`about_to_call_tile_data=1` emission is the last `_it` before the crashing call
and that call is on line 927; (D) no `_it` emission follows `_pass()` in any arm.
It had **no exec tool**, wrote nothing, spawned nothing, and returned **A/B/C/D
all CONSISTENT** with line-cited evidence (arm-by-arm key sets: census 10, atlas
26, cells 39, custom 26, terrain 27, pattern 21, encoding 28, fixinvalid 6,
srcids 18, physics 22, timing 18, quadrant 11, nav 18; `_pass()` terminal at
L190/243/335/395/467/519/594/618/657/741/802/859/915). No second dispatch; its
null runtime scope is recorded, not silently omitted.

**Concurrent-worktree disclosure.** `git diff --quiet HEAD` was **rc=0** at
freeze time (00:15:42Z, before rep1). A **foreign r93 author** lane then edited
the shared worktree's `corpus/fixtures/run_battery.py` (mtime 21:34:55, +111/−0
in two hunks: an r93 CASES block after the nullts row at `@@ -694,6 +694,107`
and a new `r93_expected_errors_all_matched` gate at `@@ -2909,6 +3010,16`).
That edit is additive and touches **no** r92 row, r92 `expected_errors` entry,
`required_stderr` pin or the r92 floor gate. Nothing in this report reads the
worktree copy of the harness: all five battery reps ran the **frozen
extraction** (`git archive HEAD corpus/fixtures`), whose 78 files match their
git blob sha1s exactly (`freeze/blob-identity.txt`, 78/78, 0 mismatches). See
`freeze/concurrent-edit.txt`.

**No tracked writes, no commits.** All artefacts are untracked
`corpus/live/r92-verifier/**` plus this report.

---

## 1. Method — frozen committed bytes

- **Whole-repo content check at freeze time**: `git diff --quiet HEAD` → rc=0,
  0-byte stderr; `git status --porcelain` carried no tracked modification.
- **Fileset**: committed `corpus/fixtures` subtree = 78 entries
  (`git ls-tree -r --name-only HEAD corpus/fixtures`) vs 78 files in the
  extraction — **0 diffs** (`freeze/fileset-diff.txt`).
- **Blob identity**: every extracted fixture hashed as a git blob sha1 against
  `git ls-tree -r HEAD` — **78/78 match, 0 mismatches**.
- **Fixture shas (frozen)**: `tilemap_lattice.gd` `a699138945ec7c1c…` (929
  lines), `run_battery.py` `5e5182815e6e…` (4225 lines), `project.godot`
  `8de8b3af…`, `nav_lattice.gd` `088843399ce3…`, `geo2d_lattice.gd`
  `dcce4c749023…` — the first two byte-equal to the author's declared pins.
- **Provenance (byte-copy, no fold)**: the committed fixture's sha is identical
  to `corpus/live/r92-scout/probes/tilemap_lattice.gd`,
  `corpus/live/r92-boundary/probes/scout_tilemap_lattice.gd` and
  `corpus/live/r92-scout/proj/tilemap_lattice.gd` — **five-way byte identity**
  (`freeze/scout-to-committed.txt`). Every receipt in both upstream corpora was
  therefore produced by the same probe bytes that landed.
- **Commit scope**: 136 paths — `corpus/fixtures/run_battery.py`,
  `corpus/fixtures/tilemap_lattice.gd`, 133 under `corpus/live/r92-author/`,
  `reports/round-92/r92-author.md`. No other fixture, no `project.godot`.

**Harness delta `045d925 → 5900431`** (`probes/audit_committed.py` →
`audit-committed.txt`):

- `git diff --numstat` = **161 / 0**, four pure-insertion hunks at CASES
  `@@ -598,0 +599,98`, `expected_errors` `@@ -1067,0 +1166,44`,
  `required_stderr` `@@ -1093,0 +1236,11`, floor gate `@@ -2750,0 +2904,8`.
- CASES **251 → 265** tuples (all arity 5); the 14 `r92_tilemap_*` rows sit at
  indices **247–260**, immediately after `nav_lattice_teardown_clean` and
  immediately before `crash_spontaneous_sigabrt`; 265 CASES + **7** meta rows
  (`probe_save_independent_process`, `probe_spontaneous_crash_classification`,
  `probe_descendant_pipe_eof`, `probe_descendant_signature_spoof`,
  `probe_while_live_signature_gate`, `probe_descendant_error_spoof`,
  `probe_error_clause_surface`) = **272** result rows.
- 13 rows carry a scalar signature; `r92_tilemap_nav` carries a **2-payload
  envelope**; `r92_tilemap_nullts_crash` carries `expected_exit=-6`.
- `expected_errors` r92 entries: **9 cases / 18 lines**, all `shape: exact`;
  `required_stderr` r92: **1 case / 2 fragments**; the floor gate
  `r92_expected_errors_all_matched` (predicate
  `case.startswith("r92_")`) is present at harness line 2907.

---

## 2. Results per dispatch item

### 2.1 Battery ×5 on the frozen committed bytes — **two full greens, tuple-identical to both author runs**

| rep | window loadavg | verdict | r92 rows | failures |
|---|---|---|---|---|
| rep1 `…T001542945819Z` | 55.8 | FAIL 271/272 | 14/14 PASS | `nav_lattice_path` (r91 row) |
| rep2 `…T002302210530Z` | 61.3 | FAIL 270/272 | 13/14 | `overlap` (pre-existing class), **`r92_tilemap_nullts_crash` TIMEOUT** |
| rep3 `…T003135088173Z` | 51.3 | **PASS 272/272** | 14/14 | none |
| rep4 `…T003533246361Z` | 51.5 | **PASS 272/272** | 14/14 | none |
| rep5 `…T003933515651Z` | 53.7 | FAIL 271/272 | 13/14 | **`r92_tilemap_nullts_crash` TIMEOUT** |

- **rep3 and rep4 are tuple-identical (signature, verdict, actual_exit, error)
  to BOTH committed-worktree author runs** (`r92-author/runs4/…`,
  `runs5/…`) across all 272 rows — 0 mismatches, 0 row-set diffs — and to the
  r91 green on `77d2f7e` across the 258 pre-existing rows (0 mismatches).
  The committed bytes reproduce a full green in a different session under load.
- **Per-row stability** (`probes/r92-row-stability.txt`): 13 of the 14 r92 rows
  produced **byte-identical observed output in all five reps** (1 distinct
  shape each). Only `nullts` varies (exits `[-6, None, -6, -6, None]`).
- **All round gates true in all five reps**: `r87…r92_expected_errors_all_matched`
  (plus `phys2d`), `dead_entry_count=0`, `dead_entries=[]` in every rep.
- **Nav row matched payload[0] (`regions_f1=1`) in all five reps** — the
  production scheduler regime, as the author's two runs did.
- Prior-row identity vs the r91 green: rep1's only deviation is
  `nav_lattice_path`; rep2's is `overlap`; rep3/rep4 are 258/258 identical;
  rep5 is 258/258 identical. No pre-existing row drifted for an r92-attributable
  reason.

### 2.2 Fresh arms — **41/42 clean**; the 9 allowlists are load-bearing; the author's committed receipts re-check

14 arms × 3 fresh launches in the battery's launch shape on the frozen fixture
(`subprocess.run(capture_output=True)`, 8 s bound), receipts `arms/*.rep*.{out,err,rc}`,
re-classified with the **AST-extracted production `classify_process`**
(segment sha256 `749fa0607e7707e6…`, the same segment r89–r92 pinned and the one
the author's `verify_author.py` reports) plus the envelope / `required_stderr` /
stdout-anchor path (`probes/check_arms.py` → `check-arms.txt`):

- **41/42 OK.** The single non-OK receipt is `nullts.rep1` = the 8 s wall bound
  (rc `None`), i.e. the timeout hazard of §3.2, **not** a classification event.
- Every PASS-arm signature is matched as a **complete PASS line**; the row pins
  include the `PASS tilemap_lattice <arm> ` prefix, so there is no unpinned tail.
- **Allowlists load-bearing, mine**: all 27 allowlist-bearing receipts
  (9 rows × 3) classify PASS *with* the committed `expected_errors` and **FAIL
  bare** — without the entry every one of the nine rows is rejected.
- **Allowlists load-bearing, author's committed receipts**: independent
  re-classification of `corpus/live/r92-author/fresh-reps/*` (`probes/custody_check.py`
  → `custody-check.txt`) = **42/42 OK, 27/27 bare-rejecting**; the author's own
  `verify_author.py` reproduces `fails=0`; `manifest.sha256` verifies
  **1510/1510 OK** and covers every tracked `r92-author` file but itself.
- **Custody of the crash receipts**: my fresh `nullts.rep2` stdout is
  **byte-identical** to the author's committed `fresh-reps/nullts.rep1.out`, and
  stderr is identical modulo ASLR'd addresses; rc `-6` in both.

### 2.3 Fold 1 — nav 2-payload scheduler envelope: **HOLDS, and is exhaustive over the committed corpus**

- **Shape** (`audit-committed.txt`, labrat clause B): the two payloads are
  identical strings except `regions_f1=1` / `regions_f1=0`; **both** pin
  `regions_f2=1`; the settled field is therefore single-valued in both modes.
- **Exhaustiveness** (`probes/nav_envelope.py` → `nav-envelope.txt`,
  `nav-envelope-cells.txt`): every line-anchored `PASS tilemap_lattice nav …`
  receipt in the committed scout+boundary corpora — **136 receipts — matches
  exactly one payload, with residual = `''` (byte-identical to the pinned
  string); NEITHER = 0**: payload[0] = **90**, payload[1] = **46**.
- **Regime law** (per-cell recount): default `def20` 20/20 p0 · `ff120x20` 20/20
  p0 · `ff150x10` 10/10 p1 · `ff600x10` 10/10 p1 · `f10/f20/f30/f60/f120` all p0
  · `f600`, `ff600load`, the whole `scan` (ff240–900) and `scan2` (ff150–210)
  bands p1 · `t120` (120-tps project) p0 · `t120_ff120` p0 · `t120_ff240`
  (ratio 2) p0 · `t120_ff480` (ratio 4) p1. **Highest p0 ratio = 2.0, lowest p1
  ratio = 2.5, no receipt in between** — the harness comment's stated boundary
  (`≤ 2` → 1, `≥ 2.5` → 0) is exactly the observed partition.
- **Live crossing** (`probes/nav_envelope_live.py` → `nav-envelope-live.txt`):
  12/12 — default and `--fixed-fps 120` produce `regions_f1=1` (payload[0]),
  `--fixed-fps 150` and `--fixed-fps 600` produce `regions_f1=0` (payload[1]),
  each admitted by the row and by no other payload. Both modes are live shapes,
  not dead pins.
- **Discrimination** (`probes/classify_discriminate.py`): the live receipt is
  admitted; a synthetic payload[1] receipt is admitted; four single-field
  mutations of the PASS line (`regions_f1=7`, `regions_f2=0`,
  `regions_reenabled=0`, `nav_map_valid=0`) are **all rejected**.

### 2.4 Fold 2 — nullts SIGSEGV negative control: **the pin is correct; the row's wall-time margin is not** (F1)

- **Pin correctness**: 3/3 fresh launches rc=**-6** (SIGABRT after the engine's
  signal-11 handler), the stdout anchor `R92 nullts about_to_call_tile_data=1`
  present with **no** PASS line, and **both** `required_stderr` fragments on
  stderr (`handle_crash: Program crashed with signal 11`,
  `_nullts (res://tilemap_lattice.gd:927)`). The scout's own committed hazard
  receipts carry the identical pair, and line 927 is exactly
  `var td := layer.get_cell_tile_data(Vector2i(0, 0))` (labrat clause C; the
  `_it("about_to_call_tile_data", "1")` on 926 is the last emission before it).
  The author's correction of the scout's label is right: 134 = 128+6 is SIGABRT,
  not SIGSEGV; the Python returncode is -6.
- **Discrimination 7/7**: real receipt admitted; fragments-moved-to-stdout,
  signature-on-stderr-only, signature-absent, rc-flipped-to-0,
  one-fragment-removed, and a foreign signal-11 dump without the pinned
  fragments are **all rejected**.
- **Wall-time hazard (new evidence)**: the crash path costs **1.5–8.0 s**
  (n=20: min 1.521 s, median 5.334 s, max completed 7.909 s) against the
  battery's **8 s** per-case bound — **4/20 runs were killed at 8.018 s**
  (`probes/nullts_wall.py`, `arms/nullts_wall/`). A normal arm costs
  0.354–0.680 s (census/nav/encoding, n=8 each). In the battery itself the row
  timed out in **2 of 5 reps**; in the fresh sweep **1 of 3**. Aggregate
  **7 timeouts / 28 observations ≈ 25 %**.
- The hazard is **pre-existing, not introduced by r92**: the existing
  `crash_spontaneous_sigabrt` row timed out **2/6** in the same launch shape,
  while the two rows that abort *without* the engine's crash handler
  (`geo2d_lattice_lineempty` libstdc++ assert, `nav_lattice_teardown_crash`
  glibc abort) completed in **0.73–0.91 s, 0/12 timeouts**. The cost is the
  crash handler's dump/backtrace, and it is inherited by the new row.
- Failure direction is **loud** in every observation: `exit=None`,
  `error="TIMEOUT after 8 seconds"`, row FAIL — there is no mis-PASS shape.

### 2.5 Fold 3 — tombstone encoding: **HOLDS (47/47 independent re-derivations)**

`probes/rederive_encoding.py` decodes the pinned arrays with an independent
reader (2-byte format header + 12-byte records of six little-endian int16
fields) and cross-checks against the row's other pinned fields — the probe only
prints raw bytes, so nothing here trusts its own decoder:

- Header = 0 on all eight pinned arrays (matching the refusal message
  `Unsupported tile map data format: 513 … lower or equal to: 0`; 513 = 0x0201
  is the first two bytes of the 3-element input `[1,2,3]`); every length is
  `2 + 12k` with zero remainder; `stride == 12 == two_bytes_len − one_bytes_len`.
- Decoded cells match the independently pinned reads: `one_bytes` → (3,4) src 0
  atlas (1,0); `two_bytes` → [(3,4,0,1,0,0), (7,-2,0,0,1,0)] with
  `arr_roundtrip_used=n2[3,4;7,-2]`, `arr_roundtrip_atlas=0,1`;
  `alt_bytes` rec0 carries `alt_id_created` and its rec1 is a **tombstoned
  stale (7,−2) record** — the high-water-mark claim, visible in bytes.
- **Tombstone law (independently derived, and one of my own expectations was
  wrong)**: `erase_cell` and `clear()` write the **same** 8 × `0xFF` tail
  (fields 2–5 = −1) at **unchanged length**, preserving x/y;
  `tomb_erase_bytes == tomb_clear_bytes` exactly. My first check asserted a
  single trailing int16 — the artifact is right and my expectation was wrong;
  the corrected law is in the receipt (47/47 after correction).
- `truncated.resize(20)` leaves a 6-byte partial record → `truncated_len=14`
  (one record survives) with the pinned `Corrupted tile map data: tiles might be
  missing.` refusal; `short_arr_len=0`.

### 2.6 Fold 4 — `expected_errors` +9 with floor gate: **HOLDS**

- **9 cases / 18 exact-match lines** at harness lines 1174–1209, one per
  deliberate refusal class (atlas 2, cells 2, custom 3, terrain 1, pattern 1,
  encoding 2, fixinvalid 3, srcids 3, physics 1).
- **Coverage is exact, both directions** (`probes/classify-discriminate.txt`,
  fresh receipts): the nine arms emit **18 unique `ERROR:` lines**, and those 18
  are precisely the 18 pinned entries — no uncovered line, no dead entry. Where
  a line repeats (cells `p_coords` ×4, custom `ghost` ×2, pattern ×2, fixinvalid
  `id -1` ×2, physics ×2) one exact entry covers all occurrences, as the
  comments state.
- The harness's own census agrees in all five reps: 9 r92 rows, 18 entries, all
  `shape: exact`, `matched_lines ≥ 1`, `dead_entry_count=0`, `dead_entries=[]`,
  `r92_expected_errors_all_matched=true`. The **floor gate is live**: a dead
  r92 allowlist entry fails it loudly.
- `census`/`timing`/`quadrant`/`nav` carry no entry and emit no `ERROR:` line;
  nav's only stderr is the `make_polygons_from_outlines` deprecation WARNING
  (no `ERROR:` substring → classifier-inert), unchanged from the author's claim.

### 2.7 Signature coverage over the committed measurement corpus — **595/595 EXACT**

`probes/signature_coverage.py`: every line-anchored
`PASS tilemap_lattice <arm> …` receipt in the committed scout+boundary corpora
is **byte-identical to one of the committed signatures** (the pins include the
`PASS …` prefix, so EXACT = full line). atlas 36, cells 36, census 36, custom
36, encoding 36, fixinvalid 36, pattern 36, srcids 36, terrain 36, nav 136,
physics 46, quadrant 43, timing 46 → **595 receipts, 0 MATCH-with-tail, 0 MISS**.
No r92 PASS row admits a shape outside its pin.

### 2.8 Prior-row identity and stability

- rep3/rep4: **258/258** pre-existing rows tuple-identical to the r91 green and
  **272/272** to both author greens.
- The only pre-existing-row deviations across the five reps are the documented
  volatile classes (`overlap` in rep2) plus `nav_lattice_path` in rep1 (F4).

---

## 3. Findings (ranked)

**F1 (HIGH — operational flake in the new crash row; loud, never a mis-PASS).**
`r92_tilemap_nullts_crash` fails **~25 % of runs** at the battery's 8 s bound
because the engine's signal-11 crash handler spends 1.5–8.0 s printing the dump
and backtrace before `abort()`. Evidence: 4/20 standalone (`nullts_wall`), 1/3
fresh sweep, **2/5 battery reps** (rep2, rep5 — both `exit=None`,
`TIMEOUT after 8 seconds`); worst completed run 7.909 s against the 8 s bound
(margin 0.989). Normal arms cost 0.35–0.68 s. The **same hazard already affects
the pre-existing `crash_spontaneous_sigabrt` row (2/6 timeouts)**, while rows
that abort without the handler (`geo2d_lattice_lineempty`,
`nav_lattice_teardown_crash`) are 0/12 at 0.73–0.91 s — so this is an
engine/host property the new row inherits, not an r92 regression. Consequence:
the committed tree does **not** reliably produce a green battery (2 greens in 5
here; the author's "272/272 ×2" is reproducible, not guaranteed). Options are
for the operator: raise the bound for handler-crash rows, or reduce the dumped
backtrace. No artifact claim is falsified by this finding.

**F2 (LOW — comment/caption error; no landing effect).**
`corpus/fixtures/run_battery.py:1236–1237` says the nullts pin "binds the
**rc=-11** to the engine's own signal-11 crash handler". The pinned
`expected_exit` and the measured returncode are **−6** (SIGABRT after the
handler); −11 is the signal, not the exit. The same file states −6 correctly at
:634–637 and :687–694, and the author report's correction is explicit — so this
is a stale comment on one line, not a claim mismatch.

**F3 (LOW — evidence-caption counts do not match the committed corpus).**
My recount of the nav receipts is **136 = 90 payload[0] + 46 payload[1] + 0
neither**; the author report cites the labrat's "139 … payload[0]=93 …
payload[1]=46 … neither=0" and the harness comment cites "all 65 quiet/load
matrix receipts". The **invariant those counts support (a strict partition with
zero unadmitted shapes) holds exactly**; only the arithmetic differs. Method:
line-anchored `^PASS tilemap_lattice nav ` over `corpus/live/r92-scout` +
`corpus/live/r92-boundary` (loose greps also match the same strings embedded in
reports/JSON, which inflates a naive count — likely the source of the 139).

**F4 (INFO — one unreproduced failure of the r91 `nav_lattice_path` row).**
rep1's only failure: the arm returned a **2-point partial path** (missing the
first waypoint) with rc=0 and no error, i.e. the known load-conditioned
query/settle margin of an r91 row. It is **0/20 standalone**
(`probes/path_stability.py`), was not seen in r91's five reps, and cannot be
attributed to r92: the r92 rows are inserted at CASES 247–260, strictly after
every `nav_lattice_*` row, so the arm's execution context is unchanged.
Recorded, unresolved, pre-existing class.

**F5 (INFO — the author's green battery runs are worktree-only).**
`corpus/live/r92-author/runs{1..5}/` (incl. both greens) are gitignored and not
in `5900431`; the commit carries the five `battery*.log` files and the 42
fresh-rep receipts. My byte-identical comparison therefore used worktree
artefacts, and the durable green substitute is this seat's own rep3/rep4
(`runs/20261016T003135088173Z/verdicts.json`,
`runs/20261016T003533246361Z/verdicts.json`, untracked receipts). Same class as
the r91 verifier's F5.

**F6 (INFO — argv[0] text in the crash dump).** The author's receipts resolve the
binary as `/usr/bin/godot(+0x…)`, mine as `godot(+0x…)`; ASLR'd addresses and
that path text are deliberately unpinned, and both receipts carry the two pinned
fragments verbatim. No effect; recorded because the raw dumps differ.

---

## 4. Residual risks / disclosures

- **R1 — the 8 s bound vs the crash handler (F1).** Any row that routes through
  the engine's signal-11 handler has a load-dependent wall time; the new row and
  `crash_spontaneous_crash`/`crash_spontaneous_sigabrt` share it. Failure is
  loud; the risk is a non-green wave, not a false PASS.
- **R2 — the envelope's second payload is unreachable inside the battery.** The
  battery launches no case under `--fixed-fps`, so payload[1] is only produced by
  an external harness. It is a **live** shape (verified 12/12 at ff150/ff600) and
  the settled `regions_f2=1` law is pinned in both payloads, so the admitted
  extra mode is the boundary-measured scheduler flip and not a defect — but the
  battery alone cannot discriminate it.
- **R3 — build/host tokens.** `class_method_counts`, enum orders, `srv_methods`-
  class values, 4-dp vertex floats (`travel=0.0000,1.9531`), the glibc
  `double free or corruption` fragment and the pinned
  `_nullts (res://tilemap_lattice.gd:927)` site are engine/toolchain/line-number
  conditional; each flips loudly. The `:927` token is bound to this frozen
  probe's line numbering by design.
- **R4 — nav's deprecation WARNING.** The nav row's stderr carries only the
  `make_polygons_from_outlines` WARNING (no `ERROR:` substring, classifier-inert
  today); a future classifier that tightens WARNING handling would reject the
  row. Author-disclosed (scout hazard #11), unchanged.
- **R5 — 60-tps-conditioned reads in the r91 rows** (`nav_lattice_path`'s
  settle margin, R2/R3 of the r91 report) remain the source of the r91-class
  flakes; F4 is one instance.
- **R6 — foreign worktree churn.** An r93 author is editing `run_battery.py` in
  the shared worktree right now (additive, does not touch any r92 row/entry/gate).
  Any commit that folds it is a new artefact set whose r92 rows would need a
  diff-scoped re-check. Nothing in this report reads those edits.

## 5. Blockers

None. Shipping/admission decisions remain with the operator.

## 6. Verdict

**VERIFIED-WITH-RESERVATIONS.** The committed `5900431` bytes are exactly what
the author claims. Frozen tree: whole-repo content check rc=0 at freeze time,
78/78 fixture blobs sha1-identical, fileset 0-diff, both declared fixture shas
match, and `tilemap_lattice.gd` is a five-way byte-identical copy of the frozen
scout probe (no fold). Harness delta: **insertion-only +161/−0**, 4 hunks, CASES
251→265, the 14 rows at indices 247–260 in the declared slot, 265+7 meta = 272
rows, 9 `expected_errors` cases / 18 exact lines, 1 `required_stderr` case / 2
fragments, and the `r92_expected_errors_all_matched` floor gate present.

All four folds are encoded and live-verified:

1. **nav 2-payload envelope** — exhaustiveness over the committed corpus is
   **136/136 (90 p0, 46 p1, 0 neither)** with byte-exact residual, the regime
   crossing is exactly `≤2 → p0 / ≥2.5 → p1` with no receipt in between, the
   live crossing is 12/12, both payloads pin `regions_f2=1`, four field
   mutations are rejected, and every battery rep matched payload[0].
2. **nullts rc=−6 + `required_stderr`** — 3/3 fresh rc=−6 with the stdout anchor
   and both stderr fragments, 7/7 forged shapes rejected, the line-927 site
   confirmed; **but the row's 8 s wall margin is ~1.0** and it times out ~25 % of
   runs (F1).
3. **Tombstone encoding** — 47/47 independent byte-layout re-derivations
   (2-byte header + 12-byte LE int16 records; erase/clear = identical 8×0xFF
   tail at unchanged length; stale records visible as tombstones).
4. **expected_errors +9 with floor gate** — 18 unique `ERROR:` lines == the 18
   exact entries, no dead entries, gate true in all five reps.

Battery on the frozen bytes: **rep3 and rep4 are full 272/272 greens,
tuple-identical to both author runs and to the r91 green on the 258 pre-existing
rows**, with 13/14 r92 rows byte-identical across all five reps. Fresh arms
41/42 (the one non-OK is the F1 timeout), all 9 allowlists load-bearing in my
receipts (27/27) and in the author's committed receipts (42/42 re-classified,
27/27 bare-rejecting, manifest 1510/1510). 595/595 committed receipts match a
committed signature byte-for-byte. The frozen probeParent's four static clauses
all returned CONSISTENT.

Reservations: (a) **F1** — the new crash row is a loud ~25 % wall-time flake at
the 8 s bound, inherited from the engine's crash-dump path that already affects
`crash_spontaneous_sigabrt`; the artifact's claims are unaffected, but the wave
cannot count on a green battery; (b) **F2** — one stale `rc=-11` comment line;
(c) **F3** — evidence-caption counts (139/93 vs my 136/90) do not match the
committed corpus although the partition invariant holds; (d) **F4** — one
unreproduced `nav_lattice_path` failure (0/20 standalone, r91 row, not
r92-attributable); (e) **F5** — the author's green battery trees are
worktree-only; this seat's rep3/rep4 are the durable substitute until the wave
folds evidence.
