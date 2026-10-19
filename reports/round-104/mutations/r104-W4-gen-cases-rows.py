"""Emit the exact CASES tuple text (one row per arm) for the res_uid_ family,
using the measured PASS line as the 5th field, and verify each against the gate."""
import importlib.util, copy
from pathlib import Path
RB = Path("corpus/fixtures/run_battery.py")
spec = importlib.util.spec_from_file_location("rb", RB); rb = importlib.util.module_from_spec(spec); spec.loader.exec_module(rb)
lines = Path("/var/tmp/r104-w4/all_rows.txt").read_text().splitlines()
bystamp = {}
for l in lines:
    t = l.split(" ")
    tag, arm = t[1], t[2]
    if tag == "res_uid" and arm == "s04":
        bystamp[("res_uid_s04", t[3].split("=",1)[1])] = l
    else:
        bystamp[(tag, arm)] = l

ORDER = [
 ("res_uid_text",      "res_uid.gd",     "text"),
 ("res_uid_path",      "res_uid.gd",     "path"),
 ("res_uid_collide",   "res_uid.gd",     "collide"),
 ("res_uid_cache",     "res_uid.gd",     "cache"),
 ("res_uid_modes",     "res_uid.gd",     "modes"),
 ("res_uid_import",    "res_uid.gd",     "import"),
 ("res_uid_persist",   "res_uid.gd",     "persist"),
 ("res_uid_missing",   "res_uid.gd",     "missing"),
 ("res_uid_s01_census","res_uid_s01.gd", "census"),
 ("res_uid_s01_roundtrip","res_uid_s01.gd","roundtrip"),
 ("res_uid_s01_pathtouid","res_uid_s01.gd","pathtouid"),
 ("res_uid_s01_createid","res_uid_s01.gd","createid"),
 ("res_uid_s01_collide","res_uid_s01.gd", "collide"),
 ("res_uid_s01_diag",  "res_uid_s01.gd", "diag"),
 ("res_uid_s02_reuse", "res_uid_s02.gd", "reuse"),
 ("res_uid_s02_ignore","res_uid_s02.gd", "ignore"),
 ("res_uid_s02_replace","res_uid_s02.gd","replace"),
 ("res_uid_s02_deep",  "res_uid_s02.gd", "deep"),
 ("res_uid_s02_deleted","res_uid_s02.gd","deleted"),
 ("res_uid_s02_resdir","res_uid_s02.gd", "resdir"),
 ("res_uid_s02_xproc_seed","res_uid_s02.gd","xproc_seed"),
 ("res_uid_s03_resolve","res_uid_s03.gd","resolve"),
 ("res_uid_s03_missing","res_uid_s03.gd","missing"),
 ("res_uid_s03_refuse","res_uid_s03.gd", "refuse"),
 ("res_uid_s03_cache", "res_uid_s03.gd", "cache"),
 ("res_uid_s03_uidcache","res_uid_s03.gd","uidcache"),
 ("res_uid_s04_persist","res_uid_s04.gd","persist"),
 ("res_uid_s04_classes","res_uid_s04.gd","classes"),
 ("res_uid_s04_collision","res_uid_s04.gd","collision"),
]
out = []
bad = 0
for name, script, arm in ORDER:
    line = bystamp[(script.removesuffix(".gd"), arm)]
    out.append('    (%r, %r, ["--arm=%s"], 0,\n     %r),' % (name, script, arm, line))
    rb.CASES_SIG_BY_CASE[name] = line
    f = rb.receipt_shape_flag({"case": name, "verdict": "PASS", "output": [line],
                               "signature": line, "expected_errors": []})
    if f:
        bad += 1
        print("FLAG", name, [x["why"] for x in f])
print("rows:", len(out), "flagged:", bad)
Path("/var/tmp/r104-w4/cases_rows.txt").write_text("\n".join(out) + "\n")
print("written /var/tmp/r104-w4/cases_rows.txt")
