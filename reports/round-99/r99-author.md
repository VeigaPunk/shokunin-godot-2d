# r99 author — headless in-engine audio lattice landed (21 rows: 18 scout cells + 3 boundary law rows); r88's null refuted, its two "law" keys folded out

Seat `AUTHOR` (g2d lane `r99-author`, branch `wt-r99`) | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, `--headless`, Dummy audio
driver, mix rate 44100, 60 physics tps). Worktree
`/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin-wt-r99`, HEAD **`89f85ed8`**
(*r96 author*), working-tree changes only — **nothing committed, nothing staged,
nothing pushed**.

**Scope per dispatch:** read `reports/round-99/r99-scout.md` + `r99-boundary.md`
(plus `reports/round-96/r96-author.md` for conventions); encode **only
boundary-surviving claims**; insertion-only additions to
`corpus/fixtures/run_battery.py`; new fixtures under `corpus/fixtures/`; full
battery twice on final bytes; live receipts under `corpus/live/r99-author/`;
this report. Zero commits.

**`lsp` disclosure.** No `lsp` device in this session and no GDScript language
server on this host; `definition`/`references`/`hover` were **unavailable for
every file**. No cross-file symbol work was required (the deliverable is two new
self-contained fixtures plus an insertion-only battery block), so no
rename/reference risk exists. Semantic carriers here are the production
`classify_process` (AST-extracted from the shipped `run_battery.py`, segment
sha256 `749fa0607e7707e614c1ab157a6f8e756dfc2f460746e6d218e6734ad8fa72c3` — the
same segment r89/r90/r91/r95/r97/r99 pinned), the battery's own verdicts (three
runs on the shipped bytes), this seat's 26 fresh-process smoke/robustness
receipts, and the 699 retained scout/boundary receipts the shipped signatures
were replayed against.

**Labrat disclosure (frozen `probeParent`, exactly one dispatch).** One
read-only `ufo-labrat` was dispatched once, bounded and documentary (H1–H5: 21
r99 tuples and no duplicate case names; the three insertion regions and intact
pre-existing rows; fixture byte-identity; receipt coverage for all 21 shipped
signatures; the single allowlist entry sufficing for the `gen` stderr). It
reported **CONFIRMED on all five** and honestly reported that its substrate has
**no shell and no hashing tool**, so H3 was a full-content line-by-line
comparison rather than a digest proof; this seat independently verified the
digests with `sha256sum` (below). It wrote nothing and spawned nothing.

---

## 0. What was landed and why

| artefact | sha256 | provenance |
|---|---|---|
| `corpus/fixtures/audio_lattice.gd` | `165571c410d506f14915326fd0806e9ff01e5056631620f565c9a7836a920baf` (773 lines) | **byte-copy** of the frozen r99-scout probe (`corpus/live/r99-scout/probes/audio_lattice.gd`; identical bytes in the scout's `proj/` and `r99-boundary/probes/`) |
| `corpus/fixtures/r99b_modes.gd` | `b680e6f297b7534d02a3bdc33337961062f9f0a79393b2a48798308785d38624` (453 lines) | **byte-copy** of the frozen r99-boundary probe (`corpus/live/r99-boundary/probes/r99b_modes.gd`) |
| `corpus/fixtures/run_battery.py` | `71d38d91871a14667da955263e1695cc5392d6e99d3fca399098dc2d988b7829` | tracked, **insertion-only `+150 / −0`** (`git diff --numstat`): r99 comment header + 21 CASES tuples + 1 `expected_errors` entry + the `r99_expected_errors_all_matched` floor gate |

CASES 419 → **440**; result rows 426 → **447** (meta rows unchanged). The block
is inserted immediately ahead of the crash/descendant tail, so
`descendant_pipe_detached_control`'s sleep-8 gap stays adjacent to the meta
probes.

**Why no probe fold.** r96 folded its scout probe; r99 deliberately does **not**.
r99-boundary F1 measured the frozen probe's block waits as wall-time **and
frame-capped**, so every wall window collapses under `--fixed-fps` (which
disables real-time synchronisation: 102k–233k fps) and 14–16/18 cells flip
there. That is a **launch-mode scope, not a defect to patch** (boundary §7.1),
and `run_battery.py` launches with no `--fixed-fps`/`--max-fps` — the paced
149.8 fps regime where the frozen bytes are accepted 54/54 quiet + 54/54 load.
Byte-copying keeps the receipts applicable 1:1 and keeps the shipped fixture
hash-identical to the instrument the receipts came from.

---

## 1. Boundary-driven encoding decisions (the falsifications applied)

| r99-scout claim | boundary verdict | encoding consequence |
|---|---|---|
| `block_jumps_ge6=true` is a clock law (mixblock prefix) | **REFUTED as a law** — it counts exact-4096 deltas inside a 700 ms window at an unstated poll rate; the block update is observed split (`m·128 + (4096−m·128)`) when polls are µs-scale; `blocks_ge6=false` in 3/10 cap-free receipts | the `r99_audio_mixblock` pin now **ends at `all_jumps_q=true`** — the surviving law (every observed advance is a 128-frame multiple, 10/10 cap-free). The dropped `period_is_block` law (mix period == block period) is **re-pinned cap-free by `r99b_mixfree`** |
| `fin_same_frame=true` is a law (finish prefix) | **REFUTED as a law** — the signal and the `playing→false` flip land in *adjacent* frames when frames are ~10 µs apart; `fin_same_frame=false` in 2/12 cap-free receipts; `fin_frame_ge_1` is the same observer statistic (false in the frozen ff120 receipt) | the `r99_audio_finish` pin now **ends at `finished_seen=true`** (the law: transition observed, position resets to 0). The dropped `played_gt_02` — the anti-degenerate assertion that separates this cell from the one-sample `loop_degenerate` termination — is **re-pinned cap-free by `r99b_finfree_played`** |
| the 18 rows' tails are all pinnable | **tails are samples where they are wall-clock** — `pause`'s `a=0.2815419/b/c/d` ladder takes a second value (`a=0.3744218`) at other paced rates (`--max-fps` 30/60/120 receipts) | `r99_audio_pause` pins its **prefix only**; `r99_audio_loop_degenerate` is pinned **through `wraps=0`**, dropping the `frames=N` frame count (17–900 across modes) |
| `census.max_fps=0` is a mode-invariant value | **CONFIRMED with a correction** — `Engine.max_fps` mirrors `--max-fps` (30/60/120); `--fixed-fps` does not touch it | `max_fps=0` is kept as an **explicit launch-shape fact** (this launch carries no `--max-fps`); a future launch shape that adds the flag fails the row loudly, which is the intent |
| `r99b_advfree` shows a wall-clock-exact `after=0.2815419` (10/10) | **mode-scoped** — 10/10 holds for quiet/load/ff30/ff60/ff120, but the `--max-fps` 30/60/120 reps carry **both** `0.2815419` and `0.3744218` (block-phase) | **no row**: the value is a sample; its law prefix is already pinned by `r99_audio_advance` |
| `r99b_peakphase`/`splitcycle`/`modeinfo`/`mixphase` | every printed value is mode- or poll-coupled (ranges, wall samples) | **no rows**; their content is the boundary's §3/§4 report |
| `r99b_firstlaw` fwd0 group | first two fields invariant (immediate readback = 1 sample); third/fourth flip with the window | **no row** — that law is already pinned by the frozen `loop_degenerate` cell; a second instrument for one law is not a second row |
| the r88 causal repro (`r88_audio_repro.gd --fix-loop`) | replicates at paced rates; needs 20 frames ≥ one mix block (≤ ~215 fps) | **no row** — the verbatim arm duplicates the existing `r88_surfaces audio_pos` row and the fix-loop arm's pos/peak samples are mix-block-phase coupled; the attribution stays in the report |

Net effect: **no law is lost** by the folds — each dropped law is re-pinned by a
boundary row measured mode-invariantly — and two laws the frozen probe could not
express (5-cycle immediate readback; cap-free period/played keys) are added.

---

## 2. New-cell inventory (21 rows)

### `audio_lattice.gd` — the 18 scout cells (boundary-hardened pins)

`r99_audio_{census, bus, autoplay, stoppos, peak_calib, mixblock, advance,
finish, loop_degenerate, loop_pts, gen, gen_peak, poly, bus_peak, p2d,
pan_law, gen2d, pause}` — one `--arm=` per cell. Laws pinned: the Dummy-driver
census (driver/mix rate/speaker mode/latency 0.00/1 Master bus/`["Default"]`
device lists/`tps=60`); bus add-route-effect readbacks incl. the silent
invalid-name fallback to Master; autoplay on the first frame; `stop()` zeroing
the position; the peak dB scale (`20·log10(level/32768)`, `−200.00` idle); the
128-frame quantum / 4096-frame block / `0.092880 s` period / first readback
`0.002902494` / all-jumps-quantized; the Dummy mix clock advancing a live
playback with a non-null playback object; the finish transition with
`finished_seen` and `pos_end=0.0000000`; the default-points `LOOP_FORWARD`
self-termination (`maxpos=0.0000227`, `wraps=0`) vs explicit-point looping
(`wraps_ge2`, `maxpos_le_loop`); generator capacity
`next_pow2(buffer_length·mix_rate)−1` = 4095/8191/16383 with the refused
`clear_buffer()`; generator output mixed (live `−0.92 dB`) and 2D-panned
(`−6.94 dB`); polyphony (new voice per `play()`, newest tracked, older voices
advance); live vs idle bus peak; the 2D attenuation/pan lattice; `pause`
freezing with `is_playing()==false`.

### `r99b_modes.gd` — the 3 boundary law rows

| case | arm | signature | law |
|---|---|---|---|
| `r99b_startphase` | `startphase` | `PASS r99b startphase imm=[…5×"0.0029025"] imm_q=[…5×true] imm_uniq=1` | the immediate post-`play()` readback is exactly 128 frames on **5 consecutive play/stop cycles**, mode-invariant (the `one=` field, one frame later, is load-sensitive and deliberately not pinned) |
| `r99b_mixfree` | `mixfree` | `all_jumps_q=true period_is_block=true` | every observed advance is a 128-frame multiple **and** the mix period equals the block period, measured by a cap-free (wall-bounded) instrument — the re-pin of the folded `period_is_block` |
| `r99b_finfree_played` | `finfree` | `played_gt_02=true` | the 0.3 s stream really played past 0.2 s before finishing (cap-free) — the re-pin of the folded `played_gt_02` |

---

## 3. Evidence

- **Smoke (final bytes, fresh process, battery's own launch shape)**: the 21
  shipped rows re-extracted from the edited `run_battery.py` by AST and launched
  against a scratch copy that replicates the battery's staging (fixtures copy +
  app-name munging + `pickup.tscn` staging + `causal_chain` readiness fix), 8 s
  bound, production classifier → **21/21 PASS, rc=0**; every signature matched
  its fresh output; `gen` stderr 462 B (the two expected ERROR lines) and 0 B on
  the other 20. Receipts: `corpus/live/r99-author/smoke/`.
- **Battery run A** `corpus/live/runs/20261016T084826713464Z/verdicts.json`:
  **446/447 PASS**, 1 FAIL = `transition` (`initial current_scene identity/marker
  mismatch`) — the documented pre-existing one-tick scene-handoff flake
  (`controls/scene_transition_probe.gd:48`; 12 PASS/1 FAIL over the r95 census
  of 48 prior runs, untouched by any round's block). **All 21 r99 rows PASS**;
  `r99_expected_errors_all_matched=True`; `gen` entry `matched_lines=2`,
  `dead_in_run=false`.
- **Battery run B** `…/20261016T085534654592Z/verdicts.json`: **445/447 PASS**,
  2 FAIL = `negative_transition` (the documented frame-overshoot flake) and its
  documented knock-on `probe_error_clause_surface` — the single false
  discrimination is `census_bare_classifier_consistent`, broken by
  `negative_transition`'s own two dead allowlist entries (`dead_entry_count=2`,
  both `negative_transition`'s) exactly as the r95 critic recorded. **All 21 r99
  rows PASS**; r99 gate `True`.
- **Battery run C** `corpus/live/runs/20261016T090222167156Z/verdicts.json`:
  **PASS 447/447 — fully green**, zero FAILs, **all 21 r99 rows PASS**,
  `r99_expected_errors_all_matched=True`, `dead_entry_count=0`. Bytes were
  re-hashed immediately before and after the run and are unchanged
  (`fixture_sha256_pre_run_C.txt` = `fixture_sha256_post_run_C.txt`; the battery
  digest is identical to the one the smoke pass and runs A/B ran on), so the
  green run is on the shipped bytes. Machine-readable extract of all three runs:
  `corpus/live/r99-author/battery_runs_ABC.json`.
- **Receipt survival of the shipped signatures** (AST-extracted from the shipped
  battery; production classifier; `corpus/live/r99-author/receipt_survival.json`):

  | receipt set | accepted |
  |---|---|
  | battery launch shape (scout canonical 93 + scout loadtest 54 + boundary quiet 54 + boundary load 54 = 255 for the 18 frozen cells, + 12 for the 3 `r99b_*` rows) | **267/267** |
  | paced / threaded modes (`--max-fps` 30/60/120, `--single-threaded-scene`, threaded physics) | 204/210 — the only 6 rejections are `r99_audio_census` (`max_fps=30/60/120`), the documented launch-shape coupling |
  | unpaced `--fixed-fps` 30/60/120/1 | 113/222 — the boundary's F1/F4 frame-budget scope (not a semantic failure) |

- **Insertion-only proof**: `git diff --numstat corpus/fixtures/run_battery.py`
  → `150 0`; `corpus/live/r99-author/r99_insertion.diff`.
- **Row arithmetic**: CASES 419 → 440 (+21); results 426 → 447 (+21).
- **Byte-identity**: `sha256sum` of both new fixtures equals the frozen
  scout/boundary probe digests (`fixture_sha256.txt`); the labrat's line-by-line
  comparison agrees.
- **Labrat**: 5/5 CONFIRMED (advisory, read-only, wrote nothing).

---

## 4. Files changed

- `corpus/fixtures/audio_lattice.gd` — **new**, byte-copy of the frozen scout
  probe (`165571c4…`).
- `corpus/fixtures/r99b_modes.gd` — **new**, byte-copy of the frozen boundary
  probe (`b680e6f2…`).
- `corpus/fixtures/run_battery.py` — **`+150/−0`** (r99 header + 21 tuples +
  `r99_audio_gen` allowlist entry + `r99_expected_errors_all_matched`).
- `corpus/live/r99-author/**` — this seat's live receipts: battery logs A/B/C,
  `battery_runs_ABC.json` (per-run row/verdict/gate extract),
  `receipt_survival.json`, `smoke/` (21 × `.out/.err/.rc`), `bus_reps/` (5 ×
  `.out/.err/.rc`), `r99_insertion.diff`, `fixture_sha256*.txt`, the
  land/verify/smoke scripts, `manifest.sha256`.
- `reports/round-99/r99-author.md` — this report (new).
- **No commit, no push, no deploy; `project.godot` untouched; no other tracked
  file written.**

## 5. Remaining risks / blockers

- **The two folded keys are gone from the pins by design.** If a future launch
  shape makes the battery unpaced, the block's cap-bound keys still fail there
  (as they do for every round's block) — that is the boundary's documented
  scope, and the block comment says so. The three `r99b_*` rows are the
  mode-invariant instruments for the laws the folds dropped.
- **`r99_audio_census` fails under `--max-fps`** by construction
  (`max_fps=0` is a launch-shape fact). If a future launch adds the flag, the
  fix is one token, and the failure is loud rather than silent.
- **`period_is_block` carries a latent snapshot race** (boundary §3.3: one
  `modeinfo` receipt read `mix_period=0.000000` under ff30; never observed in any
  `mixblock`/`mixfree` receipt at the battery launch). Accepted risk, disclosed
  here; the row fails loudly if it ever lands.
- **`invalid_idx=-1` in `r99_audio_bus`** — the scout's *pre-freeze* `smoke-bus`
  receipt (17:12, 18 min before the canonical rep1) reads `invalid_idx=0`; every
  receipt on the frozen bytes reads `-1` (9 scout canonical+loadtest + 33
  boundary + 5 fresh-process reps run after the battery,
  `corpus/live/r99-author/bus_reps/` + the 4 in-battery launches of runs
  A/B/C and the smoke pass). Treated as an early-probe-revision artifact
  (the pre-freeze arm computed the index before assigning the invalid name),
  not a frozen-bytes flake — 47 fresh-process observations, all `-1`.
- **Pre-existing flake rows are untouched** (`transition`, `negative_transition`,
  `audio_bus_route_invalid_control`, `overlap` and the knock-on meta); nothing in
  this block interacts with them.
- **Blockers: none.** Nothing committed; other lanes' untracked artefacts
  untouched.
