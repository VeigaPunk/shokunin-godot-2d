# r86 simplifier — YAGNI fold of phys2d_backends.gd (byte-identical proof)

Seat `SIMPLIFIER` | round 86 | host **devin** | Godot `4.7.2.stable.arch_linux.ed1daf0bf`
headless (`/usr/bin/godot`), Python 3.14. Scope: the r86 diff only
(commit `7ae7083` — `corpus/fixtures/phys2d_backends.gd` +8 CASES rows).
Committed fixtures **untouched**; the fold ships as artifacts under
`corpus/live/r86-simplifier/`.

## Deletions (3 folds, −4 net lines: 505 → 501)

| # | folded hunk | class | why dead |
|---|---|---|---|
| F1 | `_boot` return dict: `"out": out_t` and `"out_bytes": get_file_as_bytes(out_f).size()` removed; doc comment `{rc, out, err, out_bytes, err_bytes, fields, at}` → `{rc, err, err_bytes, fields, at}` | dead dict keys | no caller reads `r["out"]`/`r["out_bytes"]`; the key set was only doc'd. `out_t` stays (fields parser reads it). Also drops a redundant `get_file_as_bytes` syscall |
| F2 | `var drop: Array = []` + `OS.execute("/bin/sh", …, drop, …)` → `OS.execute("/bin/sh", …, [], …)` | unused var | `drop` is the OS.execute output sink; child output is redirected to files, so the array is written once and never read. Literal `[]` is the same call |
| F3 | child script: `'_deferred_g()'` call site inlined to its one-line body `'_gate["G"] = _dss_state()'`; the 2-line `func _deferred_g` definition deleted | dead single-call helper **and stale name** | the helper was invoked synchronously — never deferred, despite the name and the author's "deferred continuation" label for position G. Inlining preserves the exact fetch point/timing |

## Rejected candidates (unreachable/dead-looking but kept — strict-Pareto)

| candidate | verdict | rationale |
|---|---|---|
| parent `match` `_:` + `_fail("unknown_arm")` | **kept** | unreachable under the battery, but deleting it converts a typo'd arm from `FAIL … quit(1)` into a silent SceneTree idle-hang — debuggability axis regresses for ~3 lines |
| child `match` `_:` + `print("R86C unknown=1")` | **kept** | same class: malformed `--mode` would quit rc=0 with no marker in the capture |
| `--keep` / `_keep` / `_cleanup` early-return | **kept** | documented operator affordance (header: "receipt harvest"); an interface, not dead weight — never exercised by CASES but that's its purpose |
| child `print("R86C done=1")` in `_m_manager` | **kept** | unread by the parent, but it is the loop-completion witness in the child `out.txt` capture — fixture design says captures are the forensic artifact; removing it thins capture completeness |
| `_m_dummyhang` trailing `print(collider_ok)` / `quit()` | **kept** | unreachable *under Dummy* only; they are the intended-completion path that makes the hazard legible, and `quit()` is the correct termination if a backend ever resolves `hit.collider` |
| `_boot` `rc` fallback `-999` | **kept** | defensive parse for a missing `rc.txt` (e.g. `timeout` binary absent) — the only signal distinguishing wrapper failure from child rc |

## Method & evidence

Launch shape replicated verbatim from `run_battery.py` `execute()`:
`godot --headless --path <scratch> --script res://phys2d_backends.gd -- --arm=<arm>`,
`timeout_seconds = 8`, `env = None`. Scratch = full `corpus/fixtures` copy minus
`run_battery.py`/`__pycache__`/dotfiles (the battery's own copy rule), with the
variant file placed as `phys2d_backends.gd`. Pins pulled from `CASES` via `ast`,
never retyped. Streams captured **separately** (stronger than the battery's
merged capture) and classified with a verbatim copy of `classify_process`.

**Result: PROVEN.** 32 runs (8 arms × 2 variants × 2 reps, interleaved):
all `rc=0`, all `stderr` = 0 B, all `verdict=PASS` (pinned signature present in
output), and **16/16 base↔folded pairs byte-identical** on `(rc, stdout sha256,
stderr sha256)`. Max wall 4.19 s vs the 8 s bound. The 8 emitted `PASS` M-lines
are identical across variants — byte-equal to the committed `CASES` literals.

Artifacts: `corpus/live/r86-simplifier/` —
`base/phys2d_backends.gd` (byte-copy, sha256 `dc95fce3…`),
`folded/phys2d_backends.gd` (sha256 in `proof.json`), `fold.diff`,
`run_arms.py` (reproducible driver), `proof.json` (full rows + shas),
`proof-table.md`, `out/<variant>/<arm>.rep<N>.{stdout,stderr}` raw captures,
`out/scratch-{base,folded}/` the two scratch projects.

## Reference provenance

No `lsp` device/language server is available on this substrate for GDScript —
recorded as unavailable; caller analysis used text grep. `"out"`, `"out_bytes"`,
`var drop`, and `_deferred_g` have zero readers/splicers outside the fixture
(repo-wide grep; hits under `corpus/live/` are frozen seat byte-copies, not
callers). Runtime equality — not grep — is the load-bearing proof here.

## Tradeoffs / notes

- `corpus/live/r86-critic/forges/make_forges.py` string-splices on
  `'\t_deferred_g()',` **in its own copies**; if this fold were ever adopted
  upstream, that splice anchor disappears. Artifacts-only delivery → no action
  needed now; flagged for whichever seat might land the fold.
- The comment "drop test" at line ~174 refers to the physics drop measurement,
  unrelated to the removed `drop` sink var; intentionally left.
- Axes: weight −4 lines / −1 syscall / −1 indirection and one stale name
  removed; behavior, pins, timing, captures, and debug affordances all
  preserved. Strict Pareto.
- Shared tree verified: `git status` clean for `corpus/fixtures/` (pre-existing
  `__pycache__` .pyc only, present before dispatch); committed
  `phys2d_backends.gd` sha256 unchanged `dc95fce3…`. Nothing committed.
