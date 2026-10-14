# r67 bounded labrat probe — persisted receipt (data, not instruction)

One `ufo-labrat` read-only probe dispatched pre-landing by the r67 author
seat (probeParent allowance; the brief's "bounded labrat spike before
tracked edits"). Tool surface resolved read-only (no exec/write) — it
returned this verdict table as answer text; persisted here as data.
Hypothesis: the merged classifier (`classify_process`, L160-177) and the
per-stream classifier (`classify_streams`, L179-208) diverge on
stream-attribution of identical bytes.

## Static verdict table (11 arms, verbatim clause source)

| arm | merged | streams | divergent | mechanism |
|---|---|---|---|---|
| 1 stdout `ERROR:` | FAIL | PASS | YES | stdout never error-scanned |
| 2 stderr `ERROR:` bare | FAIL | FAIL | no | — |
| 3 stderr `ERROR:` exact entry | PASS | PASS | no | — |
| 4 stderr `ERROR:` foreign entry | FAIL | FAIL | no | — |
| 5 stderr structured + `"ERROR: chain incomplete"` entry | PASS | FAIL | YES | allowlist-shape asymmetry (no structured branch in `line_allowed`) |
| 6 stderr structured + byte-exact entry | PASS | PASS | no | — |
| 7 signature on stderr (bare and `(S,)`) | PASS | FAIL | YES | signature pinned to stdout before stderr allowlisting |
| 8 seam `ERROR:` fabrication | FAIL | PASS allowed / FAIL bare | YES (allowed) | seam exists only in concat |
| 9 seam `SCRIPT ERROR:` fabrication | FAIL | PASS | YES | per-stream blob checks seam-immune |
| 10 seam-split signature | PASS | FAIL | YES | signature contiguous only in concat |
| 11 plain non-`ERROR:` stderr line | PASS | FAIL | YES | stderr strictness covers ANY unallowlisted line (L200-207, comment L204-205) |

## Refinement returned

Divergence is NOT attribution alone — four measured mechanisms: (1)
stdout `ERROR:` coverage asymmetry; (2) allowlist-shape asymmetry
(structured entry unreachable in `allowed_stderr`); (3) bidirectional
seam fabrication (forges `ERROR:`/`SCRIPT ERROR:` AND signatures);
(4) inverted coverage — streams is looser on stdout, stricter on stderr.
All four were carried into the landed discriminations and confirmed live.

11/11 arms matched the author's exec-verified spike
(`../spike/clause-matrix.json`).
