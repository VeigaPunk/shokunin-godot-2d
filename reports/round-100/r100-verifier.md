# r100 verifier — independent non-author verification of `2dcbb6f6` (committed bytes)

**VERDICT: VERIFIED-WITH-FINDINGS (VERIFIED-WR)** — the committed r100 lattice itself
verifies on the committed bytes: my own full battery run on a `git archive 2dcbb6f6`
extraction is **519/519 rows PASS** with all 25 r100 rows green, the r100 floor gate
`True`, and all 3 r100 allowlist entries live-matched; all 25 cells re-derive from the
committed signature bytes; 576/576 token mutations and 441/441 digit flips reject; 5/5
fixture-level behavioral mutants flip the row to FAIL; an independent fresh-process
re-run of all 25 arms is 75/75 PASS and line-for-line identical to the battery's captured
output. **The findings are about the landing's own report and hygiene, not about the
lattice's claims**: the committed harness executes **512 CASES rows (519 result rows)**,
not the 451 the author report and commit message claim, because the r100 patch was
re-applied onto the r99 base and **duplicated two crash-tail CASES tuples**
(`crash_spontaneous_sigabrt` now ×3, `crash_self_sigkill` ×2 — the r99 base already
carried the first duplicate); the "insertion-only +132/−0" claim is textually **+134/−2**;
and §8's "pyc restored to HEAD bytes" claim is false (the commit carries a regenerated
`__pycache__` blob that is nevertheless *consistent* with the committed harness). F1–F3 in
§8 are for the orchestrator; this seat makes no shipping decision. **F1 and F3 were repaired
upstream while this pass ran** (`9ede7c50` dedupe, `619ad7e0` pyc refresh — §3.1), which
corroborates the finding; the verification target stays `2dcbb6f6` as assigned.

Seat `VERIFIER` (g2d lane r100, independent non-author) | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, `--headless`, default 60 tps,
`DisplayServer.get_name()=="headless"`, 64×64 root viewport, `RendererDummy`), Python
3.14.7, 32 cores, `timeout 2400` bound on each battery run (8 s per-case bound internal to
the harness). Target: **`2dcbb6f6ed491e51aa76237b96f80c0b38fe607f`** (*r100 author: GUI/input
routing lattice (25 rows, +132/-0), green 451/451 x2*, parent `254e79dd` r99 author).
Receipts: `/var/tmp/r100-verify/**` (this seat's scratch, outside every lane worktree).
Author report `reports/round-100/r100-author.md`; sibling lane state read-only
(`game-dev-2d-shokunin-wt-r100`, branch `wt-r100` at `2d562282`) — used only for
provenance attribution in §3, never graded.

**`lsp` disclosure.** No `lsp` device in this session and no GDScript language server on
this host (unchanged lane state r89–r100): `definition`/`references`/`rename` were
**unavailable for every file** — the recorded fallback. No symbol-aware operation was
possible or required: the change is 4 new fixture files plus an insertion-only harness
block (no renames, no symbol moves). All semantic validation below is fresh-process
execution plus static reads of the committed bytes.

**Frozen probeParent disclosure.** Exactly one read-only `ufo-labrat` (L2, advisory,
writes nothing) was dispatched with one bounded six-clause read-only audit of the
committed bytes (25 r100 tuples and their distinctness; duplicate crash-tail names and
their counts; the 3 allowlist entries + gate shape; fixture↔frozen-probe text identity;
full-`PASS`-line signatures; tail ordering). Its result is reported in §7 and is
corroboration only — every load-bearing number below is re-derived on this seat's own
runs.

**Concurrent-work disclosures (shared host, honest load).** loadavg at run 1 start
`3.87 12.40 32.67`, at run 2 start `11.82 13.73 21.97` (the aborted first attempt started
at `15.32 13.32 24.17`); a foreign lane's mutant battery (`corpus/live/r97-verifier`,
pid 3815083, `ps` start 06:30) was running throughout, as were other lanes' worktrees.
Run 2 was **restarted once**: the first attempt died at row 230/519 when its launching
shell was reaped (empty stderr, no harness error); the re-run was detached (`setsid`) and
is the run 2 below. "Quiet" never means idle here. **Extraction-location deviation:** the
task said archive to `/tmp`; the first `/tmp` extraction died with
`tar: Cannot write: Disk quota exceeded` after ~231 MB because `/tmp` is a 16 GB tmpfs at
80 % full (`df`: 3.1 GB free) shared with concurrent lanes, so the pinned tree lives at
`/var/tmp/r100-verify/tree` (same root fs, 739 GB free). The pin is unchanged; only the
mount differs, and no concurrent lane's `/tmp` headroom was consumed.

---

## 1. Method — pinned committed tree

- `git archive 2dcbb6f6 | tar -x -C /var/tmp/r100-verify/tree` — whole-commit pin (not a
  fixtures-only slice): **125,160 files, 2.1 GB, 4.7 s**.
- **Blob identity** (`tools/blob_identity.py`): every `git ls-tree -r 2dcbb6f6` entry
  hashed as a git blob against the extracted bytes — **125,228/125,228 match, 0
  mismatches, 0 missing** (68 symlinks verified by link-text hashing);
  `corpus/fixtures` = 104 entries.
- **Fixture pins** (sha256, computed here on the committed bytes) match the author report
  §1 **exactly** and are byte-identical to the frozen probes (§4 H4):
  `r100_gui.gd` `dd826f6e…d073` (780 lines), `r100b_phase.gd` `49298e6c…d4b7` (520),
  `r100b_emul.gd` `31087e78…4960` (37), `r100b_seq.gd` `4718a19e…94dd` (790);
  `run_battery.py` `86a1aef8…dc90` (5,327 lines).
- **Commit scope** (`git show --stat`): 7 paths — the 4 new fixtures, the harness, the
  author report, and `corpus/fixtures/__pycache__/run_battery.cpython-314.pyc`
  (`Bin 443425 -> 457028`). Parent is `254e79dd` (r99 author), so the r100 delta on main
  is `git diff 254e79dd 2dcbb6f6` (the lane worktree's own `2d562282` sits on the r96 base
  `89f85ed8` and is *not* an ancestor of main's `2dcbb6f6`).

## 2. Harness delta `254e79dd → 2dcbb6f6` — measured, not asserted

- `git diff --numstat` = **134 insertions / 2 deletions** (commit message and author §4
  both say `+132 / −0`). The 2 deletions are a newline join: the crash-pair tuple line and
  the descendant tuple line are re-emitted as one line each with the r100 comment appended.
- **Tuple-level, AST-parsed CASES:** parent **485** → child **512** tuples; distinct names
  **484 → 509**. The 25 r100 tuples are contiguous at indices **483–507**, preceded by
  `r99b_finfree_played` and the crash pair (`crash_spontaneous_sigabrt` 481,
  `crash_self_sigkill` 482), followed by **another copy of the crash pair (508, 509)** and
  then `descendant_pipe_detached_control` (510) / `descendant_pipe_forged_signature_release`
  (511). `child[:483] == parent[:483]`; **0 r100 tokens in the parent**; 0 r100 fixture
  paths in the parent tree.
- **F1 — the landing duplicated two crash-tail rows.** Child duplicate names:
  `crash_spontaneous_sigabrt` ×3 (459, 481, 508) and `crash_self_sigkill` ×2 (482, 509),
  all copies byte-identical. Provenance: r96/r97/r98 have **0** duplicate names; **r99
  introduced the first duplicate** (`crash_spontaneous_sigabrt` at 459 and 481 — the same
  patch-re-application artifact, unflagged because no r99 verifier report exists in the
  lane repo or the r99 worktree); r100 added the second and third. Effect: the committed
  harness launches 512 cases + 7 meta probes = **519 result rows**, and the author's
  figures (444 CASES / 451 rows / "the final four CASES tuples are untouched") describe the
  **r96-based lane worktree**, not the committed bytes — the worktree harness
  (`wt-r100`, `2d562282`) really is 444 CASES / 444 distinct / 0 duplicates, and all 25 of
  its r100 tuples plus all 419 shared non-r100 tuples are **byte-identical** to the
  committed ones (so no row content was altered by the re-application; only the tail was).
- **Allowlist:** `expected_errors` gains exactly 3 entries / 3 strings, each the exact
  single line `ERROR: Parameter "t" is null.` for `r100_gui_render`, `r100b_seq_clean`,
  `r100b_seq_noclean`; parent has none of them.
- **Floor gate:** `r100_expected_errors_all_matched` over
  `case.startswith(("r100_gui_", "r100b_"))`, inside the `sf_discriminations` dict that
  `sf_meta_ok = all(sf_discriminations.values())` gates on — the same named-by-round shape
  as r87–r99; the parent has no r100 gate.
- **Block shape (hunk 1 = +110/−2, net +108 lines):** added line 1 is the crash-pair tuple
  re-emitted with the r100 comment appended (replacing deleted line 1 verbatim), lines 2–58
  are the 57 pure comment lines, lines 59–108 are the 25 r100 tuples (50 physical lines),
  line 109 is a **new** `crash_spontaneous_sigabrt` tuple, and line 110 is a **new**
  `crash_self_sigkill` tuple joined on the same physical line with the re-emitted
  `descendant_pipe_detached_control` tuple (replacing deleted line 2). Net new CASES
  tuples = 25 r100 + 2 crash copies = +27 (485 → 512). `python3 -m py_compile` clean.
- **Tail ordering constraint preserved:** the r88 note ("no CASES rows may sit between
  `descendant_pipe_detached_control` and the meta probes") still holds — the descendant row
  is the last-but-one CASES tuple and the meta probes follow the list.
- **pyc:** the committed `__pycache__/run_battery.cpython-314.pyc` (457,028 B, sha256
  `43b1a6de…dafe`) carries embedded source size 507,894 = the committed harness size, and
  its module code object is **equal** to a fresh `py_compile` of the committed harness →
  the blob is consistent with the committed bytes (so §8's "restored to HEAD bytes" is
  inaccurate but harmless; the *content* is right).

## 3. Full battery on the archived committed bytes

Command (per run, from the extracted tree root):
`python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot --runs <scratch>`
(`timeout 2400`), staging and run dirs outside every worktree.

| run | run dir | window (UTC) | rows | result |
|---|---|---|---|---|
| rep1 | `/var/tmp/r100-verify/runs-v/20261016T092223739395Z` | 09:22:23 → 09:30:54 | **519** | **PASS 519/519 — `PASS battery`**, rc=0 |
| rep2 | `/var/tmp/r100-verify/runs-v2/20261016T093456095598Z` | 09:34:56 → 09:44:50 | **519** | **PASS 519/519 — `PASS battery`**, rc=0 |

Both runs (`tools/extract_evidence.py`): `verdict=PASS`, `rows=519`, `pass=519`,
`fail=[]`; `r100_rows=25`, `r100_pass=25`, `r100_fail=[]`; `r100_floor_gate=true`;
`meta_verdict=PASS`; `rows_with_expected_errors=80`, `dead_entry_count=0`; duplicate case
names present in the results list = `crash_self_sigkill`, `crash_spontaneous_sigabrt`
(§2 F1, visible at the results level too). Every r100 row's pinned signature matched as a
**whole line** (25/25 `whole_line=true`) with `actual_exit == expected_exit`, in both runs.
Two green full-battery runs on the committed bytes at loadavg 3.9 and 11.8 respectively
(the author's own "451/451 ×2" receipts are for the r96-based worktree harness — §2).

### 3.1 Post-target repair landed during this pass (not covered by these runs)

While this pass was running, the lane repaired the duplicate rows upstream of my pinned
target: `9ede7c50` (*r97-r100 integration fix: dedupe crash sentinel CASES rows (509/509
unique)*, message: "Union-merge splice artifact flagged by r98-critic F1"), then `619ad7e0`
(*pyc refresh: src_size 507480 matches deduped source (r100-reviewer F4)*), HEAD
`2ac38451`. Measured on HEAD's bytes (static, `git show HEAD:corpus/fixtures/run_battery.py`):

- CASES **509 tuples / 509 distinct / 0 duplicate names**; the 25 r100 tuples are
  **byte-identical** to `2dcbb6f6`'s, all 484 shared non-r100 tuples are unchanged, the
  r100 block sits at CASES indices 480–504 with the tail order `… r100b_seq_noclean,
  crash_spontaneous_sigabrt, crash_self_sigkill, descendant_pipe_detached_control,
  descendant_pipe_forged_signature_release`, the 3 allowlist entries and the
  `r100_expected_errors_all_matched` gate are intact with the same prefix filter, and
  `2dcbb6f6..HEAD` touches only 5 harness lines (+3/−2) plus the refreshed pyc.
- **These runs do not cover the post-fix bytes**: both full batteries above are pinned to
  `2dcbb6f6` (the assigned target). A full-battery pass on `9ede7c50`/`2ac38451` bytes (509
  rows) is a *different* target and is left to the orchestrator / the next wave — the
  static delta above is what this seat can honestly assert about it.

## 4. Cell re-derivation (25/25)

Three independent legs, all on the committed bytes:

1. **Law re-derivation from the committed signature bytes** (`tools/rederive_laws.py`,
   `laws.json`): each of the 25 cells has an explicit law check that reads the *stimulus
   constants out of the committed fixture source* and predicts the pinned outcome. **25/25
   OK, 0 FAIL.** Examples: `r100_gui_drag` — fixture stimuli `rel=10.0` then `rel=10.5`
   with the strict `|relative| > 10` law predict `drag=0` then `drag=1`, matching the pinned
   `d1_at_threshold drag=0 calls=0` / `d2_over_threshold drag=1 calls=1`;
   `r100b_phase_dragphase` — `rel(+6)` then `rel(-6)` gives `|Σ|=0 ≤ 10` (no drag) while
   Σ|rel| = 12 would predict drag, and the pinned `dp_sign_same drag=0 calls=0` matches the
   net-sum law only; `r100b_phase_velphase` — 14 velocity samples, all `(0.0, 0.0)`;
   `r100b_phase_dblclick` — 9 `double_click` fields, all 0; `r100b_phase_orderin` — 6
   interleaved callback logs, `_input` copy before `_gui_input` copy in every one;
   `r100b_seq_clean` / `r100b_seq_noclean` — the replayed cursor/hover cells diverge from
   their single-cell values (`c0=(30.0,14.0)` vs `(0.0,0.0)`; `h0=P` vs `h0=null`).
2. **Independent fresh-process re-run** (`tools/rederive.py`, own staging that replicates
   the harness's whole-fixture copy, `config/name` munging, `pickup.tscn` staging and the
   scratch-only 2-frame `causal_chain.gd` readiness patch; production classifier extracted
   **verbatim** from the committed harness via AST → source → `exec`): **25 arms × 3 reps =
   75/75 PASS, 0 failures**, 56 s. Receipts `rederive/20261016T093508264727Z/`.
3. **Cross-environment line identity**: the signature line captured *inside* the battery
   vs the same case's line in this seat's own fresh-process receipt —
   **25/25 line-for-line identical, 0 mismatches** in two different scratch environments.

## 5. Mutation and negative controls

Classifier-level (`tools/mutants.py`; production clause verbatim; run twice, once against
the battery's captured output and once against this seat's fresh-process output — **both
sources give identical numbers**):

| control | mutations | rejected |
|---|---|---|
| per-token signature mutation (append `Z` to each whitespace token) | 576 | **576/576** |
| first-digit flip inside each digit-bearing token | 441 | **441/441** |
| foreign `ERROR:` line prepended to a non-allowlisted PASS row's output | 22 rows | **22/22** |
| allowlist live-match (committed entry present) | 3 rows | **3/3 PASS** |
| allowlist *bare* classification (entry removed) | 3 rows | **3/3 reject** |
| allowlist dead-entry detection (entry mutated to `…nullX.`) | 3 rows | **3/3 reject** |

Method note (a negative control on my own method): prefix/truncated signatures
(50 of them) still classify PASS **by construction** — `classify_process` is a substring
test, so any prefix of a true signature matches. Truncation is therefore not a
discriminator; the load-bearing sensitivity evidence is the per-token leg (576/576) plus
the 25/25 whole-line equality in §3.

Fixture-level **behavioral** mutants (`tools/fixture_mutants.py`; one source edit each,
fresh Godot process, committed signature must be absent = the row would FAIL) —
**5/5 REJECT**:

| mutant (case) | one-line behavioral edit | mutant's own measured line (excerpt) | committed line (excerpt) |
|---|---|---|---|
| `dragphase_net_sum` (`r100b_phase_dragphase`) | second sign-test motion `rel(-6,0)` → `rel(+6,0)` | `dp_sign_same drag=1 calls=1` | `dp_sign_same drag=0 calls=0` |
| `cursorphase_no_flush` (`r100b_phase_cursorphase`) | drop the explicit `Input.flush_buffered_events()` after the first parsed motion | `mm_flush=(0.0, 0.0) mm_f1=(20.0, 20.0)` | `mm_flush=(20.0, 20.0)` |
| `gui_drag_threshold_boundary` (`r100_gui_drag`) | d1 stimulus `rel(10,0)` → `rel(10.5,0)` | `d1_at_threshold drag=1 calls=1` | `d1_at_threshold drag=0 calls=0` |
| `gui_routing_right_button` (`r100_gui_routing`) | right-button event → left-button event | `s9_rb[-][P:mb(b=1,…)]` | `s9_rb[-][P:mb(b=2,…)]` |
| `emul_release_becomes_press` (`r100b_emul_state`) | second ScreenTouch release → press | `touch_release held=1 … second_press cursor=(44.0, 44.0)` | `touch_release held=0 … second_press cursor=(10.0, 10.0)` |

In-harness floor-gate mutant (does the r100 gate actually fail when an entry dies?):
a one-line mutant harness (`r100_gui_render` entry `…null.` → `…nullX.`) was prepared at
`/var/tmp/r100-verify/mutant-deadentry/fixtures/run_battery.py` (exactly 1 line differs)
and run as a full battery — **it FAILS exactly as the gate predicts** (§7.1).

Negative controls on the *landing* itself: the parent tree `254e79dd` contains **0** r100
CASES tokens and **0** `corpus/fixtures/r100*` paths (the rows and fixtures are genuinely
new); the committed harness's 25 r100 tuples are byte-identical to the lane worktree's
(so the re-application altered no row).

## 6. Expected-error entries — live-matched

From each run's own census (`probe_error_clause_surface` → `census`; rep1 shown, rep2
identical in every cell), for each of the three allowlisted cases:

| case | entry | matched_lines | dead_in_run | bare_classification_rejects | allowlisted_classification_passes | raw occurrences in that case's output | `ERROR:` lines in that case's output |
|---|---|---|---|---|---|---|---|
| `r100_gui_render` | `ERROR: Parameter "t" is null.` | 1 | false | true | true | 1 | 1 |
| `r100b_seq_clean` | `ERROR: Parameter "t" is null.` | 1 | false | true | true | 1 | 1 |
| `r100b_seq_noclean` | `ERROR: Parameter "t" is null.` | 1 | false | true | true | 1 | 1 |

i.e. each entry is **live** (matched exactly once, not a dead allowlist line), each is
**needed** (removing it makes the row's bare classification reject), and no unrelated
`ERROR:` line hides behind the entry in any of the three cases. Battery-wide:
`rows_with_expected_errors=80`, `dead_entry_count=0`, `dead_entries=[]`.

## 7. Independent probe + in-harness mutant

### 7.1 In-harness dead-entry mutant (gate load-bearing)
A one-line mutant harness (`r100_gui_render` allowlist entry `…null.` → `…nullX.`; exactly
1 line differs from the committed file) was run as a **full battery** from its own fixture
copy (`/var/tmp/r100-verify/mutant-deadentry/fixtures/run_battery.py`,
run dir `/var/tmp/r100-verify/runs-mutant/20261016T094502189139Z`, 09:45:02 → 09:53:15,
519 rows):

- **verdict FAIL**, and exactly **two** rows fail: `FAIL r100_gui_render` (the case whose
  entry was mutated) and `FAIL error-clause surface meta` (the gate row). All 24 other r100
  rows stay PASS, including the two sibling allowlist rows (`r100b_seq_clean`,
  `r100b_seq_noclean`: `matched_lines=[1]`, `dead_in_run=[false]`) — the blast radius is
  exactly the mutated entry.
- `discriminations`: only two false — **`r100_expected_errors_all_matched: false`** and
  `census_bare_classifier_consistent: false`; census `dead_entry_count=1` with
  `dead_entries=[{"case":"r100_gui_render","entry":"ERROR: Parameter \"t\" is nullX.",
  "shape":"exact"}]`, and that case's census entry is `matched_lines=0`,
  `dead_in_run=true`, `allowlisted_classification_passes=false`.

So the r100 floor gate is not decorative: kill one r100 allowlist entry and the gate row
plus the affected case go red, while a *live* entry is exactly what keeps them green (§6).

### 7.2 Frozen probeParent labrat (one, read-only, advisory)
One `ufo-labrat` (L2, agent `9ceacfe3`) returned **6/6 clauses CONFIRMED** on the committed
bytes, reading every file end-to-end (it reports no shell/hash tool, so identity was proven
by full line-wise reads, not sampling — its own stated caveat, and this seat's sha256 table
in §1 is the digest leg):
H1 the committed harness carries exactly 25 r100 CASES tuples, 25 distinct names, at file
lines **1593–1641**; H2 `crash_spontaneous_sigabrt` appears **3×** (L1403, L1535, L1643) and
`crash_self_sigkill` **2×** (L1535, L1644) — the crash tail re-emitted ahead of and after
the r100 block (F1 corroborated at file-line precision); H3 the three allowlist entries at
**L2221–2229** are each the exact single string `ERROR: Parameter "t" is null.` and the gate
at **L4009–4013** filters `("r100_gui_", "r100b_")`; H4 all four fixture↔frozen-probe pairs
are line-for-line identical (780/520/37/790 lines); H5 all 25 signatures are full `PASS`
lines and pairwise distinct (the two seq rows intentionally carry `PASS r100_gui cursor …`
/ `PASS r100_gui hover …` because the seq probe replays gui cells); H6 the last four CASES
names in order are `crash_spontaneous_sigabrt`, `crash_self_sigkill`,
`descendant_pipe_detached_control`, `descendant_pipe_forged_signature_release` — detached →
forged remain the last two, no r100 tuple after them. Advisory only; it wrote nothing.

## 8. Remaining risks / findings for the orchestrator

- **F1 (hygiene, real, cheap to fix): the committed r100 landing duplicates two crash-tail
  CASES tuples.** `crash_spontaneous_sigabrt` ×3 and `crash_self_sigkill` ×2 in
  `corpus/fixtures/run_battery.py`; the battery therefore runs 519 rows, launches the
  SIGABRT probe three times and the SIGKILL probe twice per run, and the results list
  carries duplicate case names. The lattice's own claims are unaffected (all 25 r100 rows
  pass; no r100 row is duplicated), and the duplicates are byte-identical tuples, so this
  is a hygiene/claim-fidelity defect rather than a broken guarantee. The fix is deleting
  the 2 re-emitted tuples — file lines **1643** (`crash_spontaneous_sigabrt`) and **1644**
  (`crash_self_sigkill`, joined on the same line with `descendant_pipe_detached_control`) in
  `corpus/fixtures/run_battery.py`, leaving exactly one copy of the crash pair (either
  placement satisfies the r88 descendant→meta adjacency) — **not done by this seat** (no
  tracked writes). **Status: repaired upstream while
  this pass ran** (`9ede7c50`, "Union-merge splice artifact flagged by r98-critic F1", which
  also removes the r99 copy; HEAD is 509/509 unique — §3.1). The finding stands as a true
  statement about the assigned target `2dcbb6f6`.
- **F1b (process, for the orchestrator): the same artifact hit r99 first.** Two consecutive
  landings (r99, r100) were re-applied onto a newer base and each re-emitted a trailing
  context tuple; the r99 instance was flagged only later, by **r98-critic F1**, and repaired
  at `9ede7c50`. A cheap standing control is an
  AST-level "CASES names are distinct / count matches the claimed row count" check in the
  verifier lane, and/or applying author patches with an explicit tuple-level assertion.
- **F2 (claim fidelity): the author report and commit message describe the r96-based lane
  worktree, not the committed bytes** — `444 CASES / 451 rows / +132 −0 / "final four CASES
  tuples untouched"` vs committed `512 CASES / 519 rows / +134 −2 / two extra crash tuples`.
  The 451-row "green ×2" receipts are real *for the worktree harness*; the committed harness
  had never been run end-to-end before this pass (rep1/rep2 here are its first full runs).
- **F3 (claim fidelity, harmless): §8's "pyc restored to HEAD bytes after the final run" is
  false** — the commit carries a regenerated pyc (`443425 → 457028` B). It is *consistent*
  with the committed harness (module code equal to a fresh compile; embedded source size =
  committed size), so nothing downstream is misled; only the sentence is wrong. **Status:
  the pyc was refreshed again at `619ad7e0` for the deduped source (507,480 B) — §3.1.**
- **R1 (inherited, not r100's): the battery is load-conditional at this HEAD.** The r89–r100
  documented family (`negative_transition` + the `probe_error_clause_surface` census
  coupling) is untouched by the r100 block (the 4 new fixtures never call
  `change_scene_to_*`), and both of this seat's runs were green on the committed bytes; but
  the host ran at loadavg 4–15 with a foreign mutant battery alongside, so a future red
  battery on that row family is expected occasionally and is not evidence against r100.
- **R2 (engine/host pinning): every value is this host / Godot
  `4.7.2.stable.arch_linux.ed1daf0bf` / `--headless` / 64×64 root viewport / identity
  transform.** The `render`/`seq` allowlist line is the `RendererDummy` backbuffer-readback
  diagnostic text and is engine-version pinned like the corpus's other allowlist entries.
- **R3 (single-cell-per-process by construction): the `r100b_seq_*` rows deliberately pin
  contamination.** If a future engine makes the cells composable (or the cursor /
  emulated-button state resettable), those two rows FAIL loudly — the correct failure for a
  changed claim. The tracked battery launches one fresh process per case, so the other 23
  rows are unaffected either way.
- **R4 (cosmetic): the r100 block's own comment header is accurate for the committed
  bytes** ("Rows inserted ahead of the crash/descendant tail — descendant_pipe_detached_control's
  sleep-8 gap stays adjacent to the meta probes"), and the r88 ordering constraint it cites
  holds (labrat H6). Only the author report's prose anchor ("after `r96b_seed_seedcheck`")
  fails to describe the committed file, where the block sits after the r99 rows — folded
  into F2.
- **Blockers: none.** This seat wrote no tracked file in the lane repo except this report;
  no commits, no pushes, no lane-worktree mutations; the pinned extraction lives outside
  every worktree; no stray Godot processes were left behind by this seat.

## 9. Evidence index (exact paths)

- Pinned tree: `/var/tmp/r100-verify/tree` (blob-verified `git archive 2dcbb6f6`;
  125,228/125,228 blobs).
- Tools (this seat): `/var/tmp/r100-verify/tools/{blob_identity,harness_delta,rederive,
  rederive_laws,mutants,fixture_mutants,extract_evidence}.py`.
- Battery runs: `/var/tmp/r100-verify/runs-v/20261016T092223739395Z/verdicts.json`
  (+`battery-rep1.out|err`, `rep1.start` with UTC window and loadavg); run 2 =
  `/var/tmp/r100-verify/runs-v2/20261016T093456095598Z/verdicts.json`
  (+`battery-rep2b.out|err`, `rep2b.start`); the aborted first attempt's partial run dir is
  `runs-v2/20261016T093100037354Z` (killed at row 230, kept as-is).
- In-harness dead-entry mutant: `/var/tmp/r100-verify/runs-mutant/20261016T094502189139Z/`
  (+`battery-mutant-deadentry.out|err`, `mutant-deadentry.start`).
- Post-target repair delta (static, git-side): `git diff 2dcbb6f6 HEAD -- corpus/fixtures/`
  in the lane repo; HEAD `2ac38451` (`9ede7c50` dedupe, `619ad7e0` pyc refresh).
- Fresh-process re-derivation: `/var/tmp/r100-verify/rederive/20261016T093508264727Z/`
  (`rederive.json`, 75 receipts `<case>.rep{1,2,3}.{out,err,rc}`).
- Laws: `/var/tmp/r100-verify/laws.json`; mutations:
  `/var/tmp/r100-verify/{mutants,mutants-battery,mutants-fresh,fixture-mutants}.json`;
  signatures/flags: `/var/tmp/r100-verify/{signatures,flags}.json`.
- Evidence summary: `/var/tmp/r100-verify/evidence-summary.json`.
- Harness delta: `/var/tmp/r100-verify/harness.diff`; dead-entry mutant harness:
  `/var/tmp/r100-verify/mutant-deadentry/fixtures/run_battery.py`; fixture-mutant scratches:
  `/var/tmp/r100-verify/mutants-fixture/<mutant>/`.
