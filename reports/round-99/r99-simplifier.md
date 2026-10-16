# r99 simplifier — committed-tree audit of the r99 audio block (`254e79dd`, lane HEAD `f02ee348`)

**VERDICT: PROVEN-LEAN.** The r99 landing carries a verified **−31-line fixture
fold** (3 dead-store lines — a write-only local plus a never-read declaration —
and 28 terminal `stream = null` stores) plus a **+1-line provenance rewrite** in
the harness comment — net **−30 lines** — proven on **252 fresh headless
launches** (21 rows × 4 reps × 3 trees: committed, a semantic no-op control,
folded) with every harness-pinned field byte-identical on every launch and all
21 rows classified PASS by the production classifier; the frozen receipts'
pinned fields match 267/267; two authored mutations are caught by the same
comparator (detector teeth). **Nothing landed: the fold is an unapplied patch
(`fold-proposal.diff`), zero tracked writes, zero commits.** Five candidates are
REFUTED and three report-only items are filed (a duplicate emit, a receipt-count
claim the author's own evidence contradicts, and the byte-identity tradeoff).

Seat `SIMPLIFIER` (g2d lane `r99-simplifier`) | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, `--headless`, Dummy
audio driver, mix rate 44100, 60 tps), Python 3.14. Audit target: the r99 block
of `254e79dd81202b2f25b3064681c96d95a37ccdfe` (*r99 author: headless audio
lattice*), byte-verified inside the lane HEAD `f02ee348` (see §1). Scratch and
receipts live under the untracked `corpus/live/r99-simplifier/`.

**`lsp` disclosure (device answered — this is not a grep audit).** The lane's
engine-LSP device (`godot --headless --editor --lsp-port N` on a staged
project; the r97 lane's `lsp_refs.py` client, reused verbatim) answers
`textDocument/references` (`referencesProvider: true`) for both fixtures. The
cold-empty guard is satisfied: `pass1_immediate` == `pass2_warm` for every
symbol. A synthetic two-file control (`lsp_xfile_target`) returns hits in
**two** files, so "every hit is in the owning file" is a real statement, not a
device limitation. Candidate proofs: `prev_t` → **2 hits** (its declaration
and its own write; **zero reads**), `pairs` → **1 hit** (its declaration
only). Live controls: `_arm_mixblock` 2, `_on_finished` 2 (its `connect`
site), `_is_q` 7, `_drain` 21, `_wait_ms` 26, `PH` 3 (read at 242/344). No hit
outside the owning file. Text grep is used nowhere as semantic proof.

---

## 1. Audit scope and committed-byte verification

| item | value |
|---|---|
| r99 landing on main | `254e79dd81202b2f25b3064681c96d95a37ccdfe` |
| lane HEAD at audit start | `2dcbb6f6ed491e51aa76237b96f80c0b38fe607f` (r100 author) |
| lane HEAD when the report was written | `f02ee34861c15bcf1b9d2b5ede3bd5560b51eb94` (three **foreign** commits landed mid-seat: the r97–r100 integration dedupe `9ede7c50`, a `.pyc` refresh `619ad7e0`, and two wave-B report commits) |
| r99 block bytes | comment header + 21 CASES rows = 132 lines, `sha256 bd932403ecfb1f448c5243b28ebc8ed5ba6242d3bfe8d9681919ae47853b2f21` — **identical at `254e79dd`, `2dcbb6f6`, `9ede7c50` and the final HEAD `f02ee348`** (`head-check.txt`); the fold patch still applies cleanly there |
| fixtures | `audio_lattice.gd` `165571c4…` (773 lines) and `r99b_modes.gd` `b680e6f2…` (453 lines) — **byte-identical to the frozen r99-scout / r99-boundary probes** and to the working tree at audit time |
| harness | `run_battery.py`: 509 CASES tuples / 509 unique at `9ede7c50`; the r99 block's allowlist entry and floor gate are byte-identical to `254e79dd` |

The shared tree is a moving target: sibling integrator/adjudicator commits
landed during the seat (the integration dedupe above and a `.pyc` refresh).
None touches the r99 block (proven above); every claim below is pinned to the
**committed bytes**, staged with `git archive` into `tree/` and re-hashed,
never to a dirty worktree. This seat wrote nothing tracked.

## 2. The fold (PROVEN per fold, net line delta)

Method: (a) scope-aware value-observation scan over every `var`/`const` with
string literals and comments stripped (`deadstore_scan.py`,
`deadstore-strict.txt`) — the *only* two dead locals in both fixtures are
listed below; (b) engine-LSP `references` for every deletion candidate and its
neighbours; (c) execution: 21 rows × 4 reps × 3 trees in the battery's own
launch shape; (d) the full battery before/after.

| # | fold | weight | LSP/census proof | execution proof | call |
|---|---|---|---|---|---|
| **F1** | `audio_lattice.gd` `_arm_mixblock`: `var prev_t := Time.get_ticks_usec()` (161) + its per-iteration store `prev_t = now` (176) are **write-only** | **−2 lines** (2 edits) | `references(prev_t)` = {161 decl, 176 store}, **0 readers**; strict scan agrees | 252 launches: pinned fields byte-identical; `mixblock` fully byte-identical on 4/4 reps | **PROVEN — take** |
| **F2** | `r99b_modes.gd` `_arm_splitcycle`: `var pairs: Dictionary = {}` (403) declared and never read or written again | **−1 line** (1 edit) | `references(pairs)` = {403 decl} only; strict scan agrees | `r99b` rows: the arm is not executed by any row, and no other reference exists | **PROVEN — take** |
| **F3** | both fixtures: the terminal `X.stream = null` that immediately precedes `X.free()` at **28 sites** (20 + 8) — every readback has already happened, the player is already stopped | **−28 lines** (28 edits) | not a local dead store but a property write with engine-teardown semantics — see the caveat below; no reader can observe it | 252 launches: **no** `WARNING:`/leak line on any launch, no rc change, no signature change; full battery green (§4) | **PROVEN at this launch shape — take, caveat disclosed** |
| **F4** | `run_battery.py` r99 provenance paragraph: it says the fixtures are BYTE-COPIES and "deliberately NOT folded", which F1–F3 make false; rewritten to record the fold while keeping the frozen probe paths + sha256s, the boundary F1 launch-mode finding and the author's receipt numbers verbatim | **+1 line** | comment-only: `CASES` (509 tuples, r99 rows identical) and `classify_process` (sha `749fa060…`) are unchanged vs HEAD | both batteries run this harness (folded side) | **PROVEN — take** |

**Net line delta: −30** (fixtures −31, harness comment +1). Patch:
`fold-proposal.diff` (`git apply -p1` clean at the final HEAD `f02ee348`,
re-verified to reproduce the folded bytes exactly).

**F3 caveat (honest scope).** Unlike F1/F2 this deletes *engine-facing
statements*, not unread locals: `stream = null` detaches the stream before the
node is freed. The claim proven here is *observational*: at the battery's
launch shape it changes no emitted byte, no rc, no stderr line (including the
ObjectDB-leak warning the fixture header promises to avoid), on 252 fresh
launches plus two full batteries. It is **not** a semantic proof that a real
(non-Dummy) audio driver could never observe the teardown order; the seat
records that as the fold's scope. If the operator prefers to keep the teardown
discipline byte-for-byte, apply **F1+F2 only** (`folded-min/`, −3 lines) —
that fold is provably a no-op by construction (its deletions are in an
unexecuted arm and a never-read local) and was verified identically.

## 3. Verification method and results

`verify_folds.py` (252 launches + 2 mutant launches) → `fold-verification.json`,
`fold-runs/`; `analyze.py` → `fold-analysis.json`:

| check | result |
|---|---|
| signature present on stdout | **252/252** launches (all sides, all reps) |
| production `classify_process` verdict | **252/252 PASS**, rc == expected, no unexpected `ERROR:` line |
| `r99_audio_gen` allowlist entry | live on every side: exactly the 2 expected `ERROR: Condition "active" is true.` lines, `dead_in_run` never fires |
| `WARNING:` lines | **0** anywhere (the fixture header's leak-free promise holds after F3) |
| **harness-pinned fields** | every `key=value` the CASES signature contains is **single-valued and correct on all 252 launches** (`pinned_field_diffs: []`) |
| **null-control rule** | a key counts as a fold effect only if it is single-valued on *both* committed and the no-op control and differs on folded → **zero such keys** (`regression_keys_null_control: []`) |
| masked comparison | after masking (a) GDScript backtrace line numbers and (b) the fields that vary on the no-op control, the merged output is **byte-identical across all sides for all 21 rows** (`masked_identical_all_sides: true`) |
| frozen-receipt oracle | **267/267** battery-shape receipts (scout canonical + loadtest + boundary quiet + load) carry the signature **and** the pinned field values |
| detector teeth (mutant) | authored mutations caught: `q_frames=128→127` → `sig_present=false`; `_arm_stoppos` `player.stop()` removed → `imm_zero=false`, row FAILs. The comparator resolves real changes |

**Declared non-semantic differences (all listed, none pinned):**

| class | rows | observation |
|---|---|---|
| backtrace line numbers | `r99_audio_gen` | `res://audio_lattice.gd:358,363` (committed) → `:356,361` (no-op control) → `:350,355` (folded); the harness allowlist matches the `ERROR:` line only, so the verdict is unchanged. Same class r95/r96 declared |
| wall-clock tail fields | `r99_audio_finish` (`transition_f`, `fin_frame`, `fin_us`, `frames`), `r99b_finfree_played` (`fin_us`) | these fields vary **on the committed side itself** across reps (the author's documented load sensitivity); the signature ends before them (`finished_seen=true` / `played_gt_02=true`) |
| split block publish | `r99b_mixfree` (`blocks`, `other`, `hist`, `chg`) | the block update is observed split (`1664+2432 = 4096`, `640+3456 = 4096`) — the author's documented µs-poll observer artifact. It appears on the **no-op control** (`folded-min` rep 2, whose executed arm is byte-identical to committed) as well as on folded, so it is run-to-run noise by construction; `all_jumps_q=true period_is_block=true` holds on all 12 reps |

## 4. Full battery A/B

`run_batteries.sh`: control = `python3 corpus/fixtures/run_battery.py` from the
lane repo root (task contract) on the committed bytes at `9ede7c50` (the only
commit that landed during the run, `619ad7e0`, changes the tracked `.pyc`
only); folded = the same battery from a fresh `git archive HEAD corpus/fixtures`
checkout under `/tmp/r99-simplifier-archive` carrying `folded/` +
`folded-harness/` (`c49916fc…`).

| | control (committed) | folded |
|---|---|---|
| run dir | `battery-committed/20261016T094227114204Z` | `battery-folded/20261016T095051144169Z` |
| verdict / rows | **PASS**, 516 results | **PASS**, 516 results |
| FAILs | **0** | **0** |
| r99 rows | **21/21 PASS** | **21/21 PASS** |
| `r99_expected_errors_all_matched` | True | True |
| `dead_entry_count` | 0 | 0 |
| `census_bare_classifier_consistent` | True | True |
| `r99_audio_gen` allowlist entry | `matched_lines=2`, `shape=exact`, `dead_in_run=false` | same |
| gates compared | — | **49/49 identical**, `verdict_diffs {}`, `case_set_diff []` |
| `scan_clause_census` | `ERROR:_per_line_lines=162`, `objectdb_leak_audio_lines=0` | identical |
| loadavg at start / end | 13.06 / 7.21 | 7.21 / 4.23 |
| seed-guard complaint | none | none |

`battery_compare.py` reports **zero** verdict diffs, zero case-set diffs, zero
r99 diffs and zero gate diffs (`battery-compare.json`) — the fold is
battery-invisible on the full 516-row run, on both sides, at the same sha
basis.

## 5. LSP evidence (raw)

`lsp-refs-audio.json`, `lsp-refs-modes.json`, `lsp-refs-xfile.json`
(`pass1_immediate` == `pass2_warm` in every entry; `error: null` in every entry):

| file | symbol | hits |
|---|---|---|
| `audio_lattice.gd` | `prev_t` (candidate) | 2 — line 161 (decl), 176 (its own write); **no read** |
| `audio_lattice.gd` | `_arm_mixblock` / `_on_finished` / `_is_q` / `_peak2` / `PH` / `_drain` / `_wait_ms` | 2 / 2 / 3 / 2 / 3 / 21 / 26 — all in-file |
| `r99b_modes.gd` | `pairs` (candidate) | 1 — line 403 (decl) only |
| `r99b_modes.gd` | `_arm_splitcycle` / `_busy_us` / `_is_q` / `PH` / `_on_finished` | 2 / 2 / 7 / 3 / 2 — all in-file |
| cross-file control | `lsp_xfile_target` | 2 — `lsp_xfile_a.gd:3`, `lsp_xfile_b.gd:3` |

## 6. Refuted candidates and report-only findings

| # | candidate | verdict | reason |
|---|---|---|---|
| **SP1** | `_is_q(pos, rate := 44100.0)` — the `rate` parameter is never passed by any call site | **REFUTED (no weight)** | 0-line change; it would replace an explicit named rate with a literal. Not dead code, an unexercised default (r95 SP11 class) |
| **SP2** | 9 helpers duplicated between the two fixtures (`_arg`, `_p`, `_db`, `_mk`, `_wait_ms`, `_drain`, `_is_q`, `_on_finished`, `_initialize`) plus 3 shared file-scope vars (`PH`, `_fin_frame`, `_fin_us`) | **REFUTED** | Both are standalone `extends SceneTree` scripts with no `preload`/`class_name`/`load(` (census in `head-check.txt`); a shared base would add a new convention and break the probe-of-record relation for a per-row-isolated battery |
| **SP3** | the 6 unrowed `r99b_modes.gd` arms (`modeinfo`, `mixphase`, `peakphase`, `advfree`, `splitcycle`, `firstlaw`) | **REFUTED** | They are the boundary's instruments of record; the harness comment cites their measurements as the justification of the pin folds (r95 SP11) |
| **SP4** | the 89-line r99 harness comment block | **REFUTED** | It *is* the landing's justification record (boundary verdicts, refutations, exclusions, receipt counts); deleting it orphans every pin (r95 SP7) |
| **SP5** | `r99_audio_census`'s `max_fps=0` pin | **REFUTED** | Documented launch-shape fact, deliberately loud (author §1) |
| **R1** | `audio_lattice.gd` `_arm_finish` emits the **same predicate twice**: `finished_seen=%s fin_frame_ge_1=%s` both take `_p(fin_frame >= 1)` (committed lines 257–259). The signature pins only `finished_seen=true` | **report-only finding (LOW)** | Removing `fin_frame_ge_1` is classifier-safe but **not byte-neutral** (the boundary receipts carry the field), so it is the author's/integrator's convention call — same class r96 §5 filed |
| **R2** | the harness comment claims "Accepted 1185/1185 receipts at the battery launch shape and every paced/threaded mode; every rejection in the corpus is confined to the unpaced `--fixed-fps` modes" | **report-only finding (LOW/MEDIUM)** | The author's own `receipt_survival.json` gives battery **267/267** + paced **204/210** = **471/477** (699 row-receipt classifications in total); the 6 paced rejections are `r99_audio_census` under `--max-fps 30/60/120` — which the author's §3 table records. The number 1185 is not reproducible from the shipped receipts (949 corpus receipt files + 89 author-side launches). The claim is the author's; this seat did not edit it (the fold patch keeps the author's numbers verbatim) |
| **R3** | the fold breaks the fixtures' byte-identity with the frozen probes (the author's stated reason for not folding) | **disclosed tradeoff, not a blocker** | Receipt applicability drops from *byte-level* to *signature + pinned-field level*, which is what the battery actually checks — measured **267/267** on the frozen receipts. F4 rewrites the one comment sentence that the fold makes false; the frozen paths + sha256s stay as provenance of record |

## 7. Preserved contract

- No rename, no new helper, no new file convention: F1–F3 delete statements only; F4 rewrites one comment paragraph and keeps the author's numbers and the frozen probe provenance.
- Every harness-pinned field, every signature, every expected-exit, the single `expected_errors` entry, the `r99_expected_errors_all_matched` floor gate and the fixture headers' stated discipline ("every arm frees its players and drains frames", "wall-time waits only") survive unchanged.
- The folded harness's `CASES` (509 tuples) and `classify_process` (sha `749fa060…`) are byte-identical to HEAD's — the harness change is comment-only.
- Provenance explicitly marked historical is untouched: frozen probe paths + sha256s, the r88 confound record, the boundary refutations, the "deliberately NOT authored" list.

## 8. Shared-tree state at report time

- `git rev-parse HEAD` = `f02ee348…`; the tracked tree is **clean** (a foreign `.pyc` refresh was committed mid-seat as `619ad7e0`; the two later foreign commits only added wave-B reports). Re-verified at report time: the r99 fixtures and the harness in the working tree are byte-identical to HEAD (`head_check.py`).
- This seat's tracked writes: **only** `reports/round-99/r99-simplifier.md` (untracked until the orchestrator commits). Everything else lives under `corpus/live/r99-simplifier/` (untracked): `tree/`, `folded/`, `folded-min/`, `folded-harness/`, `mutant/`, `proj-*/`, `fold-runs/`, `fold-runs-smoke/`, `battery-committed/`, `battery-folded/`, the scripts, the logs and the JSON receipts. No commit, no stage, no push; the r99 fixtures and the harness in the working tree are **byte-identical to HEAD** (`head_check.py` re-runs the check).
- Load/host caveats: sibling lanes ran throughout (loadavg 9.9–16.5 during the 252-launch proof; recorded per battery in `battery-*-head.txt`); the three declared noisy fields above are exactly the classes that vary under that load, and the no-op control separates them from the fold. No row was called green that measured nothing: every launch is recorded with stdout/stderr/rc.

## 9. Evidence index (`corpus/live/r99-simplifier/`)

| artefact | content |
|---|---|
| `head-check.txt`, `head_check.py` | HEAD/block/fixture byte identity, self-containment census |
| `deadstore_scan.py`, `deadstore-scan.{json,txt}`, `deadstore-strict.txt` | scope-aware dead-store scan (strings/comments stripped): exactly 2 dead locals |
| `fold.py`, `folded/`, `folded-min/`, `mutant/`, `fold_harness.py`, `folded-harness/`, `make_patch.py`, `fold-proposal.diff` | the fold, its no-op control, the detector control, the harness rewrite and the reviewable patch |
| `stage.py`, `verify_folds.py`, `fold-verification.json`, `fold-runs/` | 252 + 2 launches, per-rep stdout/stderr/rc |
| `analyze.py`, `fold-analysis.json` | pinned-field audit, null-control rule, declared masks, receipt oracle |
| `lsp_refs.py`, `lsp_run.sh`, `lsp-refs-*.json`, `lsp-*.log` | engine-LSP references receipts (pass1/pass2) |
| `run_batteries.sh`, `battery-committed/`, `battery-folded/`, `battery-*.log`, `battery-*-head.txt`, `battery-compare.json`, `battery_compare.py` | full-battery A/B and its comparator |

## 10. Blockers

**None.** The r99 block is green on its committed bytes; the only provable
weight in it is the −30-line fold above, and the next deletion (the unrowed
boundary arms, the harness comment, the duplicated helper surface) would harm
the instrument/provenance axes, which is where this seat stops.

— r99 simplifier, seat output; the canonical Rust runtime judges.
