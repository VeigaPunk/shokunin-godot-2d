# Round 6 — scratch Linux/X11 export readiness

Reproduce: `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing` (Godot 4.7.2 and installed matching Linux template). Named final non-author verifier `r6-export-verifier-final`; report `.shokunin/game-dev-2d/reports/r6-export-verifier-final.md`, raw independent 25/25 record `r6-export-verifier.json`. Prior `r6-export-verifier.md` HOLD caught negative-copy sidecars; corrected runner excludes positive `out` and asserts entire negative output directory remains empty. Initial HOLD remains evidence.

| Observation | Classification | Limit |
|---|---|---|
| Godot `--headless --path <scratch> --export-debug Linux/X11 <scratch>/out/fixture.x86_64` exit 0; 73,703,800-byte file SHA-256 `1a291d3d15e4180b60b0af96cf6458f11fe143636d76575ddf1e23d1a3f24f2e`; `.pck`, `.sh`, `.x86_64` inventoried then deleted | local scratch export succeeded | generated executable, not published or launch-tested |
| Separate scratch copy selects nonexistent preset; exact `Invalid export preset name: Missing preset.` exit 1; output dir starts and remains empty | missing preset detected | does not test missing platform templates |
| `WARNING: Detected another project.godot at res://controls` | nested controls project skipped by export scan | cannot claim all controls or production project packaged |

The runner checks positive process status and absence of ERROR diagnostics, artifact size/hash, and deletion. Matching installed templates plus one successful export do not grant asset rights, prove production readiness, other platforms, launch behavior, or shipping permission. No publishing was performed.
