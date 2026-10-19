# r104-crit4 — C4 crit: adopted companions predate the gate (receipt_shape_audit exposure per fixture)

KEY=C4 · round 104 (amended p4, devin fallback) · lane game-dev-2d-shokunin · branch `main` @ `eff29d1d`
HOST: `22:29:45 up 1 day, 22:29, 1 user, load average: 3.77, 2.11, 1.84` (load low; sibling game-dev-3d lane never touched).
Scratch: `/var/tmp/r104-C4/` (never `/tmp` — measured `tmpfs 16G 13G 3.1G 80% /tmp`). `run_battery.py` was **never executed**.
NO COMMITS. Shared files untouched; every deliverable here is shard/mutation content.

## Plan (5 lines)
1. Extract `receipt_shape_flag` / `receipt_shape_audit` + tables from `run_battery.py` by AST (no battery run) into a scratch harness.
2. Census each of the 11 orphaned companions statically (print sites, PASS multiplicity, DIAG/SEQ tokens) and cross-check against the r101 pins in `reports/round-101/r101-E*.md`.
3. Run each companion on HEAD with targeted `godot --headless` under `/var/tmp/r104-C4/`, capture stdout/stderr bytes, and evaluate the real gate over those real bytes with the synthetic CASES row an adoption would register.
4. Classify each flag as gate false-positive (fail-closed on an adoptable receipt) vs declaration the registration owes (grammar entry / anchor multiplicity / expected_errors), and measure the adoption cost against the battery's 8 s row bound.
5. Emit per-fixture exposure + flakiness table, the exact declaration edits, and the adopt/retire routing as mutation content.

## Status
- [x] shard header written (first action)
- [x] gate extracted (AST) — `missing: (none)`, 552 CASES rows, 19 grammar entries
- [x] all 11 companions run on HEAD; s11 arms run (pack/launch/ladder/corrupt/alt_main/early_quit/hang0/all)
- [x] exposure evaluated against the real gate
- [x] stability census complete (6 reps s01/s02, 5 s04/s08, 2 s07) — §5
- [x] declaration mutations + evidence table emitted under `reports/round-104/mutations/`

## Verdict table

| # | finding | class | § |
|---|---|---|---|
| V1 | **5 of 10 runnable companions are RED on HEAD before the gate is even consulted** (s05 parse error, s06 type error, s09 census drift, s10 4× FAIL, s11 default arm `unknown_arm`) | obs | §1 |
| V2 | The in-battery gate **audits PASS rows only** (`if row.get("verdict") != "PASS": continue`) — an adopted companion that FAILs is *silently outside* the shape audit, `audited=0` | obs (function replay) | §2 |
| V3 | A registered companion's **own PASS print sites are not counted** by the in-battery gate: s08's 4-PASS default receipt flags `unaccounted_pass_lines` unless a `RECEIPT_MULTI_PASS_GRAMMAR` entry is declared | obs | §3 |
| V4 | The **standalone** auditor and the in-battery gate disagree on the same bytes: clean s08 default → in-battery `CLEAN`, standalone `foreign_line` (runtime-built absolute path) | obs | §3 |
| V5 | Adoption cost: **s07 exceeds the battery's 8 s row bound** (62.0 s rep1) and **s08 sits at 7.0–7.3 s (≈1.1× margin)**; s01/s02/s04 are 3.0–4.7 s | obs | §4 |
| V6 | **s01/s02/s04/s07 flip verdict between identical runs** (s01 3/6, s02 3/6, s04 5/6, s07 1/2, s08 6/6) | obs | §5 |
| V7 | `PASS\t` / `PASS`-no-space shapes: **0 occurrences** in 39 806 stored lines across 8 runs — C2a's tightening has zero false positives on the stored corpus | obs | §6 |
| V8 | `PASS\t…` is invisible to *both* the in-battery gate and the standalone auditor; `PASS export_prod_s01 forged` is caught by the in-battery gate but only `foreign_line`-caught standalone | obs | §7 |
| V9 | The in-battery gate has **no foreign-line check** outside a DIAG window / SEQ span, and the standalone auditor's `RICH_STRIP` deletes a fixture's own literal when its tag is not a real rich-text tag (s04's `[s04] arm=…` → census prefix `' arm='`) | obs | §7 |

## §1 V1 — HEAD run status of the 11 companions (the adoption gate that binds first)

Command shape (each fixture, one process, scratch project = a byte copy of `corpus/fixtures/` plus the orphan):

```
cd /var/tmp/r104-C4 && TMPDIR=/var/tmp/r104-C4/tmp timeout 180 godot --headless \
  --path /var/tmp/r104-C4/proj --script res://export_prod_sNN.gd   # + " -- --arm=NAME" for s11
```

| fixture | exit | stdout B | stderr B | first blocking line (verbatim) |
|---|---|---|---|---|
| s01 | 0 | 3647 | 0 | — |
| s02 | 0 | 3041 | 0 | — |
| s03 | n/a | — | — | not run: its file has 1 `print(r.text)` and no scenario body (README: "exit=2, no PASS line") |
| s04 | 0 | 418 | 0 | — |
| s05 | **1** | 101 | 340 | `SCRIPT ERROR: Parse Error: Invalid argument for "_emit_pack()" function: argument 2 should be "PackedByteArray" but is "Dictionary".` `at: GDScript::reload (res://export_prod_s05.gd:623)` |
| s06 | **2** | 4764 | 1137 | `SCRIPT ERROR: Trying to assign an array of type "Array" to a variable of type "Array[String]".` `at: _semantics (res://export_prod_s06.gd:370)` |
| s07 | 0 | 2140 | 0 | — (but 62 s, §4) |
| s08 | 0 | 1221 | 0 | — |
| s09 | **2** | 602 | 0 | `ERROR: EXPORT_PROD_S09 ASSERTION FAILED: census mismatch: entries=12, dot_n=3, remap=[39, 45, 49, 97], paths=[…]` — its r101 pin was `entries=13` (`r101-E9.md` §3) |
| s10 | **1** | 3376 | 943 | 4× `FAIL` rows (`FAIL count = file_count=9`, `FAIL log_count = stored_lines=9`, `FAIL uid:sidecar_text =`, `FAIL uid:script_match = uid://1925607530165064467 vs sidecar none`) |
| s11 (default, no `--arm`) | **2** | 153 | 0 | `FAIL export_prod_s11  reasons=unknown_arm evidence=` |

s11's arms, run individually (they are the row shapes an adoption would register):

| arm | exit | stdout B | receipt line (verbatim, PASS) |
|---|---|---|---|
| pack | 0 | 317 | `PASS export_prod_s11 pack magic=GDPC pck_bytes=2008 sha256=bab1a5b8… dircount=7 project_binary_bytes=164 savepack_receipt=true export_rc=0 export_stderr_bytes=0` |
| launch | 0 | 252 | `PASS export_prod_s11 launch rc=0 quit_after=5 frames=5 exit_frames=5 exact_receipt=true ready_lines=1 stderr_bytes=0 export=reused cwd_project_files=0` |
| ladder | 0 | 186 | `PASS export_prod_s11 ladder n1=1 n2=2 n3=3 n4=4 exit_frames_match=true export=reused` |
| corrupt | 0 | 250 | `PASS export_prod_s11 corrupt bad_rc=0 missing_rc=0 bad_error=true missing_error=true bad_receipts=0 missing_receipts=0 exit0_trap=true export=reused` |
| hang0 | 0 | 229 | `PASS export_prod_s11 hang0 rc=124 timeout_bound_s=3 frames_gt0=true exit_receipts=0 quit_after_zero_disables=true export=reused` |
| alt_main | **2** | 176 | `FAIL export_prod_s11 alt_main reasons=pck_project_binary_bytes=0 evidence=` |
| early_quit | **2** | 178 | `FAIL export_prod_s11 early_quit reasons=pck_project_binary_bytes=0 evidence=` |
| all | **2** | 306 | `FAIL export_prod_s11 all reasons=pck_project_binary_bytes=0` ×6 |

`alt_main`/`early_quit` fail on the M5/M4 glitch class (`project.binary` 0 bytes) that `r101-E9.md` §2 M5 documented as a *known intermittent*; the fixture's own `pack` arm guards it (`project_binary_bytes=164`) but the variant arms do not retry.

**Consequence for C3b:** "adopt-with-fresh-pins" is decidable from evidence for exactly **s01, s02, s04, s07, s08** (5 fixtures), and for **5 of s11's 8 arms**. The remaining fixtures are red on HEAD for reasons that have nothing to do with the receipt gate; adopting them would require repair work the README does not authorize ("Do not register them in CASES without fresh measured pins"). **This list is the *first* stage only** — §5 then removes s01/s02/s07 from it on verdict stability and leaves **s04 and s08** as the fixtures a pin can actually be written against.

## §2 V2 — the gate audits PASS rows only: a FAILed adoption is unaudited

`receipt_shape_audit` (extracted verbatim, `run_battery.py:1998-2019`):

```python
for row in rows:
    if row.get("verdict") != "PASS":
        continue
```

Replayed with the real s10 bytes (55 lines, 4× `FAIL`, exit 1) and its adoption-shaped signature:

```
verdict=FAIL  audit: {'audited': 0, 'flags': [19 × dead_shape_allowlist_entry]}
verdict=FAIL  flag : ['anchor_line_multiplicity']          # direct call, bypassing the filter
verdict=PASS  audit: audited=1, flags=[anchor_line_multiplicity observed=0 declared=1, …]
```

Two readings, both true: (a) a FAIL row contributes **no** shape audit (`audited` stays 0); (b) if the same bytes are mislabelled PASS the gate does fire. The r103 lesson already bounds the gate as "audits stored receipts", and the r103 F5 comment deliberately skips non-CASES rows — so this is not a defect claim, it is an **adoption precondition**: *a companion's shape claim is only non-vacuous once its row PASSes*. C3b's disposition table must therefore carry the row verdict as a precondition, not as a postscript. The dead-entry floor does **not** catch it: presence is computed over all rows, so a FAIL row suppresses `dead_shape_allowlist_entry`.

## §3 V3/V4 — declaration debt vs gate false positive, separated by measurement

Four-step replay, real s08 default bytes (1221 B, 14 lines, 4 PASS), synthetic CASES row spliced into the extracted gate:

```
UNREGISTERED  -> []                              # case not in CASES_SIG_BY_CASE: gate is blind
REGISTERED    -> [{'why': 'unaccounted_pass_lines', 'observed': 4, 'declared': 1}]
GRAMMAR-DECL  -> []                              # after RECEIPT_MULTI_PASS_GRAMMAR[name] = the 4 observed (verb,token) pairs
ECHO-CONTROL  -> [{'why': 'anchor_line_multiplicity', 'observed': 2, 'declared': 1}]
```

- The **unregistered → blind** step is the adoption trigger: while a companion lives outside `CASES`, `receipt_shape_flag` returns `[]` at the `case not in CASES_SIG_BY_CASE` early return — the r103 gate protects nothing about it.
- The **registered → flag** step is *declaration debt*, not a false positive: the fixture prints 4 PASS lines (`control_exe`, `missing_exe`, `missing_pack`, `done`) and the gate's non-grammar branch declares exactly 1. Declaring the observed 4-tuple silences it. **Registration must land the grammar entry in the same commit.**
- The **echo control** shows the residual hazard: appending a line that merely *echoes* the pin (`S08 child: PASS export_prod_s08 control_exe …`) trips `anchor_line_multiplicity` 2≠1. `run_battery.py` has such echo sites (e.g. `"PASS " not in candidate_output` over a child's output), so an adopted row whose harness echoes a child receipt needs `RECEIPT_ANCHOR_MULTIPLICITY` declared with the echo count.

Standalone-vs-in-battery divergence on the **same** s08 bytes:

```
standalone s08 whole-default: ['foreign_line']    # /home/vgpnk/.local/share/godot/app_userdata/MechanicOneShotTest/r101e8-NNNNNNN/xdg-empty-exe/…/linux_debug.x86_64
```

The line is a **runtime-built absolute path** (varies per run: `r101e8-2180194` vs `r101e8-2243949`), so `script_account`'s literal-prefix census cannot cover it — 2 such lines per run. In-battery the gate is silent here only because those lines sit *after* a PASS line and the gate never enters the foreign-line path (it has no foreign-line check for non-DIAG rows; only the DIAG-window and SEQ-span closures do). **Routing: if C3b adopts s08, the row is clean in-battery but the standalone auditor flags it — the two must be reconciled in the same commit (either a declared non-DIAG account or a fixture change that stops printing the template path).**

## §4 V5 — adoption cost against the battery's 8 s row bound

`run_battery.py:2231` — `timeout_seconds = 60 if script.startswith("__godot_export") else 8`. Orphans are ordinary `.gd` rows ⇒ **8 s**.

| fixture | wall, all reps (s) | min margin to 8 s |
|---|---|---|
| s01 | 3.1, 3.7, 3.9, 3.8, 3.1, 3.1 | 2.2× |
| s02 | 3.0, 3.0, 3.1, 3.1, 3.1, 3.1 | 2.7× |
| s04 | 4.6, 4.7, 4.5, 4.8, 5.0 | 1.7× |
| s07 | **62.0**, 7.1 | **0.13×** |
| s08 | 7.3, 7.0, 7.1, 7.3, 7.0 | **1.1×** |

Six reps for s01/s02, five for s04/s08, two for s07.

s07's 62 s rep is the `empty_name` arm, which is *designed* to be timeout-bound (`rc=124`, `ms=40026` — two 40 s bounded launches); any adopted s07 row must be an arm that excludes `empty_name`, or it TIMEOUTs the battery. s08's 7.0–7.3 s is a **cold-project** export comparing a 73 519 416-byte template against the produced executable — 0.7–1.0 s of headroom on a quiet host, and this round measured loadavg 3.8. Both numbers are inside the "cost census" the C3 critique asked for.

## §5 V6 — flakiness: identical commands, flipping verdicts

| fixture | rep1 | rep2 | rep3 | rep4 | rep5 | rep6 | blocker verbatim (first red rep) |
|---|---|---|---|---|---|---|---|
| s01 | **rc=2** | rc=0 | rc=0 | rc=0 | **rc=2** | **rc=2** | `ERROR: EXPORT_PROD_S01 ASSERTION FAILED: R7a declared census mismatch matched=12/14 extras=1` |
| s02 | **rc=2** | rc=0 | rc=0 | **rc=2** | rc=0 | **rc=2** | `EXPORT_PROD_S02 FAIL zip_empty path=/var/tmp/r101-export-prod-s02/2059112-809/out/prod.zip` |
| s04 | **rc=2** | rc=0 | rc=0 | rc=0 | rc=0 | rc=0 | stderr `ERROR: export_prod_s04 --main-pack swapped pack exited rc=1 (want 0)` |
| s07 | rc=0 (62 s) | **rc=2** | — | — | — | — | rep2: `s07 ASSERTION FAILED: known_path rc=1 expected 0; … empty_name rc=0 expected timeout-bound 124; …` |
| s08 | rc=0 | rc=0 | rc=0 | rc=0 | rc=0 | rc=0 | — (6/6 green; bytes differ only in the `r101e8-NNNNNNN` run-id) |

Totals: **s01 3/6, s02 3/6, s04 5/6, s07 1/2, s08 6/6.** Only s08 has a stable verdict across every rep; s01 and s02 fail half the time.

Byte-level stability is a *different* axis from verdict stability, and it separates the two survivors cleanly (all values from `r104-crit4-evidence.json`):

| fixture | reps | bytes/lines | sha256 | reading |
|---|---|---|---|---|
| s08 | 5 | 1221 B / 14 L, PASS=4 in **all 5** | 5 distinct | verdict + shape stable; the sha moves only with the embedded `r101e8-NNNNNNN` run-id |
| s04 | 4 | 418 B / 5 L, PASS=1 in **all 4** | 4 distinct | verdict + shape stable, same run-id caveat |
| s01 | 4 green/red mix | 3647/3647/4025/**1721**/1359 B | all distinct | shape *not* stable: the green reps themselves differ in line count |
| s02 | 2 green | 3041/3041 B, 21 L | distinct | shape stable in the greens, verdict is not |

So **s04 and s08 are the only two fixtures whose receipt shape is reproducible**, and s08 is the only one that is reproducible in both axes. That is the concrete answer to "adopt-with-fresh-pins or retire": *pin s04/s08 (s08 with its grammar declaration), and do not pin s01/s02/s07 until they have a shape census, not just a verdict census.*

Run-to-run drift is also visible *inside* a green rep: `r3_s01.out` is 54 lines, `r4_s01.out` is 65 — the same command produced 11 extra `MUT`/`ROW` lines in rep4 (both green). So the byte-level pin on an adopted s01 row is not yet justified even where the verdict holds.

Same fixture, same command, same host, minutes apart ⇒ **no single-run pin is a stable pin**. r101-E9 already named this class for the export lattice (`M4`: "Never treat a first-export-after-edit pack as reproducible"); this table generalises it to the *row verdict*, which is what C3b's "fresh measured pins" language would otherwise freeze. **Routing: an adopted companion needs an N≥3 stability census, not one green run**, and s01/s02/s04/s07 do not currently have one.

## §6 V7 — PASS-prefix census (feeds C2a, zero false positives measured)

The r103-routed C2a tightening (extend the pass-line census from `PASS\t` to all PASS-prefixed lines) measured over every stored receipt:

```
8 runs / 39806 output lines / PASS-prefix=4548 / PASS-tab=0 / PASS-no-space=0
```

Per-capture cross-check on this seat's own bytes: 9 captures, PASS-prefix == `PASS `-count in all 9, tab=0 in all 9. **So C2a's tightening is free on today's corpus** — it cannot introduce a false flag on any stored line; its value is entirely forward-looking (catching a future `PASS\t` fabrication). Evidence for the C2 seat's false-positive analysis, not a substitute for it.

## §7 V8 — evasion shapes vs both gates (real s01 bytes as carrier)

| injected line | in-battery `receipt_shape_flag` | standalone auditor (`cen/` with the orphan staged) |
|---|---|---|
| clean | CLEAN | CLEAN |
| `PASS\texport_prod_s01 forged` | **CLEAN** | **CLEAN** |
| `PASS export_prod_s01 forged` | `unaccounted_pass_lines` | `unaccounted_pass_line` |
| `PASSexport_prod_s01 forged` | **CLEAN** | `unaccounted_pass_line` |
| `totally foreign line here` | **CLEAN** | `foreign_line` |

With the orphan **not** staged in the census dir, the standalone auditor additionally emits `foreign_line` on the clean receipt (its census cannot see the fixture) — so a C3b adoption must stage the fixture where the auditor's `build_census` looks, or every adopted row reads as foreign. Two gate layers, two different blind spots; neither subsumes the other.

**A third finding on the same line — the census rule's own blind spot (measured, `cen/` with the orphan staged):** two adoption-shaped receipts still read `foreign_line` standalone while being **CLEAN** in-battery:

| fixture | line the standalone auditor calls foreign | why the census misses it |
|---|---|---|
| s04 | `[s04] arm=swap pck_bytes=3440 pck_sha256=4335382081e3…` | the fixture's print literal is `"[s04] arm=%s pck_bytes=%d pck_sha256=%s"`; `RICH_STRIP` strips `[s04]` as a rich-text tag, leaving the census prefix `' arm='` — which does **not** match a line starting `[s04]` |
| s08 | `/home/vgpnk/.local/share/godot/app_userdata/…/r101e8-2353872/xdg-empty-exe/…/export_templates/4.7.2.stable/linux_debug.x86_64` | runtime-built absolute path (run-id varies per run) — no literal prefix can cover it |

The `RICH_STRIP` mechanism is deliberate and correct for real `print_rich` output, but it means **any fixture whose tag is not a rich-text tag loses its own literal** from the census. `reports/round-103/mutations/r103-receipt-shape-gate.py:78` (`RICH_STRIP.sub`) is the site. Both classes are invisible in-battery only because the gate has no foreign-line check outside a DIAG window or SEQ span — so a companion adopted into the `export_prod_*` family (no `*_DIAG` token) inherits *no* foreign-line coverage at all. Routing: **C3b adoption must decide per fixture whether the row needs a DIAG-shaped receipt** (which would arm the window closure) **or an explicit non-DIAG account**, and must not treat in-battery CLEAN as proof of shape-accounted bytes.

## Per-fixture exposure table (adoption lens)

| fixture | HEAD verdict | in-battery flags on registration | declaration owed | adoption verdict |
|---|---|---|---|---|
| s01 | PASS 3/6 reps (rep1, rep5, rep6 red) | none | none (1 PASS line, pin unique) | **NOT ADOPTABLE YET** — verdict flips; also 54→65 lines between green reps |
| s02 | PASS 3/6 reps (rep1, rep4, rep6 red) | none | none | **NOT ADOPTABLE YET** — verdict flips (`zip_empty`) |
| s04 | PASS 5/6 reps (rep1 red) | none | none | **ADOPT-CANDIDATE** — flaked once before stabilising; needs a longer census |
| s07 | PASS 1/2 reps (62 s / 7.1 s) | none | none, but arm must exclude `empty_name` | **NOT ADOPTABLE YET** — 7.8× over bound on default arm and verdict flips |
| s08 | PASS 6/6 reps (7.0–7.3 s) | `unaccounted_pass_lines` | `RECEIPT_MULTI_PASS_GRAMMAR` 4-tuple | **ADOPT-CANDIDATE** — only companion with a stable verdict; 1.1× bound, standalone `foreign_line` unreconciled |
| s11 pack/launch/ladder/corrupt/hang0 | PASS | none | none | **ADOPT-CANDIDATE** (5 rows, each 1 PASS line, 186–317 B) |
| s11 alt_main/early_quit/all | FAIL | n/a (unaudited) | — | **RETIRE-or-REPAIR** (`pck_project_binary_bytes=0`) |
| s05 | FAIL (parse) | `anchor_line_multiplicity` if registered | — | **RETIRE** (does not load) |
| s06 | FAIL (type err) | none | — | **RETIRE** (does not complete) |
| s09 | FAIL (census drift) | `anchor_line_multiplicity` if registered | — | **REPAIR-THEN-ADOPT** (re-pin `entries=12`, then re-measure) |
| s10 | FAIL (4×) | `anchor_line_multiplicity` if registered | — | **RETIRE** (scenario superseded by `export_prod_icon_uid_census`) |
| s03 | n/a | — | — | **RETIRE** (no scenario body; r101 README agrees) |

**Bottom line for C3b:** of 11 companions, **2 retire outright** (s03 no body, s05 parse error), **2 more retire on scenario supersession** (s06, s10), **1 repairs then adopts** (s09), **1 needs repair or arm-scoping** (s11's three variant arms), and **4 pass the HEAD-verdict stage** (s01, s02, s04, s08). Applying the second stage (verdict/shape stability, §5) removes s01 and s02, and s07 was never in the set on its default arm — leaving **s04 and s08 as the only two fixtures a fresh pin can be written against**, with **s08 the only one stable on both axes** and the one that owes a grammar declaration.

## Reproduction one-liners (read-only; no battery, no commits)

```
python3 /var/tmp/r104-C4/extract_gate.py corpus/fixtures/run_battery.py /var/tmp/r104-C4/gate.py   # missing: (none)
cd /var/tmp/r104-C4 && ./run_all.sh          # per-fixture HEAD captures
cd /var/tmp/r104-C4 && ./run_s11.sh && ./run_s11b.sh
python3 /var/tmp/r104-C4/exposure2.py /var/tmp/r104-C4 /var/tmp/r104-C4 /var/tmp/r104-C4/exposure2.json
python3 reports/round-104/mutations/r104-crit4-registration.py --check    # 10 adoptable rows, s08 flagged pre-declaration
python3 reports/round-104/mutations/r104-crit4-evidence.py /var/tmp/r104-C4 \
        reports/round-104/mutations/r104-crit4-evidence.json              # 37 captures, sha256 + flags
bash /var/tmp/r104-C4/reconstruct.sh      # rebuild the scratch harness from the repo, if /var/tmp was cleared
```

Deliverables in the repo (all additive, no shared file touched):

- `reports/round-104/r104-crit4.md` — this shard.
- `reports/round-104/mutations/r104-crit4-registration.py` — the registration-debt mutations + `--check` replay against the extracted gate.
- `reports/round-104/mutations/r104-crit4-evidence.py` — the evidence-table generator.
- `reports/round-104/mutations/r104-crit4-evidence.json` — 37 captures with sha256, byte/line counts, PASS-prefix census, standalone flags.

Scratch harness (outside the repo, not committed): `/var/tmp/r104-C4/{extract_gate.py,gate.py,auditor.py,exposure2.py,reconstruct.sh,run_all.sh,run_s11.sh,run_s11b.sh,rep3.sh,rep56.sh,proj/,cen/,tmp/,*.out,*.err}`. No git worktree was created by this seat (`git worktree list` shows only the pre-existing r98/r99/r100 worktrees, none from r104-C4), so nothing needs removing.

## Routed to the orchestrator (not this seat's to land)

1. **C3b disposition must be two-stage**: (a) HEAD verdict (this shard §1), then (b) gate exposure (§3). A companion that is red at (a) cannot be adopted with pins alone.
2. **Registration is atomic**: the CASES row, its `RECEIPT_MULTI_PASS_GRAMMAR` entry (s08), and its `expected_errors` entry land in one commit, per the r103 V1 ordering law.
3. **s07's default arm blows the 8 s bound**; register arm-scoped rows only.
4. **Stability census N≥6 before pinning** — s01/s02 fail half of six identical runs; one green run is not evidence.
5. **Reconcile the two gate layers** for any adopted row that prints a runtime-built path (s08) or whose census literal is rich-text-stripped (s04).
6. **C2a is free**: 0 `PASS\t` / `PASS`-no-space lines in 39 806 stored lines — the tightening cannot false-positive on today's corpus.

## Open / unknown

- `s03` was not executed (its file has no scenario body; r101 README already records `exit=2, no PASS line`).
- Whether the s01/s02/s04 red reps are host-load artifacts or genuine fixture defects is **not decidable from this seat's evidence** — they need a load-matched N-run census with the loadavg recorded per rep (this seat recorded loadavg once, at session start).
- `alt_main`/`early_quit`'s `project.binary` glitch is the r101-E9 M5 class; whether a retry loop (as in s09) would stabilise them is untested here.
- The s11 `--arm=all` row's 6× `pck_project_binary_bytes=0` was not traced to a single mechanism.
