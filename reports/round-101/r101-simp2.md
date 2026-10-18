# r101 SIMP-2 — Queued simplifications, second half of fixtures (patch shards only, no in-repo edits)

## Plan header (written first, before any measurement)
1. Harvest queued-deletion queues from r91/r98/r99/r100 critic+simplifier sections (same harvest class as SIMP-1).
2. Scope: second half of `corpus/fixtures/` alphabetically (> `r99b_modes.gd`); out-of-scope candidates recorded as hand-off, not deleted.
3. For each candidate: copy repo tree to scratch, apply deletion, run the single targeted fixture headless, diff stdout bytes + exit code vs unmodified baseline.
4. Emit ready-to-apply `diff -u` patches (against untouched copies) + before/after evidence lines. Orchestrator applies; seat does not edit repo.
5. Never run `corpus/fixtures/run_battery.py`; never edit shared registry files; all mutation work in scratch.

## Host load context (once)
```
$ uptime
 16:21:24 up 1 day, 16:21,  1 user,  load average: 41.05, 21.42, 13.72
$ uptime   (end of seat)
 16:27:32 up 1 day, 16:27,  1 user,  load average: 48.26, 44.63, 27.29
```
Godot `4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`). No retry-storm needed; per-launch ~0.8 s even at load 41–48.

## 0. Scratch-location deviation (disclosed)
`/tmp` is a tmpfs with `usrquota` and is **exhausted for this user**: a 1-byte write to `/tmp/r101-simp2/t.txt` returns `echo: write error: Disk quota exceeded` although `df` shows 3.1 G "avail" (same wall r100-simplifier hit, `reports/round-100/r100-simplifier.md` §header). Scratch therefore lives at **`/var/tmp/r101-simp2/`** (root fs, 771 G free) — same `git archive` fresh-extraction contract, different mount.

## 1. Scope (16 entries > `r99b_modes.gd`, LC_ALL=C)
`rb_lattice.gd rb_watch.gd run_battery.py* save_process.gd save_roundtrip.gd scene_a.tscn scene_b.tscn scene_io_lattice.gd scene_marker.gd slider_adjust.gd spontaneous_crash_probe.gd stream_attribution_probe.gd stree_lattice.gd tilemap_lattice.gd timeout_probe.gd tween_flash.gd ui_signal_hud.gd`
(`run_battery.py` is shared/immutable for this seat — never edited, never run.)

Baseline bytes are committed bytes: `git archive HEAD corpus/fixtures | tar -x -C /var/tmp/r101-simp2/`; staged `stree_lattice.gd` sha256 `61954f87f453762e5291a01422ff55e858d51d7ca0ce2a909a29f9115d33c528` and `scene_io_lattice.gd` sha256 `8aeab1cb5492320eb3ba407e1c1f9db32fe6bdee10a4ca607b8004eeefe1302d` — both byte-equal to the working tree at seat start and to the shas cited by `reports/round-97/r97-author.md:31` / `reports/round-96/r96-author.md:22`.

## 2. Harvest result — where the queue actually sits
| round | queued item | target file | in SIMP-2 scope? |
|---|---|---|---|
| r91 | dead `SETTLE` const + 2 write-only `hits` sinks (−3) | `nav_lattice.gd` | no — SIMP-1 half |
| r95 | 15 dead stores (F2) | `dss_lattice.gd`, `r95b_order.gd` | no — SIMP-1 half |
| r95 | `--offy` phantom row (F1, C3 claim) | `r95b_order.gd` | no — SIMP-1 half |
| r96 | −55-line fold across 6 fixtures | `scene_io_lattice.gd` (−12) + `r96b_*` (5 files) | **yes, scene_io −12** |
| r97 | −21 fold, F1–F5 | `stree_lattice.gd` (−17) | **yes, stree −17** |
| r97 | F6 dead field `ready_ticks` (−4) | `r97_scene_marker.gd` | no — SIMP-1 half (hand-off §7) |
| r98 | −19 fold (F1–F4/F6, F5 dropped) | `canvas_lattice.gd`, `r98b_attack.gd` | no — SIMP-1 half |
| r99 | conservative −2 | `audio_lattice.gd`, `r99b_modes.gd` | no — SIMP-1 half |
| r100 | −2 (dup CASES rows landed at `9ede7c50`; dead `--arm` path) | `run_battery.py`, `r100b_seq.gd` | no — SIMP-1 half / shared |

Both SIMP-2 queue items are **still unlanded in the working tree** (candidate tokens present: `it_valid(`, `_tree_names`, `var child := _mk_child`, `var e2 := ResourceSaver.save(b, p2)`, terminal `= null` stores) — patch shards below land them.

## 3. Patch A — `stree_lattice.gd` (−17 lines, 941 → 924; r97 F1–F5, F6 excluded as out-of-scope)
- F1 `_tree_names()` deleted (dead helper; r97-simplifier LSP refs = declaration only).
- F2 `it_valid()` forwarding alias folded to `_it()` — **51 call sites**, def deleted.
- F3 `it_connected(k, v)` folded to `_it(k, _v(v))` — **6 call sites**, def deleted.
- F4 `it_paused(n)` folded to `_it("paused_seen", str(n))` — **3 call sites**, def deleted.
- F5 `_arm_defer_ladder` comment: restated general L10 law replaced by pointer to the header laws block (comment-only, −1).
- Fold builder: `reports/round-101/mutations/r101-simp2-fold_stree.py` (exact-string, every edit count-asserted; asserts no `it_valid|it_connected|it_paused|_tree_names` remains).
- folded sha256 `4c457f887d933760f0ce446d68fda935a561689995f356384d7b3520e754314e`, 34 675 → 34 029 bytes.
- patch `reports/round-101/mutations/r101-simp2-stree_lattice.gd.diff` (368 lines, 73 `-` lines) sha256 `e830869f45aa5aab…`.

## 4. Patch B — `scene_io_lattice.gd` (−12 lines, 839 → 827; r96 simplifier fold)
14 edit sites: 2 binding→bare-call rewrites (0 net lines; the side-effecting `_mk_child`/`ResourceSaver.save` calls stay invoked) + 12 terminal `= null` stores after last read (`l1` takeover; `cached/stale/repl/ign/ign2/ign3` cache; `spr.texture` + `gt` subres; `loaded` extres; `back` editstate; `loaded` refuse). **Kept** `var loaded = ResourceLoader.load(p)` in `_arm_refuse` — r96 proved the *binding* is liveness-load-bearing; only its terminal store is dead.
- Fold builder `…/r101-simp2-fold_scene_io.py`; folded sha256 `18bc06da6c4d5ca6c261051f9ee56eb4b0de0b4f60ba33a764a1ddae184fff50`; patch `…/r101-simp2-scene_io_lattice.gd.diff` (74 lines, 14 `-`) sha256 `ad7fc4984b6d56ca…`.
- `patch -p1 --dry-run` on a committed-byte copy: both patches "checking file …" exit 0 (no fuzz).

## 5. Verification (executed, not inferred)
Method: `reports/round-101/mutations/r101-simp2-v.py` replicates `run_battery.py`'s staging byte-for-byte (fixture copy, project-name munge, `controls/pickup.tscn` staging, causal-chain two-frame anchor fix) and launches
`godot --headless --path <scratch> --script res://<fixture> -- <flags>`, recording merged stdout+stderr + rc (the battery's own `run_process` shape).
Row set: **25 real rows** (13 `r96_scene_io_*`, 12 `stree_lattice_*`) + 2 unknown-arm controls, parsed from CASES.

| check | command | result |
|---|---|---|
| baseline (committed bytes) | `python3 v.py run --src corpus/fixtures --rows rows.json --out committed.json --stamp committed1` | 27/27 launched, rc as pinned |
| folded bytes | same with `--overlay stree_lattice.gd=folded/… --overlay scene_io_lattice.gd=folded/…` | 27/27 launched |
| cross diff | `python3 v.py diff --a committed.json --b folded.json` | `rows=27 raw_diffs=1 masked_diffs=0` |
| rep 2 both sides | two more full sweeps (`committed2`, `folded2`) | committed rep1↔rep2 `raw_diffs=0`; folded rep1↔rep2 `raw_diffs=0`; cross rep2 `raw_diffs=1 masked_diffs=0` |
| battery-pin classification | `python3 classify.py committed.json folded.json` (parses the battery's 509 CASES via `ast`, battery NOT run) | committed **25/25 pass**, folded **25/25 pass** (rc + signature substring) |
| detector teeth | 1-token mutants (`group_meths`→`group_methx`, `save_missing_dir=`→`save_missing_dirX=`), 2 launches | `rows=2 raw_diffs=2 masked_diffs=2`; `classify.py teeth.json` → **2/2 FAIL** (`sig=False`) — the comparator and the battery's pin both have teeth |

The single raw diff is the declared backtrace-line-number class and nothing else: `r96_scene_io_refuse` prints `ERROR:` backtraces containing `_arm_refuse (res://scene_io_lattice.gd:746)` → `:735` (after the 11 deletions above line 746); mask `res://…\.gd:\d+` makes it equal, exactly the class r96-simplifier declared. Full per-row tables: `reports/round-101/mutations/r101-simp2-evidence.txt` (sha256 `b4e2baacd21cd582…`).

## 6. Static census of the other 14 scope files (textual, unexecuted — labelled as such)
- Terminal `= null` store-after-last-use (the r96 fold class): **0 candidates** in all 14 files.
- Defs with ≤1 occurrence (declaration only): only engine-invoked lifecycle callbacks — `_initialize` (10 files), `_input` (`slider_adjust.gd:11`) — both are the documented engine-invoked class (r90-SP9/r95-SP11 precedent), **not** deletions.
- `tilemap_lattice.gd` carries r92-simplifier's independent "zero provable YAGNI deletions" (14 rows ↔ 14 arms) — corroborates the census. Not re-audited here beyond the scan.

## 7. Hand-offs (no repo edits by this seat; orchestrator decides)
1. `r97_scene_marker.gd` F6 `ready_ticks` (−4) — queued, in SIMP-1's half; not touched here.
2. SIMP-1-half queue: nav_lattice −3 (r91), dss_lattice/r95b_order −15 stores (r95), canvas_lattice/r98b_attack −19 (r98), audio_lattice/r99b_modes −2 (r99), r100b_seq dead `--arm` path (r100).
3. r96 critic/scribe comment drift in `run_battery.py` ("two cases / 15 entries" vs actual 3/16) — shared file, orchestrator-owned.
4. Landing these two patches stales provenance citations (`reports/round-97/r97-author.md:31`, `reports/round-96/r96-author.md:22` cite the pre-fold fixture shas). No runtime pin exists: `run_battery.py` cites only the *scout probe* shas in comments (grep confirmed; no `hashlib`/assert on fixture bytes).
5. C1/C2/C3 of this round were not this seat's remit and are untouched (no overlap with the E/D seats).

## 8. Limits / unknowns
- Two fixture files (`stree_lattice.gd`, `scene_io_lattice.gd`) were verified by **targeted rows only** (25 rows × 2–3 sweeps), not by a full-battery run — hard rule 1. The classify step re-uses the battery's own pins so the acceptance shape is the battery's.
- The folded sprites' byte-stability was measured over 2 fresh-process reps per side (raw-identical); longer-horizon flake classes (wall-clock, load) are outside this seat's window.
- Own-scan results in §6 are textual (grep/occurrence), explicitly **not** execution-proven, and are reported as census only, not as fold candidates.
- Seat wrote nothing tracked; deliverables are the two patches + builders + evidence under `reports/round-101/mutations/r101-simp2-*`. Nothing committed (orchestrator owns round close).
