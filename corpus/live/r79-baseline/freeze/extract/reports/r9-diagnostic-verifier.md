# Round 9 diagnostic verifier — independent replay

I acted as the named non-author verifier. I did not delegate, commit, push, or change engine/editor source. The only repository file I wrote is this report.

## Replays and raw evidence

1. `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error` exited 0. Godot reported PASS for all 27 original cases, including both opt-in mutants. Four additional diagnostic probes also PASS; the JSON contains 31 records total. The four probe `clean_classification` values are true, while appended-error and exercised same-line spoof classifications are false. Each original case record has its actual captured Godot output in `output`; the probe records retain the original and modified output lines separately.
   - Raw JSON: `.shokunin/game-dev-2d/corpus/live/runs/20261012T172538827146Z/verdicts.json`
   - Godot: `godot`; payload overall verdict: `PASS`; `probe_failing: true`.
   - Export readiness: exit 0; real output includes `[ DONE ]`/`savepack`; executable was 73,703,800 bytes (SHA-256 `1a291d3d15e4180b60b0af96cf6458f11fe143636d76575ddf1e23d1a3f24f2e`). Products were `fixture.pck`, `fixture.sh`, and `fixture.x86_64`; `artifacts_deleted: true`.
   - Missing preset: actual exit 1, expected exit 1; exact expected diagnostic appears in captured output and `out` remained empty.
   - The exported executable is scratch evidence only; it was deleted after inventory.

Probe details: successful export, broken-scene mutant, and removed-collision mutant each reject an appended unrelated `ERROR:` and both same-line prefix/suffix spoofs. Missing-preset export rejects the appended diagnostic and same-line suffix spoof. In every probe the real captured output classifies cleanly first. The classifier helper reused by mutant probes is `classify_mutant`; the export paths use their `classify_export` helpers, each calling production `classify_process`.

2. `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --fault-injection` exited 0 with overall meta verdict PASS. The clean expected-negative control is PASS; injected hang and unrelated-error controls are inner FAIL as expected. The hang timed out after 0.25s with actual exit null.
   - Raw JSON: `.shokunin/game-dev-2d/corpus/live/runs/20261012T172538827168Z/fault-verdicts.json`

## Branch-bypass sabotage

I copied the fixtures to `/tmp/r9-sabotage-oh0l_1bf/fixtures` and changed only that scratch copy of `run_battery.py` so `classify_process` accepts every `ERROR:` line (the unrelated-error filter is disabled). I reran the full `--probe-failing --probe-unrelated-error` command against that copy. The command exited 1 and battery meta verdict was FAIL. All four diagnostic probe records became FAIL: clean classifications remained true, while appended and injected same-line classifications became true, violating each probe's required rejection. This confirms those probe meta verdicts fail when the shared classifier is sabotaged, rather than bypassing the altered classifier. Scratch sabotage JSON: `/tmp/r9-sabotage-oh0l_1bf/runs/20261012T172619386399Z/verdicts.json`.

## Integrity and scope

I SHA-256 hashed all 37 tracked paths in `corpus/fixtures` before and after replay (the 36 fixture files plus `run_battery.py`): zero changed hashes. No seeded fixture or runner mutation was made for the sabotage; it remained under `/tmp`.

Qualification: the unrelated diagnostics in the opt-in probes are edits to captured output strings, not errors emitted by a real Godot process. These runs establish that the tested classifier branches reject appended and same-line `ERROR:` text while accepting their clean captured outputs; they do not establish end-to-end handling of a Godot process that actually emits such a fault, nor universal diagnostic cleanliness.
