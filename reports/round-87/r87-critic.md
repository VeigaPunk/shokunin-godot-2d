# game-dev-2d round 87 — critic (r87-critic): the api_press pin is not a pin

Seat `CRITIC` (LEAF) | lane `r87-critic` | round 87 | host **devin**.
Repo `~/Projects/shokunin/game-dev-2d-shokunin`, work commit **`ebcf2bb`**
(*r87 input event/action lattice*). Runtime Godot `4.7.2.stable.arch_linux.ed1daf0bf`
(`/usr/bin/godot`, headless), Python 3.14.7, 32 CPUs.

**No git mutation, no tracked file written, no subagent, no commit.** Writes are
this report and `corpus/live/r87-critic/**` only. `git status --porcelain`
shows **no tracked modification** from this seat (the only dirty tracked file in
the tree is another lane's `corpus/fixtures/run_battery.py`, whose content is
byte-identical to `ebcf2bb` — verified `git diff ebcf2bb -- …/run_battery.py`
empty).

**Method.** 609 fresh `godot --headless --path <scratch proj> --script …`
processes in the battery's exact launch shape, each under an 8 s per-rep bound
(no strays at exit; the one host-wide `godot` visible during the run belongs to
the `r87-simplifier` lane, not this seat). Scratch project is a byte-copy of
`corpus/fixtures/` minus `run_battery.py` (`corpus/live/r87-critic/proj/`,
untracked). Payload verdicts use the **production `classify_process` extracted
verbatim from the committed file** (`ebcf2bb:corpus/fixtures/run_battery.py`
lines 431–448), plus a byte-comparison of the 25 landed evidence objects against
the 20 rows in `corpus/live/r87-scout/author-rows.py.txt` and against every
PASS line in the record (scout `arms-*.json` + `runs/`, boundary `census-*.json`
+ `runs*/`, author `runs{1,2,3}/` + `battery-rep*.stdout`).

**Legend:** **[F]** falsified on this host (fresh-process counterexample);
**[O]** observed, no counterexample; **[N]** no defect found on attack.

---

## Findings

### F1 **[F, HIGH]** `input_lattice_api_press` is bimodal; the landed row FAILS on its alt mode

**Counterexample** (fresh process, scratch copy of the landed fixtures, battery
launch shape, `rc=0`, no `ERROR:` lines, no `SCRIPT ERROR:`/`Parse Error:`):

```
PASS input_lattice api_press imm[1/0.70/1/0] raw=0.70 pl=["ap"] recv=[] pr=["pr0{ap=1/0.70/1/0}", "pr1{ap=1/0.70/0/0}", "pr2{ap=0/0.00/0/1}"] ph=["ph1{ap=1/0.70/1/0}", "ph2{ap=0/0.00/0/0}", "ph3{ap=0/0.00/0/1}"]
```

The landed pin differs in exactly four characters: `ph1{ap=1/0.70/1/1}` (jr=1)
vs the measured alt `ph1{ap=1/0.70/1/0}` (jr=0). 211 bytes both.

**Rates on this host state** (`probe-smoke/base30/load16.json`):

| condition | reps | alt mode | pin mode |
|---|---|---|---|
| unloaded, first sample | 3 | **1** (`rep1`) | 2 |
| unloaded | 30 | **1** (`rep23`) | 29 |
| 16 CPU hogs on 32 cores | 30 | **27** | 3 |

**It fails the battery, not just a byte-diff.** Feeding the recorded alt-mode
rep to the production classifier against the landed evidence returns `False`
(`code==0`, `error is None`, no unrelated `ERROR:` line, no `SCRIPT ERROR:` /
`Parse Error:`); the same call with the alt payload as signature returns `True`.
The only failing axis is the signature — so the row verdict is **FAIL** whenever
the alt mode lands. The round's stability claim for this row is a 2-sample
claim ("207/207 ×2"), while the arm flips at ~5% unloaded and ~90% under load.

**Mechanism = the boundary seat's own selector.** The arm issues
`Input.action_release(&"ap")` in one process frame and `Input.action_press(&"ap")`
one idle frame later (`corpus/fixtures/input_lattice.gd:438–441`). The pin
requires **zero** physics steps to interpose in that gap so the release pulse is
still pending at `ph1`; a step consumes it and `ph1` reads jr=0. That is exactly
`r87-boundary.md` §7.3 (lines 324–333: *"Its predicted `api_press` alt mode
`ph1{ap=1/0.70/1/0}` … requires one physics step to interpose in `api_press`'s
1-idle-frame release→press gap"*) and §3's selector (`inter == 0 ⟺ jp == 1`,
300/300). My probe independently **confirms** the boundary law's prediction on
this arm — the law is right; the pin is the thing that is wrong.

**Impacted axes:** pin-vs-mode classification of a shipped cell; the round's
`207/207 ×2` stability claim; the "verbatim arms are stable" provenance of the
20-row block.

**Smallest safe correction:** make `input_lattice_api_press` a 2-payload
envelope — replace the string evidence with the tuple
`(pin, 'PASS … ph=["ph1{ap=1/0.70/1/0}", …')`. The `any()` envelope mechanism is
already landed and already admits *observed* modes; no probe edit, no new file,
and the `input_lattice.gd` sha `2b68531d…` cited in the CASES comment stays
valid. (Alternative: re-cut the release→press gap physics-anchored per
`r87-boundary.md` §5.3 — deterministic, but it changes the probe sha and
invalidates that citation.)

### F2 **[O, MEDIUM]** the risk register dropped the one arm the boundary seat explicitly flagged

`r87-boundary.md` §5.5 and §7.3 name `api_press` by hand: *"`phys_peer` is clean
(48/48) and safe as written; `api_press` is clean (24/24) but latently bimodal"*
and *"Treat `api_press` as clean-but-latent, not as proven deterministic."*
`r87-author.md`'s envelope list covers only `press_phys`, `release_edge`,
`ui_ns`, `pre_frame`; `api_press` is absent from the risk accounting, and the
shipped CASES row is a plain string with no comment — the mode risk lives only
in unshipped prose. F1 is the consequence.

**Impacted axes:** completeness of the round's residual-risk register; durability
of the caveat in the artifact that ships (CASES), not the report.

**Smallest safe correction:** fold F1's envelope (which both fixes and documents
it), or, if the pin is kept for any reason, a one-line comment on the row:
`# latently bimodal: interposed step in the release→press gap ⇒ ph1{…/1/0}`.

### F3 **[O, MEDIUM-LOW]** the `expected_errors` floor gate (r79-C2) does not cover the 3 new whitelists

`run_battery.py` carries the gate
`phys2d_expected_errors_all_matched: all(not e["dead_in_run"] for r in census_rows if r["case"].startswith("phys2d_") …)`
with the comment *"r79 critic C2: expected_errors was ceiling-not-floor — a dead
allowlist entry (never matched a real emitted line) passed silently."* The three
new rows (`input_lattice_null_edge`, `r87_edge_jpbe`, `ei_bound_refusal`) are
**outside** that filter, so a dead r87 entry would pass silently. The census
machinery already computes `dead_in_run` for every allowlisted row and already
covers the new ones, so extending the scope is free: in
`corpus/live/r87-author/runs2/20261015T171747859030Z/verdicts.json`
(`probe_error_clause_surface.census`) all 6 new entries are present with
`dead_in_run: false`, `dead_entry_count: 0`; my own 12 fresh reps per row
reproduce the same matched line counts (null_edge 4/4, jpbe 1/1, ei_bound 4
lines from 1 entry).

Related precision note: `allowed_errors` only *tolerates* lines — it never
requires one. `ei_bound_refusal` therefore tolerates the `ei≥32` refusal without
asserting its presence, and does not pin the refusal *count* (4 in every
receipt); the stdout ladder pins the semantics, so this is acceptable, but
"the refusal is pinned" would be an overclaim.

**Impacted axes:** expected_errors minimality/justification; silent-masking
surface for the new rows.

**Smallest safe correction:** extend the gate's filter to the three new case
names (one line, cannot fail on the current record).

### F4 **[O, LOW]** "20 verbatim rows" is off by one — `pre_frame` was re-cut inside the 20

Byte-comparison of the 20 rows in `corpus/live/r87-scout/author-rows.py.txt`
against the landed CASES rows: **19** are byte-verbatim in all five tuple fields;
`input_lattice_pre_frame` is the 20th and its evidence is a 2-tuple whose element
0 is byte-equal to `pins.json["pre_frame"]["signature"]`. The block is therefore
19 verbatim + 4 envelope (`pre_frame`, `press_phys`, `release_edge`, `ui_ns`) +
2 edge = 25 rows. The author report's "20 verbatim rows … plus 4 mode-envelope
rows" double-counts `pre_frame`, and the commit subject (`20 verbatim arms + 4
mode-envelope cells`) repeats it.

**Impacted axes:** provenance/identity claim of the shipped block; nothing
byte-level.

**Smallest safe correction:** correct the wording (19 verbatim + 1 re-cut); no
code change.

### F5 **[O, LOW]** `press_phys`'s envelope is a *saturated* mode, and its low tail is unlisted

`_fmt_ticks_rel_ev()` caps `post_ph`/`post_pr` at 3 entries
(`corpus/fixtures/input_lattice.gd:183–186`), so payload[0]
(`post_ph=[ph+0 ph+1 ph+2]`) means **"≥3 steps landed in the 10-process-frame
window"**, not "3 steps" — and the scout's own interleave histogram for that
window shape is `{4:14, 5:2}`. Payload[1] means "exactly 2". A window holding 1
or 0 steps emits `post_ph=[ph+0{…}]` / `post_ph=[]`, which the envelope does not
admit. **Not falsified:** 50 reps (30 unloaded + 20 under load) stayed inside the
envelope. The asymmetry is that `pre_frame`'s mirror tail (≥2 entries) is
explicitly disclosed in the author report while `press_phys`'s ≤1 tail is not,
and neither is recorded on the shipped row.

**Impacted axes:** the envelope-completeness claim ("both observed modes
enumerated, nothing else admitted") — true as written, incomplete as a
description of the mode family.

**Smallest safe correction:** one comment line on the row (or mask/anchor the
count per `r87-boundary.md` §5.2). No byte change.

### F6 **[N, PASS with one note]** the pulse law survives the pinned rows; `pre_frame`'s envelope is honest

- **Pulse law vs pins.** Programmatic scan of every physics-indexed state cell in
  all 25 landed payloads: every `just_*` pulse is live for **exactly one** step,
  at the first step after the change (`press_idle ph+0`, `acc_off ph+0`,
  `pre_frame ph+0`, `press_phys ph+0`, `phys_peer d+1`, `burst ph+0` both flags,
  `release_edge ph+0`, `r87_edge_jpbe post[1/1.00/1/0]`, `api_press ph+1`).
  `api_press`'s ladder (`ph1 1/1`, `ph2 0/0`, `ph3 jr=1`) is fully explained by
  the law, and my F1 probe independently reproduces the law's prediction for the
  alt branch (`jr=0` exactly when a step interposes). **No pinned row contradicts
  the physics-step half of the mechanism.**
- **One unclosed case, process phase:** `dz_ladder`'s first sample reads
  `s0.00[1/0.00/1/0]` — `just_pressed=1` **two process frames after** the buffered
  parse — while every later sample at the same offset reads 0. The law's
  process-phase wording ("immediate, decays next process frame") does not cover
  this; it is stable 21/21 (scout 9 + my 12) and 10/10 under load, so it is a
  mechanism-precision note on `r87-boundary.md` §1, not a row defect.
- **`pre_frame` residual-risk honesty: verified.** The author warns that a
  ≥2-tick window (`post_ph=[ph+0{…} ph+1{…}]`) is physically possible but
  unobserved in 33 reps. My 70 additional fresh-process reps (30 unloaded, 30
  under 16 hogs, 20 in the load-envelope batch — which produced **both**
  whitelisted payloads, including the ALT `post_ph=[]`) add no third mode:
  ~103 cumulative reps across the three seats, 2 payloads, both whitelisted. The
  disclosure is honest and now better supported. The boundary seat's *proven*
  deterministic re-cut (`sel_pf_anchor`, `r87-boundary.md` §4, ×3 byte-identical,
  three structural entries) remains unadopted — a fold option, not a defect.

---

## Attacks that failed (verified clean)

- **Envelope `execute()` semantic is correctly any-of, not all.**
  `passed = … any(classifier(code, error, output, expected_exit, sig, expected_errors) for sig in evidence)`
  is equivalent to `(A in output or B in output) AND` all the non-signature
  conditions, because those conditions are identical across the calls; exit code,
  unrelated-ERROR scan, `SCRIPT ERROR:`/`Parse Error:` rejection are unchanged.
  `classify_mutant` keys off `evidence[0]` and the mutant path only fires for
  seeded mutant rows. **No pre-existing CASES row carries tuple/list evidence**
  (checked all 200 rows: only the 4 new envelope rows are non-`str`), so the new
  branch cannot silently re-interpret a prior row.
- **Both whitelisted payloads are genuinely observed, and nothing else is.**
  Across every record file (scout `arms-*.json` reps + `runs/`, boundary
  `runs*/`, author `runs{1,2,3}/verdicts.json` + `battery-rep*.stdout`), distinct
  PASS payloads per envelope arm are: `pre_frame` 24/21, `press_phys` 24/19,
  `release_edge` 13/30, `ui_ns` 16/27 — exactly the whitelisted pair in every
  case, **zero** unwhitelisted payloads, and no payload is a substring of its
  sibling (so `any()` cannot cross-match).
- **Envelope coverage under load:** `press_phys`, `release_edge`, `ui_ns`,
  `pre_frame` — 20/20 inside the envelope each with 16 CPU hogs (60 of the 80
  reps used both modes for `press_phys`/`release_edge`/`ui_ns`/`pre_frame`).
- **The other 19 verbatim rows and the 2 edge rows are rep-stable here:**
  18 rows × 12 reps clean; 10 of them also 10/10 under 16 hogs; `press_idle`
  30/30; `phys_peer` 30/30 (corroborates the boundary seat's 48/48 and the
  falsification of the scout's `phys_peer jr=1` claim); `r87_edge_jpbe` and
  `ei_bound_refusal` 12/12 with byte-identical payloads.
- **The 3 `expected_errors` whitelists are sufficient and alive in-run**
  (12 fresh reps each: no unwhitelisted `ERROR:` line; null_edge's 4 entries each
  match exactly 1 line; jpbe's 1 entry matches 1; ei_bound's 1 entry matches 4).
- **`api_press`'s alt payload is not in the historical record** — 36+ recorded
  reps (scout 9, boundary 24, author battery 3 + direct reps) are all pin-mode.
  That absence is a sampling artifact, not evidence of determinism (F1).

---

## Evidence index (`corpus/live/r87-critic/`, all untracked)

| artefact | content |
|---|---|
| `run_critic.py` | bounded runner (8 s/rep), production launch shape, byte-compares each rep's PASS line against the landed evidence |
| `probe-smoke.json` | 3 × `api_press` — **alt at rep1** |
| `probe-base30.json` | 30 each × `api_press`, `press_idle`, `phys_peer`, `pre_frame`, `press_phys` — **alt at api_press rep23** |
| `probe-load16.json` | 30 each × `api_press`, `pre_frame` under 16 CPU hogs — **27/30 api_press alt** |
| `probe-verbatim12.json` | 12 each × the other 18 verbatim/edge rows — all clean |
| `probe-load16env.json` | 20 each × the 4 envelope rows under load — all inside envelope |
| `probe-load16vb.json` | 10 each × 10 verbatim rows under load — all clean |
| `proj/` | scratch copy of `corpus/fixtures/` minus `run_battery.py` |

Reproduce (≈1 min): `cd corpus/live/r87-critic && python3 run_critic.py --arms
api_press --reps 30 --tag x` and `… --arms api_press --reps 30 --load 16 --tag y`.

---

## Fold recommendation (smallest safe set)

1. **`input_lattice_api_press` → 2-payload envelope** (F1). Blocking: the row
   flakes at ~5% unloaded / ~90% loaded on this host state, and the alt mode is
   already in hand.
2. **Extend the `expected_errors` floor gate to the 3 new rows** (F3) — one line,
   cannot fail today.
3. **Correct the "20 verbatim" wording** (F4) and **comment the mode tails** on
   `press_phys`/`pre_frame` (F5) — documentation only.
4. Optional: adopt `r87-boundary.md` §4's deterministic `pre_frame` re-cut
   instead of the 2-payload envelope (F6).

I do not judge, admit, edit, integrate, or ship. This is the seat output.
