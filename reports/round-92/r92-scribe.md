# game-dev-2d round 92 — scribe (r92-scribe): wave-B evidence custody + claim audit on committed `5900431`

Seat `SCRIBE` (LEAF) | lane `g2d-r92-scribe` | round 92 | host **devin** (`plazir27`, 32 cores).
Read-only audit of the r92 TileMapLayer landing: **no tracked file written, no commit, no
runtime config mutated**. The only writes are this report (new, untracked) and
`corpus/live/r92-scribe/**`. Every number below was recomputed from receipts on disk or from
a fresh launch on the committed bytes; nothing is quoted from the audited reports without
re-derivation.

Audit-time repository state: HEAD **`5900431`** (*r92 author: 14 tilemap rows (272 total) —
nav 2-payload envelope (boundary falsification folded), nullts SIGSEGV armed rc=-6, tombstone
encoding; 272/272 x2*). `git status --porcelain -uno` was **empty** at audit start
(00:15:46Z) and at every re-check; `tilemap_lattice.gd`, `run_battery.py` and `project.godot`
are byte-identical to `HEAD`, and the three r92 dossier reports are tracked and equal to
`HEAD` (`7d69d654…`, `90bb9f54…`, `86ca1c8c…`). No concurrent lane modified the tree during
this audit (unlike r91).

**Custody verdict: HOLDS — 4/4 declared folds are encoded and load-bearing.** All three
manifests verify completely (295/295, 2471/2471, 1510/1510) and each covers every artefact in
its directory except itself. **Two fresh battery runs on the committed bytes** (worktree, and
a `git archive HEAD` extract) are green on the r92 surface: **14/14 in both**, the
`r92_expected_errors_all_matched` floor gate `true` in both, `dead_entry_count=0` in both, and
**all 14 emitted lines byte-identical between the two runs**. The nullts row's two halves are
separately necessary (all 9 single-half mutations rejected across 10 receipts). One
low-severity comment defect (A1), one low-severity envelope consequence (A2) and eight info
items are recorded; none falsifies a landed pin, payload, allowlist entry, gate key or verdict.

---

## 0. What was run (method)

| # | check | command shape |
|---|---|---|
| 1 | manifest verification (all three) | `sha256sum -c manifest.sha256` in `corpus/live/r92-{scout,boundary,author}` |
| 2 | manifest completeness | entry set vs `os.walk` file set per dir (`audit/static_folds.py`) |
| 3 | committed-tree identity | worktree `sha256sum` vs `git show HEAD:<path>`; report files vs `HEAD` |
| 4 | CASES / row arithmetic + fold shape | AST parse of `HEAD:corpus/fixtures/run_battery.py` (`ast.literal_eval`) |
| 5 | **fresh battery run 1 (worktree = committed bytes, under load)** | `python3 corpus/fixtures/run_battery.py --runs corpus/live/r92-scribe/battery-runs` (stamp `20261016T001546769898Z`) |
| 6 | **fresh battery run 2 (`git archive HEAD` extract)** | same harness from `/home/vgpnk/r92-committed-extract` → `battery-committed/` (stamp `20261016T001825616636Z`) |
| 7 | cross-run tuple comparison | `audit/compare_runs.py` (row-by-row, payload-aware pin region vs tail) |
| 8 | nav envelope census | `audit/nav_envelope.py` over every committed nav receipt (scout/boundary/author) |
| 9 | **envelope reachability from the landed fixture** | `audit/fixedfps_probe.py`: landed `tilemap_lattice.gd --arm=nav` under default / `--fixed-fps {120,150,180,600}` |
| 10 | nullts binding falsification | `audit/forge_nullts.py`: production `classify_process` (AST-extracted from HEAD) + the row's real pins, 9 single-half mutations × 10 receipts + 2 foreign-crash cross-checks |
| 10b | signature-forge re-run on the landed rows | `audit/forge_rows_landed.py`: 396 mutants (value-flips + appended conjuncts) vs the landed payloads |
| 11 | author dossier recompute | `audit/recompute_claims.py`: runs1–5 `verdicts.json`, 42 fresh reps, gate/census |
| 12 | boundary dossier recompute | 416 matrix receipts re-gated with the **landed** rows and with a payload[0]-only variant |
| 13 | scout dossier recompute | 51 canonical cells `out_uniq`/`err_uniq`/rc |
| 14 | tombstone/encoding decode | byte-array pins parsed to 6×int16 records and re-decoded |

No `lsp` device and no GDScript language server on this host (unchanged state, same as all
audited seats); no symbol edits were performed — the only "edit" surface was new receipts.
All probe launches were bounded (25–40 s); no orphaned processes were left.

**Frozen-`probeParent` disclosure.** Exactly **one** read-only `ufo-labrat` was dispatched
(agent `6b97dea4`), one bounded hypothesis (see §3.4). It returned a **static** result: its
toolset on this host is read-only filesystem only — it cannot spawn processes or write
scratch — so it re-derived the payload↔line byte-equality from the receipts with its own code
and confirmed payload0/payload1 exactly, but executed nothing. Verdict CONFIRMED, with the
capability caveat recorded as finding **A6** below: on this host a labrat dispatch buys
independent *re-derivation*, not independent *measurement*.

---

## 1. Custody table — manifests, git tracking, verdict

| dossier artefact | manifest | verification | completeness | git state at audit |
|---|---|---|---|---|
| `corpus/live/r92-scout/` | `manifest.sha256`, **295 entries** | **295/295 OK** | exact — only the manifest itself is unlisted | 19 tracked / 296 on disk (`runs/` ignored by `corpus/live/.gitignore:1`) |
| `corpus/live/r92-boundary/` | `manifest.sha256`, **2471 entries** | **2471/2471 OK** | exact | 22 tracked / 2472 on disk (`runs/` ignored) |
| `corpus/live/r92-author/` | `manifest.sha256`, **1510 entries** | **1510/1510 OK** | exact | 133 tracked / 1511 on disk (`runs*/` ignored) |

The author's five battery runs (`runs1..5`, 3.5 MB each) and the scout's/boundary's `runs/`
trees are therefore **worktree-only custody** — manifest-covered, not tracked (same convention
as r87–r91; A4). The scout's and boundary's *frozen probes* are tracked and equal to the
landed fixture byte-for-byte (§2).

---

## 2. Committed-tree identity + two fresh runs on the committed bytes

Worktree bytes == committed bytes for every landing file, so "committed tree only" holds for
all execution below:

| file | sha256 (worktree == `git show HEAD:`) |
|---|---|
| `corpus/fixtures/tilemap_lattice.gd` (929 lines) | `a699138945ec7c1c…` |
| `corpus/fixtures/run_battery.py` | `5e5182815e6e3c50…` |
| `corpus/fixtures/project.godot` (untouched by the landing) | `8de8b3af9cc737ed…` |
| `corpus/live/r92-scout/probes/tilemap_lattice.gd` | `a699138945ec7c1c…` — **byte-copy** |
| `corpus/live/r92-boundary/probes/scout_tilemap_lattice.gd` | `a699138945ec7c1c…` — **byte-copy** |

The landed fixture is thus literally the frozen scout probe (929 lines, no fixture folds), and
`git show --numstat 5900431` is insertion-only (`+161 run_battery.py`, `+929
tilemap_lattice.gd`) plus the receipts/manifest/report.

**Fresh battery run 1** — worktree at `5900431`, tracked tree clean at launch, host under
foreign load (loadavg ≈60, 32 cores, 48 foreign `yes` hogs owned by ppid 1537 of another
lane; no other lane's battery was running during my window):

```
rep1 — stamp 20261016T001546769898Z  (battery-runs/, log battery-rep1.log)
  rows=272  verdict=PASS (272/272)  tilemap 14/14 PASS
  r92_expected_errors_all_matched=true   census rows_with_expected_errors=68  dead_entry_count=0
  census_bare_classifier_consistent=true
  nav emitted payload[0] (regions_f1=1)   nullts actual_exit=-6
```

**Fresh battery run 2** — executed from a `git archive HEAD` extract
(`/home/vgpnk/r92-committed-extract`; `tilemap_lattice.gd=a6991389…`,
`run_battery.py=5e518281…` verified before launch), independent of the worktree:

```
rep2b — stamp 20261016T001825616636Z  (battery-committed/, log battery-rep2b.log)
  rows=272  verdict=FAIL (271/272)  tilemap 14/14 PASS
  r92_expected_errors_all_matched=true   dead_entry_count=0   rows_with_expected_errors=68
  fails: overlap (exit=1 — the pre-existing scene-install race class; A7)
```

**Cross-run comparison** (`audit/compare_runs.py`, 272 rows): **217 rows byte-identical**,
**11 rows differ only after their pinned signature**, **0 rows differ inside a pin**, 44 rows
carry no pinned PASS line by construction (negative controls, export cases, meta probes; all
PASS/PASS except `overlap`).

| bucket | rows |
|---|---|
| identical | 217 |
| tail-only (unpinned tail bytes) | `input_lattice_api_press`, `input_lattice_ui_ns`, `nav_lattice_agent`, `nav_lattice_avoid`, `nav_lattice_bake`, `nav_lattice_region`, `release`, `save_process_reader`, `save_process_writer`, `save_roundtrip`, `tween_flash` |
| pin-diff | — none — |
| **all 14 r92 rows** | **identical** (`r92_tilemap_census` … `r92_tilemap_nullts_crash`) |

No r92 row appears in either variance bucket: the 14 new lines are byte-stable across two
independent committed-byte runs, including the crash row (`rc=-6`, identical stdout, stderr
differs only in ASLR'd addresses, which are unpinned by design).

---

## 3. Fold 1 — `r92_tilemap_nav` is a 2-payload envelope on `regions_f1`

### 3.1 Static shape (re-derived from `HEAD`)

`CASES` carries the row's signature as a **list of 2 payloads** (`audit/static_folds.json`).
The two payloads are 22 tokens each and differ at **exactly one index**:

```
index 14   payload[0] = "regions_f1=1"   payload[1] = "regions_f1=0"
```

Every other token — including the settled form `regions_f2=1` and the
disable/re-enable/erase lever trio — is identical. The harness branch
(`isinstance(evidence, (tuple, list))` → `any(classifier(...) for sig in evidence)`) admits
either payload and nothing else; the `required_stderr` path is unaffected (this row has none).
The `mutate=True` path (which keys off `evidence[0]`) is used only by the two explicit
`mutant_*` rows, so the envelope cannot interact with the mutant probes.

**Signature discrimination survives the envelope.** Re-running the scout's forge test
(mutate the *pinned signature*, classify against the real receipt) with the **landed** rows,
including the 2-payload nav row (`audit/forge_rows_landed.py`):

```
TOTAL mutants=396 rejected=396 accepted=0        (nav alone: 46/46)
```

Every key=value value-flip and every appended never-emitted conjunct (`forged=1`,
`empty_source=-2`, `disabled_f1=hit`, `regions_f1=0`) is rejected on all 14 rows — the
classifier still requires a payload to appear verbatim in the emitted output, so the envelope
admits *two real lines*, not arbitrary ones.

### 3.2 Receipt census — the envelope partitions every committed nav receipt

`audit/nav_envelope.py` walks every committed nav line (`.out` files **and** the `output`
arrays inside `verdicts.json`) and compares byte-for-byte against the two payloads:

| source | receipts | payload0 | payload1 | neither |
|---|---|---|---|---|
| scout `runs/` (canonical 6 + loadtest 1 + tps120 3) | 10 | 10 | 0 | 0 |
| boundary `runs/` (13-condition matrix + scans/rate test) | 126 | 80 | 46 | 0 |
| author `fresh-reps/` (3 reps) | 3 | 3 | 0 | 0 |
| author battery `runs1..5` (`verdicts.json`) | 5 | 5 | 0 | 0 |
| **total** | **144** | **98** | **46** | **0** |

Across all 144 receipts the only multi-valued field is `regions_f1 ∈ {0,1}`;
`regions_f2=1`, `regions_after_plain_cell=1`, `regions_disabled_*=…`, `regions_reenabled=1`,
`regions_erased_*=…` are **single-valued in both modes**. So the envelope moves the one
frame-counted read and never the law, exactly as the landing comment claims.

### 3.3 Boundary re-gating — the envelope is load-bearing, not decorative

Re-running the production classifier over the boundary's **416 matrix receipts**
(`audit/recompute_claims.py`) with the **landed** rows:

```
landed 2-payload envelope      receipts=416  rejected=0
pre-envelope payload[0]-only   receipts=416  rejected=2   (f600_nav.rep1.out, f600_nav.rep2.out)
```

The 2 rejections are precisely the receipts the boundary falsified (`regions_f1 1→0` at
`--fixed-fps 600`) and they are the only ones the envelope rescues — the fold consumes the
falsification rather than inheriting it.

### 3.4 The envelope's payload[1] branch — reachability closed by this seat

Before this audit the **landed fixture had no committed receipt emitting payload[1]**: all 46
committed `regions_f1=0` receipts came from the boundary's *copy* of the probe (different
`res://` name, same bytes). I closed the gap with `audit/fixedfps_probe.py` (landed fixture,
battery launch shape, `--fixed-fps` inserted before `--script`); these five receipts are
**untracked scribe receipts**, not committed evidence:

| launch (60-tps project) | idle:physics ratio | emitted `regions_f1` | payload match | envelope accepts | payload0-only |
|---|---|---|---|---|---|
| default | 2.5–3 irregular | 1 | payload0 | yes | yes |
| `--fixed-fps 120` | 2 | 1 | payload0 | yes | yes |
| `--fixed-fps 150` | 2.5 | **0** | **payload1** | yes | **no** |
| `--fixed-fps 180` | 3 | **0** | **payload1** | yes | **no** |
| `--fixed-fps 600` | 10 | **0** | **payload1** | yes | **no** |

`regions_f2=1` held in **all five** launches, rc=0 throughout, stderr carrying only the
deprecation WARNING. The labrat independently re-derived the payload0/payload1 byte-equality
from these receipts with its own comparison code (it could not execute; §0 disclosure). So the
envelope's second branch is now receipt-backed **on the landed bytes**, not only by analogy to
the boundary's copy.

---

## 4. Fold 2 — `r92_tilemap_nullts_crash`: `rc=-6` bound to the null-deref

### 4.1 Static shape

Row: `('r92_tilemap_nullts_crash', 'tilemap_lattice.gd', ['--arm=nullts'], -6,
'R92 nullts about_to_call_tile_data=1')`, with
`required_stderr = ('handle_crash: Program crashed with signal 11',
'_nullts (res://tilemap_lattice.gd:927)')`. Line 927 of the committed fixture is
`var td := layer.get_cell_tile_data(Vector2i(0, 0))` inside `_nullts()` — the crash site, so
the fragment is anchored to *this* probe's line numbering (author-disclosed, A10).

### 4.2 Binding falsification (production classifier, real streams)

`audit/forge_nullts.py` extracts `classify_process` **verbatim from `HEAD`** (segment sha256
`13473e6def6cd2da…`) and applies the row's *full* pass condition to real receipts, mutating
one half at a time. Expected column: the row must PASS only on the genuine receipt.

| receipt (real streams) | A genuine | A2 rc normalised to −6 | A3 rc=134 (shell 128+6) | B stderr stripped | C stdout stripped | D fragments moved to stdout | E rc=0 | F other hazard's anchor | G wrong site `:928` | H wrong handler `signal 6` |
|---|---|---|---|---|---|---|---|---|---|---|
| author `nullts.rep{1,2,3}` (rc −6) | **true** | true | false | false | false | false | false | false | false | false |
| scribe `nullts.rep1` (rc −6) | **true** | true | false | false | false | false | false | false | false | false |
| scout `hazard-nullts.r{1,2,3}` (rc 134) | false | **true** | false | false | false | false | false | false | false | false |
| scout `disc4-setcell_td.r{1,2,3}` (different hazard, `disc4.gd:22`) | false | false | false | false | false | false | false | false | false | false |

Cross-receipt foreign crashes: `r91-scribe/fresh/teardown_crash` (SIGABRT, `double free or
corruption`) → rejected; a synthetic foreign SIGABRT with the signal-11 header but no nullts
site → rejected.

Reading: (a) the row is bound to **rc −6 + stdout anchor + both stderr fragments** — each half
is separately necessary; (b) the scout's `134` is the same crash under the shell wrapper
encoding and is *correctly rejected* by the −6 pin (A2 shows it accepted once the rc is
normalised), so the author's "same termination, two encodings" correction is exactly right;
(c) a foreign SIGSEGV/SIGABRT — right signal, wrong cause — cannot satisfy the pair.

### 4.3 Receipts on the committed bytes

Both of my battery runs recorded `actual_exit=-6`, verdict PASS, with the last pre-crash
diagnostic `R92 nullts about_to_call_tile_data=1` on stdout and both fragments on stderr
(`audit/run_summary.json`). My independent single-arm launch (`fresh/nullts.rep1`) reproduces
it with `rc=-6` and the `:927` frame.

---

## 5. Fold 3 — tombstone encoding pinned verbatim

The `r92_tilemap_encoding` pin carries the raw `tile_map_data` bytes. Re-decoding them
(`audit/static_folds.py`, 2-byte header + 6 little-endian int16 per record = `x, y,
source_id, atlas_x, atlas_y, alternative`):

| pin field | len | decoded records | law |
|---|---|---|---|
| `one_bytes` | 14 | `(3,4,0,1,0,0)` | header + 1 record, `stride=12` |
| `two_bytes` | 26 | `(3,4,0,1,0,0) (7,-2,0,0,1,0)` | second write appends |
| `tomb_set_bytes` | 14 | `(1,1,0,0,0,0)` | live cell |
| `tomb_erase_bytes` | 14 | `(1,1,-1,-1,-1,-1)` | **erase writes an in-place tombstone** (source/atlas/alt = −1, x/y kept), **length unchanged** |
| `tomb_reset_bytes` | 14 | `(1,1,0,0,0,0)` | re-set rewrites the same record |
| `tomb_clear_bytes` | 14 | `(1,1,-1,-1,-1,-1)` | **`clear()` tombstones every record, never truncates** |
| `tomb_clear_set_bytes` | 26 | `(1,1,-1,-1,-1,-1) (5,5,0,0,0,0)` | post-clear write appends at the high-water mark |
| `alt_bytes` | 26 | `(3,4,0,1,0,1) (7,-2,-1,-1,-1,-1)` | alternative id in-record; a tombstoned second record |

Every pinned `*_len` field equals the corresponding array length (14/26/14/14/14/26), and
`stride=12`, `two_arr_equals_bytes=1` complete the law. The "buffer is a high-water mark, never
a live-cell count" claim is exactly what the bytes say. Both of my runs emitted this row
byte-identically.

---

## 6. Fold 4 — `expected_errors` +9 with the floor gate

- `CASES` at `HEAD` is **265 tuples** (251 + 14); the 14 `r92_tilemap_*` rows are contiguous at
  indices 247–260, immediately after `nav_lattice_teardown_clean` (246) and **ahead** of
  `crash_spontaneous_sigabrt`, `crash_self_sigkill`,
  `descendant_pipe_detached_control`, `descendant_pipe_forged_signature_release` — the
  sleep-8 adjacency the comment requires is preserved.
- The r92 `expected_errors` block has **9 cases / 18 exact lines** (`atlas` 2, `cells` 2,
  `custom` 3, `terrain` 1, `pattern` 1, `encoding` 2, `fixinvalid` 3, `srcids` 3, `physics` 1);
  `census`/`timing`/`quadrant`/`nav` carry none. `required_stderr` gains 1 case (the nullts pair).
- Run-level: `rows_with_expected_errors` **59 → 68** (+9) — verified against the committed r91
  author runs (59) and my own two runs (68).
- Floor gate `r92_expected_errors_all_matched` exists, is prefix-scoped to `r92_`, and is
  **`true` in all 7 retained committed-byte runs** (author ×5 + mine ×2), with
  `dead_entry_count=0` in the four green ones.
- The 9 allowlists are **load-bearing, not decorative**: for every one of the 9 cases, the
  bare classifier rejects the receipt (`bare=False`) and the allowlisted classifier passes —
  recomputed on the 42 author fresh reps *and* in my two runs, where the census records
  `any_entry_matched=True`, `bare_classification_rejects=True`,
  `allowlisted_classification_passes=True` for each. `census_bare_classifier_consistent=true`
  in both green runs and in the author's runs4/runs5.
- In the author's three interim (flake) runs the gate stays `true` while
  `dead_entry_count` is 2–3: those dead entries belong to `negative_transition`-class rows,
  i.e. the gate is correctly scoped and does not absorb unrelated flakes.

---

## 7. Dossier claim recompute

### 7.1 Author (`reports/round-92/r92-author.md`, `5900431`)

| claim | recomputed |
|---|---|
| fixture = byte-copy of the frozen scout probe, 929 lines, no folds | ✓ `a6991389…` in all three copies |
| `run_battery.py` +161/−0, CASES 251→265, rows 258→272 | ✓ insertion-only, AST-verified |
| two green runs 272/272 | ✓ `runs4` `20261016T000237…`, `runs5` `20261016T000655…` |
| interim runs fail only on documented volatile classes | ✓ `runs1` `negative_transition`; `runs2` `transition, negative_transition, audio_playback, audio_bus_route_invalid_control`; `runs3` `overlap, transition, negative_transition`; no r92 row in any of them (14/14 ×5). Each interim run additionally fails the `probe_error_clause_surface` meta row, whose `dead_entry_count` follows those flakes (2/3/2) — recomputed, and correctly *not* propagated into the r92 floor gate |
| 42 fresh reps, all PASS through the production classifier, allowlists load-bearing | ✓ 14 arms × 3 reps: all PASS; stdout byte-identical ×3 for all 14; stderr identical for 13 (nullts differs only in ASLR addresses); bare classification fails for exactly the 9 allowlist arms |
| nullts ×3: rc −6 + stdout signature + both fragments | ✓ (and the pin is *tight* — §4.2) |
| nav fresh rep carries payload[0] | ✓ (`regions_f1=1`) |
| "`134` is the same SIGABRT through the shell wrapper" | ✓ forge variant A2/A3 |
| labrat advisory: envelope partitions "all 139" nav receipts, payload0=93, neither=0 | **substantively ✓, count under-stated**: my census finds **144** (98/46/0); the delta is exactly the 5 nav lines embedded in the author's own `runs1..5/verdicts.json`, which are not `.out` files (A6) |

### 7.2 Boundary (`reports/round-92/r92-boundary.md`)

- 12/13 rows scheduler- and load-invariant; `nav` falsified at ratio ≥ 2.5 — reproduced: the
  416-receipt matrix re-gates **0 rejected** with the landed envelope and exactly **2** with
  payload[0]-only (§3.3); my `--fixed-fps` probe reproduces the flip between ff120 (1) and
  ff150 (0) on the **landed** fixture.
- "126 nav receipts, 46 with `regions_f1=0`, every other field single-valued" — ✓ exact
  (126/46, only `regions_f1` multi-valued).
- 639 `.rc` sidecars / 2450 files in `runs/` — ✓ (`find`: 2450 files, 639 `*.rc`).
- Scout control 64/64, `verify_rows.py` — ✓ 51 canonical + 13 loadtest = 64, and the scout's
  51 canonical cells are `out_uniq=1 err_uniq=1 rc=[0]`.
- §6 directive 1 (envelope / pin `regions_f2` / restrict the harness) — the author took the
  **envelope** branch and pinned `regions_f2=1` in *both* payloads; directives 2–6 are
  consistent with what landed.

### 7.3 Scout (`reports/round-92/r92-scout.md`)

- 51 canonical runs, every cell `out_uniq=1 err_uniq=1 rc=[0]` — ✓ recomputed from receipts.
- §4.4 tombstone law, §4.7/§5.1 nullts hazard (both halves required), §5.1 isolation table —
  ✓ (§4.2 cross-receipt: the `setcell_only`-style receipts and the `disc4` variant are
  rejected by the row, while the nullts receipts pass).
- §6.2 directive 7 "**No envelope is needed** — 13/13 cells single-valued" — **superseded** by
  the boundary falsification and correctly not inherited: the landing carries the envelope for
  `nav` only. (This is the one scout claim the landing deliberately contradicts; the commit
  message names it.)

---

## 8. Arithmetic cross-check ledger (all reconcile)

| identity | result |
|---|---|
| landing: CASES 265 = 251 + 14; rows 272 = 258 + 14; `run_battery.py` +161/−0 | ✓ |
| r92 rows contiguous at 247–260 after `nav_lattice_teardown_clean` (246); crash tail intact | ✓ |
| `expected_errors` 9 cases = 18 lines; `rows_with_expected_errors` 59 → 68 | ✓ |
| `required_stderr` +1 case = 2 fragments; `nav` has none | ✓ |
| manifest arithmetic: 295 = 296 − self; 2471 = 2472 − self; 1510 = 1511 − self | ✓ |
| author fresh-reps: 126 files = 14 arms × 3 reps × 3 streams (42 reps) | ✓ |
| author runs: 272 rows × 5; r92 14/14 × 5; green ×2 | ✓ |
| mine: rep1 272/272; rep2b 271/272 (`overlap`); r92 14/14 ×2; 217 identical + 11 tail-only + 0 pin-diff | ✓ |
| boundary: 416 matrix receipts = 39×6 + 26×7; 2450 files, 639 `.rc` | ✓ |
| envelope census: 144 = 10 + 126 + 3 + 5; 98 + 46 + 0 = 144 | ✓ |
| scout: 51 canonical = 9×3 + 4×6; +13 loadtest = 64 gated; +9 tps120 = 22 | ✓ |

---

## 9. Adjudication items (ranked)

| id | dossier | item | severity | disposition |
|---|---|---|---|---|
| **A1** | author (harness comment) | The comment above the r92 `required_stderr` block reads "binds the **rc=-11** to the engine's own signal-11 crash handler". The row's `expected_exit` is **−6** (SIGABRT); −11 is the *signal*, not the process return code. The pin itself is right and provably load-bearing (§4.2). | **low** (comment-only; a future reader could "fix" the row to −11 and silently break it) | reword to "binds the rc=−6 (SIGABRT through the engine's crash handler) to the signal-11 handler header …". Same class as r91's recorded comment-formula defect |
| **A2** | landing (envelope) | The envelope admits exactly **2** emitted lines (differing only in `regions_f1`). This does **not** loosen the signature pin: re-running the scout's signature-forge against the **landed** rows rejects **396/396** mutants (nav alone 46/46 — including the `regions_f1=0` value-flip and the appended `regions_f1=0` conjunct), because the classifier still requires a payload to appear verbatim in the emitted output. What changes is the row's ability to tell the two *modes* apart: a production-regime `regions_f1` regression (1 → 0 for a non-scheduler reason) is now absorbed by payload[1] instead of failing. `regions_f2=1` — single-valued in all 144 receipts and in **both** payloads — remains the settled-form guard. | **low** (intended fold; the second mode is real: 46 committed receipts + 3 fresh landed-fixture launches) | record as the price of "envelopes, never fixed frames". Note the boundary's §8 unknown: on a genuinely idle host the *default* scheduler's uncapped ratio could itself cross 2.5, which is the portability argument for the envelope |
| **A3** | this seat | The envelope's payload[1] branch had **no receipt from the landed fixture** in the committed corpus (all 46 came from the boundary's copy). Closed here: `fixedfps/nav_ff{150,180,600}` on the landed bytes match payload[1] exactly, `regions_f2=1` holds, and a payload[0]-only check rejects them. | info (gap closed) | retain the three receipts with the landing's evidence index if the round is re-opened |
| **A4** | custody | The author's two green runs (`runs4`,`runs5`) and the scout/boundary `runs/` trees are gitignored (`corpus/live/.gitignore` `runs*/`) but manifest-covered → **worktree-only custody**. A worktree prune would lose the only receipts of the two green runs. | info | same convention as r87–r91; recorded, not escalated |
| **A5** | author §"Fresh-arm evidence" | "42 receipts (`out`/`err`/`rc`)" is imprecise: the directory holds **126 files** = 42 reps × 3 streams. | info (label) | reword to "42 reps × (out/err/rc)" |
| **A6** | frozen `probeParent` labrat | The dispatched labrat could not execute anything on this host (read-only filesystem toolset — no process spawn, no scratch write) and returned a static re-derivation instead. Its payload byte-equality check reproduces mine, but the seat cannot deliver independent *measurement* here; it also labelled my (untracked, scribe-generated) receipts as "committed". | info (operational) | if a wave needs independent execution, dispatch a seat with exec (`ufo-mutation-tester`, `subagent_general`); otherwise the probe allowance is spent on re-derivation |
| **A7** | my runs | `overlap` failed in rep2b (committed-extract, rc=1) and passed in rep1 — the pre-existing scene-install race class (also present in the author's runs1–3). No r92 row was affected. | info (pre-existing flake) | not r92-caused; the landing surface is 14/14 in both runs |
| **A8** | environment | Host never idle: loadavg 59–65 on 32 cores with 48 foreign `yes` hogs (ppid 1537) throughout both of my runs and the author's five. `/tmp` is a 16 GB tmpfs at 76 % (12 GB used); the committed-tree extract was therefore run from `/home` (r91 A8 precedent). | info | environment note for replay instructions |
| **A9** | landing (envelope threshold) | The envelope's declared threshold shape ("1 at ratio ≤ 2, 0 at ≥ 2.5") has an **unmeasured band** (2, 2.5): the boundary's scans jump ff120 → ff150 and my probe confirms only the endpoints (ff120 = payload0, ff150 = payload1). | info | harmless for acceptance (both values are admitted), but the *law statement* should say "endpoints measured; the band is unmeasured" or be closed with one ff135 launch |
| **A10** | landing (nullts pin) | `_nullts (res://tilemap_lattice.gd:927)` is bound to the frozen fixture's line numbering (author-disclosed). Verified: line 927 is the `get_cell_tile_data` call. Any future fixture fold moves it and the row fails loudly. | info | keep; re-pin deliberately on the next touch |

---

## 10. Remaining risks / blockers

1. **No blockers to the landing.** Both committed-byte runs are green on the r92 surface
   (14/14 each, floor gate true, zero dead entries), the three manifests verify completely,
   and every recomputable dossier claim reproduces.
2. **Envelope mode-blindness (A2).** The row accepts both scheduler modes, so it cannot tell
   them apart: a future *production-regime* regression of `regions_f1` (the 1 → 0 direction,
   for a non-scheduler reason) would be absorbed by payload[1] instead of failing. The
   signature pin itself is unweakened (396/396 signature mutants rejected on the landed rows,
   §3.1) and the settled-form pin `regions_f2=1` plus the other 13 rows are unaffected. If the
   round is ever re-opened, a `regions_f1`-conditioned *gate* (measure the idle:physics ratio,
   assert the expected payload) would restore discrimination — that is a new mechanism, not a
   fold.
3. **Worktree-only custody (A4)** for the two green runs and the scout/boundary `runs/` trees:
   manifest-verified but not tracked.
4. **Comment defect (A1)** could mislead a future author into re-pinning the nullts row to −11
   (SIGSEGV's signal number) and breaking a load-bearing pin.
5. **Host-conditional pins by design**: `class_method_counts=TileMapLayer=58 TileSet=90 …`,
   enum orders, 4-dp floats, `tps=60` — all flip loudly on an engine/solver bump (same class
   as existing census/geometry pins). The scout's `ROWS_PREFIX` variant (census tail cut) is
   staged at `corpus/live/r92-scout/author-rows.py.txt` for such a bump.
6. **The watchdog**: the fixture's 20 s process-time watchdog is longer than the harness's 8 s
   per-case bound, so a stall surfaces as a harness TIMEOUT (loud) rather than a watchdog FAIL.
   Under `--fixed-fps 1/5` the boundary still saw PASS/rc=0; unchanged by this landing.
7. **Pre-existing flake classes** reproduce under load on committed bytes (`overlap` in my
   rep2b; `transition`/`negative_transition`/audio classes in the author's interim runs). None
   touches an r92 row.
8. **`nav`'s stderr carries only the deprecation WARNING** (no `ERROR:` substring, so
   classifier-inert today). A future classifier that tightens WARNING handling would reject the
   row — the scout's hazard #11, unchanged by this landing.

---

## 11. Host notes / cleanup

- I added no load of my own beyond the two batteries and five godot probe launches; no `yes`
  hogs, no orphaned processes (`ps` clean of my launches). The 48 foreign `yes` hogs (ppid
  1537) belong to another lane and were left untouched.
- `corpus/fixtures/.godot/` does not exist (verified); the battery writes its engine cache into
  each run's own `scratch/`. The two probe projects (`fresh-proj/`, `fixedfps-proj/`) are
  untracked byte-copies under this lane's receipts.
- The `/home/vgpnk/r92-committed-extract` tree (used for run 2) is retained this session; its
  launched fixture bytes are preserved inside `battery-committed/*/scratch/`.
- Zero tracked files written by this seat; `git status --porcelain -uno` is empty at the end of
  the audit.

---

## 12. Evidence index

All under `corpus/live/r92-scribe/`; `manifest.sha256` covers every artefact in that directory
except itself.

| artefact | path | notes |
|---|---|---|
| battery run 1 (worktree, committed bytes) | `battery-runs/20261016T001546769898Z/verdicts.json` + `battery-rep1.log` | 272 rows, **PASS 272/272**, r92 14/14, gate true, dead 0 |
| battery run 2 (`git archive HEAD` extract) | `battery-committed/20261016T001825616636Z/verdicts.json` + `battery-rep2b.log` | 272 rows, 271/272 (`overlap`), r92 14/14, gate true, dead 0 |
| fresh single-arm receipts | `fresh/{nav,nullts,encoding,census}.rep1.{out,err,rc}` | battery launch shape; nullts `rc=-6` |
| envelope reachability (landed fixture) | `fixedfps/nav_{default,ff120,ff150,ff180,ff600}.{out,err,rc}` + `audit/fixedfps_probe.json` | payload0/payload1 per mode; `regions_f2=1` ×5 |
| static custody + folds | `audit/static_folds.py` → `static_folds.json` | landing identity, CASES/rows, allowlist census, manifest completeness, tombstone decode |
| envelope census | `audit/nav_envelope.py` → `nav_envelope.json` | 144 receipts: 98/46/0; single multi-valued field |
| nullts binding falsification | `audit/forge_nullts.py` → `forge_nullts.json` | 9 mutations × 10 receipts + 2 foreign-crash cross-checks |
| signature-forge on the landed rows | `audit/forge_rows_landed.py` → `forge_rows_landed.json` | 396/396 mutants rejected (nav 46/46) |
| dossier recompute | `audit/recompute_claims.py` → `recompute_claims.json` | author ×5, fresh ×42, boundary 416, scout 51 |
| cross-run comparison | `audit/compare_runs.py` → `compare_runs.json` | 217 / 11 / 0 / 44 |
| run summary | `audit/summarize_runs.py` → `run_summary.json` | per-run gate/census + the 14 emitted lines |
| lane index / replay | `RECEIPTS.md` | commands + headline numbers |
| source reports | `reports/round-92/r92-{scout,boundary,author}.md` | tracked, sha-verified |
| source reports (r91 precedent used in A6/§4.2) | `reports/round-91/r91-scribe.md`, `corpus/live/r91-scribe/fresh/teardown_crash.*` | foreign-crash cross-check |
