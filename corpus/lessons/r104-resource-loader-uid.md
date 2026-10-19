# Round 104 — ResourceLoader / ResourceUID cache lattice (Godot 4.7.2.stable)

First-hand receipts for the round-104 C1 surface: how `ResourceUID` maps ids to paths, which artifact
is authoritative at runtime, what the `uid://` text encoding actually is, how the load cache answers per
`CacheMode`, and how `.import` remaps resolve. All runs on godot
`4.7.2.stable.arch_linux.ed1daf0bf`, headless, scratch under `/var/tmp/r104-R1/` (never `/tmp`, EDQUOT);
`run_battery.py` was never executed. Every row is [obs] unless labelled [inf] (inference) or [unk]
(unknown). Verbatim stdout is archived under `reports/round-104/mutations/r104-R1-evidence/`; the nine
probe scripts are archived as `reports/round-104/mutations/r104-R1-res_uid_scr{1..9}.gd`.

Probe project: `/var/tmp/r104-R1/uidproj` — `assets/thing.gd` (+ hand-written `assets/thing.gd.uid` =
`uid://bq1a2b3c4d5e6`), `sub/deep.gd` (+ `.uid` = `uid://cq7f8g9h0j1k2`), `data/res.tres`, `tiny.png`,
`scene.tscn` (inline `uid="uid://bq1a2b3c4d5e6"` — deliberately colliding with `thing.gd`), plus
`assets/plain.txt` as a non-resource. Launch shape used for every arm:

```
godot --headless --path /var/tmp/r104-R1/uidproj --script res://res_uid_scrN.gd -- --arm=<arm>
```

## 1. The runtime authority is the binary cache, not the `.uid` text

`ResourceUID` is a singleton (`Engine.has_singleton("ResourceUID")` = true) with exactly one integer
constant, `INVALID_ID = -1` [obs: `ClassDB.class_get_integer_constant_list`]. Its method set is
`add_id/2 set_id/2 remove_id/1 has_id/1 get_id_path/1 text_to_id/1 id_to_text/1 create_id/0
create_id_for_path/1 uid_to_path/1 path_to_uid/1 ensure_path/1` [obs, 12 methods, sorted].

The decisive measurement: with all `.uid` sidecars present but `.godot/uid_cache.bin` deleted, a plain
`--script` process resolves **nothing**.

```
# rm .godot/uid_cache.bin  (sidecars untouched)
[r104R1c] cachebin_exists=false
[r104R1c] resolve=uid://bq1a2b3c4d5e6 has=false path=
[r104R1c] resolve=uid://cq7f8g9h0j1k2 has=false path=
[r104R1c] uidfile_thing=uid://bq1a2b3c4d5e6      <- the text file is right there
[r104R1c] uidfile_deep=uid://cq7f8g9h0j1k2
```

Re-running the editor pass rebuilds it, and reports what it had to reconstruct:

```
$ godot --headless --path <proj> --import
WARNING: Missing .uid file for path "res://sub/deep.gd". The file was re-created from cache.
```

**Law.** `res://.godot/uid_cache.bin` is the runtime authority for `uid://` resolution. `<name>.*.uid` is
the editor's durable *input*; a plain `--script` process never reads it. Losing the cache loses every
custom UID until an editor pass rebuilds it — and rebuilding is possible only while the sidecars (or the
cache) survive. Corroborated independently by the sibling fixture `corpus/fixtures/res_uid_s04.gd`
(sha256 `543ae0a9…`), whose own receipt reads
`PASS res_uid s04 arm=persist cache_version=1 cache_records=1 … nocache_has=false uidfile_only_authority=false`.

## 2. `uid_cache.bin` layout — the leading u32 is a row COUNT

Byte-verified by a self-checking parse (`f.get_length() - f.get_position()` = 0 after the last row) and by
byte arithmetic:

```
u32 count
repeat count:  u64 id | u32 path_len | path_len bytes UTF-8 path
```

| file | size | count | arithmetic |
|---|---|---|---|
| 6 rows | 153 B | 6 | 4 + Σ(12 + len(path)) = 4 + 12·6 + Σlen = 4 + 72 + 77 = **153** |
| 2 rows | 70 B | 2 | 4 + 24 + 42 = **70** |

`count` is not a version: the same project produced count=5, 6 and 9 across cache rebuilds. [obs]

```
[r104R1c] count=9 eof_remaining=0
rows=3563164315850256711|res://scene.tscn|uid://bq1a2b3c4d5e6 ;; 5962285837902618511|res://sub/deep.gd|uid://cq7f8hah0j1k2 ;;
     0|res://bad1.gd|uid://a ;; 2716476453200264457|res://res_uid_scr1.gd|uid://bex478w0shhdp ; … 
```

**Contradiction flag.** `corpus/fixtures/res_uid_s04.gd:11` states the header is `u32 version(=1)` and its
receipt prints `cache_version=1`. That reading is not supported by any of my three independent rebuilds
(5/6/9 rows with the file ending exactly after the rows). Either that fixture observes a different header
under some other editor path, or the label is wrong. The sibling's other claims agree with mine, so this
is a labelling defect rather than a behavioural one — but a fixture that pins `cache_version=1` on a
9-record cache would be pinning a coincidence. [inf: row count; the alternative "version" reading is
falsified by the three sizes]

## 3. The `uid://` text encoding is lossy — round-trip is id→text→id, not text→id→text

`text_to_id` is not injective, and `id_to_text` is the canonicalising side.

| input text | id | `id_to_text(id)` | text stable? | id stable? |
|---|---|---|---|---|
| `uid://bq1a2b3c4d5e6` | 3563164315850256711 | `uid://bq1a2b3c4d5e6` | yes | yes |
| `uid://cq7f8g9h0j1k2` | 5962285837902618511 | `uid://cq7f8hah0j1k2` | **no** | yes |
| `uid://zzzzzzzzzzzzz` | 6128179328542129927 | `uid://ctkshoiimsrhf` | **no** | yes |
| `uid://ab` | 1 | `uid://b` | **no** | yes |
| `uid://aa` | 0 | `uid://a` | **no** | yes |
| `uid://10000000000000` | 3571867273499803399 | `uid://bq5ieq0tbicxb` | **no** | yes |
| `uid://a` | 0 | `uid://a` | yes | yes |
| `uid://0` | 25 | `uid://0` | yes | yes |
| `uid://10` | 909 | `uid://10` | yes | yes |

Reading is case-sensitive and only accepts the lowercase `uid://` prefix: `uid://A`, `uid://B`,
`uid://BQ1A2B3C4D5E6`, `UID://b` all parse to `-1`; so do `bq1a2b3c4d5e6`, `res://…`, `""`, `uid:/b`. [obs]

Boundary rows: `uid://` (prefix, empty body) parses to **0** (= `uid://a`), while `""` and
`uid://<invalid>` parse to **-1**. `id_to_text(-1)` = `uid://<invalid>`. A 30-char body and a 41-char body
both parse to a non-negative id and canonicalise to a 13-char body — so the body is a base-34
big-endian numeral that silently truncates/overflows past 13 digits. `id_to_text(2^63-1)` =
`uid://d4n4ub6itg400`, and its round-trip returns exactly `9223372036854775807`, so the full 63-bit range
is representable in 13 canonical digits. [obs]

**Law.** Treat a `.uid` file's text as an *untrusted spelling* of an id. Compare ids, never strings. The
body is **base 34, big-endian, lowercase, 13 digits max** — `34^12 < 2^63 < 34^13`, which is exactly why
13 digits suffice. The digit alphabet is `a`..`y` → 0..24, `z` → 25, `0`..`9` → 25..34. Note the
**deliberate collision: `z` and `0` both mean 25**, which is why `uid://z` parses to 25 and canonicalises
to `uid://0`, and why `uid://zz` (875) canonicalises to `uid://00`. Arithmetic check on the measured
table: `ba` = 1·34+0 = 34 ✓, `bb` = 35 ✓, `a0` = 25 ✓, `0a` = 25·34 = 850 ✓, `10` = 26·34+25 = 909 ✓,
`100` = 26·34²+25·34+25 = 30,931 ✓, `vvv` = 21·34²+21·34+21 = 25,011 ✓. Every digit `a`..`z`, `0`..`9`
is accepted; every other byte (uppercase, punctuation, space, DEL, high bytes) parses to -1. One quirk:
the digit `9` has value 34, i.e. it equals the base itself (`uid://9` = 34 = `uid://ba`), so a single
digit can parse to a value outside `[0, base)`. [obs]

The editor writes canonical text back: after a delete-and-reimport cycle, `sub/deep.gd.uid` changed from
`uid://cq7f8g9h0j1k2` (hand-written) to `uid://cq7f8hah0j1k2` — same id, canonical spelling. [obs]

## 4. Collision class — one record, deterministic survivor, and a WARNING

Two `.uid` sidecars declaring the **same** id reproduce the duplicate path live:

```
$ godot --headless --path <proj> --import
WARNING: UID duplicate detected between res://beta.gd and res://alpha.gd.
```

and the cache keeps exactly one record for the contested id. The survivor is deterministic and is *not*
scan order: in three independent fresh projects — including one where `beta.gd`/`beta.gd.uid` were written
first — the same file won:

```
[alpha-first] all=res://beta.gd -> uid://bq1a2b3c4d5e6 ;; …
[beta-first]  all=res://beta.gd -> uid://bq1a2b3c4d5e6 ;; …
```

The warning names `beta` first as well. [obs; the *rule* that selects the survivor is [unk] — it is not
"last written", not alphabetical (alpha < beta), and not directory order]

A second, cheaper collision shape is an **inline `uid=` in a scene**: `scene.tscn` declaring
`uid="uid://bq1a2b3c4d5e6"` — the same id as `assets/thing.gd.uid` — wins outright. `ResourceUID` then maps
that id to `res://scene.tscn` and `res://assets/thing.gd` becomes unreachable by UID:

```
[r104R1c] resolve=uid://bq1a2b3c4d5e6 has=true path=res://scene.tscn
[r104R1d] load=uid://bq1a2b3c4d5e6 null=false class=PackedScene path=res://scene.tscn
```

The losing resource is still reachable by path (`ResourceLoader.load("res://assets/thing.gd")` succeeds),
and the scene that consumed it then fails to load — `ERROR: res://scene.tscn:6 - Parse Error:
[ext_resource] referenced non-existent resource`. So a collision is **not** fail-safe: it silently
re-points an id and surfaces later as an unrelated-looking scene parse error. [obs]

Misuse classes, each an engine `ERROR` with a file:line, never a silent no-op [obs]:
duplicate `add_id` → `resource_uid.cpp:164` (`Condition "unique_ids.has(p_id)" is true.`); `set_id` on an
unknown id → `:178`; `get_id_path`/`uid_to_path` on an unknown id → `:214` (`Unrecognized UID: "<text>".`),
on a malformed string → `:196` (`Invalid UID.`). A failed duplicate `add_id` leaves the **first** binding
intact. Two *different* ids bound to one path is accepted silently (`add_id(i2, existing_path)`).

## 5. Load cache: `CacheMode` identity semantics

The real enum [obs: `ClassDB.class_get_enum_list("ResourceLoader")` → `CacheMode`]:

| constant | value |
|---|---|
| `CACHE_MODE_IGNORE` | 0 |
| `CACHE_MODE_REUSE` | 1 |
| `CACHE_MODE_REPLACE` | 2 |
| `CACHE_MODE_IGNORE_DEEP` | 3 |
| `CACHE_MODE_REPLACE_DEEP` | 4 |

There is **no** `CACHE_MODE_REUSE_DEEP`; a script naming it fails to parse (and the failure is worth
noting for the harness: `--script` with a parse error exited rc=0 on one invocation and rc=1 on another,
while still printing `PASS`-free output — a fixture whose script fails to parse can therefore look like a
clean run; [obs, exact bytes in `evidence/dump.txt` vs the later rerun]).

Identity, measured by `get_instance_id()` on `res://data/res.tres`, with the file rewritten on disk from
inside the process between loads [obs]:

| step | mode | result |
|---|---|---|
| load, then load again | `REUSE` | same RID, `v=1` (disk change invisible) |
| after disk now says `v=999` | `REUSE` | same RID, still `v=1` |
| | `IGNORE` | **new** RID, `v=999` |
| | `REPLACE` | `v=999` |
| `REUSE` again | `REUSE` | RID == the `REPLACE` RID, `v=999` |
| | `IGNORE_DEEP` | `v=777` (new disk value), new RID |
| | `REPLACE_DEEP` | `v=777`, RID ≠ `IGNORE_DEEP` RID |
| `REUSE` after `REPLACE_DEEP` | `REUSE` | RID == `REPLACE_DEEP` RID, `v=777` |

**Law.** `REUSE` is a pure cache hit and never re-reads the source. `IGNORE` bypasses the cache *and
leaves it untouched* (`REUSE` after `IGNORE` still returns the original RID). `REPLACE` bypasses the cache
*and installs the new instance* (`REUSE` afterwards returns the `REPLACE` RID). `*_DEEP` variants behave
like their non-deep counterparts at the top level for a leaf `.tres` — the "deep" in the name governs
sub-resource recursion, which these probes did not exercise. [obs for identity/values; [inf] for the
deep-vs-shallow distinction, which is unverified here]

A plain `.gd` script is cache-stable too: two default `load()` calls return the same RID
(`gd_default_identity=true`). [obs]

## 6. `.import` remap resolution and refusal classes

`--import` on a 1×1 PNG produced a sidecar with the remap in `[remap]` and the dependency list in `[deps]`:

```
[remap]
importer="texture"
type="CompressedTexture2D"
uid="uid://cfo35nu5y4frk"
path="res://.godot/imported/tiny.png-4c2a616b3090ed27619d4dea97b52b2a.ctex"
[deps]
source_file="res://tiny.png"
dest_files=["res://.godot/imported/tiny.png-4c2a616b3090ed27619d4dea97b52b2a.ctex"]
```

- `ResourceLoader.load("res://tiny.png")` → `CompressedTexture2D`, and `resource_path` is the **source**
  path (`res://tiny.png`), not the imported artifact. `ResourceLoader.exists()` = true. [obs]
- The same source loads under an explicit type hint: `load("res://tiny.png", "Image")` → still a
  `CompressedTexture2D`; the hint does not defeat the remap. [obs]
- The artifact path loads directly and reports itself: `load("res://.godot/imported/tiny.png-<md5>.ctex")`
  → `CompressedTexture2D` with `resource_path` = that artifact path. [obs]
- **Remap-miss** (sidecar present, artifact deleted) fails the whole chain, source included:
  `dest_exists=false`, `load("res://tiny.png")` → null with
  `ERROR: Failed loading resource: res://tiny.png.` — while `ResourceLoader.exists("res://tiny.png")`
  still returns **true**. `--import` restores both. [obs]
- Non-resource refusal: `load("res://assets/plain.txt")` → null with
  `ERROR: No loader found for resource: res://assets/plain.txt (expected type: unknown)`. A missing script
  gives `Attempt to open script '…' resulted in error 'File not found'.` + `Failed loading resource: …`.
  Both are null-returns with an engine ERROR, never a throw. [obs]
- `uid://` paths work in the loader *and* in `FileAccess`: `ResourceLoader.load("uid://cfo35nu5y4frk")`
  → the texture; `FileAccess.file_exists("uid://cfo35nu5y4frk")` = true. But `FileAccess` uid resolution
  is **not** the resource resolution: `FileAccess.get_file_as_string("uid://cfo35nu5y4frk")` returns 8
  bytes whose hex is `efbfbd 504e470d0a1a0a` — i.e. U+FFFD followed by the PNG magic `\x89PNG\r\n\x1a\n`,
  the leading `\x89` having been replaced as invalid UTF-8. `FileAccess.open(uid, READ)` reports length 69,
  the true file size. So the bytes are correct and the *string* accessor is what mangles them. [obs]

## 7. Malformed `.uid` sidecars are non-fatal but they do register garbage

| `.uid` content | `text_to_id` | registered? | `load(path)` |
|---|---|---|---|
| `uid://` (bare prefix) | 0 | **yes** — as `uid://a` → `res://bad1.gd` | succeeds |
| `not-a-uid` | -1 | no (`ERROR: Invalid UID.`) | succeeds |
| *(empty file)* | -1 | no | succeeds |

The bare-`uid://` row is the sharp one: a truncated sidecar registers the file at id **0**, and id 0 is a
legal id (`id_to_text(0)` = `uid://a`), so it can collide with a genuine `uid://a` mapping. The cache
records it as `0|res://bad1.gd|uid://a`. No warning is emitted for any of the three. [obs]

## 8. Persistence across processes

Resolution is stable and idempotent across separate invocations — three consecutive fresh `--script`
processes returned the identical mapping [obs]:

```
[r104R1c] resolve=uid://bq1a2b3c4d5e6 has=true path=res://scene.tscn   (×3, byte-identical)
[r104R1c] resolve=uid://cq7f8g9h0j1k2 has=true path=res://sub/deep.gd
```

The cache row set is also stable across processes once written (no reordering on read). `create_id_for_path`
is deterministic and pure — same path ⇒ same id across calls, and it does **not** register the result:

```
[r104R1g] cidf path=[res://assets/thing.gd] i1=7819409213968401341 i2=7819409213968401341 deterministic=true
[r104R1g] cidf_registered path=[res://assets/thing.gd] has=false
```

`create_id()` is non-deterministic (`8190281634667759801` vs `3536972823274993262` in one process).
`path_to_uid()` and `ensure_path()` **echo their argument back** when the path is unregistered — they are
not error paths, so a caller cannot use them to test registration; `has_id()` is the only reliable
predicate. [obs]

## 9. Gaps and unknowns

- [unk] The rule that picks the collision survivor (§4) — measured deterministic, mechanism unknown.
- [unk] Whether `*_DEEP` differs from its shallow twin for nested sub-resources; only a leaf `.tres` was
  probed. The identity rows in §5 are for the top-level resource only.
- [unk] Whether the cache row order is insertion order or sorted; observed rows are not sorted by id or by
  path, and only one rebuild was diffed.
- [unk] What the `0|res://bad1.gd` row does when a real `uid://a` is also present — the collision would be
  between a truncated sidecar and a legitimate id.
- Contested with the round-104 C1 sibling fixtures (`res_uid_s04.gd`, `res_uid_w07.gd`, sha256
  `543ae0a9…` / `f1ec8f8e…`): the `cache_version=1` header reading in §2. `res_uid_s04.gd` was replayed
  from my own scratch and its `persist` / `classes` / `collision` arms all reproduced (§1, §4 agree);
  only the header label diverges.
