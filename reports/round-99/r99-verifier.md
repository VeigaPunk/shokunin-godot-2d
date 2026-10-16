# r99 verifier — independent non-author verification of committed `254e79dd`

Seat `VERIFIER` (g2d lane `r99-verifier`, independent non-author) | host **devin** |
Godot `4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, `--headless`, Dummy
audio driver, mix rate 44100, 60 physics tps), Python 3.14.7, 32 cores, 30 GB RAM.
Target: **`254e79dd81202b2f25b3064681c95d95a37ccdfe`** (*r99 author: headless audio
lattice (21 rows, +150/-0), green 447/447*), whose parent is
`9d421fb2c0577488cf6f34399c123d81a91a067b` (*r98 author*). Author report:
`reports/round-99/r99-author.md`. Receipts: `corpus/live/r99-verifier/`
(archive scratch under `/tmp/r99-verify/`). **No tracked file written, no commit,
no push.** Only new untracked receipts + this report.

**`lsp` disclosure.** No `lsp` device in this session and no GDScript language
server on this host — `definition`/`references`/`hover` were **unavailable for
every file**. No symbol-aware operation was required (verification is fresh-process
execution plus AST/byte analysis of two files), so no rename/reference risk exists.

**Labrat disclosure (frozen `probeParent`, exactly one dispatch).** One read-only
`ufo-labrat` was dispatched once, bounded and documentary (H1–H5: the committed
`CASES` count and the duplicate name; the 21 r99 rows; the r99 allowlist entry +
gate; fixture byte-identity vs the frozen probes; the branch-vs-committed delta).
It reported **CONFIRMED on all five** (its own count: 483 line-start tuples + 2
mid-line tuples = 485; duplicate `crash_spontaneous_sigabrt` at indices 459/481;
the line-join at line 1403 present) and honestly disclosed that its substrate has
**no shell and no hashing tool**, so its fixture check was a full line-by-line
comparison, not a digest proof — this seat verified the digests independently
(`sha256sum`, below). It wrote nothing and spawned nothing.

---

## 0. Verdict

**VERIFIED — the 21 r99 rows and the laws they pin hold on the committed bytes.**
Two independent full-battery runs on a fresh `git archive` checkout of `254e79dd`
are **PASS 492/492, zero FAILs**, all 48 meta discriminations true, the
`r99_expected_errors_all_matched` floor true in both; 21/21 r99 cells re-derived
byte-exact in 63/63 fresh-process launches; the single r99 allowlist entry is
live-matched (2 lines) and load-bearing in all four directions; 21/21 expected-signature
mutations and 21/21 cross-arm signature swaps are rejected.

**Landing-integrity findings (F1/F2/F3 below) are recorded, not papered over: the
committed `run_battery.py` is not the byte stream the author measured.** The landed
file carries the r97/r98 blocks from main plus the r99 block, and it carries a
**duplicated `CASES` row**. Its committed sha256 is `fd2ed16c…`, the author's
declared pin is `71d38d91…` (the unlanded branch file). The commit message's
"green 447/447" describes the branch bytes; the landed bytes are green at
**492/492**. Both runs below measured the landed bytes, so the r99 verdict does not
depend on the author's numbers — but the r99 landing is not byte-faithful and the
duplicate row was never measured by the author or their labrat.

---

## 1. Method — frozen tree

```
git archive --format=tar 254e79dd | tar -x -C /tmp/r99-verify/tree   # attempted, quota-truncated
git archive --format=tar 254e79dd -- ':!corpus/live' | tar -x -C /tmp/r99-verify/tree   # exact, re-run
```

- **Full-tree content proof without materialization.** `git archive` was streamed
  through a verifier script (`/tmp/r99-verify/verify_stream.py`) that recomputes each
  entry's git blob sha1 and compares it to the committed blob id from
  `git ls-tree -r 254e79dd`:
  `tree_entries=125223, archive_regular_files=125155, archive_links=68, seen=125223,
  mismatch_count=0, missing_count=0, archive_exit=0`
  (`receipts/stream_verify.json`). No export filters, no substitutions.
- **On-disk extract.** The full 1.8 GB / 124 k-file `corpus/live` portion could **not**
  be materialized: `/tmp` is a 16 GB tmpfs mounted `usrquota`, and sibling lanes had
  exhausted it (inode use peaked at 1,015,713/1,048,576; `tar` wrote **zero-length
  stubs** for 764 non-live files and 119,145 `corpus/live` files — `receipts/stubbed-nonlive.txt`).
  After re-extracting `git archive 254e79dd -- ':!corpus/live'`, the non-live tree
  (1,079 files, 16,466,545 B = 15.7 MiB) is **byte-identical**:
  `GIT_WORK_TREE=/tmp/r99-verify/tree git diff --quiet 254e79dd -- . ':!corpus/live'` → **rc=0**.
  The battery-relevant subtree (`corpus/fixtures`, 100 files) is fully materialized and
  exact; the full tree is proven at the stream level above. This is a host-quota caveat,
  not a verification gap.
- **Fixture digests on the archived bytes** (`receipts/fixture_sha256_pre_run1.txt`,
  re-checked unchanged after run 1):
  | file | sha256 | author's declared pin |
  |---|---|---|
  | `corpus/fixtures/audio_lattice.gd` | `165571c410d506f14915326fd0806e9ff01e5056631620f565c9a7836a920baf` | **matches** (`165571c4…`) |
  | `corpus/fixtures/r99b_modes.gd` | `b680e6f297b7534d02a3bdc33337961062f9f0a79393b2a48798308785d38624` | **matches** (`b680e6f2…`) |
  | `corpus/fixtures/run_battery.py` | `fd2ed16c934ed251ae86bde64ece2b134db8c5652a0795a8e8724bf9437eeae8` | **differs** from `71d38d91…` (F2) |
  | `corpus/fixtures/project.godot` | `8de8b3af9cc737edc3e5969b76bf049720266537ec366e03aa42702aa15406e9` | unchanged |
  Both fixtures are also byte-identical to the frozen probes
  (`corpus/live/r99-scout/probes/audio_lattice.gd`, `corpus/live/r99-boundary/probes/r99b_modes.gd`)
  by `sha256sum`; the labrat's independent 773/453-line comparison agrees.

---

## 2. Landing-integrity findings

**F1 — the committed `CASES` list has 485 entries and one duplicated row.**
`receipts/landing_integrity.json`:

| tree | `CASES` | rows in run |
|---|---|---|
| `89f85ed8` (r96, author's branch base) | 419 | 426 (author's report) |
| `9d421fb2` (r98, landing parent) | 463 | — |
| author branch `fe1a996e` (worktree `…-wt-r99`) | 440 | 447 (author's runs A/B/C) |
| **`254e79dd` (committed)** | **485** | **492** (this seat, ×2) |

`crash_spontaneous_sigabrt` occurs **twice** (0-based indices 459 and 481; the second
shares a physical line with `crash_self_sigkill`). No r98 row was removed
(`rows_removed_vs_r98 = []`) and no preserved row's tuple changed
(`preserved_row_tuple_mismatches_vs_r98 = []`), so the landed delta is
`+21 r99 rows +1 duplicate`. The live runs execute the duplicate: both runs record
**two** `crash_spontaneous_sigabrt` rows, both `PASS`, both `exit=-6`, both carrying the
crash marker. Nothing downstream keys on row count or row identity
(`crash_records`/`process_records` are name-keyed dicts; no gate compares `len(results)`),
so the duplicate is a **hygiene defect with runtime cost only** (the SIGABRT probe runs
twice) — it is not a behavioural failure, and it is not green-by-omission either: it is
a row nobody authored or measured, now measured here (PASS in 4 in-battery executions).

**F2 — the author's declared `run_battery.py` digest is the unlanded branch file.**
`sha256` of the branch worktree file `…/game-dev-2d-shokunin-wt-r99/corpus/fixtures/run_battery.py`
(HEAD `fe1a996e`) is exactly the author's declared `71d38d91…`; the committed file is
`fd2ed16c…`. The author's fixtures match the commit byte-for-byte; only the harness differs.

**F3 — the committed harness diff is `+151/−2`, not `+150/−0`, because of a line-join.**
`git diff --numstat 254e79dd^ 254e79dd -- corpus/fixtures/run_battery.py` → `151  2`.
The two deletions are the parent's `…bounded=1'),    ("crash_spontaneous_sigabrt", …)`
line and the `("crash_self_sigkill", …)` line; the r99 block header was **appended to the
tail** of that first line and the two crash rows were re-emitted joined on one line. All
150 author-added lines are present in the committed file — 149 verbatim, the 150th (the
`# --- r99 block: the headless in-engine audio surface (r88's` header) present but joined
to the preceding line. All **21 r99 tuples are tuple-identical to the author's branch
rows**. The same artifact class already exists in the r98 landing (its `r98c_flush` line
is likewise joined with `crash_spontaneous_sigabrt`), so the join is a **landing-tool
behaviour**, not an author edit — reported as observation, not as a proven mechanism.

---

## 3. Full battery ×2 on the archived committed bytes

`python3 corpus/fixtures/run_battery.py` from the archive root, default launch shape
(`--headless`, no `--fixed-fps`/`--max-fps`, Dummy audio), per-case bound 8 s.

| rep | run dir | verdict | rows | FAILs | 48 meta gates | `r99_expected_errors_all_matched` |
|---|---|---|---|---|---|---|
| rep1 | `20261016T094354828019Z` | **PASS** (rc=0) | 492 | **0** | all true | **true** |
| rep2 | `20261016T095201841385Z` | **PASS** (rc=0) | 492 | **0** | all true | **true** |

- **Row arithmetic:** 485 `CASES` + 7 meta rows = 492 (measured, both reps).
- **r99 rows: 21/21 PASS in both reps** (`receipts/battery_runs_rep12.json` →
  `r99_verdicts`); every shipped signature matched its live output.
- **rep1 vs rep2:** identical case multiset, **zero** verdict/exit/signature/error
  mismatches, identical gate dicts. 32 rows differ only in incidental output text
  (timestamps, pids, ASLR'd crash addresses).
- **Census:** `rows_with_expected_errors=76`, **`dead_entry_count=0`**,
  `scan_clause_census={'SCRIPT ERROR:':0,'Parse Error:':0,'ERROR:_per_line_lines':160,'objectdb_leak_audio_lines':0}`.
- **Live-matched expected-error entry (r99).** `r99_audio_gen` is the only r99
  allowlist-bearing row. Live stderr is **462 B** in every execution, containing the
  allowlisted line **twice** — `ERROR: Condition "active" is true.` (from
  `clear_buffer` at `servers/audio/effects/audio_stream_generator.cpp:166`, GDScript
  sites `_arm_gen` `audio_lattice.gd:358` and `:363`). Census record:
  `{'entry': 'ERROR: Condition "active" is true.', 'shape': 'exact', 'matched_lines': 2,
  'first_match': 'ERROR: Condition "active" is true.', 'dead_in_run': False}`,
  `any_entry_matched=True`, `bare_classification_rejects=True`,
  `allowlisted_classification_passes=True`. The entry is live-matched, not dead.
- **Bytes measured, not assumed:** fixture digests were re-hashed after run 1 and are
  unchanged; the archive tree was extracted from the commit object, and the tree's
  non-live portion re-verified byte-identical to `254e79dd` before the runs.

---

## 4. Cell re-derivation — every r99 cell, fresh process, 3 reps

Harness `/tmp/r99-verify/rederive.py`: `CASES` and the allowlist are AST-extracted from
the **shipped** `run_battery.py` (sha256 `fd2ed16c…`), the classifier is the production
`classify_process` AST-extracted from the same file, and staging replicates `main()`
exactly (fixture copy, app-name munging, `pickup.tscn` staging, `causal_chain` readiness
fix); launch shape `godot --headless --path <scratch> --script res://<script> -- <flags>`,
8 s bound.

**21/21 cells PASS on all 3 reps — 63/63 launches**, every launch `rc=0` and every
shipped signature byte-exact in stdout (`receipts/rederive.json`):

| cell | reps | rc | stderr B | bare (no allowlist) |
|---|---|---|---|---|
| `r99_audio_gen` | 3/3 PASS | 0 | 462,462,462 | **0/3** (bare reject — entry load-bearing) |
| the other 20 cells | 3/3 PASS each | 0 | 0,0,0 | 3/3 |

---

## 5. Mutation / negative controls

All controls ran on the archived committed bytes; results in
`receipts/mutations.json`, `receipts/mutations_m4b.json`, `receipts/m5_floor.json`.

- **M1 expected-signature mutation — 21/21 discriminate.** One pinned token per row
  mutated (last token's value flipped), mutated signature verified **absent** from the
  live output, then re-classified with the production classifier: **21/21 FAIL**.
- **M2 allowlist load-bearing — 4/4 controls.** `r99_audio_gen` live bytes:
  shipped entry → PASS; **no** entry → bare reject; **forged** entry
  (`ERROR: some other diagnostic`) → reject; shipped entry + flipped signature → reject.
- **M3 cross-arm signature swap — 21/21 discriminate.** Each row's live output
  classified against its neighbour's shipped signature: **21/21 FAIL** (no vacuous or
  interchangeable pins).
- **M4 real-behaviour mutations.**
  | control | measured | verdict |
  |---|---|---|
  | baseline `--arm=census` | `mix_rate=44100 … max_fps=0` | PASS (control) |
  | `--max-fps 60` as an **engine** flag (flag verified effective: output `max_fps=60`) | `max_fps=60` | **FAIL** — the documented launch-shape coupling |
  | project setting `[audio] driver/mix_rate=48000` | output `mix_rate=48000` | **FAIL** — the row binds **real engine state**, not a constant |
  | fixture lie (`"mix_rate=%d" % 48000` in a scratch copy of `audio_lattice.gd`) | emitted `48000` | **FAIL** — the pin compares emitted bytes |
  | `r99b_mixfree --fixed-fps 120` | `all_jumps_q=true period_is_block=true` | PASS — the cap-free re-pin holds in a frame-capped launch |
  | `r99_audio_mixblock --fixed-fps 120` | `all_jumps_q=true block_jumps_ge6=false` | PASS — the surviving pin holds; the **folded** key is exactly the one that reads false |
  | `r99_audio_advance --fixed-fps 120` | `pos_after_gt_before=false` | **FAIL** — the frame-capped launch-mode scope the block comment documents |
- **M5 gate floor re-derived.** Reproducing the shipped census matcher on the live run:
  shipped entry → `matched_lines=2`, `dead_in_run=false`, gate **true**; a dead entry →
  `matched_lines=0`, `dead_in_run=true`, gate **false**. The `r99_expected_errors_all_matched`
  floor is load-bearing, and the row would bare-reject without its entry.
- **First (aborted) battery attempt, disclosed.** A first launch of the battery
  (09:22:54 UTC, run dir `20261016T092254075653Z`) died silently at row 172 with no
  traceback and no `verdicts.json` — it **measured nothing** and is not counted; the two
  reps above were relaunched under `setsid` at 09:43:54 and 09:52:01 UTC. Host load during
  the verified window was 3.6–12.5 (1-min average) with **sibling lanes running their own
  batteries** (`/var/tmp/r100-critic`, `/tmp/r100-scribe-archive`) and physics-heavy
  fixtures; both reps are still fully green, so no row is credited on a quiet-host claim.

---

## 6. What the 21 rows pin (spot-checked against live output)

18 `audio_lattice.gd` cells — the Dummy-driver census (`driver=Dummy mix_rate=44100
bus_count=1 bus_names=["Master"] out_devices=["Default"] tps=60`, `max_fps=0` as an
explicit launch-shape fact), bus add/route/effect readbacks with the silent invalid-name
fallback (`invalid_idx=-1`, `invalid_readback=Master`), autoplay-on-first-frame,
`stop()` zeroing, the peak dB scale (`-200.00` idle), the 128-frame quantum / 4096-frame
block / `0.092880 s` period with `all_jumps_q=true`, the Dummy mix clock advancing a live
playback, the finish transition with `pos_end=0.0000000`, default-points `LOOP_FORWARD`
self-termination vs explicit-point looping, generator capacity
`next_pow2(buffer_length·mix_rate)−1` (4095/8191/16383) with the refused `clear_buffer()`,
generator output mixed and 2D-panned, polyphony, live-vs-idle bus peak, the 2D
attenuation/pan lattice, and `pause` freezing. 3 `r99b_modes.gd` cells — the
five-cycle immediate 128-frame readback, the cap-free `all_jumps_q + period_is_block`
pair, and the cap-free `played_gt_02`. Each of the 21 was measured here in a fresh
process ×3 and in-battery ×2; nothing is reported green that was not executed.

---

## 7. Artefacts

- `corpus/live/r99-verifier/` — `battery_runs_rep12.json` (per-run verdict/rows/fails/r99
  verdicts/gates/census), `landing_integrity.json`, `stream_verify.json`,
  `rederive.json` + `.log`, `mutations.json`, `mutations_m4b.json`, `mutations.log`,
  `m5_floor.json`, `fixture_sha256_pre_run1.txt`, `fixture_sha256_post_run1.txt`,
  `author_branch_r99.patch`, `rep1.log`, `rep2.log`, `rep1.rc`, `rep2.rc`.
- Scratch: `/tmp/r99-verify/` (archived tree, scripts `verify_stream.py`, `rederive.py`,
  `mutations.py`, `m4b.py`).
- `reports/round-99/r99-verifier.md` — this report. **Nothing committed.**

## 8. Remaining risks / blockers

- **F1 duplicate row** — harmless to the verdict (name-keyed consumers, no count gates),
  but it is a landed artefact nobody authored. **Downstream context (read-only, not part of
  this verification):** a later commit on main, `9ede7c50` *"r97-r100 integration fix:
  dedupe crash sentinel CASES rows (509/509 unique)"*, removed exactly this class of glued
  duplicate (`CASES` at that commit = 509 tuples, 0 duplicates, `crash_spontaneous_sigabrt`
  ×1) and names the artifact "union-merge splice … flagged by r98-critic F1 … semantically
  inert (same row run twice) but broke CASES uniqueness and row-count arithmetic" — an
  independent corroboration of F1 on the same byte class. This report remains scoped to
  `254e79dd`, where the duplicate is present.
- **F2/F3 byte provenance** — the committed harness is not the author's measured stream;
  the author's `+150/−0`, `CASES 419 → 440`, `447/447` and `71d38d91…` describe the branch.
  Any future claim tied to the author's digests must be re-pinned to `fd2ed16c…` (or the
  file re-landed).
- **Launch-shape scope (measured here, not a defect):** the cap-bound cells fail under
  `--fixed-fps` (`advance` shown above), and `r99_audio_census` fails under `--max-fps`.
  The three `r99b_*` rows and the frozen `mixblock` pin survive the frame-capped launch.
- **Host caveat:** `/tmp` quota prevented materializing the full 125 k-file tree; the full
  tree is proven at archive-stream level and the non-live portion on disk, so the
  battery-relevant bytes are exact. Nothing in the verdict rests on a partially written file.
- **Blockers: none.**
