# r105 seat report — R105Critic (critic)

Verbatim final output of L2 `W2RoundGameDev2d.R105Critic` (round 105, batched swarm; transcript `history://W2RoundGameDev2d.R105Critic` is session-scoped and not evidence — this file is).

---

## Axes and results

- **Coverage (C1):** the isolation fix must survive exact-row and reversed-order checks.
- **Calibration (C2):** quality criteria must have usable checks and traceable motivation.
- **Depth (C3):** tile-RID and replay claims must stay within what the measurements establish.

**Counterexample — K1, depth:** On Godot `4.7.2.stable.arch_linux.ed1daf0bf`, quadrant size 1 returned the placed cell coordinates; size 16 did not. The probe used both requested cells and queried both collider and probe RIDs. Each of the three bounded, serial runs emitted the same output:

```text
Run 1:
tile_rid q=1 cell=(5, 0) hit=true collider_has=true collider_coords=(5, 0) probe_has=false probe_coords=(0, 0)
tile_rid q=1 cell=(21, 0) hit=true collider_has=true collider_coords=(21, 0) probe_has=false probe_coords=(0, 0)
tile_rid q=16 cell=(5, 0) hit=true collider_has=true collider_coords=(0, 0) probe_has=false probe_coords=(0, 0)
tile_rid q=16 cell=(21, 0) hit=true collider_has=true collider_coords=(1, 0) probe_has=false probe_coords=(0, 0)
PASS tile_rid probe cells=2 quadrants=1,16
Run 2:
tile_rid q=1 cell=(5, 0) hit=true collider_has=true collider_coords=(5, 0) probe_has=false probe_coords=(0, 0)
tile_rid q=1 cell=(21, 0) hit=true collider_has=true collider_coords=(21, 0) probe_has=false probe_coords=(0, 0)
tile_rid q=16 cell=(5, 0) hit=true collider_has=true collider_coords=(0, 0) probe_has=false probe_coords=(0, 0)
tile_rid q=16 cell=(21, 0) hit=true collider_has=true collider_coords=(1, 0) probe_has=false probe_coords=(0, 0)
PASS tile_rid probe cells=2 quadrants=1,16
Run 3:
tile_rid q=1 cell=(5, 0) hit=true collider_has=true collider_coords=(5, 0) probe_has=false probe_coords=(0, 0)
tile_rid q=1 cell=(21, 0) hit=true collider_has=true collider_coords=(21, 0) probe_has=false probe_coords=(0, 0)
tile_rid q=16 cell=(5, 0) hit=true collider_has=true collider_coords=(0, 0) probe_has=false probe_coords=(0, 0)
tile_rid q=16 cell=(21, 0) hit=true collider_has=true collider_coords=(1, 0) probe_has=false probe_coords=(0, 0)
PASS tile_rid probe cells=2 quadrants=1,16
```

For each process, querying `get_coords_for_body_rid(probe.get_rid())` also emitted this error/backtrace four times; its `(0, 0)` return is **not** a valid coordinate observation:

```text
ERROR: Parameter "found" is null.
   at: get_coords_for_body_rid (scene/2d/tile_map_layer.cpp:3124)
GDScript backtrace (most recent call first):
       [0] _probe_cell (res://x.gd:54)
```

**Smallest safe correction:** In the fixture/knowledge, use coordinates only when `has_body_rid()` is true; treat the arbitrary probe RID’s error as a distinct negative result, not as a coordinate. The size-16 observations are consistent with reduced precision, not an exact-cell guarantee.

**Counterexample — K3, depth:** The six-body drop produced **one distinct digest in each ten-run set**. All invocations returned `rc=0`, reported 240 physics frames, and emitted the following raw receipt; this is an observation for this host/setup, not evidence of a determinism guarantee.

Without `--fixed-fps 60` (runs 1–10; each line is one serial process):

```text
PASS replay bodies=6 physics_frames=240 sha256=2430339ff690f557962ad51802d1c2c5cdc987a9c4ac4bc3b47c61996dd17e3b
PASS replay bodies=6 physics_frames=240 sha256=2430339ff690f557962ad51802d1c2c5cdc987a9c4ac4bc3b47c61996dd17e3b
PASS replay bodies=6 physics_frames=240 sha256=2430339ff690f557962ad51802d1c2c5cdc987a9c4ac4bc3b47c61996dd17e3b
PASS replay bodies=6 physics_frames=240 sha256=2430339ff690f557962ad51802d1c2c5cdc987a9c4ac4bc3b47c61996dd17e3b
PASS replay bodies=6 physics_frames=240 sha256=2430339ff690f557962ad51802d1c2c5cdc987a9c4ac4bc3b47c61996dd17e3b
PASS replay bodies=6 physics_frames=240 sha256=2430339ff690f557962ad51802d1c2c5cdc987a9c4ac4bc3b47c61996dd17e3b
PASS replay bodies=6 physics_frames=240 sha256=2430339ff690f557962ad51802d1c2c5cdc987a9c4ac4bc3b47c61996dd17e3b
PASS replay bodies=6 physics_frames=240 sha256=2430339ff690f557962ad51802d1c2c5cdc987a9c4ac4bc3b47c61996dd17e3b
PASS replay bodies=6 physics_frames=240 sha256=2430339ff690f557962ad51802d1c2c5cdc987a9c4ac4bc3b47c61996dd17e3b
PASS replay bodies=6 physics_frames=240 sha256=2430339ff690f557962ad51802d1c2c5cdc987a9c4ac4bc3b47c61996dd17e3b
```

With `--fixed-fps 60` (runs 1–10; each line is one serial process):

```text
PASS replay bodies=6 physics_frames=240 sha256=2430339ff690f557962ad51802d1c2c5cdc987a9c4ac4bc3b47c61996dd17e3b
PASS replay bodies=6 physics_frames=240 sha256=2430339ff690f557962ad51802d1c2c5cdc987a9c4ac4bc3b47c61996dd17e3b
PASS replay bodies=6 physics_frames=240 sha256=2430339ff690f557962ad51802d1c2c5cdc987a9c4ac4bc3b47c61996dd17e3b
PASS replay bodies=6 physics_frames=240 sha256=2430339ff690f557962ad51802d1c2c5cdc987a9c4ac4bc3b47c61996dd17e3b
PASS replay bodies=6 physics_frames=240 sha256=2430339ff690f557962ad51802d1c2c5cdc987a9c4ac4bc3b47c61996dd17e3b
PASS replay bodies=6 physics_frames=240 sha256=2430339ff690f557962ad51802d1c2c5cdc987a9c4ac4bc3b47c61996dd17e3b
PASS replay bodies=6 physics_frames=240 sha256=2430339ff690f557962ad51802d1c2c5cdc987a9c4ac4bc3b47c61996dd17e3b
PASS replay bodies=6 physics_frames=240 sha256=2430339ff690f557962ad51802d1c2c5cdc987a9c4ac4bc3b47c61996dd17e3b
PASS replay bodies=6 physics_frames=240 sha256=2430339ff690f557962ad51802d1c2c5cdc987a9c4ac4bc3b47c61996dd17e3b
PASS replay bodies=6 physics_frames=240 sha256=2430339ff690f557962ad51802d1c2c5cdc987a9c4ac4bc3b47c61996dd17e3b
```

Distinct digests: no fixed FPS **1/10**; fixed FPS 60 **1/10**; combined **1**. This does not refute S009’s warning, but it would refute an inference that this experiment demonstrated divergence. **Smallest safe correction:** report the 0/20 divergence observation and do not promote it to a determinism claim.

## C1 attack — coverage

- **Isolation may leave the contaminated authority shared.** The current battery copies one project to `scratch` per run (`run_battery.py:2333–2348`) and all rows use that same `--path`; its UID rows also receive the same `run_dir/xdg-data` (`2526–2534`). The r104 lesson says runtime UID resolution depends on `.godot/uid_cache.bin` (`r104-resource-loader-uid.md:27–37`). **Check:** inspect every restored row’s recorded command and environment; require a unique project root/cache path per row, plus its intended `user://` isolation. Preserve that same row’s root across any processes needed to test persistence.
- **A row can be absent or a no-op while aggregate coverage looks green.** **Check:** in both forward and genuinely reversed full-battery reports, assert each exact row—`res_uid_path`, `res_uid_collide`, `res_uid_cache`, `res_uid_missing`, `res_uid_s01_collide`, `res_uid_s01_diag`, `res_uid_s02_deleted`, and repaired `res_uid_s01_createid`—appears exactly once with its pinned receipt and `verdict=PASS`; also assert the `res_uid_` total is at least 28. Do not rely on a count that changes when both `CASES` and results omit the same row.
- **Reversed-order evidence is not currently exposed by the battery CLI.** It iterates `for case in CASES` (`run_battery.py:2973`) and the parser has no reverse option (`2316–2331`). **Check:** only claim the reversed run after adding/exercising an explicit reverse-order path (or a reversed-order test copy); use a fresh run root and compare the exact row sets and outcomes.
- **The shared-scratch negative may fail for the wrong reason.** **Check:** use the actual writer→reader UID pair and shared project/cache; require the reader’s captured diagnostic to include the specific `ERROR: Unrecognized UID:` class (lesson §4), and require the isolated reader to pass. A generic `ERROR`, `null`, timeout, or parse failure does not establish the control.
- **Self-derived `createid` expectations can be tautological.** **Check:** require independent invariants: `text_to_id(id_to_text(id)) == id`, repeated `create_id_for_path(path)` is stable, and querying `has_id()` proves whether the operation registered the result. Do not compare a value only to itself or derive both expected and actual from the same call.

## C2/C3 attacks — calibration and depth

- **QUALITY criteria can cite lessons yet contain no executable check.** If criteria use one line per `- [Qnn]` record with `Check:` and `Source:`, this prints missing checks/pointers: `awk '/^- \[Q[0-9]+\]/ && ($0 !~ /Check: `[^`]+`/ || $0 !~ /Source: `(LOG\.md:[0-9]+|corpus\/lessons\/[^:]+\.md:[0-9]+)`/) {print NR ":" $0}' corpus/QUALITY.md`. Guard against vacuity with `grep -cE '^- \[Q[0-9]+\]' corpus/QUALITY.md`. Then execute the stated checks, including their intended negative controls; a command-shaped string alone is not an admission check.
- **A source row can show an `opened` date without round-local evidence it was opened.** **Check:** use an AWK registry-ID-versus-`## Gate` sweep to print any `SNNN` row absent from the round lesson’s Gate; require each Gate record to contain the URL, access date, anchored ≤25-word quote, then actually reopen the source. ID/date text alone cannot prove access.
- **Tiers can be inflated.** The contract’s tier/kind/status AWK census catches enum violations and community-at-A; also explicitly reject `S025` at A and require `S015` to remain rejected: `awk -F'|' '/^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|/ && NF==13 {i=$2;k=$4;t=$5;s=$9;gsub(/[[:space:]]/,"",i);gsub(/[[:space:]]/,"",k);gsub(/[[:space:]]/,"",t);gsub(/[[:space:]]/,"",s);if((t=="A"&&k=="community")||(i=="S025"&&t=="A")||(i=="S015"&&s!="rejected"))print i,k,t,s}' corpus/SOURCES.md`.
- **`mined` can point to dead or irrelevant `used-by` entries.** **Check:** apply the contract’s `mined`-path existence AWK check; also print `mined` rows whose `used-by` is blank/`—`, and for every listed `SNNN path`, require both `[ -e "$path" ]` and `grep -Fq "$id" "$path"`.

## Reopened ART sources

- **S002 supported** — “Higher values will make that function less precise.” *TileMapLayer class*, Property Descriptions → `physics_quadrant_size`.
- **S005 supported** — “Higher values of TileMapLayer.physics_quadrant_size will make this function less precise.” *Upgrading from Godot 4.4 to Godot 4.5*, Behavior changes → TileMapLayer.
- **S009 supported** — “Physics in Godot, regardless of physics engine, is not deterministic.” *Physics introduction*, Warning.

Scratch only: copied `project.godot` and wrote `x.gd` / `replay.gd` under `/var/tmp/gd2d-r105/R105Critic/`; no lane files were touched.
