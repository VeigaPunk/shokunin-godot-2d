# r105 seat report — R105Reviewer (reviewer)

Verbatim final output of L2 `W2RoundGameDev2d.R105Reviewer` (round 105, batched swarm; transcript `history://W2RoundGameDev2d.R105Reviewer` is session-scoped and not evidence — this file is).

---

**R105 pre-landing audit (read-only; base `e8990516`).** No lane files written. Scratch: `/var/tmp/gd2d-r105/R105Reviewer/`.

## 1. Before-value table (`git show e8990516:…`)

| Item | Expected | Measured | Command / output |
|---|---|---|---|
| res_uid CASES rows (AST) | 21 | **21** | `ast` over `run_battery.py`; `grep -cE "^\s*\('res_uid_"` → 21 |
| Total CASES | 585 | **585** | single `CASES` list at line 18; AST `len(elts)` → 585 |
| Knowledge entries | 2 | **2** | `2026-10-12-production-checklist.md` (289 w), `seed.md` (208 w) |
| Knowledge with `source:/verified-at:/recheck:` | 0 | **0** | `grep -cE '^(source\|verified-at\|recheck):'` → 0 per file |
| `corpus/QUALITY.md` | absent | **absent** | `git ls-tree -r --name-only e8990516 \| grep -i QUALITY` → none |
| `corpus/SOURCES.md` | absent | **absent** | same, for SOURCES → none |
| `grep -c '^## Frontier' corpus/README.md` | 0 | **0** | README 24 lines, 22 `^- ` bullets, "29 inherited" |

Mismatches: none in this list. STATE knowledge words (497) also verified. One **claim** mismatch (not a before-value): LOG:1313, adjudicator:42, and commit 5f924226's subject say "23 res_uid rows". The landed count is 21. The LOG's own "+33 net" equals 21+12, while 23+12 would be 35.

## 2. M1–M14 audit (STATE §4 cites checked at e8990516)

| # | Cited | What the line says | Verdict |
|---|---|---|---|
| M1 | LOG:57 (`## Round 6`) | r6 HOLD: negative scratch inherited positive sidecars | supports |
| M2 | LOG:169 (`### Round 17 HOLD`); open-cause at :172 | r16 zero-product export; "causal diagnosis … remains open" | supports (cite 169–172) |
| M3 | SC:24 (`## Round 64`) | claims 1+5 DISAGREE on pre-fix commit; runner diff uncommitted | supports |
| M4 | SC:64 (`## Round 68`) | ~80× resolution overstated, falsified as written | supports |
| M5 | SC:81 (`## Round 70`, depth) | fabrication window is runner plumbing, not engine-general | supports |
| M6 | SC:158 (`## Round 79`, depth) | P1 dispatch-order snapshot, P2 same-frame visibility, P3 new member | supports (cite 158, not "§r79 row") |
| M7 | LOG:1108 (`## round 88`, lowercase header :1103) | critic F1 BLOCKER: hardcoded ENet ports cross-connect while printing PASS | supports (note: `^## Round` grep misses this header) |
| M8 | SC:280 (`## Round 95`, calibration) | dead `--offy` flag; Y-translation unmeasured | supports |
| M9 | LOG:1196 (ROUND 99, :1194); :1206 (ROUND 100) | "systemic **r98-r100**" | **wrong range** → correct to r98–r100 (not r96–r99) |
| M10 | LOG:1255 (ROUND 101, :1227) | 4 provider-orphaned, 7 design-superseded | supports |
| M11 | LOG:1319 (ROUND 104, :1311) | SEVEN res_uid rows retired; shared scratch uid cache | supports |
| M12 | LOG:1324 (ROUND 104) | re-run precluded by operator reboot, disclosed | supports |
| M13 | LOG:520 (under `## Round 52 parent adjudication`, :518) | "simplifier breached read-only scope" | **wrong round** → r52 (r53 header is at :522) |
| M14 | LOG:60 (`## Round 6` section) | broad `git add` swept 180 scratch files | supports |

## 3. res_uid r104 retirement — recovery

- **Source:** the 7 PASS lines plus createid exist only in `reports/round-104/mutations/r104-W4-res-uid-cases.patch` (saved at `/var/tmp/gd2d-r105/R105Reviewer/w4.patch`). Their first and only appearance is 5f924226. The patch holds 29 rows: 21 landed + 8 retired.
- **Retired PASS lines** (patch line; full text is in the file):
  - path (23): `PASS res_uid path save=OK after_save_shape=path …`
  - collide (25): `PASS res_uid collide two_ids_one_path fwd_ia_kept=true …`
  - cache (27): `PASS res_uid cache same_path=true same_uid=true loaders_same=true …`
  - missing (35): `PASS res_uid missing ghost_has_id=false ghost_path_empty=true …`
  - s01_createid (43): `PASS res_uid_s01 createid cfp_res=8476142776992359011 cfp_res_matches_pinned=true …`
  - s01_collide (45): `PASS res_uid_s01 collide add=res://e1_x1.gd dup_add_refused=true …`
  - s01_diag (47): `PASS res_uid_s01 diag diag_queried_id=103876737118377468 …`
  - s02_deleted (57): `PASS res_uid_s02 deleted removed=true reuse_stale=v3 …`
- **Failure mechanism (code):**
  - One `scratch` project per battery run (`run_battery.py` L2333–2342), so all rows share `.godot/uid_cache.bin`.
  - One `XDG_DATA_HOME = run_dir/xdg-data` per run, not per row (L2526–2533). The per-row isolation claimed at r104 is not implemented.
  - CASES run forward only (L2973); no reverse-order knob exists.
  - The r96_scene_io_uid allowlist (L2832–2838) fires only when the shared cache exists, so the battery encodes cross-row state.
  - Lesson §1 (r104 lesson:46–51): `res://.godot/uid_cache.bin` is the runtime authority; plain `--script` never reads `.uid` text. XDG cannot isolate it. This is why the LOG's "XDG insufficient" holds.
- **Minimal isolation** [inf, not run]: battery-side, before each `res_uid*.gd` process, give a fresh per-row project copy (or unlink `scratch/.godot/uid_cache.bin`) and a per-row `XDG_DATA_HOME`. A fixture-side reset cannot work because the cache loads at engine start.
- **Predictions:** all 29 rows pass forward and reversed. Reversed order needs a new harness knob. Current shared behavior should reproduce Unrecognized-UID in path/collide/s01_diag. If it does not, the shared-cache hypothesis is falsified.
- **What it confirms or falsifies:**
  - Confirms: "XDG insufficient" and lesson §1 (state lives in project dir).
  - Falsifies: the r104 claim that res_uid XDG isolation is done (it was per-run).
  - Tests: s02_deleted's "bimodal" flake. If it still flakes with per-row isolation, it is not uid-cache state.
- **createid:** the literal pins `cfp_res=8476142776992359011` and `cfp_user=4163091229239537790` (res_uid_s01.gd:201–206) match only in W4. In-battery they self-report false (LOG:1321–1322). The repair should drop the literal pins and keep the stable/unregistered/roundtrip tokens. Root cause is [unk].

## 4. Census self-test (contract v1 commands, verbatim, run from a scratch root)

Synthetic table (S031 good; S032 community tagged A; S033 malformed, NF=12). Per-row NF: S031=13, S032=13, S033=12.
```
# rows                 3
# malformed rows       1
# tier histogram       A=2 B=1
# status histogram     queued=3
# duplicate ids        (empty)
# enum/tier inflation  tier-inflation S032
# mined used-by        (empty)
```
Negative control (one good row): rows=1, malformed=0, A=1, queued=1, nothing flagged.

**Blind spot** (single community-A row with NF=12): rows=1, malformed=1, tier histogram A=1, and **no** tier-inflation line. The enum/tier and used-by checks are gated on `NF==13`. The malformed count still fails the gate, so this is a reporting gap, not a bypass.

Peer note from W2RoundProtocol about kotoba blobs is outside this assignment and was not acted on.
