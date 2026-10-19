#!/usr/bin/env python3
"""r103 C5 gate probe: synthetic evaluation of the two gates the w5 patch adds.

Purpose (C5 seat, exposure/wording audit): the w5 patch comment claims

  (a) "r103_expected_errors_all_matched ... is vacuous-but-honest for it [the
      export_div_ family]", and
  (b) "r103_export_div_count_floor ... A partial drop with CASES and results
      shrunk together is invisible here by construction".

This script evaluates the patch's two expressions VERBATIM (copied from
reports/round-103/mutations/w5_export_div.patch) against synthetic row sets, so
both claims are proven or falsified without running corpus/fixtures/run_battery.py.

No shared file is imported, executed, or modified. Pure-data evaluation only.
"""

CASES = []       # (name, script, flags, expected_exit, evidence) tuples
RESULTS = []     # {"case": ..., "verdict": ...} dicts
CENSUS_ROWS = [] # {"case": ..., "entries": [{"dead_in_run": bool}, ...]} dicts


def gate_expected_errors_all_matched(census_rows):
    """Verbatim from the w5 patch hunk 1 (r103_expected_errors_all_matched)."""
    return all(
        not e["dead_in_run"]
        for r in census_rows
        if r["case"].startswith(("export_div_",))
        for e in r["entries"])


def gate_export_div_count_floor(results, cases):
    """Verbatim from the w5 patch hunk 1 (r103_export_div_count_floor)."""
    return (
        sum(1 for r in results if r["case"].startswith("export_div_"))
        == sum(1 for c in cases if c[0].startswith("export_div_"))
        >= 1)


def row(name, dead=False):
    return {"case": name, "entries": [{"dead_in_run": dead}]}


def scenario(label, cases, results, census, expect_floor, expect_ee):
    got_floor = gate_export_div_count_floor(results, cases)
    got_ee = gate_expected_errors_all_matched(census)
    ok = (got_floor == expect_floor) and (got_ee == expect_ee)
    print(f"[{'OK ' if ok else 'MISMATCH'}] {label}")
    print(f"        count_floor={got_floor} (expected {expect_floor})   "
          f"expected_errors_all_matched={got_ee} (expected {expect_ee})")
    return ok


def main():
    checks = []

    # A: family registered, every row produced a result -> floor holds.
    checks.append(scenario(
        "A registered(2) == ran(2)",
        [("export_div_s02_user_iso",), ("export_div_s02_xdg_override",)],
        [{"case": "export_div_s02_user_iso"}, {"case": "export_div_s02_xdg_override"}],
        [row("export_div_s02_user_iso")],
        True, True))

    # B: full-family drop — gone from CASES and results together.
    #    Comment does NOT claim this fires; the floor's own text does ("the
    #    family is non-empty"). Expect TRUE (fires) only if sum>=1 fails...
    checks.append(scenario(
        "B full-family drop (0 rows both sides)",
        [], [], [], False, True))

    # C: partial drop with CASES and results shrunk together (the declared hole).
    checks.append(scenario(
        "C partial drop, CASES and results shrink together (declared invisible)",
        [("export_div_s02_user_iso",)],
        [{"case": "export_div_s02_user_iso"}],
        [row("export_div_s02_user_iso")],
        True, True))

    # D: row registered but the execution loop produced no result record
    #    (execution-loop splice defect the patch names).
    checks.append(scenario(
        "D registered(2) but ran(1) (execution-loop splice defect)",
        [("export_div_s02_user_iso",), ("export_div_s02_xdg_override",)],
        [{"case": "export_div_s02_user_iso"}],
        [row("export_div_s02_user_iso")],
        False, True))

    # E: allowlist entry went dead in run -> expected_errors gate must fire.
    checks.append(scenario(
        "E export_div allowlist entry dead_in_run",
        [("export_div_s02_user_iso",)],
        [{"case": "export_div_s02_user_iso"}],
        [row("export_div_s02_user_iso", dead=True)],
        True, False))

    # F: empty generator — all() over nothing is True (the "vacuous-but-honest"
    #    property the patch asserts, same shape as r100-critic GD-1).
    checks.append(scenario(
        "F no census rows for the prefix (empty generator)",
        [("export_div_s02_user_iso",)],
        [{"case": "export_div_s02_user_iso"}],
        [],
        True, True))

    # G: floor is a *family* floor, not a re-count of an unrelated family —
    #    a sibling family dropping must not move it.
    checks.append(scenario(
        "G sibling family dropped (no export_div_ rows involved)",
        [("export_launch_embed_boot",)],
        [],
        [{"case": "export_launch_embed_boot", "entries": [{"dead_in_run": True}]}],
        False, True))

    print()
    print(f"verdict: {sum(checks)}/{len(checks)} scenarios behaved as the patch "
          f"comment claims")
    print("note: scenario G's census row is an export_launch_ row, so the "
          "expected_errors gate ignores it (prefix filter) -> True is correct.")


if __name__ == "__main__":
    main()
