# r104-planner — lattice map for C1/C2/C3 (planner seat, KEY=PLANNER)

Date: 2026-10-18. Repo `/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin`, branch `main`,
HEAD `eff29d1d` (round-103 record). Sibling lane `game-dev-3d-shokunin` — hands off entirely
(read-only HEAD check only: `3ea02ff`, committed 22:24:32, i.e. its r106 closed ~5 min before
this seat opened). No git commit by this seat. No device-census token pinned.

Host (shard header, hard rule): `uptime` at open = `22:29:29 up 1 day, 22:29, 1 user, load
average: 3.06, 1.89, 1.77`; at close = `22:37:14 up 1 day, 22:37, 1 user, load average:
13.60, 9.75, 5.42` (the rise is the r104 swarm's own Godot runs, not a foreign lane). Scratch
`/var/tmp/r104-planner/` (never `/tmp` — EDQUOT).

Plan (5 lines):
1. Read SCORECARD tail + LOG tail + `r103-adjudicator.md` + the contract Amendments → claims, routed items, laws.
2. Measure HEAD state (CASES count, gate code, stored runs) and the exact surfaces C1/C2/C3 touch.
3. C2: measure the tab-PASS tightening against the landed gate — discrimination × false-positive matrix over all stored runs.
4. C1/C3: registration order, probe/companion lattice, file-collision matrix for the orchestrator.
5. Saturation bookkeeping; label observation/inference/unknown. (§6b is the freshness delta; the cap was exceeded by 35 lines and trimmed to 435 — the four measurement tables that justify C2 are kept whole, narrative was cut.)

## 0. Contract facts that bind r104 (verbatim-sourced)

- [obs] Amended schedule: p4 = `hyper/deepseek-v4.1-flash` 32–64 (fallback
  `devin/deepseek-v4-1-flash-high`); p6 skipped; cycle = 12 positions; total 2D rounds = 36
  (101–136). 3D side-round: once, **before 2D r105**, `devin/deepseek-v4-1-flash-high`, 32–64.
  (`.scratch/goal-20261018-game-dev-2d-training.md`, "Amendments" §1–3.)
- [obs] r104 runs the **p4 fallback** per operator directive (hyper attempts interrupted).
- [obs] `SCORECARD.md` declares saturation + stagnation **N = 5**, and r101–r103 each returned
  `improved` on all three axes → **stagnation count = 0** entering r104. The declaration is
  explicit that it is a conservative fleet default, not calibrated from history.
- [obs] Fleet `MANIFEST.json` `rounds[]` holds only 4 `game-dev-2d` entries (rounds 61–64);
  r101–r103 are absent from the ledger. This is a DONE-WHEN gap ("each closed in the fleet
  MANIFEST.json rounds[] ledger") that no r104 seat owns — **routed to the orchestrator**
  (it is a fleet file, outside the 2D write boundary's per-round report dir).

## 1. HEAD state measured by this seat

| item | value | command |
|---|---|---|
| `run_battery.py` sha256 | `2af2bc841ccb416e5fb0e1bbaadc08627e2d4768a8822f6956e867d905a3d0fe` | `sha256sum corpus/fixtures/run_battery.py` |
| CASES rows | **552** unique, arity set `{5}`, `CASES` list at `run_battery.py:18-1759` | AST `literal_eval` of the `CASES` assignment |
| distinct CASES scripts | 79 (5 are harness pseudo-scripts: `__godot_export__`, `__godot_export_missing__`, `__save_process_missing__`, `__save_process_reader__`, `__save_process_writer__`) | AST |
| `receipt_shape_flag` | `run_battery.py:1877`; census line `1904`; `receipt_shape_audit` at `1998` | grep |
| `RECEIPT_MULTI_PASS_GRAMMAR` | `1782`, 22 case keys | grep |
| `CASES_SIG_BY_CASE` | `1775` | grep |
| `expected_errors` dict | `run_battery.py:2339-2605`, 84 keys, enclosed by `if passed is None:` at `2338` | AST |
| `cases_integrity` gate | `run_battery.py:4442`; prefix tuple already contains `export_div_` | grep |
| `r103_export_div_count_floor` | `run_battery.py:4425-4428` | grep |
| registered family counts | `export_div_s01..s05` = 5/2/3/3/3 (16); `export_launch_` = 8; `export_prod_` = 12; `r101_seqfull_` = 2; `r101_ytrans_` = 6 | AST |
| newest stored runs | `20261019T004115354212Z` and `20261019T005558434174Z`: 571 rows, **571 PASS / 0 FAIL**, `probe_receipt_shape_gate` PASS `audited=554 flags=0` both | `json.load(verdicts.json)` |
| r103 closure re-verified | `B-A` between the r103 run and the newest = exactly the 16 `export_div_*` rows + `probe_receipt_shape_gate` | set difference over `results` |
| `--min-rows` | **does not exist** in HEAD (`grep -n 'min-rows\|min_rows'` → only a comment at `4421`) — the floor is still `>= 1`, the r103 freeze is still owed | grep |
| fixture dir | at 22:35: 119 files on disk / 118 tracked, 1 untracked (`res_uid_w07.gd`) — by 22:36 five more `res_uid*` fixtures landed (§6b) | `git status --porcelain corpus/fixtures` |
| worktrees | 3 locked legacy (`wt-r98/r99/r100`) + `/var/tmp/r104-ver5/repo` (detached, r104 seat) | `git worktree list` |

`run_battery.py` was **never executed** by this seat (hard rule 1). All gate evaluation below is
by importing the module (its `main()` is `__name__`-guarded) or by `exec`ing an AST-extracted
function source.

## 2. C1 (coverage) — ResourceLoader / UID-cache lattice

### 2.1 Lattice map (claim → sub-item → owner → state; §6b supersedes the fixture rows)

| # | sub-item | owner | state |
|---|---|---|---|
| C1-a..e | `res_uid.gd` + `res_uid_s01..s04.gd` | E0 / E1–E4 | **LANDED (untracked)** during this run — see §6b for bytes/shas/arms |
| C1-f | `res_uid_w07.gd` (independent repro) | W7 | **LANDED (untracked)** 9469 B |
| C1-g | CASES rows for the family | orchestrator | **MISS** — 0 `res_uid` occurrences in `run_battery.py`; W10's splice planner carries a 4-row placeholder set (`res_uid_s01_census`, `res_uid_s02_cache_identity`, `res_uid_s03_remap`, `res_uid_s04_persist`) marked "reconstructed from sibling shard specs" |
| C1-h | `cases_integrity` prefix + floor gate | W4 | **PLAN** — `r104-W4.md` |
| C1-i | adversary mut01 (cache-identity forgery) / mut02 (UID round-trip spoof) | M1 / M2 | **PLAN** (`mut02.py` landed 14112 B; `mut01.py` absent) |
| C1-j | independent verifiers | ver1–ver4 / w7 / ver10 | **PLAN** |
| C1-k | `expected_errors` needs | E0-spec | **SPEC'D** — every arm that triggers `Invalid UID.` / `Unrecognized UID: "…".` / `Condition "!unique_ids.has(p_id)" is true.` needs a per-case entry (stderr is merged into `output`, and `classify_process` rejects any un-allowlisted `ERROR:` line) |

### 2.2 Mechanism notes measured on scratch (`/var/tmp/r104-planner/uid2/`) — for the executors

These are [obs] from this seat's own headless runs; they are offered to E0/E1–E4 as ground truth
so their pins rest on measured behaviour. **They are not registered rows** (this seat owns no
fixture) and every literal below still needs a fresh pin from the landed fixture.

1. [obs] `ResourceUID` exists and exposes exactly 12 methods: `id_to_text`, `text_to_id`,
   `create_id`, `create_id_for_path`, `has_id`, `add_id`, `set_id`, `get_id_path`, `remove_id`,
   `uid_to_path`, `path_to_uid`, `ensure_path`. There is **no** `id_to_path`.
2. [obs] `.uid` sidecar text is `uid://<13 chars>` + a trailing `\n` (20 bytes for
   `uid://bf3qfun33wlt8`); `text_to_id` on the stripped text round-trips to the same text.
3. [obs] `.godot/uid_cache.bin` layout (55 B for 2 scripts): magic `02 00 00 00`, then per entry
   `u32 id_le` + `u32 path_len_le` + path bytes. Cross-process persistence works without any
   `--import` re-run: a second process resolved `res://thing.gd` by the sidecar UID.
4. [obs] `ResourceUID.get_id_path(INVALID_ID)` → `""` + `ERROR: Invalid UID.` on stderr;
   `get_id_path(<unknown id>)` → `""` + `ERROR: Unrecognized UID: "uid://…".`. Both are the
   `expected_errors` hazard named in C1-k.
5. [obs] `ResourceUID.path_to_uid("res://res_a.tres")` returned **`res://res_a.tres`** (the path
   itself) for a `.tres` that has no UID sidecar, and `uid_to_path` of that echo returned `""`
   (+ `ERROR: Invalid UID.`). The `path` arm's "unknown path echoes path" intent (E0-spec) is
   therefore confirmed for `.tres`, but the *return-value* contract is path-echo, not `""` —
   pin the echo, not an emptiness claim.
6. [obs] Cache identity: repeated `load()` → same object (`==` true); `CACHE_MODE_IGNORE` →
   different object; `CACHE_MODE_REPLACE` → same object as the default load. Same result for
   `.gd` and `.tres`. Enum values: `IGNORE=0 REUSE=1 REPLACE=2 IGNORE_DEEP=3 REPLACE_DEEP=4`.
7. [obs] `res_uid.gd`/`res_uid_s0*.gd` must survive the battery's scratch staging: the stage
   copy **excludes dot-prefixed entries** (`run_battery.py:2044-2045` skips `item.name.startswith(".")`),
   so no `.godot/uid_cache.bin` is inherited and the `persist` arm must mint its own cache
   (a nested child process, the `__godot_export__` precedent).

### 2.3 CASES row-name + registration order (recommendation — superseded by the landed receipts)

The fixtures' own arms are now known (§6b: E0 8, s01 6, s02 10, s03 5, s04 3). Names must be
taken from each fixture's own PASS line, never invented; the W10 4-row placeholder set is not
usable. Registration block: insert a **contiguous family block after the r103 `export_div_s05_ctb`
row (`run_battery.py:1750`) and before the `crash_*`/descendant tail (`1751`)** — the r63/r101
insertion convention — ordered so each fixture's arms are adjacent.

Constraints on the block (all [obs] from HEAD code):
- Row names **must** carry the `res_uid_` prefix, which must be added to the `cases_integrity`
  tuple at `run_battery.py:4443-4448`, or the family is invisible to the integrity gate.
- **One PASS line per process.** Every fixture now ships exactly one `print("PASS …")` site, so
  each arm is one row; a multi-arm process would need a `RECEIPT_MULTI_PASS_GRAMMAR` entry in the
  same splice (floor-not-ceiling).
- Any arm that triggers an engine `ERROR:` line needs its exact string in the `expected_errors`
  dict (`2339`), keyed by the row name — the C1-k hazard, and E1's fixture deliberately keeps one
  arm off the `uid_cache.bin`-dependent diagnostic for exactly this reason.
- The count floor should be frozen to the **AST count after the splice**; today it is `>= 1` and
  `--min-rows N` does not exist.

## 3. C2 (depth) — gate boundary

### 3.1 C2(a) tab-PASS tightening — measured discrimination × false-positive matrix

Method: for each candidate predicate, the `pass_lines = [...]` census line at
`run_battery.py:1904` was textually replaced in a **scratch copy** of HEAD
(`/var/tmp/r104-planner/tighten/`), the module imported, and `receipt_shape_flag` /
`receipt_shape_audit` evaluated over (i) the r103 `mut05` 10-shape catalog rebuilt from its own
base run `corpus/live/runs/20261018T213443471189Z/verdicts.json` (sha256
`65e7fae0ca987563b40601439b4afe5388196c18ffe38dd91a8fc1c09a6a5f68`, 554 rows) and (ii) **all 8
stored runs** on disk. [obs]

The "FP counts" column is **this seat's own offline `receipt_shape_audit` recomputation** over the
stored rows (identical under P0 and every widening), *not* the `flag_count` field the runs
recorded: the two oldest runs predate the gate (no `probe_receipt_shape_gate` row at all), and for
`20261019T001435805887Z` the stored field says `flag_count=23` (reasons
`fail_closed_missing_signature` + `foreign_in_diag_window`) where the offline audit says 15 —
the difference is the F4 pin-timing race that r103 fixed *after* that run was written. The
predicate-invariance claim below rests on the offline recomputation, which is the only form
comparable across all 8 runs.

| predicate | shapes flagged | green controls flagged | FP counts over the 8 stored runs (oldest→newest) |
|---|---|---|---|
| P0 landed `line.startswith("PASS ")` | **4/10** | 0/4 | 12, 10, 0, 0, 15, 0, 0, 0 |
| P1 `line.lstrip().startswith("PASS")` | **6/10** | 0/4 | 12, 10, 0, 0, 15, 0, 0, 0 |
| P2 `re.match(r"^[ \t]*PASS(?![A-Za-z0-9_-])", line)` | **6/10** | 0/4 | 12, 10, 0, 0, 15, 0, 0, 0 |
| P3 `re.match(r"^PASS(?:\b\|$)", line)` | **5/10** | 0/4 | 12, 10, 0, 0, 15, 0, 0, 0 |

Per-shape under P1/P2 (the shapes that move are exactly the two tab shapes):

| shape | P0 | P1 | P2 | P3 |
|---|---|---|---|---|
| `s1a_banner_forged_seq` | – | – | – | – |
| `s1b_banner_dup_launch` | – | – | – | – |
| `s2a_diag_other_family_simple` | – | – | – | – |
| `s2b_diag_forged_launch` | – | – | – | – |
| `s3a_flood5_simple` | `unaccounted_pass_lines` | same | same | same |
| `s3b_flood1_seq` | `pass_line_grammar_mismatch` | same | same | same |
| `s4a_tab_lead_simple` | – | **`unaccounted_pass_lines`** | **`unaccounted_pass_lines`** | – |
| `s4b_trail_space_simple` | `unaccounted_pass_lines` + `anchor_line_multiplicity` | same | same | same |
| `s4c_trail_nbsp_simple` | `unaccounted_pass_lines` | same | same | same |
| `s4d_tab_after_pass_simple` | – | **`unaccounted_pass_lines`** | **`unaccounted_pass_lines`** | **`unaccounted_pass_lines`** |

**False-positive analysis (the required deliverable of C2a).** [obs]
- The three nonzero FP counts are **pre-existing and predicate-invariant**: they belong to the
  historical runs `20261018T200239625248Z` (12), `20261018T202131127599Z` (10) and
  `20261019T001435805887Z` (15) — the first two are the r101 runs whose redness is already
  recorded (they carry no gate row at all), the third is the r103 run 1 whose 15
  `foreign_in_diag_window` flags are the in-flight export_div fixtures' own output. Tightening
  changes **none** of these counts.
- Over the **five** certified-green runs (`20261018T212500022987Z`, `20261018T213443471189Z`,
  `20261019T003019776183Z`, `20261019T004115354212Z`, `20261019T005558434174Z`) the widened
  census adds **0 flags**.
- Why the FP risk is structurally near-zero: a scan of **every output line of every stored run**
  (39806 lines) finds **0** lines that start with `PASS` and are not `PASS ` (space) — and 0
  lines anywhere that are PASS-shaped after leading whitespace. So P1/P2 are *floor* widenings
  on today's corpus: they cost nothing now and close the tab class for the future.
- **Discrimination is the whole point**: with P1/P2 a forged `PASS\t…` line is no longer
  grammar-invisible. P3 is strictly weaker than P1/P2 (it misses the leading-tab shape because
  `^PASS` is anchored) — **prefer P1 or P2**; do not land P3.

### 3.2 C2(a) secondary mechanism finding: the tightening is defence-in-depth, not a live hole

[obs] `classify_process` (`run_battery.py:2093-2110`, extracted verbatim by AST and replayed;
body sha256 `3a306a7a4747128b…`) requires `signature in output` — a **raw substring** test over
the whole merged output, newline-agnostic. A tab-separated receipt
(`PASS\tinput_route route=…`) therefore still **fails** classification for the shipped
space-separated pins: measured `classify_process(0, None, tab_out, 0, "PASS input_route route=…")`
→ `False`, while the space-separated control → `True`.
Consequence [inf]: no existing fixture can silently emit a tab-PASS line — the pin itself would
have to be tab-shaped. The tightening closes the *census* blind spot (a forged extra tab-PASS
line is currently invisible to multiplicity/anchor accounting), not a presently-live PASS path.
This is exactly the honest framing the round's C2a wording asks for.

### 3.3 C2(b) verdict-layer harmlessness proofs for the 6 unflagged r103 shapes

Method: for each unflagged shape, the shape's mutated row and its unmutated base row were both
run through the **verbatim-extracted** `classify_process` with the base row's own
`expected_exit` / `signature` / `expected_errors`. [obs]

| shape | base row | exit / expected | allowlist entries | verdict before → after | class |
|---|---|---|---|---|---|
| `s1a_banner_forged_seq` | `r100b_seq_clean` | 0 / 0 | 1 | True → **True** | banner-shaped line outside every declared span: the non-grammar account binds PASS lines + anchor multiplicity, not arbitrary out-of-census lines |
| `s1b_banner_dup_launch` | `export_launch_embed_boot` | 0 / 0 | 0 | True → **True** | the DIAG-window closure admits any `RECEIPT_BANNER_RE` line → an exact banner duplicate inside the window is accounted |
| `s2a_diag_other_family_simple` | `input_route` | 0 / 0 | 0 | True → **True** | DIAG-window closure only binds rows that already carry a `*_DIAG` line; a DIAG-shaped line in a plain row is out of census |
| `s2b_diag_forged_launch` | `export_launch_embed_boot` | 0 / 0 | 0 | True → **True** | any `RECEIPT_DIAG_RE` line is legal inside a DIAG window; payload unbound |
| `s4a_tab_lead_simple` | `input_route` | 0 / 0 | 0 | True → **True** | pass-line census blind to leading-tab lines — **closed by C2a (P1/P2)** |
| `s4d_tab_after_pass_simple` | `input_route` | 0 / 0 | 0 | True → **True** | census blind to `PASS\t…` — **closed by C2a (P1/P2/P3)** |

**Result: 6/6 harmless at the verdict layer**, i.e. none of the six can convert a FAIL into a
PASS or vice versa. Four of the six are *by-design accounted* (banner/DIAG closure classes);
two are the tab-PASS census class that C2a closes at the shape layer. So the r103 statement
"6 unflagged" decomposes exactly as 4 accounted-by-design + 2 closing-under-C2a — no residual
evasion class survives r104. [obs]

### 3.4 C2 file-collision matrix (four patches, one line)

All four r104 gate patches touch the same region; each was context-checked against HEAD
line-for-line (every `@@` context line matches HEAD exactly, so all four apply to a **pristine**
copy — `patch --dry-run` in `/var/tmp` was inconclusive only because that mount is under a
quota that rejected patch's temp file; the byte-level check is authoritative): [obs]

| patch | bytes | hunks | edits `1904` census | other |
|---|---|---|---|---|
| `r104-G1-tabpass.patch` | 36 lines | 2 (1855, 1901) | yes → `^[ \t]*PASS(?![A-Za-z0-9_-])` | + new `pass_line_separator` flag before accounting |
| `r104-crit2-passprefix-tighten.patch` | 25 lines | 1 (1901) | yes | — |
| `r104-V7-pass-prefix-tighten.patch` | 19 lines | 2 (1854, 1901) | yes → `^\s*PASS\b` | — |
| `r104-S0-evasion-probe.patch` | 219 lines | 2 (2020, 5771) | no | inserts `gate_evasion_replay` + a `probe_*` row |

**Only ONE tightening text can land.** And it is load-bearing for C3a: S0's probe declares
`s4a_tab_leading_pass_line` and `s4d_tab_after_pass_token` with `expected_reasons = ()` (i.e.
"accounted-silent"), so the moment a tightening lands those two shapes flag and the probe goes
**red until re-declared** — which S0's own comment calls deliberate. Choose P1 or P2 (2
re-declarations) over P3 (1 re-declaration but weaker). G1's P2 variant additionally emits a
distinct `pass_line_separator` reason, which is the best-calibrated option: it names the class
instead of reusing `unaccounted_pass_lines`.

## 4. C3 (calibration)

### 4.1 C3(a) in-battery gate-evasion replay probe

Lattice: `r104-S0.md` (probe lead, plan-only) → `r104-S0-evasion-probe.patch` (219 lines,
sha256 `f92fb6cc500d93aa…`) → V5 verify (plan-only) → crit3 vacuity/cost (plan-only) → W8 cost
census (plan-only) → ver5/ver6 verify (plan-only).
[obs] The patch's contract: `GATE_EVASION_SHAPES` = 10 shapes (the r103 catalog, incl. the two
`!BANNER!` / `!LAST_LINE!` sentinel ops), `GATE_EVASION_CONTROLS` = 4 unmutated bases,
`GATE_EVASION_MIN_SHAPES = 8` floor, `GATE_EVASION_ACCOUNTED_CLASSES` = the 6 accounted-silent
classes, and `gate_evasion_replay(rows)` returns
`{"shapes", "controls", "skipped", "flags"}` — fail-closed on a base row present-but-not-green or
without stored output, and `skipped` (not flagged) when a base case is absent (so pre-family
historical runs stay replayable).
[obs] The tampered twin deliberately keeps its **base case name** so `receipt_shape_flag`'s F5
probe-artifact rule cannot silently skip it. [inf] That is correct given F5, but it means the
probe's greenness is coupled to the tightening decision above — record the coupling in the
round's evidence.

### 4.2 C3(b) orphaned-companion disposition — census + recommendation

There are **two distinct orphan families** on disk; both are "companion fixtures" in the lane's
own vocabulary (`r102-adjudicator.md:29` calls the export_launch set "companions, unregistered").

**Family A — r102 `export_launch_s01..s06.gd`** (in `corpus/fixtures/`, tracked, 6 files):

| fixture | bytes | arms | r102 shard | shard PASS pins | relation to the 8 landed rows |
|---|---|---|---|---|---|
| `export_launch_s01.gd` | 19544 | `embed`, `embed_ref` | `r102-E1.md` | 4 | embedded self-contained boot — **subsumed** by `export_launch_embed_*` |
| `export_launch_s02.gd` | 16264 | `embed` | `r102-E2.md` | 4 | embedded quit-frames — **subsumed** by `export_launch_embed_boot` |
| `export_launch_s03.gd` | 26773 | `refuse`,`contrast`,`sibling` (and an `all` arm printing **3 PASS lines**) | `r102-E3.md` | 6 | stock refusal + editor contrast — **subsumed** by the `--arm=probe` trio |
| `export_launch_s04.gd` | 12186 | `both`(+`lower`,`upper_excl`) | `r102-E4.md` | 4 | include/exclude filter case-sensitivity — **superseded** (r102 mut08 proved the filter case-INSENSITIVE) |
| `export_launch_s05.gd` | 22333 | `tmpl`,`feat_*` (8 arms) | `r102-E5.md` | 16 | templates feature census — **not in any landed row** (a distinct mechanism) |
| `export_launch_s06.gd` | 29466 | `base`,`patch`,`patchboot`,`preset`,`refusals`,`union`,… | `r102-E6.md` | 17 | `--export-patch` probe — **not in any landed row** (a distinct mechanism) |

**Family B — r101 `reports/round-101/mutations/orphaned-fixtures/export_prod_s01..s11.gd`**
(11 `.gd` + README, all tracked, name never referenced by `run_battery.py` — `count == 0` for
all 11). `fixture: bytes / r101 shard / shard PASS pins / README class`:
`s01: 23533 / E1 / 5 / design-superseded` · `s02: 21473 / E2 / 2 / design-superseded` ·
`s03: 13510 / E3 / 0 / provider-orphaned` · `s04: 12424 / E4 / 6 / design-superseded` ·
`s05: 27720 / E5 / 0 / provider-orphaned` · `s06: 30395 / E6 / 0 / provider-orphaned` ·
`s07: 17875 / E7 / 4 / design-superseded` · `s08: 12912 / E8 / 15 / design-superseded` ·
`s09: 16348 / E9 / 6 / provider-orphaned` · `s10: 20048 / E10 / 2 / design-superseded` ·
`s11: 17879 / E11 / 15 / design-superseded`.

Note [obs]: the README's "provider-orphaned" label is stale for `export_prod_s09.gd` — its seat
(`r101-E9.md`) **completed** (`Status: DONE — 4 arms authored + validated`, 6 pins). Only
s03/s05/s06 genuinely have no measured pins. Any disposition table must correct this.

**Per-fixture decision rule this seat recommends** (applied by S1/S2, verified by ver5/ver6):

- **ADOPT-with-fresh-pins** iff (i) the fixture exercises a mechanism **not** covered by any
  landed row, (ii) it has a completed shard with measured pins, and (iii) its receipt shape
  survives the receipt-shape gate (single PASS line per row, or an explicit
  `RECEIPT_MULTI_PASS_GRAMMAR` entry; no un-allowlisted `ERROR:` line).
  → ADOPT candidates: `export_launch_s05.gd` (templates feature census),
  `export_launch_s06.gd` (`--export-patch`), plus `export_prod_s09.gd` (nested-depth subdir
  census) if S2 re-measures it green ×2.
- **RETIRE**: `export_launch_s01/s02/s03/s04` (mechanism subsumed by landed rows; s03's `all` arm
  prints 3 PASS lines → would need a grammar declaration) and `export_prod_s01/s02/s04/s07/s08/s10/s11`
  (design-superseded — the README itself calls registration "additive coverage, not repair").
- **REPAIR-then-decide** for `export_prod_s03/s05/s06`: re-run on HEAD; adopt only what returns
  green ×2 with a fresh pin; retire the rest with the failure bytes recorded.
- [obs] Cost warning: the `all` arm of `export_launch_s03.gd` and the `union`/`refusals` arms of
  `export_launch_s06.gd` are **multi-PASS** shapes; the gate's non-grammar branch fails any row
  with `len(pass_lines) > 1` (`unaccounted_pass_lines`), so each adopted multi-arm fixture needs
  its per-row PASS tuples declared in `RECEIPT_MULTI_PASS_GRAMMAR` **in the same splice** as its
  CASES row.

## 5. Saturation bookkeeping

| item | value | source |
|---|---|---|
| saturation line | declared at r101 (an axis is saturated at R when R's verdict is `unchanged`) | `SCORECARD.md` §Saturation |
| stagnation window N | **5** consecutive rounds with no `improved` on any axis | `SCORECARD.md` |
| stagnation count entering r104 | **0** (r101/r102/r103 all returned `improved` on all three axes) | r101–r103 verdict tables |
| consequence | no stagnation nudge is owed for r104; the ≥1-lowest-axis rule is satisfied automatically since all three axes are non-retired and all three are claimed | contract §LOOP 2 |
| lowest non-retired axis entering r104 | coverage and calibration are the thinnest *structurally* (coverage's remaining open surfaces: non-headless/platform; calibration's: gate-evasion classes) — but no axis is retired, so no waiver is needed | [inf] from the verdict tables |
| CASES trajectory | r101 528 → r102 536 → r103 552; r104 will add the `res_uid_*` rows (count frozen only after the splice) | SCORECARD rows + AST count |
| receipt trajectory | r102 554 rows → r103 570 → post-r103 571 rows / 571 PASS ×2 | stored `verdicts.json` |
| capability table | `headless production export` entered at r101; **no** capability row may enter through this rollout (`AXES.md` §Capabilities) — the r104 `res_uid_*` rows are evidence, not a capability entry | SCORECARD §Capabilities |

## 6. Integration order + collision matrix for the orchestrator

1. **Land the C1 fixtures first** (parallel per seat): `res_uid.gd` (E0) + `res_uid_s01..s04.gd`
   (E1–E4); each fixture's own receipt freezes its row tuple. W7's `res_uid_w07.gd` is an
   independent repro, not a registration candidate (its arms overlap E1/E2/E4).
2. **Freeze the row tuples** from the landed receipts (E0-spec) and reconcile with §2.3.
3. **One combined splice** of `run_battery.py`: CASES rows + `cases_integrity` prefix +
   count floor (**with `--min-rows N` finally introduced** — it does not exist today) + the
   `expected_errors` entries, in a single edit; `py_compile`-gated; never land the gate-only or
   rows-only halves separately (the r103 W5 atomicity rule).
4. **Exactly one C2a tightening** from §3.4 (recommend `r104-G1-tabpass.patch`'s P2 text), then
   **re-declare** S0's `s4a`/`s4d` accounted-classes in the same session, then land
   `r104-S0-evasion-probe.patch` **after** the tightening (order matters — landing the probe
   first makes the next run red).
5. **C3b dispositions**: retire Family A's subsumed four + Family B's design-superseded seven by
   moving them (the r101 precedent moved its companions out of `corpus/fixtures/`); adopt
   s05/s06 (+s09 if green) with fresh pins + grammar declarations in the same splice.
6. **Battery ×2** by the orchestrator on the fully spliced tree (never by a seat); then
   adjudicator; then LOG/SCORECARD/report.
- **Collision note** [obs]: steps 3, 4 and 5 all edit `run_battery.py`; steps 3–4 must be
  applied sequentially in one session with a post-splice sha recorded between them, because four
  r104 patches compete for the same line (`1904`). Step 5's fixture moves do not collide.
- **Hygiene**: `reports/round-104/mutations/__pycache__/` exists (a seat imported a sibling
  script); exclude from any commit, as r103 did with its own.

## 6b. FRESHNESS DELTA (snapshot 2, ~22:36 local — concurrent landings during this seat's recon)

The C1 executors landed their fixtures while this shard was being written. Corrections to §2:

**The five C1 fixtures now exist** (all untracked, all `_emit`-shaped with exactly ONE
`print("PASS …")` site → 1 PASS line per process, which is what the non-grammar gate branch
requires): [obs]

| fixture | bytes | sha256 (12) | arms declared | PASS template |
|---|---|---|---|---|
| `res_uid.gd` (E0) | 16210 | `5d11b241becf` | 8: `text path collide cache modes import persist missing` | `PASS res_uid %s %s` |
| `res_uid_s01.gd` (E1) | 12298 | `d24bd3b21c53` | 6: `census roundtrip pathtouid createid collide diag` | `PASS res_uid_s01 %s %s` |
| `res_uid_s02.gd` (E2) | 13321 | `721c13fd532b` | 10: `reuse ignore replace deep bust deleted resdir classes xproc_seed xproc_read` | `PASS res_uid_s02 %s %s` |
| `res_uid_s03.gd` (E3) | 22666 | `7d91a8e197ac` | 5: `resolve missing refuse cache uidcache` | `PASS res_uid_s03 %s %s` |
| `res_uid_s04.gd` (E4) | 17445 | `803aa5acbba4` | 3: `classes collision persist` | **`PASS res_uid s04 arm=%s %s`** |
| `res_uid_w07.gd` (W7) | 9469 | — | 9 (repro, not a registration candidate) | `PASS res_uid_w07 …` |

Two shape findings for the splice [obs]:
1. **`res_uid_s04.gd` uses a different PASS shape** — `PASS res_uid s04 arm=…` (no `_s04` suffix
   in the family token) while s01–s03 use `PASS res_uid_sNN …`. Both are legitimate (the pin is
   whatever the fixture prints), but the row's `CASES` 5th field must be copied from the
   fixture's own bytes, and a reviewer grepping `^PASS res_uid_s04` will miss it.
2. `run_battery.py` still contains **0** occurrences of `res_uid` — no CASES row, no
   `cases_integrity` prefix, no floor gate. The whole C1 registration remains the orchestrator's
   single splice (as §6 step 3 says).
3. Three r104 lesson files also landed: `corpus/lessons/r104-resource-loader-uid.md` (289 L),
   `r104-gate-boundary-tabpass.md` (160 L), `r104-evasion-probe-and-disposition.md` (217 L).
   `reports/round-104/mutations/` now holds 63 files and `reports/round-104/` 49 shards.

**Independent confirmation of E1's U3/U4 laws** (this seat's own scratch, `/var/tmp/r104-planner/sidecar/`;
these are *not* E1's receipts, they are a second measurement of the same claim): [obs]

```
godot --headless --path . --script res://main.gd      # project with a hand-written thing.gd.uid, NO .godot/
SIDECAR_ONLY has_cache=false
SIDECAR_ONLY has_id=false            # the sidecar alone does NOT register
SIDECAR_ONLY get_id_path=            # (empty; "Invalid UID." on stderr)
SIDECAR_ONLY path_to_uid=res://thing.gd     # path ECHO — E1's U2 confirmed
SIDECAR_ONLY uid_to_path=            # (empty)

godot --headless --path . --import                    # editor pass mints .godot/uid_cache.bin
godot --headless --path . --script res://main.gd
SIDECAR_ONLY has_cache=true
SIDECAR_ONLY has_id=true
SIDECAR_ONLY get_id_path=res://thing.gd
SIDECAR_ONLY path_to_uid=uid://bf3qfun33wlt8   # the sidecar's own text, now honoured
SIDECAR_ONLY uid_to_path=res://thing.gd
```
The sidecar text was **unchanged** by the import (`uid://bf3qfun33wlt8` before and after), so
the cache is what changed the answer — E1's "sidecars are an editor artifact, the runtime
authority is `.godot/uid_cache.bin`" is independently reproduced here. [obs]
[inf] For the `persist` arms this also means the battery's dot-excluded staging
(`run_battery.py:2044-2045`) makes the fixture responsible for minting its own cache — which
`res_uid.gd:325` does (`FileAccess.open(proj + "/.godot/uid_cache.bin", WRITE)`).

## 7. Residual / unknown (explicit, for the orchestrator)

- [obs→resolved] The C1 fixtures landed during this seat's run (see §6b); the row *names* are
  still unmeasured pins until each fixture's own receipt is quoted — the §2.3 list remains a
  proposal, and `res_uid_s04.gd`'s differing PASS shape (§6b) is the concrete reason not to
  copy any name table into `run_battery.py` without the receipt.
- [unk] The count-floor N for the `res_uid_` family cannot be frozen before the splice; today
  `--min-rows` does not exist and `r103_export_div_count_floor` is still `>= 1` — the r103
  freeze remains owed into r104.
- [unk] `export_prod_s03/s05/s06` behaviour on HEAD is unmeasured by this seat (running them is
  the S1/S2 job); their README state (exit 2/1/0 with 0–4 PASS lines) predates the r102/r103
  engine and gate changes.
- [inf] The 4-shape `GATE_EVASION_*` placeholder row set inside `r104-W10-splice.py`
  (`res_uid_s01_census` … `res_uid_s04_persist`) must not be used verbatim — those PASS pins are
  invented placeholders ("reconstructed from sibling shard specs"), and a fabricated pin is the
  one thing the lane's rules forbid.
- [obs] Fleet-ledger gap: r101–r103 absent from `MANIFEST.json` `rounds[]` (only 61–64 present);
  routed to the orchestrator (fleet file, outside this seat's boundary).
- [obs] The r104 `mut05.py` (25580 B) and `mut02.py` (14112 B) landed in
  `reports/round-104/mutations/` during this seat's recon; neither was executed by this seat.
- [obs] 28 G of `/var/tmp` scratch now exists across r103/r104 seats; `patch`'s temp-file write
  to `/var/tmp` failed with `Disk quota exceeded` even though `df` shows 756 G free on `/` — the
  EDQUOT class the briefing names. Seats should prefer `git apply` (no temp file) over `patch`.

## 8. Method / honesty notes

- Every number above is [obs] unless labelled [inf] or [unk]; each table row names its command or
  its source file. Nothing was copied from a sibling shard without re-measuring it here (the two
  attributed exceptions: the r103 `mut05` catalog and the r102/r101 shard pin counts).
- This seat ran **no** `run_battery.py` (rule 1), edited **no** shared file (rule 2), created only
  this shard plus scratch under `/var/tmp/r104-planner/` (rule 3), and left no worktree behind
  (`git worktree list` unchanged from §1). Godot probes ran as
  `godot --headless --path /var/tmp/r104-planner/uid2 --script res://main.gd`; the only engine
  version observed is `4.7.2.stable.arch_linux.ed1daf0bf`.
