# game-dev-2d: curated source to consider, batch 2 — 2026-11-03

**Status: unassimilated candidate for post-hyaku review.** Reading queue only, not training, admission or capability evidence. No candidate code was installed, run or integrated. This note contains original summaries; no third-party code or prose is reproduced.

## Godot saving games: nested restore order and typed-state limits

- **Primary source:** [Godot saving games: nested restore order and typed-state limits](https://docs.godotengine.org/en/4.4/tutorials/io/saving_games.html).
- **Verified reading anchor:** [fd9c88a424709a46bdcf53442712a723ab401e81](https://github.com/godotengine/godot-docs/blob/fd9c88a424709a46bdcf53442712a723ab401e81/tutorials/io/saving_games.rst). Godot 4.4 documentation; the path's last commit in that branch is dated 2024-11-29T06:46:08Z. This is a documentation revision, not an engine release date. Opened 2026-11-03.
- **Source summary:** The tutorial marks persistent nodes, serializes per-object dictionaries and restores scene instances. Its caveats explicitly exclude nested persistent objects from the simple example: parents must exist before children, and stored NodePaths can become invalid. JSON cannot directly preserve several Godot value types. This is a bounded starting point rather than a production save-system specification.
- **Read first:** Saving games: Identify persistent objects; Serializing; Some notes; JSON vs binary serialization / JSON limitations. Source path tutorials/io/saving_games.rst.
- **Why useful here:** Save/load is already core, so this is not a claim of a new capability. It adds a specific nested-scene restoration failure surface absent from the supplied source registry and first-batch localization/demo selections.
- **License:** [CC BY 3.0](https://github.com/godotengine/godot-docs/blob/fd9c88a424709a46bdcf53442712a723ab401e81/LICENSE.txt). Retain attribution for adapted documentation. Attribution, redistribution and AI-training permission remain separate; no training or input-asset rights determination is made.
- **Hard limits:** The 4.4 documentation is historical, not the lane's recorded 4.7.2 runtime contract. Reconcile APIs before any later experiment. The tutorial does not establish migration, crash-safe persistence or safe handling of untrusted save data. Do not copy its dynamic resource loading into a production loader without separate review.

## Original lane-specific evaluation proposal, not performed

**Future question:** Does a proposed 2D save format preserve parent-child identity and typed state when reconstruction order and NodePaths change?

After hyaku, propose an original parent/child scene record with explicit stable IDs, position fields and an optional child. On paper, permute record order and rename the parent path. Define a positive two-phase reconstruction case and negative dangling-parent, duplicate-ID and malformed-type cases. Require all invalid records to be reported before state replacement. This is a fixture proposal, not a claim that existing lane save/load tests fail.

## Duplicate and selection review

Same Godot documentation publisher as existing sources, explicitly retained for a distinct serialization topic. Exact URL/path absent across supplied context. The first-batch demo repository includes serialization examples; this selection adds the authoritative nested-object limitation rather than reselecting that demo.

Reviewed existing-urls.json and all four assigned lane contexts, including their published first-batch notes; candidate names/paths were also searched across all supplied lane contexts. This is source-inventory dedup, not a claim that every private corpus file was read. One focused candidate was retained; no broader framework adoption is implied. Re-open the pinned source and define an authorized, lane-local admission gate before future execution.

