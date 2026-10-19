# r104-connector — sibling scan (read-only) + routed imports + contested scope

uptime: `22:29:29 up 1 day, 22:29,  1 user,  load average: 3.06, 1.89, 1.77` (load low)
date: Sun Oct 18 10:29:29 PM -03 2026
cwd: `/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin` (branch `main`, HEAD `eff29d1d`)
scratch: `/var/tmp/r104-connector/` (never `/tmp` — 80% full, EDQUOT class)

## Plan (5 lines)
1. Sibling-lane scan (read-only): locate game-dev-3d repo/worktree; detect parallel session; record what is observable without touching.
2. Routed imports: collect r101/r102/r103 hand-offs addressed to *other* seats that never landed — verify each against current corpus state.
3. Contested scope: enumerate files/claims where two seats' declared ownership overlaps or where a claim was routed away from this lane.
4. Disposition: per routed item, evidence-backed {landed | still-open | superseded | out-of-lane} with exact command bytes.
5. Hard rules honored: no `run_battery.py` execution, no shared-file edits, no commits, no sibling-lane writes.

Status: **COMPLETE** (scan + read-only measurement). Findings §1–§7.

---

## 1. Sibling lane scan — `game-dev-3d-shokunin` is QUIESCENT

### 1.1 Process check → no lane process
`ps -eo pid,etimes,args | grep -F 'game-dev-3d' | grep -v grep` at 22:29:40 → **rc=1, empty output** (only this seat's own grep matched itself). Live agent processes on the host at the same sample: `devin-shim/shim.py` (pid 1574, etimes 167378), four `kimi` sessions (878959/880650/2299991/2342280), `opencode serve` (1277097). **No `godot`, no `run_battery.py`, no lane-owned shell.** Load low (3.06).

### 1.2 Disk state
- `git log --oneline -3` → HEAD `3ea02ff` "r106 report-last: verdict (improved, bounded, interrupted round)…"; `git status --short` → clean (no output).
- `git worktree list` → **only the main worktree** (`/home/vgpnk/Projects/shokunin/game-dev-3d-shokunin 3ea02ff [main]`). No stray 3D worktrees.
- `reports/round-106/` holds the close-out set (mtimes 22:24): `final-verdict-prep.md`, `final-integrity.md`, `next-iteration-carry.md`, `operator-package-carry.md`, `pc-carry.md`, `gate/`, `consistency/`. `ls -d reports/round-107` → **no such directory**.

### 1.3 LOG close section (read-only tail)
3D `LOG.md` final section = `ROUND 106 (2026-10-18): corpus citation sweep + census refresh + consistency audit — INTERRUPTED round, closed as ADMIT-with-findings on the landed and L1-verified subset.` Provider history: xai-oauth/grok-4.7-fast died at 47/128 (credits exhausted), cursor/grok-4.7-xhigh-fast landed work then hit the Cursor Pro rate limit. `ROUTED (r107+)`: sweep completion, consistency chunk audits, jolt ruling, cursor Pro rate-limit recovery (**OPERATOR-owned**), hyper-lane directive recorded for r110. `L0: Epic link / docker image / lutris / P-C ruling — unchanged.`

**Consequence:** the sibling is between rounds with no live process. Any timing-sensitive comparison against 3D artifacts is safe *at this instant* — but see §6 CS-1: the sibling's own carry list is ready to start r107, so quiescence is a window, not a state.

### 1.4 Fleet MANIFEST census (read-only)
`MANIFEST.json` has 244 `rounds[]` entries. Last entry = round 103, `type: closure`, `lane_rounds: {"game-dev-2d": 103}`, `admitted: true`, `closed_at: 2026-10-19T00:59:00-03:00`, `verdicts: {depth: improved, coverage: improved, calibration: improved}`.

- **`game-dev-3d` has ZERO `lane_rounds` entries anywhere in 244 rounds** (`sum(1 for r in rs if isinstance(r.get('lane_rounds'),dict) and 'game-dev-3d' in r['lane_rounds'])` → `0`).
- Total rounds whose JSON mentions `game-dev-3d` → **4** (the r70–r73 `type: train` entries, 2026-10-13/14).
- 2D's r103 note carries verbatim: *"3D side-round still deferred (3D at r106, parallel session) - must land before 2D r105."*
- Rounds 8 and 9 (`closure`, `closed_at 21:35` / `23:20`) have `lane_rounds: None` — unrelated lanes, recorded only to show the ledger is live during this window.

---

## 2. C2a — the PASS-line census: landed form vs every proposed widening

### 2.1 The landed rule (read verbatim)
`corpus/fixtures/run_battery.py:1904`:

```python
    pass_lines = [line for line in output if line.startswith("PASS ")]
```

`sha256sum corpus/fixtures/run_battery.py` → `2af2bc841ccb416e5fb0e1bbaadc08627e2d4768a8822f6956e867d905a3d0fe`, 5783 lines, last commit `afe5b636` (r103). The module is import-safe: `import` block is all stdlib, `HERE`/`CASES` are pure literals, and the program body is under `if __name__ == "__main__":` at line 5782 — so the predicates can be imported without running the battery. **Verified by import** (`importlib` load succeeded; `len(rb.CASES) == 552`).

### 2.2 Four different widening rules are on disk from four seats

| rule | form | seat/artifact |
|---|---|---|
| **A (landed)** | `^PASS ` | `run_battery.py:1904` |
| **B** | `^PASS(?:\s\|$)` | `reports/round-104/mutations/r104-G0-passline-census.py` RULE B |
| **C** | `^\s*PASS(?:\s\|$)` | same file, RULE C (the G0 headline) |
| **D** | `^PASS` | `reports/round-104/mutations/r104-X2-pass_census.py` |
| **E** | `^\s*PASS(?:\b\|$\|[:=])` | r103-G0 *proposal*, `reports/round-103/mutations/r103-G0-receipt_gate.py:31` |

**This is the contested-scope crux**: four seats proposed four different rules and nothing on disk reconciles them.

### 2.3 Measured on real bytes — all five agree exactly; only D has a false-positive class

Script: `reports/round-104/mutations/r104-connector-passprefix-census.py` (durable). Command:

```
python3 reports/round-104/mutations/r104-connector-passprefix-census.py
```

Over 8 stored `corpus/live/runs/*/verdicts.json`, **39,806 output lines**:

```
rule                              matches  nonlanded
A landed  ^PASS\s                    4548          0
B col0    ^PASS(\s|$)                4548          0
C G0      ^\s*PASS(\s|$)             4548          0
D X2      ^PASS                      4548          0
E mine    ^\s*PASS(\b|$|[:=])        4548          0
```

**Zero divergence between A and any candidate.** Independently corroborated by the G0 seat's own script (`RUNS=8 ROWS=4352 LINES=39806`, `DELTA B_minus_A = 0`, `DELTA C_minus_B = 0`, `FPCLASS D = 0`).

Syntactic probe (synthetic, labelled — not real bytes):

| line | A | B | C | D | E |
|---|---|---|---|---|---|
| `PASSWORD=secret` | F | F | F | **T** | F |
| `PASSING=true` | F | F | F | **T** | F |
| `PASSED_forged=1` | F | F | F | **T** | F |
| `PASS-FAIL` | F | F | F | **T** | **T** |
| `PASS=1` | F | F | F | **T** | **T** |
| `PASS\tx` | F | T | T | T | T |
| `PASS` | F | T | T | T | T |

**Finding (observation):** rule **D is unsound** — it swallows `PASSWORD`/`PASSING`/`PASSED`, a real false-positive class. Rule **B** (`^PASS(?:\s|$)`) is the minimal tightening that closes the tab-after-PASS hole with no false-positive class and no leading-whitespace tolerance. Rule **C** additionally tolerates leading whitespace (invisible to B), which no stored receipt contains. Rule **E** additionally admits `PASS-`, which no stored receipt contains. On today's bytes B, C and E are **indistinguishable** (all 4548, all nonlanded=0) — the choice is purely about which *future* shape you want caught.

### 2.4 The r103 claim "tab-PASS is grammar-invisible" — reproduced exactly

`receipt_shape_flag` imported from the real module, replayed against the r103 mut05 catalog (`reports/round-103/mutations/mut05_gate_evasion.py` shapes, reconstructed verbatim from that file) on base run `corpus/live/runs/20261018T213443471189Z`:

```
shape                       before  after  why_after
CTRL_simple                      0      0  []
CTRL_seq                         0      0  []
CTRL_launch                      0      0  []
CTRL_prod                        0      0  []
s1a_banner_forged_seq            0      0  []
s2a_diag_other_simple            0      0  []
s2b_diag_forged_launch           0      0  []
s3a_flood5_simple                1      1  ['unaccounted_pass_lines']
s3b_flood1_seq                   1      1  ['pass_line_grammar_mismatch']
s4a_tab_lead_simple              0      1  ['unaccounted_pass_lines']
s4b_trail_space_simple           2      2  ['unaccounted_pass_lines', 'anchor_line_multiplicity']
s4c_trail_nbsp_simple            1      1  ['unaccounted_pass_lines']
s4d_tab_after_pass_simple        0      1  ['unaccounted_pass_lines']
s4e_lead_space                   0      1  ['unaccounted_pass_lines']
s4f_PASS_equals                  0      1  ['unaccounted_pass_lines']
s4g_PASS_bare                    0      1  ['unaccounted_pass_lines']
```

"before" = landed gate; "after" = the same module with **only line 1904** replaced by a `^\s*PASS(?:\b|$|[:=])` census (`/var/tmp/r104-connector/run_battery_mutant.py`).

- **r103's "4 of 10 flag" reproduces exactly** (`s3a`, `s3b`, `s4b`, `s4c`).
- The widening flips **five** shapes from 0 → 1 flag: `s4a` (leading tab), `s4d` (TAB after PASS), plus three shapes **beyond** r103's catalog — `s4e` (leading spaces), `s4f` (`PASS=`), `s4g` (bare `PASS`) — each of which the landed census also misses. All four green controls stay 0.
- **Boundary honesty (from r103, confirmed here):** the six unflagged r103 shapes do **not** become flagged by the census change — they are the banner/diag classes, which live at a different layer. The census tightening closes the whitespace/separator family only; §3 proves the banner/diag/tab family is verdict-layer-harmless.

### 2.5 False-positive analysis on real receipts (the required half)

Naive "widened flags more" is meaningless without a control. Baseline (landed gate) vs mutant, same rows, 8 receipts:

| run | auditable rows | baseline flags | mutant flags | delta |
|---|---|---|---|---|
| 20261018T200239625248Z | 530 | 5 | 5 | 0 |
| 20261018T202131127599Z | 530 | 1 | 1 | 0 |
| 20261018T212500022987Z | 538 | 0 | 0 | 0 |
| 20261018T213443471189Z | 538 | 0 | 0 | 0 |
| 20261019T001435805887Z | 554 | 5 | 5 | 0 |
| 20261019T003019776183Z | 554 | 0 | 0 | 0 |
| 20261019T004115354212Z | 554 | 0 | 0 | 0 |
| 20261019T005558434174Z | 554 | 0 | 0 | 0 |
| **TOTAL** | | **11** | **11** | **0** |

**Delta is 0 in every receipt.** The non-zero baselines are *not* census-related and must not be read as widening damage:
- run 1 (`…200239625248Z`, 10 flags) and run 2 (`…202131127599Z`, 2 flags) — `r101_ytrans_*` `pass_line_unanchored` + `anchor_line_multiplicity`, the **pre-fold legacy rows** the r103 record already names.
- `20261019T001435805887Z` (15 flags) — `export_div_s01_*` `foreign_in_diag_window`, an r104-era seat's live finding; the **other three** r104-era receipts flag 0.

Receipt mtimes: `20261019T001435805887Z` 21:25:38, `…T003019776183Z` 21:40:24, `…T004115354212Z` 21:53:07, `…T005558434174Z` 22:06:47 — the last three postdate r103's close (00:59-03). **The three most recent receipts in the lane flag 0 under both the landed gate and the widening.**

**C2a conclusion [observation]:** the tab-PASS tightening is **provably false-positive-free on all 4,548 real PASS lines / 39,806 real output lines**, and closes 5 evasion shapes. r103's `PASS\t` routing is confirmed; the r103 *proposal's* regex (rule E) is a strict superset of the minimum needed, and rule D as implemented by the X2 seat is **unsound** and should not land.

---

## 3. C2b — verdict-layer harmlessness proof for the tab-PASS shape

`classify_process` is nested inside `main()` (line 2093, 4-space indent), so it is not module-level. Extracted **faithfully** via `ast` (`ast.unparse` of the real `FunctionDef` node, rebound with only `re`), then driven with the real `input_route` row from `20261018T213443471189Z` (`actual_exit=0`, `signature='PASS route=parse_input_event-to-Node._input'`, 3 output lines).

```
base (no injection)              -> classify=True
base + tab-PASS                  -> classify=True
base + PASS<tab>                 -> classify=True
base + lead-space                -> classify=True
base + PASS=                     -> classify=True
base + bare PASS                 -> classify=True
base + space-PASS (forged)       -> classify=True

control: stripped-signature row            -> classify=False
control: stripped + tab-PASS               -> classify=False
control: stripped + space-PASS             -> classify=False
control: stripped + unrelated ERROR        -> classify=False
```

**Proof (observation):** `classify_process`'s predicate is `signature in output and not unrelated_errors` — it never counts PASS lines. No injected PASS-shaped line, in **any** whitespace/separator form, changes its answer on either a passing or a failing row. The six unflagged r103 shapes are therefore **verdict-layer-harmless by construction, not by luck**: the tab-PASS shape cannot alter a verdict, only the *receipt's shape*, which is exactly what the gate audits.

The same extraction was then driven with the **banner/diag** shapes, so the claim covers all four injected-line families (not just the PASS-shaped ones):

```
input_route + s1a forged banner          -> classify=True
input_route stripped + s1a forged banner -> classify=False
input_route + s2a foreign DIAG           -> classify=True
input_route stripped + s2a foreign DIAG  -> classify=False
input_route + s4a lead-tab               -> classify=True
input_route stripped + s4a lead-tab      -> classify=False
input_route + s4d PASS-tab               -> classify=True
input_route stripped + s4d PASS-tab      -> classify=False
```

Every injected line leaves the verdict at its no-injection value in **both** directions (True stays True on a passing row, False stays False once the signature is stripped) — so no injected shape can *create* a PASS, which is the harm that would matter.

**Honest scope of this proof (unknowns):** it is a **single-row, single-`classify_process`-variant** proof against one base receipt, not an exhaustive one. It does not cover `classify_streams` (which rejects on unexpected *stderr* lines), `classify_audio_process`, or the export branch — a `DIAG`/banner line arriving on **stderr** could still reject there, and that is the residual for the C2b seat that owns the banner/diag classes. It also does not claim the shapes are *desirable*: they are unflagged at the shape layer, which is precisely why the census tightening in §2 matters.

---

## 4. Contested scope

- **CS-1 (schedule gate, now live).** The contract says the 3D re-vendoring side-round "runs once **before 2D r105**" (`../../.scratch/goal-20261018-game-dev-2d-training.md`, ROUND SCHEDULE + DONE WHEN), and both r102 and r103 LOG records carry it as ROUTED. **r104 is the last 2D round in that window.** At this sample the sibling is quiescent (§1.1–1.3) and r106 is closed, so **the blocking condition (sibling busy) is currently false** — the window is schedulable now. The 3D lane's own carry list is loaded for r107, so this is a closing window, not an open one. **Orchestrator decision, not this seat's.**
- **CS-2 (registry lag, non-accusatory).** `game-dev-3d` still has zero `lane_rounds` closures across 244 fleet rounds while its local LOG is at r106. Persists after r106 artifacts completed.
- **CS-3 (four unreconciled widening rules).** §2.2 — G0's B/C, X2's D, and r103's E are all on disk with no reconciliation. **D is unsound** (§2.3). Recommend the orchestrator land **B** (minimal, no false-positive class) or **C** (B + leading-whitespace tolerance, indistinguishable on today's bytes), never D.
- **CS-4 (implementation void for C2a).** The widening exists only as *proposals*: `grep -n 'min-rows' corpus/fixtures/run_battery.py` → **1 hit, and it is inside a comment** (`:4421`), so `--min-rows N` is still **not implemented**; and line 1904 is still `startswith("PASS ")` in the tree. `r103_export_div_count_floor` landed (line 4425) but its `>= 1` floor is **unfrozen** — with `export_div_s01..s05` all registered (lines 1717–1749) the exact-count freeze is now possible and still owed.
- **CS-5 (worktree hygiene).** `git worktree list` for this repo shows 5 entries: main, three **locked** r98/r99/r100 worktrees under `…-wt-r98/-wt-r99/-wt-r100`, and two live r104 seats' worktrees (`/var/tmp/r104-ver3/wt`, `/var/tmp/r104-ver5/repo`, both detached at `eff29d1d`). The r98–r100 ones are long-standing (r98–r100 era) — flagged, not touched.
- **CS-6 (scratch debris).** `/var/tmp/r103c-*` → **56 directories still present** from round 103; `/var/tmp/r103-*` → 0. Per hard rule 5 these are not this seat's to remove, but the 56-dir residue is worth an orchestrator sweep.
- **CS-7 (fixture-write race).** `corpus/fixtures/res_uid_w07.gd` (9415 B, 22:30) landed while E0/E1/E2/E3/E4 seats were still reconnoitering and `r104-mut2.md:19` records that **no** `res_uid*.gd` existed at its open. Multiple seats are now writing into `corpus/fixtures/` concurrently — the r103 concurrent-writer law (RI-4) applies in-lane: a `seeds_unchanged` FAIL mid-run is a possible writer, not a broken row.
- **CS-8 (host-shared hazards).** `/dev/input/js0` **and** `js1` both present; never pin device-census tokens (r85/r101/r102 F3 law). `/tmp` is a 16 G tmpfs at **80% used (3.1 G avail)** — the EDQUOT class is live; scratch stayed under `/var/tmp/r104-connector/`.

---

## 5. Routed-import status table (r101/r102/r103 hand-offs, measured at HEAD `eff29d1d`)

| # | routed item (source) | status measured now | evidence |
|---|---|---|---|
| 1 | **tab-PASS grammar tightening** (r103 LOG `ROUTED (r104+)`) | **still open, but fully measured** — no code change in tree | §2; `run_battery.py:1904` unchanged; `sha256 2af2bc84…` |
| 2 | r102 pre/post-span foreign-line residual (mut09 span attack) | **landed in r103** as the receipt-shape META gate | `receipt_shape_flag` + `RECEIPT_MULTI_PASS_GRAMMAR` at `:1782`, `:1877` |
| 3 | `--min-rows N` freeze (r103 w5 patch comment; r103-C4:67, E0-spec:170, E1:149, mut7:148) | **still open** — flag not implemented; count floor landed unfrozen | `grep -c 'min.rows'` → 1, comment only, at `:4421`; floor at `:4425` |
| 4 | VER-13 hygiene (derived-evidence rows) | **partially landed** — F6 account in place, hygiene follow-up owed | `RECEIPT_SHAPE_DERIVED_EVIDENCE = {"export_readiness","export_preset_missing"}` at `:1779` |
| 5 | orphaned companion fixtures (4 provider-orphaned + 7 design-superseded, `reports/round-101/mutations/orphaned-fixtures/`, 12 files incl. README) | **still open** — dir intact, still unregistered; r104 S1/S2/scout own the disposition | `ls` → 12 entries; `ls corpus/fixtures/export_prod*` → only `export_prod.gd` |
| 6 | QUALITY.md census | **answered in r103, decision unmade** — fleet convention is `<lane>/corpus/QUALITY.md` | r103-scout S7:6; r104-scout carries it |
| 7 | S4 lessons stale-citation family (preserve-vs-rewrite) | **operator-owned, still open** | r103-scr4:314 |
| 8 | 3D side-round before 2D r105 | **still open, window = this round** | §1, CS-1 |
| 9 | mut05 full gate-replay wiring (catalog vs verdicts) | **in progress this round** — `reports/round-104/mutations/mut05.py` landed (25546 B, 22:31) | `ls -la reports/round-104/mutations/` |
| 10 | w5 `export_div` splice | **landed** | rows at `run_battery.py:1717–1749`; gates at `:4413`, `:4425` |

---

## 6. Observation / inference / unknown

- **Observed:** every uptime, `ps` row, `git` output, MANIFEST count, file size/mtime/sha, regex match count and classifier return value quoted above. The two independent census scripts' agreement (`4548/0` from this seat; `DELTA 0/0/0` from the G0 seat). `len(rb.CASES) == 552`, `554 auditable rows` matching r103's stated audit count.
- **Inference (labelled):** the recommendation that rule **B** or **C** (not D) should land; that the r104-era receipts' 0-flag status means the gate is currently clean on live output; that the sibling's quiescence is a window rather than a state (its r107 carry list is already written).
- **Unknown:** whether any r104 seat will land the census change in `run_battery.py` (all four rules are proposals only); the r104 round's final verdict and admission; whether the 3D side-round will be dispatched inside the remaining window; the content of the 3D r106 close-out shards (not read — lane content out of scope beyond LOG/manifest/status).

## 7. Files touched

- `reports/round-104/r104-connector.md` (this shard) — the only lane file written by this seat.
- `reports/round-104/mutations/r104-connector-passprefix-census.py` (6259 B) — durable measurement script, the provenance for §2.
- Scratch: `/var/tmp/r104-connector/` only (`passprefix-census.txt`, `run_battery_mutant.py`, and the script's own mutant copy). No worktrees created. `run_battery.py` **never executed as a program** — imported only for its pure predicates. No shared files touched; **no commit**.
