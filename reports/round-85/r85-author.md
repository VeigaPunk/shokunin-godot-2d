# game-dev-2d round 85 — author (g2d): `camera_proc.gd` fixture landed, standalone-verified and rehearsed through the production battery

Seat `AUTHOR` (LEAF) | lane `g2d` | round 85 | host **devin**. This seat is the **finisher** of a
rate-limited prior `r85-author` lane: it audited the partial landing, produced the missing
standalone evidence, reproduced the scout's merge rehearsal on a scratch copy, ran the two
required ablations, and wrote this report. **No git mutation, no commit, no subagent.**
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), Python 3.14.7.
Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD **`f27f952`** (unchanged).

**Deliverable: `corpus/fixtures/camera_proc.gd`, sha256
`34f53f32c0fbb37da86f91ec7b7d9fc0e7d20d9f3e29c4c9680f05e36f123c40`** — the scout probe
`corpus/live/r85-scout/proj/camera_proc.gd` (sha256 `6a94e052…`, MANIFEST-pinned) with the
prologue comment conformed to the r80/r81 fixture convention and **zero code bytes changed**.
`corpus/fixtures/run_battery.py` was **not touched by this seat** (sibling author holds it; the
r81 landing is uncommitted in the tree). The r85 `CASES` rows are in §6 verbatim for the
parent's fold — the tracked harness still carries **no** `camera_proc_*` row.

`lsp` disclosure: no `lsp` device is exposed on this host and no GDScript language server is
installed (same host state r79…r85 recorded). This seat's only symbol-level edit is the fixture
*prologue comment*, so no semantic rename was needed; all evidence below is fresh-process
execution receipts, not text claims.

---

## 1. Audit of the partial landing (honest divergence report)

| check | result |
|---|---|
| probe pinned sha | `6a94e052760e9a10019ff05b43983c9f4958ea859fc48f618ea6de70e20cbe29` — matches `r85-scout/MANIFEST.sha256` **and** `land_r85.py`'s `PROBE_SHA256` |
| landed fixture sha | `34f53f32c0fbb37da86f91ec7b7d9fc0e7d20d9f3e29c4c9680f05e36f123c40` |
| delta probe → fixture | **prologue comment only** (probe lines 2–6 → fixture lines 2–11); probe is 1152 lines, fixture 1157 lines (+5) |
| tail byte-equality | from the lone `#` separator ahead of `# Arms` (probe line 7 → fixture line 12) to EOF: **byte-equal** |
| code byte-equality | from `const PFX := "PASS camera_proc "` to EOF: **byte-equal** (no measured literal re-typed, no token renamed) |
| arm index | the `match arm:` dispatch in `_run` is the sole index: **15 pinned arms + 5 inert `diag_*` arms** (`diag_delta`, `diag_world_step`, `diag_draw`, `diag_cam_internal`, `diag_stretch`) that no `CASES` row references |
| `expected_errors` | **empty** — no r85 row emits `ERROR:`; the block contributes no whitelist entries |
| header convention | fixture header is `# r85 fixture — …`; the same shape as tracked `phys2d_motion.gd` (`# r80 fixture — …`) and the sibling's untracked `phys2d_joints.gd` (`# r81 fixture — …`) |

**Divergence (the one intended token rename):** the probe's first prologue line
`# r85-scout scratch probe — …` becomes `# r85 fixture — …`, and four comment lines are added
(the battery launch shape is split across two lines, the byte-stability clause, and the arm-index
note). This is a **naming/comment deviation from the scout artifact, not a behavioral one** — the
executed bytes from `const PFX` onward are identical. The prior seat's `fixture-vs-probe.diff`
records exactly this diff and nothing else.

**Prior-seat state found:** `land_r85.py`, `standalone_r85.py`, `fixture-vs-probe.diff` present;
`corpus/live/r85-author/standalone/` present but **empty** and `standalone.json` **absent** — the
standalone verification had *not* run. This seat ran `standalone_r85.py` **unmodified** to produce
it (§3.1).

---

## 2. Arm table (15 pinned rows, one fresh Godot process per row)

| # | `CASES` case | fixture arm | measured class (scout §1.1–1.4) | `expected_exit` | `expected_errors` |
|---|---|---|---|---|---|
| 1 | `camera_proc_cam_comp` | `cam_comp` | canvas-transform composition law pinned as transforms | 0 | — |
| 2 | `camera_proc_cam_zoom_center` | `cam_zoom_center` | world point at screen centre under fractional zoom | 0 | — |
| 3 | `camera_proc_cam_phase` | `cam_phase` | camera writes are cached, not live: the visibility ladder | 0 | — |
| 4 | `camera_proc_cam_subpixel` | `cam_subpixel` | 1/60 fixed-tps moves are sub-pixel exact | 0 | — |
| 5 | `camera_proc_cam_space` | `cam_space` | the four transform spaces; stretch transform's seat | 0 | — |
| 6 | `camera_proc_cl_stack` | `cl_stack` | CanvasLayer value is render metadata only | 0 | — |
| 7 | `camera_proc_cl_follow` | `cl_follow` | `follow_viewport_*` is a transform source, basis-only scale | 0 | — |
| 8 | `camera_proc_cl_phase` | `cl_phase` | a CanvasLayer write is live in the writing callback | 0 | — |
| 9 | `camera_proc_cl_draworder` | `cl_draworder` | headless redraw order is creation order, not layer order | 0 | — |
| 10 | `camera_proc_vp_worlds` | `vp_worlds` | world sharing must be explicit; each world steps its own physics | 0 | — |
| 11 | `camera_proc_vp_render_indep` | `vp_render_indep` | physics is byte-independent of canvas/camera state | 0 | — |
| 12 | `camera_proc_vp_subcam` | `vp_subcam` | cameras are per-viewport; canvas transforms do not leak | 0 | — |
| 13 | `camera_proc_par_layer` | `par_layer` | `ParallaxLayer` inert without a `ParallaxBackground` | 0 | — |
| 14 | `camera_proc_par_2d` | `par_2d` | `Parallax2D` needs no parent; `position = ct.origin * (scroll_scale − 1)` | 0 | — |
| 15 | `camera_proc_par_phase` | `par_phase` | parallax lands in the camera's frame, not one later | 0 | — |

All 15 rows are two-clause pins (exit + byte-exact `PASS camera_proc <arm> …` signature) and carry
no whitelist entry.

---

## 3. Verification receipts

### 3.1 Standalone verification of the landed fixture (missing from the partial landing)

`python3 -B corpus/live/r85-author/standalone_r85.py` — runs every arm against the **landed**
`corpus/fixtures/camera_proc.gd` in place, in the battery's own launch shape
(`godot --headless --path corpus/fixtures --script res://camera_proc.gd -- --arm=<name>`, 8 s
bound, merged stdout+stderr), and compares the printed `PASS` line **byte-for-byte** to
`corpus/live/r85-scout/pins.json`.

| receipt | value |
|---|---|
| verdict | **PASS, `bad=[]`** — 15/15 pinned arms `pin_match=True`, 5/5 `diag_*` arms PASS |
| `corpus/live/r85-author/standalone.json` | `stamp=20261015T065904460125Z`, `godot=4.7.2.stable.arch_linux.ed1daf0bf`, `fixture_sha256=34f53f32…`, 20 arms |
| per-arm | `rc=0`, `error_lines=[]` (no `ERROR:` anywhere), wall 0.508 s–1.166 s (worst `vp_render_indep`) |
| raw streams | `corpus/live/r85-author/standalone/<arm>.merged.txt` (20 files) |

### 3.2 Merge rehearsal (reproduced on a scratch copy, exactly as the brief specifies)

`python3 -B corpus/live/r85-author/merge_rehearsal.py` — copies `corpus/fixtures/**` (minus
`run_battery.py`/dotfiles/`__pycache__`) into `corpus/live/r85-author/merge-check/`, pastes the
scout's 15 `CASES` rows verbatim ahead of the crash/descendant tail
(`    ("crash_spontaneous_sigabrt",`), asserts the pasted block is byte-equal to the source
block, then runs the production battery.

| receipt | value |
|---|---|
| verdict | **174/174 PASS, `verdict=PASS`**, `camera_proc` **15/15 PASS** with byte-exact pinned signatures |
| run | `corpus/live/r85-author/merge-runs/20261015T070315089724Z/verdicts.json` |
| base count in the scratch | **159 = 152 `CASES` rows + 7 meta probes** (`probe_save_independent_process`, `probe_spontaneous_crash_classification`, `probe_descendant_pipe_eof`, `probe_descendant_signature_spoof`, `probe_while_live_signature_gate`, `probe_descendant_error_spoof`, `probe_error_clause_surface`); +15 r85 rows = **174** |
| base harness snapshot | tree `corpus/fixtures/run_battery.py` sha `ba3badff4ce24ec04d6cdd18375a85e7a7ab24e70ad231e9dcfb2f19f67bb13f` (the tree's uncommitted **r81** landing is already in it: 152 `CASES` vs the scout's 132 at HEAD `f27f952`) |
| pasted harness | sha `34fc5c2cbfd8d824715c336ed9c9f260ac8de908d1f6a6a433b1dec935bb0944` — **byte-identical to the scout's own `merge-check/run_battery.py`** (same MANIFEST pin), i.e. the scout's paste is reproduced exactly, not merely re-approximated |
| rows source | `corpus/live/r85-scout/author-rows.py.txt`, sha `2221a9e815d8deecfbe3d2e243d2760eec76e5a530d9195f3970373c67c8d97b` (MANIFEST-pinned) |
| wall / rc | 144.1 s, rc=0 |

**Honest divergence (first pass, retained):** this seat's first rehearsal pass ran the battery
with a *stripped* environment (`PATH` only) and scored **172/174** — all 15 `camera_proc_*` rows
PASS, but `export_readiness` and `export_preset_missing` FAILed because Godot then resolved
export templates as `./godot/export_templates/…` instead of
`$HOME/.local/share/godot/export_templates/4.7.2.stable/…` (no export template found →
`executable_bytes=0` → signature mismatch; the second row additionally picked up unrelated
`ERROR:` lines). Cause was **this seat's wrapper, not the fixture**: re-running with the ambient
environment gives 174/174. The bad run is kept as
`merge-runs/20261015T065931148350Z/` with an `ENV-STRIPPED-DIAGNOSTIC.txt` marker; **the receipt
to fold is `merge-runs/20261015T070315089724Z/`**.

### 3.3 Ablations (spot-check on the scratch harness)

`python3 -B corpus/live/r85-author/ablation_check.py --mode …` — each mode copies
`merge-check/**` into `ablation/<mode>/`, mutates the copy only, and runs the production battery.

| ablation | mutation | expected | observed | receipt |
|---|---|---|---|---|
| **sig-drop** | all 15 row signatures → `'PASS camera_proc __absent__'` | FAIL | **159/174 PASS, `verdict=FAIL`; FAIL = exactly the 15 `camera_proc_*` rows, 0 non-camera failures** | `ablation-sig-drop.json`, `ablation/sig-drop-runs/20261015T070543683132Z/verdicts.json` |
| **whitelist-drop** | drop `expected_errors` entries for `camera_proc_*` | PASS (vacuous) | **174/174 PASS, 0 failures** | `ablation-whitelist-drop.json`, `ablation/whitelist-drop-runs/20261015T070810089299Z/verdicts.json` |

Whitelist-drop is **vacuous by construction and proven so, not assumed**: `exec` of the scout's
generated error block yields `{}`; the harness's own `expected_errors` map contains no
`camera_proc_*` key; the dropped harness is **byte-identical** to the pristine scratch harness
(`sha256` equality asserted), so the drop is the identity and the run *is* the pristine run.
The sig-drop ablation is the non-vacuous counterpart: the pins are load-bearing in the real
harness, and no unrelated row is disturbed by the paste.

---

## 4. Risks / caveats for the fold

1. **Naming deviation (benign, measured).** The landed fixture's prologue comment differs from
   the scout probe's (`r85-scout scratch probe` → `r85 fixture`, +4 comment lines). Code bytes
   from `const PFX` onward are byte-equal; §1 proves it. Any tool that diffs the probe against the
   fixture will see exactly this hunk (it is `fixture-vs-probe.diff`).
2. **Concurrency caveat.** `corpus/fixtures/run_battery.py` is held by a sibling author (r81
   landing uncommitted in the tree). This seat copied a **frozen snapshot**
   (`sha ba3badff…`) into its scratch and never wrote the tracked file; the rehearsal's base is
   therefore **152 `CASES` + 7 meta = 159**, not the scout-era 132 `CASES` + 7 = 139. If the
   sibling's landing changes before the fold, the fold's base count moves with it — the r85
   block itself is invariant (15 rows, 0 whitelist entries).
3. **Environment sensitivity of two *unrelated* rows.** `export_readiness` /
   `export_preset_missing` depend on `HOME`/`XDG_*` (export templates at
   `~/.local/share/godot/export_templates/4.7.2.stable/`). A battery invoked with a stripped env
   fails those two rows while every `camera_proc_*` row still passes (§3.2). Not an r85 defect;
   recorded so the parent does not misattribute a 172/174.
4. **`cam_phase` timing class.** The scout had to redesign the idle-phase write cell to be
   physics-frame-armed after a ×3 verify instability. Across this seat's four battery runs
   (standalone + rehearsal + 2 ablations) all 15 pinned signatures were byte-stable; no
   counterexample observed.
5. **Untracked sibling artifacts in the scratch.** `corpus/fixtures/phys2d_joints.gd` (r81,
   untracked) and the r81 rows in the uncommitted `run_battery.py` were copied into the scratch
   as-is — that is the rehearsal's fidelity requirement, not a change; both remain untouched.
6. **Not committed, by brief.** Everything below `corpus/live/r85-author/**`,
   `corpus/fixtures/camera_proc.gd` and this report is untracked/modified-but-uncommitted; the
   shipping decision is the operator's.
7. **`diag_*` arms are inert.** The fixture carries 5 non-pinned diagnostics that no `CASES` row
   references; they run only when invoked by hand (`standalone_r85.py` does so) and cannot affect
   the battery.

---

## 5. What the parent folds

* Insert the §6 block into the tracked `corpus/fixtures/run_battery.py` **immediately after the
  r80 `phys2d_motion_*` block and before `("crash_spontaneous_sigabrt", …)`** — same ordering
  constraint the r79/r80/r81 blocks encode (`probe_descendant_pipe_eof` needs
  `detached_descendant_orphaned_alive` inside the descendant's `sleep 8`, so no `CASES` rows may
  sit between `descendant_pipe_detached_control` and the meta probes).
* Land `corpus/fixtures/camera_proc.gd` (sha `34f53f32…`) as the fixture the rows name.
* No whitelist entries: `expected_errors` stays untouched for all 15 names.
* Do **not** fold the `merge-check/` or `ablation/` scratch trees; they are rehearsal receipts.

---

## 6. The 15 `CASES` rows, verbatim (for the parent's fold)

Source: `corpus/live/r85-scout/author-rows.py.txt` (sha256
`2221a9e815d8deecfbe3d2e243d2760eec76e5a530d9195f3970373c67c8d97b`), extracted byte-for-byte by
`merge_rehearsal.py` and pasted byte-identically into the scratch harness that scored 174/174.
`repr()`-generated literals; several signatures carry quote-heavy payloads.

```python
    # r85: CanvasLayer / Viewport / Camera2D transform lattice — 15 arms,
    # measured x3 byte-stable (r85-scout). Insert ahead of the crash/descendant tail:
    # probe_descendant_pipe_eof requires detached_descendant_orphaned_alive within the
    # descendant's `sleep 8` lifetime, so no CASES rows may sit between
    # descendant_pipe_detached_control and the meta probes.
    # Signature literals are repr()-generated: several arms carry quote-heavy
    # payloads (dict/list renderings) that a hand-quoted literal would corrupt.
    ('camera_proc_cam_comp', 'camera_proc.gd', ['--arm=cam_comp'], 0,
     'PASS camera_proc cam_comp vp2=(64.0, 64.0) nocam=(1.0000,0.0000;0.0000,1.0000;0.0000,0.0000) s0=(1.0000,-0.0000;-0.0000,1.0000;32.0000,32.0000) s1=(1.0000,-0.0000;-0.0000,1.0000;-68.0000,-18.0000) s2=(2.0000,-0.0000;-0.0000,2.0000;-168.0000,-68.0000) s3=(2.0000,-0.0000;-0.0000,2.0000;-188.0000,-108.0000) s4=(2.0000,-0.0000;-0.0000,2.0000;-220.0000,-140.0000) s5=(1.0000,-0.0000;-0.0000,1.0000;32.0000,32.0000) n3=(2.0000,0.0000;-0.0000,2.0000;412.0000,292.0000) comp=(2.0000,0.0000;-0.0000,2.0000;412.0000,292.0000) t0=0.0000,0.0000 c0=0.0000,0.0000 t3=100.0000,50.0000 c3=110.0000,70.0000 t4=100.0000,50.0000 c4=126.0000,86.0000 eq[cam_vp=1 screen=1 comp=1 inv=1] probe=32.0000,32.0000'),
    ('camera_proc_cam_zoom_center', 'camera_proc.gd', ['--arm=cam_zoom_center'], 0,
     'PASS camera_proc cam_zoom_center zoom=1.5 pos=10.5,-3.25 ct=(1.5000,-0.0000;-0.0000,1.5000;16.2500,36.8750) screens=[16.2500,36.8750|32.0000,32.0000|166.2500,186.8750|5.3750,42.5000] center_world=10.5000,-3.2500 anchor_ok=1 dx=1.5000,0.0000 dy=0.0000,1.5000 sub60=-0.0250,0.0000 sub_ok=1 ct2=(1.5000,-0.0000;-0.0000,1.5000;16.2250,36.8750)'),
    ('camera_proc_cam_phase', 'camera_proc.gd', ['--arm=cam_phase'], 0,
     'PASS camera_proc cam_phase pc_idle=1 prio[o=100] A.w1[32.0000,32.0000>32.0000,32.0000] A.i1[22.0000,32.0000] A.w2[22.0000,32.0000>22.0000,32.0000] A.i2[12.0000,32.0000] A.w3[12.0000,32.0000>12.0000,32.0000] A.i3[2.0000,32.0000] A.next[2.0000,32.0000] B.w1[32.0000,32.0000>12.0000,32.0000] B.i1[12.0000,32.0000] B.w2[12.0000,32.0000>-8.0000,32.0000] B.i2[-8.0000,32.0000] B.w3[-8.0000,32.0000>-28.0000,32.0000] B.i3[-28.0000,32.0000] B.next[-28.0000,32.0000] C.w1[32.0000,32.0000>32.0000,32.0000] C.i1[2.0000,32.0000] C.w2[2.0000,32.0000>2.0000,32.0000] C.i2[-28.0000,32.0000] C.w3[-28.0000,32.0000>-28.0000,32.0000] C.i3[-58.0000,32.0000] C.next[-58.0000,32.0000] D.p1[32.0000,32.0000] D.w1[after=32.0000,32.0000] D.i1[-8.0000,32.0000] D.p2[-8.0000,32.0000] D.w2[after=-8.0000,32.0000] D.i2[-48.0000,32.0000] D.p3[-48.0000,32.0000] D.w3[after=-48.0000,32.0000] D.i3[-88.0000,32.0000] E.w1[after=32.0000,32.0000] E.o1[sees=32.0000,32.0000] E.i1[-18.0000,32.0000] E.w2[after=-18.0000,32.0000] E.o2[sees=-18.0000,32.0000] E.i2[-68.0000,32.0000] E.next[-68.0000,32.0000]'),
    ('camera_proc_cam_subpixel', 'camera_proc.gd', ['--arm=cam_subpixel'], 0,
     'PASS camera_proc cam_subpixel n=12 distinct=12 samples=[32.0000,32.0000|31.9833,31.9917|31.9667,31.9833|31.9500,31.9750|31.9333,31.9667|31.9167,31.9583|31.9000,31.9500|31.8833,31.9417|31.8667,31.9333|31.8500,31.9250|31.8333,31.9167|31.8167,31.9083] eq_exact=111111111111 eq_close=111111111111 zoom15=31.7000,31.8500 want15=31.7000,31.8500 z15_ok=1 zoom05=31.9000,31.9500 want05=31.9000,31.9500 z05_ok=1'),
    ('camera_proc_cam_space', 'camera_proc.gd', ['--arm=cam_space'], 0,
     'PASS camera_proc cam_space vpr=[P: (0.0, 0.0), S: (64.0, 64.0)] g0=(1.0000,0.0000;-0.0000,1.0000;300.0000,200.0000) g1=(1.0000,0.0000;-0.0000,1.0000;300.0000,200.0000) g_indep=1 ct0=(1.0000,-0.0000;-0.0000,1.0000;32.0000,32.0000) ct1=(2.0000,-0.0000;-0.0000,2.0000;-168.0000,-68.0000) wc0=(1.0000,0.0000;-0.0000,1.0000;332.0000,232.0000) wc1=(2.0000,0.0000;-0.0000,2.0000;432.0000,332.0000) sc0=(1.0000,0.0000;0.0000,1.0000;332.0000,232.0000) sc1=(2.0000,0.0000;0.0000,2.0000;432.0000,332.0000) vx0=(1.0000,0.0000;0.0000,1.0000;32.0000,32.0000) vx1=(2.0000,0.0000;0.0000,2.0000;-168.0000,-68.0000) wc_eq=1 screen_eq=1 vp_eq=1 cl[has_final=1 final=(1.0000,0.0000;0.0000,1.0000;0.0000,0.0000) lwc=(1.0000,0.0000;0.0000,1.0000;300.0000,200.0000) lsc=(1.0000,0.0000;0.0000,1.0000;300.0000,200.0000) lvx=(1.0000,0.0000;0.0000,1.0000;0.0000,0.0000) l_indep=1] stretch[f2_final=(2.0000,0.0000;0.0000,2.0000;0.0000,0.0000) f2_ct=(2.0000,-0.0000;-0.0000,2.0000;-184.0000,-84.0000) f2_wc=(2.0000,0.0000;-0.0000,2.0000;416.0000,316.0000) f2_sc=(2.0000,0.0000;0.0000,2.0000;416.0000,316.0000) f2_vx=(4.0000,0.0000;0.0000,4.0000;-368.0000,-168.0000) vx_final_ct=1 sc_wc=1 layer_unscaled=1 half=16.0000,16.0000 restored=1]'),
    ('camera_proc_cl_stack', 'camera_proc.gd', ['--arm=cl_stack'], 0,
     'PASS camera_proc cl_stack cam=50.0000,0.0000 root_wc=82.0000,32.0000 layers=[L-1[wc=100.0000,0.0000 vx=0.0000,0.0000 fin=0.0000,0.0000]|L0[wc=100.0000,0.0000 vx=0.0000,0.0000 fin=0.0000,0.0000]|L7[wc=100.0000,0.0000 vx=0.0000,0.0000 fin=0.0000,0.0000]] t1[off=10.0000,20.0000 rot=0.5000 scale=1.0000,1.0000 xf=(0.8776,0.4794;-0.4794,0.8776;10.0000,20.0000)] t2[off=5.0000,5.0000 rot=0.5000 scale=1.0000,1.0000 xf=(0.8776,0.4794;-0.4794,0.8776;5.0000,5.0000)] t3[off=5.0000,5.0000 rot=0.5000 scale=2.0000,2.0000 xf=(1.7552,0.9589;-0.9589,1.7552;5.0000,5.0000)] wc7=(1.7552,0.9589;-0.9589,1.7552;180.5165,100.8851) expect7=(1.7552,0.9589;-0.9589,1.7552;180.5165,100.8851) comp7=1 nested[wc=100.0000,0.0000 isolated=1]'),
    ('camera_proc_cl_follow', 'camera_proc.gd', ['--arm=cl_follow'], 0,
     'PASS camera_proc cl_follow ct=(2.0000,-0.0000;-0.0000,2.0000;-168.0000,-68.0000) rows=[F0[en=0 sc=1.0 wc=100.0000,0.0000 fin=(1.0000,0.0000;0.0000,1.0000;0.0000,0.0000)]|F1[en=1 sc=1.0 wc=32.0000,-68.0000 fin=(2.0000,0.0000;0.0000,2.0000;-168.0000,-68.0000)]|F2[en=1 sc=0.5 wc=-68.0000,-68.0000 fin=(1.0000,0.0000;0.0000,1.0000;-168.0000,-68.0000)]|F3[en=1 sc=2.0 wc=232.0000,-68.0000 fin=(4.0000,0.0000;0.0000,4.0000;-168.0000,-68.0000)]] f2b[wc=52.0000,-28.0000 fin=(2.0000,0.0000;0.0000,2.0000;-148.0000,-28.0000)] moved[ct=(2.0000,-0.0000;-0.0000,2.0000;-568.0000,32.0000) wc=-348.0000,72.0000 fin=(2.0000,0.0000;0.0000,2.0000;-548.0000,72.0000)]'),
    ('camera_proc_cl_phase', 'camera_proc.gd', ['--arm=cl_phase'], 0,
     'PASS camera_proc cl_phase A.w1[cl=100.0000,0.0000 vp=32.0000,32.0000>cl=110.0000,0.0000 vp=32.0000,32.0000]A.i1[cl=110.0000,0.0000 vp=32.0000,32.0000]A.w2[cl=110.0000,0.0000 vp=32.0000,32.0000>cl=120.0000,0.0000 vp=32.0000,32.0000]A.i2[cl=120.0000,0.0000 vp=32.0000,32.0000]A.w3[cl=120.0000,0.0000 vp=32.0000,32.0000>cl=130.0000,0.0000 vp=32.0000,32.0000]A.i3[cl=130.0000,0.0000 vp=32.0000,32.0000]A.next[cl=130.0000,0.0000 vp=32.0000,32.0000]B.w1[cl=100.0000,0.0000>cl=105.0000,0.0000]B.i1[cl=105.0000,0.0000]B.w2[cl=105.0000,0.0000>cl=110.0000,0.0000]B.i2[cl=110.0000,0.0000]B.w3[cl=110.0000,0.0000>cl=115.0000,0.0000]B.i3[cl=115.0000,0.0000]B.next[cl=115.0000,0.0000] inv[wc=100.0000,0.0000 vp=32.0000,32.0000]'),
    ('camera_proc_cl_draworder', 'camera_proc.gd', ['--arm=cl_draworder'], 0,
     'PASS camera_proc cl_draworder seq=L7@pf1|L-1@pf1|L0@pf1|LR@pf1|LR@pf2|L7@pf2|L-1@pf2|L0@pf2|LR@pf3|L7@pf3|L-1@pf3|L0@pf3|LR@pf4|L7@pf4|L-1@pf4|L0@pf4 n=16 counts={ "L7": 4, "L-1": 4, "L0": 4, "LR": 4 } first=[L7,L-1,L0,LR] later=[LR,L7,L-1,L0] hidden_draws=0 creation_order=1 layer_sorted=0'),
    ('camera_proc_vp_worlds', 'camera_proc.gd', ['--arm=vp_worlds'], 0,
     'PASS camera_proc vp_worlds share[d_own=1 d_shares=0 s_shares=1 o_shares=0] pos[br=0.0007,76.3000 bs=40.0007,76.3000 bo=0.0000,207.9190 bd=0.0007,76.3000] contacts[br=0 bs=0 bo=0 bd=0] same_rest=1 shared_floor=1 own_fall=1'),
    ('camera_proc_vp_render_indep', 'camera_proc.gd', ['--arm=vp_render_indep'], 0,
     'PASS camera_proc vp_render_indep names=V0|V1|V2|ROOT pos=[0.0007,76.3003|0.0007,76.3003|0.0007,76.3003|0.0007,76.3003] eq_exact=1 eq_4dp=1 root_ct=30.8158,32.0000'),
    ('camera_proc_vp_subcam', 'camera_proc.gd', ['--arm=vp_subcam'], 0,
     'PASS camera_proc vp_subcam root_vpr=(64.0, 64.0) sub_vpr=(320.0, 180.0) r0=(1.0000,-0.0000;-0.0000,1.0000;32.0000,32.0000) s0=(1.0000,-0.0000;-0.0000,1.0000;120.0000,90.0000) r1=(1.0000,-0.0000;-0.0000,1.0000;-68.0000,32.0000) s1=(1.0000,-0.0000;-0.0000,1.0000;120.0000,90.0000) r2=(1.0000,-0.0000;-0.0000,1.0000;-68.0000,32.0000) s2=(1.0000,-0.0000;-0.0000,1.0000;80.0000,70.0000) cams[sv=1 root=1] iso[sub_only=1 root_only=1]'),
    ('camera_proc_par_layer', 'camera_proc.gd', ['--arm=par_layer'], 0,
     'PASS camera_proc par_layer cam=128.0000,0.0000 ms=0.5000,0.5000 mm=0.0000,0.0000 mo=0.0000,0.0000 rows=[p0[wc=32.0000,32.0000]|ms05[cam0 wc=32.0000,32.0000 lp=0.0000,0.0000]|cam64[wc=-32.0000,32.0000 lp=0.0000,0.0000]|cam128[wc=-96.0000,32.0000 lp=0.0000,0.0000]|mirror100[cam128 wc=-96.0000,32.0000 lp=0.0000,0.0000]|cam150mirror[wc=-118.0000,32.0000 lp=0.0000,0.0000]|moff10[wc=-118.0000,32.0000 lp=0.0000,0.0000]|has_pbg=1|pbg0[follow=0 wc=16.0000,16.0000 lp=16.0000,16.0000]|pbg64[wc=-16.0000,16.0000 lp=-16.0000,16.0000 fin=(1.0000,0.0000;0.0000,1.0000;0.0000,0.0000)]|pbg128[wc=-48.0000,16.0000 lp=-48.0000,16.0000]|pbgmirror[wc=-48.0000,16.0000 lp=-48.0000,16.0000]|pbgmoff[wc=-38.0000,16.0000 lp=-38.0000,16.0000]|pbgms1[wc=-96.0000,32.0000 lp=-96.0000,32.0000]|pbgms0[wc=0.0000,0.0000 lp=0.0000,0.0000]|pbgz2[ct=-224.0000,32.0000 wc=-112.0000,16.0000 lp=-112.0000,16.0000 ign=0]|cl_follow[wc=-96.0000,32.0000 lp=0.0000,0.0000]|cl_nofollow[wc=0.0000,0.0000 lp=0.0000,0.0000]]'),
    ('camera_proc_par_2d', 'camera_proc.gd', ['--arm=par_2d'], 0,
     'PASS camera_proc par_2d cam=150.0000,0.0000 rows=[d0[off=0.0000,0.0000 wc=16.0000,16.0000]|cam64[off=0.0000,0.0000 wc=-16.0000,16.0000]|ignore[off=0.0000,0.0000 wc=-16.0000,16.0000]|rep100x3[off=0.0000,0.0000 wc=-16.0000,16.0000]|cam150rep[off=0.0000,0.0000 wc=-59.0000,16.0000]|follow[off=0.0000,0.0000 wc=-59.0000,16.0000]|screen_off[off=0.0000,0.0000 wc=-59.0000,16.0000]]'),
    ('camera_proc_par_phase', 'camera_proc.gd', ['--arm=par_phase'], 0,
     'PASS camera_proc par_phase PL.w1[cam=32.0000,32.0000 pl=32.0000,32.0000 p2=16.0000,16.0000 pbl=16.0000,16.0000 pbc=16.0000,16.0000>cam=32.0000,32.0000 pl=32.0000,32.0000 p2=16.0000,16.0000 pbl=16.0000,16.0000 pbc=16.0000,16.0000]PL.i1[cam=-32.0000,32.0000 pl=-32.0000,32.0000 p2=-16.0000,16.0000 pbl=-16.0000,16.0000 pbc=-16.0000,16.0000]PL.w2[cam=-32.0000,32.0000 pl=-32.0000,32.0000 p2=-16.0000,16.0000 pbl=-16.0000,16.0000 pbc=-16.0000,16.0000>cam=-32.0000,32.0000 pl=-32.0000,32.0000 p2=-16.0000,16.0000 pbl=-16.0000,16.0000 pbc=-16.0000,16.0000]PL.i2[cam=-96.0000,32.0000 pl=-96.0000,32.0000 p2=-48.0000,16.0000 pbl=-48.0000,16.0000 pbc=-48.0000,16.0000]PL.next[cam=-96.0000,32.0000 pl=-96.0000,32.0000 p2=-48.0000,16.0000 pbl=-48.0000,16.0000 pbc=-48.0000,16.0000]'),
```

Trailing block (the scout's error block, exec-checked here to `{}`):

```python
# --- expected_errors entries (merge into the expected_errors map inside execute()) ---
                # (no row in this block needs a whitelist)
```

---

## 7. Artifacts

| artifact | sha256 (see `corpus/live/r85-author/MANIFEST.sha256`) | note |
|---|---|---|
| `corpus/fixtures/camera_proc.gd` | `34f53f32…` | **deliverable fixture** (untracked) |
| `corpus/live/r85-author/land_r85.py` | `12a837e3…` | prior seat's landing script (asserted probe sha, tail/code equality) |
| `corpus/live/r85-author/fixture-vs-probe.diff` | `ec523aeb…` | the single header hunk |
| `corpus/live/r85-author/standalone_r85.py` | `c2d5f20c…` | prior seat's standalone runner (run unmodified) |
| `corpus/live/r85-author/standalone.json` + `standalone/*.merged.txt` | `c2e190b8…` | **20/20 PASS** receipts |
| `corpus/live/r85-author/merge_rehearsal.py` | `2f7ed468…` | this seat's rehearsal driver |
| `corpus/live/r85-author/merge-check/**` | harness `34fc5c2c…` | scratch copy == scout's paste, byte-for-byte |
| `corpus/live/r85-author/merge-runs/20261015T070315089724Z/verdicts.json` | `0d67fdbc…` | **174/174 PASS** (receipt to fold) |
| `corpus/live/r85-author/merge-runs/20261015T065931148350Z/` | — | stripped-env diagnostic (172/174), retained |
| `corpus/live/r85-author/ablation_check.py` | `82281d16…` | this seat's ablation driver |
| `corpus/live/r85-author/ablation-sig-drop.json` | `591be403…` | FAIL, exactly 15/15 camera rows |
| `corpus/live/r85-author/ablation-whitelist-drop.json` | `d22530b9…` | PASS vacuous, 174/174 |
