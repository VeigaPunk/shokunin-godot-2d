#!/usr/bin/env python3
"""r104-E1 registration applier — inserts the res_uid_s01 rows into run_battery.py.

OWNERSHIP: this file is a MUTATION under reports/round-104/mutations/. It is
never run against the shared corpus/fixtures/run_battery.py by this seat; the
orchestrator applies it. This seat validated it against a scratch COPY only
(py_compile + anchor-count assertions, never a battery run).

Usage:
    python3 r104-E1-register.py <path-to-run_battery.py> [--check-only]

Three insertions, each anchored on a unique existing byte-string and each
asserted to match exactly once, so a stale anchor fails loudly instead of
silently mis-patching:

  I1  module scope, after RECEIPT_SHAPE_DERIVED_EVIDENCE: the
      `r104_e1_expected_errors` dict (the two rows that deliberately provoke
      an engine diagnostic).
  I2  inside execute(), after `expected_errors = ()\n required_stderr = ()`:
      the lookup that installs the allowlist for those two cases. It sits
      BEFORE `if passed is None:` so it binds only real CASES rows and never
      races the negative-control branch (which reassigns expected_errors).
  I3  in the post-run gate dict, before `"r96_expected_errors_all_matched"`:
      the matching dead-entry floor, so an allowlist entry that stops firing
      turns the battery red instead of dying silently.

  I4  the six CASES rows themselves, inserted before the
      'r96_scene_io_takeover' row (they run before the crash/descendant tail).

Every PASS pin below is a verbatim `godot --headless` output line measured on
Godot 4.7.2.stable.arch_linux.ed1daf0bf — see reports/round-104/r104-E1.md.
"""
import argparse
import hashlib
import sys

ROWS = """\
    # r104-E1: ResourceUID census + id<->path round-trips (builtin + custom
    # .uid sidecars) and the refusal/missing classes. Fixture res_uid_s01.gd.
    # Every pin is a verbatim PASS line measured on
    # 4.7.2.stable.arch_linux.ed1daf0bf; each arm is byte-stable across two
    # processes in BOTH a uid_cache.bin-bearing and a cache-absent scratch
    # project (the only regime-varying field is diag's has_cache, pinned true
    # because the export_readiness row populates the cache before these rows).
    # EXPECTED_ERRORS: uid_collide (the duplicate add_id assert) and uid_diag
    # (`get_id_path(INVALID_ID)` -> `ERROR: Invalid UID.`, cache-independent).
    ('r104_e1_uid_census', 'res_uid_s01.gd', ['--arm=census'], 0,
     'PASS res_uid_s01 census uid_sigs=id_to_text(id:int)->String|text_to_id(text_id:String)->int|create_id()->int|create_id_for_path(path:String)->int|has_id(id:int)->bool|add_id(id:int,path:String)->Nil|set_id(id:int,path:String)->Nil|get_id_path(id:int)->String|remove_id(id:int)->Nil|uid_to_path(uid:String)->String|path_to_uid(path:String)->String|ensure_path(path_or_uid:String)->String saver_sigs=set_uid(resource:String,uid:int)->int|get_resource_id_for_path(path:String,generate:bool)->int loader_sigs=has_cached(path:String)->bool|get_cached_ref(path:String)->Object|exists(path:String,type_hint:String)->bool|get_resource_uid(path:String)->int uid_consts=INVALID_ID=-1'),
    ('r104_e1_uid_roundtrip', 'res_uid_s01.gd', ['--arm=roundtrip'], 0,
     'PASS res_uid_s01 roundtrip tok=uid://bqk3m5n7qar1 tok_id=103876737118377468 tok_id_text=uid://bqk3m5n7qar1 roundtrip=true invalid_id=-1 id_to_text_-1=uid://<invalid> id_to_text_0=uid://a id_to_text_1=uid://b id_to_text_max=uid://d4n4ub6itg400 text_to_id_empty_payload=0 text_to_id_single=23 malformed=<empty>=-1,uid://=0,uid://x=23,not-a-uid=-1,bqk3m5n7qar1=-1,uid://@@@@=-1 sid_unregistered=true id_text_stable=true'),
    ('r104_e1_uid_pathtouid', 'res_uid_s01.gd', ['--arm=pathtouid'], 0,
     'PASS res_uid_s01 pathtouid ptu_missing=res://zzz_absent_e1.gd ptu_missing_is_path=true ptu_noside=res://project.godot ptu_noside_is_path=true sidecar_written=true sidecar_text=uid://bqk3m5n7qar1 sidecar_readback=uid://bqk3m5n7qar1 ptu_sidecar=res://e1_sidecar_probe.gd sidecar_honoured=false sidecar_get_resource_uid=-1 ensure_plain=not-a-uid ensure_path_arg=res://project.godot ensure_missing=res://zzz_absent_e1.gd exists_missing=false get_resource_uid_missing=-1'),
    ('r104_e1_uid_createid', 'res_uid_s01.gd', ['--arm=createid'], 0,
     'PASS res_uid_s01 createid cfp_res=8476142776992359011 cfp_res_text=uid://ds053len3my3l cfp_res_matches_pinned=true stable=true cfp_res_registered=false cfp_res_path_to_uid=res://e1_selfreg_probe.gd cfp_user=4163091229239537790 cfp_user_matches_pinned=true stable=true user_registered=false create_id_distinct=true create_id_unregistered=true cfp_text_roundtrip=uid://ds053len3my3l'),
    ('r104_e1_uid_collide', 'res_uid_s01.gd', ['--arm=collide'], 0,
     'PASS res_uid_s01 collide add=res://e1_x1.gd dup_add_refused=true set_id_overrides=true two_ids_same_path=true a_path=res://e1_x3.gd b_path=res://e1_x3.gd ptu_x3=uid://t1fa remove_a_has=false remove_b_has=true ptu_x3_after_remove_a=res://e1_x3.gd add_invalid_has=true add_invalid_ptu=res://e1_x4.gd'),
    ('r104_e1_uid_diag', 'res_uid_s01.gd', ['--arm=diag'], 0,
     'PASS res_uid_s01 diag diag_queried_id=103876737118377468 diag_queried_tok=uid://bqk3m5n7qar1 invalid_id=-1 get_id_path_invalid_empty=true invalid_has_id=false has_cache=true'),
"""

ALLOWLIST = '''\
# r104-E1: the two rows whose arms deliberately provoke an engine diagnostic.
# Both strings are byte-equal to an observed line on this seat's own receipts.
#   uid_collide — the duplicate add_id refusal (fires once per arm in both
#     cache regimes; the assert names the id that was already present).
#   uid_diag    — get_id_path(INVALID_ID) (fires in both cache regimes, unlike
#     a get_id_path on an unknown-but-valid id, whose text flips to
#     `Unrecognized UID: "uid://<tok>".` once uid_cache.bin exists).
r104_e1_expected_errors = {
    "r104_e1_uid_collide": (
        'ERROR: Condition "unique_ids.has(p_id)" is true.',
    ),
    "r104_e1_uid_diag": (
        'ERROR: Invalid UID.',
    ),
}
'''

LOOKUP = """\
        if case in r104_e1_expected_errors:
            expected_errors = r104_e1_expected_errors[case]
"""

FLOOR = """\
        # r104-E1: same named-by-round / covers-round-prefixes shape as
        # r87-r103 — an allowlist entry above that stops firing turns the
        # battery red instead of dying silently.
        "r104_e1_expected_errors_all_matched": all(
            not e["dead_in_run"]
            for r in census_rows
            if r["case"].startswith("r104_e1_")
            for e in r["entries"]),
"""

I1_ANCHOR = 'RECEIPT_SHAPE_DERIVED_EVIDENCE = {"export_readiness", "export_preset_missing"}\n'
I2_ANCHOR = "        expected_errors = ()\n        required_stderr = ()\n"
I3_ANCHOR = '        "r96_expected_errors_all_matched": all(\n'
I4_ANCHOR = "    ('r96_scene_io_takeover', 'scene_io_lattice.gd', ['--arm=takeover'], 0,\n"


def apply(text):
    for name, anchor in (("I1", I1_ANCHOR), ("I2", I2_ANCHOR),
                         ("I3", I3_ANCHOR), ("I4", I4_ANCHOR)):
        if text.count(anchor) != 1:
            raise SystemExit(
                f"anchor {name} matched {text.count(anchor)} times, expected 1 — "
                "run_battery.py drifted; refuse to mis-patch")
    text = text.replace(I1_ANCHOR, I1_ANCHOR + ALLOWLIST, 1)
    text = text.replace(I2_ANCHOR, I2_ANCHOR + LOOKUP, 1)
    text = text.replace(I3_ANCHOR, FLOOR + I3_ANCHOR, 1)
    text = text.replace(I4_ANCHOR, ROWS + I4_ANCHOR, 1)
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--check-only", action="store_true")
    args = ap.parse_args()
    src = open(args.path, encoding="utf-8").read()
    out = apply(src)
    if not args.check_only:
        open(args.path, "w", encoding="utf-8").write(out)
    print("rows_inserted=%d bytes=%d->%d sha256=%s" % (
        ROWS.count("    ('r104_e1_"), len(src), len(out),
        hashlib.sha256(out.encode()).hexdigest()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
