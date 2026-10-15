# Round 89 baseline (g2d) — frozen-tree regression replay (host: plazir27 / devin)

Seat: `g2d-r89-baseline` (LEAF, executor / frozen `probeParent`). Read-only on
tracked files: no fixture or runner edit, no commit, no LOG/SCORECARD write.
All artifacts under `corpus/live/r89-baseline/` (untracked scratch) plus this
new report. All Godot launches `--headless`, `timeout`-bounded (harness 8 s/row,
60 s for the two export rows; outer `timeout 1200` per rep, per assignment).

**STATUS: FROZEN TREE IS GREEN — 215/215 PASS in both reps, and every stable
verdict tuple is byte-identical to the canonical 215-row r88-verifier receipt
(`70bf54f2…`). Zero new findings. The only raw-stdout deltas are the declared
volatile class (8 rows), the 5-row envelope class (observed modes vary by
design, all PASS, tuples carry the full payload set), and the declared
`mp_loopback` random-peer-id token. Neither documented flake
(`crash_spontaneous_sigabrt` timeout class, `input_lattice_phys_peer`
`ev_step_delta` ladder) manifested in either rep — including rep2 under heavy
sibling load (loadavg 29.2 at end).**

| headline | value |
|---|---|
| rows replayed | **215** (208 seeded `CASES` + 7 meta) × 2 reps on the frozen tree |
| HEAD frozen at start | **`062893255cfa1e2559cf61990ecd758971b000f9`** (*r88 verifier: VERIFIED w/ reservation*), unchanged pre/post every rep |
| row-count determinant | HEAD contains `3c47eee` → **215-row scope** (the 207-row alternative does not apply; both receipts `rows=215`) |
| rep1 | **215/215 PASS**, rc=0, stderr 0 B, 202.849 s, verdicts sha `4389b713d650d5272b22c49847490d8210d58f2073a79714b6fd37e067de54f7` |
| rep2 | **215/215 PASS**, rc=0, stderr 0 B, 223.971 s, verdicts sha `1dc26e0b9abfb7586445a9a32274c3c42eb30bfce5f596c994342038bf9ea9a9` |
| rep1 ↔ rep2 ↔ ref `70bf54f2…` | **tuple byte-identical 215/215, 0 mismatches** (all three pairwise diffs empty) |
| raw-stdout deltas vs ref | rep1: 11 = 2 envelope + 8 declared-volatile + 1 declared `mp_loopback` uid; rep2: 12 = 3 envelope + 8 volatile + 1 uid |
| 5 envelope cells | **5/5 PASS in both reps**; modes vary vs ref on 4 of 10 cell-reps (matrix §3.3); tuples identical everywhere |
| frozen-tree purity after reps | content vs HEAD `rc=0`; file-set 95886 == 95886, 0 differences (pre and post) |
| documented flakes | **none manifested** (crash-row timeout class and `phys_peer` ladder both clean; envelope alt modes observed, by design) |
| sibling contention | r88-fold battery (19:03:29Z→) + g3d r93-baseline battery + r91-scout/r89-boundary probes concurrent; load 2.75 → 16.46 (rep1 end) → 29.20 (rep2 end) |
| live-tree movement during seat | r88 **fold** seat's uncommitted edits to `corpus/fixtures/{run_battery.py,r88_surfaces.gd}` landed 19:01:42–19:02:14Z (rep1 tail); HEAD never moved; frozen receipts unaffected (disclosed §5) |
| lsp device | not present on this host (no GDScript server); not needed — this seat performed no symbol edit, only new untracked artifacts |

---

## 1. Freeze procedure and file-set identity

1. `git rev-parse HEAD` → `062893255cfa1e2559cf61990ecd758971b000f9` at
   **18:58:33Z**, frozen to `freeze-head.txt`; HEAD identical at every
   pre/post-rep check and at report time (no commit landed during the seat).
2. `git archive HEAD | tar -x -C corpus/live/r89-baseline/tree` at
   **18:58:33–18:58:37Z**; archive sha256
   `cd0736b7d08843f2e9714303ed75c20efc361e20e4afd258dd199b22c66ee54a`.
3. **File-set identity** vs `git ls-files`: tracked **95886**; extracted
   (files + symlinks) **95886**; `diff` empty **pre** and **post** the reps.
   (The two committed absolute symlinks
   `corpus/live/r67-simplifier/del-measure/fixtures/{controls,level_collision}`
   extract as symlinks and are counted with `-type l`; with `-type f` only they
   read as 68 "missing" entries — the 95886==95886 identity above is the
   correct file-set comparison, and `git-ls-files.txt`/`tree-files-{pre,post}.txt`
   are all the same sha `b9e1f163…`.)
4. **Content identity**: `git --work-tree=<tree> diff --quiet HEAD` → **rc=0**
   before and after both reps; 0 tracked modifications, 0 untracked files in
   the tree.
5. Harness sha on the frozen tree: `fde5913be1ffbf2632050c62bb8006ae74b7cdb486ae7fba6cc34167024e1754`
   (`tree/corpus/fixtures/run_battery.py`), identical in all four pre/post
   timing lines. Frozen fixture shas cross-check the r88 landing:
   `r88_surfaces.gd 78370a04…`, `r88_spawnable.tscn 89b9ddbe…` — both equal to
   the r88-verifier receipt at `3c47eee`.

Rep command (per assignment shape; executed from the frozen tree, receipts
written to live scratch so the tree stays pure):

```
cd corpus/live/r89-baseline/tree
PYTHONDONTWRITEBYTECODE=1 timeout 1200 python3 -B corpus/fixtures/run_battery.py \
  --runs /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r89-baseline/runs{N}
```

Runner script: `corpus/live/r89-baseline/run-reps.sh` (sha `fb02979c…`);
timing log `rep-timing.txt` (sha `05b3c5b8…`). Environment: Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`), Python 3.14.7,
`plazir27`, 32 cores (`env.txt` sha `60c648b3…`).

---

## 2. Rep receipts

| rep | start (UTC) | end (UTC) | secs | rc | rows | verdict | stderr | verdicts sha256 |
|---|---|---|---|---|---|---|---|---|
| 1 | 18:58:50 | 19:02:13 | 202.849 | 0 | 215 | PASS | 0 B | `4389b713…de54f7` |
| 2 | 19:02:16 | 19:06:00 | 223.971 | 0 | 215 | PASS | 0 B | `1dc26e0b…ea9a9` |

- Both `verdicts.json` carry `verdict=PASS`; `Counter({'PASS': 215})`; zero
  non-PASS rows; zero rows with a non-null `error` field.
- `godot-battery-rep{1,2}.stdout` each contain 216 `PASS ` lines (215 rows +
  the final `PASS battery:` line); stderr both exactly 0 B
  (`e3b0c442…`, the empty-string sha).
- Loadavg at rep boundaries: pre-rep1 `2.75 4.18 6.05`; rep1 end
  `16.46 8.94 7.43`; pre-rep2 `16.67 9.11 7.49`; rep2 end `29.20 19.56 11.85`.
  Concurrent siblings observed: g3d `r93-baseline` battery (from ~18:59Z),
  r88-fold battery (`runs1` stamp `20261015T190329837761Z`), r91-scout and
  r89-boundary Godot probes. **Rep2 was the contended one and still returned a
  full green 215/215** — a flake-free result under load, recorded as such.

---

## 3. Comparisons vs the canonical 215-row receipt

Reference: `corpus/live/r88-verifier/runs2/20261015T183553023488Z/verdicts.json`
sha `70bf54f2412d040c56e6ce518e8494adbb4a4d07c90ebd6ec151ffc8b7f7668b`
(215/215 PASS). `git diff f9e8a5b 0628932 -- corpus/fixtures/` is empty, so the
reference fixture bytes are exactly the frozen fixture bytes.

### 3.1 Tuple identity (canonical stable tuple per row)

`freeze/godot-tuples-rep{1,2}.txt` and `…-ref-r88verifier2.txt` each 215 rows;
all three pairwise diffs are **empty** (`tuple-diff-*.txt` = empty-string sha
`e3b0c442…`):

| pair | common | new/old only | tuple mismatches |
|---|---|---|---|
| rep1 ↔ rep2 | 215 | 0 / 0 | **0** |
| rep1 ↔ ref | 215 | 0 / 0 | **0** |
| rep2 ↔ ref | 215 | 0 / 0 | **0** |

### 3.2 Raw / normalized stdout classification (`r88_compare.py`)

| pair | RAW identical | RAW differing (classes) | NORMALIZED differing | not-carried |
|---|---|---|---|---|
| rep1 ↔ ref | 197/215 | 11 = 2 envelope + 8 volatile + 1 uid | 3 = 2 envelope + 1 uid | 7 |
| rep2 ↔ ref | 196/215 | 12 = 3 envelope + 8 volatile + 1 uid | 4 = 3 envelope + 1 uid | 7 |

- The 8 declared-volatile rows raw-differ exactly as declared: ASLR
  (`crash_spontaneous_sigabrt` Load address), pids
  (`descendant_pipe_detached_control`, `descendant_pipe_forged_signature_release`),
  pid+path (`save_process_{writer,reader,missing}`, `save_roundtrip`), and the
  tween transient floats (`tween_flash`). All normalized-identical; all tuple-identical.
- `not-carried=7` = the 7 meta probe rows that carry no `output` key
  (`probe_save_independent_process`, `probe_spontaneous_crash_classification`,
  `probe_descendant_pipe_eof`, `probe_descendant_signature_spoof`,
  `probe_while_live_signature_gate`, `probe_descendant_error_spoof`,
  `probe_error_clause_surface`) — expected shape, same in the reference.
- **`r88_surfaces_mp_loopback` uid (informational, not a fail):** raw line
  carries a run-random decimal peer id (`uid_c`: ref `364173685`, rep1
  `711476664`, rep2 `1665996349`). This is the **declared** volatile token
  (fixture comment + r88 scout §7.6 / author §"declared volatile peer-id token"
  / scribe: *"envelope payload text + `mp_loopback` raw-uid diagnostic line"*),
  and the r88-verifier's own comparisons classify it as `other=1` in both its
  runs. It appears as a NORMALIZED diff here only because `compare.py`'s
  address regex cannot mask digits glued to `s_conn`/`uid_c=` (word-boundary
  gap in the tooling, not drift). Tuple identical; pin itself is normalized.

### 3.3 Envelope-cell mode matrix (all cells PASS in every run)

`mode[k]` = which whitelisted payload the raw output matched (r88 taxonomy).

| cell | rep1 | rep2 | ref r88v2 | tuple identical |
|---|---|---|---|---|
| `input_lattice_api_press` | mode[0] | mode[0] | mode[0] | ✓ |
| `input_lattice_pre_frame` | mode[0] | **mode[1]** | mode[0] | ✓ |
| `input_lattice_press_phys` | mode[0] | mode[0] | **mode[1]** | ✓ |
| `input_lattice_release_edge` | **mode[1]** | mode[0] | mode[0] | ✓ |
| `input_lattice_ui_ns` | **mode[1]** | mode[0] | **mode[1]** | ✓ |

Alt-mode instances in this seat's 2 reps: rep1 `release_edge`+`ui_ns`; rep2
`pre_frame`. `api_press` never left mode[0] (consistent with r88's note that
its alt mode is the rare arm). Every cell PASSed in every run and every tuple
carries the full whitelisted payload set, so tuple identity holds regardless of
observed mode — the documented design.

---

## 4. Flake catalog (documented classes, evidence)

| id | documented class | observed? | evidence |
|---|---|---|---|
| F-A | `crash_spontaneous_sigabrt` 8 s crash-dump timeout | **no** | both reps: `PASS crash_spontaneous_sigabrt: exit=-6 signature='SPONTANEOUS_CRASH_PROBE: expected signature'`; row `verdict=PASS error=None`; only raw delta vs ref is the ASLR `Load address` line (volatile class). r88's rep2 hit this under load; rep2 here ran at loadavg 16.7–29.2 without it |
| F-B | `input_lattice_phys_peer` `ev_step_delta` ladder (0 vs 2; pre-existing, r88 fold fixing) | **no** | both reps: `PASS input_lattice phys_peer same_tick[…] ev_step_delta=0 …`; row raw-identical to ref, tuple-identical; never appears in any diff list |
| F-C | envelope bimodality (`api_press`/`pre_frame`/`press_phys`/`release_edge`/`ui_ns`) | **yes, by design** | matrix §3.3: 4 of 10 cell-reps hit an alt mode vs ref; all 5 cells PASS in both reps; 0 tuple mismatches |
| F-D | `mp_loopback` random peer id (declared volatile) | yes, declared | §3.2 — tuple identical, `other=1` class identical to r88-verifier's own classification |

**Any OTHER fail:** none. Zero non-PASS rows in both receipts; zero non-null
`error` fields; stderr 0 B in both reps. No timeout-class instance of any kind
was observed (the harness's own per-row timeouts never fired).

---

## 5. Purity, custody, live-tree movement

- **This seat's writes**: `corpus/live/r89-baseline/**` (untracked scratch:
  tree, runs1, runs2, freeze, stdout/stderr, runner, receipt) and this new
  report file. No tracked file was modified; `git status --porcelain` shows
  only `??` entries for this seat's paths. No commit, no push, no runtime
  invocation beyond the assigned battery.
- **Frozen tree purity**: content vs HEAD `rc=0` and file-set 0 differences
  pre and post the reps (0 status entries in the foreign work-tree check).
  The battery writes only under `--runs` (scratch project + receipts), so the
  tree stayed byte-pure through both reps.
- **Live-tree movement during the seat (disclosed, does not invalidate the
  pin)**: at 19:01:42–19:02:14Z (rep1 tail) the live repo gained uncommitted
  edits to `corpus/fixtures/r88_surfaces.gd` (+76/−13) and
  `corpus/fixtures/run_battery.py` (+14) — the **r88 fold seat in flight**
  (its own battery started `19:03:29Z`, visible in `pgrep`). Live harness sha
  moved `fde5913b…` → `7fb7f847…`; HEAD never moved and the frozen harness sha
  stayed `fde5913b…` in all pre/post lines. Both reps executed the **frozen**
  tree, so every receipt here is the pre-fold 215-row scope at HEAD `0628932`.
  At session start (18:58:12Z) `git status` showed no tracked modifications;
  the fold edits are not this seat's.
- No `r89-baseline` process remained after rep2 (`pgrep -af r89-baseline` empty).

---

## 6. Evidence index

`corpus/live/r89-baseline/receipt-shas.txt` (sha
`57e482d082090b36fd7a952d9e8f77fffbd63388451fb7790059e9bf2ee2dba5`) covers
every artifact below.

| artefact | path | sha256 (prefix) |
|---|---|---|
| rep1 receipt | `runs1/20261015T185850976403Z/verdicts.json` | `4389b713d650d527` |
| rep2 receipt | `runs2/20261015T190216535161Z/verdicts.json` | `1dc26e0b9abfb758` |
| canonical reference (external) | `corpus/live/r88-verifier/runs2/…/verdicts.json` | `70bf54f2412d040c` |
| rep stdout/stderr | `godot-battery-rep{1,2}.{stdout,stderr}` | `9757bdc7…` / `71a10134…` / `e3b0c442…` ×2 |
| tuple sets | `freeze/godot-tuples-rep{1,2}.txt`, `…-ref-r88verifier2.txt` | `d08df268…`, `67e9dced…`, `f28df983…` |
| tuple diffs (all empty) | `freeze/tuple-diff-*.txt` | `e3b0c442…` |
| raw/normalized compares | `freeze/compare-rep{1,2}-vs-ref.txt` | `da799fa7…`, `a9368464…` |
| envelope matrices | `freeze/envelope-rep{1,2}-vs-ref.txt` | `f7bf21dd…`, `45980ee6…` |
| frozen harness / fixtures | `tree/corpus/fixtures/{run_battery.py,r88_surfaces.gd,r88_spawnable.tscn}` | `fde5913b…`, `78370a04…`, `89b9ddbe…` |
| file-set receipts | `freeze/git-ls-files.txt`, `tree-files-{pre,post}.txt` (all same sha) | `b9e1f163…` |
| freeze pins | `freeze-head.txt`, `freeze-{start,end}-utc.txt` | `bd3b9c40…`, `dcc41dd5…`, `505bea83…` |
| env / runner / timing | `env.txt`, `run-reps.sh`, `rep-timing.txt` | `60c648b3…`, `fb02979c…`, `05b3c5b8…` |

Reproduce: `bash corpus/live/r89-baseline/run-reps.sh 1 && bash …/run-reps.sh 2`,
then `python3 corpus/live/r88-baseline/tuples.py godot <verdicts.json> <out.txt>`
and `python3 corpus/live/r88-baseline/r88_compare.py <mine> r88verifier2=<ref>`
(expect `tuple byte-identical=215/215`, `tuple_mismatches=0`).

---

## 7. Remaining risks / blockers

1. **Pre-fold scope.** This baseline pins the *landed r88* work at HEAD
   `0628932`; the r88 fold's in-flight live edits (`phys_peer` re-pin per F5,
   etc.) are outside this scope by construction and need their own verification
   after the fold lands. Frozen fixture bytes are exactly the committed bytes.
2. **Envelope mode distribution** is sampled, not derived: 2 reps observed alt
   modes on `pre_frame`/`release_edge`/`ui_ns` (and ref on `press_phys`/`ui_ns`);
   `api_press` alt mode remains rare/not observed here — same caveat r88
   recorded. Tuple identity is mode-independent, so this does not affect the
   verdict, only the mode census.
3. **`mp_loopback` uid token is not masked by `compare.py`'s normalizer**
   (word-boundary gap). It is declared volatile and tuple-neutral, but the
   comparison tooling will keep flagging it as a normalized diff until the
   regex covers `uid_c=`/`s_conn<digits>` tokens.
4. **Load-sensitivity is not exercised to failure**: both reps passed under
   high contention, but the crash-row timeout budget (8 s) remains the class
   r88 saw fail under load; a green rep under loadavg 29 is evidence of margin,
   not proof of immunity.
5. Blockers: **none**. Frozen tree is green in the canonical condition; no
   other fail, no defect found, nothing fixed (by instruction).
