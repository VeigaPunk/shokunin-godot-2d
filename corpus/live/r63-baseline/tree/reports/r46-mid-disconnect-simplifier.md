# Round 46 — minimal mid-run disconnect branch (read-only)

## Minimal implementation shape

Keep both r44 connected and r45 disconnect-at-start paths byte-for-byte unchanged. Add a distinct `--disconnect-after-first` mode, valid only with `--repeat-right --second-focus-restore` and without `--disconnect-signal`. Unlike `disconnected`, this mode must still connect `value_changed` during setup, so edge 0 proves the callback ran: after its one-frame check require value `6`, receipts `[6]`, and Label `Value 6`; then disconnect `_on_value_changed` before edge 1. Keep the existing nine events, focus transfers, owner-before checks, and one-frame cadence unchanged.

For this mode expected values remain `[6,6,6,5,5,5,5,4,4]`; expected receipt history is `[6]` at every edge after edge 0, and expected Label is `Value 6` at every edge. The callback disconnection belongs immediately after successful edge-0 state assertions. The new terminal expected-negative marker/diagnostic and exit 2 belong only after all nine checks; setup, owner, or edge assertion errors must remain distinguishable. Add one runner row with a unique case and exact terminal classifier, guarded by the two required mode flags. Do not repurpose or change either prior row.

## Source-state distinction / risk

The current r45 branch is explicitly selected by `--disconnect-signal`; setup skips connecting the callback, and its expected histories are `[]` / `Value 5`. That is not a valid implementation of this round's mid-run condition. Merely changing the flag name while leaving this setup behavior would falsely test disconnect-at-start. The `disconnected` setup boolean must remain specific to the existing at-start control; mid-run state needs its own mode and the existing callback must be connected until edge 0 has been checked.

Godot available in this environment reports `4.7.2.stable.arch_linux.ed1daf0bf`. This is a read-only minimal-branch analysis, not independent scratch evidence or a full battery replay. No fixture or runner edits made. Scope is synthetic parsed actions plus frames only; no OS repeat, physical input/timing, rendering/pointer UI, accessibility, production, or claim about internal handling of no-change edges.
