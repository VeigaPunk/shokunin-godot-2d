# r101-crit6 — Floor-gate / dead-entry census audit (seat CRIT-6)

Audited revision: `corpus/fixtures/run_battery.py` sha256 `c4db6153…b40076`,
git HEAD `05a72899` (untracked at audit time: `corpus/fixtures/r101_seqfull.gd`,
`corpus/fixtures/r101_ytrans.gd`, `reports/round-101/`). I never ran
`run_battery.py` (hard rule); every observation below is either a targeted
`godot --headless` run of my own or a read-only analysis of the source.
Scratch root: `/var/tmp/r101-crit6/` (E7's shard reported `/tmp` EDQUOT at
16:21; a 16:27 re-test of `/tmp` showed `tmp_write=OK`, but I kept `/var/tmp`
for the runs — deviation from the `/tmp` wording, no system paths touched).
Templates used in my probes are the installed `4.7.2.stable` ones; the
missing-templates probe isolates them via `XDG_DATA_HOME`, not by editing
`~/.local/share`.

Load context (uptime @ start, recorded once):
`16:21:26 up 1 day, 16:21, 1 user, load average: 41.13, 21.77, 13.87`
(host shared with the 3D lane r104 swarm — slowness expected, no retries).

## 0. Verdict

* The census **kernel** is generic and stays live for any CASES-registered
  row carrying `expected_errors` — no per-family work needed for that half.
* The **floor protection** is *not* generic: it is 15 hardcoded
  per-round prefix gates. The r101 families are not in CASES yet, so today
  they are covered by nothing; §5 carries the exact integration deltas.
* Both new refusal classes (unknown preset, missing templates) are measured
  byte-exact (§4.1–4.2) and are expressible as one/two `expected_errors`
  exact-line entries.
* The **existing** export refusal row has two defects of this round's exact
  class (§4.3): its CASES signature string appears in neither stream of the
  real run, and its `expected_errors` dict key is statically unreachable —
  the row is invisible to the census and to every gate.

## 1. What the r87 floor-gate law requires (and how the machinery works)

Law source: `reports/round-87/r87-critic.md` §F3 (lines 103–129) — r79-C2
had established "`expected_errors` was ceiling-not-floor — a dead allowlist
entry (never matched a real emitted line) passed silently"; F3 extends the
all-matched floor to each new round's prefixes because the gate filters on
hardcoded `startswith(...)` prefixes and a new row name outside them is
unprotected. The r95 precedent `corpus/live/r95-scribe/audit/floor_gate.json`
(synthetic `dead_non_r95_entry: true` = the hole, `dead_r95_entry: false` =
caught) is the lane's own proof of this wiring.

Census mechanics (all line refs are the audited sha):
* `run_battery.py:3663–3707` builds `census_rows` from **every** result with
  a non-empty `expected_errors` and a list `output`; per entry computes
  `matched_lines` / `dead_in_run`; `dead_entries` is data only.
* Self-validation by the real classifier: `census_covers_all_allowlisted_rows`
  (3858), `census_bare_classifier_consistent` (3862),
  `census_allowlisted_reproduces_verdicts` (3865). These make a **dead entry
  whose row also FAILs** loud (that is how the committed r95 run's
  `dead_entry_count=2` surfaced: both entries `negative_transition`, the row
  itself flaked FAIL — `r95-reviewer` lines 176–177). The **silent** class is
  a dead entry on a row that still PASSes — closed only by the per-round
  `*_expected_errors_all_matched` gates.
* Gates: 15 blocks at 3877–4014, each `all(not e["dead_in_run"] for r in
  census_rows if r["case"].startswith(<hardcoded prefixes>) …)`; plus
  `cases_integrity` (4022–4027) = CASES uniqueness + non-empty-existence for
  8 prefixes (r100-critic F1's drop/dup/rename gate).
* `dead_entry_count` itself is **never gated** (dict field at 3731; comment
  3856–3857: "dead entries themselves are data, not a failure").
* Placement: the census is inline in `main()` after the CASES loop (2303)
  and before opt-in probes (first opt-in append after 4039; scope string
  3726–3728). **Rows appended after it are invisible.** Families must land as
  CASES rows (or pre-census probes) to be censused at all.
* Row-level entry rule: `classify_process` (1739–1742) rejects any
  `ERROR:`-containing line not covered by an allowlist entry — so any r101
  harness whose capture echoes refusal bytes **must** carry matching
  `expected_errors` entries, which is exactly what pulls it into the census.

## 2. Measured gate inventory (audited revision)

Checker: `reports/round-101/mutations/crit6_floor_gate_coverage.py`
(static AST/regex; never executes run_battery). Full output saved to
`reports/round-101/mutations/crit6_audit_output.txt`. Command:
`python3 reports/round-101/mutations/crit6_floor_gate_coverage.py --plan-prefix export_prod_ --plan-prefix r101_ytrans_ --plan-prefix r101_seqfull_`
→ exit 1 (planned entry-bearing families currently uncovered).

Summary from that run: CASES 509 rows, 509 unique, 0 duplicates; 82
entry-bearing cases; 15 gates, all non-dangling, covering 39 entry-bearing
cases; **43 entry-bearing CASES rows are outside every gate** (legacy
pre-gate rows: slider_adjust_*, camera_*, ui/button/checkbox/audio/tween,
negative_*, save_*, contact_no_collision, animation_stuck,
crash_spontaneous_sigabrt, export_preset_missing, health_gauge_disconnected).
`cases_integrity` existence prefixes: `stree_lattice_, r98_canvas_, r98b_,
r98c_, r99_audio_, r99b_, r100_gui_, r100b_` — all non-empty. The 43 orphans
are the standing silent-class surface (their entries die silently if the row
still passes); that is the same shape r87-F3 fixed for that round's rows, not
a new defect by itself, but it means **the r101 families get floor coverage
only if the deltas in §5 are applied**.

## 3. Per-family status at audit time

* **export_prod lattice (E1–E11, C1)** — no `export_prod*.gd` row exists yet
  in CASES (fixtures not landed at audit time). Contract requirements for the
  landing: (a) register rows in CASES *before* the census point; (b) give
  them a prefix that a gate covers — today that means the §5 new gate unless
  they are named into an existing gate's prefix (recommend NOT: r100 gate is
  about r100 semantics); (c) if a row's capture contains `ERROR:` bytes, it
  needs exact entries or the row itself FAILs (§1 row-level rule); (d) new
  prefixes go into `cases_integrity`'s existence tuple, else a dropped or
  renamed family is invisible (r100-critic F1 class).
* **seqfull full-replay pins (C2 / D-seats / E12)** — `corpus/fixtures/
  r101_seqfull.gd` exists untracked; it prints `PASS r100_gui <cell> …`
  receipt lines and `SEQ_BEGIN/SEQ_CENSUS/SEQ_END digest=` lines; it never
  prints `ERROR:` itself (grep 0 hits). The render cell's engine stderr class
  is real and captured: `corpus/live/r101-ver11/receipts/seq_base_clean0.err`
  (296 B) = `ERROR: Parameter "t" is null.` + backtrace `[0] _cell_render
  (res://r100b_seq.gd:762)`. So any battery row replaying render keeps
  needing the `ERROR: Parameter "t" is null.` entry (already present for
  `r100_gui_render`, `r100b_seq_clean`, `r100b_seq_noclean`). If new rows are
  named `r100b_*` the r100 gate covers them; if `r101_*` they need the §5
  gate. I did not execute the new fixture; the receipts cited are the
  ver11 seat's.
* **ytrans (C3 / E17)** — `corpus/fixtures/r101_ytrans.gd` exists untracked;
  prints `PASS r101_ytrans <arm> …`; `ERROR:` 0 hits; `corpus/live/
  r101-ver17/receipts/*.err` = 0 B. Likely entry-free rows → any gate is
  vacuous for them, but `cases_integrity` existence is still the needed pin.
  Dead-flag confirmation, for the record: `offy` = 0 hits in
  `corpus/fixtures/r95b_order.gd`; the ver11 receipt `offy_1000.out` (1078 B)
  shows `--offy=1000` accepted with the PASS line `off=0.0000` byte-shaped
  like the x0 row (`stdout_sha 36af4675…`), i.e. the flag is dead and the
  replacement measurement is E17's file. The r95 gate already covers the
  `r95b_order_`/`dss_lattice_` prefixes if any new row lands there.
* **r100b seq rows stay covered** — census output: r100 gate matches 25 rows,
  entry_bearing 3 (`r100_gui_render`, `r100b_seq_clean`, `r100b_seq_noclean`).
  C2/D's pin-shape change (1-line → full-transcript signature) does not touch
  the allowlist wiring; keep the entries.

## 4. Measured refusal classes + existing export-row defects

Scratch project = byte-copy of `corpus/fixtures/{project.godot,
export_presets.cfg}` (same project shape the battery's `__godot_export__`
path builds), at `/var/tmp/r101-crit6/proj`.

### 4.1 Unknown-preset refusal (E7's class), measured

Command (mirrors the battery's `--export-debug` form):
`godot --headless --path /var/tmp/r101-crit6/proj --export-debug "NoSuchPreset" /var/tmp/r101-crit6/proj/out/fixture.x86_64`
Observed: `exit=1`; stdout 747 B (progress + `[ DONE ] first_scan_filesystem`);
stderr 196 B, first line exactly
`ERROR: Invalid export preset name: NoSuchPreset.`, then
`The following presets were detected in this project's `export_presets.cfg`:
"Linux/X11"` and `   at: _fs_changed (editor/editor_node.cpp:1417)`.
Entry string for preset name `N`: `ERROR: Invalid export preset name: N.`
(one entry; the trailing lines carry no `ERROR:` token).

### 4.2 Missing-templates refusal (E8's class), measured — XDG-isolated

Command: `XDG_DATA_HOME=/var/tmp/r101-crit6/xdg-empty godot --headless
--path /var/tmp/r101-crit6/proj --export-debug "Linux/X11" /var/tmp/r101-crit6/proj/out/fixture.x86_64`
Observed: `exit=1`; stdout 747 B (same shape); stderr **500 B**:
`ERROR: Cannot export project with preset "Linux/X11" due to configuration errors:`
`No export template found at the expected path:`
`/var/tmp/r101-crit6/xdg-empty/godot/export_templates/4.7.2.stable/linux_debug.x86_64`
(the same line again for `linux_release.x86_64`)
`   at: _fs_changed (editor/editor_node.cpp:1401)`
`ERROR: Project export for preset "Linux/X11" failed.`
`   at: _fs_changed (editor/editor_node.cpp:1417)`
Out dir empty. The `--export-release` variant is byte-identical (500 B — both
template paths are listed either way). Entries needed: **two exact lines**
(the two `ERROR:`-carrying lines; the `No export template found…` lines carry
no token). Isolated system templates confirmed present before the run
(`ls ~/.local/share/godot/export_templates/4.7.2.stable/` → linux_debug/
linux_release x86_64, android, icudt…), so the failure is attributable to the
XDG redirect, not a broken install.

### 4.3 Existing export refusal row — two defects of this round's class

`export_preset_missing` (CASES line 59) is special-cased: `execute()` takes
the `__godot_export_missing__` branch (1846–1855, 1908–1928), classifies
inline with its own `evidence` (1909) and `passed = classify_export(output)`
(1913).

1. **Stale CASES signature.** The CASES tuple's evidence is
   `"No export preset 'Missing preset' found"` (line 59). Running the exact
   condition (`--export-debug "Missing preset"`, measured): stderr 198 B,
   first line `ERROR: Invalid export preset name: Missing preset.`; the CASES
   string occurs **0 times** in either stream. `record["signature"]` (2293)
   therefore stores a string never asserted against output; the row passes
   only because the inline classifier uses a different, real string.
2. **Unreachable `expected_errors` key.** `export_preset_missing` is a key in
   the `expected_errors` dict (2011), but that dict is consulted only under
   `if passed is None:` (1970), and this branch sets `passed` first → the key
   is statically unread; `record["expected_errors"]` = `[]` (2296) → the row
   is absent from `census_rows` and from every gate. The harness documents
   this as `allowlists_outside_expected_errors[0]` (3741) — no dead-entry
   protection exists for the lane's only prior export-refusal row.
   Recommendation for E7/E8: do **not** clone this shape. Either use the
   standard path (CASES evidence that really appears in output + entries in
   the dict, i.e. leave `passed = None`), or keep inline and add the row to
   `allowlists_outside_expected_errors` while accepting no floor protection.
   (Note the inline shape is still verdict-correct today: evidence == required
   signature, so message drift FAILs the row — the defect is the missing
   census/gate coverage and the misleading stored signature.)

## 5. Proposed integration deltas (orchestrator owns run_battery.py)

1. New floor gate, after the r100 block (~4014). Fill the prefix tuple with
   the actually landed r101 row names (see §6 checker):

```python
        # r101 author/crit6: the r101 families (export lattice rows, seqfull
        # receipts, ytrans) land in CASES ahead of this census — same
        # named-by-round / covers-round-prefixes shape as r87-r100, so a dead
        # r101 allowlist entry cannot pass silently either; the prefix list
        # must cover every r101 row name (verified by
        # reports/round-101/mutations/crit6_floor_gate_coverage.py).
        "r101_expected_errors_all_matched": all(
            not e["dead_in_run"]
            for r in census_rows
            if r["case"].startswith(("export_prod_", "r101_"))
            for e in r["entries"]),
```

2. `cases_integrity` (4024–4027): append the same new prefixes to the
   existence tuple so a dropped/renamed r101 family is caught.

```python
                for p in ("stree_lattice_", "r98_canvas_", "r98b_", "r98c_",
                          "r99_audio_", "r99b_", "r100_gui_", "r100b_",
                          "export_prod_", "r101_")):
```

3. Keep `allowlists_outside_expected_errors` (3740–3744) accurate: if the
   E7/E8 lanes keep inline classifiers, add their row names there; if the new
   export rows carry entries, nothing to add.

4. Optional, stronger (orchestrator decision, not required by the r87 shape):
   gate `surface_census["dead_entry_count"] == 0`. It would cover all 82
   entry-bearing rows (including the 43 legacy orphans), but it converts
   every tolerated-not-required entry into a hard pin and inherits any
   load-bimodality of flake-prone rows (r95's `negative_transition` flake
   produced dead entries *with* a FAIL row; a flake that still PASSes would
   now fail the meta). The per-round gate above matches the established
   precedent; the global form is the maximal-coverage alternative.

## 6. Re-runnable checker (reports/round-101/mutations/)

`crit6_floor_gate_coverage.py` — parses run_battery.py with `ast`/regex
(never imports/executes it). Usage from the repo root:

```
python3 reports/round-101/mutations/crit6_floor_gate_coverage.py \
    --plan-prefix <new_prefix> [--plan-prefix <more>...]
```

Exit 0 = no orphan entry-bearing row, no dangling gate prefix, no planned
entry-bearing prefix without a gate; exit 1 otherwise. Run it **after** the
r101 rows land: it reports per-gate row/entry counts (vacuity), the orphan
list, `cases_integrity` prefix row counts, and whether each planned family is
covered. It proves static wiring only — verdict-level facts (census PASS,
today's `dead_entry_count`, whether every entry actually fires) require the
battery run, which only the orchestrator may execute.

## 7. Not verified here / open items

* No battery run (hard rule): the r101 rows' actual verdicts, the census
  `dead_entry_count` after landing, and gate PASS are integration-time facts.
* r101 row names for the export lattice and for D-seats' seqfull registration
  are not yet fixed; §5's prefix tuples must be reconciled with them (checker
  makes the reconciliation mechanical).
* E-side fixtures (`r101_seqfull.gd`, `r101_ytrans.gd`) were not executed by
  me; receipt dirs `corpus/live/r101-ver11|ver17` are those seats' evidence.
* Observed anomaly in `corpus/live/r101-ver11/receipts/manifest.txt`: their
  script reports `bc: command not found` on every line (timing fields empty);
  no verdict impact in the receipts, but worth a fix by that seat.
* `/tmp` EDQUOT reported by E7 at 16:21 was not reproducible at 16:27
  (`tmp_write=OK`); load-dependent host condition, recorded as such.
