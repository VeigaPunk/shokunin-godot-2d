# game-dev-2d round 72 — scribe report (seat: scribe, host: devin)

Declared lane axis (dispatch brief `.ufo/waves/shokunin-train-20261101-w12/
tasks/g2d-scribe.txt`, verbatim):

> ROUND 72 — 2d lane. REORDER FABRICATION (xconnector X1 — the composed
> mechanism). Evidence: `.ufo/waves/shokunin-train-20261101-w11/
> xconnector.md` — fd1-inheritance x block-buffering = reorder fabrication:
> descendant bytes land BEFORE the parent's earlier buffered bytes on
> buffered-Python runtimes (demonstrated on host: `INJECTEDHEAD  TAIL`;
> `-u`/`flush=True` restores midline splice). MOVE (depth): add `reorder`
> arm to pygame_probe + battery cases — a spawned descendant writing into
> inherited fd1 mid-window; pin: buffered child -> prefix/reorder topology;
> flushed/-u child -> midline splice (Godot/LOVE topology). Claim: the
> fabricated byte ORDER is a language-layer property (buffering mode), the
> seam is spawn-layer — composition, two mechanisms, one window family.
> SCRIBE: knowledge note + LOG/SCORECARD drafts; mechanism not narrative.

Scribe duty per lane practice (r76–r80 precedent, no r72 addendum beyond the
brief's draft line): independently re-run the round's declared claim shape
under `corpus/live/r72-scribe/` with this seat's OWN harness — raw-pipe
reorder cells plus battery-grammar parse-survival cells — verify byte-stability
of r71's 36 cases on the pre-landing tree, draft the knowledge note + LOG +
SCORECARD entries. Report-only; not the judge. LEAF: no subagent dispatch, no
git mutations; write scope = this report + `corpus/live/r72-scribe/` only
(one incident: an accidental tracked-file delete restored byte-identical from
HEAD, recorded verbatim below).

Terminology used below (per the brief): **child** = the Python process whose
piped stdout the reader captures (the tracked fixture's role; buffered by
default, `-u`/flush variants collapse the window); **descendant** = the
spawned process writing into the inherited fd1 (`os.system`/`Popen` child);
**reader** = the pipe consumer (battery / this seat's driver).

## Landed state at measurement time

- HEAD `44127afed9b68a28bf671a195f85a4b4f37a2c57` (r71 report-last).
- Tracked fixtures = r71 rev 3, unchanged:
  `corpus/fixtures/pygame_probe.py` sha256
  `4d426a3ba6098186c8ef4d6c6cdf6e4e8ecd17dc7af3828ceb91ccb510bb4738`,
  `corpus/fixtures/pygame_battery.py` sha256
  `0a579819658ee9be9dbd3e6fb81414a036f712a5d03358c7b57a8481a2cec47f`;
  `git status --porcelain -- corpus/fixtures` empty at measurement
  (re-verified after the incident repair below).
- **The r72 author's tracked `reorder` arm landed during this seat's window**
  (first fixture change observed 14:42:58 UTC; final settle 14:48:26) and
  was **committed as `fee55631c1424de169f5b2d4f8af6d3cb9be0330`** at
  14:46:58 UTC ("r72: reorder fabrication arm — fd1-inheritance x
  stdio-withholding composition (xconnector X1)"); worktree clean for
  `corpus/fixtures` after the commit, committed tree byte-identical to the
  replayed worktree. Two observed revisions:
  - rev A (14:45:11): probe `1d95c3bc…`, battery `077af0b5…`, probe
    +100/0 — replayed 55/55 ×2 (`runs-landed1/2`).
  - rev B (14:45:44, final): probe
    `7c0f9c737cebacf29e6c21c4a01e3a84c8d2800fa373f73b5ca2c95ba53ac8e4`
    (+102/−1), battery
    `077af0b52daf38080a7f209eb908ac75824cefc4c4cd004ff6b6eb5ff0315d28`
    (+71/0) — replayed 55/55 ×2 (`runs-landed3/4`). The single modified
    line is `popen_arm` gaining `env=CHILD_ENV` (prior-arm env hygiene;
    behaviorally neutral on this host, where `PYTHONUNBUFFERED` is unset
    — prior-arm stability re-checked below).
  All pre-landing receipts above stay pinned to the r71 tree; the landed
  replay is its own section below (the rev-B replays ran after the commit,
  against blobs hash-verified equal to the committed tree). Watcher:
  `corpus/live/r72-scribe/watch.log` (15 s polls; fixture hash pair
  `06f80833f7c6…` constant until 14:42). Sibling reports `r72-critic.md`
  and `r72-boundary.md` landed during this seat's window and are cited in
  the converge section.
- Sibling scratch observed in flight (data, not relied on):
  `corpus/live/r72-{baseline,boundary,critic,reviewer,scout,simplifier,
  verifier}/`. Their overlapping measurements are cited in the
  converge section as seat evidence, pre-adjudication.
- Toolchain: CPython 3.14.7, `pygame 2.6.1 (SDL 2.32.72)`,
  `io.DEFAULT_BUFFER_SIZE = 131072` (r71-pinned,
  `pygame_battery.py:78`), Linux, SDL_VIDEODRIVER=dummy, piped (non-TTY)
  stdout throughout. All r72-scribe runs: exit 0, stderr empty.
- **Finalization note (added at write-out, 14:51 UTC):** the landed rev B
  was replayed green (55/55 ×2 + `PYTHONUNBUFFERED=1` control, section
  below) and the fixture hashes were re-checked immediately before this
  report was saved — unchanged from rev B (probe `7c0f9c73…`, battery
  `077af0b5…`, committed `fee5563`, worktree clean). The pre-landing
  receipts, the rev-A replay, and the rev-B replay are kept as separate
  provenance blocks; no receipt mixes the trees.

## Claim shape measured (own harness) — CONFIRMED pre-landing

Harness: `corpus/live/r72-scribe/reorder_parent.py` (child side; modes
`buffered | flushed | sleep_before_spawn | fill_before_spawn | popen_child |
popen_wait | ownpipe_control | hybrid_flush | arm_lines | arm_prefix |
arm_midline`, `--pygame` runs the same sequence inside an initialized
pygame/SDL-dummy process) + `reorder_driver.py` (reader: `Popen(stdout=PIPE)`
+ `select`/`os.read` chunk-timestamped raw capture; optional per-cell reader
stall). Byte layout is ground truth; `topology` is derived from marker
indices only.

| cell (captured child / HEAD-writer mode) | wire bytes (repr) | topology | reps |
|---|---|---|---|
| `buffered` | `'INJECTEDHEAD  TAIL\n'` (19 B) | **prefix_reorder** | 10/10 + 3/3 |
| `unbuffered_u` (`-u`) | `'HEAD INJECTED TAIL\n'` (19 B) | **midline_splice** | 10/10 + 3/3 |
| `flush_inside` (`sys.stdout.flush()` before spawn) | `'HEAD INJECTED TAIL\n'` | **midline_splice** | 10/10 + 3/3 |
| `env_unbuffered` (`PYTHONUNBUFFERED=1`) | `'HEAD INJECTED TAIL\n'` | **midline_splice** | 3/3 |
| `sleep_before` (0.30 s between head write and spawn) | `'INJECTEDHEAD  TAIL\n'` | **prefix_reorder** | 10/10 + 3/3 |
| `popen_wait` (descendant awaited) | `'INJECTEDHEAD  TAIL\n'` | **prefix_reorder** | 10/10 + 3/3 |
| `popen_child` (descendant NOT awaited) | `'HEAD  TAIL\nINJECTED'` | post_tail (race lost) | 10/10 + 3/3 |
| `ownpipe_control` (descendant stdout=PIPE) | `'HEAD  TAIL\n'` (11 B) | no-injection | 3/3 |
| `pg_buffered` (pygame process) | `'INJECTEDHEAD  TAIL\n'` | **prefix_reorder** | 10/10 + 3/3 |
| `pg_unbuffered` | `'HEAD INJECTED TAIL\n'` | **midline_splice** | 10/10 + 3/3 |
| `pg_flush` | `'HEAD INJECTED TAIL\n'` | **midline_splice** | 3/3 |
| `pg_sleep_before` | `'INJECTEDHEAD  TAIL\n'` | **prefix_reorder** | 3/3 |
| `pg_popen_wait` | `'INJECTEDHEAD  TAIL\n'` | **prefix_reorder** | 3/3 |

Verdict: the declared pin holds on this host, pre-landing —
**buffered child → prefix/reorder; `-u`/`flush`/`PYTHONUNBUFFERED` → midline
splice** — and it reproduces inside an initialized pygame process, not only
under bare `python3`. The midline shape is the Godot/LOVE topology
(cross-reference: LOVE splice probe `corpus/live/r70-critic/splice_probe/
main.lua:26-29` — `io.write` head, `io.stdout:flush()`, gap, `io.write`
tail; Godot midlineforge arm `corpus/fixtures/descendant_pipe_probe.gd`).
The two topologies are produced by the same seam and the same descendant
command; only the captured process's (fd1 owner / HEAD-writer) stdio mode
differs — the composition claim (writer's stdio mode picks topology, spawn
layer supplies the seam) is supported as stated, with the referent named
per critic F1.

## The window is byte-bounded, not wall-time

- `sleep_before`: head bytes written at t≈0, descendant spawns at +300 ms,
  writes into fd1; the **first readable bytes on the pipe are the
  descendant's** (~310.4–313.1 ms, 10/10), and the child's `HEAD…TAIL`
  surface only at exit flush (~0.1–0.2 ms later). The head was invisible
  for >300 ms — the window tracks buffer lifetime, not wall-ms. This is the
  same conclusion r71 reached from the other direction (bound =
  `io.DEFAULT_BUFFER_SIZE` = 131072 on this build).
- `fill_before` (140 000-byte unflushed write before the awaited spawn):
  the crossing write flushes **fully** before the descendant's write
  (140 005 bytes delivered in one ~10 ms burst: 62 181 + 65 536 + 12 288 B
  chunks; `INJECTED` at byte 140 005, 3/3). So a plain crossing write
  *closes* the window before an awaited descendant runs — no reorder.
- `hybrid_flush` (xconnector prediction (iii) — descendant writes while a
  crossing write is in flight): with the reader stalled 150 ms after the
  first chunk, the child's 400 000-byte write blocks and the descendant's
  delayed write lands **inside it**: `INJECTED` at byte 195 205 of
  400 019, with 204 800 fill bytes after it (3/3, identical offset). A
  hybrid/interleaved topology is real — but it requires a *blocked* flush
  (slow/stalled reader); with a prompt reader the fill completes first
  (`fill_before`).

## Seam pins and the ordering race (design-relevant)

- **fd1 inheritance is the seam**: `ownpipe_control` — the same descendant
  with `stdout=PIPE` writes nothing into the child's stream (wire =
  `HEAD  TAIL\n`, no injection). Corroborated in flight by the scout's
  `readlink /proc/self/fd/1` identity cell (`corpus/live/r72-scout/receipts/
  mechanism_cells.txt`, C2: parent and descendant share `pipe:[…]`).
- **Await the descendant**: an unawaited `Popen` loses the ordering race
  deterministically on this host — `HEAD  TAIL\nINJECTED` (post_tail)
  **10/10**, because the child's exit flush reaches the pipe before the
  spawned process writes; `Popen(...).wait()` / `os.system` → reorder
  10/10. Any arm that spawns without waiting will measure post_tail, not
  reorder. (Scout's C3/C4 independently: 3/3 `R-HEAD|R-TAIL|R-INJ`.)
- **Env trap**: `PYTHONUNBUFFERED=1` in the child's env collapses the
  buffered cell to midline 3/3 — the tracked probe already strips it for
  its withhold children (`pygame_probe.py:59`); the reorder arm must do the
  same or the buffered pin is env-fragile.
- **Flush trap in-fixture**: the tracked probe's `emit()` prints every ARM
  line with `flush=True` (`pygame_probe.py:62-64`). A reorder arm that
  emits its head bytes through `emit()` would collapse its own window by
  construction; the head/tail markers need a deliberate non-flushing write
  path.

## Parse-survival / verdict-integrity cells (battery grammar)

`parse_hazard.py` feeds the captured stream to the **tracked battery's own**
`parse_arms` (imported read-only from `corpus/fixtures/pygame_battery.py:
120-129`; per-arm `dict.update`, i.e. last-wins) and to a first-wins
line-streaming convention, over three battery-grammar streams:

| cell | wire stream (repr) | tracked `parse_arms` | first-wins | shape |
|---|---|---|---|---|
| `arm_lines` (buffered; descendant emits a complete ARM line first) | `'PYGAME-ARM order \| seq=2 …\nPYGAME-ARM order \| seq=1 …\nPYGAME-ARM order \| seq=3 …\n'` | `{seq: 3, marker: parent_tail}` | `{seq: 2, marker: descendant}` | both parse; **attribution diverges by convention** |
| `arm_prefix` (buffered; descendant bytes without newline precede the withheld line) | `'INJECTEDPYGAME-ARM order \| seq=1 …\nPYGAME-ARM order \| seq=2 …\n'` | `{seq: 2, …}` — seq=1 line **lost** (regex fails) | same | **line loss** |
| `arm_midline` (flushed; ARM line split across the spawn) | `'PYGAME-ARM order \| seq=1INJECTED marker=parent_head\n'` | `{seq: "1INJECTED", …}` | same | **value corruption** (parseable, payload wrong) |

Reading: the post-exit battery (`capture_output=True`,
`pygame_battery.py:108`) is order-insensitive for distinct keys and
convention-stable, but the reordered stream (i) can flip duplicate-key
attribution depending on merge convention, (ii) can destroy a prefixed ARM
line, (iii) can corrupt a split line's values. xconnector's hazard class
("any future streaming parser of ARM lines over a pipe can see reordered
output on Python runtimes", `xconnector.md:66-69`) is measurable in the
fixture's own grammar; the tracked battery today observes none of it
because it parses post-exit and last-wins. Boundary's in-flight
`capture.json` shows the same loss shape (`capture_buffered`:
`'INJHEAD PYGAME-ARM reorder | x=1\nTAIL\n'`, `arm_line_parseable=false`).
The script was invoked twice (before/after the bytecode-write fix) with
identical cell output; `parse-hazard.json` holds one run, exit 0.

## Prior-row byte-stability (pre-landing tree)

- `python3 corpus/fixtures/pygame_battery.py --runs corpus/live/r72-scribe/
  runs-pre1` → **36/36 PASS**, exit 0, `launch_ok=True`, done marker;
  receipt `runs-pre1/pygame-20261014T143704019838Z/verdicts.json`.
- same → `runs-pre2/pygame-20261014T143712579983Z/verdicts.json`:
  **36/36 PASS**, exit 0.
- `compare_prior_rows.py` on the two runs: 24 differing fields, **all**
  wall-clock/timing (`_ms`, `hz`, `fps`, `dt_*`); **0 non-volatile
  differences**; normalized stream sha256 identical
  `fe03bf63e5feb99b45769072d02de74cf590e3ffca2ff1710b729abf56e49190`
  (raw hashes differ only through those volatile fields:
  `e9a15adc…` vs `99503c42…`). So "prior rows byte-stable" holds in the
  lane's convention: verdicts, exact pins and all non-jitter fields
  unchanged from r71 rev 3.
- Godot/LOVE batteries not re-run by this seat (their fixtures are not
  referenced by the pygame runner; the author's diff is pygame-scoped —
  `run_battery.py`, `love_battery.py`, `love_probe/` untouched by
  construction). Stated as a residual gap, not a claim.

## Landed diff replay (author's r72 arm)

Diff (committed `fee5563`; final rev B):
`pygame_probe.py` +102/−1 (docstring arm list; `REORDER_SYNC`/
`REORDER_FLUSH`/`REORDER_LATE` child programs; `reorder_arm()` reading
the piped child to EOF and classifying `prefix_reorder | midline_splice |
append` by marker byte order; five `reorder_*` cells; `reorder_self`
putting raw `REORDER-HEAD/CHILD/TAIL` markers on the probe's own fd1;
plus the one modified line `popen_arm(..., env=CHILD_ENV)`),
`pygame_battery.py` +71/0 (18 new CASES rows; `RAW_CASES` model +
raw-wire classifier for `reorder_self`; `run_process` now pops
`PYTHONUNBUFFERED` for the probe run). Rev A was probe +100/0; the rev A→B
delta is exactly the `popen_arm` env line.

My replay on the landed tree (own `--runs`, pre-receipts untouched):

- rev A: `… --runs corpus/live/r72-scribe/runs-landed1` → **55/55 PASS**
  (`runs-landed1/pygame-20261014T144529449571Z/verdicts.json`); same →
  `runs-landed2/pygame-20261014T144538650196Z/verdicts.json` **55/55**.
- rev B (final): `… --runs …/runs-landed3` → **55/55 PASS**, exit 0
  (`runs-landed3/pygame-20261014T144832830788Z/verdicts.json`); same →
  `runs-landed4/pygame-20261014T144841834684Z/verdicts.json` **55/55**,
  exit 0. These rev-B replays ran **after** the `fee5563` commit on the
  committed blobs (`git show fee5563:<path> | sha256sum` equals the
  worktree hashes above). (Author's own receipts, rev A tree:
  `corpus/live/r72-author/runs/pygame-20261014T1444{28,47,56}*/` —
  55/55 each.)
- **Env-swept control (my own):** `PYTHONUNBUFFERED=1 python3
  corpus/fixtures/pygame_battery.py --runs …/runs-landed-env1` → **55/55
  PASS**, exit 0 (`runs-landed-env1/pygame-20261014T144932688434Z/
  verdicts.json`) — the committed hygiene (probe-env strip + `CHILD_ENV`
  on `popen_arm`) holds against the ambient leak the commit message
  attributes to the r71 verifier (ambient leak flipped `popenbuf_l1_held`
  2/2).
- Emitted reorder rows in my rev-B runs (byte-identical topology to the
  independent harness above): `reorder_buf` `prefix_reorder
  head_at=8 injected_at=0 tail_at=14 wire_bytes=19 ret=0`;
  `reorder_unbuf`/`reorder_flush`/`reorder_env` `midline_splice
  head_at=0 injected_at=5 tail_at=14`; `reorder_late` `append head_at=0
  injected_at=11 tail_at=6`; `reorder_self` `fd1_isatty=False`.
- Raw-wire verification (my own read of `runs-landed3/…/probe.stdout.txt`):
  `REORDER-CHILD` at byte 1890 < `REORDER-HEAD` at 1904 < `REORDER-TAIL`
  at 1917 — the fabricated order on the probe's own fd1; battery
  `self_wire_reorders` PASS (the RAW_CASES predicate).
- Prior-row stability across the landing: `compare_prior_rows.py`
  pre1 vs landed3 — **0 non-volatile differences on the 36 r71 arms**
  (also 0 vs rev A's landed1); the 38 non-volatile diffs are exclusively
  new-arm keys (`reorder_{buf,unbuf,flush,env,late}` ×7 + `reorder_self`
  ×3); all other diffs are the usual `_ms`/`hz`/`fps`/`dt_*` volatiles.
  The rev-B `popen_arm` env line is behaviorally neutral here
  (`PYTHONUNBUFFERED` unset on this host) and the popen/popen_buf rows
  pass identically in pre1/pre2/landed3/landed4.
- The landed arm matches the critic's pre-landing corrections where they
  apply: the swept variable is the probe-spawned **captured child's**
  stdio mode (the fd1 owner of its pipe; descendant = the `os.system`
  grandchild) — the critic's correct reading of F1; `run_process` strips
  `PYTHONUNBUFFERED` (F3); `RAW_CASES` + newline markers off the ARM line
  (F4); pipe capture asserted by the battery path and `fd1_isatty=False`
  recorded for `reorder_self` (F2). The late cell (backgrounded
  descendant, parent held 600 ms) is my `popen_child`/post_tail shape —
  `append` here — i.e. the window-closed boundary, not a reorder.

## Converge/diverge vs sibling seats (pre-adjudication, cited as data)

- **reviewer** `corpus/live/r72-reviewer/reorder_probe_ref.out`: buffered →
  `reorder`, `-u`/flushed → `splice` (3 cells). CONVERGE.
- **boundary** — scratch `corpus/live/r72-boundary/cells.stdout.txt`
  (~40-cell grid, `cells.json`): `grid_pp_bufchild`
  `b'INJHEAD  TAIL\n'`; unbuffered/flush/env parents → `HEAD INJ TAIL`;
  extra edge classes beyond my set — `win_after_exit` (INJ after TAIL),
  `cross_hi` (INJ at 131 072), `paced2` (interleave at 126 005),
  `kill`/`os_exit` (head lost), `receipt_after` (`INJHEAD PYGAME-ARM
  reorder | x=1`). **Landed report** `reports/round-72/r72-boundary.md`
  (also written during this seat's window): 27 cells × 2 runs all
  `stable=True`; headline "composition claim CONFIRMED byte-exact"; F1 —
  topology class is set by the parent (probe) mode, the descendant's
  buffer only moves WHEN its bytes land (same referent pin as critic
  F1); F2 — byte topology alone cannot witness fabrication (an
  honestly-earlier child write is byte-indistinguishable; the arm needs a
  write-time witness, their fd2 `TRACE` method); F6 — the arm's own
  receipt line is unparseable for the battery's anchored parser unless
  newline-terminated. CONVERGE on all overlapping cells; F2/F6 are
  methodological additions my harness does not carry (see limits). Their
  labels ("INVERTED (fabricated reorder)" vs "splice (honest order)")
  differ from my topology names.
- **critic** — scratch `corpus/live/r72-critic/pg_reorder-matrix.json` (13
  rows): buffered parent → 6 `reorder` + 1 `append`; `u` parent → 4
  `midline` + 1 `append`; `envunbuf` → `midline`. `capture.json`
  parse-survival cell matches my `arm_prefix` loss shape. **Landed report**
  `reports/round-72/r72-critic.md` (written during this seat's window,
  14:38:38Z snapshot) adds four corrections this report carries forward:
  F1 (:37-80) — the brief's "buffered child" wording is ambiguous; the
  variable that flips topology is the **fd1-owner/HEAD-writer's** stdio
  mode, not the spawned descendant's (measured: `-u` descendant under a
  buffered writer still reorders 4/4 cells; buffered descendant under a
  `-u` writer still splices); my cells above sweep exactly the
  HEAD-writer mode and my terminology (child = captured process,
  descendant = spawned fd1 writer) is the critic's "correct reading" —
  no conflict with my measurements, a wording pin for the arm. F2
  (:82-107) — capture medium matters: pty capture → midline for both
  modes (line-buffered), file redirect ≡ pipe; window-closed cell
  (flush after TAIL + backgrounded writer at 0.3 s) → append. F3
  (:109-138) — the battery does not strip `PYTHONUNBUFFERED` for the
  **probe run itself** (`pygame_battery.py:104-117` builds env from
  `os.environ`); measured through the battery path: clean → reorder,
  `PYTHONUNBUFFERED=1`/`-u` → midline. F4 (:140-165) — the CASES model
  cannot express an order relation; needs a raw-order predicate +
  newline markers kept off the ARM line (matches my parse-hazard
  findings). F5 (:167-176) — `c_reorder.c` shows the same topology from a
  C writer: writer-side stdio buffering is the mechanism, CPython the
  lane's instance. F6 (:181-192) — patched-battery insertion 36/36 and
  `-u` control 36/36. CONVERGE on every overlapping cell; F1 is a
  correction to the brief's wording, not to the measured law.
- **scout** `corpus/live/r72-scout/receipts/mechanism_cells.txt`: C1 exit
  flush → `R-INJ|R-HEAD|R-TAIL`; C2 fd1 identity; C3/C4 unawaited
  descendant → `R-HEAD|R-TAIL|R-INJ` 3/3. CONVERGE (and matches my race
  pin).
- **baseline/simplifier/verifier**: scratch present (`frozen/`,
  `frozen-extract/`, landing-wait log, runs); no reports at write time.
  Not relied on.
- No conflicts found. All sibling items are in-flight seat evidence, not
  landed truth; the author's tracked arm was absent throughout.

## Incident (verbatim)

While cleaning up a byproduct, this seat ran `rm -rf
corpus/fixtures/__pycache__` in the lane repo. The directory contained an
**untracked** `pygame_battery.cpython-314.pyc` (created by my
`parse_hazard.py` importing the tracked battery) **and the TRACKED**
`run_battery.cpython-314.pyc` (committed with r71's report-last). The
command therefore deleted a tracked file — a write outside my scope. Repair
within seconds: `mkdir -p` + `git show HEAD:…pyc > …pyc` (no git mutation
command run; `git checkout/restore` not used). Result: `git status
--porcelain -- corpus/fixtures` and `git diff --stat -- corpus/fixtures`
empty; restored blob sha256 `13319b13c823a206074c36ad84b484f959c40fe2d00aca
0cc143d39caed3035e` identical to `git cat-file blob HEAD:…`. The import now
sets `sys.dont_write_bytecode = True` (and the incident-free re-run
confirmed no new pyc). Recorded unsoftened per seat card.

## Findings

1. **Claim confirmed pre-landing, deterministic.** Buffered captured
   process (fd1 owner/HEAD-writer) → prefix reorder 10/10 (+3/3);
   `-u` / `flush()` / `PYTHONUNBUFFERED=1` → midline splice 10/10 (+3/3);
   same two shapes inside an initialized pygame process 10/10 (+3/3). The
   fabricated byte ORDER tracks that process's stdio mode; the seam is
   fd1 inheritance. (Referent named per critic F1; my cells sweep the
   writer mode, not the descendant's.)
2. **Window = buffer lifetime, not wall-ms.** A descendant write at +300 ms
   still lands before the child's withheld head bytes (10/10); the first
   visible bytes are the descendant's.
3. **Crossing writes close the window before an awaited descendant runs**
   (140 000 B flushes fully; INJ at byte 140 005, 3/3). The interleaved
   "hybrid" shape (prediction iii) is real only while the flush is
   *blocked* (stalled reader): INJ at a fixed byte 195 205 inside a
   400 000 B write, 3/3.
4. **Ordering race pin:** an unawaited `Popen` descendant loses to the
   child's exit flush → post_tail 10/10; `wait()`/`os.system` → reorder.
   Any arm that spawns without awaiting measures the wrong topology.
5. **Env/flush traps:** `PYTHONUNBUFFERED` collapses the buffered cell
   (3/3); the fixture's `emit()` flushes every ARM line, so the reorder
   arm's head bytes must bypass it.
6. **Parse-survival:** three measured hazard shapes in the battery's own
   grammar — convention-dependent attribution on duplicate keys (last-wins
   parent vs first-wins descendant), ARM-line loss when prefixed, value
   corruption when split mid-line. Post-exit parsing is currently
   convention-stable; streaming consumers are not.
7. **r71's 36 cases are byte-stable on the pre-landing tree** (36/36 ×2,
   0 non-volatile diffs, normalized hash equal, fixtures = r71 rev 3).
8. **The landed arm reproduces the independent cells and stays green:**
   final rev B committed as `fee5563` (probe `7c0f9c73…` +102/−1,
   battery `077af0b5…` +71/0; the one non-additive line is
   `popen_arm(..., env=CHILD_ENV)`, an r71-verifier ambient-leak fix),
   55/55 PASS in my two rev-B replays plus the `PYTHONUNBUFFERED=1`
   env-swept control (plus two rev-A replays and the author's three),
   every reorder topology matching the independent harness
   cell-for-cell, the probe's own wire measured reordered
   (`REORDER-CHILD` 1890 < `REORDER-HEAD` 1904), and 0 prior-arm
   non-volatile diffs across the landing.

## Known limits

- **Provenance split.** The claim-shape receipts are pinned to the
  pre-landing r71 tree; the landed replay is a separate block on the
  landed rev-B hashes (probe `7c0f9c73…`, battery `077af0b5…`) and ran
  after the `fee5563` commit on the committed blobs. What remains for
  the verifier lane is an *independent* non-author post-commit audit
  (own harness on the committed tree), as usual.
- Host-bounded: CPython 3.14.7, pygame 2.6.1/SDL 2.32.72, Linux,
  SDL dummy, this host's pipe/spawn timing. The 131072 fill bound and
  300 ms sleep cell are properties of this build/host; topology labels are
  the stable quantities.
- This harness is not the tracked fixture: the child is a plain
  `python3`/pygame-init process; the battery's probe path (env, emit
  grammar, ARM parser) is only exercised through `parse_hazard.py`'s
  read-only import of `parse_arms`.
- `hybrid_flush` requires a constructed reader stall (150 ms); the
  default battery reader would not observe it.
- First-wins is my own convention, not a tracked parser; the
  "streaming consumer" is a hazard class, not a measured product.
- Timing fields are wall-clock volatile; no ms-precision claim beyond
  the chunk timeline recorded in the receipts.
- **Write-time witness.** My cells pin program order by construction
  (source: head write → spawn → tail write), so a byte reorder is
  fabricated by definition; the harness does not carry an in-stream
  write-time witness. Per boundary F2, byte topology alone is
  ambiguous (an honestly-earlier writer looks identical) — an in-fixture
  arm should witness write order (e.g. fd2 traces).
- **Capture medium.** All cells here use pipes (as does the tracked
  battery, `pygame_battery.py:108`). Per critic F2, a pty capture is
  line-buffered and yields midline for both modes — the "byte order is a
  language-layer property" claim is scoped to non-tty capture; file
  redirect ≡ pipe.
- **Window-family scope.** "One window family" = one withholding-interval
  family, not one closing edge: the splice window closes at the tail
  write (gap-relative, r69), the reorder window closes at the first
  flush/exit (buffer lifetime). No new constant belongs to this arm —
  `131072` stays the r71 provenance row only (critic's over-strong audit
  :194-207).
- **Mechanism owner.** Writer-side stdio buffering is the mechanism;
  CPython is this lane's instance (critic F5's `c_reorder.c` shows the
  same two topologies from a C writer). "Language-layer" in the claim
  means "the writing process's stdio mode", not "Python".
- No bpy/g3d X1 claim (sibling lane r81); no non-Linux claim; no
  production/gameplay claim.

## Draft: `corpus/lessons/r72-reorder-fabrication.md`

```markdown
# R72 — reorder fabrication: the fabricated byte ORDER is the withholder's stdio mode; the seam is fd1 inheritance (CPython 3.14.7 / pygame 2.6.1 headless)

Sources: `reports/round-72/r72-{author,critic,scribe,…}.md`;
`.ufo/waves/shokunin-train-20261101-w11/xconnector.md` §X1
(:31-69; host demo :44-50); scribe harness
`corpus/live/r72-scribe/{reorder_parent.py,reorder_driver.py,
parse_hazard.py,compare_prior_rows.py}` + receipts
`reorder-results-rep3.json` (45 runs), `reorder-results-rep10.json`
(80 runs), `parse-hazard.json`; r71 tree pins
`pygame_battery.py:78` (bufsize 131072), `:108` (post-exit capture),
`:120-129` (last-wins parse); LOVE splice reference
`corpus/live/r70-critic/splice_probe/main.lua:26-29`.

verified-at: 2026-10-14, CPython 3.14.7, pygame 2.6.1 (SDL 2.32.72),
Linux headless (SDL dummy), piped stdout. Pre-landing claim cells:
HEAD 44127af, fixtures = r71 rev 3 (`pygame_probe.py` 4d426a3b…,
`pygame_battery.py` 0a579819…). Landed-arm replay: probe 7c0f9c73…,
battery 077af0b5… (committed `fee5563`), 55/55 ×2 + env-swept control,
topologies matching the pre-landing cells.

## Mechanism

Two landed mechanisms compose in one window family:

- **Seam (spawn layer):** a spawned descendant inherits the child's fd1
  and writes straight into the kernel pipe (`os.system`/awaited `Popen`).
  With its own pipe (`stdout=PIPE`) it writes nothing into the stream —
  the seam is fd1 inheritance, not "a descendant exists".
- **Topology (writer's stdio layer):** the mode of the **fd1 owner that
  writes the head** decides WHERE the descendant's bytes land relative to
  the writer's own bytes (naming pin; critic F1: the spawned descendant's
  mode does not flip the topology — measured 4/4 cells):
  - block-buffered writer (default piped CPython): head bytes sit in
    userspace → descendant bytes land BEFORE them → **prefix/reorder**
    (`INJECTEDHEAD  TAIL`), 10/10;
  - `-u` / `flush()` / `PYTHONUNBUFFERED=1`: head is on the wire before
    the spawn → **midline splice** (`HEAD INJECTED TAIL`), 10/10 —
    the Godot/LOVE topology.
  Scope: non-tty capture (a pty is line-buffered → midline for both
  modes, critic F2); writer-side stdio buffering is libc-level, not
  Python-specific (C writer reproduces both topologies, critic F5).
- **Window = buffer lifetime, not wall-ms:** a descendant write at +300 ms
  still precedes the writer's head bytes (10/10); fill (131072 B on this
  build), explicit flush, or exit closes the window. A crossing write
  flushes fully before an awaited descendant runs (INJ at byte 140 005,
  3/3); an interleaved hybrid appears only while a flush is blocked
  (stalled reader: INJ at byte 195 205 of a 400 000 B write, 3/3).
  Scoping: this is one withholding-interval family with the splice
  window, but the closing edges differ — splice closes at the tail write
  (gap-relative, r69), reorder at the first flush/exit; do not introduce
  a new constant (131072 remains the r71 provenance row).
- **Ordering race:** an unawaited descendant loses to the child's exit
  flush → `HEAD  TAIL\nINJECTED` (post_tail, 10/10). Await it.
- **Parse consequences (battery grammar, `parse_arms`):** reordered
  streams can (i) flip duplicate-key attribution by merge convention
  (tracked last-wins → parent tail; first-wins → descendant),
  (ii) destroy a prefixed ARM line, (iii) corrupt a split line's value
  (`seq=1INJECTED`). The post-exit battery is order-insensitive for
  distinct keys; a streaming consumer is not.

## Authoring consequences

- Pin TOPOLOGY by byte order (marker indices), never by timing; the
  CASES key=value model needs a raw-order predicate for this (critic F4).
- Spawn the descendant awaited (`os.system`/`Popen.wait`) or the pin
  measures post_tail; keep reorder markers newline-terminated and off the
  ARM line so the ARM parse stays clean.
- Strip `PYTHONUNBUFFERED` for the buffered run at BOTH levels: the
  probe's own env (the battery builds it from `os.environ`,
  `pygame_battery.py:104-117`; critic F3) and the spawned child's env
  (`pygame_probe.py:59` does the latter); bypass `emit()` (it flushes)
  for the head/tail marker writes.
- For parse-survival pins, use distinct keys per line to keep the
  post-exit parser convention-stable, and keep the ARM line intact
  (avoid descendant writes mid-line).

## Recheck conditions

Interpreter/engine upgrade re-measures the fill constant
(131072 on 3.14; 8192 on ≤3.13) and the textio layer (8192 pending);
other runtimes (bpy `-b -P`) are the g3d r81 arm's check. The topology
mapping (buffered → reorder, flushed/-u → midline) is the portable
claim; the window constant is not.
```

## Draft: LOG.md round-72 entry

```markdown
## Round 72 — reorder fabrication (wave-12, xconnector X1 composition)

- Declared (dispatch brief): add a `reorder` arm to `pygame_probe.py` +
  battery cases — spawned descendant writing into inherited fd1
  mid-window; pin buffered child → prefix/reorder topology, flushed/-u
  child → midline splice (Godot/LOVE topology). Claim: the fabricated
  byte ORDER is a language-layer property (buffering mode), the seam is
  spawn-layer — two mechanisms, one window family. Insertion-only; prior
  rows byte-stable.
- Wave `shokunin-train-20261101-w12`: 2d lane leaf set
  `reports/round-72/r72-{author,baseline,boundary,critic,reviewer,scout,
  scribe,simplifier,verifier}.md`, disjoint `corpus/live/r72-*/`.
- At first measurement HEAD 44127af, fixtures = r71 rev 3
  (`4d426a3b…`/`0a579819…`), corpus/fixtures clean; the author's tracked
  arm landed mid-window in two revisions (rev A 14:45:11 probe
  `1d95c3bc…` +100/0; rev B final 14:45:44→settled 14:48:26, probe
  `7c0f9c73…` +102/−1, battery `077af0b5…` +71/0, the single modified
  line `popen_arm(..., env=CHILD_ENV)` — r71-verifier ambient leak;
  watcher `corpus/live/r72-scribe/watch.log`) and was **committed as
  `fee5563`** at 14:46:58 UTC. Scribe replay: rev A 55/55 ×2, rev B
  55/55 ×2, rev B under `PYTHONUNBUFFERED=1` 55/55 (author's own 55/55
  ×3); 0 prior-arm non-volatile diffs across the landing;
  probe-own-wire reorder verified (`REORDER-CHILD` 1890 <
  `REORDER-HEAD` 1904, RAW_CASES PASS).
- Scribe independent harness (own raw-pipe reader; 45 + 80 runs, all
  exit 0; `parse-hazard.json`): buffered child → `INJECTEDHEAD  TAIL`
  10/10 (+3/3); `-u`/flush/PYTHONUNBUFFERED → `HEAD INJECTED TAIL`
  10/10 (+3/3); same inside pygame 10/10 (+3/3). Window = buffer
  lifetime: descendant write at +300 ms still first (10/10); 140 000 B
  crossing write flushes fully before an awaited descendant (INJ at
  140 005, 3/3); blocked-flush hybrid INJ at 195 205 of 400 000 B, 3/3.
  Seam pins: own-pipe control → no injection; unawaited Popen → post_tail
  10/10 (await or lose). Parse hazards measured in battery grammar:
  convention-dependent duplicate-key attribution, prefixed-line loss,
  split-line value corruption. Landed arm's emitted topologies match
  cell-for-cell (`reorder_buf` prefix_reorder; `-u`/flush/env
  midline_splice; `reorder_late` append).
- r71 byte-stability: 36/36 ×2, 0 non-volatile field diffs, normalized
  stream sha equal (fe03bf63…) on the pre-landing tree.
- Sibling in-flight convergence (seat evidence, pre-adjudication):
  reviewer ref cells, boundary ~40-cell grid, critic matrix + capture,
  scout fd1/race receipts — same two topologies, no conflicts. Critic's
  landed `r72-critic.md` corrections for the arm: name the HEAD-writer
  (fd1 owner) as the pinned variable (F1); record/assert the capture
  medium, pipe only (F2); strip `PYTHONUNBUFFERED` for the probe run too
  and record `probe_stdio` (F3); add a raw-order predicate with
  newline markers off the ARM line (F4); scope the mechanism as
  writer-side stdio, not Python (F5).
- Incident (verbatim): cleanup `rm -rf corpus/fixtures/__pycache__`
  removed the tracked `run_battery.cpython-314.pyc`; restored
  byte-identical from HEAD blob (`13319b13…`) within seconds; imports now
  set `sys.dont_write_bytecode`.
- Non-author verification + per-axis verdicts: TBD (Sol
  `reports/round-72/r72-adjudicator.md`). Bounded: CPython 3.14.7 +
  pygame 2.6.1, Linux headless, this host; topology labels portable,
  window constants not. Work commit `fee5563`; report-last follows.
```

## Draft: SCORECARD.md round-72 entry (for the report-last writer)

```markdown
## Round 72 verdict — 2026-10-14 (wave-12; adjudicator verdicts TBD)

| axis | draft verdict | evidence (draft) |
|---|---|---|
| depth | improved (draft) | X1 composition pinned pre-landing: buffered child → prefix/reorder (`INJECTEDHEAD  TAIL`, 10/10), -u/flush/env → midline splice (`HEAD INJECTED TAIL`, 10/10), reproduced inside pygame (10/10); window byte-bounded (descendant write at +300 ms still first; 131072 fill/exit/flush close it); seam pins (fd1 inheritance necessary; awaited spawn required — unawaited Popen → post_tail 10/10); blocked-flush hybrid measured (INJ at 195 205 of 400 000 B, 3/3); parse-survival shapes measured in the battery's own grammar. |
| coverage | improved (draft) | first composition of the two landed mechanisms (spawn × writer-stdio) on the third runtime; tracked `reorder` arm + battery cases landed mid-window (5 child-mode cells + `reorder_self` raw-wire cell + RAW_CASES model; 55 cases; scribe replay 55/55 ×2 rev B + 55/55 ×2 rev A + 55/55 under `PYTHONUNBUFFERED=1`; author 55/55 ×3), committed `fee5563` (rev A insertion-only; rev B's one modified line is the r71-verifier ambient-leak fix); sibling cell families in flight (boundary grid, critic matrix). |
| calibration | unchanged (draft) | r71 tree byte-stable pre-landing (36/36 ×2, 0 non-volatile diffs, normalized hash equal) and across the landing (0 prior-arm non-volatile diffs vs landed 55/55 ×2); no fixture edits by this seat; topology pins by byte order, not timing. |

Bounded: scribe pre-landing + landed-replay evidence (rev B committed as
`fee5563` mid-window; post-commit audit is the verifier lane's), CPython
3.14.7 / pygame 2.6.1 / Linux headless / this host; topology portable,
window constants build-dependent. Sol verdict TBD.
```

## Artifact inventory (all under `corpus/live/r72-scribe/`)

| artifact | sha256 (prefix) | content |
|---|---|---|
| `reorder_parent.py` | `f0a9657a6a561594` | child-side modes incl. `--pygame`, hybrid, ARM-grammar cells |
| `reorder_driver.py` | `a5cd511c2f391d03` | raw-pipe reader, topology classifier, reps/only args |
| `parse_hazard.py` | `4354704b9aabdf8e` | tracked-parser vs first-wins over 3 grammar streams |
| `compare_prior_rows.py` | `54d75c8c8a77b69f` | volatile-field scrubber, normalized stream hash |
| `watch.sh` | `ed9d786880ce8328` | 15 s landing watcher (`watch.log`) |
| `reorder-results-rep3.json` | parent `f0a9657a…`, driver `a5cd511c…` | 45 runs, 15 cells × 3 |
| `reorder-results-rep10.json` | parent `f0a9657a…`, driver `a5cd511c…` | 80 runs, 8 headline cells × 10 |
| `reorder-results.json` | (superseded first pass) | 12 cells × 1 |
| `parse-hazard.json` | parent `f0a9657a…` | 3 grammar cells, both parser conventions |
| `runs-pre1/pygame-20261014T143704019838Z/` | — | tracked battery 36/36, exit 0 (pre-landing tree) |
| `runs-pre2/pygame-20261014T143712579983Z/` | — | tracked battery 36/36, exit 0 (pre-landing tree) |
| `runs-landed1/pygame-20261014T144529449571Z/` | — | landed battery 55/55, exit 0 (rev A) |
| `runs-landed2/pygame-20261014T144538650196Z/` | — | landed battery 55/55, exit 0 (rev A) |
| `runs-landed3/pygame-20261014T144832830788Z/` | — | landed battery 55/55, exit 0 (rev B, final) |
| `runs-landed4/pygame-20261014T144841834684Z/` | — | landed battery 55/55, exit 0 (rev B, final) |
| `runs-landed-env1/pygame-20261014T144932688434Z/` | — | landed battery 55/55 under `PYTHONUNBUFFERED=1`, exit 0 |
| `watch.log` | — | landing-surface transitions 14:35–14:50 |

Commands run by this seat (cwd `~/Projects/shokunin/game-dev-2d-shokunin`,
all exit 0 unless noted): `python3 corpus/live/r72-scribe/reorder_driver.py
--reps 3 --out reorder-results-rep3.json`; `… --reps 10 --only
buffered,unbuffered_u,flush_inside,pg_buffered,pg_unbuffered,popen_child,
popen_wait,sleep_before --out reorder-results-rep10.json`;
`python3 corpus/live/r72-scribe/parse_hazard.py`; `python3
corpus/fixtures/pygame_battery.py --runs corpus/live/r72-scribe/runs-pre1`
and `…runs-pre2`; `python3 corpus/live/r72-scribe/compare_prior_rows.py
runs-pre1/…/probe.stdout.txt runs-pre2/…/probe.stdout.txt`; `python3
corpus/fixtures/pygame_battery.py --runs corpus/live/r72-scribe/runs-landed1`
and `…runs-landed2` (rev A), `…runs-landed3` and `…runs-landed4`
(rev B, after the second landing); `compare_prior_rows.py
runs-pre1/… runs-landed3/…`; `sha256sum corpus/fixtures/pygame_probe.py
corpus/fixtures/pygame_battery.py`; incident repair `git show HEAD:…pyc >
…pyc` + `git status/diff` verification.
