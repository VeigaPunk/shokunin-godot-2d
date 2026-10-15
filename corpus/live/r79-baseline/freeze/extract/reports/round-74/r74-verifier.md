# game-dev-2d round 74 — verifier (seat: verifier; host: devin)

Independent replay of r74-author on committed HEAD `ae6cb16`
("r74: LOVE physics interior-write lattice"). Leaf seat: no git
mutation, no subagents. Scratch/receipts under
`corpus/live/r74-verifier/runs{,2}/`.

## Replay procedure (commands + exits)

```
python3 corpus/fixtures/love_battery.py --runs corpus/live/r74-verifier/runs   # exit 0
python3 corpus/fixtures/love_battery.py --runs corpus/live/r74-verifier/runs2  # exit 0
```

Run dirs: `love-20261014T164300938674Z`, `love-20261014T164310636556Z`.
Both printed `totals: cases=37 pass=37 fail=0 launch_ok=True
done_marker=True exit=0` and `PASS battery: <dir>/verdicts.json`.
Host: `love --version` = `LOVE 11.5 (Mysterious Mysteries)`, Python
3.14.7 — matches the author's recorded build.

## Byte-compare results

- **iw-*.stdout.txt concatenated sha256** (shell glob order):
  `58af4e7e1bc6c754de7e3ad8dd55d75b1d1a05f1fbf831968092aeb116801f86`
  on **all 6 run dirs** — my 2 replays + all 4 author dirs. Byte-identical,
  matching the author's published hash verbatim.
- **verdicts.json (case,verdict,pinned) projection** sha256
  `0df245fb27d6cff8…` identical across all 6 dirs; all 37 verdicts PASS;
  the 18 IW observed-class strings identical run-to-run.
- **Prior rows byte-identical**: `git show ae6cb16~1:…love_battery.py` vs
  HEAD — `CASES` block (19 lines) and `SPLICE_CELLS` block (11 lines)
  `diff` clean; committed diff is `+292/-0` (0 removed content lines;
  `git diff` `-` count excluding the `---` header = 0).
- **Committed diff shape**: `git show --stat ae6cb16` =
  `love_battery.py +292`, `love_phys_probe/conf.lua +20`,
  `love_phys_probe/main.lua +234`, `r74-author.md +168`. `love_probe/`,
  `pygame_battery.py`, `pygame_probe.py` untouched (no diff in commit;
  `git status` clean).
- probe.stdout.txt / splice-*.stdout.txt differ between my runs ONLY in
  jittered arm headers (`dt_mean_ms` ~1.04, `l2_wait_ms` ~120.5 tracking
  the child's 120ms sleep, `osx ms`) — all inside pinned bounds, verdicts
  PASS. The author's byte-identical claim is scoped to iw-*.stdout.txt
  and holds exactly.

## Per-claim verdict

| # | author claim | verdict | evidence |
|---|---|---|---|
| 1 | love_phys_probe NEW, 2 files purely additive (conf.lua + main.lua ~235 ln) | **AGREE** | commit stat: conf.lua 20 ln, main.lua 234 ln; new dir in ae6cb16 |
| 2 | love_battery.py +292/-0, prior CASES/SPLICE_CELLS rows byte-identical | **AGREE** | `git diff` 0 removed lines; both tables diff-clean vs parent (15+4=19 case rows) |
| 3 | IW_PROBE_DIR const, IW_CELLS 18 rows, parse_iw/iw_classify/iw_flat_extras | **AGREE** | love_battery.py:55,118-245,251,288,332 |
| 4 | IW loop after SPLICE loop, one `love` launch per cell, iw-<cell>.{stdout,stderr}.txt, verdict=class+pins | **AGREE** | love_battery.py:451-475; 36 iw receipt files + verdicts.json per run dir |
| 5 | Partial-capture structural: fatal needs fire-line + no CELL_DONE + rc!=0 + assert on stdout | **AGREE** | iw_classify love_battery.py:323-328; my `iw-bc_setpos_unp.stdout.txt`: fire@step73 then `Error: main.lua:91: Box2D assertion failed: m_world->IsLocked() == false`, no CELL_DONE; stderr 0 bytes; rc=1 |
| 6 | love_probe/ + pygame battery/probe untouched (control) | **AGREE** | ae6cb16 touches neither; `git status` clean |
| 7 | 37/37 PASS x4 author reps | **AGREE** | all 4 author verdicts.json PASS 37/37; + my 2 independent replays PASS 37/37 on committed HEAD |
| 8 | concat iw-*.stdout.txt sha256 = 58af4e7e… | **AGREE** | reproduced on 6/6 run dirs (2 mine + 4 author) |
| 9 | Partition table classes + decisive pins | **AGREE** | all 18 classes reproduced verbatim; spot pins confirmed: refused err=`Box2D assertion failed: m_world->IsLocked() == false`; deferred `evpin cb=ec locked=false step=73` + `after_update count=3 b1pos=ERR:Attempt to use destroyed body.`; contactmask `b1vel=0,763.8724365234375` (no impulse); fatal rc=1/assert-on-stdout/no done |
| 10 | Build record: LOVE 11.5 / LuaJIT 2.1.1788460057; loveAssert catchable on this build | **AGREE (bounded)** | `love --version` + viability line `love=11.5.0 jit=LuaJIT 2.1.1788460057`; pcall catch measured directly in every refused cell. Cross-build "unconditional" is critic's strings+source claim — outside replay scope, consistent with all observed behavior |
| 11 | ext_destroy applied immediately (not deferred) | **AGREE** | pin verified: `count_after=3` + `ERR:Attempt to use destroyed body.` in-line |
| 12 | Interior-write cells ordered last, `*_unp` last of all | **AGREE** | IW_CELLS order: baseline, ext×3, interior refused/deferred/edge, unp×2 terminal; IW loop runs after CASES+SPLICE |
| 13 | ~15 s wall per battery run | **AGREE (bounded)** | my runs ~10-15 s; not pinned, plausible |

## Measured partition reproduced on committed HEAD (this host)

`captured`×1, `applied`×5 (ext×3 + contactmask + setvel),
`refused`×7 (setpos/newbody ×3 channels + setactive),
`deferred`×3 (destroy ×3 channels), `fatal`×2 (uncontained escapes) —
18/18 class-identical to the author's table and byte-identical receipts.

## Anomalies / notes

- `corpus/fixtures/__pycache__/love_battery.cpython-314.pyc` — untracked
  bytecode noise from running the battery (pre-existing pattern, not a
  source drift).
- main.lua is 234 lines vs report's "~235" — cosmetic, immaterial.
- Everything else: clean. No drift, no silent holes. The `*_unp` cells
  demonstrably die (rc=1, truncated receipt, error on stdout) and are
  classified `fatal` — the un-PASSable-default reasoning is sound.

## Verdict

**AGREE 13/13** — every falsifiable claim in
`reports/round-74/r74-author.md` reproduces on committed HEAD `ae6cb16`
with byte-identical IW receipts and identical verdict tables.
