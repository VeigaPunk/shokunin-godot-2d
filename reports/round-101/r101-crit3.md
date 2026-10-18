# r101-crit3 — CRIT-3 attack on C3 (r95 `--offy` dead flag)

Load context (`uptime`): `16:21:22 up 1 day, 16:21, 1 user,  load average: 41.05, 21.42, 13.72`
and at shard write `16:29:44 ... load average: 30.24, 40.11, 28.00`. Sibling 3D lane r104
running heavy; all Godot runs below are targeted `--headless` scratch runs, never the battery.

## PLAN (5 lines, as written before execution)
1. Read r100-critic §F2 + r94 cpu_contam precedent + r95 `--offy` claims to fix the attack targets precisely.
2. C3a: locate every `offy` read path in `corpus/fixtures/`; run a reachability census (grep + AST-ish scan) for the flag.
3. C3b: reproduce the r95 `--offy` invocation verbatim and record observed output bytes — measurement vs claim.
4. C3c: load-bimodality probe — run one identical fixture scenario N times under current load, record timing spread.
5. C3d: tautology/bookkeeping audit of C3's own claims; write shard, no shared-file edits, no battery run.

## Verdict

**C3 must not be closed by "census + echo token".** The defect is wider than the r95 filing scoped
it, and the obvious cheap fix (echo `offy=` into the PASS line) is forge-accepting: it converts a
dead flag into an echoed-input tautology of the r94 `cpu_contam` class. C3's deliverable only closes
the class if the pinned surface contains a token **derived from geometry**, not from the flag value.

**Measured against the artifacts actually in flight** (§F2b): E17's `r101_ytrans.gd` and ver8's
`r95b_order.gd` patch both satisfy that criterion for **Y** — each rejects the echo-only forgery and
the dead-translation mutant with my harness-rule classifier. Neither closes the **X** residual (§F1):
after ver8-C the `celloff_x0`/`x1000` rows still accept a fixture that never translates anything.
So the round can land a correct Y measurement, but must either strengthen the X pins or record the
residual explicitly; it must not describe the surviving `celloff` X rows as "real offsets stand".

All receipts below are observations from my runs at the stated load; the reproduction scripts are
`reports/round-101/mutations/r101-crit3-offy-attack.py` (28 launches, ~55 s) and
`r101-crit3-ytrans-check.py` (8 launches, ~15 s), both writing only under `CRIT3_ROOT`/`CRIT3B_ROOT`.

---

## F1 — HIGH (new, widens r95-simplifier F1) · the **whole** `celloff` lattice is dead-path-producible; "the X cells stand" is false at the pin level

r95-simplifier F1 concluded: *"Y-translation invariance is unmeasured, not falsified; the X cells
(real offsets) stand"* (`reports/round-95/r95-simplifier.md:82`). The X cells' **runs** do apply the
offset (`_pile(order, off, 0.0)`, `_ladder(ticks, off)`), but the **pins** do not bind it:

```gdscript
# corpus/fixtures/r95b_order.gd:139-149
func _relpos(arr: Array, ox: float) -> String:
    ...
    parts.append("%.4f,%.4f" % [p.x - ox, p.y])     # x normalised, y raw
# :186-188
func _ladder(ticks: Array, ox: float) -> Dictionary:
    var q := Vector2(16.0 + ox, 0.0)                # query follows ox
```

Mutant `m_dead_off` (2 replacements: `_pile(...,0.0,0.0)`, `_ladder(ticks,0.0)`; the `off=` echo
untouched). Verdicts computed with the harness's own rule (`signature in stdout+stderr`, exit 0,
no `SCRIPT ERROR:`), committed signatures extracted by AST from `corpus/fixtures/run_battery.py`:

| row | command | m_dead_off |
|---|---|---|
| `r95b_order_celloff_x0` | `--arm=celloff --off=0` | **accepted (PASS)** |
| `r95b_order_celloff_x1000` | `--arm=celloff --off=1000` | **accepted (PASS)** |
| `r95b_order_celloff_y1000` | `--arm=celloff --off=0 --offy=1000` | **accepted (PASS)** |

The pinned surface is offset-normalised by construction, so the only pinned token that varies across
the X cells is the echoed input. Measured: `x0` and `x1000` signatures are masked-equal
(`re.sub(r'off=[-0-9.]+','off=X', …)`), i.e. **the entire signature delta between the two X cells is
the echo**. A consistent refactor that stops translating the pile and the query together passes all
three rows. Observed, not inferred.

Consequence for C3: retiring/dropping only `celloff_y1000` leaves the sibling rows unable to bind
translation; the X claim is as bookkeeping-only as the Y one at the pin level.

## F2 — HIGH (new) · the cheap fix is forge-accepting; only a geometry-derived token closes the class

`_relpos` leaves Y raw, so with a live `offy` a naive implementation that moves the pile but not the
query degenerates (`m_live_offy_naive`: y1000 row **rejected**, PASS line
`ladder=[t2:;t3:;…;t64:] distinct_ticks=1 last_change_tick=-1 t2_vec=[]`). Moving the query too, plus
offset-normalising Y, yields a "correct" fixture — but its measured tokens are **still invariant**:

* `m_live_offy_full` (10 replacements: read `offy`, translate pile and query, normalise Y, echo
  `offy=`): PASS lines for `offy ∈ {0, +1000, -777.25}` are **byte-identical after masking
  `off=`/`offy=`** (sha256[:16] `f80130f4c7a364cc` × 4 runs). So all measured tokens carry zero
  information about whether the translation happened.
* `m_live_offy_full_raw` adds one unpinned diagnostic read from geometry:
  `oy_raw`/`ox_raw` from `made[0].global_position` → observed
  `(x=0.0000,y=1000.0000)`, `(x=0.0000,y=-777.2500)`, `(x=1000.0000,y=0.0000)` for the four cells.
  Physical translation is real; the normalised tokens cannot see it.

Pin matrix (flags `--arm=celloff --off=0 --offy=1000`; `PIN_echo_normalised` = the cheap-fix line
with `offy=` but only normalised measured tokens; `PIN_geometry` = same plus
`oy_raw=<pile raw y>`):

| fixture | `PIN_echo_normalised` | `PIN_geometry` |
|---|---|---|
| `m_control` (committed bytes) | reject | reject |
| `m_forge_offy_echo` (echoes `offy=`, **never translates**) | **ACCEPT** | reject |
| `m_live_offy_full` (translates, no geometry token) | accept | reject |
| `m_fix_pinned_live` (translates + `oy_raw`) | reject (tokens differ) | **ACCEPT** |
| `m_dead_off` | reject | reject |

`m_forge_offy_echo` is the decisive forgery: two edits, the flag is echoed, the ladder is the
committed one, `oy_raw` is absent — and the echo-pin **accepts** it. The geometry-pin is the only
candidate that separates a measurement from an echo. (Raw scratch receipts were deleted to keep the
tree clean; `python3 reports/round-101/mutations/r101-crit3-offy-attack.py` regenerates
`mutant_verdicts.json` + `remediation_pin_matrix.json` in ~55 s.)

### F2b — the in-flight fixes, tested on their own bytes (observation)

`corpus/fixtures/r101_ytrans.gd` (E17, sha256 `0d5093d64b3745ce…`) run with the harness shape,
`godot --headless --path <scratch> --script res://r101_ytrans.gd -- --arm=ytrans --offy=1000`:

```
PASS r101_ytrans ytrans offy=1000.0000 add_order=[a,b,c,d,e] dy_resid=0.0000 ladder=[t2:4,0,2,3,1;t3:4,0,1,3,2;t4:4,0,1,2,3;t6:3,4,1,2,0;t8:3,4,0,1,2;t16:1,2,3,4,0;t32:2,3,4,0,1;t64:4,0,1,2,3] distinct_ticks=7 last_change_tick=64 t2_vec=[e#0,a#0,c#0,d#0,b#0] t2_relpos=[32.0000,0.0000|0.0000,0.0000|16.0000,0.0000|24.0000,0.0000|8.0000,0.0000] t2_absy=[1000.0000|1000.0000|1000.0000|1000.0000|1000.0000] t2_vec_eq_canon=true t2_relpos_eq_canon=true n_at_y=5 n_at_0=0 t64_relpos=[32.0000,0.0000|0.0000,0.0000|8.0000,0.0000|16.0000,0.0000|24.0000,0.0000] t64_absy=[1000.0000|1000.0000|1000.0000|1000.0000|1000.0000]
```

* echo-only forgery (my analogue of `m_forge_offy_echo`: echo `offy=1000.0000`, geometry at y=0):
  emitted `dy_resid=-1000.0000 … t2_absy=[0.0000|…] … n_at_y=5 n_at_0=5` → **the live y1000 pin is
  NOT a substring of the forgery** (rejected, 1 launch, exit 0 both sides). The unforgeable part is
  that `dy_resid`/`t2_absy`/`n_at_0` are read from collider nodes, not from the flag.
* `--arm=census` emits `r95b_offy_tokens=0 r95b_lines=778
  r95b_sha256=4f7e945e1b16f241d510e1b1aa7c7fc1aafca6369626e3910bb36cf62d9e2490 replacement_arm=ytrans`
  — an executable retirement census that flips if a reader is added to the r95b source.
* `--arm=ysep`: `dy_resid=0.0000 n_at_q=0 n_at_pile=5` — falsification cell, as claimed.

`reports/round-101/mutations/r101-ver8-offy-C.patch` applied with `patch -p1` to a scratch copy
(live fixture) and then mutated to dead-off (`_pile(...,0.0,0.0)`, `_ladder(ticks,0.0,0.0)`),
classified against the patch's own reissued signatures:

| probe | live fixture | dead-off fixture |
|---|---|---|
| `celloff_x0` (committed signature) | accepted | **accepted** |
| `celloff_x1000` (committed signature) | accepted | **accepted** |
| `celloff_y1000` (ver8-C reissued signature, 439 B) | accepted | **rejected** |

ver8-C therefore binds **Y** liveness through the raw `t2_relpos` y-column (`_relpos` subtracts only
`ox`), but leaves **X** unbound — the measured form of F1 after the fix. `r101-ver8-offy-C2.patch`
(adds an `offy=` echo on top) is self-consistent (its own pin accepts its own fixture, verified) but
the echo adds no discriminating token that C's raw-y column does not already provide.

## F3 — MEDIUM · measurement-vs-pin conflation at the source (r95-boundary §4)

`reports/round-95/r95-boundary.md:192-196`:

```
**14/14 offsets return the identical 8-tick ladder** — x ∈ {0, ±0.25, 0.5, 1, 2, 4, 8, 16, 32, 64, ±1000} and y = +1000.
celloff off=0 offy=1000.0  ladder=[…]                        (identical)
```

and `:211`: *"B alone at y=+1000 (`celloff_y1000`) is `[e,a,c,d,b]` — i.e. the same phase as an
untranslated pile."* The `y=+1000` cell is a run whose independent variable was **never applied**
(`offy` has zero occurrences in the fixture). Arithmetic: 13/14 cells had the X IV applied, 1/14 (Y)
did not; **0/3 CASES pins** bind the IV (F1). The inference "same phase as an untranslated pile" is
not supported by that receipt — it *is* an untranslated pile. r95-adjudicator item 1 already ruled
"Fix `--offy` or drop the row"; this shard adds that "drop the row" does not restore any Y evidence
and that the X rows need the same treatment.

## F4 — INFO · fleet-wide flag census: `offy` is the **only** zero-occurrence flag among 552 tokens

AST census of all 509 CASES rows (504 with `.gd` fixtures), 54 distinct `--key` tokens, 552 tokens,
word-boundary count of each key against its fixture source:

* exactly **1** zero-occurrence token: `offy` on `r95b_order_celloff_y1000`;
* `grep -c offy corpus/fixtures/r95b_order.gd` = 0; the only corpus occurrence outside `live/` is
  the CASES row at `run_battery.py:1004`.

This reproduces and generalises r95-simplifier's "only unread flag among all 52 rows' flags" to the
whole battery — C3's "formal retirement census (0 reachable reads)" is cheap and its answer is
unambiguous. E17's `--arm=census` emits the executable form independently
(`r95b_offy_tokens=0 r95b_lines=778 r95b_sha256=4f7e945e…`), so the census claim is now confirmed by
two independent methods (this seat's 552-token AST scan; E17's in-fixture token count + digest
tripwire). Bound: occurrence ≠ reachable read (a key could occur only in a comment), so this is
necessary-not-sufficient for the other 551 tokens; for `offy` the count is 0, which is decisive.

## F5 — INFO · load-bimodality exposure: pinned surface stable, unpinned diagnostics not

Six identical launches of the y1000 row at load avg 30–41 (`--arm=celloff --off=0 --offy=1000`):

| field | observation |
|---|---|
| PASS line sha256[:16] | `4eb7afed20b2d44c` × 6/6 |
| wall | 1.84, 1.86, 1.86, 1.88, 1.94, 1.98 s |
| `pf=` (unpinned diag) | 65 × 6 |
| `proc=` (unpinned diag) | 156,156,156,156,156,**157** |

Mode exposure: `--fixed-fps 30` and `--fixed-fps 120` both emit a PASS line **byte-identical** to
the default launch (verified against the default line), so these rows are mode-robust (contrast
r94-critic F3's tps conditioning).

Calibration trap observed live: my first A/B full-transcript `cmp` reported **DIFFER** solely from
`proc=155` vs `156` while the PASS lines were identical. Whole-output equality is not a valid
stability criterion here; only the pinned line is. Any C3 verification that diffs transcripts will
produce false positives under this load.

## F6 — LOW · duplicate-signature census; `cases_integrity` cannot see signature collisions

509 CASES rows → 502 distinct signature values; **6 signature values are shared by 13 rows**:

| rows | shared signature | flag delta |
|---|---|---|
| `negative_overlap`, `negative_signal` | `negative control: …` | different scripts |
| `camera_top_limit`, `camera_left_limit`, `camera_bottom_limit` | `PASS camera_limit …` | `--top/-left/-bottom-bound` (read) |
| `button_activation_disconnected`, `button_activation_unfocused` | `UI BUTTON ASSERTION FAILED …` | `--disconnect-signal`, `--no-focus` (read) |
| `r95b_order_celloff_x0`, `r95b_order_celloff_y1000` | `PASS r95b_order celloff off=0.0000 …` (**409 B, byte-identical**) | `--offy=1000` — **unread** |
| `crash_spontaneous_sigabrt`, `crash_self_sigkill` | `SPONTANEOUS_CRASH_PROBE: expected signature` | different signals |
| `descendant_pipe_detached_control`, `descendant_pipe_forged_signature_release` | `DESCENDANT_PIPE_PROBE: expected signature` | different modes |

The celloff pair is the only one of the six whose differing flag is unread (F4), hence the only one
where the two rows' acceptance sets are identical for the committed fixture. `cases_integrity`
(`run_battery.py:4022-4028`) checks **name** uniqueness only — it cannot see this class; a hard
signature-uniqueness gate would be wrong (it would fail the legitimate camera-limit trio), so this
belongs to review, not to a gate.

---

## What C3 must satisfy to close (acceptance criteria for the round)

1. **If landing the measurement (option A):** the PASS line must contain a token **derived from
   geometry** and not offset-normalised (examples that work: E17's `dy_resid`/`t2_absy`/`n_at_0`, or
   keeping the raw y-column of `t2_relpos` as ver8-C does) — an `offy=` echo alone is forge-accepting
   (F2). Keep the normalised ladder/relpos tokens for the invariance claim, and pin the arm at ≥2 Y
   values (0 and +1000; -1000 adds a third; E17 validated all three). **Status: both in-flight
   artifacts satisfy this for Y** (§F2b, measured: echo-only forgery and dead-off mutant rejected).
   CASES rows are orchestrator-serialized; E17's spec rows and ver8's CASES patches are in the
   round's mutations dir.
2. **Residual that no in-flight patch closes — the X cells.** After ver8-C, `celloff_x0` and
   `celloff_x1000` still accept a fixture where neither pile nor query translates (F1/F2b, measured).
   Either add an X counter-token (the mirror of `dy_resid`: `dx_resid`/`t2_absx`), or state in the
   round record that the X-translation claim is *run-measured, pin-unbound*. Do not write "the X
   cells (real offsets) stand" (r95-simplifier F1's wording) without that qualification.
3. **If retiring the r95 row (option B):** the census must be battery-wide (509 rows / 552 tokens),
   not 52-row; it must say Y invariance was **unmeasured** in r95, and it must not claim the X rows
   stand. E17's `--arm=census` is the executable form (`r95b_offy_tokens=0`, source sha256 tripwire).
4. Any closure claim must quote the **pinned** line, not a whole-transcript diff (F5).

## Files

* created: `reports/round-101/r101-crit3.md` (this shard),
  `reports/round-101/mutations/r101-crit3-offy-attack.py` (r95-row forge matrix; `CRIT3_ROOT`),
  `reports/round-101/mutations/r101-crit3-ytrans-check.py` (in-flight artifact check; `CRIT3B_ROOT`).
* read-only inputs: `corpus/fixtures/{run_battery.py,r95b_order.gd,r101_ytrans.gd,project.godot}`,
  `reports/round-95/*`, `reports/round-101/mutations/r101-ver8-offy-*.patch`.
* no shared file edited; `corpus/fixtures/run_battery.py` never executed; no commit made.
* scratch: `/tmp/r101-crit3/` (224 KB, usrquota-limited) and two repo-local transient dirs
  `reports/round-101/mutations/.scratch-crit3{,b}/` — **removed**, `git status` re-checked.

## Unknowns / not measured

* Whether any of the other 551 flag tokens is read only by a dead branch (occurrence census is not a
  reachability census). Follow-up: per-key call-site census.
* Whether other arms in other rounds pin offset-normalised tokens in the same way (only `celloff`
  was attacked here; `dss_lattice` and the r95 `twopiles` arm were not re-derived).
* Load-bimodality beyond the 6 reps: no run was slow enough to expose the 3D lane's worst case, so
  "stable under load 41" is an observation at that load, not a bound.
