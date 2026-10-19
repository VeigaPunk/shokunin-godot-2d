#!/usr/bin/env python3
"""r103 V12 — receipt-shape META gate (prototype; closes the C2/G1 implementation gap).

Contract (G0/G1/W7 lineage — `reports/round-103/r103-G0.md`, `r103-G1.md`, `r103-crit2.md`):
a META gate over STORED per-row battery records ONLY. It never changes the
production classifier (`classify_process`) and never executes `run_battery.py`.
For each record it returns {"case", "flagged", "reasons", "accounted"}.

Rules (all measured against the r102 close run, see ACCOUNT provenance below):
  S1 structure, fail-closed: the record must be a mapping carrying a str `case`,
     a str `verdict`, a list `output` of str lines (a case in NO_OUTPUT_CASES is
     the only exemption, and the exemption is an enumerated allowlist, not a
     wildcard), and a non-empty str `signature` when `verdict == "PASS"`.
  S2 banner discipline: exactly one line starting with "Godot Engine", at index 0.
     (Measured: all 538 output-bearing rows of the r102 close run have exactly one,
     at index 0 — a duplicated or displaced banner is a foreign capture splice.)
  S3 whitespace hygiene: no line carries trailing whitespace (space, TAB, NBSP).
     (Measured: 0 trailing-whitespace lines across all 1x? lines of the run.)
  S4 stored-byte accounting: for an accounted case the observed output must match
     the stored account (line count, sorted-line digest, PASS-line count,
     sorted-PASS-line digest). This is the whole-capture equality G-A..G-F demanded:
     it catches an inserted line whose shape is otherwise designed/legit (mut05 s2b),
     because the account binds the capture's bytes, not its grammar.
  S5 unknown case: NOT a flag (a new row must not be born red); reported as
     accounted=False so a caller/census can fail closed at the family level.

Provenance of ACCOUNT: derived (offline, once) from
corpus/live/runs/20261018T213443471189Z/verdicts.json
sha256 65e7fae0ca987563b40601439b4afe5388196c18ffe38dd91a8fc1c09a6a5f68 (1407893 bytes),
554 rows -> 538 accounted cases + 16 NO_OUTPUT_CASES. Account entries are
(n_lines, sha256(sorted lines)[:32], n_pass_lines, sha256(sorted pass lines)[:32]).
A copy of this file under /var/tmp is import-safe: import has no side effects and
reads nothing.

Ceiling (disclosed, per the SF1/SF2 precedent): the account is run-bound and
byte-bound; it cannot separate a forgery that replaces a legit line with another
legit-shaped line in a post-signature position (the r101-crit2 SF2 surface). The
grammar-level extension (designed-verb vocabulary + path envelopes) is the G0/G3/W2
landing path; this prototype is the conformance target for their evasion battery
(mut05: `reports/round-103/mutations/mut05_gate_evasion.py --gate <this file>`).

CLI: python3 r103-V12-receipt_gate.py [--json OUT]   (replays the stored run if found,
plus mut05 evasions and 6 synthetic corruptions; writes nothing unless --json).
"""
import hashlib
import json
import sys
from pathlib import Path

RUN_PATH = "corpus/live/runs/20261018T213443471189Z/verdicts.json"
RUN_SHA256 = "65e7fae0ca987563b40601439b4afe5388196c18ffe38dd91a8fc1c09a6a5f68"
NO_OUTPUT_CASES = [
    'probe_crash_exit', 'probe_descendant_error_spoof', 'probe_descendant_pipe_eof',
    'probe_descendant_signature_spoof', 'probe_error_clause_surface',
    'probe_export_launch', 'probe_godot_error',
    'probe_save_independent_process', 'probe_spontaneous_crash_classification',
    'probe_stream_attribution', 'probe_timeout',
    'probe_unrelated_error_export_preset_missing',
    'probe_unrelated_error_export_readiness',
    'probe_unrelated_error_mutant_broken_scene_route',
    'probe_unrelated_error_mutant_level_collision_removed',
    'probe_while_live_signature_gate',
]
# Measured on the reference run: 8 rows carry verdict PASS with an empty/absent
# 'signature' (the classifier for those rows keys on output/exit alone). They are
# enumerated so the fail-closed rule still fires on any *new* signatureless PASS
# row, and the condition is retained as a note on the green rows.
SIGNATURELESS_OK = [
    'input89_edges_exact', 'input_lattice_api_press', 'input_lattice_phys_peer',
    'input_lattice_pre_frame', 'input_lattice_press_phys',
    'input_lattice_release_edge', 'input_lattice_ui_ns', 'r92_tilemap_nav',
]
ACCOUNT = {
    'animation_property': (3, "b434a4af5c4b0e2a6906f5f47c1e7a9e", 1, "ab0ee83a85764b027f3d7d3f575025f4"),
    'animation_stuck': (6, "becb3d4847299d368f18c70944be10b3", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'audio_bus_route': (3, "eff1019a88ae9c552058fe26a366916a", 1, "939b9a0bdd40a13d8c8ea365c99910cc"),
    'audio_bus_route_invalid_control': (6, "4327c6fcfddc2021b1c83fa820d4b8d1", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'audio_no_play': (6, "863e6361d98cd3b029a77e37fc22e5ed", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'audio_playback': (3, "842a3f01358fc0f7766df216aba63bc5", 1, "2ae5b0626dd1614370cba16eaa799210"),
    'button_activation': (5, "4e077ae049daa737b75dd06390d9f54b", 1, "ce35555ddae2c4fdecc8804063e9c841"),
    'button_activation_disconnected': (7, "fbe81911532f59a29eff572dd2749971", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'button_activation_focus_loss': (6, "f210fe2b10b1149683088138066561fe", 1, "c1720a1e36c598f3563cfbfef24285d6"),
    'button_activation_unfocused': (7, "40a987ee82e45f2398db3c08286d5fda", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'button_group_selection': (5, "50a1112a0f71950abd7bedb3b571b23a", 1, "1bdd075de3562f7f1782e0759d6a34a8"),
    'button_group_selection_disconnected': (9, "99471e0b8fab5779351918a2270375de", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'button_group_selection_ungroup_b': (9, "126b915a1477696f7fc2543fe5f9828f", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'camera_bottom_limit': (3, "03473bf5c622bf39c98bdfd6c3af4085", 1, "435db14b38238087e4f284125ab73791"),
    'camera_far_bottom_bound': (7, "82c16b69a568b9ab8801984c41f69160", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'camera_far_bound': (7, "7d8de825238d3789802c0f1dd6e008f5", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'camera_far_left_bound': (7, "438f50024aa28b6962cdca121fa7791b", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'camera_far_top_bound': (7, "e6716fbbf7f9aa8a7d41faeab5c8eee9", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'camera_follow': (3, "25242e879536617da880dfe806d16217", 1, "58f94e6f2e3bc5725527b6a1b191b506"),
    'camera_left_limit': (3, "8f7837636348da926aee4a90335759c5", 1, "cdc6be68142c854133d62335c7e47e3a"),
    'camera_limit': (3, "925992b7011cf096f04dc9d7a93209e2", 1, "73260578381e5062b6d3e787010b9b65"),
    'camera_no_follow': (6, "7c2d9530ef38593c19b07d4b2f976ca1", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'camera_proc_cam_comp': (4, "ccad3b9c72c2f8f63e053e701d352b54", 1, "fd0c2990450fd39fe47dbaa99c2426c9"),
    'camera_proc_cam_phase': (4, "2c75c70179606ddfaa98119c0edf5bea", 1, "8be12b6e4466bd50e1c9b7541e50ddba"),
    'camera_proc_cam_space': (4, "cf940777082df456cff8a7d80d5a5661", 1, "67e837b95b162923eb6d8a75a46bf4f7"),
    'camera_proc_cam_subpixel': (4, "cc2e44e79f632af5ffb9c987a3401d7b", 1, "ed3bba9e1808fa07bf2dbc8330d9149a"),
    'camera_proc_cam_zoom_center': (4, "d1d1bc60f41779c4b7fd0e4138d6e193", 1, "a85c3346b2e1fffe49a00bc5df242cd5"),
    'camera_proc_cl_draworder': (4, "f2e9bc3e21f89dbde85e4de14a5de3e9", 1, "c157f9a2de9b0f5e7eab25e89913df50"),
    'camera_proc_cl_follow': (4, "fbdf33b21d0207169eb6fd72ae06552c", 1, "235cabf5363ab8292074bdab51db84ac"),
    'camera_proc_cl_phase': (4, "0dc0b45a960d623ea32db137709b7664", 1, "4922147c8ec55ec01aa1fec954d59ccb"),
    'camera_proc_cl_stack': (4, "a238785ae6b11b0eca1516f7c3a7daf3", 1, "0f3099b3d3f49795b0491976c132635b"),
    'camera_proc_par_2d': (4, "b82ec95a9f279d211cae90c6d8501a9d", 1, "68e8a5f71a2f71dcf086d1b2d538b6f4"),
    'camera_proc_par_layer': (4, "9e303a76bdae566ff6160ccf44d04410", 1, "3ba47236ed1f16a5fb81c4417e482c65"),
    'camera_proc_par_phase': (4, "37ff882f22aee0c0de40c2b9b5574ee1", 1, "0e9daf8c93f76b1ef13f32bb3efd405a"),
    'camera_proc_vp_render_indep': (4, "245e9b22ed3fe04622a54efaa83d96a0", 1, "beeaa57253aaaeb9216b5d16f0553ef6"),
    'camera_proc_vp_subcam': (4, "f5f30bac36550ab33f3ffb0fb048585f", 1, "a1ab62845db083b37b6ab530c092a37f"),
    'camera_proc_vp_worlds': (4, "7257172aa51380ab3589787cee090c87", 1, "ff09de9628f19f0e213bb7fe3fa1a6e7"),
    'camera_top_limit': (3, "c34064ccd75fda535dec371e4b78a38c", 1, "7cdcccbbd84bd0d554a4515231dc0af3"),
    'causal': (3, "738cc6d0d14c3761afb7303656b02079", 1, "06d5b5f7763f6bbddc323ef5d7df6091"),
    'checkbox_toggle': (5, "14ca985cf446d3c81e228887b5980d70", 1, "eb35c0ba917a523b2583c0c657898a9d"),
    'checkbox_toggle_disconnected': (8, "967626395bf97cebb06f26ab05902b30", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'contact_no_collision': (6, "70c3056c28150e0b4e9c0ed454230fba", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'contact_runtime': (3, "1b0864e70cb7a0b65e8bef86221ee5a6", 1, "3c32963692307b9cf3386e4970751c12"),
    'crash_self_sigkill': (3, "23d30bb54262a5d12a8ce841bfb63046", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'crash_spontaneous_sigabrt': (30, "08308a95c32be6e42dabb9810e24fcc1", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'descendant_pipe_detached_control': (5, "82c7dfc041da8d95ba86e303ad1938e1", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'descendant_pipe_forged_signature_release': (7, "9bed058490ce79061061621b6344924b", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'dss_lattice_cast_rest': (35, "8bfd91d2fa1d609311946e53b9e235b9", 1, "503819bd71de411e9d8304b566122878"),
    'dss_lattice_census': (13, "f138e59fe33edd50bdeb7a5fa7a2edf9", 1, "3d1529fe19a1bc26ed813337bfacde71"),
    'dss_lattice_excl_space': (16, "93c16872ffb8344093efa5727d0d7f11", 1, "6d766c6c8962e1134aa6c9991e0de97e"),
    'dss_lattice_fresh': (23, "a7bfa6f403d96ea56178f9a6eb335a3c", 1, "68954c2b0689f6b0a46088cbb5545064"),
    'dss_lattice_layer_forms': (14, "05754b02674f58cdea40b10bab495d6c", 1, "ac52c205ca83ca91ada444f3f5b8fea5"),
    'dss_lattice_order_core': (20, "b8170e21c0355d9d165c86b0d23344a7", 1, "e413b0ef328a4a75fc7d672342a0af8e"),
    'dss_lattice_order_core_rev': (20, "5a6ff49f14a533bdab72c85d81be99ca", 1, "836d5b695fcc067e8ad5562fc2489291"),
    'dss_lattice_point_canvas': (14, "2a77197b1b9364e647475da2114d462e", 1, "5dcf8035fcc8a4e6ebf32ef0129077ce"),
    'dss_lattice_point_cap': (18, "5b57023b5eb7d35b94bd72a3e69a7025", 1, "e7d7d38786596b81d76bcb675c9eaee6"),
    'dss_lattice_point_cap_rev': (18, "e54b9dd49d24ca7ebef519dfde0bb9fb", 1, "88f200e72aa7d8eeeaf75ed0bda55e9c"),
    'dss_lattice_point_edge': (21, "f7a842545b2140a27aeaae2d4ba30e9e", 1, "8775a708d080dc7985da8ff954924808"),
    'dss_lattice_ray_flags': (16, "265dc90b8fb43f89a6350d647007b033", 1, "5559cb1810f74439e984aeea1d838edf"),
    'dss_lattice_ray_geom': (16, "9ab54f06bf1f8289751505b451c90481", 1, "03c60cd016b3040e5ab8613b78dd76ed"),
    'dss_lattice_ray_order': (10, "9c5fa4a83415fe8188c1e14faf72cf91", 1, "0997520f4afbbc5fbd2413bf7d8b388d"),
    'dss_lattice_ray_order_rev': (10, "300ef53dc92b896641061dba94676e18", 1, "0ec9683b6358410e1a141df3d9f299f3"),
    'dss_lattice_shape': (20, "c17e5de6b6529664507259c9759f5eb4", 1, "bb00df6bba156da9939eeef4416418a8"),
    'dss_lattice_shape_rev': (20, "51c94b3b60772a78bb87d3de7fa40b6c", 1, "ddc04e976fa15c66a19e8235d91a9993"),
    'ei_bound_refusal': (19, "aecd733356bf3e550fd456b8ebd7e8ff", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'export_launch_editor_mainpack_contrast': (13, "a62a4a9945b5853f37fc67c26a85c02a", 3, "ae05df9b00243ad438caca80859a676a"),
    'export_launch_embed_boot': (11, "395e0eb85499a46fd9586250b6ff748c", 3, "e5c95a04046a217a643397d8d596d80c"),
    'export_launch_embed_mainpack_refusal': (11, "395e0eb85499a46fd9586250b6ff748c", 3, "e5c95a04046a217a643397d8d596d80c"),
    'export_launch_embed_self_contained': (11, "395e0eb85499a46fd9586250b6ff748c", 3, "e5c95a04046a217a643397d8d596d80c"),
    'export_launch_stock_boot': (9, "8dff1150fa0aeaf4c54fe80c97050e3d", 2, "0b24f36534133f65d9dc46b07b2f2f4c"),
    'export_launch_stock_mainpack_refusal': (13, "a62a4a9945b5853f37fc67c26a85c02a", 3, "ae05df9b00243ad438caca80859a676a"),
    'export_launch_stock_missing_sidecar': (13, "a62a4a9945b5853f37fc67c26a85c02a", 3, "ae05df9b00243ad438caca80859a676a"),
    'export_launch_stock_sidecar_census': (9, "8dff1150fa0aeaf4c54fe80c97050e3d", 2, "0b24f36534133f65d9dc46b07b2f2f4c"),
    'export_preset_missing': (99, "a142cc30bec9005d6ba61751c71bbca2", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'export_prod_base_pck': (9, "e112b083753082f3540bc76dcce4e4ba", 3, "9daff7640c1cea145e39149ac499b23e"),
    'export_prod_det_a': (6, "18d6ca3eb93a46e55031568a9e0b9a50", 1, "79b26abf2f0bd27059acdcc06b88dac5"),
    'export_prod_det_b': (6, "41303dacd81014f32cdf5d74cf7116a0", 1, "f9c977eead3e8c05988e1d72cd8e2fa2"),
    'export_prod_icon_uid_census': (8, "2df3d58a8ab99792860cf293f0b815f8", 2, "be95e27b979c23927d2b2d87df44a1ec"),
    'export_prod_include_exclude_filter': (9, "e112b083753082f3540bc76dcce4e4ba", 3, "9daff7640c1cea145e39149ac499b23e"),
    'export_prod_main_scene_swap': (9, "3481578779fdd797dcfc3c2659091310", 2, "b9c307bf7a3649e5c954caca8a67d0c8"),
    'export_prod_mainpack_quit_after_frames': (9, "3481578779fdd797dcfc3c2659091310", 2, "b9c307bf7a3649e5c954caca8a67d0c8"),
    'export_prod_resource_remap_census': (8, "2df3d58a8ab99792860cf293f0b815f8", 2, "be95e27b979c23927d2b2d87df44a1ec"),
    'export_prod_subdir_census': (9, "e112b083753082f3540bc76dcce4e4ba", 3, "9daff7640c1cea145e39149ac499b23e"),
    'export_prod_templates_missing_class': (6, "19d03ca138fd79119301291913bd950c", 1, "ef7793b662471d27273bd7fc63656007"),
    'export_prod_unknown_preset_refusal': (6, "e109e5657a9dd4c1ec6171e55eafc2d6", 1, "b998e75b2ca405d409236041f276c2f0"),
    'export_prod_zip_census': (6, "66ed92a5302db8b34e1efec8fdb2aa6c", 1, "9a94ceb489a8feadcaec5d328d12ccf3"),
    'export_readiness': (269, "0f3b93d3b94877f9a23e346dece50b5c", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'geo2d_lattice_atlasempty': (10, "3a0b71d87ade34e57c6d02470767fd49", 1, "b452342b3676c671670465a5e175115b"),
    'geo2d_lattice_bridge': (6, "dcba1d706e3fc0b99aaa0fa5100c413a", 1, "d3adc8ef9fb6b3a3a4406894316a3ab4"),
    'geo2d_lattice_census': (10, "99af8b5b1792f59aa2bd84c71ff02583", 1, "21bfd4117c33ca1b3b21583579bb1fde"),
    'geo2d_lattice_contain': (17, "c6bcd540ad62f41112244fd8b35dbcca", 1, "e47bf662d2837fbf98641b23e46e424e"),
    'geo2d_lattice_edge': (22, "b4b87450497b86b88221d9dcde9ad73b", 1, "523f13059f3d3d1c248c2e3a3c5170d8"),
    'geo2d_lattice_joins': (19, "fe14d3bea9eb4eb4ac32a88f8ec6c041", 1, "613756625d263d8d361d6592f00fdb0b"),
    'geo2d_lattice_lineempty': (4, "b3dc4ff84b5f15100692fc9d582ae077", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'geo2d_lattice_offdeg': (6, "c896424d864033d90307cac1b47b4765", 1, "f0a3d61bf58c09e0db6b88ebbca8030c"),
    'geo2d_lattice_offempty': (5, "f9967a5aef29f7f503cfe296bb3bb6b0", 1, "c7ca2f7fa634a78afde6fef300aa19eb"),
    'geo2d_lattice_ops': (14, "e205f1160f4827df8234e83890e3783b", 1, "6a5761d94e9dbfc0f9be41e99e7fbd08"),
    'geo2d_lattice_pipedges': (8, "dd96056c00c8f13ca8070cfe1839fa36", 1, "8c08435c0176b379db2bc15687325733"),
    'geo2d_lattice_polyendpoly': (17, "53d1c244961768cba26fe1b0939de00e", 1, "55c6c89a4c1751e9bf0d8a81c4edd782"),
    'geo2d_lattice_pred': (10, "4c71178a7883723fc075c7611990be0a", 1, "83e160225f82e891ab5f0e66f8d8eb98"),
    'geo2d_lattice_ring': (6, "0746c7d8597cda8e6f0cb85f3e34f903", 1, "edd851df888145acec17a3bf68e3385e"),
    'geo2d_lattice_ring2': (6, "ca91c5a4ad97f895015a5f7c1f3e3b83", 1, "a1f0c85cf0c5e7d8c60ec14f50cd5fe3"),
    'geo2d_lattice_ring4': (5, "2e55b32ee9a80f47380d7a1884c6c6ee", 1, "763d4ad44e7287fd52cd4f6169e17a17"),
    'geo2d_lattice_ringhits': (6, "e8da5d6a35be857a1aebfdf169af677a", 1, "8f8a5fd3013ba9add04752e83e20eaa4"),
    'geo2d_lattice_trig': (10, "d703593df398e18dbf51a7cf0dbeeae9", 1, "33c62a760711949ecb08e4790b7e80ec"),
    'health_gauge': (3, "f85c95c210f9ec70fac0011cda0e84ad", 1, "94903a831b6fb9ad3e5e885f14aaa94e"),
    'health_gauge_disconnected': (7, "677a33f053ef5cb203fb02bbe18864e7", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'input89_edges_axisdev': (12, "b64c7fd2d643f4d8609ddae5f0aba622", 1, "f0d61dbbd2b9be04f93ffbb12712e9dd"),
    'input89_edges_exact': (14, "a7ccb4e53643e5afed9df6338691a719", 1, "ef834ace0eefcce6bd35282b68e652bc"),
    'input_lattice_acc_flush': (4, "6d27929e8aa67dc346be3e28ec18b4be", 1, "c95d1d802ed1860f6b3c5f4d8f681dfd"),
    'input_lattice_acc_off': (4, "3a4701b450f47eb137a0546aba6114e5", 1, "7a5671e288d6afd5dbb5e3f1823d5f2e"),
    'input_lattice_api_press': (4, "e54a2d3d691c5b6f5c44bf1830108278", 1, "91fbc03f0698c4ea1d1ce225113935e1"),
    'input_lattice_burst': (4, "03e300b8aeb2b7d3d8de64ca2bac57ae", 1, "0a554fcbfd731e1a1cffea0da63b251d"),
    'input_lattice_census': (4, "701a2b2fcd598d76409f6b7b0f5270c9", 1, "d9b042fc29e4add1a55ea9d19fc050b2"),
    'input_lattice_conflict': (4, "fab853fd9f714f5d6876f0c204acd873", 1, "8e7937419e431fc8169d1f95514255f8"),
    'input_lattice_dev_joy': (4, "0f52f7e229e7f799d80ab97961728acd", 1, "40d38f88d28f956008a975785d13945a"),
    'input_lattice_dispatch_order': (4, "c0cddaa34b410579c5cdaff549d75067", 1, "965b4eb863e7e2e952ad4b8d19517abd"),
    'input_lattice_dz_ladder': (4, "d469644e0393619e6dbae75aeee227cc", 1, "5f9e22ef5a19229a3aba9a37c6ac63e0"),
    'input_lattice_echo_edge': (4, "c83b18a1857e9d2fcf8f0f716fdc2d27", 1, "ed80551ad277df73f4aedd1549d77cff"),
    'input_lattice_imap_erase': (4, "61233c8b890f102dfb4feb622b33b61b", 1, "962c9b7ba26de596f33995a563c76a61"),
    'input_lattice_imap_mid_cb': (4, "3f31f7a7f2bea73d56bbdfd5bad4bfd2", 1, "3b7740ec53b446a1de027ed9c26d066d"),
    'input_lattice_joy_axis': (4, "751d4c1eb38ceb88d1be33e8b8d3ae51", 1, "4a0f6b6aeeb6a6e5ecfbe447362a7efb"),
    'input_lattice_key_map': (4, "1656ca1f297322ba3c98ea776313b62b", 1, "71be13b05ac68f02ee7ce259ac1ae6b1"),
    'input_lattice_mouse_hdls': (4, "8cb17edfa7b48aa8570996f8b40eb806", 1, "f817443e1e5241bad05267bac6b97e39"),
    'input_lattice_null_edge': (24, "0dea8e0c48672e0e55c08b8573ff5803", 1, "a0a79bb9fddc3f2982e67a33cfb36f4f"),
    'input_lattice_phys_peer': (4, "6d0257202b30ca09a31a3780476d5937", 1, "d6d21fcc3c25a77d90697cc84c8e4851"),
    'input_lattice_pre_frame': (4, "a3c0e9fb24768b44c3035982e2e0feaf", 1, "a2d0eb87c556401a680fcbbd5a36fc5c"),
    'input_lattice_press_idle': (4, "bd634e944d6c7843685836fffb3002dd", 1, "8b1e3f5e087fa7594fc0dc14eec77999"),
    'input_lattice_press_phys': (4, "1012f475b26f4d5cbe36f9dfefe9ab06", 1, "da192e0560da36062041b6bd45143406"),
    'input_lattice_reentrant': (4, "f400697ebcc4b79f72da823ffc08e81e", 1, "c663a09a1315fa61db5019e3ddb5a87f"),
    'input_lattice_release_edge': (4, "b82c752ae757d0ab4ace175a70ad768d", 1, "293c74981f025be4f9c047377f572d60"),
    'input_lattice_ui_ns': (4, "97144d2bd72841f6345c59ebcec5b2ab", 1, "536006f86237780528a46f0f3f4e57f0"),
    'input_route': (3, "a182d01eb12472430cffe892019e9f4c", 1, "7ea482d8a8a98dffb47b5b4516c92b56"),
    'keyup': (3, "5d1fe33f4054c6939d49176722a7a28c", 1, "89d5acfb1f847b4a28f0aefb3ded0e1f"),
    'level_collision': (3, "2a4fe9a03782c718a6f71cab5011808e", 1, "d97abc486ee4999f720c7fcd47251368"),
    'mechanic': (3, "40b5d7cb14b3108b22aa5bae3b4f84dd", 1, "952889cfac0abe896fd0a6a14d34be40"),
    'mutant_broken_scene_route': (6, "5a906ec1cb2e5391201876aac66d8741", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'mutant_level_collision_removed': (6, "e951fc280c40875f78bacb5a05d82c93", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'nav_lattice_agent': (3, "cfceee5a85fa704d8c103cb83b06d575", 1, "9e0cd81d0619c9b72b1995b8dd2e3e0e"),
    'nav_lattice_avoid': (3, "d151efbbc94d51430469e8632540666d", 1, "3da4c510c902903d6d18561a61b53ac9"),
    'nav_lattice_bake': (14, "c83eb60ec3a01235a5dcb6512617a97d", 1, "33bb61d29086fdf53258a70beb9bd19a"),
    'nav_lattice_census': (3, "94e7ed3c29f49a87da7c8da4ea4138ce", 1, "2072cc8dd35a8868bef1e136a640ceab"),
    'nav_lattice_link': (3, "19d4780e9f5ffd9cede866f72a37cda5", 1, "201c1e9e8c0f64adb8eccda01850b34e"),
    'nav_lattice_path': (3, "1c8d3b8b1119362c718c5383706f1ebb", 1, "77fa66003c03ae2194329c56762b6657"),
    'nav_lattice_query': (3, "2ac46fdcae6a4063b03156e30a3abbeb", 1, "5b79960ba384f8b510be9a42947aba9f"),
    'nav_lattice_region': (3, "830bb3003ee65f4dc905ba13f284e0fa", 1, "73bae3ff6f10192a0c3809783d94a974"),
    'nav_lattice_sync': (10, "6a2fe5d4d8523b9da0433d84f51a93e3", 1, "7e8fdcd917f102fd204c2e718bbaa07c"),
    'nav_lattice_teardown_clean': (3, "4e02c274a02cb35cf861f7685ff382ac", 1, "a7afdc1da8d6700945cae5d51e18189e"),
    'nav_lattice_teardown_crash': (4, "05121c34bdd669a0b85c016c4f54fa44", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'negative_overlap': (6, "47b53195b43c51f19f63e6a5e76604b9", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'negative_route': (3, "fe6cbd79d10ebcf558bfa0a47e4342ae", 1, "c14fba25b0efbf12314e9874c07128e3"),
    'negative_signal': (6, "f94d5154622823b199cdef402a58e99f", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'negative_transition': (11, "ce2268a037440baf7733ac01413eeee9", 1, "1a5e8e78017076a1937a2a698b3777a8"),
    'overlap': (3, "8ea9a6c7c616c1f3280c4c332e57e0e5", 1, "89917a4e67fb4ae4fe2a7aea1edba440"),
    'phys2d_backends_census': (3, "319025ced289e8185040f998ae8be33f", 1, "dac7ee721de9f294d505825f73e3c1c8"),
    'phys2d_backends_dummy_degenerate': (3, "2eaa2ff7986540827627991b5fa7ba4e", 1, "4a0a199d05d3eec87307eabb1c118a29"),
    'phys2d_backends_dummy_timeout': (3, "b2784d791b2b412c3c74ff3a273385b3", 1, "9ab8c14f06eb1147a7c31dcda70a58c7"),
    'phys2d_backends_gate_duality': (3, "96e8936ab9c983c82ba6c4092009a1f1", 1, "850a86b3392b173fa8d845141132fe9b"),
    'phys2d_backends_gate_matrix': (3, "1c85ac62e7b5afbe2bbbd34ff7db7229", 1, "fc1bbbd55a4bf9b9ba68d8a2c67341c8"),
    'phys2d_backends_jolt3d_live': (3, "3bc163b93166bf38286fc0622f740ce2", 1, "e9f500ab9150d16b240a6cc5d35d3ba6"),
    'phys2d_backends_lattice': (3, "aa856a2d3edeedffdc702b689956db06", 1, "b700f237f8c05553a4c78d4eb1fc26c1"),
    'phys2d_backends_xcheck': (3, "5a9e198ad6c8588acac57679f1b6271d", 1, "123f92c5f666d070b3911a4ed29accc3"),
    'phys2d_events_area_dss_in_cb': (4, "d830002367b3e5c0f38ed1a36a86f6db", 1, "a2d6448c42a3c40cb349f6bcaff884b5"),
    'phys2d_events_area_edge': (4, "665f777aa0c57fb943ebf4b1b1fe5d5c", 1, "607e3e987ba28c150efb7bdebf055c75"),
    'phys2d_events_area_free_rid': (18, "7e58f3c3725c1386ce981e554232db2b", 1, "2b97c6a47ca1c2b84831d652b33efb9c"),
    'phys2d_events_area_monitoring_deferred': (4, "e31905e73a04adf549521ed947f80a3c", 1, "80541efe9a9e42ea72bcdfbac1d6fa98"),
    'phys2d_events_area_monitoring_direct': (8, "32ea81753e9c210d1727273e1c9fe152", 1, "a9397fdb36d78313b2c58a910e74c85c"),
    'phys2d_events_area_node_position': (4, "325dd58c4e1c149bbedac8ea733a7d05", 1, "1303762636fd1b1f627d8ada92fa6d6e"),
    'phys2d_events_area_queue_free': (4, "dbdfadc6a4981fd217852a4f261e9676", 1, "0207f5c68b9c93895758a7375ae4d552"),
    'phys2d_events_area_srv_set_state': (4, "0999889662b45d51b8588b6d23540945", 1, "79875be52a8ae5aa7a386ee1521311e1"),
    'phys2d_events_cm_deferred_cb': (4, "1954d5836db3ffc136101660018bfb66", 1, "3db55b1eec968fd02b61be251f4174dd"),
    'phys2d_events_cm_max0': (4, "0638e2e0fccde3fbf11da99896976113", 1, "f6a493b9c24809053863b7bd8bb6d117"),
    'phys2d_events_cm_max0_cb': (4, "8452ab630a7f1e474d953db96f587ab6", 1, "a0167a78836e90d71e75b1af448363f8"),
    'phys2d_events_cm_off': (4, "5ae1c1877ab64850c4da1ef9e646879a", 1, "9516e68cdb36c072f0a265970bfc4128"),
    'phys2d_events_cm_on': (4, "b00c96fb2d6e12ba788c44f60dddd127", 1, "d77636fa8a259be0b9489cdfbf538529"),
    'phys2d_events_cm_toggle_cb': (8, "1fe64d4fd91e4eb57e6285b031d4b600", 1, "ec1c902b5bd75b445c937ca3aff54ab4"),
    'phys2d_events_edge_node': (4, "0fe9abf38c38e7d135c371eb0bb24f71", 1, "667de7b32e32dec4947177589c8b12b5"),
    'phys2d_events_edge_node_srv': (4, "0244d64aedba6682052258f034731fc0", 1, "dabbf8c08bb749762e76a15cae9268f4"),
    'phys2d_events_edge_revert': (4, "a0c72c35283953ca215980ff4d7e4710", 1, "6e3160c349577ff12ee303dc5df8fc2e"),
    'phys2d_events_edge_srv': (4, "21a10d79fd8bfe624a9b0e74e4a937fa", 1, "95c7380d626e965111943dbaf078f9c4"),
    'phys2d_events_rb_dss_in_cb': (4, "94774506d106a538f59260c419b076a3", 1, "fad4dc6893dbf0a9b58ed197e097e5b1"),
    'phys2d_events_rb_free_rid': (18, "40fed22466058698b514a55ec63d1814", 1, "3a4bb3dbd0d80871a235a3a9ca2c4746"),
    'phys2d_events_rb_node_position': (4, "4f34badfc5cfdaa64213b097be53eacd", 1, "dd3200a69fba93f5cc8bb33a6348ab5f"),
    'phys2d_events_rb_queue_free': (4, "2eb0082b177877cc758a25dcfba3eede", 1, "0682b0b1037b274ea1f54c8643c13420"),
    'phys2d_events_rb_srv_set_state': (4, "02c261dbf5d80c210f8fe57f00fec5f7", 1, "7c8b2deb92a81c38615a164eac8458f2"),
    'phys2d_joints_area_body_gate': (4, "3789c7bdb3b89e3a970300a79c8c05ce", 1, "3263adfdfa3c3a1dab6c1cc6e3f135dc"),
    'phys2d_joints_area_entry_order': (4, "f417ef6af03335e389f340828e185ac0", 1, "a885cfa17d80c254cd0bff57262d905b"),
    'phys2d_joints_area_lattice': (4, "ffc6fe0b3f4baf23eecbcc091ae98dae", 1, "23f0fe68b4296272194030e1ca7218ff"),
    'phys2d_joints_joint_census': (4, "fbc7dc1dd1b89525da40bb70f632ed85", 1, "54e6bb1446a67fe15b6144c02902fbc6"),
    'phys2d_joints_joint_disable_coll': (4, "aac12daf723992453e3fe2d090bbcce9", 1, "e749daeedc8811fe61ff8d3cfd623b4c"),
    'phys2d_joints_joint_freed_rid': (39, "af25c404067950845ef833a59010d0ed", 1, "3a3d71c482cd6ae8bfa8683015b6adcb"),
    'phys2d_joints_joint_groove': (4, "a5c2f967efde96f7e00c93458928e860", 1, "354ed43b06a3e350e504d1ca41937b81"),
    'phys2d_joints_joint_node_anchor': (4, "9002efa4a9b7222b335bc43955749dc5", 1, "0d6b7a85069260443c06eb0aff0bc2ec"),
    'phys2d_joints_joint_node_clear': (4, "b16f5ce412dddd7632628915202d28e1", 1, "5ff055ba100fd05b460ff52f11eb63a0"),
    'phys2d_joints_joint_node_freed_rid': (27, "aab3a9ed46f418eccab1a1d5eec5518c", 1, "d7123602fb7fec46b5d792fea1e64d6a"),
    'phys2d_joints_joint_pin_clear': (9, "0280c6192e4e320932d2c421b8b9fb80", 1, "8f7deea3a814bf11ad235e38ad6ebf3a"),
    'phys2d_joints_joint_pin_params': (4, "501e9fe2d4aee42f2a87600a3ad0e780", 1, "05286c108355e64bd6b02b33eb119e6c"),
    'phys2d_joints_joint_pin_tiers': (4, "ff7fa1b907884ed46a87411808496f9f", 1, "5a1fe3abf455fe5ede98517f52123fd9"),
    'phys2d_joints_joint_spring_env': (4, "171e28f1b128052bcdbdc6d18edb4236", 1, "b056b1bb80369cb2a9c982bf6bddfb5c"),
    'phys2d_joints_joint_unset_refusal': (76, "48ceed51e0a270e07a4bc2519bd5010c", 1, "33d2481458ff17009e5cecae70b24725"),
    'phys2d_joints_layer_dyn_pair': (4, "acf6252f40e3eb509e886d9a6c0b9555", 1, "6aced0892c7b891d092b38526c921e72"),
    'phys2d_joints_layer_flip_cb': (4, "bdd0536d2df12b37a76dc18bf7ea705c", 1, "bc8f570989dde38904e0d9a1d604c811"),
    'phys2d_joints_layer_flip_mid': (4, "b636f615b9228b1ff72ab0d98522e5c2", 1, "ac02afa093fc97ad689b67ea9e8f2e14"),
    'phys2d_joints_layer_or_table': (4, "a0462da98e827fcb531ad6d044499277", 1, "eafc678ed0ea0f55ef85f084d04cd6c9"),
    'phys2d_joints_layer_zero_table': (4, "89aeca4913aa16567fde62c4bb7209d4", 1, "350dd756a3405443d58a6d5a5e3ce94b"),
    'phys2d_motion_bds_windows': (4, "4bed51ed9b43c48a9aef26d4b8c6742a", 1, "c17190a0f59fe2469a0289b5472a03c6"),
    'phys2d_motion_btm_embed': (4, "4695e7f3fafe0b41e07488f1be142f4b", 1, "c3248e633239fa748d931c3293578d1b"),
    'phys2d_motion_btm_from': (4, "790791f3923072284625d0fb6e7c0660", 1, "9b960d1386b3d9c211fded741206eff7"),
    'phys2d_motion_btm_from2': (4, "cf1f864b5bc5dcb787a710eea45711db", 1, "e2caa508d08b2c6203c7784ad492a2e8"),
    'phys2d_motion_btm_hit': (4, "434f260fd0cf7e5bb43c16a265645b30", 1, "a3bf24e13c7805efe056f97dfdb600ba"),
    'phys2d_motion_btm_margin': (4, "7e165e3039a573639b10bac42b3acab4", 1, "65740f062838af9f80a95ef654dd2ff7"),
    'phys2d_motion_btm_recflag': (4, "b62d2593d2aa97f8c13f1da2f42c31c2", 1, "7d19cb20c58d02692708308e0fb4ce09"),
    'phys2d_motion_ccd_edge': (4, "5bf21488e3ca3111133515282f931b41", 1, "48beea86d77ba6a3585c2695164768f0"),
    'phys2d_motion_ccd_gap': (4, "93820e606c4936ebc16f3aa564e41067", 1, "acc1b95a107cd0b20c3e21e6a5f1b4e8"),
    'phys2d_motion_ccd_ladder': (4, "919f7731a2a3056855ca3117cd50e4a4", 1, "1ec047c2360003eae96dae2b51f09f0c"),
    'phys2d_motion_ccd_spin': (4, "298bf02eebeff414c77d74c5d2e3fc8e", 1, "9db50dd5b563ce9531e53f748c844cda"),
    'phys2d_motion_cont_cap': (4, "058a2955f59456923cc35eaa946423ac", 1, "009fe37f0029d646fd13091f6619c3cc"),
    'phys2d_motion_cont_persist': (4, "2b42e44a70ae9f3b527e9c5d218c39a6", 1, "79e28162395a1d55fb358c43f310932c"),
    'phys2d_motion_cont_windows': (4, "2ee8f8e0abc13a7efeaaad0023e09806", 1, "a9d71e5820fe7a4b5f6198bfe6c4bcca"),
    'phys2d_motion_dss_embed': (4, "bb390449216885e8d6403701f007729a", 1, "cdf2825ae562e1364d378801885898ef"),
    'phys2d_motion_dss_motion': (4, "bd4e13eac3a525cee107d9033c23ef62", 1, "91e0aafa3ecd39837173ba073a97d3c8"),
    'phys2d_motion_dss_purity': (4, "b5701f06009ab4e141574a725d0582b2", 1, "f5f9f449c10ed1f06e068c8328b6c221"),
    'phys2d_motion_dss_shapes': (4, "b90e39ce88d610e6361cf95a48415a07", 1, "eb06075aecff3e9a79352d0622eb36cf"),
    'phys2d_motion_dss_wrongarg': (39, "9e822927737c329815228707063afefd", 1, "902949809d30890d88b4e30c352f1c2c"),
    'phys2d_motion_mac_chain': (4, "47591e658ceeca50c43e3000e0fe317d", 1, "a3e59f10d7d0f4d8f7b001db01c9f41a"),
    'phys2d_motion_mac_embed': (4, "e951051dfa1af94e92a189d02367f21b", 1, "6cee63f0076e4897ad21881f398dacd0"),
    'phys2d_motion_mac_hit': (4, "4c1ecb5c444405233089a4664809abb3", 1, "2c0f694a8e4e2d819df1ef91b113a3c9"),
    'phys2d_motion_mac_maxcol': (9, "421d4df952bd74e155a09d0c237a72fd", 1, "2806a5716f409404bd1a7e71611eed8b"),
    'phys2d_motion_mac_miss': (4, "7b7036dfaf91f2d71f2e21a7f18e9d0e", 1, "974facea1915aebec223be8612cc9155"),
    'phys2d_motion_mac_nodecomp': (4, "acc6dee191f1d00f8caafe9f5fe0930f", 1, "0040de5e594c070cb0e88320dd261036"),
    'phys2d_motion_mac_rigid': (4, "f672fb94f104dfa035ef8d5f3568fd37", 1, "ccf89a0fd0429c313f7ac7d8b0f54033"),
    'phys2d_motion_mac_test_only': (4, "6dffe3b9c493f92aefc9b5939e2bc1ed", 1, "cbcc142fc97cc6b96cb2e70e610a64ee"),
    'phys2d_motion_tm_hit': (4, "8822e08d61e9e750860ba2e74daca128", 1, "daf062c90139516fc66f00386224228b"),
    'r100_gui_census': (3, "839430feb6d3c4a2da41f8d5f934943a", 1, "6a41933327f91bf1512198d7eef649f5"),
    'r100_gui_clip': (3, "4f9130c7b09614a50c4fd67917813cca", 1, "99dbeea71a8dfac3375cabfd595dfcca"),
    'r100_gui_cursor': (3, "1bfe928e89a32c70d8ee51a6c16de276", 1, "64f02c838b627df0860a36958a04617c"),
    'r100_gui_drag': (3, "8b1b03a7a00a970b210ade7a1fc522dc", 1, "3f27abc5ace0597b7539169c9c10cc71"),
    'r100_gui_focus': (3, "4e9a1b18506a2994fbf38323e564c230", 1, "7ea628f11f8fe358c83f97c173379acd"),
    'r100_gui_hover': (3, "e770017e415a1f5db57398f92afc326b", 1, "7a9c45585bb74b120f9374a94204462d"),
    'r100_gui_localpos': (3, "1da194d8e20c617b7be62a126a3ad597", 1, "dc43ad553e8de02e7575830d1a3d0f0e"),
    'r100_gui_motion': (3, "0e0c06f71db57d9171f7ea033fc1d6da", 1, "9dd0fc4c703959db24147140550cfc38"),
    'r100_gui_osmeta': (3, "6782d53d69ac94e32cd3da879e8fa95f", 1, "b5975a6b9cd89882bf2625d2b674f82a"),
    'r100_gui_render': (8, "675d92b7ec85f4fd842d82903f13f612", 1, "c22bb40db5a79f2d1eb659a7ad833a43"),
    'r100_gui_routing': (3, "103743e26f87e092f067fc1c1ea65440", 1, "7ce4a5ddc99c3d2c5e32d449576a5f25"),
    'r100_gui_subvp': (3, "616ccbe4fe8fb82190a1c526df8a11ab", 1, "74d83847e37ba1ef12ce222ae9191317"),
    'r100_gui_touch': (3, "dde64bc36bf4ea8588eb038f7201da98", 1, "e5bb1bcb48424985c340d89f991eb69c"),
    'r100_gui_warp': (3, "1125868e6b59fcedbb176e8d96452f3d", 1, "325951051a25c3ae2a125f4a0cfd1b3b"),
    'r100b_emul_state': (3, "cc909bc19d40d6e2f046d08d20b73c7c", 1, "313a8462c35ff81ad4669149e106bacb"),
    'r100b_phase_coalesce': (3, "17b81811b9a4f7a030cbf611ee49ad90", 1, "2f7f917c0cb07f01fbf951783af462a7"),
    'r100b_phase_cursorphase': (3, "21a8f7af947cae7059c652e81e84246f", 1, "3100ee93ecab08be43430dda62384677"),
    'r100b_phase_dblclick': (3, "99a4009d0b2f4c32e9a1cc28fbbf2fe3", 1, "a64336a5d8a43b8bf049d7696d6986d4"),
    'r100b_phase_dragphase': (3, "89a96da5b45658006bee4483a448bedb", 1, "8fd288b845f2f5555cbf7a9a54e14a17"),
    'r100b_phase_flushpos': (3, "54d13c9595bee6c7f0c4ca44f5e8e028", 1, "a4a8ec00200e2d7c6c78bf88fd8ca0ac"),
    'r100b_phase_hoverphase': (3, "02251901e2f44101cd8059338c0a4301", 1, "2fb20cf827ddd664e09f48d35ff772e0"),
    'r100b_phase_orderin': (3, "b8e63b871c74912e2948af411912ba3c", 1, "ab4ed7aa3d57c5f1a8c3ffcfbca0b855"),
    'r100b_phase_velphase': (3, "d2c6a41ee31a8eb232c303a19ab1a474", 1, "3b8392bfe1be87cc18425ba5567bfb7b"),
    'r100b_seq_clean': (23, "6548c1530f6c915aad5109ef53948455", 14, "eae78045bd1277735fb30a3a5776c944"),
    'r100b_seq_noclean': (23, "7b8c56bafef57ee45e4eb5f51967806f", 14, "1dc127c77b9a4e948e62307d97dada97"),
    'r101_seqfull_clean': (25, "e13c66fe6e3283dc9560a3479ad9e3b5", 14, "eae78045bd1277735fb30a3a5776c944"),
    'r101_seqfull_noclean': (25, "047c8cdb0bc5130a7cd766d33f7f8826", 14, "1dc127c77b9a4e948e62307d97dada97"),
    'r101_ytrans_census': (9, "67dc4a79352747b9fb1052aa134df94f", 1, "2e7e267e4b46ecfb7b5c300cb561d7d8"),
    'r101_ytrans_y0': (19, "0e30ab918a5a2cb426c5c275b1d1a334", 1, "07851d90e6dc2f77640926d5c62ffcda"),
    'r101_ytrans_y1000': (19, "30149fc5e23cc4daf7d523738b954f60", 1, "25ccd7fe1220b11e622e94605b7c98eb"),
    'r101_ytrans_ycop': (23, "eac0871c17d8887f2258b7fc023d5df3", 1, "2035938bf1e1eb42f5d23a24ea07db88"),
    'r101_ytrans_ym1000': (19, "eab443660a10382b0717497b88367df5", 1, "30097a8f502f60c604e674de92b0fab0"),
    'r101_ytrans_ysep': (9, "abccaa2f4738854e3fdd292281fffdac", 1, "6049099c2451e7c4b10dff23c5ec186b"),
    'r87_edge_jpbe': (6, "50450e023cfd4c28b886705c2e756294", 1, "876c4f4f435d7f2239feba11219160d6"),
    'r88_surfaces_audio_pos': (4, "5e3ba153d9740677eb302e1b292f0ce1", 1, "2a398d7c01fcee1630f99bae084cb60b"),
    'r88_surfaces_light_props': (5, "f00f38a96fa1f7ac1d5f55020959e718", 1, "673f9924522d44d69fdbdffcbc818f5b"),
    'r88_surfaces_mp_loopback': (6, "3cead9a03f7adec8435eaeecf194ff57", 1, "31d82b153d9aa8a1dfb44d05c1eb32d7"),
    'r88_surfaces_mp_offline': (5, "0a9396bb75b650605b204a0d79eb1e6f", 1, "3206a5cde7d757558728c65233796ae5"),
    'r88_surfaces_mp_spawner': (5, "a57013497f52c44d1f82f2f91c1e1113", 1, "7975be26b48c73f184381e5cc5ebf740"),
    'r88_surfaces_sprite_meta': (4, "f4254fd6df6824be11dc4fead52f626a", 1, "33dd0e4cb155320adc9fcc1adc9b4a6b"),
    'r88_surfaces_sprite_phys': (9, "036361e796bd1de532b407b0d47fd85b", 1, "413b81b3a2a1bf015bc89f3b16d83f4a"),
    'r88_surfaces_vis_not': (4, "653f39983811980aaa3c37b8c26420b1", 1, "549884af60676b3b4abb660b13c46832"),
    'r90_lattice_comread': (17, "ad7b8db3d8057fbc9f255a0a7400e3b6", 1, "19fc1869f3cf3d64852decb99a72d640"),
    'r90_lattice_comrefuse': (15, "148d98444c21a5d7059cd1d42c49885a", 1, "2ee29f308d8c06a9e5f92b42dcf0092e"),
    'r90_lattice_contacts': (13, "348dd6fee7345d574ba0278323a57d3f", 1, "51dde04aac1b94da38c8270c7f1e1177"),
    'r90_lattice_damp': (13, "532ac348beeae159bffedb81d31ccaa5", 1, "20195d61cf6491d9646330fcfd272cdf"),
    'r90_lattice_freezelock': (12, "38ddadb190056cea6d61a9ff1deb6e03", 1, "a0abb34161de08c8c293ffc1a49ef99a"),
    'r90_lattice_gravity': (12, "f5edf3c4a8b631b449693fb4c373f506", 1, "50a75a37ef6a395dc9cc6abd2e839890"),
    'r90_lattice_impedge': (27, "1bbea62f39120b1ac56f9c1e14a29b2d", 1, "bb14a5864c840e18761c645c2022dda8"),
    'r90_lattice_impulse': (11, "7ffcb25418f38a56a2459790945cb504", 1, "10b31b06c867e0f4e2c7b0b68f34575a"),
    'r90_lattice_lag': (18, "3c0c7178c91e48f4d6dcbce8720c263a", 1, "f94c071553ccf21376a5dd64e098ae7b"),
    'r90_lattice_order': (21, "b446cac797c61dda028f02edcfa9f072", 1, "c70635c0895f51b6b808815eecc9a2c5"),
    'r90_lattice_props': (43, "b2d7e9964cd64ece9b62828453323286", 1, "1782c1716fba0e986ea80ea91b10ecad"),
    'r90_lattice_write': (13, "f4b64712940e5f570772fb1babe263e7", 1, "ec2ba7f1f4c9f49b3b3d8a4b4ecff834"),
    'r92_tilemap_atlas': (40, "93af17a47c7a99fb48acb7751d53bb8f", 1, "ba28a0a28cf15d3593b6b56173c33068"),
    'r92_tilemap_cells': (68, "02cb85a6a7a0cf328c7339629ec7001f", 1, "0a9cccc9c1dc97f9bf10bb3a822edef1"),
    'r92_tilemap_census': (14, "7c0c36ef3be0b3b26888fa240e026b7e", 1, "997293611faed4e5f0bd225c379c5677"),
    'r92_tilemap_custom': (50, "730c318a4e3eb7c473c114b345a58381", 1, "f093d7fc1888bf546d79d83a3ed9957f"),
    'r92_tilemap_encoding': (42, "f74395ce52170c6006b8e751501542df", 1, "d94fa36870319b7b65d3118a4a262659"),
    'r92_tilemap_fixinvalid': (30, "9403bc01bfa47ad17ad1850e3fa444f1", 1, "c85b4e696d8ced22b243904b311e8ad7"),
    'r92_tilemap_nav': (28, "bc2c29a25d2636f41da7bdc33bcabc98", 1, "f08f583487437d71afa554bfbebffbd7"),
    'r92_tilemap_nullts_crash': (41, "c8a486736e12fdd775a21c1e49cd05a1", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'r92_tilemap_pattern': (35, "0c25c2f1a613e7fdf9ec98aa39138e16", 1, "5348ec155f440ccd78309293b19c71e2"),
    'r92_tilemap_physics': (34, "d7749c12dddc72b471d26b5513edd2c2", 1, "df7c160482a96ea94fe23d59f226cd4e"),
    'r92_tilemap_quadrant': (15, "e3f10cfd4fa54f46c24303b7a3fb8d48", 1, "2c75980c61362b4ec1e7d62a5fdf1689"),
    'r92_tilemap_srcids': (37, "4975417fb0a9b0324dbbccc8ec711792", 1, "25c3624fc778201d55d9b43c67c5e375"),
    'r92_tilemap_terrain': (36, "f4b2aa40ee877dfd67d3b75016c0cdaa", 1, "d1d3cd73e47c611f7de6f34f807f26ba"),
    'r92_tilemap_timing': (22, "b63f25e062c01cfcd355437822a355b3", 1, "ba54b004cb772bc1556193fe7a37213f"),
    'r93_anim_await_offbyone': (3, "36887d5eaec261a4db6cb91a450b973a", 1, "623a13b4f8c01d7e02cce1ef2988e16f"),
    'r93_anim_blend_finished': (3, "7d04baf5032438679854827aea8f3d91", 1, "4b1895cf9f1f915f79188a3ae6adacf3"),
    'r93_anim_blend_interleaved': (3, "3e61ed39535ac134b77bbb553979b30a", 1, "a8d99cc7077a1f7bae5d27acb7f01622"),
    'r93_anim_blend_running': (3, "7d04baf5032438679854827aea8f3d91", 1, "4b1895cf9f1f915f79188a3ae6adacf3"),
    'r93_anim_deferred_flush': (3, "d13766dd55f68347f2c3d82b225a645a", 1, "e36a19fb4bc104db7f8f75dce97aa7b2"),
    'r93_anim_manual_clock_control': (3, "5c632704aba35dcb0bb092ec9f1c09ab", 1, "e6554db1a5efe34eeee25f8abf6646d4"),
    'r93_anim_manual_clock_interleaved': (3, "5c632704aba35dcb0bb092ec9f1c09ab", 1, "e6554db1a5efe34eeee25f8abf6646d4"),
    'r93_anim_method_callback': (3, "4957d7058c463a1ed4ab6b40f3900804", 1, "06310c8f3507bfdf9122e3c99c6f0b33"),
    'r93_anim_overshoot': (3, "1714912f980e3737d3bfb1c865f66dad", 1, "208d9af6b645a74a4243f49855bc3fab"),
    'r93_anim_phys_delta': (3, "e42d97b136c12edbd5b7d8c8b3269080", 1, "151097d71431bbe87163580049da2f69"),
    'r93_anim_physics_tick': (3, "a3e3e7758fe788c94b01b2e3ff76f5b5", 1, "9f59c47d4d6ea7a5e4d2f837449292a9"),
    'r93_anim_process_manual': (3, "acfa2a26e31395734aaa43369900b84b", 1, "18fa19ac4fa6f6c2c296898fc27ef470"),
    'r93_anim_process_stable': (3, "ae24c49c30269902d7272648bacc0b82", 1, "c60169f5f64ec58a135f9dbcba232277"),
    'r93_anim_seek': (3, "de66604bec41e8950c53075e605e5254", 1, "6e81ec5e26406a8d294025d1a121be34"),
    'r93_anim_track_interp': (3, "40412485878709505364fa6043c9ff6a", 1, "a40d4eb6ac7e74c1b0482d5a5b856ab0"),
    'r93_tween_census': (3, "d01d28c25ec6f4c80cb02fa905fc1606", 1, "7a36e0c093cabdf8c1f6278165253774"),
    'r93_tween_chain': (3, "73743dff67120d5037c4667d9b02e129", 1, "181d1b7bf09b3f7af022c3502f2ab9d5"),
    'r93_tween_interp_grid_a': (3, "bd534a18e055e89f737fab301538ac62", 1, "eb78792ff839c4426472752810ae4c4d"),
    'r93_tween_interp_grid_b': (3, "bd534a18e055e89f737fab301538ac62", 1, "eb78792ff839c4426472752810ae4c4d"),
    'r93_tween_interp_value': (3, "4012cf973e11327237ad086f06538a0e", 1, "5afe0c3e87b82715122a8ab67f32d080"),
    'r93_tween_manual_step': (3, "92567626795ee6f5f7567813e47a4b98", 1, "f347c5e4ecc84a39432fa9c5950af160"),
    'r93_tween_phys_manual_step': (3, "43f10ba6ed939767c4fadb73a3726b91", 1, "1368dd2022d1228103f0e899e1afe2a9"),
    'r93_tween_process_stable': (3, "37084fefe1f9caa639eac6668f39b243", 1, "7fec4e7278eccd740a74065b995c094d"),
    'r94_particles_census': (3, "de23f0eb16da7c1a20003447560cf6c9", 1, "6c16a127232a827f8ab42351724b763e"),
    'r94_particles_convert': (3, "e37f1215ba7b7f3f387967a6ca22d87e", 1, "2e2d8b169b164e21ec579d29294caa7a"),
    'r94_particles_cpu_amount_mid': (3, "7d5cb4bd8be473e261894b93a18e0a4b", 1, "4b7c31d280049dc95047733eecf59c95"),
    'r94_particles_cpu_contam': (3, "d176e5a8cdb7f8e9e94c51dc0d3bd0c6", 1, "97185668a845cfdf814bc0f7bfe90dae"),
    'r94_particles_cpu_expl': (3, "23b48cda5b5f1f06311526c3e6c41426", 1, "9641e55baff36056c751e4059430d576"),
    'r94_particles_cpu_lifetime': (3, "1cea6bb44278425b882953f6b08f8d63", 1, "7ed127f9cde82a03facbf52660504b62"),
    'r94_particles_cpu_lt_mid': (3, "be93301dcef73ba77eefbc907d557714", 1, "04183a0131de0bc073d6d76bf9e7f005"),
    'r94_particles_cpu_never': (3, "416055a4398099b6588f838593399c1c", 1, "b67ef6a4c5a4f71125c684c7b567e20e"),
    'r94_particles_cpu_oneshot_flag': (3, "d470e19bfa8845013cf181553d06b780", 1, "70b4e92efb4098a96ebb46aa90941cb6"),
    'r94_particles_cpu_oneshot_off': (3, "6477f407f2312e28a5addd838aa84711", 1, "5f2dae23a5c922f5263c191836563e55"),
    'r94_particles_cpu_pause': (3, "eb74269f341d54186e58991b2b9e4967", 1, "264434407590dd64342609a4f2a25873"),
    'r94_particles_cpu_request': (3, "4ded42346e5e5a461fa15cf4f366a0fa", 1, "3a1d6aa83c3311321d37d510c55aaa77"),
    'r94_particles_cpu_restart': (3, "e421db4e190830370ea6932159448655", 1, "c37d5b14c8b81c51ebf8cb75da357da8"),
    'r94_particles_cpu_retrigger': (3, "b2e5a45e81fd3112064cb5a8befe025b", 1, "64b14083763a199c0378fe1259f888a1"),
    'r94_particles_cpu_speed_mid': (3, "d0fd02f12c00af0f083ae1e1dcc4585b", 1, "4e2bfaeb95f9bec39334bbbcfc0b5f30"),
    'r94_particles_cpu_speed_pre': (3, "3eb97c2f73af8ac9e2380074055fad41", 1, "97fab7d1d274820e99339997759f8404"),
    'r94_particles_cpu_stop': (3, "08b549a3f61d0768a7e584d43b5cc9f8", 1, "298e6b96ec05aaa4950e135bf36c73c6"),
    'r94_particles_gpu_headless': (3, "20b2eaecf54562e52b3fee6194713b95", 1, "548aa0dd6cc005701c0dc51ce7b97029"),
    'r94_particles_ppm': (3, "ff4dfad163004cf9c0c945731dd3ed04", 1, "4f4d823479e36268eec7e696349f6a88"),
    'r95b_order_canon': (20, "9c54a48ecb518ac9eb9e619073881206", 1, "c47c35a967093a59f3e6755bd6c4f114"),
    'r95b_order_cap40_p0': (16, "ba64486564709babdcd89fb2584fec86", 1, "30560a3794b1385a1c538e8d5ac865b7"),
    'r95b_order_cap40_p1': (16, "43ed8faaf061cc8ab4b55b26444d210f", 1, "4701cfd722c44949a1e6b663672a5112"),
    'r95b_order_cap40_p2': (16, "f652aa2c0df8d8d11e1f8b7a7b18ce40", 1, "2d3956e7e9ffec5c6c531b3de607fdf7"),
    'r95b_order_celloff_x0': (12, "1dbf6bfaa5f84cd2164e87b4690465ce", 1, "1eab873963cf1161f91e8ee10db68b36"),
    'r95b_order_celloff_x1000': (12, "9f5a2c998bfc1c4d2c60e97c6c17f826", 1, "afa038f6cea2c147009bc9f43263c94f"),
    'r95b_order_free_ab': (13, "d43a6065dceef0bebd9ebb24676326db", 1, "2dfd9b497cb543a8121c098d957b2ab3"),
    'r95b_order_free_ba': (13, "b7980ef67709cbb26479b1daf3094624", 1, "b030dae6d7733d22ffea732f98b82376"),
    'r95b_order_layers_k0': (18, "9b1094937cc04f6316c1f1cd75bd9b18", 1, "98bc88cd5001eb60f5233d272afffb91"),
    'r95b_order_layers_k1': (18, "042905f1c00fe6a105cbf2be7e4e7680", 1, "4b3548aa4708648cd17cea0407714a62"),
    'r95b_order_period_k5': (10, "5ed89eb03e6f2f9deefac02715c2c7bc", 1, "892a0373ae0b6e5501993074337a439e"),
    'r95b_order_periodx_k10': (13, "863ae1f64925055e9ded77e28d217d92", 1, "9cfabc176ad32e5d86955c1b65f06c98"),
    'r95b_order_periodx_k2': (13, "7c6798671dfd451c9174c661c7052155", 1, "4bfb8ca74c91a910855ecf6ce5aa2b16"),
    'r95b_order_periodx_k3': (13, "2f660a1b56ac34941603459f6086df10", 1, "b59f54be193739e598cc44cfd4b65488"),
    'r95b_order_periodx_k4': (13, "aed7f3d2b1ac48c7e84ca72c81e8cf0f", 1, "aee34c549bc5d9fdedf1a27fe07624cd"),
    'r95b_order_periodx_k5': (13, "9be2de576bbe5ad4decfed781c83ccaf", 1, "2ab2313a57c24e705783bfa07d8e5479"),
    'r95b_order_periodx_k5s8': (13, "c5f6332629046e0ae391b65842d3b9dd", 1, "1d5949d28c5f0990e54568d46a96c0eb"),
    'r95b_order_periodx_k6': (13, "b55b3cc06a69b456475c747b9c810545", 1, "df520553dfb7e3ca920153f2a194de78"),
    'r95b_order_periodx_k7': (13, "c05343c4b6916a7e03f40a7df9944080", 1, "17a83cf7b92fe663ba319c3c80508931"),
    'r95b_order_periodx_k8': (13, "3ae24301da09182f80aad6d2e344b655", 1, "8d2dbcea838448c535d9bdadbd1371cb"),
    'r95b_order_perm0': (13, "acb15e9f741e8adf83e32813536722cb", 1, "0c82ae94d346cf0eda9f18c791665f1c"),
    'r95b_order_perm1': (13, "d3d54e0c60a4abc1cb0199b4fe8757c0", 1, "e0cfead9fc8e26eb3a3efb0585a840a5"),
    'r95b_order_perm2': (13, "3c81860942e14a05a5a59397c6550006", 1, "e7fc882a6a20a373ed1b937936d647d3"),
    'r95b_order_perm3': (13, "5c53afc945201652ffd2c4e11220ac8c", 1, "a302dbe4363bfecb14ebd9b2e1c6d52e"),
    'r95b_order_perm4': (13, "1e211a203a90bea2afb24f3a63138a27", 1, "225e708710df23a306c39173f6c222c6"),
    'r95b_order_perm5': (13, "0e6716b1cecbf754b8b664454ce31d69", 1, "666ba28f67e7c2e468f71656ba2d4384"),
    'r95b_order_perm6': (13, "714b1a31539cee76d64c7d74e5bec6f7", 1, "196e813e1afb6b25243b865fbb758cf2"),
    'r95b_order_perm7': (13, "33bf6eb695d5f056cf14869efbbb2fa4", 1, "e77f710fe3adfaa8bca99c9710efec3e"),
    'r95b_order_readd_a': (13, "2487e21f47b1ff03fa0ecbc4beac5d21", 1, "4f6144c2da84c2e26d1eb247c7166dfd"),
    'r95b_order_rigid': (13, "ee4cb54bc1b0569bbbf216232fbef125", 1, "749e730f72148f9e93f817199ad10a74"),
    'r95b_order_scoutrev': (13, "1d5abe4ba9fa8bdf2fbd1472ac98720a", 1, "c66abda50e339eea5c18d82cd6fa296a"),
    'r95b_order_twopiles': (12, "cfa87a79f6a90ece060c2ee300a7f2f3", 1, "ce5f3956fa40b77516dbec1ebb4448f0"),
    'r95b_order_warm_k32': (13, "abd0ce033e66478c88a8bca55435d133", 1, "1ebf804d977b7a575b46c961e028c427"),
    'r95b_order_warm_keep8': (13, "96de6914d823a159c62388a9902dce53", 1, "91a800cee917c10b6866daa654345b4c"),
    'r96_scene_io_cache': (3, "e2af25d109759039429d983aaa1afbfc", 1, "5ce38edaecb6c221840938eb628dac85"),
    'r96_scene_io_census': (4, "a7b0311508b18f3d5fba3b8ad9300624", 1, "d8db538fe0cd17d2e87d0cf29057223c"),
    'r96_scene_io_det': (5, "dd2af9d1288314988deeeafd15be70ec", 1, "63f3ca9bbf9af3eba1a29b8f4116118c"),
    'r96_scene_io_edges': (4, "d4ed2a23b1863d70b5c2c47e4a4ab6cf", 1, "6addee0355ea32ef6d5a79313a09bb82"),
    'r96_scene_io_editstate': (3, "2d1132b467094ec6281ffd709c5486d4", 1, "bb7d83e01750f338666d849b2b1afc41"),
    'r96_scene_io_extres': (6, "38e108fbab72ec7800578be564d7aa17", 1, "2622cba10841811fbd5ac1feaa8988b9"),
    'r96_scene_io_formats': (4, "f183ef70bf9ebd2753374d3b93b5d318", 1, "f999cb30b3d6af32b661a6dde0e39df8"),
    'r96_scene_io_ownership': (14, "ae79418e26020dbeb21297993223d3ea", 1, "bf31a167eb8801a438355566c4a32efe"),
    'r96_scene_io_pack_basic': (4, "b6a073b688a7ce5ef22a2399f98a0b22", 1, "a2508975ed6b742c4766490d9fbe5996"),
    'r96_scene_io_refuse': (68, "6b06c509277c8defd6493ad6b56211bd", 1, "133fa4a8154a7f19143c88388a14a9d0"),
    'r96_scene_io_subres': (5, "640201757c85f3947601e914e5cb204d", 1, "e559771e3eda68e9d16496c4ef4bb290"),
    'r96_scene_io_takeover': (3, "c7b549ca41bf07c7f26ee97b1a0095f4", 1, "8930f0d3c6e3df246ea7b38f38c7d044"),
    'r96_scene_io_uid': (9, "bd96bcb7b561760a679e07930201de79", 1, "ae43b98119a34a1e4f7ed9feb8a0179d"),
    'r96b_cache_deep_ign_deep': (4, "0f0580f57c0f9bf93826f2371819b985", 1, "8ca745ec042decfcdc376118a412fe7e"),
    'r96b_cache_deep_ignore': (4, "04d4e0ebf8faa1443a262679a885edcf", 1, "7f1ab334e00186ab3e2836ffd6301f2e"),
    'r96b_cache_deep_repl_deep': (4, "b6b1b6446daa76f8fecb012e1d41dd33", 1, "70b0b017424430ec801c2c0ea5d3d061"),
    'r96b_cache_deep_replace': (4, "6fc0b76e7a0057a0585ab99f30b2eed9", 1, "42f439564c8d2e8bfaad304d905f668a"),
    'r96b_cache_deep_reuse': (4, "a9e1f79b47c82b98fe231c652777e245", 1, "5bd19fce34a72e6b5afdc5e323bdcd5d"),
    'r96b_cache_ignoredeep': (3, "dc3b2db56fddcda285358545a733682f", 1, "e554c3ee0a6b4cb889c5491a81ab8ea8"),
    'r96b_cache_repl_uncached': (3, "5b0b2174e0ab2b97af0f7d04d44f46e4", 1, "26f918bea593ba152a05adb58567f8f8"),
    'r96b_cache_reuse_delay': (3, "9ff08b29c34e9f421aec43ff0c4f5a3d", 1, "5e8fda55a89db01bf694dd013fa12c65"),
    'r96b_cache_reuse_delete': (3, "033416318ec364825b6b53d48dcdface", 1, "0600b75fb9479359a72bd3e16d4ceaad"),
    'r96b_cache_threaded': (3, "a72d5a96dc0739a8096fddd4a861ab87", 1, "0f80c86206ef10259fe11237038e3381"),
    'r96b_id_extother': (4, "4f4a48d61e2d2ab2020ac253ddf40e79", 1, "cc453cd081c3824705bdd5a65f094f3f"),
    'r96b_id_extshift': (4, "4c846faa51c67adb2cbee6d77c7275d6", 1, "6c80e97fd039cf10841987f4ae425081"),
    'r96b_id_fingerB': (4, "0e27b69259cfa96bb44d8a0b4ccde5a8", 1, "144d2f2baae66fa83b0b9ebb3e373a4f"),
    'r96b_id_mint_two': (4, "4bbc0cf92e699d95e6df30ec2521d82a", 1, "b14fa7eb3e08c349c6acef188db121e5"),
    'r96b_id_seq2obj': (4, "c883f369f176160f18e444a06962872b", 1, "73e6d0f5ab3575dba9c7e4ba0350651d"),
    'r96b_id_seqA2': (4, "27ddac4e265a3b82c3ab8babbee7688e", 1, "be4a0b79c24fc80dfd8db20e9d146a5b"),
    'r96b_id_seqAB2': (4, "ce1a77cad5b7ccd32ce8eabef6bb6a0c", 1, "5cd8ae891b8f38ea449f9b6515b7e227"),
    'r96b_id_subcontent': (4, "2fc29746d0a765cc7c2260c6cd55ddf3", 1, "a11bc768868eec619440f70883c3ffb4"),
    'r96b_id_subextra0': (4, "c3aedf07cdfb96e700d4e6ef84f49e6b", 1, "c8cdac072f9a380247fbf49bf9cde86c"),
    'r96b_id_subextra3': (4, "78b1dfa2e21ee3d0fa27d89f61ce94ce", 1, "6878aaafd74933e4be07d0735bdde945"),
    'r96b_id_subpath': (4, "d6d0c545edd174c82cf98037e9182083", 1, "fc7b30c5eb2bcf1e765cc26e6305fc84"),
    'r96b_id_subsame': (4, "20b5eb00bd28713b497bad11b954c15d", 1, "cbd7707706e16b5328cecb03f63fa49c"),
    'r96b_id_subsamepath': (4, "7a887ad82b5c02438f18c2eec21e9137", 1, "c2fa3d46880bd2b81865d843a61a2f46"),
    'r96b_id_twoext': (5, "2d2fc12b848029fc4f7557bc918b1dd4", 1, "53365ebf765c472c46bc6e060cf32150"),
    'r96b_phase_ph0': (4, "d6b2b027d8e0a74118d48103237f67c1", 1, "91ecabe2de59b49191f342f4496f2206"),
    'r96b_phase_ph1': (4, "eba84dd66cf5222ce694794d2a945736", 1, "d2a891c97cb76726a5ff4626b4eac4d3"),
    'r96b_phase_ph2': (4, "31141ac885d8c90318fc534c349309e1", 1, "d96ab3ea1610fa1f732301ff49d9aafa"),
    'r96b_phase_ph30': (4, "5945622572b70d1920ac81c4fe93fade", 1, "1cca4b8eb0e31bf66d14073d311b3963"),
    'r96b_phase_ph5': (4, "b0a83e3e44e51a2d38c5ecfac5d5a6cf", 1, "5fac8737545f896f2fecb326342c1dc2"),
    'r96b_phase_pph0': (4, "839ffaa7db2e70119cba3c55183581c2", 1, "05033ca7385d59b1bf32aeb6314a1132"),
    'r96b_phase_pph1': (4, "8a500947500dd5bac521631b8edcf8cf", 1, "9ed240c935afbe3978ae434fb0958f3a"),
    'r96b_phase_pph2': (4, "292f016f6a47b75953325abcab15d19c", 1, "e1494cff77c7716e0be87c6464df8e39"),
    'r96b_phase_pph30': (4, "60dd8b784153d1fb9aa20983fc19a687", 1, "22ba0cc790bc6f878f277a36c64f5722"),
    'r96b_phase_pph5': (4, "a627bc4f2dd7cf03f6fa9525103e7bda", 1, "2a2e012f3c5f8884d8a7944c8d13c4e1"),
    'r96b_seed_seedcheck': (4, "a311bbfe8f0c2108b5b2105853d9e87e", 1, "a380c06ae3520fac598982b0de18c50e"),
    'r96b_seq_extbundle': (5, "bfec43066e093ac55b5bed292c09bea3", 1, "1a35d1af84a5e554e176c3014fd7b464"),
    'r96b_seq_extgen': (4, "7063dd065e637978ef46b5d1ee85a5bc", 1, "3b504c7a7426588e4c0575b018bc56e3"),
    'r96b_seq_extpin': (5, "83c36884b9ff67c2b69421fa5f24b414", 1, "71ec8dffc7343a63e174f909b098fcaa"),
    'r96b_seq_extseq': (5, "67da53dfd91c4de8695b452348561e25", 1, "8225e596f591aa9e0c944f92bffa6d22"),
    'r96b_seq_minimal': (4, "8d36667e944402e0bf498a6d36dc1c44", 1, "fbd1824a4ae2a5c629d587e9bc741490"),
    'r96b_var_conn': (4, "d09abe43b90884cf3bbe168114361706", 1, "7e151845e3a9a53ca9726c1301f39847"),
    'r96b_var_groups': (4, "7d96bfaa2367f75cefa5d89b19357cd8", 1, "39336a98e251a5336d0f7e89cf16c896"),
    'r96b_var_idstat_breadth': (4, "448da4cb9ea7f9265585c3e939f40074", 1, "1301e3b9e1deb04121f48816fa60e9b3"),
    'r96b_var_idstat_u31_gate': (4, "b065a535ff2c4bef1087694c0584bfb1", 1, "42121e09b367a290fcb6cd3f86624555"),
    'r96b_var_lever': (3, "af6d58fe1dd49ad474b2ae5440620b65", 1, "6a493fb802340c3ab2a4686fda5e061e"),
    'r96b_var_meta': (4, "f61c2b5c12ca754284f473b3aa19d15e", 1, "f5265942433b7a70d0c438976a85383a"),
    'r96b_var_rich': (5, "053f3cd50149cc0bf47881a5c4a86f5a", 1, "05c37bcc63190028f60800123b90529a"),
    'r98_canvas_census': (14, "b87b72af6c43cc7e356554bdfb944422", 1, "123a07d224bd672657a8fe41cc940aaf"),
    'r98_canvas_clip': (19, "317e29adb997985a83c2e6c633d1774b", 1, "f3a250047099fb35d8506d5e475e64f9"),
    'r98_canvas_draw_refusal': (17, "ff8b609a4c52b9ef67d0ad7fe16d0b30", 1, "12bbb6b97d178049943a7ccc7424978d"),
    'r98_canvas_draw_state': (11, "4fd830bd7159afcdbfcd8d299a31ad0f", 1, "ddfd0af4f6dd976624ad20283dc18de1"),
    'r98_canvas_draw_surface': (8, "46da79b02ff964276fa756b374f23730", 1, "7bbb737f7f2ab2edd3d5a052d21e6a68"),
    'r98_canvas_modulate': (13, "37ec84882e5c59624ce3db85018fa484", 1, "e61bc1f56902bc700c4c62c65bce7eaf"),
    'r98_canvas_notify': (14, "7ec040dc7064b4762a2ac44c9f1d19b2", 1, "63e1c80b8155eb03f0acf764b0b99d5f"),
    'r98_canvas_queue': (16, "8ba0ba4a270f43e9aef3b75d25583f47", 1, "cb67ede6f6851ab63bc50e003f0be556"),
    'r98_canvas_redraw_context': (6, "5fb2002e2a139152dad8709900bd0c9a", 1, "9aa97a89b330a26f88c135d0149827b4"),
    'r98_canvas_redraw_triggers': (4, "7640c5077d4d5bbc519771565a26f4a8", 1, "13d30cb3d34d75947a382c324fd33abc"),
    'r98_canvas_vis_chain': (17, "2361a1237686251209bddc0bcdb0a31f", 1, "78ef73aa531b9cc7ffd7f5da0bcd4af0"),
    'r98_canvas_xform_global': (14, "7991fc3bbea6f0c79c292a728b8e228c", 1, "3512af3d3921c03bd81a2d61763a533f"),
    'r98_canvas_xform_mirror': (13, "d8d2487f29385ab581adea78ad6d11d7", 1, "6cbc5b416c9bb193dbc3950422368200"),
    'r98_canvas_xform_skew': (9, "a9272fb24d7dbf7fe06173e23fe002e8", 1, "ee96f6356c91251eeacc83e2b407f642"),
    'r98_canvas_zorder': (12, "55e24bd53833d3ea7fcb9b456fbdbdaf", 1, "f1efb630c14debf4536a18832dfacbdc"),
    'r98b_clipmatrix': (43, "5d2179df85881c54ed69c9d719399555", 1, "eb4224b873edc7e12c653df13fa3a8a1"),
    'r98b_epssweep': (7, "d3180803abbd4aece7480833a75760cb", 1, "c97000c1bb2b1627f949e0d7f6f21bdf"),
    'r98b_gskew': (18, "801f5f73d88ccd247ca0dd4e7129327f", 1, "b21e1ce9572d2625bd1883da5b18341a"),
    'r98b_latch_canon': (7, "88d8e359c3c3fbd6a6ca515a57d30990", 1, "02785fc0444ca8dee8b881d9bb7594d1"),
    'r98b_latch_imm': (5, "f972053edff59281c79e8371a9df0f13", 1, "7922aa78e7d33f6e2931158e72cb7b3b"),
    'r98b_latch_second': (6, "01fddab517993353d47278368f8976a5", 1, "10d64c64ff4bfb0e60a00708960f668e"),
    'r98b_latch_t1': (6, "02cd49019ff1e63eb16c5779e48e8bdb", 1, "d40eab25a38e2fd4e58e95d39c377378"),
    'r98b_latch_t3': (6, "284056a37fc9ac26753ec8e2d11f20ae", 1, "a0b65cd4d2d7fe364d0d4bf71d2d1ca8"),
    'r98b_notifyphase': (11, "de5f67987f80808eada994088dc29956", 1, "c88c1801edb52f82b78af7ebd8084eb5"),
    'r98b_qflush_same_frame': (18, "63104ec60f0dee8babd01dea470c9b75", 1, "96029daba000bdf6d64752afb95a2924"),
    'r98b_qflush_suppress': (18, "63104ec60f0dee8babd01dea470c9b75", 1, "96029daba000bdf6d64752afb95a2924"),
    'r98b_qorder_flat': (14, "9e0988a31711f5a9adaa4a9524c6302e", 1, "c701e4bea259bdc9c5bcae3f8a53f71a"),
    'r98b_qorder_tree': (14, "6cc56a3a33cc0de8729231342ee1d243", 1, "5816f21e35e52569696bd203f3b0bbe3"),
    'r98b_rksenum': (11, "14b5f98b56dd82b9f0012b2b968e35f6", 1, "fe521e07aaf91dc4438e21cf6f615462"),
    'r98b_skewgrid': (18, "e50d91d70768310403e36eae4ab11a5f", 1, "630912762708511248f9d22d2b1de81d"),
    'r98b_visphase': (18, "349baad7ad350ac547f3f0e138ff96bf", 1, "2acb5aafe2ae5c31b6535ae2d713923f"),
    'r98c_flush': (18, "5311601762cb7f7aee19a2862036e253", 1, "9a36e00725109d1396efda8171d5cd5d"),
    'r99_audio_advance': (3, "3809f39a7b4aa7639de30583020bcad7", 1, "15316a1049dc9d3e0e675a84168b74c6"),
    'r99_audio_autoplay': (3, "564d44a63ce1c689c7193db0cce7bace", 1, "f5b3360eeb74318608d18b4760110e25"),
    'r99_audio_bus': (3, "499cd73d0b3a8e2a56e3e8a5c80ad049", 1, "4e2962cf7b0ac03319ef9e7e8b55f018"),
    'r99_audio_bus_peak': (3, "15bb5575e30268636659c1acb10d212b", 1, "dc2df2013c82cf4ed1110651c966b6fa"),
    'r99_audio_census': (3, "f3279339e92a33e27d1ea07e12a3d83c", 1, "24c1c72681392db508d69dd7599c9755"),
    'r99_audio_finish': (3, "7691c2a5fd60ebea2f4a027c42f7d2bf", 1, "61e4081f1605e490502a5dd5246a0ece"),
    'r99_audio_gen': (12, "9aed86f0ca83d3c04281fe99d1b2b3d8", 1, "d003b0b8599e11c3df53bfcc564f0054"),
    'r99_audio_gen2d': (3, "0eb1a7dcf1448a5630b9417a90512029", 1, "8148021dcb590ae4ae6fb6f68573ce2a"),
    'r99_audio_gen_peak': (3, "cbf8a457c66b3f924ff29d27de160e2b", 1, "7700a28ab22598536c88a5867def55b4"),
    'r99_audio_loop_degenerate': (3, "4c142e2e5b961cbd3a68f6afd1bae755", 1, "1f0d2be2492c2ad077546f81807384fc"),
    'r99_audio_loop_pts': (3, "8954003d15803bc72d9fce87eb3bf56b", 1, "5106b5beab27b19a8186f584f3d23eb1"),
    'r99_audio_mixblock': (3, "5de2b5d6529678c7491ea88f6b60f60e", 1, "256424895b429a90de94fbacb5f9700d"),
    'r99_audio_p2d': (3, "793de5c69132132162fc5e25348b21de", 1, "b7f5974f08729a7f708cddaf43b26215"),
    'r99_audio_pan_law': (3, "de3f794c08ea01d26363714a51d12620", 1, "370ece38feecad8acc19a429160c4e71"),
    'r99_audio_pause': (3, "f94d424165965428bc34d216a0ee9bb7", 1, "e7ec1e1281bb2d0c294b4afff9002605"),
    'r99_audio_peak_calib': (3, "bf71cc54c1e46c166036e383c7623587", 1, "ae06d07a43e4c42fca7cfbba54151a8b"),
    'r99_audio_poly': (3, "bbc4b6e5ae1c11f1cd3899a61a7fb28a", 1, "e89645927304c520b75ea434a9cff425"),
    'r99_audio_stoppos': (3, "09b7b70a2280a64ce956197fb6599a83", 1, "02e808ec279a1b17443cd14e6dec536c"),
    'r99b_finfree_played': (3, "f03a3dd29d03c3629e631231ef5989ed", 1, "ccb65616f337e5f173a0f9f2c571b6ab"),
    'r99b_mixfree': (3, "08896281956c99fdbfd61c4ee3340fb2", 1, "e894f7a5d663621fb32df3f426432b89"),
    'r99b_startphase': (3, "59780d4be7c129651935ebfa4536c0a5", 1, "fa06cfaf83d0d25279bb14bd44611cef"),
    'release': (3, "488eadf69d3113b03a4b1de2fc835c91", 1, "c43f713ed99a7d52f23ff479e89b70b5"),
    'route_toggle': (3, "f93a5fc35e9f542a555c6498940008e1", 1, "6d0b45c0e63f646206412839b7b40d04"),
    'save_corrupt_negative': (6, "f052d3982c63abc3b24d1ff8db05ec07", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'save_process_missing': (7, "eb735b2733ad51eba40243df0c6efbaa", 1, "d980381f7932ad2ea4f4251f6dc499c9"),
    'save_process_reader': (3, "4d295e34b591570b5f34e8e74f1e7df0", 1, "91f78021c0aa3222b0ea83d1714515ec"),
    'save_process_writer': (3, "53ada4e12aa7ab20f7e87ac21fec33b9", 1, "6fd97719456afb4389c8a045f7dec20f"),
    'save_roundtrip': (3, "1842ebda1e3ddfa201f1d2831050baaa", 1, "71b743decd0618d2dcdea706444b6381"),
    'scene_signal': (3, "9b601d85c5403f88bab03e3b64e1ba55", 1, "068294100559db5c65163dc6960d5b6e"),
    'slider_adjust': (3, "f1767e48e1cc883013214af5ded6c35a", 1, "cc5282bccbf1c822f82d836e66853e3d"),
    'slider_adjust_disconnected': (7, "be440a7821527a82b92d150cbd5c2eee", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'slider_adjust_no_focus': (7, "96d4bf4e6c330a1bc26bb485bc8c1175", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'slider_adjust_repeat_right': (3, "4477f2c0d4ac555ee6336196adcc1739", 1, "e2cbd7c8e82c6fd5ffd91e21a128e2fe"),
    'slider_adjust_repeat_right_disconnected': (7, "890d968d67868ff8051bfe8ae9547b4e", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'slider_adjust_repeat_right_focus_handoff': (7, "dfcced783498ff17082e278508ebe203", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'slider_adjust_repeat_right_focus_restore': (3, "da37f3fe86bfc0f206b0e6197a971036", 1, "f90ced3bc4035f11e550d56e556aa6b3"),
    'slider_adjust_repeat_right_no_focus': (7, "2e8da21efcbb24b82cb1ba9b794c88bd", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'slider_adjust_repeat_right_second_focus_loss': (7, "b9ae9669f28eb95363983a7c57b64f4f", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'slider_adjust_repeat_right_second_focus_restore': (3, "658690ec63705291f315bcb3e856d100", 1, "6c2162a54fab2bf1dc6cb65a553b03ab"),
    'slider_adjust_repeat_right_second_focus_restore_clear_frame_then_push_release': (7, "1ae2c61099a0b4859a2f8ed3833e3469", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'slider_adjust_repeat_right_second_focus_restore_clear_then_push_release': (7, "f942b4ac8bfee9890154598c6f73e98a", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'slider_adjust_repeat_right_second_focus_restore_composite_push_and_clear': (7, "1fa2124f7423c71858f750a14575731d", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'slider_adjust_repeat_right_second_focus_restore_disconnect_after_first': (7, "7ae4bcb2bbdd429dcbbe4a4964f0b1f3", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'slider_adjust_repeat_right_second_focus_restore_disconnected': (7, "3de7438b13b143da21710f741835ce0c", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'slider_adjust_repeat_right_second_focus_restore_observe_parsed_release': (7, "dd69d402c57f8a7c91db077f991221c2", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'slider_adjust_repeat_right_second_focus_restore_observe_push_input_release': (7, "273feed01aeaa893716d88bbec5b1b3c", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'slider_adjust_repeat_right_second_focus_restore_press_after_late_reconnect': (3, "8969467983a394ec53552fcd4ea89a9b", 1, "6e17612bd78ee7a7b4b9263320f99f7f"),
    'slider_adjust_repeat_right_second_focus_restore_push_frame_then_clear_release': (7, "38fb870b6e9fe8b5ec266b5d549e1db8", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'slider_adjust_repeat_right_second_focus_restore_reconnect_after_final_left': (7, "f0429cc2ba0d3c1fac35f59e433be03c", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'slider_adjust_repeat_right_second_focus_restore_reconnect_after_first_left': (3, "66b99e96b6f4b15a704ee803202f50bf", 1, "38eebaab430c3d6aff65bf5d7b82256b"),
    'slider_adjust_repeat_right_second_focus_restore_release_after_late_reconnect_press': (7, "93d1553a347942b3b54ab76e62bfdc8e", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'stree_lattice_census': (14, "b19f0a44961b28b9b21c6a0e38b9324e", 1, "88b021f366c396a8b8d1134743914782"),
    'stree_lattice_defer_ladder': (11, "ddb2e8c42aad0a16d00713789b0bf387", 1, "4285d99d9904794842206475c72ba8f1"),
    'stree_lattice_defer_order': (10, "24e1d329439bc4ea82901ac91bc5ed71", 1, "a2c87f59ec16b7388d3b1bb075a1e9d8"),
    'stree_lattice_defer_slots': (15, "9da1122f5c6b802d99b137f0f5042a64", 1, "0bee41d30ddfde5f09e3a444b6426d35"),
    'stree_lattice_group_flags': (29, "e50b4525d960ebcf6db3dcbdb831bfb9", 1, "09008128f6aac24785daefc8d3d63206"),
    'stree_lattice_group_lifecycle': (15, "96b0096f6f86d0516ced08aabe08221c", 1, "3b0978b84c5fe45d8b6f9d42472e6a56"),
    'stree_lattice_group_order': (25, "69fbf1ad18a191104f5b67e4a6e2ef58", 1, "3d4442bfa701501a40ff794f1513bb86"),
    'stree_lattice_group_order_rev': (25, "27f0f6e9d261765d593d59cccdb020fd", 1, "a8a2097f9833293fb3cae39940e7a566"),
    'stree_lattice_group_setters': (11, "9e25e253e42b7fe645480923b2e0be80", 1, "d9c28b55a67b6e98ab4d5e2f5cbe347a"),
    'stree_lattice_scene_probe': (19, "7b7da3e4051f2b3a2c0d3d6ba8aa1704", 1, "8d6d76a27a83158a88aabfe1aab67f44"),
    'stree_lattice_signal_flags': (25, "f11a516530f75790b0c0c1b56f0da417", 1, "0571fec740a8cf80e830da62ba214405"),
    'stree_lattice_signal_order': (18, "6b15cab554ec5f1a3637032b5af0bba1", 1, "efbc4ee73cb41e6b3e9d49c5f459c256"),
    'transition': (3, "052098d2c9d1e60f90dc36b45556152e", 1, "ae50ba790a1d4d58679c78ed89579ca9"),
    'tween_flash': (3, "1d0cf8ae119bbb25bf48e8c7d2055701", 1, "a63cb7cbf6a4051e41245f852a99e0e1"),
    'tween_no_start': (6, "2841a83baf1efb9a8c5cb6ff9cb03523", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'ui_signal_disconnected': (6, "60ff5d0f317b2ea21e9077f31835056e", 0, "e3b0c44298fc1c149afbf4c8996fb924"),
    'ui_signal_hud': (3, "1208f08b2d97eff487c55e797d4c155e", 1, "23e10a7c6cd81547ab34ab01e2d1efb3"),
    'wrong_key': (3, "54a5ad60fd5de5bdbb451f0de3da1d7b", 1, "f28e53271088e36b1a7762fe020854f1"),
}

BANNER_PREFIX = "Godot Engine"
_WS_TAIL = (" ", "\t", "\u00a0", "\u200b", "\r")


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:32]


def _multiset_digest(lines) -> str:
    return _sha("\n".join(sorted(lines)))


def _flag(reasons, reason):
    reasons.append(reason)


def check_record(row):
    """Return {"case", "flagged", "reasons", "accounted", "notes"} per record."""
    reasons = []
    notes = []
    if not isinstance(row, dict):
        return {"case": None, "flagged": True, "accounted": False,
                "reasons": ["S1 malformed record: not a mapping (type=%s)"
                            % type(row).__name__]}
    case = row.get("case")
    if not isinstance(case, str) or not case:
        _flag(reasons, "S1 malformed record: missing/non-str 'case'")
        case = None
    verdict = row.get("verdict")
    if not isinstance(verdict, str) or not verdict:
        _flag(reasons, "S1 malformed record: missing/non-str 'verdict'")
    if "output" not in row:
        if case not in NO_OUTPUT_CASES:
            _flag(reasons, "S1 fail-closed: 'output' field absent and case not in "
                           "NO_OUTPUT_CASES")
        return {"case": case, "flagged": bool(reasons), "accounted": False,
                "reasons": reasons}
    out = row.get("output")
    if not isinstance(out, list):
        _flag(reasons, "S1 malformed record: 'output' is %s, expected list"
              % type(out).__name__)
        return {"case": case, "flagged": True, "accounted": False, "reasons": reasons}
    bad = [i for i, l in enumerate(out) if not isinstance(l, str)]
    if bad:
        _flag(reasons, "S1 malformed record: %d non-str output line(s) at %s"
              % (len(bad), bad[:5]))
        out = [l for l in out if isinstance(l, str)]
    if verdict == "PASS":
        sig = row.get("signature")
        if not isinstance(sig, str) or not sig:
            if case in SIGNATURELESS_OK:
                notes = ["S1 note: verdict PASS with empty 'signature' "
                         "(enumerated SIGNATURELESS_OK row)"]
            else:
                _flag(reasons, "S1 fail-closed: verdict PASS with missing/empty "
                               "'signature' and case not in SIGNATURELESS_OK")
    if out:
        banners = [i for i, l in enumerate(out) if l.startswith(BANNER_PREFIX)]
        if len(banners) != 1:
            _flag(reasons, "S2 banner discipline: %d engine-banner line(s) "
                  "(expected exactly 1)" % len(banners))
        elif banners[0] != 0:
            _flag(reasons, "S2 banner discipline: banner at index %d (expected 0)"
                  % banners[0])
    ws = [i for i, l in enumerate(out) if l.endswith(_WS_TAIL)]
    if ws:
        _flag(reasons, "S3 whitespace hygiene: %d line(s) with trailing "
              "whitespace at %s" % (len(ws), ws[:5]))
    accounted = case in ACCOUNT
    if accounted:
        n, h, np_, hp = ACCOUNT[case]
        pl = [l for l in out if l.startswith("PASS ")]
        if len(out) != n:
            _flag(reasons, "S4 account: output has %d line(s), account has %d "
                  "(extra/missing whole line)" % (len(out), n))
        if _multiset_digest(out) != h:
            _flag(reasons, "S4 account: sorted-line digest mismatch (unaccounted "
                  "line content)")
        if len(pl) != np_:
            _flag(reasons, "S4 account: %d PASS line(s), account has %d "
                  "(PASS-line flood/drop)" % (len(pl), np_))
        if _multiset_digest(pl) != hp:
            _flag(reasons, "S4 account: sorted-PASS-line digest mismatch")
    return {"case": case, "flagged": bool(reasons), "accounted": accounted,
            "reasons": reasons, "notes": notes}


def receipt_shape_gate(rows):
    """Per-record META gate. `rows` = iterable of stored battery records.
    Each result carries {"case", "flagged", "reasons", "accounted", "notes"}; the
    early fail-closed returns omit "notes", which this wrapper normalizes."""
    out = []
    for r in rows:
        rec = check_record(r)
        rec.setdefault("notes", [])
        out.append(rec)
    return out


def _repo_run_path():
    here = Path(__file__).resolve()
    for up in (here.parents[2] if len(here.parents) > 2 else here.parent,
               Path.cwd()):
        cand = up / RUN_PATH
        if cand.is_file():
            return cand
    return None


def _synthetic_corruptions(rows):
    """6 corrupt variants of real green rows (G4 matrix: expect 6/6 flagged)."""
    by = {r.get("case"): r for r in rows if isinstance(r, dict)}

    def clone(case):
        return json.loads(json.dumps(by[case]))

    out = []
    c = clone("input_route")
    c["output"] = c["output"] + ["PASS forged=true"]
    out.append(("x1 extra PASS line (input_route)", c))
    c = clone("input_route")
    c["output"] = c["output"][:-1]
    out.append(("x2 dropped PASS line (input_route)", c))
    c = clone("r100b_seq_clean")
    c["output"] = [c["output"][0]] + c["output"]
    out.append(("x3 duplicated banner (r100b_seq_clean)", c))
    c = clone("export_prod_base_pck")
    c["output"] = c["output"] + ["EXPORT_PROD_DIAG base forged=1"]
    out.append(("x4 forged same-family DIAG (export_prod_base_pck)", c))
    c = clone("input_route")
    del c["output"]
    out.append(("x5 output field deleted (input_route)", c))
    c = clone("input_route")
    c["output"] = None
    out.append(("x6 output nulled (input_route)", c))
    return out


def main(argv):
    rc = 0
    path = _repo_run_path()
    if path is None:
        print("run record not found (searched %s from %s)" % (RUN_PATH, __file__))
        return 2
    raw = path.read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    data = json.loads(raw)
    rows = data["results"]
    print("RUN=%s bytes=%d sha256=%s\nRUN_SHA_MATCH=%s rows=%d"
          % (path, len(raw), got, got == RUN_SHA256, len(rows)))
    res = receipt_shape_gate(rows)
    flags = [r for r in res if r["flagged"]]
    unaccounted = [r for r in res if not r["accounted"]]
    print("green replay: rows=%d flagged=%d accounted=%d unaccounted=%d"
          % (len(res), len(flags), len(res) - len(unaccounted), len(unaccounted)))
    for r in flags:
        print("  FLAG %s %s" % (r["case"], r["reasons"]))

    ev_path = Path("/var/tmp/r103-mut5/evasions.json")
    if ev_path.is_file():
        ev = json.loads(ev_path.read_text())
        print("\nmut05 evasions (%d):" % len(ev["evasions"]))
        nf = 0
        for e in ev["evasions"]:
            rr = check_record(e["row"])
            nf += rr["flagged"]
            print("  %-28s flagged=%-5s %s" % (e["name"], rr["flagged"],
                                               "; ".join(rr["reasons"])[:110]))
        print("  green controls:")
        for g in ev["green_controls"]:
            rr = check_record(g["row"])
            print("  %-28s flagged=%s" % (g["name"], rr["flagged"]))
        print("  evasion flags: %d/%d" % (nf, len(ev["evasions"])))
        rc |= 0 if nf == len(ev["evasions"]) else 1
    else:
        print("\nmut05 evasions.json not found (run mut05 --emit-only first)")
        rc |= 1

    print("\nsynthetic corruptions (expect 6/6 flagged):")
    nf = 0
    for name, row in _synthetic_corruptions(rows):
        rr = check_record(row)
        nf += rr["flagged"]
        print("  %-46s flagged=%-5s %s" % (name, rr["flagged"],
                                           "; ".join(rr["reasons"])[:110]))
    print("  corruption flags: %d/6" % nf)
    rc |= 0 if nf == 6 else 1
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
