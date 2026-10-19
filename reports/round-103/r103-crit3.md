# r103-crit3 — Attack the folds (C3 adversarial seat)

Plan (5 lines):
1. Locate the 3 queued simplifier gaps (r99 F2 → r99b_modes.gd, r100 SP2/SP3 → r100b_seq.gd, r97 F6 → r97_scene_marker.gd) in SCORECARD/LOG/reports.
2. For each proposed fold, copy fixture to /var/tmp/r103-c3 scratch, apply fold, run targeted `godot --headless` — capture verbatim stdout bytes (receipt identity).
3. Discrimination attack: build negative/regression probes that the removed lines supposedly guard; show whether folded fixture still catches them (load-bearing vs receipt-only).
4. r94 cpu_contam reference class: check whether folds are receipt-identical but discrimination-dead; per-hunk pass/fail evidence with exact commands + output bytes.
5. Write results + verdict (keep/hold/reject each fold) here; shard is durable partial progress.

Status: recon starting. uptime: (to record)


---

## SEAT C3-RESUME (2026-10-18T21:5xZ, 3rd attempt after 2 starvations)

Plan (5 lines, resuming — the recon plan above stands, artifacts reused, nothing restarted):
1. Host header + verify the 3 landed patches (`git apply --check`) at HEAD `6e3e87f7`, then apply all 3 in my own worktree `/var/tmp/r103c-C3/wt` and pin pre→post sha256 per fixture.
2. Build battery-equivalent scratch projects `pre` (HEAD bytes) and `post` (folded) under `/var/tmp/r103c-C3/`, launch shape copied from `run_battery.py:1929` — `godot --headless --path <scratch> --script res://<fixture> -- <flags>`, 3 reps each, stdout/stderr captured separately.
3. Load-bearing attack per fold: (a) byte-compare receipts pre/post; (b) exercise the *removed line's own path* (`--arm=splitcycle` for E2 — an arm with no row; `--arm=census/zzz` injection into r100b_seq for E3; a scene-load `tag`/`ready` probe for E1); (c) teeth mutants so the comparison is non-vacuous.
4. Adjudicate the S1-flagged `startphase one_uniq` pre=2/post=1 divergence against the 3-rep noise floor (fold effect vs run noise).
5. Write per-fold verdict + verbatim commands/output bytes here; no edits to shared files, no commits, `git worktree remove` at the end.

Host (once): `uptime` @ 2026-10-18T20:55:35Z → `20:55:35 up 1 day, 20:55, 1 user, load average: 1.94, 1.79, 1.64`. HEAD `6e3e87f7b34252b1fd1deaeb8f8adef85efac849`, branch `main`, godot `4.7.2.stable.arch_linux.ed1daf0bf`. Scratch: `/var/tmp/r103c-C3/`. Sibling lanes: none observed in my scratch namespace (I only `ls`ed stray `/var/tmp/r103-*` per instructions; not removed).

### Step 1 — apply + sha pins (observation)

`git apply --check` on all three patches at HEAD → OK (no drift). Applied in `/var/tmp/r103c-C3/wt` → OK, all three. sha256 (pre = HEAD blob, post = folded):

| fixture | pre (HEAD) | post (folded) | lines |
|---|---|---|---|
| `corpus/fixtures/r97_scene_marker.gd` | `39763310044aaac40fa69a1e57c435c6969ad9d9877c9f340ddb820bc2810b1a` | `2b9bd63351df82bd1d2bd96e5c90dcca41aec2d0d329e5d6eda2d55a721d1e84` | 7→3 |
| `corpus/fixtures/r99b_modes.gd` | `b680e6f297b7534d02a3bdc33337961062f9f0a79393b2a48798308785d38624` | `e5e72573eaad6ea720975d9dedcb3b49aa506f91170ccea54fdff990cbed00f7` | 453→452 |
| `corpus/fixtures/r100b_seq.gd` | `4718a19e0050f4043613a5a93a13cbd812c811605f7a14d33e000544eafa94dd` | `e77dc55c55dbe88f1951c1762c62c5383a06b4a54b53cf485de1a9dfc3509f42` | → |

Cross-seat agreement (observation): my post `r99b_modes.gd` sha `e5e72573…` is byte-identical to the post bytes S1 reported for the same fold from an independent worktree (`r103-S1.md`), and my post `r100b_seq.gd` sha `e77dc55c…` is a *new* pin (S2 published no sha).

Provenance fact pinned (observation): `run_battery.py:1541` cites `r100b_seq.gd sha256 4718a19e…`, and `run_battery.py:1646` cites the same sha for the r101_seqfull fixture's provenance. Both citations are the *pre-fold* bytes ⇒ landing the E3 fold makes those two harness comments stale unless the orchestrator updates them (rule 2: run_battery.py is orchestrator-only; recorded as a landing precondition, not applied by me).

### Step 2 — static attack evidence (observation, gathered before the runs)

- `r97_scene_marker.gd` (E1): `ready_ticks` has **zero readers repo-wide** — `grep -rn "ready_ticks" --include=*.py --include=*.gd corpus/ reports/round-10[0-3]/` returns only the fixture's own decl+increment plus byte-copies under `corpus/live/**` (mint-era scene_marker.gd copies) — never a harness row, never `run_battery.py`. Its only consumer path is `stree_lattice.gd --arm=scene_probe` (row `stree_lattice_scene_probe`, `run_battery.py:1278`), which loads `res://r97_scene_a.tscn` / `r97_scene_b.tscn` (ext_resource → `res://r97_scene_marker.gd`, `tag` set per scene by the .tscn).
- `r99b_modes.gd` (E2): `grep -n "pairs" corpus/fixtures/r99b_modes.gd` → exactly one hit, the declaration at line 403 inside `_arm_splitcycle`. Zero reads, zero writes. The arm is **unrowed**: `grep -n "r99b_modes" run_battery.py` yields only 3 rows (`startphase`, `mixfree`, `finfree`), none of which dispatch `splitcycle` (`match arm` dispatch table at `r99b_modes.gd:83-91`).
- `r100b_seq.gd` (E3): `grep -n "\barm\b\|--arm"` → decl (8), parse (77-78), loop-assign (89), `match arm` (90); nothing else. `seq_arms` is a **hard-coded literal** (`r100b_seq.gd:83`), *not* built from cmdline args, so the parsed value is overwritten before every dispatch. The 2 consuming rows pass only `--clean=0/1`.
- Warning-class probe (observation, answers a question the fold notes never tested): a scratch `SceneTree` script with `var unused_thing: Dictionary = {}` run under the same launch shape produced **0 B stderr** (`/var/tmp/r103c-C3/probe-warn/`), i.e. Godot 4.7.2 `--script` mode does not print `UNUSED_VARIABLE` outside the editor. Combined with the strict stderr rule at `run_battery.py:1834` ("any unexpected stderr line rejects"), the deleted `var pairs` line cannot have had a stderr footprint in any receipt.

### Step 3 — sweep + teeth mutants (in progress, results appended below)

Runner: `/var/tmp/r103c-C3/sweep.py` (syntax-checked with `ast.parse`), log `/var/tmp/r103c-C3/sweep.log`. Battery runner **never executed** (hard rule 1); only `godot --headless` on scratch. Scratch `project.godot` prep mirrors `run_battery.py:1746-1765` (unique app name, `pickup.tscn` root staging, `causal_chain.gd` double-`process_frame` patch).

### Step 3 — pre/post sweep results (observation)

Runner `python3 /var/tmp/r103c-C3/sweep.py 3` (log `sweep.log`, receipts `sweep-results.json`). Launch shape (verbatim, battery's own — `run_battery.py:1929`): `godot --headless --path <scratch> --script res://<fixture> -- <row flags>`; stdout/stderr captured **separately**; 3 reps per side; rc recorded. 48 row-runs + 12 attack-runs + 6 mutant-runs.

| row | pre stdout sha256 (3 reps) | post stdout sha256 (3 reps) | bytes | stderr | rc |
|---|---|---|---|---|---|
| `stree_lattice_scene_probe` **(E1 consumer)** | `a7fb7e34856aa3608b22efd883e95798a426af630f2446073e0ef67c96c2862d` ×3 | **identical** | 954 | 0 B | 0 |
| `r99b_startphase` | `39e97921d4e464477344ac4c25c4154481bc79afb0dee2ba75697ca25bf456dd` ×3 | **identical** | 378 | 0 B | 0 |
| `r99b_mixfree` | 3 distinct shas (clock tail) | 3 distinct (clock tail) | 388-391 | 0 B | 0 |
| `r99b_finfree_played` | 3 distinct (clock tail) | 3 distinct (clock tail) | 299 | 0 B | 0 |
| `r100b_seq_clean` **(E3 consumer)** | `2fc9a28f0dc2a44f4301d346ef46a81bfab87a6514bf21b070a9334412b0372a` ×3 | **identical** | 6804 | 293 B (see §4 note) | 0 |
| `r100b_seq_noclean` | `bb1e76767fcd3bf08807cebca6ac7340c5029096793e838d0c6bf92029a95c83` ×3 | **identical** | 6279 | 296 B | 0 |
| `r101_seqfull_clean` | `2fa3673312f1eecaf2c2299936e7602638e9ede7dffba03c14f77bf0f0362077` ×3 | **identical** | 6976 | 302 B (sha identical both sides) | 0 |
| `r101_seqfull_noclean` | `7d130ed74577b2c5c50d56f1fe7fd5ec07a7e688f243e2f150a1bf8da320a4e9` ×3 | **identical** | 6482 | 305 B (sha identical) | 0 |

- **My E3 stdout shas reproduce S2's claimed shas** (`2fc9a28f…` / `bb1e7676…`) exactly, from an independent worktree/sweep — S2's numbers were not fabricated.
- `r99b_mixfree` / `r99b_finfree_played` are **not byte-stable even within one side** (3 reps → 3 shas; differing tokens are the `chg=[…@Nus]` microsecond timestamps and `fin_us=`/`transition_f=` frame-or-µs fields). Their battery pins are therefore *field fragments*, not whole lines: `run_battery.py` pins `'all_jumps_q=true period_is_block=true'` (mixfree) and `'played_gt_02=true'` (finfree) — confirmed by ast-extracting the CASES tuples. Byte-identity is the wrong criterion for these two rows; pin-presence is the right one (below).
- **Replication-axis control**: `r101_seqfull_*` does not read `r100b_seq.gd`; its stderr sha is bit-identical pre/post (`f0ecca7b2b…`, `9ba992fa42…`) — so host conditions did not drift between my pre and post batches in a way that could masquerade as a fold effect.

Row-level acceptance, **using the battery's own criterion** (ast-extracted `ROWS` signature + `expected_exit` + the `expected_errors` allowlist; classifier rules mirrored from `run_battery.py:1792-1809`; `required_stderr` has **no** entry for any of these 8 rows):

- `python3 /var/tmp/r103c-C3/verify_pins.py` → **8 rows × {pre,post} × 3 reps = 48/48 classified PASS** (`rc == expected_exit`, pinned signature present in merged output, no unrelated `ERROR:` line, no `SCRIPT ERROR:`/`Parse Error:`).
- allowlist entries involved: `('ERROR: Parameter "t" is null.',)` for `r100b_seq_clean/noclean` + `r101_seqfull_clean/noclean` — the pinned ERROR line is byte-identical pre/post (it is the classified unit).

Attacks beyond the row set (observation):

| attack | purpose | result |
|---|---|---|
| `ATK_r99b_splitcycle` (E2's own path; **no battery row exists** — `grep '--arm=splitcycle' run_battery.py` → 0) | exercise the code path the deleted `pairs` decl sits in | rc=0, 0 B stderr, `PASS r99b splitcycle` present, `first=0.002902494 changes=16 frames=220` identical both sides; only `@Nus` timestamps vary (pre r1/r2 482/486 B, post 482/484 B) → removal is unobservable **even on its own path** |
| `ATK_r100bseq_arminject_census` — pass `--arm=census` explicitly | try to make the deleted parse observable | stdout sha `2fc9a28f0dc2a44f…` = **the plain `--clean=1` run's sha, byte-for-byte**, pre and post |
| `ATK_r100bseq_arminject_zzz` — pass `--arm=zzz` (bogus) | ditto, worst case | same: `2fc9a28f0dc2a44f…`, 3/3 reps each side → the parsed value is provably unobservable in both directions |
| `ATK_marker_probe` — scratch scene-load probe reading `tag`, `is_node_ready()`, `has_method("_ready")`, `ready_ticks` | E1: is the removed line *live code* or dead text? | pre `PASS marker_probe tag=A ready=true cls=Node2D script_has_ready=true yticks=1` (sha `b5e39156cb8c…`) vs post `… script_has_ready=false yticks=<null>` (sha `962062ad0c0c…`) → the deleted `_ready` **does execute** under a scene load; it is a live but **unread instrument**, not dead text. `tag=A`/`ready=true` survive ⇒ the .tscn contract is intact |

Teeth mutants (non-vacuity of the byte-comparisons; each mutant applied to a *copy* of the respective side's project, never to a shared file):

| mutant | what it breaks | caught pre? | caught post? | evidence |
|---|---|---|---|---|
| `E1_scene_missing` — `change_scene_to_file("res://r97_scene_missing.tscn")` | the scene-load path the row pins | yes (sha `fffc7ab8ca86…`, 938 B vs 954 B; `file_t5=SceneA tag=A` → `file_t5=null`) | yes, **same mutant sha** `fffc7ab8ca86…` | teeth unchanged by the fold |
| `E2_startphase_sig_spoil` — rename `imm=` → `immX=` in the arm's print | the `r99b_startphase` pinned signature | yes (sha `73476e356e0b…`, 379 B) | yes, same sha | ditto |
| `E3_c0_shift` — `+ Vector2(1,0)` on the cursor cell's `c0` | the `r100b_seq_clean` pinned cursor line (`c0=(30.0, 14.0)` → `(31.0, 14.0)`) | yes (sha `f9cb081d2bc5…`) | yes, same sha | ditto |

### Step 4 — the S1-flagged `startphase one_uniq` divergence: **RUN NOISE, not a fold effect**

`r103-S1.md` flagged `startphase one_uniq: pre-r1=2 vs post=1` as needing adjudication. Measured with `python3 /var/tmp/r103c-C3/ext_noise.py` (9 fresh pre + 9 fresh post launches of `--arm=startphase`):

- pre: `one_uniq` = `['2','1','1','1','2','2','1','2','1']`; post: `['1','1','2','2','1','2','2','2','2']` → **both sides produce both values**.
- The stdout sha sets are **equal**: pre {`39e97921d4e4…`, `5d3592b4e6d4…`} = post {`39e97921d4e4…`, `5d3592b4e6d4…`}, `pre-only = post-only = ∅`.
- The value↔sha association is identical on both sides (`39e97921d4e4…` ⟺ `one_uniq=1`, `5d3592b4e6d4…` ⟺ `one_uniq=2`). So the fold changes the *frequency* of a host-scheduling-dependent state, not its semantics. (Corroborated by S1's own interleaved 48-launch probe, which reached the same GREEN verdict by a different route.)
- Note the `one_uniq`/`one=` tokens sit **after** the end of the pinned signature (`run_battery.py:1528-1530` stops at `imm_uniq=1`), so this field was never a graded byte even before the noise analysis.

### Step 5 — verdicts (per fold)

| fold | patch | verdict | basis |
|---|---|---|---|
| **E1** r97 F6 `r97_scene_marker.gd` −4 | `r103-S0-E1-…scene_marker.patch` | **KEEP (receipt-safe), with a docs precondition** | sole consumer row byte-identical ×3 pre/post; the `tag` contract survives (row prints `tag=A`/`tag=B`, mutant teeth identical); the removed `_ready` is live-but-unread (`ready_ticks` zero readers repo-wide) ⇒ no discrimination lost. Cost: it falsifies the live byte-identity provenance clause at `run_battery.py:1244` ("marker .gd is byte-identical") and the sha row at `reports/round-97/r97-author.md:34` — V6 §7 already emitted the exact line-pairs; landing E1 without them leaves a **false claim on disk** |
| **E2** r99 F2 `r99b_modes.gd` −1 | `r103-S0-E2-…r99b_modes.patch` | **KEEP** | declaration had zero readers/writers (`grep -n "pairs"` → 1 hit, the decl); all 3 row gates reproduce; the arm it lives in (unrowed `splitcycle`) runs clean pre/post with identical stable fields; teeth preserved; zero stderr footprint class proven by the unused-var probe. Cost: `run_battery.py:1414-1419` cites `b680e6f2…, 453 lines` → stale after landing (line-pair in §7) |
| **E3** r100 SP2+SP3 `r100b_seq.gd` −5 | `r103-S0-E3-…r100b_seq.patch` | **KEEP, with one honest caveat** | stdout byte-identical for both consumer rows (3/3) *and* for the `--arm=census`/`--arm=zzz` injections; `seq_arms` is a hard-coded literal so the parse was inert; teeth preserved. **Caveat (observation): stdout-only identity does not extend to stderr** — see below |

**E3 stderr nuance (the one thing S2's "byte-identical" wording does not cover).** `r100b_seq_clean`/`noclean` stderr is 293 B/296 B on both sides but the shas differ (pre `2dc7981c9e2b…`/`f7561237b6…` vs post `ed00e7d86509…`/`0fef124a10…`). Line diff (`difflib`, verbatim):

```
 GDScript backtrace (most recent call first):
-       [0] _cell_render (res://r100b_seq.gd:762)
-       [1] _run (res://r100b_seq.gd:116)
-       [2] _cleanup (res://r100b_seq.gd:135)
+       [0] _cell_render (res://r100b_seq.gd:757)
+       [1] _run (res://r100b_seq.gd:111)
+       [2] _cleanup (res://r100b_seq.gd:130)
```

All three frames shift by exactly −5 (the fold size). The **classified unit** — the allowlisted `ERROR: Parameter "t" is null.` line — is byte-identical, and `grep -c "res://r100b_seq.gd:" run_battery.py` = **0**, i.e. no pin, allowlist entry, or meta conjunct binds those frame numbers; `required_stderr` has no `r100b_seq` entry. Verdict: **benign but real** — any future artifact that hashes *merged* stdout+stderr of these rows will see a difference; V5 §2 independently measured the same −5 shift and reached the same "classifier unaffected" conclusion (two independent measurements, same numbers). If a strict merged-byte identity is ever demanded, it must be scoped to the pinned/allowlisted units, not to the blob.

### Step 6 — S4 probe reject-arm print fix: independently verified (C3 claim-list item)

S4's shard claims the patch is emitted and print-only. Independent check from my seat (no shared-file edit; scratch `/var/tmp/r103c-C3/s4/`):

- `git apply --check reports/round-103/mutations/r103-S4-probe_reject_prints.patch` at repo root → OK.
- HEAD `run_battery.py` sha256 = `40440356f0bf04481f518adc332d1ebb7ba79213878a9f3836421a512828a5c4`; after `patch -p1` → `f179d479825b7c609618b407fa4e9a57f438518dd945627590e6d8203e2fb2eb` — both **byte-equal to S4's own reported values**.
- `python3 -m py_compile` on the patched copy → OK.
- `diff HEAD patched` → exactly **2 changed lines** (L4647, L4720), both the identical per-arm print f-string; **no verdict/classification line touched** (so "verdict logic byte-identical" holds by construction, not just by claim).
- New expression truth table evaluated verbatim: `(inner=True, flags=[])→PASS`, `(False,[])→FAIL`, `(True,['--x'])→FAIL`, `(False,['--x'])→REJECT-ARM (designed)` — mismatch arms still print FAIL.

### Step 7 — landing preconditions (orchestrator-only files; supplied, not applied)

1. **E1**: use V6 §7 line-pairs (a) `run_battery.py:1242-1244` byte-identity clause, (b) `reports/round-97/r97-author.md:34` sha row. Without them the fold contradicts a live claim.
2. **E2 (mine, not covered elsewhere)**: `corpus/fixtures/run_battery.py:1414-1419` — current text ends `… sha256` / `b680e6f297b7534d02a3bdc33337961062f9f0a79393b2a48798308785d38624, 453` / `lines) — the cap-free (wall-bounded) instrument for the three boundary` / `law rows.` → replace the sha+line-count with `e5e72573eaad6ea720975d9dedcb3b49aa506f91170ccea54fdff990cbed00f7, 452` and append `(r103 E2: −1 dead \`pairs\` decl in the unrowed \`splitcycle\` arm; all 3 row gates and the arm's own output reproduce — reports/round-103/r103-crit3.md, r103-ver4.md)`.
3. **E3**: use V5 §7 line-pairs (L1541 sha → `e77dc55c…`; L1543 append the r103 exception line; L1646-1647 keep historical `4718a19e…`).

### Step 8 — cleanup, repro, labels

- `git worktree remove /var/tmp/r103c-C3/wt` → executed (worktree list re-checked). Scratch `/var/tmp/r103c-C3/` **kept** as evidence (receipt JSONs, per-side projects, mutant trees). Pre-existing stray worktrees `/var/tmp/r103-S2`, `/var/tmp/r103-S3`, `/var/tmp/r103-ver4`, `/var/tmp/r103c-C4/wt` listed only, not removed (instructions).
- Repro: `python3 /var/tmp/r103c-C3/sweep.py 3` (48+12+6 godot launches, ~6 min) → `sweep-results.json`; `python3 /var/tmp/r103c-C3/verify_pins.py`; `python3 /var/tmp/r103c-C3/ext_noise.py`. **The battery was never executed** (hard rule 1); `run_battery.py` was only read and `ast.parse`d (never imported, never `exec`d). No commits, no shared-file edits.
- Labels: sha256/bytes/rc tables, mutant diffs, backtrace diff, truth table = **observation** (commands above, artifacts on disk). "Host noise explains the S1 divergence" = **inference** from the equal sha-set + identical value↔sha association across sides. **Unknown:** whole-battery equivalence of the three folds under the production harness (my evidence covers the 8 rows that consume the folded fixtures + the 2 unrowed paths they sit on); `--fixed-fps`-free wall-clock regimes as they age.
- **Seat verdict: all three folds KEEP (no load-bearing line found in any of them), each conditional only on the doc/citation preconditions in §7; S4's print fix independently re-verified.**

---

**STATUS: COMPLETE** (completion seat, KEY=C3). All three folds verdict-ed KEEP with evidence in §3-§5; S4 patch re-verified in §6; landing preconditions in §7; worktree `git worktree remove --force /var/tmp/r103c-C3/wt` → done (patches were applied there, hence `--force`); scratch kept as evidence. Shard closed at 144 lines (<400).
