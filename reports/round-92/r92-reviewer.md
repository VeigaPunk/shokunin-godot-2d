# r92 reviewer — wave-B gate on the committed TileMapLayer lattice landing (`5900431`)

Seat `REVIEWER` (g2d lane r92) | host **devin** | Godot `4.7.2.stable.arch_linux.ed1daf0bf`
(`/usr/bin/godot`, `--headless`, 60 tps, GodotPhysics2D), Python 3.14.7, 32 cores.
Reviewed commit **`5900431`** (parent `045d925`); HEAD at review time `8a0da55`
(one later commit, the r92 **scribe**, which touches `corpus/live/r92-scribe/**` only —
`git diff --stat 5900431 HEAD -- corpus/fixtures/` is **empty**, so `5900431`'s fixture
bytes are still the live ones). Diff scope: `corpus/fixtures/tilemap_lattice.gd`
(**+929/−0**, new; byte-copy of the frozen scout probe), `corpus/fixtures/run_battery.py`
(**+161/−0**, 14-row insert + 9 allowlist cases + 1 `required_stderr` case + 1 floor gate),
`reports/round-92/r92-author.md` (+215), and 133 committed author artefacts
(`corpus/live/r92-author/`: 126 fresh-rep receipts + manifest + 5 battery logs +
`verify_author.py`). **No deletions anywhere** (`git show 5900431 | grep -c '^-[^-]'` = 0).

**This seat modified no tracked file and made no commit** (`git status --porcelain` shows
zero non-`??` lines, re-checked after every execution batch). Seat-owned untracked
scratch/receipts: `corpus/live/r92-reviewer/**` (951-file `manifest.sha256`, 951/951 OK,
no self-entry) and this report.

**`lsp` disclosure.** No `lsp` device and no GDScript/Python language server is exposed to
this seat (same as the r89–r92 author/verifier lanes). Every check below is a textual/AST
read of the committed bytes plus fresh-process execution receipts — the literal fallback,
recorded so it is never presented as semantic proof. The diff contains no renames (fixture
landing + literal `CASES`/allowlist/gate inserts), so no symbol-aware operation was
possible or required.

**probeParent disclosure.** Exactly one read-only `ufo-labrat` (L2) was dispatched, with
one bounded 4-clause hypothesis: *(H1)* every r92 PASS-class pin is a byte-exact full match
to the emitted PASS line with **no unpinned tail** and appears on stdout in every rep;
*(H2)* the nav envelope's two payloads differ **only** in `regions_f1`; *(H3)* each of the
9 allowlist keys has every entry matched and no `ERROR:` line uncovered; *(H4)* the nullts
signature is on stdout and both `required_stderr` fragments on stderr in all reps.
It had **no shell/exec tool** (read/grep/glob only) and executed nothing. It returned
**CONFIRMED on all four clauses** with per-file/per-line evidence (65/65 PASS lines
compared; the 20 non-`regions_f1` envelope tokens byte-identical; 18/18 allowlist entries
matched with 0 uncovered ERROR lines; fixture line 927 = `var td := layer.get_cell_tile_data(...)` inside `_nullts`). One caveat it declared: sub-visible
bytes (trailing whitespace) could not be settled statically — this seat settled that
empirically (V5). It was not re-dispatched; all execution evidence below is this seat's own.

**Concurrent-worktree disclosure.** While this review ran, four sibling lanes ran their own
full batteries in this repo (`r92-verifier`, `r92-scribe`, `r92-simplifier`, and a 3d-lane
battery), and `HEAD` advanced by one scribe commit. All of my checks read the **pinned**
committed bytes: `git archive 5900431 corpus/fixtures` → `corpus/live/r92-reviewer/pinned/`
(78 files, each sha256-compared to `git show 5900431:…` — all equal), and the harness was
launched from that directory, so its own `HERE`-copy scratch never reads the dirty
worktree. My two battery runs (`runs1`, `runs2`) are therefore committed-byte runs, and
they landed green.

**Verdict: PASS on the landed bytes.** All five folds the dispatch names are implemented as
claimed and are *demonstrated*, not merely asserted: (1) the nav row is a real 2-payload
envelope whose boundary is reproducible (payload[0] at `--fixed-fps` ≤ 120, payload[1] at
150/600, and the one-step read `regions_f1=1` is a **deterministic** production value:
`idle=0, phys=1` at the write point in 8/8 production-shape runs); (2) the `update_internals`
nav-lever claim is absent from the nav row and lives only in the physics-path `timing` row;
(3) the nullts row pins exit **`-6`** + a stdout anchor + two stderr fragments, and 8/8
forgery shapes reject while 3 committed + 5 fresh genuine receipts pass; (4) the tombstone
encoding is inside the `encoding` signature (`stride=12`, in-place `0xFF` tails for
erase/clear, high-water-mark lengths) and is byte-stable; (5) `expected_errors` carries the
9 cases (18 entries) with the floor gate load-bearing. 14/14 r92 rows PASS in **both** of my
independent committed-byte battery runs (272/272, all discriminations true) and in 70/70
fresh arm receipts; every r92 PASS line is **byte-identical across sessions** (author ×3,
mine ×5). Findings F1–F6 are evidence-integrity / precision / documentation items; **none
changes a pinned byte or a row verdict**.

---

## 1. What was verified clean

**V1 — additive, scoped diff; prior rows untouched.**
`git show --numstat 5900431` for the two fixtures: `+929/−0` and `+161/−0`; zero deletion
lines in the whole commit. AST row-diff of `CASES` from `5900431^` (251 entries) to
`5900431` (265 entries): **pure insertion of 14 rows** — common prefix 247, common suffix 4
(the crash/descendant tail `crash_spontaneous_sigabrt`, `crash_self_sigkill`,
`descendant_pipe_detached_control`, `descendant_pipe_forged_signature_release`), all 265
entries 5-tuples, names unique. Result rows **272 = 265 + 7 meta** (r91: 258 = 251 + 7).
Committed shas match the report exactly: fixture
`a699138945ec7c1c1e6c97b6bf052d0941596610ad4cb9d08d184c07409d3dfb` (929 lines),
harness `5e5182815e6e3c503f40c78b6416b5cf6aaf9d0d3ea3ed7577594bd9f35aa509`,
`project.godot 8de8b3af…` unchanged. The fixture is **byte-identical to the frozen scout
probe** `corpus/live/r92-scout/probes/tilemap_lattice.gd` (`a6991389…`) — verbatim
provenance, no fixture-side fold.

**V2 — row shape and gate mechanics.** All 14 rows: script `tilemap_lattice.gd`, one
`--arm=<suffix>` flag matching the row suffix, expected exit 0 (crash row **−6**); 13 rows
carry a plain-string signature and `r92_tilemap_nav` a 2-tuple envelope. The 9 allowlist
keys carry 18 entries total, all inside the same dict literal the harness reads
(lines 1025–1210), **no orphan keys** (every key names a real `CASES` row; 0 of 9 outside).
No envelope row in the entire battery carries `expected_errors` or `required_stderr`
(checked across all 8 envelope rows) — the r89-reviewer F6 tuple-into-classifier hazard
stays unreachable. `rows_with_expected_errors` 59 → **68** in my runs.

**V3 — classifier identity.** The `classify_process` segment extracted from the committed
harness is byte-identical (segment sha256
`749fa0607e7707e614c1ab157a6f8e756dfc2f460746e6d218e6734ad8fa72c3`) to the segment
r89/r90/r91 recorded — the r92 diff does not touch the classifier, so the r92 rows are
judged by the same production logic as their predecessors.

**V4 — fresh independent execution (this seat).** `tools/run_arms.py` in the battery's exact
launch shape (`godot --headless --path <proj> --script res://tilemap_lattice.gd -- --arm=<a>`,
`subprocess.run`, separate streams), 14 arms × 5 reps, 6-way concurrent, host loadavg 54–61
with four foreign battery lanes running: **70/70 classify PASS** with the production
classifier + committed per-row allowlists (`fresh-load/`). `out_uniq=1` for all 13 PASS
rows; `err_uniq=1` for all rows except `nullts` (ASLR addresses). rc as declared (`nullts`
`-6` in 5/5). All 9 allowlists **load-bearing** (`bare=False` on all 45 entry-bearing
receipts). `verify_author.py` re-run against the committed harness reproduces the author's
`fails=0` over their 42 receipts.

**V5 — no unpinned tail anywhere; byte-stability across sessions.** `tools/prefix_audit.py`:
for all 13 PASS rows in my 5 reps **and** in the author's committed 3 reps, the pinned
signature is a byte-prefix of the emitted PASS line with **tail length 0** (full-line match)
and one unique PASS line per row. Cross-session check: my 5 fresh receipts vs the author's
3 committed receipts — stdout byte-identical **14/14** arms; stderr byte-identical 13/14
(`nullts` differs only in ASLR'd addresses); the 3 committed + 5 fresh receipts of every
PASS arm are one unique byte string. This is a stronger stability claim than r91's
(where every row carried a scheduler tail).

**V6 — the nav envelope's boundary is real and the production payload is deterministic.**
Instrumented launch-project copy (measurement only, never the fixture): at the `set_cell`
write point `Engine.get_process_frames()`/`get_physics_frames()` read **`idle=0, phys=1`**
in the production shape (8/8: 5 instrumented reps + 3 more) — the first physics step always
precedes any idle frame, so registration flushes in it and **`regions_f1=1` is
deterministic, not modal**, in every battery-run harness shape. `--fixed-fps` cells:
**ff120 3/3 `regions_f1=1` (payload[0])**, **ff150 3/3 and ff600 3/3 `regions_f1=0`
(payload[1])**, with `regions_f2=1` in all 9 — the settled law is single-valued while the
one-step read is modal, exactly as the author declares. In the instrumented ff150/ff140
cells the physics frame counter is `0` at the write point (`idle=0, phys=0`) — the same
mechanism (an idle frame interleaving before the first physics step) from the other side.
The `discrimination.json` "bad" list holds exactly the two ff150/ff600 cells — my harness
asserted "the row must reject a payload[1] receipt" and it does **not**, which is the
envelope's declared behavior, not a defect; every other cell (77/79) landed as declared.

**V7 — the nullts negative control is armed and its stderr pin is load-bearing.**
**13 crash instances** — 8 of this seat's (5 fresh-load + 3 ff cells) + 3 committed author
fresh reps, plus the 2 author-battery rows re-read: **every one** `rc=-6`, stdout anchor
`R92 nullts about_to_call_tile_data=1` present, both fragments
(`handle_crash: Program crashed with signal 11`, `_nullts (res://tilemap_lattice.gd:927)`)
on **stderr**. Discrimination on a real receipt (`tools/discrimination.py`, 10 cells):
clean PASS; fragment dropped → FAIL; site fragment dropped → FAIL; signature on stderr only
→ FAIL; rc=0 with the right fragments → FAIL; foreign `ERROR:` line → FAIL; the scout's
shell-encoded `rc=134` → FAIL; forged PASS line + rc=0 → FAIL; raw `-11` → FAIL. The scout's
`134` vs the battery's `-6` is confirmed to be the same SIGABRT termination under two
encodings, and the row binds the **battery's** encoding.

**V8 — full battery on the committed bytes, twice (this seat).**
`runs1/20261016T001706487857Z` → **272/272 PASS**, `r92_tilemap_*` 14/14,
`r92_expected_errors_all_matched=true`, `dead_entry_count=0`, `all(41 discriminations)`
true. `runs2/20261016T002127197810Z` → **272/272 PASS**, same gate values. Each run
launched from `pinned/` (`verdicts.json.seed` points at it); run windows 00:17:06Z→00:21:27Z
and 00:21:27Z→00:25:43Z under loadavg 59→65 with the foreign lanes active. The author's two
green runs re-read from disk (`runs4`, `runs5`) are genuinely **272/272** with the same
gate values, and their 126 committed receipts re-classify **42/42 PASS** with my own
extracted production classifier.

**V9 — prior-row identity.** My rep1 vs the r91 author's green reference
(`corpus/live/r91-author/runs2/20261015T224213073214Z`): 258 common rows, **0 differences**
in `verdict`, `signature`, `expected_exit`, `actual_exit`, `script`, `flags`, `error`,
`required_stderr`, `expected_errors`; 14 new-only rows (the r92 block); 0 old-only. My
rep1↔rep2 raw-output diff is 17 rows, all documented-volatile classes (pids/paths/ASLR/
`frames=`/scheduler tails) with identical signatures and verdicts — including
`r92_tilemap_nullts_crash` (stderr ASLR only). The 14-row insertion perturbs nothing.

**V10 — floor gate is load-bearing in the direction the author claims, and not in one
direction he does not.** Two control batteries, each a copy of `pinned/` with a single
one-line mutation, run end-to-end:
- **ctlB** (weaken one `r92_tilemap_atlas` entry to a string that can never match) →
  `r92_expected_errors_all_matched=**False**`, `dead_entry_count=3` (2 pre-existing
  `negative_transition` flakes + the planted one), `error-clause surface meta FAIL`, battery
  FAIL. The gate turns a dead entry on an **executed** row into a loud failure. ✔
- **ctlA** (rename the `r92_tilemap_atlas` allowlist **key** to a non-existent case, leaving
  the row's real `ERROR:` lines uncovered) → `r92_expected_errors_all_matched=**True**`,
  `dead_entry_count=0`, battery FAIL **only** because the atlas row itself fails
  (`r92_tilemap_atlas FAIL`, its ERROR lines now unrelated). The gate never sees keys whose
  rows do not execute — see **F5**.

---

## 2. Findings (ranked by severity)

**F1 (medium-low — evidence integrity; the commit carries only part of the lane's
evidence).** `git ls-files corpus/live/r92-author` → **133 files** (126 fresh-rep receipts +
`manifest.sha256` + 5 `battery*.log` + `verify_author.py`). The manifest itself lists
**1510** entries; the difference is the five `runs{1..5}/` trees (275–276 files each), which
are excluded by `corpus/live/.gitignore` (`runs*/`) — so the manifest **cannot be verified
from a checkout**, and the two "272/272" runs the commit message and the report's evidence
index point at (`runs4/20261016T000237277486Z`, `runs5/20261016T000655453477Z`) are
**worktree-only**. I verified the manifest in the live worktree (1510/1510 OK, no
self-entry, no missing file) and re-read both green runs, and I reproduced the green claim
myself twice (V8), so no verdict changes. Same shape as r91 reviewer F1 (that lane committed
no receipts at all; r92 commits the load-bearing fresh arms and omits the run trees).
Suggested action: force-add the two run trees (or their `verdicts.json`) in the wave fold,
or scope the evidence index to tracked artefacts and state the gitignore exclusion.

**F2 (medium-low — precision; the production payload is the only reachable one, so
payload[1] admits states the battery cannot produce).** The envelope's payload[1] is
*necessary* for a `--fixed-fps ≥ ~140`-class harness and is *unreachable* in any harness the
battery runs: the default scheduler puts the first physics step before any idle frame
(`idle=0, phys=1` at the write point, 8/8 — V6), and the only knob that crosses the boundary
is `--fixed-fps`, which the battery never passes. So in the production regime the row admits
`regions_f1∈{0,1}` while the measured value is always 1, i.e. a future one-frame latency
regression in region registration would **pass** via payload[1] instead of failing loudly —
the opposite failure direction from r91's 4-frame tolerance class. It is not a hidden
weakening (the boundary falsified the fixed pin, the author declared the envelope in the
report and in the harness comment at lines 687–700, and the settled `regions_f2=1` stays
pinned in both payloads), but it is the one place in this landing where a pre-existing hard
assertion became modal. The alternative — keeping payload[0] only — would reject the
`--fixed-fps` cells the boundary measured (the scribe's independent 416-receipt matrix found
payload[0]-only rejects 2 of them). Suggested: state in the row comment that payload[1] is
the `--fixed-fps ≥ ~140` regime and is unreachable in the battery's launch shape, or add a
mode discriminator so payload[1] cannot absorb a production drift.

**F3 (low — documentation defect inside the harness; the scribe's A1, independently
re-derived here).** `corpus/live/r92-reviewer/pinned/run_battery.py:1236–1240` (the r92
nullts `required_stderr` comment) says *"binds the rc=-11 to the engine's own signal-11
crash handler"*, but the row's `expected_exit` is **−6** (SIGABRT through the engine crash
handler) — the pinned exit code is right, the prose is wrong. The author's report and the
harness comment at line 631–636 describe the mechanism correctly ("SIGSEGV hazard … the
engine crash handler's `abort()` exits `-6`"). Comment-only; no behavior. Suggested one-line
fix in the same wave that touches the harness next.

**F4 (low — the "envelope, never a fixed frame" claim is stronger than the code).** In
`--fixed-fps ≥ ~140` cells the mechanism is a *frame-ordering* predicate, not a ratio
threshold: the physics frame counter is `0` at the write point (ff140/ff150) versus `1` in
production and ff120 — the flip needs only that one idle frame interleave before the first
physics step. The boundary's `idle:physics ≥ 2.5` is the *in-situ time-averaged* ratio in
its scans (default 2.5–3, ff120 = 2.0), and my boundary bracket (ff120 passes, ff140 flips)
sits at ≈2.3, i.e. the `≥2.5` wording is an artifact of the sampled ratios rather than a
derived constant. No pin depends on the number, and the row's declared cells (ff120 vs
ff150/ff600) are reproduced exactly; recorded so a future reader does not treat "2.5" as
load-bearing.

**F5 (low — orphan allowlist keys are invisible to the floor gate; pre-existing).** The
census is built from **executed** rows (`for row in results`), so an allowlist key naming a
case that never ran produces no census entry and cannot be flagged: ctlA demonstrates the
gate reporting `r92_expected_errors_all_matched=True` with a fully orphaned key, and
`census_bare_classifier_consistent`/`census_allowlisted_reproduces_verdicts` also stay true
because the orphan key is simply absent from the census. The author's sentence "A dead r92
allowlist entry fails `probe_error_clause_surface` loudly" is therefore true for entries
attached to executed rows (ctlB: loud) but over-general as written — identical property in
r87–r90 (r91 reviewer F6). Effect today: none (all 9 keys name real rows — V2). Suggested:
compare the allowlist key set against `CASES` names in the meta block.

**F6 (info — the author report's worktree note is pre-fold).** `reports/round-92/r92-author.md`
ends with "No commit. Worktree: `M corpus/fixtures/run_battery.py` (+161) …" — true when
written, superseded by the fold commit `5900431` (whose bytes are identical to the worktree
state I measured). No action; recorded so the report's last paragraph is not read as a
current statement.

---

## 3. Residual risks

- **Build/host tokens**: `class_method_counts` (TileMapLayer=58, TileSet=90,
  TileSetAtlasSource=41, TileData=54, TileMapPattern=10), the enum orders, `layer_props=n16[…]`
  and the `*_defaults` blocks are version tokens that flip loudly on an engine bump
  (intended, same class as the existing census pins). The scout's `ROWS_PREFIX` variant is
  staged at `corpus/live/r92-scout/author-rows.py.txt` if a bump ever moves them.
- **Toolchain-pinned stderr fragments**: `handle_crash: Program crashed with signal 11`
  (Godot's own handler) and the GDScript backtrace site `…:927` are bound to this frozen
  probe's line numbering — a future fixture fold that moves the crash site SHOULD fail
  loudly (the sha is recorded in the report). ASLR'd addresses and the C++ backtrace are
  deliberately unpinned.
- **`--fixed-fps` remains an opt-in cell the battery never runs**: the landing is correct
  under it (payload[1], or payload[0] at ≤120), but a future harness change that adds
  `--fixed-fps` to the nav rows would exercise the modal path silently rather than loudly.
  My 9 fps receipts (`ff120/`, `ff150/`, `ff600/`) are the receipt set; the scribe's
  `audit/fixedfps_probe.py` is the independent one.
- **Host oversubscription**: four foreign battery lanes plus 48 `yes` hogs ran throughout
  (loadavg 54–65). Both of my committed-byte runs were green (272/272) and no r92 row flaked
  in 70 fresh receipts; the author's interim runs failed only on the documented volatile
  classes (`negative_transition`, `transition`, `overlap`, audio rows), whose dead allowlist
  entries knock on to `census_bare_classifier_consistent` — a flake consequence, not a row
  defect (reproduced by my own ctlB control, which also shows the knock-on).
- **F1**: the lane's run-tree evidence lives only in the worktree; a clean would lose it.
  My `runs1`/`runs2` (committed-byte, both green) are the durable substitute until the wave
  folds the run trees.

## 4. Blockers

None. Shipping/admission decisions remain with the operator.

---

## 5. Evidence index / reproduction

| artefact | path |
|---|---|
| committed bytes under review (`git archive 5900431 corpus/fixtures`) | `corpus/live/r92-reviewer/pinned/` — 78 files, each sha256-checked against `git show 5900431:…` |
| production `classify_process` (AST-extracted, sha `749fa0607e7707e6…`) | `tools/ufo_r92.py` (`load()` returns the segment + CASES/allowlists/required_stderr) |
| receipt re-classifier (production clause + allowlists + stream anchors) | `tools/verify_receipts.py` → `fresh-load.verify.json`, `author-receipts.verify.json` |
| prefix/byte-stability audit (no unpinned tail) | `tools/prefix_audit.py` → `fresh-load.prefix.json`, `author-receipts.prefix.json` |
| fresh arm runner (battery launch shape, `--fixed-fps` opt-in, parallel) | `tools/run_arms.py` |
| 70 loaded fresh arm receipts (14 arms × 5) | `fresh-load/` (+ `fresh-load.log`) |
| 9 `--fixed-fps` receipts (120/150/600 × 3) | `ff120/`, `ff150/`, `ff600/` |
| discrimination matrix, 79 cells (crash forgeries, allowlist load-bearing, envelope payloads, pin byte-mutation) | `tools/discrimination.py` → `discrimination.json` |
| full battery run 1 (272/272, gate true, dead 0) | `runs1/20261016T001706487857Z/verdicts.json` (+ `battery1.log`) |
| full battery run 2 (272/272, gate true, dead 0) | `runs2/20261016T002127197810Z/verdicts.json` (+ `battery2.log`) |
| gate control A (orphan key — gate stays true) | `ctlA-runs/20261016T001815197606Z/verdicts.json` (+ `ctlA.log`) |
| gate control B (dead entry on an executed row — gate false, dead 3) | `ctlB-runs/20261016T002238235164Z/verdicts.json` (+ `ctlB.log`) |
| battery driver (two sequential runs, loadavg-stamped) | `tools/battery_runs.sh` (+ `battery_driver.log`) |
| committed author receipts re-classified 42/42 + cross-session byte compare | `../r92-author/fresh-reps/`, `../r92-author/manifest.sha256` |
| r91 green reference for prior-row identity | `../r91-author/runs2/20261015T224213073214Z/verdicts.json` |
| receipt manifest (this seat) | `manifest.sha256` — 951/951 OK, no self-entry |

Reproduction:

```bash
cd /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin
# committed bytes (already extracted here; re-extract if needed):
mkdir -p corpus/live/r92-reviewer/pinned && git archive 5900431 corpus/fixtures \
  | tar -x -C corpus/live/r92-reviewer/pinned --strip-components=2
python3 corpus/live/r92-reviewer/tools/verify_receipts.py corpus/live/r92-reviewer/fresh-load
python3 corpus/live/r92-reviewer/tools/prefix_audit.py   corpus/live/r92-reviewer/fresh-load
python3 corpus/live/r92-reviewer/tools/discrimination.py
bash    corpus/live/r92-reviewer/tools/battery_runs.sh      # ≈4.5 min/run under this load
python3 corpus/live/r92-reviewer/tools/run_arms.py --proj corpus/live/r92-reviewer/proj \
        --out <receipts> --reps 5 --par 6                    # add --fps 120|150|600 for the fps cells
```
