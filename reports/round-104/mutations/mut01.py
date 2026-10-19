#!/usr/bin/env python3
"""r104 M1 / mut01 — cache-identity forgery against E2's res_uid row family.

Mandate: E2's `res_uid_s02` row (load-cache identity + cache_mode busting) must
REJECT an arm whose *cache-identity* evidence is forged — i.e. an arm that
claims same-Object identity across `ResourceLoader.load()` cache modes without a
real in-run `ResourceLoader.load()` having produced that claim.

Model arms (all booleans measured on real godot 4.7.2.stable.arch_linux.ed1daf0bf):
  G   genuine        : real `godot --headless --script res://identity_probe.gd`
                       run; evidence file written by the probe itself.
  F1  flag-forge     : genuine transcript, `same_ignore=0` -> `1` (ids untouched).
                       No run at all. Internally inconsistent.
  F2  foreign-forge  : a foreign evidence file (sentinel resource + forger
                       marker) planted at the row's evidence path. No run.
  F3  stale-forge    : genuine evidence copied + backdated to 2020; the run
                       step forced to fail (bogus script path) -> resurrection.
  F4  consistent-forge: genuine transcript with BOTH the flag and the id
                       flipped consistently (`same_ignore=1`, `id_ignore=id_default`),
                       fresh mtime, no sentinel. The strongest forgery.

Verdict logics over captured bytes (forge read BEFORE any overwrite):
  naive       : a PASS-shaped line with the expected fields exists -> accept.
  honest      : exit==0 THIS run; evidence bytes == the run's OWN stdout PASS
                lines (no re-readable side artifact); mtime >= t0; sentinel
                absent; per-row internal consistency (flag must agree with ids).
  honest_reuse: consistency + sentinel + mtime only, WITHOUT the in-run-stdout
                identity requirement — measures which forges a reuse design
                (row reads a file, never the child's own stdout) still catches.

Phase B: attacks the landed real fixture read-only (E2's `res_uid_s02.gd` if it
exists at probe time, else the landed `res_uid_w07.gd` arm=cache), recording the
substitution; plus a scratch-only vulnerable variant as the attack-lands control.

Never runs run_battery.py; touches no shared file; the corpus is copied, never
edited. Scratch: /var/tmp/r104-M1 only (never /tmp: EDQUOT quota on this host).
"""

import hashlib
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

ROOT = Path(os.environ.get("MUT01_ROOT", "/var/tmp/r104-M1/mut01"))
GODOT = "/usr/bin/godot"
SENTINEL_TOKEN = "M1_FORGED_SENTINEL"
BACKDATE = 1577836800  # 2020-01-01
CORPUS = Path(__file__).resolve().parents[3] / "corpus" / "fixtures"
E2_FX = CORPUS / "res_uid_s02.gd"
W7_FX = CORPUS / "res_uid_w07.gd"

PROJECT_CFG = (
    'config_version=5\n\n[application]\nconfig/name="M1Model"\n'
    'config/features=PackedStringArray("4.7")\n'
)

PROBE_GD = '''extends SceneTree

var evidence := ""
var arm := ""

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--evidence="):
			evidence = a.substr(11)
		elif a.begins_with("--arm="):
			arm = a.substr(6)
	_run.call_deferred()

func _rows() -> Array:
	var rows := []
	var P := "res://model/obj.tres"
	var a = ResourceLoader.load(P)
	var b = ResourceLoader.load(P)
	var ign = ResourceLoader.load(P, "", ResourceLoader.CACHE_MODE_IGNORE)
	var rep = ResourceLoader.load(P, "", ResourceLoader.CACHE_MODE_REPLACE)
	var after = ResourceLoader.load(P)
	rows.append("PASS res_uid s02 arm=%s res=res://model/obj.tres same_default=%d same_ignore=%d same_replace=%d same_after_replace=%d id_default=%d id_ignore=%d id_replace=%d cached=%d" % [
		arm, int(is_same(a, b)), int(is_same(a, ign)), int(is_same(a, rep)),
		int(is_same(rep, after)), a.get_instance_id(), ign.get_instance_id(),
		rep.get_instance_id(), int(ResourceLoader.has_cached(P))])
	var U := "user://m1/cache.tres"
	DirAccess.make_dir_recursive_absolute("user://m1")
	var g := Gradient.new()
	g.colors = PackedColorArray([Color(1, 0, 0, 1), Color(0, 0, 1, 1)])
	var e := ResourceSaver.save(g, U)
	var u1 = ResourceLoader.load(U)
	var u2 = ResourceLoader.load(U)
	var uign = ResourceLoader.load(U, "", ResourceLoader.CACHE_MODE_IGNORE)
	rows.append("PASS res_uid s02 arm=%s res=user://m1/cache.tres save=%d same_default=%d same_ignore=%d cached=%d" % [
		arm, e, int(is_same(u1, u2)), int(is_same(u1, uign)), int(ResourceLoader.has_cached(U))])
	return rows

func _run() -> void:
	var rows := _rows()
	var out := ""
	for r in rows:
		print(r)
		out += r + "\\n"
	if evidence != "":
		var f := FileAccess.open(evidence, FileAccess.WRITE)
		if f == null:
			print("FAIL res_uid s02 reason=evidence_open_failed")
		else:
			f.store_string(out)
			f.close()
	quit(0)
'''

MODEL_OBJ = ('[gd_resource type="Resource" format=3]\n\n[resource]\n'
             'resource_name = "M1Obj"\nmarker = "M1_MODEL_OBJ"\n')


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(p):
    p = Path(p)
    return sha256(p.read_bytes()) if p.is_file() else None


def fields(line):
    out = {}
    for tok in line.split():
        if "=" in tok:
            k, _, v = tok.partition("=")
            out[k] = v
    return out


def consistency(rows):
    """Per-row internal law measured this round: for a .tres/.tscn resource the
    IGNORE load returns a DIFFERENT object with a DIFFERENT instance id, so the
    boolean flag and the id fields must agree."""
    bad = []
    for r in rows:
        f = fields(r)
        if "same_ignore" not in f or "id_ignore" not in f or "id_default" not in f:
            continue
        same = f["same_ignore"] == "1"
        ids_equal = f["id_ignore"] == f["id_default"]
        if same != ids_equal:
            bad.append({"row": r, "same_ignore": f["same_ignore"],
                        "id_ignore": f["id_ignore"], "id_default": f["id_default"]})
    return bad


def naive_verdict(evidence_bytes):
    """Presence census: a PASS-shaped row that carries any identity field is
    accepted — no in-run anchoring, no internal consistency, no freshness."""
    rows = [l for l in evidence_bytes.decode("utf-8", "replace").splitlines()
            if l.startswith("PASS res_uid s02 ")]
    if not rows:
        return {"verdict": "FAIL", "reason": "no_pass_shaped_row", "rows": []}
    has_identity = any(("same_default" in fields(r)) or ("same_ignore" in fields(r))
                       for r in rows)
    if not has_identity:
        return {"verdict": "FAIL", "reason": "identity_claim_absent", "rows": rows}
    return {"verdict": "PASS", "reason": "", "rows": rows}


def honest_verdict(evidence_bytes, run, t0_ns):
    """Fail-closed: only in-run evidence, cross-checked against the run's own stdout."""
    if run.get("exit") != 0:
        return {"verdict": "FAIL", "reason": "run_exit=%s" % run.get("exit")}
    rows = [l for l in evidence_bytes.decode("utf-8", "replace").splitlines()
            if l.startswith("PASS res_uid s02 ")]
    if not rows:
        return {"verdict": "FAIL", "reason": "no_pass_shaped_row"}
    if SENTINEL_TOKEN in evidence_bytes.decode("utf-8", "replace"):
        return {"verdict": "FAIL", "reason": "foreign_sentinel_in_evidence", "rows": rows}
    if t0_ns is not None and run.get("evidence_mtime_ns") is not None \
            and run["evidence_mtime_ns"] < t0_ns:
        return {"verdict": "FAIL", "reason": "stale_evidence_mtime", "rows": rows}
    own = [l for l in run.get("pass_lines", []) if l.startswith("PASS res_uid s02 ")]
    if own != rows:
        return {"verdict": "FAIL", "reason": "evidence_not_from_this_runs_stdout",
                "rows": rows, "own_rows": own}
    bad = consistency(rows)
    if bad:
        return {"verdict": "FAIL", "reason": "internal_consistency", "rows": rows, "bad": bad}
    return {"verdict": "PASS", "reason": "", "rows": rows}


def honest_reuse(evidence_bytes, t0_ns, mtime_ns=None):
    """Consistency + sentinel + mtime, but no in-run-stdout identity requirement."""
    txt = evidence_bytes.decode("utf-8", "replace")
    rows = [l for l in txt.splitlines() if l.startswith("PASS res_uid s02 ")]
    if not rows:
        return {"verdict": "FAIL", "reason": "no_pass_shaped_row"}
    if SENTINEL_TOKEN in txt:
        return {"verdict": "FAIL", "reason": "foreign_sentinel_in_evidence", "rows": rows}
    if t0_ns is not None and mtime_ns is not None and mtime_ns < t0_ns:
        return {"verdict": "FAIL", "reason": "stale_evidence_mtime", "rows": rows}
    bad = consistency(rows)
    if bad:
        return {"verdict": "FAIL", "reason": "internal_consistency", "rows": rows, "bad": bad}
    return {"verdict": "PASS", "reason": "reuse_accepted", "rows": rows}


def write(p, text):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


def build_proj():
    proj = ROOT / "proj"
    write(proj / "project.godot", PROJECT_CFG)
    write(proj / "model" / "obj.tres", MODEL_OBJ)
    write(proj / "identity_probe.gd", PROBE_GD)
    return proj


def run_probe(proj, arm, evidence, script="res://identity_probe.gd", timeout=120):
    cmd = [GODOT, "--headless", "--path", str(proj), "--script", script, "--",
           "--arm=" + arm, "--evidence=" + str(evidence)]
    t0 = time.monotonic()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        rc, out, err = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        rc, out, err = None, "", "TIMEOUT"
    ev = Path(evidence)
    return {"cmd": cmd, "exit": rc, "seconds": round(time.monotonic() - t0, 2),
            "pass_lines": [l for l in out.splitlines() if l.startswith("PASS ")],
            "fail_lines": [l for l in out.splitlines() if l.startswith("FAIL ")],
            "stdout_sha256": sha256(out.encode()),
            "stderr_bytes": len(err.encode()),
            "evidence_exists": ev.is_file(),
            "evidence_mtime_ns": ev.stat().st_mtime_ns if ev.is_file() else None,
            "evidence_sha256": sha256_file(ev)}


def forge_flag(genuine_text):
    """F1: flip the boolean only, leave the id fields — internally inconsistent."""
    return genuine_text.replace("same_ignore=0", "same_ignore=1")


def forge_consistent(genuine_text):
    """F4: flip the boolean AND the id field so the row is internally consistent."""
    out = []
    for line in genuine_text.splitlines():
        f = fields(line)
        if line.startswith("PASS res_uid s02 ") and "same_ignore" in f and "id_default" in f:
            line = line.replace("same_ignore=0", "same_ignore=1")
            line = line.replace("id_ignore=" + f["id_ignore"], "id_ignore=" + f["id_default"])
        out.append(line)
    return "\n".join(out) + "\n"


def slim(v):
    v = dict(v)
    v.pop("rows", None)
    return v


def main():
    out = {"seat": "M1", "script": "mut01.py",
           "engine": subprocess.run([GODOT, "--version"], capture_output=True,
                                    text=True).stdout.strip(),
           "date": time.strftime("%Y-%m-%d %H:%M:%S %z"),
           "uptime": open("/proc/uptime").read().split()[0],
           "loadavg": list(os.getloadavg()),
           "scratch": str(ROOT)}
    shutil.rmtree(ROOT, ignore_errors=True)
    proj = build_proj()
    (ROOT / "out").mkdir(parents=True)

    # ---- G genuine ---------------------------------------------------------
    g_ev = ROOT / "out" / "G" / "identity_evidence.txt"
    g_ev.parent.mkdir(parents=True, exist_ok=True)
    t0_g = time.time_ns()
    r_g = run_probe(proj, "genuine", g_ev)
    g_bytes = g_ev.read_bytes() if g_ev.is_file() else b""
    g_text = g_bytes.decode("utf-8", "replace")
    out["genuine"] = {"run": r_g, "evidence_text": g_text,
                      "t0_ns": t0_g,
                      "naive": slim(naive_verdict(g_bytes)),
                      "honest": slim(honest_verdict(g_bytes, r_g, t0_g)),
                      "reuse": slim(honest_reuse(g_bytes, t0_g))}
    out["consistency_genuine"] = consistency(
        [l for l in g_text.splitlines() if l.startswith("PASS res_uid s02 ")])

    arms = {}

    # ---- F1 flag-forge -----------------------------------------------------
    f1 = ROOT / "out" / "F1"
    f1_ev = f1 / "identity_evidence.txt"
    write(f1_ev, forge_flag(g_text))
    write(f1 / "transcript.txt", forge_flag(g_text))
    f1_bytes = f1_ev.read_bytes()
    arms["F1_flag_forge"] = {
        "forge": "genuine transcript, same_ignore=0 -> 1 (ids untouched); no run",
        "evidence_sha256": sha256(f1_bytes),
        "no_run_this_arm": True,
        "naive": slim(naive_verdict(f1_bytes)),
        "reuse": slim(honest_reuse(f1_bytes, None)),
        "honest": slim(honest_verdict(f1_bytes, {"exit": None}, None)),
        "consistency_violations": consistency(
            [l for l in f1_bytes.decode().splitlines() if l.startswith("PASS res_uid s02 ")]),
    }

    # ---- F2 foreign-forge --------------------------------------------------
    f2 = ROOT / "out" / "F2"
    f2_ev = f2 / "identity_evidence.txt"
    foreign = (g_text + "PASS res_uid s02 arm=foreign res=res://foreign/obj.tres "
                         "same_ignore=1 cached=1 forger=%s\n" % SENTINEL_TOKEN)
    write(f2_ev, foreign)
    f2_bytes = f2_ev.read_bytes()
    arms["F2_foreign_forge"] = {
        "forge": "foreign evidence file with sentinel resource + forger marker; no run",
        "evidence_sha256": sha256(f2_bytes),
        "sentinel_in_evidence": SENTINEL_TOKEN in f2_bytes.decode(),
        "naive": slim(naive_verdict(f2_bytes)),
        "reuse": slim(honest_reuse(f2_bytes, None)),
        "honest": slim(honest_verdict(f2_bytes, {"exit": None}, None)),
    }

    # ---- F3 stale-forge ----------------------------------------------------
    f3 = ROOT / "out" / "F3"
    f3_ev = f3 / "identity_evidence.txt"
    write(f3_ev, g_text)
    os.utime(f3_ev, (BACKDATE, BACKDATE))
    t0 = time.time_ns()
    r_f3 = run_probe(proj, "genuine", f3_ev, script="res://no_such_probe.gd")
    f3_bytes = f3_ev.read_bytes() if f3_ev.is_file() else b""
    arms["F3_stale_forge"] = {
        "forge": "genuine evidence cp'd + backdated 2020; run forced to fail",
        "evidence_sha256": sha256(f3_bytes),
        "stale_mtime": f3_ev.stat().st_mtime if f3_ev.is_file() else None,
        "bogus_run": r_f3,
        "file_survives_failed_run": f3_ev.is_file(),
        "naive": slim(naive_verdict(f3_bytes)),
        "reuse": slim(honest_reuse(f3_bytes, t0, f3_ev.stat().st_mtime_ns if f3_ev.is_file() else None)),
        "honest": slim(honest_verdict(f3_bytes, r_f3, t0)),
    }

    # ---- F4 consistent-forge (strongest) -----------------------------------
    f4 = ROOT / "out" / "F4"
    f4_ev = f4 / "identity_evidence.txt"
    write(f4_ev, forge_consistent(g_text))
    f4_bytes = f4_ev.read_bytes()
    arms["F4_consistent_forge"] = {
        "forge": "genuine transcript, same_ignore AND id_ignore flipped together; "
                 "fresh mtime, no sentinel, no run",
        "evidence_sha256": sha256(f4_bytes),
        "naive": slim(naive_verdict(f4_bytes)),
        "reuse": slim(honest_reuse(f4_bytes, time.time_ns())),
        "honest": slim(honest_verdict(f4_bytes, {"exit": None}, None)),
        "consistency_violations": consistency(
            [l for l in f4_bytes.decode().splitlines() if l.startswith("PASS res_uid s02 ")]),
    }

    # ---- F5 fresh-run neutralization (forge planted, real run then happens) --
    f5 = ROOT / "out" / "F5"
    f5_ev = f5 / "identity_evidence.txt"
    write(f5_ev, forge_consistent(g_text))
    pre_sha = sha256(f5_ev.read_bytes())
    t0 = time.time_ns()
    r_f5 = run_probe(proj, "genuine", f5_ev)
    f5_bytes = f5_ev.read_bytes() if f5_ev.is_file() else b""
    arms["F5_forge_then_fresh_run"] = {
        "forge": "F4 bytes planted, then a REAL run writes the evidence path",
        "planted_sha256": pre_sha,
        "fresh_run": r_f5,
        "post_sha256": sha256(f5_bytes),
        "overwritten": sha256(f5_bytes) != pre_sha,
        "naive": slim(naive_verdict(f5_bytes)),
        "reuse": slim(honest_reuse(f5_bytes, t0)),
        "honest": slim(honest_verdict(f5_bytes, r_f5, t0)),
        "honest_rows": honest_verdict(f5_bytes, r_f5, t0).get("rows", []),
        "genuine_rows": [l for l in g_text.splitlines()
                         if l.startswith("PASS res_uid s02 ")],
    }
    out["arms"] = arms

    # ---- assertions --------------------------------------------------------
    asserts = {}

    def mk(name, ok, detail):
        asserts[name] = {"ok": bool(ok), "detail": detail}

    mk("genuine_row_pass_shaped",
       naive_verdict(g_bytes)["verdict"] == "PASS" and honest_verdict(g_bytes, r_g, t0_g)["verdict"] == "PASS",
       {"naive": naive_verdict(g_bytes)["verdict"],
        "honest": honest_verdict(g_bytes, r_g, t0_g)["verdict"],
        "consistency_ok": not out["consistency_genuine"]})

    f1a = arms["F1_flag_forge"]
    mk("naive_accepts_F1 (defect class proof)",
       f1a["naive"]["verdict"] == "PASS" and len(f1a["consistency_violations"]) >= 1,
       {"naive": f1a["naive"]["verdict"], "violations": len(f1a["consistency_violations"])})
    mk("honest_REJECTS_F1 (no in-run stdout)",
       f1a["honest"]["verdict"] == "FAIL", {"reason": f1a["honest"]["reason"]})
    mk("honest_reuse_REJECTS_F1 (internal consistency)",
       f1a["reuse"]["verdict"] == "FAIL" and f1a["reuse"]["reason"] == "internal_consistency",
       {"reason": f1a["reuse"]["reason"]})

    f2a = arms["F2_foreign_forge"]
    mk("naive_accepts_F2 (defect class proof)",
       f2a["naive"]["verdict"] == "PASS" and f2a["sentinel_in_evidence"],
       {"naive": f2a["naive"]["verdict"]})
    mk("honest_REJECTS_F2 / reuse_REJECTS_F2 (sentinel)",
       f2a["honest"]["verdict"] == "FAIL" and f2a["reuse"]["verdict"] == "FAIL",
       {"honest": f2a["honest"]["reason"], "reuse": f2a["reuse"]["reason"]})

    f3a = arms["F3_stale_forge"]
    mk("naive_accepts_F3 (resurrection, defect class proof)",
       f3a["naive"]["verdict"] == "PASS" and f3a["bogus_run"]["exit"] != 0
       and f3a["file_survives_failed_run"],
       {"naive": f3a["naive"]["verdict"], "bogus_exit": f3a["bogus_run"]["exit"]})
    mk("honest_REJECTS_F3 (failed run cannot resurrect)",
       f3a["honest"]["verdict"] == "FAIL" and f3a["honest"]["reason"].startswith("run_exit="),
       {"reason": f3a["honest"]["reason"]})
    mk("honest_reuse_REJECTS_F3 (stale mtime)",
       f3a["reuse"]["verdict"] == "FAIL" and f3a["reuse"]["reason"] == "stale_evidence_mtime",
       {"reason": f3a["reuse"]["reason"]})

    f4a = arms["F4_consistent_forge"]
    mk("naive_accepts_F4 (defect class proof)",
       f4a["naive"]["verdict"] == "PASS", {"naive": f4a["naive"]["verdict"]})
    mk("RESIDUAL_honest_reuse_ACCEPTS_F4 (self-consistent fresh forge)",
       f4a["reuse"]["verdict"] == "PASS" and f4a["reuse"]["reason"] == "reuse_accepted"
       and not f4a["consistency_violations"],
       {"reuse": f4a["reuse"]["verdict"], "reason": f4a["reuse"]["reason"]})
    mk("honest_REJECTS_F4 (evidence != this run's own stdout)",
       f4a["honest"]["verdict"] == "FAIL", {"reason": f4a["honest"]["reason"]})

    f5a = arms["F5_forge_then_fresh_run"]
    mk("honest_neutralizes_F5 (fresh run overwrites the forge)",
       f5a["overwritten"] and f5a["honest"]["verdict"] == "PASS"
       and f5a["honest_rows"] == f5a["genuine_rows"],
       {"overwritten": f5a["overwritten"], "honest": f5a["honest"]["verdict"],
        "post_sha": f5a["post_sha256"], "genuine_sha": sha256(g_bytes)})
    out["asserts"] = asserts

    out["phase_b"] = phase_b()

    payload = ROOT / "out" / "mut01_verdicts.json"
    payload.write_text(json.dumps(out, indent=1, default=str) + "\n")

    print("== mut01 summary ==")
    print("engine:", out["engine"], "| scratch:", out["scratch"])
    for name, a in asserts.items():
        print("ASSERT %-62s ok=%s %s" % (name, a["ok"], a["detail"]))
    for k, a in arms.items():
        print("ARM %-24s naive=%s reuse=%s(%s) honest=%s(%s)" % (
            k, a["naive"]["verdict"], a["reuse"]["verdict"], a["reuse"]["reason"],
            a["honest"]["verdict"], a["honest"]["reason"]))
    pb = out["phase_b"]
    print("phase_b: fixture_sha=%s stable=%s arms_with_fail=%s" % (
        str(pb.get("fixture_sha256_start"))[:16], pb.get("fixture_stable_during_attack"),
        pb.get("arms_with_fail")))
    print("phase_b P1 plant_reached_stdout=%s P2 naive_accepts=%s anchored_rejects=%s "
          "P3 attack_lands=%s" % (
              (pb.get("P1_plant") or {}).get("plant_reached_stdout"),
              (pb.get("P2_forged_transcript") or {}).get("naive_accepts"),
              (pb.get("P2_forged_transcript") or {}).get("anchored_rejects"),
              (pb.get("P3_variant") or {}).get("attack_lands_on_reuse_design")))
    print("wrote", payload)


# ------------------------------------------------------------------ phase B

E2_ARMS = ["reuse", "ignore", "replace", "bust", "deleted", "classes"]


def phase_b():
    """Attack the landed real fixture read-only.

    The fixture prints exactly one `PASS res_uid_s02 <arm> k=v ...` line to
    stdout and reads NO side artifact, so the forgery surface is the transcript
    itself. Three attack modes are measured:
      P1 planted evidence file : a forged transcript dropped at a plausible
         consumption path -> must not reach the row's census.
      P2 forged transcript      : the genuine line with the identity claim
         flipped -> the naive consumer accepts; an in-run-anchored consumer
         (re-run + byte-identity + exit) rejects.
      P3 variant (scratch-only) : a fixture that READS the side artifact instead
         of printing its own in-run truth -> attack-lands control.
    The fixture sha256 is pinned before and after every run (it is being edited
    concurrently by the E2 seat; a revision change is recorded, not hidden).
    """
    if not E2_FX.is_file():
        return {"status": "e2_fixture_absent_at_probe_time", "path": str(E2_FX),
                "w7_present": W7_FX.is_file()}

    src = E2_FX.read_text()
    sha_start = sha256(src.encode())
    pb = {"fixture": str(E2_FX), "fixture_sha256_start": sha_start,
          "arms": E2_ARMS}
    proj = ROOT / "fx" / "proj"
    write(proj / "project.godot", PROJECT_CFG)
    write(proj / "res_uid_s02.gd", src)

    def run_arm(arm):
        cmd = [GODOT, "--headless", "--path", str(proj), "--script",
               "res://res_uid_s02.gd", "--", "--arm=" + arm]
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            return {"arm": arm, "exit": p.returncode,
                    "pass_lines": [l for l in p.stdout.splitlines()
                                   if l.startswith("PASS ")],
                    "fail_lines": [l for l in p.stdout.splitlines()
                                   if l.startswith("FAIL ")],
                    "sentinel_in_stdout": SENTINEL_TOKEN in p.stdout,
                    "stdout_sha256": sha256(p.stdout.encode())}
        except subprocess.TimeoutExpired:
            return {"arm": arm, "exit": None, "state": "timeout_180s"}

    # ---- run every arm twice (byte-stability law) --------------------------
    runs = {}
    for arm in E2_ARMS:
        r1, r2 = run_arm(arm), run_arm(arm)
        runs[arm] = {"run1": r1, "run2": r2,
                     "byte_identical": r1.get("pass_lines") == r2.get("pass_lines")
                     and r1.get("stdout_sha256") == r2.get("stdout_sha256")}
    pb["runs"] = runs
    pb["all_arms_byte_stable"] = all(v["byte_identical"] for v in runs.values())
    pb["arms_with_pass"] = [a for a, v in runs.items() if v["run1"].get("pass_lines")]
    pb["arms_with_fail"] = [a for a, v in runs.items() if v["run1"].get("fail_lines")]
    pb["sentinel_never_in_stdout"] = not any(
        v["run1"].get("sentinel_in_stdout") or v["run2"].get("sentinel_in_stdout")
        for v in runs.values())

    # ---- P1 planted evidence file -----------------------------------------
    genuine_ignore = (runs["ignore"]["run1"].get("pass_lines") or [""])[0]
    forged_line = genuine_ignore.replace("distinct=true", "distinct=false")
    plant = ROOT / "fx" / "planted_evidence.txt"
    write(plant, forged_line + "\n" + SENTINEL_TOKEN + "\n")
    pb["P1_plant"] = {
        "path": str(plant), "sha256": sha256_file(plant),
        "genuine_line": genuine_ignore, "forged_line": forged_line,
        "forged_differs": forged_line != genuine_ignore,
    }
    r_after = run_arm("ignore")
    pb["P1_plant"]["pass_after_plant"] = r_after.get("pass_lines")
    pb["P1_plant"]["plant_reached_stdout"] = forged_line in (r_after.get("pass_lines") or [])
    pb["P1_plant"]["pass_lines_identical_to_pristine"] = \
        r_after.get("pass_lines") == runs["ignore"]["run1"].get("pass_lines")

    # ---- P2 forged transcript vs naive / anchored consumers ----------------
    def naive_e2(line):
        """E2-shaped naive consumer: a PASS line carrying the arm's identity
        token is accepted; no anchoring, no consistency, no freshness."""
        if not line.startswith("PASS res_uid_s02 "):
            return {"verdict": "FAIL", "reason": "not_pass_shaped"}
        if "distinct=" not in line and "same=" not in line:
            return {"verdict": "FAIL", "reason": "identity_token_absent"}
        return {"verdict": "PASS", "reason": ""}

    pb["P2_forged_transcript"] = {
        "genuine_line": genuine_ignore,
        "forged_line": forged_line,
        "naive_accepts": naive_e2(forged_line)["verdict"],
        "naive_reason": naive_e2(forged_line).get("reason"),
    }
    # anchored consumer: the forged transcript is not any real run's stdout
    real_stdouts = [v["run1"].get("stdout_sha256") for v in runs.values()]
    forged_sha = sha256((forged_line + "\n").encode())
    pb["P2_forged_transcript"]["forged_transcript_sha256"] = forged_sha
    pb["P2_forged_transcript"]["matches_any_real_stdout"] = forged_sha in real_stdouts
    pb["P2_forged_transcript"]["anchored_rejects"] = not (
        forged_sha in real_stdouts) or forged_line in (runs["ignore"]["run1"].get("pass_lines") or [])
    pb["P2_forged_transcript"]["anchored_reason"] = (
        "forged_transcript_is_not_any_in_run_stdout"
        if forged_sha not in real_stdouts else "transcript_matches_a_real_run")

    # ---- P3 scratch-only vulnerable variant (attack-lands control) ---------
    anchor = ("func _p(tokens: String) -> void:\n"
              "\tprint(\"PASS res_uid_s02 %s %s\" % [arm, tokens])\n")
    repl = ('func _p(tokens: String) -> void:\n'
            '\tvar ep := "/var/tmp/r104-M1/mut01/fx/planted_evidence.txt"\n'
            '\tif FileAccess.file_exists(ep):\n'
            '\t\tvar fh := FileAccess.open(ep, FileAccess.READ)\n'
            '\t\tprint(fh.get_as_text().strip_edges())\n'
            '\t\tfh.close()\n\t\treturn\n'
            '\tprint("PASS res_uid_s02 %s %s" % [arm, tokens])\n')
    variant = src.replace(anchor, repl, 1)
    pb["P3_variant"] = {"anchor_unique": src.count(anchor) == 1,
                        "changed": variant != src}
    if variant != src:
        vproj = ROOT / "fxv" / "proj"
        write(vproj / "project.godot", PROJECT_CFG)
        write(vproj / "res_uid_s02.gd", variant)
        cmd = [GODOT, "--headless", "--path", str(vproj), "--script",
               "res://res_uid_s02.gd", "--", "--arm=ignore"]
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        vlines = [l for l in p.stdout.splitlines() if l.startswith(("PASS ", "FAIL "))]
        pb["P3_variant"]["run"] = {"exit": p.returncode, "lines": vlines,
                                   "sentinel_in_stdout": SENTINEL_TOKEN in p.stdout}
        pb["P3_variant"]["attack_lands_on_reuse_design"] = \
            any(l.startswith("FAIL") for l in vlines) or SENTINEL_TOKEN in p.stdout

    sha_end = sha256(E2_FX.read_bytes())
    pb["fixture_sha256_end"] = sha_end
    pb["fixture_stable_during_attack"] = sha_start == sha_end
    # keep the attacked bytes so the verdict stays attributable after the
    # concurrent E2 seat lands further revisions
    snap = ROOT / "fx" / ("res_uid_s02_attacked_%s.gd" % sha_start[:12])
    write(snap, src)
    pb["attacked_revision_snapshot"] = {"path": str(snap), "sha256": sha_start}
    pb["revision_note"] = (
        "The E2 seat edited this fixture concurrently with this attack. An earlier "
        "revision observed at ~22:33 FAILed arm=bust "
        "(reason=post_mutation_reload_class_mismatch stale_reuse=v2, token "
        "after_reuse) and its sha256 was NOT captured at that moment; the sha "
        "ce863954c8f2 (mtime 22:34:19) and the pinned revision %s both PASS bust "
        "5/5 in a pristine project. Only the pinned revision's bytes are attacked "
        "here; the attacked bytes are snapshotted alongside." % sha_start[:12])
    return pb


if __name__ == "__main__":
    main()
