#!/usr/bin/env python3
"""Run fp probes in the battery's exact shape: subprocess.run + classify_process."""
import ast, subprocess, pathlib, json
REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
src = (REPO/"corpus/fixtures/run_battery.py").read_text()
for node in ast.walk(ast.parse(src)):
    if isinstance(node, ast.FunctionDef) and node.name=="classify_process":
        ns={}; exec("def classify_process"+ast.get_source_segment(src,node).split("def classify_process",1)[1],ns); cls=ns["classify_process"]

SIG='R89 lineempty call=offset_polyline(empty,2.0,JOIN_ROUND,END_JOINED)'
out={}
for probe in ("fp_wrongcause","fp_stderr_sig"):
    p=subprocess.run(["godot","--headless","--path","proj","--script",f"res://{probe}.gd"],
                     capture_output=True,text=True,timeout=30)
    output=p.stdout+p.stderr          # == run_process
    verdict=cls(p.returncode,None,output,-6,SIG,())
    out[probe]={"rc":p.returncode,"stderr_bytes":len(p.stderr),"verdict":"PASS" if verdict else "FAIL",
               "sig_in_stdout":SIG in p.stdout,"sig_in_stderr":SIG in p.stderr}
    pathlib.Path(f"runs/subprocess_{probe}.out").write_text(p.stdout)
    pathlib.Path(f"runs/subprocess_{probe}.err").write_text(p.stderr)
    pathlib.Path(f"runs/subprocess_{probe}.rc").write_text(str(p.returncode))
# control: the real arm, same shape
p=subprocess.run(["godot","--headless","--path","proj","--script","res://geo2d_lattice.gd","--","--arm=lineempty"],
                 capture_output=True,text=True,timeout=30)
out["real_lineempty"]={"rc":p.returncode,"stderr_bytes":len(p.stderr),
    "verdict":"PASS" if cls(p.returncode,None,p.stdout+p.stderr,-6,SIG,()) else "FAIL",
    "sig_in_stdout":SIG in p.stdout,"sig_in_stderr":SIG in p.stderr}
pathlib.Path("runs/fp_battery_shape.json").write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps(out,indent=2))
