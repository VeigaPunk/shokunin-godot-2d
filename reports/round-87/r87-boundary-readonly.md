# r87 BOUNDARY (read-only analysis pass) — receipt re-analysis of the r87 scout corpus

Seat: ufo-labrat (capability-blocked: read/grep/glob only — no exec, no
writes). Written by the orchestrator from the seat's reply payload.
Source: `corpus/live/r87-scout/` receipts (`pins.json`,
`arms-flaky-r10.json`, `inherited/arms-verify.json`,
`arms-verify-finisher{,2}-r3.json`, `MANIFEST.sha256`).

## F1 — §2.3 quirk claim falsified as stated [O]

Scout asserts `phys_peer` `d+1{…=1/1.00/1/1}` (jr=1 on a physics-resume
buffered press). The pinned, 9/9-byte-verified payload is
`d+1{s1=px=1/1.00/1/0,s0=px=1/1.00/1/0}` — **jr=0**. `jp=1 ∧ jr=1`
co-firing is NOT a property of physics-resume presses; across all pinned
arms it appears only in `api_press` `ph1{ap=1/0.70/1/1}` — whose
structure is press→release→**press**, i.e., a real release precedes the
read. Consistent model [I]: `released_frame` stamped at the idle release
stays equal to the phys counter through ph1 because zero physics steps
interposed in the 1-pr release→press gap. **Corollary: `api_press` is
latently bimodal** — predicted alt mode `ph1{ap=1/0.70/1/0}` (never
observed, ×19 clean) [?] — same hazard class as `release_edge`.

## F2 — evidence-custody gap [O]

`MANIFEST.sha256` lists `runs/{jpbe,jmode,ei_bound,ei_test}.rep*.{out,err}`
with hashes, but `corpus/live/r87-scout/runs/` does not exist on disk.
The jmode `{gap→jp}` perfect-correlation claim and the jpbe/ei_bound
signatures are unverifiable — report text only. Re-run before trusting;
do not cite as measured.

## F3 — selector drift signal [I]

Per-session mode-B fractions (chronological): `release_edge` 0/3→1/3→
2/3→9/10; `press_phys` 2/3→2/3→3/3→4/10; `ui_ns` 1/3→0/3→1/3→6/10.
Mode-B share rises across sessions — weak evidence the selector is
session/time-correlated (host load/clock), not a fixed-rate coin.
`press_phys` in finisher2: 3/3 reps on mode B, `distinct_payloads=1` — a
whole session pinned to the unpinned mode.

## Mode payloads, verbatim [O]

- `release_edge` B: `post_ph=[ph+0{re=0/0.00/0/1} …]` — jp=0 vs mode-A
  jp=1; `pressed=0` both. Fits frame-stamp model: gap=1 →
  `released_frame==G==pressed_frame+1` → jr=1, jp=0.
- `ui_ns` B: release receipts shifted `@ph+0`→`@ph+1`; identical semantics.
- `press_phys` B: `post_ph` has 2 entries not 3.
- `pre_frame`: 9/9 clean across 3 sessions, never in the r10 census —
  latent risk still untested [?].

## Prepared probe spec (handed to the exec-capable r87-boundary-r2 seat)

Scratch `corpus/live/r87-boundary/proj/` = scout `proj/project.godot` +
`input_lattice.gd` + new `r87_boundary.gd`; copy `run_arms.py` +
`pins.json`. Arms (~80 bounded runs):

- **jrq** — decisive quirk probe: persistent physics/process-frame
  callbacks log `{ph, pr, inph, st}` every tick + op-marker rows.
  Scenarios: S1 idle API-press; S2 release-then-press; S3
  press→release→wait3pr→press (split-stamp discriminator); S4 idle
  buffered parse; S5 parse inside physics_frame resume; S6 action_press
  inside physics_frame resume; S7 acc=false; S8 late-run press after 30
  idle frames (proc outruns phys — separates stamp-counter models).
- **xmat** — exact_match granularity: bind xW/xSW/xCW/xSCW; parse ladder
  {W, shift+W, ctrl+W, shift+ctrl+W, alt+W, echo-W}; per-event per-action
  pressed / is_action_pressed(t|f) / just_pressed(t|f) /
  e.is_action_pressed(t|f); release each press with modifier-stripped W.
  Flip case = `pressed=1 ∧ exact=0`.
- **eia** — extended `InputMap.event_is_action`: modifier matrix +
  device-5 joy vs device-0 binding + MouseButton binding + deadzoned
  JoyMotion (0.3/0.7 vs dz 0.5) + echo + keycode-vs-physical cross.
- **sel** — selector forensics: 24 release_edge-shape trials logging
  `Time.get_ticks_usec()` at parses, gap, jp/jr at first phys tick;
  phase-bucket histogram `usec % 16667 → {gap0,gap1}`; 16 trials inside
  physics resume; `physics_ticks_per_second=240` variant ×16.
- **pfc** — in-process census: ph-tick counts inside pr×{2,3,10} windows
  ×48 → predicts pre_frame/press_phys/release_edge flake odds.

Cross-process: `run_arms.py --mode verify --reps 30 --arms
pre_frame,press_phys,release_edge,ui_ns` in the copied harness.

Pre-registered hypothesis: under the frame-stamp model, jrq S8 shows `jp`
firing at the physics tick where `get_physics_frames()` equals the stamp;
S3 shows jp and jr firing at *different* phys ticks when a step
interposes the release→press gap.
