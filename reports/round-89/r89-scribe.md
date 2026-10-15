# game-dev-2d round 89 — scribe (r89-scribe): evidence custody + claim audit across the four-report dossier

Seat `SCRIBE` (LEAF) | lane `g2d-r89-scribe` | round 89 | host **devin**.
Read-only audit: **no tracked file written, no commit, no runtime invoked**. The
only write is this report (new, untracked). Every number below was recomputed
from the receipts on disk; nothing is quoted from the reports under audit.

Audit-time repository state: HEAD **`8cea888`** (*r89 author: Geometry2D lattice
+ input89 edges — 20 rows 215->235 …*), `git status --porcelain` clean of
modified tracked files. The four dossier reports are themselves **tracked**:
scout `7fd640f`, boundary `5be63e9`, baseline `3c1aad8`, author `8cea888`.

**Custody verdict: HOLDS.** All four manifests verify (one benign self-entry
exception, A7), every claim class I could recompute from receipts reproduces
byte-for-byte, and the arithmetic reconciles everywhere. The discrepancies
found are count/label-level, one partial-reconstruction advisory on the
boundary's mode-frequency table (A4), and report-state drift where a seat's
"no commit" claim was superseded by its own later lane commit (A6). **No
claim-level falsification touches a landed pin, an envelope payload, or a
verdict.**

---

## 0. What was run (method)

| # | check | command shape |
|---|---|---|
| 1 | manifest verification (all four) | `sha256sum -c manifest.sha256` / `-c receipt-shas.txt` in each `corpus/live/r89-*` |
| 2 | manifest completeness | compare manifest entry set vs `os.walk` file set per dir |
| 3 | git-object cross-check | `git show <rev>:corpus/fixtures/… \| sha256sum`; `git archive 0628932 \| sha256sum`; `diff -rq` archive-extract vs frozen tree |
| 4 | scout stability recompute | re-derived `out_uniq/err_uniq/rc` and signature presence for all 24 cells from `runs/` (not trusting `analyze_r89.json`) |
| 5 | scout/author row verification | ran `verify_rows.py` / `verify_arms.py` (read-only, AST-extracted production classifier) |
| 6 | author identity claims | re-ran `corpus/live/r88-baseline/compare.py godot` for rep4↔rep5 and rep4 vs baseline runs1/runs2 |
| 7 | CASES arithmetic | AST-parse of `corpus/fixtures/run_battery.py` at `fd59c11`, `2c4b1ff`, HEAD; envelope payload byte-compare |
| 8 | receipt reconciliation | per-prefix receipt counts vs each report's §0/§8 arithmetic |

No `lsp` device is present on this host (unchanged state, same as all four
audited seats); no symbol edits were performed by this seat.

---

## 1. Custody table — manifests, git tracking, verdict

| dossier artefact | manifest | verification | git state at audit |
|---|---|---|---|
| `corpus/live/r89-scout/` | `manifest.sha256`, **330 entries** | **330/330 OK**; covers all worktree files except `RECEIPTS.md` + the manifest itself | **0 files tracked** — entire dir untracked (scout commit `7fd640f` carried only the report). Evidence lives in the worktree only |
| `corpus/live/r89-boundary/` | `manifest.sha256`, **2153 entries** | **2153/2153 OK**; covers all except itself | 17 tracked (probes, `run_all.py`, analyzers, `proj/` copies, manifest); `runs/` (2136 entries) ignored by `corpus/live/.gitignore:1` (`runs/`) |
| `corpus/live/r89-author/` | `manifest.sha256`, **1713 entries** | **1712/1713 OK**; single failure is the manifest's stale **self-entry** (claims `c605ee8f…`, actual `cb2bdc9c…`) — A7 | 1317 tracked; `runs/` (396 files, the fresh-arm receipts) git-ignored, covered by the manifest only |
| `corpus/live/r89-baseline/` | `receipt-shas.txt`, 31 receipt lines (+3 header lines) | **31/31 OK**; frozen tree 95886 entries present; `fileset-diff-{pre,post}` both empty-string sha `e3b0c442…` | 527 tracked (freeze/, runs1/runs2 verdicts, runners, report); `tree/` ignored (`live/*/tree/`) |

Cross-checks: scout probe/fixture shas appear **identically** in all three
copies — `geo2d_lattice.gd` `9784716b…` (scout probe = boundary `proj/` copy =
landed fixture), `input89_edges.gd` `601c223e…`, `project.godot` `8de8b3af…`.
Author `manifest.sha256` committed at HEAD has the same self-entry as the
worktree copy (`git show 8cea888:… | sha256sum` = `cb2bdc9c…`).

---

## 2. Baseline (`r89-baseline.md`) — all claims verified

| claim | receipt | verdict |
|---|---|---|
| 215 rows ×2 reps, PASS | `runs1/20261015T185850976403Z` and `runs2/…` verdicts: `results` len **215**, `Counter({PASS:215})`, 0 non-null `error`, top verdict PASS | ✓ |
| verdict shas `4389b713…` / `1dc26e0b…` | recomputed sha256 = report values; receipt-shas `-c` OK | ✓ |
| stdout 216 PASS lines; stderr 0 B | `grep -c '^PASS '` = 216/216; stderr files 0 B (`e3b0c442…`) | ✓ |
| tuple files "each 215 rows" | 217 lines = 2 header lines (`# rows=215 …`) + 215 tuple rows; all three pairwise `tuple-diff-*` = `e3b0c442…` | ✓ |
| ref = r88-verifier `70bf54f2…` | file exists, sha matches; `compare.py` ref_rows=215 PASS | ✓ |
| rep times 202.849 s / 223.971 s; loads | `rep-timing.txt` lines match verbatim | ✓ |
| frozen HEAD `0628932…`; archive sha `cd0736b7…` | `freeze-head.txt` matches; `git archive 0628932 \| sha256sum` reproduced **exactly** `cd0736b7…` | ✓ |
| file-set 95886 == 95886; content vs HEAD rc=0 | 95818 files + 68 symlinks = 95886; `freeze/tree-files-{pre,post}.txt` and `git-ls-files.txt` all sha `b9e1f163…`; **audit re-check**: `git archive 0628932 \| tar -x` → `diff -rq` vs `tree/` = empty, rc=0 | ✓ |
| frozen harness/fixtures `fde5913b…`/`78370a04…`/`89b9ddbe…` | `git show 0628932:…` shas identical; `git diff f9e8a5b 0628932 -- corpus/fixtures/` empty | ✓ |
| raw deltas rep1 11 = 2 env+8 vol+1 uid; rep2 12 = 3+8+1; normalized 3/4; not-carried 7 | `freeze/compare-rep{1,2}-vs-ref.txt` state exactly these numbers and classes | ✓ |
| envelope matrix §3.3 | `freeze/envelope-rep{1,2}-vs-ref.txt`: rep1 `release_edge` mode[1], `ui_ns` mode[1]; rep2 `pre_frame` mode[1]; ref `press_phys`+`ui_ns` mode[1]; all tuple_identical=True | ✓ |
| `mp_loopback` uids ref `364173685`, rep1 `711476664`, rep2 `1665996349` | present verbatim in the receipts | ✓ |
| F-A/F-B flakes did not manifest | both reps: `PASS crash_spontaneous_sigabrt: exit=-6 …`; `phys_peer … ev_step_delta=0` | ✓ |
| "HEAD contains `3c47eee` → 215-row scope" | `git merge-base --is-ancestor 3c47eee 0628932` → YES | ✓ |

---

## 3. Scout (`r89-scout.md`) — claims verified; three count-level discrepancies

Verified from receipts:

- **Probe/tool shas**: every sha prefix in §9 reproduces exactly
  (`9784716b…`, `601c223e…`, `d4feb378…`, `8de8b3af…`, `1bcaeba7…`,
  `f3e35d1e…`, `7b49e47d…`, `2d9c18e4…`, `ce631ced…`, `0dbb9dd5…`,
  `91b69859…`).
- **Stability**: independent recompute over all 24 cells in
  `analyze_r89.json` against `runs/` — `out_uniq=1`, `err_uniq=1`, constant
  rc vector, claimed signature present, **0 mismatches**; JSON's own
  `unstable=[]` holds. 21/24 cells emit 0 B stderr; non-zero are
  `lineempty` (377 B), `atlasempty`, `polyendpoly`.
- **`verify_rows.py` re-run**: `rows=20 rejected=[]`, classifier segment sha
  **`749fa0607e7707e6…`** — identical at `fd59c11`, `2c4b1ff`, and HEAD (the
  author's insert did not touch `classify_process`).
- **Crash row**: `geo_lineempty` rc `134,134,134`, stderr 377 B Clipper2
  assert, stdout carries only the pre-call `R89 lineempty call=…` line.
- **Expected errors**: `atlasempty` stderr = `ERROR: Condition
  "p_rects.is_empty()" is true.` + `at:: make_atlas …:148`; `polyendpoly` =
  `ERROR: Attempt to offset a polyline like a polygon (use offset_polygon
  instead).` — both byte-match the §6.3 entries.
- **tps split** (§3.9): `tps120` 60f → `y=22.5250 vel=0.0000,478.1458`;
  `tps120` 120f → `y=82.3000 vel 0,0`; 60 tps → `y=82.3000` — all verbatim.
- **Ring/hole law** (§3.10): `ringhits` receipt carries
  `A_contour0[centre:1…] B_both[centre:2…] C_slabs[centre:0…]`; ring drop
  `y=-47.8043` — verbatim.
- **Zero pre-existing coverage**: `git grep -ic 'geometry2d\|geo2d'
  corpus/fixtures/` at `fad0b1e` and at `2c4b1ff` → **0**.
- **Arithmetic**: 99 canonical runs = `15×3 + 9×6` ✓; 128 launches =
  99 + 2 + 27 ✓; 27 = 18 + 6 + 3 ✓; `runs/` = 312 files = 99×3 + 2×2 + 9
  + 2 summaries ✓.

Discrepancies (adjudication items below): **A1** — the report says "23 cells"
/ "23/23" / "23 arms" in five places, but its own artifact
(`analyze_r89.json`) has **24 cells, 24 unique signatures, 22 distinct arm
names**, and the probe's `match arm:` block dispatches **20** geo arms
(+2 input arms); the "primary probe, 17 arms" line is likewise low. **A2** —
§0 "The 191-row battery" matches no commit: CASES was 175 at the scout's
session HEAD (`fad0b1e`/`96c0b13`) → 182 rows, 200 → 207 at r87, 208 → 215
at `fd59c11`; no 191-row state found. **A3** — "27 superseded runs" are not
individually retained (only the 3 `runs/fmtbug/` reps); `rc-summary.txt` is
per-cell, not per-run. **A9** — §6.1's "20 rows" enumeration sums to 19
(15 geo + 2 input + atlasempty + polyendpoly); the 20th is the §6.2 optional
`lineempty`, which the file and the landed battery do carry. **A10** — §0
"All 12 pure/boundary arms … 9 of them emit 0 B stderr": actual is 21/24
cells zero-stderr (9 of the 11 round-1 pure cells).

---

## 4. Boundary (`r89-boundary.md`) — claims verified; one partial-reconstruction advisory

Verified from receipts:

- **545 receipt triples** exactly: 545 `.out` / `.err` / `.rc` (+492 `.wall`).
  Reconciliation: 309 edge (103 subs ×3) + 120 row (20 ×6) + 54 bridge
  + 14 ring + 24 exact-mode + 6 diag + 18 variant = **545** ✓.
- **Manifest 2153/2153 OK**; probe/tool shas all match (`723f2e26…`,
  `10c849c1…`, `857eeb93…`, `2b18f76f…`, `a07c7691…`, `d7100c85…`,
  `1c6c6360…`); `proj/` scout copies byte-identical.
- **Row stability**: `rows-analysis.txt` = 20 rows, 19 × `sig_hits=6/6`,
  `input89_edges_exact` `sig_hits=0/6` → 19 CONFIRMED / 1 UNSTABLE ✓.
- **Bridge race-immunity**: 54/54 bridge receipts end at `82.3000` (4 of them
  — `hold` — pin it as `rest60`/`rest120` keys); Case A = 8 (`first=y=-100.000000`),
  Case B = 28 (`first=y=-99.727776 v=16.333334`), 36 with the class
  diagnostic ✓. `hold` receipt: `rest60 == rest120 == 82.300003` ✓.
- **Ring**: 14/14 ring receipts `drop_center=y=-47.8043 … hits=1` ✓;
  `ringhits` 6/6 ✓.
- **Edge killers** (all 3-rep stable out/err): 7 SIGABRT subs
  (`bool_huge_1e15` rc `134,-6,-6` + 43 B bare abort; `1e18`, `3e38`,
  `bool_inf_clip`, `off_inf_poly`, `line_inf` each `-6` ×3 + 43 B;
  `atlas_huge` `-6` ×3 + **2331 B** FATAL dump), `bresenham_nan` `-9` ×3
  (0 B stderr, hang), `line_empty_reverify` `-6` ×3 + 377 B ✓.
- **NaN/tiny laws**: `merge(nanpoly,sq)` k=2 with `-70368744177664.0000`;
  `off_nan_poly` `-92233718038528…`; `hull_nan` n6 with `nan`;
  `dec_nan` n4 with `nan`; scale ladder `s=1e-4 clip=1 → 1e-5 clip=0`;
  `s=1e-6 merge=0` — all verbatim in receipts.
- **Stale tps120 probe**: `corpus/live/r89-scout/proj_tps120/geo2d_lattice.gd`
  sha **`142780459b…`**, `_arm_bridge` **byte-identical** to the current
  probe, lacks `ringhits`/`polyendpoly`, contains the `%e` bug (3 hits) —
  exactly as §7 states.
- **Load-bimodality headline**: the load claim itself is fully receipt-backed
  — row test 6/6 mode L (`row_input89_edges_exact`), quiet 12/12 mode Q
  (`exact_mode_quiet` + `exact_pipe_quiet`), controlled series 8 Q / 4 L
  (`exact_mode_load` 12), ladder log 16-hog 2 Q / 1 L and 24-hog 3 L.

Discrepancy **A4** (advisory): the §2 frequency table (quiet 20/20; loaded
51 = 24 Q / 27 L = 71 observations) is **not fully reconstructible** from
retained artifacts. Retained mode observations: 48 receipt runs (Q 38 / L 10)
+ 18 `hog-ladder2.txt` log lines (Q 13 / L 5) = **66**. The specific
"quiet ×5", "first loaded ×5", "interleaved ×12", "scout+v1+v4 ×10" series
have no retained per-run receipts or log lines (the 18 `variant_v{1,2,4}_load`
receipts are the mechanism probes, all Q). The conclusion (load-bimodality,
envelope repair) is unaffected. **A5**: §1 row 9 "103/103 … byte-stable"
vs the shipped analyzer's `subs=102 … UNSTABLE=1` — the 103rd sub is
`sanity` (excluded by `analyze_edges.py` by construction); `UNSTABLE=1` is
`bool_huge_1e15`'s mixed shell/Python rc vector, disclosed in §4.1.

---

## 5. Author (`r89-author.md`) — every landed claim verified

| claim | receipt | verdict |
|---|---|---|
| fixtures verbatim, 581/140 lines | `geo2d_lattice.gd` = `9784716b…` = scout probe; `input89_edges.gd` = `601c223e…`; `project.godot` = `8de8b3af…` (untouched) | ✓ |
| CASES 208 → 228; rows 215 → 235 | AST: `fd59c11` 208, `2c4b1ff` 208, HEAD/worktree 228; all 5 reps `results` len 235 | ✓ |
| +82/−0, insertion-only | `git diff --numstat 2c4b1ff HEAD` = `82 0`; 20 r89 rows directly after `r88_surfaces_vis_not`, before the crash/descendant tail; no CASES row between `descendant_pipe_detached_control` and the tail | ✓ |
| envelope payloads | `input89_edges_exact` signature is a 2-tuple; payload[0] = quiet Q, payload[1] = loaded L; payload[1] **byte-identical** to the boundary's mode-L line and to all 12 hogged author reps | ✓ |
| `expected_errors` +2 exact | both dict entries present; rep5 census shows `atlasempty matched=1`, `polyendpoly matched=2` | ✓ |
| r89 floor gate | `r89_expected_errors_all_matched` over `("geo2d_lattice_", "input89_edges_")` in `discriminations`; rep5 value **true** alongside r87/r88/phys2d = true, `dead_entry_count=0`, `rows_with_expected_errors=55` (baseline receipt = **53**) | ✓ |
| 5 battery reps | rep1 232 PASS/3 FAIL (`transition`, `audio_playback`, `input_lattice_pre_frame`); rep2 234/1 (`pre_frame`); rep3 232/3 (`negative_transition`, `audio_bus_route_invalid_control`, `probe_error_clause_surface`); rep4/rep5 **235/235 PASS**; all 20 r89 rows PASS in all 5 (100/100) | ✓ |
| rep4↔rep5 tuple identity | re-ran `compare.py`: `common=235 tuple_mismatches=0`; raw diffs = envelope rows (`pre_frame`, `press_phys`) + `mp_loopback` uid | ✓ |
| prior-row identity | re-ran `compare.py` vs baseline runs1/runs2: `common=215 new_only=20 old_only=0 tuple_mismatches=2` (seeded `input_lattice_phys_peer`, meta `probe_error_clause_surface`); `phys_peer` signature is a `Constant` at `0628932` and a 6-tuple from `fd59c11` on | ✓ |
| fresh-arm evidence | `verify_arms.py` re-run: 20/20 `OK`, `out_uniq=1 err_uniq=1`, constant rc, `sig_hit=6/6`, `classified=6/6`; `lineempty` rc 134 ×6; `runs/` = 396 files = 132 runs ×3 | ✓ |
| mode series | quiet 6/6 Q; 12/12 hogs L byte-identical to boundary §2 text; battery reps1–3 raw `inex=false` (L), reps4–5 `inex=true` (Q), all PASS | ✓ |
| only harness file touched | `git show --name-only 8cea888` = `geo2d_lattice.gd`, `input89_edges.gd`, `run_battery.py` (+ r89-author evidence + report) | ✓ |

Discrepancies: **A6** — "No commit. Worktree: `M run_battery.py`, `?? …`"
was true when written but is **superseded**: the work landed as commit
`8cea888` (17:05:40 local) including this report; all audited bytes equal the
committed bytes. **A7** — manifest self-entry (above). **A8** — the
baseline-comparison narrative lists only the 2 tuple mismatches; the
normalized output diff also carries `export_preset_missing` /
`export_readiness` "39 steps" vs "37 steps" (the +2 fixture files), tuple-neutral
and unlisted. **A1b** — the fixture comment repeats the scout's "23-cell"
count (should be 24).

---

## 6. Arithmetic cross-check ledger (all reconcile)

| identity | result |
|---|---|
| scout: 15×3 + 9×6 = 99 canonical; 99+2+27 = 128 launches; 27 = 18+6+3 | ✓ |
| scout: runs/ 312 = 99×3 + 2×2 + 9 (fmtbug) + 2 summaries | ✓ |
| boundary: 545 = 309 + 120 + 54 + 14 + 24 + 6 + 18 | ✓ |
| boundary: loaded table 51 = 6+5+12+10+12+3+3; 24 Q / 27 L internally consistent (but see A4 for receipts) | ✓ arithmetic / ⚠ custody |
| author: 208+20 = 228 CASES; 215+20 = 235 rows; 396 = 132×3 runs | ✓ |
| author: rows_with_expected_errors 53 → 55 (+2) | ✓ |
| baseline: 217 tuple lines = 2 header + 215; 95886 = 95818 files + 68 symlinks | ✓ |
| cross-dossier: scout 99-run surface ⊂ boundary 120-row replay (20×6); author 132-run replay ⊂ boundary probe shas | ✓ |

---

## 7. Adjudication items (discrepancies, ranked)

| id | dossier | item | severity | disposition |
|---|---|---|---|---|
| **A1** | scout (+author comment) | "23 cells / 23 arms / 23/23" vs artifact: 24 cells, 24 unique signatures, 22 distinct arm names, 20 geo dispatch arms; §9 "17 arms" also low | low (label-only; no pin affected) | correct in any follow-up citation; consider amending the fixture comment |
| **A2** | scout §0 | "The 191-row battery" matches no commit (175→182 at session HEAD, 200→207 r87, 208→215 at fold) | low (stale context figure) | note; the substantive zero-coverage claim is independently true (0 grep hits) |
| **A3** | scout §1/§8 | 27 superseded launches not individually receipted (only 3 fmtbug retained; rc-summary is per-cell) | advisory custody | accept as disclosed; if the wave requires per-launch receipts, retain them next time |
| **A4** | boundary §2 | mode-frequency table (71 obs; quiet 20/20; loaded 51 = 24/27) only partially reconstructible: 66 observations recoverable (48 receipts + 18 ladder-log lines); the ×5/×12/×10 file series have no retained artifacts | **medium-advisory** | headline conclusion is receipt-backed; either retain those series' receipts or restate the table as sampled |
| **A5** | boundary §1/§4 | "103/103 byte-stable (one rc-convention flag)" vs shipped analyzer `subs=102, UNSTABLE=1` (103rd = `sanity`, excluded by analyzer; UNSTABLE = mixed rc convention, disclosed in §4.1) | low | wording; no action needed |
| **A6** | author | "No commit" superseded by lane commit `8cea888`; `runs/` (396 files) is git-ignored, so the committed manifest is the only git-carried coverage of the fresh-arm receipts | info (resolved) | note in the round ledger |
| **A7** | author manifest | 1/1713 entries fails: `./manifest.sha256` self-entry claims `c605ee8f…`, actual `cb2bdc9c…` (stale self-hash; scout/boundary manifests exclude themselves) | low | state "1712/1713 + stale self-entry" in any manifest claim |
| **A8** | author §"Prior-row identity" | unlisted normalized diffs `export_preset_missing`/`export_readiness` (39 vs 37 registration steps; consequence of the +2 fixtures) | info | tuple-neutral; acceptable |
| **A9** | scout §6.1/§6.2 | "20 rows" enumeration sums to 19 + the §6.2 optional `lineempty` = 20; landed inventory and `author-rows.py.txt` both carry 20 including `lineempty` | low | consistent as landed; clarify the optional-row accounting |
| **A10** | scout §0 | "12 pure/boundary arms … 9 of them 0 B stderr" — actual 21/24 cells zero-stderr (9 of 11 round-1 pure) | info | wording |

---

## 8. Remaining risks / blockers

1. **Worktree-only custody for the scout evidence** (330 entries) and the
   author's ignored `runs/` (396 entries): both are covered by verified
   manifests but exist only in the worktree — a worktree prune would lose
   them. Same convention as prior rounds (r87/r88 scout dirs also 0 tracked),
   recorded, not escalated.
2. **Boundary mode-frequency table** — see A4; the load-bimodality decision
   does not depend on the unreconstructible rows.
3. **Host-conditional tokens remain in pins by design** (`joys=0`,
   `nmethods=86`, `tps=60 frames=60`): all four seats disclose them; they flip
   loudly on host/build/config change.
4. **`compare.py` normalizer** still cannot mask `uid_c=`/`s_conn<digits>`
   (baseline §7.3): cosmetic, tuple-neutral.
5. During the audit a concurrent git repack made `0628932` briefly
   unreadable (`packfile … index unavailable`); retried successfully —
   frozen-tree identity re-proven via `git archive | tar -x` + `diff -rq`
   (rc=0). No evidence affected.
6. Blockers: **none**. No tracked writes, no commits, no runtime invoked by
   this seat; this report is the only new file (untracked).

Reproduce the audit: `sha256sum -c corpus/live/r89-{scout,boundary,author}/manifest.sha256`;
`cd corpus/live/r89-scout && python3 verify_rows.py`; `cd corpus/live/r89-author && python3 verify_arms.py`;
`python3 corpus/live/r88-baseline/compare.py godot corpus/live/r89-author/runs5/<stamp>/verdicts.json rep4=…/runs4/<stamp>/verdicts.json`;
`git archive 0628932 | tar -x -C /tmp/f && diff -rq /tmp/f corpus/live/r89-baseline/tree`.
