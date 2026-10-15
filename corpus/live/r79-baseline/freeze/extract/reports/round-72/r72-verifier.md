# r72 verifier — reorder-fabrication arm (lane g2d)

Seat: verifier | Host: CPython 3.14.7 (`io.DEFAULT_BUFFER_SIZE` = 131072),
pygame 2.6.1 / SDL 2.32.72. All commands from lane-repo root; receipts in
`corpus/live/r72-verifier/`; no writes elsewhere; no git mutations.

## Landing

Author commit **`fee5563`** ("r72: reorder fabrication arm —
fd1-inheritance x stdio-withholding composition (xconnector X1)"),
committed 14:46:58Z, detected on this seat's poll at 14:47:14Z (polls at
14:36/14:38/14:39/14:42/14:44Z showed HEAD=`44127af`; the fixture diff
went visible in the working tree at 14:43Z during polling — verified
pre-commit and identical in shape to the landed arm).

`git show --name-only fee5563` → **only** `corpus/fixtures/
pygame_probe.py` + `corpus/fixtures/pygame_battery.py`. Zero Godot/LOVE
paths, zero report/scorecard files. Working tree post-commit: clean
under `corpus/fixtures/` (`git diff HEAD` empty). Committed fixture
sha256s: probe `7c0f9c73…53ac8e4`, battery `077af0b5…315d28`
(`sha256-receipts.txt`).

## Item 1 — committed battery replay ×3 → PASS (55/55, exit 0, ×3)

`PYTHONDONTWRITEBYTECODE=1 python3 corpus/fixtures/pygame_battery.py
--runs corpus/live/r72-verifier/runs` — three fresh runs:
`pygame-20261014T{144749411913,144806129416,144829454281}Z`, all
`totals: cases=55 pass=55 fail=0 launch_ok=True done_marker=True`,
probe_exit 0. Case count grew 36 → 55 (18 reorder CASES rows +
1 RAW_CASES row). All 36 prior r71 rows still PASS — no regression.

The reorder ARM lines are **byte-identical across all 3 runs** — the new
pins are byte-order facts, not timing jitter:

| arm | observed (identical ×3) | topology |
|---|---|---|
| reorder_buf (buffered owner) | `head_at=8 injected_at=0 tail_at=14 wire_bytes=19` | **prefix_reorder** — descendant bytes first |
| reorder_unbuf (`-u` owner) | `head_at=0 injected_at=5 tail_at=14` | midline_splice |
| reorder_flush (flush=True head) | `head_at=0 injected_at=5 tail_at=14` | midline_splice |
| reorder_env (`PYTHONUNBUFFERED=1`) | `head_at=0 injected_at=5 tail_at=14` | midline_splice |
| reorder_late (descendant post-window) | `head_at=0 tail_at=6 injected_at=11` | append |
| reorder_self (probe's own fd1) | `fd1_isatty=False` + raw wire `REORDER-CHILD` at line 15 **before** `REORDER-HEAD` at line 16 of `probe.stdout.txt` | prefix_reorder (RAW_CASES `self_wire_reorders` PASS) |

Same 19 bytes on every wire — only the order moves, exactly as the arm's
docstring claims (`pygame_probe.py:39-54`). The `reorder_self` receipt is
the X1 hazard made concrete: under the battery's pipe capture the raw
stream literally reads CHILD before HEAD — the fabricated order a
*streaming* parser of ARM lines would see, while the post-exit ARM
parser cannot observe it. `pygame_battery.py:234-248` classifies raw
`stdout.find` positions; correct.

## Item 2 — ambient `PYTHONUNBUFFERED=1` sweep → PASS (55/55)

`PYTHONUNBUFFERED=1 python3 corpus/fixtures/pygame_battery.py …` →
55/55, exit 0 (`…144806129416Z`). Discriminates the commit's two
env-hygiene fixes: `run_process` pops `PYTHONUNBUFFERED` from the probe
env (`pygame_battery.py:154`) so `reorder_self`'s buffered wire and
the withhold cells can't be silently collapsed by an operator env, and
`popen_arm` now passes `env=CHILD_ENV` (`pygame_probe.py:93`)
so `popen_buf`'s child is buffered-by-construction. Both hold —
`popenbuf_l1_held` stayed PASS under the sweep (this was the r71
ambient-leak defect the commit message cites). Independent
discrimination PASS.

## Item 3 — independent scratch reproduction → claim VERIFIED (7/7)

Built and ran this seat's own probe before the commit landed
(`reorder_subject.py` + `reorder_harness.py`): a **live pygame process**
(init + dummy `set_mode`) writes unflushed `HEAD `, spawns
`os.system("printf 'INJECTED'")` — descendant writes inherited fd1 while
HEAD sits in userspace — then ` TAIL`. Outer harness reads the raw pipe
fd. Receipt `reorder_cells.json` (sha256 `34a58e73…cacd6e`):

`pygame_buffered` → `INJECTEDHEAD  TAIL\n` (reorder_prefix) ·
`pygame_dash_u` / `pygame_flushed` / `pygame_env_unbuf` →
`HEAD INJECTED TAIL\n` (midline_splice) · bare-python3 control cells
identical → topology is a **language-layer** property (buffering mode),
seam is **spawn-layer** (fd1 inheritance). 7/7 predictions PASS, exit 0.
Byte-for-byte the xconnector host demo, now reproduced inside the engine
runtime — closing the gap `xconnector.md:290` named ("not yet run inside
a pygame/bpy process — that is the arm's job").

Committed-arm results and my independent cells agree on every topology.

## Item 4 — referent correctness (critic F1 fold) → correct

The brief's pin read "buffered child → reorder; flushed/-u child →
splice". r72-critic F1 measured that the flipping variable is the
**fd1-owner / HEAD-writer's** stdio mode, not the descendant's. The
landed arm implements the correct referent: the descendant is constant
(`printf`, write-through) and the sweep is over the spawned owner's own
mode {buf, -u, flush, env, late} — the probe docstring and commit
message both name this explicitly ("the variable is the fd1-owner's
buffering, not the descendant's"). My scratch cells concur (mode applied
to the HEAD-writer, descendant constant).

## Overall

| item | verdict |
|---|---|
| author arm landed (`fee5563`, scope-clean) | confirmed — 2 fixture files only |
| committed battery replay | PASS 55/55 ×3 runs, exit 0, reorder lines byte-identical |
| topology pin vs X1 claim (buffered→reorder, -u/flush/env→splice, late→append) | AGREE — all cells as pinned incl. raw-wire `self_wire_reorders` |
| ambient `PYTHONUNBUFFERED=1` discrimination | PASS — env-strip + CHILD_ENV fixes hold (r71 leak dead) |
| independent scratch reproduction | 7/7 — concurs with committed arm, first in-pygame-process repro |
| prior 36 rows | all PASS — no regression |

## Verdict: **AGREE** — 5/5 items. The composition claim (fd1-inheritance
seam × language-layer buffering → fabricated byte ORDER) is verified on
the committed tree with deterministic, byte-order-exact pins; the
hazard-case wire (`REORDER-CHILD` before `REORDER-HEAD` in captured
stdout) is itself pinned in-repo.

## Receipts

- `corpus/live/r72-verifier/runs/pygame-20261014T144749411913Z/verdicts.json` — clean-env replay 55/55 (+ `probe.stdout.txt` lines 15-17: CHILD-before-HEAD wire)
- `corpus/live/r72-verifier/runs/pygame-20261014T144806129416Z/verdicts.json` — `PYTHONUNBUFFERED=1` sweep 55/55
- `corpus/live/r72-verifier/runs/pygame-20261014T144829454281Z/verdicts.json` — flake re-run 55/55
- `corpus/live/r72-verifier/runs/pygame-20261014T143636389287Z/verdicts.json` — pre-landing `44127af` battery replay 36/36 (baseline)
- `corpus/live/r72-verifier/reorder_cells.json` + `reorder_subject.py` + `reorder_harness.py` — independent 7-cell scratch repro
- `corpus/live/r72-verifier/sha256-receipts.txt` — fixture + receipt hashes

## Remaining risks

- `head_at`/`injected_at`/`wire_bytes=19` are exact-offset pins — brittle
  by design if marker strings are edited (intended pin behavior).
- `reorder_late` rests on sleep margins (descendant ~300ms vs owner exit
  ~600ms); a >300ms scheduling stall could flip it to reorder. Observed
  `append` ×3; margins are wide but nonzero-flake.
- `reorder_self`'s pinned `prefix_reorder` is correct only because the
  battery's `capture_output` is always a pipe; a hypothetical tty-attached
  runner would splice instead — `fd1_isatty` records the regime, so a
  regime flip would read as a keyed FAIL, not silent drift.
- The composition is verified for stdout-fd1; fd2 (stderr) composition
  is unprobed this round (out of arm scope).
