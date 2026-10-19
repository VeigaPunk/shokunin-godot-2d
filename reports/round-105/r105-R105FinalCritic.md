# r105 within-lane review — R105FinalCritic

Snapshot: first two full runs before review corrections. Non-author verification remains orchestrator-owned. Findings were actioned before final landing; see LOG.md round-105 and lesson §Draft corrections.

## Axes checked

- **C1 coverage:** The AST-only count is **600 CASES**; the README’s 585 base plus 8 re-admitted ResUID rows and 7 R105 rows reconciles to 600. The receipts’ 622 `results` rows include additional probe/meta records, not 22 more CASES.
- **C2 calibration:** All 28 M rows map to valid Q IDs. The Q5 rechecks are bounded, describe runner scratch staging, and their expected `PASS <case>:` prefixes match the runner’s output format.
- **C3 depth:** The three new knowledge paths exist. Their cited source IDs match registry rows and `used-by` paths. The map marks its surface assignments as inference and advances only the TileMapLayer RID and replay frontiers.

## Findings

1. **High — Q6 evidence is not explicit in the three admitted knowledge entries.**  
   `corpus/QUALITY.md:18` requires each behavioral claim to name its CASES tuple, including fixture, arm, exit, and exact PASS line. The entries describe fixture arms and observations (`corpus/knowledge/2026-10-19-tilemaplayer-body-rid-attribution.md:3-5,21-47`; `...res-uid-runtime-authority.md:3-5,20-37`; `...physics-replay-boundary.md:3-5,19-31`), but none supplies those tuples. The tuples are elsewhere, e.g. `corpus/fixtures/run_battery.py:1840-1846`.  
   **Smallest fix:** Add a claim-to-CASES table to each entry with the exact tuple/signature and its two serial receipt references. Keep the replay digest diagnostic separate from the stable PASS pin.

2. **High — Q9 run-to-bytes provenance is absent from the committed receipt.**  
   `corpus/QUALITY.md:21` requires the verdict to identify the blob SHA it ran. `reports/round-105/r105-receipts.py:13-49` summarizes run IDs, counts, signatures, and outcomes, but no code/fixture blob SHA; `reports/round-105/r105-battery-receipts.json:3-11` likewise has no such binding. The available receipt identifies the run, not the exact source bytes used. This is an **evidence gap**, not proof that the wrong bytes were run.  
   **Smallest fix:** Bind each verdict to the executed runner/fixture blob IDs in the run payload and committed summary; if that cannot be reconstructed, use a new post-commit receipt rather than inferring identity from current HEAD.

3. **Medium — Q18’s stated count check has the wrong denominator.**  
   `corpus/QUALITY.md:30` says CASES count equals receipt row count. The AST count is 600, while the committed summary reports 622 rows (`reports/round-105/r105-battery-receipts.json:5-10`). The summary helper defines `rows` as `len(data["results"])` (`r105-receipts.py:16-18`), which includes meta/probe records such as `probe_res_uid_shared`.  
   **Smallest fix:** Compare the CASES entries against the CASES-backed result records by case identity and multiplicity; count meta rows separately. The README’s 600-CASES map is not wrong.

4. **Medium — K1 generalizes quadrant behavior beyond the tested cells.**  
   The knowledge entry claims `floor(cell / 16)` and “identical for every cell in a quadrant” (`tilemaplayer-body-rid-attribution.md:15-16,27-31,69-71`). Its size-16 fixture tests only `(5,0)`, `(15,0)`, and `(21,0)` (`r105_tile_rid.gd:130-153`): the three outputs support those horizontal observations, not the universal 2D formula or all cells in a quadrant. The docs say larger quadrants reduce precision; they do not specify this returned-index formula.  
   **Smallest fix:** Scope the wording and decision to the measured cells, or add probes covering Y boundaries and negative coordinates before stating a general formula.

5. **Medium — The K3 admission cites a non-matching “independent critic” scenario.**  
   `corpus/lessons/round-105.md:151` cites “independent critic probe 1 digest / 20 runs.” The cited report’s probe is a **six-body** drop (`reports/round-105/r105-R105Critic.md:47-79`), whereas K3’s claim is for eight `RigidBody2D`s plus a scripted `CharacterBody2D` (`physics-replay-boundary.md:9-14`). It does not independently reproduce K3’s setup. K3’s own report does record the 8-body runs, and the knowledge entry correctly states that observed identity is not an engine guarantee.  
   **Smallest fix:** Qualify the critic probe as a different-scenario corroboration, or omit it from K3’s admission rationale.

## Clean checks and caveat

- The 31 source IDs are present, and all three knowledge entries’ source IDs match their registry `used-by` paths. The cited sources were checked against the claims; S015’s pre-release rejection/flip and S031’s 4.4-only rejection/flip are real. The C3/C4/C5 rejection reasons match the stated fixture, runner, and graphical-baseline gaps; the r106 plan for C3 is recorded in `r105-R105Planner.md:29-35`.
- The new knowledge headers have the three required fields, bounded rechecks, and scratch-staging instructions; there are no `<scratch>` placeholders. Q5’s `PASS <case>:` prefix is emitted by the runner wrapper (`run_battery.py:3082`).
- The README’s added paths resolve, and its frontier calls only the two K1/K3 surfaces “advanced”; it does not claim exhaustive coverage.
- **Depth-count caveat:** `reports/round-105/r105-count.sh:11-14` counts all 31 SOURCES rows, while the registry has 10 mined, 19 queued, and 2 rejected. That count is transparent as inventory, but it should not be presented as 31 sources supporting the three admitted entries.
- No full battery was run for this review; the count was AST-only.
