# Round 68 scout report — midlineforge fabrication-window ladder + stream-attribution receipt upgrades

Seat: scout, lane `game-dev-2d`. Canonical repo `~/Projects/shokunin/game-dev-2d-shokunin`
(brief's worktree `~/Projects/prymeagnt/game-dev-2d` resolves via `.shokunin/game-dev-2d`
symlink → this repo). All commands ran on this host (devin). Scratch + receipts:
`corpus/live/r68-scout/`. Tracked tree was clean at scout time (`git status --porcelain`:
no `M` entries); author had not landed yet — line refs are HEAD `1101cb3` working-tree
numbers.

## (1) Where the 200ms gap and the 80ms offset live

`corpus/fixtures/descendant_pipe_probe.gd` (169 lines, HEAD `1101cb3`):

| what | where | bytes |
|---|---|---|
| arm flag parse | `:116` | `var midline_forge := "--spawn-midlineforge" in user_args` |
| doc block | `:82-88` | "fixed 80ms offset, write_ppid==godot_pid … 200ms gap" |
| constants | `:103-104` | `MIDLINE_ERROR`, `MIDLINE_PPID_WRITE` |
| descendant spawn (the 80ms) | `:157-159` | `elif midline_forge:` → `OS.create_process("/usr/bin/sh", ["-c", "sleep 0.08; read -r _ _ _ pp _ < /proc/self/stat; printf '" + MIDLINE_ERROR + "\\n'; echo " + MIDLINE_PPID_WRITE + "$pp"])` — **`sleep 0.08` is the point sample, hardcoded inside the sh command string** |
| gap (the 200ms) | `:166-168` | `printraw(MARKER_SPLICE_HEAD)` → `OS.delay_msec(200)` → `print(MARKER_SPLICE_TAIL)` |
| arm ordering | `:117-130, :160-168` | banner prints (`:118-130`), spawn elif-chain (`:134-159`), `print spawned_pid` (`:161`), halves (`:163-168`) — the descendant's sleep clock starts ~at `create_process` return, i.e. ~1-2ms **before** the head bytes flush |

`run_battery.py` side: the arm is driven **unconditionally** inside the r66
clause-surface meta — `sf_mid, sf_mid_text = surface_run("surface_midlineforge",
["--spawn-midlineforge"], "DESCENDANT_PIPE_MIDLINE write_ppid=")` at `:1706-1708`.
The meta is *not* behind an `args.*` gate (unlike `--probe-stream-attribution` at
`:2199`); it runs in every battery. Splice detection: `midline_spliced` at
`:1725-1728` (line containing both `"...expected "` and the MIDLINE error);
discriminations `:1983-1993` (`_spliced`, `_signature_destroyed`, `_rejects`,
`_counterfactual_defeated`, `_write_pre_death`); meta row append `:2030-2041`
(`arms: [sf_allow, sf_split, sf_seam, sf_mid]`).

**Ladder slot (author):** the only change the .gd needs is parameterizing
`sleep 0.08` at `:159` — e.g. `--midline-offset-ms=<n>` parsed in `_initialize`
(no `key=value` flag precedent exists in these fixtures — all are bare `in
user_args` checks; a prefix-parse via `begins_with` would be a first, or use
discrete flags). Keep bare `--spawn-midlineforge` = 80ms so the existing arm
record stays byte-stable. Battery side: additional `surface_run` calls with the
extra flag. Since the clause-surface meta is unconditional, "opt-in probe path
only" argues for a new flag-gated block (e.g. `--probe-midline-ladder`) or
gating the ladder inside the surface meta; an unconditional addition changes
every future `verdicts.json` (new results rows + new discriminations).

**Caution on discrimination reuse:** the five `midlineforge_*` discriminations
assume the in-window outcome. My measured misses (below) show all three of
`_spliced`/`_signature_destroyed`/`_counterfactual_defeated` flip to False on a
post-gap write — ladder arms need their own verdict fields, not the existing
names.

## (2) Measured window — the ladder already run (scratch receipts)

I spiked it in scratch (`corpus/live/r68-scout/proj/` = fixtures copy +
instrumented variant; env-var sleep, epoch-ms anchors on both clocks, `date
+%s%3N` in the descendant). **3 reps per offset, ±1ms jitter, deterministic
order within a rep:**

| declared sleep | measured write_rel_head | outcome (all reps) |
|---|---|---|
| 0 ms   | +2 ms   | SPLICE — `expected DESC_WRITE_MS=…`/ERROR mid-head-line, `signature` orphan line, sig destroyed |
| 40 ms  | +42 ms  | SPLICE |
| 80 ms  | +82 ms  | SPLICE (matches every shipped receipt) |
| 120 ms | +122 ms | SPLICE |
| 160 ms | +162-163 ms | SPLICE |
| 200 ms | +202 ms | MISS — `expected signature` intact line; ERROR/write_ppid land **after** tail; still `write_ppid==godot_pid` (pre-death, post-gap) |
| 240 ms | +242 ms | MISS — same shape |
| 300 ms | +302 ms | MISS — and at ~300ms the write can land **post-death**: observed `write_ppid=1573` (subreaper) in the early-spawn probe run `corpus/live/r68-scout/` — the arm's pre-death provenance flips at large offsets |

So the measured bound on this host: **splice iff write-arrival ∈ [head_flush +
~0, tail_flush) — in sleep-offset terms [0, ~198ms)**: every ladder offset ≤160
lands inside; the declared 240 cleanly misses. The **lo edge is a floor**: bash
fork+exec+`date`/`read /proc` latency ≈ +2ms constant (measured `sh -c 'sleep
0'` ≈ 0.95ms wall; write_rel_head ≈ sleep + 2ms across all 8 offsets), so even
`sleep 0` lands +2ms into the gap. A *pre-head* write is not expressible from
this arm on this host — even respawning the descendant at `:131` (before
`godot_pid` print, `--early-spawn` variant) with sleep 0 still lands inside.
The falsified-claim shape would be: if any in-{0..160} offset misses or 240
splices, the [lo,hi) bound differs from measured here.

Window-edge physics on this host (`/usr/bin/sh` → **bash**; 32 CPU; monotonic
clock res 1ns):

- **gap width**: `OS.delay_msec(200)` measured head→tail 200-201ms — overshoot ≤1ms.
- **write latency floor**: +~2ms constant (bash startup + `read /proc/self/stat` + printf).
- **read-loop tick**: `communicate(timeout)`/poll drains continuously — chunk arrivals
  ~1-2ms apart in my incremental reader; NOT a bound.
- **pipe drain**: 64KiB buffer, writes are ~45-90B — atomic under PIPE_BUF(4096), ordering pure.
- **flush behavior**: incremental reads show head bytes hit the pipe at print time
  and tail bytes ~200ms later — the pipe-visible window ≈ the wall-clock gap.
- **miss signature in the record**: post-gap writes leave `signature_observed=True`,
  `midline_spliced=None`, ERROR as own line in `output_lines` after `signature`;
  ordering distinguishes post-tail miss from a (here unreachable) pre-head miss.
  `surface_run` already captures everything needed: `signature_observed`,
  `error_lines`, `write_ppid` vs `godot_pid`, `output_lines` order.

## (3) Receipt-shape upgrade slots — divergence_table + dual_classify

`divergence_table` built at `run_battery.py:2377-2384`. Row shapes today
(observed byte-for-byte in
`corpus/live/r67-scribe/runs/20261014T095922857280Z/stream-attribution-verdicts.json`):

- pair rows `:2378`: `{"case": name, **dual}` → `{case, merged_allowlist, stream_allowlist, merged_classification, stream_classification, divergent}`
- arm rows `:2379-2384`: `{case, merged_allowlist, stream_allowlist, merged_classification, stream_classification, divergent}` (explicit projection)

`divergent_clause` slots per-row at `:2378-2384`. Clause assignment from the
declared taxonomy `{exit,signature,error_scan,blob,allowlist_shape}` (evidence:
`sd_discriminations` `:2385-2503`):

| case | divergent | clause | why |
|---|---|---|---|
| stream_accept | F | null | concordant |
| stream_reject | T | `error_scan` | non-ERROR: stderr line trips streams' stderr sweep only (:2478-2481) |
| streamdiv_stdout_error | T | `error_scan` | stdout ERROR: invisible to streams (:2389-2395) |
| streamdiv_stderr_error | F | null | concordant control (:2400-2414) |
| streamdiv_stderr_structured | T | `allowlist_shape` | structured entry merged-only (:2418-2431) |
| streamdiv_sig_on_stderr | T | `signature` | sig on stderr: merged-anywhere vs stdout-bound (:2436-2445) |
| streamdiv_seam_error | T | `error_scan` *(or `blob`)* | phantom ERROR: line exists only post-merge; diverging *clause* is the line-scan — but family is seam fabrication; author picks semantics |
| streamdiv_seam_script | T | `blob` | fabricated SCRIPT ERROR: token, merged-only (:2460-2467) |
| streamdiv_seam_sig | T | `signature` *(or `blob`)* | signature contiguous only in merged (:2468-2474) |
| (exit) | — | `exit` never diverges | both classifiers take identical code/error first (:176 vs :181) |

`sha256(raw_stdout)+sha256(raw_stderr)` per dual_classify record: slot inside
`dual_classify` `:2281-2292` (`return {…}` — add e.g. `"stdout_sha256":
hashlib.sha256(so.encode()).hexdigest()`; `hashlib` already imported, used at
`:309`). Propagation is automatic to: `sd_pair_dual` (:2332-2338) → table pair
rows via `**dual`; `sd_reclass` (:2354-2374); arm records via
`record.update(dual_classify(…))` at `:2324`. The arm table rows at `:2379-2384`
pick explicit keys — sha fields do *not* propagate there unless added
(deliberate choice for author). Same-input gate check: equal `stdout_sha256`+
`stderr_sha256` between a record's reclassifications proves identical captured
input; `divergence_rows_match_expectation` (:2488-2496) reads only
`case`/`divergent` — adding keys is gate-safe. Artifact JSON changes only under
`divergence` — "prior rows + surface meta byte-stable" unaffected.

## (4) Existing midlineforge receipts to diff against

32 `verdicts.json` files carry `surface_midlineforge` arms — **all** show
`signature_observed=False`, `write_ppid==godot_pid`, `elapsed_seconds` 0.53-0.87
(enumerated via `corpus/live/**/verdicts.json` scan). Canonical diffs:

- `corpus/live/runs/20261014T053603255626Z/verdicts.json` (sha256 `d8db0344…`,
  HEAD-era run): spliced line `DESCENDANT_PIPE_PROBE: expected ERROR:
  DESCENDANT_PIPE_MIDLINE forged splice`, elapsed 0.709
- `corpus/live/r68-baseline/runs/20261014T104854073132Z/verdicts.json` +
  `…T105014927352Z` (this round's frozen baseline receipts)
- `corpus/live/r68-reviewer/runs/20261014T104813737103Z`, `…T105018887735Z`
- r66 provenance set: `r66-author/runs/20261014T051140112142Z`,
  `r66-boundary/runs/20261014T051400354771Z`, `r66-reviewer/runs-postdiff/…`,
  `r66-simplifier/runs-author/…`, `r66-verifier/runs/…`
- stream artifact for receipt-shape diff: `corpus/live/r67-scribe/runs/
  20261014T095922857280Z/stream-attribution-verdicts.json` (r67 landed shape)

Battery invocation (r67 precedent): `python3 corpus/fixtures/run_battery.py
--godot /usr/bin/godot --runs corpus/live/r68-<seat>/runs` (+ opt-in flags:
`--probe-failing --probe-unrelated-error --probe-export-launch
--probe-godot-error --probe-stream-attribution --probe-crash-exit
--probe-timeout`).

## Gotchas recorded for the author lane

1. **My first raw sweep was self-corrupted**: `sed s/sleep 0.08/…` on the live
   copy — after the 0ms run rewrote it to `sleep 0`, every later "offset" stayed
   `sleep 0` (all six off*.out files are offset-0 runs; pids differ, content
   identical). Keep `proj/descendant_pipe_probe.gd` restoration discipline;
   the env-param sweep (`t_*.out`) is the trustworthy ladder.
2. **Ladder records must key off write-arrival, not the requested offset** —
   the +2ms constant means "offset" in record should carry both the declared
   sleep and (ideally) a measured write-vs-head delta; the current arm's record
   has no timestamp fields at all — `elapsed_seconds` only. If the author wants
   measured edges, in-record timing anchors (or an epoch write like my
   `DESC_WRITE_MS`) are the cheap instrument.
3. **Post-death crossover near the far edge**: beyond ~250-300ms the write lands
   after child exit — `write_ppid` flips to the subreaper (observed 1573) and
   `midlineforge_write_pre_death`-style checks change meaning.
4. `OS.get_cmdline_user_args` bare-flag convention — no `key=value` precedent;
   `--midline-offset-ms=N` parsing needs `begins_with`+`split` or discrete flags.
5. `prior_meta_rows_stable_29_discriminations` (:1895-1900, :2018) anchors the
   r65 meta at 29 discriminations — unrelated to ladder but shows the meta's
   self-pinning idiom the author may mirror for per-offset verdicts.
