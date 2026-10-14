# r73 reviewer — topology depth + node census, pygame lane (g2d, wave w13)

Seat: **reviewer** (LEAF, dispatched specialist; recommendation only — the
canonical Rust runtime is the sole judge). Host: devin — CPython 3.14.7
(`io.DEFAULT_BUFFER_SIZE` = 131072, pipe capacity `F_GETPIPE_SZ` = 65536),
`pygame 2.6.1 / SDL 2.32.72`, **node v24.21.0** (fnm shim path). Lane repo:
`~/Projects/shokunin/game-dev-2d-shokunin`. Write scope: this report +
`corpus/live/r73-reviewer/` only; no tracked edits, no git mutations.

Artifact reviewed: commit **`43bef2d`** ("r73: topology depth — infix pin
(paced flush, byte-exact inj@126011) + detach EOF-hold + fd2-merge inversion
+ Node.js owner census …"), three files: `corpus/fixtures/pygame_probe.py`
(+165/−0), `corpus/fixtures/pygame_battery.py` (+129/−17),
`reports/round-73/r73-author.md` (new). Committed blobs are byte-identical
to the post-commit working tree (`sha256sum` probe `9a7456a3…`, battery
`6d3fbf5f…`; `committed.sha256`), so every replay below ran on the
committed bytes. `git status --porcelain corpus/fixtures/` clean at
`43bef2d`.

**`lsp` disclosure.** No language-server device on this host (`lsp`,
`pyright`, `basedpyright`, `pylsp`, `jedi-language-server`, `ruff-lsp` all
ABSENT from PATH; `pygls`/`jedi` not importable). Every caller/definition
claim below is a line-cited textual inspection, recorded per seat card —
not presented as semantic proof.

## Verdict summary

The landed arm resolves the round-73 move and the claims resolve on replay:
infix is pinned at the fill-flush boundary (independently reproduced
byte-exact), the detach EOF-hold is a bounded harness-integrity cell whose
stuck mode is a measured FAIL, the fd2-merge inversion is pinned on the
merged capture, and the node census lands both xconnector predictions
(small→splice, >64KB→infix, writeSync→splice) with honest viability
conditionals. **80/80 PASS ×3 idle + env sweep + loaded on my receipts;
zero stable prior-row diffs; both blocked paths and both failure modes
exercised.** Two LOW record/scope findings (R1, R2), three INFO notes
(R3–R5); no functional defect found in scope.

## Findings by severity

### R1 — LOW (open): author report battery line count does not match the landed commit

`r73-author.md:69` states the battery change is "`+146/-17`". The landed
commit is **+129/−17** (`git show --numstat 43bef2d` →
`129 17 corpus/fixtures/pygame_battery.py`; the report's own probe claim
"+165/-0" is correct). 146 = 129 + 17: the count appears to double-count
the 17 replaced machinery lines. Impact: evidence honesty at the report
layer only — the artifact is correct and the report *does* disclose the
−17 as the raw-wire machinery generalization; the "ZERO removed
CASES/RAW_CASES rows" half is **true** (all 17 removed lines are the old
inline reorder_self classification, verified line-by-line). Same class as
r72 R1 (report text vs artifact drift).

### R2 — LOW (open, scope note): C owner cell named in the ARM B controls is not in the tracked census

The author brief's ARM B prediction block names two controls:
"`fs.writeSync(1,...)` = write-through; C owner cell (r72-critic
c_reorder.c precedent — buffered C stdio reorders)". The landed census
implements the explicit sweep {`node_small`, `node_big`, `node_sync`}
(the brief's imperative sentence) plus the writeSync control, but **no C
cell**: `grep -iE "gcc|\.c\"|c_owner|stdio\.h|fwrite"` over both committed
fixtures → empty. The C re-pin is on record in sibling scratch only
(r72-critic `c_reorder.c`/matrix; r73-scout `c_buffered`→prefix_reorder,
`c_big_chunks`→infix; r73-critic `node_census_edges.json` exists, spot-
checked). Bounded claim: the tracked non-Python census is node + writeSync;
the C precedent remains scratch-measured. Not claim drift (the author
report never claims a C cell) — a scope-completeness note for the record.

### R3 — INFO: the `eof_hold` pin is order-based; the hold magnitude is unpinned

`det_wire_eof` pins `DETACH-LATE` *after* `PYGAME_PROBE_DONE`
(`pygame_battery.py:209-210, :349-356`). That witnesses a post-DONE writer
on the capture pipe, which — with the holder spawned unwaited and sleeping
0.9 s — implies the capture EOF outlived probe exit. The *magnitude* is
recorded but not asserted: `probe_elapsed_s` (my receipts 9.94 s vs
pre-author 8.99 s → **+0.95 s**, `pg-runs/…T154433/verdicts.json`) and the
ARM `hold_ms=900` is a declared parameter, not a measurement
(`pygame_probe.py:496`, emitted before the spawn). Undetected regression
mode: a *short* hold with a fast teardown still reads `eof_hold`. The
stuck mode **is** caught: scratch mutation (`sleep 30` holder) →
`timeout -s KILL 4` kills at 4 s → `det_wire_eof` = `markers_missing`,
**79/80, battery wall 13 s, zero stray holders** — a measured FAIL, never
a hang, as briefed.

### R4 — INFO: the infix class rule is necessary-but-not-sufficient; the offset bound is load-bearing

`raw_topo3` labels interior INJ with >64 B owner payload on both sides as
`infix` (`pygame_battery.py:308-325`). Under the `-u` wrapper the topo row
still reads `infix` (no fill-flush → INJ at 140011) while
`infx_wire_topo_injected_rel` correctly FAILs — so the class label alone is
not a mechanism witness; the fill-boundary offset bound (±1 chunk) does the
discriminating work. The mechanism claim itself is independently
reproduced: my standalone replica of the probe's exact cell gives
`injected_rel=126011`, `tail_rel=200020`, **14000 B written before the
child's write but delivered after it** (3/3) — the r72-boundary F2 infix
signature, now positional rather than paced.

### R5 — INFO: `node_big` offset is a pipe-capacity-multiple artifact, bounded by design

My receipts observe `injected_at` ∈ {65541, 98309, 131077} (idle/sweep/
loaded) and siblings observe {65536, 131072}. All are `5 + k·65536`
(k = 1, 1.5, 2; 5 = the `HEAD ` prefix) — the try-write/queue split at
host pipe capacity (65536, confirmed `F_GETPIPE_SZ`). The pin is the
topology class + the wide bound (40000, 199000); the failure mode where
every pre-spawn byte flushes synchronously (INJ adjacent to TAIL) is
caught by the class rule as `midline_splice` → FAIL. Honest bounded
saturation, as the report declares.

## Verified — commands replayed, evidence resolves

**V1 — landing, scope, byte stability.** Commit `43bef2d` = the two
fixtures + the author report; no LOG/SCORECARD/Godot/LOVE paths
(`git diff --name-only 2dd108b..43bef2d | grep -iE "godot|love|\.gd|\.tscn"`
→ empty). Probe diff **pure additive** (165/0); battery 129/17 with all 17
removed lines being the old raw-wire block and **0 removed CASES/RAW_CASES
rows** (diff inspected line-by-line). The legacy 2-tuple RAW row's result
dict is **byte-identical** pre-author vs committed (`self_wire_reorders`:
same `arm/key/pinned/observed/verdict/reasons`), and all 54 prior CASES
result key sets are identical.

**V2 — committed battery replay.** `python3 corpus/fixtures/
pygame_battery.py --runs corpus/live/r73-reviewer/pg-runs` → `totals:
cases=80 pass=80 fail=0 launch_ok=True done_marker=True exit=0`, exit 0,
×3 (`pygame-20261014T154433/154443/154453…Z`). Env sweep
`PYTHONUNBUFFERED=1 …` → 80/80 (`pg-runs-envsweep/…T154505…Z`). Loaded
(32×`yes` hogs) → 80/80 (`pg-runs-loaded/…T154518…Z`). Case count 55 → 80
= 19 appended CASES + 3 new RAW topo rows + 3 offset-bound rows.

**V3 — prior-row stability.** Comparator
(`corpus/live/r73-reviewer/compare_prior.py`), pre-author receipt
(`pg-runs-pre/…T151858…Z`, r72 hashes) vs committed: **zero stable diffs**;
all 55 prior cases PASS; every differing value is a jitter-class timing key
(dt/fps/l1_wait/…). 25 rows added, none missing.

**V4 — independent ground truth (scratch, all outside the fixture).**
- *Infix* (`infix_replica.py`): exact replica of `pygame_probe.py:439-450`
  → `inj_rel=126011`, `tail_rel=200020`, 14000 B withheld-before-child,
  3/3 identical; wire = `[HEAD+126×1000][INJ][14×1000A][60×1000B][TAIL]`.
- *fd2mrg* (`fd2_detach_replica.py`): `FD2-ERR\nFD2-HEAD\nFD2-TAIL\n`,
  ERR@0 < HEAD@8 < TAIL@17, `stderr_leak=False`, 3/3.
- *detach*: parent DONE at ~10 ms, `DETACH-LATE` + EOF at ~911 ms, 3/3;
  both capture pipes held symmetrically (stdout EOF 912.19 ms, stderr
  912.21 ms) — the author's "holds the stderr pipe equally" claim verified.
- *node* (`node_ref.js` + `raw_reader.py`): small → `HEAD INJECTED TAIL\n`
  (19 B) splice; `fs.writeSync` → splice; 200000 B single write → infix
  with INJ at **65536** (3/3); plain `execSync` without `{stdio:'inherit'}`
  drops INJ entirely — the trap the landed code correctly avoids
  (`pygame_probe.py:266-283`).
- *Witness-grade paced ref* (`paced_witness_ref.py`): withheld 21.3–21.8 kB
  at inj@126005 — concurs with r72-boundary `paced2` (21279/21683/21538 B)
  and r73-scout (54992–55000 B at K=180): same mechanism, different K.

**V5 — error paths (all bounded).**
- *node absent* (`PATH=/usr/bin:/bin`): probe emits
  `node_census | node_present=False node_version=absent node_major=absent`
  and `node_small/big/sync | status=blocked topology=blocked_node_absent
  ret=NA`; exit 0, DONE present — **no fabricated wire**. Battery → 65/80,
  exactly the 15 node rows FAIL (`blocked_node_absent`, `key missing`,
  `'NA' != '0'`), `launch_ok=True` — honest bounded red.
- *timeout absent* (`PATH=<scratch-with-node-only>`): `detach | status=blocked
  mode=blocked_no_timeout`, no `DETACH-LATE`, exit 0; node cells still
  measure.
- *stuck detach* (scratch probe copy, holder `sleep 30`): 79/80,
  `det_wire_eof` `markers_missing`, 13 s wall, no stray processes.
- *infix marker missing* (scratch probe copy, `INFIX-HEAD` renamed): 4
  bounded FAILs (`markers_missing` + `head_at` bound + 2 `key missing`).
- *fd2 closed* (`2>&-`): exit 0, DONE, all 22 ARM lines; FD2 cell still
  ERR<HEAD<TAIL (fd2 reallocated before `os.dup`) — no crash.

**V6 — regime guard (by design red).** `--python <pyu_wrapper.sh>` (`exec
python3 -u`): 77/80 — exactly `self_wire_reorders` (r72's known cell),
`infx_wire_topo_injected_rel` (140011 outside bound) and `fd2m_wire_topo`
(now honest midline). The new cells inherit the r72 pipe+block-buffered
regime pin; `fd1_isatty=False` records it. Canonical invocation green.

**V7 — sibling control.** LOVE battery on the committed tree: **19/19 PASS,
exit 0** (`love-runs-committed/…T154835…Z`); zero LOVE/Godot paths in the
diff (hash-level argument). Godot battery not replayed (heavy; no paths).

**V8 — callers / definitions / diagnostics (textual, line-cited).**
All new symbols have a single definition and all call sites resolve:
`NODE_EXE`/`TIMEOUT_EXE` (`pygame_probe.py:260-261`) → `node_arm:292,296`,
`main:467,471,479,492,498`; `INFIX_GAP_MIN:282` → `:313`; `node_arm:285` →
3 calls `:481-483`; `raw_topo3:308` → `:339`; `RAW_ARMS:328` → `:336`;
`check` (`pygame_battery.py:248`) → `:296` (CASES) and `:363` (bounds).
No renames; `import shutil:87` used only by the two `which` calls. ARM
grammar contract intact (new lines parse; values space-free; new arm and
marker namespaces collision-free — each raw marker count=1 in stdout).
Error paths: missing markers → `markers_missing`; missing bound key →
`key missing`; both produce FAIL rows, never exceptions (verified V5).

**V9 — author receipts re-read.** 4 author runs all 80/80
(`corpus/live/r73-author/runs/…T1536/1537…Z`); dry-run receipts byte-checked:
`infix_wire.bin` (200031 B, inj_rel 126011, tail_rel 200020), `fd2_wire.bin`
(`FD2-ERR/FD2-HEAD/FD2-TAIL`), `probe_dry.stdout.txt` indices
REORDER-CHILD@1892 < REORDER-HEAD@1906, INFIX-INJ@128019, FD2-ERR@202120 <
FD2-HEAD@202128, DONE@202682 < DETACH-LATE@202700 — every stated index
reproduces. New-pin stability across my 5 receipts + author's 4:
`injected_rel=126011` and `tail_rel=200020` on all 9; `head_at` 2004–2009
(inside bound 1500–2600); `node_big` {65541, 98309, 131077} (inside bound).

Claim adjudication: *infix pin* — CONFIRMED (byte-exact, independently
reproduced); *detach EOF-hold harness-integrity* — CONFIRMED with the R3
magnitude caveat; *fd2-merge inversion* — CONFIRMED on the merged capture;
*node small→splice / >64KB→infix / writeSync→write-through* — CONFIRMED
independently, with offsets explained by pipe capacity; *viability
conditional* — CONFIRMED both directions (absent → blocked, never
fabricated).

## Residual risk

1. **R3 detach magnitude**: the pin is order-based; a short-hold regression
   would not be caught (stuck/missing modes are caught). The elapsed delta
   (+0.95 s) is the only magnitude witness and is unpinned.
2. **`node_big` bound width**: (40000, 199000) is deliberately wide; future
   reader-drain regimes could approach its edges. The honest all-flushed
   FAIL mode exists and is class-caught.
3. **Per-build/per-host pins**: `bufsize=131072` and the infix fill law
   (textio 8192 / buffer 131072) are this build's; `node_version=v24.21.0`
   is exact (node-less/different-version hosts read honest red, verified);
   `node_big`'s split assumes pipe capacity 65536.
4. **Regime pin**: infix/fd2mrg/self-wire cells are correct only under the
   battery's pipe + block-buffered probe; a `-u` wrapper reads 3 by-design
   FAILs (documented, V6). TTY regime untested.
5. **Marker-namespace coupling**: `_rel` offsets depend on unique marker
   strings in the captured stdout; a future cell reusing one of these
   strings would corrupt offsets (currently count=1 each).
6. **R2 C cell**: tracked census is node-only; the C precedent stays
   scratch-measured.
7. **`resume_continuity_v1` / one-canonical-runtime / same-identity
   rerouting**: N/A to this diff — fixture-only change, no runtime route,
   resume path, or judge surface touched; the canonical Rust runtime is the
   sole judge and outside this lane.

## Verification gaps

1. No `lsp` device (recorded above) → no semantic references/definition/
   diagnostics; all caller claims are textual line citations.
2. Godot battery not replayed (heavy; zero Godot paths in the diff —
   hash-level argument only).
3. TTY stdout regime untested (harness is pipe-only by design).
4. The `premature` detach branch (`b <= a`) is code-read only;
   `eof_hold` and `markers_missing` are exercised.
5. Loaded regime sampled once (32 hogs); `node_big`'s jitter envelope is
   sampled, not saturated.
6. Sibling seat reports/scratch were not used as evidence for any claim
   above except where explicitly cited as sibling context (V4 paced ref,
   R2 C precedent); every finding stands on my receipts.

## Receipts (all under `corpus/live/r73-reviewer/`)

- Pre-author baseline: `pg-runs-pre/…T151858…Z/` (55/55 at r72 hashes);
  `pre-author.sha256`, `pre-head.txt`
- Idle replay ×3: `pg-runs/pygame-20261014T{154433499495,154443523514,
  154453460003}Z/`
- Env sweep: `pg-runs-envsweep/…T154505505141Z/`; loaded:
  `pg-runs-loaded/…T154518874593Z/`
- Regime: `pg-runs-uwrap/…T154721363423Z/` + `pyu_wrapper.sh`
- Error paths: `pg-runs-nodeabsent/…T154633529003Z/`,
  `probe_nodeabsent.{stdout,stderr}.txt`; `probe_notimeout.*` + `bin/node`;
  `pg-runs-stuckdetach/…T154808580157Z/`; `pg-runs-infmissing/…T154825202292Z/`;
  `probe_nofd2.stdout.txt`; `stuck-scratch/`
- Independent harnesses: `infix_replica.{py,json}`, `paced_witness_ref.{py,json}`,
  `paced_driver.py`+`paced_ref.json`, `fd2_detach_replica.{py,json}`,
  `node_ref.js`+`node_big_timed.json`, `raw_reader.py`, `detach_ref.py`+
  `detach_driver.py`+`detach_ref.json`, `fd2_ref.out`
- Stability/compare: `compare_prior.py`, `committed.sha256`,
  `snapshots/{probe,battery}-committed.py`
- Sibling control: `love-runs-committed/love-20261014T154835159572Z/`
- Author receipts compared: `corpus/live/r73-author/runs/…T{153659,153713,
  153723,153736}…Z/`, `infix_wire.bin`, `fd2_wire.bin`, `probe_dry.stdout.txt`

## Method (exact commands, from repo root)

```
git show --numstat 43bef2d ; git diff --numstat 2dd108b..43bef2d -- corpus/fixtures/
python3 corpus/fixtures/pygame_battery.py --runs corpus/live/r73-reviewer/pg-runs            # ×3
PYTHONUNBUFFERED=1 python3 corpus/fixtures/pygame_battery.py --runs corpus/live/r73-reviewer/pg-runs-envsweep
# 32×yes hogs:
python3 corpus/fixtures/pygame_battery.py --runs corpus/live/r73-reviewer/pg-runs-loaded
python3 corpus/fixtures/pygame_battery.py --python "$PWD/corpus/live/r73-reviewer/pyu_wrapper.sh" --runs corpus/live/r73-reviewer/pg-runs-uwrap
env PATH=/usr/bin:/bin python3 corpus/fixtures/pygame_battery.py --runs corpus/live/r73-reviewer/pg-runs-nodeabsent
env PATH="$PWD/corpus/live/r73-reviewer/bin" /usr/bin/python3 corpus/fixtures/pygame_probe.py
python3 corpus/live/r73-reviewer/stuck-scratch/pygame_battery.py --runs corpus/live/r73-reviewer/pg-runs-stuckdetach
python3 corpus/live/r73-reviewer/stuck-scratch/pygame_battery.py --runs corpus/live/r73-reviewer/pg-runs-infmissing
python3 corpus/live/r73-reviewer/compare_prior.py <pre> <committed>
python3 corpus/live/r73-reviewer/infix_replica.py 3
python3 corpus/live/r73-reviewer/fd2_detach_replica.py
python3 corpus/live/r73-reviewer/paced_witness_ref.py 3
python3 corpus/live/r73-reviewer/raw_reader.py -- node corpus/live/r73-reviewer/node_ref.js big
python3 corpus/fixtures/love_battery.py --runs corpus/live/r73-reviewer/love-runs-committed
```

## Bottom line

Evidence resolves: 80/80 ×3 idle + env sweep + loaded, byte-stable new
pins independently reproduced (infix 126011/200020/14000 B withheld; fd2
ERR-first; detach EOF ~911 ms; node small/sync splice, big infix @pipe-
capacity multiples), prior 55 rows untouched with zero stable diffs, both
viability conditionals honest, and both failure modes measured-not-hung.
Recommendation: **ACCEPT the artifact as landed**; fold R1 as a record
correction and R2 as a scope note. No functional defect found in scope.
