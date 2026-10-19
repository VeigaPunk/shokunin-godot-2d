#!/usr/bin/env python3
"""r104 C4 — dump the companion-evidence table (hashes + byte counts + gate flags).

Reads the HEAD captures under /var/tmp/r104-C4/ and writes a compact JSON so the
measurement survives scratch cleanup. Read-only with respect to the repo.

Usage: python3 r104-crit4-evidence.py [capture-dir] [out.json]
"""
import hashlib
import importlib.util
import json
import os
import sys

CAP = sys.argv[1] if len(sys.argv) > 1 else "/var/tmp/r104-C4"
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), "r104-crit4-evidence.json")

CAPTURES = {
    # key -> (capture file, signature an adoption would register)
    "s01": ("r3_s01.out", "PASS export_prod_s01 magic=GDPC"),
    "s01:rep1": ("run_s01.out", "PASS export_prod_s01 magic=GDPC"),
    "s01:rep4": ("r4_s01.out", "PASS export_prod_s01 magic=GDPC"),
    "s01:rep5": ("r5_s01.out", "PASS export_prod_s01 magic=GDPC"),
    "s01:rep6": ("r6_s01.out", "PASS export_prod_s01 magic=GDPC"),
    "s02": ("r3_s02.out", "PASS export_prod_s02 entries=9"),
    "s02:rep1": ("run_s02.out", "PASS export_prod_s02 entries=9"),
    "s02:rep4": ("r4_s02.out", "PASS export_prod_s02 entries=9"),
    "s02:rep6": ("r6_s02.out", "PASS export_prod_s02 entries=9"),
    "s04": ("r3_s04.out", "PASS export_prod_s04 swap=true"),
    "s04:rep1": ("run_s04.out", "PASS export_prod_s04 swap=true"),
    "s04:rep5": ("r5_s04.out", "PASS export_prod_s04 swap=true"),
    "s04:rep6": ("r6_s04.out", "PASS export_prod_s04 swap=true"),
    "s05": ("run_s05.out", "PASS export_prod_s05"),
    "s05:err": ("run_s05.err", ""),
    "s06": ("run_s06.out", "PASS export_prod_s06"),
    "s06:err": ("run_s06.err", ""),
    "s07": ("r1_s07.out", "PASS export_prod_s07 arms=11"),
    "s07:rep2": ("r2_s07.out", "PASS export_prod_s07 arms=11"),
    "s08": ("r3_s08.out", "PASS export_prod_s08 control_exe"),
    "s08:rep1": ("run_s08.out", "PASS export_prod_s08 control_exe"),
    "s08:rep2": ("r2_s08.out", "PASS export_prod_s08 control_exe"),
    "s08:rep5": ("r5_s08.out", "PASS export_prod_s08 control_exe"),
    "s08:rep6": ("r6_s08.out", "PASS export_prod_s08 control_exe"),
    "s09": ("s09.out", "PASS export_prod_s09 census entries=13"),
    "s09:negative": ("s09neg.out", "ERROR: EXPORT_PROD_S09 EXPECTED NEGATIVE"),
    "s10": ("run_s10.out", "PASS export_prod_s10 icon_pack_entries=3"),
    "s10:err": ("run_s10.err", ""),
    "s11:default": ("run_s11.out", "PASS export_prod_s11 pack magic=GDPC"),
    "s11:pack": ("s11_pack.out", "PASS export_prod_s11 pack magic=GDPC"),
    "s11:launch": ("s11_launch.out", "PASS export_prod_s11 launch rc=0"),
    "s11:ladder": ("s11_ladder.out", "PASS export_prod_s11 ladder n1=1"),
    "s11:corrupt": ("s11_corrupt.out", "PASS export_prod_s11 corrupt bad_rc=0"),
    "s11:hang0": ("s11_hang0.out", "PASS export_prod_s11 hang0 rc=124"),
    "s11:alt_main": ("s11_alt_main.out", "PASS export_prod_s11 alt_main rc=0"),
    "s11:early_quit": ("s11_early_quit.out", "PASS export_prod_s11 early_quit rc=0"),
    "s11:all": ("s11_all.out", "PASS export_prod_s11 all rc=0"),
}


def main():
    spec = importlib.util.spec_from_file_location("gate", os.path.join(CAP, "gate.py"))
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    spec2 = importlib.util.spec_from_file_location("auditor", os.path.join(CAP, "auditor.py"))
    aud = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(aud)
    census = aud.build_census(os.path.join(CAP, "cen"))

    rows = {}
    for key, (name, sig) in sorted(CAPTURES.items()):
        path = os.path.join(CAP, name)
        if not os.path.exists(path):
            rows[key] = {"capture": name, "status": "absent"}
            continue
        raw = open(path, "rb").read()
        lines = raw.decode("utf-8", "replace").split("\n")
        if lines and lines[-1] == "":
            lines = lines[:-1]
        rows[key] = {
            "capture": name, "bytes": len(raw), "lines": len(lines),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "pass_lines": sum(1 for l in lines if l.startswith("PASS ")),
            "pass_prefix_lines": sum(1 for l in lines if l.startswith("PASS")),
            "pass_tab_lines": sum(1 for l in lines if l.startswith("PASS\t")),
            "first_line": lines[0][:100] if lines else "",
            "last_line": lines[-1][:160] if lines else "",
        }
        fixture = key.split(":")[0]
        script = f"export_prod_{fixture}.gd"
        row = {"case": f"export_prod_{fixture}_adopt", "script": script, "flags": [],
               "command": ["godot"], "expected_exit": 0, "actual_exit": 0,
               "signature": sig, "verdict": "PASS", "error": None, "expected_errors": [],
               "required_stderr": [], "output": lines}
        if sig:
            rows[key]["standalone_flags"] = aud.audit({"results": [row]}, census, {})[0]["flags"]
        else:
            rows[key]["standalone_flags"] = None   # stderr capture: no receipt claim
    json.dump({"capture_dir": CAP, "rows": rows,
               "note": ("captures are the raw HEAD stdout/stderr of the orphaned companions; "
                        "regenerate with run_all.sh / run_s11.sh / run_s11b.sh under "
                        "/var/tmp/r104-C4 (scratch, not committed). sha256 is over the raw bytes, "
                        "so several rows differ only by an embedded run-id.")},
              open(OUT, "w"), indent=1)
    print("wrote", OUT, "rows:", len(rows))


if __name__ == "__main__":
    main()
