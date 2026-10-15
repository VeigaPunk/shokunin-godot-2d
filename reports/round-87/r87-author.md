# r87 author — input event/action lattice armed (25 cells, 4 mode-envelopes)

Seat `AUTHOR` (g2d lane r87) | host **devin** | Godot `4.7.2.stable.arch_linux`,
Python 3.14.7. HEAD `fad0b1e` (uncommitted worktree changes only — nothing
committed). No `lsp` device exposed; no GDScript/Python server installed —
same host state as scout; all work was fixture-level file landing + harness
inserts, verified by fresh-process execution, not symbol operations.

## Landed files

| file | sha256 | provenance |
|---|---|---|
| `corpus/fixtures/input_lattice.gd` | `2b68531d…` (854 lines) | byte-copy of `corpus/live/r87-scout/proj/input_lattice.gd` — scout's adopted r83 probe, verbatim |
| `corpus/fixtures/r87_edge.gd` | `7cd80727…` (195 lines) | byte-copy of scout `proj/r87_edge.gd` (jpbe arm) |
| `corpus/fixtures/ei_bound.gd` | `0493a257…` (14 lines) | byte-copy of scout `proj/ei_bound.gd` (event_index refusal boundary) |

`jmode` **not authored** — its histogram *is* the interleave mode (scout §6);
unpinnable by construction.

## run_battery.py changes (insertion-only + one additive mechanism)

1. **CASES 175 → 200** inserted ahead of the crash/descendant tail (before
   `crash_spontaneous_sigabrt`), preserving the descendant `sleep 8` gap:
   - **20 verbatim rows** from `corpus/live/r87-scout/author-rows.py.txt`
     (`input_lattice_<arm>`), plus
   - **4 mode-envelope rows** — signature is a *tuple* of whitelisted full
     PASS-line payloads: `press_phys`, `release_edge`, `ui_ns` (both r10-census
     payloads each), and `pre_frame` (see correction below).
   - **2 edge rows**: `r87_edge_jpbe` (byte-stable ×3 scout + ×3 battery here),
     `ei_bound_refusal` (full 9-line `ei=` ladder pinned as signature).
2. **Envelope mechanism (additive, ~9 lines)**: in `execute()`, when `evidence`
   is a tuple/list, `passed = any(classifier(..., sig, ...) for sig in evidence)`
   — PASS iff any whitelisted payload appears; everything else (exit code,
   unrelated-ERROR scan, SCRIPT ERROR / Parse Error rejection) unchanged.
   `classify_mutant` keys off `evidence[0]` for tuple rows (mutant path only
   fires for seeded mutant rows anyway). String rows take the identical code
   path as before.
3. **`expected_errors` += 3 entries**: `input_lattice_null_edge` (4 lines,
   verbatim from author-rows tail), `ei_bound_refusal` and `r87_edge_jpbe`
   (1 line each: `ERROR: Input singleton does not support more than 32 events
   assigned to an action.` — the `ei≥32` refusal).

## Pre-envelope censes (fresh `godot --headless --path` reps vs landed probe)

Direct reps on a scratch copy of `corpus/fixtures/` (the battery's launch
shape), payload sets diffed against `arms-flaky-r10.json`:

| arm | reps | distinct payloads | identical to r10 whitelist |
|---|---|---|---|
| `press_phys` | 8 | 2 (3-entry `post_ph` ×5, 2-entry ×3) | yes — set-equal |
| `release_edge` | 8 | 2 (`jp=1` ×7, `jp=0` ×1 at `ph+0`) | yes — set-equal |
| `ui_ns` | 8 | 2 (`@ph+0` ×7, `@ph+1` ×1 release receipts) | yes — set-equal |
| `pre_frame` | 24 | 2 (`[ph+0{pf0=1/1.00/1/0}]` ×23, `[]` ×1) | n/a (see correction) |

## Full battery — before/after

| run | rows | verdict | command |
|---|---|---|---|
| baseline (r87-baseline rep1, frozen tree) | 182 | PASS | `python3 -B corpus/fixtures/run_battery.py --runs corpus/live/r87-author/runsN` |
| author rep1 (pre-fix) | 207 | FAIL×2 | `pre_frame` + `r87_edge_jpbe` (see below) |
| author rep2 | 207 | **PASS** | `…/r87-author/runs2/20261015T171747859030Z/verdicts.json` |
| author rep3 | 207 | **PASS** | `…/r87-author/runs3/20261015T172055148545Z/verdicts.json` |

**Prior-182-row identity** (`corpus/live/r87-baseline/compare.py godot <mine>
baseline=<rep1>`), identical for rep2 AND rep3 vs baseline:
`common=182, new_only=25, old_only=0, tuple_mismatches=1 (seeded=0, meta=1)`.
- All 175 prior *seeded* row tuples byte-identical; the 1 meta diff is
  `probe_error_clause_surface` — its census intentionally enumerates every
  CASES row carrying `expected_errors`, which now includes the 3 new
  whitelists. Expected, not drift.
- `output-normalized identical=173, differing=2`: `export_readiness` /
  `export_preset_missing` line 11 `Registering global classes (36 steps)` vs
  baseline `(33 steps)` — +3 = the three landed `.gd` files scanned at export.
  Attributable progress-log jitter; signature/verdict unchanged.
- rep3 vs rep2: `tuple_mismatches=0`; 1 output diff = `pre_frame` emitting its
  *other whitelisted payload* (`post_ph=[]` vs `[ph+0…]`) — the envelope doing
  its job.

## New-cell rep counts (battery reps, incl. pre-fix rep1)

| cell | hits |
|---|---|
| `input_lattice_press_phys` | 3/3 PASS, all mode-A (3-entry `post_ph`) |
| `input_lattice_release_edge` | 3/3 PASS, all `jp=0` payload |
| `input_lattice_ui_ns` | 3/3 PASS, all `@ph+1` payload |
| `input_lattice_pre_frame` | rep1 `[]`, rep2 `[ph+0]`, rep3 `[]` — both modes observed across reps |
| `r87_edge_jpbe` | 3/3 identical PASS line + 1 whitelisted ERROR |
| `ei_bound_refusal` | 3/3 identical ladder + 4 whitelisted ERROR lines |

## Corrections to scout claims (disclosed)

1. **`pre_frame` is not pinnable as written** — scout marked it "clean ×9,
   latently shaped like `press_phys`". Battery rep1 empirically produced
   `post_ph=[]` (zero physics ticks inside the 3-`process_frame` window). It is
   the same n-modal ph-count shape; armed as a 2-payload envelope covering
   both modes observed in 24 direct reps + 3 battery reps. **Residual risk:**
   a ≥2-tick window (`post_ph=[ph+0{…} ph+1{pf0=1/1.00/0/0}…]`) is physically
   possible but never observed in 33 cumulative reps on this host; if it ever
   appears the row flakes — recut (ph-anchor the window) rather than widening.
2. **`r87_edge_jpbe` needs a whitelisted ERROR** the scout didn't list: the arm
   deliberately parses `event_index=42` (`bad_st` cell) → emits the typed
   `input.cpp:1010` refusal to stderr, deterministically (all 3 scout `.err`
   receipts carry it, 142 bytes each). Whitelisted; verdict was "byte-stable"
   on stdout only.
3. Scout's `expected_errors` guidance covered only `null_edge` (+optional
   `ei_bound`); jpbe's whitelisted line is an addendum, not a contradiction of
   measured bytes.

## Remaining risks / blockers

- Envelope cells whitelist **observed** payloads only; an unobserved mode
  (heavier/lighter ph:pr interleave on another host/load) flakes loudly —
  that is the intended semantics of a mode cell.
- `jmode` deliberately omitted (unpinnable histogram); `event_index 1..31`
  silent-drop semantics unprobed beyond the boundary map.
- No commit made; worktree carries: `M run_battery.py`, `?? input_lattice.gd`,
  `?? r87_edge.gd`, `?? ei_bound.gd`, receipts under `corpus/live/r87-author/`.
