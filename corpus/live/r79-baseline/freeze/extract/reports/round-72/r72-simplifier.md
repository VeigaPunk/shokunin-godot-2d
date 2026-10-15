# Round 72 simplifier report — landed reorder-arm diff: weight audit + demonstrated zero-behavior deletions

Seat: simplifier (LEAF, **audit-only** — write scope is this report +
`corpus/live/r72-simplifier/`; tracked-file edits are author-owned, none made,
no git mutations). Lane: g2d | Round: 72 | Host: devin (CPython 3.14.7,
pygame 2.6.1 / SDL 2.32.72, `io.DEFAULT_BUFFER_SIZE` = 131072).

**Audited revision:** commit `fee5563` ("r72: reorder fabrication arm —
fd1-inheritance x stdio-withholding composition (xconnector X1)"); probe
sha256 `7c0f9c73…53ac8e4`, battery sha256 `077af0b5…315d28` (fixtures
byte-identical to the commit at report time). Pre-land baseline `44127af`
(probe `4d426a3b…`, battery `0a579819…`).

## Verdict

- **Deletions made: none** (no tracked edit scope; every candidate below is
  demonstrated in a scratch copy and reported, not applied).
- **Deletion candidates found: 2** — both *pre-existing* assertion-carried rows
  (`pump_not_needed`, `pump_updates_counted`, `pygame_battery.py:110-111`),
  each demonstrated silent with byte-identical artifacts (§3). Recommended for
  a hygiene fold (r68 `e8d4fb7` precedent), not applied here.
- **Landed-diff weight audit:** insertion-only for the battery (**71+/0−**);
  probe **102+/1−** with the single modified line the documented r71-verifier
  defect fix (`popen_arm` env, `pygame_probe.py:93`). Zero unused bindings,
  zero assertion-carried *new* rows, zero never-emitted pins, zero duplicate
  `(arm,key)` pins, no verbatim helper duplication (§2). **No new dead code,
  duplicate authority, or over-gate found in the r72 insertion.**
- **Preserved contract:** fixtures byte-identical to `fee5563`; battery
  **55/55 PASS** clean ×2 and **55/55 under `PYTHONUNBUFFERED=1`**; LOVE
  sibling **19/19 PASS**; all **36 prior rows unchanged** (pinned + verdict)
  and PASS.
- **`lsp` disclosure:** no `lsp` device in this seat's tool surface and no
  Python language server on the host (§6) — every call-graph/dead-code claim
  below is an **AST/textual census, not `references` proof**.

## (1) Landing timeline and revision pinning

| time (UTC) | event | evidence |
|---|---|---|
| 14:34:22 | wave 12 dispatched; `HEAD=44127af`; fixtures at pre-land hashes | `tasks/g2d-*.txt` mtimes; `baseline-hashes.txt` |
| 14:35:45 | this seat's watcher armed (`watch.sh`, `snapshot_loop.sh`) | `watch.log`, `snapshots/log.txt` |
| 14:42:57 | probe change detected (rev A `edae50c4…`), battery still pre-land | `landing-wait.log`, `landed-sha256.txt` |
| ~14:45:29 | probe rev B (`1d95c3bc…`) captured (`del-measure/pygame_probe.rev1.py`) | sha256 in `del-measure/` |
| 14:45:35 | stable pair rev C: probe `7c0f9c73…`, battery `077af0b5…` | `snapshots/log.txt` (no further pair since) |
| 14:46:26 | this seat's landed replay → 55/55 | `runs-landed/…/verdicts.json` |
| 14:46:58 | author commit `fee5563` (ci@local) | `git show --stat fee5563` |

The landing changed twice while this seat watched (probe-only revisions); the
audit below is on the committed pair. The battery's own `git numstat` is
**71 insertions, 0 deletions**; the probe's is **102 insertions, 1 deletion**
— that 1 line is the `popen_arm` env fix named in the commit message, and §4.3
proves it load-bearing.

## (2) Landed-diff weight census (AST/textual, no language server)

Tools (scratch, runnable): `unused_locals.py`, `literal_rows.py` (AST emit
census — replaces r71's regex which false-positived on a docstring
`driver=dummy`), `arm_coverage.py`, `weight_census.py`, `case_keyed_diff.py`.

- **Shape.** Probe 242 → 343 lines, battery 212 → 283 lines. Emitted surface
  9 → **15 arms**, 69 → **107 keys**; case surface 36 → **54 CASES + 1
  RAW_CASES = 55**. All 18 new CASES rows (`pygame_battery.py:113-134`) name
  keys the probe actually emits; the RAW row is battery-side by construction
  (`:137-142`, `:234-256`).
- **Dead bindings: zero.** Function scopes: 0 non-underscore bound-but-never-
  read names in either file (only conventional `_` throwaways); module-level
  zero-load names: none. No `locals()/globals()/exec/eval/getattr` escape
  hatches, so the census is exhaustive for these files.
- **Assertion-carried rows: no new ones.** The AST emit census finds exactly
  three literal-valued emitted keys: `pump|frames_nopump=400`,
  `pump|pump_needed='false'` (both pre-existing, both pinned — §3) and
  `reorder_self|descendant='printf'` (unpinned provenance echo). Every new
  `reorder_*`/`reorder_self` key is a **computed** value (`topology`,
  `head_at`, `injected_at`, `tail_at`, `wire_bytes`, `ret`, `bufsize`,
  `fd1_isatty`) — the r72 rows are measurement-carried.
- **No never-emitted pins, no duplicate pins.** `arm_coverage.py`: "pinned but
  never emitted: none"; a dedicated duplicate check over `CASES`/`RAW_CASES`
  finds no repeated `(arm,key)` pair. Repeated *values* (`131072`, `19`,
  `midline_splice`, `0`) sit on distinct `(arm,key)` pairs — the per-key case
  model, not duplication.
- **No verbatim duplication introduced.** `reorder_arm` vs `withhold_arm`
  normalized-token ratio **0.127** (different implementations: `communicate` +
  byte-order classification vs `select`/`os.read` + timing chunks); the
  battery's raw-wire classifier vs the probe's classifier **0.319** — same
  4-way shape on *different wires* (the probe cannot classify its own
  delivered order; the battery cannot call probe code). In-convention.
- **Unreachable branches are diagnostic carriers, not dead code.**
  `markers_missing`, `degenerate`, the `TimeoutExpired` path
  (`pygame_probe.py:206-223`) are failure-class carriers — the same class the
  r71 audit ruled "not a deletion" for `splice_verdict`.
- **Titles are origin markers, not stale names.** The battery/probe docstrings
  still say "r71 …" while carrying an r72 section — this matches the lane
  convention (`love_battery.py:1` says "r70 LOVE 11.5 headless battery" and
  stayed r70 through r71). The r72 addition is explicitly sectioned
  (`pygame_probe.py:39-55`, `pygame_battery.py:23-35`).

## (3) Deletion candidates — demonstrated silent, not applied

Both candidates are **pre-existing** (r71 landing) rows that pin a value the
probe emits as a **literal**: the row cannot fail for a mechanism reason
(it can only fail if the probe's own literal changes). Demonstrated on the
landed revision, in scratch copies (`del-measure/r72/`), with the narrow
existing check = the battery itself.

| variant | change | result | artifact diff (deterministic table) |
|---|---|---|---|
| control | verbatim landed copies | **55/55 PASS** ×2 | — |
| vA | delete `pump_not_needed` (`pygame_battery.py:110`) | **54/54 PASS** | exactly the removed row + `totals cases 55→54` |
| vB | delete `pump_updates_counted` (`:111`) | **54/54 PASS** | exactly the removed row + `totals cases 55→54` |
| vC | delete both | **53/53 PASS** | exactly the two rows + `totals cases 55→53` |

Receipts: `del-measure/r72/{control,vA,vB,vC}/runs2/…/verdicts.json`,
tables in `…/table-rep2.txt`, diffs in `del-measure/r72/diff-casekeyed-*.txt`.
The case-keyed comparison is the byte-identity proof: **cases only in A =
{removed rows}, cases only in B = none, changed non-observed fields = none**
(`case_keyed_diff.py`); only wall-clock `observed` keys differ between runs.
No gate counts rows (`verdict = failed==0 and launch_ok and done_marker`,
`pygame_battery.py:267`), so the deletion is silent by construction.

Context: this is the same defect class the r71 report recorded for the LOVE
sibling (`love_battery.py:54` identical row; `love_battery.py:173` dead
`c_stderr`/`c_code` bindings) — those two stand unchanged this round (the
landing touches neither file).

## (4) Considered and rejected — the stop condition

- **4.1 Per-arm `bufsize` rows (`rord_bufsize` `:122`, `self_bufsize`
  `:134`).** They repeat the constant already pinned by `whs_bufsize` `:78`.
  *Rejected:* each is the per-receipt referent gate the xconnector's
  pin-honesty rule asks for ("carry the referent `default_buffer_size` per
  receipt, not a hardcoded edge"); deleting them removes the gate that the
  receipt's referent is the measured one. Deleting would harm the
  verdict-integrity axis.
- **4.2 `rord_buf_inj0` (`:118`) is implied by `rord_buf_head=8` +
  marker identity** (a wire with `head_at=8` forces `injected_at=0`).
  *Rejected:* the battery's case model is one row per key (r68/r71 kept the
  same redundancy); collapsing implied rows is a convention change, i.e. the
  second convention this seat exists to prevent.
- **4.3 The two env-hygiene lines are load-bearing, proven by counterfactual.**
  vD = landed copy minus the battery-side `env.pop("PYTHONUNBUFFERED")`
  (`pygame_battery.py:154`): clean env 55/55, but under
  `PYTHONUNBUFFERED=1` → **FAIL `self_wire_reorders`** (`'midline_splice' !=
  'prefix_reorder'`, idx h=1891 c=1904 t=1918) — the fabricated wire is
  invisible without the pop. vE = landed copy minus `env=CHILD_ENV` on
  `popen_arm` (`pygame_probe.py:93`): under the battery path 55/55 both envs
  (the battery pop already covers it), but the probe's **standalone** contract
  breaks under a dirty env — standalone `PYTHONUNBUFFERED=1` probe run:
  `popen_buf|l1_wait_ms` **125.61** (control, child held) vs **5.13** (vE,
  child unbuffered → would flip the `(110,180)` pin). Both lines stay.
- **4.4 `REORDER_LATE`'s `time.sleep(0.60)` (`pygame_probe.py:190`).** The
  backgrounded descendant holds the pipe write-end via the shell, so the sleep
  is belt-and-braces. *Rejected:* it is the explicit pipe-lifetime guard for
  the append cell; removing it risks that cell's semantics for one line of
  saving — not the smallest safe deletion.
- **4.5 `markers_missing`/`degenerate`/timeout branches.** Diagnostic
  carriers (r71 precedent), not dead code.
- **Stop condition reached:** after §3, the next candidates are per-receipt
  referent gates, case-model redundancy, or proven-load-bearing hygiene lines
  — each deletion would harm an axis (verdict-integrity / convention /
  robustness) rather than the weight axis.

## (5) Preserved contract (independently re-verified)

- Fixtures byte-identical to `fee5563` (`sha256sum` above; `git diff HEAD`
  empty under `corpus/fixtures/`); this seat wrote only inside
  `corpus/live/r72-simplifier/` + this report.
- Landed battery replay: `runs-landed/…144626306766Z` **55/55, exit 0**;
  control copy of the same revision `del-measure/r72/control` **55/55 ×2**.
- Author's claim re-verified: `PYTHONUNBUFFERED=1` ambient →
  `runs-dirty/…145050458440Z` **55/55**.
- Prior rows: all 36 pre-land cases present in the landed battery with
  unchanged `pinned`/`verdict`, all PASS (checked case-keyed against
  `runs-preland/…143634271434Z`, 36/36).
- Sibling untouched and green: `love_battery.py` replay
  `runs-love/love-20261014T145104087980Z` **19/19 PASS, exit 0**.
- Hazard evidence (the round's payload): landed raw capture reads
  `REORDER-CHILD@1890` **before** `REORDER-HEAD@1904` / `REORDER-TAIL@1917`
  (`runs-landed/…/probe.stdout.txt`, lines 15-18; `raw-wire-positions.txt`).

## (6) Method and `lsp` disclosure

- **No `lsp` device exists in this seat's surface**, and no Python language
  server is installed on this host: `pyright`, `basedpyright`, `pylsp`,
  `jedi-language-server`, `ruff-lsp`, `lsp` all ABSENT from PATH and not
  importable (`pylsp/jedi/pyright/basedpyright/ruff/lsprotocol` → absent);
  `clangd` is present but C/C++-only. There is therefore no server to warm up
  or retry; every dead-code/duplication claim here is an **AST/textual census,
  not semantic `references` proof**, and is stated as such.
- Scratch tools (all runnable, no tracked deps): `unused_locals.py`,
  `literal_rows.py`, `arm_coverage.py`, `weight_census.py`, `artifact_diff.py`,
  `case_keyed_diff.py`, `watch.sh`, `snapshot_loop.sh`, `wait_for_landing.sh`,
  plus the `del-measure/r72/` variant harnesses.

## (7) Cross-seat observations (out of scope, recorded for owners)

- **Author scratch doc drift:** `corpus/live/r72-author/evidence-notes.md:29`
  claims "`git diff corpus/fixtures/` = +171 lines, 0 removed/modified lines";
  the committed diff is probe **102+/1−** (the `popen_arm` env line, named in
  the commit message). Scratch-only, but the author/scribe may want the note
  corrected.
- **The r72 hazard pin is live in the artifact:** any *streaming* consumer of
  the probe's ARM lines would see the reordered marker pair before the flush
  delivers the ARM line; the post-exit parser (and the battery) sees only the
  replayed order — this is exactly what `RAW_CASES` pins (§5).
- **Scratch-only probe multiplicity:** r72 scout/critic/boundary/scribe/
  reviewer each built reorder harnesses in scratch; none is tracked, so no
  duplicate authority exists today — if any is promoted into
  `corpus/fixtures/`, the corpus acquires competing probes for one runtime
  (same note as r71 §7).
- Late r71 seats are still active (`corpus/live/r71-verifier/` runs,
  `corpus/live/r71-scribe/watch.log` appends, `reports/round-71/r71-*.md`
  untracked) — pre-existing, not this seat's writes.

## (8) Tradeoffs / stop condition

- The two §3 candidates are genuine but tiny (2 rows) and sit in a file the
  round's contract declares prior-row byte-stable — applying them now would
  trade a 2-row saving for a broken byte-stability claim; the honest path is a
  post-verifier hygiene fold with the same del-measure receipts (r68
  precedent), not an author-landing edit.
- The landed insertion itself adds **no** deletable weight: it is 15 arms /
  55 cases of measured, per-key, computed-value pins, with its two hygiene
  lines each proven load-bearing in a different invocation mode (§4.3).
- **Stop condition reached** (restated): the next deletion would harm
  verdict-integrity (per-receipt referent gates), the case-model convention,
  or the probe's standalone robustness — not the weight axis.

## Evidence index (all host-resolvable, this repo)

- Revision/contract: `corpus/live/r72-simplifier/baseline-hashes.txt`,
  `landed-sha256.txt`, `watch.log`, `snapshots/log.txt`,
  `del-measure/pygame_probe.rev1.py`; `git show fee5563`.
- Runs: `runs-preland/pygame-20261014T143634271434Z/` (36/36),
  `runs-landed/pygame-20261014T144626306766Z/` (55/55),
  `runs-dirty/pygame-20261014T145050458440Z/` (55/55, env sweep),
  `runs-love/love-20261014T145104087980Z/` (19/19).
- Deletion proofs: `del-measure/r72/{control,vA,vB,vC}/{runs,runs2,table-rep2.txt}`,
  `del-measure/r72/diff-casekeyed-v{A,B,C}.txt`.
- Load-bearing counterfactuals: `del-measure/r72/vD/{runs-clean,runs-dirty2}`,
  `del-measure/r72/vE/{runs-clean,runs-dirty}`,
  `standalone-dirty-control.txt`, `standalone-dirty-vE.txt`,
  `vD-dirty-run.txt`.
- Census receipts: `preland-coverage-pygame.txt`,
  `landed-coverage-pygame.txt`, `preland-literal-rows.txt`,
  `landed-literal-rows.txt`, `preland-census-pygame_{probe,battery}.txt`,
  `raw-wire-positions.txt`.
