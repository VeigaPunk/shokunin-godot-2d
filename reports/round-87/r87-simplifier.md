# game-dev-2d round 87 — simplifier (r87-simplifier): seven proven deletions in `input_lattice.gd` (−21 lines, pure deletions, zero pinned bytes touched); census-subsumed cells and over-long-signature trims audited and dispositioned

Seat `SIMPLIFIER` (LEAF) | lane `r87` | host **devin**. Runtime **Godot
`4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`, headless), Python
3.14.7. Repo `~/Projects/shokunin/game-dev-2d-shokunin`, work commit
**`ebcf2bb`** (*r87 input event/action lattice*, 25 new cells + 3 landed
fixtures). **No tracked file written, no commit, no git mutation.** Writes are
this report and `corpus/live/r87-simplifier/**` only.

Tree state: HEAD moved mid-session under this seat (`ebcf2bb` → `1ecca1b`
SCORECARD backfill → `adc2eaa` author+scribe record → `535b2c2` r90 scout →
`da41d54` reviewer → `f6a6ad5` critic) — all other seats' commits. The three
landed r87 **probe** files still carry the `ebcf2bb` bytes (`input_lattice.gd`
sha256 `2b68531d…`, `r87_edge.gd` `7cd80727…`, `ei_bound.gd` `0493a257…`).
`corpus/fixtures/run_battery.py` carries an **in-flight, uncommitted edit by
another lane** at report time (`325ab020…` → `a2a7e2e7…`, +17/−1: the critic-F1
`api_press` 2-payload envelope plus the r87 expected-errors census extension).
**This seat's batteries ran on the `ebcf2bb` battery file** —
`fixtures-after/run_battery.py` is byte-identical to `ebcf2bb` (`325ab020…`) —
so the fold proof is apples-to-apples on the work commit. One transient touch
by this seat is disclosed: importing `run_battery` for the alphabet audit
recompiled the **tracked** `corpus/fixtures/__pycache__/run_battery.cpython-314.pyc`;
it was restored with `git checkout --` and re-verified equal to `HEAD`
(sha256 `13319b13…`). No other tracked modification by this seat; the only
tracked-dirty file at report time is the other lane's `run_battery.py`.

**`lsp` disclosure (unchanged host state).** No `lsp` device is exposed in this
dispatch (the only MCP server is `rea`, a Ghidra/binary-analysis server; no
GDScript/Python language server is installed — same host state as
author/scout/reviewer/r79). Deletion-candidate caller proofs therefore rest on
(a) complete textual enumeration of every reader of the suspect state (grep,
**literal fallback, never presented as semantic proof on its own**), and
(b) fresh-process receipt equivalence of the *folded* tree against the
unmodified control and the canonical r87 runs. No cold-start empty result is
recorded as absence.

---

## 1. Method and proof artefacts

Per brief, only **provably** removable weight was folded: apply the diff in a
scratch copy → full battery still runs → every row's verdict tuple identical to
the unmodified tree and to the canonical PASS runs. Batteries ran sequentially,
never in parallel.

| artefact | content |
|---|---|
| `corpus/live/r87-simplifier/r87-simplifier-fold.patch` | unified diff, **21 deletions / 0 additions**, all in `input_lattice.gd`; `git apply --check` clean against the current tree |
| `fixtures-after/` | runnable folded project: full `corpus/fixtures/` copy with the `ebcf2bb` battery file byte-identical (`325ab020…`) and `__pycache__` omitted; one differing source file: `input_lattice.gd` 854 → **833 lines**, sha `2b68531d…` → `7624aa97…` |
| `before/20261015T173035054065Z/` | battery on the **unmodified** tree → 206/207 PASS, 1 FAIL (`api_press`, §6) |
| `after/20261015T173808425241Z/` | battery on `fixtures-after/` → **207/207 PASS** |
| `receipts/compare.txt`, `tuples-{before,after}.txt` | row differ (r79-baseline `compare.py` reused unmodified): stable tuple = `(case, script, flags, expected_exit, actual_exit, signature, verdict, error, expected_errors)` + normalized-output compare |
| `receipts/reps.log`, `mode-reps.log` | direct arm reps: touched arms ×6–8 reps/side, envelope arms interleaved ×12–20/side |
| `receipts/alphabet-audit.txt` | every observed payload of the 25 new cells across **8 on-disk r87 battery runs** checked against the landed (`ebcf2bb`) whitelist |
| `MANIFEST.sha256` | 25/25 files verify |

**Folded tree vs canonical PASS runs** (`compare.py godot`):

| ref | common | tuple_mismatches | output-normalized identical / differing |
|---|---|---|---|
| author run 3 `172055…` | 207 | **0** | **200 / 0** (7 meta not carried) |
| verifier run 2 `173437…` | 207 | **0** | 197 / 3 (envelope mode sampling) |
| reviewer canon `172925…` | 207 | **0** | 196 / 4 (envelope mode sampling) |
| own control (unmodified tree) | 207 | 1 = `api_press` | 196 / 4 |

Parse check both sides: `godot --headless --check-only --script
res://input_lattice.gd` → exit 0, no diagnostics.

## 2. Killed — the fold, seven deletions (SP1–SP7), all **proven-byte-identical**

One patch, `input_lattice.gd` only. None of the 25 pinned signatures, none of
`run_battery.py`, is touched — the fold is invisible to every pinned byte.

| # | site (was) | why dead | proof |
|---|---|---|---|
| SP1 | `_fmt_ticks_d()` `:193–201` (−10) | **zero call sites**: the only other formatter callers are `_fmt_recv`/`_fmt_ticks_rel_ev`; no string/dynamic dispatch exists (`cb.call`, `flags["on_event"].call` invoke stored lambdas only). Repo-wide grep finds the name **only as a definition** (incl. every seat's scratch copy) | folded battery 207/207; all 23 `input_lattice_*` CASES rows byte-identical to control |
| SP2 | `_arm_ui_ns` first `_mark()` (−1) | overwritten by the second `_mark()` after `await _pr_frames(2)`; no `_ev`/recorded `_tick`/`_fmt_*` read occurs in between (rec off, no events) | `ui_ns` 6 reps/side + 12 interleaved reps/side: identical 2-payload alphabet (sha `60dfd4ea…`/`536006f8…`), both modes on both sides |
| SP3 | `_arm_pre_frame` duplicate `flags["ph0"]/["pr0"]` (−2) | exact re-assignment of the values `_mark()` set one statement earlier; no await between | `pre_frame` 20 interleaved reps/side: identical 2-payload alphabet (sha `f4da75c4…`/`a2d0eb87…`), both modes on both sides |
| SP4 | `_arm_imap_erase` `watch=` + `ev_watch=true` (−2) | arm prints `r.desc` only; the `m/ist/echo` maps `ev_watch` builds are never formatted (`_fmt_recv` not called; rec off so `_states` never runs) | `imap_erase` 6 reps/side byte-identical single payload |
| SP5 | `_arm_imap_mid_cb` `watch=` + `ev_watch=true` (−2) | same: prints `via+tag+desc` only | `imap_mid_cb` 6 reps/side byte-identical |
| SP6 | `_arm_reentrant` `watch=` + `ev_watch=true` (−2) | same: prints `seq+via+tag+desc` only | `reentrant` 6 reps/side byte-identical |
| SP7 | `_arm_dispatch_order` `_bind(&"do", …)` + `watch=` (−2) | prints `seq+via+tag` only; the bound action is never queried (`_st`/`_pl`/`_fmt_recv` absent from the arm), and the handled gate is driven by `flags["on_event"]`, not the binding | `dispatch_order` 6 reps/side byte-identical |

**Verdict-row proof:** folded vs own control = **206/207 tuples identical**; the
one difference is `api_press`, which is a pre-existing flake reproduced *on the
unmodified tree* (§6) and whose payload alphabet is unchanged by the fold
(20/20 direct reps byte-identical before/after). Folded vs the three canonical
r87 runs = **0 tuple mismatches, 207/207**; output-normalized diffs vs
verifier/reviewer are exactly the 3–4 envelope rows sampling their other
whitelisted payload.

**Tradeoff (apply-cost, disclosed):** applying the patch invalidates the
recorded probe provenance — the `CASES` comment `probe = input_lattice.gd
sha256 2b68531d…, verbatim` and the `r87-author.md` byte-copy table row become
stale (new sha `7624aa97…`, 833 lines). The fold itself is runtime-zero-weight
(dead statements only), so the honest recommendation is: **apply only as a
bundle with the in-flight r87 corrections** (the critic-F1 `api_press` envelope
and the F3 census extension are already in the working tree, uncommitted, at
report time) and update both provenance lines in the same landing; otherwise
defer. The patch is left unapplied and proven.

## 3. Redundant rows and census-subsumed cells (task item 1)

Pairwise review of the 25 new rows against each other: **no row's observable is
fully implied by another row** — each pins a distinct arm, parse phase, or
window (`press_idle` pr-phase vs `press_phys` physics-resume vs `pre_frame`
pre-sink; `acc_off` inline vs `acc_flush` explicit flush; `imap_erase` buffered
erase vs `imap_mid_cb` mid-dispatch erase; `dispatch_order` handled gate vs
`reentrant` nested parse; `phys_peer` same-step peer visibility). Cell-level
redundancies found, all **needs-run, recommend defer** (cost > weight):

| # | subsumed cell | implied by | disposition |
|---|---|---|---|
| SP8 | `input_lattice_ui_ns` `ua_ev=3` | `input_lattice_census` `ui_accept_ev=[K4194309,K4194310,K32]` — the census enumerates **every** event of `ui_accept` (keys by keycode, others by class), so a 4th event would change the census list; the count cannot vary while census passes | needs-run (substring verdict argument, not executed); omit — removing 3 tokens costs edits in **two** provenance-pinned files (fixture + both envelope payloads) |
| SP9 | `r87_edge_jpbe` `ai=<null>` | census `evact=[device,action,pressed,strength,event_index]` — `action_index` is absent from `InputEventAction.get_property_list()`, hence `get("action_index")` is null | needs-run; omit — same cost argument |
| SP10 | ei≥32 refusal ERROR line whitelisted in **both** `ei_bound_refusal` and `r87_edge_jpbe` | — | **rejected**: whitelists are per-row by design; a shared whitelist would be a second convention. The duplication is the price of per-row stderr gating |

## 4. Dead code in the new fixtures (task item 2) — kept candidates

Beyond the seven killed sites, the remaining candidates did not survive the bar:

| # | candidate | verdict | reason |
|---|---|---|---|
| SP11 | `r87_edge.gd` `_arm_jmode` (−59 arm lines) + header/dispatch refs | **rejected** | evidence custody: scout §1 table row 4, §3's mechanism block (`flag[gap/jp] = { "1/jp0": 12, "0/jp1": 4 }`), §6.3, `runs/jmode.rep{1..3}.*`, and `r87-boundary.md` §7 (lines 320–321) quoting the jmode PASS line verbatim all reproduce through `--arm=jmode`. Deleting the arm strands the reproduction path for the `release_edge` semantic-bimodality claim (the one *semantic* envelope). Also a recorded byte-copy (`7cd80727…`) |
| SP12 | `_arm_jmode`'s `gap_hist` (implied by `flag_hist` keys) | **rejected** | same custody: the quoted boundary line includes `gap={ 1: 12, 0: 4 }`; removing it changes a quoted receipt for −1 line |
| SP13 | `r87_edge.gd` `Sink` record fields `pr/cls/act` (only `.ph` is read, by jmode; jpbe reads only `.size()`) | **rejected** | shared instrument of the retained jmode census; file is a recorded byte-copy of scout's probe; −2 lines not worth touching custody |
| SP14 | inert sinks in `_arm_dz_ladder`/`_arm_joy_axis` (no rec, no watch, no events) + `joy_axis`'s `watch=` | **rejected** | the header's stated convention is "one arm per process, exactly the battery's launch shape"; removing nodes changes the launch shape for zero pinned bytes |
| SP15 | `_arm_api_press` `watch=`/`ev_watch=true` | **rejected** | not dead by construction: the arm *does* call `_fmt_recv()`; the maps are invisible only because the pinned `recv=[]` holds. Deleting them would change the failure shape if a receipt ever appeared |

## 5. Over-long pinned signatures (task item 3) — proposals only, all rejected

No trim is byte-identical, so per brief these are proposals, not folds. Each
was assessed for refutation power:

| # | proposal | verdict | reason |
|---|---|---|---|
| SP16 | trim `input_lattice_census` (4974-char signature) to a discriminating prefix of `imap`/`input`/`ui_builtins` | **rejected** | the exhaustive list **is** the census's discriminating power: a prefix silently admits any tail change (renamed/removed method). There is no `input_lattice_*` mutant set to bound the loss, and `census` is the subsumption base for SP8/SP9 |
| SP17 | trim `ei_bound_refusal` tail `{33,42,100}` (all `pressed=0`) | **rejected** | each out-of-range value is a distinct refusal sample; `42` is cross-referenced by `r87_edge_jpbe`'s `bad_ev`; the row is 14 lines total — weight saved ≈ 0 |
| SP18 | collapse the 4 mode-envelope tuples to one payload / common prefix | **rejected** | the tuple *is* the whitelist semantics ("both observed modes, nothing else admitted"); a prefix admits unobserved modes. Do not touch while `pre_frame`/`api_press` tails are still open (critic F1/F5) |
| SP19 | trim `rec_ph`/`rec_pr` headroom (`press_idle 6/4`, `press_phys 8/3`, `burst 4/3`, `pre_frame 4/3`, `release_edge 4/3`) | **rejected** | headroom absorbs **pre-EV ticks**: `press_idle rec_pr=4` is exactly 1 pre-EV + 3 post-EV; trimming can silently collapse an envelope mode (e.g. a 2-entry `post_ph` becomes the same payload as the other mode). Unprovable from finite reps — this is the "recording budget" contract, not dead weight |
| SP20 | rename `R83 arm=…` header / `# r83-scout scratch probe` to r87 | **rejected** | the r83 marker is provenance explicitly marked historical (author table: "scout's adopted r83 probe, verbatim"); renaming is exactly a second convention. Also `R83 arm=…` is live diagnostic output every run |

**Not re-litigated (other seats own them):** the critic's F1 `api_press`
envelope prescription (**landed in the working tree, uncommitted, during this
session**), F5 `press_phys` tail, the scribe-queued F2 count correction ("20
verbatim + 4 mode-envelope" double-counts `pre_frame`; the landed `CASES`
comment "20 stable arms of 23, plus three bimodal mode-envelope cells" is the
accurate form and is still unmodified at report time), and the reviewer's
latent signature-tuple TypeError note.

## 6. Corroboration: the one non-fold finding — `api_press` escape (already `r87-critic` F1)

This seat's **unmodified-tree control run** (battery launch shape, same host)
FAILed `input_lattice_api_press` with the alt payload
`ph1{ap=1/0.70/1/0}` (jr=0) — the critic's F1 mode. The alphabet audit over all
**8 on-disk r87 battery runs** shows `api_press` is the **only off-pin payload
among the 25 new cells** (2 observed payloads vs 1 landed string); the other 24
cells are exactly inside their whitelists (envelope rows 2/2). Direct reps:
20/20 mode A before *and* after the fold. This is corroboration of an
already-reported defect, not a new proposal from this seat; the critic's
2-payload-envelope correction is the smallest safe fix and is already in the
working tree (uncommitted, other lane) at report time.

## 7. Result

- **Deletions made (scratch-proven, unapplied):** 7 sites / **−21 lines**, all
  pure deletions, `input_lattice.gd` 854 → 833. Patch:
  `corpus/live/r87-simplifier/r87-simplifier-fold.patch`.
- **Proven:** folded tree **207/207 PASS**; **0 tuple mismatches** vs the three
  canonical r87 runs (author3/verifier2/reviewer) and 200/200 normalized outputs
  identical to author3; **206/207** vs the unmodified control with the single
  difference being the pre-existing `api_press` flake reproduced on the control
  tree; touched arms byte-identical in interleaved direct reps.
- **Preserved contract:** every one of the 25 new cells and all 182 prior rows;
  every pinned PASS line; both edge rows and all 4 envelope tuples; the
  `expected_errors` gates; the descendant ordering razor; `run_battery.py`
  untouched by this fold.
- **Tradeoff:** applying the patch invalidates the two recorded probe-sha
  provenance lines (`CASES` comment + author table) for zero runtime gain.
  Recommended only bundled with the in-flight r87 corrections; otherwise defer.
- **Stop line:** the next candidates would harm an axis — `jmode`/`gap_hist`
  (evidence custody for a quoted claim), `rec_ph` headroom (envelope
  completeness), `R83` rename (historical provenance), census/`ei_bound` trims
  (refutation power). Stopped here.

Seat output complete.
