# r87 critic2 — review of the folded round-87 dossier (admitted bytes `7ef247c`, HEAD `b5cb490`)

**Seat `CRITIC-2` (g2d lane r87, flash route) | host devin | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` headless, Python 3.14.7, 32-core.
Read-only on tracked files; no commit. Writes: this report +
`corpus/live/r87-critic2/**` (untracked scratch).**

**Seat boundary (stated once, for the record).** This session's canonical seat
card is the UFO-FSD **critic** card: *dispatched specialist, never the judge;
do not judge, admit, edit, integrate, ship, or self-promote*. The dispatch
asked this seat for an adjudicator verdict (`r87-adjudicator.md`, ADMIT /
ADMIT-WITH-FOLLOWUPS / REJECT). Rendering that verdict is exactly the
judging/admitting act the seat card withholds, and in this fleet adjudication
is an operator/orchestrator lane (the wave spec routes flash to
critic/simplifier; every `r*-adjudicator.md` in this repo is authored from the
orchestrator seat). **No verdict is rendered here and no adjudicator artifact
is authored.** What follows is the critic review the adjudicator needs —
counterexamples, evidence, impacted axes, smallest safe corrections — plus the
axis-impact read, per-finding dispositions, and chain assessment as *inputs*
to that verdict. If the operator wants this session to adjudicate, re-dispatch
under an adjudicator seat card; the review below is the ~95% of the report
that is seat-legal.

Target: the **admitted bytes** = `corpus/fixtures/` at `7ef247c` (fold commit;
`git diff 7ef247c b5cb490 -- corpus/fixtures` empty; worktree clean vs HEAD).
Probe shas: `run_battery.py 69512316…`, `input_lattice.gd 7624aa97…` (833
lines), `r87_edge.gd 7cd80727…`, `ei_bound.gd 0493a257…`. Pre-fold blobs:
`run_battery.py 325ab020…`, `input_lattice.gd 2b68531d…` (854 lines).

---

## 0. What I ran (fresh evidence, this seat)

| # | run | result | receipt |
|---|---|---|---|
| E1 | full battery on HEAD, fresh process tree: `PYTHONDONTWRITEBYTECODE=1 timeout 900 python3 -B corpus/fixtures/run_battery.py --runs corpus/live/r87-critic2/runs1` | **207/207 PASS**, rc=0; surface discriminations **36/36 true** incl. `r87_expected_errors_all_matched` **true** and `phys2d_expected_errors_all_matched` true; `dead_entry_count=0`, `rows_with_expected_errors=52`; compare vs verifier2 receipt `be5b0222…`: **common=207, tuple byte-identical 207/207, 0 mismatches**; raw-diff rows **10 = 8 declared-volatile** (ASLR/pid/runpath/tween) **+ `pre_frame`/`ui_ns`** landing the complementary envelope mode; normalized 198/207 identical (7 meta not carried, the same 2 envelope rows differ) | `runs1/20261015T175608856719Z/verdicts.json` sha `a0a80fc0…` |
| E2 | focused envelope batch, battery launch shape, 5 tuple rows × 8 reps under 16 CPU hogs (`run_env.py --reps 8 --load 16`) | **40/40 PASS**, each rep matched exactly one whitelisted payload; `api_press` **payload[1] (alt, jr=0) 8/8** under load; no ERROR / SCRIPT ERROR / Parse Error lines | `env-load16-r1.json` |
| E3 | production `classify_process` extracted verbatim from the admitted `run_battery.py`, applied to my E2 alt-mode rep against the landed api_press evidence | per-payload `[False, True]` → `any()` **True**; the **pre-fold single-string pin → False** (the old row would have FAILed this rep) | same JSON, rep `payload_hit=1` |
| E4 | reviewer-F1 mechanism: `("a","b") in "xxa"`; AST of `CASES` tuple rows ∩ whitelist rows | `TypeError: 'in <string>' requires string as left operand` reproduced; tuple rows `{api_press, pre_frame, press_phys, release_edge, ui_ns}` ∩ whitelist rows `{input_lattice_null_edge, ei_bound_refusal, r87_edge_jpbe}` = **∅** → latent, unreachable today | inline |
| E5 | composition census (AST + scout `author-rows.py.txt`) | 25 new rows = 23 `input_lattice_*` (**18 string-pinned + 5 envelope**) + 2 edge; scout file holds 20 rows, `pre_frame` re-cut inside them, `api_press` re-cut at fold | inline |
| E6 | custody `sha256sum -c` | scout **101/101**, boundary **1283/1283**, simplifier **25/25**, critic **7/7**; `r87-author/` and `r87-baseline/` **untracked + no manifest**; verifier 503 / verifier2 330 files tracked in git | inline |
| E7 | ancestry/freeze | `ebcf2bb → 7ef247c → b5cb490` (HEAD); verifier `freeze-head.txt` = `ebcf2bb`; verifier2 froze `7ef247c` (= live HEAD at its run, 1 rep 207/207 + 24 focused reps) | receipts tracked in `34433ce` / `b5cb490` |
| E8 | replay corroborations | `phys_peer d+1 jr=0` (scout's `jr=1` claim falsified); `input_lattice.gd` 833 lines, no remaining `_fmt_ticks_d` references; SP1–SP7 = pure deletions (−21) | E1 receipt |

No tracked file was modified; no battery artifact was written outside my
scratch; all launches were `timeout`-bounded.

---

## 1. Attacks on the admitted bytes

### A1 — the F1 defect is real and the fold fixes it **[counterexample, verified]**
On my own fresh alt-mode rep (rc=0, no ERROR lines), the production classifier
returns `False` against the pre-fold string pin and `True` against the folded
2-payload envelope (E3). Under 16 hogs the alt mode is **dominant** (8/8 here;
critic 27/30; verifier2 22/24) — the pre-fold row would have flaked at ~5%
unloaded / ~90% loaded. The fold's payload[1] is byte-equal to the critic's
prescribed alt line. **Impacted axes:** pin-vs-mode classification of a shipped
cell; the round's stability claim. **Correction:** already folded; none further.

### A2 — independent replay confirms the folded bytes **[no falsification]**
E1: 207/207, all 36 surface discriminations true, both floor gates green, and
**207/207 tuple byte-identical** to verifier2's receipt across an independent
process tree. This is the second full-battery rep on the admitted bytes (the
official chain had one) and it exercised complementary envelope modes
(E1: `pre_frame` payload[0], `ui_ns` payload[1]; verifier2 in-battery:
`pre_frame` payload[1], `ui_ns` payload[0]; `api_press`/`press_phys`/
`release_edge` landed the same payload in both). No regression found in the
fold's three deltas (api_press row, floor gate, SP1–7).

### A3 — envelope semantics cannot cross-match **[no falsification]**
One payload per rep in E1/E2 (40/40) and in the seats' records; the pair is
mutually non-substring by construction (one-character `jr` flip). `any()`
therefore cannot admit an unwhitelisted line or match both. **Impacted axes:**
envelope vacuity. **Correction:** none.

### A4 — reviewer F1 latent TypeError: confirmed, unreachable **[latent hazard]**
Mechanism and reachability proven (E4). The census calls
`classify_process(..., row["signature"], …)` for every row carrying a whitelist;
the first envelope row that ever needs a whitelisted ERROR turns a row-level
FAIL into a battery-wide traceback. Today no tuple row has a whitelist.
**Impacted axes:** harness robustness; the hazard grows with each new
envelope+whitelist combination. **Correction:** normalize the census the way
`execute()` does, or `assert isinstance(row["signature"], str)` with an
explicit message.

### A5 — shipped classification is stale **[false provenance, minor]**
`run_battery.py:320–321` says "20 stable arms of 23, plus three bimodal
mode-envelope cells and two deterministic edge cells". On the admitted bytes
the truth is **18 string-pinned + 5 mode-envelope** (`pre_frame` and
`api_press` are envelope rows) **+ 2 edge = 25**. The numbers still sum to 25
only because the "20 stable" bucket silently contains two envelope rows. The
row-level comments for `pre_frame`/`api_press` are honest; the block header is
not. Same off-by-one as the author report's "20 verbatim + 4 envelope + 2
edge" (the scout's 20 rows include `pre_frame`) and the `ebcf2bb` subject.
**Impacted axes:** provenance/identity of the shipped block. **Correction:**
update the comment line (no byte change to any row).

### A6 — "proven byte-identical outputs" is loose **[wording]**
`run_battery.py:324`: SP1–SP7 moved the `input_lattice.gd` line numbers printed
in the `input_lattice_null_edge` backtraces — the declared-unpinned `.gd:N`
token class (`_arm_null_edge` 760–763 → 743–746, `_pr_frames` 229 → 219);
verifier2 reports the same. The qualifier "pinned strings unchanged" is
correct; "byte-identical outputs" overstates by that masked token class.
**Correction:** say "pinned/whitelisted bytes unchanged; sole raw delta the
declared-unpinned traceback line-number class".

### A7 — custody asymmetry **[evidence-loss risk]**
The seats whose bytes are the committed diff and its baseline (`r87-author/`,
`r87-baseline/`) are untracked and carry no manifest; the critic dir has a
7/7 manifest; simplifier (25/25), verifier (503), verifier2 (330) are
git-tracked. The admitted bytes' *verification* receipts are therefore
hash-anchored; the *author lane's own* receipts are not. **Correction:**
manifest or commit the author/baseline/critic scratch.

### Attacks that failed (verified clean)
- The fold's floor gate covers exactly the three r87 whitelist rows (prefix
  coverage checked in code and live: all entries matched, `dead=0`).
- No prior CASES row carries tuple evidence (5 tuple rows, all r87); the
  mutant path (`mutate=True` ×2) uses `str` evidence only, so `evidence[0]` is
  dead-but-correct today.
- Prior-row stability: 207/207 tuple-identical between two independent
  full reps; the only post-fold deltas vs pre-fold are the two declared
  (api_press signature shape; surface discriminations +1 key).
- The pulse law's predictions hold on every pinned state cell I could check
  (E8; `phys_peer` jr=0, `api_press` alt branch reproduced).

### Tradeoffs (not defects — for the judge to weigh, not fix)
1. **Envelope mode-flip admission**: a regression that permanently flips
   `api_press`/`release_edge`/`ui_ns`/`press_phys`/`pre_frame` to the other
   whitelisted mode passes silently. Inherent to mode cells; the lost
   discrimination is exactly the environmental variable (interposed steps).
2. **Engine/host-encoded pins**: `eng=0/1`, `joys=0` (`input_lattice.gd:316`)
   plus engine-derived method/keycode lists; no engine-version assert anywhere
   in the harness. Fails loudly but unattributed on another host/build; 20/20
   stable on this host.
3. **Permission-only whitelists**: `expected_errors` tolerates lines and never
   requires them; the `ei≥32` refusal count (4) is unasserted.
4. **Unobserved third modes**: `pre_frame` ≥2-tick window (~150 cumulative
   reps, never seen), `press_phys` ≤1-entry tail — fail loudly by design.
5. **Off-host surfaces**: no gamepad, non-headless, or non-Godot-4.7.2 rep;
   `event_index 1..31` semantics and `jmode` histogram unprobed/unpinnable.

---

## 2. Finding dispositions (recommendations to the adjudicator)

Status is judged **on the admitted bytes** (7ef247c), not on the pre-fold
build. "Fixed" = corrected in the fold and verified live by a non-author seat
and/or this replay.

| source | id | summary | status on admitted bytes | recommended disposition |
|---|---|---|---|---|
| critic | F1 | api_press bimodal; landed pin fails alt mode | **fixed** (2-payload envelope; E1–E3 + verifier2 22/24) | accepted-fixed |
| critic | F2 | risk register omitted api_press | **fixed** (inline row comment carries the law + F1) | accepted-fixed |
| critic | F3 | floor gate missing r87 whitelists | **fixed** (`r87_expected_errors_all_matched` green in verifier2 + E1) | accepted-fixed |
| critic | F4 | "20 verbatim" off-by-one | **partially fixed** — corrected in seat reports/fold commit; block comment still says "20 stable arms of 23" (A5) | record correction at next touch |
| critic | F5 | `press_phys` ≤1-entry tail unlisted | open as disclosed mode-tail risk; envelope covers observed modes | noted-accepted |
| critic | F6 | pulse law survives; `dz_ladder` process-phase note; `pre_frame` honesty | law re-verified (E8); note stands for boundary §1 | noted-accepted |
| reviewer | F1 | census tuple-signature TypeError (latent) | **still latent** (E4); unreachable today | deferred-to-rNN (guard; cheap) |
| reviewer | F2 | `eng=`/`joys=` engine/host pins; no version assert | open; 20/20 stable here | deferred-to-rNN |
| reviewer | F3 | floor gate + unasserted count | gate **fixed**; count unasserted | partially fixed; count deferred |
| reviewer | F4.1 | author count 26 vs 25 | record corrected (reports/commit); author report stands point-in-time | noted-accepted |
| reviewer | F4.2 | CASES comment counts `pre_frame` as stable | **residual** (A5) | record correction |
| reviewer | F4.3 | author header HEAD stale | point-in-time artifact; superseded by `ebcf2bb` | noted-accepted |
| scribe | F1 | author/baseline unmanifested (author report was untracked) | author report tracked (`adc2eaa`); scratch dirs still untracked/manifest-less (A7) | deferred-to-rNN (custody fold) |
| scribe | F2 | count off-by-one | same as critic F4 | record correction |
| scribe | F3 | floor gate | fixed | accepted-fixed |
| scribe | F4 | `ei_bound_refusal` "4 lines" vs 1 entry | wording; census shows 1 entry × 4 matched lines | noted-accepted |
| scribe | F5 | baseline citation mislabeled | claim true, citation wrong; point-in-time | noted-accepted |
| scribe | F6 | author compare outputs not custodied | open (A7) | deferred-to-rNN |
| scribe | F7 | author header staleness | point-in-time | noted-accepted |
| scribe | F8 | SCORECARD drift | resolved (`1ecca1b`) | closed |
| scribe | F9 | read-only F2 ("runs/ absent") falsified | resolved: runs/ exists, **101/101** (E6) | closed |
| scribe | F10 | round coverage at window close | resolved (all seats landed) | closed |
| simplifier | SP1–SP7 | −21 dead lines, byte-identical | **fixed**; byte-proof now tripled (simplifier control, verifier2, E1) | accepted-fixed (note A6 token) |
| simplifier | SP8–SP20 | no folds; dispositions recorded | sound (no action) | noted-accepted |
| boundary | laws/selector/falsifications | pulse law; selector `inter==0 ⟺ jp==1` (300/300); `pre_frame` falsified; `phys_peer` falsified; exactness matrix; ei boundary | landed as knowledge; api_press latent fixed via fold | noted-accepted |
| boundary | `sel_pf_anchor` re-cut | deterministic `pre_frame` alternative | unadopted fold option | noted (rNN if ≥2-tick mode ever appears) |
| boundary-readonly | F1/F2/F3 | phys_peer falsified / runs-absence / selector drift | F1 confirmed live (E8); F2 falsified (E6); F3 superseded by selector law | closed |
| verifier | 4/4 AGREE on `ebcf2bb` | pre-fold chain | chain input | accepted |
| verifier2 | VERIFIED on `7ef247c` | post-fold chain | chain input | accepted |
| critic2 | C1 | block-comment classification stale | open (A5) | record correction |
| critic2 | C2 | "byte-identical outputs" loose | open (A6) | record correction |
| critic2 | C3 | custody asymmetry | open (A7) | deferred-to-rNN |
| critic2 | C4 | official post-fold full-rep depth = 1 | open; E1 adds an unofficial second rep | record honestly in LOG/adjudication |
| critic2 | C5 | envelope mode-flip admission | inherent tradeoff, disclosed | noted-accepted (judge weighs) |
| critic2 | C7 | `.pyc` files committed in `b5cb490` (2 binaries) + stale tracked `corpus/fixtures/__pycache__/run_battery.cpython-314.pyc` | hygiene only | noted (residual debt) |

No **unfixed claim-refuting defect** remains on the admitted bytes from this
seat's attacks. The residuals above are wording/custody/latent-harness items
plus the five disclosed tradeoffs; none of them changes a verdict on the
current data.

---

## 3. Verification chain — non-author requirement on the admitted bytes

**Satisfied at the seat level.** Chain: author work `ebcf2bb` (author seat did
not commit; orchestrator integrated) → **non-author `r87-verifier`** on frozen
`ebcf2bb` (`freeze-head.txt`; 2 full reps 207/207, AGREE 4/4, receipts
git-tracked in `34433ce`) → critic/reviewer/simplifier wave → orchestrator fold
`7ef247c` → **non-author `r87-verifier2`** on frozen `7ef247c` (== live HEAD;
1 full rep 207/207, floor gate green, 24 focused api_press reps under load
22 alt / 2 pin, all PASS; receipts git-tracked in `b5cb490`). The last mutation
of the admitted fixture bytes is `7ef247c`, and it is verified by a seat that
did not author it (nor author the fold — the fold's changes came from the
critic/simplifier prescriptions and were applied by the orchestrator).

Caveats to record:
1. All commits share one git identity (`game-dev-2d-shokunin`), so non-author
   attribution rests on the seat reports' self-declaration + the wave routing,
   not on git authorship. That is this fleet's convention; no report in this
   round violates it.
2. Route-level model independence is not recorded in the reports; only seat
   independence is. (Author route swe-2; verifier routes not in the reports.)
3. Post-fold **full-rep depth is 1** (pre-fold 2), supplemented by focused
   load reps. My E1 replay (this seat) is a second full rep on the admitted
   bytes and is 207/207 tuple-identical to verifier2 — corroboration, not a
   substitute for the named verifier. If the adjudicator wants 2×post-fold,
   schedule a second official rep or record E1 as corroboration.
4. The in-row post-fold battery rep landed `api_press` pin-mode; alt-mode
   admission is proven out-of-band (24 + 8 focused reps, plus the E3
   production-classifier call). That is adequate for a mode cell but should be
   stated, not implied.

**Conclusion: yes — the admitted bytes have a named non-author verification
after their last mutation.** Record the caveats above in the round entry.

---

## 4. Axis-impact read (input for the SCORECARD call)

Per the repo convention (axes `depth`, `coverage`, `calibration`; verdict words
as in r79–r86). This is this seat's read of the evidence; the call is the
adjudicator's.

| axis | read | why |
|---|---|---|
| **coverage** | **improved** | +25 cells → 207 rows: dispatch family/order (`in/sc/uk/uh` matrix), buffering (`acc` true/false/flush), action-state semantics (`just_*`, strength/raw, deadzone, echo, keycode/physical independence, erase/mid-cb, `ui_ns` fan-out, conflict, device banks, mouse, null edge), `by_event` family, `event_index` refusal boundary; 182 prior rows zero-drift. Unprobed surfaces named (ei 1..31 semantics, jmode histogram, gamepad/non-headless, mouse viewport cursor). |
| **depth** | **improved** | The round's laws are measured, not asserted: `just_*` = exactly one physics step, first step after the change; both flags can fire on the same step; release pulse armed even on a never-pressed action; flake selector = interposed steps (`inter==0 ⟺ jp==1`, 300/300); exactness flips a polled answer iff the only matching binding matched loosely; `InputEventAction` matches by name only; `ei≤0` applies / `1..31` silent / `≥32` refusal. Three scout claims falsified and corrected (`phys_peer jr=1`, `pre_frame` determinism, `api_press` determinism). |
| **calibration** | **improved** | The round's headline stability claim was falsified pre-admission by its own critic and corrected in-fold (F1), the r80 gate class was closed again (F3), and SP1–7 landed with byte-proof + post-fold re-verification. Residuals are named rather than hidden (A5–A7, tradeoffs). The cost is recorded honestly: the api_press envelope trades that cell's `jr` discrimination for stability. |

---

## 5. Smallest safe corrections (ordered; none blocking on my evidence)

1. **Record corrections (no runtime change):** update the `run_battery.py`
   block comment to the post-fold composition (18 string + 5 envelope + 2
   edge = 25) and qualify "byte-identical outputs" per A6.
2. **Harness guard (deferred):** census tuple-signature normalization or an
   explicit `assert isinstance(..., str)` — closes reviewer F1 before the
   first envelope+whitelist cell.
3. **Engine pin (deferred):** assert/record the Godot version in the harness
   and/or delta-ize `eng`/`joys` — closes reviewer F2.
4. **Custody (deferred):** manifest or commit `r87-author/` + `r87-baseline/`
   (+ critic) scratch — closes scribe F1/F6, A7.
5. **Whitelist tightening (optional):** assert the `ei≥32` refusal count.
6. **`pre_frame` (optional):** keep the envelope; adopt boundary's
   deterministic re-cut only if the ≥2-tick mode is ever observed.

---

## 6. Draft LOG entry (for the adjudicator to complete)

```md
## round 87 — input event/action lattice (<adjudicator verdict>)

- 25 cells: 23 `input_lattice.gd` arms (18 string-pinned + 5 mode
  envelopes) + `r87_edge.gd` jpbe + `ei_bound.gd` refusal boundary.
  Surfaces: dispatch family/order, buffering, action-state semantics,
  exact_match event+polled matrices, device banks, event_index bounds.
  +25 battery rows -> 207. Author 207/207 x2 (rep1 FAILx2 pre-envelope);
  verifier 207/207 x2 on ebcf2bb; verifier2 207/207 on folded 7ef247c.
- FOLDS (7ef247c): critic F1 api_press -> 2-payload envelope (alt
  27/30 under load; pulse law inter==0 <=> jp==1); F3 floor gate
  extended to r87 whitelists (`r87_expected_errors_all_matched`);
  simplifier SP1-SP7 -21 dead lines (854->833, sha 2b68531d->7624aa97,
  pinned bytes unchanged; sole raw delta a declared-unpinned `.gd:N`
  token). Critic2 replay: 207/207, 207/207 tuple-identical to verifier2.
- RECORD: boundary pulse law (just_* = exactly one physics step, first
  after the change; release pulse armed even on never-pressed);
  flake selector = interposed steps (300/300); pre_frame falsified
  deterministic (48% off-pin); scout phys_peer jr=1 falsified (48/48
  jr=0 + replay); scout runs/ custody 101/101. Residuals: envelope
  mode-flip admission (by design), engine-encoded eng=/joys= pins
  unasserted, ei refusal count unasserted, >=2-tick pre_frame mode
  unobserved (~150 reps), author/baseline receipts unmanifested,
  latent census tuple-signature TypeError (unreachable today).
- Seats: author+baseline; scout+boundary+scribe; critic+simplifier;
  verifier x2; critic2 replay. Commits: ebcf2bb (work) + 7ef247c (fold).
```

---

## 7. Bounded claims

Everything here is this host, this build (`4.7.2.stable.arch_linux.ed1daf0bf`),
headless, 60 tps, `timeout`-bounded fresh processes; E1/E2 are single-session
reps. E1's tuple comparison uses the verifier2 compare tooling verbatim; raw
identity is modulo the declared-volatile mask. "No unfixed defect" is scoped
to the attacks in §1, not a general correctness claim. The seat boundary in
the header is a statement about *this* seat, not about the round.

## Evidence index (`corpus/live/r87-critic2/`, untracked)

| artefact | content |
|---|---|
| `runs1/20261015T175608856719Z/verdicts.json` | E1 full battery, 207 rows, sha `a0a80fc0…` |
| `run_env.py` | focused envelope runner (battery launch shape, 8 s/rep) |
| `env-load16-r1.json` | E2/E3 40 reps under 16 hogs, payload hits, verdicts |
| `proj/`, `xdg-data/` | scratch project copy + user:// isolation |

Reproduce: `PYTHONDONTWRITEBYTECODE=1 timeout 900 python3 -B
corpus/fixtures/run_battery.py --runs corpus/live/r87-critic2/runs2` and
`python3 -B corpus/live/r87-critic2/run_env.py --reps 8 --load 16 --tag r2`.
