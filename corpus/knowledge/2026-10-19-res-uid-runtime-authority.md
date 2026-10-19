# uid:// runtime authority is the binary cache, and uid text is lossy

source: S026 — https://docs.godotengine.org/en/4.7/classes/class_resourceuid.html — Method Descriptions + INVALID_ID constant, class ref en/4.7; S028 — corpus/lessons/r104-resource-loader-uid.md — §1 law, §3 lossy-encoding table, §4 collision class (r104 lesson)
verified-at: 2026-10-19 (godot 4.7.2.stable.arch_linux.ed1daf0bf; corpus/fixtures/res_uid_s04.gd --arm=persist, corpus/fixtures/res_uid_s04.gd --arm=collision, corpus/fixtures/res_uid.gd --arm=text — re-run this session in a fresh scratch with per-run XDG_DATA_HOME and RES_UID_ROOT isolation)
recheck: on-release — from lane root: `timeout --signal=TERM --kill-after=2s 1800s python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot --res-uid-order forward --probe-res-uid-shared` → expects `PASS res_uid_s04_persist:` (runner stages fresh scratch projects; full battery, not just this row)

## Claim

On godot 4.7.2.stable (this host), the runtime authority for `uid://` resolution is the
binary cache `res://.godot/uid_cache.bin`, written by an editor pass (`--editor --quit`
or `--import`). The `<name>.<ext>.uid` text sidecar is the editor's durable input, not a
runtime authority: with sidecars present and the cache deleted, a plain `--script`
process resolves nothing (`has_id` false). The `uid://` text itself is a lossy encoding:
id→text→id round-trips, text→id→text does not (aliases exist: `uid://` = 0 = `uid://aaaa`;
`z` and `0` both encode digit 25). Two sidecars declaring the same id collide: the editor
warns once, and the cache keeps exactly one record for the contested id.

## Evidence

[obs] `PASS res_uid s04 arm=persist cache_records=1 cache_declared=1 cache_consistent=true
cache_id_match=true roundtrip=true reader_has=true reader_path=res://alpha.gd
nocache_has=false uidfile_only_authority=false` — re-run this session (4.04 s). The pair
`reader_has=true` after the editor pass and `nocache_has=false` after deleting
`.godot/uid_cache.bin` while `alpha.gd.uid` still exists is the discriminating negative
control: the text file alone cannot resolve the UID.

[obs] `PASS res_uid text decode=uid://a=0,uid://9=34,uid://z=25,uid://0=25,...,uid://=0,
uid://aaaa=0 alias_empty_eq_aaaa=true alias_0_eq_z=true ... roundtrip_int63max=true
first_bad=none ...` — re-run this session. The decode row pins the aliases (`uid://`,
`uid://aaaa`, `uid://a` all parse to id 0; `uid://z` = `uid://0` = 25) and
`roundtrip_int63max=true` confirms id→text→id is lossless over the full 63-bit range.

[obs] `PASS res_uid s04 arm=collision dup_warn=true pair=res://alpha.gd,res://beta.gd
records=1 dup_records=1 dup_text_roundtrip=true winner_in_pair=true
reader_matches_winner=true` — re-run this session (3.04 s). Nested-editor diagnostic:
`WARNING: UID duplicate detected between res://beta.gd and res://alpha.gd.` One cache
record survives; a fresh reader resolves the contested id to the winner.

[obs] S028 §1 law (r104 first-hand measurement, three independent cache rebuilds):
"res://.godot/uid_cache.bin is the runtime authority for uid:// resolution." And §3:
"Treat a `.uid` file's text as an untrusted spelling of an id. Compare ids, never strings."

[obs] S026 (ResourceUID class ref, en/4.7): `has_id` "Returns whether the given UID value
is known to the cache" — the docs name the store a *cache*; `uid_to_path` "Prints an
error if the UID is invalid", i.e. lookup failure is an engine ERROR, not a null return
contract. `INVALID_ID = -1` renders as `uid://<invalid>`.

[inf] The collision survivor is deterministic across rebuilds (beta over alpha in every
observed project) but the selection rule is unknown — it is not write order, alphabetical
order, or directory order (S028 §4 [unk]).

[unk] Whether a hand-edited cache survives an editor pass byte-for-byte, and the exact
scan order that picks the collision winner.

## Decision

- Compare UIDs by integer id (`text_to_id`), never by text spelling — the editor rewrites
  sidecars to canonical form, so a non-canonical-but-valid string is not corruption.
- A checkout or scratch project without `.godot/uid_cache.bin` cannot resolve custom
  `uid://` refs from a `--script` process; run an editor pass (`--import`) first. Test
  the failure with `has_id()`, not `path_to_uid()`/`ensure_path()`, which echo the
  argument back on miss.
- Treat `UID duplicate detected` warnings as blocking: a collision silently re-points
  the id to one survivor and surfaces later as an unrelated scene parse error.
- A truncated sidecar containing bare `uid://` registers id 0 — valid, and collidable
  with a real `uid://a` mapping. Validate sidecar text before trusting a scan.

## Limits

Measured only on godot 4.7.2.stable.arch_linux.ed1daf0bf, headless, Linux x86-64. The
cache-file layout claim in this entry is bounded to "u32 record count then records" —
the r104 fixture's earlier `cache_version=1` header label is contested by three
independent parses (S028 §2) and is not asserted here. `*_DEEP` cache-mode behavior and
`.import` remap interplay are covered by S028 §§5–6, not re-verified this session.

## Claim-to-CASES binding (Q6)

Exact five-field tuples and byte-exact PASS signatures are committed at
`reports/round-105/r105-claim-tuples.json`, keyed by case below. Both serial
receipts at `reports/round-105/r105-battery-receipts.json` carry those signatures
with `signature_in_output=true`.

| claim | exact tuple key | fixture / arm / expected exit |
|---|---|---|
| cache authority vs sidecar-only negative | `res_uid_s04_persist` | `res_uid_s04.gd`, `--arm=persist`, 0 |
| lossy text aliases / integer round-trip | `res_uid_text` | `res_uid.gd`, `--arm=text`, 0 |
| duplicate sidecar collision survivor | `res_uid_s04_collision` | `res_uid_s04.gd`, `--arm=collision`, 0 |
