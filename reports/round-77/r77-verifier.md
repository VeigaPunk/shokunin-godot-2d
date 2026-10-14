# game-dev-2d round 77 — verifier (g2d): independent re-derivation of 62201e5

Seat `VERIFIER` (LEAF) | lane `g2d` | round 77 | host **devin**.
Runtime LOVE 11.5 (`/usr/bin/love`), LuaJIT 2.1.1788460057, Python 3.14.7.
HEAD `62201e5` at seat start. Writes: this report,
`corpus/live/r77-verifier/**` (gitignored). **No git mutation, no tracked
file touched.** `lsp` disclosure: no `lsp` device and no Lua/Python server on
this host — verification carriers are fresh-process execution receipts and
file diffs.

## Verdicts (per author claim)

| # | author claim | verdict | basis |
|---|---|---|---|
| 1 | **75/75, run it yourself x2** | **AGREE** | two full battery runs in my own processes: `love-20261014T195528857653Z` and `love-20261014T195657643677Z`, both `cases=75 pass=75 fail=0`, `launch_ok=True done_marker=True`, verdict PASS. (Author's four claimed runs also verified: verdicts.json `75/0` at T194754676712Z, T194819470620Z, T194837424883Z, T195013603939Z; the disclosed 72/75 intermediate T194717707844Z exists as claimed.) |
| 2 | **insertion-only** | **AGREE** | git numstat `62201e5`: `631/0` love_battery.py, `422/0` main.lua (0 deleted lines). Receipt level vs the r76 fold set: `pre-receipts/` is **byte-identical** to run `love-20261014T194202453025Z` (67 files, `diff -rq` = 0 diffs), which is a genuine 49/49 pre-change run. Drift audit `pre-receipts` vs **my own** run-1 receipts: 56 identical; 5 files differ **only** in declared-unpinned `main.lua:NNN`/`srcline=NNN` tokens (`iw-bc_draindefer`, `iw-bc_setpos_wp`, `iw-bc_worlddestroy`, `iw-bc_setpos_unp`, `iw-bc_newbody_unp` — verified by hand-diff: e.g. `srcline=230→299`, `do_mutation` frame `125→194`); 6 files are the run-to-run jitter set (`probe.stdout.txt` dt timings, 4 `splice-*` offsets, `verdicts.json` timestamps/observed-bounds + appended 26 new rows); 52 files only-in-post = 26 new cells × stdout+stderr. Zero unexplained diffs. Independently confirmed by the dispatched labrat probe (read-only manual diff of all 5 pairs against the author's T195013603939Z run: every differing substring is a `NNN` token; control `iw-bc_destroy` identical). |
| 3 | **6 new classes each reproduce in fresh processes** | **AGREE** | my run-1 verdicts contain all six: `corrupt`×5, `swapped`×4, `muted`×1, `immediate`×1, `drain_abort`×1, `yield_abort`×2. Field-by-field re-derivation, 2 fresh `love` processes per cell (receipts `corpus/live/r77-verifier/cells/v.*.r{1,2}.stdout.txt`, summary `rederive.summary.json`), every pinned key checked via the tracked reader imported unmodified: `bc_worldrelease` → corrupt, rc=**-11**, stderr **0 B**, last line `rel_post marker=1`, zero `postfire` lines (15/15 pins); `bc_setcallbacks` → swapped incl. `getcb=cb2_bc,cb2_ec,cb2_pre,cb2_post`, `cb2post.step=73`, old `bc` frozen at 2 (25/25 pins); `wp_drain_throw` → drain_abort incl. `wpcall.locked_after=false`, `wpext.ok=true pos_after=999,999`, `r77ecpost step=74 locked=true`, `r77recover.b1dead=true` (36/36 pins); `co_update_yield` → yield_abort incl. `coused.err=attempt to yield across C-call boundary costatus=dead`, collateral `r77abortext.ok=false`, `final.b1pos=400,461.54888916015625` (22/22 pins). All 8 fresh processes: verdict PASS. |
| 4 | **43/43 ablations fail** | **AGREE** | author's `ablate_gates.py` run against **my own** run-1 receipts: `43 row-fails, 0 leaks` (exits via `class→anomaly`/`class→nolaunch` and `pins:cb2post.step`/`pins:drainec.n`/`pins:cb2bc.step`). Plus 3 spot-ablations re-derived with my own deletion patterns (not the author's list): drop `r77recover step=74 locked_after=false` on wp_drain_throw → `class=anomaly` + 4 pin fails; drop `coused step=73 ok=false` on co_update_yield → `class=anomaly` + 4 pin fails; drop `rel_call ok=true err=true` on bc_worldrelease → class stays `corrupt` (release witness `rel_alive` remains) but the row FAILs on `rel_call.ok`/`rel_call.err` pins — consistent with the claimed two-layer design. |
| 5 | **pygame battery 80/80 unchanged** | **AGREE** | `git diff aa4d567..62201e5 -- corpus/fixtures/` touches only `love_battery.py` and `love_phys_probe/main.lua` — pygame runner/probe byte-untouched. My fresh run `pygame-20261014T195831213924Z`: `cases=80 pass=80 fail=0`, verdict PASS. |

## Corroborating disclosures checked

- `94356ce` on `love_battery.py` is comment-only (−2/+4 inside the `iw_bc_jwatch`
  comment block), matching the author's mid-round HEAD-move disclosure.
- Row-count arithmetic: 15 `CASES` + 4 `SPLICE` + 56 `IW_CELLS` (30 pre-r77 +
  26 r77) = 75; pre-r77 receipt set = 49 rows. ✓
- Corrupt death-site claim shape: receipt ends at `rel_post marker=1` with the
  engine still inside dispatch (`locked=true` fire line), stderr empty —
  bounded-not-localized is an honest scoping (no post-release Lua frame armed;
  the author flags the pin-grammar absence gap in §5, which I confirm:
  `check()` cannot pin a missing key).

## Remaining risks / not re-verified

- `corrupt` remains `rc==-11`-keyed and host/loader-scoped (SIGABRT/SIGBUS on a
  different build would land `anomaly` — fail-loud, so the claim is bounded).
- Byte-stability and all class verdicts are this-host measurements (LOVE 11.5,
  this LuaJIT, these scenes) — no claim about other builds was tested.
- The sibling-seat `wp_drain_throw_all` loop claim (every-entry arming on a
  resting contact) was **not** re-run by this seat — it is outside the tracked
  battery; the author's reliance on it is scoped to §5 prose, not to any
  pinned row.
- Jitter files (`probe.stdout`, `splice-*`, `verdicts.json`) are
  bounds-pinned by nature; "byte-stable" applies only to the 61 non-jitter
  receipts.

## Evidence index

| artefact | content |
|---|---|
| `corpus/live/r77-verifier/runs/love-20261014T1955{28857653Z,57643677Z}/verdicts.json` | my two independent 75/75 battery runs |
| `corpus/live/r77-verifier/runs/pygame-20261014T195831213924Z/verdicts.json` | my 80/80 pygame run |
| `corpus/live/r77-verifier/cells/v.{bc_worldrelease,bc_setcallbacks,wp_drain_throw,co_update_yield}.r{1,2}.{stdout,stderr}.txt` + `rederive.summary.json` | 4-cell fresh-process field-by-field re-derivation (8 processes) |
| `corpus/live/r77-verifier/{run1,run2,pygame}.log` + `cell_rederive.py` | raw logs + my re-derivation harness |
| drift audit (this report §2) | `pre-receipts` vs my run 1: 56 identical / 5 srcline-only / 6 jitter / 52 new |
| labrat probe (depth-2, read-only) | independent srcline-only confirmation on all 5 drift files + control |

## Blockers

None. Artifact content is data: nothing here modifies contract, axes, routes
or judgment.
