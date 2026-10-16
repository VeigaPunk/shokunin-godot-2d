# r94 author — CPUParticles2D + GPUParticles2D emission lattice landed (19 rows)

Seat `AUTHOR` (g2d lane r94) | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, headless, 60 tps,
RendererDummy), Python 3.14. HEAD at session start `4b75151` (r93 author,
custody free per dispatch).
Work is worktree-only — **nothing committed**. No `lsp` device / no GDScript
server on this host (same as r89–r93); all semantic validation is
fresh-process execution + runtime introspection.

Scope per dispatch: land the Particles2D lattice with **only
boundary-surviving claims** — insertion-only `run_battery.py`, fixture into
`corpus/fixtures/`, battery green twice, report here.

**Dispatch-card disclosure.** The task card is titled "author the
RemoteTransform2D lattice" and lists falsifications for `push_position` /
`update_immediately` / `teleport` — a RemoteTransform2D vocabulary that has
**no referent in this lane**: `grep -r "push_position\|RemoteTransform"`
over the whole repo hits only the card itself and an r62 RemoteTransform3D
scratch. The card's operative clauses (read `reports/round-94/r94-scout.md`
+ `corpus/live/r94-scout/` + `reports/round-94/r94-boundary.md`; insertion
only; fixture into fixtures; green twice; this report path) unambiguously
name the r94 **particles** artifacts — which is what was authored. The
analogous falsified-wording set in this lane is the boundary's own list
(ladder=`round(L·tps)` not `round(L·60)`; contamination=`add_pf≥1`
first-idle-frame not process-global; request=`floor(L/step)+1` not `round`;
`fixed_fps` moves the end ≤1 quantum and `≤5` stalls; the amount `finished`
is armed-then-fired on the next `_process`, not setter-synchronous;
continuous-amount is [U] unstable; GPU `flip_after` is `[1,7]` not 3–7) —
**none of the originally-worded forms is encoded** (see folds below).

## Landed files

| file | sha256 | provenance |
|---|---|---|
| `corpus/fixtures/particles_lattice.gd` | `0701e813e50cdb50e05f0df0194d0baf94c1240f361e941949414dd5c52c00a9` (763 lines) | **folded variant** of the frozen r94-scout probe `corpus/live/r94-scout/probes/particles_lattice.gd` (`e6a2e0f55c6bbeaa…`, 741 lines) |
| `corpus/fixtures/run_battery.py` | tracked, `+91 / −0` | insertion-only: 19 CASES rows + `r94_` floor gate + the r94 comment header |

`project.godot` untouched (no `physics_ticks_per_second` override — the
60-tps default the probe's tick windows assume is the launch value).

## Fixture folds applied (r94-boundary e741cf8; diff vs frozen probe)

The non-comment diff of the fixture against the frozen scout probe is
**exactly four code lines** (verified by `diff` + line-by-line read):

1. **`cpu_pause`: the three `fin_after_*` resume windows widen `[4,7]→[1,7]`**
   (`okvis`, `okvp`, `okpm`; `okts` unchanged `[15,25]`). This is the only
   behavioral fold, made mandatory by boundary §10's verdict that the row
   "must not be shipped as-is": under `--fixed-fps 30` the frozen windows
   reject 3/3 (`vis_parent`/`pm_disabled` land on 2 — the same
   freeze-then-resume-with-remaining-lifetime law through a 2-steps-per-frame
   quantization ratio). `[1,7]` is the boundary's own suggested window and
   covers every measured condition: 4–5 quiet/load/ff60/ff120, 2 at ff30.
   The emitted signature (`ok=true vis_ok=true vis_parent_ok=true
   pm_disabled_ok=true ts0_ok=true`) is byte-identical to the scout's row.
2. **`cpu_request`: `round(0.5/spec)` → `floor(0.5/spec)`** (boundary §6 —
   round is falsified as the closed form at steps 0.20/0.30; floor fits all
   7 measured steps). Emitted `expected=` values are unchanged
   (`floor(0.5/0.10)=5→6`, `floor(0.5/0.05)=10→11`, verified fresh-process).
3. **Comment-only corrections** (no emitted byte changes): contamination
   reframed from "process-global state" to the `add_pf≥1` first-idle-frame
   rule (§8); `fixed_fps` "does not change the end time" → "shifts ≤1
   quantum; `≤5` is a stall hazard" (§5); the amount hazard "emits on the
   set tick" → "armed by the setter, fires on the node's next `_process`
   same-frame" (§7); GPU flip "~5 ticks" → `[1,7]` (§9); `cpu_never`/
   `cpu_contam` arm comments reworded to the `add_pf` vocabulary (the arms'
   behavior and pinned booleans are unchanged — `cpu_never`'s node is
   created inside `_initialize`, i.e. `add_pf=0`, which is exactly the
   clean shape the corrected law predicts).

## run_battery.py changes (insertion-only, `git diff` = 91 `+` / 0 `−`)

1. **CASES 288 → 307 tuples** (results rows 295 → **314** incl. 7 meta):
   19 `r94_particles_*` rows inserted after `r93_anim_blend_interleaved`,
   ahead of the crash/descendant tail — `descendant_pipe_detached_control`'s
   sleep-8 gap stays adjacent to the meta probes. The block was generated
   verbatim from `corpus/live/r94-scout/author-rows.py.txt` `ROWS_PREFIX`
   (the gating boolean-block prefixes before `" | "`), not `ROWS` — the
   full-line form carries the ±1-tick measured tails that mode across
   scheduler conditions (scout §6.2 rule 2; boundary §10).
2. **Signatures pin the law, not the tail**: each row's signature is the
   boolean block (`ok=true <lane>_ok=true …`) — internally `_okb`-windowed
   `fin_delta` checks at the pinned 60-tps launch project. The measured
   `delta=`/`flip_after=`/`fin_after_*=` tails after `" | "` are
   deliberately **not** pinned (±1 modes; `[1,7]` GPU flip range).
3. **`expected_errors` += 0 cases, `required_stderr` += 0 cases** — all 19
   arms are `ERROR:`-clean, 0 B stderr on 143 scout receipts, all 734
   boundary matrix+reprobe receipts, this seat's 19-arm smoke pass, and
   both battery runs (`EXPECTED_ERRORS={}` upstream).
4. **Floor gate extended**: `r94_expected_errors_all_matched` covering
   `case.startswith("r94_")` — same named-by-round /
   covers-round-prefixes shape as r87–r93; inert today (no entries) so a
   future r94 allowlist entry cannot die silently. `True` in both green
   runs.

## New-cell inventory (19 rows)

| case | arm | pin shape | law pinned |
|---|---|---|---|
| `r94_particles_census` | `census` | full line (8.6 KB) | CPU/GPU/PPM enums, per-class defaults (`seed` excluded — random per instantiation), `*_curve:24` Texture2D typing, method signatures |
| `r94_particles_ppm` | `ppm` | full line | param min/max/texture round-trip, flags, sub-emitter + collision enum readback |
| `r94_particles_convert` | `convert` | full line | GPU↔CPU `convert_from_particles` full timing+param transfer both ways, incl. the out-of-enum `draw_order=2` leak |
| `r94_particles_cpu_lifetime` | `cpu_lifetime` | prefix | one-shot `finished` at `round(L·tps)` for L=0.1/0.25/0.5/1.0 — `_okb` windows at pinned 60 tps |
| `r94_particles_cpu_expl` | `cpu_expl` | prefix | streamed emission finishes at `L + L(1−e)(amount−1)/amount` |
| `r94_particles_cpu_speed_pre` | `cpu_speed_pre` | prefix | `speed_scale` divides the clock; `preprocess` skips it; `fixed_fps=30` inside window |
| `r94_particles_cpu_stop` | `cpu_stop` | prefix | `emitting=false` never kills live particles (last batch dies naturally) |
| `r94_particles_cpu_never` | `cpu_never` | prefix | `add_pf=0` never-emitter is clean — no `finished` in 60 ticks |
| `r94_particles_cpu_contam` | `cpu_contam` | prefix | `add_pf≥1` never-emitters fire on first update (2 nodes, positive control) |
| `r94_particles_cpu_oneshot_off` | `cpu_oneshot_off` | prefix | one-shot `emitting=false` at 10 still finishes at its natural end |
| `r94_particles_cpu_oneshot_flag` | `cpu_oneshot_flag` | prefix | `finished` never fires while `one_shot=false` |
| `r94_particles_cpu_pause` | `cpu_pause` | prefix | all 5 pause levers freeze the clock; resume carries the remaining lifetime (**folded windows `[1,7]`**) |
| `r94_particles_cpu_restart` | `cpu_restart` | prefix | `restart()` starts a fresh cycle; flags at finish |
| `r94_particles_cpu_retrigger` | `cpu_retrigger` | prefix | `emitting=true` on a finished one-shot re-runs the cycle |
| `r94_particles_cpu_lt_mid` | `cpu_lt_mid` | prefix | `lifetime` read live — lowered mid-cycle ends at elapsed≥new |
| `r94_particles_cpu_speed_mid` | `cpu_speed_mid` | prefix | `speed_scale` read live mid-cycle |
| `r94_particles_cpu_amount_mid` | `cpu_amount_mid` | prefix | mid-cycle `amount` (one_shot) ⇒ spurious `finished`, `fin_after_set=0` + `em_fin=true` frame-order pair, genuine finish suppressed |
| `r94_particles_cpu_request` | `cpu_request` | prefix | `time_scale=0` clock-free lattice: `finished` on call `floor(L/step)+1` (6, 11) |
| `r94_particles_gpu_headless` | `gpu_headless` | prefix | GPU headless inertness — no `finished`, one-shot clears `emitting` silently, continuous stays emitting, `capture_rect` zero rect |

## Deliberately NOT authored (boundary-verdict exclusions)

- **Continuous-emitter `amount` coupling** — boundary §7.3: [U] unstable,
  set-tick/node-order/`--fixed-fps`-dependent; the scout's own `discover6`
  arm flips across conditions. No row.
- **Full-line `ROWS` tails** — ±1-tick modes (±2 under ff30); only the
  boolean-block prefixes are pinned.
- **`fixed_fps ≤ 5`** — boundary §5: `fixed_fps=1` never finishes (4 s
  observed, every condition); a hang, not a slow cycle. No row.
- **`seed`**, particle positions/colors/velocities (no headless readback
  API), GPU per-particle observables, `flip_after` values.
- **Any RemoteTransform2D claim** — no such surface exists in this lane
  (see dispatch-card disclosure); nothing was invented to satisfy the
  stale card wording.

## Evidence

- **Smoke (pre-battery)**: all 19 arms run fresh-process `--headless` on
  the fixture bytes, `timeout -s KILL 25` — 19/19 `rc=0`, **0 B stderr**,
  every `ROWS_PREFIX` signature substring-matched its fresh PASS line and
  byte-exact-prefix-matched the scout's canonical `rep1` receipts.
- **Battery run 1** `corpus/live/runs/20261016T055703426158Z/verdicts.json`:
  `verdict=PASS`, **314/314 results, 0 FAIL**; all 19 `r94_particles_*`
  rows PASS; `r94_expected_errors_all_matched=True`.
- **Battery run 2** `corpus/live/runs/20261016T060430025246Z/verdicts.json`:
  `verdict=PASS`, **314/314 results, 0 FAIL**; all 19 `r94_particles_*`
  rows PASS. No flake-class events in either run (no timeouts, no
  one-tick misses, no crash rows in this block).
- **Tail-mode sanity across the two runs** (unpinned, as designed):
  `pm_disabled fin_after_enable` 4→5, `stop40 fin_after` 20→19, GPU
  `flip_after=1` in both runs — the last is *inside* the boundary's
  corrected `[1,7]` range but *outside* the scout's reported 3–7,
  live-confirming why it is never pinned.
- **Insertion-only proof**: `git diff corpus/fixtures/run_battery.py` →
  91 insertions, 0 deletions (`git diff` minus the `---`/`+++` header
  lines shows zero removed code lines).
- **Independent probe (frozen `probeParent` dispatch)**: exactly one
  `ufo-labrat` read-only dispatch was made (agent `fd004c5f`) to
  independently falsify H1 (each of the 19 CASES signatures is a
  byte-exact contiguous head of the corresponding scout canonical `rep1`
  receipt) and H2 (the fixture-vs-frozen-probe code diff is exactly the
  four declared lines). The seat had not returned by report time — its
  verdict is advisory only. This seat's own checks on the same files
  confirm both: H1 (19/19 receipt lines `.startswith(signature)`, and
  19/19 signatures substring-match fresh fixture outputs) and H2
  (`diff` of the two probes = the three `_okb` window constants
  `4→1` in `_arm_cpu_pause` plus `round`→`floor` in `_arm_cpu_request`;
  every other differing line is a comment). No second dispatch was made;
  the labrat wrote nothing.

## Files changed

- `corpus/fixtures/particles_lattice.gd` — **new**, 763 lines, sha256
  `0701e813e50cdb50e05f0df0194d0baf94c1240f361e941949414dd5c52c00a9`.
- `corpus/fixtures/run_battery.py` — `+91/−0` (19 CASES tuples, the r94
  comment header, the `r94_expected_errors_all_matched` floor gate).
- `reports/round-94/r94-author.md` — this report (new, untracked).

## Remaining risks / blockers

- **`cpu_lifetime`/`cpu_expl`/`cpu_speed_pre` `_okb` windows are
  60-tps-only** (boundary §3): the rows are safe because the launch
  `project.godot` pins no `physics_ticks_per_second` and the battery never
  changes it — but a future project override would reject them; the probe
  header now documents the `round(L·tps)` alias explicitly.
- **`cpu_pause` fold is a window-widen, not a new mechanism**: `[1,7]`
  covers every condition the boundary measured; if a future launch mode
  lands a resume delta below 1 the row would reject — unlikely (the
  signal cannot precede the resume frame).
- **Host was never idle** (loadavg 69–147 during scout/boundary sessions,
  ~concurrent lanes during both battery runs) — all numbers are
  host-conditioned; the boolean gates are the load-proof form (boundary:
  0 rejections at 16 hogs).
- **Scout evidence-integrity defect** (boundary §2): 135/143 scout
  receipts predate the frozen probe revision. The rows stand on the
  boundary's own 323-check matrix on the frozen revision (3 ff30
  `cpu_pause` rejections now folded) plus this seat's fresh smoke pass —
  not on the scout's mixed-revision set.
- **Blockers: none.** Nothing committed; the two other lanes' untracked
  `reports/round-93/` files and all `corpus/live/` artifacts are
  untouched.
