# r72 reviewer — reorder-fabrication arm, pygame lane (g2d, wave w12)

Seat: **reviewer** (LEAF, dispatched specialist; recommendation only — the
canonical Rust runtime is the sole judge). Host: devin — CPython 3.14.7
(`io.DEFAULT_BUFFER_SIZE` = 131072), `pygame 2.6.1 / SDL 2.32.72`.
Lane repo: `~/Projects/shokunin/game-dev-2d-shokunin`. Write scope: this
report + `corpus/live/r72-reviewer/` only; no tracked edits, no git
mutations.

Artifact reviewed: commit **`fee5563`** ("r72: reorder fabrication arm —
fd1-inheritance x stdio-withholding composition (xconnector X1)"),
two files: `corpus/fixtures/pygame_probe.py` (+102/−1),
`corpus/fixtures/pygame_battery.py` (+71/−0) (`git diff --numstat
44127af..fee5563`). The author's final pre-commit working revision
(snapshot 14:45:31Z, probe `7c0f9c73…`, battery `077af0b5…`) is
byte-identical to the committed blobs (`git show fee5563:<path> |
sha256sum` matches), so the replay below ran on the pre-commit bytes.

**`lsp` disclosure:** no language-server device on this host (`lsp`,
`pyright`, `basedpyright`, `pylsp`, `jedi-language-server`, `ruff-lsp`
all ABSENT from PATH; `pygls`/`jedi` not importable). Every
caller/definition claim below is a line-cited textual inspection,
recorded per seat card — not presented as semantic proof.

## Verdict summary

The landed arm resolves the round-72 move and the claim resolves on
replay: the fabricated byte ORDER is pinned as a property of the
fd1-owner's stdio mode (buffered → `prefix_reorder`; `-u` / flush /
`PYTHONUNBUFFERED=1` → `midline_splice`; post-window write → `append`),
the seam is the spawn layer (inherited fd1 via `os.system`), and the
composition reproduces on the probe's own wire (`reorder_self` +
`RAW_CASES`). Every author command I replayed resolves (V1–V9); no
functional defect found. Two low-severity record drifts (R1, R2) and two
INFO notes (R3, R4).

## Findings by severity

### R1 — LOW (open): author report counts / "insertion-only" claim do not match the landed commit

`r72-author.md:17` states the probe change is "+100 lines, insertion-only";
`:99` states "`git diff corpus/fixtures/` shows +171/-0 (pure insertions;
0 removed CASES rows)". The landed commit is **+173/−1** (`git diff
--numstat 44127af..fee5563`: probe 102/1, battery 71/0) — the `popen_arm`
signature line was replaced to pass `env=CHILD_ENV`
(`pygame_probe.py:93`). The report's "Landed changes" list never mentions
that change; it appears only in the commit message (citing the
r71-verifier defect). The "0 removed CASES rows" half is true — the
battery hunk is 71 insertions, 0 deletions and no `CASES` row changed.
Impact: evidence honesty at the report layer only; the artifact is
correct and the deviation is a verified defect remedy (V2). Same class as
r71 R1b (report text vs artifact drift). The scribe counts it correctly
(`r72-scribe.md:388`, "+102/−1").

### R2 — LOW (open, cross-artifact record): baseline case inventory off by one

`r72-baseline.md:23` and `:125` describe the landed battery as "54 CASES +
2 RAW_CASES". The landed shape is **54 CASES + 1 RAW_CASES = 55**
(`pygame_battery.py:140-142` holds one `RAW_CASES` entry; every receipt
reports `cases=55`). The "2" appears to double-count the `reorder_self`
metadata row, which is a `CASES` row (`:133-134`). Not a defect of the
landed artifact — a count correction for the round record.

### R3 — INFO: a `--python` wrapper forcing unbuffered stdio turns the battery red by design

Measured: `python3 corpus/fixtures/pygame_battery.py --python
corpus/live/r72-reviewer/pyu_wrapper.sh --runs …` (wrapper = `exec python3
-u "$@"`) → **FAIL battery, exit 1**, exactly one row:
`self_wire_reorders  'midline_splice' != pinned 'prefix_reorder' (idx
h=1886 c=1899 t=1913)` (`pg-runs-uwrap2/pygame-20261014T145528500389Z/`;
the first wrapper run `pg-runs-uwrap/…T145433125719Z/` shows the same
verdict at idx h=1893 c=1906 t=1920 — the offset shift is jitter in
earlier emitted numeric fields, not a different failure).
This is the raw case's discrimination proof (it is not vacuous) and the
intended regime guard: the battery's env strip (`pygame_battery.py:154`)
cannot neutralize an argv `-u` injected by a wrapper. Recorded so a
future port reads a red wrapper run as regime mismatch, not regression;
the canonical invocation is green in every run below.

### R4 — INFO: `cadence60|last_tick_ret` is unpinned ±1ms jitter

Prior-row stability compare (V6) shows one value differing from the r71
receipt outside the comparator's timing-key set: `last_tick_ret` 16 (my
runs) vs 17 (`corpus/live/runs/pygame-20261014T143255328754Z`). It is the
last `clock.tick(60)` return (ms, SDL_Delay quantization) and is not
pinned by the battery (c60 pins `n`/`dt_*`/`fps` only). No battery
impact; a comparator should classify it as jitter (my script's `JITTER`
set was incomplete — the only stable-diff it reported).

## Verified — author commands replayed, evidence resolves

**V1 — committed battery replay ×3.** `python3 corpus/fixtures/
pygame_battery.py --runs corpus/live/r72-reviewer/pg-runs` → `totals:
cases=55 pass=55 fail=0 launch_ok=True done_marker=True exit=0`, exit 0,
×3 (`pygame-20261014T145302573472Z`, `…T145311621856Z`,
`…T145320605232Z`). Case count 36 → 55 = 18 new `CASES` + 1 `RAW_CASES`;
agrees with the author's own 55/55 ×3 (`corpus/live/r72-author/runs/`).

**V2 — ambient-env sweep and the folded r71 defect.** `PYTHONUNBUFFERED=1
python3 corpus/fixtures/pygame_battery.py …` → 55/55, exit 0
(`pg-runs-envsweep/…T145400847929Z`). The `popen_arm` fix is
load-bearing, independently reproduced: pre-author probe under the sweep
emits `popen_buf|l1_wait_ms=5.36` (outside the pinned 110–180 — the
r71-verifier Item 6 defect), committed probe emits `125.15` (inside).
`run_process`'s pop (`pygame_battery.py:154`) keeps `reorder_self`
block-buffered under the sweep — raw wire still CHILD-before-HEAD (V5).

**V3 — loaded host.** 32×`yes` hogs, one battery run → 55/55
(`pg-runs-loaded/…T145509406496Z`); the declared `reorder_late` margin
held.

**V4 — new-arm byte-identity.** The six new ARM lines are byte-identical
across all five of my receipts (3 idle + sweep + loaded): `reorder_buf |
… topology=prefix_reorder head_at=8 injected_at=0 tail_at=14
wire_bytes=19 ret=0`; `reorder_unbuf|flush|env | … midline_splice head_at=0
injected_at=5 tail_at=14 wire_bytes=19`; `reorder_late | … append head_at=0
injected_at=11 tail_at=6 wire_bytes=19`; `reorder_self | bufsize=131072
fd1_isatty=False descendant=printf`. "Same 19 bytes, order moves" holds
×5.

**V5 — raw-wire regime.** My receipts `probe.stdout.txt:15-17` =
`REORDER-CHILD`, `REORDER-HEAD`, `REORDER-TAIL` (idle, sweep, loaded);
under the `-u` wrapper the same lines are `REORDER-HEAD`,
`REORDER-CHILD`, `REORDER-TAIL`. `RAW_CASES` classifies the captured
stream and gates the verdict (R3).

**V6 — prior-row stability.** Comparator
(`corpus/live/r72-reviewer/compare_prior.py`), pre-author-vs-committed
and r71-receipt-vs-committed: key sets identical for all 9 prior arms;
only jittered timing keys differ (R4); the six "missing" arms are the new
additions. All 36 prior cases PASS under their original pins in every
run.

**V7 — scope and sibling stability.** `git diff --name-only
44127af..fee5563` = the two pygame fixtures only; `git status --porcelain
corpus/fixtures/` clean at `fee5563`; LOVE battery **19/19 PASS, exit 0**
(`corpus/live/r72-reviewer/love-runs/love-20261014T145517456779Z/`).
Godot untouched by the diff.

**V8 — independent ground truth.** The X1 host demo replays exactly as
`xconnector.md:45-50` records (`INJECTEDHEAD  TAIL$`; `HEAD INJECTED
TAIL$` ×2 — `x1_replay.txt`). My own nested harness
(`reorder_probe_ref.py/.out`) and probe-level harness
(`probe_level_ref.py/.out`) independently produce the three topologies
with an `os.system`-inherited fd1 seam, concurring with the landed cells.

**V9 — callers / invariants / error paths (textual, line-cited).**
`popen_arm` has exactly two callers (`pygame_probe.py:278,284`) and
`run_process` two (`pygame_battery.py:207,212`); canonical-env behavior
unchanged (`PYTHONUNBUFFERED` unset on host, measured). ARM grammar
unaffected: the raw markers are non-ARM lines, `parse_arms` regex
(`pygame_battery.py:144`) ignores them; the raw result dict shape
(`:252-256`) matches existing rows. Error paths: `markers_missing` →
keyed FAIL (`pygame_probe.py:215`, `pygame_battery.py:240`);
`TimeoutExpired` → kill+communicate (`pygame_probe.py:208-210`); the raw
check runs on any stdout, so a launch failure yields `markers_missing`
FAIL and `launch_ok=False` gates the verdict. The `degenerate`
fallthroughs (`pygame_probe.py:223`, `pygame_battery.py:248`) are
unreachable for distinct markers — diagnostic carriers, not dead code.

Claim adjudication: *buffered child → prefix/reorder* — pinned and
observed (inj=0 < head=8); *flushed/-u child → midline splice (Godot/LOVE
topology)* — pinned and observed across three window-collapse modes;
*fabricated ORDER = language-layer (buffering mode), seam = spawn-layer* —
the crossed cells vary only the owner's stdio mode over identical source
text, with fd1 inheritance (`os.system`) supplying the seam; the referent
(fd1 owner, not descendant) is explicit in the probe docstring `:39-47`
and the battery docstring `:24-31` (critic F1 folded). *One window
family* — carried with the r71 withholding-window linkage and per-receipt
`bufsize=131072` pins.

## Residual risk

1. `reorder_late`: a >300ms stall between spawn and the owner's flush
   flips `append` → `prefix_reorder` (author-declared; observed ×5
   including one 32-hog run — wide but nonzero margin).
2. Per-build pins: `rord_bufsize`/`self_bufsize` pin 131072 exactly;
   ≤3.13 builds (8192) fail those two keys (author-declared; same
   convention as `whs_bufsize`).
3. `reorder_self` is correct only under the battery's pipe capture;
   `fd1_isatty` records the regime and is pinned False, so a tty-attached
   runner reads as keyed FAIL, not silent drift (critic F2 carried).
4. Hybrid topology (descendant between flushed chunks of a crossing
   write; xconnector prediction iii) is not battery-pinned — measured in
   boundary scratch only.
5. fd2 (stderr) composition unprobed.
6. `resume_continuity_v1` / one-canonical-runtime routing: N/A to this
   diff — fixture-only change; no runtime route or resume path touched,
   and the canonical Rust judge is outside this lane.

## Verification gaps

1. No `lsp` device → no semantic references/definition checks (recorded
   above); all caller claims textual.
2. Godot battery not replayed (heavy; zero Godot paths in
   `44127af..fee5563` — hash-level argument only).
3. Loaded regime sampled once (32 hogs); `reorder_late`'s margin not
   stressed beyond it.
4. `reorder_env` relies on this build's `PYTHONUNBUFFERED` semantics
   ("1" → unbuffered, measured); ≤3.13 differs for "0", which is not
   used here.

## Receipts (all under `corpus/live/r72-reviewer/` unless noted)

- Idle replay ×3: `pg-runs/pygame-20261014T{145302573472,145311621856,
  145320605232}Z/`
- Env sweep: `pg-runs-envsweep/…T145400847929Z/`; loaded:
  `pg-runs-loaded/…T145509406496Z/`
- Pre-author baseline (old fixture): `pg-runs-pre/…T143557118457Z/`;
  hashes `pre-author.sha256`
- `-u` wrapper FAIL: `pg-runs-uwrap/…T145433125719Z/` (grep form),
  `pg-runs-uwrap2/…T145528500389Z/` + `uwrap-run.txt` (exit 1)
- Snapshots: `snapshots/probe-HEAD.py`, `probe-144531.py`,
  `battery-144531.py` (final rev = committed blobs)
- Independent harnesses: `reorder_probe_ref.{py,out}` (sha256
  `552ff34c…`), `probe_level_ref.{py,out}`, `x1_replay.txt` (sha256
  `355051e7…`), `compare_prior.py`
- Sibling: `love-runs/love-20261014T145517456779Z/verdicts.json`
- Author receipts compared: `corpus/live/r72-author/runs/…{144428,144447,
  144456}…Z/`; r71 receipt `corpus/live/runs/pygame-20261014T143255328754Z/`

## Method (exact commands, from repo root)

```
python3 corpus/fixtures/pygame_battery.py --runs corpus/live/r72-reviewer/pg-runs            # ×3
PYTHONUNBUFFERED=1 python3 corpus/fixtures/pygame_battery.py --runs corpus/live/r72-reviewer/pg-runs-envsweep
python3 corpus/fixtures/pygame_battery.py --runs corpus/live/r72-reviewer/pg-runs-loaded     # 32× yes hogs
python3 corpus/fixtures/pygame_battery.py --python "$PWD/corpus/live/r72-reviewer/pyu_wrapper.sh" --runs corpus/live/r72-reviewer/pg-runs-uwrap2
python3 corpus/live/r72-reviewer/reorder_probe_ref.py
python3 corpus/live/r72-reviewer/probe_level_ref.py
python3 corpus/live/r72-reviewer/compare_prior.py <r71-receipt> <my-receipt>
python3 corpus/fixtures/love_battery.py --runs corpus/live/r72-reviewer/love-runs
PYTHONUNBUFFERED=1 python3 corpus/live/r72-reviewer/snapshots/probe-HEAD.py   # r71 leak repro (l1=5.36)
PYTHONUNBUFFERED=1 python3 corpus/fixtures/pygame_probe.py                   # fixed (l1=125.15)
git diff --numstat 44127af..fee5563 -- corpus/fixtures/
```

## Bottom line

Evidence resolves: 55/55 ×3 idle + sweep + loaded, byte-identical new
pins, raw-wire hazard pinned in-repo, prior rows stable, sibling LOVE
green. Recommendation: **ACCEPT the artifact as landed**; fold R1 (report
counts/"insertion-only" wording) and R2 (baseline inventory) as record
corrections. No functional defect found in scope.
