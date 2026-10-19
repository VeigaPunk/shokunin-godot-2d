# Round 103 — landing queued simplifier folds: byte-identity per evidence class, and probe reject-arm print law

Two laws closed on Godot **4.7.2.stable.arch_linux.ed1daf0bf** (`/usr/bin/godot`) headless, on
the r103 host. Both are about *text the harness emits*, not about engine behavior:

1. A **simplifier fold queued by an earlier round** (proved there, never landed) may only be
   landed after re-proving it at HEAD, and the re-proof must state byte-identity **per
   evidence class** and show **discrimination preserved**. Three such folds landed in r103
   (−10 lines total).
2. A **probe's per-arm `FAIL` line is informational, not a verdict**. Designed reject arms
   must print a designed verb; the round's counts come from the probe's meta record.

## The three queued folds at r103

| fold | source round | file | slice | lines |
|---|---|---|---|---|
| F6 | r97-simplifier §3 | `corpus/fixtures/r97_scene_marker.gd` | dead `ready_ticks` + its `_ready()` | 7 → 3 (−4) |
| F2 | r99-simplifier §2 | `corpus/fixtures/r99b_modes.gd` | dead `var pairs: Dictionary = {}` in `_arm_splitcycle` | 453 → 452 (−1) |
| SP2+SP3 | r100-simplifier §3/§5 | `corpus/fixtures/r100b_seq.gd` | dead `--arm=` parse in `_initialize` + `arm` carrier → `match a:` | 790 → 785 (−5) |

Patches of record (all `git apply --check`-green at HEAD `6e3e87f7`):
`reports/round-103/mutations/r103-S0-E1-r97-F6-scene_marker.patch`,
`…-E2-r99-F2-r99b_modes.patch`, `…-E3-r100-SP2SP3-r100b_seq.patch`.

```text
pre  sha256  b680e6f2… (453)  r99b_modes.gd      post sha256 e5e72573… (452)
pre  sha256  4718a19e… (790)  r100b_seq.gd       post sha256 e77dc55c… (785)
pre  sha256  39763310… (7)    r97_scene_marker.gd post sha256 2b9bd633… (3)
```

## Reproduce (battery launch shape, battery classifier semantics)

```text
godot --headless --path <proj> --script res://<fixture>.gd -- <flags>
```

`<proj>` = a copy of `corpus/fixtures` (the battery stages exactly that:
`run_battery.py:1740-1754`, `config/name` rewritten for `user://` isolation); the row's
`output` is `proc_stdout + proc_stderr` (`run_battery.py:1938`) and `classify_process`
matches `signature in output` as a plain substring (`run_battery.py:1792-1808`).

Rows re-proved (r103cR3 receipts, pre/post × 2 reps):
`r99b_modes.gd --arm={startphase,mixfree,finfree}`,
`r100b_seq.gd --clean={1,0}`,
`stree_lattice.gd --arm={scene_probe,census}` (scene_probe is the F6 consumer — it loads
`res://r97_scene_a.tscn`, whose `r97_scene_marker.gd` script carries `tag`).

### Law 1a — byte-identity belongs to an evidence class, not to "the output"

| evidence class | verdict on these folds | measured |
|---|---|---|
| full merged transcript | **not** preserved in general | `r100b_seq` merged sha changes (`63e48ee1…`→`a727872a…` clean; `9b15512b…`→`11141490…` noclean) |
| stdout bytes | preserved on every case | `2fc9a28f…`/`bb1e7676…` (r100b_seq) and `39e97921…`/`a7fb7e34…`/`1a31e150…` equal ×4 receipts |
| row signature substring (the graded class) | preserved | 28/28 receipts match (7 rows × pre/post × 2 reps) |
| pinned law substring on a wall-clock instrument | preserved, and that is the *only* sound class | `r99b_mixfree`/`r99b_finfree` vary run-to-run on the **same** side (`blocks=7` vs `blocks=8`; `transition_f=44` vs `48`) |

Why the merged class breaks: `r100b_seq.gd`'s render cell headless-raises
`ERROR: Parameter "t" is null.` with a **GDScript backtrace carrying source line numbers**.
The SP2/SP3 fold deletes 5 lines above those sites, so the stderr bytes move:

```text
pre   [0] _cell_render (res://r100b_seq.gd:762)   [1] _run (…:116)   [2] _cleanup (…:135)
post  [0] _cell_render (res://r100b_seq.gd:757)   [1] _run (…:111)   [2] _cleanup (…:130)
```

The row survives because its signature is a stdout line and the allowlist entry is compared
stripped-line-exact (`'ERROR: Parameter "t" is null.'`), never by offset. A
whole-transcript pin (the r101 `PALL` shape) on a fixture like this would go red on any
line-count change **above** the diagnostic site — pin stdout blocks on folded fixtures, or
regenerate the transcript pin in the same change.

### Law 1b — discrimination preserved is proved by mutants, not by passing

Passing rows after a fold prove nothing on their own. Mutate a *live carrier of the pinned
law* in the **post** tree and show the row now rejects (signature miss = `classify_process`
False):

| mutant (post tree, 1-line) | row | signature_match | verdict if rowed |
|---|---|---|---|
| `r97_scene_marker.gd`: delete `@export var tag := "?"` | `stree_lattice_scene_probe` | false | FAIL |
| `r99b_modes.gd`: `_p(all_q),` → `_p(false),` | `r99b_mixfree` | false | FAIL |
| `r100b_seq.gd`: `out.append("c0=%s" % …)` → `out.append("c0=MUTATED")` | `r100b_seq_clean` | false | FAIL |

Deadness of the deleted slices is a separate, cheaper check: `grep -rn '\bready_ticks\b'`
finds only its own declaration/increment (5 trees); at r100-simplifier the `--arm=` parse is
unobservable because `_run()` overwrote `arm` before every `match`, and no consumer of
`r100b_seq.gd` ever passes `--arm=` (its only two rows pass `--clean=0/1`).

### Law 1c — a pinned prefix leaves its tail unconstrained

`r99b_startphase`'s signature ends at `imm_uniq=1`; the same line continues with
`one=[…] one_q=[…] one_uniq=1`. A drift in the unpinned tail is invisible to the row — if the
tail matters, extend the signature in the same change that proves it (the r101 lesson's
"pin the transcript, not one line" is the multi-line form of this).

## Law 2 — probe reject-arm prints are informational; counts cite the meta

The godot-error and stream-attribution probes run one accept and one **designed reject** arm.
Both print through byte-identical f-strings (`run_battery.py:4647` and `:4720`):

```python
print(f"{'PASS' if inner else 'FAIL'} {label}: exit={code} classification={inner}", flush=True)
```

For the designed arm `inner` is False **by construction**, so the harness prints
`FAIL godot_error_unrelated: exit=1 classification=False` (and `FAIL stream_reject: …`).
Real captured bytes of those arms (r103cR3, HEAD fixtures):

| probe fixture invocation | exit | merged bytes | sha256 |
|---|---|---|---|
| `godot_error_probe.gd` (accept) | 1 | 316 | `a4df8c70fc3f3a9c…` |
| `godot_error_probe.gd --unrelated-error` (designed reject) | 1 | 529 | `8e62ad5a635ed48b…` |
| `stream_attribution_probe.gd` (accept) | 0 | 143 | `a3238da0817f995d…` |
| `stream_attribution_probe.gd --stderr-unrelated` (designed reject) | 0 | 191 | `bc1d2ecd8b880ac5…` |

r102 already ruled this informational ("2 reject-arm print lines informational (probe metas
green)", `SCORECARD.md:311`; routed in `LOG.md:1245`). The fix is **print-only**: designed
arms print a designed verb, mismatches still print `FAIL`, and no verdict variable, payload
field or meta conjunct moves — patch of record
`reports/round-103/mutations/r103-S4-probe_reject_prints.patch` (sha256 `4f111944…`, 2 hunks
at 4644/4717), printing `REJECT-ARM (designed) <label>: exit=<code> classification=<inner>`;
an equivalent variant that makes the expectation explicit (`designed_inner` in the arm tuple)
is `reports/round-103/mutations/r103-V7-reject-arm-prints.patch`. S4's replay proved the
patched probe's captured stdout differs in exactly that one line per probe and that
`results.json` / `*-verdicts.json` are byte-identical after a run-dir path scrub.

**Count law.** The number of `^PASS` lines in a battery stdout is not the number of passing
rows: per-arm probe lines include designed rejects. Count rows from the recorded `verdict`
fields, and probe health from its meta record (`probe_godot_error`,
`probe_stream_attribution`). Historical receipts still contain the old `FAIL …` shape —
preserve them, do not rewrite history.

## Pitfalls

* Claiming "byte-identical" without naming the class. stdout can be identical while stderr
  moved (line offsets) and the merged digest changed.
* Landing a fold proved in an earlier round without re-proving at HEAD: fixtures drift between
  rounds (the r99-simplifier `patchcheck` copy already differed from HEAD by another fold).
* Treating wall-clock instruments (`r99b_modes` mixfree/finfree) as byte-stable: only their
  pinned law substring is stable; two reps of the same side already differ.
* Mutating the *deleted* code to "prove" deadness — deleted code cannot be mutated. Deadness
  is shown by readers (`grep`) and by the overwritten-before-use data flow; teeth are shown by
  mutating a **live** carrier in the post tree.
* Rewriting logged receipts or the old probe line shape after the print fix lands.

## What is proved / not proved

Proved on this host/engine: the three fold patches apply clean at `6e3e87f7`; stdout sha256 is
equal pre/post for the 7 re-proved rows (2 reps each); the 7 AST-extracted signatures match
28/28 receipts; the 3 mutants each reject; `r100b_seq` stderr differs only in three backtrace
line numbers; the four probe-fixture captures above; the two print sites are the only
occurrences of that f-string shape (grep = 2).
Not proved: other hosts/engines; that no further drift exists between `corpus/live/*`
snapshots and HEAD; that the S4/V7 patch variants are equivalent under review (only S4's was
replayed by its author); the count-law audit of every historical receipt.
