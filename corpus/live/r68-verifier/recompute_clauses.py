#!/usr/bin/env python3
"""r68 verifier: independently recompute divergent_clause + sha256 from raw streams.

Reimplements classify_process / classify_streams / the clause attribution
FROM SPEC (the classifier contract), not by importing run_battery's mirrors —
an independent check that each tuple names a clause that actually differs.
"""
import json, hashlib, sys

SIG = "STREAM_STDOUT: expected attribution marker"

def merged_allowed_error(line, allowed):
    s = line.strip()
    if s == allowed:
        return True
    if allowed.endswith(","):
        return s.startswith(allowed) and s.count("ERROR:") == 1
    if allowed == "ERROR: chain incomplete":
        return (s.startswith("ERROR: chain incomplete collections=")
                and "scene=SceneB:<Node#" in s and "old_alive=false" in s
                and s.count("ERROR:") == 1)
    return False

def stream_line_allowed(stripped, allowed_set):
    if stripped in allowed_set:
        return True
    for a in allowed_set:
        if a.endswith(",") and stripped.startswith(a) and stripped.count("ERROR:") == 1:
            return True
    return False

def clause_signature(so, se, code, error, merged_allowed, stream_allowed):
    """Independent reimplementation of the clause-attribution semantics."""
    merged = so + se
    diffs = []
    # exit clause: identical inputs -> identical clause verdict, can never differ
    if (code == 0 and error is None) != (code == 0 and error is None):
        diffs.append("exit")
    # signature clause: merged-anywhere vs stdout-only
    if (SIG in merged) != (SIG in so):
        diffs.append("signature")
    # blob clause: whole-blob vs per-stream
    merged_blob = "SCRIPT ERROR:" in merged or "Parse Error:" in merged
    stream_blob = any(t in so or t in se for t in ("SCRIPT ERROR:", "Parse Error:"))
    if merged_blob != stream_blob:
        diffs.append("blob")
    # error-scan clause: merged scans merged lines for ERROR: minus merged-allowed;
    # streams rejects any non-allowed nonempty stderr line
    merged_rej = [l for l in merged.splitlines()
                  if "ERROR:" in l
                  and not any(merged_allowed_error(l, a) for a in merged_allowed)]
    stream_rej = [s for s in (l.strip() for l in se.splitlines())
                  if s and not stream_line_allowed(s, set(stream_allowed))]
    if bool(merged_rej) != bool(stream_rej):
        if (stream_rej and all("ERROR:" in l and any(
                merged_allowed_error(l, a) for a in merged_allowed)
                for l in stream_rej)):
            diffs.append("allowlist_shape")
        else:
            diffs.append("error_scan")
    return diffs

def main():
    path = sys.argv[1]
    d = json.load(open(path))
    dv = d["divergence"]
    arms = {a["case"]: a for a in dv["arms"]}
    pair = dv["pair_reclassifications"]
    res = {r["case"]: r for r in d["results"]}

    # Build the same inputs dual_classify saw: pair rows use accept/reject
    # raw streams with empty allowlists; arms use their own raw streams.
    inputs = {}
    for name in ("stream_accept", "stream_reject"):
        src = res[name]
        inputs[name] = (src["raw_stdout"], src["raw_stderr"],
                        src["actual_exit"], src["error"], (), ())
    for name, a in arms.items():
        inputs[name] = (a["raw_stdout"], a["raw_stderr"],
                        a["actual_exit"], a["error"],
                        tuple(a["merged_allowlist"]),
                        tuple(a["stream_allowlist"]))

    mism = []
    table = {r["case"]: r for r in dv["divergence_table"]}
    for name, (so, se, code, err, ma, sa) in inputs.items():
        mine = clause_signature(so, se, code, err, ma, sa)
        got = list(table[name]["divergent_clause"])
        status = "OK" if mine == got else "MISMATCH"
        if mine != got:
            mism.append(name)
        print(f"{status} {name}: mine={mine} receipt={got}")
        # sha256 recompute from raw captured bytes
        rec = pair.get(name) or arms.get(name)
        mo = hashlib.sha256(so.encode()).hexdigest()
        me = hashlib.sha256(se.encode()).hexdigest()
        ok = (rec["raw_stdout_sha256"] == mo and rec["raw_stderr_sha256"] == me)
        if not ok:
            mism.append(name + ":sha")
        print(f"      sha256 stdout={'OK' if rec['raw_stdout_sha256']==mo else 'BAD'} "
              f"stderr={'OK' if rec['raw_stderr_sha256']==me else 'BAD'}")
    # reclass records: digest must equal source arm's digest
    for key, rec in dv["allowlist_reclassifications"].items():
        src_name = {"stderr_error__exact_entry": "streamdiv_stderr_error",
                    "stderr_error__foreign_entry": "streamdiv_stderr_error",
                    "stderr_structured__exact_line_entry": "streamdiv_stderr_structured",
                    "stderr_structured__bare": "streamdiv_stderr_structured",
                    "sig_on_stderr__bare": "streamdiv_sig_on_stderr",
                    "seam_error__bare": "streamdiv_seam_error"}[key]
        src = arms[src_name]
        ok = (rec["raw_stdout_sha256"] == src["raw_stdout_sha256"]
              and rec["raw_stderr_sha256"] == src["raw_stderr_sha256"])
        print(f"{'OK' if ok else 'BAD'} reclass {key} digests==source arm")
        if not ok:
            mism.append(key)
    print("MISMATCHES:", mism if mism else "none")

main()
