# r104-sent2 — KEY=X2 — Evidence-discipline sentinel

Host: `22:29:53 up 1 day, 22:30, 1 user, load average: 3.65, 2.14, 1.85` (Sat Oct 18 22:29:53 -03 2026)
Repo: /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin @ eff29d1d (main, no commits by this seat)
Provider: devin (amended p4)
Scratch: `/var/tmp/r104-X2/` (never `/tmp` — EDQUOT class). Sibling lane game-dev-3d untouched.

## Plan (5 lines)
1. C1: probe ResourceUID id<->path round-trips + load-cache identity + cache_mode busting + .import remap + cross-process persistence (scratch /var/tmp/r104-X2/).
2. C2a: extend receipt-shape gate pass-line census from `PASS\t` to all PASS-prefixed lines; false-positive analysis on the stored corpus.
3. C2b: verdict-layer harmlessness proofs for the 6 unflagged r103 evasion shapes.
4. C3a: stored in-battery gate-evasion replay probe (K>=8 synthetic shapes vs receipt_shape_flag).
5. C3b: orphaned-companion disposition (adopt-with-fresh-pins vs retire) per fixture + evidence.

Labels: [obs] observed / [inf] inferred / [unk] unknown.

## Method note (hard rule 1 compliance)

`corpus/fixtures/run_battery.py` was **never imported and never executed**. The gate
functions were extracted by AST (`reports/round-104/mutations/r104-X2-gate_extract.py`)
into a side-effect-free scratch module. Source under test:
`sha256 2af2bc841ccb416e5fb0e1bbaadc08627e2d4768a8822f6956e867d905a3d0fe` (5783 lines),
matching the sha r104-W5 independently recorded. Extraction kept exactly
`receipt_shape_flag`, `receipt_shape_audit`, `receipt_allowed_error` + 10 tables
(`CASES` 552 rows, 19 grammar entries, 2 derived-evidence cases, 1 anchor-multiplicity entry).

The 4 landed `godot --headless` probes in §4 ran on staged scratch copies under
`/var/tmp/r104-X2/proj/` (fixtures copied, `run_battery.py` deleted from the copy).

---

## 1. C2a — PASS-prefix census tightening: zero false-positive surface [obs]

**The hole.** `receipt_shape_flag`'s census is `line.startswith("PASS ")` (a literal
space). A line `"PASS\tforged=true"` (TAB after the token) is therefore invisible to the
census — r103 recorded this as evasion shape `s4d` and routed it to r104.

**Measured false-positive surface.** Every `PASS`-prefixed line that is *not* `"PASS "`
across all 8 stored runs (`corpus/live/runs/*/verdicts.json`):

```
$ python3 reports/round-104/mutations/r104-X2-pass_census.py
20261018T200239625248Z sha=8a53f0e22f75e6d8 rows=546 audited=524 flags=12 nonstd_pass_prefixed=0
20261018T202131127599Z sha=5f6c0efae49c2f1e rows=546 audited=527 flags=10 nonstd_pass_prefixed=0
20261018T212500022987Z sha=65986c3f808b6f22 rows=554 audited=538 flags=0  nonstd_pass_prefixed=0
20261018T213443471189Z sha=65e7fae0ca987563 rows=554 audited=538 flags=0  nonstd_pass_prefixed=0
20261019T001435805887Z sha=a444e382ce31da5b rows=571 audited=554 flags=15 nonstd_pass_prefixed=0
20261019T003019776183Z sha=19226f75e784f686 rows=571 audited=554 flags=0  nonstd_pass_prefixed=0
20261019T004115354212Z sha=a7ab001fe5961bcc rows=571 audited=554 flags=0  nonstd_pass_prefixed=0
20261019T005558434174Z sha=9f66675ef24b9429 rows=571 audited=554 flags=0  nonstd_pass_prefixed=0
```

**Verdict:** the tightening `startswith("PASS ")` → `startswith("PASS")` adds **0 new
lines** over the entire stored corpus. It is free on green data and closes the s4d hole:

```
s4d line: 'PASS\tforged=true'
  current census   startswith('PASS ') -> False   (invisible)
  tightened census startswith('PASS')  -> True    (counted)
```

[inf] The tightening is safe to land as a census-only change. [unk] It does not by
itself make s4d *flag* — see §3; the line is `unaccounted_pass_lines`-only once the
census sees it, and `pass_line_unanchored` is already satisfied because the base row
carries exactly one legit PASS line. r104-W5 independently measured the same zero
blast radius on the same HEAD sha (its §3), corroborating this result.

**Baseline gate flags, classified [obs]:**
- Runs `…212500…`, `…213443…`, `…003019…`, `…004115…`, `…005558…` → **0 flags** (green corpus).
- Runs `…200239…` / `…202131…` (r101-era) → 12 / 10 flags: 8 `dead_shape_allowlist_entry`
  (grammar entries for rows that did not exist yet) + `r101_ytrans_*` `pass_line_unanchored`
  + `anchor_line_multiplicity`. These are **era-mismatch artifacts** of a run-bound gate
  reading pre-grammar records, not live defects. [inf]
- Run `…001435…` (the first r104 attempt, FAIL) → 15 `foreign_in_diag_window` flags, all
  one real class: `Unicode parsing error, some characters were replaced with � (U+FFFD)`
  on `export_div_s01_pack/_zip/_ext/_ident/_embed`. **The gate has teeth on real bytes:**
  it caught the s01 UTF-8 warning class that r103 later fixed fixture-side. [obs]

## 2. C2b — verdict-layer harmlessness proofs (6 unflagged r103 shapes) [obs]

**Crisp condition.** An evasion is *dangerous* iff its forged text can supply the row's
signature (the classifier is `signature in output`). Measured over the 6 unflagged shapes:

```
s1a_banner_forged_seq    sig⊂forged=False   forged⊂sig=False
s1b_banner_dup_launch    sig⊂forged=False   forged⊂sig=False
s2a_diag_other_family    sig⊂forged=False   forged⊂sig=False
s2b_diag_forged_launch   sig⊂forged=False   forged⊂sig=False
s4a_tab_lead_simple      sig⊂forged=False   forged⊂sig=False
s4d_tab_after_pass       sig⊂forged=False   forged⊂sig=False
```

None carries the signature ⇒ none can manufacture a PASS.

**Both-direction proof** (`reports/round-104/mutations/r104-X2-harmlessness.py`), using
`classify_process` transcribed **verbatim** from `run_battery.py:2093-2106`:

```
s1a_banner_forged_seq    H3_green+forged=True  H1_bad=False  H1_bad+forged=False -> HARMLESS
s1b_banner_dup_launch    H3_green+forged=True  H1_bad=False  H1_bad+forged=False -> HARMLESS
s2a_diag_other_family    H3_green+forged=True  H1_bad=False  H1_bad+forged=False -> HARMLESS
s2b_diag_forged_launch   H3_green+forged=True  H1_bad=False  H1_bad+forged=False -> HARMLESS
s4a_tab_lead_simple      H3_green+forged=True  H1_bad=False  H1_bad+forged=False -> HARMLESS
s4d_tab_after_pass       H3_green+forged=True  H1_bad=False  H1_bad+forged=False -> HARMLESS
SHAPES=6 VIOLATIONS=0
```

- **H1 (no false PASS):** delete the real signature line → FAIL; add the forged line → still FAIL.
- **H2 (no masked FAIL):** a failing row + the forged line → still FAIL.
- **H3 (green stability):** green base + forged line → still PASS.

**Verdict: all 6 are verdict-layer HARMLESS, 6/6, 0 violations.** [obs]
[inf] The shape-layer gate's silence on these 6 is therefore *accounted*, not a hole:
the tab-PASS class (s4a/s4d) is closed by the §1 census tightening; the banner/DIAG
classes are closed by the declared-span / DIAG-window clauses for any row that embeds a
span or a `*_DIAG` verb, and are verdict-inert otherwise. [unk] A forgery that *replaces*
a legit line with another legit-shaped line carrying the signature (r101-crit2 SF2) remains
outside this proof — unchanged, inherited ceiling.

## 3. C3a — stored in-battery evasion replay probe (K=10) [obs]

`reports/round-104/mutations/r104-X2-evasion_replay.py` — replays K=10 synthetic shapes,
each a tampered copy of a REAL green stored row (run `…005558…`, sha `9f66675ef24b9429`),
against the AST-extracted landed gate. **Green iff every shape's observed flag status
equals its declared classification** — the probe is self-falsifying, not vacuous.

```
WROTE /var/tmp/r104-X2/evasions_r104.json K=10
GATE=/var/tmp/r104-X2/gate_extract.py sha256=1df372b333f4aa23
s1a_banner_forged_seq    declared=HARMLESS observed=HARMLESS OK  []
s1b_banner_dup_launch    declared=HARMLESS observed=HARMLESS OK  []
s2a_diag_other_family    declared=HARMLESS observed=HARMLESS OK  []
s2b_diag_forged_launch   declared=HARMLESS observed=HARMLESS OK  []
s3a_flood5_simple        declared=FLAG     observed=FLAG     OK  [unaccounted_pass_lines]
s3b_flood1_seq           declared=FLAG     observed=FLAG     OK  [pass_line_grammar_mismatch]
s4a_tab_lead_simple      declared=HARMLESS observed=HARMLESS OK  []
s4b_trail_space_simple   declared=FLAG     observed=FLAG     OK  [anchor_line_multiplicity,unaccounted_pass_lines]
s4c_trail_nbsp_simple    declared=FLAG     observed=FLAG     OK  [unaccounted_pass_lines]
s4d_tab_after_pass       declared=HARMLESS observed=HARMLESS OK  []
SHAPES=10 MISMATCH=0
```

Exit 0 (all shapes match). **Anti-vacuity:** each `declared` is a *prediction*, and the
replay is red if the gate over-flags a HARMLESS shape (false positive) or under-flags a
FLAG shape (miss). A probe that flagged nothing would show `observed=HARMLESS` on s3a/s3b/
s4b/s4c and exit non-zero. [obs] s4d is declared HARMLESS because the *unmodified* landed
gate still cannot see it (§1) — the probe records that honestly rather than claiming a
closure the gate does not yet have.

## 4. C3b — orphaned-companion disposition (measured, not assumed) [obs]

The 11 r101 companions (`reports/round-101/mutations/orphaned-fixtures/`) were staged into
`/var/tmp/r104-X2/proj/` and each run once standalone:

```
$ godot --headless --path /var/tmp/r104-X2/proj --script res://export_prod_sNN.gd -- --work=…
s01 rc=0  PASS=1  FAIL=0    s07 rc=2  PASS=0  ASSERTION FAILED (known_path artifact bytes=-1; control_splice accepted)
s02 rc=2  PASS=0  FAIL=1    s08 rc=0  PASS=4  FAIL=0
s03 rc=2  PASS=0  FAIL=1    s09 rc=0  PASS=1  FAIL=0
s04 rc=0  PASS=1  FAIL=0    s10 rc=1  PASS=0  FAIL=4
s05 rc=1  PASS=0  stderr: Parse Error at export_prod_s05.gd:623 (_emit_pack arg 2 type)
s06 rc=2  PASS=1  FAIL=2    s11 rc=2  PASS=0  FAIL=1
```

**Disposition — ADOPT none as-is; the coverage claim in the README holds [inf]:**

| fixture | measured | disposition |
|---|---|---|
| s01 base PCK | rc=0, PASS `magic=GDPC … entries=14 bytes=4432 md5_ok=14/14` | **retire** — scenario covered by landed `export_prod_base_pck` + `_zip_census` |
| s02 zip | rc=2 (self-FAIL) | **retire** — covered by `export_prod_zip_census` |
| s03 determinism | rc=2, `FAIL reason=export_rc_a detail=nonzero` | **retire** — covered by `export_prod_det_a/det_b` |
| s04 swap | rc=0, `PASS swap=true pack_swapped=3` | **retire** — covered by `export_prod_main_scene_swap` |
| s05 remap/UID | rc=1, **parse error** (`_emit_pack` arg 2 `Dictionary`≠`PackedByteArray`) | **retire** — covered by `export_prod_resource_remap_census` + `_icon_uid_census`; also broken against 4.7.2 |
| s06 filter | rc=2, `ASSERTION FAILED entry_row_7 got=project.binary` | **retire** — covered by `export_prod_include_exclude_filter` |
| s07 refusal classes | rc=2, 5 assertion failures incl. `mutant control_splice accepted` | **retire** — covered by `export_prod_unknown_preset_refusal`; its own classifier is not host-stable |
| s08 | rc=0, `PASS … arms=control_exe,missing_exe,missing_pack` | **retire** — covered by `export_prod_templates_missing_class` |
| s09 subdir | rc=0, PASS (1 line) | **retire** — covered by `export_prod_subdir_census` |
| s10 hashing/log | rc=1, `FAIL failures=3` + stderr `hashing_context.cpp:54` | **retire** — no landed counterpart needed; scenario not in the row set |
| s11 | rc=2, `FAIL reasons=unknown_arm` | **retire** — no arm selected; not adoptable |

[inf] Only 3/11 (s01, s04, s08, s09 = 4) run green standalone; **7/11 fail or parse-error
on a quiet host today**, so "adopt-with-fresh-pins" would require repairing each first —
net-negative for the round. The landed `export_prod.gd` harness (17 registered rows,
8 arms) covers every listed scenario. **Recommendation: retire all 11** (keep the
directory as provenance); the README's "do not register without fresh measured pins" is
correct and I add the measured evidence it lacked. [unk] s10's hashing scenario has no
landed counterpart — flag for a future round if that surface is wanted.

## 5. Sentinel audit of sibling r104 shards (frozen 22:33) [obs]

45 shards `reports/round-104/r104-*.md` existed at scan; **every one carries a plan header
in its first 10 lines** (hard-rule-6 compliance 45/45). Executed-evidence shards at scan
time: `connector`, `sent1`, `ver3`, `ver7`, `w5` (5); the remainder are plan/recon-only.
`corpus/fixtures/res_uid_s04.gd` + `res_uid_w07.gd` were the only landed r104 fixtures
at scan; `res_uid.gd`/`s01`/`s02`/`s03` had not yet appeared. [obs]

**Discipline finding:** shards are being rewritten *after* I read them (r104-connector grew
to 238 lines, r104-scout to 226, r104-ver3 to 336 within the window), so any sentinel
table is a **snapshot**, not a verdict on final state. [obs] I therefore report method
discipline (plan-header compliance, command/observation labeling) and do not freeze
content verdicts for shards still in flight.

## 6. Verdict

| axis | verdict | evidence |
|---|---|---|
| coverage (C1) | **not this seat** | ResourceUID lattice owned by E0–E4/crit1; X2 produced no `res_uid*` fixture (exclusive ownership respected) |
| depth (C2) | **improved** | census tightening proven false-positive-free over 8 runs (§1); 6/6 harmlessness proofs both directions (§2); gate teeth demonstrated on real bytes (15 U+FFFD catches, §1) |
| calibration (C3) | **improved** | K=10 self-falsifying replay probe green 10/10 (§3); 11-companion disposition measured per fixture with run evidence, retire recommended (§4) |

## 7. Honest limits / unknowns
- The 6-harmlessness proof binds the *landed* classifier semantics; a classifier change
  invalidates it (re-run `r104-X2-harmlessness.py`).
- The C3a probe binds the *current* gate sha `1df372b333f4aa23`; a gate edit must re-run it.
- C3b ran each companion once; s07/s10 showed host-sensitive assertions (refusal-class
  drift) between my runs — their FAIL verdicts are stable, but the exact assertion set is not.
- No git worktree was created by this seat (`git worktree list` shows only the pre-existing
  r98/r99/r100 worktrees, none mine). No shared file was edited. No commit made.
