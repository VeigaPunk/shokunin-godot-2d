# game-dev-2d round 96 — boundary (r96-boundary): the saved ids are a function of the **output path and slot**, not of a per-process generator — the scout's "ext ids are re-minted per save / an ext scene can never be byte-stable" is an evidence defect; `unique_id`-only variance is CONFIRMED on a much richer scene; the shallow cache modes do **not** refresh dependencies (the DEEP modes do)

Seat `BOUNDARY` (LEAF) | lane `r96-boundary` | round 96 | host **devin**.
Runtime **Godot `4.7.2.stable.arch_linux.ed1daf0bf`** (`/usr/bin/godot`), `--headless`, 60 tps default.
Repo `~/Projects/shokunin/game-dev-2d-shokunin`; HEAD at session start **`e741cf8`** (*r94 boundary*).
HEAD moved during the session **because other lanes committed** (`f64d9de` r96 scout → … → `2db28ad`
r98 boundary) — this lane made **no commit** and has no r96b token in any tracked diff. Attack corpus:
the r96 scout's frozen probe
(`corpus/live/r96-scout/probes/scene_io_lattice.gd`, sha256 `2eded40b74971c4f…`) + **5 own probes**
(`r96b_seq`, `r96b_var`, `r96b_id`, `r96b_cache`, `r96b_phase`, plus `r96b_size`/`r96b_seed` for the
extra batch) — **544 godot launches with retained receipts**, all `timeout -s KILL 25`, all `rc=0`,
**0 timeouts**, no run left running (~80 further exploratory launches during probe development are not
counted).

**No git mutation, no tracked file written, no commit.** Writes are this report (new, untracked) and
`corpus/live/r96-boundary/**` only. `git status --porcelain` shows only the pre-existing concurrent-lane
churn (` M corpus/fixtures/run_battery.py` + other lanes' untracked files) — no r96b token in any tracked
diff. `manifest.sha256` covers every artefact of this lane.

**`lsp` disclosure.** No `lsp` device in this session and no GDScript language server installed;
`definition`/`references`/`hover` were **unavailable for every file touched**. All symbol work was
therefore done by reading the fixture sources directly (fallback per the seat card); no rename was
required — the attack is behavioral. Every mechanism statement below is marked **[I]** and kept separate
from the measurements.

**Frozen `probeParent` disclosure.** Exactly **one** read-only `ufo-labrat` (L2) was dispatched, with one
bounded hypothesis: *"every condition family has its receipts, all `rc=0`/empty-stderr, and the quoted
token vectors are present and byte-identical across families"* — the result is recorded verbatim in §12.
No second dispatch. As in r91/r95/r96-scout, that seat has no shell/exec; it fell back to reading and
hashing receipts, which is what the hypothesis needed.

**The host is shared.** loadavg **77 → 100** for the whole session (other lanes' batteries and `yes`
blocks: 64–112 host hogs; a concurrent `r98-boundary` lane ran the same matrix shape). `quiet` below
means **"no hogs added by this seat"**, never an idle host. This seat's own 16 hogs were killed by PID
(`own_hogs_killed=16`); **`pkill` was never used** (the r95 lesson).

**Legend:** **[M]** measured (fresh process); **[A]** refutation/ablation; **[I]** inference;
**[?]** unknown; **[U]** unstable payload.

---

## 0. What I ran

| # | batch | conditions | runs | loadavg start→end |
|---|---|---|---|---|
| 1 | `quiet` | 60 tps, no seat hogs | 133 (13 scout cells ×3 + 47 own arms ×2) | 84.32 → 91.74 |
| 2 | `load` | 60 tps + **16 own `yes` hogs** | 120 (13 ×2 + 47 ×2) | 91.74 → 99.69 |
| 3 | `ff1` | `--fixed-fps 1` | 36 (13 ×1 + 23 core arms ×1) | 99.69 → 89.86 |
| 4 | `ff30` | `--fixed-fps 30` | 60 (13 ×1 + 47 ×1) | 89.86 → 80.47 |
| 5 | `ff120` | `--fixed-fps 120` | 36 (13 ×1 + 23 core ×1) | 80.47 → 77.02 |
| 6 | `extra` | seedcheck/fresh2 ×3, size scan ×3, **150 `pack_basic` flip scans** | 159 | 63.80 |

Driver `run_matrix.sh` (one condition family per invocation), `run_extra.sh`, analyzer `analyze_r96b.py`
→ `runs/analyze_r96b.json`, row verifier `verify_repl.py`. Launch project `proj/` is the byte-copy of the
scout's launch project (`project.godot` sha256 `8de8b3af9cc737ed…`, identical to
`corpus/fixtures/project.godot`), plus `proj_alt/` (same, `config/name="MechanicOneShotAlt"`) for the
portability check.

**Attack design.** The scout's three headline claims were re-tested with the *one input its own probes
never varied*: **the output file path**. Their `extres` diagnostic even masks the very token under
suspicion (`t1.replace(id1, "#")`), and their `id_stable_same_obj_resave` compares a save to
`ext1.tscn` with a save to `ext1b.tscn`. Every boundary arm below isolates path, slot, object, call
index, draw history and tick phase.

---

## 1. Verdict table

| # | scout claim (r96-scout.md) | verdict | one-line evidence |
|---|---|---|---|
| 1 | §3.5/L4: "subresource ids **and** `ext_resource` ids are drawn from a deterministic per-process generator sequence … changing how many ids were drawn before changes them" | **REFUTED as a mechanism [A]** | the ids are a function of the **output path + slot**: `mint_two` pa→`Gradient_elxub` / sp→`Gradient_xlqlr` (4 steps, 2 paths, identical in all 5 families); `subextra0/1/3` (0/1/3 extra `Gradient.new()` draws) → **the same** `Gradient_xlqlr` |
| 2 | F5: "Ext ids are path-derived and stable → **REFUTED** … re-minted on every save, even for the same object" | **REFUTED [A] — the ids ARE path-derived; the scout compared two different paths** | `seqA2` (pa,pa) → `1_vwxho,1_vwxho`; `seqAB2` (pa,pb,pa) → `1_vwxho,1_0187o,1_vwxho`; `seq2obj` (two different PackedScenes, same path) → `1_vwxho,1_vwxho`; scout's own compared `ext1.tscn` vs `ext1b.tscn` |
| 3 | hazard 2 / F24: "a scene that references any external resource **can never be byte-stable**"; the pinned recipe "does not generalize" | **REFUTED [A]** | `minimal` (one ext + one sub resource, **only `node_ids` pinned**, fixed path): `sha_raw=c16f3241a476f4de…` identical in 6/6 fresh processes and in all 5 families; scout's `pin_general` compared `gen1.tscn` vs `gen2.tscn` |
| 4 | §3.4: "`unique_id` is the **only** source of variance in a scene with no ext resources" | **CONFIRMED + extended [M]** | `rich` (10 nodes, 6 connections, 3 sub-resources incl. nested + `local_to_scene`, scrambled groups, 8 metadata keys): `sha_uonly=3c89984fd6bde63d…` identical 6/6 quiet + every family; `conn`/`groups`/`meta` identical |
| 5 | L9: "REUSE stale / REPLACE identity-stable refresh / IGNORE fresh" | **INCOMPLETE → partly REFUTED [A]** | shallow `REPLACE` and `IGNORE` do **not** refresh an `ext_resource` dependency (stale red survives both); `REPLACE_DEEP` refreshes it in place; `IGNORE_DEEP` returns a fully fresh graph and leaves the cache untouched |
| 6 | (brief) "check anything claimed stable across ticks" (the r95 k(k−1) lesson) | **no tick-phase coordinate [M]** | `ph0/1/2/5/30` (physics frames) and `pph0/1/2/5/30` (process frames): ext id, sub id, `generate_scene_unique_id()` fingerprint, pinned sha **all identical** |
| 7 | §1/§6.1: all 13 cells `out_uniq=1` — "byte-stable" | **CONFIRMED with one fragile key [M/U]** | all 13 PASS lines replicate the scout's canonical receipt byte-for-byte in 104/104 receipts; but `size_in_190_200` (pack_basic) is a **rare flipper** whose measured support contains a value the assertion rejects (§7) |
| 8 | L2 ownership law: `pack()` silently drops ownerless / intermediate-owned nodes | **extended [A]** | the same silent gate exists for **non-persistent groups and connections**: default `add_to_group(name)` / `connect(sig, cb)` write **nothing** to the file; `persistent=true` / `CONNECT_PERSIST` writes them (sorted) |
| 9 | §8: node unique_id "only the serialized form is characterized" | **new constraint [M]** | ids are bounded `< 2^31` (200/200); a **pinned** `node_ids` value ≥ 2^31 is **silently dropped** (2147483648, 4294967295, 999999999999 → no `unique_id=` line; 2147483647 → written) |
| 10 | §8: "no public lever" for the node id | **CONFIRMED (measured) [M]** | `ClassDB` on `Node`: `has_get=false has_set=false`; only `set/get_scene_file_path`, `set/get_scene_instance_load_placeholder`, `set/is_unique_name_in_owner` |

---

## 2. The headline law: every written id is a function of the **output path and slot** **[M]**

### 2.1 The ext_resource id

`r96b_id` (all arms: 5 condition families, plus 6 fresh-process reps of the same arm):

```
PASS r96b_id seqA2    seq=a:1_vwxho/OK a:1_vwxho/OK                      # same path twice -> SAME id
PASS r96b_id seqAA3   seq=a:1_vwxho/OK a:1_vwxho/OK a:1_vwxho/OK         # three times -> SAME id
PASS r96b_id seqAB2   seq=a:1_vwxho/OK b:1_0187o/OK a:1_vwxho/OK         # path b -> different id, path a unchanged
PASS r96b_id seq2obj  obj1=1_vwxho obj2=1_vwxho                          # two DIFFERENT PackedScenes -> SAME id
PASS r96b_id extshift pre=dg01n,6ddvb,3nsch ext_id=1_vwxho               # 3 prior generate_scene_unique_id() draws -> unchanged
PASS r96b_id twoext   seq=a:1_c7i3r,2_ku7em b:1_cre6b,2_kmhwg a:1_c7i3r,2_ku7em   # slot prefix 1_/2_, suffix = f(path, slot)
PASS r96b_id extother id=1_vwxho                                         # a DIFFERENT ext .tres (path+content) -> SAME id
PASS r96b_seq extseq  ext_ids1=1_efiak ext_ids2=1_f4hst ext_ids1b=1_xfevf # three different paths -> three different ids
```

- `extother` is the clean isolation: the referenced resource is a different `.tres` file with different
  colours, the output path is `pa.tscn` — the id is still `1_vwxho`. ⇒ the id depends on the **output
  path and slot only**, not on the referenced resource, the object, the save index, or the process.
- The `1_`/`2_` prefixes in `twoext` are **slot numbers**, not part of the random-looking suffix; two
  ext resources in one scene get `1_c7i3r` and `2_ku7em`.
- Every one of these vectors is identical in `quiet`, `load` (16 hogs), `--fixed-fps 1/30/120` and in
  the fresh-process reps (`runs/analyze_r96b.json`: `distinct_values=1` for each).

### 2.2 The sub-resource id

```
PASS r96b_id mint_two    seq=pa:Gradient_elxub sp:Gradient_xlqlr pa:Gradient_elxub sp:Gradient_xlqlr
PASS r96b_id subsamepath seq=m0:Gradient_xlqlr m1:Gradient_xlqlr          # two DIFFERENT fresh objects, same path -> same id
PASS r96b_id subcontent  id=Gradient_xlqlr                                # different colours -> same id
PASS r96b_id subextra0   extra=0 id=Gradient_xlqlr
PASS r96b_id subextra1   extra=1 id=Gradient_xlqlr                        # 1 extra Gradient.new() before the build
PASS r96b_id subextra3   extra=3 id=Gradient_xlqlr                        # 3 extra draws before the build
PASS r96b_id subsame     id1=Gradient_elxub id2=Gradient_elxub            # same object, same path, twice -> same id
PASS r96b_id subpath     seq=a:Gradient_elxub b:Gradient_elxub a:Gradient_elxub  # same object, other path -> STICKY (first mint)
```

- The sub id is **minted at the first save from (output path, slot)** and then stored on the resource:
  saving the same object to a second path reuses the first path's value (`subpath`), while a **fresh**
  construction at the same path always yields the same value (`mint_two`, `subsamepath`, `subcontent`).
- **The scout's "extra draws shift the sub id" experiment is an artifact**: their `discover5._subid_seq`
  saved to `seq0.tscn`, `seq1.tscn`, `seq2.tscn`, `seq3.tscn` — four *different paths* — while the
  "extra" manipulation (`for i in extra: Gradient.new()`) mints nothing (ids are minted lazily at save).
  My `subextra0/1/3` hold the path fixed and the id does not move.

### 2.3 `Resource.generate_scene_unique_id()` is not the id oracle **[M]**

```
PASS r96b_id finger0  vals=<8 values>        # 6/6 fresh processes DIFFERENT  (pathless fresh resource)
PASS r96b_id fingerB  vals=dg01n,6ddvb,3nsch,07j4t,2c3ee,pghoq,dqro8,lahlw   # loaded resource: 6/6 identical
PASS r96b_seed seedcheck A=aymj7,… B=1q5w0,… C=rl1nt,… D=8od4a,…  A_eq_B=false A_eq_C=false A_eq_D=false
PASS r96b_seed fresh2 g1=… g2=… eq=false     # two fresh Gradients: different, and different per process
```

`A`/`B` (two loads of the *same* path in one process) each reproduce **byte-identically across 3 fresh
processes** yet differ from each other; a pathless `Gradient.new()` is process-random. So the public
generator is *not* the source of the ids written to files, and its sequence is not "per-process
deterministic" in the sense the scout described. **[I]** the loader-side sequence is seeded per resource
instance (path-derived), the pathless case from process-local entropy; the saver's ids come from the
output path + slot.

### 2.4 The portability check

`proj_alt/` (same project, `config/name="MechanicOneShotAlt"` ⇒ a different `user://` root) gives the
**identical** vectors: `seqA2 a:1_vwxho/OK`, `mint_two pa:Gradient_elxub sp:Gradient_xlqlr`,
`twoext a:1_c7i3r,2_ku7em`. ⇒ the id is a function of the **relative** path, not of the globalized
path — the scheme is project-name/host independent (within this engine build).

---

## 3. The evidence defect behind F5 / F24 / hazard 2

The scout's ext-id conclusion rests on two comparisons in `corpus/live/r96-scout/probes/`:

- `scene_io_lattice.gd` `_arm_extres`:
  `var p1 := BASE + "/ext1.tscn"` … `var p1b := BASE + "/ext1b.tscn"` … `_b(id1 == id1b)` shipped as
  **`id_stable_same_obj_resave=false`** — a *same object, different output path* comparison.
- `discover7.gd` `_pin_general`: `var p1 := BASE + "/gen1.tscn"` / `var p2 := BASE + "/gen2.tscn"` …
  `same=%s` → **`pin_general same=false`**, shipped as F24 ("the recipe does not generalize to scenes
  with external resources").

Both differences are **fully explained by the path change alone** (§2.1): re-running the same
construction twice to *two* paths yields two different ext ids (and two different freshly minted sub
ids), while the same construction to *one* path is byte-identical. The scout's own diagnostics masked
the ext id before printing, so its 9 receipts could not see a cross-process difference either way.

**What this changes [M]:** the correct minimal recipe is
1. `pack()` the scene,
2. pin `d["node_ids"]` (values in `[1, 2^31-1]`),
3. always save to the **same output path**.
No sub-resource pinning is required (they are already path-derived), and no ext id lever is needed.
Proof: `r96b_seq minimal` — one `ext_resource` + one `sub_resource`, only `node_ids` pinned —
`sha_raw=c16f3241a476f4de1484bf07fea7c6a7dc9f5ef8c3408f18eed5f95c6361e0b9` in **6/6 fresh processes**
and in **all five condition families**; `extpin` `sha_raw=a6fa9a9e0c4661fa…` likewise. The scout's
`det pinned_sha=a9041c…` remains valid (it is the all-ids-pinned special case).

---

## 4. `unique_id`-only variance: CONFIRMED, on a scene the scout never packed **[M]**

`r96b_var rich` — 10 nodes; 6 **persistent** signal connections (scrambled connect order, two from the
same source signal); groups added in scrambled order; 8 metadata keys (incl. a `Dictionary`,
`PackedByteArray`, `NodePath`, `Color`, `StringName`); a `Gradient` shared by two `Line2D`s, a
`GradientTexture2D` nesting that same `Gradient`, and a `resource_local_to_scene` `Gradient`;
fractional floats.

```
PASS r96b_var rich save=OK nodes=10 sha_uonly=3c89984fd6bde63d749b3de761f9e19a944b499b193e6fb7c88fb288be6be8c4
  sha_u_sub=9d1963b2c10905ff611aabe6f796e50bb1d8eb7bbefbbabb7f97041658d526de
  pinned_save=OK pinned_nodes=10 pinned_sha=e6675739cc972b2a8c7f414b21dd5e8e043ebdb61dc2e28270c2733b005afa94
```

- `sha_uonly` (the whole file with **only** `unique_id` digits masked) is identical in 6/6 quiet
  processes and in `load`/`ff1`/`ff30`/`ff120` — so the scout's "sole variance" claim survives a much
  wider feature set: connections (`conns`), groups, metadata, nested/shared/local sub-resources.
- Serialization orders are **deterministic and canonical**, not insertion orders:
  `groups=["alpha", "bravo", "mike", "zulu"]` from adds `zulu, alpha, mike, bravo`; connections sorted
  by `(from, to)` — `N0→N2, N0→N5, N1→N4, N2→N0, N3→N1, N4→N3` from a scrambled connect order;
  `metadata/…` written in insertion order (`z_last, a_first, m_dict, k_np, c_col, s_sn, f_frac, i_int`).
- `pinned_sha` (node_ids + the three sub ids pinned) is identical in all 5 families.

**New constraint (§1 #9) [M]:** `idstat` packs 200 nodes → 200 distinct ids, `min=6827419 max=2135253440`,
**0/200 above 2^31**; pinning `node_ids=[1, 2147483647, 2147483648, 4294967295, 999999999999]` writes
only the first two — values ≥ 2^31 are **silently dropped** (the node simply gets no `unique_id=` line,
and `instantiate()` still succeeds). The scout's §8 note "pinning node_ids shorter than the node count
leaves the extra node without a unique_id line" is now characterized as a **value-range gate**, not just
a length gate.

---

## 5. Cache modes: the two DEEP modes are the real hot-reload lever **[M]**

One mode per process (no cross-mode contamination), scene `sc.tscn` referencing external `dep.tres`;
`dep.tres` is rewritten red→green (same byte length) after the scene and dependency are cached:

| mode | scene object | child property (the ext dependency) | dependency object |
|---|---|---|---|
| `REUSE` | same | **red — stale** | red (stale) |
| `REPLACE` | same (refreshed scene) | **red — STALE** | red (stale) |
| `IGNORE` | **fresh** | **red — stale, and the *same cached object*** | red (stale) |
| `REPLACE_DEEP` | same | **green — refreshed, same object** | green (in place) |
| `IGNORE_DEEP` | **fresh** | **green — fresh object** | red — cache untouched |

- The scout's L9 is correct for a **dependency-free** resource (their `cache` cell saves a bare
  `Gradient`), but as a model of the loader it is incomplete: **`REPLACE` refreshes the top-level
  resource only**, and **`IGNORE` does not bypass the cache for external dependencies** — a
  `CACHE_MODE_IGNORE` load of a scene returns a fresh scene whose `ext_resource` properties are still
  the stale cached objects. `IGNORE_DEEP` is the only mode that reads the whole graph fresh **and**
  leaves the cache untouched; `REPLACE_DEEP` is the only identity-stable full refresh.
- Timing/eviction (unstated modes, all stable across families): `repl_uncached` — `REPLACE` on an
  uncached path works and caches; `reuse_delete` — deleting the file does **not** evict the cache
  (`load()` still returns the object, `exists=false`); `reuse_delay` — `REUSE` is still stale after
  `OS.delay_msec(2500)` (no TTL/mtime check); `threaded` — `load_threaded_request` → status
  `THREAD_LOAD_LOADED(3)` → `load_threaded_get` returns the object **and populates the cache**
  (`cached_same_as_got=true`, `has_cached=true`) — the scout's §8 "threaded loading never exercised" is
  now measured, and it is deterministic in all 5 families.

---

## 6. Tick-phase: there is no phase coordinate here (the r95 lesson applied) **[M]**

The r95 boundary found a `k(k−1)` tick-phase cycle behind a "stable" order row. The r96 surface has no
such coordinate:

```
PASS r96b_phase ph0  k=0  ext_id=1_qotou sub_id=Gradient_doj0s gen1=jk34a pinned_sha=c264d6ebfdd2f071841f65a79f759ff31128f0527948fdf53060923b318b001a
PASS r96b_phase ph1  k=1  …identical…        ph2 k=2 …identical…   ph5 k=5 …identical…   ph30 k=30 …identical…
PASS r96b_phase pph0/pph1/pph2/pph5/pph30 (process frames) …identical…
```

Physics-frame and process-frame awaits at k = 0,1,2,5,30 produce the **same** ext id, sub id, global
generator fingerprint, masked-text sha and pinned sha — including under load and `--fixed-fps`. Unlike
r95's `procwait`, a process-frame await here cannot change any of the pinned tokens. (This also closes
the r95-derived question "is the id generator fed by engine frames?" — it is not.)

---

## 7. The one fragile shipped key: `size_in_190_200` **[U]**

`r96_scene_io_pack_basic` asserts `190 ≤ size(basic.tscn) ≤ 200`. The file size is
`174 + len(unique_id_root) + len(unique_id_child)` (confirmed by 1 600 constructions):

```
R96B size n=400 out_of_range=1 min=189 max=194        # first scan (console only, receipt not retained)
R96B size sizes=189:1,190:1,191:18,192:73,193:180,194:127
R96B size lens=10,10:127,10,8:4,10,9:91,7,8:1,7,9:1,8,10:9,8,9:9,9,10:89,9,8:9,9,9:60
runs/extra/size.rep{1,2,3}.out: n=400 out_of_range=0 min=190 max=194  (three retained scans)
```

- The ids are bounded `< 2^31` and their digit widths are random ⇒ the size is random over the measured
  support `[189,194]`; the key is false exactly when `len1+len2 ≤ 15` (the observed `(7,8)` pair → 189).
- **Retained evidence:** 3 × 400-construction scans in `runs/extra/size.rep*.out` (1200 constructions,
  `out_of_range=0`, `min=190`) and **150 runs of the scout's own `pack_basic` arm**
  (`runs/extra/flip_pack_basic.rep1..150.out`) with **0 flips**.
- **Unretained evidence:** the first 400-construction scan produced one 189 (`out_of_range=1`, quoted
  above) — its receipt was not kept (the probe was run interactively before `run_extra.sh` existed; the
  labrat caught this gap, §12), and the single observed **row-key** flip (`scout_pack_basic.rep3.out`,
  `size_in_190_200=false`, first quiet batch) was overwritten when the arm set was re-run with `minimal`
  added. So the *rate* is uncertain: the mechanism predicts ≈0.1 %, the retained scans show 0/1200 and
  0/150.
- Because the row-key flip happened once in 3 runs — ~0.3 % if the rate is 0.1 % — a second candidate
  cause cannot be excluded: the scout's probe writes to a **fixed global base** (`user://r96/`) and
  `_wipe()`s that directory at arm end, so a concurrent lane re-running the same probe can collide with
  another process's save/read window. Either way the key is not a guaranteed PASS: its measured support
  contains a value the assertion rejects, and `verify_rows.py` would reject the row on such a receipt.

---

## 8. The silent-drop gates: non-persistent groups and connections **[A]**

The scout's L2 law ("a node is packed iff `owner == pack root`") has two siblings it never tested:

- `r96b_var conn` with default `connect(sig, cb)` → `nconn=0`: **the connections are silently absent**
  from the saved scene. With `Object.CONNECT_PERSIST` → 6 `[connection …]` lines.
- `r96b_var groups` with default `add_to_group(name)` → **no `groups=` attribute**; with
  `add_to_group(name, true)` → `groups=["alpha", "bravo", "mike", "zulu"]`.
- The scout's own `edges` row used `add_to_group("grp_a", true)` — the persistent variant — so its
  `groups_save` row is correct but does not reveal the gate.
- Both gates are silent (no `ERROR:` line, no warning) — the same hazard class as the ownership law, and
  a build-hiding trap for anything that saves a scene with runtime-made connections.

---

## 9. What survived every attack **[M]**

| attack | runs | result |
|---|---|---|
| 13 scout cells re-run vs the scout's own canonical receipts | 104 receipts over quiet/load/ff1/ff30/ff120 | **all 13 PASS lines + stderr byte-identical** to `r96-scout/runs/r96_<cell>.rep1.{out,err}` (`refuse`/`ownership` carry their allowlisted engine `ERROR:` stderr — 3424 B / 499 B, byte-identical in all 5 families) |
| 16-hog load, loadavg 91.7 → 99.7 | 120 receipts | every boundary arm identical to its quiet receipt (`distinct_values=1` per token) |
| `--fixed-fps 1 / 30 / 120` | 132 receipts | identical |
| tick phase k = 0,1,2,5,30 (physics **and** process frames) | 20 receipts | identical |
| a different project name / `user://` root (`proj_alt`) | 3 arms | identical ids |
| fresh-process repetition (6× per decisive arm) | — | identical |
| **not stable, by design** | — | `finger0` (pathless generator: 5/5 distinct across processes) and `idstat` (its `min`/`max` sample the random ids) — the two arms whose payload is *supposed* to vary |

**Row classification under attack** (`verify_repl.py`, production `classify_process` extracted by AST
from `corpus/fixtures/run_battery.py`, segment sha256 `749fa0607e7707e6` — the same segment r89–r96
pinned): **104/104 receipts accepted, `rejected=[]`** across quiet (39), load (26), ff1 (13), ff30 (13),
ff120 (13). The 13 shipped rows are therefore load- and fixed-fps-stable on this evidence, with the
single caveat of §7.

---

## 10. What an author must know now (no shipping decision here)

1. **Byte-stable ext-resource scenes are possible.** Pin `node_ids` only and keep the output path fixed
   (§2.4/§3). If a row wants an ext-scene determinism receipt, `r96b_seq minimal`'s
   `sha_raw=c16f3241a476f4de1484bf07fea7c6a7dc9f5ef8c3408f18eed5f95c6361e0b9` is the candidate
   (verified 6/6 + 5 families). The shipped `det pinned_sha` stays valid.
2. **`size_in_190_200` should not ship as a strict `[190,200]` key** — it flips at ≈0.25 % (range
   `[189,194]`); widen the bound or drop the key.
3. **Hot reload of a scene/resource graph needs the DEEP modes**; `REPLACE`/`IGNORE` leave
   `ext_resource` dependencies stale (and `IGNORE` still returns the cached dependency object).
4. **A scene save's ids are path-dependent**: two saves of the same construction to two paths differ in
   the ext id (and in freshly minted sub ids). Any tool that diffs or hashes scene files must fix the
   path, or mask ids.
5. **Groups/connections need the persistent flag** to reach the file at all.
6. **`node_ids` must be `< 2^31`** or the pinned value is silently dropped.
7. Do **not** use `Resource.generate_scene_unique_id()` as an id oracle (process-random for pathless
   resources; per-instance sequences otherwise) and do not model the saved ids as a draw sequence.

**Remaining unknowns [?]:** the exact hash/seed formula behind the path+slot ids (no engine source on
this host) **[I]**; whether the scheme survives a Godot minor bump (saver-internal); runtime semantics of
`unique_id`; `.res` binary internals; `FLAG_OMIT_EDITOR_PROPERTIES`; the sub-id stickiness hazard for
tools that reuse one resource object across many scenes (the first path's id wins).

---

## 11. Host cleanup

- 544 launches with retained receipts (385 matrix + 159 extra), all `--headless`, all
  `timeout -s KILL 25` (0 timeouts, 0 non-zero `rc`), no run left running
  (`pgrep -fa "r96b_|scene_io_lattice"` → none).
- Loadtest hogs: 16 own `yes` started and **only their own PIDs killed** (`own_hogs_killed=16`,
  `host yes` remained 64–112 — other lanes' blocks untouched); `pkill` never used.
- No tracked file written: writes are this report and `corpus/live/r96-boundary/**`. Probe writes go to
  `user://r96b/` (wiped per arm); the empty `~/.local/share/godot/app_userdata/MechanicOneShotTest/r96b/`
  and `…/MechanicOneShotAlt/r96b/` directories remain outside the repository. The launch project
  `proj/` and `proj_alt/` are untracked copies of the fixtures' `project.godot`; no `res://` file was
  ever written by this lane (the scout's relative-path hazard was not re-triggered).
- HEAD unchanged (`e741cf8`); no commit, no push, no runtime invocation beyond `/usr/bin/godot`.

---

## 12. Delegated probe (frozen `probeParent`) — result, verbatim

One read-only `ufo-labrat` (L2) was dispatched with the bounded hypothesis of §0 (evidence-chain check
over the receipts). It had no shell (read/grep/glob only) and made zero mutations. Its own words:

> **Headline verdict on the bounded hypothesis: REFUTED as stated.** Token-vector claims (items 1–5)
> are fully confirmed, but the hypothesis's clause "all have empty stderr" is falsified by non-empty
> `scout_*.err` files (Godot ERROR backtraces, e.g. `ff120/scout_refuse.rep1.err`), and the claimed
> `r96b_size` receipt does not exist.

| # | item | labrat verdict | note |
|---|---|---|---|
| 1 | `minimal sha_raw=c16f…e0b9` in all five families | **CONFIRMED** | byte-identical line in `quiet/load/ff1/ff30/ff120` receipts |
| 2 | `seqAB2` `1_vwxho / 1_0187o / 1_vwxho` quiet vs ff120 | **CONFIRMED** | identical strings |
| 3 | `seqA2` same-path-twice; `extseq` three-paths-three-ids | **CONFIRMED** | as shipped |
| 4 | `mint_two` `pa:Gradient_elxub`×2, `sp:Gradient_xlqlr`×2 | **CONFIRMED** | as shipped |
| 5 | `deep_replace` stale red + `ch_same=true`; `deep_repl_deep` green + `ch_same=true` | **CONFIRMED** | as shipped |
| 6 | scout `.rc` all `0` **and** `.err` all empty | **PARTLY REFUTED (the `.err` clause)** | `.rc` 91/91 `0`; but `refuse`/`ownership` stderr is *intentionally* non-empty (allowlisted `ERROR:` text — the scout's own design, byte-identical to its canonical receipts). My hypothesis clause was over-broad; the labrat was right to refute it |
| 7 | 150 flip scans all `true`; size receipt present | **FIRST CONFIRMED / SECOND REFUTED** | 150/150 `size_in_190_200=true`; **no size receipt existed** — a real evidence gap this seat then closed by retaining `runs/extra/size.rep{1,2,3}.out` (§7) |
| 8 | exactly one `own_hogs_killed=16` | **CONFIRMED** | `load/summary.txt:17`; no other summary claims hogs |

**Effect on this report:** items 1–5 (the decisive token vectors) survived an independent read-only
check; the two refuted clauses were *my* hypothesis's fault, not the data's — the `refuse`/`ownership`
stderr is by design (and my analyzer verifies it byte-identical to the canonical receipts), and the
missing size receipt was a genuine retention gap that is now fixed and re-checked. The probe's counts
(385 `.rc` outside `runs/extra`, 150 flip rep-sets) agree with the seat's own counts. No second dispatch.

---

## 13. Evidence index

All under `corpus/live/r96-boundary/`; `manifest.sha256` covers every artefact.

| artefact | path | sha256 (prefix) |
|---|---|---|
| boundary probes | `probes/r96b_{seq,var,id,cache,phase,size,seed}.gd` | `manifest.sha256` |
| scout frozen probe copy (for the replication) | `probes/scene_io_lattice.gd` | `2eded40b74971c4f` (scout's, byte-identical) |
| launch project | `proj/project.godot` | `8de8b3af9cc737ed` |
| portability project | `proj_alt/project.godot` | `manifest.sha256` |
| matrix driver / extra driver | `run_matrix.sh`, `run_extra.sh` | `manifest.sha256` |
| analyzer → json | `analyze_r96b.py` → `runs/analyze_r96b.json` | `manifest.sha256` |
| row verifier (production classifier) | `verify_repl.py` | `manifest.sha256` |
| condition receipts | `runs/{quiet,load,ff1,ff30,ff120}/**` (385 `.rc`) | `manifest.sha256` |
| extra receipts | `runs/extra/**` (159 `.rc`: 150 flip scans, 3 size scans, 6 seed) | `manifest.sha256` |
| analysis dumps | `runs/analysis_all.txt` | `manifest.sha256` |

Reproduce: `bash run_matrix.sh quiet && bash run_matrix.sh load && bash run_matrix.sh ff1 &&
bash run_matrix.sh ff30 && bash run_matrix.sh ff120 && bash run_extra.sh && python3 analyze_r96b.py &&
python3 verify_repl.py`
