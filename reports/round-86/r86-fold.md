# r86 fold — simplifier vfold + critic corrections + discovered bimodality envelopes

Seat: FOLD (orchestrator) | round 86 | tree `7ae7083` work + this fold
Inputs: author✓ baseline✓ scout✓ verifier✓(ADMIT) critic✓ simplifier✓
boundary✓ scribe✓ — all eight seats landed.

## Applied

### Simplifier vfold (proven, byte-identical ×16/16 battery-faithful pairs)
- `out`/`out_bytes` dead keys removed from `_boot` return + doc comment.
- `drop` sink inlined to `[]` in `OS.execute`.
- `_deferred_g` inlined (stale name — called synchronously).

### Critic corrections (16/18 PASS-forges drove these)
- **F1 dummy_timeout**: `dur_ge=1` emitted (child ran ≥ bound−200 ms) —
  kills f09's 1.1 s `quit(124)` synthesis; `bound_s` now emitted from the
  arg variable, not a literal (F8).
- **F2 gate path-attribution**: `_frames()` extracts child backtrace
  `[N] fn (res://child.gd:L)` user frames; gate_matrix emits `tf=`/`df=`,
  gate_duality emits `pf=`/`af=` — f06/f14/f16 can't produce
  `_dss_state,…,_process` or the `_dss_state`/`_loud_state` split without
  taking the real paths. Per-position `errpos` was emitted in draft but
  folded into the envelope below.
- **F3 cm_n**: child emits `cm0/cm1` fractions (control `0.4688/0.4727`
  = real contact; dummy `-1.0000/-1.0000` = empty) — kills f07's
  aimed-at-empty-space arity forge.
- **F4 xcheck**: pins `offered2d/3d` (child's own lists) not parent
  constants — kills f01's label substitution; `errs_total=4` covers
  out-of-window stderr (f02).
- **F5 stderr symmetry**: `errB=` byte counts on gate/nf children.
- **F6 nofetch stimulus**: `nofetch[thr=true,errs=0]` pins the child's
  own `thr` readback — kills f03's unthreaded baseline.
- **F7 _boot stale captures**: out/err/rc unlinked before spawn;
  `OS.execute` failure → rc=-998 class — kills f13's leftover-receipt
  consumption.
- **F9 enum%d**: count computed from `probes.size()` — kills f12's
  shrunken-probe-list literal.
- **F10 stored_has**: lattice emits `stored_has` presence flag —
  disambiguates unset vs explicit `"DEFAULT"` (f10).

### Newly discovered latent bimodality — enveloped (same class as g3d r90)
While re-running reps under host contention: `gate_duality prop`
realized `B=ok,errs=0` once — the deferred `_run` fetch can land inside
the threaded server's physics-accessible window. 12/12 dedicated reps
refused; under load it raced. Also `dummy_degenerate` control
`moved=17.867`→`21.104` once (frame-count coupling).
- `gate_duality`: `dual_ok` envelope — per-side named modes
  a(refused: null+error+state-frame)/b(fetched: ok+no error); all four
  combos legitimate; `at_eq` gated only when both refused. Emits
  `dual_ok=1` constant token, fail-closed on foreign tuples.
- `gate_matrix`: `thr_ok` envelope — refused-count == error-count,
  frames ⊆ refused-fetch paths, ≥4 refusals required (keeps evidence).
- `moved`: `mv=pos|zero` class — the 12-frame drop distance is
  frame-coupled (17.867/21.104 both realized); the law is
  moves-vs-frozen, not the magnitude.
- `dur_ms`: `dur_ge` threshold token (jittered 3005/3006).

All 8 CASES rows repinned; standalone ×3 stable; **full battery
182/182 PASS** (run `20261015T160405358447Z`).

## Record-level (non-blocking, filed)
- r86 boundary armed-but-unrun classes B8–B14 live in
  `corpus/live/r86-boundary/` (harness ready, ~150 launches) — future
  exec-capable seat.
- Critic's `make_forges.py` splices on the pre-fold `_deferred_g` line;
  the anchor needs re-aiming if reused post-fold (simplifier-flagged).
- Critic non-forge note: battery outer 8 s budget < inner `timeout 15`
  — effective bound is the outer one; fail-safe direction.
- Scribe F1–F6 non-blocking (MANIFEST count drift 752→761 etc.).
- Verifier ADMIT predates this fold; fold changes emit semantics per
  critic corrections — verifier's 182/182 ×2 + my fresh 182/182 on
  folded bytes both on record.
