from pathlib import Path
HEAD=Path("corpus/fixtures/run_battery.py"); MUT=Path("/var/tmp/r104-w4/verify_mut.py")
def slice_paren(src, key):
    i=src.index('"%s": (' % key); depth=0; j=i
    while True:
        ch=src[j]
        if ch=='(': depth+=1
        elif ch==')':
            depth-=1
            if depth==0: break
        j+=1
    return src[i:j+1]
def gate(path, keys):
    src=path.read_text()
    body="def G(CASES, results):\n    return ("+slice_paren(src,"cases_integrity")+")"
    for k in keys:
        body+="\nG0=G\n_dummy=0"
    # simpler: build conjunction
    parts=[slice_paren(src,"cases_integrity")]
    for k in keys: parts.append(slice_paren(src,k))
    # strip the leading "key": and unwrap
    exprs=[]
    for p in parts:
        e=p.split(":",1)[1].strip()
        if e.startswith("(") and e.endswith(")"): e=e[1:-1]
        exprs.append(e)
    body="def G(CASES, results):\n    return (" + ") and (".join(exprs) + ")"
    ns={}; exec(body,ns); return ns["G"]
import importlib.util
def load(p,n):
    s=importlib.util.spec_from_file_location(n,p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
head=load(HEAD,"h")
HEAD_G=gate(HEAD,[])
MUT_G=gate(MUT,["r104_res_uid_count_floor","r104_export_prod_count_floor"])
CASES=head.CASES
full=[{"case":c[0],"verdict":"PASS"} for c in CASES]
RES=[("res_uid_s01_idpath",),("res_uid_s02_reuse",),("res_uid_s04_classes",)]
C2=CASES+[(c[0],"x.gd",[],0,"p") for c in RES]
R2=full+[{"case":c[0],"verdict":"PASS"} for c in RES]
scen=[("A current reality (no res_uid_ rows)",CASES,full),
 ("B res_uid_ rows landed + present",C2,R2),
 ("C res_uid_ rows landed, results DROPPED",C2,full),
 ("D sync-drop 1 res_uid_ CASES+results",[c for c in C2 if c[0]!="res_uid_s02_reuse"],[r for r in R2 if r["case"]!="res_uid_s02_reuse"]),
 ("E ALL res_uid_ sync-dropped",CASES,full),
 ("F sync-drop 1 export_prod_ CASES+results",[c for c in CASES if c[0]!="export_prod_base_pck"],[r for r in full if r["case"]!="export_prod_base_pck"]),
 ("G ALL export_prod_ sync-dropped",[c for c in CASES if not c[0].startswith("export_prod_")],[r for r in full if not r["case"].startswith("export_prod_")]),
 ("H export_prod_ CASES dropped, results kept",[c for c in CASES if c[0]!="export_prod_base_pck"],full),
]
print(f"{'scenario':48s} {'HEAD':>6s} {'PATCHED':>8s}")
for l,C,R in scen: print(f"{l:48s} {str(HEAD_G(C,R)):>6s} {str(MUT_G(C,R)):>8s}")
