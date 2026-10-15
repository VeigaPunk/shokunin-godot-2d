# Round 71 simplifier report — weight audit + withholding-edge bound-check (pre-land census + landed diff)

Seat: simplifier (LEAF, **audit-only** — write scope is this report +
`corpus/live/r71-simplifier/`; tracked-file edits are author-owned, none made).
Lane: g2d | Round: 71 | Host: devin (Python 3.14.7, pygame 2.6.1/SDL 2.32.72,
`/usr/bin/python3`). Pre-land snapshot: `HEAD=d9ae2071bd23283ad041642d3321b277bd105b0f`
(`preland-sha256.txt`).

## Verdict

- **Deletions made: none** (no tracked edit scope; every candidate below is
  demonstrated in a scratch copy and reported, not applied).
- **Landed r71 diff audited** (§9): `corpus/fixtures/pygame_probe.py` +
  `pygame_battery.py`, both landed mid-audit and revised once while this seat was
  running. **Revision 1 FAILed 35/36** on a clean run (`whf_early_bytes`); the cause
  was diagnosed to the byte-accounting rule, demonstrated in scratch, and the
  author's **revision 2 PASSes 36/36** — but revision 2 also **widened a pin from
  `(60000,135000)` to `(65536,200000)` without need**, which strictly reduces that
  row's discriminating power (measured: the value under the fixed rule is 126007,
  inside the *old* pin). That is this round's one real weight finding.
- **Deletion candidates found: 2** in the tracked 2d corpus (one of them now in the
  landed pygame battery), each demonstrated silent in scratch (§4.1, §4.2, §9.6).
- **Bound-check (the measurement this round's arm (b) rests on):** the piped-stdout
  withholding edge on this build is **131072 B = `io.DEFAULT_BUFFER_SIZE`**, not the
  `~8KB` the frontier report states. The mechanism claim *"bounded by buffer size"*
  is **CONFIRMED** — moving the declared buffer size moves the edge exactly (§2).
  The landed fixture derives the bound from the interpreter (`BUFSIZE = io.DEFAULT_BUFFER_SIZE`),
  so it carries no stale constant.
- **Preserved contract:** tracked tree byte-identical to the pre-land snapshot
  (`sha256 -c` 4/4 OK); LOVE sibling battery re-run **19/19 PASS, exit 0**; the
  landing is additive (two new files, `run_battery.py`/`love_battery.py` untouched).

## (1) Audit state — timeline (the diff landed mid-audit, then changed again)

| time (UTC) | event | evidence |
|---|---|---|
| 14:17 | wave 11 dispatched; `HEAD=d9ae207` | `git log --oneline -1` |
| 14:18–14:23 | no `corpus/fixtures/pygame_*`, no `reports/round-71/`, no `corpus/live/r71-author/` | polls recorded in `watch.log` |
| 14:23:33 | author scratch appears (`withhold_experiment.py`, `withhold_variants.py`) — pre-land census written (§2–§7) | `ls corpus/live/r71-author/` |
| **14:28** | **landing rev 1**: `pygame_probe.py` (9617 B, `1b48060b…`), `pygame_battery.py` (9876 B, `0a579819…`) | `landed-sha256.txt` |
| 14:28:58 | author's own battery run → **FAIL 35/36**, `whf_early_bytes` 191543 | `corpus/live/runs/pygame-20261014T142858275396Z/verdicts.json` |
| 14:29–14:30 | this seat's rev-1 runs → **FAIL 35/36**, 191543 ×2; diagnosis + scratch variants | `runs-pygame/`, `runs-pygame-rep2/`, `del-measure-pygame/` |
| **14:30:15–25** | **author rev 2**: probe rule fixed, `whf_early_bytes` pin widened | `diff -u` in §9.2 |
| 14:30:56 | this seat's rev-2 run → **PASS 36/36**, `whf_early_bytes` **126007** | `runs-pygame-rev2/…/verdicts.json` |

Audited digests — rev 1: probe `1b48060bb886baff5fc4393b45b685580c362f43460d6ed022857d68b3ce2c70`,
battery `0a579819658ee9be9dbd3e6fb81414a036f712a5d03358c7b57a8481a2cec47f`;
rev 2 (current at report time): probe
`4d426a3ba6098186c8ef4d6c6cdf6e4e8ecd17dc7af3828ceb91ccb510bb4738`, battery
`f0630a9b1ca43180084d08a57134193149929b3287c2886f0af8a241898b3166`. Both revisions
are preserved in scratch (`del-measure-pygame/fixtures/*.control.py` = rev 1), so
every claim below is checkable against the bytes it was measured on. The author may
have revised again after the last digest read.

## (2) Bound-check — the withholding edge, measured three ways

The round's arm (b) must "pin measured bound" on the withholding window. The
frontier report pins it as *"unflushed line parent-invisible until ~8KB or exit"*
(`reports/frontier/fa-pygame.md:79`) and leaves the >8 KB case open (`:119`).
Measured independently here:

### (a) The edge is not 8 KB — it is the buffer size, and the default moved

`flush_edge_bisect.py` (`flush-edge-bisect.txt`) — child writes an unflushed head
line at t0, a bulk payload at t0+300 ms, a tail line at t0+600 ms; parent timestamps
the first chunk carrying the bulk bytes:

| write layer | payload | parent sees bulk at | verdict |
|---|---|---|---|
| `sys.stdout.buffer` (default) | ≤ 122880 B | ~605 ms (exit) | WITHHELD |
| `sys.stdout.buffer` (default) | 131072 B | ~305 ms | EARLY |
| `os.fdopen(1,"wb",buffering=8192)` | ≥ 65536 B | ~305 ms | EARLY |
| `os.fdopen(1,"wb",buffering=131072)` | ≤ 122880 B | ~606 ms | WITHHELD |
| `os.fdopen(1,"wb",buffering=131072)` | 131072 B | ~305 ms | EARLY |
| `os.write(1, …)` (raw fd) | 8192…1048576 B | write time | never withholds |

Interpreter fact from the same receipt: **`io.DEFAULT_BUFFER_SIZE = 131072`** on
Python 3.14.7 (the ~8 KB figure is the ≤3.13 default). Exact-edge pin, 3 reps
(`flush-edge-pin.txt`):

| config | bulk | reps (ms) | verdicts |
|---|---|---|---|
| default | 131071 | 605.5 / 605.3 / 605.3 | WITHHELD ×3 |
| default | 131072 | 305.7 / 305.5 / 305.3 | EARLY ×3 |
| `buffering=8192` | 8191 | 605.1 / 605.5 / 606.2 | WITHHELD ×3 |
| `buffering=8192` | 8192 | 305.3 / 305.2 / 305.1 | EARLY ×3 |

Rule (consistent with every cell above): a single write from an empty buffer with
`len(data) >= buffer_size` flushes and writes directly (parent-visible at write
time); `len(data) < buffer_size` accumulates and is withheld until a later
`>= buffer_size` write displaces it, or until exit.

### (b) The window is buffer/exit-bounded, not time-bounded

`withhold_time_bound.py` (`withhold-time-bound.txt`): a child that writes `A1` at
t=0, sleeps **5 s**, then writes `A2` and exits — the parent sees **both** lines at
5005.1 / 5005.4 ms (2/2 reps), i.e. the t=0 line stayed invisible for the whole 5 s.
There is no absorption timer; nothing surfaces mid-life without a buffer-filling
write.

### (c) Layer attribution and the pygame-child control

`flush_edge_layers.py` (`flush-edge-layers.txt`): raw `os.write` never withholds;
`sys.stdout.buffer` (BufferedWriter) and `sys.stdout` (TextIOWrapper → BufferedWriter)
share the same edge — the withholding is stdio's block buffer, not the text layer.
`flush_edge_pygame.py` (`flush-edge-pygame.txt`): under a **pygame-importing** child
(`SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy PYGAME_HIDE_SUPPORT_PROMPT=1`) the edge
is unchanged (8192 → WITHHELD 3/3; 131071 → EARLY 3/3, since `print` adds the
newline to the write) — the pygame import only shifts the timeline by its own
~38 ms cost (343 vs 305 ms). `rc=0` 3/3, stderr only the known avx2 `RuntimeWarning`.

### (d) Falsifiability consequence for arm (b)

- The claim *as written* ("bounded by buffer size") is confirmed: the edge moves to
  8192 when the buffer size is declared 8192 (3/3) and to 131072 when declared 131072
  (3/3). That is the discriminating control, and it is cheap.
- The claim's **declared falsifier** (">8KB write surfaces early") is wrong for this
  build: a 9 KB / 64 KB mid-run unflushed write is still withheld (measured), because
  the actual buffer is 128 KiB. A battery that pins 8 KB as the edge would be
  **unfalsifiable by design** — it passes under both the 8 KB model and the 128 KiB
  model. Pinning the *measured* edge (131071 withheld / 131072 early) plus the
  explicit-`buffering=` control is what discriminates.
- The `~8KB` figure lives only in tracked provenance (`reports/frontier/fa-pygame.md:79,119`)
  — flagged, **not edited** (provenance; also outside this seat's write scope).

## (3) Weight census of the tracked 2d lane (what the landing must not add)

`weight_census.py` + `convention-census.txt`, all refs `corpus/fixtures/`:

- **No shared-helper authority exists in this lane.** `love_battery.py` vs
  `run_battery.py` normalized-token similarity is **0.019** (`census-love_battery.txt`):
  the Godot battery is a monolith (`CASES` at :18, one `main()` at :108); the LOVE
  sibling is a fresh, self-contained runner. The established convention is therefore
  **one self-contained sibling runner per runtime**, not a shared library — and
  r68's precedent already ruled that hoisting helpers is *the larger change*.
  A third sibling must **not** introduce a shared module (that would be a second
  convention); the honest cost of staying in-convention is the helper block:
  `splice_verdict` :74-85 (12 lines) + `run_process` :88-101 (14) + `parse_arms`
  :104-113 (10) + `check` :116-130 (15) = **51 lines**, plus ~74 lines of `main`
  scaffolding.
- **Convention surface a pygame sibling must match** (`convention-census.txt`):
  arm grammar `<RUNTIME>-ARM <arm> | k=v` — the pygame prefix is already fixed by the
  tracked frontier probe (`corpus/live/frontier-pygame/pygame_probe.py:3`,
  `PYGAME-ARM`), so a second prefix would be a stale-name/duplicate-authority defect;
  `verdicts.json` payload keys (`love_battery.py:195-203`); `--runs` default
  `HERE.parent/"live"/"runs"` (:138) with run dirs named `<runtime>-<stamp>` (:142);
  probe dir resolved relative to `HERE` (:33-34); jittered keys pinned as `(lo, hi)`
  bounds, never point values (:37-56).
- **Basename collision to watch:** the fixture `corpus/fixtures/pygame_probe.py` will
  share its name with the tracked provenance probe
  `corpus/live/frontier-pygame/pygame_probe.py`. The frontier copy is the evidence base
  of `fa-pygame.md` (historical — **never delete**); the fixture must be the single
  runtime authority, and drift between the two should be recorded rather than
  silently absorbed.

## (4) Deletion candidates — found, demonstrated, not applied

All three files involved are LOVE-side and round 71 declares them byte-stable, so
these are **reported, not made** (the next deletion would harm the round's declared
byte-stability axis — the stop condition).

### (4.1) `pump_not_needed` row is assertion-carried, not measurement-carried

`love_battery.py:54` pins `("pump", "pump_needed", "false")`; the probe emits
`pump_needed = false` as a **literal** (`love_probe/main.lua:81`). The row can never
fail for a mechanism reason — the fixture states its own conclusion. The measured
half of the pump claim is the *other* row (`pump_updates_counted` →
`updates_without_pump=123`). Found by `arm_coverage.py`
(`coverage-love.txt`: "pinned value is a probe LITERAL → pump_not_needed"), which
also reports the inverse gap: 6 emitted keys carry no assertion
(`osx|ms`, `osx|ret_c`, `popen|open_ms`, `popen|ticks_before`, `splice|offset_ms`,
`splice|gap_ms`).

Demonstrated in scratch (`del-measure/`, `artifact_diff.py`): deleting the row from a
copy → **PASS 18/18**, and the artifact diff is exactly the removed row plus
`totals.cases 19→18` — nothing else is pinned by it (no gate counts rows).

### (4.2) Dead bindings at `love_battery.py:173`

`c_stdout, c_stderr, c_code, c_err = run_process(...)` — `c_stderr` and `c_code` are
never read (`unused_locals.py` → `unused-love_battery.txt`; file has no
`getattr/locals/globals/exec/eval` escape hatches, so the census is exhaustive for
this file). Scratch variant vA renames them to throwaways: **PASS 19/19**, all rows
identical, PASS both. Zero-behavior; the edit is a 2-name rename, not a line
deletion — a nit, recorded for a future touch.

### (4.3) What is *not* a deletion

`splice_verdict`'s `"spliced-no-tail"` / `"ambiguous:"` returns are unreachable from
the battery's expectations but are diagnostic carriers, not dead code;
`_` at :145 is a conventional throwaway; the 4-tuple return of `run_process` is the
shared record shape. No `sd_sig_head`-class dead binding exists this round.

## (5) Preserved contract (independently re-verified)

- Tracked tree byte-identical to pre-land: `sha256sum -c preland-sha256.txt` →
  `love_battery.py: OK`, `run_battery.py: OK`, `love_probe/main.lua: OK`,
  `love_probe/conf.lua: OK`. `git status` shows **no modification of any tracked file
  by this seat** (only `corpus/live/r71-simplifier/**` + this report).
- LOVE sibling battery re-run by this seat:
  `python3 corpus/fixtures/love_battery.py --runs corpus/live/r71-simplifier/runs-love`
  → **19/19 PASS, exit 0** (`runs-love/love-20261014T142144814250Z/verdicts.json`).
  (Pre-existing unrelated dirty rows `corpus/live/frontier-lovephysics/*` belong to
  the frontier-lovephysics seat, not this one.)
- del-measure control run (scratch copy of the same battery) reproduces 19/19 PASS —
  the scratch harness is faithful to the tracked runner.

## (6) Method and `lsp` disclosure

- **No `lsp` device in this seat's surface**, and no Python language server on this
  host: `clangd` is present (C/C++ only); `pyright`, `basedpyright`, `pylsp`, `jedi`,
  `ruff-lsp` are all absent from PATH and not importable
  (`python3 -c "import pylsp|jedi|pyright|basedpyright|ruff"` → absent ×5).
  Every call-graph claim above is therefore a **textual/AST census, not a semantic
  proof** — stated plainly so it is not read as `references` evidence.
- Tooling left in scratch (all runnable, no tracked deps):
  `weight_census.py <target> --sibling <other> [--table CASES]`,
  `arm_coverage.py --probe-out … --cases-file … [--probe-src …]`,
  `unused_locals.py <target>`, `artifact_diff.py A.json B.json`,
  `flush_edge_*.py`, `flush_child*.py`, `withhold_time_bound.py`,
  `fill_timeline.py`, `fill_layer_variant.py`, `del-measure*/` variant harnesses,
  `wait_for_landing.sh`, `watch.sh`.

## (7) Cross-seat observations (out of scope, recorded for the owners)

- **No divergent authority on the edge.** The scout's independent sweep agrees with
  this seat's: 131071 withheld / 131072 early, 3/3 each
  (`corpus/live/r71-scout/withhold_probe.stdout.txt`). Two independent harnesses, one
  bound.
- **A control that produced no data.** The scout's pygame-parity arms (`small_pg`,
  `big_200k_pg`) recorded `rc=2`, `total_bytes=0`, `integrity=0` on 3/3 reps
  (`withhold_probe.stdout.txt`). The same child invocation reproduces clean here
  (`PYGAME_HIDE_SUPPORT_PROMPT=1 python3 corpus/live/r71-scout/withhold_child.py
  '[["w",100,"x"],["s",300]]' --import-pygame` → `rc=0`, expected bytes), and this
  seat's own pygame-child harness ran `rc=0` 3/3. Cause not attributed (their probe's
  internals); the effect is that the pygame-child edge is **not** pinned by that
  receipt — §2(c) pins it instead.
- **Five seats each built their own withhold probe** in scratch
  (`r71-{scout,critic,reviewer,boundary,simplifier}/`). That is scratch-only, so it
  adds no tracked duplicate authority today; if any of it is promoted into
  `corpus/fixtures/`, the corpus acquires N competing probes for one runtime.

## (8) Tradeoffs / stop condition

- The two candidates in §4 are genuine but tiny, and both sit in files round 71
  declares byte-stable: applying them now would trade a 2-line saving for a broken
  byte-stability claim. **Stop here** — the next deletion (the LOVE row) would harm
  the declared round axis, not the weight axis.
- Pinning 8 KB would make arm (b) unfalsifiable-by-design; pinning the measured edge
  (131071/131072, 3/3) plus the explicit-`buffering=` control makes it a real
  discriminator between "bounded by buffer size" and "bounded by something else".
- If the author's landing mirrors `love_battery.py` wholesale, that is **in
  convention** (0.019 similarity to the Godot battery; no shared-helper authority to
  join). Extraction into a shared module is the larger change and would create the
  second convention this seat exists to prevent.
- **Landed-diff tradeoff (§9.4):** the author's rev-2 fix to the accounting rule is
  correct and measured (36/36, `whf_early_bytes` = 126007); the accompanying pin
  widening to `(65536,200000)` buys nothing and passes the rev-1 buggy artifact
  (vC: 36/36 with observed 191543). Tightening the pin back is a one-token edit with
  the deterministic value measured 4/4 runs — but it is the author's call, and the
  artifact is *not* byte-stable for this round anyway (the file is new).
- **Stop condition reached:** the remaining candidates are (a) one assertion-carried
  row and (b) one dead-binding nit in a sibling the round declares byte-stable. The
  next deletion would harm the byte-stability axis, not the weight axis — stop here.

## (9) Landed-diff audit — `corpus/fixtures/pygame_probe.py` + `pygame_battery.py`

### 9.1 Shape and preserved contract

Two **new** files, nothing else touched: `sha256sum -c preland-sha256.txt` →
`love_battery.py: OK`, `run_battery.py: OK`, `love_probe/main.lua: OK`,
`love_probe/conf.lua: OK`; LOVE sibling battery **19/19 PASS, exit 0**. The arm
grammar is `PYGAME-ARM <arm> | k=v` — the grammar the tracked frontier probe already
uses (`corpus/live/frontier-pygame/pygame_probe.py:3`), so no second convention; the
`verdicts.json` payload mirrors `love_battery.py:195-203` modulo runtime names; the
probe resolves relative to `HERE`; run dirs are `pygame-<stamp>` under the ignored
`corpus/live/runs` default. **`BUFSIZE = io.DEFAULT_BUFFER_SIZE`
(`pygame_probe.py:55`)** — the bound is read from the interpreter, so the stale-8 KB
trap of §2(d) is not baked into the fixture. Probe shape: 241 lines, 9 arms
(`viability`, `cadence60`, `cadence0`, `popen`, `popen_buf`, `withhold_{small,big,fill}`,
`pump`); battery: 212 lines, 36 pinned rows.

### 9.2 Revision 1 — a clean run FAILed, and the cause was the accounting rule

Rev 1 (`0a579819…`/`1b48060b…`): `python3 corpus/fixtures/pygame_battery.py` →
**FAIL 35/36, exit 0**, single failing row

```
whf_early_bytes  withhold_fill|early_bytes  pinned (60000,135000)  observed 191543
```

Reproduced **3/3 with the identical value** — twice by this seat
(`runs-pygame/`, `runs-pygame-rep2/`) and once by the author's own run
(`corpus/live/runs/pygame-20261014T142858275396Z/verdicts.json`: verdict FAIL, 35/36,
191543). Not flaky, not load-dependent.

Mechanism, measured (`fill-timeline.txt`, replication of the arm's child, 3/3 reps):

| burst | reads (ms, bytes) | bytes |
|---|---|---|
| mid-run fill flush (~105 ms) | (104.99, 65536), (105.02, 60471) | **126007** |
| exit burst (~205 ms) | (205.10, 65536), (205.14, 8471) | **74007** |

The landed rule was
`early_bytes = sum(n for ms, n in chunks if 0 <= ms < mark2_ms)` — i.e. *every read
before the read that completes MARK-2*. The fill arm's exit burst (74007 B) exceeds
the 65536 B pipe capacity, so it spans two reads; the first lands ~0.04 ms before the
MARK-2 read and is therefore counted as "early": 126007 + 65536 = **191543**. The true
early bytes are **126007**, which is *inside* the pinned `(60000,135000)` — **the pin
was right; the rule was wrong.** `withhold_big` escaped the bug only because its exit
burst is 7 B (one read), and `withhold_small`'s single 9014 B read completes MARK-2, so
it also escaped.

Layer control (`fill-layer-variant.txt`): the same fill pattern through
`sys.stdout.buffer` (no text layer) flushes **131000 B** at ~105 ms and exits with
69014 B — so the 126007 figure is the text-layer's flush boundary, deterministic
across 4 independent runs (3 mine + the author's rev-2 run).

### 9.3 The diagnosis demonstrated in scratch (no tracked edit)

`del-measure-pygame/` — copies of rev 1 (`*.control.py`), run under a scratch battery
so the tracked tree is untouched:

| variant | change | result |
|---|---|---|
| control | verbatim rev-1 copies | 35/36 FAIL — harness faithful |
| vA | delete the `pump_not_needed` row | 34/35, same FAIL; artifact diff = row + `totals.cases` only (silent deletion) |
| **vB** | probe rule → **burst attribution** (group reads within 20 ms; exit burst = last group) | **36/36 PASS with the ORIGINAL pins**, `whf_early_bytes` observed **126007** |
| vC | rev-2 **widened pin** + rev-1 **buggy probe** | **36/36 PASS with `whf_early_bytes` observed 191543** |

### 9.4 The weight finding: rev 2's pin widening is unnecessary and strictly weaker

Rev 2 (`f0630a9b…`/`4d426a3b…`, current at report time) fixed the rule
(`early_bytes = sum(n for ms, n in chunks if 0 <= ms < eof_ms - 25)`,
`pygame_probe.py:141`) → this seat's run is **36/36 PASS** with
`whf_early_bytes` observed **126007** (`runs-pygame-rev2/…/verdicts.json`). But the same
commit also moved the row's pin from `(60000,135000)` to **`(65536,200000)`**
(`pygame_battery.py:94`), and the measurement says the widening was not needed and
costs discrimination:

| value (early_bytes) | meaning | old pin `(60000,135000)` | new pin `(65536,200000)` |
|---|---|---|---|
| 126007 | measured fill-flush boundary (deterministic) | PASS | PASS |
| 191543 | rev-1 *misattribution* (exit-burst read counted early) | FAIL | **PASS** |
| 200007 / 200014 | whole payload flushed mid-run (the failure the arm exists to catch) | FAIL | 200007 **PASS** / 200014 FAIL (7-byte margin) |

Two consequences, both measured: (a) the widened pin **passes the buggy rev-1
artifact** (vC above) — it no longer witnesses the very defect the rule fix addressed;
(b) its upper edge sits **7 bytes** from the value it must reject. The old pin
brackets the deterministic value with ~10% margin and rejects both failure modes with
>50 000 bytes of margin. Author's call, but the minimal expression is to keep the
fixed rule and restore the tight pin (`126007` measured 4/4 independent runs).

Bound-quality remark on rev 2's rule: keying on `eof_ms - 25` is a time-margin
heuristic, and it is *less* robust for the single-read `withhold_small` arm than rev 1's
read-boundary rule — that arm's only read lands at `eof − 2.0 ms`, so any >25 ms delay
of that read (loaded host) would flip `whs_early_none` from 0 to 9014 and FAIL a row
that is currently PASS. Burst-gap grouping (vB) has the same class of margin but keys
off the ~100 ms inter-burst spacing the arm is built on.

### 9.5 Weight census of the landed diff

- **Verbatim helper duplication — expected, but now measurable at three instances.**
  `pygame_battery.py` vs `love_battery.py`: whole-file normalized-token ratio
  **0.659**, with `run_process` **1.000**, `parse_arms` **1.000**, `check` **1.000**
  (byte-identical modulo whitespace) and `main` 0.818 (`census-pygame_battery.txt`).
  `pygame_probe.py` vs the frontier provenance probe: whole-file **0.455**, with
  `emit` **1.000**, `readline_timed` **1.000**, `popen_arm` **1.000** and `main` 0.742
  (`census-pygame_probe.txt`). This is in-convention (§3) — the alternative (a shared
  module) is the second convention this seat exists to prevent — but the 2d lane now
  carries **two** byte-identical copies of the same 51-line helper block (LOVE +
  pygame), and a fourth runtime would make it three: that is the honest cost line, and
  the point at which extraction stops being "the larger change".
- **Zero unused bindings** in both new files (`unused_locals.py`) — cleaner than
  `love_battery.py:173`'s `c_stderr`/`c_code` (§4.2).
- **Case coverage** (`coverage-pygame.txt`, 9 arms / 69 emitted keys / 36 rows):
  **0 rows pinned-but-never-emitted** (every row names a real key); **33 emitted keys
  carry no assertion** — the load-bearing ones are `popen_buf|l1`, `popen_buf|l2`,
  `popen_buf|rest_len` (byte-exactness is asserted for `popen` but *not* for the
  buffered child), `pump|queued_after_nopump`, `viability|flags`, `viability|sdl`.
  The rest are parameter echoes/provenance (`write_bytes`, `bufsize`, `eof_ms`,
  `total_bytes`, `exit_bytes`).
- **Literal-carried rows:** `pump_not_needed` → `pump_needed="false"` (probe emits the
  literal at `pygame_probe.py:235`) and `pump_updates_counted` → `frames_nopump=400`
  (`pygame_probe.py:233`, the fixture's own loop constant). The measured half of the
  pump claim is `posted_survived=1`.
- The frontier probe is now a **frozen provenance copy** of the fixture's arm set
  (same basename, `corpus/live/frontier-pygame/`) — historical evidence for
  `fa-pygame.md`, **never delete**; drift between the two should be recorded, not
  silently absorbed.

### 9.6 Deletion candidate in the landed file (demonstrated, not applied)

`("pump_not_needed", "pump", "pump_needed", "false")` at `pygame_battery.py:96` —
assertion-carried by construction; demonstrated silent in vA (35→34 cases, no verdict
change). One row. This is the **second** instance of the same pattern in the lane —
`love_battery.py:54` carries the identical `pump_not_needed` row against
`love_probe/main.lua:81`'s literal — i.e. a convention propagated across runtimes
rather than a fresh error (the frontier probe, by contrast, emitted a *computed*
`posted_found_at_end`). Not applied: no tracked edit scope, and removing it changes a
byte-stable sibling's artifact.

## Evidence index (all host-resolvable, this repo)

- `corpus/live/r71-simplifier/preland-sha256.txt` (4 × OK),
  `census-love_battery.txt`, `coverage-love.txt`, `unused-love_battery.txt`,
  `convention-census.txt`
- Landed-diff audit: `landed-sha256.txt` (rev 1),
  `census-pygame_battery.txt`, `census-pygame_probe.txt`, `coverage-pygame.txt`,
  `fill-timeline.txt` (3/3 replication of the fill arm),
  `fill-layer-variant.txt` (text vs raw-buffer flush boundary),
  `runs-pygame/…` + `runs-pygame-rep2/…` (rev 1: FAIL 35/36 ×2),
  `runs-pygame-rev2/…` (rev 2: PASS 36/36),
  `del-measure-pygame/{fixtures,runs-control,runs-vA,runs-vB,runs-vC,diff-control-vA.txt,diff-control-vB.txt}`
  (rev-1 copies preserved as `*.control.py`; vC = rev-2 pin against the rev-1 probe)
- `corpus/live/r71-simplifier/flush-edge.txt`, `flush-controls.txt`,
  `flush-edge-layers.txt`, `flush-edge-bisect.txt`, `flush-edge-pin.txt`,
  `flush-edge-pygame.txt`, `withhold-time-bound.txt`
- `corpus/live/r71-simplifier/del-measure/` — `fixtures/` (control + vA + vB),
  `runs-control/`, `runs-vA/`, `runs-vB/`, `diff-control-vB.txt`
- `corpus/live/r71-simplifier/runs-love/love-20261014T142144814250Z/verdicts.json`
  (19/19 PASS)
- `corpus/live/r71-simplifier/{weight_census,arm_coverage,unused_locals,artifact_diff}.py`
- Cross-seat: `corpus/live/r71-scout/withhold_probe.stdout.txt`;
  `reports/frontier/fa-pygame.md:79,119`
