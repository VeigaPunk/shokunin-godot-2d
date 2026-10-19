# r105 within-lane review — R105FinalReviewer

Snapshot: first two full runs before review corrections. Non-author verification remains orchestrator-owned. Findings were actioned before final landing; see LOG.md round-105 and lesson §Draft corrections.

**Verdict: no false-PASS and no broken invariant found in the landed diff; 5 actionable findings, highest is a control-attribution defect (F1).** All counts/claims in the ticket verified against the raw run records, not the summary.

## Findings by severity

**F1 — MEDIUM. `probe_res_uid_shared` reproduces a *cache-regime flip*, not cross-row leakage; per-row project isolation is not shown to be the load-bearing unit.**
`corpus/fixtures/run_battery.py:3089-3099` (seed) · `:3132-3173` (probe) · cited by `corpus/lessons/round-105.md` M11 / `corpus/QUALITY.md` Q10.
- The shared arm's project is seeded by an editor export **before any shared row runs** (`copytree(res_uid_template, …)` at 3090, then `execute("probe_res_uid_shared_seed", "__godot_export__", …)` at 3095). The isolated arm's projects contain **no `.godot` at all**: `find …/res-uid-isolated -maxdepth 2 -name .godot` → 0 (both runs), template → 0; the shared project has `.godot/uid_cache.bin` (3284 B, sha256 `03c74325…` = `scratch/.godot/uid_cache.bin`).
- Run 1: the **first** shared row (`res_uid_path`) already FAILs — in a project no sibling row has touched; its only difference from its isolated twin is the seed. FAIL set identical forward vs reversed ({path, missing, s01_diag}) ⇒ order-independent.
- The FAIL set is exactly the rows whose pinned/allowlisted text is regime-dependent: `res_uid_s01.gd:259` pins `has_cache=FileAccess.file_exists("res://.godot/uid_cache.bin")`; `res_uid_s01.gd:42,250` document the text flip (`Invalid UID.` ↔ `Unrecognized UID: "uid://<tok>".`) "once uid_cache.bin exists"; allowlists at `run_battery.py:2891-2915` carry the no-cache text. The other 5 shared rows PASS and emit only cache-independent ERROR lines (verified in the isolated receipts).
- Smallest fix: make the arms symmetric (seed both, or neither) and retain each shared row's emitted line (`append_result=False` discards it); reword M11/Q10 to "pins are cache-regime dependent; rows run per-row against a cache-less pre-CASES template; a cache-seeded shared project reproduces the class".

**F2 — MEDIUM/LOW. Duplicate meta row: 622 receipt rows for 600 CASES + 21 unique meta names.**
`run_battery.py:3093-3099` (seed re-enters the `__godot_export__` branch) → unconditional append at `:2626`.
Both runs: 622 rows, 600 CASES names, 21 distinct non-CASES names, `probe_unrelated_error_export_readiness` twice at indices **[0, 40]** (index 0 = seed, 40 = CASES export row). Receipts inherit the doubled count; no gate keys on it today. Fix: append only when `append_result` (or exclude the seed case name).

**F3 — LOW/MEDIUM. `corpus/QUALITY.md` Q18's first clause is unsatisfiable as written** ("CASES entry count equals the receipt's row count"): 600 vs 622 now; 585 vs 606 and 585 vs 613 in the r104-era runs (meta count varies with opt-in probes). Fix: "every CASES row appears exactly once, in CASES order (forward run), plus only named meta-probe rows".

**F4 — LOW. Stale evidence citation, the M9/Q13 class this round lands.** `round-105.md` M15 and `QUALITY.md` Q22 cite `run_battery.py:2817-2819`; those lines *do* hold `'r92_tilemap_physics': ('ERROR: Parameter "found" is null.',)` **at e8990516** but now hold the `geo2d_lattice_polyendpoly` entry (the object is at **2889**, plus a new one at 2922). M28/Q10 rev-qualify ("at e8990516"/"@e8990516"); these two do not. Fix: add the rev qualifier.

**F5 — LOW. `res_uid_s01_createid` cannot falsify its own "path hash" clause.** `corpus/fixtures/res_uid_s01.gd:192-211`. Pinned tokens are same-path repeatability, `text_to_id(id_to_text(a)) == a` (true for every valid id by construction — already pinned by `res_uid_text roundtrip_int63max=true`), non-registration, and `create_id` distinctness. A constant-returning `create_id_for_path` (e.g. always 0, which also satisfies `has_id(0)==false` in a cache-less project and round-trips as `uid://`) passes all tokens. Fix (one line): `_p("cfp_paths_differ=%s" % _b(a != ua))` — CFP_RES/CFP_USER are distinct paths with a shared basename (`res_uid_s01.gd:48-49`), and the removed pins proved the values differ (8476142776992359011 vs 4163091229239537790); add the token…

**F6 — LOW. Q4's check fails on two corpus entries.** `grep -cE '^(source|verified-at|recheck):' corpus/knowledge/*.md` → `2026-10-12-production-checklist.md:0`, `seed.md:0`; the three r105 entries: 3 each. Fix: scope Q4 to entries landed from r105 on (naming the two inherited files) or retrofit the headers.

## Verified clean (ticket axes)

- **C1 isolation**: 29/29 unique `scratch_project`, `xdg_data_home`, `res_uid_root` in both runs; template copied pre-CASES (`:2403`), per-row copytree at `:2560-2562`, `RES_UID_ROOT` honored by s03 (`res_uid_s03.gd:312`) and s04 (`res_uid_s04.gd:110`, scratch tree `res-uid-root/res_uid_s04_persist/uid_s04/persist/proj` present); 73 MB of copies; `--res-uid-order reversed` is an exact reverse (`receipts[1].res_uid_execution_order == reversed(receipts[0])`, static CASES order == run-1 order, non-res_uid rows untouched); no pinned CASES string removed (`git diff -U0 … | grep -cE "^-    \('"` → 0), non-res_uid rows still run in `scratch` (`export_preset_missing` only, as before).
- **Receipts**: both runs 622/622 PASS, 0 FAIL, 29/29 res_uid, 7/7 r105, `signature_in_output` true for all 36 focus rows, focus block contiguous 551-586, `audited_rows=602 flag_count=0`, evasion probe 10 shapes/4 controls unflagged; serial timeline 19:37:06.3 (run 1 written) → 19:37:12.9 (run 2 template) — no overlap.
- **r105 fixtures**: `r105_tile_rid.gd` hard-fails on missed drop/invalid/untracked RID and on `c5!=5,0`/`c21!=21,0`/`c5==c21`; wrongrid is a paired in-session negative with only the allowlisted `Parameter "found" is null.`; `r105_phys_replay.gd` pins invariants + in-process equality + perturb-differs only, digest on `REPLAY` lines, `_teardown` frees between runs, no `leaked` warnings; mutants rc=1 (seat receipts).
- **C4 artifacts**: SOURCES census all 8 contract commands from the frozen `SOURCES-CONTRACT-v1.md` → rows 31 / malformed 0 / A=30 B=1 / mined 10 queued 19 rejected 2 / no dups / no enum-tier violations / no missing `used-by`; 28 M rows, 22 Q rows, 31 gate bullets, all ids with URL + ISO date, each quoted span ≤25 words (max single 16); S015/S031 reject text carries `REJECTED: …; flip: …`. Live re-opens: S031 (4.4 page: `rendering_quadrant_size` present, `physics_quadrant_size` absent), S015 (footer commit `97241ffea`, "a pre-release piece of software"), S002 (4.7 exact-cell Note verbatim), S005 (4.5 "Behavior changes → TileMapLayer" verbatim), S027 (`get_collider_rid` verbatim); S029 quotes resolve at `tilemap_lattice.gd:716,790`.

## Residual risk / gaps

- Re-admitted pins encode the no-cache regime; 3 rows flip in any cache-bearing project (topology proven by the probe) — currently disclosed in-fixture (`res_uid_s01.gd:42,250`) but not in M11/Q10.
- `_rid_read` returns `Vector2i.ZERO` after `quit(1)`, so a partially-failed `chunked` read could still print a stray PASS line; bounded — exit code is 1 and the verdict is exit-code + signature (shape gate skips non-PASS rows).
- `r105_tile_rid_wrongrid` pins `own_coords=0,0` inside a PASS line while riding an allowlisted ERROR; Q22-clean only because `own_has=0` sits adjacent and K1 labels it a refusal receipt.
- K3's entry does not quote the invariant margins (observed max speed / char-x vs the 1200 and 170/600 bounds) that Q17 asks for; digest is exact and ε=1e-4 stated.
- Not run: the battery (13 min ×2, per assignment) and the three `recheck:` commands — Q5 verified statically (flag tokens exist, `PASS <row>:` matches the battery's `f"{verdict} {case}: exit=…"` print shape, pinned rows exist and are green ×2). No LSP server covers Python/GDScript here, so no semantic-navigation claims are made; findings rest on `ast`, raw receipts, and live source re-opens. No writes were made.

[Some lines truncated to 768 chars. Use agent://W2RoundGameDev2d.R105FinalReviewer:raw:20-20 to read line 20 whole]
