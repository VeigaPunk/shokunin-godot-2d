#!/usr/bin/env python3
"""r102-mut9 — seqfull-style contiguity attack against ONE planned export_launch row.

Target row model: r102-E2's planned `export_launch_s02` contract — an
embed_pck=true self-contained Linux/X11 binary launched headless with
`--quit-after 5`, stdout carrying the r101-measured marker
`EXPORT_LAUNCH_READY scene=fixture` plus `FRAME 1..5`; row receipt in the
export_prod single-line idiom with the tokens `frames=[1,2,3,4,5]` and
`extra=false`.

Attack (seqfull m_seq shape: a foreign stdout line inside the expected span):
  A1  foreign print between FRAME 2 and FRAME 3   (in-span)
  A2  foreign print after FRAME 5                 (post-span, same process tail)
  A3  foreign print before the marker             (pre-span ceiling)
Each variant is a real edit of the launched project's scene script, re-exported
with the real templates, launched twice (byte-determinism check). All verdicts
are computed from captured stdout/stderr bytes. After the model matrix, the same
in-span attack is re-run against the landed `corpus/fixtures/export_launch_s02.gd`
(read-only; mutant = scratch copy with the foreign print injected into its own
MAIN_GD constant) so the model verdict is checked against the real artifact.
No corpus fixture is edited, and run_battery.py is never executed.

Scratch only: /var/tmp/r102-w8/ (projects, logs, binaries). Exports run under
`unshare -m --map-root-user` with a private tmpfs /tmp (r101-E0 measured the
host /tmp EDQUOT hazard for the packer's fixed /tmp/tmpproject.binary-* path).
"""
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import time
from pathlib import Path

SCRATCH = Path("/var/tmp/r102-w8")
GODOT = "/usr/bin/godot"
QUIT_AFTER = 5
MARKER = "EXPORT_LAUNCH_READY scene=fixture"
FRAME_RE = re.compile(r"^FRAME (\d+)$")
VARIANTS = ("base", "A1", "A2", "A3")
CORPUS_S02 = (Path(__file__).resolve().parents[3]
              / "corpus" / "fixtures" / "export_launch_s02.gd")

PROJECT_GODOT = """[application]
config/name="R102W8Launch"
config/features=PackedStringArray("4.7")
run/main_scene="res://launch.tscn"
"""

LAUNCH_TSCN = """[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="res://launch.gd" id="1"]

[node name="ExportLaunch" type="Node"]
script = ExtResource("1")
"""

PRESETS = """[preset.0]

name="Linux/X11"
platform="Linux/X11"
runnable=true
advanced_options=false
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path=""

[preset.0.options]

binary_format/architecture="x86_64"
binary_format/embed_pck=true
"""


def launch_gd(inject):
    body = ["extends Node", "", "var _n := 0", "", "",
            "func _ready() -> void:"]
    if inject == "A3":
        body.append('\tprint("FOREIGN_EXTRA injected=pre_span")')
    body.append('\tprint("EXPORT_LAUNCH_READY scene=fixture")')
    body += ["", "", "func _process(_delta: float) -> void:",
             "\t_n += 1",
             '\tprint("FRAME %d" % _n)']
    if inject == "A1":
        body += ["\tif _n == 2:",
                 '\t\tprint("FOREIGN_EXTRA injected=into_span")']
    if inject == "A2":
        body += ["\tif _n == 5:",
                 '\t\tprint("FOREIGN_EXTRA injected=post_span")']
    return "\n".join(body) + "\n"


def build(name, inject):
    proj = SCRATCH / name
    if proj.exists():
        shutil.rmtree(proj)
    (proj / "out").mkdir(parents=True)
    (proj / "project.godot").write_text(PROJECT_GODOT)
    (proj / "launch.tscn").write_text(LAUNCH_TSCN)
    (proj / "launch.gd").write_text(launch_gd(inject))
    (proj / "export_presets.cfg").write_text(PRESETS)
    return proj


def export(proj):
    exe = proj / "out" / "launch.x86_64"
    inner = ('mount -t tmpfs tmpfs /tmp && exec godot --headless --path %s '
             '--export-debug "Linux/X11" %s'
             % (shlex.quote(str(proj)), shlex.quote(str(exe))))
    cmd = ["unshare", "-m", "--map-root-user", "sh", "-c", inner]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return {"cmd": cmd, "exit": p.returncode,
            "binary": str(exe), "binary_size": exe.stat().st_size if exe.is_file() else 0,
            "binary_sha256": hashlib.sha256(exe.read_bytes()).hexdigest() if exe.is_file() else None,
            "log_tail": (p.stdout + p.stderr).strip().splitlines()[-3:]}


def launch(proj):
    exe = proj / "out" / "launch.x86_64"
    runs = []
    for _ in range(2):
        p = subprocess.run([str(exe), "--headless", "--quit-after", str(QUIT_AFTER)],
                           cwd=str(proj / "out"), capture_output=True, timeout=20)
        runs.append({"exit": p.returncode, "stdout": p.stdout, "stderr": p.stderr})
    det = runs[0]["stdout"] == runs[1]["stdout"] and runs[0]["stderr"] == runs[1]["stderr"]
    return runs, det


def tail_window(text):
    ls = text.splitlines()
    i = ls.index(MARKER)
    return [l for l in ls[i:] if l.strip()]


def evaluate(merged):
    ls = merged.splitlines()
    frames = [int(FRAME_RE.match(l).group(1)) for l in ls if FRAME_RE.match(l)]
    win = tail_window(merged)
    expected = [MARKER] + ["FRAME %d" % n for n in range(1, QUIT_AFTER + 1)]
    foreign = [l for l in win if l != MARKER and not FRAME_RE.match(l)]
    span_sig = "\n".join(expected)
    return {
        "frames": frames,
        "foreign_lines_in_tail_window": foreign,
        "extra_naive": frames != list(range(1, QUIT_AFTER + 1)),
        "extra_honest": bool(foreign),
        "stdout_nonempty_lines": len([l for l in merged.splitlines() if l.strip()]),
        "pin_marker_presence": MARKER in merged,
        "pin_span_contiguous": span_sig in merged,
        "digest_expected_only": hashlib.sha256(span_sig.encode()).hexdigest(),
        "digest_tail_window_raw": hashlib.sha256("\n".join(win).encode()).hexdigest(),
    }


def attack_landed_fixture(out):
    """Re-run the in-span attack against the landed r102 export_launch_s02.gd.

    Corpus fixture is read read-only; the mutant is a scratch copy whose own
    MAIN_GD constant (embedded scratch project) gets the foreign print between
    frames 2 and 3. The fixture derives its `extra` token as frame-vector
    inequality, which the model matrix measured to be invariant under in-span
    injection; the observed receipts below decide whether that hole is real.
    """
    if not CORPUS_S02.is_file():
        out["landed_fixture"] = {"status": "corpus fixture absent at probe time"}
        return
    src = CORPUS_S02.read_text()
    out["landed_fixture"] = {"fixture": str(CORPUS_S02),
                             "fixture_sha256": hashlib.sha256(src.encode()).hexdigest()}
    anchor = r'\tprint(\"LAUNCH_S02_FRAME %d\" % frames)\n'
    if src.count(anchor) != 1:
        out["landed_fixture"]["status"] = "anchor not unique; mutant not built"
        return
    foreign = r'\tif frames == 2:\n\t\tprint(\"FOREIGN_EXTRA injected=into_span\")\n'
    mutant = src.replace(anchor, anchor + foreign, 1)
    fx = SCRATCH / "fx"
    proj = fx / "proj"
    if fx.exists():
        shutil.rmtree(fx)
    proj.mkdir(parents=True)
    (proj / "project.godot").write_text('[application]\nconfig/name="MechanicOneShotTest"\n'
                                        'config/features=PackedStringArray("4.7")\n')
    (proj / "export_launch_s02.gd").write_text(src)
    (proj / "mut_s02.gd").write_text(mutant)

    def run_fixture(script, root_name):
        root = fx / root_name
        env = dict(os.environ, EXPORT_LAUNCH_ROOT=str(root))
        cmd = [GODOT, "--headless", "--path", str(proj), "--script", "res://" + script,
               "--", "--arm=embed"]
        t0 = time.monotonic()
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=180, env=env)
        run_log = root / "embed" / "logs" / "run.log"
        log = run_log.read_text() if run_log.is_file() else ""
        return {"cmd": cmd, "exit": p.returncode, "seconds": round(time.monotonic() - t0, 2),
                "pass_lines": [l for l in p.stdout.splitlines()
                               if l.startswith("PASS export_launch s02 ")],
                "fail_lines": [l for l in p.stdout.splitlines()
                               if l.startswith("FAIL export_launch s02 ")],
                "stderr_tail": p.stderr.strip().splitlines()[-4:],
                "foreign_in_run_log": "FOREIGN_EXTRA" in log,
                "run_log_span": [l for l in log.splitlines()
                                 if l.startswith(("LAUNCH_S02_", "FOREIGN_EXTRA"))]}

    pristine = run_fixture("export_launch_s02.gd", "root-pristine")
    attacked = run_fixture("mut_s02.gd", "root-mutant")

    def pinned(line):
        cut = line.find(" exit=")
        return line[:cut + len(" exit=0")] if cut >= 0 else line

    out["landed_fixture"].update({
        "pristine": pristine, "attacked": attacked,
        "pinned_region_identical": bool(pristine["pass_lines"] and attacked["pass_lines"])
        and pinned(pristine["pass_lines"][0]) == pinned(attacked["pass_lines"][0]),
        "attack_lands": (not attacked["fail_lines"] and attacked["foreign_in_run_log"]
                         and not pristine["foreign_in_run_log"]),
    })


def main():
    out = {"engine": subprocess.run([GODOT, "--version"], capture_output=True,
                                    text=True).stdout.strip(),
           "quit_after": QUIT_AFTER, "marker": MARKER, "variants": {}}
    base_digest_expected = base_digest_raw = None
    base_stdout_sha = base_count = None
    for name in VARIANTS:
        inject = None if name == "base" else name
        proj = build(name, inject)
        exp = export(proj)
        runs, det = launch(proj)
        raw_out, raw_err = runs[0]["stdout"], runs[0]["stderr"]
        merged = raw_out.decode(errors="replace") + raw_err.decode(errors="replace")
        ev = evaluate(merged)
        rec = {
            "inject": inject, "export": exp, "launch_exit": runs[0]["exit"],
            "deterministic_two_runs": det,
            "stdout_sha256": hashlib.sha256(raw_out).hexdigest(),
            "stderr_sha256": hashlib.sha256(raw_err).hexdigest(),
            "stdout_text": raw_out.decode(errors="replace").splitlines(),
            "stderr_text": raw_err.decode(errors="replace").splitlines(),
            **ev,
        }
        rec["receipt_naive"] = ("PASS export_launch s02 marker=ok frames=[%s] extra=%s exit=%d"
                                % (",".join(map(str, ev["frames"])),
                                   "true" if ev["extra_naive"] else "false", runs[0]["exit"]))
        rec["receipt_honest"] = ("PASS export_launch s02 marker=ok frames=[%s] extra=%s exit=%d"
                                 % (",".join(map(str, ev["frames"])),
                                    "true" if ev["extra_honest"] else "false", runs[0]["exit"]))
        out["variants"][name] = rec
        if name == "base":
            base_digest_expected = ev["digest_expected_only"]
            base_digest_raw = ev["digest_tail_window_raw"]
            base_stdout_sha = rec["stdout_sha256"]
            base_count = ev["stdout_nonempty_lines"]

    # Row-level verdicts, pinned against baseline-token values (attack lands iff
    # the receipt the fixture would derive still carries the baseline tokens).
    for name, rec in out["variants"].items():
        rec["row_verdict"] = {
            "pin_marker_only": rec["pin_marker_presence"],
            "pin_frames_vector_substring": "frames=[1,2,3,4,5]" in rec["receipt_naive"],
            "pin_receipt_naive_extra_false": "extra=false" in rec["receipt_naive"],
            "pin_receipt_honest_extra_false": "extra=false" in rec["receipt_honest"],
            "pin_span_contiguous": rec["pin_span_contiguous"],
            "pin_digest_expected_only_matches_base": rec["digest_expected_only"] == base_digest_expected,
            "pin_digest_tail_window_matches_base": rec["digest_tail_window_raw"] == base_digest_raw,
            "pin_stdout_bytes_sha256_matches_base": rec["stdout_sha256"] == base_stdout_sha,
            "pin_stdout_nonempty_count_matches_base": rec["stdout_nonempty_lines"] == base_count,
        }
    attack_landed_fixture(out)
    payload = Path(__file__).resolve().parent / "mut09_export_launch_span_attack.json"
    payload.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({n: out["variants"][n]["row_verdict"] for n in VARIANTS}, indent=1))
    for n in VARIANTS:
        r = out["variants"][n]
        print(n, "rc=%s det=%s" % (r["launch_exit"], r["deterministic_two_runs"]),
              "stdout=", r["stdout_text"])
    lf = out["landed_fixture"]
    print("landed_fixture:", lf.get("fixture_sha256", lf.get("status")),
          "| pristine:", lf.get("pristine", {}).get("pass_lines"),
          "| attacked:", lf.get("attacked", {}).get("pass_lines"),
          "| foreign_ran:", lf.get("attacked", {}).get("foreign_in_run_log"),
          "| pinned_identical:", lf.get("pinned_region_identical"),
          "| attack_lands:", lf.get("attack_lands"))
    print("wrote", payload)


if __name__ == "__main__":
    main()
