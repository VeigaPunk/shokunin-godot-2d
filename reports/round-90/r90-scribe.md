# game-dev-2d round 90 — scribe (r90-scribe): wave-B evidence custody + claim audit on committed `ee20575`

Seat `SCRIBE` (LEAF) | lane `g2d-r90-scribe` | round 90 | host **devin**.
Read-only audit of the r90 rb2d dossier: **no tracked file written, no commit, no
runtime config mutated**. The only writes are this report (new, untracked) and
`corpus/live/r90-scribe/**`. Every number below was recomputed from the receipts
on disk; nothing is quoted from the reports under audit without re-derivation.

Audit-time repository state: HEAD **`ee20575`** (*r90 author: 12 rb_lattice rows
(247 total) — tps-qualified pins, eng=Dummy precondition gate, typed refusals,
dy=n\*g\*dt^2 oracle; 247/247 x2 green*). At audit start `git status --porcelain`
showed **no modified tracked file** (only the pre-existing untracked lanes and
`corpus/fixtures/__pycache__/…`); a concurrent sibling lane (r89 fold) modified
tracked files mid-audit — recorded in §2 and untouched by this seat. The dossier
reports are themselves **tracked**: scout `535b2c2`, boundary `520ed6d`, author
`ee20575`.

**Custody verdict: HOLDS.** All three manifests verify completely
(208/208, 1143/1143, 4015/4015), each covers every artefact in its directory
except itself, and every claim class I could recompute reproduces byte-for-byte
— including fresh committed-tree battery runs under load, one of them **fully
green 247/247** (r90 12/12, r90 gate `true`). **No landed pin, envelope payload,
allowlist entry, gate key, or verdict is falsified.** One **medium
evidence-provenance defect** was found in the author's 30-tps side receipt
(A1: the cited `--physics-ticks-per-second` flag does not exist in Godot 4.7.2
and the two receipts are 60-tps runs), plus four low/info label items (A2–A5).
None touches the landing; the boundary fold the receipt was meant to evidence is
independently re-verified here.

---

## 0. What was run (method)

| # | check | command shape |
|---|---|---|
| 1 | manifest verification (all three) | `sha256sum -c manifest.sha256` in `corpus/live/r90-{scout,boundary,author}` |
| 2 | manifest completeness | entry set vs `os.walk` file set per dir (`audit/manifest_completeness.py`) |
| 3 | committed-tree identity | `sha256sum <worktree>` vs `git show ee20575:<path> \| sha256sum`; cross-seat probe shas |
| 4 | scout stability recompute | re-derived `out_uniq/err_uniq/rc`/PASS-line count for all 12 cells from `runs/` (`audit/scout_recompute.py`) |
| 5 | scout row verification | re-ran `verify_rows.py` (read-only, AST-extracted production classifier) |
| 6 | boundary receipt census | counts, rc values, max wall, per-cell pass/rc uniqueness over all 82 cells (`audit/boundary_recompute.py`) |
| 7 | boundary hash/claims recompute | md5 PASS-hash literals, sv-tier byte-identity, 9/9 cross-seat scout equality, 30-tps pairing census |
| 8 | author claim recompute | `verify_arms.py` re-run; `compare.py godot` re-runs (rep9↔rep12b, rep4↔r89-rep5); per-stamp verdict census; rep9 census/gate keys (`audit/author_checks.py`) |
| 9 | CASES arithmetic | AST parse of `corpus/fixtures/run_battery.py` at `ee20575`; emitted-vs-landed row tuples |
| 10 | **fresh committed-tree battery under load** | `python3 corpus/fixtures/run_battery.py --runs corpus/live/r90-scribe/battery-runs` (rep1) and the same from a `git archive ee20575` extract (rep2b); 2 × 247 rows, rep2b fully green; host loadavg 56–125 from concurrent lanes + 48 foreign `yes` hogs |
| 11 | 30-tps provenance probe | committed probe on 60-tps / real-30-tps projects, engine-flag and after-`--` flag variants (`probe-tests/`) |

No `lsp` device is present on this host (unchanged state, same as all audited
seats); no symbol edits were performed by this seat. All probe launches were
`timeout -s KILL 25`-bounded.

---

## 1. Custody table — manifests, git tracking, verdict

| dossier artefact | manifest | verification | git state at audit |
|---|---|---|---|
| `corpus/live/r90-scout/` | `manifest.sha256`, **208 entries** | **208/208 OK**; covers all worktree files except the manifest itself | **0 files tracked** — entire dir untracked (scout commit `535b2c2` carried only the report) |
| `corpus/live/r90-boundary/` | `manifest.sha256`, **1143 entries** | **1143/1143 OK**; covers all except itself | 45 tracked (probes, analyzers, `RECEIPTS.md`, `analysis.*`, `run_cells.sh`, project copies, manifest); `runs/` (1099 entries) ignored by `corpus/live/.gitignore:1` |
| `corpus/live/r90-author/` | `manifest.sha256`, **4015 entries** | **4015/4015 OK**; covers all except itself | **0 files tracked** — entire dir untracked (48 MB: `runs{1..13}/`, 72 arm reps, `proj/`); the landing commit carried only the two fixtures + `run_battery.py` + report |

Completeness is exact in all three: the only file on disk not listed in each
manifest is the manifest itself (verified by `audit/manifest_completeness.txt`).

---

## 2. Committed-tree identity + fresh battery under load (my behavioural check)

Worktree bytes == committed bytes for every landing file (so "committed tree
only" holds for all execution below):

| file | sha256 | worktree vs `git show ee20575:` |
|---|---|---|
| `corpus/fixtures/rb_lattice.gd` | `10da2291…` (author claim) | **SAME** |
| `corpus/fixtures/rb_watch.gd` | `e349faa0…` (scout pin, verbatim) | **SAME** |
| `corpus/fixtures/run_battery.py` | `76c0b1f5…` | **SAME** |
| `corpus/fixtures/project.godot` | `8de8b3af…` (untouched) | **SAME** |
| `reports/round-90/r90-author.md` | `c53888b2…` | **SAME** |

Cross-seat probe identity: scout `probes/rb_lattice.gd` = `4f201e85…` =
boundary `probes/scout_rb_lattice.gd`; `rb_watch.gd` = `e349faa0…` in scout,
boundary and author `proj/`; author `proj/rb_lattice.gd` = landed fixture
`10da2291…`.

**Fresh battery runs on the committed bytes under load** (`battery-runs/`):

```
rep1 — stamp 20261015T221426402427Z. The worktree was clean of modified tracked
  files when the run started and the process loaded the committed run_battery.py
  (22:14:26Z; a concurrent lane's first tracked edit landed 22:16:20Z, after the
  load).  rows=247  r90 12/12 PASS  r90_expected_errors_all_matched=true
  rows_with_expected_errors=57  loadavg 103.8 at start (48 foreign `yes` hogs)
  fails: transition, audio_bus_route, audio_bus_route_invalid_control,
         probe_error_clause_surface (cascade: dead_entry_count=1 = the audio entry)

rep2b — stamp 20261015T222520528392Z, executed from a `git archive ee20575`
  extract (/tmp/r90-committed; committed shas verified 76c0b1f5/10da2291/e349faa0).
  rows=247  **verdict=PASS (247/247)**  r90 12/12 PASS
  r90 + r89 gates true  census_bare_classifier_consistent=true
  dead_entry_count=0  rows_with_expected_errors=57  0 B stderr
  loadavg 56–65 at start

r90 census (both committed runs): comrefuse entry matched x1 dead=false;
  impedge p_inertia<0 x1 + p_mass<=0 x2 dead=false;
  both bare_classification_rejects=true / allowlisted_classification_passes=true
```

rep1's four failures are the same pre-existing flake classes the author
documented (`transition` scene-readiness, `audio_bus_route*` audio-load, meta
cascade); rep2b is **fully green** on the committed bytes. The r90 surface is
12/12 + gate-true in both.

**Concurrent-lane note (custody).** While this audit ran, a sibling lane (r89
fold) modified tracked files in the worktree (`corpus/fixtures/run_battery.py`,
`corpus/fixtures/geo2d_lattice.gd`, `corpus/.gitignore`, `corpus/live/.gitignore`,
`corpus/live/r89-author/manifest.sha256`) at 22:16:20–22:17:32Z. A first
second-rep attempt that started after those edits therefore ran against the
modified worktree; it is retained under `noncommitted-rep2/` and **excluded**
from the committed-tree evidence, and the clean rep2b above replaces it. This
seat wrote none of those files and left them untouched.

---

## 3. Scout (`r90-scout.md`, `535b2c2`) — all claims verified

- **Stability**: independent recompute over all 12 cells in `runs/` — every cell
  `out_uniq=1`, `err_uniq=1`, constant `rc=[0]`, exactly one `PASS` line;
  `analyze_r90.json` own fields agree (`unstable=[]`, `crash=[]`,
  `error_carrying=['rb_comrefuse']`). Cell rep counts exactly as reported:
  5 cells ×3 (`props`, `comread`, `comrefuse`, `tps120_f120`, `tps120_f60`) +
  7 ×6 (`gravity`, `damp`, `order`, `write`, `impulse`, `freezelock`,
  `contacts`) = **57 canonical runs** (171 receipt files); `runs/` = 193 files
  = 171 + 20 smoke + `driver.log` + `rc-summary.txt`; **71 launches** = 57 + 14
  smoke (10 surviving receipt pairs).
- **`verify_rows.py` re-run**: `rows=10 rejected=[]`; classifier segment sha
  `749fa0607e7707e6…` (identical to the author's and r89's).
- **Values**: `nprops=88` incl. the `Thread Group` header; `comrefuse` stderr
  **286 B** with the single `:376` ERROR + backtrace; `tps120` `g1[y=478.1452,
  vy=932.9641]` / `g1[y=122.5250,vy=478.1458]`; gravity `f60` ladder;
  `f_lock[y=-128.0000,vy=-60.0000]`; contacts `count=1 pos=0.0000,0.3000
  cvel=0.0000,16.3333 entered=1` — all verbatim in the receipts.
- **Arithmetic**: 57 = 15 + 42; 193 = 171 + 20 + 2; 71 = 57 + 14. ✓
- No discrepancy found in this dossier.

---

## 4. Boundary (`r90-boundary.md`, `520ed6d`) — all claims verified; two count/format advisories

- **Receipt census**: 281 `.out` / 281 `.err` / 281 `.rc` (+255 `.wall` — the
  26 `p_*` concurrent runs have no wall file, as `RECEIPTS.md` states); **all
  281 rc=0**; max wall **2.96 s** (bound never hit). Launches reconcile:
  99 base + 54 com + 39 L1 + 15 L2 + 18 delay + 26 par + 36 t30 (two passes)
  + 12 dummy = **299**, retained 281 after the t30 rerun overwrote 18.
- **All 82 cells**: single PASS line and single rc value each
  (`pass_uniq=1`), matching the analyzer's expectation; `pins/*/all_ok=True`
  for the 12 pinned cells.
- **Scout-pin reproduction**: the 9 verbatim scout cells are byte-identical at
  baseline; `sv_order` (15 reps), `sv_freezelock` (18), `sv_contacts` (18) are
  byte-identical **across base/L1/L2/par**. The three quoted "PASS hash"
  literals reproduce exactly **3/3** as **md5 of the PASS line + LF**
  (`764c523cd0c9…` `sv_order`, `3b6250190357…` `sv_freezelock`,
  `0c9cecc3d1ee…` `sv_contacts`) — the digest convention is unstated in the
  report (A6, info). Cross-seat: all 9 boundary `sv_*` PASS lines are
  **byte-equal** to the scout's own receipts.
- **30-tps pairing census** (retained receipts): 12/12 30-tps `order` receipts
  are `late_body` (`cb0_rel=2 obs0_rel=1`; 3 `b_order_t30` + 9 `t30_order`),
  9/9 `t30_lag` are `late_body` (`exp=N=29`), the all-sweep `b_lag_t30_*` are
  `sync0` (`exp=N=30`), and the 3 Dummy `order` receipts are `cb0_rel=-1`. The
  report's §4 "12/12 on disk plus 3/3 in the earlier window" double-counts the
  `b_order_t30` set (A4, low); the first t30 pass's 18 receipts were overwritten
  by design (A5, info).
- **Engine split**: Dummy receipts `ncb=0 tld=-1.0000 drop=y=-100.0000` with
  `pf_delta=30/60` still ticking; `"Jolt Physics"` and `garbage_xyz` both fall
  back to `PhysicsServer2D` byte-identically to DEFAULT (`drop=y=24.5675`).
- **Impulse table**: all 15 lanes reproduce the §5 table (incl. `tiny`
  `iI=1000000`, `nano` ω=`480000016384.0000`, `huge` `iI=0.000000` oracle
  collapse, `neg`/`mass0`/`massneg` refusals `:334`/`:324` ×1/×2, `nan_i`/
  `inf_i` accepted silently, sign lanes ±15/+60).
- **COM**: 18 scenarios ×3 reps; 10 with exactly 1 `:376` ERROR, 8 with 0 —
  exactly the §6 table; `mode 99` and `mode -1` (reads `4294967295`) verified.
- **Stall / settle**: the 300 ms stall trio's near-stall payload is byte-equal
  to the no-stall control (`ncb=90/90`, `tick_dh=1:89`); the 120-frame settle
  window matches the §7 quote (rest `-7.7000` from f60, `so` sleeps, `sf`
  never).
- **Lag closed forms**: 30/60/120/240 tps rows all match `dy = n·g·dt²`
  (2.0417 / 4.0833 / 8.1667 / 0.5104 / 8.1667 / 16.3333 as tabulated), and the
  30-tps `N` bimodality (29 vs 30) is exactly as reported.

---

## 5. Author (`r90-author.md`, `ee20575`) — landing fully verified; one medium receipt-provenance defect

- **Harness arithmetic**: AST at `ee20575`: **CASES = 240 tuples** (228 → 240),
  12 `r90_*` rows; battery rows **247** (235 → 247) in all 14 retained stamps;
  `git show --numstat ee20575 -- run_battery.py` = **74/0** (insertion-only);
  the r90 block sits ahead of the crash/descendant tail, and
  `descendant_pipe_detached_control` remains the penultimate CASES row (no r90
  row sits between it and the tail, as the harness comment requires).
- **Allowlists**: `r90_lattice_comrefuse` (1 entry) and `r90_lattice_impedge`
  (2 entries, `:334`/`:324`) present; the r90 floor gate
  `r90_expected_errors_all_matched` exists in the harness and is **true** in
  the author's rep9 and in my committed rep2b run; `rows_with_expected_errors=57`,
  `dead_entry_count=0` in rep9 and rep2b.
- **Fresh arms**: `verify_arms.py` re-run against the **committed** battery
  (from the `git archive ee20575` extract; `audit/author_verify_arms_committed.txt`)
  → 12/12 `OK`, `out_uniq=1`, `err_uniq=1`, constant rc, `sig_hit=6/6`,
  `cls=6/6`; the two refusal arms `bare_rejects=6/6` (whitelists load-bearing).
  `runs/` = 216 files = 72×3.
- **Battery history**: 14 stamps (13 dirs; `runs12` holds rep12a + rep12b),
  rows=247 each; **r90 12/12 in every stamp after rep1**; rep1 = 11/12 with the
  `r90_lattice_props` pin-transcription failure — the rep1 output **contains**
  `Thread Group` (so the probe was right and the pin was wrong, exactly as
  reported). Greens: `runs9/20261015T212551992799Z` and
  `runs12/20261015T220233737605Z`, both 247/247 PASS. Across all 14 stamps the
  r90 surface is **167/168** row-instances (rep1 11/12; 156/156 post-fix) —
  the report's "156/156" is post-fix-only and reconciles with its parenthetical.
- **Tuple comparisons re-run**:
  `compare.py godot rep9 rep12b` → `common=247 new_only=0 old_only=0
  tuple_mismatches=0`; the 6 differing outputs are exactly the declared classes
  (`api_press`, `release_edge`, `ui_ns` envelope modes, `mp_loopback` uid,
  `route_toggle`/`tween_flash` frames jitter).
  `compare.py godot rep4 r89-rep5` → `common=235 new_only=12 old_only=0
  tuple_mismatches=5` (4 = rep4's flakes, 1 = meta census) and the normalized
  `export_*` step diff 39→41 (+2 fixture scripts) — all as reported.
- **Fold fidelity**: every one of the 12 landed signatures carries
  `eng=PhysicsServer2D tps=60`; all 9 motion rows additionally carry
  `cb0_rel=/obs0_rel=/pf_delta=/tick_dh=` (order also `cbpf_dh=`); the impulse
  row stays in the resolvable band (`iI ∈ {0.031250, 0.024000}`), `impedge`
  pins only typed refusals + the AUTO sentinel. The 10 shared rows are
  **payload-identical** to the scout's verbatim-ready rows with **only** the
  documented fold fields added (`audit/cross_dossier.txt`); the two new rows
  (`impedge`, `lag`) are the boundary's directives §5/§8.8.
- **Dummy vacuity receipt** (`dummy_gravity.out`): `eng=PhysicsServer2DDummy
  ncb=0 cb0_rel=-1`, every body frozen at spawn, `pf_delta=60 tick_dh=1:59`,
  0 B stderr — exactly the §Scope.2 claim; no r90 pin can match it.
- **Defect A1 (medium)**: `f_pair_30tps.rep{1,2}.out` are **not** 30-tps runs.
  `--physics-ticks-per-second` is absent from `godot --help` (4.7.2) and is
  **silently ignored** (engine-level arg: rc=0, 0 B stderr, byte-identical
  output); both receipts are **byte-identical to a 60-tps `--frames=60` run**
  of the committed probe (`probe-tests/a_proj60_f60.out`). A real 30-tps
  control (project setting `physics_ticks_per_second=30`) gives
  `tps=30 ncb=60 … f_normal[y=-7.7000]|f_lock[y=-156.0000]` (`c`), and at
  `--frames=120` gives `ncb=120 tick_dh=1:119` — i.e. the **pairing fields are
  await-count echoes, not rate evidence**; the rate is carried by `tps=` and
  the f30 payload. The report's mechanism sentence is therefore wrong, but its
  **conclusion** (no 60-tps pin can be satisfied by a 30-tps run) is **true and
  independently receipted** here and by the boundary's `proj_tps30` cells: the
  pinned row's `tps=60` + 60-tps f30 values cannot be produced at 30 tps.

---

## 6. Arithmetic cross-check ledger (all reconcile)

| identity | result |
|---|---|
| scout: 57 = 5×3 + 7×6; 193 = 171 + 20 + 2; 71 = 57 + 14 | ✓ |
| boundary: 281 = 299 − 18; 299 = 99+54+39+15+18+26+36+12; 1144 files = 1143 + self | ✓ |
| boundary: 12 late_body = 3 `b_order_t30` + 9 `t30_order`; 9 `t30_lag`; 3 dummy `cb0_rel=-1` | ✓ |
| author: 240 CASES = 228 + 12; 247 rows = 235 + 12; 216 = 72×3; 14 stamps = 13 dirs + rep12b | ✓ |
| author: 57 = 55 + 2 `rows_with_expected_errors`; 167/168 = 11 + 13×12 | ✓ |
| cross-dossier: 10/10 shared rows payload-identical (fold fields only); 9/9 boundary `sv_*` == scout receipts | ✓ |

---

## 7. Adjudication items (ranked)

| id | dossier | item | severity | disposition |
|---|---|---|---|---|
| **A1** | author §"30-TPS deliberately not pinned" | `f_pair_30tps.rep{1,2}` are 60-tps `--frames=60` runs: `--physics-ticks-per-second` does not exist in Godot 4.7.2 and is silently ignored; the "effective rate is carried by the pairing fields" mechanism is wrong (my real-30-tps control: identical pairing fields, different `tps=`/f30 values) | **medium** (evidence provenance; no landed pin affected) | correct the sentence / relabel the receipts; the fold's conclusion stands (my `c`/`d` + boundary `proj_tps30`) |
| **A2** | author §Scope.3 | "heaviest authored cell is `inertia=33` (`iI=0.031250`)" conflates cells: `inertia=33` is the `comread` property-override readback; `iI=0.031250` is the default r=8 circle (I=32); the impulse family's heaviest is the rect (I=41.67, `iI=0.024000`) | low (label-only) | reword in any follow-up citation; conclusion (no lane near the 1e9 collapse) unaffected |
| **A3** | author §"30-TPS…" | "the scout measured the normal-body pairing unstable at 30 tps" — the scout report contains no 30-tps/`late_body` measurement; the 30-tps race is the **boundary's** §2/§4 finding | low (attribution) | attribute to the boundary |
| **A4** | boundary §4 | "12/12 on disk plus 3/3 in the earlier window" double-counts the `b_order_t30` set (part of the 12); no separate earlier-window order receipts exist | low (count-level) | reword; the retained 12/12 late_body census holds |
| **A5** | boundary §0/§4 | the first t30 pass (18 launches) was overwritten by the rerun; "identical second pass" is not receipt-backed (disclosed in the report itself) | info | accept as disclosed |
| **A6** | boundary §0/§2/§7 | quoted "PASS hash" literals are **md5(PASS line + LF)**, reproduced exactly 3/3; the digest algorithm is unstated | info | state the convention in future citations |
| **A7** | author evidence index | `hunt.log` retains only the final rep12 green line; the 14-stamp rep table is backed by `runs*/verdicts.json` (verified), not by the log | info | note |
| **A8** | author §"Full battery" | "13 completed reps × 12 = 156/156" is post-rep1 only; the all-stamp total is 167/168 (rep1 11/12) — consistent with the parenthetical | info | note |

---

## 8. Remaining risks / blockers

1. **Worktree-only custody** for the scout (208 entries, 0 tracked) and author
   (4015 entries / 48 MB, 0 tracked) evidence dirs: both are covered by verified
   manifests but exist only in the worktree; a worktree prune would lose them
   (same convention as prior rounds, recorded not escalated).
2. **A1's sentence, if left uncorrected**, could teach a future author that
   `--physics-ticks-per-second` exists. The landing is safe (the pinned row is
   protected by `tps=` + 60-tps f30 values), but the correction belongs in the
   round ledger.
3. **Host-conditional tokens remain in pins by design** (`nprops=88`, `Thread
   Group`, `tps=60`, 4-dp float fixed points): all seats disclose them; they
   flip loudly on an engine/build change.
4. **Pre-existing flake classes** (`transition`, `audio_bus_route*`) reproduce
   under load in my fresh run — they are not r90-caused (r90 12/12 in all 14
   retained stamps + my run); per the recorded policy the fix is rerun under
   better conditions.
5. Sibling wave-B seats: `r90-critic`, `r90-reviewer` and `r90-simplifier`
   landed their reports while this audit was running (`r90-verifier` was still
   live at report time). They are separate seats and their findings are **not
   adjudicated here** — this audit covers the landing dossier
   (scout/boundary/author) and the committed tree only.
6. **Blockers: none.** No tracked writes, no commits; this report + the
   `corpus/live/r90-scribe/` receipts are the only new files (untracked).

Reproduce the audit:
`sha256sum -c corpus/live/r90-{scout,boundary,author}/manifest.sha256`;
`cd corpus/live/r90-scout && python3 verify_rows.py`; `cd corpus/live/r90-author && python3 verify_arms.py`;
`python3 corpus/live/r90-scribe/audit/{manifest_completeness,scout_recompute,boundary_recompute,author_checks}.py`.
