# Round 59 audio bus executor report

## Scope and implementation

Added `audio_bus_route.gd` and two additive rows to `corpus/fixtures/run_battery.py`; no existing case or seven opt-in flag was changed. The positive dynamically adds `FixtureBus`, assigns an in-tree `AudioStreamPlayer` to it, and checks the resolved bus index/name plus active playback and advancing position. It frees the player and removes the temporary bus. The paired invalid-name control records playback but exits 2 with a distinct expected diagnostic if `NoSuchFixtureBus` silently resolves to Master; it does not claim playback itself rejects the route.

## Causal scratch evidence

Godot `4.7.2.stable.arch_linux.ed1daf0bf`. Before tracked edits, unique scratch experiment showed explicit `FixtureBus` resolves index 1 and remains playing/advances (0.00580→0.09868 s). For `NoSuchBus`, playback also remains playing/advances, but bus getter returns `NoSuchBus`, `AudioServer.get_bus_index()` returns -1 and `get_bus_name(-1)` is invalid. A later tracked-fixture run showed it instead resolved to index 0 / `Master`; this exact runtime behavior is treated as fallback, not route success. Causal scratch sabotage changed only the positive's created bus name; playback still advanced, but the probe exited 2 with `AUDIO BUS ROUTE ASSERTION FAILED` after resolution was Master. This distinguishes route assertion from transport progress. The first scratch used a relative XDG path and emitted an XDG warning; it is retained as adverse setup evidence, not used in verdicts. Corrected scratch and all later runs used absolute run-local XDG paths.

## Verification

Full seven-flag run at `corpus/live/r59-audio-executor/seven-flags/20261013T133844697031Z/verdicts.json`: **89/89 PASS** (77 ordinary +2 mutants +10 opt-in/meta records). Against r58 `r58-process-non-author.json`, all 87 prior case rows retain identical `(verdict, actual_exit, signature)`; two additive audio cases are present. Positive: exit 0, explicit index 1 `FixtureBus`, active and advancing. Invalid-route control: exit 2 with exact expected “silently fell back to Master” diagnostic; run battery classifier accepts only that diagnostic. Audio cases emitted no ObjectDB leak warning after teardown. The earlier attempted seven-flag run at `20261013T133719712820Z` failed the pre-existing `checkbox_toggle` row despite its success output; it is retained adverse evidence and excluded from PASS claim. A fresh complete replay then passed, with the same pre-existing expected inner FAIL probes (Godot unrelated diagnostic and stream reject) classified by their outer probe metadata.

## Limits

This is headless Godot 4.7.2 property/routing-name and playback-position evidence only. It does not establish that samples reached a specific bus, audible output, mixer fidelity, rendered audio, production sound, asset rights, or behavior on other versions/platforms.
