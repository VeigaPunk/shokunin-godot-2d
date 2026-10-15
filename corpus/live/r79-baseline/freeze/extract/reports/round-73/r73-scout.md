# game-dev-2d round 73 — scout: pre-measurement of the declared surface

Seat: scout (LEAF) | Lane: g2d | Round: 73 | Wave
`shokunin-train-20261101-w13`.

Host: devin — CPython **3.14.7** (GCC 16.2.1), pygame 2.6.1 (SDL 2.32.72),
**node v24.21.0** (`/run/user/1000/fnm_multishells/650927_…/bin/node`),
pipe capacity **65536** (`F_GETPIPE_SZ`), `io.DEFAULT_BUFFER_SIZE=131072`,
`PYTHONUNBUFFERED` unset. Repo `~/Projects/shokunin/game-dev-2d-shokunin`
at HEAD `2dd108b`; tracked fixtures at r72 hashes (probe
`7c0f9c73…`, battery `077af0b5…`; `state.txt`); **no tracked file touched,
no git mutation** — scratch `corpus/live/r73-scout/` + this report only.

**`lsp` disclosure.** No `lsp` device in this seat's toolset and none on
PATH (`lsp`, `pyright`, `basedpyright`, `pylsp`, `jedi-language-server`,
`ruff-lsp` all absent). Every trace below is a process-level measurement,
a textual `file:line` citation, or a fetched `v3.14.7` source read (sha256
recorded) — literal fallback, recorded; not presented as semantic proof.

**Concurrency.** Sibling r73 seats were active during all runs (load
jitter visible in ms keys); every byte-order key below was stable across
reps. All probes are pipes-only; every driver ran under
`timeout -s KILL`.

## Headline

All four briefed pre-measurements reproduce; **two brief-level deltas and
one design constraint** change how the arm must be built:

1. **INFIX is deterministic, not a band.** Paced-flush offset is exactly
   `H + B·floor((131072−H)/B)` with `B = cs·ceil(8192/cs)` (8/8 structure
   cells + CPython `v3.14.7` source). 3/3 infix cells land INJ at the
   byte-exact flush prefix (`126004`; `126005` with a 5-byte HEAD — the
   r72-boundary `paced2` value, independently reproduced).
2. **DETACH EOF-hold is real and clean**: parent `ret=0` at ~60 ms, fd1
   EOF at ~511 ms; the hold is the descendant's remaining lifetime
   (≈ 451 ms from process exit / ≈ 501 ms from the P-EXIT write witness
   for a 0.5 s descendant; 2.4 ms for the waited control). A stuck detach
   under a bounded capture becomes a measured FAIL (`timed_out=True`),
   never a hang.
3. **NODE census: both xconnector predictions confirmed**, plus a
   razor-edge: `>64KB` single write → infix with INJ at **exactly 65536**
   (pipe capacity); a write of exactly 65536 → splice (fully
   synchronous), 65537 → a 1-byte queued remainder behind INJ (byte shape
   fixed; its class label is witness-racy — see N2). **`execSync` default
   `stdio:'pipe'` means
   the child does not write into the inherited fd1** — the briefed cell
   as literally worded measures nothing; `{stdio:'inherit'}` is required.
4. **Design constraint (actionable):** the battery's raw-wire classifier
   (`pygame_battery.py:237-248`, `h<i<t → midline_splice`) cannot express
   infix — it calls a measured infix wire `midline_splice`
   (`classifier_demo.json`). The infix pin needs a write-order/delivery
   witness or an offset bound; byte offsets alone are insufficient
   (r72-boundary F2, re-confirmed here).

## Method

Every cell is captured by `wire.py`: the owner is spawned with **fd1 and
fd2 piped**, read with `select`+`os.read` (no reader-side stdio),
`PYTHONUNBUFFERED` stripped, every read timestamped, fd2 lines reassembled
with completion times. Owners emit TRACE lines on fd2 via `os.write`
(never buffered); spawned children emit a `C-WRITE` fd2 line immediately
before their fd1 payload — the **write-order witness** (SHARED guard).
Classification separates infix from midline by
`withheld_before_child = written_before_child − delivered_before_child > 0`
(a *delivery-time* discriminator, not a byte-offset one).

## 1 — ARM A / INFIX via paced flush (X4)

### 1.1 The flush law (structure cells, no injector)

`paced_pilot.py` — owner writes `HEAD` (H bytes, withheld) then `n` chunks
of `cs` index-tagged bytes paced 1 ms, no child. Measured flush-1 prefix
(first fd1 delivery) vs model `prefix1 = H + B·floor((131072−H)/B)`,
`B = cs·ceil(8192/cs)`:

| cs | n | measured flush1 | model | flush2 |
|---|---|---|---|---|
| 500 | 400 | 127504 | 4+15·8500 ✓ | 72504 (exit) |
| 1000 | 300 | 126004 | 4+14·9000 ✓ | 126000 |
| 1000 | 100 | none (exit-only) | ✓ below boundary | 100008 |
| 2000 | 150 | 130004 | 4+13·10000 ✓ | 130000 |
| 3000 | 130 | 126004 | 4+14·9000 ✓ | 126000 |
| 4000 | 100 | 120004 | 4+10·12000 ✓ | 120000 |
| 8192 | 40 | 122884 | 4+15·8192 ✓ | 131072 |
| 10000 | 40 | 130004 | 4+13·10000 ✓ | 130000 |

Source (fetched `v3.14.7`, sha256 `textio.c 21d8942c…`,
`bufferedio.c f0d51b02…` — the same hashes r72-scout cited; excerpts in
`cpython_src_excerpts.txt`): textio buffers sub-chunk writes and hands the
whole pending over when `pending_bytes_count >= chunk_size`
(`textio.c:1206` default **8192**, `:1790`); the BufferedWriter accepts a
batch iff `len <= avail && len < buffer_size` (`bufferedio.c:2103-2104`),
otherwise it flushes the buffered prefix and re-buffers the batch. The
`cs=8192` row (15 batches, not 16) is the exact-fill edge of that branch.

**Inference (moderate).** The law is this-build; `8192`/`131072` are
build constants (SHARED guard). The model is corroborated 8/8 cells, not
merely cited.

### 1.2 Infix cells (timed mid-chunk child write between flushes)

`paced_parent.py` + injector spawned at chunk K writing `C-WRITE` (fd2)
then `INJECTED` (inherited fd1):

| cell | cs | H | K | topology | inj_at | flush1 | withheld-before-child | reps |
|---|---|---|---|---|---|---|---|---|
| `infix_cs1000_inj180` | 1000 | 4 | 180 | **infix** | 126004 | 126004 | 54992–55000 | 3/3 |
| `infix_cs1000_inj150` | 1000 | 4 | 150 | **infix** | 126004 | 126004 | 24992 | 2/2 |
| `infix_cs2000_inj100` | 2000 | 4 | 100 | **infix** | 130004 | 130004 | 71992–73992 | 3/3 |
| `infix_cs1000_head5` | 1000 | 5 | 180 | **infix** | **126005** | 126005 | 54992–55992 | 3/3 |
| `infix_cs1000_pygame` | 1000 | 4 | 180 | **infix** | 126004 | 126004 | 54992–55000 | 2/2 |

- Window (rep 1): flush1 @143.8 ms → `C-WRITE` @190.6 ms → flush2
  @269.8 ms; the child lands ~46 ms after flush1 and ~79 ms before
  flush2. **The infix offset equals the flush-1 prefix byte-exactly** in
  every rep; the parent bytes written before the child's write but
  delivered after it (54 992–55 000 B at K=180) are the infix signature.
- `infix_cs1000_pygame` runs the same owner inside a headless pygame
  process (author context): byte-identical offset, times shifted ~+460 ms
  (pygame init) — consistent with r72-critic's 13/13 parent-identity
  result.
- The H=5 cell reproduces r72-boundary `paced2`'s **INJ@126005 3×**
  independently; the H=4 cell shows the law's 1-byte shift.

Controls (same driver):

| control | injection | topology | inj_at | reps |
|---|---|---|---|---|
| `infix_ctl_before_flush1` | K=50 (child writes at ~61 ms < flush1) | **prefix_reorder** | 0 | 2/2 |
| `infix_ctl_after_exit` | K=299 + 30 ms delay (child writes ~340 ms > parent exit) | **append** | 300008 | 2/2 |

### 1.3 The pin the brief asked for (bounded, measured)

- topology class: **infix** (with the delivery-time witness, not the byte
  offsets).
- offset bound: `inj_at ∈ [flush1_prefix − 1 chunk, flush1_prefix + 1 chunk]`;
  measured point values 126004 (cs=1000, H=4), 126005 (H=5), 130004
  (cs=2000). Exact offsets are reproducible here, but the band is the
  portable pin.
- structural timing keys: `flush1_ms < c_write_ms < flush2_ms` (order
  only; absolute ms are pacing-dependent and load-jittered).

### 1.4 Design constraint for the tracked RAW_CASES check

`classifier_demo.py` feeds a measured infix wire through the battery's
exact predicate (`pygame_battery.py:237-248`): the wire is
`h=0, i=126004, t=300012` → the battery says **`midline_splice`** while
the write-order witness says **infix** (flush1 < C-WRITE < flush2,
withheld=54992). The current 4-way classifier is **wrong-sign for infix**;
the author's raw check must add a fifth class with a delivery/write-order
key (or pin the offset band above and treat it as `infix`). `RAW_CASES`
today has exactly one row (`self_wire_reorders`,
`pygame_battery.py:140-142`).

## 2 — ARM A / DETACH EOF-hold

`detach_parent.py` writes `HEAD\n` (flushed), spawns a descendant that
inherits fd1, exits cleanly; `detach_eof.py` timestamps the parent exit
(poll + fd2 `P-EXIT` write witness) and fd1 EOF:

| cell | mode | ret | exit_ms | P-EXIT ms | EOF ms | hold (exit→EOF) | wire |
|---|---|---|---|---|---|---|---|
| `setsid_hold` | setsid, 0.5 s | 0 | 59.4 | 9.3 | 510.5 | **451.1** | `HEAD\nDETACHED\n` |
| `setsid_hold_rep2` | setsid, 0.5 s | 0 | 60.0 | 9.9 | 511.1 | **451.1** | same |
| `nohup_hold` | nohup, 0.5 s | 0 | 59.6 | 9.5 | 511.9 | **452.3** | same |
| `waited_ctl` | waited | 0 | 513.7 | 511.4 | 513.7 | **−0.02** | same |
| `setsid_late_marker` | setsid, 0.4 s, parent writes `DONE\n` | 0 | 59.9 | 9.8 | 410.9 | **351.0** | `HEAD\nDONE\nLATE\n` |
| `setsid_forever_bounded` | setsid, holds forever, 1.5 s bound | 0 | 60.0 | 9.9 | **None** | — | `HEAD\n` (`timed_out=True`) |

Battery capture shape (`subprocess.run(capture_output=True)` — the
battery's exact path, `pygame_battery.py:155-157`):

| cell | wall ms | outcome |
|---|---|---|
| `battery_like_setsid` | 511.1 | ret 0, `HEAD\nDETACHED\n` |
| `battery_like_waited` | 515.0 | ret 0, same wire |
| `battery_like_forever` | **1502.0** | `TimeoutExpired` at the 1.5 s probe bound; descendant killed |

**Observed:** the parent exits clean (ret 0) ~60 ms in, but the capture
EOF waits for the detached pipe holder. Hold measured from the P-EXIT
write witness = **501 ms** (the descendant's own 0.5 s sleep) vs 2.4 ms
for the waited control. A stuck holder is a measured FAIL under a bounded
timeout, not a hang; without a bound it would cost the battery's whole
`TIMEOUT_S=30` (`pygame_battery.py:54`) and report a launch timeout.

**Inference (design).** The probe cannot observe its own post-exit EOF;
the battery can. The `setsid_late_marker` cell shows the RAW_CASES-native
pin: a late marker (`LATE`) lands **after** the done marker on the raw
stdout, and the run wall-time carries the hold. Keep the detached hold
bounded (≤ ~0.5 s); a deliberate stuck-detach cell must be a separate
opt-in invocation, never in the default battery run.

## 3 — ARM A / FD2-merge inversion

`fd2_parent.py` + `fd2_merge.py` (stderr=STDOUT, the 2>&1 capture):

| cell | wire | topology | reps |
|---|---|---|---|
| `sameproc` | `ERR\nHEAD  TAIL\n` | fd2 write precedes the buffered fd1 bytes | 3/3 |
| `child_fd2` (descendant writes fd2 mid-window) | `CERR\nHEAD  TAIL\n` | prefix_reorder on the merged capture | 3/3 |
| `child_fd2_flush` (control) | `HEAD CERR\n TAIL\n` | midline_splice | 2/2 |
| `child_fd1` (r72 control on merged capture) | `CINJHEAD  TAIL\n` | prefix_reorder | 2/2 |

**Observed:** r72-boundary F7 `fd2mrg` reproduces byte-exact 3/3, and the
briefed descendant-fd2 variant measures the same inversion on the merged
capture. A second write path outranks the fd1 userspace buffer with no
spawn at all (`sameproc`); fd1 inheritance is one instance of it.

## 4 — ARM B / NODE owner census (new-runtime contact)

`node_owner.js` = node **as the fd1 owner** (node writes HEAD, spawns a
`printf` child, writes TAIL), captured by the same raw-wire driver
(fd1/fd2 piped). Child = `printf 'C-WRITE\n' >&2; printf INJECTED` via
`execSync(..., {stdio:'inherit'})`. 3 reps each (node), plus 2 reps from
a pygame parent for `node_small`/`node_big` (identical results):

| cell | topology | head | inj | tail | wire bytes | c_write ms | reps |
|---|---|---|---|---|---|---|---|
| `node_small` | **midline_splice** | 0 | 5 | 14 | 19 | 13.2–13.5 | 3+2 |
| `node_big` (>64KB single write) | **infix** | 0 | **65536** | 200013 | 200018 | 13.9–14.1 | 3+2 |
| `node_edge_65536` (exactly cap) | **midline_splice** | 0 | 65536 | 65545 | 65550 | 13.5–15.2 | 3 |
| `node_edge_65537` (+1 byte) | fixed byte-shape `[65536][INJ][1][TAIL]`; class label races (N2) | 0 | **65536** | 65546 | 65551 | 13.2–14.0 | 3 |
| `node_writesync_small` | **midline_splice** | 0 | 5 | 14 | 19 | 12.2–13.3 | 3 |
| `node_writesync_big` | **midline_splice** | 0 | 200004 | 200013 | 200018 | 12.6–13.3 | 3 |
| `node_small_piped_exec` | markers_missing | 0 | — | 6 | 11 | — | 3 |
| `c_buffered` (control) | **prefix_reorder** | 8 | 0 | 14 | 19 | 0.8–1.0 | 3 |
| `c_flush` (control) | **midline_splice** | 0 | 5 | 14 | 19 | 0.7–1.1 | 3 |
| `c_big_chunks` (200×1000 fwrite) | **infix** | 0 | 196608 | 200013 | 200018 | 0.9–1.1 | 3 |

`node_big` rep-1 timeline (ms, bytes): `12.29: 65536` (partial fill),
`14.02: 8` (INJECTED, C-WRITE at 14.02), `14.18: 65536`, `14.22: 65536`,
`14.27: 3396` (event-loop queue remainder), `14.40: 6` (` TAIL\n`).

**Observed vs xconnector predictions.**
- "Node small-write owner → SPLICE family (libuv uv_write try-write fast
  path = synchronous small writes)" — **CONFIRMED**: HEAD is on the wire
  before the child's write in 3/3 (+2 pygame-parent) reps.
- "node >64KB single write → INFIX (partial fill + event-loop queue
  remainder = third withholding layer)" — **CONFIRMED**, and the partial
  fill is byte-exact: **INJ at 65536 = the host pipe capacity**
  (`F_GETPIPE_SZ=65536`), remainder 134 468 B delivered after the child's
  write (third layer = libuv's write queue, not libc/stdio).
- "Control: `fs.writeSync(1,…)` = write-through" — **CONFIRMED** for
  small and >64KB payloads (writeSync loops the partial writes; INJ after
  the full payload).
- "C owner cell (r72-critic c_reorder.c precedent — buffered C stdio
  reorders)" — **re-pinned**: `c_buffered` → `INJECTEDHEAD  TAIL\n`
  3/3; `c_flush` → splice; `c_big_chunks` → infix at 196608 (glibc stdio
  auto-flush; 48×4096 blocks).

**New findings (brief-level).**
- **N1 — `execSync` stdio trap.** `child_process.execSync` defaults to
  `stdio:'pipe'`, so `execSync('printf INJECTED')` captures the child's
  bytes and **nothing lands on the inherited fd1**: measured wire
  `HEAD  TAIL\n` (11 B, INJECTED absent), fd2 witness
  `EXEC-CAPTURED INJECTED` (`node_small_piped_exec`, 3/3). The seam
  requires `{stdio:'inherit'}`; the briefed cell as literally worded
  would produce a `markers_missing` row.
- **N2 — the >64KB boundary is ±1 byte sharp.** A single write of exactly
  65536 B completes synchronously (splice 3/3); 65537 B leaves a 1-byte
  queued remainder, so the byte shape is `[65536][INJ][1][TAIL]` 3/3
  (INJ still at 65536). **Do not pin the 1-byte-remainder cell by the
  delivery-time class rule**: the remainder's delivery races the fd2
  `C-WRITE` witness read at 1-byte granularity (run 1: 3/3 infix;
  run 2: 1/3 infix, 2/3 "midline" — a witness-read artifact; the pipe is
  FIFO, so the remainder is always written after INJ). The robust infix
  pin is the large-remainder cell (`node_big`) or the fixed byte offsets.
  Carry the pipe capacity as a provenance key (like `bufsize`), as it is
  the boundary on this host.
- **N3 — see §1.4** (classifier cannot express infix).

## 5 — Viability + provenance

- `node --version` → `v24.21.0` (expected); resolved via PATH
  (`/run/user/1000/fnm_multishells/…`, an fnm shim path — ephemeral per
  session). The probe must resolve node at runtime and record
  version+path per receipt; node absent → bounded blocked verdict (not
  exercised here; node is present).
- `gcc` 16.2.1 built `c_owner` (`-O0`); C cells exit 0.
- pygame-parent cells reproduce byte-exactly (`infix_cs1000_pygame`,
  `node_pg_check.py`).
- Sibling seats ran concurrently; only ms keys jittered (±1 ms typical).

## 6 — Remaining unknowns / risks

- **Paced arm shape not landed.** My cells use a spawned owner; the
  author may instead run the paced flush on the probe's own fd1. The
  byte law transfers, but the battery-side *check* must change (§1.4).
- **Portability.** `B=8192`, `buffer_size=131072`, pipe capacity 65536
  are this-host/this-build constants; other builds shift the band.
- **Timing bounds.** All timing keys above are load-jittered single-host
  measurements; only the order relations (`flush1 < c_write < flush2`)
  are structural.
- **Stuck-detach cost.** Not run in the battery itself; the 1.5 s bound
  demonstrates the semantics, the real battery bound is 30 s.
- **Node >64KB under a *slow* reader** (reader not draining) was not
  measured — my driver drains continuously (the battery's
  `capture_output=True` does too).
- No TTY-regime cells (harness is pipe-only, as before).

## 7 — Reproduce

```
cd corpus/live/r73-scout && sh reproduce.sh          # all receipts, ~60 s
# exits: every driver 0; battery_like_forever times out BY DESIGN (measured FAIL)
```

Receipts (`corpus/live/r73-scout/`): `paced_pilot*.json|.stdout.bin`
(8 structure cells), `infix_*.json` (5 infix + 2 controls),
`detach_eof.json`, `fd2_merge.json`, `node_census.json`,
`classifier_demo.{json,stdout.bin}`, `summary.json`,
`cpython_src_excerpts.txt`, `state.txt`; scripts `wire.py`,
`paced_parent.py`, `paced_parent_pg.py`, `paced_pilot.py`,
`infix_cells.py`, `detach_parent.py`, `detach_eof.py`, `fd2_parent.py`,
`fd2_merge.py`, `node_owner.js`, `c_owner.c`, `node_census.py`,
`node_pg_check.py`, `classifier_demo.py`, `summarize.py`.

No commit, no tracked mutation, no LOG/SCORECARD write.
