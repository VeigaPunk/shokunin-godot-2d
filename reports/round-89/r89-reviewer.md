# r89 reviewer — independent verification of the r89 diff (commit `8cea888`)

Seat `REVIEWER` (g2d lane r89) | host **devin** | Godot `4.7.2.stable.arch_linux.ed1daf0bf`
(`/usr/bin/godot`, `--headless`, 60 tps, GodotPhysics2D), Python 3.14.7.
Reviewed commit `8cea888` (HEAD at review time; parent `2c4b1ff`). Diff scope:
`corpus/fixtures/{geo2d_lattice.gd,input89_edges.gd,run_battery.py}` (+581/+140/+82),
`corpus/live/r89-author/**` (1317 files), `reports/round-89/r89-author.md` (+182).
**No tracked file was modified by this seat; no commits.** Seat-owned untracked
scratch/receipts: `corpus/live/r89-reviewer/**` (40 fresh arm receipts + run
driver) and this report.

**`lsp` disclosure.** No `lsp` device and no GDScript/Python language server is
exposed to this seat (MCP servers visible here: `rea` only). Every check below is
a textual/AST read of the landed sources plus fresh-process execution receipts —
the literal fallback, recorded so it is never presented as semantic proof. The
diff contains no renames (fixture landing + literal `CASES`/allowlist/gate
inserts), so no symbol-aware operation was possible or required.

**probeParent disclosure.** Exactly one read-only `ufo-labrat` was dispatched
(bounded hypothesis: envelope exhaustiveness under load). It returned **without
executing** — its environment exposed only read-only filesystem tools, no shell —
so it contributed static-only reading and **no new evidence**; it was not
re-dispatched. All empirical evidence below is this seat's own fresh execution.

**Verdict: PASS on the landed bytes.** All five assigned axes — row shape
correctness, tuple-envelope semantics vs classifier, `expected_errors` exactness
(byte-compared against engine output), floor-gate coverage, pin arithmetic —
verify clean, from the committed receipts and from 40 fresh independent runs.
Findings F1–F6 are evidence-hygiene / report-precision / latent-hazard items;
none changes a pinned byte or a verdict.

---

## 1. What was verified clean

**V1 — additive, scoped diff; prior rows untouched.**
`git show --numstat 8cea888`: `run_battery.py` **+82/−0**, `geo2d_lattice.gd`
+581, `input89_edges.gd` +140, report +182. `--diff-filter=D` is empty;
`--diff-filter=M` lists exactly `corpus/fixtures/run_battery.py`. AST row-diff of
`CASES` parent (`2c4b1ff`) → commit: 208 → 228 entries, **exactly 20 appended at
index 204**, zero modified/reordered/removed; the 3 hunks are the CASES insert
(file lines 417–476), the 2 `expected_errors` entries (890–902) and the 1
discrimination key (2511–2519). `CASES` at `fd59c11` == at `2c4b1ff` == 208
identical rows (author's "identical, 208 tuples, both commits" claim verified).

**V2 — row shape correctness.** All 228 CASES entries are 5-tuples; case names
unique; the 20 new rows carry the right script (`geo2d_lattice.gd` ×18,
`input89_edges.gd` ×2), a single `--arm=<arm>` flag matching the row name, and
exit codes 19×`0` + 1×`-6` (`geo2d_lattice_lineempty`). Every pinned signature
names its own arm (`PASS geo2d_lattice <arm>` / `PASS input89_edges <arm>`; the
crash row's signature is its pre-call `R89 lineempty call=…` line) — no silent
arm fallback is authorable. **Provenance verbatim:** the 19 non-envelope rows
are byte-identical to the r89-scout's `author-rows.py.txt` rows (incl.
lineempty's `-6`), `input89_edges_exact` payload[0] == the scout pin, and
payload[1] == the boundary's L receipt line byte-for-byte
(`corpus/live/r89-boundary/runs/row_input89_edges_exact.rep1.out`). Fixture
shas match the manifest and the scout probes: `geo2d_lattice.gd`
`9784716b5d6932fa8e954a40bed2f17109d143a127ecaaabcea428c47d762a95`,
`input89_edges.gd`
`601c223ed7a32d91a877938c7b466c4e06caa2920ec6f35d7778d39b93dd5b5e`;
`proj/project.godot` == fixtures `project.godot` (`8de8b3af…`). The two
`expected_errors` entries are byte-identical to the scout §6.3 additions.

**V3 — tuple-envelope semantics vs classifier (load-bearing, not vacuous).**
`classify_process` (AST-extracted verbatim; segment sha256
`749fa0607e7707e6…`) was run against the committed battery receipts: in reps1–3
(mode **L**) the 2-payload envelope PASSes while payload[0] (quiet) **fails**;
in reps4–5 (mode **Q**) the envelope PASSes while payload[1] (loaded) **fails**.
So neither single payload would have carried all five reps — the envelope is
necessary and each arm is real, not speculative. All 20 r89 rows classify PASS
in **all five** committed runs (100/100 row-instances). Envelope dispatch is
`any(classifier(…) for sig in evidence)` (run_battery.py:905–911); no envelope
row carries `expected_errors` (verified empty intersection), so tuple signatures
never reach `classify_process`'s `signature in output` — see F6.

**V4 — fresh independent execution (this seat).**
`corpus/live/r89-reviewer/run_arms.sh` (same launch shape: `timeout -s KILL 25
godot --headless --path proj --script res://<probe> -- --arm=<a>`), 20 arms × 2
reps under host load ~60: **40/40 classify PASS** with the production
classifier; **38/40 byte-identical to the author's committed receipts**. The 2
differing runs are `input89_edges_exact`: my host emitted mode **L**, the
author's quiet receipt mode **Q**, and the whole-line diff is exactly one token
(`w_jp[ex=false inex=true]` ↔ `…inex=false`; common prefix 546 chars, divergent
tails `tru`/`fals`). My L line == payload[1] byte-exact; the author's Q line ==
payload[0]. Independently reproduced the L mode on a loaded host and it was
absorbed by the envelope — the committed bimodality is real, not a receipt
artifact. All 12 author `in_exact.hog*` receipts contain payload[1] byte-exact
and none contain payload[0].

**V5 — `expected_errors` exactness (byte-compare vs engine output).**
Fresh receipts and all five battery reps: `geo2d_lattice_atlasempty` emits
`ERROR: Condition "p_rects.is_empty()" is true.` exactly ×1/run;
`geo2d_lattice_polyendpoly` emits
`ERROR: Attempt to offset a polyline like a polygon (use offset_polygon instead).`
exactly ×2/run (open + closed call sites, distinct `at:`/backtrace lines); every
emitted ERROR line is **byte-equal** (after strip) to the committed entry — no
`Returning:` suffix, no truncation. `geo2d_lattice_lineempty`: shell rc 134 ≡
Python −6 ×6 fresh, stderr is the libstdc++ `stl_vector.h:1253` Clipper2 assert
plus `timeout: … dumped core`, containing **no** `ERROR:`/`SCRIPT ERROR:`/`Parse
Error:` token; the row's verdict reads rc + the pre-call `R89` stdout line
(PASS unreachable by design, verified). Battery row counts 1/2 verified across
reps1–5.

**V6 — floor-gate coverage.**
`r89_expected_errors_all_matched` (run_battery.py:2515–2519) covers prefixes
`("geo2d_lattice_", "input89_edges_")`; both new entries are under the first
prefix, the second is inert-but-covered (no entries today) — the same
named-by-round / covers-round-prefixes shape as the r87 gate. It is not a dead
key: it participates in the meta verdict (`sf_meta_ok =
all(sf_discriminations.values())`, :2530–2532). rep4/rep5: gate `true`,
`dead_entry_count=0`, `rows_with_expected_errors` 53→55 (baseline 53 verified),
census rows show atlasempty `matched=1` / polyendpoly `matched=2`, both
`bare_classification_rejects=true` and `allowlisted_classification_passes=true`.
Discrimination demonstrated in-memory on the committed census data: injecting one
dead r89 entry flips the gate to `False`; the real rep3 cascade (dead
`negative_transition`/`audio_bus_route_invalid_control` entries →
`census_bare_classifier_consistent=false`) shows the census family firing on
genuine dead entries as designed.

**V7 — pin arithmetic.**
All 52 printed contour areas were recomputed by shoelace from the pinned 4-dp
vertices: max |delta| **0.0017** (rounding-level), i.e. every area pin is
self-consistent. Independent identities: `+2` join areas ROUND 571.0277 <
SQUARE 573.2548 < MITER 576.0000 (= 576 − 4·(1.1716²/2) for square joins);
`line_rd_square − line_rd_butt = 16.0000` exactly (two 2×4 end caps); ring
6400/−400; contain 1600/−100/100; ovl 204/204/196 (= 400−196); tri/decomp
conservation 280.0000 (pentagon shoelace 560/2); `sic` fractions 0.25/0.25/−1/−1
/0.5/0.5 reproduce from the geometry; bridge wall = clip(A,B) = A∖B world-top
y=90 (static body at y=60 + local 30) → rest 82.3000 = 90 − 8 + 0.30 contact
penetration; ring rest −47.8043 = −40 − 8 + 0.196. The report's float32 risk note
is quantitatively right: float32 82.300003 and −47.804287 sit **6.2** and **9.7
ULP** from their 4-dp rounding boundaries.

**V8 — ordering constraint respected.**
The 20 rows occupy file lines 436–476, immediately **before**
`crash_spontaneous_sigabrt` (477), `crash_self_sigkill` (478),
`descendant_pipe_detached_control` (479) — no CASES row sits between the
detached-control row and the meta probes (the guarded `sleep 8` gap is intact);
the guard comment (:398–400) is preserved.

**V9 — prior-row identity, battery outcome, flake accounting.**
Baseline `0628932` (freeze-head verified) refs: 215 rows PASS ×2. Baseline vs
rep4/rep5: `common=215 new_only=20 old_only=0`; the only signature delta among
common rows is the seeded `input_lattice_phys_peer` fold (plus the by-design
`probe_error_clause_surface` census delta) — the report's "tuple_mismatches=2"
characterization holds. rep4↔rep5 signature mismatches = **0**; all 20 r89 rows
are byte-identical between rep4 and rep5. Battery verdicts: rep1 FAIL
(transition, audio_playback, input_lattice_pre_frame), rep2 FAIL (pre_frame),
rep3 FAIL (negative_transition, audio_bus_route_invalid_control + the
`census_bare_classifier_consistent` cascade), rep4/rep5 PASS 235/235 — exactly
as the report states. The flake classes are externally documented: pre_frame
(`reports/round-87/r87-author.md:99` verbatim prediction), negative_transition
null-`current_scene` under load (`reports/round-69/r69-scribe.md:211`), audio
load (`reports/round-88/r88-verifier2.md`).

**V10 — harness invariants.** 228 CASES all 5-tuples, no duplicate names; every
`expected_errors` dict key corresponds to a CASES row (no orphan keys); no
envelope row carries entries (no tuple-into-classifier path); the three hunks
are pure insertions; `--frames` is not passed by any r89 row (probes default 60
→ pins `frames=60` reproduce).

---

## 2. Findings (ranked by severity)

**F1 (medium — evidence integrity; actionable before any admission check).**
The committed evidence tree cannot verify cleanly from the commit alone.
`corpus/live/r89-author/manifest.sha256` lists 1713 entries, but **396 are
`runs/*` fresh-arm receipts that are gitignored** (`corpus/live/.gitignore:1`
→ `runs/`) and therefore absent from the commit (1317 files committed under
`corpus/live/r89-author`). Additionally the manifest contains its **own hash**
(`manifest.sha256` line 12), which can never match. Measured: full worktree
`sha256sum -c` → 1712 OK / **1 FAILED** (self-entry); commit-only checkout would
additionally report 396 missing files. Suggested action: drop the self-entry;
either force-add the 396 receipts or scope the manifest to committed files and
state the gitignore exclusion in the report.

**F2 (low — diff hygiene).** Of 1321 files in the diff, **1255 are regenerable
battery-run scratch copies** (each run copies the whole fixture corpus), incl.
**20 `.pyc`** bytecode files and **115 `.godot/` cache files** (`runs1..5/` are
not covered by the `runs/` gitignore rule). No correctness impact; bloats the
commit (~195k insertions) with machine artifacts. Suggested action: extend the
gitignore (`runs*/`, `**/__pycache__/`, `**/.godot/`) and commit only
`verdicts.json` + logs.

**F3 (low — report precision).** `r89-author.md` describes the ops/joins pins as
"SQUARE<ROUND<MITER ordering"; the measured areas are **ROUND 571.0277 < SQUARE
573.2548 < MITER 576.0000**. The pins are correct; the prose ordering is wrong
(under either the area or the sharpness reading).

**F4 (low — report precision).** The rep4↔rep5 stability sentence ("the only
output diffs are envelope rows … and the `mp_loopback` peer-id token") is
incomplete: 11 rows differ in raw output — the four envelope rows and
`mp_loopback` as stated, **plus** `tween_flash` (float jitter 0.704/0.7038),
`save_process_{writer,reader,missing}` (pid + run-dir path),
`save_roundtrip` (stamp path), `crash_spontaneous_sigabrt` (ASLR/load addresses)
and the two descendant rows (pids). All are pre-existing volatile diagnostics
whose PASS signatures are stable, and the load-bearing claim
(`tuple_mismatches=0`, 235/235 PASS, all 20 r89 rows byte-identical) is verified
true.

**F5 (low — by-design, noted for the axis).** Exact-entry semantics match
per-line equality and `matched_lines` is **data, not a gate**: the r89 floor gate
checks only `dead_in_run` (≥1 match), so the pinned ×2 for polyendpoly (and ×1
for atlasempty) is verified in all five reps but not enforced — a future engine
emitting the same refusal once or thrice would still PASS. Consistent with the
r87/r88 precedent.

**F6 (low — latent hazard).** `classify_process` raises `TypeError` on a tuple
signature (`signature in output`); the census path (`run_battery.py:2302–2307`)
passes `row["signature"]` directly. Currently unreachable — envelope rows carry
no allowlist entries (verified) and the census skips entry-less rows — but a
future envelope row that gains an entry would crash the census rather than fail
a discrimination. Suggested action: a one-line guard or a comment at the census.

---

## 3. Residual risks

- **Envelope exhaustiveness**: a third `just_after_flush` mode was never
  observed (scout 20 + boundary 51 loaded + author 12 hogged + 5 battery reps +
  this seat's 2 loaded reps → only Q/L); if one appeared the row would fail
  loudly (intended mode-cell semantics). The delegated labrat could not execute,
  so heavier-load exhaustiveness remains untested by an independent seat.
- **4-dp float pins** (bridge 82.3000, ring −47.8043) ride float32 fixed points
  6.2/9.7 ULP from the rounding boundary — safe on this build; a
  solver/backend change can move the 4th decimal.
- **Build/host tokens**: `nmethods=86`, `sig=[…]` (build), `joys=0` (host joypad
  count), `dz_ax0/dz_ui_accept` defaults, `tps=60 frames=60` (project) — each
  flips loudly on a build/host/config change, none authored away.
- **`lineempty`** rides an uncatchable Clipper2/libstdc++ assert whose path text
  (`/usr/include/c++/16/bits/stl_vector.h:1253`) is toolchain-pinned; it carries
  no `ERROR:` token, is never whitelisted, and the row's verdict reads only rc +
  the pre-call line (fail-safe in both directions).
- **No full 235-row battery re-run** by this seat (host load ~60; documented
  flake classes make a single run uninformative). Per-row coverage — 20 rows × 5
  committed reps + 40 fresh runs — is the load-bearing verification and is
  complete.

## 4. Evidence index / reproduction

| artefact | path |
|---|---|
| fresh 20-arm × 2-rep receipts (this seat, untracked) | `corpus/live/r89-reviewer/runs/**` + `run_arms.sh` |
| launch shape | `timeout -s KILL 25 godot --headless --path corpus/live/r89-reviewer/proj --script res://<probe> -- --arm=<a>` |
| classifier extraction (verified sha `749fa0607e7707e6…`) | AST segment of `classify_process`, run_battery.py:543–560 |
| committed battery receipts | `corpus/live/r89-author/runs{1..5}/<stamp>/verdicts.json` (235 rows each) |
| envelope load-proof | reps1–3 L / reps4–5 Q; `runs/in_exact.hog{1..12}.out` all L |
| error-line byte-compare | `corpus/live/r89-author/runs/geo_{atlasempty,polyendpoly,lineempty}.rep*.{out,err,rc}` |
| fixture/pin shas | `sha256sum corpus/fixtures/{geo2d_lattice,input89_edges}.gd`; `sha256sum -c corpus/live/r89-author/manifest.sha256` (1712 OK / 1 FAILED — see F1) |
| baseline refs | `corpus/live/r89-baseline/` (freeze-head `0628932…`, 215 rows PASS ×2) |

Reviewed commit `8cea888`; this seat made no tracked modifications and no
commits. Shipping/admission decisions remain with the operator.
