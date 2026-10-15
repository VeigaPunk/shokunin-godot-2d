# r86 verifier — 2D backend-select lattice (phys2d_backends, 8 cells)

Seat `VERIFIER` | round 86 | host **devin** | Godot `4.7.2.stable.arch_linux.ed1daf0bf`
headless (`/usr/bin/godot`), Python 3.14.7. Verified commit `7ae7083` (tracked
fixtures untouched; `git status` clean for `corpus/fixtures/` — forge work was
confined to `corpus/live/r86-verify/forge-scratch/`).

Independent evidence: `corpus/live/r86-verify/run1/20261015T133754513801Z/`,
`run2/20261015T134054380982Z/`, `standalone/report.json`, `forge_report.json`.
Author receipt `corpus/live/r86-author-battery/` was **not** trusted — all
results below are from my own fresh processes.

## Check 1 — fresh battery run → **PASS**

`python3 corpus/fixtures/run_battery.py --runs corpus/live/r86-verify/run1`
→ **182/182 PASS** (`verdicts.json` `verdict=PASS`, all 182 results PASS, 0
FAIL lines in `run1.log`). Matches the author's 182/182 claim.

## Check 2 — second run + byte-compare → **PASS**

`run2` → **182/182 PASS**, identical case order. For all 8
`phys2d_backends_*` rows the emitted `PASS` line is **byte-identical** to the
pinned `CASES` literal **and** byte-identical across run1/run2
(`run1==run2==pin` for all 8). Independently, my standalone driver ran each arm
as 3 fresh processes in a separate scratch project: **24/24 runs `uniq=1`,
`pin_match=True`, rc=0, parent stderr = 0 B**. The author's
`standalone.json` pins are byte-identical to the committed `CASES` literals
(8/8), so the "rows pasted from standalone pins" claim is accurate.

Note (pre-existing, out of r86 scope): 5 of the 174 old rows emit volatile
output across run1/run2 under substring pins — `tween_flash` (float jitter),
`save_roundtrip`/`save_process_*` (pid, absolute path). Verdict and signature
fields are unaffected; the pins are deliberate prefixes. Not a regression.

## Check 3 — prior-row stability vs r85 receipt → **PASS**

Against `corpus/live/r85-foldc-final2/20261015T085238195177Z/verdicts.json`
(174 rows): with the 8 new rows excised, **name order is identical** and
**0 field mismatches** on `verdict`, `signature`, `expected_exit`,
`actual_exit`, `expected_errors` — for **both** run1 and run2. The new rows
occupy result indices 163–170 (between the last `camera_proc` row and
`crash_spontaneous_sigabrt`), respecting the descendant-tail ordering
constraint documented in `run_battery.py`.

## Check 4 — forge-kill → **PASS**

Scratch-only mutations (`corpus/live/r86-verify/forge-scratch/`), battery
`execute()`+`classify_process()` semantics replicated for the
`phys2d_backends_lattice` row:

| condition | verdict |
|---|---|
| control: clean fixture, real pin | PASS |
| fixture forge: `["jolt", …]` row deleted from `LAT` → emitted signature loses the `jolt{stored=[Jolt Physics],…}` segment | **FAIL** (`pin_present=False`) |
| pin forge: `moved=17.867`→`moved=17.866` in the pin vs clean output | **FAIL** |

The witness catches both directions. Residual bound: a fixture that prints the
pinned string verbatim while skipping measurement is still undetectable by this
harness — signature pins are not proof-of-work; mitigated here only by the
fixture's structure (each field is a measured child-boot value).

## Check 5 — arm-level claims → **PASS**

- **Volatile tokens:** regex scan (abs paths, pids, timestamps, hex addrs,
  RIDs/object ids) over all 8 emitted signatures ×3 reps → **NONE**. The sole
  `rid` hit is the literal dict-key `"rid"` inside `ray_keys=[…]`.
- **Nested-boot state leak:** `user://r86bt/<arm>/<tag>` dirs are `rm -rf`'d at
  arm end — post-run `r86bt` husks are **empty** in my standalone dir, the
  author battery dir, and both verify battery dirs. Per-run isolation via the
  battery's stamped `config/name` holds; each `_boot` rewrites
  `project.godot`/`child.gd`/capture files fresh, so even a leftover could not
  contaminate. The child project's own `app_userdata/R86BT/` accumulates only
  engine log files (out of measured streams; minor disk note, not a leak).
- **`expected_errors=()` honesty:** parent stderr = **0 bytes** on all 24
  standalone reps and all 16 battery row-runs; battery rows carry
  `expected_errors=[]` and PASS — no engine `ERROR` escapes the child captures.
  Verified by `--keep`: `thr` child's `err.txt` holds the 5
  `space_get_direct_state` ERROR frames the signature counts (`errs=5`),
  `def`/`nf` are empty; parent stderr still 0 B with `--keep`.
- **Tracked-file hygiene:** `git status` shows no modification to
  `corpus/fixtures/`; HEAD = `7ae7083` as claimed.

## Verdicts

| check | result |
|---|---|
| 1 fresh battery 182/182 | PASS |
| 2 byte-stable sigs vs pins, run1=run2 | PASS |
| 3 prior 174 rows identical vs r85 | PASS |
| 4 forge-kill (fixture + pin mutation) | PASS |
| 5 volatile tokens / state leak / expected_errors | PASS |

## **ADMIT**

The 8 cells are byte-pinned, deterministic across fresh processes and full
battery runs, honestly classified (`expected_errors=()` verified against split
child captures), forge-sensitive in both directions, and non-regressing on all
174 prior rows. The author's receipt stands.
