# r73 verifier — topology depth + node owner census (lane g2d)

Seat: verifier | Host: CPython 3.14.7 (`io.DEFAULT_BUFFER_SIZE` = 131072 —
this build's constant), pygame 2.6.1 / SDL 2.32.72, node v24.21.0
(`/usr/bin/python3`, node via fnm). All commands from lane-repo root;
receipts in `corpus/live/r73-verifier/` only; no writes elsewhere; no
git mutations; no subagent dispatch.

## Landing

Polled from 15:19Z; HEAD was `2dd108b` (r72 report-last) through 15:43Z.
The arm appeared in the working tree ~15:35Z and was committed as
**`43bef2d`** ("r73: topology depth — infix pin … + Node.js owner
census"), commit timestamp 15:43:36Z, detected on this seat's poll at
15:44:15Z. I dry-replayed the working tree during polling — the first
draft failed 3 infix bound rows (absolute-vs-relative offset mixup,
77/80); the committed revision carries the fix (`_rel` keys + widened
`head_at` band) and passes clean.

`git show --name-only 43bef2d` → **only** `corpus/fixtures/
pygame_probe.py` (+165/−0), `corpus/fixtures/pygame_battery.py`
(+146/−17), `reports/round-73/r73-author.md`. Zero Godot/LOVE paths,
zero scorecard files. The −17 battery lines are the r72 raw-wire
classifier block replaced by the generalized `raw_topo3` machinery —
**zero removed CASES/RAW_CASES rows** (`git diff | grep '^-\s*("'`
matches only the old `("REORDER-HEAD",…)` generator argument inside the
replaced code, not a data row; the `("self_wire_reorders", …)` row is
byte-preserved). Probe diff is fully additive (`git diff … | grep -cE '^-'
→ 0`; the `+` count over reports/ is the new report file). Working tree
clean under `corpus/fixtures/` post-commit; sha256 probe
`9a7456a3…d0d7f`, battery `6d3fbf5f…6fe79`
(`corpus/live/r73-verifier/sha256-committed.txt`, `state.txt`).

## Item 1 — committed battery replay ×2 → PASS (80/80, exit 0, ×2)

`PYTHONDONTWRITEBYTECODE=1 python3 corpus/fixtures/pygame_battery.py
--runs corpus/live/r73-verifier/runs` — runs
`pygame-20261014T154429348129Z` and `…T154444922296Z`, both
`totals: cases=80 pass=80 fail=0 launch_ok=True done_marker=True
exit=0`, ~10.0s wall (r72 was 8.9s; +~1.0s ≈ the 0.9s detach hold + 3
node spawns). Case count 55 → 80 (+19 CASES rows +5 raw-wire rows +1
expanded bounds row — infx carries 3 bound keys). All 55 prior r72
cases still PASS.

**Determinism across the two HEAD replays** (and the sweep below): every
r73 ARM line is byte-identical across all three runs except
`node_big.injected_at` (65541, 65541, 131077 — the documented
pipe-drain bimodal jitter, all inside the pinned `(40000,199000)`
band; `topology=infix` stable in every rep). Raw-wire offsets:

| marker relation | r1 | r2 | sweep | verdict basis |
|---|---|---|---|---|
| `injected_rel` (INFIX-INJ − INFIX-HEAD) | **126011** | **126011** | **126011** | byte-exact ×3; = 11B head + 126×1000B, the r72-boundary flush-epoch law |
| `tail_rel` | 200020 | 200020 | 200020 | byte-exact |
| `head_at` (absolute) | 2008 | 2006 | 2008 | ±2B ARM-line-width jitter, inside (1500,2600) |
| FD2-ERR vs FD2-HEAD | 202120<202128 | 202118<202126 | 202120<202128 | prefix_reorder ×3 |
| DONE vs DETACH-LATE | 202682<202700 | 202680<202698 | 202683<202701 | eof_hold ×3 |
| REORDER-CHILD vs HEAD | 1892<1906 | 1890<1904 | 1892<1906 | r72 hazard preserved |

My own marker scans of `probe.stdout.txt` (not just the verdicts)
confirm every classification: `INFIX-INJ` strictly interior with ~126KB
of owner payload before and ~74KB after; `FD2-ERR` lands before the
withheld `FD2-HEAD`; the stream literally ends
`PYGAME_PROBE_DONE\nDETACH-LATE\n` — the captured EOF arrived ~0.9s
after probe exit while `probe_exit=0` (verdicts `probe_elapsed_s`
9.94–9.97 vs r72's 8.92).

## Item 2 — ambient `PYTHONUNBUFFERED=1` sweep → PASS (80/80)

`PYTHONUNBUFFERED=1 python3 corpus/fixtures/pygame_battery.py …` → run
`pygame-20261014T154500288734Z`, 80/80, exit 0. `run_process` pops
PYTHONUNBUFFERED from the probe env (pygame_battery.py:~154) so all four
own-wire cells (self/infix/fd2mrg/detach) keep their buffered-pipe
regime; spawned children (reorder, withhold, **and node**) all run under
`CHILD_ENV` — the r73 node_arm passes `env=CHILD_ENV` at
pygame_probe.py:293. Ambient env cannot collapse a pin.

## Item 3 — prior-rows byte-compare vs newest committed run → STABLE

Newest committed-tree receipt: r72-era
`corpus/live/runs/pygame-20261014T144544784421Z/probe.stdout.txt`
(55-case run on the pre-r73 HEAD). Parsed per-key against replay r2's
prior prefix (everything before `INFIX-HEAD`):

- ARM key sets identical (11 arms, zero added/removed keys on prior
  arms).
- **Zero stable-key drift** — all topology/offset/byte/ret/bufsize/
  marker keys byte-identical (reorder_* lines verbatim, incl.
  `head_at=8 injected_at=0 tail_at=14 wire_bytes=19`).
- 23 values moved, **all bound-pinned jitter keys** (dt_* / hz /
  *_wait_ms / *_read_ms / eof_ms / nopump_total_ms) — every one inside
  its CASES bound (all 55 prior rows PASS).
- Raw-marker block `REORDER-CHILD\nREORDER-HEAD\nREORDER-TAIL`
  byte-preserved in order (prefix_reorder hazard intact).

## Item 4 — LOVE sibling battery → PASS (19/19, control)

`python3 corpus/fixtures/love_battery.py --runs
corpus/live/r73-verifier/love-runs` → `love-20261014T154510313174Z`,
`totals: cases=19 pass=19 fail=0`, exit 0. The commit touched zero
LOVE/Godot paths (`git diff 2dd108b 43bef2d -- love_battery.py
run_battery.py` empty); sha256 `25977ad9…13647` unchanged from the r72
recorded value.

## Item 5 — viability gates (independent spot checks)

- **node-absent**: `env -i PATH=/usr/bin:/bin python3 pygame_battery.py`
  → 65/80, battery FAIL, and all 15 failures are exactly the node-pinned
  rows reporting `blocked_node_absent` / `key missing` — bounded honest
  FAILs, no fabricated wire, no hang (matches "never fabricated").
- **detach bound**: the cell self-bounds via `timeout -s KILL 4` and
  spawns LAST; my three runs all eof_hold with no stall. The stuck-detach
  path was exercised by r73-critic's replay (holder sleep 60 →
  `det_wire_eof` FAIL in 13.1s, markers_missing, no stray, no hang —
  `corpus/live/r73-critic/replay/stuck_detach/`), which this seat
  reviewed but did not re-run (the landed cell itself bounded correctly
  ×3 here).

## Per-claim adjudication

| # | claim (r73 brief/author) | verdict | evidence |
|---|---|---|---|
| C1 | INFIX pinned as topology class + bounded offsets (±1 chunk), never exact | **AGREE** | `infx_wire_topo=infix` ×3; `injected_rel=126011` byte-exact ×3 (bounds 125000–127500), `tail_rel=200020` ×3; interior INJ with owner payload both sides; positional construction (fill-flush, no sleeps) per critic F4 fold |
| C2 | DETACH EOF-hold: parent exits clean, capture EOF delayed, bounded timeout = measured FAIL not hang | **AGREE** | `det_wire_eof=eof_hold` ×3 (DONE@20268x < DETACH-LATE@20269x); probe_exit=0; elapsed +~1.0s vs r72; kill bound verified by critic stuck-test (13.1s FAIL, no hang) |
| C3 | FD2-INVERSION pinned as merge topology cell | **AGREE** | `fd2m_wire_topo=prefix_reorder` ×3 — probe-side `dup2(1,2)` + distinct `FD2-*` markers make the wire attributable (critic F5 fold); `merge=fd2_dup2_to_fd1` receipt; fd2 restored (later arms unaffected, 80/80) |
| C4 | node small-write owner → SPLICE family | **AGREE** | `node_small` midline_splice, wire `HEAD INJECTED TAIL\n` 19B, ×3 — libuv try-write synchronous, as predicted |
| C5 | node >64KB write → INFIX (event-loop remainder = third withholding layer) | **AGREE** | `node_big` infix ×3; `injected_at` {65541,65541,131077} — pipe-capacity-multiple reader-race, all inside (40000,199000); `wire_bytes=200019`; tail bound holds |
| C6 | writeSync control = write-through | **AGREE** | `node_sync` midline_splice 19B ret=0 ×3 |
| C7 | RAW_CASES machinery + owner-mode sweep convention; PYTHONUNBUFFERED stripped | **AGREE** | r73 rows ride the generalized raw_topo3; all controlled envs use CHILD_ENV / run_process pop; sweep 80/80 |
| C8 | prior rows byte-identical; insertion-only | **AGREE** | 0 removed case rows; probe fully additive; prior-row stable keys byte-identical to r72 receipt |
| C9 | LOVE sibling battery untouched = control | **AGREE** | 19/19 PASS, fixture bytes unchanged |
| C10 | node absent → bounded blocked verdict | **AGREE** | PATH-restricted run: 15 bounded FAILs on node rows only, `blocked_node_absent` emitted |

## Overall

**AGREE — 10/10 claim items.** The r73 arm lands the full X4 topology
depth set (infix positional pin at the 126011 flush-epoch, detach
eof_hold, fd2-merge prefix_reorder) plus the X1 new-runtime contact
(node owner: small→splice, 200KB→infix, writeSync→splice on v24.21.0),
all through the raw-wire machinery with determinism-grade pins. Both
briefed node predictions measured true on this host. Replays: 80/80 ×2
on HEAD `43bef2d` + 80/80 under `PYTHONUNBUFFERED=1` + LOVE 19/19
control + node-absent gate behaves as designed. Prior 55 rows stable
(zero non-jitter drift). HEAD has not moved past the author commit at
report time — no report-last delta to audit.

## Receipts (`corpus/live/r73-verifier/`)

- `runs/pygame-20261014T154429348129Z/` — HEAD replay 1, 80/80
- `runs/pygame-20261014T154444922296Z/` — HEAD replay 2, 80/80
- `runs/pygame-20261014T154500288734Z/` — PYTHONUNBUFFERED=1 sweep, 80/80
- `runs/pygame-20261014T153638981800Z/` — pre-fix working-tree run
  (77/80, caught the absolute/relative bound mixup before commit)
- `runs/pygame-20261014T154203246549Z/` — fixed working-tree preview,
  80/80
- `runs-nodeabsent/pygame-20261014T154619219184Z/` — node-absent gate,
  65/80 (15 bounded node-row FAILs)
- `love-runs/love-20261014T154510313174Z/` — LOVE control, 19/19
- `state.txt`, `sha256-committed.txt` — host + fixture hashes

## Remaining risks (bounded, disclosed, non-blocking)

- `infx_wire_topo_head_at` pins an ABSOLUTE offset against jittered
  preceding-wire bytes (observed 2005–2008, bound 1500–2600) — couples
  to upstream ARM-line widths; `_rel` keys are the mechanism-pure pins
  (critic F4 residual).
- `node_big.injected_at` is a reader-race multiple of pipe capacity
  (65541/131077 observed; {65536,69637,131072} across seats) — bounded
  only, per-design; an async-spawn owner would flip the class
  (critic F2 residual — execSync's loop-blocking is the mechanism).
- Latent: `proc.communicate()` after `kill()` in `reorder_arm`/
  `node_arm` has no post-kill bound (pygame_probe.py:~208, ~296) —
  unreachable from landed cells (critic F1 residual).
- `node_ver`/`infx_bufsize`/`self_bufsize` pin per-host constants
  (v24.21.0 / 131072) — same convention as r72 `whs_bufsize`.
- Node-absent host → battery verdict FAIL (honest; the pins assume the
  measured runtime — this is the intended gate, not a defect).
- All own-wire cells are pipe-regime pins: under a tty, fd1 is
  line-buffered and the wires honestly differ — `fd1_isatty=False`
  pins record the regime (same convention as reorder_self).
