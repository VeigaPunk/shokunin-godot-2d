# Round 66 — boundary recon: rejection-clause SURFACE map edges

## Scope and method

LEAF boundary/revenger seat, scratch-only and report-only. I wrote only this
report and `corpus/live/r66-boundary/`. No tracked fixture, runner, CASES row,
lesson, LOG, or SCORECARD entry was touched; no subagent dispatch; no git
mutation.

Assignment (lane brief, verbatim edges): (1) the three-clause order —
`SCRIPT ERROR:`/`Parse Error:`/`unrelated_errors` — evaluation order on a
record tripping all three; (2) marker embedded in >64KiB writes, split across
pipe-buffer boundaries; (3) allowlist forms — the `,`-prefix and
`chain incomplete` structured forms — minimal mutations that escape/absorb;
(4) error bytes on stderr vs stdout THROUGH `classify_streams` (the
stderr-only latent asymmetry — does a stdout-carried forged error pass
`classify_streams` while failing `classify_process`?); (5) a marker carrying
BOTH signature and error substrings (dual-clause single-line).

**Provenance — the r66 author landed mid-run (again).** At probe start the
tree was clean at HEAD `2efaae2` (runner sha256 `cd4824cc…`, 2006 lines —
the r65-committed artifact). During my session the author's uncommitted
diff landed in the working tree (+565/−1: `probe_error_clause_surface`
meta, `record["expected_errors"]` exposure, four fixture arms
`--spawn-allowforge/-splitforge/-seamforge/-midlineforge`; working-tree
runner sha256 `76d37ace…`, 2506 lines; fixture `9ff5a9ae…`, 167 lines).
Still uncommitted at report time (`git status` → `M` both files).
**Every function I extract and exec — `run_process`, `classify_process`,
`classify_streams`, `classify_audio_process`, `pid_alive`, `kernel_ppid`,
`gated_signature_run` — is byte-identical between `HEAD:` and the working
tree** (verified by re-parsing both; CASES 81 and the 43-key
expected_errors dict also identical). My measurements therefore
characterize BOTH revisions. Two scratch fixtures:
`proj_r66/descendant_pipe_probe.gd` sha256 `8a001c83…` (my edge arms);
`proj_landed/` byte-identical copy of the author's working-tree fixture.

Method: `ast.get_source_segment`-extract the seven production functions
from the working-tree runner and `exec` them — rows tagged `comm_*`,
`st_*`, `vg_*`, `allowforge/splitforge/seamforge/midlineforge_*` run
production code verbatim. `eval_with_trace` (order-tracing replica),
`clauses` (per-conjunct truth table), and `allowed_error`/`match_branch`
(per-entry attribution replicas) are corroborating-only, disclosed as
replicas. Anchor: every CASES/mutant row of the r65-author battery receipt
re-classified through the verbatim functions — **81 rows replayed, 0
mismatches**. Environment: Godot `4.7.2.stable.arch_linux.ed1daf0bf`, Linux
x86_64, CPython 3.14.7, subreaper pid 1573. Reaper safety: driver SIGKILLs
only pids its own runs printed AND whose `/proc/<pid>/cmdline` carries
fixture-unique tokens; sibling seats ran live batteries concurrently on
this host untouched.

## Author-claim verification (independent reproduction)

- Author battery receipt `corpus/live/r66-author/runs/20261014T051140112142Z/
  verdicts.json`: **88 rows, all PASS**; `probe_error_clause_surface`
  **34/34 discriminations True**.
- MY OWN independent no-flag battery on the landed working tree:
  `python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot --runs
  corpus/live/r66-boundary/runs` → exit 0, `PASS battery`,
  `corpus/live/r66-boundary/runs/20261014T051400354771Z/verdicts.json` —
  **88 rows, all PASS; surface meta 34/34 discriminations True**;
  census block reads 39 allowlisted rows, 0 dead entries.
- Prior-row stability vs the frozen pre-landing baseline
  (`corpus/live/r66-baseline/runs/20261014T050234068765Z/verdicts.json`,
  frozen `git archive HEAD` @ `2efaae2`, 87 rows): **87 common rows, 0
  diffs** on (verdict, actual_exit, error, expected_exit, signature); the
  only new row is `probe_error_clause_surface`. Prior metas all hold in my
  run: error_spoof 29/29, gate 12/12, sig_spoof 10/10, pipe_eof 7/7,
  crash 4/4. "All 87 rows + discriminations stable" holds.
- Landed arms independently re-driven through verbatim classifiers
  (`drive_landed.py`, `landed-verdicts.json`): allowforge
  bare-rejects/matched-absorbs/foreign-rejects/counterfactual all True;
  splitforge evades (clean exit-0, forged bytes in-record, zero ERROR:
  lines, contiguous twin rejects); seamforge fabricated line in merged,
  in NEITHER stream (split-run: stdout tail `…ends in ERROR` /
  stderr head `: SEAMFORGE phantom fabricated line`), merged rejects;
  midlineforge splice `DESCENDANT_PIPE_PROBE: expected ERROR:
  DESCENDANT_PIPE_MIDLINE forged splice` observed 3/3 with
  `write_ppid == godot_pid` (pre-death). All confirmed.

## Edge 1 — three-clause order: vetoes in AND order; the allowlist preempts exactly one

`classify_process` (runner :160-177) is a flat six-conjunct AND evaluated
left-to-right with Python short-circuit; the `unrelated_errors`
list-comprehension at :174-175 is computed **eagerly** before the AND —
so the scan work happens even when an earlier conjunct will mask it, but
the *verdict attribution* follows the AND order
(`code_eq → error_none → signature → no_unrelated → no_script → no_parse`).

Per-unit `eval_with_trace` + verbatim verdicts
(`surface-verdicts.json → edge1_clause_order_units`) and real post-death
records (`comm_*`):

| record shape | verdict | first-false conjunct | mechanism |
|---|---|---|---|
| unrelated `ERROR:` only | False | `no_unrelated_errors` | line-scan |
| `SCRIPT ERROR:` only | False | `no_unrelated_errors` | the line contains `ERROR:` → clause-1 vetoes BEFORE clause-5 |
| `Parse Error:` only | False | `no_parse_error` | a `Parse Error:` line contains NO `ERROR:` substring → invisible to the line-scan; the blob clause is its sole veto |
| all three lines | False | `no_unrelated_errors` | clause-1 fires first in eval order |
| all three lines, ALL allowlisted | False | `no_script_error` | allowlist clears clause-1; blob veto stands — measured live on `comm_err_triple_allowed` and `comm_err_allowed_script` (the script line itself was an allowlist entry) |
| triple + signature absent | False | `signature_present` | error clauses never evaluated — masked |
| `SCRIPT ERR\n` + `OR:` split | **True** | none | newline-split EVADES the blob clause too — live record `comm_err_scriptsplit` PASSes with the split bytes in-capture |
| `Parse Er\n` + `ror:` split | **True** | none | same for the parse clause |
| allowlist entry containing `SCRIPT ERROR:`/`Parse Error:` | False | `no_script_error`/`no_parse_error` | self-neutralizing-entry class: absorbed from clause-1, vetoed by the blob — no such entry exists in-tree (census) |
| fabricated `SCRIPT ERROR:` splice line | False | `no_unrelated_errors` | the phantom contains `ERROR:` → clause-1 vetoes it before clause-5 |

So "order" is: eager scan, then short-circuit veto order; the allowlist is
a **clause-1-scoped preemptor only** — it can never preempt the two blob
clauses. `SCRIPT ERROR:` is reachable via clause-1 (its line carries
`ERROR:`) unless the line is allowlisted; `Parse Error:` is reachable only
via clause-3 (its line never carries `ERROR:`). All three are
line-presence functions, and all three are newline-splittable.

## Edge 2 — >64KiB / pipe-buffer boundary: presence is position-free; the evasion is too

Real post-death writes through verbatim `run_process`+`classify_process`
(pipe buffer 65536 on both fds):

| arm | bytes | verdict | mechanism |
|---|---|---|---|
| `comm_bulk_straddle` — 65535 pad bytes then `ERROR:…\n`: the token begins at stream offset 65535, straddling the 64KiB position | 65,840 | False | reassembled contiguously; the line-local scan has no offset arithmetic |
| `comm_bulk_embed` — ERROR line embedded mid-150KiB burst | 150,307 | False | same |
| `comm_bulk_nlsplit` — pad to 65534 then `ERR\n`+`OR:…` — the newline split itself straddles the boundary | 65,846 | **True** | evasion is position-free: no captured line contains `ERROR:` anywhere in 64KiB+ |
| `vg_bulk_straddle` under the verbatim r64 gate | — | gate **accepts** (sig at 0.572s while-live, death 0.639s); `inner=False` | the >64KiB-carried forged error is gate-invisible, as r65 pinned |

The signature marker is position-free by the same construction (blob
substring over the full capture; the gate checks cumulative `captured` —
an `os.read(65536)` chunk seam inside the marker still matches).
Inference: no boundary exists at 64KiB for either axis because both scans
are offset-free — supported by the straddle arms.

## Edge 3 — allowlist forms: minimal mutations, both directions

Verbatim `classify_process`/`classify_streams` on unit lines
(`edge3_allowlist_units`, 26 cells) — entry shapes and their 1-byte
mutations:

- **exact** (`SAVE_SIG`): absorbs the identical line only. Escapes: any
  suffix (`+" tail"`), any prefix (`"noise "+`), a second `ERROR:` on the
  same line, even a doubled internal space. The preemptor is
  whitespace-exact after `.strip()`.
- **`,`-prefix** (`COMMA_ENTRY`, ends with `,`): absorbs the bare entry
  itself via the *exact* branch (order inside `allowed_error`: exact →
  comma → structured), and any `startswith(entry)` continuation with
  `count("ERROR:")==1` — **arbitrary suffixes absorb**
  (`comma_arbitrary_tail_absorbs` True). Escapes: appended ` ERROR:`
  (count==2), prepended text (unanchored), and — the smallest mutation
  found — **deleting the entry's trailing comma**: the line is then
  shorter than the entry and can neither exact- nor prefix-match
  (`comma_no_comma_escapes` False; the author's
  `comma_entry__exact_shaped_line` cell measures the same wall from the
  other side).
- **structured** (`"ERROR: chain incomplete"`): requires
  `startswith("ERROR: chain incomplete collections=")` +
  `scene=SceneB:<Node#` + `old_alive=false` + count==1. Absorbs: the
  canonical forged line (real-pipe `comm_chain_absorbed` True), **the
  bare entry string itself as a line** (`chain_bare_entry_absorbs` —
  the exact-match backdoor), reordered `old_alive`/`scene` fields
  (the two `in`-checks are order-free), and arbitrary suffixes.
  Escapes: `SceneB→SceneC` (live `comm_chain_escape` False), missing
  `old_alive=false`, missing the literal prefix, second `ERROR:`,
  prepended text.
- **Foreign entry does not absorb** (`entry_cross_case_inert` False):
  the allowlist is a per-call parameter — entries preempt only on the
  row that supplies them.
- **Streams asymmetry**: `classify_streams.line_allowed` (:192-198) has
  NO structured branch — the same chain-shaped stderr line under
  `("ERROR: chain incomplete",)` is **absorbed by classify_process,
  rejected by classify_streams** (`streams_chain_rejects`:
  streams=False/merged=True). Exact and `,`-prefix forms exist in both.

## Edge 4 — the stream cross: divergence in BOTH directions

Real post-death writes classified through verbatim `classify_streams`
(separate pipes) and `classify_process` (concat), `stream_runs`:

| arm | streams | merged | reading |
|---|---|---|---|
| `st_err_stdout` (descendant `echo` on stdout) | **True** | **False** | **yes — the asked asymmetry**: streams audits stderr lines only; a stdout-carried forged error is invisible to it while the merged scan rejects |
| `st_err_stderr` (`>&2`) | False | False | stderr-carried rejects under both |
| `st_stderr_noise` (non-ERROR chatter `>&2`) | **False** | **True** | reverse divergence: streams' stderr audit is a strict whitelist — ANY un-allowlisted stderr line vetoes; merged doesn't care |
| `st_script_stdout` (SCRIPT ERROR: on stdout) | False | False | streams' blob checks DO scan both streams (:185-188) |
| `st_dualline_stdout` (dual line on stdout) | True | False | dual line inherits the stdout invisibility |
| `st_forge_sig_stderr` (forged MARKER on stderr) | **False** | **True** | signature-axis asymmetry, opposite direction: streams requires the signature in *stdout*; merged accepts it from either stream |
| `st_comma_stderr_allowed` (allowlisted error `>&2`) | True | False | the streams allowlist is per-call, same shapes-minus-structured |
| `allowforge_streams` (landed arm, forged allowlisted line lands on stdout) | True | False | the landed arm also evades streams — on stdout it needs no allowlist |
| `splitforge_streams` (landed `ERR\n`+`OR:` on stdout) | True | True | the split evades both, via different scopes |
| `seamforge_split_capture` (landed arm) | False | False | streams rejects the seam arm too — but via its any-stderr-line audit (the stderr head `: SEAMFORGE phantom…`), not via the phantom, which exists only post-merge |

`classify_process` is stream-blind (concat before scan); `classify_streams`
is stdout-content-blind except for signature + the two blob substrings,
and stderr-strict to the point of rejecting non-error chatter. The two
consumers disagree in both directions — `streams∧¬merged` and
`¬streams∧merged` are both realizable post-death.

## Edge 5 — dual-substring single line: the forged signature can carry its own veto; negative-row evidence is fabricatable wholesale

| arm | sig present | verdict | mechanism |
|---|---|---|---|
| `comm_dualline` — one post-death line `MARKER + " " + ERROR:…` (child also printed genuine MARKER) | True | False | the same line satisfies the signature substring AND trips the line-scan — the clause pair is not disjoint |
| `comm_dualline_wh` — child withholds; the descendant's dual line is the ONLY signature occurrence | True (forged) | False | **the forged signature carries its own veto**: signature clause satisfied by the very line that rejects |
| `vg_dualline_wh` under the verbatim gate | observed post-death (marker_at 0.552 > dead_at 0.520) | gate rejects | timing veto on the signature axis vs content veto on the error axis — different consumers catch the same line differently |
| `comm_negrow_fabricated` — child exits 2 printing only a banner; descendant echoes `SAVE_SIG` (which is both the row's signature AND its allowlisted error) | True (forged) | **True** | classify(2, None, out, 2, SAVE_SIG, (SAVE_SIG,)) **accepts**: on expected-negative rows the signature line IS an allowlisted error line — one post-death write satisfies signature presence AND absorbs into clause-1. The row's entire expected-negative proof fabricated wholesale |
| `comm_negrow_noallow` — identical bytes, allowlist=() | True | False | the allowlist is the sole preemptor — axis (a) on a real negative-shape record |
| `vg_negrow` under the gate | while-live marker accepted | inner False | (gate run used expected_exit=0 — n/a for the exit-2 shape; recorded as control) |

The allowforge arm lands the preemptor on a clean exit-0 positive shape
(genuine signature + absorbed forged error). `comm_negrow_*` extends it to
the sharper dual: on `save_corrupt_negative`-shaped rows the *evidence
itself* — the signature the row exists to assert — is a forgeable
allowlisted line; a descendant can fabricate the whole negative proof in
one write, gated only by the child's own exit code.

## Census (axis d) — dead entries and dead clauses

Mine (`dead_entry_census`, replayed r65-author receipt, 98 rows incl.
mutants) + the author's in-run census (39 allowlisted rows on my
independent run) agree:

- **0 dead `expected_errors` entries** — all 40 entries carried on my
  landed-run records matched ≥1 line of their own row's output (every
  allowlisted row genuinely emits its entry). Author's in-run census:
  `dead_entry_count: 0` likewise.
- **Branch-level**: 7 `,`-prefix entries fire via the `,`-prefix branch
  (contact_no_collision, animation_stuck, tween_no_start, audio_no_play,
  audio_bus_route_invalid_control, button_activation_disconnected,
  button_activation_unfocused); `save_process_missing`'s `,`-entry matches
  via the **exact** branch only — its emitted line ends AT the comma, so
  the prefix branch is shadowed on real output (live entry, dead branch
  path). The mutant `structured` branch is live (mutant_broken_scene_route).
- **Dead clauses on reachable output**: `SCRIPT ERROR:` and `Parse Error:`
  appear in **0 of 98** receipt rows (author's scan: 0) — both blob vetoes
  are latent guards no current fixture trips, and both are newline-splittable
  (edge 1). The audio `leaked_objectdb` regex matched 0 lines.
- **Dead mechanism**: `classify_streams`'s allowlist has exactly one in-tree
  call site (:1721) which always passes `allowed_stderr=()` — its
  exact/`,`-prefix matching is dead code in-tree; `classify_streams` also
  lacks the structured branch entirely (edge 3).

## Verdict on the declared falsifiable claim

"The rejection clause's verdict is a pure function of merged-output line
presence modulo the allowlist — forgeable in both directions by a
post-death descendant" — **CONFIRMED**, with the standing r65 carve-out:

- pure function of merged LINE presence: fabricated reject from a line in
  neither stream (xstream/seam) and neither process (intra-pipe);
  evasion with the bytes fully in-capture (newline-split, incl. across
  the 64KiB boundary); modulo allowlist in all three entry shapes —
  confirmed on real post-death records in both directions.
- Scope precision: "verdict" here is the *clause's* vote inside the AND;
  the row verdict additionally reads exit code, runner error, and
  signature presence — the negrow fabrication shows even those jointly
  admit the whole evidence layer on negative rows.
- Standing precondition (r65 critic CE-1): the function is over
  *captured* merged lines — a post-death write must land before pipe EOF.
- The author's landed discriminations cover (a)-(d) as declared; the
  five brief edges extend the map beyond the landed rows (clause-order
  attribution, >64KiB positions, streams cross-table both directions,
  dual-line self-veto, negrow wholesale fabrication).

## Divergences / sharpenings beyond the landed map

1. `classify_streams` and `classify_process` disagree in BOTH directions —
   stdout-carried errors evade streams (asked; measured True/False) while
   any non-allowlisted stderr chatter rejects streams but not merged
   (False/True), and a forged signature on *stderr* is accepted by merged
   but rejected by streams (sig axis, opposite direction).
2. `classify_streams` has no structured-allowlist branch — a
   chain-incomplete-shaped stderr line is absorbed by `classify_process`
   and rejected by `classify_streams` under the identical entry.
3. Negative-row wholesale fabrication: the `save_corrupt_negative` shape
   makes the signature itself an allowlisted `ERROR:` line — one
   post-death write satisfies signature AND absorbs; the row's proof is
   forgeable modulo only the child's exit code.
4. Clause-order attribution measured: `unrelated` vetoes before `script`
   before `parse` in the AND; the allowlist preempts only clause-1; a
   `Parse Error:` line is invisible to the line-scan entirely (no `ERROR:`
   substring) — clause-3 is its sole veto; SCRIPT/parse clauses are
   newline-splittable like the line-scan.
5. Self-neutralizing-entry class exists in the shape grammar (entry
   containing a blob-veto substring) — none exists in-tree.
6. `evasion is position-free`: the newline split defeats the scan at the
   64KiB pipe-buffer boundary and mid-150KiB alike.
7. Landed-arm streams side-effects: allowforge lands on stdout → also
   evades `classify_streams` without needing its allowlist; seamforge is
   rejected by streams via the any-stderr-line audit, not via the phantom;
   the r64 gate accepts the seamforge arm (genuine while-live signature)
   while merged rejects on the phantom — gate-invisible like every
   error-axis flip.

## UNKNOWNs / retained caveats

- Single host (godot 4.7.2 headless, CPython 3.14.7): absolute timings
  slide with load; clause-level and directional results do not.
- `eval_with_trace`/`allowed_error`/`match_branch` are byte-faithful
  replicas used for attribution only; all verdicts are verbatim-function
  outputs (81-row replay anchor, 0 mismatches).
- midlineforge splice observed 3/3 (80ms offset into a 200ms gap);
  race-stable on this host, structurally timing-dependent by design —
  the author's own discrimination asserts the splice, so a miss would
  surface as a discrimination failure, not silent drift.
- The seamforge streams rejection is via stderr-audit scope; a seam
  variant with the phantom head on stdout was not run (stderr head is the
  landed shape).
- Working tree uncommitted at report time: `76d37ace…` runner /
  `9ff5a9ae…` fixture; if the operator amends before commit, shas shift —
  the extracted clause functions were verified byte-identical to `HEAD:`,
  so the clause-level results hold either way.
- `pidfd`, non-POSIX, exported-build, `OS.execute` paths unprobed
  (carried from r61–r65).

## Artifact inventory (`corpus/live/r66-boundary/`)

- `drive_surface.py` — verbatim-extraction surface driver (replay anchor,
  edge-1 unit matrix, edge-3 allowlist matrix, comm/st/vg real-pipe arms,
  line-faithfulness units, dead-entry census).
- `surface-verdicts.json` — all phase outputs on runner sha `76d37ace…`.
- `drive_landed.py`, `landed-verdicts.json` — the author's landed arms
  re-driven verbatim (allowforge/splitforge/seamforge/midlineforge +
  streams/gate extras).
- `proj_r66/` — scratch fixture `8a001c83…` (251 lines, 31 flag arms)
  + project.godot.
- `proj_landed/` — byte-identical working-tree fixture copy `9ff5a9ae…`.
- `raw/`, `raw_landed/` — merged/per-stream captures per run.
- `runs/20261014T051400354771Z/` — my independent landed battery receipt
  (88 rows, all PASS; surface 34/34).
- `battery.stdout`, `drive.stdout`, `drive_landed.stdout`.

No commit, no tracked mutation, no LOG/SCORECARD write; descendants
SIGKILLed only on own-run pids with fixture-unique cmdline tokens;
post-run /proc scan clean.
