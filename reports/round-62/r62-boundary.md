# Round 62 — boundary recon: porting 3d's tree-timeout mechanism onto the 2d pipe-EOF surface

## Scope and method

LEAF boundary/revenger seat, scratch-only and report-only. I wrote only this
report and `.shokunin/game-dev-2d/corpus/live/r62-boundary/`. No tracked
fixture, runner, CASES row, lesson, LOG, or SCORECARD entry was touched; no
subagent dispatch; no git mutation.

Task (from the wave brief): measure in scratch what porting game-dev-3d's
verified tree-timeout mechanism
(`~/Projects/shokunin/game-dev-3d-shokunin/corpus/fixtures/run_battery.py`
`probe_tree_timeout`, lines 423–543) into 2d's `run_process` would change on
the pipe-EOF surface — (a) does 3d's approach kill the descendant group, and
(b) does it change classification of the r61 pipe-holding mutant — plus a
concrete port-diff sketch.

Method (same discipline as r61):
`corpus/live/r62-boundary/drive_port_recon.py` (sha256 `fed3033a…`)
`ast.get_source_segment`-extracts `run_process` and `classify_process`
**verbatim** from the tracked `corpus/fixtures/run_battery.py` and execs them
(V0 baseline = production code path), then runs the r61 `tree_probe.gd`
fixture (byte-identical copy, sha256 `ceec716e…`) under three scratch port
variants. All four arms × four variants ran on this host; receipts in
`port-recon-verdicts.json` (sha256 `6869b88b…`), raw captures under `raw/`.

**Provenance note — mid-flight sibling diff (same as r61).** At probe time
`HEAD` runner sha256 is `d705bca719fcdf24009f2302866ecf8066d49baa2adbc81dbd044c77b3bc5019`;
during this wave the r62 coverage seat landed its tracked move in the working
tree (runner now `0c4c9bee7056…`, `git diff HEAD`: +142 −0 — CASES row
`descendant_pipe_detached_control`, meta row `probe_descendant_pipe_eof`,
new fixture `descendant_pipe_probe.gd`). Verified via the same `ast`
extraction: `run_process`, `classify_process`, `classify_streams`,
`classify_audio_process` are **byte-identical** between `HEAD:` and the
working tree — additive-only outside those functions, so every number below
characterizes both revisions.

Environment: Godot `4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`),
Linux `7.2.3-arch1-3 x86_64`, Python `3.14.7`.

## Mechanism diff (as measured, not assumed)

| | 2d `run_process` (r62, sha d705bca7) | 3d `probe_tree_timeout` (sha b4b31499) |
|---|---|---|
| spawn | `subprocess.run(capture_output=True, text=True, timeout=T)` | `Popen(stdout=PIPE, stderr=PIPE, start_new_session=True)` |
| on timeout | CPython POSIX: `kill()` = SIGKILL to **direct child pid only**, `wait()`, re-raise | verify one witness via pidfile+`/proc` (ppid==child, pgid==self, cmdline tokens), `os.killpg(child.pid, SIGKILL)`, **SIGTERM the verified witness BEFORE draining**, then bounded second `communicate(3)` |
| descendant handling | none — orphans under `systemd --user` (pid 1573) | one identified detached witness, SIGTERM→3s grace→SIGKILL |
| return shape | `(out+err, None, "TIMEOUT after T seconds")` | `actual_exit=None`, `cleanup_exit` recorded separately |

3d's own LOG records the load-bearing falsification (round 5): a Godot
`OS.create_process` witness measured `PGID=SID=own pid` — the "descendant in
the child's process group" premise was **false**, so `killpg` alone could
never claim descendant cleanup; and their first implementation hung waiting
on `communicate` before terminating the pipe-holding witness — corrected to
kill the witness *before* draining. My measurements below re-derive both.

## Q1 — does 3d's approach kill the descendant group? **No.**

**S0 blast-radius control** (no `start_new_session`): Godot child spawned
under plain `Popen` gets `pgid=801478` == driver's own `pgid=801478`
(`s0_no_new_session` record). A `killpg` patch without `start_new_session`
SIGKILLs the harness's own group — the session isolation is a *required*
companion, not an optional extra.

**Descendants escape the group.** Every `OS.create_process` descendant
observed is its own session+group leader at timeout time — e.g. V1/hang:
godot `pgid=802736` (=godot pid, session isolated by `start_new_session`),
descendant `sh` pid 802774 `pgid=sid=802774`. Under V1 (minimal port:
killpg child group on timeout) the `hang` arm sent `killpg`, godot died
(`godot_alive_at_return=False`, cleanup_exit path), and **both** the `sh`
and its nested `sleep` survived — `descendant_alive_at_return=True`, orphaned
to ppid 1573, outlived-file landed +0.5s after return.

**Corroborating receipt — 3d's own runner on this host:**
`python3 …/game-dev-3d-shokunin/corpus/fixtures/run_battery.py --only
navagent3d_next --probe-tree-timeout --runs
corpus/live/r62-boundary/runs` → PASS;
`runs/20261013T234321317706Z/tree-timeout-verdicts.json` (sha256
`6b7212db…`): witness `pgid=782947`=own pid, `ppid=782714`=live godot,
`witness_verified=true`, `cleanup_exit=-9` (group kill got godot),
`witness_cleanup="SIGTERM to verified detached witness"`, `witness_gone=true`.
The descendant dies by **explicit verified identity kill**, not the group
kill — and only because the child was still alive at timeout (ppid check).

**Where 3d's verify rule fails for 2d's mutant**: for the `hold` arm (child
pre-exits ~0.4s), the descendant is already reparented at timeout —
measured `ppid 1573 != child 802287` → `witness_verify_3d_rule=false`. A
verbatim port of their witness protocol cannot even *identify* the orphan
in the child-dead case, let alone kill it.

## Q2 — does the port change classification of the pipe-holding mutant? **No — unless you also change the return shape; then it's an explicit choice.**

Full 4×4 matrix in `port-recon-verdicts.json`; condensed:

| variant | arm | exit | error | elapsed | classify (verbatim `classify_process`) | descendant |
|---|---|---|---|---|---|---|
| V0 stock | clean | 0 | None | 0.426s | True | — |
| V0 stock | hold | None | TIMEOUT 3.0s | 3.002s | **False** | alive, orphaned (file +4.5s) |
| V0 stock | detach | 0 | None | 0.554s | True | alive, silently leaked |
| V0 stock | hang | None | TIMEOUT 3.0s | 3.006s | **False** | alive, orphaned (file +2.5s) |
| V1 minimal port | hold | 0 | TIMEOUT + drain-exceeded 2.0s | **5.013s** | **False** | still alive+orphaned; killpg never sent (child dead) |
| V1 minimal port | hang | None | TIMEOUT + drain-exceeded | 5.013s | **False** | godot −9 via killpg; `sh`+`sleep` survive (own group) |
| V2 +pipe-holder kill | hold | 0 | TIMEOUT 3.0s | **3.011s** | **False** | holders [802934, 802946] SIGKILLed; file never landed |
| V2 +pipe-holder kill | hang | **−9** | TIMEOUT 3.0s | 3.012s | **False** | group killed + holders [803485, 803486] killed; tree reaped |
| V3 attributed | hold | **0** | "TIMEOUT (pipe held after child exit 0)" | 3.010s | **False** (error non-None); **True if error=None** | holders killed |
| V3 attributed | hang | −9 | "TIMEOUT (child alive at bound; group killed)" | 3.011s | **False** | holders killed |

Reading:

- **Minimal port (V1) is strictly worse**: same False verdicts, +2s wall on
  held pipes (drain grace burned waiting for a pipe the orphan still holds),
  same orphan. `communicate`'s EOF wait is untouched by group isolation.
- **The leak is fixable without fixture cooperation**: scanning
  `/proc/*/fd` for holders of the parent's own pipe inodes found *both* the
  `sh` descendant and its nested `sleep` (V1/V2/V3 `pipe_holders` records) —
  a strictly wider net than 3d's single-verified-witness (it catches
  grandchildren and post-reparent orphans; identity = "holds the pipes we
  created"). Killing holders before the drain returns EOF instantly:
  `drain_elapsed=0.0s`, `cleanup_exit=0`/`-9`.
- **Classification of the hold mutant stays False** under every variant that
  keeps `error` non-None. The V3 measurement shows the flip exists as a
  *decision*: `classification_if_error_none=True` — the child really did
  exit 0 with its marker emitted; returning `error=None` would admit it.
  Porting is what *makes the choice available* — Popen exposes
  `child_precipitated_exit=0` (poll() reaps the dead child inside the
  TimeoutExpired handler), which stock `subprocess.run` never surfaces
  (`actual_exit=None` on every timeout, origin-blind as r61 noted).
- **`subprocess.run` + `start_new_session=True` alone is a no-op** on this
  surface (measured: hold arm → TIMEOUT at 3.003s, descendant alive) — its
  POSIX timeout path still kills only the direct pid and still awaits EOF.
- **The `detach` leak is invisible to all four variants**: an fd-detached
  descendant holds no pipes, so the holder scan can't see it and nothing
  times out. Leak detection for that arm needs a different mechanism —
  retained UNKNOWN.

## Concrete port-diff sketch (additive, field-stable)

Goal: keep every observed verdict byte-stable (all 92 rows + the r62
pipe-EOF rows) while reaping the timeout-path tree. The *only* observable
field a port may change without drifting prior receipts is nothing —
so preserve the return contract exactly:

```python
def run_process(command, timeout_seconds, env=None):
    if os.name != "posix":
        ...existing subprocess.run path...               # unchanged fallback
    proc = subprocess.Popen(command, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True,
                            env=env, start_new_session=True)   # REQUIRED
    try:
        out, err = proc.communicate(timeout=timeout_seconds)
        return (out or "") + (err or ""), proc.returncode, None
    except subprocess.TimeoutExpired as exc:
        output = <exc.stdout/stderr decode, same as today>
        if proc.poll() is None:                    # child alive: kill group
            try: os.killpg(proc.pid, signal.SIGKILL)
            except OSError: pass
        for pid in _pipe_holders(proc):            # /proc fd-inode scan,
            try: os.kill(pid, signal.SIGKILL)      # self+child excluded
            except OSError: pass
        try:
            out2, err2 = proc.communicate(timeout=3)   # bounded drain
            output += (out2 or "") + (err2 or "")
        except subprocess.TimeoutExpired:
            for s in (proc.stdout, proc.stderr):       # release our ends
                try: s.close()
                except OSError: pass
        return output, None, f"TIMEOUT after {timeout_seconds} seconds"
        #   ^ keep None + identical error string: verdicts and the 7-field
        #     tuple stay byte-stable; attribution lives in internal/meta
        #     fields only (e.g. proc.poll() at timeout == 0 → pipe-held case)
```

Measured deltas this sketch produces vs stock: hold/hang arms return at the
bound (~3.0s, not +grace), orphan reaped instead of leaked; `clean`/`detach`
paths and all classifications unchanged. Optionally expose
`child_precipitated_exit` to meta rows (the new `probe_descendant_pipe_eof`
already computes it by hand); do **not** put it in `actual_exit` — a
`None → -9` change on the seeded `timeout` rows would drift prior receipts.

Port caveats measured or carried from 3d's record: identity strings in
descendant cmdlines break under relative `--runs` (3d r69 saw the FAIL —
resolve to absolute); non-POSIX/no-`/proc` hosts need the gated fallback; the
pipe-holder scan races a holder that exits between scan and kill
(ProcessLookupError → skip, already handled); nothing on this surface
detects an fd-detached orphan (detach arm).

## UNKNOWNs / retained caveats

- Single host, bound 3.0s/drain 2.0s, n=1 per variant×arm — the failure
  modes are mechanism-determined (session leadership, EOF semantics), but
  timings are host-specific.
- `verify_3d_rule` was evaluated at return time; for `hang` 3d's own receipt
  shows it verifies while the child lives — my records show only that it
  *cannot* verify once the child pre-exits (hold arm, ppid already 1573).
- The scan kills anything holding the pipes we opened — correct for a
  per-case serial battery; a hypothetical concurrent writer sharing our fds
  would be killed too (none exist today).
- Not probed: `OS.execute` blocking paths, exported builds, >2 depth chains,
  Windows/macOS, pidfd-atomic ownership.

## Artifact inventory (`.shokunin/game-dev-2d/corpus/live/r62-boundary/`)

- `drive_port_recon.py` sha256 `fed3033a…`; `proj/tree_probe.gd` `ceec716e…`
  (verbatim r61 probe), `proj/project.godot` `8de8b3af…`.
- `port-recon-verdicts.json` `6869b88b…` (16 arm×variant records + S0
  blast-radius control); raw captures `raw/V{0..3}_*/*.stdout`;
  `runs/20261013T234321317706Z/` = 3d runner's own `--probe-tree-timeout`
  corroborating PASS (`tree-timeout-verdicts.json` `6b7212db…`,
  `verdicts.json` `a88fb218…`).
- `hold.descendant-outlived`, `detach.descendant-outlived` — deferred writes
  landed by orphaned descendants under the non-killing variants (V0 series,
  V1, and the `start_new_session`-only control); V2/V3 killed the holders
  before their writes could land (their `descendant_file_landed=false`).

No commit, no tracked-fixture mutation, no LOG/SCORECARD write; any runner
change belongs to a later executor + named non-author replay.
