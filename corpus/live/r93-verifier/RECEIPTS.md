# r93 verifier receipts — independent non-author verification of `4b75151`

Seat `VERIFIER` (g2d lane r93) | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, headless, 60 tps,
GodotPhysics2D), Python 3.14.7, 32 cores, foreign loadavg 49–85 with 48 foreign
`yes` hogs during the battery window (none mine).

Report: `reports/round-93/r93-verifier.md`. Author report:
`reports/round-93/r93-author.md`; inputs `reports/round-93/r93-scout.md`,
`reports/round-93/r93-boundary.md`.

`manifest.sha256` covers every file below except the declared scratch trees
(scope header in line 1): `freeze/x/**` (frozen `git archive HEAD
corpus/fixtures` extraction, 80 files), `arms/proj/**` (scratch project copy),
`gate-probe/**` (mutant harness tree + run scratch), `runs/*/scratch/**`,
`runs/*/xdg-data/**`, `runs/*/missing-preset-scratch/**`.

| artefact | path |
|---|---|
| freeze record (HEAD, rc, fileset, blob identity) | `freeze/freeze-time.txt` |
| committed fixture blobs vs extraction (80/80 OK) | `freeze/blob-identity.txt` |
| fixture sha256 (anim_lattice / r93b_anim / run_battery) | `freeze/fixture-shas.txt` |
| fileset diff (empty = 0 diffs) | `freeze/fileset-diff.txt` |
| committed harness static audit | `probes/audit_committed.py`, `probes/audit-committed.txt` |
| provenance (byte-copy chain, scout ROWS, commit scope) | `probes/provenance.py`, `probes/provenance.txt` |
| battery reps 1–5 on the frozen bytes | `battery{1..5}.log`, `runs/*/verdicts.json` |
| fresh arm sweep (17 arms × 3 reps) + classification | `probes/fresh_arms.py`, `probes/fresh-arms.txt`, `arms/*.{out,err,rc}` |
| author custody (re-classification, proj identity, manifest) | `probes/author_custody.py`, `probes/author-custody.txt` |
| signature coverage over committed corpora | `probes/signature_coverage.py`, `probes/signature-coverage.txt` |
| law re-derivation (crossfade / overshoot / N−1 / DEFERRED) | `probes/verify_laws.py`, `probes/laws.txt` |
| independent N−1 + DEFERRED probe (outside the fixtures) | `probes/r93v_probe.gd`, `probes/nminus1/*.{out,err}` |
| discrimination matrix (120 mutations + 3 global axes) | `probes/discriminate.py`, `probes/discrimination.txt` |
| mode-tail isolation (pinned vs mode fields) | `probes/mode_tail_isolation.py`, `probes/mode-tail-isolation.txt` |
| `--fixed-fps` stabilizer measurement | `probes/ff_stabilizer.py`, `probes/ff-stabilizer.txt` |
| battery identity/stability across reps | `probes/prior_identity.py`, `probes/prior-identity.txt` |
| r93 floor gate mutant run | `probes/gate_mutation.py`, `probes/gate-mutation.txt`, `gate-probe/mutant.log` |
| manifest generator | `probes/make_manifest.py` |

All artefacts are untracked (`corpus/live/**` except the `runs*/` gitignore);
**no tracked writes, no commits**.
