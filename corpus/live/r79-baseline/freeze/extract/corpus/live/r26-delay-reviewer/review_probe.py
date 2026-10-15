import json, subprocess, time, hashlib, pathlib
root=pathlib.Path(__file__).parent / "project"
script=root/"timeout_probe.gd"
cmd=["godot","--headless","--path",str(root),"--script","res://timeout_probe.gd","--"]
marker="TIMEOUT_PROBE: expected signature"
def attempt(label, timeout, hold=False):
    c=cmd + (["--hold-open"] if hold else [])
    started=time.monotonic()
    p=subprocess.Popen(c,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
    try:
        out,err=p.communicate(timeout=timeout)
        ended=time.monotonic()
        return {"arm":label,"command":c,"timeout_seconds":timeout,"elapsed_seconds":ended-started,"timed_out":False,"actual_exit":p.returncode,"marker_observed":marker in out+err,"pre_marker_observed":"TIMEOUT_PROBE: pre-delay" in out+err,"raw_stdout":out,"raw_stderr":err,"direct_child_alive_after_cleanup":False,"classification":p.returncode==0 and marker in out+err}
    except subprocess.TimeoutExpired as e:
        out=e.stdout.decode(errors="replace") if isinstance(e.stdout,bytes) else (e.stdout or "")
        err=e.stderr.decode(errors="replace") if isinstance(e.stderr,bytes) else (e.stderr or "")
        alive=p.poll() is None
        if alive: p.kill()
        try:
            more_out,more_err=p.communicate(timeout=3)
            out += more_out or ""; err += more_err or ""
            cleanup_error=None
        except subprocess.TimeoutExpired:
            cleanup_error="direct child cleanup timeout"
        return {"arm":label,"command":c,"timeout_seconds":timeout,"elapsed_seconds":time.monotonic()-started,"timed_out":True,"actual_exit":p.returncode,"marker_observed":marker in out+err,"pre_marker_observed":"TIMEOUT_PROBE: pre-delay" in out+err,"raw_stdout":out,"raw_stderr":err,"process_was_running":alive,"direct_child_alive_after_cleanup":p.poll() is None,"cleanup_error":cleanup_error,"classification":False}
results=[attempt("old-bound-delayed-valid",.75),attempt("new-bound-delayed-valid",3.0),attempt("new-bound-hold-open",3.0,True)]
payload={"script_sha256":hashlib.sha256(script.read_bytes()).hexdigest(),"results":results}
(pathlib.Path(__file__).parent/"r26-delay-results.json").write_text(json.dumps(payload,indent=2)+"\n")
print(json.dumps([{k:v for k,v in r.items() if k not in ("raw_stdout","raw_stderr")} for r in results],indent=2))
