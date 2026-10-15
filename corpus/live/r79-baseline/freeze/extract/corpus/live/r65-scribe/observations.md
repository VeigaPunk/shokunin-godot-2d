# r65 scribe — forged-REJECTION dual, independent measurement log

Host: devin. Date: 2026-10-14 (~02:25–02:50Z). Godot `4.7.2.stable.arch_linux.ed1daf0bf`,
Python `3.14.7`, Linux `7.2.3-arch1-3`, `/usr/bin/sh` children for synthetic arms.

## Extraction provenance

`drive_errforge.py` ast.get_source_segment-extracts `run_process` and
`classify_process` VERBATIM from `corpus/fixtures/run_battery.py` and execs them
(production code path, no transcription — the r61..r64 seat discipline).
Extraction ran against the pre-author-landing worktree file: recorded
`runner_sha256 = 66a18a0056aedbd6c99ed8637ed30d03a3404556ab49d05826e8c63f4fe1f07d`
— byte-identical to the r64-verified blob (r64 LOG: fix commit `5265da6`
landed blob `66a18a00`). Post-landing worktree sha is `1acbc73d…`; the four
extracted/edited functions' segment shas are IDENTICAL between HEAD and the
landed worktree blob (verified below), so the measurement applies unchanged.

Fixture: `proj/` is a two-file copy (`project.godot` +
`descendant_pipe_probe.gd`) — the tracked file's four arms preserved, five
scribe-owned arms added IN THE COPY ONLY (`--self-error`, `--errforge-release`,
`--errforge-hold`, `--errforge-quiet`, `--errforge-stderr`,
`--errforge-withhold`, `--errforge-script`). Error marker:
`ERROR: INJECTED_DIAGNOSTIC classification tripwire` (un-allowlisted for every
CASES row; no `SCRIPT ERROR:`/`Parse Error:` collision). The ppid gate is the
fixture's own `/proc/self/stat` reparenting gate — the write is provably
post-exit; `write_ppid` records the reparented ppid.

## Exact commands

```sh
cd ~/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r65-scribe
mkdir -p proj raw
cp ../../fixtures/project.godot proj/
# wrote proj/descendant_pipe_probe.gd (tracked copy + scribe arms) and
# drive_errforge.py
timeout 10 godot --headless --path proj --script res://descendant_pipe_probe.gd -- --self-error          # smoke: exit 0, MARKER+godot_pid+ERROR
timeout 10 godot --headless --path proj --script res://descendant_pipe_probe.gd -- --errforge-release    # smoke: post-exit ERROR+write_ppid=1573
python3 drive_errforge.py godot | tee run-matrix.stdout   # 148 gated+naive runs
sha256sum drive_errforge.py errforge-verdicts.json proj/descendant_pipe_probe.gd
```

## Measured matrix (full per-rep data: errforge-verdicts.json; raw/: per-run captured output)

### naive path — extracted `run_process` + `classify_process` (the CASES verdict path)

| arm | n | actual_exit | error | sig present | unrelated ERROR lines | verdict | classify_if_error_none |
|---|---|---|---|---|---|---|---|
| syn_genuine | 5 | 0 | None | yes | 0 | **True** | True |
| syn_self_error | 5 | 0 | None | yes | 1 | **False** | False |
| syn_errforge_release | 15 | 0 | None | yes | 1 | **False** ×15 | False |
| syn_errforge_quiet | 10 | 0 | None | yes | 1 | **False** ×10 | False |
| syn_errforge_hold | 3 | None | TIMEOUT 3.0s | yes | 1 | False | **False** (dual datum) |
| syn_errforge_stderr | 5 | 0 | None | yes | 1 | False | False |
| syn_errforge_withhold | 5 | 0 | None | yes (forged) | 1 | False | False |
| syn_script_errforge | 5 | 0 | None | yes | 1 (`SCRIPT ERROR:`-class) | False | False |
| syn_pre_error | 5 | 0 | None | yes | 1 | False | False |
| syn_sigforge_release | 5 | 0 | None | yes (forged) | 0 | **True** ×5 | True |
| godot_genuine | 3 | 0 | None | yes | 0 | True | True |
| godot_self_error | 3 | 0 | None | yes | 1 | False | False |
| godot_detach | 2 | 0 | None | yes | 0 | True | True |
| godot_errforge_release | 8 | 0 | None | yes | 1 | **False** ×8 | False |
| godot_errforge_quiet | 3 | 0 | None | yes | 1 | False | False |
| godot_errforge_hold | 2 | None | TIMEOUT 3.0s | yes | 1 | False | **False** |
| godot_errforge_stderr | 3 | 0 | None | yes | 1 | False | False |
| godot_errforge_withhold | 3 | 0 | None | yes (forged) | 1 | False | False |
| godot_errforge_script | 3 | 0 | None | yes | 1 (`SCRIPT ERROR:`-class) | False | False |
| godot_sigforge_release | 3 | 0 | None | yes (forged) | 0 | **True** ×3 | True |

### gated path — my while-live-gate replica (poll() primitive; error observation added)

| arm | n | marker obs | alive@marker | error obs | alive@error | err−death ms | gated_accept | inner classify |
|---|---|---|---|---|---|---|---|---|
| syn_genuine | 5 | ~0.5ms | True | — | — | — | True | True |
| syn_self_error | 5 | ~0.5ms | True | ~0.5ms | **True** | ~−0.7 | True | False |
| syn_errforge_release | 10 | ~0.5ms | True | ~1.2–1.6ms | **False** | +0.02…+0.39 | **True** ×10 | False |
| syn_errforge_quiet | 5 | ~0.5ms | True | ~1.2ms | False | +0.03…+0.10 | True | False |
| syn_errforge_hold | 2 | ~0.5–0.9ms | True | ~1.4–2.0ms | False | +0.2…+0.8 | True | False |
| syn_errforge_withhold | 5 | ~1.9–55ms | **False** | ~1.9–53ms | False | +34ish | **False** | False |
| syn_pre_error | 5 | ~0.8ms | True | ~252ms | **True** | ≈−1250 | True | False |
| syn_sigforge_release | 5 | ~1.3–1.8ms | False | — | — | — | False | True |
| godot_genuine | 3 | ~334–458ms | True | — | — | — | True | True |
| godot_self_error | 3 | ~311–457ms | True | same-chunk | **True** | ≈−67 | True | False |
| godot_errforge_release | 5 | ~323–458ms | True | ~427–561ms | **False** | +33.4…+35.3 | **True** ×5 | False |
| godot_errforge_quiet | 3 | ~322–387ms | True | ~426–490ms | False | +34.0…+34.9 | True | False |
| godot_errforge_hold | 2 | ~320–437ms | True | ~423–541ms | False | +32.5…+34.3 | True | False |
| godot_errforge_withhold | 3 | ~401–467ms | **False** | same-chunk | False | +34.3…+35.0 | False | False |
| godot_sigforge_release | 3 | ~401–420ms | False | — | — | — | False | True |

### CASES-field identity (the claim's core)

`godot_errforge_release` vs `godot_self_error` — identical on every
classification-visible field: `actual_exit=0, error=None, signature_present=True,
unrelated_error_lines=[ERROR: INJECTED_DIAGNOSTIC…] ×1, script_error_present=False,
verdict=False`. Output differs only in provenance lines: forged adds
`DESCENDANT_PIPE spawned_pid=N` + `DESCENDANT_PIPE_ERRFORGE write_ppid=N`
(=1573, the subreaper — kernel-corroborated on hold arms, `kernel_ppid ==
write_ppid != godot_pid`).

`godot_errforge_quiet` vs `godot_self_error`: `output_shape` (pid values
normalized) is **line-for-line identical** —
`[banner, '', MARKER, godot_pid=N, ERROR line]` — zero in-record provenance.
The claim's conceded "except withheld/ppid fields" is itself a courtesy echo:
drop it and nothing remains.

Counterparts: `godot_genuine`/`godot_detach` are the PASS shape the forged
record was flipped FROM; `godot_sigforge_release` is the r63 forged-PASS
record (True) — pairing it with `godot_errforge_release` (False) shows the
same ppid-gated descendant write accepted on one axis and rejected on the
other depending only on which marker it carries.

## Landed author diff (uncommitted at measurement finalize; `git status` ` M`)

`descendant_pipe_probe.gd` +35 (`--spawn-errforge-release`,
`--spawn-errforge-hold`, `--emit-errforge` push_error genuine control) +
`run_battery.py` +431 (`probe_descendant_error_spoof` + `errforge_run` /
`gated_errforge_run` dual-marker / `split_errforge_run`, 22 discriminations,
`stripped_classification` counterfactual). `run_process`/`classify_process`/
`classify_streams`/`classify_audio_process` segment sha256 identical
HEAD↔worktree (`88728b23/749fa060/a886968f/3a6bc0e8` prefixes). Classifiers
untouched — additive only, as constrained.

## Settled sibling receipts observed at finalize

- Reviewer fresh seven-flag **97/97**:
  `corpus/live/r65-reviewer/runs/20261014T022426865258Z/verdicts.json`
- Baseline frozen-archive seven-flag **97/97**:
  `corpus/live/r65-baseline/runs/20261014T022523005280Z/verdicts.json`
- Reports settled: `reports/round-65/r65-{baseline,reviewer}.md`
- Author post-diff battery IN PROGRESS (run dir `runs/20261014T023015140150Z`,
  no verdicts.json at ~02:50Z); pretree battery also in progress. Author
  receipt/discriminations `[pending]`.
