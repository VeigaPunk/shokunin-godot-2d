# Round 69 critic report — fabrication-window REFERENT (gap-relative vs absolute) + sha256(merged) receipt upgrade

Seat: critic | Lane: g2d | Host: devin (Godot 4.7.2.stable, Linux headless)
Audited: the declared axis-move AS SPECIFIED (tracked author diff not yet
landed at audit time — `git status` clean for both tracked files;
`corpus/fixtures/descendant_pipe_probe.gd` still has hardcoded
`OS.delay_msec(200)` at :180 and `gap_ms=200` banner at :136; no
`--midline-gap-ms`/`gapladder`/`sha256(merged)` tokens in
`corpus/fixtures/run_battery.py`). All numbers below are from my own
independent re-implementation of the declared flag in scratch
(`corpus/live/r69-critic/proj/descendant_pipe_probe.gd` — verbatim copy +
`--midline-gap-ms=N` parse mirroring the `--midline-offset-ms` pattern,
wired to BOTH the banner and `OS.delay_msec`) run through a surface_run-
semantics bounded Popen (`corpus/live/r69-critic/gap_sweep.py`, records in
`gap-sweep-results.json`, 27 cells x 1 record each: exit/elapsed/
signature/spliced_line/write_ppid/godot_pid + channel & merged digests).

## (1) Can offset=80 × gap-sweep distinguish gap-relative from absolute? — NO, as declared. 4/5 cells are non-distinguishing; the 5th is confounded with flag wiring.

The two models' verdict matrix (write arrives at ≈ offset+2.5ms relative
to head flush, r68-measured ~1.7–3ms exec+sleep latency; fabrication =
byte-order splice, requires head < write < tail):

| cell (off,gap) | relative (edge=tail flush) | absolute ~198ms edge | distinguishing? |
|---|---|---|---|
| (80,50)  | miss | "fab" — physically impossible if flag wired; only reachable via `--midline-gap-ms` not reaching `delay_msec` | confounded: tests WIRING, not referent |
| (80,100) | fab | fab | no |
| (80,200) | fab | fab | no |
| (80,400) | fab | fab | no |
| (80,800) | fab | fab | no |

Under byte-order semantics a write landing between the two flushes MUST
splice — so an "absolute" referent can only be expressed as edge
E≈198ms < tail. At offset=80 (< E) every gap ≥ ~83ms fabricates under BOTH
models; the only declared cell that differs is gap=50, and there "fab"
cannot mean absolute-bound — it can only mean the flag failed to reach
`OS.delay_msec`. **The declared falsifier "persists at gaps <<80ms"
mislabels a wiring defect as a model verdict.** The other horn, "fails at
gaps >>80ms", is unproducible by the absolute model at offset=80 — a miss
there would refute byte-order itself, not select between referents. The
region where the models actually disagree — offsets in (E, gap), i.e.
offset > ~198 with gap > offset — is entirely unsampled.

Measured proof of the missing region (my scratch, 3 reps each,
`gap-sweep-results.json`):

| cell | outcome ×3 | signature | what it rules out |
|---|---|---|---|
| (80,50)   | miss 3/3 | intact | edge < ~82ms (wiring + referent jointly) |
| (80,100..800) | fab 3/3 each | destroyed | absolute edge E < ~82ms |
| **(300,400)** | **fab 3/3** | destroyed | absolute edge E < ~302ms |
| **(300,800)** | **fab 3/3** | destroyed | absolute edge E < ~302ms |
| **(600,800)** | **fab 3/3** | destroyed | absolute edge E < ~602ms |
| (300,200) control | miss 3/3 | intact | write lands post-tail AND post-death |

So measured, the bound IS gap-relative — the edge tracks the tail flush
to at least ~602ms — but the DECLARED design alone could not have shown
it: every one of its cells returns the verdict both models predict. The
verdict "gap-relative" as declared rests on cells that cannot express the
alternative.

**Smallest safe correction:** add one offset row inside (198, gap) —
e.g. `(300,400)` and `(300,800)` (2 cells x 3 reps, ~8s) — predictions:
relative=fab, absolute=miss. That makes the cross real instead of a
single row.

**Wiring witness (required for honest verdict):** `elapsed_seconds` is
already in every surface_run record and scales with the wired delay —
mine: 0.80s@50 / 0.93s@200 / 1.08s@400 / 1.55s@800 (≈ gap + 0.74s). A
`fab` at gap=50 with elapsed ≈ 0.93s is an unwired flag, not an absolute
bound. If the landed discrimination set doesn't consume elapsed (or the
`gap_ms=` banner value — which must print the flag value, :136) per cell,
the absolute/relative verdict is unearned either direction.

## (2) Transition band at each gap size — sampled, but the band that matters is in OFFSET space, unvisited.

Gap-space transition (write-arrival ≈ 82.5ms ± ~1ms jitter) is bracketed
by {50,100}: my reps were unanimous each side (miss 3/3 vs fab 3/3),
~17.5ms clearance at gap=100 — fine for a coarse YES/NO on the small
side. But the referent question needs the EDGE LOCATION at ≥2 gap sizes;
the fixed-offset design never re-samples the offset transition at any
gap ≠ 200. Rep count per cell is the author's choice (r68 used 3);
edge-adjacent cells need more — r68's own critic measured the hi edge
stochastic ~1ms wide (mixed 12/15 vs 3/15 at offset 198.2). None of the
declared cells sit inside a band, so 3 reps suffice for them — but they
also answer almost nothing (see §1). One extra provenance caveat for the
landed discrimination set: when write-time > child-exit the descendant
reparents — my (300,200) reps show `write_ppid != godot_pid`
(pre_death=False) on a CORRECT miss. Any blanket `all_writes_pre_death`
discrimination copied from the r68 ladder will false-FAIL on cells whose
write lands post-exit (gap=50 offset≥~child-exit, or large-offset
misses). My (80,50) stayed pre_death=True on this host (engine keeps the
child alive past ~82ms), but that's host timing, not a contract.

## (3) sha256(merged) — does it gate anything the per-channel pair can't? YES, narrowly: concat ORDER + separator identity. It is derivable (zero new entropy) and vacuous on single-channel records.

Demonstrated on real captured two-channel bytes (`--emit-errforge` arm —
stdout 56311884…, stderr 94c38e64…): sha256(so+se)=de6374a2…,
sha256(se+so)=b3ccf0e2…, sha256(so+"\n"+se)=57cef0d5… — three distinct
digests over THE SAME channel contents. The per-channel pair carries no
order/separator information, so a merge-path drift is invisible to it;
the merged digest is the record's only attestation that the classified
blob was literally so+se. That gate is real: an inserted "\n" separator
would also DEFUSE the r66 seam fabrication (splits the fabricated
reject line) — a verdict-changing merge change that channel digests
cannot see. Honest limits to record: (a) merged is a pure function of the
already-pinned channels — the digest adds no entropy, it attests the
merge function; since `merged` itself isn't stored, that's exactly its
value; (b) vacuous when a channel is empty — ALL my 27 midline records
have stderr_bytes=0, so swapped==merged trivially there (the gate lives
on dual_classify rows like the stderr-carried streamdiv arms); (c) the
r66 caveat it answers is about the seam — the digest pins concat
semantics, it does NOT pin which channel a byte came from (already in the
channel fields). Byte-stable-modulo-additive-field is consistent: new key
on new records only.

## (4) Honest verdict if the bound is absolute — the design can't return "absolute"; it can only return "relative", "wiring bug", or "mechanism refuted".

As §1 shows: fab@50 = flag failure (check elapsed_seconds); miss@≥100 =
mechanism refuted (byte-order broken — bigger than the declared
question); the absolute model produces NO distinct signature at offset
80. If the landed report records "absolute" from this ladder alone, it's
a wiring artifact; if it records "gap-relative", the honest citation is
that the sweep found no counterexample AND (if the author adds §1's
crossed cells) that the edge was observed tracking the tail. My own
measurement already supports gap-relative with E > ~602ms excluded
— but through cells the declared design omits.

## Impacted axes / smallest safe correction

- **measurement-referent (the round's axis):** underpowered as declared —
  add ≥1 offset row in (198,gap), e.g. (300,400)+(300,800); consume
  `elapsed_seconds`+banner `gap_ms=` as wiring witnesses per cell.
- **receipt-integrity:** sha256(merged) is a legitimate additive pin
  (order/separator attestation); record its derivable/vacuous-on-empty
  limits honestly.
- **discrimination soundness:** post-exit writes reparent — don't copy
  `ladder_all_writes_pre_death` over cells whose write time can exceed
  child exit.

## Evidence index (all under corpus/live/r69-critic/)

- `gap_sweep.py` — surface_run-semantics runner (bounded Popen, merged
  classify, ppid provenance, digests).
- `gap-sweep-results.json` — 27 records: declared row (80 ×
  {50,100,200,400,800} × 3) + missing crossed cells ({300,600} ×
  {200,400,800}).
- `proj/descendant_pipe_probe.gd` — fixture copy + `--midline-gap-ms`
  (scratch only; tracked file untouched).
- digest demo: emit-errforge merged/swapped/separator sha256 triple
  (numbers in §3).
- `git status` at audit: both tracked files unmodified (no r69 author
  diff landed yet); flagless behavior of my scratch copy is byte-stable
  only because the flag defaults to 200 — same opt-in contract as
  `--midline-offset-ms`.
