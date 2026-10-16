# r98 reviewer — independent re-derivation of the CanvasItem draw/transform lattice on committed bytes

Seat `REVIEWER` (lane `r98-reviewer`) | round 98 | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, `--headless`) | Python 3.14.7.

**Commit verified: `9d421fb2c0577488cf6f34399c123d81a91a067b`** ("r98 author:
canvas/draw-flush lattice (32 rows, 426->458)", parent `f67094bb` = r97 author
landing; confirmed an ancestor of `main`). Lane repo HEAD was `2dcbb6f6` (r100)
when the archive checkout was taken and advanced to `9ede7c50` ("r97-r100
integration fix: dedupe crash sentinel CASES rows", 509/509 unique) while this
review ran — later landings are out of scope here; the review targets the pinned
r98 landing. The r98 block is present and unchanged at `9ede7c50` (32 r98 rows),
so this verdict is not invalidated by the fix. The landing was re-derived from an
archive checkout of the committed tree at `9d421fb2`, never from the author's
worktree.

**`lsp` disclosure.** No `lsp` device is exposed to this seat (the session's tool
list carries none) and no `lsp` CLI or GDScript/Python language server exists on
this host (`command -v lsp` → none). `definition`/`references`/`diagnostics`
were therefore **unavailable for every file in scope**; that is a recorded
unavailability, not a clean result. Semantic checks are `ast.parse` of the
landed `run_battery.py`, AST-extracted execution of the production
`classify_process`, and the engine launches below (one landed battery run of 463
case launches plus its meta probes, 65 direct row launches, 5 independent
law-probe launches). Text search was used only for
literal evidence (line numbers, hashes, signature containment) and is never
presented as semantic proof.

## Verdict

**PASS with findings.** Every substantive r98 claim re-derives on the committed
bytes: the landed battery is **470/470 PASS, 0 FAIL** (all 32 r98 rows PASS),
the three allowlist entries are live and load-bearing, the 32 row signatures are
byte-identical to the author's derived rows, the r98c_flush row rejects its own
mechanism mutation, and three headline laws re-derive from probes written by
this seat. The findings are about **which bytes the author's green evidence is
bound to** (F1) and two cosmetic consequences of the landing rebase (F2, F3);
none of them is a behavioral defect.

## Evidence re-derived on the committed bytes

| # | check | method | result |
|---|---|---|---|
| 1 | committed tree identity | `git archive 9d421fb2 corpus/fixtures` → 98 files, each `git hash-object`-compared to its `git ls-tree` blob sha | **0 mismatches** (checkout at `/home/vgpnk/r98-review/archive`) |
| 2 | landed `run_battery.py` hash | `sha256sum` of the checkout vs `git show 9d421fb2:…` | `df4563c8ec1f22c31ea1c60fc10817fabeec20ae29b376d8ab4579f891bac973` |
| 3 | fixture hashes vs report | `sha256sum` of the four landed fixtures | `866480a1…` (canvas), `2e71c715…` (attack), `7bb51902…` (rksenum), `c038f748…` (flush) — all four **equal the report's table** |
| 4 | byte-copy provenance | `cmp` of each fixture vs the frozen upstream probe + upstream `manifest.sha256` entries | 3/3 **clean**; upstream manifests verify in the main clone (r98-scout 505/505, r98-boundary 1068/1068 entries, 0 missing, 0 bad) |
| 5 | **full battery on landed bytes** | `python3 corpus/fixtures/run_battery.py` from the archive checkout | **470 rows, 470 PASS, 0 FAIL**, payload `verdict: PASS`; all **32 r98 rows PASS**; `r97_expected_errors_all_matched=true`, `r98_expected_errors_all_matched=true`; `dead_entry_count=0`; r98 allowlist census `matched_lines` **2 / 1 / 6**, `dead_in_run=false`, `shape=exact` (runs: `/home/vgpnk/r98-review/runs1/20261016T092635441993Z/verdicts.json`) |
| 6 | row census on landed bytes | AST `literal_eval` of `CASES` | **463 CASES** (431 at parent), 463 unique names, **32** r98-prefixed tuples; rows = 463 + 7 meta = **470** |
| 7 | landed r98 rows vs author rows | AST tuple-by-tuple compare of the landed `CASES` r98 block vs `corpus/live/r98-author/author-rows.py.txt` `ROWS` | **0 diffs** (32/32 tuples identical, incl. flags and signatures) |
| 8 | landed classifier identity | `ast.get_source_segment` of `classify_process` from the landed file | `749fa0607e7707e614c1ab157a6f8e756dfc2f460746e6d218e6734ad8fa72c3` — **equal to the segment the report pins** (and to r89/r90/r91/r95/r96) |
| 9 | author receipts (claim check) | 1446 files under `corpus/live/r98-author` hashed against its own `manifest.sha256` | **1446/1446 verify**, 0 missing, 0 bad; all **186** cell receipts (31 cells × 2 reps × 3 batches) have `rc=0`; the two battery runs it reports are 458 rows / PASS / 32 r98 rows PASS |
| 10 | receipt re-classification | every receipt of every cell classified with the **landed** `classify_process` and the **landed** signatures (this seat's own script, not the author's analyzer) | 32/32 rows match **their own cell 6/6**, **0 foreign-cell hits**, 0 rows without a hit — reproduces `ROWS=32 / hits 6/6 / REJECTED=[]` |
| 11 | direct re-derivation of the 32 rows | own fresh scratch project built from the landed fixtures; the battery's own launch shape (`godot --headless --path … --script res://… -- <flags>`, 8 s bound); **2 reps each** | **64/64 PASS**, 0 FAIL (2.6–2.8 s for `r98c_flush`, 0.55–1.2 s for the rest) |
| 12 | rep-to-rep stability | landed-signature classification of rep1 vs rep2 (and vs the harness run) | all pinned keys stable; the only moves are the keys the report **declares** unstable — `r98b_qorder` `stagger`/`stagger_off`, `r98b_qflush` `hide_span_pf` (2 vs 3) — and those keys are not in any pinned signature |
| 13 | mutation of the new row | `pace.delay_ms = 80` → `= 0` on a scratch copy, landed signature, landed classifier | mutant **REJECTED** (flips `multitick_frames_ge2` 1→0, `draws_gt_frames` 1→0, `max_draws_per_pf_ge2` 1→0, `hide_ticksep_same_frame` 1→0); the clean receipt is accepted — the multi-tick regime is caused by the process-step block |
| 14 | signature bleed | every r98 signature searched across all 470 rows' merged outputs | no unintended bleed: the only shared lines are the two declared same-arm pairs (`r98b_qflush_same_frame`/`_suppress`, `r98b_qorder_tree`/`_flat`), each gating disjoint key sets; the `qflush_suppress` fragment does **not** occur in `r98c_flush`'s line |
| 15 | independent law probes (this seat's own bytes, `review_laws{,2,3}.gd`) | epsilon law; clip refusal/cast; the 200-combo ctor / R·K·S grid | epsilon ratio **exactly 1e-5** at parent scale 0.5 / 2 / 100; `clip_children` `== MAX(3)` refused (previous kept), `-3`→`4294967293`, `INT_MIN`→`2147483648`; grid **`combos=200 ctor_fail_n=75 ctor_fail_z=75 ctor_fail_nz=0 rks_fail_n=72 rks_fail_z=12 rks_fail_nz=60 first_fail=ctor@25(r=0.00,s=0.00,0.00,k=0.00)`**, `sign_pairs=++=24,-+=12,+-=12,--=12`, `max_abs_diff=0.000000477` — **all equal the landed `r98b_skewgrid` / `r98b_rksenum` pins** |
| 16 | merge fidelity of the rebase | AST compare of landed vs parent vs branch `CASES` | landed stree rows == parent stree rows (12); landed r98 rows == branch r98 rows; landed non-r98 rows == parent rows **exactly**; both lines the diff "deletes" reappear verbatim as a line prefix and a substring |

## Findings

### F1 (major, report↔bytes integrity) — the author's green evidence is bound to the pre-rebase branch bytes, not to the landed commit

The landing `9d421fb2` was rebased onto post-r97 HEAD (`f67094bb`), so the file
that landed is **not** the file the author ran. Evidence:

- The author's own `corpus/live/r98-author/final_bytes.sha256` records
  `b5b86169c962f22ae591c8e729fa778f8d6819de88389546cdbee502028f65fa` for
  `corpus/fixtures/run_battery.py` — that is exactly `git show
  68bee6e7:corpus/fixtures/run_battery.py` (the author's branch commit), while
  the landed blob is `df4563c8…` (row 2 above).
- Both author battery runs are **458 rows** = 451 CASES + 7 meta (its branch
  base, r96 `89f85ed8`, had 419 CASES); the landed file has **463 CASES / 470
  rows** because the rebase re-applied r97's 12 `stree_lattice_` rows and r97's
  gate. The landed bytes were therefore **never battery-run by the author**.
- Consequently the report's arithmetic — "CASES 419 → 451", "results rows 426 →
  458", "`git diff --numstat` = `150 0`", "`grep -c '^-[^-]'` → 0" — describes
  the branch file, not `9d421fb2`. (The commit message itself says "Author
  greens 458/458 x2 **on branch bytes**", so the divergence is disclosed there
  but not in the report body, which calls those bytes "final bytes".)

Not a behavioral defect: this seat's landed-bytes run is **470/470 green** and
every r98 row passes on both paths (rows 5, 11). But the report's evidence block
cannot be cited for the landed artifact; the landed green is this report's (or a
fresh author re-run's), not the author's.

### F2 (minor, cosmetic) — the landed diff is not insertion-only: `+150 / −2`

`git diff --numstat f67094bb 9d421fb2` gives **150 2** (three hunks: +123 at
`CASES`, +17 `expected_errors`, +10 floor gate). The two deletions are line
re-joins introduced by the rebase: the r97 `stree_lattice_scene_probe` tuple
line now carries the r98 comment header on the same line, and the `r98c_flush`
tuple line now carries the `("crash_spontaneous_sigabrt", …)` tuple. Both
deleted lines reappear **verbatim** (row 16), `ast.parse` is clean, and the 463
case names are unique — so the file is content-equivalent to a pure insertion,
but "insertion-only, +150 / −0" (report §Files changed, RECEIPTS.md) holds only
for branch commit `68bee6e7` (`git diff --numstat 89f85ed8 68bee6e7` = 150 0,
0 deletions — confirmed).

### F3 (minor, stale referent) — the independent-probe line range and "CASES 451" refer to the branch file

The report's probe section places the r98 `CASES` block at
`run_battery.py:1228–1350`; on the landed file the block is at **1281–1403**
(header joined onto line 1281, tuples 1340–1403). Same root cause as F1/F2. No
consequence for the rows.

### Positive findings worth recording

- The three `expected_errors` entries are **live and load-bearing** on the
  landed bytes (census `matched_lines` 2 / 1 / 6, `dead_in_run=false`,
  `dead_entry_count=0`, gate `true`) and are byte-equal to observed engine
  lines (`shape=exact`, `first_match` == entry).
- The declared-unstable key set is **honest**: the only keys that moved across
  reps/harness in this seat's own runs are `r98b_qorder` `stagger`/`stagger_off`
  and `r98b_qflush` `hide_span_pf` — precisely the keys the block header
  declares "deliberately NOT authored". No pinned key moved in any of the 3
  observations of the 32 rows.
- The `r98c_flush` row is not an echo pin: its own mutation (delay 80→0) is
  rejected while the clean line is accepted.
- Three headline laws were re-derived with this seat's own probes, not by
  re-running the author's: the 1e-5·parent-scale epsilon law, the
  `clip_children` refusal/uint32-cast law, and the full ctor / R·K·S grid
  (including the 4.77e-7 max component diff and the sign-pair split).

## Residual risk and verification gaps

1. **No second full battery run on the landed bytes** (wall clock; one landed
   run = ~7.5 min, 470 rows). The r98 rows carry 2 direct reps + 1 harness rep
   each, so rep-to-rep coverage exists for the reviewed rows, not for the whole
   470-row suite on landed bytes.
2. **Load/host caveat (honest).** The landed battery ran with concurrent lanes
   active (loadavg 9.5–15.2 1-min, 12.7–12.9 5-min, 24.7 15-min), and the
   direct reps ran afterwards. Every row was still green; timing-sensitive rows
   (`r98c_flush`, `r98b_qflush`, `r98b_qorder`) passed with the pinned keys
   unchanged, but this is a loaded-host observation, not a quiet-host one.
3. **`/tmp` deviation.** `/tmp` is tmpfs with `usrquota`; during this seat's
   window every `tar` write failed with `EDQUOT` (verified with `dd`), so the
   fresh `git archive` checkout was materialized under
   `/home/vgpnk/r98-review/archive` instead of `/tmp`. It is still a fresh
   archive checkout of the committed bytes, file-by-file hash-verified (row 1);
   nothing was read from the author's worktree except its receipts and report.
4. **Float32-derived pins** (`r98b_skewgrid`, `r98b_rksenum`, `r98b_epssweep`
   epsilon chain) are engine-build/CPU pinned. This seat reproduced them exactly
   on the same engine build; a different build is a real signal by design, but
   the pins are not portable evidence.
5. **Upstream provenance** is verified at manifest level in the main clone
   (row 4); the report's caveat that the upstream `runs/` trees are absent from
   the author's *worktree* is accurate, and this seat did not need them — it
   used the author's own 186 receipts plus fresh engine runs.
6. **Scope note (out of r98):** `main` carries later landings; this review
   deliberately did not evaluate them. For the record: measured at `2dcbb6f6`,
   r99 had landed one duplicate case name (485 CASES / 484 unique) and r100
   three (512 / 509); HEAD `9ede7c50` has since deduped the crash sentinel rows
   to 509/509 unique and leaves the r98 block unchanged.

## Method / reproduction

```
# fresh archive checkout of the committed bytes (tmpfs quota forced $HOME)
git -C game-dev-2d-shokunin archive 9d421fb2 corpus/fixtures | tar -x -C /home/vgpnk/r98-review/archive
cd /home/vgpnk/r98-review/archive && python3 corpus/fixtures/run_battery.py --runs /home/vgpnk/r98-review/runs1
# independent re-derivation of the 32 rows (2 reps + mutation arm)
python3 /home/vgpnk/r98-review/rederive.py 2
# receipt re-classification with the landed classifier
python3 /home/vgpnk/r98-review/receipts_check.py
# independent law probes (own bytes)
godot --headless --path /home/vgpnk/r98-review/indep/scratch --script res://review_laws{,2,3}.gd
```

Artifacts: `/home/vgpnk/r98-review/{battery-run1.log,runs1/,rederive/rederive.json,receipts_check.py,summarize.py,indep/}`.
**No file in the lane repo was written or committed by this seat; this report is
its only write.** (The `M corpus/fixtures/__pycache__/run_battery.cpython-314.pyc`
visible in `git status` is not this seat's: it was rewritten at 06:34:12 by the
concurrent integration lane, whose `9ede7c50` commit landed at 06:34:32 together
with `corpus/live/runs/` at 06:35 — every launch in this review ran from the
`/home/vgpnk/r98-review/archive` checkout with `--runs /home/vgpnk/r98-review/runs1`.)
