# Round 79 baseline report — freeze + post-fold references (host: devin)

Seat: g2d baseline (LEAF). Read-only on tracked files: no fixture/runner edit,
no commit, no LOG/SCORECARD write. All artifacts under
`corpus/live/r79-baseline/` (untracked scratch) plus this report.

Battery scope per brief: **Godot battery** (`corpus/fixtures/run_battery.py`,
**88 rows** = 81 seeded `CASES` + 7 meta) + **LOVE battery**
(`corpus/fixtures/love_battery.py`, **92 rows** = 15 `CASES` + 4
`SPLICE_CELLS` + 73 `IW_CELLS`). The r79 declared axis-move touches
`run_battery.py` + new `phys2d_events.gd` only (`tasks/g2d-r79-author.md`,
pre-measured by `reports/round-79/r79-scout.md`); the brief requires
`love_battery.py` untouched this round — verified: its live bytes never
changed during this seat (mtime frozen at 18:58:25 -0300, sha
`be91ba25…`).

**STATUS: COMPLETE.** Frozen `884a4c4` (r78 report-last) at **23:50:06Z**
and replayed both batteries on frozen-HEAD bytes twice each (Godot
23:50:28→23:52:07Z / 23:52:35→23:54:16Z; LOVE 23:52:10→23:52:30Z /
23:54:16→23:54:35Z, all four PASS, all four provably before the author's
first tracked write at **23:55:35Z**). Godot: **88/88 PASS** both reps,
**0 tuple mismatches vs all 15 refs** (11 of them the Godot 88-row runs
carried inside `corpus/live/r78-baseline/freeze/extract/`). LOVE:
**92/92 PASS** both reps, **0 tuple mismatches and 0 real drift vs all 9
refs** (r78-baseline frozen + postland primary), the only row-byte deltas
being 4–7 bound-pinned `observed` timing rows per ref.

**`lsp` disclosure.** No `lsp` device is exposed in this session. This seat
made no symbol-aware edit (no rename/reference/definition work exists in a
read-only freeze): it wrote new scratch files (`corpus/live/r79-baseline/**`)
and this new report. Nothing was hand-renamed.

---

## 0. Timeline — freeze provably predates the r79 arm

All times UTC, receipts first-hand (`run-start.txt`, `poll-author.txt`,
`freeze/extract-done.txt`, run stdout headers).

| time (UTC) | event |
|---|---|
| 23:48Z | wave `shokunin-train-20261101-w20` task dir created |
| **23:50:06Z** | `run-start.txt`; HEAD + `git status` + live arm-file digests captured; `git diff HEAD -- corpus/fixtures/` **empty** |
| 23:50:06–23:50:14Z | `git archive HEAD` → 688,373,760 B tar; sha256 `6f1f16cb…` (re-run identical) |
| **23:50:15Z** | extraction done: 44,888 files + 34 symlinks = **44,922** non-dir entries == `git ls-files` |
| **23:50:28→23:52:07Z** | Godot frozen replay **rep1** — 88/88 PASS (99 s) |
| **23:52:10→23:52:30Z** | LOVE frozen replay **rep1** — 92/92 PASS |
| **23:52:35→23:54:16Z** | Godot frozen replay **rep2** — 88/88 PASS |
| **23:54:16→23:54:35Z** | LOVE frozen replay **rep2** — 92/92 PASS |
| 23:50:42Z | author creates new untracked `corpus/fixtures/phys2d_events.gd` (sha `7329acb2…` = the scout's scratch source) — during rep1, **not in frozen HEAD, never read by any replay** (runs source from the frozen extract) |
| **23:55:35Z** | author's **first tracked write**: `corpus/fixtures/run_battery.py` `f55c27d8…`→`9cb52531…` (+67 lines, insertion-only) — **after all four replays** |
| 23:55:37Z | `poll-author.txt`: ` M corpus/fixtures/run_battery.py`, `?? corpus/fixtures/phys2d_events.gd` |

Author divergence evidence: `stat` mtimes above plus the frozen extract still
carrying `run_battery.py` `f55c27d8…` and **no** `phys2d_events.gd`
(`ls` → ENOENT). No replay can have seen post-freeze bytes.

---

## 1. Frozen-tree provenance

- Frozen HEAD: `884a4c4245f7a0838b8e00c8b7595f1056544032` — *r78 report-last:
  adjudicator ADMIT-corr + ledger*, committed 2026-10-14 20:42:34 -03:00.
  Parent chain `1fde57d` (r78 fold) → `1a03b7a` (r78 work) → `d4aaa95`.
- Archive `freeze/HEAD-884a4c4….tar`: **688,373,760 B**, sha256
  `6f1f16cb70728c1aaa96bfdb3d9f9436bbfce4dc692ba4bf01f57f03659cc2a9`;
  `git archive HEAD | sha256sum` re-run = **identical** (deterministic).
- Tar members 44,922 == `git ls-files | wc -l` 44,922 (r78: 44,920; +2 =
  r78 report-last payload). `comm` both directions → **0 missing / 0 extra**.
- Extraction `freeze/extract/`: 44,888 files + 34 symlinks == 44,922 exactly.
- **Fixture seed**: 61-entry sha256 manifest of every file under
  `corpus/fixtures/` (minus `__pycache__`) — frozen vs live
  **byte-identical (61/61, `diff` empty)** at freeze time.
- Fixture digests **triple-match** (`HEAD:` blob == live == frozen extract) for
  all 8 checked: `love_battery.py` `be91ba25…`, `run_battery.py` `f55c27d8…`,
  `love_phys_probe/main.lua` `ff148ccc…`, `love_phys_probe/conf.lua`
  `85aa6232…`, `love_probe/main.lua` `a0afe6ca…`, `love_probe/conf.lua`
  `0b45ef73…`, `descendant_pipe_probe.gd` `c86bda84…`,
  `stream_attribution_probe.gd` `dc0b0d5c…`.
- `run_battery.py` content history: last change **`9fb50aa` (r69)**; identical
  sha `f55c27d8…` at `1a03b7a`, `1fde57d`, `884a4c4` — every Godot ref below
  therefore ran the same harness bytes.
- Pre-move surface snapshot (`preland-snapshot.log`): Godot `CASES` 81 rows
  (sha `e1a55eb7…`); LOVE `CASES` 15 (`a03a4559…`, unchanged since r74),
  `SPLICE_CELLS` 4 (`d3790623…`), `IW_CELLS` **73** (`50d64eff…`, grew from 56
  at r78) → 92.
- Post-replay pristine check: `find freeze/extract -newer extract-done.txt`
  → **0 entries** (runs wrote only into their own `--runs` trees).
- Scratch isolation: the Godot run's scratch is a copy of the **frozen**
  fixtures (`seed` field = `…/freeze/extract/corpus/fixtures`); its extra
  top-level files are only Godot-generated `.gd.uid` sidecars, `out`, and a
  probe-written `pickup.tscn`; **`phys2d_events.gd` absent**; `run_battery.py`
  excluded by design. LOVE `probe_dir` = `…/freeze/extract/corpus/fixtures/love_probe`.

### Exact invocations

cwd `/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin`,
`X=corpus/live/r79-baseline/freeze/extract`, all with
`PYTHONDONTWRITEBYTECODE=1 python3 -B` (no `.pyc` into the frozen tree):

```
python3 -B $X/corpus/fixtures/run_battery.py --runs corpus/live/r79-baseline/freeze/godot-runs   # rep1
python3 -B $X/corpus/fixtures/run_battery.py --runs corpus/live/r79-baseline/freeze/godot-runs2  # rep2
python3 -B $X/corpus/fixtures/love_battery.py --runs corpus/live/r79-baseline/freeze/love-runs   # rep1
python3 -B $X/corpus/fixtures/love_battery.py --runs corpus/live/r79-baseline/freeze/love-runs2  # rep2
```

Environment (`env.txt`, identical profile to r70–r78): LOVE 11.5
"Mysterious Mysteries" (`/usr/bin/love`), Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`godot` on PATH — see caveat C3),
Python 3.14.7 + pygame 2.6.1 / SDL 2.32.72, `io.DEFAULT_BUFFER_SIZE` 131072,
node v24.21.0, Linux 7.2.3-arch1-3.

---

## 2. The frozen reference tuples

**Godot 88-row verdict tuple** — per row:
`(case, script, flags, expected_exit, actual_exit, signature, verdict, error,
expected_errors)` for the 81 seeded rows; for the 7 meta rows
`(case, verdict, mode, bounded_claim, discriminations, census, shape_matrix,
midline_spliced_line, provenance_only_line_diff, bound_seconds,
poll_tick_seconds, crash_allowlist, self_sigkill_exit, sigabrt_exit)`. Per-arm
launch records (`arms`, `hold_arm`, `hold_output_lines`, `genuine_control`,
`split_*`, `release_arm`, `gated_*_reps`, `seam_split_run`) and pid/path/
elapsed fields are **excluded** — they carry the run's own pids, streams and
paths and are volatile by construction (declared, not silently dropped).

**LOVE 92-row receipt tuple** — per row `(arm, key, pinned, verdict)`
(r62–r78 precedent) plus the whole-row canonical-JSON sha256.

Frozen sets (row-level shas in the files):
`freeze/godot-tuples-rep{1,2}.txt` (88 rows each),
`freeze/love-tuples-rep{1,2}.txt` (92 rows each); receipt digests in
`freeze/receipt-shas.txt`.

| artifact | sha256 |
|---|---|
| Godot rep1 `verdicts.json` | `1b244c74e2183b5c3d66af0a194146e46f89d201983680100b62cd6055c67237` |
| Godot rep2 `verdicts.json` | `a9fef5dfba5f704a61ef7db64deb1a4f81c139b2524084f162dbab92faa96362` |
| LOVE rep1 `verdicts.json` | `e034d39ddda5b00581f16d5641af9e6daf3a7ed91933cd4c4166e90ee556940b` |
| LOVE rep2 `verdicts.json` | `150c1ed4ca686421bab605b668e539d7f0239264a53417e42673d7019f459fec` |
| Godot tuple set rep1 / rep2 | `6c372761…` / `98384065…` |
| LOVE tuple set rep1 / rep2 | `e96dc587…` / `74f78572…` |

**Rep-to-rep stability.** Godot tuple bodies (rep1 vs rep2) **identical**;
output-normalized 81/81 identical. LOVE tuple bodies differ on **exactly 6
rows** — the bound-pinned `observed` timing keys (`dtcadence|dt_min_ms`,
`dtcadence|dt_max_ms`, `dtcadence|dt_mean_ms`, `popen|l1_wait_ms`,
`popen|l2_wait_ms`, `popen|close_wait_ms`, `popen|total_ms`); pinned ranges and
verdicts identical, `real_drift=0`.

---

## 3. Godot battery vs references — ZERO tuple drift

`compare.py godot` (`godot-compare-rep1.txt`, `godot-compare-rep2.txt`).
Per-ref: 88 common rows, 0 new/old-only, **0 tuple mismatches**; the
output-normalized column is a secondary whole-stdout check with declared
volatile tokens masked (run paths, pids, ASLR addresses, tween floats,
fixture line numbers).

| ref (rep1 pass) | rows | tuple mism | output-normalized |
|---|---|---|---|
| `r79-scout/runs/20261014T213005111532Z` (HEAD `1a03b7a`) | 88 | **0** | 81/81 |
| `r78-reviewer/sibling-runs/…T211913141844Z` (r78 work tree) | 88 | **0** | 81/81 |
| r78-baseline freeze extract — r66-reviewer `runs-postdiff` | 88 | **0** | 80/81 |
| r78-baseline freeze extract — r66-simplifier `runs-author` | 88 | **0** | 81/81 |
| r78-baseline freeze extract — r67-simplifier `runs-landed` | 88 | **0** | 80/81 |
| r78-baseline freeze extract — r68-scribe `runs-flagless` | 88 | **0** | 80/81 |
| r78-baseline freeze extract — r68-simplifier `runs-landed` | 88 | **0** | 80/81 |
| r78-baseline freeze extract — r69-baseline `runs-livectl` | 88 | **0** | 80/81 |
| r78-baseline freeze extract — r69-scribe `runs-flagless` | 88 | **0** | 80/81 |
| r78-baseline freeze extract — r69-scribe `runs-landed-flagless` | 88 | **0** | 80/81 |
| r78-baseline freeze extract — r69-simplifier `runs-landed` | 88 | **0** | 80/81 |
| r78-baseline freeze extract — r69-simplifier `runs-preland` | 88 | **0** | 80/81 |
| r78-baseline freeze extract — r71-baseline `godot-runs` | 88 | **0** | 80/81 |
| `runs/20261014T140233983332Z` (shared r70-era) | 88 | **0** | 81/81 |
| `gd-scout/runs/20261014T194720280349Z` (r77 map) | 88 | **0** | 81/81 |

Rep2 re-ran 7 of these (r79-scout, r78-reviewer, r69-baseline, r71-baseline,
r66-simplifier, runs-shared, gd-scout): **7/7 refs, 0 tuple mismatches**.

**Brief compliance note.** `corpus/live/r78-baseline/` contains **no
seat-executed Godot run** (that seat ran LOVE+pygame only), so the brief's
fallback applies: the comparison uses the HEAD~1/HEAD~2-tree artifacts
(`r78-reviewer` sibling and `r79-scout`, both on the `1a03b7a` r78 work
tree) plus
the **11 88-row Godot runs carried inside the r78-baseline freeze extract**
(the historical lattice frozen at `d4aaa95`) and two older live refs.

---

## 4. LOVE battery vs references — ZERO tuple drift

`compare.py love` (`love-compare-rep1.txt`, `love-compare-rep2.txt`).
Compared on `(arm, key, pinned, verdict)` + whole-row sha; `real_drift` =
row differences beyond the `observed` field.

| ref | rows | common | tuple mism | byte-identical | observed-only | real drift |
|---|---|---|---|---|---|---|
| **r78-baseline postland rep1** (primary) | 92 | 92 | **0** | 85/92 | 7 | **0** |
| **r78-baseline postland rep2** (primary) | 92 | 92 | **0** | 86/92 | 6 | **0** |
| **r78-baseline frozen** (pre-move) | 75 | 75 | **0** | 68/75 | 7 | **0** |
| r78-author final (`…T210943322605Z`) | 92 | 92 | **0** | 85/92 | 7 | **0** |
| r78-reviewer (`…T211903490145Z`) | 92 | 92 | **0** | 86/92 | 6 | **0** |
| r78-verifier r1 | 92 | 92 | **0** | 85/92 | 7 | **0** |
| r78-simplifier `runs-vfold` | 92 | 92 | **0** | 85/92 | 7 | **0** |
| `runs/love-20261014T215836641142Z` (shared) | 92 | 92 | **0** | 88/92 | 4 | **0** |
| r77-baseline postland (pre-r78) | 75 | 75 | **0** | 68/75 | 7 | **0** |

Rep2 re-ran 6 refs (postland ×2, frozen-75, verifier, simplifier, shared):
**6/6, 0 tuple mismatches, 0 real drift**. Against both 75-row refs the
`new_only` set is **exactly the 17 r78-added `iw|cell=*` keys** (livelock ×3,
n_* ×11, z_* ×3) — no other delta.

The `observed` jitter is the declared bound-pinned class only
(`dtcadence|dt_min_ms`, `dtcadence|dt_max_ms`, `dtcadence|dt_mean_ms`,
`popen|l1_wait_ms`, `popen|l2_wait_ms`, `popen|close_wait_ms`,
`popen|total_ms`); every pinned `(lo,hi)` range and verdict is identical.

---

## 5. Remaining risks / caveats

- **C1 — meta-row arm records are not tuple-compared.** The 7 Godot meta rows
  are compared on verdict-bearing fields; their per-arm launch records
  (pids, raw streams, elapsed) are excluded by declaration. A regression
  *inside* an arm record that leaves `discriminations`/`verdict` intact would
  not be caught by this freeze (it is caught by the battery's own meta
  verdict, which is in the tuple).
- **C2 — volatile classes are masked in the output check**, named exactly:
  run paths under `corpus/live/**`, pids, ASLR `Load address`/`0x…`
  backtrace addresses, `tween_flash` transient floats, and fixture
  line-number tokens (`.gd|.lua|.py:NNN`). Masking applies to the secondary
  output comparison only; the tuple comparison is unmasked.
- **C3 — invocation-form token.** 10 of 15 Godot refs invoke the binary as
  `/usr/bin/godot` (explicit `--godot`), this freeze uses PATH `godot`; the
  single residual output diff (`… - godot(+0x…)` vs `… - /usr/bin/godot(+0x…)`
  in the `crash_spontaneous_sigabrt` backtrace) is that declared form, not
  lattice drift.
- **C4 — author divergence during rep1.** `phys2d_events.gd` appeared in the
  live tree 14 s after Godot rep1 started. It is untracked, absent from the
  frozen extract, absent from the run's scratch, and irrelevant to the 88
  frozen rows; the tracked arm file's first write is 23:55:35Z, after rep2.
  Both timestamps are recorded above rather than smoothed.
- **C5 — post-freeze replay of the landed arm is out of scope** for this seat
  (the r79 author had not landed a commit at report time); the r79 wave's
  post-land comparison belongs to the r79 verifier/baseline follow-up.
- **C6 — state size.** `corpus/live/r79-baseline/` is ~1.4 GB (657 MB tar +
  759 MB extract), same order as r76–r78 baselines; retention is the
  operator's call.

## 6. Verdict

Frozen HEAD `884a4c4` reproduces the r78-closed lattice exactly on both
batteries: **Godot 88/88 PASS ×2 with 0/88 tuple mismatches vs 15 refs**;
**LOVE 92/92 PASS ×2 with 0/92 tuple mismatches and 0 real drift vs 9 refs**.
The r79 before-state is the two frozen tuple sets in
`corpus/live/r79-baseline/freeze/` (shas in §2), and the freeze provably
predates the r79 arm's first tracked write. No tracked file was modified by
this seat (`post-run-dirty-state.txt`: only the author's `run_battery.py` +
`phys2d_events.gd` and pre-existing r72-simplifier dirt).
