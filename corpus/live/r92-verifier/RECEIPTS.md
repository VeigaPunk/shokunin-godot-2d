# r92 verifier — receipts index

Seat `VERIFIER` (g2d lane r92, independent non-author), gate on committed
**`5900431`** (`r92 author: 14 tilemap rows (272 total) — nav 2-payload envelope
(boundary falsification folded), nullts SIGSEGV armed rc=-6, tombstone encoding;
272/272 x2`). Host **devin**, Godot `4.7.2.stable.arch_linux.ed1daf0bf`
(`/usr/bin/godot --headless`, GodotPhysics2D, 60 tps), Python 3.14.7, 32 cores.

**No tracked write, no commit.** Every artefact below lives under
`corpus/live/r92-verifier/` (untracked) except the report
`reports/round-92/r92-verifier.md` (new, untracked at write time).

**Frozen probeParent.** Exactly one read-only `ufo-labrat` (agent `9c32ddd9`)
was dispatched with one bounded static hypothesis (four clauses: per-arm
signature field-completeness, nav envelope shape, nullts last-emission/line-927,
no post-`_pass()` emission). It had **no exec tool**, wrote nothing, spawned
nothing; all four clauses returned **CONSISTENT** with line-cited evidence. No
second dispatch.

**`lsp` disclosure.** No `lsp` device and no GDScript language server is exposed
to this seat; every semantic check is an AST/static read of the committed bytes
plus fresh-process execution — the recorded fallback. The change is one new
fixture file plus an insertion-only harness block (no renames), so no
symbol-aware operation was possible or required.

## Layout

| artefact | path | notes |
|---|---|---|
| frozen extraction of `5900431` (`corpus/fixtures`) | `tree/` | `git archive HEAD corpus/fixtures`; 1.5 M; excluded from the manifest (prunable) |
| freeze evidence | `freeze/` | `fileset-diff.txt` (0 lines), `blob-identity.txt` (78/78 git-blob sha1 match), `content-diff.{err,rc}`, `fixture-shas.txt`, `scout-to-committed.txt` (five-way byte identity), `concurrent-edit.txt` (foreign r93 worktree edit, additive) |
| battery runs (5) | `runs/<stamp>/verdicts.json` | rep1 271/272, rep2 270/272, **rep3 272/272**, **rep4 272/272**, rep5 271/272; `rep{1..5}.{log,load.start,start}` |
| fresh-arm receipts (14 arms × 3) | `arms/*.rep*.{out,err,rc}` | battery launch shape, `subprocess.run` + 8 s bound |
| nullts wall-time ladder (20) | `arms/nullts_wall/` | 4/20 hit the 8 s bound |
| fixed-fps nav envelope cells (12) | `arms/fixedfps/nav_{default,ff120,ff150,ff600}.rep*.{out,err,rc}` | live crossing of both payloads |
| r91 `nav_lattice_path` stability (20) | `arms/path_stability/` | 20/20 PASS standalone |
| launch project | `arms/proj/` | copy of the frozen `corpus/fixtures/` + the three battery scratch transforms; excluded from the manifest |
| static audit | `probes/audit_committed.py` → `probes/audit-committed.txt` | CASES census, row indices, entries, floor gate, field inventory |
| field inventory | `probes/field-inventory.txt` | pinned-token vs `_it` keys (+ composite-value note) |
| envelope exhaustiveness | `probes/nav_envelope.py` → `nav-envelope.txt`, `nav-envelope-cells.txt` | 136 committed nav receipts: 90 p0 / 46 p1 / 0 neither |
| envelope live check | `probes/nav_envelope_live.py` → `nav-envelope-live.txt` | 12/12 (default+ff120 → p0; ff150+ff600 → p1) |
| signature coverage | `probes/signature_coverage.py` → `signature-coverage.txt` | 595/595 committed receipts byte-identical to a committed signature |
| tombstone re-derivation | `probes/rederive_encoding.py` → `rederive-encoding.txt` | 47/47 independent byte-layout checks |
| production-classifier discrimination | `probes/classify_discriminate.py` → `classify-discriminate.txt` | 32/32 (9 allowlists load-bearing, 7 nullts shapes, 4 nav mutations) |
| fresh-arm re-check | `probes/check_arms.py` → `check-arms.txt` | 41/42 OK; the 1 non-OK is the nullts wall-timeout |
| author-receipt custody | `probes/custody_check.py` → `custody-check.txt` | 42/42 re-classified OK; 27/27 allowlists load-bearing |
| prior-row identity | `probes/prior_identity.py` → `prior-identity.txt`, `prior-identity-green.txt` | rep3/rep4 = 0 mismatches vs r91 green **and** both author greens |
| per-row stability table | `probes/r92-row-stability.txt` | 13/14 rows byte-identical across all 5 reps |
| wall-time probes | `probes/nullts_wall.py`, `probes/path_stability.py` | `arms/nullts_wall/`, `arms/path_stability/` |
| manifest | `manifest.sha256` | 332 files covered, 1514 scratch files excluded by scope header |

## Reproduction

```bash
# freeze (whole-repo content check + fixture extraction)
git diff --quiet HEAD; echo rc=$?                                   # rc=0
git archive HEAD corpus/fixtures | tar -x -C corpus/live/r92-verifier/tree
# battery (five reps, from the frozen extraction)
python3 corpus/live/r92-verifier/tree/corpus/fixtures/run_battery.py \
        --runs corpus/live/r92-verifier/runs
# fresh arms / static audits / discriminators
python3 corpus/live/r92-verifier/probes/fresh_arms.py 3
python3 corpus/live/r92-verifier/probes/audit_committed.py
python3 corpus/live/r92-verifier/probes/signature_coverage.py
python3 corpus/live/r92-verifier/probes/classify_discriminate.py
python3 corpus/live/r92-verifier/probes/nullts_wall.py 20
python3 corpus/live/r92-verifier/probes/nav_envelope_live.py
```

## Key raw cells

```
rep3/rep4  PASS battery 272/272   r92_expected_errors_all_matched=true  dead_entries=0
rep1       FAIL nav_lattice_path  (r91 row; 2-point partial path; 0/20 standalone)
rep2/rep5  FAIL r92_tilemap_nullts_crash  exit=None  "TIMEOUT after 8 seconds"
nullts wall: n=20 timeouts=4 min=1.521s median=5.334s max completed=7.909s (bound 8s)
normal arm wall (census/nav/encoding): 0.354–0.680s
spontaneous_crash_probe (pre-existing row): n=6 timeouts=2
geo2d_lattice_lineempty / nav_lattice_teardown_crash (glibc/libstdc++ abort): 0.73–0.91s, 0 timeouts
nav receipts: 136 = 90 payload[0] + 46 payload[1] + 0 neither
signature coverage: 595/595 EXACT (full-line pins, zero unpinned tail)
```
