# r104-crit2 — C2 crit: PASS-prefix false-flag census + tightening attack

Host: `uptime` at session start 2026-10-19T01:29:43Z -> `up 1 day, 22:29, 1 user, load average: 3.77, 2.11, 1.84`. Repo `/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin` @ eff29d1d (main). Provider: devin (contracted p4 fallback). `run_battery.py` sha256 `2af2bc841ccb416e5fb0e1bbaadc08627e2d4768a8822f6956e867d905a3d0fe`.

Seat: KEY=C2. Question asked: *false-flag census — are there any legit PASS-prefixed non-receipt lines in fixtures?* Answer below is byte-measured, with the tightening's two directions separated.

## Plan (5 lines)
1. Locate the r103 receipt-shape gate (`receipt_shape_flag`) and read its pass-line census rule verbatim.
2. Census every `^PASS`-prefixed line shape across `corpus/**` (1,633 JSON records + fixture sources + non-row text) — classify receipt vs non-receipt.
3. Measure tightening: extend the census to all `PASS`-prefixed lines; compute new-flag set vs old-flag set on real corpus bytes.
4. False-positive analysis: each newly flagged line — legit non-receipt (false flag) or evasion shape? Attack the direction that removes flags.
5. Write shard: rule text, byte-cited census table, false-positive verdicts, tightening patch as mutation content.

Status: COMPLETE. All four sub-questions measured. No blocker.

## 1. The rule under attack (verbatim)

`corpus/fixtures/run_battery.py:1877-1995`, `receipt_shape_flag(row)`. The census predicate:

```
1904:    pass_lines = [line for line in output if line.startswith("PASS ")]
```

The same predicate is used as a *tolerance* in three more places:

```
1965:                if not (line.startswith("PASS ") or RECEIPT_SEQ_RE.match(line)):   # inside SEQ span
1970:                if (line.startswith("PASS ") or RECEIPT_SEQ_RE.match(line)          # post-span tail
1988:            if (line.startswith("PASS ") or RECEIPT_BANNER_RE.match(line)            # DIAG window
```

`RECEIPT_BANNER_RE = ^Godot Engine v`, `RECEIPT_DIAG_RE = ^[A-Z][A-Z0-9_]*_DIAG\b`, `RECEIPT_SEQ_RE = ^SEQ_[A-Z_]+\b`, `RECEIPT_PROGRESS_RE = ^\[ *\d+% *\]`, `RECEIPT_ANSI_ONLY_RE = ^(?:\x1b\[[0-9;]*m)+$` (lines 1852-1856).

**Rule text**: a line is a *receipt PASS line* only if byte 5 is a space. `PASS` followed by tab / `=` / a word character / end-of-line is neither a receipt line nor a foreign line — it is invisible to every one of the four predicates. That is the routed r103 boundary (LOG.md:1306 "tab-PASS is grammar-invisible (hardening candidate, routed)"; LOG.md:1307 "ROUTED (r104+): tab-PASS grammar tightening").

## 2. C1-adjacent: the false-flag census (the seat's actual question)

Method: `/var/tmp/r104-c2/census_pass_prefix.py`, walked `corpus/**` (excluding `.git`), parsed every `*.json`, yielded every dict carrying an `output: list[str]` at any depth.

Command: `python3 /var/tmp/r104-c2/census_pass_prefix.py` -> `/var/tmp/r104-c2/census_out.txt` (1,028 B, sha256 `55c2c7417388ae33…`).

```
files=1633 rows=35072 lines=265298
HISTOGRAM of ^PASS-prefixed lines:
  PASS<space>            24867
NEWLY-FLAGGED (^PASS but not 'PASS '): 0
OLD-CENSUS (startswith 'PASS '): 24867
```

| byte shape | count | receipt? |
|---|---|---|
| `PASS<space>` | 24,867 | yes — the only shape that exists |
| `PASS<tab>`, `PASS=`, `PASSX…`, `PASS<EOL>`, `PASS<NBSP>`, `PASS<CR>` | **0** | — |
| total `^PASS`-prefixed | 24,867 | — |

Source-side cross-checks (no stored bytes involved):
- Every fixture emits the canonical form. `grep -rnoE '"PASS[^ "]*"' corpus/fixtures/ --include=*.gd --include=*.py` returns no PASS-prefixed-non-space literal in any `.gd`; `PASS` appears only as a bare token inside f-strings in `run_battery.py` / `love_battery.py` / `pygame_battery.py`.
- `grep -rnoE '\bPASS[A-Za-z_]+' corpus/fixtures/` -> **0 hits**: no `PASSENGER`/`PASSWORD`/`PASSED` word ever appears in fixture stdout.
- Non-row text that *does* start with `PASS` exists only in prose/console transcripts, never inside a stored receipt: `corpus/lessons/r101-seq-replay-transcript-pin.md:107`, `corpus/lessons/r101-ytrans-dead-flag.md:13`, and `corpus/live/r25-own-absolute/console-1.txt:1-18` (harness console log lines `PASS mechanic: exit=0 signature='…'`, not Godot stdout). `grep -rlE '^PASS' corpus/` -> 2,805 files, all of them console/prose, none of them a `verdicts.json` receipt line.

**Verdict on the seat's question — false-flag census = 0.** There is no legitimate PASS-prefixed non-receipt line anywhere in the record corpus. A census over `^PASS` cannot produce a false flag on any existing evidence. The tightening is therefore *free* of false positives by measurement, not by assumption.

## 3. Tightening (a): the naive swap, measured both directions

Two candidate folds were built as pure functions in the probe (`/var/tmp/r104-c2/c2gate.py`, `gatev2.py`, `final_probe.py`) and compared against the real `receipt_shape_flag` imported by module path (module-level data only; `main()` never runs, the battery is never executed):

- **naive** = widen all four `startswith("PASS ")` sites to `startswith("PASS")` — the literal reading of "extend the census to all PASS-prefixed lines".
- **v3** = widen only the census to `lstrip().startswith("PASS")`, flag non-canonical prefixes explicitly as `pass_prefix_noncanonical`, keep the account on the canonical subset, and leave the span/DIAG windows on canonical `PASS `.

### 3a. The good direction (naive closes real forgeries)

`/var/tmp/r104-c2/tighten_probe.py` -> `tighten_out.txt` (2,791 B, sha256 `d120587a5840924d…`), injection of one line into the real green r102 run:

| injected line | landed | naive | v3 |
|---|---|---|---|
| `PASS\tforged=true` | 0 | **1** | **1** |
| `PASS=forged=true` | 0 | **1** | **1** |
| `PASSX forged=true` | 0 | **1** | **1** |
| `PASS` (bare, EOL) | 0 | **1** | **1** |
| `PASS\xa0forged=true` (NBSP) | 0 | **1** | **1** |
| `PASS\rforged=true` (CR) | 0 | **1** | **1** |
| `\tPASS forged=true` | 0 | 0 | **1** |
| `  PASS forged=true` | 0 | 0 | **1** |
| `\rPASS forged=true` | 0 | 0 | **1** |
| `\x0bPASS forged=true` (VT) | 0 | 0 | **1** |
| `\x1bPASS forged=true` (ESC) | 0 | 0 | 0 — residual, see §5 |

Landing this against the r103 mut05 catalog (`/var/tmp/r104-c2/mut05_v3.txt`, 2,210 B, sha256 `776cd9b7af0a1b1a…`): the catalog row `s4d_tab_after_pass_simple` goes from **unflagged (landed)** to **flagged**, and `s4a_tab_lead_simple` (the orchestrator's noted "verdict-layer-harmless" shape) is closed by v3.

### 3b. The harm direction — naive widening REMOVES a flag (this is the attack result)

The window tolerances are the opposite polarity: widening them *tolerates* lines the landed gate calls foreign. Byte-exact harm case, grammar row `r100b_seq_clean` (14 declared arms), delete the declared arm `PASS r100_gui warp …` and re-add it as a PASS-word forgery (`/var/tmp/r104-c2/final_probe.py` -> `final_out.txt`, sha256 `62669a54bde6f7b5…`):

```
canonical (control)  landed=[]                              naive=[]   v3=[]
PASSENGER forgery    landed=['pass_line_grammar_mismatch']  naive=[]   v3=['pass_prefix_noncanonical','pass_line_grammar_mismatch']
PASSWORD forgery     landed=['pass_line_grammar_mismatch']  naive=[]   v3=['pass_prefix_noncanonical','pass_line_grammar_mismatch']
PASSLIST forgery     landed=['pass_line_grammar_mismatch']  naive=[]   v3=['pass_prefix_noncanonical','pass_line_grammar_mismatch']
```

[obs] Naive widening counts the forgery's tokens `("r100_gui","warp")` as the declared arm, `sorted(observed) == sorted(grammar)`, so the grammar flag disappears: the widened gate reports **0 flags where the landed gate reports 1**. The naive fold does not just fail to tighten here — it *un-accounts a forged arm*, which is strictly worse than the status quo. [inf] This is why the routed instruction must not be implemented as a literal `"PASS "` -> `"PASS"` swap: the predicate serves both a census role and a tolerance role, and only the census role may be widened.

Broader sweep for the harm class (`/var/tmp/r104-c2/find_loosening.py` -> `loosening_out.txt`, 334,329 B, sha256 `b19e53a38d8bdfdf…`): 8 injections x 554 real rows = 4,432 units.

```
total (case,injection) pairs harmed by naive widening = 0
count of (case,injection) pairs harmed by corrected v3  = 0
distinct (case,injection) pairs newly closed by v3      = 3584
rows newly closed by v3                                 = 512 of 554
```

[obs] Count-level harm of the naive swap is **0** over the 554-row r102 run, because a forgery in the census needs to duplicate a declared arm's tokens to mask it, and `PASSENGER …`/`PASSWORD …` do not collide with any declared `(verb, arm)` pair except in the constructed arm-fill case above. [inf] The harm is real but token-collision-gated; a fence that only checks flag *counts* over the current corpus would call the naive fold safe and ship the loosening. The arm-fill construction is the counterexample that a count-only fence misses — this is the argument for the v3 shape over the naive shape.

[unknown] Whether a future grammar row declares an arm whose name is a prefix of `PASS<something>`; today none does (`RECEIPT_MULTI_PASS_GRAMMAR` arms are `r100_gui`, `export_prod`, `export_launch`).

## 4. False-positive analysis of the tightened gate (the required false-positive sweep)

`v3` and the applied patch were swept over **every stored PASS row in the corpus**, not just the current run (`final_probe.py`, and a second sweep re-running the *applied patched module*):

```
APPLIED-PATCH vs v3: rows=34215 mismatches=0
rows=34215 landed=110 v3=110 delta=0 rows_disagree=0
```

| gate | PASS rows swept | flags | delta vs landed | rows disagreeing |
|---|---|---|---|---|
| landed `startswith("PASS ")` | 34,215 | 110 | — | — |
| naive `startswith("PASS")` | 34,215 | 110 | 0 | 0 |
| v3 `lstrip().startswith("PASS")` | 34,215 | 110 | **0** | **0** |
| applied patch (`patched.py`) | 34,215 | 110 | 0 | 0 (byte-identical flag JSON to v3) |

**False positives introduced by the tightening = 0, over 34,215 PASS rows and 265,298 receipt lines.** The 110 pre-existing flags are unchanged in count, reason and row set; none is a newly created false flag. They classify as:

| reason | count | class | first exemplar |
|---|---|---|---|
| `anchor_line_multiplicity` | 60 | old-era rows (`r15`, `r27`-`r30`, `r50` lessons copies) | `corpus/lessons/r15-gauge-verifier.json :: health_gauge` observed=0 declared=1 |
| `pass_line_unanchored` | 35 | same old era | `corpus/lessons/r15-gauge-verifier.json :: health_gauge` |
| `foreign_in_diag_window` | 15 | current-era records carrying the *pre-fix* s01 Unicode warning | `corpus/live/runs/20261019T001435805887Z/verdicts.json :: export_div_s01_pack` |

[obs] The 15 `foreign_in_diag_window` flags are the r103 fixture fix's own evidence: `export_div_s01_pack` line 8 is `Unicode parsing error, some characters were replaced with \ufffd (U+FFFD): Unexpected NUL character`, the class LOG.md:1303 records as eliminated fixture-side ("decode names NUL-sliced ASCII (fixtures)"). The two runs that carry it (`20261019T001435805887Z`, `20261019T003019776183Z`) are FAIL runs; the post-fix runs `20261019T004115354212Z` and `20261019T005558434174Z` are PASS with the same 571 rows. [inf] The gate is flagging exactly the defect the round then fixed — corroboration that the shape layer works, not a false positive.

## 5. Residuals (disclosed, not closed)

- **R-C2-1 ESC-prefixed forgery**: `\x1bPASS forged=true` is not closed by any of landed/naive/v3. [inf] The census reads the raw line, so `\x1bPASS` does not start with `PASS` even after `lstrip()` (`\x1b` is not whitespace). Closing it needs an ANSI-strip before the census — the gate already owns `RECEIPT_ANSI_ONLY_RE`, so the mechanism exists, but stripping changes the recorded line and would need its own false-positive sweep. Routed.
- **R-C2-2 count-level fence blindness**: §3b — a count-only regression fence cannot distinguish naive from v3. Any in-battery replay (C3's K>=8 probe) must replay the **arm-fill shape**, not just append-and-count.
- **R-C2-3 old-era flag mass**: the 95 `anchor_line_multiplicity`/`pass_line_unanchored` flags live in r15/r27-r30/r50-era lesson copies, not in current runs. They are stable and pre-existing; the round-103 gate already disclosed the audit is over stored PASS rows regardless of era. Not a tightening regression, but any future "flags must be 0" claim has to scope by era.
- **R-C2-4**: `RECEIPT_ANSI_ONLY_RE`/`RECEIPT_PROGRESS_RE` tolerate lines in the DIAG window that a stricter account might reject; out of this seat's scope, unchanged by the fold.

## 6. Mutation content (for the orchestrator to apply + commit)

Patch: `reports/round-104/mutations/r104-crit2-passprefix-tighten.patch` — 25 lines, sha256 `e82d620bcbb243a2e74c2325924c747c07832c49658ae5e6479210b64325eb97`, md5 `e7d1237f96b68877b14183d49b3ca30a`. Generated with `diff -u` against a scratch copy of `run_battery.py`; the repo file was never modified.

```
--- a/corpus/fixtures/run_battery.py
+++ b/corpus/fixtures/run_battery.py
@@ -1901,7 +1901,21 @@
         return [{"case": case, "why": "fail_closed_missing_signature"}]
     anchors = [s.split("\n")[0].strip() for s in sigs]
     flags = []
-    pass_lines = [line for line in output if line.startswith("PASS ")]
+    # r104 C2 fold: the census reads every PASS-prefixed line, not just the
+    # canonical `PASS ` token. A line that starts with PASS but is not the
+    # canonical receipt prefix (PASS<tab>, PASS=, PASSENGER, bare PASS, and
+    # lead-whitespace forms) is a forgery surface: it is invisible to the
+    # `PASS `-only census, so the account below never sees it. Flag it
+    # explicitly, then keep the account on the canonical subset so the
+    # grammar/one-line checks are unchanged. The span and DIAG windows
+    # deliberately stay on `PASS `: widening them would TOLERATE forged
+    # PASS-word lines that the landed gate flags as foreign (measured).
+    pass_prefix = [line for line in output if line.lstrip().startswith("PASS")]
+    for line in pass_prefix:
+        if not line.startswith("PASS "):
+            flags.append({"case": case, "why": "pass_prefix_noncanonical",
+                          "line": line[:80]})
+    pass_lines = [line for line in pass_prefix if line.startswith("PASS ")]
     grammar = RECEIPT_MULTI_PASS_GRAMMAR.get(case)
     if grammar is not None:
         observed = []
```

Apply check: `patch -p0` onto a pristine copy -> `chk.py`, sha256 `e760599e61ce6eb9333fee62fc85c98451ad41a7b8c5af518d4d18767ddb9052`, byte-identical to the intended `patched.py` (same sha256). The patched module imports cleanly and, re-swept, produces flag JSON byte-identical to v3 on all 34,215 PASS rows (mismatches=0), and restores the harm case:

```
APPLIED PATCH on harm case: ['pass_prefix_noncanonical', 'pass_line_grammar_mismatch']
```

No new account-table entry is needed: `pass_prefix_noncanonical` is a shape flag, not an allowlist entry, so the floor-not-ceiling discipline (`RECEIPT_MULTI_PASS_GRAMMAR` / `RECEIPT_ANCHOR_MULTIPLICITY`) is untouched. No fixture emits a non-canonical prefix (§2), so no fixture needs changing and no re-pin is required.

## 7. Reproduction

```
# census (the seat's question)
python3 /var/tmp/r104-c2/census_pass_prefix.py                 # -> census_out.txt
# naive vs v3 on injected shapes + 34,215-row false-positive sweep
python3 /var/tmp/r104-c2/tighten_probe.py                      # -> tighten_out.txt
python3 /var/tmp/r104-c2/attack_widening.py                    # -> attack_out.txt
python3 /var/tmp/r104-c2/boundary_probe.py                     # -> boundary_out.txt
python3 /var/tmp/r104-c2/find_loosening.py                     # -> loosening_out.txt
python3 /var/tmp/r104-c2/final_probe.py                        # -> final_out.txt
# patch generation + apply check (scratch copy; repo file untouched)
cd /var/tmp/r104-c2 && cp <repo>/corpus/fixtures/run_battery.py orig.py && diff -u ... && patch -p0 chk.py < r104-crit2-passprefix-tighten.patch
```

All probes import the gate by module path; `run_battery.py` was never executed in any form (no `main()`, no `godot`, no fixture run). No git worktree was created (`git worktree list` shows only the main worktree), so nothing to remove. Scratch is under `/var/tmp/r104-c2/` (never `/tmp`, which is EDQUOT).

## 8. Axis read (this seat)

| axis | verdict | evidence |
|---|---|---|
| coverage | **improved** | false-flag census is now measured rather than assumed: 24,867 `^PASS` lines / 1,633 records / 35,072 rows, all canonical; the tightening's blast radius is bounded to 0 new flags over 34,215 PASS rows |
| depth | **improved** | the naive swap's harm direction is proven byte-exact (grammar arm-fill: landed 1 flag -> naive 0 flags), so the routed instruction is shown to be under-specified; the corrected fold (v3) closes tab/`=`/`X`/EOL/NBSP/CR plus the lead-whitespace class the orchestrator called "verdict-layer-harmless" |
| calibration | **improved** | patch is apply-clean and byte-reproduces v3 (sha256 `e760599e…` both sides); 4 residuals disclosed with exact bytes; no new table entry, no re-pin, no fixture change |

## 9. Cross-seat reconciliation (read after writing §1-8)

Sibling seats landed while this one ran; the two overlaps are consistent:

- **`r104-crit3.md` F2 "15-flag false-flag surface inside the gate's own DIAG window"** is the same 15 flags this shard classifies in §4 — all 15 are `foreign_in_diag_window` on `export_div_s01_pack` (and siblings) carrying the pre-fix `Unicode parsing error … U+FFFD` line. Two seats, two labels, one byte class. [obs] `grep -n 'foreign_in_diag_window\|F2' reports/round-104/r104-crit3.md` shows crit3's framing is "false flag" while mine is "the gate correctly flagging the defect r103 fixed". [inf] The reconciliation: it is a *correct* flag on a *stale* record — post-fix runs (`20261019T004115354212Z`, `20261019T005558434174Z`) do not carry it. Either label is defensible; what matters for the tightening is that neither the landed nor the v3 census *creates* it (delta 0 on those rows).
- **Base-run drift**: crit3 measures against `20261019T005558434174Z` (571 rows, `audited=554 flags=0`); this shard measured shape injection against `20261018T213443471189Z` (554 rows, 0 flags). [obs] Both are green runs of the same gate sha256 `2af2bc84…`; the row delta is corpus growth (571 vs 554), not a gate change. [inf] The `flags=0` of crit3 and the `110` of §4 do not conflict: 110 is over *all* stored PASS rows corpus-wide (old-era lesson copies dominate), 0 is over the one current run.
- **`mutations/r104-X2-*`** (a third seat's C2a artifacts: `r104-X2-pass_census.py`, `r104-X2-harmlessness.py`, `r104-X2-evasion_replay.py`) also target this sub-claim. This shard did not read their results (they were mid-flight); the orchestrator should merge the two measurements rather than treat either as the sole C2a evidence. [obs] `r104-X2-pass_census.py` widens to plain `startswith("PASS")` (the naive fold), so §3b's arm-fill counterexample applies to it directly — worth checking whether its harmlessness run covers the arm-fill shape or only append-and-count.
