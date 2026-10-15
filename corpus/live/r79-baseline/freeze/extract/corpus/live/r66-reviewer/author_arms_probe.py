#!/usr/bin/env python3
"""r66 reviewer: execute the author's IN-FLIGHT new fixture arms through the
verbatim production classifier — direct review of the uncommitted diff.

run_process/classify_process are ast-extracted from the *modified worktree*
run_battery.py (sha 065d0e31 at measurement) — the +2 hunk doesn't touch
either function, so these are the same bytes as the verified cd4824cc blob.

Arms (author's diff, descendant_pipe_probe.gd worktree sha 9ff5a9ae):
  --spawn-allowforge   post-death echo of save_corrupt_negative's allowlist
                       -> rejects without allowlist, admits with it
  --spawn-splitforge   post-death 'ERR\n' + 'OR: ...' -> evades line scan
  --spawn-seamforge    unterminated '...ends in ERROR' stdout tail +
                       ': phantom...' stderr head -> concat fabricates a
                       reject line present in neither stream
  --spawn-midlineforge pre-death splice into signature halves -> dual-clause
                       corruption (sig destroyed AND ERROR: fabricated)
"""
import ast, hashlib, json, shutil, subprocess, time
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
RUNNER = REPO / "corpus/fixtures/run_battery.py"
FIX = REPO / "corpus/fixtures/descendant_pipe_probe.gd"
SCRATCH = REPO / "corpus/live/r66-reviewer"
PROJ = SCRATCH / "proj_author_diff"
MARKER = "DESCENDANT_PIPE_PROBE: expected signature"
SAVE_ALLOW = "ERROR: SAVE EXPECTED NEGATIVE: malformed JSON rejected signature=JSON_PARSE_ERROR"

src = RUNNER.read_text()
ns = {"subprocess": subprocess, "re": __import__("re")}
for node in ast.walk(ast.parse(src)):
    if isinstance(node, ast.FunctionDef) and node.name in ("run_process", "classify_process"):
        exec(ast.get_source_segment(src, node), ns)

if PROJ.exists():
    shutil.rmtree(PROJ)
PROJ.mkdir(parents=True)
shutil.copy2(FIX, PROJ / "descendant_pipe_probe.gd")
(PROJ / "project.godot").write_text('[application]\nconfig/name="MechanicOneShotTest"\nconfig/features=PackedStringArray("4.7")\n')

OUT = {"runner_sha256": hashlib.sha256(RUNNER.read_bytes()).hexdigest(),
       "fixture_sha256": hashlib.sha256(FIX.read_bytes()).hexdigest()}


def run(arm, allowed=(), bound=12.0):
    cmd = ["/usr/bin/godot", "--headless", "--path", str(PROJ),
           "--script", "res://descendant_pipe_probe.gd", "--", arm]
    t0 = time.monotonic()
    output, code, error = ns["run_process"](cmd, bound)
    return {"arm": arm, "elapsed": round(time.monotonic() - t0, 3),
            "exit": code, "error": error,
            "classification": ns["classify_process"](code, error, output, 0, MARKER, allowed),
            "marker_whole_present": MARKER in output,
            "error_lines": [ln for ln in output.splitlines() if "ERROR:" in ln],
            "tail_lines": output.splitlines()[-8:],
            "raw_tail_bytes": output[-260:]}


OUT["allowforge"] = run("--spawn-allowforge")
OUT["allowforge_with_save_allowlist"] = {
    **OUT["allowforge"],
    "classification": ns["classify_process"](
        OUT["allowforge"]["exit"], OUT["allowforge"]["error"],
        "\n".join(OUT["allowforge"]["tail_lines"]) if False else
        "\n".join(OUT["allowforge"]["raw_tail_bytes"].split("\n")), 0, MARKER, ())}
# classify needs the FULL output, not the tail — re-run classify on stored bytes:
# (kept simple: reclassify from the raw record via stored fields is impossible;
#  capture full output below instead.)
OUT.pop("allowforge_with_save_allowlist")

def run_full(arm, allowed=(), bound=12.0):
    cmd = ["/usr/bin/godot", "--headless", "--path", str(PROJ),
           "--script", "res://descendant_pipe_probe.gd", "--", arm]
    t0 = time.monotonic()
    output, code, error = ns["run_process"](cmd, bound)
    return {"arm": arm, "allowed": list(allowed),
            "elapsed": round(time.monotonic() - t0, 3),
            "exit": code, "error": error,
            "classification": ns["classify_process"](code, error, output, 0, MARKER, allowed),
            "marker_whole_present": MARKER in output,
            "error_lines": [ln for ln in output.splitlines() if "ERROR:" in ln],
            "all_lines": output.splitlines()}

OUT["allowforge_full_no_allowlist"] = run_full("--spawn-allowforge")
OUT["allowforge_full_with_allowlist"] = run_full("--spawn-allowforge", (SAVE_ALLOW,))
OUT["splitforge_full"] = run_full("--spawn-splitforge")
OUT["seamforge_full"] = run_full("--spawn-seamforge")
OUT["midlineforge_full"] = run_full("--spawn-midlineforge", bound=14.0)
OUT["stock_release_control"] = run_full("--spawn-errforge-release")

checks = {
    "allowforge_rejects_without": OUT["allowforge_full_no_allowlist"]["classification"] is False,
    "allowforge_admits_with": OUT["allowforge_full_with_allowlist"]["classification"] is True,
    "splitforge_evades": (OUT["splitforge_full"]["classification"] is True
                          and not OUT["splitforge_full"]["error_lines"]),
    "seamforge_fabricates": (OUT["seamforge_full"]["classification"] is False
                             and any("SEAMFORGE tail ends in ERROR: SEAMFORGE" in ln
                                     for ln in OUT["seamforge_full"]["error_lines"])),
    "midlineforge_corrupts_both": (OUT["midlineforge_full"]["classification"] is False
                                   and OUT["midlineforge_full"]["marker_whole_present"] is False
                                   and OUT["midlineforge_full"]["error_lines"]),
    "stock_release_detected": OUT["stock_release_control"]["classification"] is False,
}
OUT["checks"] = checks
(SCRATCH / "author-arms.json").write_text(json.dumps(OUT, indent=2, default=str))
print(json.dumps(checks, indent=2))
print("AUTHOR_ARMS_BEHAVE_AS_DECLARED" if all(checks.values()) else "ARM_MISMATCH")
