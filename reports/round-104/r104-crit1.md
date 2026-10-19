# r104-crit1 — C1 attack seat: UID-census echo / cache-identity spoof / remap forgery / collision miss

KEY=C1 (attack C1 receipts). Lane `game-dev-2d-shokunin`, round 104 (amended p4, devin fallback).
Host at seat open (observation): `uptime` = `22:29:42 up 1 day, 22:29, 1 user, load average: 3.77, 2.11, 1.84`
(`godot --version` → `4.7.2.stable.arch_linux.ed1daf0bf`). Load was 9.6 by the last matrix run — a
sibling lane (game-dev-3d) is hands-off and was never touched. `/tmp` carries EDQUOT; all scratch is
under `/var/tmp/r104-crit1/`. No git commit; no shared file edited; `run_battery.py` never executed;
no git worktree created (nothing to remove). Repo writes by this seat are only the two files under
`reports/round-104/mutations/` plus this shard.

## Plan (as executed)
1. Recon the goal contract Amendments, r103 receipts, battery launch shape, and the `res_uid*` fixtures.
2. Build an independent ground-truth rig (own project, own cache parser) so every UID claim is
   re-derivable from bytes without trusting a fixture's printed census.
3. Probe the four mandated attack classes headless on `/var/tmp/r104-crit1/`.
4. Turn the probes into a reproducible 14-shape attack matrix (one fresh project per shape) with an
   expected/observed pair and a verdict per shape.
5. Emit the required discriminators and verdicts; leave mutations/scripts for the orchestrator.

## 0. The surface under attack (observation)

The battery copies `corpus/fixtures/` into a fresh scratch project per run (`run_battery.py:2043-2049`)
and launches each case as
`godot --headless --path <scratch> --script res://<fixture>.gd -- <flags>` (`:2230`, 8 s timeout).
No `res_uid*` fixture exists at HEAD in `corpus/fixtures/` other than the siblings' *uncommitted*
`res_uid.gd`, `res_uid_s01..s04.gd`, `res_uid_w07.gd` (sha256 recorded in §7) and **none of them is
registered in `run_battery.py`** (`grep -n "res_uid" corpus/fixtures/run_battery.py` → no output; CASES
count 400 at read time). So the receipts C1 must attack are, at seat time, *claimed but not pinned*.

On-disk UID state in a fresh project (all produced by this seat's own scratch rig):
- `<name>.gd.uid` sidecar: exactly `uid://<base32-ish>\n`, one per scanned script.
- `<asset>.import`: a `[remap]` block carrying `uid="uid://…"`, `path="res://.godot/imported/<hash>.ctex"`.
- `.godot/uid_cache.bin`: `u32 record_count`, then `record_count` × (`u64 id`, `u32 path_len`,
  path bytes). Header is a COUNT, not a version (independently confirmed: 1 row → `01000000`,
  2 rows → `02000000`, 10 rows → `0a000000`; `reports/round-104/mutations/r104-crit1_driver.py`).
- `.godot/editor/filesystem_cache10`: the editor's own scan state, one line per asset carrying the
  same id; it short-circuits a rescan when the tree is unchanged.

## 1. Ground-truth laws (observation, one-shot rig `/var/tmp/r104-crit1/gt/proj`)

Commands were `godot --headless --path . --script res://<probe>.gd` and
`godot --headless --path . --import` / `--editor --quit`; each row below is the verbatim engine output
of one such run.

- **L1 the cache is the runtime authority; sidecars are not read at runtime.** With the cache intact,
  rewriting `res_a.gd.uid` to `uid://zzzzzzzzzzzzz` changes nothing:
  `R1 path=res://res_a.gd uid=6171864013913705472 txt=uid://ct6xx0tlatrd5 back=res://res_a.gd`.
- **L2 deleting `.godot/uid_cache.bin` zeroes the whole lattice.** Every
  `ResourceLoader.get_resource_uid` → `-1`, `ResourceUID.has_id` false, and a plain `--script` run does
  **not** regenerate the file (`ls` → No such file). `--import` / `--editor --quit` does rebuild it
  (4 rows → 10 rows including the probe scripts).
- **L3 the sidecar is the importer's input and is barely validated.** Forcing a rebuild with a
  hand-written sidecar (`rm -rf .godot; --import`):
  | sidecar text | resulting id | note |
  |---|---|---|
  | `uid://zzzzzzzzzzzzz` | 6128179328542129927 | accepted; the 'z's are *valid* base-32 digits (my "malformed" label was wrong) |
  | `uid://short` | **24345957** | accepted; length unchecked, tiny ids mintable |
  | `uid://!!!!!!!!!!!!!` | `-1` | non-alphabet chars → path unregistered |
  | `not-a-uid` | `-1` | rejected |
  | `` (empty) | `-1` | rejected |
  | `uid://ct6xx0tlatrd5` (no trailing newline) | 6171864013913705472 | newline optional |
- **L4 collision = silent eviction of one path.** Two sidecars carrying the same uid text →
  `WARNING: UID duplicate detected between res://beta.gd and res://alpha.gd.` (stderr, the *only*
  diagnostic) and the cache keeps **one** record; the loser then answers `-1`:
  `R7 path=res://res_a.gd uid=-1 back=n/a has=n/a` / `R7 path=res://res_b.gd uid=4304914206904813609`.
  Order law (clean 2-step rig): scanning alpha first then beta leaves **beta** as the winner
  (`ORD path=res://alpha.gd uid=-1 back=n/a`). Re-scanning an unchanged tree is idempotent, and
  **removing the winner's sidecar does not give the loser its id back** (still `alpha uid=-1`).
- **L5 load-cache modes.** Scripts (`.gd`): `CACHE_MODE_IGNORE` and `CACHE_MODE_REPLACE` both return
  the **cached** object (`R2 ignore same_as_a=true`, `R2 replace same_as_a=true`). Non-script resources
  (`.tres`, imported `.ctex`): `CACHE_MODE_IGNORE` returns a *fresh* object
  (`R3 reuse_same=true ignore_same=false ignore_path=res://data_a.tres`), `CACHE_MODE_REPLACE` returns
  the cached one (`replace_same=true`), and `set_meta` on the cached object is visible after a plain
  reload (`meta_after_reload=true`).
- **L6 `.import` remap.** `load("res://tex_red.png")` → `class=CompressedTexture2D`,
  `resource_path=res://tex_red.png` (the *source* path, not the `.ctex`).
  `ResourceLoader.exists` → `png=true`, `import=false`, `dest(.ctex)=true`, `missing=false`.
  Loading `res://tex_red.png.import` itself → `ERROR: No loader found for resource:
  res://tex_red.png.import (expected type: unknown)` → null.
- **L7 remap-missing has two distinct classes.** (a) dest `.ctex` deleted:
  `exists=true` but load fails (`ERROR: Unable to open file: …ctex`, `ERROR: Failed loading resource:
  res://tex_red.png`) → null; the uid is still reported. (b) `.import` deleted:
  `exists=false` and `ERROR: No loader found for resource: res://tex_red.png` → null.
- **L8 `ResourceUID` mutations are volatile.** `add_id`/`set_id`/`remove_id` change the in-process map
  only; after a run that did all three, `cmp .godot/uid_cache.bin <baseline>` → **SAME**. `remove_id`
  then `get_resource_uid` → `-1` in-process, cache row intact.
- **L9 malformed / hostile inputs are not errors.** `text_to_id("uid://")=0`, `text_to_id("")=-1`,
  `text_to_id("uid://<invalid>")=-1`; `has_id(-5)`/`has_id(INT64_MAX)` → false; `has_id(0)` → false;
  `id_to_text(-1)` → `uid://<invalid>`. `add_id` twice logs
  `Condition "unique_ids.has(p_id)" is true.` and keeps the FIRST path.
- **L10 `ResourceSaver.save` does not register a UID.** Saving `res://saved_x.tres` returns 0, creates
  the file (51 B) but **no `.uid`**; `get_resource_uid` → `-1` in that process and in a second process.

## 2. Attack matrix (14 shapes, reproducible)

Driver: `reports/round-104/mutations/r104-crit1_driver.py` (sha256 `6935ac61…`);
reader fixture: `reports/round-104/mutations/r104-crit1_read.gd` (sha256 `ff8756e2…`).
Command: `python3 reports/round-104/mutations/r104-crit1_driver.py` (root `/var/tmp/r104-crit1/matrix`,
override with `R104_CRIT1_ROOT`). Full captured output: `/var/tmp/r104-crit1/out/matrix-final.txt`
(111 lines). Two consecutive full runs differ in **zero** `=== SHAPE`/`obs` lines (`diff` → IDENTICAL),
and the minted ids are stable because they are derived from the sidecar text.

```
=== SHAPE S0_baseline : AS_EXPECTED
   obs    census        CRIT1 census alpha.gd=803467965278618112 beta.gd=72315778293730335 tex.png=7070736749366049730
   obs    ident         CRIT1 ident reuse_same=1 ignore_same=1 post_reuse_same=1
   obs    remap         CRIT1 remap load_ok=1 class=CompressedTexture2D path=res://tex.png exists_png=1 exists_import=0 uid=7070736749366049730
   obs    collision     CRIT1 collision alpha=803467965278618112 beta.gd=… same_id=0 alpha_resolves=res://alpha.gd beta_resolves=res://beta.gd
=== SHAPE A1_sidecar_uid_collision : AS_EXPECTED
   obs    census        CRIT1 census alpha.gd=-1 beta.gd=72315778293730335 tex.png=7070736749366049730
   obs    engine_warning ['WARNING: UID duplicate detected between res://beta.gd and res://alpha.gd.']
   data   cache_ids     {'res://beta.gd': …, 'res://tex.png': …}          loser ['res://alpha.gd']
=== SHAPE A2_import_uid_collision : AS_EXPECTED
   obs    census        CRIT1 census alpha.gd=803467965278618112 beta.gd=-1 tex.png=7070736749366049730
   obs    collision     CRIT1 collision alpha=803467965278618112 beta=-1 same_id=0 alpha_resolves=res://alpha.gd beta_resolves=<none>
   obs    engine_warning []                                              # incremental reimport is SILENT
   data   cache_ids     {'res://alpha.gd': 803467965278618112, 'res://tex.png': 7070736749366049730}   # beta gone
   data   tex_rows      [72315778293730335, 7070736749366049730]         # TWO rows for res://tex.png
=== SHAPE A3_cache_id_swap : AS_EXPECTED
   obs    census_line   CRIT1 census alpha.gd=72315778293730335 beta.gd=803467965278618112 tex.png=…
   data   sidecars      ['uid://alphaaaaaaaaa', 'uid://bbbbbbbbbbbb']     # sidecar texts unchanged
=== SHAPE A4_cache_collision : AS_EXPECTED
   obs    census        CRIT1 census alpha.gd=803467965278618112 beta.gd=803467965278618112 tex.png=…
   obs    collision     CRIT1 collision alpha=… beta=… same_id=1 alpha_resolves=res://beta.gd beta_resolves=res://beta.gd
   data   cache_after   [[803467965278618112,'res://alpha.gd'], [803467965278618112,'res://beta.gd'], …]
=== SHAPE A5_cache_ghost_path : AS_EXPECTED
   obs    census_line   CRIT1 census alpha.gd=-1 beta.gd=… tex.png=…
   data   cache_after   {'res://ghost_never_created.gd': 803467965278618112, …}   ghost_on_disk False
=== SHAPE A6_sidecar_garbage : AS_EXPECTED     # alpha.gd=-1, no cache row
=== SHAPE A7_sidecar_short_token : AS_EXPECTED  # alpha.gd=24345957
=== SHAPE A8_cache_deleted : AS_EXPECTED
   obs    census        CRIT1 census alpha.gd=-1 beta.gd=-1 tex.png=-1
   obs    remap         CRIT1 remap load_ok=1 class=CompressedTexture2D path=res://tex.png … uid=-1
   data   regenerated   False
=== SHAPE A9_remap_dest_missing : AS_EXPECTED   # exists_png=1, load_ok=0
=== SHAPE A10_remap_import_missing : AS_EXPECTED # exists_png=0, load_ok=0
=== SHAPE A11_sidecar_overrides_cache_after_rescan : AS_EXPECTED
   obs    before        CRIT1 census alpha.gd=803467965278618112 beta.gd=… tex.png=…
   obs    after_forge   CRIT1 census alpha.gd=803467965278618112 beta.gd=… tex.png=…   # unchanged: cache wins
   obs    after_scan    CRIT1 census alpha.gd=-1 beta.gd=… tex.png=…                  # full rescan re-decides
   obs    engine_warning ['WARNING: UID duplicate detected between res://beta.gd and res://alpha.gd.']
=== SHAPE A12_path_move_stale : AS_EXPECTED
   obs    census_line   CRIT1 census alpha.gd=803467965278618112 beta.gd=… tex.png=…   # file renamed, uid alive
   data   cache_after_plain_run {…'res://alpha.gd': 803467965278618112…}   # dead path persists
   data   cache_after_rescan    {'res://alpha_moved.gd': 1184013101569247247, …}       # new path, NEW id
=== SHAPE A13_uid_reference_anti_echo : AS_EXPECTED
   obs    lookup_lines  ['CRIT1 lookup uid://alphaaaaaaaaa -> res://beta.gd',
                         'CRIT1 lookup uid://bbbbbbbbbbbb -> res://alpha.gd']
shapes_run=14 unexpected=0
```

Two independent measurements corroborate A13 outside the matrix (gt rig, forged cache):
`R13 load(uid://ct6xx0tlatrd5) -> res://res_b.gd` while the sidecar `res_b.gd.uid` says
`uid://b2llkqc5dkvl6`; and a forged id `999999999999` is honoured by three consecutive fresh
processes (`R1 path=res://res_a.gd uid=999999999999 txt=uid://tbli2bd4 back=res://res_a.gd`), with
`ResourceUID.id_to_text(999999999999) = uid://tbli2bd4` — the cache fully determines id↔text.

## 3. The four required discriminators

- **D1 UID-census echo — PASS (no echo).** The census is not read back from a prior receipt: the
  driver independently parses `.godot/uid_cache.bin` with its own struct reader and the numbers agree
  with the engine's (`S0 data cache_ids` vs `S0 obs census`), and the engine's own `uid://` lookup
  follows a byte-forged cache in the *opposite* direction from the sidecar text (A13, R13). A row that
  echoed a stored census would keep the sidecar direction. Residual: the census row is only as strong
  as the `u64` id it prints; ids are minted from sidecar text, so an attacker who controls the sidecar
  text controls the id (see D4).
- **D2 cache-identity spoof — ACCEPTED (residual, bounded).** A byte-forged `.godot/uid_cache.bin`
  fully determines `get_resource_uid` for every path (A3), survives across processes (R13/persistence
  probe), and re-points the engine's own `uid://` resolution (A13). Nothing in the lattice is
  tamper-evident: no digest, no mtime cross-check, no re-derivation from the sidecars at runtime.
  Required discriminator for any receipt that claims "the cache says X": re-derive X from the cache
  bytes **and** assert the sidecar texts the row claims to have written (A3 shows the two disagree by
  construction). Also `CACHE_MODE_IGNORE`/`REPLACE` receipts must be split by resource kind: on
  **scripts** both modes return the cached object (L5) — a row that asserts "IGNORE gives a fresh
  object" from a `.gd` would be wrong.
- **D3 remap forgery — PASS with a measured asymmetry.** Remap resolution is pinned from both sides:
  source path loads to `CompressedTexture2D` with `resource_path` = the *source* path (L6), `exists()`
  is true for the source and the `.ctex` dest and **false** for the `.import`, and the two
  remap-missing classes are distinguishable by `exists` (A9 `exists_png=1` vs A10 `exists_png=0`).
  Asymmetry worth pinning: the `.import` `uid=` field is honoured **only on an actual reimport**; with
  an unchanged source the editor keeps its `filesystem_cache10` row and the forged uid is ignored (my
  first two A2 attempts). Once forced, the collision evicts the loser path and leaves **two cache rows
  for the same path** — an inconsistent state a census row could report wrongly if it counts rows.
- **D4 collision miss — ACCEPTED (the sharpest finding).** Collisions are handled by *silent eviction*,
  not by error: sidecar-vs-sidecar warns once on stderr and drops a path (A1); `.import`-uid-vs-sidecar
  on reimport drops a path with **no diagnostic at all** (A2); a forged cache can bind one id to two
  paths with the map then resolving to the *later* path while the other is unreachable (A4); a forged
  cache can bind an id to a path that does not exist on disk (A5); a renamed source keeps its old dead
  path registered and its old id alive until a full rescan mints a **new** id for the new path (A12).
  A "collision miss" receipt is therefore easy to write and hard to falsify: `same_id=0` (A1) and
  `same_id=1` (A4) are both reachable outcomes, and `len(cache_rows)==len(paths)` holds in A4 while the
  id→path map is already degenerate.

## 4. Verdicts

| C1 surface | attacked shape(s) | verdict |
|---|---|---|
| UID-census echo | A3, A13, S0 cross-parse | **no echo measured** — census re-derives from bytes and the engine follows the forged cache, not the receipt |
| cache-identity spoof | A3, A5, A12, R13 | **attack succeeds** — the cache is unauthorised, unaudited and persists; row must pair a byte re-parse with the sidecar texts |
| remap forgery | A2, A9, A10, L6 | **partially succeeds** — the `.import` uid is honoured on reimport (silent eviction); `exists()` asymmetry is the reliable discriminator |
| collision miss | A1, A2, A4, A12 | **attack succeeds** — collision ⇒ silent eviction; two cache rows can share one path; dead paths stay resolvable |

No sibling receipt was found *forged as landed*: the `res_uid*` fixtures were unregistered at seat
time, so the rows are claims, not pinned receipts. Nothing above contradicts the siblings' own
findings; §5 records the one place my measurements are sharper than theirs.

## 5. Cross-checks against sibling work (read-only, observation)

- `res_uid_s04.gd` (E4, sha256 `7e3c637f…`) independently reports the same format, the same
  `WARNING: UID duplicate detected between …` text, and the same "editor writes, plain run does not"
  split; its header was corrected from "version" to "record count", which my 1/2/10-row files confirm.
- `res_uid_s04.gd:419-430` counts cache records matching the contested id and pins `hits==1`. **My
  measurements show `hits` can be 2**: A2 leaves `[72315778293730335, 7070736749366049730]` for
  `res://tex.png`, and A4 leaves two rows carrying the same id for two paths. If s04's collision arm
  ever reaches that state its `hits` assertion goes red for a reason unrelated to its own claim.
- `res_uid.gd` (E0 composite) and `res_uid_s01/s02/s03` exist but are **not registered in
  `run_battery.py`** (no `res_uid` string in the file; CASES = 400). The C1 coverage row for round 104
  is therefore not yet countable by the battery — orchestrator action, not a fixture defect.

## 6. Evidence index / hygiene

- My files: `reports/round-104/r104-crit1.md` (this shard);
  `reports/round-104/mutations/r104-crit1_driver.py`; `reports/round-104/mutations/r104-crit1_read.gd`.
- Scratch retained under `/var/tmp/r104-crit1/` (`gt/`, `ord/`, `a2/`, `a11/`, `matrix/`, `out/`) —
  no git worktree, nothing to `git worktree remove`.
- No `run_battery.py` run; no shared file edited; no commit; joystick device-census tokens never used;
  sibling lane untouched.
- Unknowns (labelled): why the incremental-reimport collision in A2 prints no warning (the fresh-scan
  path does) — inference: the editor's `filesystem_cache10` fast path bypasses the duplicate check;
  not proven. The exact base-32 alphabet used by `uid://` text is not a plain `0-9a-v` map — decoding
  observed (text,id) pairs as base-32 conflicts (a permuted table is likely) — **unknown**, and not
  needed for any row here. `ResourceUID` behaviour under a *signed* 63-bit id at the top of the range
  (`has_id(INT64_MAX)` → false) was checked but the encoding boundary was not mapped.
