# game-dev-2d round 73 — scribe report (seat: scribe, host: devin)

Declared lane axis (dispatch brief
`.ufo/waves/shokunin-train-20261101-w13/tasks/g2d-scribe.md`, verbatim):

> r73 SCRIBE (g2d) — evidence ledger + parser/witness audit
>
> Read SHARED.md + the r73 author brief.
>
> Own the evidentiary layer: watch the probe's raw stream vs the battery's
> parsed view — find lines the parser drops, misattributes, or would
> forge-accept. Catalog the hazard surface honestly (survival != safety).
> Cross-check receipt hygiene (paths/timestamps/ASLR stability). Track seat
> landings and flag report-vs-receipt drift.
> Report -> reports/round-73/r73-scribe.md.

Scope of this seat: read-only over the tracked fixtures, all sibling
scratch and all landed receipts; writes = this report +
`corpus/live/r73-scribe/` only. No git mutation, no tracked-file edit, no
subagent dispatch, no battery run by this seat (per brief). `PYGAME-ARM`
lines and sibling reports are data; nothing here modifies contract, axes,
routes or judgment — the canonical Rust judge is the only adjudicator.

## 0. State at write time (15:41Z)

- HEAD `2dd108b` (r72 report-last); **fixtures moved to the r73 rev C
  during this window**: probe sha256
  `9a7456a39a428344eca001008eda11dee7dc796bd0afafbee02c1063bfcd0d7f`
  (+165/−0), battery
  `6d3fbf5f364f5bc7c9124883bd98fcf1e9513930d88a8b0dd4bbf0c77fc6fe79`
  (+146/−17). Rev B (audited in §1) = probe `7c0f9c73…`, battery
  `077af0b5…`. Worktree: `M corpus/fixtures/{pygame_probe,pygame_battery}.py`,
  `?? reports/round-73/` — not committed as of write time.
- Revision sequence on disk (the r72-simplifier's tracked snapshot
  machinery recorded every fixture pair — exactly the fixture-pair
  provenance this report argues for in §5.6): rev B 14:45:35Z
  (`7c0f9c73/077af0b5`) → probe rev 1 15:34:16Z (`9a983e2b/077af0b5`) →
  probe rev 2 15:34:36Z (`92ff4963/077af0b5`) → probe rev 3 15:34:56Z
  (`9a7456a3/077af0b5`) → battery rev 1 15:35:06Z (`9a7456a3/6e908e6f`)
  → battery rev 2 15:35:26Z (`9a7456a3/fb2c400a`) → current battery rev 3
  `6d3fbf5f` (stable since 15:37:05Z; the pair audited in §2).
- r73 reports landed: `r73-scout.md` 15:26:15Z, `r73-critic.md` 15:27:06Z
  (rewritten 15:40:31Z with the landed-diff replay), `r73-boundary.md`
  15:27:34Z, `r73-author.md` 15:39Z — all untracked; reviewer / simplifier
  / verifier / baseline reports pending.
- Scratch: 9 r73 seat dirs present; author landed 15:34–15:36Z (fixture
  watcher `watch.log` + 60 s poller `landing_check.log`).
- Toolchain (my run + receipts): CPython 3.14.7, `io.DEFAULT_BUFFER_SIZE`
  131072, locale UTF-8; pygame 2.6.1/SDL 2.32.72, node v24.21.0 per
  sibling receipts on this host; local clock = UTC−3.

## 1. Raw stream vs parsed view — parser audit

### 1.1 The parser as shipped (rev B, line cites; core unchanged in rev C)

- `parse_arms` (`pygame_battery.py:167-176` rev B; `:236` rev C):
  anchored `^PYGAME-ARM (\S+) \| (.*)$` on `line.strip()`; kv tokens with
  `=`; per-arm `dict.update` → **last-wins**.
- `check` (`:179-193`): exact string pins; `(lo,hi)` float bounds;
  missing key → FAIL.
- RAW_CASES predicate (rev B `:237-248`): first `str.find` hit of each
  marker anywhere; 4-way relation. Rev C generalizes it (§2).
- `done_marker` (`:220`): exact stripped-line equality; `launch_ok`
  (`:219`) from the process exit — not stream-forgeable.

### 1.2 Audit over every landed pygame receipt (98 runs; rev-B window 80)

`raw_vs_parsed.py` re-derives the parsed view from each run's
`probe.stdout.txt` with the **tracked** `parse_arms` and compares to the
run's `verdicts.json`:

| metric | result |
|---|---|
| pygame-family receipts audited (r71–r73, excl. frozen copies) | **98** (83 tracked-vocabulary, 15 seat-variant) |
| receipt-vs-raw drift on re-derivable keys | **0** |
| lines containing `PYGAME-ARM` the regex drops | **0** |
| runs with duplicate ARM lines for one arm (last-wins overwrites) | **0** |
| REORDER marker occurrences per stream | 0× (pre-r72 runs) or exactly 1× (post-r72) — no stray text |
| hex tokens in any stdout | exactly `0x1000000` (SDL flags) in all runs |
| address-like tokens (ASLR surface) | **0** |
| derived-classification cases not re-derivable by key lookup | 121 (15 seat-variant batteries) |

The tracked receipts are self-re-derivable (raw key ↔ observed); the
seat-variant receipts are not — their `observed` values are seat-side
classifications whose classifiers are not in the receipt.

### 1.3 Synthetic hazard cells (rev-B logic; `parser_audit.json`)

Fed to the tracked parser via read-only import; RAW_CASES predicate
replicated verbatim with line cites.

| cell | shape | tracked view | class |
|---|---|---|---|
| E / J | stray-prefixed (`INJECTEDPYGAME-ARM…`) / no-space-pipe line | **dropped** | drop (safe, silent) |
| G | arm-name pollution (`reorder_bufX`) | queried arm missing | drop-as-missing |
| F | split value (`topology=prefix_reorderINJECTED`) | observed corrupt → FAIL | visible corruption |
| D | duplicate key in one line | last-wins | forge-accept (inline) |
| B | honest midline line + **appended** forged line | `rord_buf_topo` **FAIL→PASS** | **forge-accept** |
| C | forged line prepended | last-wins keeps honest → FAIL | direction matters |
| H / I | indented / CRLF forged line | parsed | forge variants |
| K | empty value | FAIL | visible |
| L | `injected_at=0.0` vs pinned `"0"` | **FAIL** though semantically equal | repr brittleness |
| N / O / P | `REORDER-HEADER` / `REORDER-CHILDISH` / marker text in a comment earlier | hijacked first hit → wrong class either direction (**O = prefix PASS on an honest midline wire**) | **forge-accept (RAW_CASES)** |

`forge_flip_B`: `{rord_buf_topo: {honest: FAIL, forged: PASS}}`.

### 1.4 Forge mechanism cell — the round's own seam delivers it

`forge_cell.py` (own harness, parent piped to this reader; no tracked
fixture run): parent writes an honest
`reorder_buf … topology=midline_splice` line, then a descendant
(`Popen`, inherited fd1 — the r72 seam) writes a complete forged
`PYGAME-ARM reorder_buf | topology=prefix_reorder` line. Measured:
honest at byte 0, forged at 119 → parser last-wins → observed
`prefix_reorder` → pinned verdict **PASS** on a wire its own producer
wrote midline. Variants: partial forgery; descendant `0xFF` byte → reader
raises `UnicodeDecodeError`.

### 1.5 Crash-not-FAIL (decode boundary)

`run_process` catches `TimeoutExpired`/`OSError` only; `text=True` decodes
strictly (UTF-8). A non-UTF-8 byte on the capture raises
`UnicodeDecodeError` out of the battery → **no `verdicts.json`**: no PASS,
no FAIL row, no receipt (measured via imported `run_process` and the
mechanism cell). The studied seam can deny evidence rather than fail a
case.

### 1.6 Raw-wire pin stability

24 post-landing streams (20 canonical): first cross-run differing byte at
offset 145/146 inside `cadence60` timing fields; REORDER marker offsets
drift across identical topologies (canonical h ∈ [1897,1906], c ∈
[1883,1892], t ∈ [1910,1919], ±10 B) while the relation is constant and
every run's replica equals its receipt's `wire_topology`. **Topology class
is receipt-stable; exact offsets are not** — the brief's bounded-range
instruction is receipt-supported.

## 2. Post-landing audit — r73 rev C machinery

Revision pinned by assertion in `landed_audit.py` (probe
`9a7456a3…`, battery `6d3fbf5f…`; audit refuses to run if moved).

### 2.1 Diff shape

- probe `+165/−0` (docstring, `shutil`, node programs, `node_arm`, the
  four `main()` cells). Fully additive.
- battery `+146/−17`: the −17 are **inside the raw-wire processing
  block** — the r72 4-way predicate was *replaced* by the generalized
  `raw_topo3` + row loop (not insertion-only at the battery level).
  Verified: **0 removed CASES/RAW_CASES rows** (the r72 row is
  byte-identical), and `run_process` / `parse_arms` / `check` are
  **byte-identical to HEAD 2dd108b** (`inspect.getsource` comparison in
  `landed_audit.json`).
- New pin model: 19 appended CASES rows (metadata + per-cell pins) and
  RAW_CASES rows extended to `(name, pinned, markers, offset_bounds)`;
  `_rel` bounds are measured relative to the HEAD marker (offset-stable
  across preceding-wire jitter — the author replaced absolute bounds
  within the window; the dry run at 15:35:57Z still carried absolute
  bounds that would have failed at 128019 vs ≤127500).

### 2.2 Author evidence, re-derived

- 4 author runs (15:36:59–15:37:36Z): **80/80 PASS** each, exit 0,
  ~9.8 s, 0 receipt-vs-raw drift; newest run's raw-wire rows re-derived
  from its own `probe.stdout.txt` by my replica: **0 mismatches**
  (`landed_audit.json`).
- Dry-run wire replay (`r73-author/probe_dry.stdout.txt`): all landed raw
  rows + bounds + all CASES rows reproduce → MATCH. Wire facts: INFIX
  markers `head 2008 / inj 128019 / tail 202028` (rel 126011/200020);
  `FD2-ERR 202120 < FD2-HEAD 202128 < FD2-TAIL 202137`;
  `PYGAME_PROBE_DONE 202682 < DETACH-LATE 202700`; REORDER unchanged
  (CHILD 1892 < HEAD 1906).
- Prior-receipt regression: 55 receipts with REORDER markers, **0
  classification flips** between the old 4-way rule and the landed
  `raw_topo3` (the >64 B infix rule cannot flip any prior row) — the r72
  row's semantics survive the block rewrite.

### 2.3 New-marker hazard cells (`landed_audit.json`)

| cell | injection | outcome |
|---|---|---|
| H1 | `note: INFIX-HEADER mode` before the wire | INFIX-HEAD first hit hijacked (h=6) → **3 bounds rows FAIL** (128037 > 127500; 202046 > 201000) |
| H2 | `note: FD2-HEADER mode` before the wire | FD2-HEAD hijacked → **`fd2m_wire_topo` flips to midline_splice → FAIL** |
| H2b | `note: FD2-ERR seen` before the wire | row still prefix (honest wire was prefix) — same hijack class, non-discriminating instance |
| H3 | `log: PYGAME_PROBE_DONE reached` before the wire | detach anchor hijacked; `det_wire_eof` still **PASS** — the anchor is a substring find, not the line-anchored done-marker check: an earlier occurrence of the text satisfies it (forge-accept) |
| H4 | `DETACH-LATE` before the anchor | `premature` → FAIL (safe direction) |
| H5 | `PYGAME-ARM note \| text=INFIX-HEAD` | bounds hijack (h=23, rel 128030) |
| H6 | forged `INFIX-HEAD`+100B+`INFIX-INJ` mini-triple before the wire | class row **PASS (infix)**; bounds rows catch this instance (h=0, rel=111) — bounds are a partial mitigation, not a witness |

Reading: the landed raw-wire rows are still first-occurrence,
unattributed predicates. The bounds rows catch offsets outside their
windows, but a marker fragment placed to satisfy the class relation can
flip a class row; the detach anchor in particular does not require the
real done marker.

### 2.4 Node-absent conditional (replica cell + independent receipt)

Synthetic blocked wire (`node_present=False` + `blocked_node_absent`
cells) through the landed CASES rows → **15 FAILs**: `node_present`
(False≠True), `node_ver` (absent≠v24.21.0), `nsm_topo`/`nbig_topo`/
`nsy_topo` (blocked_node_absent≠pinned), plus the missing keys/`ret=NA`.
The critic's PATH-stripped replay (`r73-critic/replay/runs-nodeabsent/`,
15:38:50Z) measured exactly this: **65/80, 15 FAILs**. So the brief's
"node absent → bounded blocked verdict" is implemented **probe-side**
(no fabrication) but the **battery verdict on a node-absent host is
FAIL** — the author's report states this explicitly ("FAILed pins
(bounded, honest)"). Scribe records the convergence; a viability-
conditional pin would need a different case model (out of this seat's
scope).

### 2.5 Independent replays observed (seat landings, cited as data)

- **critic**: 6 clean replays 80/80 (`replay/runs`, `runs-rep0/1/2` ×2
  rounds); `stuck_detach` **79/80** with the single FAIL
  `det_wire_eof markers_missing` (anchor present, late=−1) at 13.05 s —
  the designed measured FAIL for a stuck detach (the `timeout -s KILL 4`
  self-bound fires inside the battery's 30 s); `runs-unbuf` **77/80**:
  `self_wire_reorders` midline, `infx_wire_topo_injected_rel` 140011
  (no withholding → no fill-flush epoch), `fd2m_wire_topo` midline — all
  three are expected deviations of an unbuffered probe (the infix/fd2
  cells are buffer-regime-coupled by construction).
- **simplifier**: `runs-draft1` 80/80.
- **verifier**: `runs/pygame-20261014T153638981800Z` **77/80** — the 3
  FAILs are `infx_wire_topo_head_at` (obs 2005 vs pinned [0,1000]),
  `…_injected_at` (128016 vs [125000,127500]), `…_tail_at` (202025 vs
  [199000,201000]). The receipt's own `pinned` fields show the **old
  absolute bounds**; the verifier ran at 15:36:38Z, ~3 s before the
  author replaced them with relative bounds (15:36:41Z). **Stale-revision
  artifact, not a live defect** — but it is the receipt↔revision binding
  gap made concrete: the receipt records no fixture hash, so only the
  embedded pinned values (or run-dir mtime vs tree mtime) reveal which
  revision it judged. This is the strongest argument in this round for a
  `fixture_sha256` field in `verdicts.json`.

## 3. Receipt hygiene (paths / timestamps / ASLR)

`receipt_hygiene.py` — 68 pygame-family receipts (r71–r73) + 29 sibling
receipts:

| check | result |
|---|---|
| stamp == dirname, totals/verdict consistent, exit 0, done_marker, paths exist | 68/68 |
| `verdicts.json` mtime − `started_utc` | 8.3–22.6 s (median ~9.0), never negative |
| stderr | **all non-empty and byte-identical** (334 B AVX2 `RuntimeWarning`, single sha group `5ebca6a8…`); never asserted by the battery |
| address-like tokens in any pygame receipt | **0** |
| fixture sha256 recorded | **0/68** — provenance by path only |
| non-canonical `probe` path (copy / patched probe) | 17/68 |
| `python` field is a wrapper script | 3/68 |
| effective env (`PYTHONUNBUFFERED`, SDL_*) recorded | no — behavioral-only |

ASLR, precisely: pygame receipts carry no address-like values (only the
SDL flags constant); the godot-family sibling receipts (8 runs) carry
per-run-varying backtrace addresses (`…(+0x3e6f0) [0x7f…]`, different
every run) — cross-family receipt diffing must scrub those. No
audio/g3d claim by this seat.

Receipt mutability: the scout's `detach_eof.json` was **rewritten in
place** between two reads ~1 min apart (15:24Z values vs the 15:25:29Z
file the scout report cites); the critic's report was rewritten at
15:40:31Z (adding the landed-diff replay). Scratch receipts/reports are
not immutable; every citation in this report carries a read-time sha256
pin (§7).

### 3.1 Prior-round drift items

1. `reports/round-71/r71-{reviewer,scribe,verifier}.md` exist on disk but
   are **untracked** at HEAD (written after the r71 report-last commit
   `44127af`, which contains the other seven).
2. Two **tracked** r72-simplifier scratch files are modified in the
   worktree after the r72 report-last commit: `corpus/live/r72-simplifier/
   watch.log` (two appended watcher lines, 14:57:19/14:57:29Z) and
   `corpus/live/r72-simplifier/snapshots/log.txt` (six appended
   revision-pair lines, 14:45:35–15:35:26Z), plus five new **untracked**
   snapshot dirs under the tracked `snapshots/` path
   (`92ff4963…/9a7456a3…/9a983e2b…` probe pairs, `9a7456a3-6e908e6f…/
   9a7456a3-fb2c400a…` battery pairs). All insertion-only, log/snapshot
   only — but they are tracked byte deltas the reviewer's "touched prior
   bytes" check should expect.
3. `reports/round-72/r72-scribe.md:76` "All r72-scribe runs: exit 0,
   stderr empty." — exit 0 ✓, stderr **not** empty (334 B AVX2 warning,
   byte-identical, all 7 runs). The separate r72-baseline claim "seven
   `.stderr` captures 0 bytes" (Godot batteries) **is** verified 7/7.

## 4. Seat landings + report-vs-receipt audit

`seat_receipt_check.py` — **27 MATCH, 2 DRIFT, 1 resolved** across the
four landed r73 reports (scout/critic/boundary/author):

| # | item | evidence |
|---|---|---|
| D1 | `r73-critic.md` F1 table cites four hang receipts; `hang_shape_r72_shape.json` / `hang_shape_pgroup_kill.json` **do not exist** (only `bounded_drain` / `self_bounded`). Those two variants are the ones the table says were SIGKILLed by the outer bound — `hang_shape.py:130` writes the JSON only after the variant returns, so a killed variant cannot leave that receipt. The two hang rows are exit-code observations; the two surviving receipts match their rows. | `corpus/live/r73-critic/hang_shape*.json`, `hang_shape.py:119-132` |
| D2 | `r73-boundary.md:19` calls `21ca0cd4…`/`31918715…` "the r72 hashes" — they are **md5**, unlabeled (lane convention sha256). Verified: md5 of the **rev-B HEAD blobs** (`git show HEAD:…`) equals those values, so the content pin is correct; the label/algorithm is the drift. (A working-tree check today reads a spurious mismatch because the tree moved to rev C — precisely the hazard.) | `r73-boundary/state.txt`; `git show HEAD:… \| md5sum` |
| D3 | `r73-critic.md:10` "snapshot 15:23–15:35Z" — at my first read (file mtime 15:27:06Z) the window end postdated the artifact; the 15:40:31Z rewrite added the landed replay (15:36–15:39Z) and **resolves** it. Retained as a note on read-time drift checking. | `stat`, current text |

Verified MATCH (selected): scout detach/node/infix/classifier tables vs
its receipts; critic detach battery replay (FAIL, 55/55, `probe_exit
None`, `TIMEOUT after 30 seconds`, detach ARM line before the done
marker), node bimodality `{65536×4, 131072×6}`, async control 200000×5,
infix epochs 126005×6 / 252005×2 / owner-stall prefix×3 / explicit 101005×3,
fd2 byte-identity; boundary 37 cells × 3 runs all stable with 0 byte-order
diffs, hazard rcs (3× −9, bounded pair 0), D-family `fd1_eof_ms`; author
80/80 ×4, `infx_rel=126011` ×4, `det=eof_hold`, tails
`PYGAME_PROBE_DONE\nDETACH-LATE`.

### 4.1 Label-convention divergence (critic report ↔ its own receipts)

F2 table calls `big65536` and `writesync_200k` "splice";
`node_census.json` records `topology: "infix"` for both (its positional
rule: non-adjacent INJ ⇒ infix), while `node_census_edges.json` records
`classes: ["splice"×5]` for `big200k_async`. Offsets the report pins
match the receipts; only the class word differs, because the critic's two
receipts use two label rules.

### 4.2 Cross-seat conflict — reported verbatim, not adjudicated

**node >64 KB single write: INJ offset and its mechanism.**
- scout: `node_big` INJ **exactly 65536** (= pipe capacity), 3/3 (+2);
  receipt `r73-scout/node_census.json`.
- critic: `big200k` ×10 → **{65536×4, 131072×6}**, class infix 10/10;
  calls exact-65536 a **reader-timing artifact** and attributes the class
  to the spawn API's loop-blocking (`execSync` infix 10/10 vs `cp.spawn`
  splice 10/10); receipt `r73-critic/node_census_edges.json`.
- boundary: its driver measures INJ@65536 (65535/65536 midline, 65537
  infix); receipt `r73-boundary/edge.json`.
- author: `nbig_inj_bound (40000,199000)` bounded; observed
  65541/65541/65541/98309 across its 4 runs; receipt
  `r73-author/runs/*`.

All four receipt sets exist and are internally consistent; the
disagreement is offset stability across readers and the attribution of
the class. The canonical judge decides. Scribe note only: this is the
"survival ≠ safety" class — a pin that survives on one reader may fail on
another; a set/band pin plus the write-order witness is the shape all
four receipts can support.

## 5. Findings

1. **Forge-accept is real and measured through the round's own seam.**
   The parser has no writer attribution and last-wins per arm; one
   appended well-formed ARM line flips a pinned content row FAIL→PASS
   (rev-B synthetic cell B; mechanism cell via a descendant writing into
   the inherited fd1). `launch_ok`/exit are not stream-forgeable. On the
   landed 80/80 tree there is no headroom today; the hazard is
   load-bearing exactly when a row FAILs.
2. **The raw-wire rows remain first-occurrence, unattributed predicates**
   (rev B and rev C alike): substring hijack (H1/H2/H5), marker text in
   unrelated lines, and — rev C — the detach anchor being a substring
   find of `PYGAME_PROBE_DONE` (H3: `eof_hold` can PASS without the real
   done marker). The `_rel` bounds are a partial mitigation (H6 caught
   the forged mini-triple on offsets), not an attribution witness.
3. **Crash-not-FAIL:** a non-UTF-8 byte on the capture kills the battery
   (`UnicodeDecodeError` escapes `run_process`) and leaves **no
   receipt** — denial-of-evidence, measured.
4. **Drop-not-misattribute holds for the demonstrated glue shapes** —
   silently: a legitimate line with a stray prefix is equally lost.
5. **Exact-string pins are repr-brittle; exact offsets are not
   receipt-stable** (±10 B across canonical runs); the landed rev C
   `_rel` bounds are the right instrument (the pre-fix absolute bounds
   failed the verifier's 15:36:38Z replay 3/80 — §2.5).
6. **Receipts are path-pinned, not byte-pinned, and mutable in place**:
   no fixture hash in any of 68 pygame receipts; 17 point at
   copies/patched probes; 3 use a wrapper script as `python`; one receipt
   was rewritten between my reads. Citations need read-time hashes; a
   `fixture_sha256` field would have made the verifier's stale-revision
   FAIL self-explaining. The r72-simplifier's tracked snapshot log
   (§0/§3.1) is the in-flight mitigation — it recorded all seven fixture
   pairs; the durable form is a per-receipt field.
7. **stderr is captured and never asserted**; all pygame receipts carry
   the same deterministic 334 B warning; one prior-round report's
   "stderr empty" claim is drift by construction.
8. **Node-absent hosts FAIL the battery by pin design** (15 rows; critic
   measured 65/80 PATH-stripped): probe-side blocked verdict ✓, battery
   verdict FAIL — author and scribe converge on this reading.
9. **Landing/drift items:** three r71 reports untracked; a tracked r72
   watcher log modified; two cited critic hang receipts cannot exist as
   written; one boundary hash label is md5 in a sha256 lane.
10. **Cross-seat node-offset conflict** reported verbatim (§4.2); no
    adjudication by this seat.

## 6. Known limits / hand-off

- This seat audited both revisions (rev B receipts + rev C machinery) but
  ran **no** tracked battery; all replay numbers cited are sibling
  receipts re-read, and all hazard cells are synthetic streams or
  bounded own-harness probes.
- The post-landing audit is pinned to the rev C hashes asserted in
  `landed_audit.py`; if the author lands further revisions, re-run:
  `parser_audit.py`, `landed_audit.py`, `raw_vs_parsed.py`,
  `receipt_hygiene.py`, `seat_receipt_check.py`.
- Raw-vs-parsed drift checks are key-lookup + replica based; 121 derived
  seat classifications are not independently re-derived.
- Host-bounded: CPython 3.14.7, locale UTF-8, this host's clocks
  (UTC−3 local). No tty-regime, audio, or g3d claim; no fifo cells; no
  production claim.
- The reviewer/verifier/simplifier/baseline r73 reports had not landed at
  write time; their receipts were audited as they appeared (§2.5).

## 7. Artifact inventory (`corpus/live/r73-scribe/`)

| artifact | sha256 (prefix) | content |
|---|---|---|
| `parser_audit.py` | `8d9cb4878e1aa80f` | rev-B hazard cells (17) vs tracked parser (2-tuple rows) |
| `parser_audit.json` | `c956d80ed83f170a` | cells + `forge_flip_B` + decode probe |
| `forge_cell.py` / `forge_cell.json` | `4baf65e5db135595` / `ff57a40d6413890d` | descendant-fd1 forgery mechanism cells |
| `raw_vs_parsed.py` | `16d606dd09fbf06b` | 98-receipt raw↔parsed re-derivation (rev-C rows) |
| `raw_vs_parsed.json` | `362b6e77a4df4944` | per-run drift/drop/marker/hex tables |
| `receipt_hygiene.py` / `receipt_hygiene.json` | `de31c8aa6369d9d0` / `a7d166a1f6a16f7e` | 97-receipt hygiene sweep |
| `stream_stability.py` / `stream_stability.json` | `d8a999f141b4ca82` / `c75880cf10702e98` | cross-run byte diffs, marker offsets |
| `landed_audit.py` | `8a7c9177925fdc0c` | rev-C: function identity, dry-run + receipt replay, H-cells, node-absent, regression |
| `landed_audit.json` | `1f51e57c0cc226eb` | all rev-C cells (asserted revision pins inside) |
| `seat_receipt_check.py` / `.json` | `7ec7f227a32a71e3` / `04f93d0d71ea89b2` | report↔receipt checks (27/2/1) + conflicts |
| `watch.sh`, `watch.log`, `landing_check.log` | — | 15 s watcher + 60 s poller (fixture/HEAD/report transitions) |
| `r73-scribe-draft.md` | — | pre-landing draft (superseded by this report; kept as provenance) |

Read-time sha256 pins for the seat receipts cited (files are live
scratch): `r73-scout/{detach_eof,node_census,classifier_demo}.json`
`23504dc9…`, `9fd361ff…`, `ba2d6967…`; `r73-critic/node_census.json`
`ba4d8af4…`, `node_census_edges.json` `cae2bc4e…`, `paced_infix.json`
`aab5fff5…`, `fd2_driver_config.json` `7d9389d5…`,
`detach_battery/…/verdicts.json` `94f243eb…`; `r73-boundary/edge.json`
`f3e1ca64…`, `edge-run2.json` `f0fc085c…`, `edge-load.json` `9f83d9b6…`,
`hazard.json` `75a84019…`, `state.txt` `d32e057f…`; rev-C fixture pins in
§0.

## 8. Commands run (cwd `~/Projects/shokunin/game-dev-2d-shokunin`; all exit 0 unless noted)

- `python3 corpus/live/r73-scribe/parser_audit.py` → 17 cells; `forge_flip_B` FAIL→PASS; decode probe raises `UnicodeDecodeError`
- `python3 corpus/live/r73-scribe/forge_cell.py` → forgery PASS on honest-midline wire; partial; decode raise
- `python3 corpus/live/r73-scribe/raw_vs_parsed.py` → 98 runs, 0 drift, 121 derived-unverifiable
- `python3 corpus/live/r73-scribe/receipt_hygiene.py` → 68 pygame receipts; 1 stderr sha group; 0 addr tokens; 0 fixture-sha fields
- `python3 corpus/live/r73-scribe/stream_stability.py` → 24 post-landing runs; first diff @145/146
- `python3 corpus/live/r73-scribe/landed_audit.py` → function identity 3/3 MATCH; dry-run + receipt replay MATCH; H1–H6 HAZARD; node-absent 15 FAILs; 55-receipt regression 0 flips
- `python3 corpus/live/r73-scribe/seat_receipt_check.py` → 27 MATCH / 2 DRIFT / 1 resolved
- read-only: `sha256sum`/`md5sum`, `git show HEAD:…`/`git diff`/`git status`, `stat`, `grep`, `find`, `inspect.getsource` comparisons
- `bash corpus/live/r73-scribe/watch.sh` (background) + 60 s poller
- No tracked file written; no git mutation; only this report and
  `corpus/live/r73-scribe/` written.

## 9. Return shape

- **Behavior:** evidentiary audit — raw-vs-parsed re-derivation over 98
  receipts, 17 rev-B hazard cells + 8 rev-C hazard/conditional cells, 3
  forgery mechanism cells, 97-receipt hygiene sweep, landing tracking,
  report↔receipt checks across four landed r73 reports. Read-only over
  product surfaces; no product code, no judge, no commit.
- **Gates exercised:** tracked parser (read-only import, both
  revisions), tracked `run_process` (decode boundary), sibling receipts
  and reports (read-only), watcher logs.
- **Touched surfaces:** `reports/round-73/r73-scribe.md` (new) and
  `corpus/live/r73-scribe/**` (new). Nothing else.
- **Out of scope (not done, by rule):** no tracked edit, no battery run,
  no subagent dispatch, no audio/g3d claim, no adjudication of the
  node-offset conflict, no rerun of sibling harnesses, no
  contract/axis/route/judgment change.
- **Findings:** §5 (10 items), §3.1 + §4 drift tables, §4.2 conflict.
- **Artifacts:** §7.
