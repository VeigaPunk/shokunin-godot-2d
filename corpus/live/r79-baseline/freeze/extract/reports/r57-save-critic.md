# Round 57 save/load critic — corruption and persistence falsification

## Scope

I used only the named unique scratch `.shokunin/game-dev-2d/corpus/live/r57-save-critic/`; no fixture, battery, engine/editor source, or other lane files were edited. Godot observed: `4.7.2.stable.arch_linux.ed1daf0bf`. This is an adversarial semantic check, not named non-author verification of the fixture/runner.

## Independent scratch observations

I created `critic.gd` in a fresh scratch project and ran:

```sh
godot --headless --path .shokunin/game-dev-2d/corpus/live/r57-save-critic --script .shokunin/game-dev-2d/corpus/live/r57-save-critic/critic.gd
```

Result: exit 0; `CRITIC_POSITIVE_PASS reopened=true structured_match=true` and `CRITIC_NEGATIVE_PASS corrupted_copy_rejected=true error=43`. The script writes JSON to `user://`, reopens/parses it and compares structured values, then makes a separate copied file malformed and confirms `JSON.parse` returns an error. This supports basic JSON write/reopen/parse and syntactically malformed rejection for that scratch implementation only.

I also ran the same independent script with copied bytes changed from the valid JSON string `Ada` to `Eve` (scratch `critic_valid_corruption.gd`):

```sh
godot --headless --path .shokunin/game-dev-2d/corpus/live/r57-save-critic --script .shokunin/game-dev-2d/corpus/live/r57-save-critic/critic_valid_corruption.gd
```

It printed `CRITIC_NEGATIVE_FAIL validly_corrupted_data_parsed` and showed parsed `name: "Eve"` with parse error code 0. **This falsifies any broad claim that the proposed negative control rejects arbitrary corrupted/tampered data or provides integrity/authenticity.** JSON syntax parsing accepts a valid-but-changed value. Its eventual `EXIT:0` is not a pass for the negative assertion: this scratch test prints the failure but then exits zero; treat the printed FAIL as the evidence, and the process code as a test-harness weakness. The exact malformed negative did yield a distinct parse-error marker, but it tests syntax rejection only.

The executor's current scratch fixture `.shokunin/game-dev-2d/corpus/live/r57-save-executor/save_roundtrip.gd` does write and reopen structured data, and on `--corrupt-negative` overwrites a separate `user://` copied file with `{`, then checks `JSON.parse` error and emits `PASS save_corrupt_negative ... signature=JSON_PARSE_ERROR`. This design detects a syntactically invalid document, not semantically altered valid JSON, truncation that remains valid JSON, a wrong-but-well-formed value, or malicious edits. Also, it uses the JSON parser directly rather than exercising a separate application loader/validation contract. Do not characterize it as general corrupted-data rejection.

## Run-quality caveat

My initial scratch run (before I corrected the source literal from integer `7` to JSON-equivalent float `7.0`) emitted `CRITIC_POSITIVE_FAIL` due to Godot's parsed numeric representation, followed by a misleading PASS print and exit 0. That initial run is not positive-roundtrip evidence. The final corrected run is the one above; it did compare equal (`7.0`) and produced the positive marker. The valid-mutation scratch also exits zero despite its explicit negative FAIL marker; its exit status is not a success signal.

## Verdict / limits

- Basic persistence: demonstrated only as one write-close-reopen-parse round trip in isolated `user://` scratch, with structured value equality.
- Negative: malformed JSON copied bytes rejected distinctly (`JSON.parse` error 43 in my smoke; executor marker `JSON_PARSE_ERROR`).
- Falsification: valid JSON mutation (`Ada` → `Eve`) parses successfully; integrity protection/general corruption rejection is **not established**.
- These checks say nothing about crash durability, fsync, power loss, atomic replacement, recovery, schema validation/migration, encryption, authentication, platform-specific user-data locations, or production save design.

Artifacts: `.shokunin/game-dev-2d/corpus/live/r57-save-critic/{project.godot,critic.gd,smoke.log,critic_valid_corruption.gd,valid-corruption.log}`; inspected executor artifact `.shokunin/game-dev-2d/corpus/live/r57-save-executor/save_roundtrip.gd` (read only). No tracked-file edits or constants changed.
