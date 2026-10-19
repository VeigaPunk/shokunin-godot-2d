# r105 seat report — R105SourcesExec (executor)

Verbatim final output of L2 `W2RoundGameDev2d.R105SourcesExec` (round 105, batched swarm; transcript `history://W2RoundGameDev2d.R105SourcesExec` is session-scoped and not evidence — this file is).

---

Done. Full deliverable report:

## Census outputs (lane root, verbatim)

```
rows:            31
malformed:       0
tier histogram:  A=30 B=1
status:          mined=10 queued=19 rejected=2
duplicate ids:   (none)
enum/tier violations: (none)
mined used-by missing:
  missing: corpus/knowledge/2026-10-19-physics-replay-boundary.md  ×4 (S009,S010,S025,S030)
```
The only used-by misses are K3 (`2026-10-19-physics-replay-boundary.md`) — sibling hasn't landed it yet; expected per assignment. K1 (`2026-10-19-tilemaplayer-body-rid-attribution.md`) landed mid-wave and resolves.

## Ids opened vs demoted
**All 31 rows opened this session** — S001–S025 (ART dossier leads, each re-opened, never trusted), S026 ResourceUID + S027 KinematicCollision2D (web), S028 r104 lesson + S029 tilemap_lattice arms + S030 r105 fixtures (own-work, fixtures landed mid-wave and were executed), S031 (new honest reject: 4.4 TileMapLayer ref — predates `physics_quadrant_size`, EOL branch). **0 demoted to Leads.** S030 was at risk until `r105_tile_rid.gd`/`r105_phys_replay.gd` landed; they did, and I opened + ran them before writing the row.

## K2 rerun outputs (fresh scratch, per-run XDG_DATA_HOME + RES_UID_ROOT, bounded, serial)
```
PASS res_uid s04 arm=persist cache_records=1 cache_declared=1 cache_consistent=true cache_id_match=true roundtrip=true reader_has=true reader_path=res://alpha.gd nocache_has=false uidfile_only_authority=false   (rc=0, 4.04s)
PASS res_uid text decode=uid://a=0,uid://9=34,uid://z=25,uid://0=25,uid://bqk3m5n7qar1=103876737118377468,uid://b=1,uid://=0,uid://aaaa=0 alias_empty_eq_aaaa=true alias_0_eq_z=true a0=0 z25=25 roundtrip_int63max=true first_bad=none …   (rc=0)
PASS res_uid s04 arm=collision dup_warn=true pair=res://alpha.gd,res://beta.gd records=1 dup_records=1 dup_text_roundtrip=true winner_in_pair=true reader_matches_winner=true   (rc=0, 3.04s)
```
All match pinned battery lines. S030 evidence also executed: `PASS r105_tile_rid exact … c5_coords=5,0 c21_coords=21,0`, `PASS r105_tile_rid wrongrid … own_has=0 own_coords=0,0`, `PASS r105_phys_replay perturb differs=true …`.

## Files touched
- `corpus/SOURCES.md` (new — registry 31 rows, 4 study paths, 4 search-log notes, Leads section)
- `corpus/knowledge/2026-10-19-res-uid-runtime-authority.md` (new — K2, contract shape, cites S026+S028)
- `/var/tmp/gd2d-r105/R105SourcesExec/gate-quotes.md` (scratch — per-row URL/date/≤25-word-quote+location for all 31 rows)

Risks: S015 row uses `docs` kind with teaches as the mandated `REJECTED: …; flip: …` text — tier A is scoped to "the snapshot itself" (honest for its narrow scope). K3 `used-by` rows will fail the used-by existence check until the sibling lands the file.
