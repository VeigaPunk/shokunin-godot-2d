# r86 scribe — audit of author/scout/verifier evidence chain

Seat `SCRIBE` | lane `r86-scribe` | round 86 | host devin | repo HEAD `7ae7083`
(committed+pushed; this seat wrote nothing tracked, no commit). Audit notes:
`corpus/live/r86-scribe/audit-notes.md` (full command trace + per-claim table).

Scope: (1) trace r86-author.md claims to receipts; (2) check the 8 CASES pins
against recorded runs; (3) author-vs-scout consistency on the falsified r77
law; (4) receipt hygiene (cited files exist, SHAs match).

## Task 2 first — CASES signatures vs recorded runs

All 8 `phys2d_backends_*` pins in `corpus/fixtures/run_battery.py` appear
**byte-identically** as the single emitted `PASS` line in every recorded run:

- author battery `corpus/live/r86-author-battery/20261015T130812159398Z/verdicts.json`
- verifier `run1/20261015T133754513801Z` and `run2/20261015T134054380982Z`

Each row: `verdict=PASS`, `actual_exit=0`, `expected_errors=[]`, exactly one
`PASS phys2d_backends` output line equal to the pin. Rows sit at result
indices 163–170 (between `camera_proc_par_phase` and `crash_spontaneous_sigabrt`);
excising them leaves name order identical to the r85 receipt (174 rows).
`standalone.json` pins == `CASES` literals 8/8, so "rows pasted from the
standalone pins" is accurate.

## Task 1 — author-report claims

Every material claim traces to a receipt or to the committed fixture. The
8-cell law table matches the pins field-for-field (census hint strings and
`jolt2d_ns=0`/`jolt3d_ns=32`; lattice silent fallback incl. `stored=[Jolt
Physics]`→`GodotPhysicsDirectSpaceState2D`; jolt3d_live control; xcheck
`errs2d=[0,0,1,1,1]`/`errs3d=[0,0,0,1]` at `physics_server_2d.cpp:959`/
`physics_server_3d.cpp:1193`; gate_matrix A,B,C,F,G=null/D,E=ok/`errs=5` all at
`godot_physics_server_2d.cpp:281`; gate_duality `at_eq=true`; dummy_degenerate
empty-hit dict; dummy_timeout `rc=124 bound_s=3 hang_begin=1 collider_sig=1`).
Child captures confirm the mechanism claims: split out/err/rc per boot,
`user://r86bt` work root, `timeout` wrapper writing real child rc, ERROR
frames confined to child `err.txt` (parent streams clean — 0 ERROR lines in
all 8 battery outputs and all 24 standalone reps).

## Task 3 — author-vs-scout consistency (r77 falsified law)

**Acknowledged.** r86-author.md's `gate_duality` cell states the correction
explicitly: "refines r77's pinned split (boundary-falsified: paths emit
byte-identical errors)". The falsification itself is receipt-sound — r77's own
`win.thr.stderr.txt` attributes space-state ERROR frames to the property path
(`w2.gd:24` ×1, `w2.gd:53` ×3) alongside the explicit call (`w2.gd:54` ×3), and
the scout's cited `at:`-line sha256 `e18944622af0bc30…` verifies against the
raw line bytes.

**No silent dependence.** No r86 pin depends on the falsified version; two
pins actively encode the correction (`gate_matrix` `errs=5` is unreachable if
property-path refusals were silent; `gate_duality` pins `at_eq=true`). Pre-r86
pins cannot encode it either — the battery scratch `project.godot` never sets
`physics/2d/run_on_separate_thread`, so the gate never arms in tracked rows.

## Task 4 — receipt hygiene

All files cited by the three reports exist. All 9 scout sha256 prefixes match
the live artifacts; scout file counts (315/81/288/36) match; every
MANIFEST.sha256 entry verifies. Verifier's cited run dirs, `report.json`,
`forge_report.json`, `forge-scratch`, and the r85 baseline all exist; HEAD
`7ae7083` confirmed; `corpus/fixtures/` unmodified since commit.

## Findings

| id | severity | blocking? | finding |
|---|---|---|---|
| F1 | low | no | Scout §9 cites `MANIFEST.sha256` as "752 lines"; actual is **761** lines (754 non-empty, ~751 hash entries). Manifest contents verify clean — a count drift, not missing evidence. |
| F2 | low | no | Author: dummy_timeout is "the only row whose PASS signature contains a 124" — literally false as a substring claim (`phys2d_joints_joint_census`'s pin contains `124` inside `max_bias=340282001837565597733306976381245063168.0`). The intended claim — only row pinning `rc=124` — is true. |
| F3 | trivial | no | Author: "`intersect_ray` returns `[]`" reads as an empty Array; the measured return is an empty **Dictionary** (`ray_keys=[]`, `ray_pos=<absent>`). The pin itself is unambiguous. |
| F4 | info | no | "Died in the 09:0x rate-limit sweep" is a narrative claim with no receipt; timestamps are consistent (standalone stamp 08:56Z, battery 13:08Z). Recorded as attestation-consistent, unverifiable. |
| F5 | info | no | Isolation nuance: `user://r86bt/` resolves under the host's real `~/.local/share/godot/app_userdata/MechanicOneShotTest-<stamp>/` — the battery overrides `XDG_DATA_HOME` only for `save_*` rows. All husks found **empty**; `_cleanup` rm -rf works, each `_boot` rewrites inputs fresh, so no cross-run contamination observed. |
| F6 | info | no | Author's "Wave-B pending" line was true at write time; `r86-verifier.md` (untracked, post-commit) now records ADMIT. Temporal staleness only. |

## Verdict of the audit

The r86 author report is receipt-backed end to end: standalone pins ≡ CASES
pins ≡ three independent battery-run emissions (byte-identical, ×3 runs), the
falsified r77 law is acknowledged and the new pins depend on the *corrected*
law, and cited artifacts exist with matching SHAs except the one numeric drift
in F1. Nothing blocking. Consistent with the verifier's ADMIT.
