# game-dev-2d round 74 — critic (g2d, adversarial falsification)

Seat: critic (LEAF) | Lane: g2d | Round: 74 | Wave `shokunin-train-20261101-w14`.
Host: devin. Runtime **LOVE 11.5** (Arch `love 11.5-3`, `/usr/bin/love`,
`liblove-11.5.so`), LuaJIT 2.1.1788460057, Python 3.14.
Repo `~/Projects/shokunin/game-dev-2d-shokunin`, audited at HEAD `ae6cb16`
(landed arm). **No git mutation, no subagent, no tracked file touched** —
scratch `corpus/live/r74-critic/` + this report only.

Scope of this seat: attack the landed `{refused|deferred|fatal|applied}`
partition at its joints — unp cells, fatal-class overreach, byte-identity
claims, containment-level relativity — by replaying the landed diff and
mutating it in scratch. Predecessor scratch (`r74-critic/notes.md`, F1–F8)
was read first and re-verified against the *landed* artifact, not reused
unchecked (§2, re-classification table).

## 0. What I ran

| # | command (cwd = repo root) | exit | receipt |
|---|---|---|---|
| 1 | `python3 corpus/fixtures/love_battery.py --runs corpus/live/r74-critic/replay` | 0 | `replay/love-20261014T164236427110Z/` — `totals: cases=37 pass=37 fail=0 launch_ok=True done_marker=True exit=0` |
| 2 | per-cell `cmp` of my 18 `iw-*.stdout.txt` vs the author's run1 | 0 | no DIFF lines (18/18 byte-identical) |
| 3 | `cat replay/<run>/iw-*.stdout.txt \| sha256sum` | 0 | `58af4e7e…801f86` = the author's claimed sha (all 4 author run dirs identical) |
| 4 | `IW_CELL=<c> timeout -s KILL 12 love <scratch mutant probe>` ×2 reps ×6 cells | 0/0/1/134 | `corpus/live/r74-critic/cells/*` (§2) |
| 5 | `python3 corpus/live/r74-critic/classify_receipts.py` (imports the tracked `love_battery.py`, unmodified) | 0 | `classify_out.txt` — landed classifier applied to every receipt |
| 6 | field-level provenance diff, landed receipts vs `corpus/live/r74-scout/cells/*.r1.stdout.txt` | 0 | 18/18 cells: **every shared tag.field equal**; only difference = the scout's trailing bare word `counts` (the artifact the author documents dropping) and the scout-only `trace` tag |
| 7 | `git diff ae6cb16^ ae6cb16 --numstat`; `git diff --stat ae6cb16 -- corpus/fixtures/` | 0 | `292/0` battery, `20/0` conf, `234/0` main; 0 removed lines; working tree == commit under `corpus/fixtures/` |
| 8 | `ls ~/.local/share/love/` after 20+ probe launches | 1 | absent — **no `$HOME` side effect** despite `t.identity` (conf.lua:5) |

## 1. What survives the attack

- **Insertion-only / prior-row byte-identity**: `+292/-0` on
  `love_battery.py`, 0 removed content lines; `CASES` and `SPLICE_CELLS`
  untouched; `love_probe/`, `pygame_battery.py`, `pygame_probe.py` clean
  (`git status --porcelain corpus/fixtures/` shows only an untracked
  `__pycache__`, §2-C5). Verified, not trusted.
- **37/37 and byte-identity**: independently reproduced (row 1–3). My replay
  is byte-identical to the author's receipts *per cell*, not merely equal in
  concatenated hash — a stronger statement than the landed claim.
- **Provenance vs the scout**: all 18 landed cells reproduce every field the
  scout's 22-cell scratch measured (row 6). The "ports the scout probe
  verbatim minus trace spam and the `counts` bare word" claim is exact.
- **The two `*_unp` cells behave as designed**: `fire` present, `CELL_DONE`
  absent, `rc=1`, `Error: …Box2D assertion failed…` on stdout, stderr 0
  bytes, traceback names the call (`[C]: in function 'setPosition'` /
  `'newBody'`), byte-identical across ≥5 same-format reps (author ×4 + this
  seat ×1; the scout's ×2 are field-identical, §0 row 6). The partial-capture
  pin is structural in code (`love_battery.py:323-326`), and a fatal cell kills
  only its own process — the default run stays PASSable (predecessor F6 is moot
  under the landed one-process-per-cell loop, `love_battery.py:448-475`).
- **Falsified hypotheses** (negative results, each a plausible hidden
  regression): (a) no `$HOME` identity dir is created by 20+ launches;
  (b) the `parse_iw` value-run heuristic does not mis-split any real receipt
  field (unit probes in `classify_out.txt`, incl. the `== false` and
  `ERR:Attempt to use destroyed body.` cases); (c) the unp cells' `rc=1` is
  stable, not flaky; (d) the mutant's non-`wp` code path is byte-identical to
  the landed probe (`m_wp.bc_setpos` receipt == landed `iw-bc_setpos`), so my
  patches are single-variable.

## 2. Counterexamples

### C1 (MED) — `unp` ⇒ fatal is false in general: the fatal class is *derived*, not orthogonal

Attacked claim: the brief's `{refused | deferred | fatal}` reading, and the
scout's headline "fatal is the shape of the same assertion when *not*
contained", invite "an uncontained interior write is fatal". The landed arm
only has `_unp` twins for two of its five measured write classes
(`love_phys_probe/main.lua:87-96`; rows `love_battery.py:237-244`).

Probe: added uncontained twins for the other classes in a scratch copy
(`corpus/live/r74-critic/m_unp/probe/main.lua`, sha256 `3fd220f5…`), 2 reps
each, one process per cell.

Measured (`cells/m_unp.*.r{1,2}`, byte-identical across reps):

| cell | rc | CELL_DONE | class (landed classifier) |
|---|---|---|---|
| `bc_setactive_unp` | 1 | no | **fatal** (`assert_txt=m_world_islocked`) |
| `bc_destroy_unp` | 0 | yes | **deferred** — `count_after=4`, drain `ec locked=false step=73`, `after_update count=3`, `b1pos=ERR:` |
| `bc_setvel_unp` | 0 | yes | **applied** — `vel_after=55,-7`, `after_update b1vel=55,-7` |

(Class column from the v2 re-runs, which reuse the contained cells' tags. The
first-run tags `cb_*_unp` classify **`anomaly`/FAIL** — `iw_classify`'s
mutation-tag list is hard-coded (`love_battery.py:299-302`), so any new cell
must reuse a known tag or edit the classifier. That coupling is what makes
correction (2) below a 2-row table edit rather than a code change.)

So `fatal ⟺ (assert-gated class) × uncontained`, and the containment
dimension is *inert* for the deferred/applied classes. The landed docstring
(`love_battery.py:34-36`) is narrowly correct ("the same structural write"),
but the artifact contains no cell that separates the two readings, and the
class set gives a reader no way to see that `setActive` is a third
assert-gated class with no fatal twin.

Smallest safe correction: 2 probe branches (~6 lines, reuse the existing
`cb_destroy`/`cb_setvel` tags so the classifier needs no edit — proven:
`m_unp_v2` receipts classify `deferred`/`applied` under the landed classifier,
`classify_out.txt`) + 2 `IW_CELLS` rows pinning `done=true rc=0`. Zero-cost
alternative: one docstring sentence scoping `fatal` to the assert-gated
classes.

### C2 (MED) — fatal-class overreach: the *measured* second fatal shape is unrepresentable

Attacked claim: "the measured partition is `{refused|deferred|fatal|applied}`"
and "the fatal class is a containment fact, not a build fact" (author report).
Local evidence says `fatal` is 2-shaped on this exact host/runtime:
`reports/round-74/r74-boundary.md:46,58,68-85` measures `fatal(abort)` —
sensor→solid morph of the fixture whose own `beginContact` is dispatched →
**SIGABRT rc=−6**, `terminate called after throwing an instance of
'love::Exception'` + `what(): Box2D assertion failed: p == entry->data` on
**stderr**, no done marker (2 scenes × 2 reps, byte-identical).

Probe: ported that cell into the landed IW receipt format
(`corpus/live/r74-critic/m_abort/probe/main.lua`, sha256 `4cae167c…`, scene
copied from `corpus/live/r74-boundary/cells/main.lua:84-93`, mutation from
`:401-409`), 2 reps. Result — reproducible, byte-identical:

```
IW | cell=bc_morph_abort | fire cb=bc kind=morph_abort step=1 locked=true count=2 fa_sensor=true
IW | cell=bc_morph_abort | morph_after groundFix_sensor=false
stderr: terminate called after throwing an instance of 'love::Exception'
          what():  Box2D assertion failed: p == entry->data
rc=134 (SIGABRT; = the boundary seat's `rc=-6`, same signal 6 in Python's
convention), CELL_DONE absent, stdout truncated after the morph line
```

Fed to the **landed** classifier (`classify_receipts.py`, `classify_out.txt`):
`err_on=stderr`, `assert_txt=none`, `rc=134` → **class `died`**, and a
hypothetical `IW_CELLS` row for it reports **FAIL** under every variant
(`class died != fatal`, `rc: '134' != pinned '1'`, `err_on`, `assert_txt`).
Cause is visible in code: the fatal branch and the extras both consult
**stdout only** (`love_battery.py:323-326`, `:334-347`), and the only accepted
death shape is `rc="1"` (`:239-244`).

So "fatal" as landed = `fatal(lua)`. That is deliberate and documented
(author report, "Remaining unknowns" — `died` vs `fatal`), and *sound for the
18 landed cells*; the overreach is the class **name** over its evidence: a
real, reproducible interior-write death class measured in this same round on
this same host cannot pass any row of the partition. Severity is latent
(false FAIL for a future morph cell), not active.

Smallest safe correction (choose one): (a) rename/scope the class to
`fatal(lua)` in the docstring + report (0 code); or (b) add an expected-class
`fatal_abort` to `iw_classify` keyed on `rc < 0` + `terminate called after
throwing` in stderr (`iw_flat_extras` already computes `err_on`, so this is
~4 lines) — then a future morph row is pinnable. (b) is the fuller fix; (a) is
strictly safe and zero-risk.

### C3 (MED, HIGH if the partition is read as a model) — containment-level relativity: "refused" collides two materially different measurements

Attacked claim: `refused` = "catchable Lua error … state unchanged; step
continues when contained" (scout §Headline; docstring `:27-30`). All 18 landed
cells contain the write at the **callback** level (`pcall` inside
`do_mutation`). The idiomatic LOVE containment is one level **up** —
`pcall(world.update, world, dt)` in `love.update` — which the landed arm does
not sample (probe `main.lua:218-220` calls `world:update` uncontained).

Probe: scratch copy with an update-level pcall variant
(`corpus/live/r74-critic/m_wp/probe/main.lua`, sha256 `a8b1012d…`), 2 reps,
byte-identical. Receipt (`cells/m_wp_v2.bc_setpos_wp.r1.stdout.txt`):

```
fire cb=bc kind=setpos_wp step=73 locked=true count=4 pos=400,520.1500244140625 …
wpcall step=73 update_ok=false err=main.lua:102: Box2D assertion failed: m_world->IsLocked() == false locked_after=true
cb_setpos ok=false err=main.lua:102: Box2D assertion failed: m_world->IsLocked() == false pos_after=400,520.1500244140625
wpcall exterior_setpos ok=false err=Box2D assertion failed: m_world->IsLocked() == false pos_after=400,520.1500244140625
wpcall_next step=74 update_ok=true locked_after=false b1pos=400,509.53021240234375
```

Same write, same scene, containment one level up:
- the write is still refused (pos unchanged) — but the **step aborts**
  (`update_ok=false`, no integration: b1 is at `400,509.53` on recovery vs
  `400,511.13` for the callback-contained twin), and
- the world is **transiently locked**: an unrelated *legal exterior*
  structural write (`b1:setPosition(999,999)`) is refused while
  `world:isLocked()` is true, until the next update clears it, and
- callback counts shift (`pre=37 post=37` vs baseline `36/36`).

The landed classifier still returns **`refused`** for this receipt (proven:
tagged with the known `cb_setpos` tag, `m_wp_v2` classifies `refused`,
`classify_out.txt`). So a materially different measurement — aborted step +
transient lock + collateral refusal — would PASS an `expected=refused` row.
The partition is 2-dimensional (write class × containment level) and the
landed artifact samples only the callback-level diagonal, which is the
*less* idiomatic level for a game loop. Independent corroboration of the
update-level shape already exists in this round: `r74-boundary.md:94-97`
(`uncaught_setpos_bc` → `step=1 update_ok=false`, next step clean).

Smallest safe correction: either scope the docstring/report line to
"callback-level containment" (0 code, strictly safe), or add one cell
(probe branch + `wp_mode` update-pcall ≈ 20 lines, row pins `update_ok=false`,
`locked_after=true`, recovery at step+1). The second is additive and would
close the collision; it is the one I would fold if the judge wants the
partition to be a model rather than a receipt set.

### C4 (LOW) — the fatal rows do not pin *which* call threw

`iw-bc_setpos_unp` and `iw-bc_newbody_unp` are pinned on `rc`, `done`,
`err_on`, `assert_txt` and the `fire.kind` label (`love_battery.py:237-244`).
`assert_txt` distinguishes body-level (`m_world->…`) from world-level
(`IsLocked()…`) only; predecessor F3 established that the assert text does not
identify the function, and the *independent* witness — the traceback's
`[C]: in function 'setPosition'` / `'newBody'` line, present in every unp
receipt (my replay, §0 row 1) — is parsed nowhere (`parse_iw` ignores
non-`IW` lines, `:251-285`). A future probe bug that throws the *same-shaped*
assert from a different body-level call in the same branch would PASS both
rows. Safe direction is not automatic here (it is a false-PASS shape).
Smallest safe correction: have `iw_flat_extras` scan stdout for
`in function '<name>'` into `esc_fn`, and pin it on the two unp rows (~4
lines + 2 pins). Acceptable alternative: document that the escape function is
deliberately unpinned.

### C5 (LOW / INFO) — two provenance nits

1. `corpus/fixtures/love_phys_probe/conf.lua:1-3` claims "Same regime the
   frontier phys_probe **and** the r74 scout scratch measured under". True for
   the scout (`corpus/live/r74-scout/probe/conf.lua` — identical module set,
   only comment/identity differ), **false for the frontier**
   (`corpus/live/frontier-lovephysics/phys_probe/conf.lua` leaves `sound`,
   `video`, `font`, `joystick`, `keyboard`, `mouse`, `thread`, `touch`,
   `sensor` at default on). No measurement impact (physics/timer/event on in
   both; every pose pin is byte-identical to the scout's), comment-only.
   Fix: name only the scout scratch as the shared regime.
2. `corpus/fixtures/__pycache__/love_battery.cpython-314.pyc` is untracked and
   **not** gitignored (`git check-ignore` → not ignored), so any harness that
   *imports* the battery leaves a stray file inside the tracked fixture tree
   (this seat's `classify_receipts.py` does; the pattern predates the landing
   — `run_battery.cpython-314.pyc`, 13:05 local, before `ae6cb16` at 13:40).
   INFO only; the landed arm did not introduce it.

### Re-classification of predecessor findings (verified against the landed artifact)

| prior | status on the landed artifact |
|---|---|
| F1 containment-dependence (refused vs poison) | **Confirmed and sharpened** → C3 (the "poison" is a transient lock, recovered next step) |
| F2 deferred = end-of-current-update drain at `locked=false` | **Confirmed** — landed pins `evpin_ec_lck=false evpin_ec_step=73` (`love_battery.py:196-213`) |
| F3 assert text does not identify the function | **Confirmed**, and now mitigated for unp cells by the traceback — which is unpinned (C4) |
| F4 `loveAssert` unconditional / silent-refusal path dead | Not re-fetched by me; landed build record (`love_phys_probe` receipts `love=11.5.0 codename=Mysterious Mysteries`) + boundary source anchor (`r74-boundary.md:106-129`) stand |
| F5 effect-only pins not load-bearing (`mutant_noop`) | **Superseded** — every refused row pins `pos_after` to the fixed channel-split pose (a no-mutation witness), not merely `ok=false` |
| F6 a fatal cell in the default battery ⇒ un-PASSable run | **Moot** under the landed per-cell loop; 37/37 exit 0 reproduced |
| F7 BC `setvel` is solver-authoritative (`54.15,0`) | **Does not reproduce in the landed scene**: landed `iw-bc_setvel` shows `after_update b1vel=55,-7` and `final b1pos x=479.47` (x-velocity persists 200 steps). F7 was predecessor-scene-specific and must not be carried as a general claim. Note the landed row pins only the in-callback read-back, so "applied" is currently a *legality* claim; the effect witness exists in every run dir and could be pinned (`after_update.b1vel: 55,-7`) at zero regression risk |
| F8 scout summary drift (`pre_contactmask`) | **Confirmed corrected** in the landed table (`:221-229`, class `applied`) |

## 3. Impacted axes

1. **Partition expressiveness / pin fidelity** — C1, C2, C3 (a class that
   collides two measurements, and a measured death shape with no bucket).
2. **Evidence provenance & false-pass resistance** — C4 (unpinned independent
   witness), C2 (stdout-only assert scan).
3. **Regression safety of the landed diff** — clean: insertion-only, controls
   untouched, byte-identity reproduced independently, one process per cell.
4. **Claim precision / scope** — C2, C3, C5-1 (all claim-scope, not
   measurement errors).

Pareto-admissible moves only: every correction in §2 is additive (extra rows,
extra pin, extra class shape) or a comment/docstring scope edit; none removes
a pin, changes a class for an existing cell, or alters the landed receipts.

## 4. Smallest safe corrections (ranked, minimal)

1. **(0 code, strictly safe)** Scope the docstring/report wording: `refused`
   is callback-level-containment relative; `fatal` = `fatal(lua)`
   (`rc=1` + assert on stdout); a second measured fatal shape
   (`fatal(abort)`, rc<0 + stderr) classifies `died`→FAIL by design.
2. **(+2 rows, +~6 probe lines)** `bc_destroy_unp` (expected `deferred`) and
   `bc_setvel_unp` (expected `applied`) — reuse existing tags; classifier
   agreement already proven (`m_unp_v2`).
3. **(+1 cell, +~20 probe lines)** update-level containment
   (`bc_setpos_wp`) pinning `update_ok=false`, `locked_after=true`,
   next-update recovery — closes the C3 collision.
4. **(+~4 lines, +2 pins)** `esc_fn` from the traceback on the two unp rows.
5. **(+1 pin)** `after_update.b1vel: "55,-7"` on `iw_bc_setvel` to make
   "applied" effect-bearing rather than legality-only.
6. Comment fix for C5-1; optional `corpus/fixtures/__pycache__/` ignore for C5-2.

None of these is required for the landed 37/37 to be *true* — they are the
cheapest moves that keep the partition from over-claiming. Whether to take
(2)/(3)/(4) or stop at (1) is a judge tradeoff (host-bound pin count vs
partition completeness), not a defect I can settle from this seat.

## 5. Provenance / reproduce

- Audited commit `ae6cb16` (`git log --oneline -1`); `git diff --stat ae6cb16
  -- corpus/fixtures/` empty ⇒ working tree == commit for the fixture tree.
- Landed hashes (`git show ae6cb16:<path> | sha256sum`):
  `love_battery.py` `281f57c8aa7c66bc29345136e26eabb1844ab548e6517aecb92c4dbd49b1f4b4`,
  `love_phys_probe/main.lua` `2c0ac37826c9487e15deded2eedb8122e024c98d1fff144740e34871780495b5`,
  `love_phys_probe/conf.lua` `d2b9e62b6c998673266af31a1f57e1e2e4025bdcea7c3a5b86fed8b3413c8088`.
- `git status --porcelain | grep -v '^??'` shows only two files modified, both
  **before this seat started** and outside its write scope:
  `corpus/live/r72-simplifier/snapshots/log.txt`, `corpus/live/r72-simplifier/watch.log`
  (present in the first status of this session). This seat's only additions are
  `corpus/live/r74-critic/` and this report.
- This seat's scratch (all under `corpus/live/r74-critic/`, no tracked file
  touched):
  `m_unp/probe/main.lua` `3fd220f5…`, `m_wp/probe/main.lua` `a8b1012d…`,
  `m_abort/probe/main.lua` `4cae167c…`, `classify_receipts.py` `d8cb0b6a…`,
  `notes.md` (predecessor) `e46c95b9…`.
- Reproduce: `python3 corpus/fixtures/love_battery.py --runs corpus/live/r74-critic/replay`
  (37/37, exit 0); mutant cells: `cd corpus/live/r74-critic && IW_CELL=<c>
  timeout -s KILL 12 love <m_*>/probe`; classifier replay:
  `python3 corpus/live/r74-critic/classify_receipts.py`.

## 6. Bounded claims / not measured

- All claims are for **this host**: LOVE 11.5 / liblove-11.5.so / LuaJIT
  2.1.1788460057. The exact physics poses (`400,511.13113403320312`, fire
  step 73, callback counts) are this-build values; the *classes* are the
  load-bearing assertion, as the author states.
- I did not re-fetch LOVE/Box2D sources; the abort mechanism is cited from
  `r74-boundary.md:106-129` (their source anchor), and my contribution is the
  reproduction + the classifier verdict, not the mechanism.
- The abort port is *my* scene reconstruction of the boundary cell in IW
  format (same scene constants, same mutation); it reproduces their rc/stderr
  shape byte-identically across 2 reps, but it is not a byte-replay of their
  driver.
- Not exercised: `world:destroy()` interior, double-`destroy()`,
  `contact:setEnabled` in `beginContact`/`postSolve` (scout/boundary gaps,
  unchanged), and any hard-abort build (`b2Assert` as `assert()`); the last is
  the one build variant that would flip C1/C2 rows to `died`/FAIL by design.
- `lsp` disclosure: no lsp/pyright/pylsp/jedi/lua-language-server on PATH
  (same host state as r72/r73/r74 scout); all findings are process-level
  measurements plus `file:line` citations.
