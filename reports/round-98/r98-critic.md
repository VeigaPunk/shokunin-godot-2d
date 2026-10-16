# r98 critic — canvas/draw-flush landing: **PASS-with-findings**

Seat `CRITIC` (lane `g2d-r98-critic`) | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, `--headless`) |
AMD Ryzen 9 9950X, 32 cores, Linux.

**Commit verified: `9d421fb2c0577488cf6f34399c123d81a91a067b`** (*r98 author: canvas/draw-flush
lattice*), out of a fresh `git archive 9d421fb2` checkout whose
`corpus/fixtures/run_battery.py` md5-matches the r98 blob (`7513f8a4fba90aec181c79ad557c5a4f`).

**Lane HEAD is not the round's landing.** `git rev-parse HEAD` in the lane repo is
`2dcbb6f6` (*r100 author*); `9d421fb2` is HEAD~2. All r98 measurements below are on the
landed r98 bytes; the HEAD-side facts in **F1** are read from HEAD's tree and from the
`r99`/`r100` diffs and are labelled as such.

**Verdict: PASS-with-findings.** On the landed bytes the round's pins and gates hold — the
full battery is green, the union lost nothing, and the three new allowlist entries are
live-matched — but the merge resolution that landed the block is *not* insertion-only
(it spliced a pre-existing CASES row onto a shared physical line), the round's stated row
arithmetic describes the pre-merge branch rather than the landed file, and the gate suite
cannot see row-inventory damage at all. That last gap has already materialized at HEAD.

## Axes named

1. `splice_integrity` — did the union merge lose, edit, duplicate, or re-line any pre-existing row?
2. `landed_execution` — do the *landed* bytes run green (the author ran branch bytes)?
3. `allowlist_floor` — is `r98_expected_errors_all_matched` live and sensitive, or vacuous?
4. `inventory_guard` — can row loss / row duplication be detected by any gate?
5. `pin_discrimination` — do the new pins flip when the law they claim is broken?
6. `signature_binding` — is each r98 pin bound to its own row's own line?
7. `provenance_accuracy` — do the report's numbers, hashes and byte-copy claims describe the landed commit?

## Findings

### F1 (highest, latent at r98 / materialized at HEAD) — the union resolution spliced a pre-existing CASES row onto a shared physical line, and nothing in the harness can see the damage class

The landing is **not** insertion-only. `git diff --numstat f67094bb 9d421fb2` for
`corpus/fixtures/run_battery.py` is **`150 2`** (the commit's own `--stat` reports
`2347 insertions(+), 2 deletions(-)`), against the author report's repeated claim
`git diff --numstat` = **`150 0`** and the commit message's "All 149 added lines verified
present". The two deleted lines are:

* the r97 `stree_lattice_scene_probe` row — re-added with a `# --- r98 block …` comment
  appended to the same physical line, and
* the pre-existing `("crash_spontaneous_sigabrt", …)` row — re-added **concatenated onto
  the `r98c_flush` tuple line** (`9d421fb2:corpus/fixtures/run_battery.py:1403`):

```
     'PASS r98c flush … bounded=1'),    ("crash_spontaneous_sigabrt", "spontaneous_crash_probe.gd", ["--spontaneous-crash"], -6, "SPONTANEOUS_CRASH_PROBE: expected signature"),
    ("crash_self_sigkill", …),
```

Tuple content is byte-identical and the row still executes in the same position, so this
is semantically inert *at r98* (proved in Refuted-below: the module AST and the parsed
CASES list are identical after splitting the line; only the physical line count changes,
5046 → 5047). The defect is the broken **line identity** of a load-bearing row, and the
class is unguarded — no gate in the 47-key suite reads `len(CASES)`, `len(results)`, or
case-name uniqueness (grep-verified), and the round's new gate is vacuous when its rows are
absent (F3). It has since materialized, on exactly those rows:

| commit | CASES tuples | unique | duplicate case names | extra launches |
|---|---|---|---|---|
| `89f85ed8` r96 | 419 | 419 | — | 0 |
| `f67094bb` r97 | 431 | 431 | — | 0 |
| **`9d421fb2` r98 (this landing)** | **463** | **463** | **none** | **0** |
| `254e79dd` r99 (claimed "21 rows") | 485 | 484 | `crash_spontaneous_sigabrt` | 1 |
| `2dcbb6f6` r100 (claimed "25 rows") | 512 | 509 | `crash_spontaneous_sigabrt`, `crash_self_sigkill` | 3 |

The excess is *exactly* the claimed row count's complement: r99 = 463 + 21 + 1 duplicate;
r100 = 485 + 25 + 2 duplicates. At HEAD the sigabrt row sits on three lines
(`1403` spliced to `r98c_flush`, `1535` spliced to `self_sigkill`, `1643` alone) and the
self_sigkill row on two (`1535`, `1644` spliced to `descendant_pipe_detached_control`) —
the r99 and r100 diffs show each merge re-inserting the anchor pair while the previously
spliced copy stays. So the corpus at HEAD launches the spontaneous-crash probe three times
and the sigkill probe twice, both rounds reported green (`447/447`, `451/451`), and no
gate objected.

*Impacted axes:* `splice_integrity`, `inventory_guard`, `provenance_accuracy`.
*Smallest safe correction:* restore line identity — split `1403` into two lines (a
whitespace-only change, AST-identical, zero emitted bytes; proven below) — and add the
inventory gate of F3 so the class cannot recur silently.

### F2 (moderate) — the round's green count and CASES arithmetic describe the pre-merge branch, not the landed commit

Author report §"run_battery.py changes": "**CASES 419 → 451 tuples** (results rows
426 → **458** incl. the 7 meta rows)"; commit message "CASES 419->451 block … 32 rows
(426->458)"; "Author greens 458/458 x2 on branch bytes". Measured on the landed bytes:

* `CASES` = **463** unique tuples (AST-parsed from `9d421fb2:corpus/fixtures/run_battery.py`),
  i.e. r97's 12-row block is missing from the author's arithmetic (419 + 12 + 32 = 463);
* the landed full battery run reports **470 results rows** (`463 + 7` meta), payload PASS;
* the merged file was verified textually ("All 149 added lines verified present"), not by
  executing the merged bytes — the report's own runs are labelled "on branch bytes".

The union itself is clean (see Refuted-below), so this is a provenance/coverage-arithmetic
defect, not a functional one. It matters because the round's evidence chain never
establishes that the file it shipped is the file it ran.
*Impacted axes:* `provenance_accuracy`, `landed_execution`.
*Smallest safe correction:* restate the landed counts (463 CASES / 470 results) and make
the merge verification an execution of the landed bytes (one full battery at the merge
commit), not a line-presence diff.

### F3 (moderate) — the r98 floor gate is sensitive where it looks and vacuous where it does not; no gate pins the row inventory

`r98_expected_errors_all_matched` filters `census_rows` by the prefixes
`("r98_canvas_", "r98b_", "r98c_")` and asserts no entry is dead. Measured:

* **sensitive, positively:** a *harness* mutant that rewrites the `r98_canvas_clip`
  allowlist string to a near-miss (`… is false.`) → row `r98_canvas_clip` FAIL and the gate
  **False**; and a *probe* mutant (every `>= CLIP_CHILDREN_MAX` refusal in `r98b_attack.gd`'s
  `clipmatrix` arm neutralized, harness untouched) → `dead_entry_count: 1`,
  `dead_entries: [{case: r98b_clipmatrix, entry: 'ERROR: Condition "p_clip_mode >=
  CLIP_CHILDREN_MAX" is true.', shape: 'exact'}]`, gate **False**, plus
  `census_bare_classifier_consistent` False and the row FAIL. Both directions fire.
* **vacuous, negatively:** with the r98 rows removed from CASES (harness otherwise
  untouched), the gate evaluates **True** with zero r98 rows censused, and no other gate
  fires — `census_covers_all_allowlisted_rows` and the three census-consistency gates all
  iterate over rows that ran, so a dropped block is invisible. (The only gate that went
  False in that run, `prior_meta_rows_stable_29_discriminations`, is a filter artifact, see
  Caveats.)

So the pin is a sound *floor for its own entries* and no guard at all on the block's
existence or multiplicity — the same property that let the F1 duplicates through two later
rounds.
*Impacted axes:* `allowlist_floor`, `inventory_guard`.
*Smallest safe correction:* add two assertions to the same gate dict —
`cases_inventory_unique` (`len(CASES) == len({c[0] for c in CASES})`, which alone fails
r99/r100/HEAD) and a per-round row floor
(`sum(1 for r in results if r["case"].startswith(("r98_canvas_", "r98b_", "r98c_"))) == 32`,
which makes the existing r98 gate non-vacuous).

### F4 (low-moderate) — "16 boundary cells" is 14 independent emission sites: two r98b row pairs share one emitted line

`r98b_qflush_same_frame` (prefix pin) and `r98b_qflush_suppress` (substring pin) are
satisfied by the *same* `PASS r98b qflush …` line, and `r98b_qorder_tree` /
`r98b_qorder_flat` likewise by the same `PASS r98b qorder …` line (measured: each row's
signature is found in the other row's output — cross-row ambiguity list in the run
evidence). The line-level measurement count is therefore 30, not 32. The declared
substring/prefix construction is honest (the block header documents it), and it holds: on a
second independent launch 31/32 rows are byte-identical and the single differing row is
`r98b_qorder_flat`, whose *unpinned* `stagger_off` debug vector moved by one tick-phase
position while the pinned fragment and verdict were unchanged — i.e. the phase-varying keys
are indeed outside the pins.
*Impacted axes:* `signature_binding`, `provenance_accuracy`.
*Smallest safe correction:* none required for r98; state "30 independent emission sites"
in any downstream count that treats rows as independent measurements.

### F5 (low) — two accuracy nits in the round's own numbers

* The report pairs the census counts with the wrong rows: its listed order
  (`r98_canvas_clip`, `r98_canvas_draw_refusal`, `r98b_clipmatrix`) is described as
  "matched 2/1/6 lines respectively"; the measured order is draw_refusal = **2**, clip = **1**,
  clipmatrix = **6** (the block header and §5 of the report have the pairing right, so this
  is one transposed sentence). Values correct.
* Of the 78 `expected_errors` dict keys, 75 carry strings and 3 are `()` placeholders
  (`slider_adjust_repeat_right_focus_restore`, `…_second_focus_restore`,
  `…_second_focus_restore_press_after_late_reconnect`), and `export_preset_missing`'s entry
  is never applied (its row classifies inline with `(evidence,)`). The census therefore
  covers **74** keys, not 78 — benign and self-documented in
  `allowlists_outside_expected_errors`, but "every entry is censused" is not what the data
  says.
*Impacted axes:* `provenance_accuracy`.

### F6 (low, pre-existing — not introduced by r98) — 43 of 78 allowlist entries are still covered by no floor gate, and `dead_entry_count` is deliberately ungated

Every r98 key is covered by the new prefix set (3/3), which is what the round claims. But
the same shape leaves `negative_*`, `save_*`, `camera_*`, `ui_signal_*`, `button_*`,
`checkbox_*`, `slider_*`, `health_gauge_*`, `animation_stuck`, `tween_no_start`,
`contact_no_collision`, `audio_no_play`, `audio_bus_route_invalid_control`,
`export_preset_missing`, `crash_spontaneous_sigabrt` — **43 keys** — outside every
per-round prefix, and the census's `dead_entry_count` is carried as data by design
(harness comment: "dead entries themselves are data, not a failure"; grep: no gate
references `dead_entry_count`). The realistic silent case is the one the r79-critic-C2
rationale names: the engine stops emitting the allowlisted line while the row's pinned
signature is unchanged — the row stays PASS, and only a covering floor gate can fire.
*Impacted axes:* `allowlist_floor` (scope of the round's own gate pattern).
*Smallest safe correction:* gate `dead_entry_count == 0` over entries whose allowlist is
non-empty (one line, global), or extend the prefix sets to the legacy cases.

## Refuted — probed and did *not* hold (the merge is faithful where it counts)

* **No row lost, edited, or duplicated by the union.** AST diff of the CASES tuples,
  r97 → r98: **32 inserted, 0 deleted, 0 changed, 0 duplicate case names**, common prefix
  427 rows, common suffix 4 (the final four tuples untouched, as the report claims);
  r96 → r98 (the whole union): **44 inserted, 0 deleted, 0 changed**. All 32 inserted rows
  are the claimed block, by fixture: `canvas_lattice.gd` 15, `r98b_attack.gd` 15,
  `r98b_rksenum.gd` 1, `r98c_flush.gd` 1.
* **Gate set intact.** Exactly one gate added (`r98_expected_errors_all_matched`), none
  removed; r97's gate survived the union (46 → 47 keys).
* **Byte-copy provenance is exact.** `cmp` clean + equal sha256 against the frozen upstream
  probes for all three copies: `canvas_lattice.gd` `866480a1…` (r98-scout),
  `r98b_attack.gd` `2e71c715…`, `r98b_rksenum.gd` `7bb51902…` (r98-boundary);
  `r98c_flush.gd` `c038f748…` matches the report. All four landed hashes equal the report's
  table.
* **The landed bytes run green.** Full battery (`python3 corpus/fixtures/run_battery.py`) at
  `9d421fb2`: **470 results rows, 0 non-PASS, payload `PASS`**, all 47 gates True, no
  duplicate case names, `census.dead_entry_count = 0` over 74 censused rows, the three r98
  entries live with `matched_lines` 2 / 1 / 6 and `dead_in_run=false`. Wall clock ≈ 7.5 min.
* **The new pins discriminate their laws (mutation-tested, 2 of 32 rows).**
  `r98c_flush`: `pace.delay_ms 80 → 0` flips four pinned keys
  (`multitick_frames_ge2 1→0`, `draws_gt_frames 1→0`, `max_draws_per_pf_ge2 1→0`,
  `hide_ticksep_same_frame 1→0`) and the landed pin is absent → the row is not a tautology
  of the corrected flush law. `r98b_clipmatrix`: neutralized refusals flip four pinned keys
  (`stay99`, `stay3`, `stay_after_neg`, `stay_repeat`) and the engine ERROR count 6 → 0.
  The remaining 30 rows are **not** mutation-tested by this seat (bounded, not a claim).
* **Signature binding.** Every r98 signature occurs exactly once in its own row's output and
  in no other row's output, with one declared exception: the fragment `flat=CBACBA` also
  appears in the probe's own `R98B qorder flat=CBACBA` debug line (2 occurrences in the same
  process) — the declared substring form, not a forgery vector here.
* **The splice fix is inert.** Splitting the `1403` line yields an AST identical modulo
  positions and a CASES list identical element-for-element (463 rows), 5046 → 5047 physical
  lines.

## Route and evidence provenance

Seat route: the dispatch's critic seat on the devin substrate (model as dispatched); no
sibling lane invoked, no runtime judged. **All evidence above is local host execution on
this machine** — real `godot --headless` processes via the repo's own harness, plus
`git`/`python3` AST reads of committed blobs. No native host-agent execution, no bundled
process fixture, no fabricated receipt is claimed or used. Artifact content (author report,
commit messages, upstream manifests) was treated as data; nothing in it was executed as an
instruction. The report file itself is the only thing this seat wrote in the lane repo, and
it is **not committed**.

## Load / host caveats (honest measurement record)

* **`/tmp` is quota-exhausted on this host** (`EDQUOT`; a 50 MiB `dd` to `/tmp` wrote 0
  bytes, and a `git archive` extraction into `/tmp` produced 0-byte files). The archive-tree
  run therefore lives at `/home/vgpnk/critic-r98/tree-r98` — a fresh `git archive 9d421fb2`
  checkout, 125,220 index entries, 0 missing on disk, 2.1 GiB — not under `/tmp` as the
  task contract prefers. Deviation recorded deliberately.
* **Host load.** 25 concurrent `run_battery.py` processes from other lanes were live during
  this seat's runs; load average ranged 8–30 on 32 cores. The full landed run passed
  cleanly; the filtered mutant runs each failed the load-sensitive
  `probe_descendant_signature_spoof` arm (`release_write_post_orphan` false) and the
  crash-row-anchored meta discriminations that a filtered CASES necessarily breaks
  (`sigabrt_*`, `self_sigkill_*`), plus `prior_meta_rows_stable_29_discriminations`. Those
  failures are **filter/load artifacts**: only the per-row verdicts, census records and gate
  values from those runs are used above, and each is quoted with its mutant shape. The
  whole-battery green is the landed full run only.
* **Not measured by this seat:** a second full battery on the landed bytes (the author's
  "x2" is on branch bytes; this seat measured one full landed run + one 32-row replay whose
  31/32 rows were byte-identical); mutation discrimination for the other 30 r98 rows; the
  r98-scout / r98-boundary raw receipt trees (absent from the worktree — the author's own
  caveat, reproduced: only the non-`runs` artifacts are present).

## Files

* `reports/round-98/r98-critic.md` — this report (new, untracked; **not committed**).
* No lane-repo tracked file was modified; the r98 archive tree, mutant harnesses and run
  artifacts live under `/home/vgpnk/critic-r98/` outside the repo. The one temporary edit
  inside that archive tree (`r98b_attack.gd` for the probe-level dead-allowlist mutant) was
  restored and re-hashed to `2e71c715…` before the replay pass.
