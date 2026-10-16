# r99 reviewer — PASS-WR on **254e79dd**: the 21 audio rows are independently re-derived green on the committed bytes, but the report's artefact hash / diff shape / row arithmetic describe the author's **pre-landing branch** (`fe1a996e`), and the landing duplicated one `CASES` row

Seat `REVIEWER` (g2d lane `r99-reviewer`) | round 99 | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, `--headless`, Dummy audio
driver, mix rate 44100, 60 physics tps).

**Commit verified: `254e79dd81202b2f25b3064681c96d95a37ccdfe`** ("r99 author: headless audio
lattice (21 rows, +150/-0), green 447/447", parent `9d421fb2` = r98). The lane HEAD
advanced twice while this review ran: `2dcbb6f6` (r100 author) and then `9ede7c50`
("r97-r100 integration fix: dedupe crash sentinel CASES rows (509/509 unique)",
06:34:32). Per the dispatch ("Author landing: 254e79dd") this review is of the r99
landing; the author's own branch commit `fe1a996e` (parent `89f85ed8` = r96) and the
integration fix matter below — the fix removes exactly the duplicate row this review
found (F2), and leaves all 21 r99 rows byte-identical.

**Method.** Fresh archive checkout of the commit, not the author's worktree:
`git archive 254e79dd | tar -x --exclude='corpus/live/*' -C /tmp/r99rev`. All 1079
tracked blobs outside `corpus/live` were re-hashed with `git hash-object` against
`git ls-tree -r 254e79dd` (0 mismatches, 0 missing). `corpus/live` (≈1.7 GiB) is
excluded because `/tmp` is a quota-bound tmpfs and the first full extraction died on
`Disk quota exceeded`; the fixtures needed by the battery are all in the 18 MiB kept.
Battery run outputs were written to `/home/vgpnk/r99-review/runs/`. Evidence copied to
`corpus/live/r99-reviewer/` (untracked; nothing committed).

**`lsp` disclosure.** No `lsp` device in this session and no GDScript/Python language
server on this host, so `references`/`definition`/`diagnostics` were unavailable for
every file. The carrier set here is small and self-contained (one fixture pair + one
`CASES` list + one classifier inside `run_battery.py`), so I used the semantic tools
that *are* available and reproducible: Python `ast` (tuple identity, occurrence
counts, `ast.get_source_segment` for the classifier), `git hash-object` blob identity,
and fresh-process launches through the shipped classifier. Every claim below cites the
command or artefact that produced it; nothing rests on text grep.

---

## 0. Verdict

**PASS-WR.** Every shipped row is real and green on the committed bytes, and every
*measurement* claim in `r99-author.md` that I could re-derive reproduced exactly
(21/21 rows, 267/267 battery-shape receipts, 204/210 paced, 113/222 unpaced, fixture
byte-identity, classifier-segment identity). What does **not** hold is the report's
description of the artefact it shipped: the pinned `run_battery.py` hash, the
"insertion-only +150/−0" diff shape, and the "CASES 419 → 440 / rows 426 → 447"
arithmetic are all true of `fe1a996e` and false of `254e79dd`. The landing additionally
contains one unintended duplicate `CASES` row. None of that produces a false green —
it produces a custody gap and a duplicated instrument, which the adjudicator should
either have removed or explicitly accept.

| # | finding | severity |
|---|---|---|
| F1 | pinned battery sha256 is the author-branch blob, not the committed blob | **high** |
| F2 | landed diff is `+151/−2` (not insertion-only) and duplicated a `CASES` row | **high** |
| F3 | row arithmetic (419→440 / 426→447) describes the pre-landing branch; landed is 463→485 / 492 rows | medium |
| F4 | shipped comment claims "1185/1185 receipts"; the seat's own artefact totals 471/477 | low |
| F5 | `r99b_finfree_played` / `r99b_mixfree` pins are bare key substrings that can pass vacuously | low |
| F6 | tracked `__pycache__/*.pyc` binary churn rides the commit | info |

---

## 1. Re-derivation of the author's claims against committed bytes

| claim (`reports/round-99/r99-author.md`) | verdict on `254e79dd` | evidence |
|---|---|---|
| `audio_lattice.gd` is a byte-copy of the frozen scout probe (`165571c4…`) | **CONFIRMED** | `git show 254e79dd:corpus/fixtures/audio_lattice.gd \| sha256sum` = `165571c410d506f14915326fd0806e9ff01e5056631620f565c9a7836a920baf`; identical in `r99-scout/probes/`, `r99-scout/proj/`, `r99-boundary/probes/`, `r99-boundary/proj/`, `r99-boundary/proj2d/` |
| `r99b_modes.gd` is a byte-copy of the frozen boundary probe (`b680e6f2…`) | **CONFIRMED** | committed = `b680e6f297b7534d02a3bdc33337961062f9f0a79393b2a48798308785d38624`; identical in `r99-boundary/probes/`, `proj/`, `proj2d/` |
| the classifier segment is the same one r89–r97 pinned (`749fa060…`) | **CONFIRMED** | `ast.get_source_segment(src, classify_process)` on the committed file → `749fa0607e7707e614c1ab157a6f8e756dfc2f460746e6d218e6734ad8fa72c3` (same on `fe1a996e`) |
| 21 rows: 18 scout cells + 3 boundary law rows | **CONFIRMED** | `ast.literal_eval(CASES)` filter `r99_audio_`/`r99b_` → exactly 21 tuples; all 21 identical (tuple-for-tuple) between `fe1a996e` and `254e79dd`, and all 440 shared tuples identical |
| the r99 allowlist entry + the `r99_expected_errors_all_matched` gate | **CONFIRMED** | identical text at both revisions; the gate rides `probe_error_clause_surface.discriminations` and is `True` in my run |
| fresh-process smoke 21/21 PASS, gen stderr 462 B, 0 B elsewhere | **CONFIRMED (my own run)** | `/tmp/r99rev_smoke.py` (my launcher, shipped classifier AST-extracted, 8 s bound, battery launch shape): 21/21 PASS, every signature on stdout, `gen` stderr = 462 B = the two exact `ERROR: Condition "active" is true.` lines, 0 B on the other 20 → `corpus/live/r99-reviewer/smoke-21rows.log` |
| receipt survival: 267/267 battery-shape, 204/210 paced, 113/222 unpaced | **CONFIRMED (independently replayed)** | my replayer (`r99rev_receipt_replay.py`) over the surviving receipts with the *shipped* pins + *shipped* classifier: scout-canon 93/93, scout-load 54/54, boundary quiet 60/60, load 60/60 = **267/267**; paced (maxfps30/60/120, single, proj2d) **204/210**, the only rejects being `r99b_census` ×2 reps ×3 maxfps modes (the documented `max_fps=30/60/120` launch-shape coupling); unpaced (ff30/60/120/1) **113/222**; `ff30slow` 13/36 (inert control, no rows) → `corpus/live/r99-reviewer/receipt_replay_all_modes.txt` |
| `invalid_idx=-1` on the frozen bytes; the single `0` is a pre-freeze probe revision | **CONFIRMED** | 46 surviving receipts read `invalid_idx=-1`, exactly one reads `0`; my fresh `bus` launch reads `-1` (47th) |
| the battery launches with no `--fixed-fps`/`--max-fps`; the block sits ahead of the crash/descendant tail | **CONFIRMED** | launch command construction (`--headless --path <scratch> --script res://…`), block between `r98c_flush` and the crash rows |
| "no law is lost by the folds" | **CONFIRMED as stated** | `period_is_block` re-pinned by `r99b_mixfree`; `played_gt_02` re-pinned by `r99b_finfree_played`; `block_jumps_ge6`/`fin_same_frame` were refuted as laws by the boundary and are deliberately unpinned (I replayed the boundary receipts and reproduced the flips: e.g. `ff30`/`ff60`/`ff120` `r99b_mixfree`/`r99b_finish` rejects) |
| **artefact sha256 `71d38d91…` for `run_battery.py`** | **FALSE for the commit** | see F1 |
| **"insertion-only `+150/−0`"** | **FALSE for the commit** | see F2 |
| **"CASES 419 → 440; result rows 426 → 447"** | **FALSE for the commit** | see F3 |
| **"Accepted 1185/1185 receipts…" (shipped comment)** | **UNSUPPORTED** | see F4 |

---

## 2. Findings

### F1 — high — the report's pinned `run_battery.py` hash is not the committed file

```
committed  254e79dd : fd2ed16c934ed251ae86bde64ece2b134db8c5652a0795a8e8724bf9437eeae8
author     fe1a996e : 71d38d91871a14667da955263e1695cc5392d6e99d3fca399098dc2d988b7829
report claim        : 71d38d91871a14667da955263e1695cc5392d6e99d3fca399098dc2d988b7829
```

`git show <rev>:corpus/fixtures/run_battery.py | sha256sum` for both revisions
(`corpus/live/r99-reviewer/claims_vs_committed.txt`). `fe1a996e` is the author's own
branch commit ("r99 author: audio lattice 21 rows (+150/-0), green 447/447", parent
`89f85ed8` = r96, branch `wt-r99`, still present as a worktree). The landed commit
`254e79dd` is a *different* commit with a different message, re-created on top of r98.

Consequence: the report's evidence chain (hash → smoke/battery receipts → green) is
anchored to bytes that were never the landed bytes. A reader who verifies the commit
by the report's hash gets a mismatch; the three battery runs cited (A/B/C) were run in
the author's worktree against the author-branch blob — their `rows = 447` is the
author-branch count, and their receipts live in `wt-r99/`, not in the lane repo. This
is a landing/claim provenance failure, not a row failure — the row content is identical
between the two revisions (see F2), which is why the battery still passes on the
committed bytes.

### F2 — high — the landed diff is not insertion-only, and the reflow duplicated a `CASES` row

```
$ git diff --numstat 254e79dd^ 254e79dd -- corpus/fixtures/run_battery.py
151     2       corpus/fixtures/run_battery.py
```

The report says `+150 / −0` (`git diff --numstat`). The two deletions are the anchor
lines that the landing reflowed: the `r98c_flush` signature line (which gained the r99
comment head) and the `crash_self_sigkill` tuple line (which was joined onto the
previous line). The reflow is not content-neutral — it **duplicated** the sigabrt row:

```
9d421fb2 (r98, parent)  CASES-tuple occurrences: {'crash_spontaneous_sigabrt': 1, 'crash_self_sigkill': 1}
fe1a996e (author)       CASES-tuple occurrences: {'crash_spontaneous_sigabrt': 1, 'crash_self_sigkill': 1}
254e79dd (landing)      CASES-tuple occurrences: {'crash_spontaneous_sigabrt': 2, 'crash_self_sigkill': 1}
```

(occurrence counts from `ast.literal_eval(CASES)` per revision —
`corpus/live/r99-reviewer/crash_row_occurrences.txt`; the row text at committed lines
1403 and 1535 is byte-identical: `("crash_spontaneous_sigabrt",
"spontaneous_crash_probe.gd", ["--spontaneous-crash"], -6, "SPONTANEOUS_CRASH_PROBE:
expected signature")`).

Observed behaviour change on the committed bytes (my full battery run): the sigabrt
crash probe is launched **twice** per run and yields **two** result rows named
`crash_spontaneous_sigabrt` (and two census rows). `crash_records` is a name-keyed
dict, so the crash meta row keeps the last record and no gate breaks — but the block's
real row delta is +22, not +21, and one of the two instruments is redundant.

**This is systemic, not r99-private, and it is now corroborated by the fleet's own
repair:** the same landing pattern compounded in r100 (`2dcbb6f6` has
`crash_spontaneous_sigabrt` ×3, `crash_self_sigkill` ×2), and integration commit
`9ede7c50` ("Union-merge splice artifact flagged by r98-critic F1: …
crash_spontaneous_sigabrt appeared x3 and crash_self_sigkill x2 after serial union
landings. Semantically inert (same row run twice) but broke CASES uniqueness and
row-count arithmetic") removed the glued duplicates, leaving 509 unique tuples with the
21 r99 rows byte-identical (my AST check). So the defect class is confirmed by a second
seat and repaired at HEAD; what remains for r99 is that the *landing under review*
(`254e79dd`) carries it, and that the landing step which produces it is the same step
that made the report's hash/diff-shape claims wrong.

### F3 — medium — the row arithmetic describes the pre-landing branch

| revision | CASES | +meta (7) | report/commit-message claim |
|---|---|---|---|
| `89f85ed8` (r96) | 419 | 426 | "CASES 419 → 440; rows 426 → 447" ← the author's *base* |
| `f67094bb` (r97) | 431 | 438 | — |
| `9d421fb2` (r98) | 463 | 470 | the true parent of the landing |
| `fe1a996e` (author branch) | **440** | **447** | what the report measured (and what the commit message repeats) |
| `254e79dd` (landing) | **485** | **492** | what is actually on main |

My full battery on `254e79dd` emitted **492 rows** (485 cases + 7 meta), consistent with
the table. The commit message "green 447/447" and the report's "CASES 419 → 440" are
therefore statements about `fe1a996e`; on the landing the honest numbers are 485 cases /
492 rows (+22 cases, one of them the F2 duplicate).

### F4 — low — an unsupported number ships inside the block comment

The committed comment says "Accepted 1185/1185 receipts at the battery launch shape and
every paced / threaded mode". The seat's own `receipt_survival.json` totals (which I
reproduced exactly) are 267/267 + 204/210 = **471/477**; the corpus holds 699 r99
receipts in total. No artefact produces 1185. Comment-only, but it is a claim in
committed bytes and it is the kind of number a later round will cite.

### F5 — low — two boundary pins are bare key substrings that can pass vacuously

* `r99b_finfree_played` pins `played_gt_02=true` alone — no `PASS r99b` anchor and none
  of its sibling keys (`stopped`, `finished_seen`). A regression where the 0.3 s stream
  plays past 0.2 s but the `finished` signal never fires would still PASS this row. The
  transition itself is separately pinned by `r99_audio_finish`
  (`stopped=true playing_end=false pos_end=0.0000000 finished_seen=true`), so no law is
  lost — the row is just weaker than its siblings.
* `r99b_mixfree` pins `all_jumps_q=true period_is_block=true`; `all_q` starts `true` and
  is only falsified inside the observed-delta branch, so an arm that observes **zero**
  jumps (frozen clock) still prints both keys true and PASSes. The block's
  anti-frozen-clock key lives in another row: `r99_audio_advance`'s
  `pos_after_gt_before=true` (my fresh run: before `0.0029025` → after `0.2815419`).

Neither is a false green in this run (my fresh `r99b_finfree_played` output is
`stopped=true playing_end=false pos_end=0.0000000 finished_seen=true fin_same_frame=true
played_gt_02=true`; my fresh `r99b_mixfree` is `blocks=8 blocks_ge6=true sub=0 other=0
hist={4096:8}`), but both pins admit degenerate payloads that the author's prose claims
they exclude.

### F6 — info — tracked bytecode churn

`corpus/fixtures/__pycache__/run_battery.cpython-314.pyc` is tracked and changes in the
commit (as in every round's commit; `9ede7c50` rewrote it again via `py_compile`, which
is the ` M` it leaves in `git status`). Harmless — the battery is executed as a script,
so the cache is never consulted — but it is binary noise in the custody chain and in
every round's diff.

---

## 3. Independent re-derivation — the run that carries the verdict

**Full battery, committed bytes, one pass** (the contract's command, archive tree):

```
cd /tmp/r99rev && python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot \
    --runs /home/vgpnk/r99-review/runs        # rc=0
```

* run `20261016T093530209921Z/verdicts.json`: **492 rows, 0 FAIL, payload `verdict:
  PASS`** (`corpus/live/r99-reviewer/verdicts_C.json`).
* all **21 r99 rows PASS**; `r99_expected_errors_all_matched` = `true`; every
  discrimination in `probe_error_clause_surface.discriminations` = `true`;
  `dead_entry_count = 0`; `r99_audio_gen` census entry `matched_lines = 2`,
  `dead_in_run = false`; the duplicate row appears as `crash_spontaneous_sigabrt` ×2
  in both `results` and `census.rows` (F2's behavioural footprint).
* no pre-existing flake fired in this pass (`transition`, `negative_transition`,
  `probe_error_clause_surface` were all PASS) — the landing's green is not merely the
  author's runs A/B luck.
* second, independent instrument: the 21-row fresh-process smoke above (different
  launcher, same shipped classifier) → 21/21, and the receipt replay → 267/267 +
  204/210 + 113/222.

**Load / host caveats (honest).** The host was shared and busy for the whole review:
sibling lanes ran concurrent full battery passes throughout (≥8 distinct
`run_battery.py` invocations observed at 06:29, each with its own `timeout` wrapper —
r97-simplifier, r97-verifier, r98-scribe, r98-review, r100-reviewer, r100-scribe,
r100-author); loadavg was 10–16 at 06:26–06:44; I added **0** `yes` hogs (host
`pgrep -c yes` = 0 when sampled). Two of my three full-battery attempts died mid-run
without a traceback: attempt 1 (run dir on the `/tmp` tmpfs) truncated its log mid-line
at case 143 on `Disk quota exceeded`; attempt 2 (setsid'd, run dir on `/home`) exited
silently at case 158. The completing run is attempt 3, tool-managed, run dir on
`/home`, ~9 min wall. I record those two deaths as harness/tmpfs faults, not as
artefact properties — but they are why the report rests on one full pass plus the two
independent instruments rather than on repeated full passes.

---

## 4. Residual risk

* **Custody (F1/F2/F3).** The landed artifact is not the verified artifact. If the
  adjudicator admits r99 as landed, it admits bytes that were never green-run *as such*
  (the only content delta is the duplicated crash row, which is behaviourally benign but
  real), and it admits a report whose hash, diff shape, and row counts do not describe
  the commit. The cheap repair is one line: drop the duplicate tuple and re-pin the
  landed hash; the rows themselves need no change.
* **Pin strength (F5).** The two short boundary pins can pass on degenerate payloads;
  the laws they were meant to re-pin are carried by sibling rows, so the block as a
  whole is not weaker, but a future launch/mode change could hollow those two rows out
  without a red.
* **Host-only facts.** `r99_audio_census` pins `out_devices=["Default"]
  in_devices=["Default"]`, `output_latency=0.00`, `enable_input=false`, `max_fps=0`.
  These are Dummy-driver/launch-shape facts measured on this host; `max_fps` coupling is
  disclosed and fails loudly, the device lists are not (they would be the first thing to
  break on a host with a real audio device).
* **Disclosed latent race.** `period_is_block` (`AudioServer.get_time_since_last_mix() +
  get_time_to_next_mix()`) carries a snapshot race the author already discloses
  (boundary §3.3, `mix_period=0.000000` seen once under `ff30`); never observed at the
  battery launch shape in any receipt I replayed.
* **The duplicate is repaired in-tree, not by r99.** HEAD `9ede7c50` dedupes the crash
  sentinels (509/509 unique, r99 rows untouched), so the landed tree no longer carries
  F2's row; the r99 *landing* still does, and the landing step that produced it (serial
  union splice on the anchor line) is the same step that produced the wrong hash and
  diff shape in the report. Until that step is fixed, each round's report will keep
  describing bytes that are not the bytes on main.

## 5. Verification gaps

* I did **not** re-execute the author's three battery runs; their `verdicts.json`
  (447 rows, 0 FAIL for run C) was read from the author's worktree receipts as secondary
  evidence only.
* The paced/unpaced rejections are **classifier replays** of captured receipts, not
  fresh measurements; the unpaced-mode frame-budget scope is therefore inherited from
  the boundary's receipts, not re-measured here.
* The scout's/boundary's own captures are taken as given: my replay validates the
  shipped pins *against those receipts*, not the receipts' provenance or the 741-process
  matrix behind them.
* One full battery pass on the committed bytes (plus the 21-row fresh-process smoke).
  A second full pass was attempted twice and both attempts died on the host/tmpfs faults
  above; it was not re-attempted a fourth time.
* `lsp` unavailable (no server for `.py`/`.gd` in this session): no semantic
  reference/definition check was possible, and none was needed — the only caller of both
  new fixtures is `run_battery.py` itself (`grep` for the fixture names outside
  `corpus/live/` and `reports/` finds no other consumer; `corpus/fixtures` tracks no
  `.uid` files, so no import metadata is missing).
