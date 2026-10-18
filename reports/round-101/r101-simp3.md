# r101 SIMP-3 — queued folds for the r91/r92/r93/r94/r95 lattice fixtures (patch shards only)

Plan (5 lines):
1. Scratch root per assignment is `/tmp/r101-simp3`; §0 records why the Godot projects were materialised under `/var/tmp/r101-simp3` instead (tmpfs `EDQUOT`).
2. Re-audit every fixture in scope at HEAD with the originating round's own write-only-store scanner; enumerate the queued deletions per lane (r91 nav, r92 tilemap, r93 anim, r94 particles, r95 dss/order).
3. Reproduce each proposed fold on HEAD bytes in a battery-shaped scratch project; require the folded sha to equal the sha the originating patch recorded.
4. Run every scenario row of the folded lanes on baseline and folded trees (`godot --headless --path <tree> --script res://<fixture> -- <flags>`), 2 reps each, and compare gate status, PASS lines, diagnostics, exit codes.
5. Emit ready-to-apply unified diffs under `reports/round-101/mutations/`; never run `run_battery.py`, never edit a shared file, no commits.

Load context (recorded once at seat start, and mid-pass):
```
$ uptime
 16:21:20 up 1 day, 16:21,  1 user,  load average: 40.10, 20.91, 13.51
$ uptime            # ~3 min later, while the receipt pass was running
 16:24:50 up 1 day, 16:25,  1 user,  load average: 61.89, 40.57, 22.77
```
Runtime: `godot 4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`). Python 3.14.

## 0. Environment deviation (recorded, not hidden)

`/tmp` is a 16 GiB tmpfs held at 13 GiB by other lanes this round; small writes
sometimes succeed, but anything above a few KiB fails with `EDQUOT` while
`df` still reports 3.1 GiB free:

```
$ cp corpus/fixtures/nav_lattice.gd /tmp/r101-simp3/
cp: error writing '/tmp/r101-simp3/nav_lattice.gd': Disk quota exceeded
$ df -h /tmp
tmpfs  16G  13G  3.1G  80% /tmp
```
The assignment's scratch root is therefore `/var/tmp/r101-simp3` (root fs,
772 GiB free) for the Godot projects and receipts. This shard stays at
`reports/round-101/r101-simp3.md`.

## 1. Verdict

All three queued folds that exist for this fixture set (r91 nav, r94 particles,
r95 dss+order) reproduce **byte-for-byte on HEAD**, apply cleanly, and are
**byte-neutral on every scenario row of their fixture** in a fresh receipt pass:
every row's committed signature still appears, every expected exit code is
unchanged (365 receipts, 0 timeouts), and every stable field keeps its value.
r92 and r93 have empty queues on HEAD bytes (0 write-only stores), so no patch
is proposed for them. One `--offy` retirement census is included for C3.

## 2. Scope and queue census

| lane | fixture(s) | queued deletion | source |
|---|---|---|---|
| r91 | `nav_lattice.gd` | `const SETTLE := 10` + the two append-only `hits` sinks in `_arm_teardown_{crash,clean}` (−3 lines) | `reports/round-91/r91-simplifier.md` §6 |
| r92 | `tilemap_lattice.gd` | **none** — 0 write-only stores | `reports/round-92/r92-simplifier.md` F1 |
| r93 | `anim_lattice.gd`, `r93b_anim.gd` | **none** — 0 write-only stores | `reports/round-93/r93-simplifier.md` |
| r94 | `particles_lattice.gd` | `var T0 := 0` (file scope) + `var start3: int = PH` (`_arm_gpu_headless`) (−3 lines) | `reports/round-94/r94-simplifier.md` |
| r95 | `dss_lattice.gd`, `r95b_order.gd` | 15 dead stores, 18 edit sites (−5 lines): 8 in dss (`pile:357 box:370 made2:499 made3:506 fresh:514 cast:571 ar:585 b2:629`), 7 in r95b (`dss:415 dss:455 made:530 made:567 made:609 a:745 b:750`) | `reports/round-95/r95-simplifier.md` F2 |

## 3. Reproducibility on HEAD bytes

Scratch project built to the battery's own shape (`corpus/fixtures/*` minus
`run_battery.py`, unique `config/name`, `controls/pickup.tscn` staged at root,
`causal_chain.gd` readiness fix), then folded with scripts that reproduce the
originating proposals. The folded shas match the shas the originating patches
recorded — the folds are the same folds:

| fixture | HEAD sha256 | folded sha256 | matches |
|---|---|---|---|
| `nav_lattice.gd` | `088843399ce37eb…` | `b23887e5b05d83…` | r91 `fold-proposal.diff` (b23887e5) |
| `particles_lattice.gd` | `0701e813e50cdb…` | `afd2aa88876abc…` | r94 patch comment (afd2aa88) |
| `dss_lattice.gd` | `77ae4adb8a47cc…` | `c128e9ccf3b3f5…` | r95 battery comment (c128e9cc) |
| `r95b_order.gd` | `4f7e945e1b16f2…` | `b367559e831e5e…` | r95 battery comment (b367559e) |

Applied-patch validation on the untouched working tree (check-only, no writes):

```
$ git apply --check /var/tmp/r101-simp3/patches/r101-simp3-nav-fold.patch        ; rc=0
$ git apply --check .../r101-simp3-particles-fold.patch                          ; rc=0
$ git apply --check .../r101-simp3-r95-fold.patch                                ; rc=0
$ git apply --check .../r101-simp3-r95-harness-comment.patch                     ; rc=0
$ patch -p1 --dry-run -i .../r101-simp3-r95-fold.patch
checking file corpus/fixtures/dss_lattice.gd
checking file corpus/fixtures/r95b_order.gd
```

## 4. Independent HEAD-byte re-audit (observation)

Each round's own scope-aware write-only-store scanner was re-pointed at the
HEAD fixture bytes (`/var/tmp/r101-simp3/base/*.gd`), so the audit is not just
re-cited from the original commit:

```
r91 (nav_lattice.gd)          -> write-only stores: ['SETTLE']
r92 (tilemap_lattice.gd)      -> write-only stores (zero reads anywhere): 0
r93 (anim_lattice.gd, r93b)   -> write-only stores (zero reads anywhere): 0   (0 for each fixture)
r94 (particles_lattice.gd)    -> write-only stores (zero reads anywhere): 2   WO T0:53, WO start3:723
r95 (dss_lattice.gd)          -> 8 dead sites, lines 357/370/499/506/514/571/585/629 (exact r95 list)
r95 (r95b_order.gd)           -> 7 dead sites, lines 415/455/530/567/609/745/750 (exact r95 list)
```
No extra dead store appeared at HEAD in any of the five files, and none of the
listed ones has become live. The r91 scanner classifies the two `hits` arrays
as read_lines (its `append` counts as a read), which is why the append-only
class comes from the r91 seat's own §6 analysis — I re-ran its proposal
verbatim, not a re-derivation.

## 5. Fresh receipts (baseline vs folded, HEAD bytes)

Launch shape is the battery's (`run_battery.py` `execute()`): per row
`godot --headless --path <scratch> --script res://<fixture> -- <flags>`, one
process per row, stdout/stderr captured separately and merged for comparison.
My timeout is 25 s (the battery's is 8 s) so load-induced slowness is not
misread as a verdict; there were **0 timeouts**.

365 receipts total: 119 baseline rows (all seven fixtures, rep1), 82 baseline
rep2 (the four folded-lane fixtures), then 2 reps per folded tree
(nav 11×2, particles 19×2, dss 17×2, r95b 35×2). Exit codes:
**360 × 0, 5 × −6** (the five runs of the two crash arms: nav
`teardown_crash` ×4, tilemap `nullts` ×1 — exactly their `expected_exit`).
Median launch 1.16 s, max 5.68 s.

The 37 r92/r93 lane rows (tilemap 14, anim 15, r93b 8) ran once each on the
base tree: signature present and exit code as expected for **37/37** (0
failures) — consistent with their empty fold queues (no separate folded tree
was needed for a lane with no deletion).

Per lane, comparing 4 receipts per row (base rep1, base rep2, folded rep1,
folded rep2):

| lane | rows | signature+exit gate failures | PASS line identical 4/4 | non-PASS lines identical after mask | whole receipt identical 4/4 | stable-key clash |
|---|---|---|---|---|---|---|
| nav | 11 | 0 | 5 | 11 | 5 | 0 |
| particles | 19 | 0 | 13 | 19 | 13 | 0 (see §6) |
| r95 dss | 17 | 0 | 17 | 17 | 17 | 0 |
| r95 b order | 35 | 0 | 35 | 35 | 4 | 0 |

Mask = `env=tps=… pf=… proc=…` counters (process-local), engine `ids`/`fresh_id`
diagnostics, and `t*_bodypos` diagnostics — i.e. exactly the unstable keys the
round-95 seat declared. On `r95b_order_*` the **only** differing line in the
whole four-receipt set is the `env=` line (`proc=155/156/157`); every PASS line
is byte-identical. The same three-mask rule was applied to every lane.

The six nav PASS lines that are not byte-identical vary on `settle`,
`seq_a/seq_b`, `vel_a/vel_b`, `sum_max`, `first_reachable`, `ladder` — the
boundary fold's declared tail fields — and they vary **inside the baseline too**
(rep1 vs rep2 differ on the same keys; 0 stable-key clashes between trees).
The same holds for the six particles rows that vary (frame counters).

The only stderr difference anywhere is the GDScript backtrace line number on
nav `sync`/`bake`, shifted by the three deleted lines:
`[0] _arm_sync (res://nav_lattice.gd:234)` → `:233`, `[1] _initialize …:142` →
`:141`. No pin, `expected_errors` entry or `required_stderr` fragment references
a line number, so the harness cannot see it (r91's own finding, re-observed).

The nav teardown rows are whole-receipt identical 4/4, including the `rc=-6`
crash and its glibc stderr — the SP2 rewrite (`hits.append` → `pass`) is
byte-neutral in the battery's launch shape.

## 6. The one anomaly and its resolution

`r94_particles_cpu_restart` emitted `second_after=14` in both baseline reps and
`second_after=15` in both folded reps; every other field was stable. The fold
touches no code executed by that arm (`T0`/`start3` live in the file scope and
`_arm_gpu_headless`), so the suspicion was host-load drift between passes.
Focused interleaved A/B (base,fold alternating per rep, 4 reps each,
`scripts/ab_focus.py`) resolves it — **load-conditioned, not fold-conditioned**:

```
r94_particles_cpu_restart: second_after base=[15,15,15,15] fold=[15,15,15,15]
r94_particles_cpu_pause  : fin_after_show  base=[5,5,5,5]   fold=[5,5,5,5]      (both trees 4/4)
r94_particles_gpu_headless: whole receipt identical base==fold (4/4 each, one distinct value)
r94_particles_cpu_lifetime: unstable in BOTH trees (3 distinct base / 2 distinct fold — frame counters)
```
The 14-vs-15 split of the first pass is a pass-time load artifact (the base
passes ran ~10 min earlier under a different load); under interleaved
conditions both trees emit 15. No row of the particles fold is withheld.

(Command shape per rep: `godot --headless --path <tree> --script
res://particles_lattice.gd -- --arm=cpu_restart` etc.; raw receipts in
`/var/tmp/r101-simp3/runs/ab-particles_lattice.json`.)

The same interleaved A/B was run for the six varying nav rows (4 reps each):

```
nav_lattice_agent : base==fold whole receipt, stable (4/4 each)
nav_lattice_bake  : base==fold whole receipt, stable (4/4 each)
nav_lattice_link  : base==fold whole receipt, stable (4/4 each)
nav_lattice_path  : settle varies (base 5..6, fold 4..6) — varies in both trees
nav_lattice_sync  : ladder/first_reach vary in both trees (2 distinct values each)
nav_lattice_avoid : seq_a/seq_b/vel_a/vel_b/sum_max/settle vary in both trees
                    (6 distinct vectors each; sum_max ∈ {19.8508, 20.0000} both)
```
No pinned byte changes; the varying fields are exactly the boundary fold's
declared tails, and their value ranges overlap between the two trees. Raw
receipts: `/var/tmp/r101-simp3/runs/ab-nav_lattice.json`.

## 7. C3 — `--offy` retirement census (r95 order lattice)

**Token census** (tracked tree, HEAD): the only occurrence of `offy` in code is
the scenario row's flag; no `.gd` file contains the token at all:

```
$ git grep -c offy HEAD -- corpus/fixtures/
HEAD:corpus/fixtures/run_battery.py:1      # the r95b_order_celloff_y1000 flags list
$ git grep -n offy HEAD -- 'corpus/fixtures/*.gd'   # (no output)
```
**Reachable-read census**: `r95b_order.gd` reads CLI keys only through
`_opt_int/_opt_float/_opt_str`. All call sites:

```
$ grep -o '_opt_[a-z]*([^)]*)' corpus/fixtures/r95b_order.gd | sort | uniq -c
  1 _opt_float("off", 0.0)      1 _opt_float("spacing", 4.0)
  2 _opt_int("k", 0)            2 _opt_int("k", 5)
  1 _opt_int("keep", 0)         2 _opt_int("perm", 0)
  1 _opt_str("order", "")       1 _opt_str("which", "")   1 _opt_str("which", "a")
```
`"offy"` is absent ⇒ **0 reachable reads**. `dss_lattice.gd` has no `_opt_*`
call at all (it parses `--rev` by hand, `dss_lattice.gd:36-37`).

**Duplicate-row proof on fresh receipts** (base tree, this seat):
`r95b_order_celloff_y1000` and `r95b_order_celloff_x0` emit stdout with the
same sha256 `36af4675fc0f24c4…` (byte-identical, rc=0 both); `celloff_x1000`
differs (`ea0e747d74c86d7d…`). The Y row is an exact duplicate of x0, so the
claimed Y translation is unmeasured — consistent with r95-simplifier F1 and
with the boundary analyzer's `offy=None` for every cell (`corpus/live/r95-boundary/analysis.txt:216-229`).

**Replacement measurement (scratch-only, executed).** A probe copy of
`r95b_order.gd` with `--offy` wired through `_pile()` and the ladder query
(`q = Vector2(16 + off, offy)`) shows the missing cell is measurable and the
invariance holds:

```
$ godot --headless --path /var/tmp/r101-simp3/work/offy --script res://r101_offy.gd -- --arm=celloff --off=0 --offy=0
  R95B celloff offy=0.0000  body0_y=0.0000   ladder=[t2:4,0,2,3,1;…;t64:4,0,1,2,3]
$ … --off=0 --offy=1000
  R95B celloff offy=1000.0000 body0_y=1000.0000 ladder=[t2:4,0,2,3,1;…;t64:4,0,1,2,3]
  t2_relpos=[32.0000,1000.0000|0.0000,1000.0000|…]
```
The body really moved (y=1000), the ladder/order is unchanged, and the y-relpos
carries the translation. `corpus/fixtures/r101_ytrans.gd` (E17-YTRANS, untracked
at HEAD, 11 464 bytes) is the round's landed probe for this surface; this
census is the retirement evidence and the minimal fixture patch, not a second
probe.

**Independent corroboration of the queued fix.** The shared mutations directory
already holds ver8's `r101-ver8-offy-C2.patch` (+ `-cases.patch`), which wires
`--offy` exactly as my scratch probe does. My probe was written before those
files were seen; its `--offy=1000` PASS line is **byte-identical (454/454
chars)** to the expected signature in `r101-ver8-offy-C2-cases.patch`, and its
`--offy=0` line equals the committed `celloff_x0` signature once the added
`offy=` key is removed. So the C2 cells are executable as written; the only
decision left to the orchestrator is whether to take C2 (new `offy` key, 3
signatures change) or ver8's `C` variant (no new key, only `t2/t64_relpos`
change on the y row).

## 8. Deliverables

Ready-to-apply patches (unified, against HEAD paths, validated `git apply --check`):

| file | content |
|---|---|
| `reports/round-101/mutations/r101-simp3-nav-fold.patch` | r91: −3 lines in `nav_lattice.gd` (SETTLE + 2 sinks) |
| `reports/round-101/mutations/r101-simp3-particles-fold.patch` | r94: −3 lines in `particles_lattice.gd` (T0 + start3) |
| `reports/round-101/mutations/r101-simp3-r95-fold.patch` | r95: −5 lines in `dss_lattice.gd` + `r95b_order.gd` (15 dead stores) |
| `reports/round-101/mutations/r101-simp3-r95-harness-comment.patch` | comment-only: update the two fixture sha lines in `run_battery.py` (lines 882/885) |

Reproduction scripts and receipts live in `/var/tmp/r101-simp3/` and are
mirrored into `reports/round-101/mutations/r101-simp3-evidence/` (664 KiB:
`setup.sh`, `build_folds.py`, `extract_rows.py`, `run_rows.py`, `compare.py`,
`analyze_folds.py`, `ab_focus.py`, `rows.json` = the 119 scenario rows
extracted from the current `CASES` list, the 12 receipt JSONL files, both A/B
JSONs, `fold-shas.json`, `fold-analysis.json`), so the pass can be re-run and
every number above re-derived without the `/var/tmp` tree.

**Overlap with SIMP-1 (apply one, not both).** `reports/round-101/mutations/r101-simp1-r91-nav_lattice.patch`
(scoped by that seat to the r91 queue) is **byte-identical** to this seat's
`r101-simp3-nav-fold.patch` (`diff -u` → no output) — two independent
reproductions of the same r91 fold, not two different changes. The r94/r95
patches have no counterpart in the mutations directory.

Do **not** apply the r95 fixture patch without the harness comment patch (the
comment would then quote stale shas) and vice versa; the two are independent
files but the comment's parentheticals "(…, identical bytes)" also become
false — reword them (r95's own §5 note) if the patch is taken.

## 9. Costs, leftovers, risks

- **Cost**: applying a fold stales the historical sha citations: nav changes
  `088843399…` → `b23887e5…`, which the r91 author report and
  `corpus/live/r91-simplifier/MANIFEST.sha256` quote as *historical* receipts;
  particles changes `0701e813…` → `afd2aa88…` (quoted in
  `reports/round-94/r94-*`); r95 changes both fixture shas (quoted in the
  harness comment, handled by the comment patch). No *live* gate reads a sha.
- **r92/r93**: nothing to do; their fixtures are byte-identical to their
  landing shas and their queues re-audit to 0 on HEAD bytes.
- **Residual risk (r91 SP2)**: the rewrite assumes the crash is bound to the
  registered Callable, not to the callback body. Measured identical today
  (4/4 receipts incl. `rc=-6` + glibc stderr); an engine change that made the
  abort depend on the body would invalidate that arm. The r91 seat flagged the
  same class.
- **Residual risk (r94 cpu_restart)**: resolved in §6 — the 14-vs-15 split was
  pass-time load drift; interleaved A/B gives `second_after=15` in both trees
  4/4 and `gpu_headless` whole-receipt identical. No row withheld.

Seat output complete.
