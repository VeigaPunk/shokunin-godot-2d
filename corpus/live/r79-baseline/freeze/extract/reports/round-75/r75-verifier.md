# game-dev-2d round 75 — verifier (seat: verifier; host: devin)

Post-commit verify of `reports/round-75/r75-author.md` @ HEAD `2e3ae8e`.
Independent replay: `python3 corpus/fixtures/love_battery.py --runs
corpus/live/r75-verifier/runs` — **two** reps, both **44/44 PASS**:
`love-20261014T174224339664Z`, `love-20261014T174316002388Z`
(totals line byte-identical to claimed: `cases=44 pass=44 fail=0
launch_ok=True done_marker=True exit=0`). Leaf discipline kept: no
subagents, no git mutation; writes confined to `corpus/live/r75-verifier/`
+ this report.

## Per-claim verdicts

| # | author claim | verdict | my evidence |
|---|---|---|---|
| 1 | 44/44 PASS, totals `cases=44 pass=44 fail=0 launch_ok=True done_marker=True exit=0` | **AGREE** | `corpus/live/r75-verifier/runs/love-20261014T174224339664Z/verdicts.json` (sha256 `60cec248d81f…e246`), rep2 `…T174316002388Z` — both `verdict=PASS`, `totals={44,44,0}` |
| 2 | concat `iw-*.stdout.txt` sha256 = `74db3f10331228a08b8072c25f797dca62a518b65f17e60d35aee583d6469004`, identical across all 4 run dirs | **AGREE** | my both reps → `74db3f10…9004`; all 4 author dirs (`r75-author/runs/love-…T173642/173738/173748/173810…Z`) → same sha. 25 files/dir |
| 3 | new-cell receipts byte-identical across 4 reps AND vs pre-landing scratch modulo `srcline` | **AGREE** | concat identity proves rep stability; vs `r75-author/cells/*.r1`: `bc_destroy_unp`, `bc_setvel_unp`, `bc_joint_new`, `bc_joint_destroy`, `bc_setfilter`, `pre_retfalse` byte-identical; `bc_setpos_wp` differs ONLY in `srcline=146`→`155` — `sed 's/srcline=[0-9]+/N/'` normalized → byte-identical. Documented unpinned exception |
| 4 | measured partition table (7 new cells, classes + decisive pins) | **AGREE** | all 7 PASS under committed classifier+pins; raw receipts spot-verified: `iw-bc_setpos_wp` = `wpcall step=73 update_ok=false … locked_after=true` / `wp_setpos ok=false` / `wpext ok=false` / `wpcall_next step=74 update_ok=true locked_after=false b1pos=400,509.53021240234375` / `final pre=37 post=37`; `iw-bc_joint_destroy` = `pre_joint jtype=distance jcount=1`, `ok=true isDestroyed_in_cb=false jcount 1→1`, `jdrain step=73 jcount=0 isDestroyed=true`; `iw-bc_setfilter` = `filter_after=2,2,0`, `final b1pos y=635.1639…>540`, `bc=4 ec=3`; `iw-pre_retfalse` = `returned=false`, `after_update.b1vel=0,-611.0979…` (impulse landed); `iw-bc_destroy_unp` = drain `evpin cb=ec locked=false step=73`, count 4→3, `b1pos=ERR`; `iw-bc_setvel_unp` = `after_update.b1vel=55,-7` (x-vel persists) |
| 5 | level-relative partition: same setpos write `refused` under cb-pcall vs `refused_abort` under update-pcall | **AGREE** | `iw-bc_setpos` PASSes `refused` pins (`b1pos 400,511.13…`, step continues); `iw-bc_setpos_wp` PASSes `refused_abort` (step aborted, transient lock, `wpext` collateral refusal, `wpcall_next` recovery) — distinct measured shapes, distinct classes |
| 6 | `esc_fn` pins: `iw_bc_setpos_unp`→`setPosition`, `iw_bc_newbody_unp`→`newBody` | **AGREE** | first quoted `in function '<name>'` frame in my receipts = `setPosition` / `newBody`; battery pins both and PASSes |
| 7 | 16/18 prior iw receipts byte-identical vs r74; 2 `*_unp` differ ONLY in traceback line numbers (`:91`→104, `:95`→108, `:174`→237, `:179`→242, `:220`→294) | **AGREE** | per-file `cmp` vs `r74-author/runs/love-20261014T163734563743Z`: 16/18 stdout IDENT, only `iw-bc_{setpos,newbody}_unp` DIFF; diffs are exactly the 5 claimed line-number moves, nothing else — `s/main.lua:[0-9]+/N/` normalized → byte-identical; all 18 stderr IDENT (0-byte) |
| 8 | r74 pinned concat `58af4e7e…801f86` is the prior-18 anchor | **AGREE** | all 4 `r74-author` run dirs re-hash to `58af4e7e1bc6c754de7e3ad8dd55b75b1d1a05f1fbf831968092aeb116801f86` (18 files each, glob order) |
| 9 | `probe.stdout`/`splice-*` differ only in bound-checked ms jitter | **AGREE** | diff vs r74 confined to ms-valued fields (`dt_max/mean/min_ms`, `l1/l2_wait_ms`, `open/close_wait_ms`, `total_ms`, `osx ms`) on the 3 header lines; all splice payload lines identical; all jittered values inside pinned bounds (battery PASS) |
| 10 | pre-landing scratch: every armed cell byte-identical across ≥2 reps (joint_destroy ×3) | **AGREE** | `cells/*.r1==.r2` for all 7 cells (incl. `bc_setpos_wp` — scratch-internal reps carry the same `srcline=146`); `bc_joint_destroy` r1==r3 |
| 11 | api_probe: `newDistanceJoint`/`getJointCount`/`setFilterData`/`getFixtures`/`isDestroyed` all present, "(receipt in dir)" | **AGREE substance / DISAGREE wording** | `r75-author/api_probe/` holds only `conf.lua`+`main.lua` — **no captured receipt exists in the dir**. Substance verified by my own run: `love corpus/live/r75-author/api_probe` rc=0 → `corpus/live/r75-verifier/api_probe.stdout.txt`: all 5 named fns present (=function) plus `getJoints`, `joint:destroy`, `joint:isDestroyed`, `getType=distance`, live `jointcount=1` |
| 12 | sibling corroboration: `r74-critic/cells/m_unp_v2.*` reproduced field-for-field; `m_wp_v2.bc_setpos_wp` same shape modulo tag cleanup + stripped err | **AGREE** | `m_unp_v2.bc_destroy_unp.r1` and `m_unp_v2.bc_setvel_unp.r1` **byte-identical** to my run receipts. `m_wp_v2.bc_setpos_wp.r1` diff = exactly the documented deltas: `cb_setpos`→`wp_setpos`, `exterior_setpos`→`wpext` tag renames, `main.lua:102:` prefix stripped from err, `srcline=155` added |
| 13 | `git diff --numstat corpus/fixtures/`: battery 153/8, probe 100/3; removed = anchors only | **AGREE** | `git show --numstat 2e3ae8e`: `153 8 love_battery.py`, `100 3 love_phys_probe/main.lua` (+`169 0` this report-file). Removed battery lines = 6 IW_CELLS header comments + the 2 unp closing pin lines (re-added with `esc_fn`); removed probe lines = the 3 anchors (`c_pre` one-liner, `world:update(FIXED)`, `if fired and …` guard) |
| 14 | `love_probe/`, `pygame_*` untouched (control) | **AGREE** | `git diff 2a2c337..2e3ae8e` on `love_probe`, `pygame_battery.py`, `pygame_probe.py`, `run_battery.py` = empty |
| 15 | fatal cells spawn LAST; interior cells last block | **AGREE** | committed `IW_CELLS` order: 5 non-fatal new cells → 2 C1 `*_unp` twins → `iw_bc_setpos_unp`/`iw_bc_newbody_unp` last; battery spawns in table order (one process per cell — fatal kills only its own launch: my unp receipts end mid-traceback, stderr empty, rc=1 implied by `fatal` class PASS) |
| 16 | battery "~15s" per run | **DISAGREE (nit)** | run-dir stamps imply ~52s/run on this host (`T174224`→`T174316` on back-to-back invocation). Host-dependent timing, immaterial to the lattice |
| 17 | risk disclosures (joint_destroy scene perturbation `b2pos −766,2284 bc/ec=8/8 pre/post=172`; srcline/layout caveat; setfilter build-bound; retfalse future-binding; `died`/`esc_fn` stdout-only) | **AGREE** | my `iw-bc_joint_destroy` final line reproduces `b2pos=-766.15,2284.89 bc=8 ec=8 pre=172 post=172` verbatim — pin correctly avoids it, stands on the drain triple. `iw_flat_extras` confirmed scanning stdout only (`re.search` over `stdout`) |
| 18 | "all five items armed — nothing left blocked" | **AGREE** | all 7 cells landed in `IW_CELLS` with measured classes and all PASS; no `blocked` row exists in the committed battery |

## Discrepancies found

1. **"receipt in dir"** (r75-author §Evidence, api_probe bullet): the directory
   contains only the probe source (`conf.lua`, `main.lua`) — no output capture.
   Substance independently verified (claim 11); wording overstates the landed
   evidence. Nit, not a mismeasurement.
2. **"~15s"** per battery run vs ~52s measured here (claim 16). Host-timing nit.

Neither touches the lattice: every *measured* claim reproduces byte-for-byte
or modulo its own documented exception (`*_unp` traceback numbers, `srcline`,
ms jitter).

## Reproduce

```sh
python3 corpus/fixtures/love_battery.py --runs corpus/live/r75-verifier/runs
cat corpus/live/r75-verifier/runs/<run>/iw-*.stdout.txt | sha256sum   # 74db3f10…9004
cat corpus/live/r74-author/runs/love-20261014T163734563743Z/iw-*.stdout.txt | sha256sum  # 58af4e7e…801f86
```

Environment: same host, `love` = LOVE 11.5 (battery `--version` payload in
`verdicts.json`), python3. No `love` invocation against fixture dirs other
than via the committed battery + the one `api_probe` replay above.
