#!/bin/bash
# r101-E3 discrimination mutants for corpus/fixtures/export_prod_s03.gd.
#
# Two mutants, each aimed at one claimed law of the row:
#   M1 nondet_second_export : the project's project.godot changes between export #1
#     and export #2                -> the repeat-identity claim must reject.
#   M2 variance_escape      : the fresh-import copy ships a different project.godot,
#     so a NON-scene entry differs -> the "variance confined to the scene entry"
#     bound must reject.
#
# Both mutations are same-length (ExportProdS03 -> ExportProdS04) so every entry
# size is unchanged and the md5/sha comparisons are the discriminator, not sizes.
# project.godot is chosen because it is not served from the export file_cache
# (unlike .tscn/.tres, whose conversion intermediates are cached by mtime and were
# measurably immune to an in-run rewrite — see the shard).
#
# Each mutant runs in its own scratch Godot project so the real fixture is never
# modified. Expected: both mutants print FAIL. Observation recorded in
# reports/round-101/r101-E3.md.
set -u
REPO=/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin
SRC="$REPO/corpus/fixtures/export_prod_s03.gd"
WORK=${1:-/tmp/r101-E3-mutants}
GODOT=${GODOT:-godot}

rm -rf "$WORK"
mkdir -p "$WORK"

python3 - "$SRC" "$WORK" <<'PY'
import sys, pathlib
src = pathlib.Path(sys.argv[1]).read_text()
work = pathlib.Path(sys.argv[2])
MUT = ('\t_write(proj_%s + "/project.godot", PROJECT_GODOT.replace("ExportProdS03", "ExportProdS04"))\n')

a1 = "\tvar sha_a := FileAccess.get_sha256(pack_a)\n"
assert src.count(a1) == 1
m1 = src.replace(a1, a1 + MUT % "a")

a2 = '\tif _godot(exe, ["--headless", "--path", proj_b, "--export-release", PRESET, pack_c]) != 0:\n'
assert src.count(a2) == 1
m2 = src.replace(a2, (MUT % "b") + a2)

for name, text in (("m1", m1), ("m2", m2)):
    assert text.count("ExportProdS04") == 1 and src.count("ExportProdS04") == 0
    d = work / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "project.godot").write_text(
        'config_version=5\n\n[application]\n\nconfig/name="Mutant%s"\n' % name)
    (d / "export_prod_s03_mutant.gd").write_text(text)
print("mutants written (m1=%d bytes, m2=%d bytes)" % (len(m1), len(m2)))
PY

for m in m1 m2; do
  log="$WORK/$m.out"
  echo "== mutant $m"
  timeout 280 "$GODOT" --headless --path "$WORK/$m" --script res://export_prod_s03_mutant.gd > "$log" 2>&1
  rc=$?
  line=$(grep -E "^(PASS|FAIL) export_prod_s03" "$log" | head -1)
  echo "   rc=$rc line=${line:-<none>}"
  if [ -z "$line" ]; then
    echo "   raw-tails:"; tail -3 "$log" | sed 's/^/     /'
  fi
done
