# Round 72 — boundary: reorder-fabrication edge cells (27 cells × 2 runs, all stable)

Seat: boundary (LEAF) | Lane: g2d | Round: 72 | Host: devin — CPython
**3.14.7**, `pygame 2.6.1 (SDL 2.32.72)`, `/usr/bin/python3`.

**Scope.** Scratch-only + report-only: wrote only this report and
`corpus/live/r72-boundary/`. No tracked fixture, runner, CASES row, LOG or
SCORECARD touched; no subagent dispatch; no git mutation.

**`lsp` disclosure.** No `lsp` device on this host (`lsp`, `pyright`,
`basedpyright`, `pylsp`, `jedi-language-server`, `ruff-lsp` all absent from
PATH and not importable). Every claim below is a process-level measurement
plus textual `file:line` citations — no semantic navigation was available or
needed for this seat.

**Probe-time state — author arm not landed.** `corpus/fixtures/pygame_probe.py`
/ `pygame_battery.py` at the r71 hashes (probe `4d426a3b…`, battery
`0a579819…`, HEAD `44127af`), `git status` clean for `corpus/fixtures/`: the
r72 `reorder` arm was **not in the tree at probe time**, so every cell below
is scratch-driven (same convention as r71-boundary). Receipt: `state.txt`.

## Claim under test / the author arm

Brief verbatim: *"add `reorder` arm to pygame_probe + battery cases — a
spawned descendant writing into inherited fd1 mid-window; pin: buffered child
-> prefix/reorder topology; flushed/-u child -> midline splice (Godot/LOVE
topology). Claim: the fabricated byte ORDER is a language-layer property
(buffering mode), the seam is spawn-layer — composition, two mechanisms, one
window family."*

**Headline: the composition claim is CONFIRMED byte-exact (2 full runs ×
2–3 reps); seven boundary edges the briefed arm does not cover are measured
below — two of them change how the arm must be built (F2: byte topology
alone cannot witness fabrication; F6: the arm's own receipt line is
unparseable for the battery's anchored parser unless newline-terminated).**

## Method

Parent program = the "probe process". It emits `TRACE <tag>` lines on **fd2
via `os.write`** (never buffered) at every HEAD write / flush / spawn /
child-done / TAIL event; the driver timestamps every **fd1 chunk**
(`select`+`os.read`, 64 KiB) and every fd2 line arrival. The descendant =
plain `python3 -c` (write-through `os.write(1,…)`, block-buffered
`sys.stdout.write`, or `-u`) or `sh`/`os.system` — never pygame (the claim
is language-layer). The child's `C-WRITE` TRACE is the **write-time
witness**: byte order *plus* write order separates fabricated reorder from
an honestly-earlier child write (F2).

Sanity: the xconnector demo reproduces on this host
(`INJECTEDHEAD  TAIL$` / `HEAD INJECTED TAIL$` / flush `HEAD INJECTED TAIL$`).

Receipts: `reorder_cells.py` → `cells.json` (27 cells) + `cells-run2.json`
(second full run) + `lines.json` (line reader) + `capture.json` (battery
capture path). All 27 cells `stable=True` in both runs; byte-order keys are
identical across reps, timing keys jitter within ~±3 ms (`win_after_exit`
±5 ms). `paced2` re-run 3× (`paced2-run{2,3}.json`).

## F1 — the grid: topology class is set by the PARENT (probe) mode; the descendant's buffer only moves WHEN its bytes land

| cell | parent mode | descendant mode | stream (byte-exact) | INJ vis ms | HEAD vis ms |
|---|---|---|---|---|---|
| `grid_pw_wtchild` | buffered | write-through | `INJHEAD  TAIL\n` | 35.2 | 36.4 |
| `grid_pu_uchild` | buffered | `python3 -u` | `INJHEAD  TAIL\n` | 35.0 | 36.2 |
| `grid_pp_bufchild` | buffered | block-buffered | `INJHEAD  TAIL\n` | 56.4 (child exit flush) | 57.7 (parent exit) |
| `grid_pn_nlchild` | buffered | write-through + `\n` | `INJ\nHEAD  TAIL\n` | 35.3 | 36.6 |
| `grid_up_unbufparent` | `-u` | block-buffered | `HEAD INJ TAIL\n` | 56.0 | 10.5 |
| `grid_uw_unbufparent` | `-u` | write-through | `HEAD INJ TAIL\n` | 35.8 | 10.3 |
| `grid_fp_flushparent` | `flush=True` before spawn | block-buffered | `HEAD INJ TAIL\n` | 54.9 | 9.5 |
| `grid_fw_flushparent` | `flush=True` before spawn | write-through | `HEAD INJ TAIL\n` | 36.3 | 10.9 |
| `grid_ew_envparent` | `PYTHONUNBUFFERED=1` | write-through | `HEAD INJ TAIL\n` | 35.0 | 9.7 |

Observed: parent buffered → prefix/reorder in **every** descendant mode
(3/3 reps × 2 runs for `grid_pw`/`grid_pp`); parent unbuffered/flushed →
midline splice in every descendant mode. So "buffered child → prefix" in the
brief is true when *child* = the probe process (the battery's child); the
descendant's own stdio is a **second withholding layer** that delays the
descendant's bytes to *its* flush epoch (`grid_pp`: `C-WRITE` 34.3 ms,
`C-EXIT` 54.4 ms, INJ delivered 56.4 ms) — it does not change the topology
class. X1 prediction (iv) (`PYTHONUNBUFFERED=1` collapses) confirmed.

## F2 — the window is a write-time interval; byte topology alone cannot witness fabrication

- `win_before` (child writes at 34.9 ms; parent writes HEAD at 90.2 ms):
  stream `b"INJHEAD  TAIL\n"` — **byte-identical to the fabricated cells** —
  but the order is honest (child genuinely first). A reorder arm pinning only
  the byte stream cannot distinguish the two.
- `win_flush_after_child` (child writes 65.7 ms, explicit flush 90.8 ms):
  still INVERTED — the window closes at the parent's flush, wherever it is.
- `win_after_exit` / `win_after_exit_u` (child writes ~315 ms, after the
  parent's exit flush ~10 ms): `b"HEAD  TAIL\nINJ"` — append, no reorder,
  both parent modes. Far edge = the parent's flush.
- Measured window: **reorder iff the descendant's write ∈ (parent HEAD
  write, parent flush)**; three regimes, and regimes "child before HEAD" and
  "inside window" have identical byte order.
- **Pin requirement:** the arm's fabrication verdict needs the write-order
  construction (spawn after HEAD, wait before TAIL — the briefed arm has it)
  and/or a temporal key; byte order alone is not a witness.

## F3 — "buffered" is per-byte, not per-process (buffer-lifetime edges)

- `cross_hi`: HEAD = one 131072-byte write → raw write-through (r71 R2);
  HEAD visible at 10.4 ms, before the child writes → `HEAD HHH… INJ TAIL`
  (splice) *in buffered mode*.
- `cross_after_child`: exactly 131072 B accumulated (withheld, R3) + child
  writes at 65.5 ms + a 1-byte crossing write at 67.0 ms → the flush delivers
  the whole 131072 B **after** INJ: deterministic 131072-byte inversion block
  (`INJHEAD AAAA…B TAIL`).
- `edge_head131071`: 131071 B buffered + 1 B after the child → **no flush**
  (len==avail does not flush, r71 R3) → reorder preserved to exit. The
  1-byte edge between "withheld" and "crossing flush" is pinned on the
  reorder topology.

## F4 — infix/hybrid topology (X1 prediction (iii) confirmed)

`paced2`: parent writes 1000 B chunks paced ~1 ms; child writes at ~165 ms.
INJ lands at **stream offset 126005**, splitting the parent's chunk stream:
chunks ~0–126 delivered at flush 1 (150.7 ms, 126005 B — *not* 131072; the
textio pending tail lags the BufferedWriter, corroborating r71's two-layer
edge), INJ at 164.7 ms, chunks ~127–268 at flush 2 (283.4 ms), TAIL at
325.6 ms. **~21.3–21.7 kB of parent bytes written before the child's write
were delivered after it** (21279 / 21683 / 21538 B across 3 runs;
interpolation ±1 chunk). The topology family is 4-valued
{prefix, infix, midline, append} — a two-shape pin under-specifies a paced
probe.

## F5 — loss edge: abnormal exit removes the bytes instead of reordering them

`kill` (SIGKILL at 90 ms, exit **-9**) and `os_exit` (`os._exit(0)`) →
stream `b"INJ"` only; HEAD/TAIL never flushed. The fabrication family has a
sibling failure class (silent loss) on the probe's exit path; keep the arm's
exit normal, or pin the loss cell deliberately.

## F6 — receipt-line × raw-marker interaction (battery-level, actionable)

Measured through the battery's own capture path (`subprocess.run(
capture_output=True, text=True)`) and parser regex
`^PYGAME-ARM (\S+) \| (.*)$` on `line.strip()`
(`corpus/fixtures/pygame_battery.py:101`):

| cell | captured stdout | ARM line parseable |
|---|---|---|
| `capture_buffered` (= `receipt_after`) | `'INJHEAD PYGAME-ARM reorder \| x=1\nTAIL\n'` | **False** (parsed=[]) |
| `capture_unbuf` (probe `-u`) | `'HEAD INJPYGAME-ARM reorder \| x=1\nTAIL\n'` | **False** |
| `capture_head_nl` (HEAD `\n`-terminated) | `'INJHEAD\nPYGAME-ARM reorder \| x=1\nTAIL\n'` | **True** |
| `capture_unbuf_nlchild` (descendant marker `\n`-terminated) | `'HEAD INJ\nPYGAME-ARM reorder \| x=1\nTAIL\n'` | **True** |

- `receipt_before` (probe emits its `flush=True` ARM receipt **before** the
  descendant's write): HEAD out at 10.2 ms → **splice**; the receipt line
  itself collapses the window. The arm's receipt must be emitted *after* the
  descendant's write.
- `receipt_after`: reorder preserved, but the receipt line is prefixed
  (`INJHEAD PYGAME-ARM…`) → the battery reports "missing PYGAME-ARM reorder"
  for a **parse** reason, not a mechanism reason.
- **Either the last raw marker before the receipt must end with `\n`, or the
  battery parser must locate `PYGAME-ARM` unanchored.** Note `-u` on the
  probe does not unbuffer its descendants (argv vs env) — the control is
  orthogonal to the descendant mode.

## F7 — same-process sibling channel inverts with no spawn

`fd2mrg` (2>&1 merged, no child): HEAD → fd1 (buffered), then `ERR\n` → fd2,
then TAIL → stream `b"ERR\nHEAD  TAIL\n"`: fd2's later write is delivered
before the buffered fd1 bytes. The "second write path outranks the fd1
userspace buffer" family is wider than the spawn seam; fd1-inheritance is
one instance. (Inference from one cell.)

## F8 — write-path control: the determinant is the write path, not a global "buffering mode"

`parent_oswrite_head`: HEAD written via `os.write(1, …)` (bypassing the
userspace buffer) in an otherwise buffered probe → `HEAD INJ TAIL` splice.
Same process, same spawn seam; only the HEAD write path changed. Consistent
with the per-byte reading (F3); the arm's pin should name the write path.

## F9 — parity + seam reproductions

- `pygame_pw` (real pygame process, dummy driver): `b"INJHEAD  TAIL\n"` —
  inverted; INJ visible ~608 ms, HEAD at exit ~640 ms — pygame init shifts
  times only.
- `sh_os_system` (`os.system("printf INJ")`): `b"INJHEAD  TAIL\n"` with
  witness `C-WRITE` 10.45 ms > `P-HEAD` 9.78 ms — the xconnector demo
  reproduced under the write-time witness.
- `multi`: two write-through descendants → `b"INJINJHEAD  TAIL\n"`; both
  prefix; order among descendants preserved.

## F10 — streaming-consumer line view

| cell | lines (ms, content) |
|---|---|
| `grid_pw_wtchild` | (36.6, `INJHEAD  TAIL`) — one line, at exit |
| `grid_pp_bufchild` | (56.6, `INJHEAD  TAIL`) |
| `grid_pn_nlchild` | (35.7, `INJ`), (37.0, `HEAD  TAIL`) |
| `grid_up_unbufparent` | (56.5, `HEAD INJ TAIL`) |
| `win_after_exit` | (10.5, `HEAD  TAIL`), INJ appended ~315 ms |
| `receipt_after` | (37.3, `INJHEAD PYGAME-ARM reorder \| x=1`) |

A line-oriented streaming consumer sees the descendant marker first (or
merged into the receipt line) — the xconnector hazard class, now with the
line shapes measured.

## Suggested pins for the author's tracked arm (measured)

- buffered probe, small markers: stream byte-exact `b"INJHEAD  TAIL\n"`
  (INJ offset 0; 3/3 × 2 runs); newline-marker alternative
  `b"INJ\nHEAD  TAIL\n"`.
- `-u` / `PYTHONUNBUFFERED=1` / flush-before-spawn control: byte-exact
  `b"HEAD INJ TAIL\n"`.
- timing keys (jitter bounds): write-through descendant first INJ visibility
  ~35 ms (30–45); block-buffered descendant INJ at its exit flush ~55 ms
  (45–70); TAIL ~1.5 ms after INJ; whole cell < 100 ms.
- receipt line must be preceded by `\n` and emitted after the descendant's
  write; do not pin byte order alone as the fabrication witness (F2).
- prior rows byte-stable: fixtures untouched (hashes in `state.txt`).

## Remaining unknowns

- TTY stdout (line-buffered) untested — harness is pipe-only; the battery
  runs under a pipe, so this is the right regime, but the claim is untested
  for interactive stdout.
- Python ≤3.13 (8192 B buffer, different textio interaction) unmeasured on
  this host — constants are per-build (r71-boundary caveat stands).
- The landed arm's exact byte shapes (marker strings, newlines, receipt
  placement) were not in the tree at probe time; if they differ from this
  scratch pattern, re-drive the edge cells on landed bytes.
- bpy `-b -P` (X1's second Python runtime) is g3d's arm, not measured here.
- One host; byte-order keys deterministic across reps, timing keys jittered
  (bound-pinned above).

## Reproduce

```
cd corpus/live/r72-boundary
python3 reorder_cells.py --json cells.json --lines-json lines.json --capture-json capture.json    # exit 0, ~6 s
python3 reorder_cells.py --json cells-run2.json --lines-json lines-run2.json --capture-json capture-run2.json
python3 reorder_cells.py --only paced2 --json paced2-run2.json --lines-json lines-paced2-run2.json
# sanity (xconnector demo, host interpreter):
python3 -c 'import sys,os; sys.stdout.write("HEAD "); os.system("printf INJECTED"); sys.stdout.write(" TAIL\n")' | cat -A
```

## Artifact inventory (`corpus/live/r72-boundary/`)

- `reorder_cells.py` — 27-cell driver (raw reader + line reader +
  battery-capture mode).
- `cells.json` + `cells.stdout.txt`, `cells-run2.json` + `cells-run2.stdout.txt`
  — full runs.
- `lines.json`, `capture.json`, `capture-run2.json` — line-reader and
  battery-mode receipts.
- `paced2-run{2,3}.json`, `lines-paced2-run{2,3}.json` — infix-cell
  stability.
- `state.txt` — probe-time hashes / HEAD / host.

No commit, no tracked mutation, no LOG/SCORECARD write.
