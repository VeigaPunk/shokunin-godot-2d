# Round 69 scout report — midlineforge crossed GAP ladder (referent pin) + sha256(merged) receipt

Seat: scout, lane `game-dev-2d`, round r69. Canonical repo
`~/Projects/shokunin/game-dev-2d-shokunin` (brief worktree
`~/Projects/prymeagnt/game-dev-2d` resolves via `.shokunin/game-dev-2d`
symlink → this repo). All commands read-only on this host (devin). Scratch:
`corpus/live/r69-scout/`.

**Landing state at map time:** author is IN FLIGHT — `git status --porcelain`
shows `M corpus/fixtures/descendant_pipe_probe.gd` and
`M corpus/fixtures/run_battery.py` (uncommitted; `corpus/live/r69-author/`
already holds `battery-gapladder.stdout`). All line refs below are **HEAD
`aa94cb7`** (pre-landing); the author's working-tree diff was observed but not
reviewed. Observed uncommitted tokens: fixture flag `--midline-gap-ms=N`
(default 200), battery flag `--probe-midlineforge-gapladder`.

## (1) How `gap_ms` is expressed — and one-clock vs two-clock structure

`corpus/fixtures/descendant_pipe_probe.gd` (182 lines at HEAD; brief's
":129" is stale — it was the banner line at HEAD~5 / pre-r68 layout; current
anchors):

| what | HEAD line | bytes |
|---|---|---|
| arm flag | `:123` | `var midline_forge := "--spawn-midlineforge" in user_args` |
| banner (literal `200`) | `:136` | `print("DESCENDANT_PIPE_MIDLINE child=splice_target signature=halved gap_ms=200")` — **must become `+ str(gap_ms)` or receipts lie** |
| doc block | `:82-95` | documents "200ms gap" + `--midline-offset-ms` |
| offset flag parse | `:165-168` | `var midline_offset_ms := 80` + `begins_with("--midline-offset-ms=")` / `get_slice("=",1).to_int()` — the exact pattern the gap flag should mirror |
| descendant spawn (the OFFSET clock) | `:169-171` | `OS.create_process("/usr/bin/sh", ["-c", "sleep %d.%03d; read ppid; printf MIDLINE_ERROR\n; echo write_ppid=$pp"])` — **sleep lives INSIDE the spawned sh** |
| the GAP (the second clock) | `:179-181` | `printraw(MARKER_SPLICE_HEAD)` → `OS.delay_msec(200)` → `print(MARKER_SPLICE_TAIL)` |
| ordering | `:172-181` | `print spawned_pid` (:173) sits between spawn and head; halves emitted last; `quit(0)` :182 |

**Two processes, two clocks.** The offset clock starts at `sh` exec (≈
`OS.create_process` + fork/exec/sh-init, `:169`); the gap clock starts at the
head flush (`printraw`, `:179`), after `print spawned_pid` (:173). r68's
instrumented spike (`corpus/live/r68-author/spike/spike-results.json`, same
CLOCK_REALTIME domain) measured `write_rel_head = offset + 2..3ms` (offsets
0/40/80/120/160 → 2-3/42-43/82-83/122-123/162) and `gap = tail_ms − head_ms =
200–201ms` (delay_msec accurate ~1ms). Jitter ≤1ms across 33 spike + 18
ladder reps. So at the r69 fixed offset=80, **write arrival ≈ 82.5ms after
head flush** — the quantity the gap ladder compares against each gap.

## (2) Decidability at offset=80 — YES, decisively

Gap-relative model: fabrication iff `write_rel_head < gap` (tail flush at
≈gap). Absolute model: fabrication iff `write_rel_head < T_abs` — outcome is
**flat in gap** since arrival is fixed at ~82.5ms.

| gap_ms | arrival 82.5 vs tail | margin vs jitter≤1ms, skew~2.5ms |
|---|---|---|
| 50 | write ~32ms AFTER tail | relative→MISS by ~32ms — decisive; the ONLY rung below arrival |
| 100 | ~17.5ms inside | relative→FAB — smallest margin, still ~7× skew |
| 200 | ~117ms inside | FAB — reproduces r66 point sample / r68 fab cells (control) |
| 400 | ~317ms inside | FAB |
| 800 | ~717ms inside | FAB; child total ~1.35s ≪ `surface_bound=3.0` (`run_battery.py:1578`) |

The set {50,100} brackets the ~82.5 arrival; {200,400,800} tests persistence
at >>80. Range is sufficient — no extra rung needed; a boundary gap
(~80-85ms) would be jitter-racy and adds nothing.

**Provenance caveat (channel 2, do NOT gate verbatim):** r68's
`ladder_all_writes_pre_death` (`run_battery.py:2109-2111`) assumed
write<exit for all cells. At gap=50 the write (~82.5) lands ~32ms after the
tail flush; child exit = tail + exit-latency where exit latency is **>42ms**
(measured: all 3 r68 offset=240/gap=200 reps still `write_ppid==godot_pid`,
i.e. child alive ≥242ms with tail at ~200). At gap=50 exit ≈ >92ms → write
likely STILL pre-death, but the margin is ~10ms — racy under load. Expected:
`write_ppid==godot_pid` for all five cells, with a flip at gap=50 being
consistent (post-death post-tail write), not a falsifier. Gate pre-death
only on cells where it's load-bearing ({100..800}), record it at 50.
`descendant_alive_at_return` is `os.kill(pid,0)` existence (`:633`) — zombie
semantics (Godot never reaps create_process children mid-run); secondary
channel only.

**Order refinement available for free:** `surface_run` records
`output_lines` (`:1660`). At a gap=50 MISS, the standalone
`ERROR: DESCENDANT_PIPE_MIDLINE forged splice` line sits **after** the
intact signature line iff the write arrived post-tail (relative-consistent).
If a falsifier cell shows the ERROR line **before** the signature, the write
landed pre-head — a deferred-flush anomaly, not a post-tail miss. Line-index
discrimination distinguishes the two miss mechanisms.

## (3) Where `sha256(merged)` slots

One site covers all records — inside `dual_classify`'s return dict,
`run_battery.py:2522-2532`, adjacent to the r68 per-channel digests:

```python
"raw_merged_sha256": hashlib.sha256((so + se).encode()).hexdigest(),
```

This is `sha256` over the exact concat the merged classifier consumed at
`:2518` (`classify_process(code, error, so + se, …)`). The per-channel pair
cannot see concat ORDER: `so+se` and `se+so` share identical per-channel
digests — that is the r66 caveat (`reports/round-66/r66-author.md:215-216`,
"fixed `stdout + stderr` concat order … a consumer concatenating
stderr+stdout would fabricate a different phantom"). The merged digest pins
order.

Coverage: all 15 records get the field from the single edit — 2 pair rows
(`sd_pair_dual`, `:2572-2578`), 7 arm records via `record.update` in
`streamdiv_arm` (`:2564`), 6 allowlist reclassifications (`sd_reclass`,
`:2594-2614`). **Projection follow-ups needed:**
`divergence_table` arm rows (`:2619-2627`) enumerate keys explicitly — add
`"raw_merged_sha256": a["raw_merged_sha256"]` (pair rows spread `**dual`,
get it free). `dual_records_same_input_digests` (`:2775-2799`) can
self-validate: `a["raw_merged_sha256"] == sha256((a["raw_stdout"] +
a["raw_stderr"]).encode())` per arm, pair rows vs accept/reject raws, reclass
== source — same pattern as the existing per-channel checks. No external
consumers: `raw_*_sha256`/`divergence_table`/`dual_classify` appear nowhere
outside `run_battery.py` + reports/lessons (grep over repo). Additive field
→ prior dual rows byte-stable modulo it.

## (4) Predicted cell outcomes (author check table)

Detection per rep identical to r68 (`:2067-2072`): `spliced_line` = merged
line containing `"DESCENDANT_PIPE_PROBE: expected "` AND the MIDLINE error;
`fabrication_landed = spliced_line is not None`.

| gap_ms | gap-relative claim (`write<tail`, predicted) | absolute T_abs>~83ms | absolute T_abs<~83ms | signature_observed (rel) | inner_classification (all models) |
|---|---|---|---|---|---|
| 50 | **missed** | fabricated* | missed | True | False (standalone ERROR: line) |
| 100 | **fabricated** | fabricated | missed | False | False (dual-clause) |
| 200 | **fabricated** (control) | fabricated | missed | False | False |
| 400 | **fabricated** | fabricated | missed | False | False |
| 800 | **fabricated** | fabricated | missed | False | False |

\* fabricated at gap=50 is physically possible ONLY via deferred flush (tail
bytes not in pipe at ~82.5ms despite `print` at ~50ms) — itself the
falsifier: the bound is then not tail-flush-relative.

Row signatures: **N,Y,Y,Y,Y** = gap-relative CONFIRMED (upward-closed in gap;
single threshold crossing in (50,100] brackets ~82.5 — the mirror image of
r68's downward-closed offset set). **Y,Y,Y,Y,Y** = falsifier (persists at
gap << arrival → absolute/buffering bound). **N,N,N,N,N** = falsifier (fails
at gap >> arrival; also contradicts r68 — check environment). Any
nonmonotone or shifted-threshold pattern (e.g. N,N,Y,Y,Y) = neither clean
model — record actuals, follow-up needed. 3 reps/cell (r68 ladder size,
`:2057`) suffices: minimum margin ~17.5ms vs ≤1ms jitter.

Battery-side anchors for the new block: parser flag after
`--probe-midlineforge-ladder` (`:118`); sibling gated block at `:2043-2181`
reusing `surface_run` (`:1588-1661`, merged text `sf_out+sf_err` `:1612`)
with args `["--spawn-midlineforge", "--midline-offset-ms=80", <gap flag>]`;
per-cell `gap_ms` in the record (the fixed `midline_gap_ms=200` const at
`:2058`/`:2093` stays for the r68 offset ladder, which keeps default 200).
The unconditional r66 arm `sf_mid` (`:1707-1709`) passes bare
`--spawn-midlineforge` → default gap 200 → byte-stable.

## Flagless/surface baselines (counts verified at HEAD)

CASES list `:18-105` = **81** rows; unconditional meta rows at
`:515, :549, :688, :871, :1101, :1530, :2031` = 7 → **88 flagless**.
`sf_discriminations` (`:1914`) = **34 keys** — matches "flagless 88/88 +
surface 34/34". Current HEAD fixture shas:
`descendant_pipe_probe.gd` `5c5c629ac187b1…`, `run_battery.py`
`55314bb55b409e…` (working tree dirty — author's in-flight edits).

## Confidence / remaining unknowns

- High confidence: gap expression sites, two-clock structure (direct read +
  r68 instrumented spike), decidability margins, dual_classify slot.
- Moderate: gap=50 provenance (pre-death expected, ~10ms margin — treated as
  secondary, not gated).
- Unknown until the author lands: exact flag/record naming; whether
  `ladder_all_writes_pre_death` gets a per-cell relaxation; whether the
  ERROR-line-position refinement is picked up.
- Not measured by this lane: no fixture re-runs performed (mapping only).
