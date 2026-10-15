# game-dev-2d round 85 — verifier (g2d): independent re-run, prior-159 stability, forge-kill

Seat `VERIFIER` (LEAF) | lane `g2d` | round 85 | host **devin**.
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), Python 3.14.7.
Repo `~/Projects/shokunin/game-dev-2d-shokunin`.
Verified commit **`45232c7`** (r85 landing); prior-159 baseline **`5ab058b`** (r81 landing) /
**`71405b2`** (r81 LOG — harness byte-identical to `5ab058b`).

**No git mutation, no commit, no tracked file written.** Every artifact this seat produced is
under the untracked `corpus/live/r85-verify/**` plus this report. The tracked harness was
executed only; it is byte-clean against HEAD (`corpus/fixtures/run_battery.py` sha256
`1abc9629…` == `git show HEAD:…`).

**`lsp` disclosure.** No `lsp` device is exposed on this host: the only MCP server available is
`rea` (binary-analysis provider), no `lsp` tool exists in this session's tool surface, and no
GDScript/Python language server binary is installed (`gdscript-lsp`, `pylsp`, `pyright`,
`pygls`, `lsprotocol` all absent). Godot exposes `--lsp-port`, but there is no client device to
speak the protocol. **Semantic carriers are therefore fresh-process execution receipts plus
AST-level structural analysis (Python); no LSP result is claimed or implied, and no text grep
output is presented as semantic proof.**

---

## 0. Verdict table (brief items 1–5)

| # | brief item | verdict | decisive evidence |
|---|---|---|---|
| 1 | Full battery ×2 fresh → 174/174 PASS | **PASS** | rep1 `20261015T083126153779Z` **PASS 174/174** (sha `b6b700c7…`, 2 m 22 s); rep2 `20261015T083402818671Z` **PASS 174/174** (sha `0f599a11…`, 2 m 17 s) |
| 2 | Prior-159 semantic stability vs r81 (`5ab058b`/`71405b2`) — rep-vs-rep **and** vs git archive | **PASS** | harness diff vs `5ab058b` = one contiguous **37-line insertion, zero deletions**; fresh `git archive 71405b2` run **PASS 159/159** (sha `57ad5b83…`); **contract-level differences vs archive: NONE** for all 159 rows (both reps); rep-vs-rep: 0 verdict differences |
| 3 | Forge-kill: one load-bearing mechanism removal → must FAIL | **PASS (kills)** | 2 independent forge cells, each FAILs the battery and **exactly** its target row, at exit 0 with a *value* mismatch (not a crash) |
| 4 | Byte-stability of the 15 new rows across reps | **PASS** | 15/15 `camera_proc_*` rows: merged output **byte-identical** rep1↔rep2 (4 lines each, exact-line equality with the pin) |
| 5 | Export rows are HOME/env-sensitive — verify under normal env only | **PASS (normal env)** | both export rows PASS in both reps (`HOME=/home/vgpnk`); the author's retained 172/174 is reproduced and fully attributed to a stripped env below |

Supporting claim checks (author/fold/scout): **174/174 author rehearsal reproduced**, **fold-verify
174/174 reproduced**, **scout ×3 byte-stability reproduced from its receipt**, **paste block
byte-identical to the tracked insertion**, **standalone 20/20 rc=0**, **zero `expected_errors`
for all 15 rows**.

---

## 1. What the diff actually is (mechanism of the landing)

| fact | value | how checked |
|---|---|---|
| commit scope | `camera_proc.gd` (new, 1156 lines), `run_battery.py` (+37), 3 reports | `git show --stat HEAD` |
| harness diff vs `5ab058b` | **single contiguous insert** `r81[266:266] -> HEAD[266:303]`, **0 deletions, 0 modifications elsewhere** | `difflib.SequenceMatcher` over the two full file texts |
| CASES growth | 152 → 167 rows (+7 meta probes = 159 → 174 results) | AST extraction of the `CASES` literal in both revisions |
| `CASES` order | `HEAD[:148] + HEAD[148+15:] == r81 CASES` **ordered-equal** | AST tuple comparison |
| r85 rows == scout paste | tracked HEAD lines **267–303 byte-equal** to `author-rows.py.txt` lines 1–37 (sha `2221a9e8…`); the 4-line tail (`]` + comment block) is the disclosed drop | byte compare + `ast.literal_eval` tuple compare |
| `expected_errors` map | **untouched** — the insertion is inside `CASES` only; no r85 row has a whitelist entry | single-insertion diff + per-record `expected_errors == []` in both reps |
| landed fixture | sha256 `34f53f32c0fbb37da86f91ec7b7d9fc0e7d20d9f3e29c4c9680f05e36f123c40` | `sha256sum`; scratch copy in both reps has the same sha (the battery ran the landed bytes) |
| insertion anchor | HEAD lines 267–303, immediately after `phys2d_joints_area_entry_order` (l.265) and before `crash_spontaneous_sigabrt` (l.304) — the anchor the r79/r80/r81 blocks encode | line map + execution order in §2 |

**Callers/invariants.** `run_battery.py` is a leaf harness: no tracked script, gate, or CI entry
point imports it or reads `CASES` (only `love_battery.py`/`pygame_battery.py` mention it in
prose; each has its own `CASES`). The only invariants that can be affected are the harness's own
(ordering constraint, classifier clauses, meta probes) — all exercised below. No stale
battery-size claim exists in tracked docs outside the round reports (grep over `*.md`/`*.py`).

---

## 2. Battery reps — 174/174 ×2, plus checks the harness does not make

Both fresh runs were serial (no concurrency), normal env, `python3 corpus/fixtures/run_battery.py
--runs corpus/live/r85-verify`.

| run | stamp | verdict | results | sha256(verdicts.json) | wall |
|---|---|---|---|---|---|
| rep1 | `20261015T083126153779Z` | **PASS** | 174/174 | `b6b700c7c822936b0c8ec50fbf3e333609933736f14f8a11ecfb3a5422c59bf6` | 2 m 22 s |
| rep2 | `20261015T083402818671Z` | **PASS** | 174/174 | `0f599a1126713cb26f557e4d205d50ea853e7aa39a3c9f9053c4c5298a2251c2` | 2 m 17 s |

Checks performed **beyond** `classify_process` (`corpus/live/r85-verify/integrity_checks.py`):

- **case-name uniqueness**: 174 records, 174 unique names, **0 duplicates** in both reps (a
  duplicate would silently re-run/shadow a row).
- **exact-line equality**: all 15 `camera_proc_*` rows' `PASS camera_proc …` output line is
  **byte-equal to the pinned literal** (the harness only requires `signature in output`). The
  pinned literals are 162–1208 bytes and are full-line pins.
- **launch shape**: every camera row's recorded command is
  `godot --headless --path <scratch> --script res://camera_proc.gd -- --arm=<arm>`.
- **arm header**: every camera row's output carries `R85 arm=<arm> …` — the requested arm is the
  executed arm.
- **one PASS line per row**, `actual_exit == 0`, `expected_errors == []`, no `SCRIPT ERROR:` /
  `Parse Error:` / unexpected `ERROR:` line.
- **ordering constraint honoured**: the execution tail is
  `… camera_proc_par_phase → crash_spontaneous_sigabrt → crash_self_sigkill →
  descendant_pipe_detached_control → descendant_pipe_forged_signature_release →
  probe_save_independent_process → probe_spontaneous_crash_classification →
  probe_descendant_pipe_eof → probe_descendant_signature_spoof → probe_while_live_signature_gate
  → probe_descendant_error_spoof → probe_error_clause_surface`, and both
  `probe_descendant_pipe_eof` and `probe_descendant_signature_spoof` are **PASS** in both reps —
  the r85 block sits ahead of the crash/descendant tail exactly as its comment claims.
- **whole-battery error scan**: the only `ERROR:` line outside a row's own allowlist is
  `export_preset_missing`'s `ERROR: Invalid export preset name: Missing preset.`, which the export
  branch admits through its own literal at `run_battery.py:553` (the record's `expected_errors`
  field is `[]` because that branch does not use the map). **Scan artifact, not a defect.**

### 2.1 The 15 new rows, rep1 (rep2 identical)

| case | arm | exit | pin bytes | exact line | rep1==rep2 output |
|---|---|---:|---:|---|---|
| `camera_proc_cam_comp` | `cam_comp` | 0 | 688 | yes | yes |
| `camera_proc_cam_zoom_center` | `cam_zoom_center` | 0 | 339 | yes | yes |
| `camera_proc_cam_phase` | `cam_phase` | 0 | 1066 | yes | yes |
| `camera_proc_cam_subpixel` | `cam_subpixel` | 0 | 402 | yes | yes |
| `camera_proc_cam_space` | `cam_space` | 0 | 1208 | yes | yes |
| `camera_proc_cl_stack` | `cl_stack` | 0 | 715 | yes | yes |
| `camera_proc_cl_follow` | `cl_follow` | 0 | 650 | yes | yes |
| `camera_proc_cl_phase` | `cl_phase` | 0 | 713 | yes | yes |
| `camera_proc_cl_draworder` | `cl_draworder` | 0 | 290 | yes | yes |
| `camera_proc_vp_worlds` | `vp_worlds` | 0 | 221 | yes | yes |
| `camera_proc_vp_render_indep` | `vp_render_indep` | 0 | 162 | yes | yes |
| `camera_proc_vp_subcam` | `vp_subcam` | 0 | 427 | yes | yes |
| `camera_proc_par_layer` | `par_layer` | 0 | 983 | yes | yes |
| `camera_proc_par_2d` | `par_2d` | 0 | 375 | yes | yes |
| `camera_proc_par_phase` | `par_phase` | 0 | 770 | yes | yes |

Each row's merged output is exactly 4 lines (engine banner, blank, `R85 arm=…` header, `PASS …`).
30 fresh Godot processes (15 × 2 reps) — **15/15 rows byte-stable**, matching the scout's ×3
receipt and the author's ×1 standalone + ×1 rehearsal.

---

## 3. Prior-159 semantic stability

### 3.1 Source-level (vs `5ab058b`/`71405b2`)

`git diff 5ab058b..71405b2` is `LOG.md` only ⇒ the r81 harness is identical at both revisions.
Against the r85 harness the diff is the single 37-line insertion of §1 — **no prior row, no
classifier clause, no whitelist entry, and no other byte of the harness changed**. That is the
strongest available form of "no prior row was touched".

### 3.2 Behavioural — rep-vs-rep

Both reps agree on **every verdict** (174/174 PASS each) and on **every case name**.
8 rows differ in raw output text between reps, all pre-existing rows and all non-semantic:

| row | nature of the difference |
|---|---|
| `tween_flash` | transient tween sample `(0.7045, 0.791, 0.8881)` vs `(0.7045, 0.7909, 0.8879)` — pin is the prefix `PASS tween_flash transient_modulate=` |
| `save_roundtrip`, `save_process_writer/reader/missing` | run-dir path + pid in the `user_path=`/`pid=` tail — pin is a prefix |
| `crash_spontaneous_sigabrt` | ASLR load address + stack-trace addresses |
| `descendant_pipe_detached_control`, `descendant_pipe_forged_signature_release` | `godot_pid=`/`spawned_pid=` |

**No `camera_proc_*` row drifts**, and no pinned literal is affected in either rep.

### 3.3 Behavioural — vs a pristine `git archive 71405b2` run

Pristine r81 harness + r81 fixtures extracted with
`git archive 71405b2 corpus/fixtures | tar -x -C corpus/live/r85-verify/r81-archive` (harness sha
`60175b10c52a315b654cafd2147b385af38c83e59a0197d512575c1075bc0116`), then run fresh:
**PASS 159/159** (`…/r81-archive/runs/20261015T084210127534Z/verdicts.json`, sha `57ad5b83…`).

`corpus/live/r85-verify/prior159_compare.py` compares all 159 shared rows on
verdict / actual exit / expected exit / script / flags / CASES pin / unexpected-ERROR set, plus a
masked byte diff (run-dir path, run stamp, pids, ASLR + stack addresses, ANSI, progress chatter,
savepack listing order):

```
rep  PASS n=174 | arch PASS n=159 | prior rows compared: 159
archive-only cases: none | rep-only cases (excluding r85): none
-- contract-level differences: NONE
-- rows whose masked output differs: ['export_preset_missing', 'export_readiness', 'tween_flash']
VERDICT: prior-159 contract-stable=True
```

Identical result against **both** reps. The three residual byte diffs are fully attributed:

| row | residual | attribution |
|---|---|---|
| `export_readiness`, `export_preset_missing` | editor chatter: `Registering global classes… (31 steps)` → **(32 steps)**, shifted percent lines, and two extra `Storing File: res://camera_proc.gdc` / `camera_proc.gd.remap` lines | **caused by the r85 landing and fully explained**: the tracked fixture dir has exactly one more `.gd` file than the r81 archive (`diff` of the two `find . -name '*.gd'` listings = `./camera_proc.gd`), so the editor registers and packs one more script. Both rows' *pins* (`[ DONE ]`+`savepack`+nonempty artifact; the missing-preset ERROR) are unaffected and both PASS. |
| `tween_flash` | one transient tween sample float | pre-existing, pin is a prefix; same class as the rep-vs-rep drift |

**Conclusion: prior-159 semantic stability holds — 159/159 contract-identical to a fresh r81
archive run, in both reps.** The only r85-attributable byte movement in a prior row is unpinned
export chatter, and its cause is the new fixture script.

---

## 4. Forge-kill receipts

Two independent mechanism removals, each applied to a **scratch copy** of the fixture
(`corpus/live/r85-verify/forge-*/fixtures/`, tracked file untouched), each run through the full
production battery in its own tree. Full-battery runs, not arm-level spot checks, so the receipt
covers blast radius as well as kill.

### 4.1 Forge A — `follow_viewport_enabled` mechanism removed

```diff
--- corpus/fixtures/camera_proc.gd
+++ corpus/live/r85-verify/forge-followview/fixtures/camera_proc.gd   (sha ee6e9686…)
@@ -535,7 +535,7 @@  (in _arm_cl_follow)
 		cl.layer = i + 1
-		cl.follow_viewport_enabled = bool(cfgs[i][0])
+		cl.follow_viewport_enabled = false  # FORGE A (r85 verifier): mechanism removed
```

| field | value |
|---|---|
| run | `…/forge-followview/runs/20261015T083624685110Z/verdicts.json` (sha `be33e217…`) |
| battery verdict | **FAIL** |
| failing rows | **exactly 1**: `camera_proc_cl_follow` (other 173 PASS) |
| failure mode | `actual_exit 0`, `error None`, a `PASS camera_proc cl_follow …` line **is** printed — the pin mismatches on **values**: `F1/F2/F3` collapse from `en=1 wc=32.0,-68.0 fin=Scale(2)` to `en=0 wc=100.0,0.0 fin=identity` |
| reading | the pin is load-bearing for the mechanism, and the row's blast radius is exactly the arm that owns it |

### 4.2 Forge B — camera write dropped (the `cam_phase` ladder)

```diff
--- corpus/fixtures/camera_proc.gd
+++ corpus/live/r85-verify/forge-camwrite/fixtures/camera_proc.gd     (sha 148f6018…)
@@ -298,7 +298,7 @@  (in _arm_cam_phase, lane A)
 	# A: default process_callback (IDLE), plain write
-	await _phase_probe("A", func(k: int): camref.position = Vector2(10.0 * k, 0.0),
+	await _phase_probe("A", func(_k: int): pass,
```

| field | value |
|---|---|
| run | `…/forge-camwrite/runs/20261015T083918617563Z/verdicts.json` (sha `669a97c5…`) |
| battery verdict | **FAIL** |
| failing rows | **exactly 1**: `camera_proc_cam_phase` (other 173 PASS) |
| failure mode | exit 0, no error, PASS line printed; the A-ladder collapses to a constant `32.0000,32.0000` instead of `A.i1[22.0000,32.0000] …` — value mismatch |
| reading | the phase ladder pins the *write's* observable effect, not merely a printed shape |

Both forges therefore kill **by value discrimination at exit 0**, which is the meaningful test:
neither row passes vacuously, and neither failure is a crash/parse artifact. The scout's own
ablation matrix (`arms-verify.json`, `signature_dropped: false` for all 15 arms) is consistent
with this and is corroborated here at battery granularity.

---

## 5. Item 5 — the HOME/env-sensitive export rows

Both export rows PASS in both reps under the normal env (`HOME=/home/vgpnk`). The author's
retained stripped-env diagnostic (`corpus/live/r85-author/merge-runs/20261015T065931148350Z`,
`verdict=FAIL`, 172/174) fails **exactly** `export_readiness` and `export_preset_missing` — no
r85 row, no prior row. Cause, read from that receipt's captured output:

```
ERROR: Cannot create file 'res://godot/cache/editor_doc_cache-4.7.res'.
ERROR: Cannot save editor help cache (./godot/cache/editor_doc_cache-4.7.res).
ERROR: Could not create ObjectDB Snapshots directory: user://home/vgpnk/…
ERROR: Cannot open directory './godot/feature_profiles'.
```

With no `HOME`, the editor export path emits unrelated `ERROR:` lines, which
`classify_process`'s unrelated-error clause rejects (`export_readiness` additionally ends with a
0-byte artifact). **The 172/174 is a stripped-env artifact of two pre-existing r6/r9-era export
rows and must not be attributed to r85** — the author's and fold's disclosure is correct and this
seat reproduces it. Both rows are outside the r85 delta; nothing in the r85 diff touches them.

---

## 6. Claim-chain cross-checks (upstream receipts vs the landed artifact)

`corpus/live/r85-verify/claim_receipts.py`:

| claim | source | result |
|---|---|---|
| scout ×3 byte-stability, 15 arms | `r85-scout/arms-verify.json` | `reps=3`, **unstable arms: none**, **1 distinct stdout hash per arm** (15 arms), all rep verdicts PASS |
| scout pins are the landed pins | `arms-verify.json` vs tracked `CASES` | `signature` and `measured_line` **== tracked pin for all 15** |
| rows verbatim from the paste block | `author-rows.py.txt` (sha `2221a9e8…`) | HEAD lines 267–303 **byte-equal** to paste lines 1–37; tuples structurally equal |
| author standalone 20/20 | `r85-author/standalone.json` | 20 arms (15 pinned + 5 inert `diag_*`), **rc=0 all**, pinned arms' `pass_line` == tracked pin |
| author merge rehearsal 174/174 | `merge-runs/20261015T070315089724Z` | PASS 174, all 15 camera rows PASS |
| fold verify 174/174 | `r85-fold-verify/20261015T082834904650Z` | PASS 174 |
| fixture identity | `corpus/fixtures/camera_proc.gd` | sha `34f53f32…` == author/scout-recorded fixture sha |
| no whitelist entries | tracked harness | 15/15 camera records `expected_errors == []` in both reps |

---

## 7. Findings by severity

**F1 — [low] `r85-fold.md` over-compresses the stretch-pin scope.** The fold writes "scout's
stretch-mode numbers remain deliberately unpinned" (`reports/round-85/r85-fold.md:17`). The scout
is precise: only the **DISABLED-mode factor-2** stretch case is pinned (it is inside the
`camera_proc_cam_space` literal: `stretch[f2_final=… f2_ct=… f2_wc=… f2_vx=… half=16.0000,16.0000
restored=1]`); the **CANVAS_ITEMS/VIEWPORT** variants are the deliberately unpinned ones
(`r85-scout.md:334-339`). Impact: a downstream reader could conclude the stretch phase is
unverified when the load-bearing DISABLED case is in fact pinned. Documentation accuracy only;
no artifact change required.

**F2 — [low] Two pre-existing export rows' *unpinned* output shifts because of this landing.**
Adding `camera_proc.gd` makes Godot's editor register/pack one more script
(`(31 steps)` → `(32 steps)`; extra `Storing File: res://camera_proc.gdc` and
`camera_proc.gd.remap`). Both rows still PASS (their pins are untouched) and this is not a
contract change — but anyone diffing raw r81-era vs r85-era export receipts will see it and must
not read it as drift. Worth one line in the round's LOG entry.

**F3 — [info] `LOG.md` carries no r85 entry.** The latest entry is `## round 81 — … (ADMIT-corr)`;
the r85 landing commit changes code/fixtures/reports only, and the r81 precedent is a separate
`r81 LOG: ADMIT-corr` commit after adjudication. Expected sequencing, not a defect — flagged so
the round is not closed without it.

**F4 — [info] Working tree carries an unrelated uncommitted modification.**
`SCORECARD.md` is modified (`M`, +29/−1) and does **not** belong to `45232c7`. It is another
lane's in-flight edit; nothing in this seat's verification touched it, and the harness used for
every run is byte-clean against HEAD. Not a finding against r85 — recorded so a later reviewer
does not attribute it to this round.

**F5 — [info] The two `r81-fold-verify` FAIL receipts are mid-fold artifacts, not r81 drift.**
`corpus/live/r81-fold-verify/20261015T081816645412Z` and `…/r81-fold-verify2/…` are `FAIL` with
9 `phys2d_joints_*` rows, while `…/r81-fold-verify3/…` is PASS. Cause, measured here: the first
two used a **stale pin** — their `phys2d_joints_joint_groove` signature lacks `j3_type=1`, which
the fixture output already carried; verify3 and the tracked harness carry the corrected pin
(`signature == tracked pin: True`). A reviewer comparing a fresh 174-row rep against those two
receipts would see 9 phantom differences. **Do not misattribute them to r85** — the correct
prior-159 baseline is `5ab058b`/`71405b2` (used in §3).

**No high- or medium-severity defect was found in the diff or the changed behaviour.** Every
affected caller, invariant, error path and observable contract in scope checks out.

---

## 8. Residual risk and verification gaps

- **Pinned physics-resting floats (residual risk, not a defect).** `camera_proc_vp_worlds`
  (`pos[br=0.0007,76.3000 bs=40.0007,76.3000 bo=0.0000,207.9190 bd=0.0007,76.3000]`),
  `camera_proc_vp_render_indep` (`pos=[0.0007,76.3003|…]`) and the `par_*`/`cl_*` transform pins
  are 4-decimal measurements of a stepping GodotPhysics2D scene. They are byte-stable on this
  host/build (scout ×3, this seat ×2 — 45 + 30 processes), but they are not *derivation-proof*:
  a host with a different idle:physics iteration ratio, a different build, or a threaded twin
  could move them and fail a *correct* fixture. The scout discloses exactly this ("no portability
  claim"; the idle:physics ratio is deliberately absent from every pinned token). No evidence of
  drift exists in this round; the risk is cross-host, and it is inherent to pinning measured
  floats — the only real mitigation would be a tolerance form the harness does not support.
- **`vp_worlds` resting-contact question stays open** (scout §5): resting bodies report
  `get_contact_count() == 0`; positions are the witness. Not investigated here either.
- **Not re-measured by this seat** (out of scope, and deliberately so): rendered/non-headless
  canvas behaviour, `content_scale_mode = CANVAS_ITEMS|VIEWPORT` stretch derivations, threaded
  physics, camera smoothing/limits (tracked `camera_follow.gd`/`camera_limit.gd` territory),
  mouse-position/viewport input mapping (unmeasurable headless).
- **Sampling bound.** 2 reps × 174 + 2 forge × 174 + 1 archive × 159 = **855 battery result rows**
  across 5 serial battery runs (every seeded row is one fresh Godot process); the timing-sensitive
  meta probes (200 ms signature gaps, the descendant's `sleep 8` window) all passed in all 5 runs.
  Reps were run serially to keep those bounds unperturbed; a concurrent-load re-run is not
  covered by this receipt.
- **Host scope.** All numbers are this host, Godot `4.7.2.stable.arch_linux.ed1daf0bf`, headless,
  64×64 root viewport, 60 tps, GodotPhysics2D, these scenes — no portability claim.

---

## 9. Reproduction

```bash
cd ~/Projects/shokunin/game-dev-2d-shokunin
# item 1 — two fresh reps (serial)
python3 corpus/fixtures/run_battery.py --runs corpus/live/r85-verify
python3 corpus/fixtures/run_battery.py --runs corpus/live/r85-verify
# item 2 — pristine r81 baseline, then the comparison
git archive 71405b2 corpus/fixtures | tar -x -C corpus/live/r85-verify/r81-archive
python3 corpus/live/r85-verify/r81-archive/corpus/fixtures/run_battery.py \
        --runs corpus/live/r85-verify/r81-archive/runs
python3 corpus/live/r85-verify/prior159_compare.py \
        corpus/live/r85-verify/20261015T083126153779Z/verdicts.json \
        corpus/live/r85-verify/r81-archive/runs/20261015T084210127534Z/verdicts.json
# item 3 — forge cells (each tree carries its own mutated camera_proc.gd + mutation.diff)
python3 corpus/live/r85-verify/forge-followview/fixtures/run_battery.py \
        --runs corpus/live/r85-verify/forge-followview/runs
python3 corpus/live/r85-verify/forge-camwrite/fixtures/run_battery.py \
        --runs corpus/live/r85-verify/forge-camwrite/runs
# items 2/4/6 — analysis
python3 corpus/live/r85-verify/analyze.py            # exact-line, error scan, rep-vs-rep
python3 corpus/live/r85-verify/integrity_checks.py   # uniqueness, scratch-sha, meta probes
python3 corpus/live/r85-verify/claim_receipts.py     # scout/author/fold claim chain
```

| artifact | sha256 |
|---|---|
| `corpus/fixtures/camera_proc.gd` (landed) | `34f53f32c0fbb37da86f91ec7b7d9fc0e7d20d9f3e29c4c9680f05e36f123c40` |
| `corpus/fixtures/run_battery.py` (landed) | `1abc9629448f299bb222b200b034d191a221c469ca4ffc9fae061b389c205115` |
| r81 archive harness (`71405b2`) | `60175b10c52a315b654cafd2147b385af38c83e59a0197d512575c1075bc0116` |
| rep1 / rep2 verdicts | `b6b700c7…` / `0f599a11…` |
| forge A / forge B verdicts | `be33e217…` / `669a97c5…` |
| forge A / forge B mutant fixture | `ee6e9686…` / `148f6018…` |
| r81 archive verdicts | `57ad5b83…` |

---

## 10. Seat verdict (recommendation, not an admission)

**PASS.** Independently reproduced: **174/174 ×2 fresh**; the r85 delta is a purely additive
37-line insertion plus one self-contained fixture; **prior-159 contract-stable against a pristine
`git archive 71405b2` run with zero contract-level differences** in both reps; the 15 new rows are
**exact-line and byte-stable across reps**; two independent forge cells each kill the battery on
**exactly** their target row by value mismatch at exit 0; the claimed 20/20 standalone, ×3 scout
stability, paste-block provenance, and zero-whitelist properties all verify against the artifacts
on disk. Findings are documentation/precision level (F1–F5); the residual risk is the
cross-host behaviour of pinned measured floats, disclosed by the scout and not observable on this
host in 75 camera-row processes.
