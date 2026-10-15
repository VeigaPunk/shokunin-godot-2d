#!/usr/bin/env python3
"""r66 critic: re-run the AUTHOR'S r66 fixture arms through my verbatim
classifier extraction — independent reproduction of the surface arms.
Same bounded-Popen shape as author's surface_run; merges stdout+stderr
verbatim; records kernel ppid provenance."""
import json, os, re, subprocess, textwrap, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIXTURES = ROOT.parent.parent / "fixtures"
SRC = (FIXTURES / "run_battery.py").read_text()
GODOT = "/usr/bin/godot"
SIG = "DESCENDANT_PIPE_PROBE: expected signature"
ALLOW = ("ERROR: SAVE EXPECTED NEGATIVE: malformed JSON rejected signature=JSON_PARSE_ERROR",)
m = re.search(r"(    def classify_process\(.*?\n)(?=    def classify_streams)", SRC, re.S)
ns = {"re": re}
exec(textwrap.dedent(m.group(1)), ns)
cls = ns["classify_process"]


def pid_alive(pid):
    if not pid: return None
    try: os.kill(pid, 0)
    except ProcessLookupError: return False
    except PermissionError: return True
    except OSError: return False
    return True

def kppid(pid):
    if not pid: return None
    try: s = Path(f"/proc/{pid}/stat").read_text()
    except OSError: return None
    return int(s.rsplit(")", 1)[1].split()[1])


import shutil
PROJ = ROOT / "author_proj"
if PROJ.exists(): shutil.rmtree(PROJ)
shutil.copytree(FIXTURES, PROJ, ignore=shutil.ignore_patterns(".godot", "out"))
(PROJ/".godot").mkdir(exist_ok=True); (PROJ/".godot"/".gdignore").write_text("")


def arm(flag, ppid_token, bound=3.0):
    cmd = [GODOT, "--headless", "--path", str(PROJ),
           "--script", "res://descendant_pipe_probe.gd", "--", flag]
    t0 = time.monotonic()
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         text=True, bufsize=1)
    try:
        out, err = p.communicate(timeout=bound); timed_out=False
    except subprocess.TimeoutExpired:
        p.kill(); out, err = p.communicate(); timed_out=True
    text = (out or "") + (err or "")
    pm = re.search(re.escape(ppid_token) + r"(\d+)", text)
    gm = re.search(r"DESCENDANT_PIPE godot_pid=(\d+)", text)
    return {"flag": flag, "timed_out": timed_out, "exit": p.returncode,
            "elapsed": round(time.monotonic()-t0, 3),
            "signature_observed": SIG in text,
            "error_lines": sorted({l.strip() for l in text.splitlines() if "ERROR:" in l}),
            "write_ppid": int(pm.group(1)) if pm else None,
            "godot_pid": int(gm.group(1)) if gm else None,
            "cls_no_allow": cls(p.returncode, None, text, 0, SIG),
            "cls_save_allow": cls(p.returncode, None, text, 0, SIG, ALLOW),
            "cls_foreign_allow": cls(p.returncode, None, text, 0, SIG, ("ERROR: foreign",)),
            "stdout_tail": (out or "").splitlines()[-1] if (out or "").splitlines() else None,
            "stderr_head": (err or "").splitlines()[0] if (err or "").splitlines() else None,
            "stdout_endswith_no_nl": bool(out) and not out.endswith("\n"),
            "stdout_blob_tail": (out or "")[-160:],
            "stderr_blob_head": (err or "")[:160],
            }


res = {}
for flag, tok in [("--spawn-allowforge", "DESCENDANT_PIPE_ALLOWFORGE write_ppid="),
                  ("--spawn-splitforge", "DESCENDANT_PIPE_SPLITFORGE write_ppid="),
                  ("--spawn-seamforge", "DESCENDANT_PIPE_SEAMFORGE write_ppid="),
                  ("--spawn-midlineforge", "DESCENDANT_PIPE_MIDLINE write_ppid=")]:
    res[flag] = [arm(flag, tok) for _ in range(3)]
    for r in res[flag]:
        print(flag, "exit", r["exit"], "sig", r["signature_observed"],
              "cls", r["cls_no_allow"], "errlines", r["error_lines"],
              "wppid", r["write_ppid"], "gpid", r["godot_pid"], flush=True)

(ROOT / "author-arms-results.json").write_text(json.dumps(res, indent=2) + "\n")
print("wrote author-arms-results.json")
