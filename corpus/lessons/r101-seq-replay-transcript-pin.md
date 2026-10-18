# Round 101 — `r100b_seq`: pin the whole replay transcript, not one line

Closes r100-critic **F2**: each `r100b_seq_*` row pinned 1 line of a 14-cell
replay, so a forged extra output line rode both rows to PASS and 3 of the
replay's 4 measured divergences from the fresh-process pins were unconstrained.

Reproduce on Godot **4.7.2** (`/usr/bin/godot` → `4.7.2.stable.arch_linux.ed1daf0bf`):

```text
godot --headless --path <scratch> --script res://r100b_seq.gd -- --clean=1
godot --headless --path <scratch> --script res://r100b_seq.gd -- --clean=0
```

`<scratch>` = a project dir containing `corpus/fixtures/r100b_seq.gd` (sha256
`4718a19e…`) + the r100-boundary `project.godot` (sha256 `8de8b3af…`). Launch
shape is the battery's (run_battery.py:1862); the row's `output` is
`proc_stdout + proc_stderr` (run_battery.py:1870-1871), and `classify_process`
matches `signature in output` as a plain substring (run_battery.py:1725-1742).

## The gap, measured

The replay prints all 14 `PASS r100_gui <cell> …` lines in one process, then
`SEQ_DONE clean=N` (17 stdout + 6 stderr = 23 merged lines). The landed rows
pinned one line each. Measured on captured bytes
(`reports/round-101/mutations/scr2_seq_gap_demo.py`, log in the r101 SCR-2 shard):

| mutation | landed rows | verdict |
|---|---|---|
| forged extra stdout line at any of the 13 inter-cell seams | `seq_clean` + `seq_noclean` | both **PASS** (gap) |
| replay→fresh line swap: `touch` / `subvp` / `warp` (clean; same in noclean) | `seq_clean` | **PASS** (gap) |
| replay→fresh line swap: `motion` / `localpos` / `clip` / `drag` (noclean) | `seq_noclean` | **PASS** (gap) |

Each row discriminated exactly 1 of 14 cells (`cursor` / `hover`); the clean
row's `cursor` pin is even byte-identical across `--clean=1` and `--clean=0`.

## The closure

A multi-line signature is expressible without touching `execute()`: build it
from the **replay's own measured bytes** (never from the fresh-process pins):

* **P14** = `"\n".join` of the 14 cell lines in `make_seq.py` ARMS order
  (`census routing hover motion localpos cursor clip drag touch subvp warp focus render osmeta`)
* **P15** = P14 + `"\n" + "SEQ_DONE clean=N"` (recommended tail anchor)
* **PALL** = the whole stdout block, banner included (strict edge closure;
  couples the row to the engine banner string — use only if that coupling is accepted)

As adjacent string literals in the CASES tuple:

```python
('r100b_seq_clean', 'r100b_seq.gd', ['--clean=1'], 0,
 'PASS r100_gui census …'
 '\nPASS r100_gui routing …'
 …  # one source line per cell, '\n'-prefixed
 '\nSEQ_DONE clean=1'),
```

Measured catch matrix (production classifier semantics on real captured bytes):

| mutation | landed 1-line pins | P14 | P15 | PALL |
|---|---|---|---|---|
| baseline | PASS | PASS | PASS | PASS |
| forged line, seams after `census` … `render` (13) | PASS | FAIL | FAIL | FAIL |
| forged line, seam after `osmeta` | PASS | PASS | FAIL | FAIL |
| forged line, head (before `census`) | PASS | PASS | PASS | FAIL |
| replay→fresh swap of any divergent cell | PASS (own cell excepted) | FAIL | FAIL | FAIL |

The full pin also freezes the contamination evidence itself: the 4 measured
clean divergences (fresh → replay) are `cursor c0=(0.0, 0.0)→(30.0, 14.0)`;
`touch t3_emul_touch a=[A:mb(b=1,p=1,dc=0,bm=1,…)|A:st(…)]→a=[A:st(…)] only`;
`subvp cursor_root=(0.0, 0.0)→(20.0, 4.0)`; `warp cursor=(0.0, 0.0)→(20.0, 4.0)`.
The noclean replay diverges in 9 cells (adds `hover h0=null→P`, `motion m1[-]`,
`localpos c[-]`, clip far-press `ed=[ED:…]`→`ed=- fa=[FA:…]`, `drag d2
data=null`). Pin the replay's values — do not "correct" them to the fresh pins.

## Verification recipe (red/green)

1. Capture stdout/stderr split for both variants (same launch shape).
2. Build P14/P15 from the 14 cell lines; assert this host's digests:
   clean P14 `5be029c7…` (6685 B), noclean P14 `da5cd7d7…` (6160 B);
   clean P15 `3bd85c74…` (6702 B), noclean P15 `0975086d…` (6177 B).
3. Red check: with the landed 1-line pin, `FORGED_EXTRA_CELL_OUTPUT` inserted
   between the `hover` and `motion` lines still classifies PASS.
4. Green check: same bytes against P14 classify FAIL; the forgery rejects.
   (`scr2_seq_gap_demo.py` runs both, plus all 15 seams and every divergence swap.)
5. Keep the `'ERROR: Parameter "t" is null.'` allowlist entry on both rows
   (the render cell's headless backbuffer readback).

## Pitfalls

* Pinning fresh-process lines instead of replay lines is false-red at landing
  and erases the contamination evidence the rows exist for.
* The two variants' transcripts differ (9 cells + the `SEQ_DONE` suffix); pin
  each row against its own variant.
* The 14 cell lines are stdout; the render `ERROR:` block is stderr and is
  appended after stdout in the row's `output` — do not interleave it into the pin.
* The classifier is an exact substring test: no regex, no trailing spaces, no
  CRLF; a migrated reformat of the CASES literal must preserve the joined bytes.
* P14 leaves the head seam open and P15 leaves only the head seam open; PALL
  closes everything at the cost of engine-banner coupling. State the residual.
* On a legitimate engine/transcript change, regenerate the pin from a fresh
  capture and update the divergence table — never relax back to one line.

## What is proved / not proved

Proved: on this host/engine, the replay transcripts are byte-stable ×2 per
variant; the landed one-line pins PASS a forged extra line at every seam and
PASS every divergent-cell swap except their own cell; P14/P15 reject the forgery
and all divergence swaps; the pin digests above.
Not proved: other hosts/engine builds; the specific P14-vs-P15-vs-PALL choice
the landing uses; the same class in other multi-cell-replay fixtures (not surveyed).

