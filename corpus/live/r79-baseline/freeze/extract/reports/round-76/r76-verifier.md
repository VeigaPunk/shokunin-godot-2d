# game-dev-2d round 76 — verifier (seat: verifier; host: devin)

Lane `g2d`, wave `shokunin-train-20261101-w16`. POST-COMMIT verify of
HEAD `6ca715d` ("r76: drain-observer cells + destroy edges"). Host:
LOVE 11.5 (`/usr/bin/love`, same build as author), Python 3.14.7,
pygame 2.6.1. Leaf discipline: no subagent, no git mutation, no
tracked-file edits. Writes = this report + `corpus/live/r76-verifier/**`.

## Claim 1 — battery 49/49 PASS, launch_ok + done_marker: AGREE

Two independent runs of the committed battery:

```
python3 -B corpus/fixtures/love_battery.py --runs \
  /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r76-verifier/runs
```

| run dir | verdict | totals | launch_ok | done_marker | exit |
|---|---|---|---|---|---|
| `love-20261014T183308913807Z` | PASS | 49/49/0 | True | True | 0 |
| `love-20261014T183323023922Z` | PASS | 49/49/0 | True | True | 0 |

49 = 15 CASES + 4 splice + 30 IW cells (25 prior + 5 new). Per-run
`verdicts.json` rows carry rc; the new-five rows record
`deferred_abort/deferred/deferred/ignored/died` with rc 0,0,0,0,1 —
matching the pinned classes.

## Claim 2 — concatenated iw-receipt sha = d1cbc1f8…: AGREE

`cat iw-*.stdout.txt | sha256sum` over each run dir (30 files, glob
order):

- run 1: `d1cbc1f8d23f4cbc4706406fddcfb38046b2f3693a8866e43480a07ebb9321f0`
- run 2: `d1cbc1f8d23f4cbc4706406fddcfb38046b2f3693a8866e43480a07ebb9321f0`

Byte-exact match to the author's claimed sha, on both of my
independent reps.

## Claim 3 — prior-cell byte-identity vs r75-era receipts: AGREE

Compared all 25 prior `iw-*.stdout.txt` in my run 1 against every
`corpus/live/r75-author/runs/love-*` dir (4 r75-era dirs, identical
result set for each):

- **20/25 byte-identical.**
- **5 diffs, all declared** (none semantic, all pinned keys intact):
  - `iw-bc_setpos_unp`, `iw-bc_newbody_unp`: only `main.lua:NNN`
    numbers on the raw `Error:` line + traceback frames
    (104→125, 108→129, 237→315, 242→337, 294→399). Unpinned text;
    `esc_fn` pins (setPosition/newBody), rc=1, assert bytes unchanged.
    Declared unpinned traceback drift.
  - `iw-bc_setpos_wp`: `srcline=155→181` only — the key is
    emitted-unpinned by design.
  - `iw-bc_destroy_unp`, `iw-bc_setvel_unp`: single added field
    `mode=unp` on the `cb_destroy`/`cb_setvel` lines. This is the r75
    fold delta, not r76 drift: commit `be79ad1` (r75 fold, F1) added
    the emission and its own message declares "Expected receipt
    deltas: mode=unp on the two twin rows; unpinned traceback line
    numbers on the two fatal rows + wp srcline". The r75 run dirs
    predate that fold; the r76 battery PINS `cb_destroy.mode=unp` /
    `cb_setvel.mode=unp`, so the field is now required, not drift.

Note on baseline wording: the author's report quantified "22/25
byte-identical vs HEAD-probe" (a different baseline — fresh launches
on `git show HEAD:` source). Vs r75-era dirs the count is 20/25
identical + 5 declared diffs; the author's own 3-cell drift set is a
subset, and the remaining 2 are covered by the fold's declared deltas.
Same conclusion either way: zero undeclared drift, zero semantic
changes to pinned keys.

## Claim 4 — five new cells, independently relaunched: AGREE (all 5)

My own LÖVE processes, `IW_CELL=<c> timeout -s KILL 15 love
corpus/fixtures/love_phys_probe`, receipts in
`corpus/live/r76-verifier/cells/`; classes re-derived by the committed
`iw_classify` on my captures (not the author's):

| cell | my rc | re-derived class | claimed | verdict | decisive witnesses in MY receipt |
|---|---|---|---|---|---|
| bc_draindefer | 0 | deferred_abort | deferred_abort | AGREE | `abortq step=73 count=4 b1pos=400,520.15` (drain skipped, pose readable); `drainlate step=74 count=3 b1pos=ERR`; `ecunl cb=ec step=74 locked=false`; `wpcall_next step=74 b1pos=ERR` |
| bc_destroy2 | 0 | deferred | deferred | AGREE | `post_destroy2 ok=false err="Attempt to use destroyed body." count=3 isDestroyed=true` — lifetime guard, not IsLocked assert; normal drain at 73 |
| bc_worlddestroy | 1 | died | died | AGREE | `wdrained step=73 isDestroyed=true`; `Error: main.lua:439: Attempt to use destroyed world.`; traceback first frame `getBodyCount` (= esc_fn); no assert text; no CELL_DONE |
| bc_jwatch | 0 | deferred | deferred | AGREE | `jwlive` last-wins `cb=post step=73 locked=true jcount=1`; `jdrain step=73 jcount=0 isDestroyed=true`; `jwdrop cb=ec step=74 jcount=0` — bounded drain window |
| pre_retfalse1 | 0 | ignored | ignored | AGREE | `rf1counts falses=1 passes=1` (contact-scoped discrimination executed); `after_update.b1vel=-2.81,-611.97` impulse landed |

All 5 spot receipts are **byte-identical** to the corresponding
battery `iw-*.stdout.txt` in my run dirs — my processes reproduce the
committed pins exactly, including `final.b1pos=455.88,477.90` on
retfalse1.

## Claim 5 — pygame family (80/80) untouched: AGREE

`git show --stat HEAD`: the commit touches only
`corpus/fixtures/love_battery.py`, `corpus/fixtures/love_phys_probe/main.lua`,
`reports/round-76/r76-author.md`. No `pygame_*` file touched.
Independent run: `python3 -B corpus/fixtures/pygame_battery.py
--runs corpus/live/r76-verifier/pygame-runs` →
`totals: cases=80 pass=80 fail=0 launch_ok=True done_marker=True exit=0`
(`pygame-20261014T183425337653Z`). 80/80 PASS.

## Evidence inventory

- `corpus/live/r76-verifier/runs/love-20261014T183308913807Z/` —
  verdicts.json + 30 iw + probe + splice receipts
- `corpus/live/r76-verifier/runs/love-20261014T183323023922Z/` — rep 2
- `corpus/live/r76-verifier/cells/` — 5 own-process spot receipts
  (stdout+stderr each)
- `corpus/live/r76-verifier/pygame-runs/pygame-20261014T183425337653Z/`
- Fixture working tree: `git status corpus/fixtures/` clean (only a
  pre-existing untracked `__pycache__` pyc, predating my runs; all my
  python invoked `-B`).

## Verdict

**AGREE on all claims.** Every measured assertion in r76-author.md
reproduces on the committed tree from independent processes: 49/49 ×2,
concat sha exact-match ×2, all prior-cell deltas declared (3 unpinned
traceback/srcline + 2 fold-declared mode=unp fields), all 5 new
classes re-derived from my own receipts, pygame control 80/80.

## Caveats (bounded, this host)

- Baseline note above: author quoted identity vs a HEAD-probe; this
  verify used the tasked r75-era baseline. Both baselines support the
  same conclusion; the counts differ because the baselines differ.
- `srcline=` keys remain layout-coupled by construction (emitted
  unpinned): my spot receipt shows `srcline=230` on draindefer's
  wpcall line and `srcline=181` on setpos_wp — consistent across all
  my receipts on this HEAD, but expected to shift on any further
  additive edit.
- Bounded to LOVE 11.5 / LuaJIT on this host; no other build tested.
