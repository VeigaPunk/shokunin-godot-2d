# game-dev-2d: source candidate, batch 3 — 2026-11-03

**Unassimilated, post-hyaku reading queue.** No installation, execution, training or capability admission. Original summary only; no source code reproduced.

## Godot: keyboard/controller focus lifecycle

**Question:** Can a player enter, traverse and recover a menu using only a keyboard or controller after its focused control disappears?

**Primary source and pin:** Godot's [Keyboard/Controller Navigation and Focus](https://github.com/godotengine/godot-docs/blob/a8ccd619365dc5504bbb39a90fd4a9adaea46429/tutorials/ui/gui_navigation.rst), revision [a8ccd619365dc5504bbb39a90fd4a9adaea46429](https://github.com/godotengine/godot-docs/commit/a8ccd619365dc5504bbb39a90fd4a9adaea46429). The 4.5 branch's path history identifies this change at 2025-05-09T19:08:17Z. Opened 2026-11-03; this is documentation history, not an engine release date.

**Source summary:** Initial focus must be established explicitly. Directional neighbors differ from next/previous traversal, hidden controls can lose focus, and automatic neighbor selection can misroute complex layouts. Built-in UI actions should not double as gameplay actions. The example defers the initial focus call.

**Reading path:** Introductory action warning → Node settings → Necessary code, all in the pinned page. Documentation is [CC BY 3.0](https://github.com/godotengine/godot-docs/blob/a8ccd619365dc5504bbb39a90fd4a9adaea46429/LICENSE.txt); retain attribution and identify adaptations. Asset rights and training permission are separate questions.

**Original later exercise, not performed:** Design a small asymmetric menu with an initial button, a modal panel and a control that becomes hidden. Before implementation, specify expected focus owners after every directional and tab-style action, plus the intended recovery rule after hiding. Include an intentionally missing initial focus and an intentionally wrong neighbor as negative controls. Record focus-owner identity rather than relying on screenshots alone. Observe gameplay state during navigation to expose accidental shared action bindings. A passing trace should establish only the declared scene's behavior on a recorded build, not general accessibility.

**Novelty and limits:** The supplied source inventories and earlier batches contain no gui_navigation page or keyboard/controller-focus candidate. This is a narrow new UI lifecycle within the existing Godot family, separate from localization and save restoration. The historical documentation pin is not proof of current-engine behavior, device compatibility or usability; later review must reconcile it with the target build and include human accessibility evaluation where needed.
