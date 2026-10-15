# r87 reviewer — input event/action lattice (`ebcf2bb`)

Seat `REVIEWER` (g2d lane r87) | host **devin** | Godot `4.7.2.stable.arch_linux.ed1daf0bf`
(`/usr/bin/godot`), Python 3.14.7. HEAD `ebcf2bb`; reviewed diff = `git show ebcf2bb`
(4 files, +1140/−3). Scratch only: `corpus/live/r87-reviewer/` (untracked). No tracked
writes, no commits.

**LSP device: not available on this host.** No `lsp` tool is exposed to this seat; no
server binary answers the files (`which pylsp pyright basedpyright gdscript-lsp
lua-language-server` → none; `pygls`/`jedi` absent); the only MCP server configured
(`rea`) is a Ghidra/binary-RE server, not a language server. Caller/definition checks
were therefore done by **AST extraction + executing the canonical harness** (stronger
than text grep for this artifact: the CASES/whitelist literals were parsed out of the
tracked file, not re-typed). No grep output is presented as semantic proof.

Verdict: **ADMIT-recommend** — no blocking finding. 4 non-blocking findings.

## Verified (each independently reproduced, not taken from the author report)

| axis | check | result |
|---|---|---|
| insertion-only | AST of `CASES` in `ebcf2bb^` vs `ebcf2bb` | 171 prefix + 4 suffix rows byte-identical; exactly 25 rows inserted as one contiguous block ahead of `crash_spontaneous_sigabrt`; whole-file diff deletes 3 lines (the two `classify_mutant` lines + the `passed =` line) |
| tuple branch reach | tuple/list evidence rows in CASES | **4 only** (`pre_frame`, `press_phys`, `release_edge`, `ui_ns`) → the widening cannot touch any prior row; 200 CASES rows total (175→200 ✓) |
| mutant / negative controls | `mutate=True` call sites | only `run_battery.py:2769-2771` (two explicit mutant rows, both `str` evidence). The tuple branch's `detected if mutate` arm is unreachable for tuple rows; `classify_mutant`'s `evidence[0]` fallback (`:640`) is dead-but-correct today |
| tuple vacuity | payload pair geometry + live reps | per row, the two payloads are mutually non-substring and each spans to end-of-line (`common_prefix/suffix` measured); in 8 live reps each rep matched **exactly one** payload (`pre_frame` 5A/3B, `press_phys` 4A/4B, `release_edge` 8A/0B, `ui_ns` 8A/0B) — never both, never neither |
| whitelists | entries vs classifier modes | all 6 new entries are **exact-match** (none comma-suffixed, so no prefix mode, `:437-438`); `input_lattice_null_edge`'s four lines are byte-identical to the scout fragment in `author-rows.py.txt`; `ei_bound_refusal`/`r87_edge_jpbe` entries are the scout's documented addendum (scout fragment contains only `null_edge` — author correction #2 is accurate) |
| fixtures | sha256 vs scout probe + MANIFEST | `input_lattice.gd 2b68531d…`, `r87_edge.gd 7cd80727…`, `ei_bound.gd 0493a257…` — byte-identical to `corpus/live/r87-scout/proj/*` and to `MANIFEST.sha256` |
| report claims | receipts re-derived by me | `CASES 175→200`; runs1 = 207 rows with exactly `{pre_frame, r87_edge_jpbe}` FAIL; runs2/runs3 = 207/207 PASS; `compare.py godot runs2 vs baseline` = `common=182 new_only=25 old_only=0 tuple_mismatches=1 (meta)` / `output identical=173 differing=2` (export `(36 steps)` vs `(33 steps)`) — reproduced; `runs3 vs runs2` = `tuple_mismatches=0`, 1 output diff = `pre_frame` other payload — reproduced; the only un-normalized baseline diff I found (`crash_spontaneous_sigabrt`) is pure ASLR backtrace |
| independent full battery | `python3 -B corpus/fixtures/run_battery.py --runs corpus/live/r87-reviewer/runs-canon` (concurrent with a CPU-loaded focused run) | **207/207 PASS**, all 25 new rows PASS |
| focused re-run | 25 new rows × 8 reps, canonical launch shape, classifier + whitelists extracted from the tracked harness by AST | **200/200 PASS**, 0 flakes |
| host-state tokens | regex scan of all 25 new evidence strings (`/home`, `/tmp`, `pid=`, `<Node#`, `id=\d+`, `0x…`, epoch, session/uuid/token) | zero hits |

## Findings

### F1 — non-blocking (latent harness crash on a tuple row that also carries a whitelist)

`record["signature"] = evidence` (`run_battery.py:788`) is now polymorphic (`str` or
tuple → JSON array). The error-clause-surface census feeds that field straight into the
classifier:

- `run_battery.py:2160` — `if not entries or not isinstance(row.get("output"), list): continue`
- `run_battery.py:2171-2173` / `2174-2176` — `classify_process(..., row["signature"], ())` and `(..., tuple(entries))`
- `run_battery.py:447` — `signature in output`

`("a","b") in "text"` raises `TypeError: 'in <string>' requires string as left operand`.
Today this is unreachable **only** because every tuple row has an empty whitelist (verified:
whitelist keys = `{input_lattice_null_edge, ei_bound_refusal, r87_edge_jpbe}`, none of them
tuple rows). The first envelope cell that needs a whitelisted ERROR (a plausible next step:
the `press_phys`/`ui_ns` shapes on a host that emits a diagnostic, or a new envelope edge
cell) turns a row-level FAIL into a battery-wide traceback. Recommendation: normalize in
the census the same way `execute()` does (iterate payloads / take the matching one), or
`assert isinstance(row["signature"], str)` with an explicit message.

### F2 — non-blocking (host/engine-encoded pin; the one pin that can move for reasons unrelated to the lattice)

`input_lattice_census` pins two quantities that are not properties of the input lattice:

- `input_lattice.gd:323` → `eng=%d/%d` = `Engine.get_process_frames()/Engine.get_physics_frames()`,
  an **absolute** counter since engine start (pin: `eng=0/1`).
- `input_lattice.gd:331` → `joys=%d` = `Input.get_connected_joypads().size()` (pin: `joys=0`).

The probe's own header declares the opposite discipline — "Absolute counters are wall-clock
dependent headless, so every printed tick index is a DELTA" (`input_lattice.gd:8-11`) — so the
census pin contradicts the fixture's stated invariant. The same row also pins engine-version
derived data (Input/InputMap method lists, the `ui_*` builtin set, `ui_accept` keycodes)
while the harness never asserts an engine version anywhere (`--godot` default `godot`,
`:390`; no version check in the file), so a different Godot on `PATH` fails the row loudly
but with no attribution. Measured stability of the two host-state tokens: 9 scout reps
(`arms-verify*.json`, `inherited/arms-verify.json`) + 3 author battery reps + 8 reviewer reps
under CPU contention = **20/20 `eng=0/1, joys=0`**, no observed drift. Risk is real, low, and
cheap to retire: assert/pin the engine version in the harness (the receipts already record
`4.7.2.stable.arch_linux.ed1daf0bf`) and/or drop `eng`/`joys` from the pin (or make them
deltas/booleans).

### F3 — non-blocking (whitelist is permission-only; the live-entry gate was not extended)

The new `expected_errors` entries are exact-line permissions with no requirement that they
occur, and the harness's only "dead entry" gate is scoped to the prior block:
`phys2d_expected_errors_all_matched` (`run_battery.py:2357-2361`) filters
`r["case"].startswith("phys2d_")`. The r87 entries are censused as *data*
(`dead_in_run`, `census_covers_all_allowlisted_rows` at `:2338`), and my independent canon run
shows them all live (`matched_lines` 1,1,1,1 / 4 / 1; `dead_entry_count=0`) — so nothing is
dead today. But if a future engine stops emitting the `event_index≥32` refusal, both
`ei_bound_refusal` and `r87_edge_jpbe` keep passing on their PASS lines alone and the
"refusal pinned" reading becomes vacuous. The count is also unasserted: one entry matched the
`ei_bound` ladder **4×** (correct, as documented) — a run emitting 1 or 8 refusals classifies
identically. Recommendation: add the three new row names (or a shared prefix) to the dead-entry
gate, and optionally assert the ei-ladder refusal count.

### F4 — non-blocking (three text/claim discrepancies; artifacts unaffected)

1. `reports/round-87/r87-author.md` §"run_battery.py changes" item 1: "**20 verbatim rows** …
   plus **4 mode-envelope rows** … plus **2 edge rows**" = 26, but the commit adds 25
   (CASES 175→200 ✓). AST-verified composition: **19** rows byte-identical to
   `author-rows.py.txt`, `input_lattice_pre_frame` is that file's own row **re-cut in place**
   into a 2-payload tuple, then 3 new envelope rows (`press_phys`/`release_edge`/`ui_ns`) and
   2 edge rows.
2. The tracked harness comment (`run_battery.py:319-320`) and the commit message say
   "**20 verbatim arms** + 4 mode-envelope cells": this counts `pre_frame` among the *stable*
   arms while it is one of the four bimodal envelopes — the author's own correction #1
   (`pre_frame` is n-modal) contradicts the comment sitting above the row.
3. `reports/round-87/r87-author.md` header: "HEAD `fad0b1e` … nothing committed" — the round's
   work commit `ebcf2bb` contains exactly these four files (the report itself landed earlier in
   `adc2eaa`). Name the work commit in the record.

## Residual risk (accepted, disclosed by the author, unchanged by me)

- Envelope semantics = "any enumerated payload". A regression that flips a cell to its *other*
  whitelisted mode is admitted. Inherent to a mode cell; the author states it.
- Unobserved third modes (heavier/lighter `ph:pr` interleave; `pre_frame` ≥2-tick window) fail
  **loudly**. My loaded run shows the minority branches are common, not exotic —
  `pre_frame` mode B (`post_ph=[]`) 3/8 and `press_phys` mode B 4/8 under contention — so the
  envelopes are load-bearing: without them these rows would flake at ~40-50% under load.
- The harness's documented origin-blindness / forgery-acceptance for ERROR lines (r66-r69) applies
  unchanged to the 6 newly admissible error texts.
- `jmode` left un-authored (unpinnable histogram) and `event_index` 1..31 left unprobed beyond
  the boundary map — both disclosed, both correct calls.

## Verification gaps

- No rep on a host with an attached gamepad, a non-headless display server, or a different Godot
  build: `joys`/`ml`/`pos` and the engine-derived lists are unmeasured off this host (F2's risk).
- Soak depth: 3 full-battery reps total (author ×2 PASS + my ×1 PASS) + 8 focused reps per new row,
  not a long repeat soak.
- `pre_frame`'s disclosed ≥2-tick residual mode was not observed in 20 direct + 11 battery reps
  here or by the author (33 reps) — absence of evidence, not evidence of absence.
