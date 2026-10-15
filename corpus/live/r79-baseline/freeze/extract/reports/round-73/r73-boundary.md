# Round 73 — boundary (g2d): edge lattice + hang semantics for the r73 author arm (37 cells × 2–3 reps × 3 runs; 6 hazard modes)

Seat: boundary (LEAF) | Lane: g2d | Round: 73 | Host: devin — CPython
**3.14.7** (`io.DEFAULT_BUFFER_SIZE=131072`, this build), pygame 2.6.1
(SDL 2.32.72), node **v24.21.0**, `/usr/bin/python3`.

**Scope.** Scratch-only + report-only: wrote only this report and
`corpus/live/r73-boundary/`. No tracked fixture, runner, CASES row, LOG or
SCORECARD touched (`git diff HEAD -- corpus/fixtures/` empty at probe time);
no subagent dispatch; no git mutation.

**`lsp` disclosure.** No `lsp` device on this host (`lsp`, `pyright`,
`basedpyright`, `pylsp`, `jedi-language-server`, `ruff-lsp` all absent from
PATH; `command -v …` exit 1). Every claim below is a process-level
measurement plus textual `file:line` citations — no semantic navigation was
available or needed for this seat.

**Probe-time state — r73 author arm not landed.** `corpus/fixtures/` at the
r72 hashes (probe `21ca0cd4…`, battery `31918715…`, HEAD `2dd108b`),
`git status` clean for `corpus/fixtures/`: no `node_census` arm, no
infix/detach/fd2 cells in the tree at probe time, so every cell below is
scratch-driven. Receipt: `state.txt`.

## Headline

1. **The 8192 write-size axis does not exist on this build** (negative
   control): 8191/8192/8193-byte single writes and an 8×1024 cumulative
   fill are all withheld → `prefix_reorder`; the boundary is at
   131072, and a single write of **exactly 131072 is raw write-through**
   (131071 withheld / 131072, 131073 midline). `io.DEFAULT_BUFFER_SIZE=
   131072` is this build's constant (≤3.13's 8192 is not measurable here).
2. **The exact-fill crossing byte does not flush at the TEXT layer; the
   next write does** (80 ms pause cell: block delivered at the TAIL write,
   not at the crossing write). At the **binary layer**
   (`sys.stdout.buffer.write`) the same crossing write at exact-full DOES
   flush. Two-layer edge, measured both sides — refines r72 F3's
   "edge_head131071 → no flush" attribution (topology class unchanged).
3. **Multi-child order is write-time order**; all descendant bytes land
   before a buffered owner's HEAD, and a descendant's own buffering delays
   only its delivery epoch (INJ2 written 36.1 ms, delivered 136.2 ms).
4. **fd2-merge topology follows the fd1-OWNER's mode**: buffered →
   `ERR\nHEAD  TAIL\n` (r72 F7 re-pin, byte-exact); `-u` →
   `HEAD ERR\n TAIL\n`; a spawned descendant's fd2 write follows the same
   rule (`CHILDERR` before vs after HEAD).
5. **Detach EOF-hold**: parent exits clean at ~10 ms, capture EOF arrives
   ~400 ms later (bounded descendant); EOF ≠ process exit
   (`writerless_close`: EOF 300 ms before exit).
6. **Unbounded-read hazard is real and has a specific shape**: on 3.14.7
   `subprocess.run(…, timeout=…)` is bounded (POSIX branch does
   `kill()+wait()`, `/usr/lib/python3.14/subprocess.py:558–571`), but
   `communicate()` without a timeout and the **r72 `reorder_arm` fallback
   shape** (`TimeoutExpired → kill() → communicate()`) both hang forever
   against a detach holder (externally SIGKILLed at 6 s, rc −9). The
   battery-level 30 s bound contains the probe but leaks the holder.
7. **Node boundary is exactly 64 KiB**: small write + `fs.writeSync` →
   midline splice (brief's SPLICE prediction confirmed); 65535/65536
   midline, **65537 → infix with INJ at 65536 and exactly 1 byte after**
   (brief's >64 KB INFIX prediction confirmed). `execSync` default
   (`stdio:'pipe'`) does **not** exercise the fd1-inheritance seam; node
   ABSENT must be caught (`FileNotFoundError`) or the probe aborts.

## Method

Parent program = `python3 -c` fd1-owner; TRACE lines on **fd2 via
`os.write`** at every HEAD write / fill / crossing byte / spawn / child-done
/ TAIL event (write-time witness); driver timestamps every **fd1 chunk**
(`select`+`os.read`, 64 KiB) and every fd2 line. Merge cells (2>&1) carry no
traces — the wire is the receipt, and write order is known by construction
(single process / `p.wait()` between statements). Descendants are plain
`python3` (claim is language-layer) or `node` (owner census); the node
descendant is `printf` via `execSync(..., {stdio:'inherit'})`. All cells
bounded; the hazard class is wrapped in an external `timeout -s KILL`
(no fifo in this lattice — pipes only — guard applied to the
unbounded-read class).

Receipts: `edge.json` (run 1), `edge-run2.json`, `edge-load.json` (4 CPU
burners), `hazard.json`; stdout copies `edge*.stdout.txt`; all 37 cells
`stable=True` and **byte-order keys identical across run1 / run2 / load**
(0 diffs). Timings jitter only (~±1.5 ms under load).

## W — write-size straddle, 8192 and 131072 axes (13 cells)

Each cell: owner writes HEAD (N bytes) → spawns a write-through child that
writes `INJ` → waits → writes ` TAIL\n` → exits.

| cell | HEAD write | topology | order (HEAD/INJ/TAIL) | delivery notes |
|---|---|---|---|---|
| `w8191` | one 8191-B write | `prefix_reorder` | 3 / 0 / 8195 | withheld to exit |
| `w8192` | one 8192-B write | `prefix_reorder` | 3 / 0 / 8196 | withheld to exit |
| `w8193` | one 8193-B write | `prefix_reorder` | 3 / 0 / 8197 | withheld to exit |
| `w8192_fill` | 8×1024 cumulative | `prefix_reorder` | 3 / 0 / 8196 | withheld to exit |
| `w65536` | one 65536-B write | `prefix_reorder` | 3 / 0 / 65540 | withheld to exit |
| `w131071` | one 131071-B write | `prefix_reorder` | 3 / 0 / 131075 | block delivered 65536+65535 **at the TAIL write** |
| `w131072` | one 131072-B write | `midline_splice` | 0 / 131072 / 131076 | **raw write-through**: 2×65536 chunks at ~10.4 ms, before the spawn (10.5 ms) |
| `w131073` | one 131073-B write | `midline_splice` | 0 / 131073 / 131077 | 65536+65536+1 at ~9.9 ms, before the spawn |
| `fill131071_plus1` | 131071 accumulated + child + 1-B cross + TAIL | `prefix_reorder` | 3 / 0 / 131076 | 131072-B inversion block after INJ |
| `fill131072_plus1` | 131072 accumulated + child + 1-B cross + TAIL | `prefix_reorder` | 3 / 0 / 131077 | 131072-B inversion block after INJ |
| `fill131071_plus1_pause` | as above + **80 ms pause** after the cross byte | `prefix_reorder` | 3 / 0 / 131076 | block delivered at **TAIL (126.25 ms)**, not at the cross byte (46.02 ms) |
| `fill131072_plus1_pause` | as above | `prefix_reorder` | 3 / 0 / 131077 | block at **TAIL (126.15 ms)**, not at the cross byte (46.34 ms) |
| `buf_fill131072_plus1_pause` | same, **`sys.stdout.buffer`** layer | `prefix_reorder` | 3 / 0 / 131077 | block delivered **at the cross byte (47.5 ms)** |

Observed: on this build the topology flips exactly at a single write of
131072 B (raw write-through); the 8192 axis is flat. For accumulated exact
fill, the block is always delivered after INJ (prefix), but the text layer
defers the flush to the *following* write while the binary layer flushes at
the crossing write itself — the two-layer edge r71/r72 flagged, now
separated by the pause control. Bounded pins (never exact offsets):
`{8191,8192,8193,8×1024,65536,131071}` → `prefix_reorder`, INJ@0, HEAD@3,
wire_len = N+9; `{131072,131073}` → `midline_splice`, HEAD@0, INJ@N;
`fill*` → `prefix_reorder`, INJ@0, HEAD@3, wire_len 131081/131082.

## M — multi-child reorder (5 cells)

| cell | stream (byte-exact) | len | notes |
|---|---|---|---|
| `multi2_seq` | `INJ1INJ2HEAD  TAIL\n` | 19 | children sequential; order = write order |
| `multi2_seq_u` | `HEAD INJ1INJ2 TAIL\n` | 19 | `-u` owner collapses the window |
| `multi3_par` | `INJ1INJ2INJ3HEAD  TAIL\n` | 23 | 3 children spawned at 20/40/60 ms; order preserved |
| `multi_mixed_buf` | `INJ1INJ2HEAD  TAIL\n` | 19 | INJ2 **written** at 36.1 ms, **delivered** at 136.2 ms (child's own exit flush) — descendant buffering moves WHEN, not the class |
| `multi_fd2merge` | `TRACE C1-WRITE\nINJ1TRACE C1-WROTE\nERRINJ2\nHEAD  TAIL\n` | 53 | child fd2 rides the merged capture before the withheld HEAD |

## F — fd2 merge under the owner-mode sweep (5 cells, 2>&1)

| cell | stream (byte-exact) | len |
|---|---|---|
| `fd2mrg_buf` | `ERR\nHEAD  TAIL\n` | 15 (r72 F7 re-pin, byte-exact) |
| `fd2mrg_u` | `HEAD ERR\n TAIL\n` | 15 |
| `fd2mrg_u_child` | `HEAD CHILDERR\n TAIL\n` | 20 |
| `fd2mrg_buf_child` | `CHILDERR\nHEAD  TAIL\n` | 20 |
| `fd2mrg_u_child_split` | `HEAD CHILDERR\nCINJ TAIL\n` | 24 |

The merge topology is the **fd1-owner's** property: buffered → the later
fd2 write outranks the fd1 userspace buffer; `-u` → fd2 lands in program
order after HEAD. A spawned descendant's fd2 write follows the same rule
(fd2 bytes precede a buffered owner's withheld HEAD).

## D — detach / EOF-hold / harness integrity (3 cells)

| cell | stream | parent exit | fd1 EOF | reading |
|---|---|---|---|---|
| `detach_bounded` | `DETACH\n` (7 B) | P-EXIT 10.2 ms | **410.65 ms** | detached grandchild holds fd1 ~400 ms past parent exit; EOF delayed, bounded |
| `writerless_close` | — | P-EXIT 309.4 ms | **9.31 ms** | fd1 closed at 9.31 ms; EOF arrives ~300 ms **before** process exit |
| `silent_exit` | — | P-EXIT 209.2 ms | 211.05 ms | no writer → EOF at exit |

Harness-integrity pin: capture EOF is neither the parent's exit nor the
process's exit — a detach cell must compare EOF against *parent exit*
(bounded descendant), and a "writerless" child EOFs early.

## N — node owner census edges + absent/broken variants (11 cells)

Owner = `node -e …`; descendant = `printf INJECTED` via
`execSync(..., {stdio:'inherit'})` unless noted. Node **is** present
(v24.21.0); "absent" is exercised by PATH-stripping.

| cell | stream / shape | len | exit | notes |
|---|---|---|---|---|
| `node_small` | `HEAD INJECTED TAIL\n` | 19 | 0 | midline splice (brief's SPLICE prediction confirmed) |
| `node_b65535` | HEAD+65530 H, INJ, TAIL | 65549 | 0 | midline — all H before INJ |
| `node_b65536` | HEAD+65531 H, INJ, TAIL | 65550 | 0 | midline — all H before INJ |
| `node_b65537` | HEAD+65532 H, INJ, TAIL | 65551 | 0 | **infix**: chunks 65536 / 8 (INJ) / **1 (last H)** / 6 |
| `node_writesync` | `HEAD INJECTED TAIL\n` | 19 | 0 | midline (write-through control) |
| `node_execsync_default` | `HEAD  TAIL\n` | 11 | 0 | INJ absent — default `stdio:'pipe'` captures the child; **the fd1-inheritance seam is not exercised** |
| `node_execsync_rewrite` | `HEAD INJECTED TAIL\n` | 19 | 0 | INJ re-emitted by node's own stream (chunks 5 / **14** = INJ bundled with TAIL) — same byte order as `node_execsync_default`'s intent and as the inherit cell; the seam differs only in chunk structure, not byte order (same lesson as r72 F2) |
| `node_execsync_fail` | `HEAD PART` | 9 | **1** | execSync throws (child exits 3) → node dies before TAIL; probe-level abort if unhandled |
| `node_absent_unhandled` | — | 0 | **1** | `FileNotFoundError` traceback, no bounded verdict |
| `node_absent_handled` | `NODE-BLOCKED [Errno 2] …` | 57 | 0 | bounded blocked verdict (required shape) |
| `node_broken_shim` | `NODE-RAN rc=127\n` | 16 | 0 | a PATH-shadowing shim that exits 127 → rc-visible blockage, no fabricated topology |

Node boundary is exact at 65536: a 65536-byte try-write completes before the
child writes; 65537 leaves exactly 1 byte queued. The three owner modes
{small, >64 KB, writeSync} all measured; only >64 KB is infix.

## X — missing-runtime blockage through the tracked path

`run_process(['/nonexistent/python3', …], 5, PROBE_ENV)` imported from the
tracked `corpus/fixtures/pygame_battery.py` (read-only, no bytecode
written): returns `error="launch error: [Errno 2] No such file or
directory: '/nonexistent/python3'"`, `exit=None`, stdout empty — bounded,
no fabricated rows. Same class as the node-absent variant.

## Hazard lattice — unbounded-read semantics (6 modes, `hazard.json`)

Holder = double-forked grandchild (`setsid`), writes its pid, execs
`sleep 600`, holds the capture pipe write end past the direct child's exit.
Every mode run under an external `timeout -s KILL 6`.

| mode | rc | wall | result |
|---|---|---|---|
| `communicate_timeout` | 0 | 2.04 s | `communicate(timeout=2)` raises at 2.03 s; **kill the HOLDER** then drain → bounded |
| `run_timeout` | 0 | 2.02 s | `subprocess.run(capture_output=True, timeout=2)` bounded on 3.14.7 (POSIX `kill()+wait()`, no second `communicate`) |
| `communicate_notimeout` | **−9** | 6.0 s | `communicate()` with no deadline **never returns** |
| `run_notimeout` | **−9** | 6.0 s | `run(capture_output=True)` with no timeout **never returns** |
| `reorderarm_shape` | **−9** | 6.0 s | `communicate(timeout)` → `TimeoutExpired` → `kill()` → `communicate()` (the r72 `reorder_arm` fallback, `pygame_probe.py:207–210`) **never returns** |
| `battery_shape` | 0 | 6.02 s | probe-level hang bounded by `run(timeout=6)`; **holder still alive after** (`holder_alive_after=true`) → orphan leak |

Actionable for the author's DETACH cell: the generic `reorder_arm` shape
hangs against a stuck detach; either give the detach cell its own reader
that closes the pipes/kills the *holder* (safe pattern above), or the whole
probe burns the battery's 30 s budget and the descendant leaks.

**Harness incident (measured, same class).** While wrapping the hazard runs
I used `out=$(timeout -s KILL 6 python3 hazard_cells.py … 2>&1)`: the shell
command substitution never returned, because the detached `sleep 600`
grandchild had inherited **fd2** and held the merged (`2>&1`) capture pipe
open (verified: `/proc/<holder>/fd/2` → the same pipe as the shell's fd 3).
Fix: close fd2 in the detached descendant (`hazard_cells.py:40`) or bound
the read. Any consumer waiting for EOF on a merged capture — including a
naive battery harness — hangs the same way.

## Suggested pins for the author's tracked arm (all measured)

- INFIX (paced flush): pin a bounded range — INJ lands within
  (last-delivered offset, +1 chunk); never an exact offset (r72 `paced2`
  + r73-scout paced pilots agree on the family).
- DETACH EOF-hold: parent exit ~10 ms, capture EOF ~400 ms later for a
  ~400 ms descendant; pin `eof_after_exit ∈ (300, 600) ms` and a **bounded
  reader** (safe pattern) — a stuck detach must be a measured FAIL, never a
  hang (see hazard table).
- FD2-INVERSION: pin the four byte-exact shapes above; the merge topology
  is the owner's mode (buffered → fd2 before HEAD; `-u` → fd2 after HEAD).
- Node arm: small + `writeSync` → midline; >64 KB → infix with INJ@65536
  (65535/65536 midline, 65537 infix); use `{stdio:'inherit'}` (default
  `execSync` does not exercise the seam); catch `FileNotFoundError` →
  blocked verdict; catch the execSync throw → bounded FAIL.
- Write-size negative controls: `{8191,8192,8193}` and 8×1024 → prefix
  (no 8 KB edge on this build); 131071 prefix / 131072+ midline.
- Multi-child: pin `INJ1INJ2HEAD  TAIL\n` (buffered owner) and
  `HEAD INJ1INJ2 TAIL\n` (`-u` owner).

## Remaining unknowns

- TTY/line-buffered stdout untested (harness is pipe-only — the right
  regime for the battery, but the claim is untested for interactive stdout).
- ≤3.13 builds (8192 buffer) unmeasured on this host; the 8192 cells here
  are negative controls for *this* build's constant only.
- The textio pending-tail vs binary-buffer split is bounded by the
  binary-layer control, not fully separable inside CPython's two layers.
- Node/libuv queue timing under heavier load: byte-order keys stable under
  4 CPU burners here; not tested under I/O contention.
- The landed arm's exact bytes (markers, newlines, receipt placement) were
  not in the tree at probe time; re-drive the edge cells on landed bytes if
  they differ from this scratch pattern.
- No fifo cells in this lattice (pipes only); the SIGKILL guard is applied
  to the unbounded-read class as briefed.
- Cross-seat context (read-only, not my receipts): r73-reviewer's
  `detach_ref.json` (410 ms EOF hold) and `node_big_timed.json`
  (INJ@65536 infix) independently corroborate the detach and node cells.

## Reproduce

```
cd corpus/live/r73-boundary
timeout -s KILL 240 python3 edge_cells.py --json edge.json > edge.stdout.txt 2>&1          # rc 0, ~40 s
timeout -s KILL 240 python3 edge_cells.py --json edge-run2.json > edge-run2.stdout.txt 2>&1
timeout -s KILL 300 python3 edge_cells.py --json edge-load.json --load 4 > edge-load.stdout.txt 2>&1
timeout -s KILL 120 python3 run_hazards.py hazard.json                                     # rc 0, ~23 s
# per-cell spot checks:
timeout -s KILL 60 python3 edge_cells.py --only w131072,fill131072_plus1_pause,node_b65537
```

## Artifact inventory (`corpus/live/r73-boundary/`)

- `edge_cells.py` — 37-cell driver (raw fd1/fd2 reader, per-fd EOF,
  write-time trace, W/M/F/D/N/X families, `--load` burners).
- `edge.json` + `edge.stdout.txt`, `edge-run2.json` + `edge-run2.stdout.txt`,
  `edge-load.json` + `edge-load.stdout.txt` — full runs (idle ×2, load ×1;
  0 byte-order diffs).
- `hazard_cells.py`, `run_hazards.py`, `hang_probe.py`, `bin/node` (127
  shim), `hazard.json` — hazard lattice.
- `state.txt` — probe-time hashes / HEAD / host / lsp note.

No commit, no tracked mutation, no LOG/SCORECARD write; no leftover
processes (`pgrep -x sleep` clean after the runs).
