# game-dev-2d round 89 — boundary (r89-boundary): the input row is load-bimodal, the bridge pin is race-immune, and the edge lattice hides eight new process-killers

Seat `BOUNDARY` (LEAF) | lane `r89-boundary` | round 89 | host **devin**.
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), `--headless`,
60 tps, GodotPhysics2D. Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD **`0628932`**
(*r88 verifier*).

**No git mutation, no tracked file written, no commit.** Writes are this report (new,
untracked) and `corpus/live/r89-boundary/**` only. The frozen-probeParent depth-2 `ufo-labrat`
was dispatched **exactly once** (read-only receipt-integrity probe, §7); it created nothing.
**Not this seat's processes:** other lanes were observed live on the host (`game-dev-3d`'s
`r92_child/animphys/timing` checks, an `r88-fold` scratch run, a `b90.gd` run) — none from
this seat. All 545 of my receipts are `timeout -s KILL 25`-bounded; my own load loops were
cleaned up (`stray=0` verified after each series), and the 32 `yes` processes present at
report time belong to a concurrent lane's `bash run_cells.sh all` (PPID 1612189), not this
seat (§9).

**`lsp` disclosure (unchanged host state).** No `lsp` device and no GDScript language server
on this host; every claim below is carried by fresh-process execution receipts and
engine-emitted error text, never a source read.

**Legend:** **[O]** observed in fresh processes (byte-identical over the stated rep count
unless marked); **[I]** inference; **[?]** unknown. rc convention: shell `134` ≡ Python `-6`
(SIGABRT), shell `137` ≡ Python `-9` (SIGKILL by `timeout -s KILL 25`).

---

## 0. What I ran

| # | protocol | scope | receipts |
|---|---|---|---|
| 1 | `b89_edge.gd` (`--sub=`), **103 isolated sub-calls × 3 reps** | edge inputs: empty/degenerate/self-intersecting/huge/tiny/NaN-INF/denormal + 2 ladders | `runs/edge_*` |
| 2 | `b89_bridge.gd` (8 arms) | the geo→collision bridge vs the r88 startup step-count race: verbatim, traj, r88 v≠0 sync, delay-forced B, f59/f61, hold, ring variants | `runs/bridge_*`, `runs/ring_*` |
| 3 | r89-scout probes re-run verbatim (sha-verified copies), **20 rows × 6 reps under 16 `yes` hogs** | rep-stability of every claimed-verbatim row | `runs/row_*` |
| 4 | `b89_input_v.gd` (v1/v2/v4) + `b89_input_diag.gd` | bisection of the one failing row | `runs/variant_*`, `runs/diag_*` |
| 5 | focused mode series: quiet×6 + 16-hog×12 (file), quiet×6 (pipe launcher) | mode frequencies for the envelope | `runs/exact_mode_*`, `runs/exact_pipe_quiet.*` |
| 6 | `analyze_edges.py`, `analyze_rows.py` | per-sub/per-row uniq tables | `runs/edge-determinism.txt`, `runs/rows-analysis.txt` |

**Total: 545 receipt triples** (`runs/*.{out,err,rc}`), plus `.wall` sidecars on the
bridge arms. Launch shape everywhere is the battery convention:
`timeout -s KILL 25 godot --headless --path proj --script res://<probe> -- <flags>`;
the scout probes are byte-identical copies (`geo2d_lattice.gd` `9784716b…`,
`input89_edges.gd` `601c223e…`, `project.godot` `8de8b3af…` — all three match the scout's
manifest).

---

## 1. Verdict table (per attacked claim)

| # | claim under test | verdict | one-line evidence |
|---|---|---|---|
| 1 | `bridge` `rest_y=82.3000 / self_hit=1` is stable across the r88 startup-step-count race | **CONFIRMED** | **54 bridge-family runs**: **both** race classes live in-session (8 runs Case A `first=y=-100.000000/v=0`, 28 runs Case B `first=y=-99.727776/v=16.333334` from load + `--delay`; 36 carry the class diagnostic), yet all 54 end at the pinned value (§3) |
| 2 | `ring/ring2/ring4` `drop_center=y=-47.8043 … hits=1` and `ringhits` pins are race-safe | **CONFIRMED** | 14 drop runs + 6-row load reps all `-47.804287 / hits=1`; `ringhits` 6/6 byte-identical under load |
| 3 | the 20 claimed-verbatim rows are rep-stable (6 reps each) **under CPU load** | **19 CONFIRMED / 1 UNSTABLE** | 19 rows 6/6 byte-identical + claimed signature present; **`input89_edges_exact` 0/6** — load-bimodal (§2) |
| 4 | scout §3.7: `offset_polygon` accepts ∅/1pt/2pt/collinear without error | **CONFIRMED for those four; FALSIFIED as a generalization** | `offset_polygon(INF-vertex,2)` SIGABRT ×3; NaN vertex returns a garbage sentinel coordinate silently (§4) |
| 5 | scout §5.1: `offset_polyline(∅)` is a process-killer | **CONFIRMED, and not the only one** | ∅ ×3 rc 134 (377 B Clipper2 assert); **INF vertex also SIGABRT ×3**; 1pt/2pt/collinear/dup/NaN are all clean (§4) |
| 6 | scout §5.2: `make_atlas(∅)` is a loud refusal | **CONFIRMED, with two new failure classes** | width/height ≤0 (incl. NaN/INF/frac) → `ERROR: Condition "p_rects[i].width <= 0"` + empty result, and **one zero rect poisons a whole atlas**; `make_atlas([(1e6,1e6)])` → **FATAL + crash dump + SIGABRT ×3** (§4) |
| 7 | `input89_edges_axisdev` `census=joys=0` | **CONFIRMED on this host / environmental token** | 6/6 under load; `joys` is the host joypad count — any connected pad flips it (§5) |
| 8 | "no volatile token in the claimed pins" | **FALSIFIED** | `just_after_flush=w_jp[…]` is a load race (§2); plus `nmethods=86`/`sig=[…]`/`eia_avail=true` (build) and `tps=60 frames=60` (project) as non-run tokens (§5) |
| 9 | scout "23/23 cells byte-stable, `UNSTABLE=[]`" | **CONFIRMED no-load; incomplete** | 103/103 of my edge subs and 19/20 rows are 3-rep/6-rep byte-stable; the input row's no-load stability does not survive load |

---

## 2. Headline: `input89_edges_exact` is **load-bimodal** — the one row that must not be pinned as-is

The row's claimed signature reproduces byte-for-byte in quiet windows (**6/6** through the
production pipe launcher, 20/20 across all my quiet series) and **fails in loaded windows**.
Only one token moves; everything else (including rc=0 and 0 B stderr) is identical.

**Mode Q — quiet (matches the scout's receipts and the claimed pin), verbatim:**
```
PASS input89_edges exact control=wW_eia_ex=1_actual=1 sW_eia_ex=1_actual=1 eia_wW=ex=1 inex=1 eia_sW_vs_wW=ex=0 inex=1 eia_wW_vs_sW=ex=0 inex=0 eia_sW=ex=1 inex=1 eia_both=plainW[ex=1 inex=1] shiftW[ex=1 inex=1] poll_shiftW_on_plainW_binding=w[ex=false inex=true] sw[ex=true inex=true] poll_after_shiftW_release=w[ex=false inex=false] sw[ex=false inex=false] poll_plainW=w[ex=true inex=true] sw[ex=false inex=false] both[ex=true inex=true] poll_plainW_released=w[ex=false inex=false] both[ex=false inex=false] just_after_flush=w_jp[ex=false inex=true]
```

**Mode L — loaded (alt payload for the envelope), verbatim:**
```
PASS input89_edges exact control=wW_eia_ex=1_actual=1 sW_eia_ex=1_actual=1 eia_wW=ex=1 inex=1 eia_sW_vs_wW=ex=0 inex=1 eia_wW_vs_sW=ex=0 inex=0 eia_sW=ex=1 inex=1 eia_both=plainW[ex=1 inex=1] shiftW[ex=1 inex=1] poll_shiftW_on_plainW_binding=w[ex=false inex=true] sw[ex=true inex=true] poll_after_shiftW_release=w[ex=false inex=false] sw[ex=false inex=false] poll_plainW=w[ex=true inex=true] sw[ex=false inex=false] both[ex=true inex=true] poll_plainW_released=w[ex=false inex=false] both[ex=false inex=false] just_after_flush=w_jp[ex=false inex=false]
```

The single differing token is `just_after_flush=w_jp[ex=false inex=true]` →
`…inex=false]` (`is_action_just_pressed("r89_w", false)` after re-parsing `shift+W`).

**Frequencies [O]** (scout probe, byte-identical file; each observation a fresh process):

| regime | mode Q (`inex=true`) | mode L (`inex=false`) |
|---|---|---|
| quiet (no hogs): pipe launcher ×6 + file ×6 + ×5 + ladder ×3 | **20/20** | 0 |
| 16 `yes` hogs, production pipe launcher (the §3 rows test) | 0/6 | **6/6** |
| 16 hogs, file, first loaded series ×5 | 0/5 | **5/5** |
| 16 hogs, file, interleaved ×12 | 7/12 | **5/12** |
| 16 hogs, file, scout+v1+v4 series ×10 | 7/10 | **3/10** |
| 16 hogs, file, controlled exact-mode series ×12 | 8/12 | **4/12** |
| 16 hogs ladder ×3 | 2/3 | 1/3 |
| 24 hogs ladder ×3 | 0/3 | **3/3** |
| **loaded totals (51 runs)** | **24** | **27** |

**2×2 controls:** quiet+pipe 6/6 Q, quiet+file 6/6 Q, load+pipe 0/6 Q, load+file 4/12 L —
the discriminator is **CPU contention**, not the output channel. The battery's own
`classify_process` requires `signature in output`, so every mode-L process is a **FAIL** for
this row, not a warning.

**Mechanism probes [O], not fully dissected [?].**
- `Engine.get_process_frames()` and `get_physics_frames()` read **0/0 at the pinned read in
  every measured run, in both modes** (`runs/diag_*`, `runs/variant_v2_*`) — this is **not**
  the r88 Case A/B startup step-count race (that race needs the counters to differ).
- The mode is **construction-sensitive**: near-verbatim replicas that add one print
  (`v4`) or extra reads (`v2`) at the read point returned mode Q 6/6+6/6+10/10 while the
  scout file returned mode L 5/12 in the *same session*, and my `v1` replica flipped once in
  10. A one-line code/timing change moves the rate — i.e. a tight race inside the pinned
  read, not a deterministic arm property.
- The `just_after_flush` value is therefore **not pinnable** as written. The r87 precedent
  (mode-envelope rows) is the repair path if the author wants to keep the token; the cheap
  repair is to drop that one token from the signature (the other 17 tokens are stable in
  both modes).

---

## 3. The geo_phys bridge is race-**immune** at its sample point — with a stated margin

**Both startup classes were live in this session [O]:** 8 runs began Case A
(`first=y=-100.000000 v=0.000000`, quiet) and 28 began Case B
(`first=y=-99.727776 v=16.333334`, 16 hogs or `--delay=200/500`) — the exact mechanism r88
found. **Every one of the 54 bridge-family runs** (verbatim, f59, f61, sync, delay, hold,
traj; quiet and loaded) ended:
```
rest=y=82.3000 y6=82.300003 vel=0.0000,0.0000 self_hit=1
```
and the claimed row line reproduces byte-for-byte:
```
PASS geo2d_lattice bridge wall=k=1{n4[60.0000,60.0000;-60.0000,60.0000;-60.0000,30.0000;60.0000,30.0000]} tps=60 frames=60 rest=y=82.3000 vel=0.0000,0.0000 self_hit=1
```

**Why it is immune [O].** The pin samples a *settled fixed point*, not a trajectory point.
Frame-by-frame (`traj`, Case A; `y6` = 6-dp):
```
t=43 y=82.301697   t=46 y=82.300011   t=59 y=82.300003
t=44 y=82.300339   t=47 y=82.300003   t=60 y=82.300003   (constant from t=47 on)
t=45 y=82.300064
```
The 4-dp string first equals `82.3000` at **45 integrations**; the pin samples at 60 awaits
(59 integrations in Case A, 60 in Case B) — a **≥14-step margin**. The race only shifts the
whole sequence by one step, and both modes are inside the flat region.
`hold`: `rest60 == rest120 == 82.300003`, `hits=1` at every frame of the traj (`hits_set=uniq=[1]`).

**Where the immunity ends (for the author's sample choice):** a *shorter* sample would be
race-prone — at t=40 the value is `82.512001` and at t=41 `82.342400` (different at 4 dp),
so a 40-await bridge pin would flip with the startup mode. The scout's 60-frame choice is
load-bearing, not incidental.

**Ring family [O]:** contact at t=10 and constant from there
(`t=9 y=-50.238018 → t=10 y=-47.804287 → … t=90`), so the margin is ~50 steps;
`ring/ring2/ring4` 6/6 and 14 drop runs all `drop_center=y=-47.8043 … hits=1`; `ringhits`
6/6 byte-identical. **Rounding margin:** the underlying float32 fixed points are
`82.300003` (boundary distance ≈ **4.7e-5**) and `-47.804287` (≈ **3.7e-5**), i.e. ~6–10
float32 ULP — safe on this build, but a solver/backend change can move the 4th decimal.

---

## 4. Edge inputs — the scout's specific pins hold, but the generalizations do not

**103 isolated sub-calls × 3 reps, all `out_uniq=1 err_uniq=1`** (one rc-convention flag
only). New results are themselves 3/3 stable; the payloads below are verbatim.

### 4.1 Eight new process-killers (7 SIGABRT + 1 hang) [O]

| sub | call | rc | stderr |
|---|---|---|---|
| `bool_huge_1e15` | `clip(sq(0,0,1e15), sq(5e14,0,1e15))` | **134 / -6 ×3** | 43 B: `timeout: the monitored command dumped core` (bare abort) |
| `bool_huge_1e18` | same at 1e18 | 134 / -6 ×3 | bare abort |
| `bool_huge_3e38` | same at 1.5e38 | 134 / -6 ×3 | bare abort |
| `bool_inf_clip` | `clip(inf-vertex poly, sq)` | 134 / -6 ×3 | bare abort |
| `off_inf_poly` | `offset_polygon(inf-vertex poly, 2, ROUND)` | 134 / -6 ×3 | bare abort |
| `line_inf` | `offset_polyline(inf-vertex line, 2, ROUND, JOINED)` | 134 / -6 ×3 | bare abort |
| `atlas_huge` | `make_atlas([(1e6,1e6)])` | 134 / -6 ×3 | 2331 B: `ERROR: FATAL: Index p_index = -1 is out of bounds (size() = 0).` + GDScript backtrace (`b89_edge.gd:708`) + crash dump |
| `bresenham_nan` | `bresenham_line(Vector2(NAN,NAN), Vector2(5,3))` | **-9 (SIGKILL at 25 s) ×3** | **hang**: stdout stops after the call marker, stderr 0 B |
| `line_empty_reverify` | `offset_polyline(∅, …)` (scout §5.1) | 134 / -6 ×3 | 377 B Clipper2 assert — reproduced |

So the huge-coordinate cliff is between **1e12 (clean, precision-lossy) and 1e15 (abort)**, and
`INF` in any vertex is an abort class of its own; `bresenham_line` joins the hang family
(r88's "invalid op in a synchronous prefix = 25 s idle" lesson, now from a *value*, not a
bad call).

### 4.2 New loud refusals that the scout's `expected_errors` do not cover [O]

| sub | output | stderr |
|---|---|---|
| `atlas_zero` / `atlas_neg` / `atlas_nan` / `atlas_inf` / `atlas_frac` | `points=[] size=(0.0000,0.0000)` rc=0 | `ERROR: Condition "p_rects[i].width <= 0" is true.` (a **different** message from the scout's `p_rects.is_empty()`) |
| `atlas_zero_plus_real` `[(0,0),(4,4)]` | `points=[] size=(0.0000,0.0000)` rc=0 | same — **one zero rect poisons the whole atlas** (the 4×4 rect is silently dropped) |
| `dec_empty` | `k=0{}` rc=0 | `ERROR: Convex decomposing failed!` |

An author whitelisting only `p_rects.is_empty()` will fail any row that feeds a zero/NaN/
fractional rect; and `atlas_zero_plus_real` is a silent-wrong-answer trap (empty atlas, no
crash).

### 4.3 Silent wrong answers (rc=0, no ERROR) [O]

- **NaN/INF propagate as garbage, not refusal:** `merge(nanpoly, sq)` → `k=2` with a vertex at
  `-70368744177664.0000`; `offset_polygon(nanpoly, 2)` → `k=1` with `-92233718038528.0000`;
  `hull(nanpoly)` → `n6` containing `nan`; `decompose(nanpoly)` → `n4` containing `nan`.
- **Predicates disagree on NaN:** `is_point_in_polygon(Vector2(NAN,NAN), sq)=false` but
  `is_point_in_polygon((1,1), nanpoly)=true`; `point_is_inside_triangle(NAN…)=true`;
  `segment_intersects_circle(NaN…)=-1.0000` — the documented "entirely inside" sentinel.
- **Tiny geometry silently vanishes** (`scale ladder`, `clip(sq(0,0,s), sq(0.5s,0,s))`):
  `s=1e-4 → clip=1, merge=1` but **`s=1e-5 → clip=0`** and `s=1e-6 → clip=0, merge=0`.
  The collapse floor is between **1e-4 and 1e-5** for `clip`, **1e-5 and 1e-6** for `merge`.
- **Offset deltas have a precision floor** (`delta ladder` on the r=10 square):
  `d=1e-5 → a=400.0008`, `d=1e-6 → a=400.0000` (silent no-op, start vertex rotated),
  `d=1e-9 → a=400.0000`. At scale 1e9 the float32 ULP is 64, so `offset_polygon(sq1e9, 2, MITER)`
  returns the **unchanged** square (`n4` = input coordinates) — the offset is silently dropped.
- **Vertex-count bombs, not errors:** `offset_polygon(sq, 1e6)` and
  `offset_polyline(line, 1e6)` both return `k=1{n4448[…]}`.
- **Self-intersecting inputs are op-dependent:** `clip(bow,bow)=k=0{}` (self-clip is empty!)
  while `merge(bow,sq)=k=1 a=400.0000` (full square), `inter(bow,sq)=k=2` two triangles,
  pentagram `clip` → `k=5` triangles, `decompose(bow)` → `k=2`.

### 4.4 What the scout's pins got right [O]

`clip(∅,sq)=k=0{}` / `merge(∅,sq)=k=1{rotated sq}`; `clip(sq,∅)=k=1{rotated sq}`;
`clip(col3,sq)=k=0{}` but `clip(sq,col3)=k=1{rotated sq}`; `merge(sq,sq)=k=1`, `inter(sq,sq)=k=1`,
`clip(sq,sq)=k=0{}`; `hull(∅)=k=1{n0[]}` (new: one *empty* polygon inside the array, distinct
from `hull(1pt)=n1`); `offset_polygon(∅/1pt/2pt/collinear)` clean; `line_1pt`→`n7`,
`line_2pt`→`n10`, `line_col` and `line_col_rev` **byte-identical** (direction-insensitivity
reconfirmed), `line_dup4` == `line_2pt`; `off_negzero_delta` == `poly_zero` identity.

---

## 5. Unpinned volatile tokens in the claimed pins

| pin | token | class | evidence |
|---|---|---|---|
| `input89_edges_exact` | `just_after_flush=w_jp[ex=false inex=true]` | **load race (the real one)** | §2; mode L 27/51 loaded observations |
| `input89_edges_axisdev` | `census=joys=0` | host state (joypad count) | stable 6/6 here; a connected pad flips it |
| `census` | `nmethods=86`, `sig=[…]`, `eia_avail=true` | Godot-build constants | stable here; version-dependent, not run-volatile |
| `bridge`, `ring*` | `tps=60 frames=60` | launch-project + probe defaults | fixtures `project.godot` has no `[physics]` block and the row passes no `--frames`; either change flips the token |

No RIDs, uids, addresses, timestamps, or wall-clock tokens exist in any pin — the 19 stable
rows were byte-identical 6/6 under load, which rules out hidden per-run volatility. The
physics values are the only *values* whose stability is nontrivial, and §3 shows why they hold.

---

## 6. Author directives

1. **Do not author `geo2d_lattice` rows that feed the scout's `input89_edges_exact` signature
   as-is.** Either (a) drop the `just_after_flush` token (the other 17 tokens are stable in
   both modes), or (b) declare a two-mode envelope with both payloads from §2 (the r87
   mode-envelope precedent), or (c) re-engineer the probe to remove the race. Option (a) is
   the cheapest and keeps the r87 answer (`is_action_just_pressed` is modifier-widened) —
   which is already carried by the stable `poll_*` tokens in the same line.
2. **Keep the bridge/ring sample points exactly as measured** (60 frames at 60 tps). They are
   race-immune *because* they sit ≥14 steps past the settle boundary; shortening the sample
   re-introduces the r88 race (§3). Do not add a `--frames` override to these rows.
3. **Edge rows: isolate the eight new killers** if any are authored — they belong in
   single-call arms like `lineempty` (census §9.8 rule), never as payloads. `bresenham_nan`
   is a *hang*, so it needs the timeout wrapper and the `-9`/137 rc convention.
4. **Whitelist the exact refusal text per input class.** `p_rects.is_empty()` ≠
   `p_rects[i].width <= 0`; `decompose(∅)` has its own message. A generic whitelist will
   fail loudly, which is the safe direction — but a row that feeds `[(0,0),(4,4)]` gets an
   *empty atlas with no error of its own*, which is the unsafe direction.
5. **If any edge row is authored, pin the ladders, not just one sample**: the boolean collapse
   floor (1e-4→1e-5) and the offset no-op floor (≤1e-6 at unit scale) are the load-bearing
   facts for authors; single samples hide them.
6. **Do not treat "no error" as "correct"** for NaN/INF/tiny inputs: the sentinel coordinates
   (`-70368744177664`, `-92233718038528`) and `sic=-1.0` are silent garbage.

---

## 7. Receipt integrity (the one labrat, advisory)

The depth-2 read-only `ufo-labrat` independently checked that every claimed signature appears
byte-for-byte in the scout's own `runs/` receipts and that rc sidecars match. Result: **all 20
signatures verbatim**; the only literal mismatch is the rc convention
(`geo_lineempty.rep*.rc` = `134` vs claimed `-6` — same SIGABRT, §0 legend). Advisory only.

One receipt-integrity note for the scout's tps-split cell: `proj_tps120/geo2d_lattice.gd`
(`142780…`) is a **stale round-1 file** (it lacks `ringhits`/`polyendpoly` and still has the
`%e` bug). I diffed the two versions: **`_arm_bridge` is byte-identical**, so the
`geo_bridge_tps120` receipts remain valid for the bridge code path; the divergence is
disclosed by their manifest hash. No action needed for the 20 rows (all run from the current
probe).

---

## 8. Remaining unknowns [?]

- **The `just_after_flush` race mechanism is not dissected.** Frame counters are 0/0 in both
  modes, so it is not the r88 step-count race; adding a print or extra reads shifts the rate
  (v2/v4 ≈ 100 % mode Q, scout file ≈ 50 % mode L under the same load). Whether the internal
  cause is engine input-bookkeeping or scheduling was not proven from black-box receipts.
- The load threshold is not a sharp line: 16 hogs gives mixed modes, 24 hogs is mostly mode L;
  the exact trigger (scheduling jitter vs. wall-time budget) was not isolated.
- The huge-coordinate abort between 1e12 (clean) and 1e15 (abort) was not bisected further;
  the INF abort has no engine message at all, so its origin is unprovable from stderr.
- The 1e6-atlas FATAL path was not bisected for the exact size that first trips it.
- `%.4f` rounding margins (§3) are computed, not stress-tested across builds.

---

## 9. Cleanup and evidence index

- 545 receipts, all `timeout -s KILL 25`-bounded; no seat-owned godot left running. One
  cleanup incident: an early shell load loop left 32 stray `yes` processes alive, which
  contaminated the first hog ladder's "0-hog" row; they were killed and every ladder/series
  quoted in §2 was re-run with verified cleanup (`runs/hog-ladder2.txt`, `stray=0` checks in
  the logs). At report time `pgrep -x yes` = 32 again — those belong to a **concurrent lane's
  `bash run_cells.sh all`** (parent PID 1612189), not this seat, and were left untouched.
- **No tracked file written by this seat.** `git status --porcelain` currently shows two
  modified tracked files, both from the **concurrent r88 author lane**, not this seat:
  `corpus/fixtures/run_battery.py` (adds the six-payload mode envelope for
  `input_lattice_phys_peer` — the exact precedent §6.1 cites) and
  `corpus/fixtures/r88_surfaces.gd`. This seat only **read** `corpus/fixtures/project.godot`
  (byte-copy into `proj/`, hash `8de8b3af…`). This report and `corpus/live/r89-boundary/**`
  are untracked.

| artefact | path | sha256 (prefix) |
|---|---|---|
| edge probe, 103 subs | `probes/b89_edge.gd` | `723f2e26…` |
| bridge race probe | `probes/b89_bridge.gd` | `10c849c1…` |
| input bisection probe | `probes/b89_input_v.gd` | `857eeb93…` |
| input diag probe | `probes/b89_input_diag.gd` | `2b18f76f…` |
| driver / analyzers | `run_all.py`, `analyze_edges.py`, `analyze_rows.py` | `a07c7691…`, `d7100c85…`, `1c6c6360…` |
| scout probes (verbatim copies) | `proj/geo2d_lattice.gd`, `proj/input89_edges.gd`, `proj/project.godot` | `9784716b…`, `601c223e…`, `8de8b3af…` |
| every receipt + sidecar | `runs/` | `manifest.sha256` (2153 lines) |
| per-sub determinism / per-row load tables | `runs/edge-determinism.txt`, `runs/rows-analysis.txt` | in manifest |

Reproduce: `python3 run_all.py edges --reps 3 && python3 run_all.py bridge && python3 run_all.py rows --reps 6`,
then `python3 analyze_edges.py && python3 analyze_rows.py`.
