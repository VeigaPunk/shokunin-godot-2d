# Adjudicator report — round 92 (TileMapLayer lattice)

DECISION: **ADMIT-with-findings** on `5900431`. 14 rows (258→272), all five wave-B gates landed:
verifier VERIFIED-WR, critic PASS-WR, reviewer PASS, simplifier PASS (0 deletions), scribe CUSTODY HOLDS.

Author work: nav scheduler envelope (2-payload, boundary falsification folded), nullts SIGSEGV
armed rc=-6 + required_stderr + site :927, tombstone byte-layout, expected_errors +9 w/ floor gate.

Findings rolled to the fold queue:
1. F1 (verifier HIGH, host class): `r92_tilemap_nullts_crash` ~25% timeout at the 8 s bound —
   signal-11 dump handler 1.5–8.0 s; pre-existing (`crash_spontaneous_sigabrt` same class).
   Candidate fix: raise bound for handler-crash rows or accept the flake class.
2. F2 (3-seat consensus): nav envelope is mode-blind — payload[1] unreachable in the battery's
   launch shape (production regime always lands payload[0]; ff>=140 crosses). Absorb class, not
   silent-pass class; `regions_f2=1` stays the guard.
3. Comment defect: `run_battery.py:1236` says "rc=-11"; pinned value is -6. Fold with next writer.
4. Receipt-caption count corrections (139→136, 93→90) — cosmetic, recorded.
