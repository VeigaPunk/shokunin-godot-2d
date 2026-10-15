# game-dev-2d round 80 — scribe report (seat: scribe, host: devin)

Task (dispatch brief, verbatim): audit the r80 author's landing of
`corpus/fixtures/phys2d_motion.gd` + battery rows against
`reports/round-80/r80-scout.md`'s measured table — every `CASES` row's
expected signature must match the scout's verified bytes exactly; every
`expected_errors` entry must correspond to a real emitted line; the
`phys2d_events` convention checklist (match-arm sole index, no ids in
output, `--arm` dispatch, diagnostic header); and no perturbation of prior
rows (spot-check rows 1–111 vs HEAD). Record corrections precisely.
Write `reports/round-80/r80-scribe.md`.

Scope: **read-only audit while the landing was in flight**. Writes = this
report only. No tracked file edited, no git mutation, no battery re-run —
execution evidence audited from the author's own landed receipts
(`corpus/live/r80-author/runs/` ×3) and the scout's frozen receipts
(`corpus/live/r80-scout/`). The author's tracked write was observed
mid-flight (fixture `??` 02:49, battery `M` ~05:51Z) and re-verified after
`r80-author.md` landed.

Evidence classes: **[M]** re-derived by this seat now; **[C]** claim read
from a landed artifact (cited); **[U]** unobservable in this window.

## 0. State at read time

- HEAD **`d9320dd`** *r79 report-last: adjudicator ADMIT-corr + ledger* —
  unchanged across the audit window (author: no commit, tree left dirty per
  brief) **[M]**.
- Tracked delta vs HEAD: `M corpus/fixtures/run_battery.py` **+70/−0**
  (sha `48c4a379…` → `66bfe3e2…`), `?? corpus/fixtures/phys2d_motion.gd`
  (879 lines, sha `f622b89e3093dd5da44dd10ed26b480a506fb04b139861056567d
  37788337047`) **[M]**. The only other tracked mod is the pre-existing
  `M SCORECARD.md` **+29/−1** — the fleet round-1 calibration rewrite the
  r79 scribe already recorded; unchanged by this round **[M]**.
- Author writes match its §0/§5 declaration exactly: the fixture, the +70
  battery insertion, `reports/round-80/r80-author.md`, and
  `corpus/live/r80-author/runs/` ×3. Nothing else under
  `corpus/fixtures/` touched **[M]**.
- `reports/round-80/` now holds `r80-scout.md`, `r80-baseline.md`,
  `r80-author.md` (all untracked, as is the standing pattern) **[M]**.

## 1. CASES rows vs the scout's verified bytes — 28/28 exact

Method: parse `CASES` from the landed `run_battery.py` (AST literal), parse
the scout's paste-ready tuples from `corpus/live/r80-scout/author-rows.py.txt`
(sha `12026134dbc4bf98…`), compare all five tuple fields; separately check
each landed signature against `arms-verify.json`'s per-row `signature`
**and** `measured_line` (the actually emitted bytes, ×3 byte-stable).

- **28/28 rows byte-exact** on `(name, script, flags, expected_exit,
  signature)` — zero field diffs **[M]**. Every signature equals the
  scout's `measured_line` for that arm (28/28 `signature ==
  measured_line` in `arms-verify.json`, so the chain landed-row ==
  emitted-bytes holds transitively) **[M]**.
- **Insertion site correct**: motion block at `CASES` indexes 100–127
  (`run_battery.py:159–214`), immediately after
  `phys2d_events_area_dss_in_cb` and before `crash_spontaneous_sigabrt`
  (`:215`) — ahead of the crash/descendant tail, so nothing sits between
  `descendant_pipe_detached_control` (`:217`) and the meta probes **[M]**.
  The 10-line block comment `:149–158` restates the `sleep 8` orphan
  ordering constraint, as the r79 block's comment does **[M]**.
- **Ordering constraint confirmed in execution**: the meta probe
  `probe_descendant_pipe_eof` records `detached_descendant_orphaned_alive:
  true` and all discriminations true in both clean reps **[M]**.
- CASES count 104 → **132**; results count 111 → **139** (7 unconditional
  meta probes unchanged) **[M]**.

## 2. `expected_errors` entries vs real emitted lines

The merge adds exactly 2 entries at `:581–584`, after the `phys2d_events`
entries, byte-exact vs the scout's paste-ready text and vs
`arms-verify.json` `expected_errors` fields **[M]**:

| key | landed entry | real emitted lines (rep stderr, `arms-verify.json` ×3) | correspondence |
|---|---|---|---|
| `phys2d_motion_mac_maxcol` | 1 exact string | 1 `ERROR:` line — identical bytes | **exact; entry real, all emitted covered** **[M]** |
| `phys2d_motion_dss_wrongarg` | 3 exact strings | **7** `ERROR:` lines, distinct-set = the 3 allowlisted strings | **exact; every entry emitted, every emitted line covered** **[M]** |

- `dss_wrongarg` per-type emission is **5× `rp_shape_query`**
  (`_arm_dss_wrongarg` lines 732–736: four wrong-typed `ptq` calls +
  `intersect_shape(null)`), 1× `rp_ray_query`, 1× `rp_point_query` — see
  **F2** on the scout's "4×" parenthetical **[M]**.
- No other row carries an `expected_errors` entry: the other 26 motion
  rows emit zero `ERROR:` lines; no vacuous allowlist created **[M]**.
- The battery's own census agrees: `probe_error_clause_surface` →
  `rows_with_expected_errors` **45** (scout-run 43, +2 = the new
  error-bearing rows), `dead_entry_count` **0**,
  `phys2d_expected_errors_all_matched` **true**, **35/35**
  discriminations true — in both clean reps **[M]**.
- All **47** prior `expected_errors` dict entries unchanged; the map
  gained keys, never re-keyed **[M]**.

## 3. Fixture audit — comment-only delta vs the pinned probe

`diff corpus/live/r80-scout/proj/phys2d_motion.gd` (876 lines, sha
`ddb5921d4aff5f37…`) vs landed `corpus/fixtures/phys2d_motion.gd` (879
lines, sha `f622b89e…`):

- **Every executable line byte-identical.** The diff touches only
  comment lines: the retitle (`# r80-scout scratch probe` → `# r80
  fixture`, new-file line 2), one added convention line
  (`# The 'match arm:' dispatch in _run is the sole arm index (28 arms).`,
  line 7 — the same declaration `phys2d_events.gd` carries), and the arm
  index rewritten to carry each arm's measured class (new-file lines
  9–37). Net +3 lines **[M]**.
- The rewrite **completes** the arm index: the scout probe's header listed
  26 of 28 arms (omitted `btm_from2`, `btm_recflag`); the landed header
  lists all 28 **[M]**. Author §1.1 discloses this accurately.
- `ccd_spin` labeled `(weak cell)` in its class comment — scout directive
  5 / §7 honored **[M]**.
- Because all code bytes are identical to the probe whose outputs were
  measured ×3 stable, the landed fixture cannot emit different bytes;
  confirmed in execution by the author's clean reps (§4) **[M]**.

### Convention checklist (landed file, `phys2d_events` pattern)

| item | verdict | evidence |
|---|---|---|
| `match arm:` is the sole arm index | PASS | `match arm:` at `:74`; the only other reads of `arm` are its decl `:43`, the parse `:66`, and the header interpolation `:71`; `_fail("unknown_arm")` default `:103` **[M]** |
| `--arm` dispatch | PASS | `_initialize` parses `--arm=` from `OS.get_cmdline_user_args()` (`:65–66`), `call_deferred("_run")` — identical to r79 **[M]** |
| diagnostic header | PASS | `print("R80 arm=%s godot=%s engine2d=%s separate_thread=%s")` first in `_run` (`:70`) — the `R79`-line convention, tag rotated **[M]** |
| no ids in output | PASS | only 3 print-family calls in the file (`:70`, `:106`, `:115`); no `printerr`/`push_error`/`push_warning`; RIDs are *used* (`get_rid()` for server calls) but never printed — the `rid`/`collider_id` tokens in signatures are literal dict-key names **[M]** |

## 4. Prior-row perturbation check — none

- **All 104 prior `CASES` tuples unchanged vs HEAD** — name, script,
  flags, expected_exit, and signature sha all equal; relative order
  preserved; the diff is pure insertion (`+70/−0`, two hunks) **[M]**.
- The "rows 1–111" numbering of the brief = 104 `CASES` + 7 meta probes;
  the meta-probe codepath is untouched (no hunks outside `:149–214` and
  `:581–584`) **[M]**.
- Semantic stability across runs: for every prior row, `verdict` /
  `actual_exit` / `signature` / `expected_exit` identical between the
  author's two clean reps, and equal to the scout-run values — **except**
  two provenance deltas vs the *scout's* run (not vs HEAD): `cm_off` and
  `cm_max0` signatures in the scout's 05:08Z verdicts lack the
  `post_monitor=`/`post_max=` fields because the scout executed the
  in-flight pre-fold r79 rows (disclosed at r80-scout §0); committed HEAD
  carries the final signatures and the landed rows match HEAD exactly.
  Scout-run ≠ HEAD on those two rows is expected history, not r80
  perturbation **[M]**.
- The author's own claim "prior 111 rows zero semantic drift" is true on
  the clean reps; strictly, rep 1's `cm_max0` **verdict** differed
  (flake, §5) while its `signature`/`exit` fields stayed identical —
  author's phrasing holds on the semantic fields **[M]**.

## 5. Author's execution evidence vs receipts

Three sequential full-battery runs under `corpus/live/r80-author/runs/`
(`--runs` absolute path), verdicts sha256 verified against the author's
§2 table **[M]**:

| rep | dir | results | verdict | sha256 prefix (author-claimed) | measured |
|---|---|---|---|---|---|
| 1 | `20261015T055149737742Z` | 139 | 138/139 — `phys2d_events_cm_max0` FAIL | `a2f75e21…` | **matches**; record shows `exit=0`, signature byte-exact, one unrelated line `ERROR: Error opening gamepad at index 1: Couldn't find mapping for device (1)` `at: process_events (drivers/sdl/joypad_sdl.cpp:141)` — the unrelated-`ERROR:` clause rejecting correctly **[M]** |
| 2 | `20261015T055428670225Z` | 139 | **139/139 PASS** | `b1a8165c…` | matches **[M]** |
| 3 | `20261015T055647880085Z` | 139 | **139/139 PASS** | `7a647424…` | matches **[M]** |

- All 28 `phys2d_motion_*` rows PASS in all three reps; rep-2 vs rep-3
  merged outputs **byte-identical on all 28 rows** (the scout's
  byte-stability survives the tracked harness) **[M]**.
- Error-bearing rows in clean reps: `mac_maxcol` emitted exactly 1
  `ERROR:` line, `dss_wrongarg` exactly 7 — matching §2 **[M]**.
- All 7 meta probes PASS in both clean reps **[M]**.
- The rep-1 flake is **environmental, not a landing defect**: an SDL
  joypad enumeration line leaked into that one process's merged stream;
  same row clean in rep 2, rep 3, and the scout's run. Independent
  corroboration: `r80-baseline.md` recorded the *same flake class* on a
  **different** row (`wrong_key`) inside a frozen `d9320dd` worktree —
  host-level noise, orthogonal to content **[M]**.
- Baseline's independent timeline fixes the write order: freeze at
  05:48:10Z (sha `48c4a379…`), fixture `??` at 05:49:37Z, battery write
  to `66bfe3e2…` at 05:51:34Z (+70 insertion-only) — identical to this
  seat's observations **[C→M verified]**.

## 6. Corrections / findings for the canonical judge

- **F1 — author §1.1 boundary is off by one.** "changes only inside
  lines 1–36 (all comments)" — the diff actually spans new-file lines
  **2–37** (line 37, `#   cont_persist …`, is part of the rewritten arm
  index; line 1 `extends SceneTree` is unchanged). Claim's substance
  ("all comments") true; only the stated range is wrong **[M]**.
- **F2 — scout §2 miscounts the `dss_wrongarg` split.** "emits 7 `ERROR:`
  lines (4× `rp_shape_query`, one per shape method)" — measured rep
  stderr shows **5× `rp_shape_query`** (four wrong-typed `ptq` calls at
  `phys2d_motion.gd:732–735` plus `intersect_shape(null)` at `:736`),
  1× `rp_ray_query`, 1× `rp_point_query` = 7 total. Total and the
  3-string coverage claim are correct; the "4×, one per method"
  parenthetical is not **[M]**.
- **F3 — author §1.2 line citation off by four.**
  `descendant_pipe_forged_signature_release` is cited at `:219`; it sits
  at `:223` (the r63 comment block occupies `:218–222`). Neighboring
  citations `:215`/`:217` are exact **[M]**.
- **F4 — scout probe header arm index was 26/28.** The scout-source
  `phys2d_motion.gd` header omitted `btm_from2` and `btm_recflag`; the
  author completed the list and disclosed it. No pin affected — the
  `match` arms and all 28 `CASES` rows were always complete **[M]**.
- **F5 — scout's 111/111 sanity ran pre-fold r79 signatures** on `cm_off`
  /`cm_max0` (rows were in-flight `M` at that moment; disclosed at
  r80-scout §0). Recorded so future scribes don't misread the two
  scout-run signature fields as r80 drift **[M]**.
- **F6 — rep 1 recorded as `verdict: FAIL` (138/139)** — the author's
  table phrases it "138/139 — one environmental flake"; accurate, and
  two consecutive clean 139/139 reps follow it. Kept as provenance, not
  suppressed — correct handling **[M]**.
- **F7 — minor loose phrasing, author §0.** "`reports/round-*/` were not
  touched" — reads as if round-80's own report directory were included;
  the author obviously wrote `r80-author.md` there. Intent (prior rounds)
  is clear and verified — no `reports/round-7*/` content changed **[M]**.
- **Claims verified with no defect**: fixture sha `f622b89e…` and
  876→879; `+70/−0` insertion-only; comment `:149–158`, CASES `:159–214`,
  `expected_errors` `:581–584` (all exact); CASES idx 100–127/132;
  "no harness edits needed" (no `classify_process`/`execute()` changes —
  the only codepath touched is data) **[M]**; "`--check-only` exit 0" is
  consistent with but not independently receipted here — superseded by
  84× rc=0 arm runs + 2× 139/139 full reps, a strictly stronger parse
  proof **[C/U]**.

## 7. Gates, out of scope, limits

- Gates run by this seat: none — landed receipts audited, no battery
  re-execution (per seat card: no rerun to decorate).
- Out of scope: judgment (ADMIT/REJECT belongs to the canonical judge);
  LOVE/pygame rows (author's `corpus` footprint is Godot-only — verified
  `love_battery.py`, `pygame_battery.py`, `main.lua` untouched); the
  `corpus/live/r82-scout/` tree observed mid-window (adjacent lane, not
  this round's audit).
- Limits: the "~4.6 s spawn→check margin" figure is the r79 author's
  restated number — sufficiency proven by `detached_descendant_
  orphaned_alive=true` in both clean reps, but the 4.6 s value itself
  not re-measured here. `SCORECARD.md` attribution as "pre-existing"
  rests on the r79 scribe's record + unchanged +29/−1 numstat.
  Comment-only fixture diff guarantees emission-identical bytes *given*
  the verified probe outputs; that guarantee was also confirmed
  empirically by the two clean reps.

## 8. Artifacts

- This report: `reports/round-80/r80-scribe.md`.
- Audited tracked surface: `corpus/fixtures/run_battery.py`
  (`48c4a379…` → `66bfe3e2…`, +70/−0); `corpus/fixtures/phys2d_motion.gd`
  (new, `f622b89e…`, 879 lines).
- Audited receipts: `corpus/live/r80-author/runs/20261015T05{5149,5428,
  5647}*Z/verdicts.json` (sha `a2f75e21…`, `b1a8165c…`, `7a647424…`);
  `corpus/live/r80-scout/{author-rows.py.txt, arms-verify.json,
  arms-discover.json, proj/phys2d_motion.gd, runs/…T050846*Z/verdicts.json}`;
  `reports/round-80/{r80-scout.md, r80-author.md, r80-baseline.md}`.
- Baseline snapshot retained at `/tmp/r80-scribe-cases-baseline.json`
  (104-row pre-landing CASES digest used for the perturbation census).

**Seat output complete.**
