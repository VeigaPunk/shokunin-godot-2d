# game-dev-2d round 87 — boundary (r87-boundary): the `just_*` pulse law, exact_match granularity, and the flake selector found

Seat `BOUNDARY` (LEAF) | lane `r87-boundary` | round 87 | host **devin**.
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`, `--headless`),
Python 3.14.7. Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD **`fad0b1e`**.

**No git mutation, no tracked file written, no subagent, no commit.** Writes are this
report and `corpus/live/r87-boundary/**` only. Every run is one fresh process under a
per-rep `subprocess timeout=8 s` (the battery's own bound for non-export scripts)
inside a `timeout 500` shell bound; **588 fresh godot processes** across two sessions
(261 + 327 runs); **0 stray processes at exit**.

**`lsp` disclosure (unchanged host state).** No `lsp` device is exposed in this session
and no GDScript/Python language server is installed, so `definition`/`references`/
`hover` were **unavailable for every file touched**. This seat's work is
execution-receipt empiricism and it edited **no repository source**; the probe scripts
under `corpus/live/r87-boundary/proj/` were authored by hand, and every claim below is
carried by fresh-process receipts, never by source reading.

**Legend:** **[O]** observed in fresh processes (byte-identical over the stated rep
count unless marked as bimodal); **[I]** inference; **[?]** unknown.
(The r87 scout's `[M]` ≈ this `[O]`, its `[A]` ≈ ablation.)

---

## 0. What I ran

| # | command (cwd `corpus/live/r87-boundary`) | receipts |
|---|---|---|
| 1 | `python3 run_boundary.py --probe r87b_jr.gd --arms all --reps 3 --tag jr` (16 arms) | `runs/r87b_jr.*.rep*.jr.{out,err}` + `census-jr-r3.json` |
| 2 | `… r87b_jr.gd --arms api_ph_imm,buf_ph_imm,rel_ph_imm,hist_ph_imm --reps 3 --tag jr2` | `census-jr2-r3.json` |
| 3 | `… r87b_jr.gd --arms api_idle,buf_idle,api_ladder,rel_ladder --reps 12 --tag jr12` | `census-jr12-r12.json` |
| 4 | `… r87b_exact.gd --arms all --reps 3 --tag ex` (8 arms) + `… ex_joy_dir2,ex_mod_release --tag ex2` | `census-ex-r3.json`, `census-ex2-r3.json` |
| 5 | `… r87b_eia.gd --arms eia_matrix,eia_act --reps 3 --tag eia` | `census-eia-r3.json` |
| 6 | `… r87b_sel.gd --arms all --reps 3 --tag sel` (7 arms) + `… sel_gap_hist,sel_ratio,sel_forced,sel_anchor --reps 12 --tag sel12` | `census-sel-r3.json`, `census-sel12-r12.json` |
| 7 | `… input_lattice.gd --arms pre_frame,press_phys,release_edge,ui_ns,phys_peer,api_press --reps 12 --tag census12 --pins ref-pins.json`, and `… pre_frame,phys_peer --reps 12 --tag census12b` | `census-census12-r12.json`, `census-census12b-r12.json` |
| 8 | the same batches one session earlier (probe sources pre-final) | `runs-v1/**` (preserved, not overwritten) |

Launch shape is exactly the battery's:
`godot --headless --path proj --script res://<probe> -- --arm=<arm>`.
Census verdicts use the **production `classify_process` extracted verbatim from
`corpus/fixtures/run_battery.py`** — extraction sha256
`615d332ed428db66a03b6837d7a6ed86c4a3150609dc9c2838a11a51b50bbea3`, byte-equal to the
value the r87 scout recorded, re-checked in **all 25 census files** of this seat
(10 in the scratch root, 15 preserved in `runs-v1/`) — a single distinct value.
`runs-v1/` receipts exist because the first session's receipt filenames did not carry
the batch tag; they are kept rather than deleted (see §7).

Every probe arm: `rc=0`, **zero `ERROR:` lines**, and byte-identical payloads over its
reps — **except** the two arms flagged bimodal in §3 (`sel_gap_hist`, `api_idle`).

**A tracked file is dirty and it is not this seat's:** `corpus/fixtures/run_battery.py`
(mtime 14:10, +65/−3) is a concurrent lane's in-flight edit; its `classify_process`
body is unchanged (the sha above is identical in every census of this seat, and
identical to the scout's). Nothing in this seat writes outside
`corpus/live/r87-boundary/**`.

---

## 1. The `just_*` pulse law — the §2.3 "quirk" is solved **[O]**

**Law (headless, `acc=true`, 60 tps, 4.7.2).** A state change arms a *pulse* for
`is_action_just_pressed` and `is_action_just_released` **independently**. The
physics-phase view of a pulse is live during **exactly one physics step: the first
physics step that begins after the change was applied** — no more, no less.

| shape | cell (×3 byte-identical; ×12 where marked) | reading |
|---|---|---|
| API press **inside** physics step S | `api_ladder pre[0/0.00/0/0] same[1/1.00/0/0] n1[1/1.00/1/0] n2[1/1.00/0/0] n3[1/1.00/0/0]` (×12) | 0 at S, **1 at S+1**, 0 at S+2 |
| API press in the **process phase** | `api_ph_imm proc[1/1.00/1/0] ph1[1/1.00/1/0] ph2[1/1.00/0/0]` | immediate in process; **1 at the first step after**, 0 at the next |
| 8 in-process trials of the above | `hist_ph_imm … jp_at_first_step=[1,1,1,1,1,1,1,1]` | deterministic handoff |
| buffered parse in the process phase | `buf_ph_imm proc[0/0.00/0/0] ph1[1/1.00/1/0] ph2[1/1.00/0/0]` | same law; buffering only delays *state application* |
| press **and** release in one step | `rel_ladder press[1/1.00/0/0] rel[0/0.00/0/0] n1[0/0.00/1/1] n2[0/0.00/0/0]` | **both flags 1 at the same step** |
| press+release in one **process** frame | `rel_ph_imm ph1[0/0.00/1/1] ph2[0/0.00/0/0] ph3[0/0.00/0/0]` | the `release_edge` pinned mode, reproduced deterministically |
| process-phase ladder | `id_rel_ladder press[1/1.00/1/0] rel[0/0.00/1/1] r1[0/0.00/0/0] r2[0/0.00/0/0]` | process view is immediate and decays next process frame |
| inline (`acc=false`) parse in a step | `acc_off acc=false same_step[1/1.00/0/0] n1[1/1.00/1/0] n2[1/1.00/0/0]` | same law |
| parse + `flush_buffered_events()` in a step | `buf_flush_phys pre_flush[0/0.00/0/0] post_flush[1/1.00/0/0] n1[1/1.00/1/0] n2[1/1.00/0/0]` | state applies in-step; pulse still at the next step (the §5.3 recipe, stable ×12 via `sel_anchor`) |
| **`action_release` on a never-pressed action** | `rel_unpressed at_rel[0/0.00/0/0] n1[0/0.00/0/1] at_press[1/1.00/0/1] pn1[1/1.00/1/0] pn2[1/1.00/0/0]` | `pressed` stays 0, but the **release pulse is still armed** |

**This explains the scout's §2.3 quirk exactly.** `api_press`'s pinned
`ph1{ap=1/0.70/1/1}` is *not* "a press that seeds `just_released`": it is the **press
pulse** (the API press was applied in the process phase) **plus the release pulse of
the `Input.action_release` this same arm issued one idle frame earlier**, still
pending because no physics step had yet consumed it. Evidence:

- a **fresh** action API-pressed in the process phase reads `jr=0` at the first
  physics step (`api_ph_imm ph1[1/1.00/1/0]`, `hist_ph_imm` 8/8 `jrs=[0,…]`,
  `press_idle` pinned `ph+0{pi=1/1.00/1/0}`);
- every arm that puts a release in the same inter-step window reads `jr=1`:
  `gap0 n1[1/1.00/1/1]`, `gap1 at_repress[1/1.00/0/1]`, `gap2/gap3 at_repress[1/1.00/0/0]`
  (the release pulse survives exactly one step), `rel_ph_imm ph1[0/0.00/1/1]`,
  `hist_rel` 8/8 `jrs=[1,…]`.

**Also falsified: the scout's `phys_peer` cell.** §2.3 states "`phys_peer`
`d+1{…=1/1.00/1/1}` reads `just_released=1`". The scout's own frozen pin says
`d+1{s1=px=1/1.00/1/0,s0=px=1/1.00/1/0}` — **jr=0** — and this seat's reruns agree:
`phys_peer` **48/48 PASS over two sessions, `distinct_payloads=1`**. Its in-step parse
behaves exactly like `buf_phys` (`same_step[0/0.00/0/0] n1[1/1.00/1/0] n2[1/1.00/0/0]`):
press pulse only, no release pulse. `phys_peer` does not exhibit the quirk at all.

---

## 2. `is_action_pressed(a, exact_match)` granularity **[O]**

### 2.1 Event level — `InputMap.event_is_action`, 13 events × 8 actions × {2-arg, false, true}

Full matrix (cells are `d f t`, byte-identical ×3, `runs/r87b_eia.eia_matrix.rep0.eia.out`):

```
EIA ev=k_w       m_w=111 m_ws=000 m_pw=000 m_j=000 m_jdz=000 m_mb=000 m_ea=000 m_none=000
EIA ev=k_w_shift m_w=110 m_ws=111 m_pw=000 m_j=000 m_jdz=000 m_mb=000 m_ea=000 m_none=000
EIA ev=k_w_rel   m_w=111 m_ws=110 m_pw=000 m_j=000 m_jdz=000 m_mb=000 m_ea=000 m_none=000
EIA ev=k_q       m_w=000 m_ws=000 m_pw=000 m_j=000 m_jdz=000 m_mb=000 m_ea=000 m_none=000
EIA ev=k_w_phys  m_w=000 m_ws=000 m_pw=111 m_j=000 m_jdz=000 m_mb=000 m_ea=000 m_none=000
EIA ev=k_w_both  m_w=111 m_ws=000 m_pw=111 m_j=000 m_jdz=000 m_mb=000 m_ea=000 m_none=000
EIA ev=jm_p09    m_w=000 m_ws=000 m_pw=000 m_j=111 m_jdz=111 m_mb=000 m_ea=000 m_none=000
EIA ev=jm_m09    m_w=000 m_ws=000 m_pw=000 m_j=110 m_jdz=110 m_mb=000 m_ea=000 m_none=000
EIA ev=jm_ax1    m_w=000 m_ws=000 m_pw=000 m_j=000 m_jdz=000 m_mb=000 m_ea=000 m_none=000
EIA ev=mb1       m_w=000 m_ws=000 m_pw=000 m_j=000 m_jdz=000 m_mb=111 m_ea=000 m_none=000
EIA ev=mb1_shift m_w=000 m_ws=000 m_pw=000 m_j=000 m_jdz=000 m_mb=110 m_ea=000 m_none=000
EIA ev=ea_x      m_w=000 m_ws=000 m_pw=000 m_j=000 m_jdz=000 m_mb=000 m_ea=000 m_none=000
EIA ev=ea_other  m_w=000 m_ws=000 m_pw=000 m_j=000 m_jdz=000 m_mb=000 m_ea=000 m_none=000
PASS … default2arg=1 false=1 true=1 dz_gate_below=1 dz_gate_above=1
```

Exactness **does flip** the event predicate, in exactly two shapes:

1. **Modifiers** — `k_w_shift m_w=110` (a `shift+W` key event vs a modifier-free `W`
   binding), `mb1_shift m_mb=110` (mouse), `k_w_rel m_ws=110` (release event).
2. **Joypad direction** — `jm_m09 m_j=110`: `exact_match=false` ignores direction,
   `true` requires it (both `m_j` dz=0 and `m_jdz` dz=0.5).

It does **not** flip field selection: `k_w_phys m_w=000`/`m_pw=111`,
`k_w_both m_w=111` **and** `m_pw=111` (keycode and physical bindings are consulted
independently under every exactness value), `jm_ax1` matches nothing.

- **The 2-arg default is `exact_match=false`** — in all 13 rows `d == f` (and `t`
  differs in the three rows above).
- **The action deadzone does not gate the event predicate**: `dz_gate_below=1`
  (a 0.3 event matches a 0.5-deadzone axis binding). Matching ≠ state application.

### 2.2 Polled level — exactness *can* flip a polled answer, but not in the mixed-binding case

| arm | cell (×3 byte-identical) | note |
|---|---|---|
| `ex_key_mod` | `plain_ev[ex=1 pl=1 … s=1.00] shift_ev[ex=0 pl=1 … s=1.00]` | **the flip**: action bound *only* to modifier-free `W`, pressed by a `shift`-carrying `W` event → loose=1, exact=0, strength 1.00 |
| `ex_mouse_mod` | `plain_ev[ex=1 pl=1] shift_ev[ex=0 pl=1]` | same flip for mouse buttons |
| `ex_mod_release` | `pressed_shift_ev[ex=0 pl=1] released_plain_ev[ex=0 pl=0] re_pressed[ex=0 pl=1] released_shift_ev[ex=0 pl=0]` | state matching is modifier-insensitive **in both directions**; only the exact poll distinguishes |
| `ex_mixed` (**mixed exact+inexact bindings held simultaneously**) | `only_plain[ex=1 pl=1] both_held[ex=1 pl=1] shift_released[ex=0 pl=0] all_released[ex=0 pl=0]` | **exactness never flips here** — the exact probe is satisfied by the *other* binding; a modifier-carrying release drops the modifier-free binding too |
| `ex_api` | `pressed[ex=1 pl=1 s=1.00]` | an API press is "exact" too (no bindings at all) |
| `ex_key_mod_bind` | `shift_ev[ex=1 pl=1] plain_ev[ex=0 pl=0]` | a plain event does not press a shift-bound action under either value |
| `ex_phys_key` | `kc_only_ev[0/0] phys_only_ev[1/1]` | per-field, exactness-neutral |
| `ex_eia` | `pressed[ex=1 pl=1] released[0/0]` | `InputEventAction` presses; `jp=0` in-step (pulse law) |
| `ex_joy_dir` | `pos_ev[1/1 s=0.90] neg_ev[0/0] other_axis_ev[1/1 s=0.00]` | |
| `ex_joy_dir2` | `pos[1/1 s=0.90] other_axis[1/1 s=0.90] neg[0/0 s=0.00] exact_ev[1/1 s=1.00] zero[1/1 s=0.00] other_after_rel[1/1 s=0.00]` | **a different-axis event is inert** (state unchanged, strength retained); a **wrong-direction** event **releases**; a value-`0.0` event on the bound axis **presses with strength 0.00** |

So: **exactness flips a polled answer iff the only binding that matched did so
loosely** (modifier-carrying event, modifier-free binding). With mixed bindings the
exact poll is rescued by the other binding, and with directional axis bindings the
state path never records the loose match at all.

### 2.3 `InputEventAction` is matched by **name only** **[O]** (`eia_act`, ×3)

```
m_ea_bind=[InputEventAction:ea_x] m_ea2_bind=[InputEventAction:m_ea2]
ea_x>ea_x=111  ea_x>m_ea=000  m_ea2>m_ea2=111  m_ea2>ea_x=000  m_w_act>m_w=111
st_ea_x(ex/pl/jp)=1/1/0   st_m_ea=0/0/0   st_m_ea2=1/1/0
```

An `InputEventAction` event matches the action whose **name** equals the event's
action — even a key-bound one (`m_w_act>m_w=111`) — while an explicit
`InputMap.action_add_event(InputEventAction)` binding is **inert** for both
`event_is_action` (`ea_x>m_ea=000`) and state (`st_m_ea=0/0/0`) despite the binding
being present. This narrows the scout's "`InputEventAction` participates fully in the
by_event/eia path" to the name-matched case.

---

## 3. The flaky-set selector — **found** **[O]**

**The selector is the number of physics steps that interpose inside the arm's
idle-window gap. Nothing else correlates.**

`sel_gap_hist` reproduces the `release_edge` shape (process-phase press, 2 idle
frames, buffered release, read at the next physics step) 10× in-process and records,
per trial, the interposed step count `inter` and the resulting cell:

- **300 trials in 30 fresh-process invocations** (3 + 12 reps × 2 sessions, 10
  in-process trials each; receipts `runs*/r87b_sel.sel_gap_hist.*`,
  `census-sel*-r*.json`): **300/300** obey
  `inter == 0 ⟺ jp == 1`, tallying exactly
  `{inter=0 → jp=1,jr=1 : 150}` and `{inter≥1 → jp=0,jr=1 : 150}`.
  **`jr=1` in all 300 trials** (the release always lands in the first step after its
  own delivery). The pinned mode `ph+0{re=0/0.00/1/1}` **is** the `inter=0` branch.
- **Both branches reproduced on demand** by physics-anchored mutation, ×12
  byte-identical: `sel_forced gap0[0/0.00/0/0] gap1_at_press[1/1.00/1/0]
  gap1[0/0.00/1/0] gap1_next[0/0.00/0/1]`, and `rel_ph_imm ph1[0/0.00/1/1]` (the pinned
  mode, from the process phase).
- **Not process identity:** both branches occur *within one process* and across reps
  of one fresh-process invocation.
- **Not the read position:** physics-anchored arms are byte-identical ×12 while
  window arms flake.
- The intermediate variable is the loop's idle:physics ratio — `sel_ratio
  phys_per_10_idle=[3,4,4,4,4,4,5,4]` (byte-identical ×12 across two sessions, i.e. the
  *sequence* reproduces while the branch inside a given gap does not).

The same root produces the other two shapes: `press_phys` = count of steps inside a
10-idle-frame window (pin 3 entries vs ALT 2), `ui_ns` = a step boundary crossed
between `_mark()` and the buffered release delivery (`@ph+0` vs `@ph+1`).

### Mode census of this seat (production classifier vs the scout's frozen pins)

| arm | reps | PIN mode | ALT mode | ALT payload difference | scout's session |
|---|---|---|---|---|---|
| `pre_frame` | **48** | 25 | **23 (48%)** | `post_ph=[]` (window held **0** steps) | 9/9 clean |
| `press_phys` | 24 | 13 | 11 | `post_ph` 3 → 2 entries | 9/19 |
| `release_edge` | 24 | 9 | 15 | `ph+0{re=0/0.00/1/1}` → `{…/0/1}` | 7/19 |
| `ui_ns` | 24 | 7 | 17 | release receipts `@ph+0` → `@ph+1` | 11/19 |
| `phys_peer` | 48 | **48** | 0 | — (`distinct_payloads=1`) | 9/9 |
| `api_press` | 24 | **24** | 0 | — (`distinct_payloads=1`) | 9/9 |

Session-to-session drift is large and in both directions (`press_phys` pin 3/12 → 10/12;
`pre_frame` ALT 6/24 → 17/24) — exactly what a load-dependent selector predicts, and
further evidence that the pinned `press_phys`/`release_edge`/`ui_ns` bytes are coin
flips rather than properties.

### A new latent flake found by the law **[O]**

`api_idle` (API press in the process phase, two idle frames, then the first physics
step) is bimodal **across sessions**: session-1 gave **two** payloads in 12 reps
(11× `ph1[1/1.00/0/0]`, 1× `ph1[1/1.00/1/0]`); session-2 gave 12/12 of the first mode.
Its fully physics-anchored siblings (`api_ladder`, `rel_ladder`) are byte-identical
×12 in both sessions. Any arm that samples a pulse across an idle window carries this
risk — the pulse is visible only if no step interposed.

---

## 4. `pre_frame` — falsified as deterministic; re-cut proven **[O]**

The scout's §3 called `pre_frame` "clean ×9 … flagged, not counted against it", and §5
offered it with a "flake risk knowingly" caveat. **It flakes now:** 23 of **48**
fresh-process reps produced the alternate payload

```
… post_ph=[] post_pr=[pr+0{pf0=1/1.00/1/0}]
```

versus the pinned `… post_ph=[ph+0{pf0=1/1.00/1/0}] post_pr=[pr+0{pf0=1/1.00/1/0}]`
(ALT receipts: `runs/input_lattice.pre_frame.rep0.census12.out`,
`rep1.census12b.out`, …; both modes enumerated with rep indices in
`census-census12-r12.json` and `census-census12b-r12.json`). The selector is again the
step count: `sel_pf_hist phys_per_3_idle=[1,0,1,1,2,1,1,1]` in a steady-state window
(the arm's own window sits at process startup, where the zero-step rate was
**17/24** and **6/24** in the two sessions).

**Proven re-cut** (`sel_pf_anchor`, ×3 byte-identical): keep `pre_frame`'s parse
position (before any frame await) but anchor the post window to `physics_frame`
instead of `process_frame`:

```
PASS r87b sel_pf_anchor imm[0/0.00/0/0] post_ph=[ph+0{1/1.00/1/0} ph+1{1/1.00/0/0} ph+2{1/1.00/0/0}] post_pr[1/1.00/0/0]
```

Three structural entries, no interleave dependence.

---

## 5. Author-facing rules **[I, from the [O] above]**

1. A pinned `just_*` byte is safe only if (a) the mutation and the read are in the
   same frame/step, (b) the read is anchored by a `physics_frame` await, or (c) the
   cell *is* the pulse (deterministic at "the first step after the change").
2. Any cell sampling a pulse or a ph-count across an N-idle-frame window is a mode,
   not a pin: mask it (`ph~`), anchor it (`await physics_frame`), or split it.
3. Deterministic press/release recipe (byte-identical over 15 reps: 3 + 12):
   `await physics_frame` → parse → `Input.flush_buffered_events()` → read
   (state applied, no pulse) → `await physics_frame` → read (pulse):
   `sel_anchor flush_step[1/1.00/0/0] n1[1/1.00/1/0] n2[1/1.00/0/0]`.
4. `is_action_pressed(a, false)` is the default and the modifier-insensitive poll; use
   `true` only where a "pressed but not exact" (0) answer for modifier-carrying events
   is acceptable.
5. Do **not** author `pre_frame`, `press_phys`, `release_edge`, `ui_ns` as written
   (48/24/24/24 reps: 48%/46%/62%/71% off-pin). `phys_peer` is clean (48/48) and safe
   as written; `api_press` is clean (24/24) but latently bimodal (§7.3); `pre_frame`
   is recoverable with the §4 re-cut.
6. If a new cell needs `just_released`, remember it is armed by *any* `action_release`,
   including one on a never-pressed action (`rel_unpressed`).

---

## 6. Remaining unknowns **[?]**

- The micro-ordering of `process_frame` vs `physics_frame` inside one
  `Main::iteration()` was not measured; the pulse law is stated purely observably and
  does not depend on it.
- `event_index` semantics for `1..31` (the scout's silent-drop refusal map stands;
  what the field is *for* is untested here).
- `is_action_just_pressed/released_by_event` under the pulse law: the scout's `jpbe`
  arm sampled them, but whether the *by_event* variants are also one-step-late in the
  physics phase was not re-tested.
- Mouse `position` vs viewport cursor (SubViewport / `warp_mouse`) and analog-axis
  device filtering with `joys=0` — untouched here.
- Whether `sel_ratio`'s byte-identical sequence is a property of this host/scheduler or
  of the loop (measured identical ×12 in two sessions — suggestive, not settled).
- Everything here is `--headless`, `acc=true` (except the named `acc_off` cell),
  60 tps, 8 s per-rep bound; windowed/other-bounds runs are untested.

---

## 7. Cross-seat reconciliation (with `r87-boundary-readonly.md`, the prior capability-blocked seat) **[O]**

1. **Its F1 agrees and is now sharper.** It falsified the scout's `phys_peer`
   `jr=1` cell from the pins — this seat confirms it *live* (`phys_peer` 48/48 PASS,
   `distinct_payloads=1`) and replaces its "`released_frame` stamp" model with the §1
   pulse law, which also predicts the cell it could not explain (`api_press`
   `ph1{…/1/1}` = press pulse + pending release pulse).
2. **Its F2 (evidence-custody gap) is falsified.** `corpus/live/r87-scout/runs/`
   **does exist** (20 files, mtimes 12:52) and `sha256sum -c
   corpus/live/r87-scout/MANIFEST.sha256` passes **101/101** — including
   `runs/jmode.rep1.out`, which reads
   `PASS r87_edge jmode ph_in_10pr={ 4: 14, 5: 2 } recv_ph_delta={ 0: 16 } flag[gap/jp]={ "1/jp0": 12, "0/jp1": 4 } gap={ 1: 12, 0: 4 }`.
   The scout's selector correlation is therefore verifiable on disk, and this seat's
   300-trial `sel_gap_hist` (§3) independently reproduces it with a clean 150/150 split.
3. **Its predicted `api_press` alt mode `ph1{ap=1/0.70/1/0}` (stated as "never
   observed, ×19"; the scout's receipts actually hold **9** `api_press` reps, its
   cumulative table says 9/9) is now [O]-supported in mechanism**: it requires one
   physics step to interpose in `api_press`'s 1-idle-frame release→press gap, which
   consumes the release pulse.
   The `gap` ladder shows both sides of exactly that (`gap0 n1[1/1.00/1/1]` vs
   `gap2/gap3 at_repress[1/1.00/0/0]`), so the alt cell is reachable, just rare at a
   1-frame gap: **33 clean fresh-process reps** (9 in the scout's receipts
   — `arms-verify*.json` — plus 24 in this seat's censuses) put it below ~9%.
   Treat `api_press` as clean-but-latent, not as proven deterministic.

---

## 8. Evidence index, cleanup, git

`corpus/live/r87-boundary/` (all untracked; `MANIFEST.sha256` covers every file):

| artefact | note |
|---|---|
| `proj/` | byte-copy of the r87-scout scratch project (itself `corpus/fixtures` + probes); `proj/input_lattice.gd` sha256 `2b68531d…` unchanged from the scout |
| `proj/r87b_jr.gd` | 20 arms — the pulse law (§1) |
| `proj/r87b_exact.gd` | 10 arms — polled exact_match + directional/modifier state (§2.2) |
| `proj/r87b_eia.gd` | 2 arms — the 13×8×3 `event_is_action` matrix + `InputEventAction` cells (§2.1/2.3) |
| `proj/r87b_sel.gd` | 7 arms — the selector, both-branch reproduction, re-cut recipes (§3/§4) |
| `run_boundary.py` | bounded runner; extracts the production `classify_process` (sha `615d332e…`) and classifies against `ref-pins.json` |
| `ref-pins.json` | the r87-scout frozen pins (read-only copy) |
| `runs/` | session-2 receipts: `<probe>.<arm>.rep<i>.<tag>.{out,err}` (tagged, collision-free) |
| `runs-v1/` | session-1 receipts + its census JSONs (kept because the first session's filenames were untagged and would have been overwritten) |
| `census-*.json` | per-batch payloads, rc, merged sha256, verdicts, probe sha, classify sha, pins source |

- **Cleanup:** every godot process was bounded (`timeout 8 s` per rep inside a
  `timeout 500` shell); `pgrep -a godot` at exit shows **0** processes under
  `corpus/live/r87-boundary` — and, at the final check, **0 host-wide** (the earlier
  `game-dev-3d-shokunin` r99/r92 and `game-dev-2d` `r87-baseline` lane processes were
  never this seat's and were never touched). No `/tmp` scratch was created.
- **Git:** `git status --porcelain` shows `?? corpus/live/r87-boundary/` and (after
  this report) `?? reports/round-87/r87-boundary.md`; the only dirty tracked file is
  `corpus/fixtures/run_battery.py`, a **concurrent lane's** in-flight edit (mtime
  14:10; the `classify_process` body it contains is byte-identical to the scout's
  recorded sha). This seat committed nothing, pushed nothing, and edited no tracked
  file. Note `reports/round-87/r87-scout.md` is tracked (committed at `fad0b1e`), so
  this report is a new untracked artefact pending the orchestrator's fold decision —
  a shipping decision left to the operator.
- **Reproduce:** `cd corpus/live/r87-boundary && python3 run_boundary.py --probe
  r87b_jr.gd --arms all --reps 3 --tag jr` (etc.); census verdicts need
  `--pins ref-pins.json`.
