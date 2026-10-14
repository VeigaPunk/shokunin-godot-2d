# game-dev-2d round 74 — reviewer (seat: reviewer; host: devin)

Scope: correctness review of the landed diff `ae6cb16` ("r74: LOVE physics
interior-write lattice"), reviewed on the committed tree and replayed.

Artifact identity (verified, not assumed):

```
$ git rev-parse HEAD                  -> ae6cb16c53968439ba694f3648a9ce42a8a55480
$ git hash-object corpus/fixtures/love_battery.py love_phys_probe/{main,conf} -> 083930a5… 1b3f8a21… bc62baad…
$ git rev-parse HEAD:…                -> 083930a5… 1b3f8a21… bc62baad…   (working tree == commit)
$ git diff HEAD --stat -- corpus/fixtures/   -> empty
```

Replay (this seat, committed tree):

```
$ python3 corpus/fixtures/love_battery.py --runs corpus/live/r74-reviewer/runs
totals: cases=37 pass=37 fail=0 launch_ok=True done_marker=True exit=0     (exit 0)
$ python3 corpus/fixtures/love_battery.py --runs corpus/live/r74-reviewer/runs2
totals: cases=37 pass=37 fail=0 launch_ok=True done_marker=True exit=0     (exit 0)
```

Bounded to this host: LOVE 11.5 (Mysterious Mysteries), LuaJIT 2.1.1788460057,
Python 3.14.7. Leaf seat: no git mutation, no subagents. `lsp` device: **not
present in this seat's toolset**; no language server on PATH
(`pyright|pylsp|python-lsp-server|jedi-language-server|lua-language-server|
typescript-language-server` all ABSENT via `command -v`). All checks below are
therefore structural/textual and are labelled as such — no semantic-LSP proof
is claimed.

## Verified claims (each against raw evidence, not the author's report)

1. **Insertion-only.** `git diff --numstat 1275746 ae6cb16` = `292/0`
   (`love_battery.py`), `20/0`, `234/0`, `168/0` (new files). `git diff
   1275746 ae6cb16 -- corpus/fixtures/love_battery.py | grep -c '^-[^-]'` = 0:
   no prior line was removed or altered. Exactly four hunks, all pure
   insertions: docstring paragraph (`love_battery.py:23-41`), `IW_PROBE_DIR`
   (`:55`), the IW block (`:109-348`), and the IW loop in `main()`
   (`:448-475`).

2. **19 prior case rows byte-identical.** `CASES` (15 rows, `:59-77`) and
   `SPLICE_CELLS` (4 rows, `:82-92`) extracted from both revisions compare
   equal (string equality, not diff-of-diff). Behaviorally: the pre-author run
   snapshot (`corpus/live/r74-reviewer/pre-love-runs/love-20261014T160210Z/`,
   i.e. 16:02Z / 13:02 local, pre-commit, from the
   r73 blob — `pre-snapshot/love_battery.py` sha256 == `1275746:` blob) had
   `cases=19 pass=19 fail=0`; my post-author run has the same 19 keys, same
   `observed`/`verdict`; the only deltas are timing jitter inside the pinned
   bounds (`dt_mean_ms 1.045→1.044`, `l2_wait_ms 120.52→120.45`, …), all PASS.

3. **IW ordering.** In `main()`, the splice loop is at `:435` and the IW loop
   at `:451` — interior-write cells spawn after every r70/splice cell. Within
   `IW_CELLS`, the two uncontained cells are the last two rows (indices 16, 17
   of 0..17: `bc_setpos_unp`, `bc_newbody_unp`), matching the brief's
   "fatal crash kills the probe early" constraint. Each cell is its own
   process (`main.lua` `IW_CELL`), so a fatal cell cannot truncate another.

4. **Parse/classify correctness vs raw stdout.** Every exact-string pin in
   `IW_CELLS` was checked to appear verbatim in that cell's raw
   `iw-<cell>.stdout.txt`, and the battery's parser (`parse_iw`, `:251`)
   reproduces it — pin-vs-raw mismatch list is empty. Direct parse of the raw
   lines confirms the space-tolerant boundary rule works on the hard cases:
   `cb_setpos.err` parses to exactly `Box2D assertion failed:
   m_world->IsLocked() == false` (stops before `pos_after=`), and
   `ext_destroy.b1pos_after` to `ERR:Attempt to use destroyed body.`. I
   hand-classified all 18 raw receipts; the classes match the battery's
   `observed` in every case (baseline captured; 3 ext applied; bc/pre/post
   setpos+newbody+setactive refused; bc/pre/post destroy deferred;
   pre_contactmask + bc_setvel applied; 2 unp fatal). Key raw witnesses:
   `cb_setpos ok=false err=Box2D assertion failed: m_world->IsLocked() ==
   false pos_after=400,520.1500244140625` (unchanged pose) vs
   `ext_setpos ok=true … pos_after=1234.5,678.9000244140625`;
   `cb_destroy ok=true err=nil alive_in_cb=400,520.1500244140625
   count_after=4` then `after_update count=3 b1pos=ERR:…` with
   `evpin cb=ec locked=false step=73` emitted *before* the `after_update`
   line (i.e. during `world:update`, `main.lua:220`); `cb_contactmask
   ok=true isEnabled_after=false isTouching=true` with `b1vel` unchanged
   (`0,763.8724365234375`) vs the refused cells' `0,-611.09796142578125`.

5. **Partial-capture detection is structural, not advisory.** `iw_classify`
   (`:288`) was imported from the landed file and driven with synthetic
   capture shapes: fire-present + no CELL_DONE + rc=0 → `anomaly`; + rc=1
   without assert text → `died`; no fire line → `nolaunch`; timeout →
   `timeout`; `destroy` ok without the drain witness → `anomaly`; a survived
   `_unp` cell (CELL_DONE, mutation applied) → `anomaly`; `api_missing` →
   `anomaly`. None of these can equal a contained expected class, and the
   per-cell `done`/`rc` pins would also fail — a truncated receipt is a
   measured FAIL with the detail in `reasons`, never a silent pass. Manual
   launches confirm the endpoints: `IW_CELL=bc_setpos_unp` → rc=1, stderr
   0 bytes, `CELL_DONE` absent, `Error: main.lua:91: Box2D assertion failed:
   m_world->IsLocked() == false` on stdout; `bc_setpos`/`baseline` → rc=0,
   `CELL_DONE` present.

6. **Determinism / honest saturation claim.** Concatenated
   `iw-*.stdout.txt` sha256 = `58af4e7e1bc6c754de7e3ad8dd55d75b1d1a05f1fbf8
   31968092aeb116801f86` in *both* of my run dirs — byte-identical to the
   author's four reps (`corpus/live/r74-author/runs/*`), i.e. 6 identical
   reps. The author's quoted hash is verified exactly; the "4 stable reps"
   claim is accurate (and now stronger).

7. **Controls untouched.** `pygame_battery.py`, `pygame_probe.py`,
   `love_probe/main.lua`, `love_probe/conf.lua` blobs identical between
   `1275746` and `ae6cb16`; numstat lists only the 4 files above. One
   canonical runtime: all launches go through the single `args.love` binary
   (`:399-400`); no alternate judge or fallback runtime was introduced.

8. **Cross-seat corroboration checked, not trusted.** The r74-scout's
   independent probe receipts (`corpus/live/r74-scout/cells/*.r1.stdout.txt`,
   `R74X` prefix, 2 reps) are payload-identical to the landed battery's 18
   cells for every shared cell; the only delta is that the landed probe emits
   two extra header lines (`viability …`, `built …`). The author's
   "identical modulo prefix" claim is if anything under-stated.

## Findings by severity

**No HIGH or MEDIUM correctness defect found.** The landed diff does what the
brief asked, and every load-bearing claim I could test reproduced from raw
stdout.

LOW-1 (documentation precision, `love_battery.py:31-33`) — the docstring says
`destroy()` is "drained **after** world:update with a synthesized EndContact at
locked=false". The receipts place the drain **inside** the `world:update` call:
`evpin cb=ec locked=false step=73` is emitted before the `after_update` line,
which `main.lua:222-224` writes only after `world:update(FIXED)` returns
(`main.lua:220`). The author's own report words it correctly ("drained inside
the update epilogue"); the battery docstring (`:32`) and the `iw_bc_destroy`
table comment (`:187`) mix the two. Suggest "drained inside the update
epilogue (after the locked step), observable only after `world:update`
returns". No behavior impact.

LOW-2 (hygiene, working tree not the diff) —
`corpus/fixtures/__pycache__/love_battery.cpython-314.pyc` (mtime 16:42Z /
13:42 local, i.e. after the 16:40:56Z commit) is untracked and **not**
gitignored (`git check-ignore` exit 1);
`corpus/live/.gitignore` only carries `runs/`. It was produced by importing the
fixture as a module (as sibling scratch drivers do), not by this commit — the
committed tree is clean (`git diff HEAD -- corpus/fixtures` empty). Flagging
only because a later `git add -A` report/integration commit would sweep a
bytecode artifact into a tracked fixture directory. Cheapest fix is
`sys.dont_write_bytecode = True` in the importing drivers or a `__pycache__/`
ignore entry; neither is this arm's obligation.

LOW-3 (pin referent, disclosed) — the destroy cells' extra witness
`evpin_ec_lck=false, evpin_ec_step=73` identifies the *first* EndContact in the
run; the probe does not tag which bodies a contact event involves, so "the
drain's synthesized EndContact for the destroyed body" is inference, supported
by the contrast with baseline (first ec at step 74, locked=true) and with the
refused cells (first ec 74). The deferred *class* itself does not depend on it
(`ok=true` in-callback + `count_after=4` + post-update `count=3` + `ERR:`
pose). The author disclosed this hazard; no change required.

LOW-4 (build-bound exact pins, disclosed) — `fire.step=73`, the `%.17g`
float32 poses, and baseline's `final.bc/ec/pre/post` are this-build-exact. A
different Box2D/love build could shift them while preserving classes. Useful
property verified by reading the classifier: the build dependence is *loud* —
if `b2Assert` were compiled out, refused cells would come back `ok=true` →
class `applied` ≠ `refused` → FAIL, and the `_unp` cells would reach CELL_DONE
→ `anomaly` ≠ `fatal` → FAIL. So the assert-on/assert-off build question is
answered by the class pins, not just by the report text.

## Residual risk and verification gaps

- Determinism is 6/6 identical on this host/build only; no second Box2D build
  or love version was exercised (the arm cannot, on this host).
- The fatal-class binding is by assert *content* (`assert_txt`) plus
  `fire.step=73`, not by source line; the raw traceback does carry
  `main.lua:91` / `main.lua:95`, but the battery deliberately does not pin
  those (path/build-bound). A hypothetical unrelated assert firing at step
  ≥73 in an `_unp` cell would still classify `fatal`; with the current probe
  the only assert source is the mutation itself, so this is theoretical.
- `iw_classify`'s `evpins` parameter is unused (dead parameter, `:288`);
  cosmetic only.
- Not in scope of this seat: the r70 CASES rows' physics/timing bounds were
  re-run but not re-derived; my claim is only that they behave as before.

## Recommendation (non-binding)

ACCEPT the landed diff `ae6cb16`. No correctness defect, no prior-row drift,
insertion-only confirmed at source/diff/behavior levels, partial-capture
detection verified by direct execution of the classifier, and the author's
determinism hash reproduced exactly from an independent replay. The four LOW
items are documentation/hygiene/theoretical and need no pre-merge change.

Evidence receipts: `corpus/live/r74-reviewer/runs/`,
`corpus/live/r74-reviewer/runs2/` (full battery verdicts + all
`iw-<cell>.{stdout,stderr}.txt`), `corpus/live/r74-reviewer/manual/`
(per-cell rc/stderr/CELL_DONE checks), `replay-stdout.txt`,
`replay2-stdout.txt`.
