# r102-planner — lattice map (C1/C2/C3), CASES registration order, saturation bookkeeping

Plan: (1) read scorecard tail/LOG tail/r101-adjudicator fully; (2) map C1/C2/C3 as a lattice with
integration risks + file-ownership collisions; (3) pin exact CASES row names + registration order;
(4) saturation/stagnation bookkeeping vs N=5 declared at r101; (5) read-only on shared files, no battery runs.
Host: `uptime` 17:40:40 up 1 day 17:40, load 7.13/8.55/9.21 (local; = 20:40:40Z). HEAD 1392ca21.
Status: COMPLETE. No shared-file edits, no `run_battery.py` run, no commits. Labels: [obs]/[inf]/[unk].

## 0. Scope of this seat
Reads only: SCORECARD.md (1-40 + 205-324), LOG.md (1213-1252), r101-adjudicator.md (full),
r101-simp1/2/3.md, r101-scout.md, r101 timeouts, run_battery.py (CASES region 1600-1702, execute()
1892-1988, meta probe 4510-4600, timeout driver 5314-5402, gates 4040-4100), timeout_probe.gd,
export_prod.gd header, r26-timeout-executor.md, r62-baseline.md (74-92), in-flight r102 shards.

## 1. HEADLINE — C2 failing arm is MISATTRIBUTED (correction to the r101 record; highest-value item)

**Observed [obs]:** the verdict formula `run_battery.py:5375-5387` requires four conjuncts.
From `corpus/live/runs/20261018T200239625248Z|20261018T202131127599Z/timeout-verdicts.json`:

| arm | timed_out | marker_observed | inner_class | child_dead | conjunct result |
|---|---|---|---|---|---|
| slow_clean_old_bound | true | **FALSE** (both runs) | false | false | `old_rejects = FALSE` ← the only red conjunct |
| slow_clean_new_bound | false | true | true | – | `new_accepts = TRUE` |
| hold_open_new_bound | true | true | false | false | `hold_rejects = TRUE` (all 4 members satisfied) |

Both runs byte-identical: old arm `elapsed=0.753`, kill before marker; hold arm `elapsed 3.005/3.006`.
The r101 adjudicator (and the round-102 brief) blames the `hold_open_new_bound` arm; the bytes say the
hold arm is fully green and `slow_clean_old_bound.marker_observed=false` is the sole FAIL cause.

**Mechanism [inf, high confidence]:** marker timing vs the 0.75 s bound.
`timeout_probe.gd:7` prints the marker before `:9` awaits 1.5 s, so marker time ≈ startup overhead.
- r26 calibration [obs]: old arm elapsed 0.753 **marker observed**; new arm 1.877 (delay 1.5) → overhead ≈0.377 s.
- r101 [obs]: new arms 2.294/2.346 → overhead ≈0.794/0.846 s (upper bound of marker time). Old bound 0.75 s
  now fires *before* the marker reaches the captured stream → marker lost → red. Both runs identical because
  the load class was sustained (load 33→57 that evening; adjudicator §host). No driver data-loss needed to
  explain it: r26 was green under the same driver code with the same overwrite path (`5341-5343`→`5350`).

**Constraint inequalities for any repair (D3/mut4 own the fix; these are the decision criteria):**
- O1 `old_bound > time_to_marker` (else marker lost → red; r101 margin ≈ −0.04…−0.10 s, was +0.38 s at r26)
- O2 `old_bound < startup + delay` (else the clean exit is accepted → rejection proof lost; margin ≈ +1.0 s)
- N1 `new_bound > startup + delay + teardown` (measured cycle 2.294-2.346 vs 3.0 → margin 0.65-0.71 s, thin too)
- H1 `new_bound > time_to_marker` (hold arm; margin ≈ 2.1 s, safe)

**Option space:** (a) old bound 0.75→~1.25 s → O1 margin ≈ +0.4 s, O2 margin ≈ +1.0 s (minimal, keeps all
constants semantics); (b) separation-widening: make `--delay-clean` take seconds, e.g. old 1.25 / delay 3.5 /
new 6.0 → margins ≈ +3.2/+1.5 s (robust to heavier load; wall cost ~+4.5 s/battery); (c) envelope that drops
the marker clause — **not recommended** (destroys the "started cleanly, delayed on purpose" discrimination O2
exists to prove; a black-hole startup would then pass). Any constants change must update the payload
`constants` fields (5317-5320, 5391-5394), the r62/r63 lesson text (w7 audit) and the LOG note.
**Counterfactuals to demand of D seats:** time-to-marker instrumented under load (>0.75 proves O1); quiet-host
old arm green; old bound applied to `--hold-open` also loses the marker (arm-agnostic mechanism); post-fix
mut4 inverse (revert bound → red again).

## 2. C1 lattice — export_launch matrix

### 2.1 Files (executors own; staged automatically per scaffold §4.6)
`export_launch.gd` (E0 lead) + `export_launch_s01..s06.gd` (E1-E6). Zero existing `export_launch*` files and
zero existing CASES names starting `export_launch` at T0 [obs: r102-scout/sent1/w6].

### 2.2 CASES row contract (pinned; evidence bytes supplied by E-seats, orchestration splices verbatim)
Names must literally start `export_launch_` (w6 cell F/H: `r102_export_launch_*` and bare `export_launch` FAIL
the prefix). Registration order = insertion immediately after `('export_prod_templates_missing_class', …)` at
**line 1693** and before `("crash_spontaneous_sigabrt"` at **line 1694** (binding tail convention, r101 block
is the adjacent predecessor). Exact tuples (5-field shape; flags `[]`, expected_exit 0 unless E0-spec states
otherwise — nested refusals are classified inside the fixture à la export_prod):

```
('export_launch_s01', 'export_launch_s01.gd', [], 0, '<E1 PASS line: embed_pck=true self-contained binary, rc0+marker+size bound>'),
('export_launch_s02', 'export_launch_s02.gd', [], 0, '<E2 PASS line: embedded + --quit-after frame vector, extra=false>'),
('export_launch_s03', 'export_launch_s03.gd', [], 0, '<E3 PASS line: stock-template --main-pack refusal class + editor contrast>'),
('export_launch_s04', 'export_launch_s04.gd', [], 0, '<E4 PASS line: filter case-sensitivity census>'),
('export_launch_s05', 'export_launch_s05.gd', [], 0, '<E5 PASS line: export_presets/template feature census>'),
('export_launch_s06', 'export_launch_s06.gd', [], 0, '<E6 PASS line: patch-mode probe>'),
```

Rules: E0's own `export_launch.gd` arm rows are named `export_launch_<topic>` (never bare `export_launch`) and
inserted immediately before s01; extra arm rows for any fixture = `<primary>_<arm>` immediately after their
primary; no other ordering allowed. Refusal surface reference [obs: r102-ver2 recon]: template `--main-pack`
refusal verbatim `compiled without support for path overrides … disable_path_overrides=no`, exit 1, gate
`#ifndef TOOLS_ENABLED` + `DISABLE_PATH_OVERRIDES` (main/main.cpp:1892) — E3 must capture bytes itself.

### 2.3 Required harness splices (orchestrator, ONE atomic commit with fixtures)
- S1 the 6(+E0) CASES rows above (anchor lines 1693/1694).
- S2 `cases_integrity` prefix tuple += `"export_launch_"` — patch ready: `reports/round-102/mutations/w6_cases_integrity.patch`
  (anchor line 4099, unique; w6 cells D/J2: prefix-only splice reddens the NEXT battery — land rows+tuple together).
- S3 floor gate `r102_expected_errors_all_matched` over prefix `("export_launch_",)` (shape=r101 gate lines 4076-4080);
  vacuous-but-honest if no allowlist entries — recommended: E-seats use export_prod's nested-log redirect (evidence
  rule, export_prod.gd:48-53) so no allowlist entry is needed.
- S4 conditional: row timeout at line 1913 (`60 if script.startswith("__godot_export") else 8`). If any E receipt
  shows standalone wall time > ~5 s (embed export copies a 73.5 MB template + launches the binary), extend to
  `script.startswith(("__godot_export", "export_launch"))`; until then keep 8 s and watch the integration run.
  (r101 export_prod nested-export rows survived 8 s, but export_launch adds the binary launch leg.)
- S5 expected_errors dict entries only if an E-seat deliberately surfaces ERROR bytes (then verbatim + covered by S3).
- S6 comment sha citations in run_battery.py only if E fixtures carry them.

### 2.4 Risks / acceptance
Risks: fixture must export its OWN minimal subproject under scratch (export_prod.gd:28-34 convention), never the
battery scratch project (100+ fixtures); delete artifacts after receipt (~73 MB each) to keep run dirs small; the
opt-in meta probe `probe_export_launch` (4510-4601) is name-disjoint from the family and stays untouched (w6 R5);
no device-census tokens in any PASS line (host-conditional `joys`; host rule).
Acceptance: battery count 528 → 528+n; `grep -c '^PASS export_launch_' <log>` == n; `cases_integrity=true` in
`probe_error_clause_surface` discriminations; no TIMEOUT in any export_launch record.

## 3. C3 lattice — simplifier queue + stale citations

### 3.1 Unique hunk inventory (patches on disk, `git apply --check`-validated at r101 close)
| patch (reports/round-101/mutations/) | file | Δ | note |
|---|---|---|---|
| r101-simp1-r91-nav_lattice.patch | nav_lattice.gd | −3 | byte-identical dup of r101-simp3-nav-fold.patch → apply ONE |
| r101-simp1-r98-canvas_lattice.patch | canvas_lattice.gd | −10 | |
| r101-simp1-r98-r98b_attack.patch | r98b_attack.gd | −4 | |
| r101-simp1-r98-r98b_rksenum.patch | r98b_rksenum.gd | −3 | |
| r101-simp1-r99-audio_lattice.patch | audio_lattice.gd | −2 | |
| r101-simp3-particles-fold.patch | particles_lattice.gd | −3 | |
| r101-simp3-r95-fold.patch | dss_lattice.gd + r95b_order.gd | −5 | **conflicts with r101_ytrans_census pin — see 3.3** |
| r101-simp3-r95-harness-comment.patch | run_battery.py comments | 0 | lines 882/885 sha citations |
| r101-simp2-stree_lattice.gd.diff | stree_lattice.gd | −17 | 51+6+3 call-site folds, builder script r101-simp2-fold_stree.py |
| r101-simp2-scene_io_lattice.gd.diff | scene_io_lattice.gd | −12 | terminal `= null` stores only |
Total −59 unique lines / 9 fixtures + r95b. All deletion-only: **no new CASES rows, no gate changes.**

### 3.2 Disposition GAPS (queued but patched by NOBODY — S0 must land-or-hold each explicitly)
- r99 F2 `pairs` in `r99b_modes.gd` (−1): simp1 table says "out of half, hand off"; simp2 table says "SIMP-1 half"
  → contradictory ownership, net: unpatched. [obs: both shards]
- r100 SP2/SP3 dead `--arm` path in `r100b_seq.gd` (−5): same contradiction, unpatched.
- r97 F6 `ready_ticks` in `r97_scene_marker.gd` (−4): simp2 §7.1 calls it "SIMP-1's half"; simp1 scope excludes it
  → unpatched. If C3's claim is "land the queue", these three are the completeness test (or must be explicitly held).

### 3.3 The one real cross-patch conflict [obs]
`r101_ytrans_census` CASES row (run_battery.py:1666) pins two FIELDS of r95b_order.gd **computed at runtime**:
`r95b_lines=778` and `r95b_sha256=4f7e945e1b16f241d510e1b1aa7c7fc1aafca6369626e3910bb36cf62d9e2490`.
The r95 fold edits r95b_order.gd (7 dead stores) → both fields change → the row goes red unless re-pinned in the
same splice with the folded values (folded sha `b367559e831e5e…` per simp3 §3; folded line count from S-seat
receipts). Re-pin preserves the tripwire semantic (sha = current bytes; `r95b_offy_tokens=0` unchanged). All other
sha citations are comments only (542 scout-probe sha — unaffected; 799/1281-1282/1406 comments; safe to update).
If r95b's re-pin is judged too risky, hold the r95b half of the fold and keep dss (no CASES pin).

### 3.4 Stale `.shokunin/game-dev-2d/corpus/` citations [obs: r101-scout §2; r102 re-census pending]
- SCORECARD.md lines 8-10: 3 LIVE command occurrences — copy-paste broken today; correct form
  `python corpus/fixtures/run_battery.py …`. Fix = orchestrator (must land; C3 acceptance `grep -c` = 0).
- PROVINCE.md:6 (1 occurrence, false present-tense claim) — orchestrator fix.
- corpus/lessons/ 100 files / 736 occurrences = historical receipts → policy fork (leave as history vs dated
  bulk sweep); recommend: leave history, fix only live/functional claims. LOG.md 45 = history, keep. README 0.
- S4 evidence script exists: `reports/round-102/mutations/s4_fix_stale_citations.py`; r102-scout re-census decides.

### 3.5 C3 acceptance
Battery green at 528 rows with no signature drift beyond the declared backtrace-line-number class (12 stderr
diffs, no pin reads line numbers — simp1 §101); S-seat per-hunk receipts; post-splice `grep -c '4f7e945e…'` == 0
if re-pinned; comment-sha consistency per simp1 §5 follow-ups.

## 4. Cross-lane integration order (one close, atomic where stated)
Regions are disjoint: C1 = CASES tail + gate tuple + new fixtures; C2 = main() timeout section (5314-5402) +
timeout_probe.gd if delay-arged + lesson; C3 = fixture deletions + comments (882/885) + possibly CASES line 1666
re-pin. This round MUST land (as applicable): C1 rows+tuple as ONE splice; C3's r95b re-pin in the same commit as
the r95 fold; C2 constants + lesson text in one commit. Then: LOG entry, SCORECARD verdict table + saturation +
lines 8-10 fix, capability row decision.

## 5. Saturation / stagnation bookkeeping (SCORECARD owes, orchestrator-serialized)
Declared at r101: axis *saturated at R* ⇔ R's verdict for it is `unchanged`; **N=5** consecutive rounds with no
`improved` on any axis → stagnation nudge; count at r101 = 0 (r88-r101 all-improved; N is a conservative fleet
default, not calibrated). r102 bookkeeping: if r102 admits with ≥1 axis `improved` → count stays 0, window
r88-r102; the Saturation section text should be updated to say so ("not saturated at r102") and cite the
export/build-product surface (C1 embed/patch) + open non-headless/platform surfaces as the rationale. Other owed
edits: Round 102 verdict table; `retired:` unchanged; Capabilities — if C1 lands green, additionally register a
capability candidate "self-contained product build + launch (embed_pck path, --main-pack refusal classes,
patch-mode)" with evidence pointer = C1 rows + lesson + mutation receipts (first-working round r102); keep the
existing r101 "headless production export" row untouched. The r101 judge-attribution correction (§1) belongs in
the LOG note when C2 lands (r101 texts are frozen historical records).

## 6. Evidence index (exact commands run by this seat)
- `uptime; date -u; git rev-parse --short HEAD` → outputs in header (§0/preamble).
- python3 json load of `corpus/live/runs/{1904,1915,2002,2021}…` → only 200239/202131 have verdicts; per-arm
  fields printed verbatim (table §1); 190438/191507 dirs hold no verdicts.json [obs].
- `grep -n` for sha tokens in run_battery.py → 542/799/885/1281-1282/1406 comments, 1666 the only runtime pin [obs].
- `ls reports/round-101/mutations/*.patch|*.diff` → 10 simp patches + w6 patch present; simp2 = `.diff` suffix [obs].
- run_battery.py regions cited by line: CASES tail 1600-1702; execute() export branch 1892-1988; meta probe
  4510-4601; timeout driver 5314-5402; gates 4076-4100; timeout constant 1913 [obs].
- r26 record `reports/r26-timeout-executor.md:11-15`; r62 baseline `reports/round-62/r62-baseline.md:77-92` [obs].
- w6 matrix (12 cells) + `reports/round-102/mutations/w6_cases_integrity.patch`; w6 §3 R1-R5 read [obs].

## 7. Labels / unknowns
[obs]: arm fields, line numbers, patch inventory, r26-vs-r101 numbers, w6 cells. [inf]: C2 mechanism arithmetic
(marker time ≈ overhead; alternative "read-and-discard overwrite" considered and rejected as primary because r26
was green under identical driver code). [unk]: E0-spec row topics/evidence bytes and whether E-seats surface
ERROR lines (S5); S-seat folded r95b line count; r102-scout citation re-census numbers; final C2 constants choice.

## 8. Status
COMPLETE. No shared-file edits, no battery runs, no commits by this seat. Handoff: orchestrator owns all splices;
C2 seats (D0-D4/mut4) own the repair proposal + counterfactuals; S-seats own per-hunk C3 application evidence.
