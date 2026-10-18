#!/usr/bin/env python3
"""r101 integration splice for corpus/fixtures/run_battery.py.

Anchored, asserted edits (each anchor must occur exactly once):
  1. Retire ('r95b_order_celloff_y1000', ...) — unmeasured duplicate of
     celloff_x0 (E17 byte-identity reproduction; y=+1000 coverage moves to
     r101_ytrans_y1000 + its falsification cell r101_ytrans_ysep).
  2. Append 20 CASES after the r100b_seq_noclean tuple: 2 r101_seqfull
     (multi-line pins loaded byte-exact from r101-E12-pins.py), 6
     r101_ytrans (E17 verbatim), 12 export_prod (E0 spec table; det_a
     immediately before det_b per the shared-artifact ordering constraint).
  3. expected_errors entries for r101_seqfull_clean/noclean — same
     allowlist line as the r100b_seq rows.
  4. Floor gate "r101_expected_errors_all_matched" (r87-named-by-round shape).
  5. cases_integrity existence prefixes extended with the r101 families.
"""
import py_compile
import sys

ROOT = "/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin"
BAT = ROOT + "/corpus/fixtures/run_battery.py"
PINS = ROOT + "/reports/round-101/mutations/r101-E12-pins.py"

ns = {}
exec(open(PINS).read(), ns)
SIG_CLEAN, SIG_NOCLEAN = ns["SIG_CLEAN"], ns["SIG_NOCLEAN"]
assert "\n" in SIG_CLEAN and "\n" in SIG_NOCLEAN

lines = open(BAT).read().splitlines(keepends=True)

def find_one(pred, what):
    idxs = [i for i, l in enumerate(lines) if pred(l)]
    assert len(idxs) == 1, f"{what}: {len(idxs)} matches"
    return idxs[0]

# 1. retire r95b_order_celloff_y1000 (tuple spans 2 lines)
i = find_one(lambda l: l.startswith("    ('r95b_order_celloff_y1000',"), "retire anchor")
assert "t64_relpos" in lines[i + 1] and lines[i + 1].rstrip().endswith("),"), lines[i + 1][-80:]
del lines[i:i + 2]

# 2. CASES insertion after r100b_seq_noclean tuple (anchor line + its sig line)
i = find_one(lambda l: l.startswith("    ('r100b_seq_noclean', 'r100b_seq.gd'"), "seq anchor")
assert "h7_after_release=A'" in lines[i + 1]
insert_at = i + 2

new_cases = []
new_cases.append("    # r101 (round 101) — C2: full-replay pins closing r100-critic F2.\n")
new_cases.append("    # The r100b_seq rows pin one cell line each of the 14-cell replay, so a\n")
new_cases.append("    # forged extra replay line passed; r101_seqfull pins every cell line, the\n")
new_cases.append("    # in-fixture divergence census vs the 14 fresh-process pins, and a sha256\n")
new_cases.append("    # digest of the transcript (fixture generated from r100b_seq.gd pinned at\n")
new_cases.append("    # sha256 4718a19e…; see reports/round-101/r101-E12.md).\n")
new_cases.append(
    "    ('r101_seqfull_clean', 'r101_seqfull.gd', ['--clean=1'], 0,\n     %r),\n" % SIG_CLEAN
)
new_cases.append(
    "    ('r101_seqfull_noclean', 'r101_seqfull.gd', ['--clean=0'], 0,\n     %r),\n" % SIG_NOCLEAN
)
new_cases.append("    # r101 — C3: r95b --offy dead-flag repair. r95b_order_celloff_y1000 retired\n")
new_cases.append("    # this round (unmeasured duplicate of celloff_x0); y=+1000 coverage lives\n")
new_cases.append("    # here plus its falsification cell ysep (see reports/round-101/r101-E17.md).\n")
new_cases.append("    ('r101_ytrans_y0', 'r101_ytrans.gd', [\"--arm=ytrans\", \"--offy=0\"], 0,\n     'PASS r101_ytrans ytrans offy=0.0000 add_order=[a,b,c,d,e] dy_resid=0.0000 ladder=[t2:4,0,2,3,1;t3:4,0,1,3,2;t4:4,0,1,2,3;t6:3,4,1,2,0;t8:3,4,0,1,2;t16:1,2,3,4,0;t32:2,3,4,0,1;t64:4,0,1,2,3] distinct_ticks=7 last_change_tick=64 t2_vec=[e#0,a#0,c#0,d#0,b#0] t2_relpos=[32.0000,0.0000|0.0000,0.0000|16.0000,0.0000|24.0000,0.0000|8.0000,0.0000] t2_absy=[0.0000|0.0000|0.0000|0.0000|0.0000] t2_vec_eq_canon=true t2_relpos_eq_canon=true n_at_y=5 n_at_0=5 t64_relpos=[32.0000,0.0000|0.0000,0.0000|8.0000,0.0000|16.0000,0.0000|24.0000,0.0000] t64_absy=[0.0000|0.0000|0.0000|0.0000|0.0000]'),\n")
new_cases.append("    ('r101_ytrans_y1000', 'r101_ytrans.gd', [\"--arm=ytrans\", \"--offy=1000\"], 0,\n     'PASS r101_ytrans ytrans offy=1000.0000 add_order=[a,b,c,d,e] dy_resid=0.0000 ladder=[t2:4,0,2,3,1;t3:4,0,1,3,2;t4:4,0,1,2,3;t6:3,4,1,2,0;t8:3,4,0,1,2;t16:1,2,3,4,0;t32:2,3,4,0,1;t64:4,0,1,2,3] distinct_ticks=7 last_change_tick=64 t2_vec=[e#0,a#0,c#0,d#0,b#0] t2_relpos=[32.0000,0.0000|0.0000,0.0000|16.0000,0.0000|24.0000,0.0000|8.0000,0.0000] t2_absy=[1000.0000|1000.0000|1000.0000|1000.0000|1000.0000] t2_vec_eq_canon=true t2_relpos_eq_canon=true n_at_y=5 n_at_0=0 t64_relpos=[32.0000,0.0000|0.0000,0.0000|8.0000,0.0000|16.0000,0.0000|24.0000,0.0000] t64_absy=[1000.0000|1000.0000|1000.0000|1000.0000|1000.0000]'),\n")
new_cases.append("    ('r101_ytrans_ym1000', 'r101_ytrans.gd', [\"--arm=ytrans\", \"--offy=-1000\"], 0,\n     'PASS r101_ytrans ytrans offy=-1000.0000 add_order=[a,b,c,d,e] dy_resid=0.0000 ladder=[t2:4,0,2,3,1;t3:4,0,1,3,2;t4:4,0,1,2,3;t6:3,4,1,2,0;t8:3,4,0,1,2;t16:1,2,3,4,0;t32:2,3,4,0,1;t64:4,0,1,2,3] distinct_ticks=7 last_change_tick=64 t2_vec=[e#0,a#0,c#0,d#0,b#0] t2_relpos=[32.0000,0.0000|0.0000,0.0000|16.0000,0.0000|24.0000,0.0000|8.0000,0.0000] t2_absy=[-1000.0000|-1000.0000|-1000.0000|-1000.0000|-1000.0000] t2_vec_eq_canon=true t2_relpos_eq_canon=true n_at_y=5 n_at_0=0 t64_relpos=[32.0000,0.0000|0.0000,0.0000|8.0000,0.0000|16.0000,0.0000|24.0000,0.0000] t64_absy=[-1000.0000|-1000.0000|-1000.0000|-1000.0000|-1000.0000]'),\n")
new_cases.append("    ('r101_ytrans_ysep', 'r101_ytrans.gd', [\"--arm=ysep\", \"--offy=1000\", \"--qoffy=0\"], 0,\n     'PASS r101_ytrans ysep offy=1000.0000 qoffy=0.0000 dy_resid=0.0000 n_at_q=0 n_at_pile=5'),\n")
new_cases.append("    ('r101_ytrans_ycop', 'r101_ytrans.gd', [\"--arm=ycop\", \"--offy=1000\"], 0,\n     'PASS r101_ytrans ycop offy=1000.0000 a_t2_vec=[e#0,a#0,c#0,d#0,b#0] a_t2_relpos=[32.0000,0.0000|0.0000,0.0000|16.0000,0.0000|24.0000,0.0000|8.0000,0.0000] a_t2_absy=[0.0000|0.0000|0.0000|0.0000|0.0000] a_t2_cross_clean=true dy_meas=0.0000 a_t4_with_b_vec=[e#0,a#0,c#0,b#0,d#0] a_t4_with_b_relpos=[32.0000,0.0000|0.0000,0.0000|16.0000,0.0000|8.0000,0.0000|24.0000,0.0000] a_t4_absy=[0.0000|0.0000|0.0000|0.0000|0.0000] a_t4_cross_clean=true b_t2_vec=[e2#0,a2#0,b2#0,c2#0,d2#0] b_t2_relpos=[32.0000,0.0000|0.0000,0.0000|8.0000,0.0000|16.0000,0.0000|24.0000,0.0000] b_t2_absy=[1000.0000|1000.0000|1000.0000|1000.0000|1000.0000] b_t2_cross_clean=true n_between=0 n_origin=5 n_at_b=5 a_t6_with_b_vec=[d#0,a#0,c#0,b#0,e#0] b_t4_vec=[e2#0,b2#0,c2#0,d2#0,a2#0]'),\n")
new_cases.append("    ('r101_ytrans_census', 'r101_ytrans.gd', [\"--arm=census\"], 0,\n     'PASS r101_ytrans census r95b_offy_tokens=0 r95b_lines=778 r95b_sha256=4f7e945e1b16f241d510e1b1aa7c7fc1aafca6369626e3910bb36cf62d9e2490 replacement_arm=ytrans'),\n")
new_cases.append("    # r101 — C1: export_prod capability lattice (see reports/round-101/r101-E0-spec.md).\n")
new_cases.append("    # det_a must run immediately before det_b: det_b byte-compares against det_a's\n")
new_cases.append("    # a.pck in the shared out dir (fails reason=det_a_artifact_missing otherwise).\n")
EP = [
 ("export_prod_base_pck", "base", "PASS export_prod base magic=GDPC entry_count=16 names_sha256=d3a3d695534079a2e9d3a4f3d2e7e5bbf5b8e2a66110e94c09434611be7bd889 nested_size=15 keep_size=8 drop_in_pack=false uid_entries=0 remap_entries=3 ctex_entries=2 import_entries=2 project_binary=true pbin_size=324 census_match=true bytes=3968"),
 ("export_prod_subdir_census", "base", "PASS export_prod subdir dirs=[data,data/deep,res,secret] nested_path=data/deep/nested.txt nested_size=15 file_count=16"),
 ("export_prod_include_exclude_filter", "base", "PASS export_prod filter include=data/*,secret/keep* exclude=secret/drop* nested_in=true keep_in=true drop_in=false drop_on_disk=true"),
 ("export_prod_zip_census", "zip", "PASS export_prod zip magic=PK0304 eocd=true entry_count=16 local_headers=16 names_sha256=d3a3d695534079a2e9d3a4f3d2e7e5bbf5b8e2a66110e94c09434611be7bd889 nested_size=15 drop_in_zip=false deflate_entries=16 pbin_size=324 census_match=true"),
 ("export_prod_det_a", "det_a", "PASS export_prod det_a sample=1 bytes=3968"),
 ("export_prod_det_b", "det_b", "PASS export_prod det_b sample=2 bytes=3968 equal_to_sample1=true byte_diff_count=0 samples=2"),
 ("export_prod_main_scene_swap", "swap", "PASS export_prod swap pack_boot=main_a source_boot=main_b pbin_size=168 pack_exit=0 source_exit=0"),
 ("export_prod_mainpack_quit_after_frames", "swap", "PASS export_prod quitframes quit_after=5 frames=[1,2,3,4,5] extra=false exit=0"),
 ("export_prod_resource_remap_census", "remap", "PASS export_prod remap remap_gd=true remap_scn=true remap_tres=true raw_gd=false raw_png=false ctex_tex=true ctex_icon=true import_tex=true import_icon=true"),
 ("export_prod_icon_uid_census", "remap", "PASS export_prod iconuid icon_svg=true icon_import=true icon_uid_in_pack=false uid_on_disk=true uid_in_pack=false"),
 ("export_prod_unknown_preset_refusal", "refusal", "PASS export_prod refusal nested_exit=1 class=invalid_export_preset_name preset_listing=true artifacts=0"),
 ("export_prod_templates_missing_class", "notemplates", "PASS export_prod notemplates nested_exit=1 class=no_export_template release_template_named=true artifacts=0"),
]
for name, arm, sig in EP:
    assert "'" not in sig
    new_cases.append("    ('%s', 'export_prod.gd', [\"--arm=%s\"], 0,\n     '%s'),\n" % (name, arm, sig))
lines[insert_at:insert_at] = new_cases

# 3. expected_errors entries after the r100b_seq_noclean allowlist block
i = find_one(lambda l: l.strip() == "'r100b_seq_noclean': (", "ee anchor")
assert lines[i + 1].strip() == "'ERROR: Parameter \"t\" is null.',"
block = lines[i:i + 3]
lines[i + 3:i + 3] = [
    "                'r101_seqfull_clean': (\n",
    "                    'ERROR: Parameter \"t\" is null.',\n",
    "                ),\n",
    "                'r101_seqfull_noclean': (\n",
    "                    'ERROR: Parameter \"t\" is null.',\n",
    "                ),\n",
]
assert block[2].strip() == "),"

# 4. floor gate before the cases_integrity comment
i = find_one(lambda l: l.startswith("        # r100-critic F1 (harness ceiling)"), "gate anchor")
lines[i:i] = [
    "        # r101 author: the two whitelist-bearing seq-replay rows carry the\n",
    "        # r101_seqfull_ prefix; r101_ytrans_ / export_prod_ rows carry no\n",
    "        # allowlist entries (nested diagnostics are redirected to scratch\n",
    "        # logs), so the gate is vacuous-but-honest for them — same\n",
    "        # named-by-round / covers-round-prefixes shape as r87-r100.\n",
    "        \"r101_expected_errors_all_matched\": all(\n",
    "            not e[\"dead_in_run\"]\n",
    "            for r in census_rows\n",
    "            if r[\"case\"].startswith((\"r101_seqfull_\", \"r101_ytrans_\", \"export_prod_\"))\n",
    "            for e in r[\"entries\"]),\n",
]

# 5. cases_integrity existence prefixes
i = find_one(lambda l: '"r100_gui_", "r100b_"))' in l and "startswith" not in l, "ci anchor")
lines[i] = lines[i].replace(
    '"r100_gui_", "r100b_"))',
    '"r100_gui_", "r100b_", "r101_seqfull_", "r101_ytrans_", "export_prod_"))')

open(BAT, "w").write("".join(lines))
py_compile.compile(BAT, doraise=True)
print("splice OK; py_compile OK")
