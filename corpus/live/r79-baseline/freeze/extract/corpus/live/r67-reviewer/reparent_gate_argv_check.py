import re, subprocess
old = subprocess.run(["git","show","cb84d0a^:corpus/fixtures/descendant_pipe_probe.gd"],capture_output=True,text=True).stdout
new = subprocess.run(["git","show","HEAD:corpus/fixtures/descendant_pipe_probe.gd"],capture_output=True,text=True).stdout
PID = "424242"

def consts(text):
    return {m.group(1): m.group(2).encode().decode("unicode_escape")
            for m in re.finditer(r'const (\w+) := "((?:[^"\\]|\\.)*)"', text)}

def eval_expr(expr, C, gate=None):
    """Evaluate GDScript string concat: literals, CONST names, str(pid), reparent_gate, vars as symbols."""
    out, tokens = "", []
    for mm in re.finditer(r'"((?:[^"\\]|\\.)*)"|str\(OS\.get_process_id\(\)\)|reparent_gate|\b[A-Z][A-Z_]+\b|\b(tail|err_tail)\b', expr):
        tok = mm.group(0)
        if tok == "str(OS.get_process_id())": tokens.append(PID)
        elif tok == "reparent_gate": tokens.append(gate)
        elif mm.group(1) is not None: tokens.append(mm.group(1).encode().decode("unicode_escape"))
        elif tok in ("tail","err_tail"): tokens.append("{"+tok+"}")
        elif tok in C: tokens.append(C[tok])
        else: tokens.append("{"+tok+"?}")
    return "".join(tokens)

Co, Cn = consts(old), consts(new)
gm = re.search(r'var reparent_gate := \((.*?)\)\n', new, re.S)
gate = eval_expr(gm.group(1), Cn)
print("GATE:", repr(gate))

def arm_exprs(text):
    return re.findall(r'spawned = OS\.create_process\("/usr/bin/sh", PackedStringArray\(\["-c",\s*\n\s*(.*?)\]\)\)', text, re.S)

oe, ne = arm_exprs(old), arm_exprs(new)
# gated pre-existing arms: old 0(spawn-hold),2(forge),3(errforge) vs new same idx
for i,(o,n) in enumerate(zip(oe,ne)):
    ov, nv = eval_expr(o,Co), eval_expr(n,Cn,gate)
    print(f"arm{i} identical={ov==nv}")
    if ov != nv:
        print(" OLD:",repr(ov)); print(" NEW:",repr(nv))
# tail vars: forge tail := "; sleep 6" if forge_hold else ""; err_tail likewise
# check the tail expansions explicitly
for name, expr_old, expr_new in [("forge",oe[2],ne[2]),("errforge",oe[3],ne[3])]:
    for tailval in ('"; sleep 6"','""'):
        tv = tailval.strip('"').encode().decode("unicode_escape")
        o = eval_expr(expr_old,Co).replace("{tail}",tv).replace("{err_tail}",tv)
        n = eval_expr(expr_new,Cn,gate).replace("{tail}",tv).replace("{err_tail}",tv)
        print(name, "tail",repr(tv),"identical:",o==n)
# new gated arms argv
for i in (4,5,6):
    print("new-arm%d:"%i, repr(eval_expr(ne[i],Cn,gate)))
print("midline(no gate):", repr(eval_expr(ne[7],Cn)))
