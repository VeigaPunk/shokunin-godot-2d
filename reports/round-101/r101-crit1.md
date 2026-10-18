# r101-crit1 — Attack C1 receipts (CRIT-1)

Plan (5 lines):
1. Recon: read `run_battery.py` classify/execute semantics + C1 sibling shards (E0/E1..E17) + r100-critic F2; record uptime.
2. Ground truth: real headless export under `/var/tmp/r101-CRIT-1/` (PCK + ZIP) so every attack is patched against *measured* production bytes, not a guess.
3. Build the four assigned attack classes (fake PCK magic via header patch, size>0 vacuity, census echo-pins, forged receipt lines) plus the partial-artifact and name-forge variants they expose.
4. Measure accept/reject of the *fragile* check shape (magic-only, size>0, substring signature) vs the *required* discriminator; record exact commands + observed bytes.
5. Write per-attack discriminator table (what each C1 row must carry); keep shard <400 lines.

Load context (recorded once, at seat start):
```
$ uptime
 16:21:20 up 1 day, 16:21,  1 user,  load average: 40.10, 20.91, 13.51
```
Godot `4.7.2.stable.arch_linux.ed1daf0bf`; templates `~/.local/share/godot/export_templates/4.7.2.stable/` (`linux_release.x86_64` = 73,519,416 B present). Host shared with the game-dev-3d r104 swarm; loadavg was 40.10 at seat start and every run below returned under the same contention (no run timed out or was reaped).

Scratch-path caveat (observed, load-bearing): `/tmp` is a 16 GB tmpfs at 80 % (`df`: `16G 13G 3.1G 80%`); even a 4,096-byte write died with `OSError: [Errno 122] Disk quota exceeded`, so all attack trees live under **`/var/tmp/r101-CRIT-1/`**. E1/E5's plan to build scratch under `/tmp` will hit the same EDQUOT intermittently.

**Axis touched:** C1 receipt falsifiability (what a row can and cannot see). Every attack below is *observed* on real Godot bytes; inferences are labelled.

---

## 0. Bottom line

The four assigned attack classes are all live against the *fragile* row shapes:

| attack | fragile shape it defeats | measured verdict of fragile shape | required discriminator (short form) |
|---|---|---|---|
| A1 fake PCK magic (header patch) | `magic == b"GDPC"` and/or `size > 0` | **PASS** for 4 KiB and 1 MiB zero files with `GDPC` written at offset 0 | full v4 header + table walk + per-entry md5 + `walk_end == file size` + exact version quad + artifact sha256 |
| A2 size>0 vacuity | `os.path.getsize(p) > 0` | **PASS** for a 4-byte `GDPC` file; also PASS for a 524,288-byte **partial** ELF left by an interrupted export | structural validation of the artifact, exact expected filename, output-dir product set equality |
| A3 census echo-pin | `signature in output` | **PASS**: measuring script and hardcoded-echo script produce **byte-identical** transcripts (sha256 `10dbcdf6…`, both rc 0) | negative-control arm in the same row (corrupted artifact ⇒ rc 2 + `md5_bad=1`), plus artifact sha inside the pinned line |
| A4 forged receipt line | `signature in output` (substring) | **PASS**: appended alt-scene receipt, duplicated pinned line, appended line after a 3-line contiguous pin | full-transcript pin + external exact-sequence audit; substring tests cannot see appends (T2/T3/T5) |

Additional measured gaps a C1 row must plan for:

* **Exit code is not a discriminator for pack runs**: garbage-magic, version-99 and newer-engine packs all return **rc 0** (A1/A4); a count→1 patch returns **rc 0 with empty stderr and no marker** (a silent "success"); a count→517 patch is *tolerated* — rc 0, empty stderr, marker printed (only a structural walk rejects it).
* **Run receipt alone is blind to payload corruption** of files the scene does not read: a 1-byte flip in `sub/note.txt` left the old receipt byte-identical (rc 0, stderr 0). With the scene printing `note_md5` of a pack file, the receipt flips (`3555bc34…` → `1898785f…`) — causal coupling is the fix.
* **Name census is forgeable under a md5 walk**: renaming the `sub/note.txt` table entry to `main.gdc` (payload+md5 untouched) passes `count=17 md5_bad=0 tail=0`, rc 0 (A5). Only exact name-multiset equality catches it.
* **ZIP container sha256 is not deterministic** (4 timestamp bytes differ between two exports); the central-directory census and the `out.pck` member bytes are.

---

## 1. Ground truth: the real artifact every attack is patched against

Command (observed; `--export-pack` is the PCK-only path — `--export-release` to a `.pck` target instead tries to copy the 73 MB template and failed on the quota-starved tmpfs):

```
$ godot --headless --path /var/tmp/r101-CRIT-1/proj --export-pack "Linux/X11" /var/tmp/r101-CRIT-1/attack/out.pck
RC=0
$ stat -c %s attack/out.pck; sha256sum attack/out.pck
5332
1bacf493e2616158c28bebb06f023a552160ce6a17c8e51a6cf8b94679095af8
```

Header/table (parsed from raw bytes; layout measured, not assumed):

```
magic=GDPC ver=4 engine=4.7.2 flags=2 file_base=112 table_ofs=4144 count=17
entries=17 md5_bad=0 walk_end=5332 eof=5332 tail=0
```

17 entry names (grouped; the `.godot/…` entries are listed last): `alt.gdc`, `alt.gd.remap`, `alt_main.tscn.remap`, `icon.svg`,
`icon.svg.import`, `main.gdc`, `main.gd.remap`, `main.tscn.remap`, `project.binary`,
`sub/note.txt`, `sub/res.tres.remap`, `.godot/exported/<id>/export-…-alt_main.scn`,
`.godot/exported/<id>/export-…-main.scn`, `.godot/exported/<id>/export-…-res.res`,
`.godot/global_script_class_cache.cfg`, `.godot/imported/icon.svg-…ctex`,
`.godot/uid_cache.bin`. The remap contract is visible: source `.gd/.tscn/.tres` absent,
`.remap` + binary peer (`.gdc/.scn/.res`) present.

`--main-pack` run (observed):

```
$ godot --headless --main-pack attack/out.pck --quit-after 3
RC=0 ; stdout=158 B ; stderr=0 B
Godot Engine v4.7.2.stable.arch_linux.ed1daf0bf (2026-08-17 01:18:38 UTC) - https://godotengine.org

MAIN_SCENE_RECEIPT scene=main marker=CRIT1_MAIN frames=0
```

Alt-scene pack (`project.godot` main_scene → `alt_main.tscn`), same command:
`156 B`, `MAIN_SCENE_RECEIPT scene=alt marker=CRIT1_ALT frames=0` — the swap is observable in the receipt.

Determinism (observed): two exports of the same project state are byte-identical
(`out.pck` == `out2.pck` == `out-copy2.pck`, sha `1bacf493…`, 5332 B), **but** a copy whose
`.godot/exported` cache was deleted and re-imported exports different `.scn` payload bytes
(`out-copy.pck` sha `09291813…`, same 5332 B, 40 differing bytes: 8 payload bytes inside the
two `.scn` bodies plus their two 16-byte stored md5s).
So a sha256 pin is valid only for a fixed project state; it is not a cross-state invariant.

ZIP export (observed): `--export-release "Linux/X11" <dir>/out.zip` → 28,420,542 B, 2 entries:
`out.pck` (5332 B, CRC `0x9ce69c66`, member sha `1bacf493…` = the standalone PCK) and
`out` (73,519,416 B, CRC `0x272fec0c`, member sha `d9f79ab8…`). Two exports differ in
sha256 (`75c9ad45…` vs `02b9a6b3…`) and in exactly **4 bytes** at decimal offsets 11, 2618,
28420431, 28420484 (values octal `035`→`054`) — the DOS time fields of the two local
headers + their central directory records. Member names, CRCs, sizes and member bytes are identical.

---

## 2. Attack matrix (all observed)

Harness semantics that define "fragile" (read from `corpus/fixtures/run_battery.py`):
`classify_process` lines 1725–1742 = `code == expected_exit and signature in output and
no unexpected "ERROR:" line and no "SCRIPT ERROR:"/"Parse Error:"`; generic branch
lines 2270–2278 calls it with the CASES signature. The only artifact-level check in the
existing export row is `export_path.stat().st_size > 0` (line 1880), gated by
`"[ DONE ]"` and `"savepack"` substrings (1878–1879).

### A1 — fake PCK magic via header patch

| variant | bytes | size | fragile: magic-only | fragile: size>0 | full walk | engine `--main-pack` |
|---|---|---|---|---|---|---|
| 4 KiB zeros + `GDPC`@0 | `53ccaa78…` | 4096 | PASS | PASS | FAIL `table_ofs 0 outside file` | rc 0; stderr 206 B `ERROR: Pack version unsupported: 0.`; no marker |
| 1 MiB zeros + `GDPC`@0 | `f7a856c6…` | 1048576 | PASS | PASS | FAIL (same) | (not run) |

**Required discriminator:** reject magic-only. Parse `ver`, engine quad, `file_base`,
`table_ofs`; walk `count` entries; recompute each payload md5 from raw bytes; require
`walk_end == file size` (`tail == 0`). The A1 artifact fails at the first structural step.

### A2 — size>0 vacuity

| variant | size | magic | full walk | note |
|---|---|---|---|---|
| 4-byte `GDPC` | 4 | PASS | FAIL `bad magic/too short` | defeats `magic==GDPC and size>0` |
| 0-byte file | 0 | FAIL | FAIL | defeats `size>=0` only |
| **partial export artifact** | 524288 | ELF `7f454c46` | n/a | measured: `ulimit -f 512` during `--export-release` killed Godot with SIGXFSZ (`rc 153`), left `out.x86_64-tSeOnA` (524,288 B, no `savepack` in log; one `[ DONE ]` from `first_scan_filesystem` exists) |

**Required discriminator:** never assert `size > 0` as the artifact claim. Assert
(a) `rc == 0`, (b) the **exact expected product path** exists (the partial file's temp
name `out.x86_64-tSeOnA` is not the requested `out.x86_64`), (c) the output dir's product
set equals the expected set (no temp/partial leftovers), (d) the artifact validates
structurally (PCK walk, or ELF magic + appended-PCK walk for embedded exports).

### A3 — census echo-pin

Two standalone `SceneTree` scripts were run against the same PCK:

* `census_measure.gd` — opens the PCK, walks the header/table, hashes every payload (HashingContext MD5), hashes the whole file (SHA256), prints one `CENSUS …` line.
* `census_echo.gd` — never opens a file; prints the same line as a constant.

```
$ godot --headless --path proj --script res://census_measure.gd -- /var/tmp/…/out.keep.pck
RC=0  CENSUS magic=GDPC ver=4 4.7.2 count=17 md5_bad=0 tail=0 pck_sha256=1bacf493…
$ godot --headless --path proj --script res://census_echo.gd -- /var/tmp/…/atk-a3-payload-flip.pck
RC=0  CENSUS magic=GDPC ver=4 4.7.2 count=17 md5_bad=0 tail=0 pck_sha256=1bacf493…
$ cmp (their transcripts)  -> identical, sha256 10dbcdf6f3dbdc226876bb1eae89d8f2258df3330d76dc62067968983e4c5977
```

So a row that pins the census line (even the whole line, with the true sha) **cannot**
separate a measuring fixture from an echoing one, and the echo output is independent of
the artifact it is handed.

**Required discriminator:** the row must be *falsifiable in the same run* — a negative
arm where the fixture itself corrupts a copy of the artifact and the case pins the
**failure** receipt (measured: rc 2, `md5_bad=1`, sha `b49e548c…` for a 1-byte flip in
`sub/note.txt`). A constant echo cannot produce two different (sha, md5_bad) pairs tied
to real bytes without doing the measurement. Complement: pin the full line (not a prefix —
`CENSUS magic=GDPC ver=4` prefix still passes a fabricated sha, measured T6d).

### A4 — forged receipt lines (`classify_process` extracted verbatim via AST, lines 1725–1742)

| id | transcript shape | pinned signature | classify | external audit |
|---|---|---|---|---|
| T1 | real `--main-pack` stdout | marker line | **PASS** | — |
| T2 | real stdout + appended `MAIN_SCENE_RECEIPT scene=alt …` | alt marker | **PASS** | `whole_line_hits(alt)=1`; +2 captured lines vs real |
| T3 | real stdout + duplicated marker line | marker | **PASS** | `whole_line_hits=2` (only this sees it) |
| T4 | 3-line contiguous pin, line inserted mid-block | 3-line block | **FAIL** | insertion breaks contiguity |
| T5 | 3-line contiguous pin, line appended after block | 3-line block | **PASS** | captured 4 lines vs pinned 3 |
| T8 | real stdout + appended `ERROR: forged…` | marker | **FAIL** | harness `ERROR:` guard works |
| T9 | flipped pack, receipt has other `note_md5` | content-coupled line | **FAIL** | content coupling works |

**Required discriminator:** a substring pin cannot reject appended lines (T5/T2) and the
harness cannot reject duplicates (T3). The row must (a) pin **one canonical receipt line
containing content-derived digests** (so the value cannot be right without the bytes),
(b) emit exactly one receipt line per run so the external audit is trivial, and (c) the
**external reviewer/critic audit** must compare the captured `output` list to the pinned
sequence for exact length+order+equality (`whole_line_hits == 1`, no extra lines).
In-harness, T2/T5 are irreducible; only the round's verifier layer closes them.

### A5 — name-forge under the md5 walk (bonus, measured)

Renaming the `sub/note.txt` table entry to `main.gdc` (12-byte slot, payload and stored
md5 untouched) yields `count=17 md5_bad=0 tail=0`, census rc 0, and the pack still runs
(`rc 0`, marker present). It **passes** the whole structural census. A2's empty pack
prints `magic= ver=0 0.0.0 count=0 md5_bad=0 tail=0` — two conjuncts are vacuously true.

**Required discriminator:** exact **name multiset** equality (sorted list + duplicates
rejected), not membership and not count. Pin the full expected name set (including
`.remap`↔binary pairs and subdirectory paths with `/`), and require `magic == "GDPC"`,
`count == N`, `ver == 4`, `4.7.2` as conjuncts so an empty file cannot satisfy the rest.

---

## 3. Per-scenario discriminator the C1 rows must carry

| # | C1 scenario | measured facts it must pin | exact discriminator (what a forgery must not survive) |
|---|---|---|---|
| 1 | base PCK export + magic/size | PCK `1bacf493…`, 5332 B, `ver=4`, `4.7.2`, `count=17`, `tail=0`, `md5_bad=0` | full walk + exact sha + **negative arm** (1-byte flip ⇒ `md5_bad=1`, rc 2). Never magic-only / size>0 |
| 2 | zip export + census | 28,420,542 B; entries `out`, `out.pck`; CRCs `0x272fec0c`, `0x9ce69c66`; member `out.pck` sha `1bacf493…` | raw-byte central-directory census (EOCD offset/size, 2 names, CRC32 recomputed from payload, sizes, method) + **cross-artifact identity** `zip member out.pck sha == standalone PCK sha` (measured equal). Not container sha |
| 3 | determinism sha256 ×2 | same-state exports byte-identical (`1bacf493…` ×3); re-imported copy differs (40 bytes: 8 payload + two 16-byte `.scn` md5s) | equality of two exports **in the same run/state** only; state qualification recorded. ZIP: pin member sha + CD census, never the 4 timestamp bytes |
| 4 | main-scene swap + `--main-pack` run receipt | default pack → `scene=main marker=CRIT1_MAIN frames=0`; alt pack → `scene=alt marker=CRIT1_ALT frames=0`; both rc 0, stderr 0 B | two-arm row (both packs in the run) + `pck_sha256` in the receipt + content digest; a forged appended alt receipt passes substring (T2), so add the external exact-sequence audit |
| 5 | resource remap/UID census | 17 names incl. `.gd.remap`+`.gdc`, `.tscn.remap`+`.scn`, `.tres.remap`+`.res`, `uid_cache.bin` | exact name-multiset equality (A5 forge passes md5 walk) + per-entry payload md5 vs stored + source/remap absence pairs |
| 6 | include/exclude filter | `sub/note.txt` present (include `*.txt`); `sub/x.secret` absent though on disk (exclude `*.secret`) | absence asserted over the **raw name table** (not a pre-filtered list); negative arm with the filter flipped must change the census |
| 7 | unknown-preset refusal | rc **1**; `ERROR: Invalid export preset name: NoSuchPreset.`; out dir **empty** | rc + exact error line + empty product dir + no artifact path. Do not accept a generic `ERROR:` line |
| 8 | templates-missing error class | *not measured by this seat* (E8 owns it; **unknown**). Adjacent measurement: template copy interrupted by `ulimit -f` ⇒ rc 153, partial 524,288 B ELF, no `savepack` | pin the error **class text** + rc + **artifact absent/partial rejected**; a failed export that leaves a nonempty file must not satisfy the row (A2 partial artifact) |
| 9 | subdirectory census | `sub/note.txt` (included), `sub/res.tres.remap`; path strings keep `/` | exact names with subdirectory prefixes (no flattening), payload md5, name-multiset equality |
| 10 | icon/uid census | `icon.svg`, `icon.svg.import`, `.godot/imported/icon.svg-…ctex`, `.godot/uid_cache.bin`, `project.binary` | exact name set incl. import companion + payload md5 of `icon.svg` vs the source file; a name-only presence check is forgeable (A5) |
| 11 | `--main-pack` launch + `--quit-after` frame receipt | rc 0, stderr 0 B, `frames=0` from `Engine.get_process_frames()` inside the pack, marker line, 158/200 B stdout | rc 0 **and** marker present (count→1 patch: rc 0, stderr 0, **no marker**) + content digest + artifact sha; exit code alone is vacuous (A1/A4 all rc 0) |

---

## 4. Notes for the C1 authors (one line each)

* Scratch under `/tmp` EDQUOTs even at 4 KiB (observed); prefer the battery run dir or `/var/tmp`, and never treat a leftover partial artifact as success.
* `--export-pack <preset> <path>.pck` is the PCK-only path; `--export-release` to `.pck` writes the executable-then-pack product and needs the 73 MB template.
* PCK v4 as measured: `magic@0`, `u32 ver@4`, `u32 4,7,2@8`, `u32 flags@20`, `u64 file_base@24`, `u64 table_ofs@32`; table = `u32 count` + entries `u32 path_len, path, pad4, u64 ofs, u64 size, md5[16], u32 flags`; walk end == EOF.
* Engine tolerances (observed): garbage-magic/version-99/newer-engine (9.9.9) → rc 0 + `ERROR:` on stderr (no marker); count-517 → rc 0, empty stderr, marker printed (tolerated); count-1 → rc 0, empty stderr, **no marker**; file_base patch → rc 0 + corrupted-project ERROR; executing-code flip → rc 134 + `Error decompressing GDScript tokenizer buffer`. Only payload corruption of unread data is invisible to the run.
* A row that pins only what the fixture prints is an echo-pin; every census row needs a same-run corrupted-input arm.

---

## 5. Evidence index (scratch, not in repo)

* `/var/tmp/r101-CRIT-1/proj/` — scratch project (`project.godot`, `main.tscn`, `alt_main.tscn`, `icon.svg`, `sub/`, `export_presets.cfg`, `census_measure.gd`, `census_echo.gd`).
* `/var/tmp/r101-CRIT-1/attack/out.keep.pck`, `out3.pck`, `alt.pck`, `atk-*.pck`, `z1/out.zip`, `z2/out.zip`, `mainpack.*.out/err`, `content.*.out/err`, `census.*.out`, `negcontrol.*.out`.
* Mutation scripts (in repo, this seat's files): `reports/round-101/mutations/r101-crit1_attacks.py`, `reports/round-101/mutations/r101-crit1_forge.py`.

**Observation vs inference vs unknown**

* *Observed*: every byte count, sha256, rc, stderr size, engine tolerance row, classify verdict in §1–§4.
* *Inference*: that the same partial-artifact shape applies to the templates-missing class (scenario 8) — the exact error text for a genuinely missing template dir was not measured here.
* *Unknown*: whether Godot's ZIP writer can be made deterministic via a preset option (not probed); whether `--export-release` to a `.zip` target on an idle host still emits the 4 timestamp bytes (the non-determinism is structural in ZIP, so almost certainly yes).

No tracked file was edited; the two mutation scripts and this shard are the only repo writes. `run_battery.py`, CASES/registry files, `SCORECARD.md`, `LOG.md`, `SHONEN.md`, `PROVINCE.md` were not touched; the battery was never run.
