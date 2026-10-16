# r94-verifier receipts — independent verification of `c7228893`

Seat `VERIFIER` (g2d lane r94, independent non-author) | host **devin** |
Godot `4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, `--headless`,
default 60 tps), Python 3.14.7, 32 cores. Target commit
`c7228893434ad70674791eda52794e96369a6744` (r94 author). Report:
`reports/round-94/r94-verifier.md`.

All paths below are relative to `corpus/live/r94-verifier/`.
`manifest.sha256` covers every evidence file (432 entries, `sha256sum -c`
rc=0); `MANIFEST-SCOPE.txt` records the excluded regenerable scratch families.

## Freeze of the committed bytes

| artefact | path | note |
|---|---|---|
| extracted committed subtree | `freeze/corpus/fixtures/` | `git archive c7228893 corpus/fixtures` |
| blob identity | `freeze/blob-identity.txt` | 81/81 `git hash-object` == `git ls-tree -r c7228893` |
| fileset | `freeze/fileset-git.txt`, `freeze/fileset-extract.txt` | 81 == 81 |
| pins | `freeze/sha256-pins.txt` | `particles_lattice.gd` `0701e813…c00a9` (763 lines) = author pin; `run_battery.py` `2b1f4df5…4238` |
| launch scratch project | `freeze/launch-scratch-project.godot.txt` | rep2 scratch `project.godot`: no `physics_ticks_per_second` |

## Battery runs on the frozen committed harness (`freeze/…/run_battery.py`)

| rep | run dir | log | verdict | r94 rows | r94 gate |
|---|---|---|---|---|---|
| rep1 | `runs/20261016T063334001914Z/` | `battery1.log` | FAIL 314 rows (5 pre-existing) | 19/19 PASS | True |
| rep2 | `runs/20261016T064310819140Z/` | `battery2.log` | **PASS 314/314** | 19/19 PASS | True |
| rep3 | `runs/20261016T065158572001Z/` | `battery3.log` | FAIL 314 rows (2 pre-existing) | 19/19 PASS | True |

Load stamps: `battery{1,2,3}.start/.end`, `battery{2,3}.load.start/.end`.
Author runs re-verified: `../../runs/20261016T055703426158Z/`,
`../../runs/20261016T060430025246Z/` (both PASS 314/314, gate True).

## Probes (scripts + receipts)

| receipt | script | result |
|---|---|---|
| `probes/audit-committed.txt` | `probes/audit_committed.py` | CASES 307; r94 at 284–302; 19/19 == scout `ROWS_PREFIX`; gate text; pin shapes |
| `probes/signature-coverage.txt` | `probes/signature_coverage.py` | 618 canonical receipts → EXACT 90 / TAIL 525 / MISS 0 / REJECT 3 (pre-fold ff30 `cpu_pause`, explained); +3 foreign-seat runs 57/57 PASS |
| `probes/fresh-arms.txt` | `probes/fresh_arms.py` | 57/57 PASS (19 arms × 3 reps), rc=0, 0 B stderr; receipts `arms/<case>.rep{1,2,3}.{out,err,rc}`, `arms/summary-*.json` |
| `probes/discrimination.txt` | `probes/discriminate.py` | 111/111 pinned mutations reject; 32/32 tail controls admitted; global axes 19/19 ×3 |
| `probes/contam-tautology.txt` | inline (receipted) | `cpu_contam` tail mutation to a never-fires world ADMITTED; `n_never=2` load-bearing; 25/25 receipts carry the measured tail |
| `probes/gate-mutant-build.txt`, `probes/gate-mutant-diff.txt` | `probes/make_gate_mutant.py` | one injected dead r94 entry (exact diff vs frozen harness) |
| `gate-probe/battery.log`, `gate-probe/runs/20261016T065158659995Z/verdicts.json` | mutant run | r94 gate **False**, `dead_entry_count=3`, `r94_particles_cpu_never` still PASS |
| `probes/ff30-fold.txt`, `ff30-probe/*.rep*.{out,err}` | `probes/ff30_fold.py` | boundary ff30 values re-derived admit; committed fixture ff30 3/3 PASS; frozen probe ff30 3/3 REJECT |
| `probes/tps-windows.txt`, `tps-probe/tps-windows.json`, `tps-probe/{default,tps30,tps120}-<arm>.{out,err}` | `probes/tps_windows.py` | default tps=60 all 19 PASS; tps30 10 FAIL; tps120 11 FAIL |

## Stream hygiene

523 file receipts carry `.err`; total stderr bytes **0** (scout 143 +
boundary 323 + fresh 57). The 95 battery row-instances across the five
canonical runs carry no ERROR/WARNING line.

## Excluded from the manifest (regenerable)

`runs/*/scratch/**`, `runs/*/missing-preset-scratch/**`, `runs/*/xdg-data/**`,
`gate-probe/runs/*/…`, `gate-probe/fixtures/**` (mutant copy — delta receipted
in `probes/gate-mutant-diff.txt`), `tps-probe/proj-*/**`, `arms/scratch-*/**`,
`ff30-probe/scratch-*/**`, `**/__pycache__/**`.
