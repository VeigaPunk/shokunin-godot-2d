# game-dev-2d round 96 — scout (r96-scout): the PackedScene / ResourceSaver / ResourceLoader round-trip lattice, pre-measured; 13 rows verbatim-ready

Seat `SCOUT` (LEAF) | lane `r96-scout` | round 96 | host **devin**.
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), `--headless`,
60 tps default. Repo `~/Projects/shokunin/game-dev-2d-shokunin`; HEAD at session start
**`2c4b1ff`** (*r94 scout*), HEAD unchanged at session end (no lane commit during this
seat). The launch `project.godot` is the byte-copy of `corpus/fixtures/project.godot`
(`8de8b3af…`).

**No git mutation, no tracked file written, no commit.** Writes are this report and
`corpus/live/r96-scout/**` only. The tracked modification in `git status`
(`corpus/fixtures/run_battery.py`, +74 lines) and the untracked
`corpus/fixtures/rb_lattice.gd` / `rb_watch.gd` are **concurrent lanes'** and contain no
r96/`scene_io` token (`git diff … | grep -c "r96\|scene_io"` → 0).

**`lsp` disclosure.** No `lsp` device in this session and no GDScript language server
installed; `definition`/`references`/`hover` were **unavailable for every file touched**.
All symbol work was therefore done by reading the fixtures directly (fallback per the seat
card). Semantic carriers are fresh-process execution receipts, `ClassDB` introspection
inside the probe, engine-emitted error text, and byte hashes of the files the engine
wrote. No engine source tree exists on this host, so every mechanism statement is marked
**[I]** and kept separate from the measurements.

**Legend:** **[M]** measured (fresh process, byte-stable over N reps unless marked);
**[O]** observed/operational fact; **[I]** inference; **[A]** ablation/refutation.

---

## 0. Surface chosen — and why

**Primary: the resource round-trip lattice** — `PackedScene.pack()`/`instantiate()` (all
four `GEN_EDIT_STATE_*` values), `ResourceSaver.save()` and its eight flags, the
`.tscn`/`.scn`/`.tres`/`.res` formats, `ResourceLoader.load()` and its five cache modes,
`uid://`/`ResourceUID`/`ResourceSaver.set_uid`, `take_over_path`, `owner` edges,
subresources (sharing, `resource_local_to_scene`, `resource_scene_unique_id`),
external-resource references, and **byte-level save determinism**.

Why this surface, against the brief's other candidates **[O]/[I]**:

- The battery already loads packed scenes (`causal_chain`, `contact_probe`,
  `level_collision`, `r88_surfaces`) but **no row pins the pack/save/load round trip
  itself**: `grep -rin "PackedScene\|ResourceSaver\|ResourceLoader\|take_over_path"
  corpus/fixtures/*.gd` finds only `load(...).instantiate()` call sites, and the only
  save rows in the battery (`save_roundtrip`, `save_process`) are **JSON via
  `FileAccess`**, not `ResourceSaver`. The scene/resource serialization path is a clean
  coverage gap on an author-facing surface (scene spawning, save games, level editors,
  hot reload).
- It is where the round's headline determinism question lives — "is a saved scene
  reproducible byte-for-byte?" — and the answer is **no, not by default**, with a
  measured recipe for when it is.
- **Falsifiability was immediate**: the first probe refuted two of the scout's own
  assumptions — `PackedScene.pack()` is an *instance* method returning `Error` (the
  Godot-3 static factory is gone), and the scene saver emits a **random `unique_id=` per
  node** (§4).
- The other candidates were weighed and left: TileMapLayer (r92), PhysicsDirectSpaceState2D
  (r95), Animation/Tween (r93), particles (r94), Geometry2D (r89) are all claimed by
  concurrent or earlier scouts; `input_lattice`/`r88_surfaces` own input and the
  MultiplayerAPI/light surfaces.

---

## 1. What I ran

| # | protocol | scope | receipts |
|---|---|---|---|
| 1 | `probes/discover.gd` … `discover9.gd` (9 probes, 42 arms) | feasibility: census, pack/owner, formats, determinism, uid, take-over, cache, subresources, ext resources, edit states, refusals, bundle dict, saver flags, path bookkeeping, uid variance | `runs/disc*/…` |
| 2 | `bash run_cells.sh` | **13 cells** (1 pure ×3, 12 frame-free ×6) = **75 runs** | `runs/r96_*.{out,err,rc}` |
| 3 | `bash run_loadtest.sh` (16 own `yes` hogs, load avg 94–148) | 39 runs over all 13 cells | `runs/loadtest/*.{out,err,rc}` |
| 4 | `python3 analyze_r96.py` | per-cell reps / out-uniq / err-uniq / rc / PASS-line uniqueness | `runs/analyze_r96.json` |
| 5 | `python3 make_author_rows.py` → `python3 verify_rows.py` | 13 rows classified with the production `classify_process` (AST-extracted, segment sha `749fa060…`) over **114 receipts** | `author-rows.py.txt` |
| 6 | `python3 smoke_battery.py` | the probe re-run **inside a real battery scratch project** (fixture dir copied, project renamed with a stamp, battery's own 8 s bound, merged streams) → 13/13 classified PASS | `runs/smoke/<stamp>/` |

**Canonical cell set: 75 runs across 13 cells** — 1 census cell ×3, 12 cells ×6. All rc=0;
no cell crashed; no run left running; **all stderr 0 B** except `ownership` (499 B) and
`refuse` (3424 B), whose allowlisted refusal `ERROR:` lines are part of the measurement.

**Byte-stability: 13 of 13 cells are `out_uniq=1 err_uniq=1 pass_uniq=1 rc=[0]`**
(`runs/analyze_r96.json`: `UNSTABLE=[]`, `CRASH_CELLS=[]`) — including the cells whose
PASS line carries a full sha256 of an engine-written file and the cells that provoke
engine `ERROR:` lines.

**Load-stability [M]:** re-running all 13 cells ×3 at load avg 94–148 produced **39/39
rc=0** and **zero** row rejections: `verify_rows.py` → `ROWS` **114/114 accepted**,
`ROWS_PREFIX` **114/114 accepted**, `rejected=[]`.

**Battery-shaped smoke [M]:** `smoke_battery.py` copies `corpus/fixtures/` into a scratch
project, renames `config/name` (the battery's `user://` isolation), drops the probe in as
`res://scene_io_lattice.gd`, launches every arm under the battery's own **8 s** bound,
merges stdout+stderr exactly like `run_battery.run_process`, and classifies with the
production `classify_process` + the row's `expected_errors`: **13/13 PASS**.

**Arm-dispatch integrity [O]:** every arm prints its own name on the `PASS` line
(`PASS scene_io_lattice <arm> …`), so a silent `_:` fallback (the r88 dead-seat failure)
is impossible to miss; `arm` is parsed with the battery convention
(`OS.get_cmdline_user_args()` + `--arm=` prefix scan).

**Delegated probe [O]:** the frozen `probeParent` dispatched exactly one read-only
`ufo-labrat` seat (independent falsification of the pinned-bundle determinism recipe).
**It could not execute** — that seat's tool surface has no shell/exec and no write
capability, so it ran **0** godot launches and reported honestly rather than fabricating
shas. No empirical delta; the falsification ladder was therefore run by this seat instead
(§7, F21–F24 and the `det`/`extres`/`disc7` receipts).

---

## 2. Headline

| family | verdict headless | reps × cells | byte-stability |
|---|---|---|---|
| **API census** (PackedScene/ResourceSaver/ResourceLoader/ResourceUID/Resource/SceneState) | **PINNABLE** | 3 | uniq=1 |
| **`pack()` + owner edges** (who survives, refusals) | **PINNABLE law** | 6 | uniq=1 |
| **Plain `.tres` / `.res` round trip** (text vs binary) | **PINNABLE + byte-stable across processes** | 6 | uniq=1 |
| **Format matrix** (`.tscn`/`.scn`/`.res`/refused extensions) | **PINNABLE law** | 6 | uniq=1 |
| **Scene save determinism** (`unique_id=` random per node) | **PINNABLE hazard — NOT reproducible by default** | 6 | uniq=1 (masked) |
| **Determinism recipe** (bundle `node_ids` + `resource_scene_unique_id`) | **PINNABLE law, sha256 pinned** | 6 | uniq=1 |
| **`uid://` surface** (never emitted, never minted, set_uid no-op) | **PINNABLE law** | 6 | uniq=1 |
| **`take_over_path` / cache identity** | **PINNABLE law** | 6 | uniq=1 |
| **Cache modes** (REUSE stale / REPLACE identity-stable / IGNORE fresh) | **PINNABLE law** | 6 | uniq=1 |
| **Subresource sharing + `resource_local_to_scene`** | **PINNABLE law** | 6 | uniq=1 |
| **External resources** (ext line, sharing, inlining, unpinnable id) | **PINNABLE + one unpinnable field** | 6 | uniq=1 (masked) |
| **`GEN_EDIT_STATE_*` + editable/placeholder flags** | **PINNABLE (all four states equal)** | 6 | uniq=1 |
| **Refusal lattice** (13 allowlisted ERROR lines) | **PINNABLE** | 6 | uniq=1 |
| **Instantiation naming/groups/owner paths** | **PINNABLE law** | 6 | uniq=1 |

---

## 3. Measured values, verbatim

All payloads are `runs/r96_<cell>.rep1.out`; diagnostics that would carry process-random
tokens are masked (`unique_id=#`, sub/ext ids → `#`) before printing, so the receipts are
byte-stable while still showing the file shape. The full PASS lines are in
`author-rows.py.txt`.

### 3.1 Census (`census`) — [M]

```
PASS scene_io_lattice census ps_methods=_get_bundled_scene,_set_bundled_scene,can_instantiate,get_state,instantiate,pack
 ps_props=bundled ps_consts=GEN_EDIT_STATE_DISABLED=0,GEN_EDIT_STATE_INSTANCE=1,GEN_EDIT_STATE_MAIN=2,GEN_EDIT_STATE_MAIN_INHERITED=3
 saver_methods=add_resource_format_saver,get_recognized_extensions,get_resource_id_for_path,remove_resource_format_saver,save,set_uid
 saver_flags=FLAG_NONE=0,FLAG_RELATIVE_PATHS=1,FLAG_BUNDLE_RESOURCES=2,FLAG_CHANGE_PATH=4,FLAG_OMIT_EDITOR_PROPERTIES=8,FLAG_SAVE_BIG_ENDIAN=16,FLAG_COMPRESS=32,FLAG_REPLACE_SUBRESOURCE_PATHS=64
 loader_methods=add_resource_format_loader,exists,get_cached_ref,get_dependencies,get_recognized_extensions_for_type,get_resource_uid,has_cached,list_directory,load,load_threaded_get,load_threaded_get_status,load_threaded_request,remove_resource_format_loader,set_abort_on_missing_resources
 loader_modes=THREAD_LOAD_INVALID_RESOURCE=0,THREAD_LOAD_IN_PROGRESS=1,THREAD_LOAD_FAILED=2,THREAD_LOAD_LOADED=3,CACHE_MODE_IGNORE=0,CACHE_MODE_REUSE=1,CACHE_MODE_REPLACE=2,CACHE_MODE_IGNORE_DEEP=3,CACHE_MODE_REPLACE_DEEP=4
 uid_methods=add_id,create_id,create_id_for_path,ensure_path,get_id_path,has_id,id_to_text,path_to_uid,remove_id,set_id,text_to_id,uid_to_path
 uid_consts=INVALID_ID=-1 res_props=Resource,resource_local_to_scene,resource_name,resource_path,resource_scene_unique_id
 ss_methods=get_base_scene_state,get_connection_*,get_node_count,get_node_groups,get_node_index,get_node_instance,get_node_instance_placeholder,get_node_name,get_node_owner_path,get_node_path,get_node_property_count,get_node_property_name,get_node_property_value,get_node_type,get_path,is_node_instance_placeholder
 empty_can_instantiate=false pack_is_instance_method=true
```

- **`PackedScene.pack()` is an INSTANCE method returning `Error`** — calling it statically
  (`PackedScene.pack(root)`, the Godot-3 API) is a **parse error** on this build **[M]**
  (`SCRIPT ERROR: Parse Error: Cannot call non-static function "pack()" on the class
  "PackedScene" directly. Make an instance instead.`). `Resource.bundled` is the only
  PackedScene property; `PackedScene` has no signals and no `get_path` **[M]**.
- `Resource` exposes exactly four properties and the id surface the recipe needs:
  `resource_scene_unique_id` is **settable** (and `set_scene_unique_id`,
  `generate_scene_unique_id`, `get_id_for_path`, `set_id_for_path`, `set_path`,
  `take_over_path`, `duplicate`, `duplicate_deep` are all present) **[M]**.
- `ResourceSaver.set_uid(path, id)` exists — and is a **no-op** in headless (§3.6) **[M]**.
- `SceneState` exposes `get_node_owner_path` — the owner edge of every node in the packed
  state, which the ownership/edges cells pin **[M]**.

### 3.2 Pack + owner edges (`pack_basic`, `ownership`) — [M]

```
R96 pack_basic head=[gd_scene format=3] text=[gd_scene format=3]||[node name="Root" type="Node2D" unique_id=#]|position = Vector2(10, 20)||[node name="Child" type="Node2D" parent="." unique_id=#]|position = Vector2(3, 4)|
PASS … pack_basic save=OK(0) can=true nodes=2 names=Root,Child pcounts=1,1 types=Node2D,Node2D state_path_empty=true header=[gd_scene format=3] has_uid=false has_unique_id=true size_in_190_200=true sha_len=64 inst_name=Root inst_pos=(10.0, 20.0) kids=1 kid_name=Child kid_pos=(3.0, 4.0) kid_owner_root=true scene_file_is_path=true back_path_is_path=true resave=OK(0) resave_same_in_process=true load_cached_identity=true
R96 ownership text=[gd_scene format=3]||[node name="Root" type="Node2D" unique_id=#]||[node name="Owned" type="Node2D" parent="." unique_id=#]|position = Vector2(1, 1)|
PASS … ownership save=OK(0) packed_nodes=2 packed_names=Root,Owned orphan_dropped=true deep_dropped=true bad_owner_refused=true self_owner_refused=true cleared_owner_null=true child_of_tree_nodes=1 unparented_nodes=2 inst_child_owner_root=true owner_paths=Root:.:,Owned:./Owned:.
```

- The saved text is `[gd_scene format=3]` — **no `load_steps`, no `uid=`** — and each node
  line carries **`unique_id=<random>`** **[M]**. Property blocks appear only for
  properties that differ from the class default (`pcounts=1,1` for two `position` writes;
  a node with no writes records none) **[M]**.
- **Ownership law:** a node is packed **iff `node.owner == the pack root`**. The ownerless
  `Orphan` and the grandchild `Deep` (owned by the intermediate `Owned`) are both
  **dropped**, silently — the file contains only `Root,Owned` **[M]**. A node whose owner
  is set to a non-ancestor or to itself is **refused** (`owner` stays `null`) with
  `ERROR: Invalid owner. Owner must be an ancestor in the tree.` /
  `ERROR: Condition "p_owner == this" is true.` **[M]**; `owner = null` after being set
  is honoured (the node is then dropped).
- Packing a node that already has a parent works and yields a **1-node** scene; packing an
  unparented tree yields the full tree **[M]**. `instantiate()` restores owners (children
  owned by the instance root) and sets `scene_file_path` to the loaded path **[M]**.
- `get_state()` before saving has an **empty** `get_path()`; after loading, the state path
  is the file path **[M]**. `SceneState.get_node_owner_path(i)` returns `""` for the root
  and `"."` for root-owned children; `get_node_index(i)` is `-1` for ordinary nodes **[M]**.

### 3.3 Format matrix (`formats`) — [M]

```
PASS … formats grad_tres=OK(0) size=101 sha=94ca8c1804aa166ebfce76ff354bc9adbcf5fb0ea108436dedf560fd7ba2356a header=[gd_resource type="Gradient" format=3] colors_match=true grad_res=OK(0) size=354 sha=6f13538bfb452af9193d4ba487ccdf755afda3db8d4f5034c3f149c703e3ef76 magic=RSRC colors_match=true text_eq_bin=false grad_refused=tscn=File unrecognized(15),tres.bak=File unrecognized(15),resx=File unrecognized(15),json=File unrecognized(15) refused_files_absent=true scene_scn=OK(0) scene_res=OK(0) scn_eq_res=true both_reload=true scene_tres_refused=File unrecognized(15)
```

- A plain `Gradient` round-trips to text (`.tres`, 101 B, `[gd_resource type="Gradient"
  format=3]` + `[resource]` block) and to binary (`.res`, 354 B, `RSRC` magic), and both
  **reload with equal values** **[M]**.
- **These two files are byte-identical across processes**: the shas above are the same in
  all 9 canonical + loadtest receipts (and in the discovery runs) **[M]** — a resource
  save with no nodes and no external references is reproducible.
- `PackedScene` → `.scn` and `.res` are **the same binary bytes** (`scn_eq_res=true`); the
  `.scn`/`.res` payloads are *not* cross-process stable (node ids) **[M]**.
- Extensions are matched **exactly**: `.tres.bak`, `.resx`, `.json`, and `.tscn` for a
  non-scene resource are refused with `ERR_FILE_UNRECOGNIZED(15)`, **no file is created,
  and nothing is printed** — a silent failure if the return value is ignored **[M]**.
  `.tres` for a PackedScene is refused the same way **[M]**.

### 3.4 Scene determinism (`det`, `discover9`) — [M]

```
R96 det text_a=[gd_scene format=3]||[sub_resource type="Gradient" id="Gradient_1u3dt"]|colors = PackedColorArray(0.1, 0.2, 0.3, 1, 0.4, 0.5, 0.6, 1)||[node name="DetRoot" type="Node2D" unique_id=#]|position = Vector2(5, 6)||[node name="Line" type="Line2D" parent="." unique_id=#]|gradient = SubResource("Gradient_1u3dt")|
R96 det text_pin=[gd_scene format=3]||[sub_resource type="Gradient" id="subpinned"]|colors = PackedColorArray(0.25, 0.5, 0.75, 1, 0, 0, 0, 1)||[node name="PinRoot" type="Node2D" unique_id=111111]||[node name="PinLine" type="Line2D" parent="." unique_id=222222]|gradient = SubResource("subpinned")|
PASS … det save=OK(0) same_obj_resave=OK(0) unpinned_sha_len=64 two_builds_same=false subid_minted=true subid_settable=true bundle_keys=conn_count,conns,editable_instances,id_paths,names,node_count,node_ids,node_paths,nodes,variants,version bundle_version=3 node_ids_len=2 pinned_save=OK(0) pinned_save2=OK(0) pinned_sha=a9041c7939a77470f126e51458f7bb14e9a5b1a36fba46bbcbf5c8a572b84fb9 two_pinned_builds_same=true pinned_unique_ids=true instantiate_ok=true
```

`discover9` (six fresh processes, the frozen `pack_basic` construction, raw values):

```
R96 uidvar save=OK size=193 bytes ids=288446871,1959357352 widths=9,10
R96 uidvar save=OK size=194 bytes ids=1036010547,1570537358 widths=10,10
R96 uidvar save=OK size=193 bytes ids=961994085,1118615552 widths=9,10
R96 uidvar save=OK size=193 bytes ids=927845416,1142635696 widths=9,10
R96 uidvar save=OK size=193 bytes ids=1692937132,217489373 widths=10,9
R96 uidvar save=OK size=193 bytes ids=1457060877,490325017 widths=10,9
```

- **A scene save is byte-stable for one in-memory resource but not across processes**:
  re-saving the same `PackedScene` (or the scene loaded back from disk) is byte-identical,
  while two identical constructions differ — because every node gets a random
  `unique_id` (6/6 fresh processes differ; the file size moves 193/194 bytes with the
  digit width) **[M]**. The masked texts are identical across all 9 processes, so
  `unique_id` is the **only** source of variance in a scene with no ext resources **[M]**.
- The random ids live in the **bundle dict** (`_get_bundled_scene()`), whose keys are
  `conn_count, conns, editable_instances, id_paths, names, node_count, node_ids,
  node_paths, nodes, variants, version` with `version=3` **[M]**; `node_ids` holds one
  entry per node.
- **Determinism recipe [M]:** pin `d["node_ids"]` and every subresource's
  `resource_scene_unique_id`, then `PackedScene.new()._set_bundled_scene(d)` → the saved
  `.tscn` is **byte-identical across processes**: `pinned_sha=a9041c7939a77470f126e51458f7bb14e9a5b1a36fba46bbcbf5c8a572b84fb9`
  in **9/9 processes** (6 canonical + 3 loadtest) plus two earlier discovery runs. The
  pinned scene still instantiates normally **[M]**. The subresource id is **settable**
  (`id="subpinned"` appears verbatim) and is minted lazily at first save
  (`Gradient_1u3dt` here) **[M]**.

### 3.5 Id generation (`discover3`, `discover5`, `discover7`, `discover8`, `extres`) — [M]

```
R96 subid_seq n0=Gradient_6nckn err=OK(0)
R96 subid_seq extra=1 subid=Gradient_pk8cq err=OK(0)
R96 subid_seq extra=2 subid=Gradient_to5g3 err=OK(0)
R96 subid_seq extra=3 subid=Gradient_cs0oe err=OK(0)
R96 subid_seq two_fresh_ids=,          # fresh resources have an EMPTY scene unique id
R96 extid_same save1=OK(0) id1=1_xltw3
R96 extid_same save2=OK(0) id2=1_4vr82 same_obj=false   # SAME PackedScene object resaved
R96 extid_same gen_scene_unique_id=7hu1n len=5
R96 extid_pin readback=pinned_ext …    # resource_scene_unique_id on the referenced resource
R96 extid_pin save=OK(0) text=[gd_scene format=3]||[ext_resource type="Gradient" path="user://r96/e8p.tres" id="1_7xqbi"]|…
R96 pin_general save1=OK(0) sha1=91bdbaf99e0ea07af00047e7a852fac75b6af5974b6e0e0ab703c71aa72c02a6
R96 pin_general save2=OK(0) sha2=6bed9ec4fb4b6cf67a9d010f1d74235323ce5938efcb4e39d0e5bd97ed313893 same=false
```

- Subresource ids and `ext_resource` ids are drawn from a **deterministic per-process
  generator sequence**: the same construction order produces the same values in every
  fresh process (9/9), but changing how many ids were drawn before changes them (0/1/2/3
  preceding allocations → four different subids) **[M]**. Do **not** treat them as stable
  identifiers across refactors.
- **Ext ids are re-minted on every save call — even for the same in-memory object**
  (`1_xltw3` → `1_4vr82`) **[M]**, and no public API controls them:
  `resource_scene_unique_id` on the referenced resource, `set_id_for_path`, and
  `ResourceUID.add_id` all leave the emitted id random **[M]**.
  `Resource.generate_scene_unique_id()` returns a 5-char id, the same shape as the
  `1_xxxxx` suffix **[M]** (same generator is **[I]**).
- **Bound on the recipe:** a scene that references an external resource **cannot be made
  byte-stable** — `pin_general` (3 nodes + one ext resource + one nested subresource, all
  node ids pinned, inner subresource id pinned) still saves to two different shas in one
  process (`same=false`) **[M]**.

### 3.6 `uid://` surface (`uid`, `discover5`, `discover6`) — [M]

```
R96 uid tres_head=[gd_resource type="Gradient" format=3] scene_text=[gd_scene format=3]||[ext_resource type="Gradient" path="user://r96/uid_ext.tres" id="1_seim5"]|…
PASS … uid create_id_text_prefix=true create_id_unregistered=true get_id_path_unknown_empty=true roundtrip=103876737118377468 roundtrip_text=uid://bqk3m5n7qar1 invalid_text=-1 invalid_text_back=uid://<invalid> invalid_id=-1 tres_save=OK(0) header_has_uid=false saver_id_before=-1 loader_uid_before=-1 loader_uid_after_add=4242 saver_id_after_add=-1 scene_save=OK(0) ext_line_has_uid=false header_has_uid=false any_uid_token=false
R96 setuid save=OK(0) head=[gd_resource type="Gradient" format=3] id_for_path=-1 uid=-1     # set_uid BEFORE save
R96 setuid2 after_set head=[gd_resource type="Gradient" format=3] uid=-1 id_path= has=false  # set_uid AFTER save (file exists)
R96 setuid_res after_set sha=3bebc5deee1b333c changed=false uid=-1 has=false               # binary .res, file bytes unchanged
R96 uidload loaded=true inst=true grad_is_loaded=true grad_path=user://r96/uidload_ext.tres
```

- **Headless saves never emit `uid://`**: no `uid=` in a `[gd_resource]`/`[gd_scene]`
  header, no `uid=` in an `ext_resource` line, for `user://` **or** `res://` paths, text
  or binary **[M]**. `ResourceSaver.get_resource_id_for_path` and
  `ResourceLoader.get_resource_uid` stay `-1` for a saved path **[M]**, and
  `ResourceUID.add_id(id, path)` populates `ResourceUID.get_id_path`/`get_resource_uid`
  (`4242`) **without changing the emitted text** **[M]**.
- `ResourceUID.create_id()` mints an id that is **not registered**
  (`has_id=false`, `get_id_path=""` + `ERROR: Invalid UID.`); `id_to_text` round-trips
  engine-minted ids, but a hand-written text decodes to the canonical form
  (`uid://bqk3m5n7qar1`), and garbage text maps to `INVALID_ID=-1` /
  `uid://<invalid>` **[M]**.
- **The `id_to_text` length is NOT fixed** — the scout's own first key
  (`len == 18 or len == 19`) was **load-bimodal**: 18/19 in 8/9 receipts, **17** in one
  loadtest rep (leading digits are dropped). The shipped key is the stable
  `create_id_text_prefix=true`; do not assert a length **[M]** (see F27).
- `ResourceSaver.set_uid(path, id)` is a **no-op**: on an existing `.tres` or `.res` the
  file bytes are unchanged and `ResourceLoader.get_resource_uid` stays `-1`
  (`ResourceUID.has_id(4242)` false); called on a path that does not exist it prints
  `ERROR: Method/function failed. Returning: ERR_CANT_OPEN` +
  `ERROR: Cannot open file '<path>'.` **[M]**.
- A hand-written `.tscn` whose `ext_resource` carries a `uid="uid://…"` the registry does
  not know loads **successfully** with a **WARNING**
  (`ext_resource, invalid UID: uid://… - using text path instead: <path>`) — the **path**
  wins, and the warning is classifier-inert (no `ERROR:`) **[M]**.

### 3.7 `take_over_path` + cache (`takeover`, `cache`, `discover4`) — [M]

```
PASS … takeover save=OK(0) path_after_save_empty=true load_after_save_is_new=true b_wins=true b_path_is_p=true a_path_empty=true c_wins=true b_displaced=true disk_sha=ad113a5cb9144c27c0461d59b0c4164804f769acb97990f688b978e3c3c98716 disk_unchanged=true exists=true exists_missing=true has_cached=true get_cached_ref=true deps_empty=true
PASS … cache save=OK(0) default_identity=true ignore_distinct=true ignore_path_kept=true ignore_two_distinct=true external_write=OK(0) stale_after_write=[(1.0, 0.0, 0.0, 1.0), (0.0, 0.0, 0.0, 1.0)] repl_same_object=true repl_refreshed=[(0.0, 1.0, 0.0, 1.0), (0.0, 0.0, 0.0, 1.0)] after_repl_identity=true ignore_refreshed=[(0.0, 1.0, 0.0, 1.0), (0.0, 0.0, 0.0, 1.0)] reuse_is_repl=true cached_now_refreshed=[(0.0, 1.0, 0.0, 1.0), (0.0, 0.0, 0.0, 1.0)] exists_dir=false exists_empty=false
R96 chgpath2 save2=OK(0) path_after=user://r96/cp1.tres load_p2_is_same=false     # FLAG_CHANGE_PATH on a loaded resource
R96 chgpath setpath_then_save=OK(0) path_after=                                    # FLAG_CHANGE_PATH after set_path
```

- **`ResourceSaver.save` does not set `resource_path`** — `load(path)` immediately after
  `save(res, path)` returns a **different** object (`load_after_save_is_new=true`) **[M]**.
  `take_over_path` does claim the cache: after `b.take_over_path(p)`, `load(p)` is `b`;
  a second `c.take_over_path(p)` displaces `b` (`b.resource_path` becomes `""`), and the
  **file on disk is untouched** (`disk_sha` unchanged) **[M]**.
- Cache modes: default `REUSE` returns the cached object (`default_identity=true`) and
  keeps returning it **after the file changed on disk** (stale colours measured) **[M]**;
  `CACHE_MODE_REPLACE` returns the **same object identity** with the **new on-disk
  content** loaded into it (`repl_same_object=true`, `after_repl_identity=true`,
  `reuse_is_repl=true`) **[M]**; `CACHE_MODE_IGNORE` returns a **fresh, uncached** object
  that **still carries `resource_path`** (`ignore_path_kept=true`) and never affects the
  cache **[M]**. `ResourceLoader.exists(<dir>)` and `exists("")` are `false` **[M]**.
- A type hint is ignored: `load(p, "PackedScene")` returns the `Gradient` stored in the
  file **[M]**. `set_path` on a path already claimed by a cached resource is **refused**
  (`ERROR: Another resource is loaded from path '…' (possible cyclic resource inclusion).`,
  `resource_path` stays empty) **[M]**.

### 3.8 Subresources (`subres`) — [M]

```
R96 subres text=[gd_scene format=3]||[sub_resource type="Gradient" id="#"]|colors = PackedColorArray(1, 0, 0, 1, 0, 0, 1, 1)||[node name="SubRoot" type="Node2D" unique_id=#]||[node name="Line" type="Line2D" parent="." unique_id=#]|gradient = SubResource("#")|
R96 subres text_local=[gd_scene format=3]||[sub_resource type="Gradient" id="Gradient_bx1ia"]|resource_local_to_scene = true||[node name="LocalRoot" type="Node2D" unique_id=#]||[node name="LocalLine" type="Line2D" parent="." unique_id=#]|gradient = SubResource("Gradient_bx1ia")|
PASS … subres save=OK(0) subid=Gradient_643c0 subid_present=true shared_across_instances=true shared_with_source=true mutation_leaks=true local_save=OK(0) flag_in_file=true local_shared=false local_leak=false nest_save=OK(0) nested_reuses_subid=true dup_shallow_distinct=true dup_deep_distinct=true
```

- **Subresources are shared, not copied**: two `instantiate()` calls return nodes whose
  `gradient` is the **same object**, and that object is also **the source resource the
  packer was given** (`shared_with_source=true`); mutating one instance's gradient is
  visible in the other (`mutation_leaks=true`) **[M]** — the classic shared-material
  hazard, measured.
- `resource_local_to_scene = true` flips this: each instance gets its own copy
  (`local_shared=false`) and the mutation does **not** leak (`local_leak=false`); the flag
  is written into the file (`flag_in_file=true`) **[M]**.
- `duplicate()` and `duplicate(true)` both produce distinct objects **[M]**. A nested
  subresource (`GradientTexture2D.gradient`) references the **same** sub id as the outer
  reference — one `[sub_resource]` block, two references **[M]**.

### 3.9 External resources (`extres`) — [M]

```
R96 extres t1=[gd_scene format=3]||[ext_resource type="Gradient" path="user://r96/ext.tres" id="#"]||[node name="ExtRoot" type="Node2D" unique_id=#]||[node name="ExtLine" type="Line2D" parent="." unique_id=#]|gradient = ExtResource("#")|
R96 extres t3=[gd_scene format=3]||[sub_resource type="Gradient" id="#"]|colors = PackedColorArray(1, 0, 0, 1, 0, 1, 0, 1)||[node name="ExtRoot" type="Node2D" unique_id=#]||[node name="ExtLine" type="Line2D" parent="." unique_id=#]|gradient = SubResource("#")|
R96 extres t4=[gd_scene format=3]||[sub_resource type="Gradient" id="Gradient_u756m"]|colors = PackedColorArray(1, 0, 0, 1, 0, 1, 0, 1)||[node name="NoPathRoot" type="Node2D" unique_id=#]||[node name="NoPathLine" type="Line2D" parent="." unique_id=#]|gradient = SubResource("Gradient_u756m")|
PASS … extres ext_save=OK(0) save=OK(0) save2=OK(0) save_same_obj=OK(0) ext_line=true id_prefix=true id_stable_across_saves=false id_stable_same_obj_resave=false gen_id_len=5 inst_is_loaded=true two_instances_share=true inst_path_is_ext=true deps=["user://r96/ext.tres"] bundle_flag=OK(0) inlined_as_subresource=true no_ext_line=true nopath_save=OK(0) serialized_as_subresource=true no_ext_line=true relative_flag=OK(0) keeps_path=true
```

- A node property holding a resource **with a `resource_path`** is serialized as an
  `[ext_resource type="…" path="…" id="1_xxxxx"]` and the instantiated node's property is
  the **cached loaded object** (`inst_is_loaded=true`), shared by every instance
  (`two_instances_share=true`); `ResourceLoader.get_dependencies(path)` reports the ext
  path **[M]**.
- A resource **without** a path (a runtime `Gradient`) is serialized as a
  `[sub_resource]` instead — no ext line **[M]**.
- `FLAG_BUNDLE_RESOURCES` **inlines** the external resource as a `[sub_resource]` and
  removes the `ext_resource` line entirely **[M]**.
- `FLAG_RELATIVE_PATHS` leaves a `user://` path **absolute** (no relativization) **[M]**.
- The `1_xxxxx` id is **not stable** — neither across two constructions
  (`id_stable_across_saves=false`) nor for the same object resaved
  (`id_stable_same_obj_resave=false`) **[M]**.

### 3.10 Edit states and instantiation edges (`editstate`, `edges`) — [M]

```
PASS … editstate save=OK(0) states=s0[kids=1,owner=true,name=EditRoot,ph=false,ed=false]|s1[…identical…]|s2[…identical…]|s3[…identical…] scene_file_is_path=true part_of_edited=false editable_readback=true placeholder_readback=true unique_name_before=false unique_name_after=true root_placeholder=false
R96 edges groups_text=[gd_scene format=3]||[node name="GRoot" type="Node2D" unique_id=#]||[node name="GChild" type="Node2D" parent="." unique_id=# groups=["grp_a", "grp_b"]]|
PASS … edges save=OK(0) inst_names=NameRoot,NameRoot added_names=NameRoot,@Node2D@2 auto_renamed=true state_path_is_p=true duplicate_cls=PackedScene packed_twice_same_object=false groups_save=OK(0) state_groups=["grp_a", "grp_b"] inst_groups=grp_a,grp_b owner_paths=ORoot:.:,OChild:./OChild:.,OGrand:./OChild/OGrand:.
```

- **All four `GEN_EDIT_STATE_*` values are observationally identical in headless** (child
  count, child owner, root name, placeholder flag, `is_editable_instance`) **[M]**;
  `set_editable_instance`/`is_editable_instance` and
  `set/get_scene_instance_load_placeholder` round-trip **in memory** **[M]**;
  `is_part_of_edited_scene()` is `false` and `unique_name_in_owner` starts `false` and is
  settable **[M]**.
- `instantiate()` twice yields two nodes both named after the saved root; adding both to a
  parent auto-renames the second (`@Node2D@2`) **[M]**. Groups survive the round trip
  (`groups=["grp_a", "grp_b"]` in the file, `&"grp_a"`/`&"grp_b"` in the instance) **[M]**.
- `PackedScene.pack()` called twice on the same node yields **different PackedScene
  objects** (`packed_twice_same_object=false` — consistent with fresh node ids) **[M]**.

### 3.11 Refusals (`refuse`) — [M]

```
PASS … refuse save_missing_dir=Can't open(19) no_file=true save_null=Invalid parameter(31) save_empty_path=Invalid parameter(31) save_no_ext=File unrecognized(15) save_dir=File unrecognized(15) load_missing_null=true load_dir_null=true load_empty_null=true pack_null=Invalid parameter(31) empty_can_instantiate=false empty_instantiate_null=true relative_save=OK(0) relative_file_created=true relative_in_project_dir=true deleted=true set_path_collision_refused=true
```

- `ResourceSaver.save` into a **missing directory** → `ERR_CANT_OPEN(19)` +
  `ERROR: Cannot save file '<path>'.`, **no file**; `FileAccess.open` on a missing
  directory returns **null** (it does not create directories either) **[M]**.
- `save(null, path)` → `ERR_INVALID_PARAMETER(31)` (`Can't save empty resource to path …`);
  `save(res, "")` → `31` (`Can't save resource to empty path …`); `save(res, <dir>)` and
  `save(res, <unknown ext>)` → `15` with **no printed error** **[M]**.
- `load(<missing>)`, `load(<dir>)`, `load("")` all return **null** with ERROR lines (all
  thirteen exact strings are in `author-rows.py.txt` `EXPECTED_ERRORS`) **[M]**.
- `PackedScene.new().pack(null)` → `31` + `ERROR: Parameter "p_scene" is null.` and leaves
  an **empty** PackedScene (`can_instantiate=false`); `instantiate()` on it returns
  **null** + `ERROR: Failed to instantiate scene state of "", node count is 0. …` **[M]**.
- A **relative save path resolves against the project dir**: `save(res,
  "r96_relative.tres")` returns `OK(0)` and creates `<project>/r96_relative.tres`
  (= `res://r96_relative.tres`; `relative_in_project_dir=true`), which is invisible to a
  `res://`-only export; the probe deletes it again (`deleted=true`) **[M]**.

---

## 4. How the laws were found (falsification-driven discovery)

The discovery probes were written to be wrong on purpose; the following first-pass
assumptions were refuted by their own output and drove the frozen probe's design:

1. **`PackedScene.pack(root)` is the Godot-3 static factory** → **REFUTED**: it is an
   instance method returning `Error`; the static call is a parse error.
2. **`ResourceSaver.save` creates missing directories** → **REFUTED**: `ERR_CANT_OPEN(19)`,
   and `FileAccess.open` does not create them either.
3. **A saved scene is byte-identical across runs** → **REFUTED**: `unique_id=` is random
   per node (6/6 processes differ).
4. **Subresource ids are random per process** → **REFUTED** (they are a deterministic
   per-process sequence — same construction, same id in 9 processes) — but **the sequence
   is order-sensitive** (0/1/2/3 preceding allocations → four different ids), so the
   *weaker* claim ("stable for a frozen construction") is what survived.
5. **Ext ids are derived from the path** → **REFUTED**: re-minted on every save, even for
   the same object.
6. **`set_id_for_path` / `resource_scene_unique_id` control the ext id** → **REFUTED**.
7. **`ResourceSaver.set_uid` mints a uid** → **REFUTED** (no-op on existing text/binary;
   `ERR_CANT_OPEN` on a missing path).
8. **`FLAG_CHANGE_PATH` sets `resource_path`** → **REFUTED** in four measurements
   (fresh resource + loaded resource, `user://` + `res://`).
9. **`CACHE_MODE_REPLACE` returns a new object** → **REFUTED**: identity is preserved and
   the content is refreshed into the same object.
10. **Subresources are copied per instance** → **REFUTED**: shared with each other *and*
    with the source object the packer was given.
11. **`GEN_EDIT_STATE_*` changes the instantiated tree** → **REFUTED**: four states,
    identical observables.
12. **A big-endian `.res` round-trips** → **REFUTED**: it reloads as **zeroed** data.
13. **The pinned-bundle recipe generalizes to any scene** → **REFUTED**: a scene with an
    `ext_resource` stays non-reproducible (`pin_general same=false`).
14. **A leaked node holding a cached resource is harmless** → **REFUTED**: the engine
    prints `ERROR: 1 resources still in use at exit …` — a **row-killer** for the
    production classifier (and freeing a `Resource` raises
    `SCRIPT ERROR: Attempted to free a RefCounted object.`).

---

## 5. Hazards recorded (for the author and the boundary seat)

1. **`unique_id=` makes every `.tscn`/`.scn` non-reproducible** (§3.2/§3.4). Hashing,
   diffing, or caching a saved scene across builds needs the bundle pin.
2. **`ext_resource` ids are re-minted on every save** (§3.5) — a scene that references any
   external resource can never be byte-stable; there is no public lever.
3. **Subresources are shared across instances and with the source object** (§3.8) —
   runtime mutation of a subresource leaks into every instance. Use
   `resource_local_to_scene = true` (or `duplicate()` before assigning).
4. **`ResourceSaver.save` does not create directories** (§3.11) — `ERR_CANT_OPEN(19)`,
   no file, one ERROR line. `DirAccess.make_dir_recursive_absolute` first.
5. **An unknown extension fails silently** (§3.3): `ERR_FILE_UNRECOGNIZED(15)`, **no**
   printed error, no file. Never ignore the return value.
6. **`save()` does not set `resource_path`** (§3.7): `load(path)` right after a save
   returns a *different* object; `take_over_path` is the way to make them the same.
7. **`FLAG_CHANGE_PATH` is a no-op on this build** (§3.7) — code that relies on it leaves
   the resource with an empty path.
8. **Default `load()` returns stale content after an external write** (§3.7). Hot reload
   must use `CACHE_MODE_REPLACE` (identity-stable refresh) or `CACHE_MODE_IGNORE`.
9. **`CACHE_MODE_IGNORE` still sets `resource_path`** (§3.7) — `is_built_in()` is not a
   "did this come from disk" test for such objects.
10. **Sub/ext ids are sequence-dependent** (§3.5): don't use them as identifiers in tests
    or save games.
11. **`pack()` silently drops ownerless nodes and nodes owned by an intermediate node**
    (§3.2). Every node you want in the scene needs `owner = <pack root>`.
12. **`set_owner` refusal leaves `owner` null with only an engine ERROR line** (§3.2) — a
    dropped node, not a crash, so it can hide in a build.
13. **`ResourceSaver.set_uid` is unusable headless** (§3.6): no-op on existing files,
    `ERR_CANT_OPEN` otherwise.
14. **An unknown `uid://` in a `.tscn` is only a WARNING** (§3.6) and the path is used —
    uid-based lookup is not a substitute for path correctness.
15. **A big-endian `.res` reloads as zeroed data** (§5 note, `flags` discovery) — no
    endian detection on load.
16. **A relative save path lands in the project dir** (§3.11) and would be exported.
17. **Leaked nodes that hold a cached resource print `ERROR: N resources still in use at
    exit`** (§4.14) — a row-killer; free every node you build, and drop resource refs.
18. **`RefCounted.free()` is a `SCRIPT ERROR:`** — never `free()` a `Resource`; drop the
    reference.
19. **Do not assert the length of a `uid://` text** (§3.6/F27) — the canonical encoder
    drops leading digits, so the length is 17–19 depending on the id.
20. **A node leaked at exit that holds a cached resource prints
    `ERROR: N resources still in use at exit`** — the `edges` cell initially leaked two
    inline `instantiate()` nodes and had to be fixed; free every instance you create.

---

## 6. Author directives (exact)

### 6.1 Verbatim-ready rows (13, exec-checked)

`corpus/live/r96-scout/author-rows.py.txt` holds the 5-tuple sets and the
`EXPECTED_ERRORS` dict; `python3 verify_rows.py` classifies every row against **every**
canonical + loadtest receipt with the production `classify_process` (AST-extracted from
`corpus/fixtures/run_battery.py`, segment sha256 `749fa060…` — the same segment
r89–r95 pinned):

- **`ROWS` (full-line): 114/114 receipts accepted, `rejected=[]`.**
- **`ROWS_PREFIX`: 114/114 accepted, `rejected=[]`** — identical except that
  `r96_scene_io_census` stops before its `SceneState` method list (`ss_methods=…`), the one
  pure engine-surface block the other twelve cells already exercise.
- `expected_errors` additions: `ownership` (2 strings) and `refuse` (13 strings), both
  byte-stable across all 9 receipts each; every other cell is `ERROR:`-clean with 0 B
  stderr.
- **End-to-end smoke:** `python3 smoke_battery.py` runs all 13 rows inside a real battery
  scratch project (renamed project, 8 s bound, merged streams) → **13/13 PASS**.

Row names / arms / signature lengths:

| case | arm | sig len |
|---|---|---|
| `r96_scene_io_census` | `census` | 1884 |
| `r96_scene_io_pack_basic` | `pack_basic` | 435 |
| `r96_scene_io_ownership` | `ownership` | 294 |
| `r96_scene_io_formats` | `formats` | 584 |
| `r96_scene_io_det` | `det` | 471 |
| `r96_scene_io_uid` | `uid` | 444 |
| `r96_scene_io_takeover` | `takeover` | 350 |
| `r96_scene_io_cache` | `cache` | 502 |
| `r96_scene_io_subres` | `subres` | 313 |
| `r96_scene_io_extres` | `extres` | 450 |
| `r96_scene_io_editstate` | `editstate` | 430 |
| `r96_scene_io_refuse` | `refuse` | 480 |
| `r96_scene_io_edges` | `edges` | 332 |

`expected_errors` (exact strings in `author-rows.py.txt`):

```python
'r96_scene_io_ownership': (
    'ERROR: Invalid owner. Owner must be an ancestor in the tree.',
    'ERROR: Condition "p_owner == this" is true.',
),
'r96_scene_io_refuse': (
    "ERROR: Cannot save file 'user://r96_absent_dir_xyz/deep/x.tscn'.",
    "ERROR: Can't save empty resource to path 'user://r96/null.tscn'.",
    "ERROR: Can't save resource to empty path. Provide non-empty path or a Resource with non-empty resource_path.",
    "ERROR: Cannot open file 'user://r96/nope.tscn'.",
    "ERROR: Failed loading resource: user://r96/nope.tscn.",
    "ERROR: Error loading resource: 'user://r96/nope.tscn'.",
    "ERROR: Resource file not found: user://r96 (expected type: unknown)",
    "ERROR: Error loading resource: 'user://r96'.",
    "ERROR: Resource file not found: res:// (expected type: unknown)",
    "ERROR: Error loading resource: ''.",
    'ERROR: Parameter "p_scene" is null.',
    'ERROR: Failed to instantiate scene state of "", node count is 0. Make sure the PackedScene resource is valid.',
    "ERROR: Another resource is loaded from path 'user://r96/collide.tres' (possible cyclic resource inclusion).",
),
```

Probe file lands at `corpus/fixtures/scene_io_lattice.gd` (sha256 `2eded40b…`,
self-contained `SceneTree` script, battery `--arm=` convention). Insert the rows ahead of
the crash/descendant tail like prior blocks; no other fixture change is needed and the
only `expected_errors` additions are the two dict entries above.

### 6.2 What to pin and what not to pin

1. **Pin the `PASS scene_io_lattice …` line** — it carries the arm name, so the r88
   silent-fallback failure cannot recur.
2. **Pin the pinned-bundle sha256** (`det pinned_sha=a9041c…b84fb9`) — it is the round's
   only cross-process byte-level claim, and it survived 9 processes.
3. **Pin the plain-resource shas** (`formats grad_tres sha=94ca8c…`, `grad_res
   sha=6f1353…`) — text and binary resource saves are reproducible; these are the
   byte-level baseline the scene case violates.
4. **Do not pin raw `unique_id`s, subresource ids, ext ids, `1_xxxxx` strings, object
   ids, RIDs, or file paths containing a process-specific token** — the probe masks them
   before printing; the author must not re-introduce them.
5. **Do not add a length assertion on `ResourceUID.id_to_text`** — 17–19 chars measured
   (one loadtest rep produced 17; the shipped key is the `uid://` prefix check).
6. **Keep the `ownership`/`refuse` allowlists exact** — the classifier rejects any
   `ERROR:` line not in the list; the strings above are the measured set.
7. **No envelope is needed for any cell** — 13/13 single-valued across canonical +
   loadtest + smoke.
8. **A probe that keeps a node (or a resource reference) alive at exit is rejected** —
   free everything (`ERROR: N resources still in use at exit` / `Attempted to free a
   RefCounted object.`).

---

## 7. Falsification list

| id | hypothesis (must-differ input) | result |
|---|---|---|
| F1 | `PackedScene.pack(root)` is a static factory returning a PackedScene (Godot-3 API) | **REFUTED [A]** — parse error: "Cannot call non-static function `pack()` on the class `PackedScene` directly" |
| F2 | `pack()` keeps every child of the packed node | **REFUTED [A]** — ownerless and intermediate-owned nodes are dropped (`packed_names=Root,Owned`) |
| F3 | A saved scene is byte-identical across processes | **REFUTED [A]** — 6/6 fresh processes differ (random `unique_id`; 193/194-byte files) |
| F4 | Subresource ids are random per process | **REFUTED [A]** — same construction ⇒ same id in 9 processes; but sequence-sensitive (0/1/2/3 prior allocations ⇒ 4 ids) |
| F5 | Ext ids are path-derived and stable | **REFUTED [A]** — re-minted per save; even the same object resaved differs |
| F6 | `set_id_for_path` controls the ext id | **REFUTED [A]** — id stays random |
| F7 | `resource_scene_unique_id` on the referenced resource controls the ext id | **REFUTED [A]** — id stays random (`1_7xqbi`) |
| F8 | `ResourceSaver.set_uid` mints/patches a uid | **REFUTED [A]** — no-op on existing `.tres`/`.res` (bytes unchanged), `ERR_CANT_OPEN` otherwise |
| F9 | A headless save writes `uid="uid://…"` | **REFUTED [A]** — no uid in `.tres`, `.tscn`, `res://` or `user://` |
| F10 | `ResourceUID.add_id(path)` makes the saver emit the uid | **REFUTED [A]** — registry updated, text unchanged |
| F11 | An unknown `uid://` in a `.tscn` fails the load | **REFUTED [A]** — WARNING + path fallback, load succeeds |
| F12 | `ResourceSaver.save` creates missing directories | **REFUTED [A]** — `ERR_CANT_OPEN(19)`, no file; `FileAccess.open` also returns null |
| F13 | `FLAG_CHANGE_PATH` sets `resource_path` | **REFUTED [A]** — 4 measurements (fresh/loaded, `user://`/`res://`) |
| F14 | `CACHE_MODE_REPLACE` returns a new object | **REFUTED [A]** — same identity, refreshed content |
| F15 | Default `REUSE` re-reads the file | **REFUTED [A]** — stale colours after an external write |
| F16 | `CACHE_MODE_IGNORE` leaves `resource_path` empty | **REFUTED [A]** — path is kept |
| F17 | Subresources are copied per instance | **REFUTED [A]** — shared across instances **and** with the source object |
| F18 | `resource_local_to_scene = true` still shares | **REFUTED [A]** — per-instance copies, no mutation leak |
| F19 | `GEN_EDIT_STATE_*` changes the instantiated tree | **REFUTED [A]** — four states observationally identical |
| F20 | A big-endian `.res` round-trips | **REFUTED [A]** — reloads as zeroed colours |
| F21 | `FLAG_BUNDLE_RESOURCES` writes an `ext_resource` | **REFUTED [A]** — inlined as `sub_resource`, no ext line |
| F22 | A resource with an empty path referenced from a node becomes an `ext_resource` | **REFUTED [A]** — serialized as a `sub_resource` |
| F23 | `pack(null)` returns null | **REFUTED [A]** — returns an empty PackedScene + `ERR_INVALID_PARAMETER(31)` |
| F24 | The pinned-bundle recipe generalizes to scenes with external resources | **REFUTED [A]** — `pin_general same=false` (ext id + an unpinned nested subid re-mint) |
| F25 | `save(res, path)` sets `resource_path` so a later `load(path)` returns the same object | **REFUTED [A]** — distinct object; only `take_over_path`/`set_path` claim the cache |
| F26 | The four refused extensions fail loudly | **REFUTED [A]** — `ERR_FILE_UNRECOGNIZED(15)` with **no** engine error and no file |
| F27 | `ResourceUID.id_to_text(create_id())` has a fixed length (18–19) | **REFUTED under load [A]** — one loadtest rep returned **17**; the scout's own key was load-bimodal and was replaced by a `uid://` prefix check |

---

## 8. Remaining unknowns / not measured

- **Which generator feeds `unique_id` vs the sub/ext ids** — the two behave differently
  (per-process-varying vs sequence-deterministic); the mechanism is **[I]** only.
- **Whether `unique_id` has runtime semantics** (node identity across reloads, editor
  scene-instance merging) — only the serialized form is characterized here.
- **`_get_bundled_scene`/`_set_bundled_scene` are underscore-private**: the dict layout
  (`version=3`) is pinned in the row, but it is not a documented API and a Godot minor
  bump may change it. Pinning `node_ids` **shorter** than the node count was measured to
  leave the extra node without a `unique_id` line — not characterized further.
- **`FLAG_OMIT_EDITOR_PROPERTIES`** did not strip `editor_description` on a Node; which
  properties it *does* strip was not found.
- **A known/registered `uid://` end-to-end** (registry populated *and* file carrying the
  matching uid, then loading by `uid://` path) was not exercised — only the unknown-uid
  fallback.
- **`.res` binary internals**: only sizes, shas, magic and reload equality were measured;
  `FLAG_SAVE_BIG_ENDIAN`'s zeroed reload is characterized but not root-caused.
- **Threaded loading** (`load_threaded_request`/`get_status`/`get`) — in the census,
  never exercised.
- **Custom format savers/loaders** (`add_resource_format_saver`,
  `get_recognized_extensions`) — untouched.
- **`ResourceUID.path_to_uid`/`ensure_path`/`uid_to_path`/`create_id_for_path`** — only
  `create_id`/`text_to_id`/`id_to_text`/`add_id`/`get_id_path`/`has_id` were exercised.
- **Resource packs** (`ProjectSettings.load_resource_pack`) and encrypted/packed exports —
  out of scope, untouched.
- **Portability**: every value is this host/build/`--headless`/GodotPhysics-free scene IO;
  the file bytes and the `format=3` header are engine-version-bound.

---

## 9. Host cleanup

- **155 launches with retained receipts** (75 canonical + 39 loadtest + 41 discovery)
  plus **13 battery-shaped smoke launches** classified in-process — all `--headless`, all
  `timeout -s KILL`-bounded (30 s for the harness, 8 s for the smoke; none hit), no run
  left running (`pgrep -fa scene_io_lattice` → none). Roughly **590 further launches**
  during probe development (superseded canonical/loadtest passes and discovery
  iterations) are not counted.
- Loadtest hogs: 16 own `yes` processes started and **only their own PIDs killed**
  (`own_hogs_killed=16`, `own_hogs_remaining=0`; `host_yes_remaining` 90–112 — other
  lanes' blocks untouched). **`pkill -x yes` was never used** (the r95 lesson).
- No tracked file written: `git status --porcelain` shows only the concurrent lane's
  ` M corpus/fixtures/run_battery.py` (+74 lines, zero r96/scene_io tokens), their
  untracked `corpus/fixtures/rb_lattice.gd`/`rb_watch.gd`, and untracked `corpus/live/*`.
- Probe file writes go to `user://r96/` and are removed by the probe's `_wipe()`; the
  (empty) `~/.local/share/godot/app_userdata/MechanicOneShotTest/r96/` directory remains
  on the host — outside the repository. The battery-shaped smoke ran in its own
  uniquely-named scratch project (`runs/smoke/<stamp>/scratch`).
- The one relative-path save in the `refuse` cell creates `<project>/r96_relative.tres`
  and deletes it immediately (`find / -name r96_relative.tres` → none).
- `manifest.sha256` covers every artefact under `corpus/live/r96-scout/`.

---

## 10. Evidence index

All under `corpus/live/r96-scout/`; `manifest.sha256` covers every artefact (568 files).

| artefact | path | sha256 (prefix) |
|---|---|---|
| **frozen primary probe, 13 cells** | `probes/scene_io_lattice.gd` | `2eded40b74971c4f` |
| discovery probes #1–#9 | `probes/discover[2..9].gd` | `manifest.sha256` |
| launch project (fixtures `project.godot` byte-copy) | `proj/project.godot` | `8de8b3af9cc737ed` |
| canonical driver (13 cells, 75 runs) | `run_cells.sh` | `28e3098616a716d8` |
| loadtest driver (39 runs, load 95–148) | `run_loadtest.sh` | `e171090bc90e7b44` |
| analyzer → json | `analyze_r96.py` → `runs/analyze_r96.json` | `ec33169028854a96` |
| author rows + builder + verifier | `author-rows.py.txt`, `make_author_rows.py`, `verify_rows.py` | `84e5f7b3ad8294c1` / `b41be47cdb6cf4d7` / `5cd44b05fc207a33` |
| battery-shaped smoke | `smoke_battery.py` → `runs/smoke/<stamp>/` | `b608046be882438e` |
| per-cell receipts (75 × 3 files) | `runs/r96_*.{out,err,rc}` | `manifest.sha256` |
| loadtest receipts (39 × 3 files) | `runs/loadtest/` | `manifest.sha256` |
| discovery receipts | `runs/disc*/`, `runs/disc9/` | `manifest.sha256` |
| receipts summary | `RECEIPTS.md` | `manifest.sha256` |

Reproduce: `bash run_cells.sh && bash run_loadtest.sh && python3 analyze_r96.py &&
python3 make_author_rows.py && python3 verify_rows.py && python3 smoke_battery.py`
