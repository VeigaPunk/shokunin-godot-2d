# r19 claim planner (L2 leaf)

**Role:** planner  
**Round:** game-dev-2d round 19  
**Branch / HEAD:** `craft/game-dev-2d-r1` @ `fa31bef`  
**Working tree:** `/home/vgpnk/Projects/prymeagnt/game-dev-2d`  
**Parent axis:** calibration  
**Lane-owned axes:** depth, coverage, calibration  
**Godspeed:** name axes, one job, no questions, no subagents, no commit/push, no MANIFEST/sibling books, paths only as named.

## Scope of this leaf

- **Wrote:** `.shokunin/game-dev-2d/reports/r19-claim-planner.md` (this file).
- **Changed:** nothing else.
- **Refused:** code edits; Godot runs; `run_battery.py`; fixtures; `MANIFEST.json`; sibling books; commits/pushes; spawning; judging the round.

## Axes (named)

| Axis | Expected effect of the parent-integrated move (if implementer lands contract) |
|------|--------------------------------------------------------------------------------|
| **calibration** | **Improved** only if a named non-author verifier re-runs the after command and confirms accept/reject stream split + meta PASS. Planner does not claim improvement. |
| **depth** | **Unchanged** — no new mechanic fixture; ordinary case list untouched; bounded stream-attribution probe only. |
| **coverage** | **Unchanged** — one paired probe of existing Godot print/stderr behavior already noted in r11; not a new product surface. |

Verdict vocabulary for the round (parent/judge use; this leaf does not judge):  
`improved` | `harmed` | `unchanged` | `unprovable-but-better`.

## Falsifiable claim (before → after)

**Before** (`fa31bef`, no stream-attribution case):

```text
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py \
  --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error
```

→ **33/33 PASS**. No `--probe-stream-attribution`. Stream attribution unprobed: `run_process` concatenates stdout+stderr before `classify_process` (r11 lesson; SceneTree `print` → stdout, `printerr`/`push_error`/`push_warning` → stderr under Godot 4.7.2 at `/usr/bin/godot`).

**After** (same flags **plus** `--probe-stream-attribution`):

```text
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py \
  --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error \
  --probe-stream-attribution
```

→ **33+k / 33+k PASS** with **k = 1** (one new results record for the stream-attribution probe pair/meta, per contract: one probe flag → one results record).

Hard constraints that keep the claim falsifiable:

1. **Prior 33 ordinary outcomes unchanged** (same accept/reject as before for existing probes/cases).
2. **Tracked fixture hashes stable** except the **new** fixture and the **runner** edit only:
   - New fixture ONLY: `.shokunin/game-dev-2d/corpus/fixtures/stream_attribution_probe.gd` (SceneTree, like `godot_error_probe.gd`).
   - Edit ONLY: `.shokunin/game-dev-2d/corpus/fixtures/run_battery.py` for `--probe-stream-attribution`.
   - Must **not** edit seeded fixtures, `classify_process`, `classify_audio_process`, existing probe flags, or ordinary case list.
3. **Paired real headless Godot runs of the SAME script** (`res://stream_attribution_probe.gd`):
   - **ACCEPT:** `print` marker on **stdout only**, no `printerr`. Classifier accepts when expected print signature is on stdout, stderr has no case-owned error, exit is the script’s quit code.
   - **REJECT:** same script + user flag that also `printerr()`s an unrelated diagnostic. Classifier rejects because that diagnostic is on **stderr** and is not an allowed error. **Exit codes of both runs identical** so rejection is stream attribution, not exit-code difference.
4. Capture **stdout and stderr separately** (do not only concatenate). Record **both streams** in the verdict JSON.
5. **Meta PASS** only if: accept classifies true, reject classifies false, both actually emitted their markers on the claimed stream, and both used `res://stream_attribution_probe.gd`.
6. Do not weaken unrelated-error rejection.

## Bounded claim (what this is / is not)

- **Is:** one Godot **4.7.2** headless **stream-attribution** pair under the battery probe flag.
- **Is not:** crash classification; process-tree timeout; export reliability; rendered output.

## Calibration improvement gate

**Calibration can be scored improved only if** a **named non-author verifier** re-runs the **after** command above and confirms:

- accept → classify true with print marker on stdout only;
- reject → classify false with printerr diagnostic on stderr;
- identical exit codes across the pair;
- both streams present in verdict JSON;
- meta PASS conditions;
- 33 prior outcomes unchanged;
- k=1 additive record;
- paths/hashes limited to new fixture + runner.

Until that re-run, any “better runner” story is at most **unprovable-but-better**, not **improved**.

## Depth / coverage

If implementer adds **no** new mechanic fixture and leaves ordinary cases untouched, **depth** and **coverage** should stay **unchanged**. This leaf does not implement or verify that.

## Files written (this leaf)

| Path | Action |
|------|--------|
| `.shokunin/game-dev-2d/reports/r19-claim-planner.md` | created/written |

## Leaf report path

`.shokunin/game-dev-2d/reports/r19-claim-planner.md`
