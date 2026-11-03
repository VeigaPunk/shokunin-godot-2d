# game-dev-2d: curated sources to consider — 2026-11-03

**Status: unassimilated future reading after hyaku.** This is a reading queue, not an admitted lesson, training round, or capability claim. Original summaries and source links only; no source code or third-party prose copied. No candidate code was run, installed or integrated. Existing daily-reflection files and source registries remain unchanged.

Selected after reviewing this lane’s PROVINCE, supplied source registry and historical considerthese context. Two complementary sources are enough for this first batch: one method/specification and one maintained implementation.

## 1. Godot internationalization: contexts, plurals and pseudolocalization

- **Source / type:** [Godot internationalization: contexts, plurals and pseudolocalization](https://docs.godotengine.org/en/stable/tutorials/i18n/internationalizing_games.html) — methodology. Opened 2026-11-03.
- **Why this lane:** Directly targets localization wiring, an explicit frontier absent from the current source registry.
- **Verified anchor:** Sections on translation contexts, pluralization, resizable controls, TranslationServer, and bidirectional UI describe distinct testable surfaces.
- **Read first:** Read translation contexts and pluralization first, then locale switching and pseudolocalization limits.
- **Proposed later exercise (not performed):** After hyaku, propose a tiny 2D UI fixture that switches locales, distinguishes two meanings of one key, checks plural boundaries and preserves placeholders. Keep layout and glyph rendering checks in a separately declared real-render path.
- **Rights:** Godot documentation: CC BY 3.0; retain attribution for reuse. This batch links and summarizes only. [License evidence](https://raw.githubusercontent.com/godotengine/godot-docs/master/LICENSE.txt).
- **Limits:** Stable is mutable and the page includes legacy DynamicFont wording; verify APIs against the lane’s pinned engine before use. Pseudolocalization does not certify CJK/RTL fonts or translation quality; headless state is not visual evidence.
- **Duplicate review:** New localization topic rather than another tilemap, physics replay, UID or runner reference. Exact/normalized primary URL absent from supplied lane inventory.

## 2. Official Godot demonstration projects

- **Source / type:** [Official Godot demonstration projects](https://github.com/godotengine/godot-demo-projects) — repository. Opened 2026-11-03.
- **Why this lane:** An upstream-owned source of small production patterns to turn into bounded 2D/UI fixtures; not another testing-framework wrapper.
- **Verified anchor:** README defines each project.godot directory as a separate demo and explains matching stable branches versus development master; repository contains 2d and gui examples.
- **Read first:** Select only relevant 2d/gui projects, then use the stable branch matching the installed engine and record a commit.
- **Proposed later exercise (not performed):** After hyaku, extract one behavioral question from a small demo and implement an original minimal fixture with a failing control. Avoid importing the full demo collection.
- **Rights:** MIT for repository demos per README/LICENSE.md; inspect individual asset notices before any reuse, not asset-rights clearance. [License evidence](https://github.com/godotengine/godot-demo-projects/blob/master/LICENSE.md).
- **Maintenance evidence:** Opened commit history shows 2026-09-08 fix a3b5c11 and August 2026 maintenance, including 2D drawing updates. [History/release evidence](https://github.com/godotengine/godot-demo-projects/commits/master/).
- **Limits:** Master targets development Godot. A demo running successfully is not a test oracle, determinism guarantee or export-readiness certificate. No engine/editor source edits.
- **Duplicate review:** Official demo repository is absent from the lane’s supplied inventory; complements existing GUT/gdUnit sources. Exact/normalized primary URL absent from supplied lane inventory.

## Family-overlap and revision check

Method/specification: targeted new surface in existing source family. Repository: new source family in supplied lane inventory. These checks include repository identity and publisher-domain overlap, not just exact URLs.

Repository revision evidence: [a3b5c113112f77291d5f3d1360f33a882fdc52f7; commit page opened](https://github.com/godotengine/godot-demo-projects/commit/a3b5c113112f77291d5f3d1360f33a882fdc52f7). This is a reading anchor, not proof of host compatibility; mutable README/license links above were inspected separately on 2026-11-03.

## Admission gate, later

Re-open and pin versions when hyaku work is authorized. State the narrow claim, build original positive and negative cases within this lane’s province, and retain measured limitations. Reading or successful third-party tests alone does not admit a capability. Attribution, redistribution rights and AI-training permission remain distinct; this queue makes no training-permission or asset-rights determination.
