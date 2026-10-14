import subprocess,signal,json,time,threading
p=subprocess.Popen(["godot","--headless","--path",r"/home/vgpnk/Projects/prymeagnt/game-dev-2d/.shokunin/game-dev-2d/corpus/live/r21-signal-reviewer-scratch","--script","res://signal_probe.gd"],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
started=time.monotonic(); lines=[]
def read():
    for line in p.stdout:
        lines.append(line.rstrip())
t=threading.Thread(target=read,daemon=True); t.start()
deadline=time.monotonic()+5
while time.monotonic()<deadline and "SIGNAL_REVIEW_SIGNATURE" not in lines and p.poll() is None: time.sleep(.01)
observed=("SIGNAL_REVIEW_SIGNATURE" in lines and p.poll() is None)
print("OBS",json.dumps({"lines":lines,"pid":p.pid,"poll_before_signal":p.poll(),"running_after_signature":observed}),flush=True)
p.send_signal(signal.SIGTERM)
try: p.wait(timeout=5)
except subprocess.TimeoutExpired: p.kill(); p.wait()
print("RESULT",json.dumps({"returncode":p.returncode,"signal":-p.returncode if p.returncode<0 else None,"elapsed":time.monotonic()-started,"stdout":lines}),flush=True)
