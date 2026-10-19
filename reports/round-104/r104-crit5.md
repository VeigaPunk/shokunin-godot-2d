# r104-crit5 — KEY=C5 Exposure/wording audit

Host (`uptime`, first action): `22:29:59 up 1 day, 22:30, 1 user, load average 3.60, 2.16, 1.86`
Repo HEAD `eff29d1d` (main); remote `origin/main` = `eff29d1d`; no commits by this seat.
Scratch root `/var/tmp/r104-C5/` (never `/tmp` — EDQUOT class). `run_battery.py` never executed
(parsed with `ast` and `grep` only). No shared file edited.

## Plan (5 lines)
1. Pin host/engine facts (`uptime`, `godot --version`, binary path, templates dir) as the baseline every wording claim is judged against.
2. Exposure census: scan all r104 shards + new `corpus/fixtures/res_uid*.gd` for absolute host paths, device-census (joystick) tokens, `/tmp` scratch, RID/address leakage into receipts, sibling-lane references.
3. Wording audit: every load/timing/tps/env/template-path claim in r104 shards vs measured bytes or vs the code it describes; flag ambiguous "engine version" wording and unlabeled inference.
4. Hash-snapshot the concurrent `res_uid*.gd` fixtures (moving-target discipline, as r103-crit5 §3) and audit their receipt byte-stability claims by independent scratch re-run where the file is frozen.
5. Shard-only output + scripts under `reports/round-104/mutations/`; never `run_battery.py`; no shared-file edits; no commits.

**Status: COMPLETE.** Load series during the seat: `3.60 → 7.77 → 12.93 → 13.81 → 12.60`
(the swarm was mid-execution; every timing/identity datum below names its own condition).
Re-runnable evidence script: `reports/round-104/mutations/r104-C5-exposure-census.py` (read-only;
parses `run_battery.py` with `ast`, never executes it).

---

## §1 Baseline pins [obs]

| fact | measured value | command |
|---|---|---|
| engine | `4.7.2.stable.arch_linux.ed1daf0bf` | `godot --version` |
| editor path | `/usr/bin/godot` (single hit) | `which -a godot` |
| templates dir | `~/.local/share/godot/export_templates/4.7.2.stable/` (`version.txt` = `4.7.2.stable`) | `ls`, `cat` |
| `XDG_DATA_HOME` | `/home/vgpnk/.local/share` (**exported by the host**, not by a fixture) | `env \| grep ^XDG_` |
| `XDG_CONFIG_HOME` / `XDG_CACHE_HOME` | `/home/vgpnk/.config` / `/home/vgpnk/.cache` | `env` |
| `/tmp` | `tmpfs 16G, 13G used, 3.1G avail (80%)` | `df -h /tmp` |
| `/var/tmp` | `/dev/mapper/root 930G, 160G used (18%)` | `df -h /var/tmp` |

`cwd`/`HOME` are `/home/vgpnk/...` and `XDG_DATA_HOME` is already set by the host — so the r103-crit5 §2
finding (the XDG branch is the live branch, not the HOME branch) still holds, and any `user://` isolation
claim that redirects only `HOME` is unmeasured-by-construction on this host.

## §2 F1 — the brief's "round 103 closed at a322bce5" names a commit that is not an ancestor of HEAD

The seat brief states: *"Round 103 closed at a322bce5 (rebased lineage; remote main = eff29d1d)"*.
Measured [obs]:

```
$ git merge-base --is-ancestor a322bce5 eff29d1d   → exit 1 (NO-NOT-ANCESTOR)
$ git cat-file -t a322bce5                          → commit          (the object EXISTS)
$ git log --oneline --all | grep a322bce                → (no hit)
$ git for-each-ref → refs/heads/main eff29d1d ; refs/remotes/origin/main eff29d1d
$ git reflog --all | grep a322bc
  a322bce5 refs/heads/main@{1}: commit: round-103 record: LOG + SCORECARD verdicts (work 752cdc32)
  a322bce5 HEAD@{11}: commit: round-103 record: LOG + SCORECARD verdicts (work 752cdc32)
```

`a322bce5` is a **dangling reflog object** — the pre-rebase twin of `eff29d1d`. The two commits share
the parent `752cdc32` and the identical subject; their trees differ:

```
$ git diff --stat a322bce5 eff29d1d
 LOG.md   | 8 ++++++++
 README.md| 2 ++
 2 files changed, 10 insertions(+)
```
The 10 inserted lines are the README `**Wiki:**` header (operator directive 2026-10-17) and its LOG entry,
i.e. `eff29d1d` is the *later* of the two and `a322bce5` is superseded [inf from the diff direction].

**Exposure consequence.** Two r104 shards repeat the superseded sha as a factual round-close citation with
no label: `r104-scr2.md:4` and `r104-scr3.md:4` both read
`round 103 closed a322bce5 (rebased lineage)`. Every other r104 shard cites `eff29d1d` (32 shards).
Wording verdict: **ambiguous-to-wrong, harmless to results** — no artifact resolves through that sha
(`grep -rn a322bce5 reports/ LOG.md SCORECARD.md` returns only those two shard headers), but a reader
following the citation lands on a commit that is not in any branch.

## §3 F2 — every stored receipt's `command` field carries absolute host paths (measured)

`r104-C5-exposure-census.py` over all 8 stored runs (`corpus/live/runs/*/verdicts.json`) [obs]:

| run id | rows | verdicts | with `command` | PASS lines w/ host path | …carrying the run's own stamp |
|---|---|---|---|---|---|
| 20261018T200239625248Z | 546 | 537 PASS / 9 FAIL | 530 | 4 | 4 |
| 20261018T202131127599Z | 546 | 542 PASS / 4 FAIL | 530 | 4 | 4 |
| 20261018T212500022987Z | 554 | 554 PASS | 538 | 4 | 4 |
| 20261018T213443471189Z | 554 | 554 PASS | 538 | 4 | 4 |
| 20261019T001435805887Z | 571 | 570 PASS / 1 FAIL | 554 | 12 | 12 |
| 20261019T003019776183Z | 571 | 570 PASS / 1 FAIL | 554 | 12 | 12 |
| 20261019T004115354212Z | 571 | 571 PASS | 554 | 12 | 12 |
| 20261019T005558434174Z | 571 | 571 PASS | 554 | 12 | 12 |

- **4352 of 4352 command-bearing rows** carry `/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/runs/<stamp>/scratch` in `command` (the harness records the absolute `--path`). Verbatim first hit:
  `mechanic ['godot','--headless','--path','/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/runs/20261018T200239625248Z/scratch','--script']`
- **872 PASS lines** contain a host path; the 12 per r103-era run each carry the run's **own** stamp, e.g.
  `PASS save_roundtrip structured=true reopened=true values_match=true user_path=/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/runs/20261019T004115354212Z/xdg-data/godot/app_userdata/MechanicOneShotTest-20261019T004115354212Z/r57-save.json`

**Consequence [inf].** A stored receipt is **not byte-stable across runs** by construction; the 12 cases are
`save_roundtrip`, `save_process_{writer,reader,missing}` and the 8 `export_div_s0{2,3,4}_*` rows. Any
acceptance form that requires full-transcript byte-identity between two runs is unsatisfiable for these rows
unless the run stamp is normalized first. The absolute host path also makes the recorded `command` unusable
verbatim on any other host.

## §4 F3 — r103's "549 comparable rows / 542 byte-identical" is not reproducible from the stored bytes

`reports/round-103/r103-adjudicator.md:43-44` and `:77` claim *"cross-run stability: 549 comparable rows
r102↔r103, 542 byte-identical, 7 diffs = run-dir paths (5) + by-design print-fix lines (2)"*.
Measured with the census script, every reasonable comparability rule over the r102 run
`20261018T202131127599Z` vs the r103 run `20261019T004115354212Z` [obs]:

| rule | comparable | byte-identical | note |
|---|---|---|---|
| rows with `command`, keyed by case | **530** | 482 | |
| all rows, keyed by case | **546** | 486 | |
| command-bearing rows, keyed by PASS-line name (r101-comparator method) | **453** | 451 | |
| positional (index) over command-bearing rows | 530 | 465 | |

No rule yields 549 or 542. The nearest pair under run-stamp normalization is 546 comparable / 497 identical.
Two further [obs] facts make a conflation likely [inf]:
- **549 is a different quantity elsewhere in the same round**: `r103-scr4.md:255` projects
  *"CASES 536 → 536+13 (=549)"*, and r103 landed 552 CASES.
- **542 is that run's PASS-verdict count** (`Counter` over `20261018T202131127599Z` → `{'PASS': 542, 'FAIL': 4}`),
  not an identity count.

Wording verdict: the number pair is **not verifiable as stated**; the counting rule is unstated and no
stated-rule reading reproduces it. Either number may be right under an undisclosed rule — this seat cannot
confirm or refute it, only show that the published rule-free phrasing is not reproducible. Routed for r105
(verification round) or for a corrected footnote.

## §5 F4 — r104's own `res_uid_s01.gd` pins a project-name-dependent constant that the battery invalidates

**The mechanism (measured).** `ResourceUID.create_id_for_path(p)` is a hash that **includes the project
name**. Same directory, same script, same queried path, only `config/name` changed [obs]:

```
name=AlphaProbe   → create_id_for_path 5895645791453644569
name=AlphaProbeX  → create_id_for_path 6955841509840796941   (same dir, same res:// path)
name=AlphaProbe   → create_id_for_path 5895645791453644569   (restored → identical)
name=NameOne  (×2 distinct dirs) → 624454918949361878
name=NameTwo            → 4379528761313762603
```
Unrelated extra files, a renamed caller script, and moving the project directory do **not** change it
(control: b1/b2/b3 and `c1-moved` all returned `5895645791453644569`). So the input includes the project
name, not the project path.

**The harness changes exactly that field.** `corpus/fixtures/run_battery.py:2052-2053` [obs]:
```python
project_text = project_text.replace('config/name="MechanicOneShotTest"',
                                    f'config/name="MechanicOneShotTest-{stamp}"', 1)
```

**The fixture pins the pre-rename value.** `corpus/fixtures/res_uid_s01.gd:201-206` (sha256
`fdef4f3cf945531a916be3c247e1f471ae69f4c32ac6abaeefe077e7124756bc`, 259 lines) [obs]:
```
_p("cfp_res=%d cfp_res_text=%s cfp_res_matches_pinned=%s stable=%s" % [
    a, ResourceUID.id_to_text(a), _b(a == 8476142776992359011), _b(a == b)])
_p("cfp_user=%d cfp_user_matches_pinned=%s stable=%s user_registered=%s" % [
    ua, _b(ua == 4163091229239537790), _b(ua == ub), _b(ResourceUID.has_id(ua))])
```

**Measured in the battery-shaped project** (fixture copied to scratch, `config/name` renamed to
`MechanicOneShotTest-20261019T999999999999Z` exactly as the harness does), `--arm=createid` [obs]:
```
PASS res_uid_s01 createid cfp_res=1525762664572567523 cfp_res_text=uid://v0dc86neuait \
  cfp_res_matches_pinned=false stable=true cfp_res_registered=false \
  cfp_res_path_to_uid=res://e1_selfreg_probe.gd cfp_user=2833486841379459172 \
  cfp_user_matches_pinned=false stable=true user_registered=false \
  create_id_distinct=true create_id_unregistered=true cfp_text_roundtrip=uid://v0dc86neuait
```
Control, same fixture, original project name: `cfp_res=8476142776992359011 … matches_pinned=true`.
Output sha differs accordingly (`bedec8f5…` renamed vs `b683c7d8…` original).

**Why this is an exposure defect regardless of how the row is registered** [inf, two branches]:
- if the registered signature contains `cfp_res_matches_pinned=true`, the row **FAILs** in the battery —
  the token is absent from the real output (`classify_process` requires `signature in output`);
- if the signature omits the pin token, the row **PASSes with a false pin** — a receipt that prints
  `matches_pinned=false` while claiming PASS, i.e. exactly the "UID-census echo" failure mode C1 exists
  to catch.
Either way the pin as written cannot be true inside the battery. Corroborating exposure: `r104-E1.md`
(the owning seat's shard) contains **only the plan header — no measurement, no command, no bytes**, so the
pin's provenance is unrecorded and unreviewable at integration time.

## §6 F5 — E0's `create_id()` claim is contradicted by measurement and by E0's own fixture

`reports/round-104/r104-E0.md:33-35` claims [verbatim]:
> `create_id()` sampled n=32: all values **≥ 2^63** (min 432880470429673677, max 8291027300687686723) —
> outside the 63-bit range `text_to_id` accepts, so a minted id does not round-trip through
> `id_to_text`/`text_to_id` (unknown class, not asserted).

The claim is **internally self-contradictory and false as measured**:
- `2^63 = 9223372036854775808`; the cited minimum `432880470429673677` is ~21× smaller, so "all values ≥ 2^63"
  cannot hold for the very sample quoted [obs: the two numbers are in the same sentence].
- Independent n=512 sample (`/var/tmp/r104-C5/big/a.gd`): `min=30320009849551765 max=9201158012304641735
  negative_count=0 min_ge_2p63=false`, and `roundtrip_of_max=true text_len=19`. n=32 sample: `count_ge_2p63=0`.
- E0's own landed fixture prints the opposite of the derived conclusion [obs]:
  `PASS res_uid text … minted_positive=true minted_le_int64max=true minted_text_shape=uid minted_roundtrip=true …`
  (3× byte-identical, sha `e8a7e45a52f73725`, 379 lines).

So the shard's "does not round-trip" inference is wrong and its fixture already encodes the correct law
(`minted_roundtrip=true`). The fixture is right; the shard prose is stale or mis-typed. Worth a fold.

## §7 F6 — tracked regenerable artifacts: 1961 `.godot/` files, 117 `uid_cache.bin`, 2848 `.uid`, 1 `.pyc`

[obs] `git ls-files` (total tracked files) and class counts:

| class | tracked count | note |
|---|---|---|
| under `.godot/` | **1961** | editor caches, `filesystem_cache10`, `project_metadata.cfg` |
| `uid_cache.bin` | **117** | the exact artifact class C1 is probing |
| `*.uid` | **2848** | sidecars |
| `*.pyc` | **1** | `reports/round-102/mutations/__pycache__/r102-S3-verify.cpython-314.pyc`, **in HEAD** (`git cat-file -e HEAD:<path>` → present) |

`corpus/.gitignore` carries `**/__pycache__/` and `**/.godot/` but is **scoped to `corpus/`**; there is no
repo-root `.gitignore` (`ls .gitignore` → absent) [obs]. `git check-ignore -v` answers:
```
corpus/fixtures/__pycache__/x.pyc                        → corpus/.gitignore:17:**/__pycache__/   rc=0
reports/round-102/mutations/__pycache__/x.pyc            → rc=1  (NOT IGNORED)
corpus/live/r25-export-scout/.../.godot/uid_cache.bin    → rc=1  (NOT IGNORED — tracked, so ignore is moot)
```
`git status --porcelain` shows the tracked `.pyc` as ` D` (unstaged deletion) — it will enter history as a
deletion. The same class is being regenerated live: `reports/round-103/mutations/__pycache__/` and
`reports/round-104/mutations/__pycache__/` now hold unignored `.pyc` files created by r104 seats importing
r103 scripts (independently confirmed by `r104-sent1.md` §F2). Also [obs]: every battery run copies the
harness's own bytecode into its scratch tree (`run_battery.py:2043-2047` skips only `run_battery.py` and
dot-names) — 8 run dirs carry a 478–497 KB stale `run_battery.cpython-314.pyc`.

**Device-census exposure** [obs]: no r104 shard pins a joystick/device token — `grep -rn -E 'js[0-9]|joystick|gamepad|/dev/input' reports/round-104/` returns **only this shard's own axis text**. And no new
`res_uid*.gd` contains a device token.

## §8 Wording audit — ambiguous or unlabelled claims found (per-shard)

| # | location | claim | measured reality | verdict |
|---|---|---|---|---|
| W1 | `r104-scr2.md:4`, `r104-scr3.md:4` | "round 103 closed a322bce5 (rebased lineage)" | not an ancestor of HEAD; dangling reflog object (§2) | misleading citation |
| W2 | `r103-adjudicator.md:43-44,77` (carried into r104 context) | "549 comparable / 542 byte-identical" | 530/482 or 546/486 depending on rule; 549 also = a CASES projection, 542 = the run's PASS count (§4) | not reproducible |
| W3 | `r104-E0.md:33-35` | `create_id()` all ≥ 2^63, no round-trip | 0 of 544 sampled ≥ 2^63; round-trip true (§6) | wrong |
| W4 | `r104-E1.md` | 8 "MEASURED LAWS" in the fixture header attributed to `reports/round-104/r104-E1.md` | that shard is **plan-only**; it contains no command, no bytes | provenance missing |
| W5 | `r104-E0.md:5` | "Godot: pending probe" removed but "HOST uptime: (see below)" was left with no value for a while | current bytes now carry `uptime`; resolved | minor |
| W6 | all 34 r104 shards | `uptime` load average quoted as "load low"/"quiet host" | the quoted value is the **1-minute** average at a single instant inside a 48-seat swarm; the seat's own series ran 3.6 → 13.8 | inference stated as fact |
| W7 | `r104-scout.md:7` | "CASES count at HEAD — expect 552" | `ast` parse of HEAD: **552** | correct (confirmed) |
| W8 | `r104-connector.md:53` | `run_battery.py` sha256 `2af2bc841ccb…`, 5783 lines | `wc -l` = 5783 | correct (confirmed) |
| W9 | `r104-E0.md:33` | "outside the 63-bit range `text_to_id` accepts" | `text_to_id(id_to_text(v)) == v` holds for all sampled v ≤ int64 max | wrong premise (see W3) |
| W10 | r103-era "570 PASS / 0 FAIL ×2" vs stored 571 rows | counting semantics differ (554 receipts + 16/17 harness rows) | both readings coexist in `r104-scr5.md` §1.5 with the discrepancy disclosed | disclosed, not a defect |

Engine-version wording: the r103-crit5 §1 split (`.official` export banner vs `.arch_linux` editor banner)
is unchanged this round [obs: `godot --version` → `4.7.2.stable.arch_linux.ed1daf0bf`; exported-binary banner
`Godot Engine v4.7.2.stable.official.ed1daf0bf`]. Every r104 shard that names the engine quotes the editor
form; none is ambiguous, because none quotes the export banner.

## §9 Receipt-stability audit of the new r104 fixtures (independent scratch re-run)

All six landed fixtures copied to `/var/tmp/r104-C5/{proj2,w7run}` (battery-shaped: `run_battery.py`
excluded, `controls/pickup.tscn` staged, `config/name` renamed). Engine
`4.7.2.stable.arch_linux.ed1daf0bf`, `XDG_DATA_HOME`/`TMPDIR` redirected.

| fixture | sha256 (first 16) | lines | PASS print sites | abs-path leak in PASS format | 3× distinct output sha |
|---|---|---|---|---|---|
| `res_uid.gd` (E0) | `e8a7e45a52f73725` | 379 | 2 | 0 | 1 of 3 (`--arm=text`) |
| `res_uid_s01.gd` (E1) | `fdef4f3cf945531a` | 259 | 2 | 0 | 1 of 3 (`--arm=createid`, orig name) |
| `res_uid_s02.gd` (E2) | `551ecb76f0b9397c` | 290 | 2 | 0 | 1 of 3 × 8 arms |
| `res_uid_s03.gd` (E3) | `501f79288ee02d21` | 600 | 1 | 0 | 1 of 3 × 5 arms |
| `res_uid_s04.gd` (E4) | `7e3c637fe2a47c1a` | 476 | 1 | 0 | (not re-run; no arms parse) |
| `res_uid_w07.gd` (W7) | `f1ec8f8ede3ad675` | 303 | 3 | **1** | 3 of 3 (`--arm=builtin`) |

- **Zero absolute paths in any PASS format string** [obs, grep over all six files]. The fixtures'
  no-host-path claims are true.
- **`res_uid_w07.gd` `--arm=mkpng` prints a host path**: `PASS res_uid_w07 mkpng save=0 bytes=90
  import_exists=0 path=/var/tmp/r104-C5/rundir/scratch/w07_probe.png` — `ProjectSettings.globalize_path`.
  A receipt of this shape can never be byte-stable across roots [obs].
- **`res_uid_w07.gd` `--arm=builtin` is nondeterministic**: `create_id text=uid://bogaoielrrvma` /
  `…c068n1mqjsygv` / `…cu5f7xf30j7pl` on 3 consecutive runs; full-output sha 5/5 distinct. The fixture's
  own header does not claim byte-stability for this arm, but `res_uid.gd`/`res_uid_s01.gd`/`res_uid_s02.gd`
  headers **do** claim it, and those claims held for every arm I re-ran except s01's pinned-constant arm (§5).
- **Moving-target discipline**: `res_uid.gd`, `res_uid_s01.gd` and `res_uid_s02.gd` were all rewritten
  during this seat (s01 `d24bd3b2…` → `fdef4f3c…`; E0 374 → 379 lines; E2 309 → 290 lines). Any pin quoted
  before ~22:36 names different bytes. Integration must pin **final** bytes.

## §10 Unregistered fixtures — 28 `.gd` on disk with no CASES row

`ast`-parsed `CASES`: **552 rows / 79 distinct scripts**. On-disk `corpus/fixtures/**/*.gd` (excluding
`.godot`, `__pycache__`): **102** → **28 unregistered** [obs]. Classified by reference:

- **Genuinely orphaned (0 in-corpus referrers):** `export_launch_s01..s06.gd` (6), `controls/negative_test.gd`.
- **This round's deliverables, pending registration (0 referrers, correct):** `res_uid.gd`, `res_uid_s01..s04.gd`,
  `res_uid_w07.gd` (6). `res_uid_s03.gd` is listed because E3 landed it after my first census pass.
- **Helper/child scripts with in-corpus referrers (not orphans):** `baseline_actor.gd`(1), `causal_actor.gd`(1),
  `causal_pickup.gd`(1), `controls/input_route_receiver.gd`(3), `controls/pickup.gd`(5),
  `controls/scene_marker.gd`(8), `crash_exit_probe.gd`(2), `godot_error_probe.gd`(1), `pickup.gd`(5),
  `r97_scene_marker.gd`(4), `rb_watch.gd`(2), `save_process.gd`(1), `scene_marker.gd`(8),
  `stream_attribution_probe.gd`(1), `timeout_probe.gd`(1).
- The `export_launch_s0*.gd` orphan class is **pre-existing** (not created this round) and is reported
  independently in `r104-scr5.md` §1.6 — two seats agree [obs].

## §11 Labels

**Observation:** §1 pins; §2 sha/ancestry/reflog/diff outputs; §3 the census table, the verbatim command and
`user_path` receipts, the 12 per-run cases; §4 the four comparability rules and their counts; §5 the
`create_id_for_path` name-sensitivity matrix, the `run_battery.py:2052-2053` bytes, the fixture's pin lines,
and the renamed-vs-original receipts; §6 the n=512/n=32 samples and the fixture's `minted_roundtrip=true`
line; §7 all `git ls-files` counts, the three `check-ignore` answers, the 8 scratch `.pyc` copies; §8 the
grep censuses; §9 the sha/line/arm table and the three nondeterministic-output runs; §10 the `ast` counts.

**Inference (labelled):** §2 that `eff29d1d` is the later twin (from the diff direction); §3 that
full-transcript byte-identity is unsatisfiable for the 12 stamped rows; §4 that the 549/542 pair is a
conflation with the CASES projection and the run's PASS count; §5 that the s01 pin must either FAIL the row
or produce a PASS with a false pin (both branches shown, neither chosen); §6 that E0's prose is stale rather
than its fixture; §7 that the missing root `.gitignore` is the mechanism behind the recurring `reports/**`
bytecode strays; §8 W6 that "load low" is a single-instant 1-minute average.

**Unknown:** which registration (if any) the orchestrator picks for `res_uid_s01 createid`, and therefore
which of the two §5 branches binds; whether r103's 549/542 came from a rule this seat did not try (e.g. a
per-seat receipt directory rather than `verdicts.json`); whether `res_uid_s04.gd` has arms at all (its
`--arm=` grammar did not parse for me; not asserted); whether `res_uid_s03.gd`/`s04` rows are byte-stable
across the 2-run battery (not re-run here); whether a *different* Godot binary writes to `XDG_CONFIG_HOME`.

## §12 Boundaries, non-actions, scratch

- `corpus/fixtures/run_battery.py` **never executed** — parsed with `ast`/`grep` only. No shared file edited
  (`SCORECARD.md`, `LOG.md`, `SHONEN.md`, `PROVINCE.md`, `corpus/lessons/*`, `reports/round-10{1,2,3}/`
  untouched by this seat). No commit. Sibling lane `game-dev-3d-shokunin` never read or written.
- New files: this shard + `reports/round-104/mutations/r104-C5-exposure-census.py`.
- Scratch: `/var/tmp/r104-C5/` is a **plain directory tree, not a git worktree** ⇒ nothing to
  `git worktree remove`. No worktree was created by this seat.
- Every engine invocation was targeted `godot --headless --path /var/tmp/r104-C5/<proj> --script …` with
  `TMPDIR` and `XDG_DATA_HOME` redirected under the scratch root.
- Retained evidence store: `/var/tmp/r104-C5/{proj2,fx2,w7run,s01r2,s01r0,alpha,a4,a5,a6,b1..b3,c1-moved,
  n1..n4,big,ids,rundir}` + `builtin_{1,2,3}.out`, `s01_createid_{renamed,orig}.out`, `logs_mkpng.txt`.
- Re-runnable: `python3 reports/round-104/mutations/r104-C5-exposure-census.py` from the lane root
  reproduces §3, §4, §7 and §10 verbatim.
