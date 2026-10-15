# r86 critic — PASS-forge hunt on the 8 `phys2d_backends_*` rows

Seat `CRITIC` | round 86 | Godot `4.7.2.stable.arch_linux.ed1daf0bf` headless | commit `7ae7083` (unmodified)

Method: 18 fixture-mutation forges under `corpus/live/r86-critic/forges/` (one
scratch project each, isolated `user://` namespaces via unique `config/name`),
each run as the battery runs it — `godot --headless --path <proj> --script
res://phys2d_backends.gd -- --arm=<arm>` — then classified with the battery's
own `classify_process` predicate against the pinned `CASES` signature. Base
receipts (`receipts/base_*.out`) byte-match all 8 pins; the four hottest arms
(gate_matrix, gate_duality, xcheck, dummy_timeout) were re-run fresh this
session with `--keep` for capture harvest.
Child captures harvested with `--keep` (left under
`~/.local/share/godot/app_userdata/R86Critic*/r86bt/`).

**Scoreboard: 16/18 forges produce a byte-identical pinned signature (FORGED
PASS); 2 are caught (f11, f17).** Every pinned claim was also verified against
real kept captures — the pins are honest digests of real engine behavior; the
defects below are about what the digest cannot see, not about false evidence.

## Findings

### 1. HIGH — `dummy_timeout`: `rc=124` cannot distinguish a timeout-kill from `quit(124)`; the whole hazard row is synthesizable

Counterexample `f09_timeout_clean124`: child boots with **no Dummy engine**,
performs **no ray query**, **never hangs** — it prints `R86C hang_begin=1`,
`printerr`s the collider-error text, and calls `quit(124)`:

```
godot --headless --path forges/f09_timeout_clean124/proj \
    --script res://phys2d_backends.gd -- --arm=dummy_timeout
→ PASS phys2d_backends dummy_timeout dummy_timeout rc=124 bound_s=3
  hang_begin=1 collider_sig=1 errs=1            (byte-identical to pin)
```

`timeout` propagates a self-exit `124` exactly like a SIGTERM kill, `errs`
counts any line containing `"ERROR:"` (the forged `SCRIPT ERROR:` printerr
qualifies), and `collider_sig` is a substring test. The real arm took **3.42s**
(external kill at the 3s bound); the forge took **1.1s** — wall time alone
would have exposed it. The row's core claim ("only an external bound ends the
process") is unverifiable from the pinned fields.

Smallest correction: parent measures `_boot` wall duration and emits
`dur_ms=%d` pinned `>=2900`-shaped (or `dur_ge_bound=true`); optionally pin the
child's `at: _m_dummyhang (res://child.gd:…)` line so the error must originate
from the fixture's own frame, not any printerr.

### 2. HIGH — `gate_duality`/`gate_matrix`: the digest drops the backtrace frames that attribute an error to a code path

The parent strips stderr to `at:` payload lines + an `ERROR:` count. The kept
base captures show the discriminating evidence exists but is discarded:

```
prop err.txt:  [0] _dss_state  (res://child.gd:17)  → _run
api  err.txt:  [0] _loud_state (res://child.gd:22)  → _run
```

Both reach `space_get_direct_state (...:281)` — the pinned comparison — but the
`*_state` frame is what proves which path was exercised. Proven consequences:

- `f06_duality_collapse` — `"api"` mode rewired to `_dss_state()` (both
  children now take the SAME path) → signature byte-identical. The "duality"
  is unverifiable at the emit layer.
- `f14_duality_synthetic` — both children emit `B=null`, one `printerr("ERROR:
  …")`, and a literal `printerr("   at: space_get_direct_state
  (modules/godot_physics_2d/godot_physics_server_2d.cpp:281)")` with **no
  space-state fetch on either path** → byte-identical signature. `at=` is a
  text parse, not provenance.
- `f16_gate_null_forge` — C fabricated (`"null"` when threaded, real fetch
  otherwise) plus one extra real refused fetch (`_gate["_x"]`) to keep the
  total at 5 → `thr[A=null,B=null,C=null,…,errs=5]` byte-identical with one
  pinned position **fabricated**. `errs` is an aggregate count with no
  per-position binding; `f04_gate_err_redistribute` (extra fetch + hardcoded F)
  confirms the same balance-forge from a different mutation.

Smallest correction: child prints the top user frame of each error (or parent
extracts `[0] <fn>` per block) and the pin carries per-path frame names /
per-position error flags (e.g. `errpos=ABCFG`), not a bare count. ~10 lines in
`_child_src` + digest.

### 3. MEDIUM — `dummy_degenerate`: `cm_n=2` measures return-arity, not contact

`cast_motion` returns the `[safe, unsafe]` fraction array even on a complete
miss. `f07_dummy_castmotion_miss` aims the cast away from the wall
(`motion=(0,200)` instead of `(200,0)`) → `cm_n=2` still → forged PASS. The
Dummy/control contrast in the pin only proves `[]` vs a 2-element array — the
control side cannot see "hit" vs "missed the wall entirely". If live
`cast_motion` regressed to always-miss, this pin stays green.

Smallest correction: pin the values, not the size — emit e.g.
`cm0=%.3f,cm1=%.3f` (first fraction < 1 proves a pre-target contact) or the
raw array.

### 4. MEDIUM — `xcheck`: `names2d`/`names3d` pin segments are parent-side echoes; out-of-window stderr is unscanned

- `f01_xcheck_substitute_jolt`: child offers `unregistered_zed` where the
  pinned label still says `Jolt Physics`; the refusal vector is identical
  (`[0,0,1,1,1]`) → forged PASS. `names2d=[…]` comes from the parent's
  `NAMES2D` constant; the child's offer list is an independent literal — the
  pin can silently mislabel what was offered.
- `f02_xcheck_ambient_err`: `printerr("ERROR: r86_forge_ambient_outside_window")`
  lands at `err.txt:1`, before the first `R86CM` window →
  `_window_counts` drops it, no `errB` pin exists on this arm → forged PASS.
  A real engine error outside the windows would be equally invisible.

Smallest correction: child emits `R86C offered2d=[…]`/`offered3d=[…]` and the
parent pins *those*; add `errs_total=%d` (`_err_count` over the whole stderr)
to catch out-of-window frames.

### 5. MEDIUM — `gate_matrix`: stderr coverage counts `ERROR:` lines only

`f05_gate_warning_slip`: `printerr("WARNING: r86_forge_drift")` inside the gate
child → identical signature; `_err_count` matches only `"ERROR:"` and this arm
pins no byte count. Sibling arms are inconsistent: `lattice`/`dummy_degenerate`
pin `errB=0` (full stderr bytes — strong), `xcheck`/`gate_*` count ERROR lines
or window frames only (weaker). Smallest correction: pin `errB` or a
non-marker stderr digest on the gate/xcheck children too.

### 6. MEDIUM — `gate_matrix`: the `nofetch` baseline's stimulus is unpinned

`f03_gate_nofetch_def`: drop `THREAD_ON` from the `nf` child's project.godot.
The child itself reports `R86C thr=false` (harvested from kept captures), but
the parent never reads that field — only `errs`. → `nofetch[errs=0]` PASSes
while the "threaded, fetch-free baseline" ran **unthreaded**. The negative
control's stimulus is self-reported and unread.

Smallest correction: the child already emits `thr=` — emit
`nofetch[thr=%s,errs=%d]` in the pin (one-line change).

### 7. MEDIUM — `_boot` consumes stale captures: no freshness check, `OS.execute` return ignored

`f13_stale_capture`, two-stage: (1) unpatched twin project with the same
`config/name` runs `lattice --keep` → six real capture sets persist under
`user://r86bt/lattice/`; (2) same namespace, fixture with dead shell path —
`OS.execute("/bin/sh_r86gone", …)` fails silently, `_boot` then reads the
**leftover** `out.txt`/`err.txt`/`rc.txt` as fresh:

```
→ PASS phys2d_backends lattice … moved=17.867 … errB=0}   (byte-identical,
   in 0.6s vs ~5s for six real boots — children never ran)
```

`_boot` rewrites `project.godot`/`child.gd` but never unlinks the capture
files, and `cdir` reuse is stable across runs (`OS.get_user_data_dir()` keyed
on the *parent's* project name — the battery's scratch name is fixed per run,
and a parent killed by the 8s budget mid-arm skips `_cleanup`, leaving
residue for the next run). Needs exec-failure + residue to fire, but the parse
layer cannot tell "fresh capture" from "leftover".

Smallest correction: unlink `out/err/rc` before spawn (or write a run nonce
into `project.godot` and require it echoed back in a `R86C nonce=` field);
check `OS.execute`'s return code.

### 8. LOW — `bound_s=3` is a literal echo, not a readback

`f08_timeout_bound_literal`: real bound changed 3→8, child hung the full 8s
(8.6s wall), signature still prints `bound_s=3`. The field documents intent,
not the bound actually exercised. Correction: emit from the `_boot` argument
variable (or drop the field).

### 9. LOW — label-integrity echoes: `enum5`

`f12_census_enum5_drop`: probe list shrunk to 4 names, `enum5=0` unchanged —
the `5` lives in the format literal, not in `probes.size()`. Same class as the
xcheck name labels. Correction: `enum%d=%d` with the real count.

### 10. LOW — `lattice` `default` cell can't distinguish absent key from explicit `"DEFAULT"`

`f10_lattice_default_explicit`: writing `2d/physics_engine="DEFAULT"` yields
`stored=[DEFAULT]` identical to the unset cell. The pin's "no override" claim
is ambiguous at the stored-value layer. Correction: also emit
`ProjectSettings.has_setting`-style presence, or make the default cell's
marker distinguishable.

### 11. INFO — coverage tolerance (by design, noted)

`f18_lattice_junk_emit`: non-`R86C` stdout lines and unknown `R86C` keys
(`R86C injected=forged_field`) are ignored → identical signature; duplicate
keys are last-write-wins in `fields`. Probably intentional noise tolerance —
recorded so the trust boundary is explicit.

`f19_dummy_keys_echo` (hardcoded `keys="[]"` under Dummy) and the general
"print the pinned string" attack are the emit-trust tautology every battery
row shares; the verifier already flagged it. Not counted as defects.

## Caught forges — discrimination that works

| forge | mutation | result |
|---|---|---|
| `f11_lattice_moved_sens` | drop test 12→11 frames | `moved=14.898` ≠ `17.867` → FAIL. `moved` is genuinely measured. |
| `f17_xcheck_cursor_shift` | stray `R86CM end2d` marker | `errs2d=[0,0,0,1,1]` ≠ `[0,0,1,1,1]` → FAIL. Window misattribution is loud, not silent. |

Verified-true pins (from kept base captures): `thr/err.txt` holds exactly 5
ERROR blocks with backtraces `_initialize`/`_run`/`_m_gate`/`_process`/
`_deferred_g` ↔ the 5 null positions; `xcheck` refusals are real
`Condition "id == -1" is true.` at `set_default_server` :959/:1193;
`dummy/hang` `rc.txt` = 124 after a real 3.42s hang. Excuse/fallback classes
**are** gated on real readbacks today — the findings are digest-coverage and
echo-field defects, not false claims.

## Non-forge robustness note (no mutation needed)

Battery outer budget is **8s** (`execute()`), while r86 children internally
bound at `timeout 15` and `lattice` serializes six boots (~5s observed). A
hung non-dummy child fails the row as TIMEOUT — fail-safe direction — but a
loaded machine can push `lattice` toward the ceiling (inner 15s bound can never
fire inside it). Consider lowering inner bounds below the outer budget or
documenting the effective bound as min(8s, N×15s).

## Impacted axes

- **Evidence provenance** — `at:`/`errs`/`collider_sig` are stderr/stdout text
  parses; emit-layer synthesis (f09, f14) reproduces them with no engine event.
- **Discrimination depth** — `cm_n` arity-vs-contact (f07), aggregate `errs`
  vs per-position (f04/f16), unpinned stimuli (f03), unread stimulus fields.
- **Freshness** — `_boot` accepts stale captures (f13).
- **Label fidelity** — echoed constants presented beside measured values:
  `names2d/3d`, `enum5`, `bound_s` (f01, f08, f12); `stored=[DEFAULT]`
  unset-vs-explicit ambiguity (f10).
- **Coverage symmetry** — stderr: byte-pinned (lattice) vs ERROR-only
  (gate/xcheck) vs none outside windows (f02, f05); stdout: `R86C`-only parse.

## Verdict framing for the judge

All 8 pinned claims are **true of this build** — the forges prove digest
coverage bounds, not falsehoods. Findings 1–3 are the strongest
counterexamples (hazard class synthesizable; path-attribution evidence
discarded; a field that cannot distinguish hit from miss). Findings 1,2,6,7
have <15-line corrections wholly inside `phys2d_backends.gd` (emit `dur_ms`,
backtrace frame/`errpos`, read `thr`, unlink+check in `_boot`); findings 3–5
are one-line pin/emit additions. None require contract or battery changes.
Whether these are blocking tradeoffs vs accepted emit-pin bounds is the
canonical judge's call.

Artifacts: `corpus/live/r86-critic/forges/` (generator + 18 patched projects +
runner), `corpus/live/r86-critic/receipts/` (base + forged outputs),
`corpus/live/r86-critic/forge_verdicts.txt` (scoreboard). Nothing committed.
