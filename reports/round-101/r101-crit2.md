# r101-crit2 — Attack C2: beyond `m_seq` (CRLF seam, split-stream, timeout truncation, echo-pins)

Plan (5 lines):
1. Read `reports/round-100/r100-critic.md` §F2 + find the r100b replay source & pin mechanism in `corpus/fixtures/`.
2. Enumerate the 4 named attack surfaces: CRLF seam in replay pins, split-stream forgery, timeout truncation of multi-line replay, echo-pins on divergences.
3. Build scratch forgeries under `/tmp/r101-crit2/` for each reachable attack; record exact accept/reject behavior with observed output bytes.
4. Classify which attacks the current pin design *misses*; derive the required row guards (per-row predicates, run receipt here).
5. Write verdict + required-guards table; keep shard < 400 lines.

Load context (recorded once): `uptime` → `16:21:23 up 1 day, 16:21, 1 user, load average: 41.05, 21.42, 13.72`
(godot `4.7.2.stable.arch_linux.ed1daf0bf`; 3D lane r104 swarming concurrently).

**Verdict: the C2 design as stated (a `\n`-joined 14-line pin in the existing merged classifier) is necessary but NOT sufficient.**
It rejects the reported `m_seq` in-span insertion (measured), but it is stream-blind, newline-normalizing, timeout-path-asymmetric, and — absent a fixture-digest gate — echo-forgeable. Eight guards below turn each measured bypass into a rejection; G8 (fixture digest) is the only one that closes the out-of-span ceiling.

**Addendum — in-flight E12 design probed (§5).** While this seat ran, `corpus/fixtures/r101_seqfull.gd`
landed (new fixture, not yet referenced by any CASES row): `SEQ_BEGIN` + 14 cells + `SEQ_CENSUS` +
`SEQ_END digest=<sha256>`; the digest matched an independent recomputation of the captured 14 lines
(measured). It catches mechanism mutations (m_focus: digest+census both move), but a **digest-line-only
row pin still accepts the `m_seq` foreign-print forgery** (measured SF1: `pin_D=true, pin_SPAN=false`).
The row must pin the contiguous `SEQ_BEGIN…SEQ_END` span, not just the digest line — pin recipe in §5.

---

## 0. What I ran (all scratch, no battery)

| # | artifact | scope | result |
|---|---|---|---|
| 1 | `reports/round-101/mutations/r101-crit2-attack-matrix.py` (+ `.json`) | 18 Godot launches on `/tmp/r101-crit2/` (15 harness-classified + 3 raw-byte captures): pristine clean=1 ×2, pristine clean=0, and 12 forged variants; harness-exact capture (`subprocess.run(capture_output=True, text=True, timeout=8)`, `output=stdout+stderr`, `signature in output`, allowlist `('ERROR: Parameter "t" is null.',)`) | all completed, 1.35–2.02 s/run |
| 2 | `reports/round-101/mutations/r101-crit2-followup.py` (+ `.json`) | stderr-carried pinned line; full-transcript echo + mechanism mutation; `TimeoutExpired.stdout` type/newline probe | completed |
| 3 | inline guard check on pristine clean/noclean | G1/G3/G4 must not false-reject the real transcript | 2/2 clean |
| 4 | recon | `sha256sum corpus/fixtures/r100b_seq.gd`; grep for a digest assertion | digest = `4718a19e0050f4…eafa94dd`; **no assertion** (comment only, `run_battery.py:1543`) |

Pristine replay ground truth (observed): 14 `PASS r100_gui <cell>` lines in
`census, routing, hover, motion, localpos, cursor, clip, drag, touch, subvp, warp, focus, render, osmeta`
order, then `SEQ_DONE clean=1|0`; exit 0; stdout 6804 B / stderr 293 B; clean=1 run twice byte-identical.
Transcript-string digests (normalized text, 14 lines + receipt):
`clean` block `sha256=5be029c7d129bf6d9289a3b484efac34c73e2eae8fd34e47f8cdf4f88293718c`,
block+receipt `sha256=3bd85c74ea0d26934d7e5050c46914a615b1d75bd1a1b69fcea13621d9e75467`;
`noclean` block `sha256=da5cd7d773a50624f8bb9ae5ef90f2fa282901cab00d192d0eb67bee7bcf856a`,
block+receipt `sha256=0975086d640305ed965bd517df7fa0e58c30c1c53aa85d9478c228649ad94138`.
Exact lines are in `r101-crit2-attack-matrix.json` (`c1_sha_lines`, `c0_sha_lines`).

---

## 1. Attack matrix (observed on scratch; O = observation)

Pin shapes evaluated: **landed** = today's 1-line row pin; **F14** = 14 cell lines `\n`-joined;
**F14+S** = F14 + terminal `SEQ_DONE` line contiguous; **closure** = G3+G4 predicates (block on
stdout, no `PASS `/`SEQ_DONE ` line on stderr, one `PASS r100_gui` line per cell / 14 total,
one receipt) — a column value `fail` means the composite guard rejects, whether via the stdout
anchor or via the count clauses.

| variant (fixture edit) | landed pin | F14 | F14+S | closure | reading |
|---|---|---|---|---|---|
| v1 inside-span forged line after `cursor` (clean=1) | **PASS** | FAIL | FAIL | **fail** | F2 confirmed; F14/G1 + stdout anchor reject; the non-PASS forged line itself is invisible to G4 |
| v1b inside-span forged line after `hover` (clean=0) | **PASS** | FAIL | FAIL | **fail** | m_seq replica; same as v1 |
| v2 forged pre-block + between block/`SEQ_DONE` + post-receipt | – | **PASS** | **FAIL** | pass | receipt closes only the "between" slot |
| v3 forged payload on **stderr only** (`printerr`) | – | **PASS** | **PASS** | **pass** | no pin shape sees it |
| v4 last cell + receipt routed to stderr (real fixture) | – | FAIL | FAIL | fail | merged-order artifact: engine `ERROR:` lands between pinned lines |
| v4b synthetic 7/7 split (lines 1–7 stdout, 8–14 stderr) | – | **PASS** | FAIL | **fail** | merged seam; stdout has only 7/14 |
| v5 echoed block first + real `focus` mechanism mutated (`f.grab_focus()` removed) | – | **PASS** | FAIL | **fail** | echo-pin; closure catches |
| v5b echoed block after receipt + same mutation | – | **PASS** | FAIL | **fail** | order-independent |
| v6 all 15 receipt lines emitted CRLF (`printraw … "\r\n"`) | – | **PASS** | **PASS** | pass | text-mode capture normalizes CRLF→LF |
| v7 lone `\r` inside forged payload | – | FAIL | FAIL | **fail** | text mode split it into 2 receipt lines; block broken by the insertion slot |
| v8 14 cells then hang (8 s timeout) | – | – | – | – | 14 lines present in truncated capture, `SEQ_DONE` absent, classified **FAIL** (error clause) |
| v9 only first 7 cells run, exit 0 | – | FAIL | FAIL | – | 7-cell+receipt prefix pin **PASS** (truncated-pin ceiling) |
| follow-up A: `cursor` line moved to stderr alone | **PASS** | FAIL | – | **fail** | landed pin is stream-blind; stdout 13/14 |
| follow-up B: full transcript (14+receipt) echoed first + `focus` mutated | **PASS** | **PASS** | **PASS** | **fail** | 28 `PASS` lines; only closure/digest distinguish |
| pristine clean=1 / clean=0 | PASS | PASS | PASS | **pass** | no false rejection |

Artifact note: v1b's `seq_done_once` column in the JSON reads False because the script evaluated
the clean=1 receipt string against the clean=0 run; the real `SEQ_DONE clean=0` was present.
JSON artifact disclosed, not a finding.

### 1.1 CRLF seam (v6, v6b, follow-up C) — observed
* Normal path: `subprocess.run(..., text=True)` returns translated text. A fixture emitting 15
  CRLF receipt lines classifies **PASS** against the LF-joined F14/F14+S pins, and
  `record["output"]` contains **no `\r`** (`runtime.crlf.textmode_capture_has_cr = false`;
  raw bytes: `raw_stdout_has_crlf = true`, 15 `\r\n`).
* Timeout path: follow-up C hung a CRLF-emitting probe; `TimeoutExpired.stdout` on this host's
  Python is **`bytes`** (`type=bytes`, `repr=b'…PROBE_A\\r\\nPROB…'`), and
  `run_process_streams` decodes it **without** newline translation. The same process bytes are
  therefore LF-text in one path and CR-text in the other; the LF pin matches only one of them.
* Consequence: the pin is byte-exact **after universal-newline normalization**, not over process
  bytes. The harness retains no raw bytes on the normal path, so a raw-byte guard needs a
  capture-layer change (G0/G6), not a row edit.

### 1.2 Split-stream (v3, v4, v4b, A) — observed
* The classifier consumes `proc_stdout + proc_stderr`; a pin is stream-blind. Moving the `cursor`
  cell's pinned line to stderr leaves the landed row **PASS** (`cursor_in_stdout=false,
  cursor_in_stderr=true`).
* The synthetic 7/7 split satisfies F14 in the merged blob while stdout carries 7 of 14 lines.
  (A real-fixture reroute of the tail fails F14 because the render cell's engine `ERROR:` line is
  concatenated between pinned lines — merged concatenation does not preserve temporal order. So
  this is a deliberate-forgery/classifier seam, not an accidental-mutation hole.)
* `printerr` payloads that are not `PASS`-shaped are invisible to every pin and to closure.

### 1.3 Timeout truncation (v8, v9) — observed
* 8 s timeout: all 14 cell lines are present in `exc.stdout` (decoded raw), `SEQ_DONE` is absent,
  and the row fails **only** because `error is not None`. Any future "signature present even on
  timeout" tolerance would turn truncation into a PASS.
* A pin harvested from a 7-cell truncated run (or a 7-cell prefix pin) accepts a 7-cell prefix
  transcript: `prefix7_plus_seqdone_pin = true`. Pins must span all 14 cells **and** the receipt.
* Headroom: pristine replay 1.35–2.02 s across all non-hang launches (18 matrix + 4 follow-up +
  3 inline guard runs) at load 33–41 vs the 8 s bound (≥3.9×); no observed truncation of a
  genuine run.

### 1.4 Echo-pins on divergences (v5, v5b, B) — observed
* A literal echo of the pinned block (including the 4 divergence lines) anywhere in the output
  satisfies F14 — and B shows that even F14+S is satisfied by echoing block+receipt first, while
  the **real** `focus` mechanism is mutated (`f0 owner=null` class; mutated line present in output).
* Contiguous pins are defeated by echo because they are presence predicates, not transcript
  equality. Closure (one line per cell / 14 total) rejects v5/v5b/B; a deliberate forger can still
  emit an echo outside any count shape, so G8 (fixture digest) is the decisive guard.

---

## 2. Required row guards (for the integration seat; stated as row predicates)

Apply to **both** `r100b_seq_clean` (`--clean=1`) and `r100b_seq_noclean` (`--clean=0`).

| guard | predicate | measured attack it closes |
|---|---|---|
| **G0 capture** | For these rows capture bytes (`text=False`) or return a raw-byte sidecar; decode with one frozen policy (no newline translation) so the verdict is a function of process bytes | normal-vs-timeout representation asymmetry (§1.1) |
| **G1 full block** | signature = all 14 `PASS r100_gui <cell>` lines in replay order, contiguous, `\n`-joined | v1/v1b in-span forged line (landed pins PASS, F14 FAIL) |
| **G2 receipt** | append the exact terminal `SEQ_DONE clean=<v>` line contiguously after the 14th cell; keep `code == 0 and error is None` | v2 between-block-and-receipt insertion; v9 prefix/truncated pin; v8 truncation |
| **G3 stdout anchor** | the whole signature must appear in `proc_stdout` alone; stderr must contain no `PASS r100_gui` / `SEQ_DONE ` line | follow-up A (stderr-carried pin); v4b split seam |
| **G4 closure** | exactly 14 `PASS r100_gui` lines, one per cell name; exactly one `SEQ_DONE clean=<v>`; no other `PASS ` line | v5/v5b/B echo transcripts (28 PASS lines) |
| **G5 stderr closure** (optional) | stderr exactly within the 6-line per-variant allowlist (see below) | v3 stderr-only forged payload |
| **G6 newline discipline** | if G0 is not adopted, the pin claim must read "byte-identical after universal-newline normalization" and receipts must carry that flag; do not claim raw-byte exactness | v6 CRLF transcript accepted by LF pin |
| **G7 timeout** | keep the 8 s bound; never accept a pin present in a `TimeoutExpired` capture | v8 truncation pass-shape |
| **G8 fixture digest** | assert `sha256(corpus/fixtures/r100b_seq.gd) == 4718a19e0050f4043613a5a93a13cbd812c811605f7a14d33e000544eafa94dd` at battery time (meta row or `main()` assert) | all echo/out-of-span forgeries (v2 pre/post, v3, v5/v5b/B); freezes G5 frame line numbers |

G3 implementation shape: mirror the existing `required_stderr` post-check with an inverted
`required_stdout` clause, or move these two rows to `classify_streams` with a per-row stderr
allowlist. Do not widen `classify_process` globally.

G5 measured stderr sets (6 lines each, **variant-specific**):
```
both:  ERROR: Parameter "t" is null.
       at: texture_2d_get (./servers/rendering/dummy/storage/texture_storage.h:110)
       GDScript backtrace (most recent call first):
       [0] _cell_render (res://r100b_seq.gd:762)
       [1] _run (res://r100b_seq.gd:116)
clean: [2] _cleanup   (res://r100b_seq.gd:135)
noclean:[2] _cell_focus (res://r100b_seq.gd:750)
```
These frame line numbers are fixture-byte-bound; that is why G5 must be paired with G8.

**Suggested pin values** (if the author lands the simple in-classifier form): signature =
14 lines + `SEQ_DONE clean=<v>`; verify against the digests above. If G0 changes capture,
recompute the digests from raw bytes (values are engine-build- and fixture-byte-conditional:
`4.7.2.stable.arch_linux.ed1daf0bf`, fixture `4718a19e…`).

**Ceiling statement to put in the row comment / report:** output pins are *presence* predicates.
Extra output outside the pinned span is invisible to them; a fixture that echoes the pinned span
and diverges elsewhere is caught only by G4 (PASS-shaped echoes) and G8 (arbitrary echoes). They
discriminate accidental mechanism mutations (the `m_clip`/`m_focus`/`m_seq` class), not a
fixture that deliberately prints the pin.

---

## 3. Observation vs inference vs unknown

* **Observation**: every matrix/follow-up row above; `TimeoutExpired.stdout` type `bytes` with
  `\r` retained on this host; pristine transcript bytes/digests; 6-line stderr sets; fixture
  sha256; no digest assertion anywhere in `run_battery.py` (grep: `4718a19e` appears only at
  line 1543, a comment).
* **Inference**: G5's noclean frame `[2] _cell_focus` follows from the same render call site
  (measured in the noclean capture); V4b's split seam is a classifier-semantics probe using a
  synthetic script, not an edit of the real fixture (the real-fixture reroute fails F14 because
  the engine `ERROR:` line intervenes — measured v4).
* **Unknown**: Python-version portability of the `TimeoutExpired.stdout` bytes/str behavior
  (CPython implementation detail; measured only here); U+0085/U+2028 `splitlines()`-only seams
  (not probed — `splitlines()` splits on them but universal-newline translation does not);
  whether the integration seat adopts G0/G8 (outside this seat's file ownership).

---

## 4. Files touched (no shared-file edits, no commit)

* `reports/round-101/r101-crit2.md` (this shard)
* `reports/round-101/mutations/r101-crit2-attack-matrix.py` + `r101-crit2-attack-matrix.json`
* `reports/round-101/mutations/r101-crit2-followup.py` + `r101-crit2-followup.json`
* `reports/round-101/mutations/r101-crit2-seqfull.py` + `r101-crit2-seqfull.json`
* scratch only under `/tmp/r101-crit2/` (Godot projects, logs; not in the repo)

---

## 5. Addendum — the in-flight E12 design (`corpus/fixtures/r101_seqfull.gd`), probed

**What I ran:** `reports/round-101/mutations/r101-crit2-seqfull.py` (+ `.json`), 9 Godot launches on
`/tmp/r101-crit2/sf_*/` scratch copies (pristine clean=1/clean=0, SF1–SF6, one raw-byte capture).
Fixture sha256 at probe time: `426075c8993b1a93ff9dd8e2cd6a14145644b64587bbc30c89d929a0f674273d`
(file is untracked/in-flight; digest may move before integration).

**Base facts (observed):** `SEQ_BEGIN cells=14 clean=1 pins=14`; all 14 cell lines on stdout;
`SEQ_CENSUS identical=10 divergent_n=4 divergent=[cursor|touch|subvp|warp]` (clean-1) and
`identical=5 divergent_n=9 divergent=[hover|motion|localpos|cursor|clip|drag|touch|subvp|warp]`
(clean-0); `SEQ_END digest=5be029c7d129bf6d9289a3b484efac34c73e2eae8fd34e47f8cdf4f88293718c` (1) /
`da5cd7d773a50624f8bb9ae5ef90f2fa282901cab00d192d0eb67bee7bcf856a` (0). The printed digest equals
the sha256 of the captured 14 cell lines recomputed independently → the self-binding is honest on
this host. stderr = the same 6-line set as the old fixture.

**Attack table** (candidates: `D` = digest line alone, merged; `DS` = census+digest lines, merged;
`SPAN` = `SEQ_BEGIN…SEQ_END` contiguous, merged; `anchor` = SPAN in stdout alone + no `PASS `/`SEQ_`
line on stderr):

| variant | D | DS | SPAN | anchor | reading |
|---|---|---|---|---|---|
| SF1 foreign `print()` between cells (m_seq shape) | **PASS** | **PASS** | **FAIL** | fail | digest binds only `_emit` lines; a foreign print is outside it → **digest-only pin inherits the F2 hole** |
| SF2 foreign print after `SEQ_END` | PASS | PASS | **PASS** | pass | out-of-span ceiling → G8 |
| SF3 stderr payload | PASS | PASS | PASS | pass | needs G5 |
| SF4 census+digest moved to stderr | **PASS** | **PASS** | FAIL | fail | merged pins stream-blind → G3 |
| SF5 `f.grab_focus()` removed (m_focus) | **FAIL** | **FAIL** | FAIL | fail | digest+census both move → mechanism mutations caught |
| SF6 receipts+cell lines emitted CRLF | PASS | PASS | PASS | pass | text-mode normalization → G6 (raw `\r\n` present) |

**Required pin recipe for the seqfull rows (if landed):**
1. signature = the **full contiguous span** `SEQ_BEGIN cells=14 clean=<v> pins=14` + the 14
   `PASS r100_gui` lines + `SEQ_CENSUS …` + `SEQ_END digest=…`, `\n`-joined. This single signature
   carries G1/G2, pins the 4 divergences by name (closing F2's second half) and binds the values
   via the digest. **Digest-line-only or census+digest pins are insufficient (SF1, SF4, measured).**
2. plus G3 (span in stdout alone; no `PASS `/`SEQ_` line on stderr), G4 (one line per cell, 14
   total, one `SEQ_BEGIN`/`SEQ_END`), G5 (6-line stderr allowlist), G6 (newline policy), G7
   (timeout clause), and G8 with the fixture sha256 above.
3. The self-digest does close the m_clip/m_focus/F2 cell-mutation class (SF5) — its remaining hole
   is exactly foreign bytes outside `_transcript`, i.e. the span pin + G8, not a weaker pin.

**Observation vs inference here:** SF1–SF6 all observed; "digest-only pin inherits the F2 hole" is
the observed SF1 verdict; the recipe is this seat's prescription, not a landed fact.
