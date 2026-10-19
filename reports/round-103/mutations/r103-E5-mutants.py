#!/usr/bin/env python3
"""r103-E5 discrimination runner for corpus/fixtures/export_div_s05.gd.

Regenerates the three adversarial mutants of the landed fixture in a scratch
host project and asserts each one FAILs with the predicted reason — i.e. the
three arms' checks are not vacuous:

  mut1_store  notes.tres content changed between export#1 and export#2
              -> expect FAIL reason crafted_store_changed_pack
  mut2_heal   store re-corrupted after export#1 (simulates a non-healing run)
              -> expect FAIL reason store_not_healed
  mut3_ctb    project.godot built WITHOUT the explicit `=false` setting
              -> expect FAIL reason explicit_false_not_text_pack

usage: r103-E5-mutants.py [godot_bin] [scratch_root]
Never runs run_battery.py; all work happens under the scratch root.
"""
import os
import pathlib
import shutil
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[3]
FIXTURE = REPO / "corpus" / "fixtures" / "export_div_s05.gd"
HOST_PROJECT = 'config_version=5\n\n[application]\n\nconfig/name="MechanicOneShotTest"\nconfig/features=PackedStringArray("4.7")\n'

MUTANTS = [
    ("mut1_store", "store",
     'var pack_b := _out_dir().path_join("store_b.pck")',
     'var pack_b := _out_dir().path_join("store_b.pck")\n\t_write_text(_vdir().path_join("proj").path_join("notes.tres"), CHILD_TRES.replace("s05", "s05x"))',
     "crafted_store_changed_pack"),
    ("mut2_heal", "heal",
     'var log_path := _log_path("heal_export_1")',
     '_write_text(store, GARBAGE)\n\tvar log_path := _log_path("heal_export_1")',
     "store_not_healed"),
    ("mut3_ctb", "ctb",
     "if not _build_project(true):",
     "if not _build_project(false):",
     "explicit_false_not_text_pack"),
]


def main():
    godot = sys.argv[1] if len(sys.argv) > 1 else "/usr/bin/godot"
    root = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "/var/tmp/r103c-E5/mutcheck")
    host = root / "host"
    shutil.rmtree(root, ignore_errors=True)
    host.mkdir(parents=True)
    (host / "project.godot").write_text(HOST_PROJECT)
    src = FIXTURE.read_text()
    env = dict(os.environ, EXPORT_DIV_ROOT=str(root / "root"))
    bad = 0
    for name, arm, old, new, reason in MUTANTS:
        assert src.count(old) == 1, (name, src.count(old))
        (host / f"{name}.gd").write_text(src.replace(old, new))
        proc = subprocess.run(
            [godot, "--headless", "--path", str(host), "--script", f"res://{name}.gd", "--", f"--arm={arm}"],
            cwd=root, env=env, capture_output=True, text=True)
        line = next((l for l in proc.stdout.splitlines() if l.startswith(("PASS", "FAIL"))), "<no-verdict>")
        ok = line.startswith("FAIL") and f"reason={reason}" in line
        bad += 0 if ok else 1
        print(f"[{'OK' if ok else 'MISS'}] {name} rc={proc.returncode} {line}")
    print(f"mutants_ok={len(MUTANTS) - bad}/{len(MUTANTS)}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
