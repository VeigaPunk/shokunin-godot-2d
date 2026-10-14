# game-dev-2d round 73 — author (seat: author; host: devin)

## Declared move (verbatim)

"ARM A — topology depth (xconnector X4). The measured-unpinned set is
{prefix, infix, midline, append, fd2-inversion}; r72 pinned prefix +
midline + append. Now pin:
- INFIX: paced-flush owner (pre-buffered HEAD, timed mid-chunk child
  write between flushes — r72-boundary `paced2` measured INJ@126005 3x).
  Pin bounded ranges (topology class + offset bounds +/-1 chunk), never
  exact offsets.
- DETACH EOF-hold: detached descendant (double-fork/nohup) holds the
  capture pipe open past parent exit — battery EOF arrives late. Pin as
  a harness-integrity cell: parent exits clean, capture EOF delayed;
  bounded timeout so a stuck detach = measured FAIL not hang.
- FD2-INVERSION: descendant writes fd2 while fd2 merges into the same
  capture (2>&1) — r72-boundary fd2mrg measured `ERR\nHEAD  TAIL\n`.
  Pin the merge topology cell.
All cells through the RAW_CASES raw-wire machinery + owner-mode sweep
convention from r72. PYTHONUNBUFFERED stripped from controlled envs.

ARM B — non-Python owner census (xconnector X1, NEW-RUNTIME contact).
Node.js v24.21.0 is on this host (`node --version` to confirm).
Source-derived UNMEASURED predictions:
- node small-write owner -> SPLICE family (libuv uv_write try-write
  fast path = synchronous small writes).
- node >64KB single write -> INFIX (partial fill + event-loop queue
  remainder = third withholding layer beyond libc/Python).
- Control: `fs.writeSync(1,...)` = write-through; C owner cell
  (r72-critic c_reorder.c precedent — buffered C stdio reorders).
Implement a `node_census` arm in pygame_probe.py — spawn `node -e ...`
as the fd1-OWNER (not descendant): node writes HEAD, spawns printf
child via execSync, writes TAIL; capture the wire. Sweep {small,
>64KB, writeSync} cells. Viability-conditional: node absent ->
bounded blocked verdict, never fabricated."

## Landed changes

- `corpus/fixtures/pygame_probe.py` (+165/-0, purely additive):
  - docstring: r73 arm descriptions appended (`infix`, `fd2mrg`,
    `node_census`, `detach`).
  - `import shutil` (new line in the import block).
  - After `reorder_arm` (pygame_probe.py:256-320): `NODE_EXE` /
    `TIMEOUT_EXE` via `shutil.which`, `NODE_SRC_{SMALL,BIG,SYNC}` child
    programs, `INFIX_GAP_MIN=64`, and `node_arm()` — reorder_arm-class
    wire classifier + the `infix` class (interior INJECTED with owner
    payload on BOTH sides, gap > 64B vs the 1-byte midline spacing).
    Node absent -> `status=blocked topology=blocked_node_absent`.
  - In `main()` after the reorder_self emit, before `pygame.quit()`
    (pygame_probe.py:432-501):
    - `infix` — probe's OWN fd1: `INFIX-HEAD\n` + 140x1000B chunks force
      exactly one fill-flush mid-stream (140011 > 131072, < 262144);
      `printf INFIX-INJ` lands strictly after that flush while 60x1000B
      + `INFIX-TAIL\n` remain withheld. Positional, not timed — the
      r72-boundary `paced2` shape made deterministic.
    - `fd2mrg` — `os.dup2(1,2)` merges fd2 onto the fd1 capture, then a
      descendant `printf FD2-ERR >&2` reaches the wire immediately while
      `FD2-HEAD` sits withheld; fd2 restored in `finally` so the
      battery's stderr pipe stays intact for all later arms.
    - `node_census` — emits `node_present`/`node_version`/`node_major`
      then three spawned-owner cells: `node_small`
      (process.stdout.write), `node_big` (one 200000B write before the
      execSync spawn), `node_sync` (fs.writeSync). execSync uses
      `stdio:'inherit'` so the printf descendant writes the real fd1.
    - `detach` — spawned LAST: `subprocess.Popen([timeout, -s, KILL, 4,
      sh, -c, "sleep 0.9; printf 'DETACH-LATE\n' >&1"],
      start_new_session=True, stdin=DEVNULL)` holds the capture pipe
      ~0.9s past probe exit. `timeout` absent -> `status=blocked`.
- `corpus/fixtures/pygame_battery.py` (+129/-17 as committed — the
  pre-commit draft line read +146 by double-counting the 17 replaced
  lines; reviewer R1; the -17 are all inside
  the raw-wire processing block — machinery generalization, ZERO removed
  CASES/RAW_CASES rows; probe diff has 0 deletions):
  - r73 lattice paragraph in the docstring.
  - 19 appended CASES rows: metadata pins on `infix`/`fd2mrg`/`detach`
    (`fd1_isatty=False`, `bufsize=131072`) + `node_census`
    (`node_present=True`, `node_version=v24.21.0`) + per-cell pins:
    `node_small`/`node_sync` midline_splice head_at=0 wire_bytes=19
    ret=0; `node_big` infix + bounded `injected_at` (40000,199000) +
    `tail_at` (199000,200100) + wire_bytes=200019.
  - RAW_CASES extended, prior row byte-identical: r73 rows are
    `(name, pinned, markers, offset_bounds)` — a 3-tuple marker set is
    classified {prefix_reorder, midline_splice, infix, append} by the
    same relation plus a >64B-gap infix rule; a 2-marker row
    `(anchor, late)` classifies {eof_hold, premature, markers_missing};
    `offset_bounds` add per-key (lo,hi) result rows. `_rel` keys measure
    marker offsets relative to HEAD so the pin is independent of how
    much wire precedes the cell.
    - `infx_wire_topo` -> `infix` + bounds head_at(1500,2600),
      injected_rel(125000,127500) [= +/-1 chunk around measured 126011],
      tail_rel(199500,201000).
    - `fd2m_wire_topo` -> `prefix_reorder` on (FD2-HEAD, FD2-ERR,
      FD2-TAIL).
    - `det_wire_eof` -> `eof_hold` on (PYGAME_PROBE_DONE, DETACH-LATE).
  - The legacy 2-tuple row still flows through the same code path with
    identical result fields (`arm=reorder_self`, `key=wire_topology`,
    same idx reason format).

## Measured result (80/80 PASS, 4 stable reps)

Wire topologies, all confirmed on the captured stdout itself:

| cell | delivered wire (markers) | topology | pin basis |
|---|---|---|---|
| `infix` | `INFIX-HEAD` …~126KB… `INFIX-INJ` …~74KB… `INFIX-TAIL` | **infix** | injected_rel=126011 byte-identical x4; inj strictly interior, owner payload both sides |
| `fd2mrg` | `FD2-ERR` @0-of-cell < `FD2-HEAD` < `FD2-TAIL` | **prefix_reorder** | merged-fd2 descendant byte outranks withheld fd1 buffer |
| `detach` | `PYGAME_PROBE_DONE` then `DETACH-LATE` | **eof_hold** | capture EOF held ~0.9s past probe exit; parent rc=0 |
| `node_small` | `HEAD INJECTED TAIL` 19B | midline_splice | try-write synchronous (predicted SPLICE family) |
| `node_big` | `HEAD ` + A… `INJECTED` + A… ` TAIL` 200019B | **infix** | inj {65541,98309} across reps — pipe-drain jitter inside bound (65536/69637/131072 seen across seats) |
| `node_sync` | `HEAD INJECTED TAIL` 19B | midline_splice | fs.writeSync write-through control |

- Both ARM B predictions confirmed on v24.21.0: small writes splice
  (libuv try-write is synchronous for sub-capacity pipe writes), and a
  200000B write goes infix — the event-loop remainder is a real third
  withholding layer, blocked by execSync. First non-Python owner
  contact: the topology family survives a runtime swap; only the
  withholding mechanism changes.
- `infx_wire_topo_injected_rel` = 126011 in all 4 reps — the same
  fill-flush boundary r72-boundary measured as 126005 (their HEAD was
  5B, ours is 11B; 126011-11 = 126000 = 126 chunks exactly). The
  positional construction (spawn after exactly 140 chunks) removes
  paced2's timing dependence entirely.
- `nbig` inj offset is the one jittered offset: 65541/65541/65541/98309
  here, {65536, 131072} in r73-critic's scratch — pipe-capacity
  multiples set by reader drain rate. Bounded, never exact, as briefed.
- Harness integrity: probe exits rc=0 at ~9.8s wall; `DETACH-LATE`
  lands after `PYGAME_PROBE_DONE` in every rep — proof the battery's
  `communicate()` kept reading a post-exit writer (EOF delayed).
  Double-bounded: inner `timeout -s KILL 4` + outer `TIMEOUT_S=30`.
- Prior rows: all 55 r72 cases still PASS under original pins
  (`git diff` shows 0 removed case lines; probe diff fully additive).

## Evidence

- `python3 corpus/fixtures/pygame_battery.py --runs
  corpus/live/r73-author/runs` -> `totals: cases=80 pass=80 fail=0
  launch_ok=True done_marker=True exit=0`, exit 0, ~10s wall, x4 reps:
  `pygame-20261014T153659421700Z`, `...T153713657039Z`,
  `...T153723580295Z`, `...T153736173937Z`. Every new-case verdict PASS
  in all four; `probe.stdout.txt` tails all read
  `PYGAME_PROBE_DONE\nDETACH-LATE\n`.
- Standalone dry-runs before landing (discipline carried from r72):
  `corpus/live/r73-author/infix_wire.bin` (inj@126011, tail@200020,
  len 200031, 3/3 identical), `fd2_wire.bin`
  (`FD2-ERR\nFD2-HEAD\nFD2-TAIL\n`, stderr verified restored),
  detach harness probe (rc=0, EOF at +912ms), node cells direct
  (`small`/`sync` midline 19B, `big` infix inj 69637).
- Sibling scratch corroborates: r73-critic `node_census.json` (small
  midline x3), `node_census_edges.json` (big200k infix, inj
  {65536,131072}), `detach_eof.json` (eof_lateness ~1450ms on a 1.5s
  hold, DETACHED-LATE post-DONE); r73-scout `infix_cs1000_*.json`
  (inj@126005 x3), `detach_eof.json` (setsid/nohup hold ~450ms),
  `fd2_merge.json` (child_fd2 -> `CERR\nHEAD  TAIL\n` prefix_reorder).
- Probe dry-run receipt: `corpus/live/r73-author/probe_dry.stdout.txt`
  — marker indices REORDER-CHILD@1892 < REORDER-HEAD@1906 (r72
  preserved), INFIX-INJ@128019 interior, FD2-ERR@202120 <
  FD2-HEAD@202128, DETACH-LATE@202700 > DONE@202682.
- `lsp` disclosure: no `lsp`/pyright/pylsp/jedi/ruff-lsp on this host
  (r72-boundary checked the same PATH) — hand edits only; all edits are
  additive insertions, no symbol renames, so no callsite risk. ARM key
  names verified by the battery runs themselves.

## Remaining unknowns / risks

- `nbig_inj_bound` (40000,199000) is deliberately wide: try-write
  delivers pipe-capacity multiples while the reader drains; a path
  where ALL 200005 pre-spawn bytes flush synchronously would land INJ
  adjacent to TAIL -> midline/degenerate -> measured FAIL (the topology
  pin is the real assertion; the bound documents the observed region).
- `infx_wire_topo_head_at` (1500,2600) bounds the ABSOLUTE index, which
  includes jittering preceding-wire bytes (ARM line widths) — observed
  2004-2008. `injected_rel`/`tail_rel` are the mechanism-pure pins.
- `node_ver` pins `v24.21.0` exactly — per-host convention, same class
  as `bufsize=131072`. Node absent -> `blocked_node_absent` verdicts +
  FAILed pins (bounded, honest); `timeout` absent -> detach blocked the
  same way.
- `detach` margin: spawn is the last action before quit+DONE; teardown
  is ~ms vs the 900ms hold — a >900ms quit stall would flip to
  `premature`. Not observed (eof margin ~890ms each rep).
- The detached writer holds the battery's stderr pipe open equally
  (inherited fd2) — EOF delayed on both streams, symmetric and bounded;
  it writes nothing to fd2.
- fd2mrg restores fd2 via dup2-finally; an exception between dup and
  restore still restores. TTY regime: all self-wire cells would show
  line-buffered honest order — `fd1_isatty=False` pins the pipe regime
  (same convention as reorder_self).
- Love/Godot batteries untouched; no git mutations; commits remain
  operator-owned.
