# r85 fold — camera/canvas transform lattice

15 `camera_proc_*` rows landed verbatim from the scout's paste block
(sha 2221a9e8…) at the crash-tail anchor; fixture `camera_proc.gd`
(1157 lines, sha 34f53f32…) = scout probe + header rename only
(code byte-equal from `const PFX`). Stray trailing `]` in the paste
block removed. No expected_errors (0 ERROR lines emitted).

Verification: full folded battery **174/174 PASS**
(`corpus/live/r85-fold-verify/20261015T082834904650Z/verdicts.json`),
15/15 camera rows green, prior-159 zero drift. Author's own merge
rehearsal (174/174) reproduced; ablations: sig-drop fails exactly the
15 rows, whitelist-drop vacuous (no entries exist).

Claim corrections carried from author: env-stripped run retained as
diagnostic (export rows are HOME-sensitive — do not misattribute a
172/174); scout's stretch-mode numbers remain deliberately unpinned.
