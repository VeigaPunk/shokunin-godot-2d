#!/usr/bin/env python3
"""Divergence matrix: feed identical (stdout, stderr) byte pairs to the
verbatim classifiers. merged = stdout + stderr (run_process l.152 semantics).
Each row reports merged verdict / streams verdict / divergent / mechanism."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verbatim_classifiers import classify_process, classify_streams

SIG = "SIG: expected marker"
ERR = "ERROR: injected diagnostic"
STRUCT_ENTRY = "ERROR: chain incomplete"
STRUCT_LINE = "ERROR: chain incomplete collections=1 scene=SceneB:<Node#7> old_alive=false"
COMMA_ENTRY = "ERROR: COMMA expected,"
COMMA_LINE = "ERROR: COMMA expected, tail=forged-suffix"

# (label, stdout, stderr, code, error, expected_exit, signature,
#  allowed_errors_for_merged, allowed_stderr_for_streams, mechanism_tag)
ROWS = [
    # --- claimed axis: ERROR: placement ---
    ("A_stdout_error_absorbed", f"{SIG}\n{ERR}\n", "", 0, None, 0, SIG, (), (),
     "claim-1: stdout ERROR: invisible to streams"),
    ("B_stderr_error_both_reject", f"{SIG}\n", f"{ERR}\n", 0, None, 0, SIG, (), (),
     "stderr ERROR: scanned by both"),
    ("C_stderr_error_allowlisted_both", f"{SIG}\n", f"{ERR}\n", 0, None, 0, SIG,
     (ERR,), (ERR,), "same allowlist entry, same stderr line"),
    ("D_stdout_error_allowlisted", f"{SIG}\n{ERR}\n", "", 0, None, 0, SIG,
     (ERR,), (), "merged absorbs via allowlist; streams ignores stdout"),
    ("E_sig_on_stderr_only", "banner\n", f"{SIG}\n", 0, None, 0, SIG, (), (),
     "claim-2: signature must be stdout for streams, anywhere for merged"),
    ("F_sig_on_stdout_clean", f"{SIG}\n", "", 0, None, 0, SIG, (), (),
     "control: both pass"),
    # --- seam fabrications (merged = stdout+stderr literal concat) ---
    ("G_sig_split_seam", f"banner\n{SIG[:3]}", f"{SIG[3:]}\n", 0, None, 0, SIG,
     (), (), "seam-forged signature: exists in merged, in NEITHER stream"),
    ("H_error_split_seam", f"{SIG}\nERR", "OR: allowlisted tail\n", 0, None, 0, SIG,
     (), ("OR: allowlisted tail",),
     "seam-forged ERROR:: merged sees 'ERROR: allowlisted tail'; streams sees benign allowlisted stderr line"),
    ("I_error_split_seam_merged_allows", f"{SIG}\nERR", "OR: exact merged\n", 0, None, 0, SIG,
     ("ERROR: exact merged",), ("OR: exact merged",),
     "same seam forgery, merged allowlist keyed on forged text"),
    ("J_script_error_split_seam", f"{SIG}\nSCRIPT ERR", "OR: benign\n", 0, None, 0, SIG,
     (), ("OR: benign",),
     "seam-forged SCRIPT ERROR: blob conjunct"),
    # --- non-ERROR stderr strictness ---
    ("K_stderr_benign_chatter", f"{SIG}\n", "WARNING: benign chatter\n", 0, None, 0, SIG,
     (), (), "streams requires EVERY stderr line allowlisted; merged ignores non-ERROR lines"),
    ("L_stderr_plain_text", f"{SIG}\n", "some engine info line\n", 0, None, 0, SIG,
     (), (), "same strictness, zero error markers"),
    ("M_stderr_blank_line", f"{SIG}\n", "\n", 0, None, 0, SIG, (), (),
     "control: blank stderr line skipped by streams"),
    # --- allowlist semantics asymmetry ---
    ("N_struct_entry_on_stderr", f"{SIG}\n", f"{STRUCT_LINE}\n", 0, None, 0, SIG,
     (STRUCT_ENTRY,), (STRUCT_ENTRY,),
     "'ERROR: chain incomplete' special-case matcher exists ONLY in merged allowed_error"),
    ("O_comma_entry_on_stderr", f"{SIG}\n", f"{COMMA_LINE}\n", 0, None, 0, SIG,
     (COMMA_ENTRY,), (COMMA_ENTRY,), "comma-prefix matcher identical both sides"),
    ("P_allowlist_scoped_merged_only", f"{SIG}\n", f"{ERR}\n", 0, None, 0, SIG,
     (ERR,), (), "entry in allowed_errors only: merged absorbs, streams rejects"),
    ("Q_allowlist_scoped_streams_only", f"{SIG}\n", f"{ERR}\n", 0, None, 0, SIG,
     (), (ERR,), "entry in allowed_stderr only: streams absorbs, merged rejects"),
    ("R_stdout_error_dual", f"{SIG}\n{ERR}\n", "ERROR: other\n", 0, None, 0, SIG,
     (), ("ERROR: other",), "stdout ERROR absorbed by streams while stderr allowlisted"),
    # --- marker clauses ---
    ("S_stdout_script_error", f"{SIG}\nSCRIPT ERROR: x\n", "", 0, None, 0, SIG,
     (), (), "SCRIPT ERROR: checked in stdout by streams too — both reject"),
    ("T_stderr_script_error", f"{SIG}\n", "SCRIPT ERROR: x\n", 0, None, 0, SIG,
     (), (), "SCRIPT ERROR: on stderr: streams clause rejects AND line unallowlisted"),
    ("U_sig_contains_error_substring", "ERROR: embedded sig\n", "", 0, None, 0,
     "ERROR: embedded sig", (), (), "signature itself contains 'ERROR:' — merged line-scans its own signature"),
    # --- exit/error channel ---
    ("V_wrong_exit", f"{SIG}\n{ERR}\n", "", 1, None, 0, SIG, (), (),
     "exit mismatch dominates both"),
    ("W_error_channel", f"{SIG}\n{ERR}\n", "", 0, "TIMEOUT after 8 seconds", 0, SIG,
     (), (), "error channel dominates both"),
]

results = []
n_div = 0
for (label, out, err, code, error, exp, sig, al_m, al_s, mech) in ROWS:
    merged = classify_process(code, error, out + err, exp, sig, al_m)
    streams = classify_streams(code, error, out, err, exp, sig, al_s)
    div = merged != streams
    n_div += div
    row = {"row": label, "merged": merged, "streams": streams,
           "divergent": div, "mechanism": mech,
           "merged_dir": ("merged_only_pass" if merged and not streams else
                          "streams_only_pass" if streams and not merged else
                          "agree_pass" if merged else "agree_fail")}
    results.append(row)
    print(f"{'DIV' if div else '  ='} {label:42s} merged={merged!s:5s} "
          f"streams={streams!s:5s}  {row['merged_dir']}")

out_path = Path(__file__).resolve().parent / "matrix_results.json"
out_path.write_text(json.dumps(results, indent=2) + "\n")
print(f"\n{sum(1 for r in results if r['divergent'])}/{len(results)} divergent rows -> {out_path}")
