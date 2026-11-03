# game-dev-2d: curated source to consider, batch 4 — 2026-11-03

**Status: unassimilated post-hyaku reading.** No training, installation, import integration or candidate execution.

## LDtk: external-level completeness and coordinate ownership

**Source and revision:** [LDtk JSON schema](https://github.com/deepnight/ldtk/blob/72c75f1abfdc28f58522b858c6a69fe4af6a9522/docs/JSON_SCHEMA.json), schema 1.5.3. [Release v1.5.3](https://github.com/deepnight/ldtk/releases/tag/v1.5.3) was published 2024-01-15 at 15:18:29 UTC and resolves to the pinned commit. Opened 2026-11-03; this is a versioned reading anchor, not a claim about the latest editor.

**Source summary:** Separate-level projects retain level metadata while layerInstances becomes null and externalRelPath points to another JSON file. Layer order is front-to-back. Total pixel offsets already combine definition and instance offsets. IntGrid values are row-major, with zero denoting an empty cell. Entity pixel positions are level-relative and still require applicable layer offsets.

**Read first:** In docs/JSON_SCHEMA.json, follow LdtkJsonRoot.externalLevels, otherTypes.Level.layerInstances/externalRelPath, otherTypes.LayerInstance.__pxTotalOffsetX/Y and intGridCsv, then otherTypes.EntityInstance.px.

**Domain gap and novelty:** Godot tile collision attribution and resource imports are already covered. LDtk adds an independently specified authoring boundary: absent external data must not become an empty playable level, and offsets must not be applied twice. LDtk, deepnight/ldtk and its JSON format were absent from the reviewed source inventory and prior notes.

**License:** [MIT](https://github.com/deepnight/ldtk/blob/72c75f1abfdc28f58522b858c6a69fe4af6a9522/LICENSE), including associated documentation; preserve required notices on reuse. Tileset/image rights and AI-training permission are separate questions.

**Original future question, not performed:** Can equivalent embedded and external two-layer levels produce the same declared cell/entity coordinates? After hyaku, propose a paper fixture with nonzero definition and instance offsets, one empty IntGrid cell and a centered entity. Add a missing external file control. Require explicit unresolved-data reporting, preserved layer order and a coordinate ledger before any engine comparison.

**Limits:** Schema conformance does not prove collision behavior, asset availability, Godot importer compatibility or rendered equivalence. No editor replacement or third-party importer adoption is proposed.

