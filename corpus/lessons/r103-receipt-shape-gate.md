# Round 103 — receipt-shape meta-gate for stored verdict records (offline auditor)

**Scope.** `run_battery.py` classifies a row with `signature in "\n".join(output)` plus exit/error
arithmetic (`run_battery.py:1792-1807`); the stored record keeps the merged output verbatim.
Nothing re-checks the record's shape after the run, so the r98/r99/r100-critic F1 family — a duplicate,
dropped or renamed row, a record carrying unaccounted PASS lines or foreign output lines — is invisible
to every gate family *at the record layer*. r102-mut9 measured the extreme: an E1/E2-shaped receipt
accepts foreign stdout lines injected in-span/post-span/pre-span, byte-identical in its pinned region.

**What this gate is.** `reports/round-103/mutations/r103-receipt-shape-gate.py` — a standalone offline
auditor over stored `verdicts.json` payloads. It never imports or edits `run_battery.py` and it makes
no classifier change (`git diff --stat -- corpus/fixtures/run_battery.py` empty at land time).

```
python3 reports/round-103/mutations/r103-receipt-shape-gate.py [-o out.json] <verdicts.json>...
python3 reports/round-103/mutations/r103-receipt-shape-gate.py --census <verdicts.json>...   # W2 account
python3 reports/round-103/mutations/r103-receipt-shape-adversary.py                            # G2/G4 matrix
```

**Flag classes** (fail-closed: malformed/missing evidence flags, never passes):

| flag | meaning | FC |
|---|---|---|
| `schema:{case,script,verdict,signature,output,record}` | missing/ill-typed field on a process-bearing row (non-process probe rows exempt) | ✓ |
| `output_unreplayable` | row has a `command` but no `output` list | ✓ |
| `exit_or_error_state` | `verdict=PASS` while `actual_exit != expected_exit` or `error` set | ✓ |
| `signature_absent` | no signature alternative contained in the merged output (skipped for synthetic `EXPORT PASS …` rows) | |
| `artifact_binding` | `executable_bytes=<n>` in signature ≠ `export_artifact.artifact_bytes` | ✓ |
| `banner_shape` | engine banner not exactly once at line 0 | |
| `foreign_line` | non-PASS line matched by neither the row script's literal census nor the engine-diag regex | |
| `unaccounted_pass_line` | PASS line not covered by the matched signature prefix, the w4 multi-PASS allowlist, or the script's own PASS print sites | |
| `pass_multiplicity` | `#PASS lines > max(#signature PASS lines, allowlist count, #script PASS sites)` | |

**Record semantics the gate had to learn (measured, live corpus 2026-10-18):**
- `signature` is a **prefix-substring pin**, not a full line: `PASS first=true` pins
  `PASS first=true second=false consumed=true`.
- `signature` may be a **list of alternatives** (bimodal rows, e.g. `input_lattice_pre_frame`,
  CASES row `run_battery.py:338`); require ≥1 alternative contained.
- Export rows: the signature is **synthetic** (`EXPORT PASS preset=Linux/X11 executable_bytes=<size>`)
  and never appears in the process output — bind it to `export_artifact.artifact_bytes` instead.
- 16/554 live rows are battery-internal probes: no `command`, no `output`, no `script`.
- Row sentinels: `__save_process_{missing,writer,reader}__` → the real script `save_process.gd`.
- Negative rows may pin an ERROR line while the fixture still prints an unpinned `PASS …` line
  (`save_process_missing`); PASS print-site accounting covers it.

**The W2 diag-reg-ex account.** Line accounting is per row: (T1a) the row script's print-family
literals, `%`-truncated (authoritative grammar); (T1b) any string literal ≥6 chars of that script
(`%`-truncated) — this is how const/spliced/spawned-echo probe vocabulary is accounted; (T2) an
anchored engine-diagnostic regex. Measured on both fresh 554-row runs (command
`… --census …`, 2026-10-18): **4908 lines each — 566 PASS, 2259 engine-diag, 2083 script-literal,
0 unaccounted**. The T2 set (22 patterns) covers: engine banner; blank; `at:`/`[N]` C++ and
`GDScript backtrace` frames; `-- END OF … BACKTRACE --`; `handle_crash: Program crashed with signal N`;
`Dumping the backtrace…`; `Load address:`; `Engine version:`; `(ERROR|WARNING|SCRIPT ERROR|USER ERROR|USER WARNING|Parse Error): `;
the NavigationServer deprecation tail; ANSI resets; editor import progress `[ N% ]` and
`[ DONE ]`; a rule of `=`; crash-handler C frames `[N] <hex> (`; glibc `double free or corruption (!prev)`;
libstdc++ asserts `^/usr/include/c++/`; the export preset listing pair.

**Evidence at land (r103-scr2.md carries commands + bytes).** Green silence: 0 flags on
2×554 fresh rows + 514 (r100-simplifier folded2) + 519 (r100-verify runs-v2) = **2141 records**.
Adversaries: 6/6 attacks flagged — mut09 A1–A3 foreign lines (exact r102-mut9 bytes), PASS-line
flood, second banner, cross-script splice — and 6/6 corruptions flagged (output dropped/nulled,
error-on-PASS, exit tamper, signature rewrite, artifact mismatch); unmodified control clean, **12/12**.
Cross-round: the r101-ver10 record-variant payloads — `mut-swap` flagged (`banner_shape`), the other
five silent (their mutations are row-count-level, `cases_integrity`'s domain, `run_battery.py:4119`).

**Ceilings (do not over-trust).** (a) A duplicated census-matching line up to the print-site bound can
escape; the prevention remains the row-design pin (r102-mut9 G-A/G-B: whole-capture expected-grammar
equality plus an output-bytes binding — `run_log_sha256=… run_log_lines=…`). The meta-gate audits
stored receipts; it is not a classifier substitute. (b) Engine vocabulary is version/platform bound
(measured on 4.7.2.stable.arch_linux.ed1daf0bf, ANSI editor progress, Linux crash handler). (c) The gate
expects the run_battery payload contract; foreign payload classes (custom runners, acceptance-cell
studies) fail-closed as `schema:`/`output_unreplayable` by design, not as defects.
