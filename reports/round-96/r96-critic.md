# r96 critic — adversarial review of committed `89f85ed8` (60 scene_io/r96b rows, 426-row battery)

Seat `CRITIC` (g2d lane r96) | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, `--headless`, 60 tps default,
`RendererDummy`), Python 3.
Reviewed commit **`89f85ed8`** (`r96 author: 60 rows (426 total) — scene_io + r96b
lattices, 16 expected-errors all live-matched; 426/426 x2`, parent `4a8bb124`). HEAD at
session start and at report time **`89f85ed8`** — the reviewed commit *is* HEAD.

**Committed tree only.** All harness checks ran on `git archive HEAD` extracted to
`corpus/live/r96-critic/tree/` (gitignored). The worktree's unrelated r97 churn — ` M
corpus/fixtures/run_battery.py` (+66/−0, `stree_*` rows), untracked `r97_scene_*.tscn`,
`stree_lattice.gd`, regenerated `__pycache__` — **was not read as evidence and no tracked
file was written by this seat**. The committed CASES carry no `stree` token (AST scan).
**No commit.**

**`lsp` disclosure.** No `lsp` device / GDScript language server on this host (same as
r89–r95 seats). Change under review is fixtures + an insertion-only harness block;
fresh-process execution + textual diff is the fallback in use.

**No delegated probe.** No `probeParent` dispatch was used; every check below is direct
shell/fresh-process evidence on the committed bytes.

---

## 0. What I ran

| # | batch | scope | result |
|---|---|---|---|
| 1 | **full battery** on the archived committed tree (`python3 corpus/fixtures/run_battery.py`, per-case 8 s bound, run dir `corpus/live/r96-critic/tree/corpus/live/runs/20261016T083057480254Z/verdicts.json`) | 426 results | **PASS 426/426, 0 FAIL** |
| 2 | standalone fresh-process arms in an independent scratch project (`/tmp/r96c-proj`, byte-copy of committed fixtures, `timeout -s KILL 25`) | 10 arms across all 7 probes | 10/10 emit the pinned tokens **byte-identical** to the committed signatures |
| 3 | fixture mutant `m1` | `r96b_id.gd`: save path `p%s.tscn` → `px%s.tscn` | emitted `seq=a:1_ytqgp/OK a:1_ytqgp/OK` — committed signature (`1_vwxho`) **would FAIL** |
| 4 | fixture mutant `m2` | `r96b_seq.gd` `minimal`: `node_ids` `[111111,…]` → `[111112,…]` | `sha_raw` `c16f3241…` → `7288d34d…` — committed signature **would FAIL** |
| 5 | static: AST CASES census, `git show` diff shape, sha256 provenance vs sibling lanes, expected_errors census mechanics, ordering | — | all claims verified (§2) |

Battery run detail: 419 CASES + 7 meta = **426 results**; `r96_*` rows **60/60 PASS**;
census `dead_entry_count=0`; `r96_expected_errors_all_matched=True`. The three
allowlist-bearing rows emitted **exactly** their allowlisted lines, once each:
`uid` 1× `Unrecognized UID: "uid://bqk3m5n7qar1".`, `ownership` 2×, `refuse` 13× — no
unallowlisted `ERROR:` anywhere in the r96 block. The scratch carried
`.godot/uid_cache.bin` (created by `export_readiness`, CASES[0] — ordering verified), so
the uid diagnostic fired in-battery; in the standalone scratch (no `.godot`) the same
probe is silent with the identical PASS line — the disclosed context dependency is real
in both directions.

---

## 1. Findings (ranked)

### F1 — INFO (doc) · the r96 floor-gate comment miscounts its own entries

`run_battery.py:3510–3514` comment: *"the two whitelist-bearing cases … 15 entries
total"*. Measured: **three** cases carry entries — `ownership` (2) + `uid` (1) +
`refuse` (13) = **16** — matching the author's own "+3 entries / 16 strings" claim and
the live census (16 entries, all `matched_lines=1`). The gate code itself iterates
`case.startswith(("r96_scene_io_", "r96b_"))` — correct; only the comment is wrong.
Smallest safe correction: fix the comment next insertion round ("three
whitelist-bearing cases … 16 entries"). No row impact.

### F2 — INFO (doc) · r96-boundary §5 prose contradicts its own retained receipt on `reuse_delete`

Boundary report §5 says "deleting the file does not evict the cache (`load()` still
returns the object, `exists=false`)". Every retained receipt —
`corpus/live/r96-boundary/runs/quiet/r96b_cache_reuse_delete.rep{1,2}.out`, plus the
analyze json and all 5 families — records `exists=true`, and the shipped signature
(`run_battery.py:1170`) correctly pins `exists=true`: **`ResourceLoader.exists` consults
the cache/path table and survives file deletion** — arguably the more interesting half
of that law. Shipped bytes are right; the report prose is wrong. Smallest safe
correction: amend `r96-boundary.md` §5 `exists=false` → `exists=true` (or qualify which
`exists` was meant). Evidence-only fix; no contract impact.

### F3 — LOW (disclosed) · `r96_scene_io_uid`'s allowlist entry is context-dependent by construction

`get_id_path(sid)` emits `ERROR: Unrecognized UID: "uid://bqk3m5n7qar1".` **iff**
`.godot/uid_cache.bin` exists in the project. In-battery this is deterministic
(`export_readiness` runs first, verified live this run); standalone it is silent
(verified — my `/tmp` run emitted no ERROR line and the same PASS). If a future battery
edit drops or reorders the export row after the r96 rows, the entry goes dead and the
`r96_expected_errors_all_matched` gate fails loudly — the correct failure mode, and the
author documents exactly this. Tradeoff, not a defect; no action needed.

### F4 — LOW (disclosed) · `size_in_176_194` is the provable support bound — weaker than the frozen key, correctly so

The scout's `size_in_190_200` was a measured flake (support `[189,194]`; one 189 in
boundary scans). The fold widens to `[176,194]` = 174 fixed bytes + 1–10 digits per
minted id (ids `< 2^31`, boundary-measured). The row still gates the size mechanism (any
structural layout change pushes size outside the bound) while no longer flippable on a
digit-width draw. Correct tradeoff; the width it gave up (`size≥195` impossible without
a format change) is exactly the load-bearing part.

### F5 — INFO · `idstat_breadth` substring could in principle prefix-match `distinct=2000`

`signature in output` is substring semantics, and `distinct=200` is a strict prefix of
`distinct=2000`. The composite signature `n=200 distinct=200` makes the degenerate case
unreachable: `distinct > n` is impossible, and `n=2000` breaks the `n=200 ` literal
first. Recorded for completeness; harmless today. (The real, disclosed rare window is
`distinct=200` flipping at ~1e-5 — a genuine generator-collision event, surfaced
deliberately.)

### F6 — INFO (corpus-wide, pre-existing) · single-condition battery

Same class as r95-critic F2: the battery pins 60 tps / one host / RendererDummy. The r96
surface is I/O- not tick-bound and the boundary ran all 13 scout cells + 23 core arms
across `quiet`/`load`/`ff1`/`ff30`/`ff120` byte-identically (and `ph*`/`pph*` arms pin
the no-phase-coordinate law directly in-battery), so the r96 exposure to this is
minimal. Not r96-specific.

---

## 2. What survived (positive verifications)

### 2.1 Commit hygiene and provenance

1. `89f85ed8` = 9 files, **+2712/−0** total; `run_battery.py` **+243/−0** — pure
   insertion (0 deletion lines) ⇒ no pre-existing row or allowlist could have been
   altered by construction.
2. AST census of the committed file: CASES **419** tuples (359+60), **0 duplicate case
   names**; the 60 r96 rows are contiguous at indices **355–414**, immediately after
   `r95b_order_rigid` and ahead of the unchanged tail
   (`crash_spontaneous_sigabrt`, `crash_self_sigkill`,
   `descendant_pipe_detached_control`, `descendant_pipe_forged_signature_release`) —
   the claimed insertion site.
3. All six `r96b_*.gd` fixtures are **sha256-byte-identical** to
   `corpus/live/r96-boundary/probes/` (verified: cache `f7d06de3…`, id `53a63d65…`,
   phase `4bb89614…`, seed `69a6413f…`, seq `3cae3659…`, var `71653a79…`).
4. `scene_io_lattice.gd` (839 L, `8aeab1cb…`) vs frozen scout probe (805 L,
   `2eded40b…`): diff = **+34 net**, every hunk accounted for — the 13-line fold header,
   the L4 law-comment correction, the `size_in_176_194` fold (bound + renamed key), the
   `get_id_path(created)` → `get_id_path(sid)` fold (+7 L comment), and the
   same-path-resave block (`e1c`/`sha_p1b`/`id1c`) with `id_stable_*` →
   `id_differs_*`/`id_stable_same_path`/`same_path_bytes_identical` renames including
   the `_b(id1 == id2)` → `_b(id1 != id2)` sign flips. No unexplained bytes.
5. Deliberate exclusions verified: no `seqAA3`/`subextra1`/`finger0`/`fresh2` rows, no
   `min=`/`max=` tokens pinned on `idstat`, `r96b_size.gd` not landed. The `extshift`
   and `fingerB` generator draws are on a **loaded** resource (`t[2]`) — path-seeded
   deterministic, not the refuted pathless `finger0` shape.
6. `project.godot` untouched; probes emit no `printerr`/`push_error`/self-`ERROR` text;
   `_:` fallback prints `FAIL`, arm name is on every PASS line (the r88 dead-seat class
   cannot recur).

### 2.2 Independent fresh-process replication (10 arms, committed bytes)

`seqA2` `1_vwxho`, `extshift` `pre=dg01n,6ddvb,3nsch ext_id=1_vwxho`, `minimal`
`sha_raw=c16f3241…e0b9`, `pack_basic` `size_in_176_194=true`, `extres` all folded keys,
`uid` (incl. `roundtrip=103876737118377468`), `threaded` `status=3`,
`ph0` `pinned_sha=c264d6eb…`, `idstat` `n=200 distinct=200` + `pin_found` vector,
`seedcheck` full `A=…/B=…/C=…/D=…` vector — **every pinned token byte-identical** to the
committed signatures on a project the battery never touched.

### 2.3 Row discrimination (fixture mutants)

| mutant | change | emitted | committed row |
|---|---|---|---|
| `m1` | `r96b_id` save path renamed (`pa.tscn`→`pxa.tscn`) | `a:1_ytqgp` | signature `1_vwxho` **rejects** — and independently re-confirms ids are f(output path, slot) |
| `m2` | `r96b_seq minimal` `node_ids` perturbed by 1 | `sha_raw=7288d34d…` | signature `c16f3241…` **rejects** |

⇒ the pinned literals/shas are load-bearing engine measurements, not echo pins (the r95
F1 class is absent: every landed row's signature carries measured tokens; the two
declared substrings — `idstat` breadth/gate — are composite pins on real output).

### 2.4 Battery hygiene on the committed tree

No `audio_playback` flake this run (the author's run-A flake is the documented
wall-clock class, unrelated to r96). All 7 meta rows PASS including
`probe_error_clause_surface` (which carries the r96 gate). Standalone probes leave only
`user://` residue (`_wipe()` per arm) and the `refuse` arm's `res://r96_relative.tres`
is created-and-deleted in-arm (`deleted=true` pin).

---

## 3. Verdict

**PASS** — the r96 landing survives every counterexample I could mount locally: the
commit is provably insertion-only, the fixtures' provenance is byte-exact, the fold is
faithful and disclosed, all 60 rows classify PASS fresh-process on the committed tree,
all 16 allowlist entries are live-matched exactly once, and both fixture mutants prove
the new rows discriminate engine behaviour. Findings are documentation-tier only
(F1/F2) plus disclosed tradeoffs (F3/F4) — **no blocker, nothing for the judge to weigh
beyond the residual flake surfaces already declared by the author** (`idstat` ~1e-5
collision window; uid entry's `.godot` context dependency — both loud-failing).

Blockers: **none**.
