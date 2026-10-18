import json, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor

ROOT = '/var/tmp/r101-simp3'

def run_one(tree, row, timeout=25):
    name, script, flags = row
    cmd = ['godot', '--headless', '--path', tree, '--script', 'res://' + script, '--', *flags]
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        rc, out, err, to = p.returncode, p.stdout, p.stderr, False
    except subprocess.TimeoutExpired as e:
        rc, to = None, True
        out = (e.stdout or b'').decode(errors='replace') if isinstance(e.stdout, bytes) else (e.stdout or '')
        err = (e.stderr or b'').decode(errors='replace') if isinstance(e.stderr, bytes) else (e.stderr or '')
    return {'name': name, 'script': script, 'flags': flags, 'tree': tree, 'command': cmd,
            'rc': rc, 'timeout': to, 'stdout': out, 'stderr': err,
            'elapsed': round(time.time() - t0, 3)}

def main():
    tree, tag, rowsfile = sys.argv[1], sys.argv[2], sys.argv[3]
    jobs = int(sys.argv[4]) if len(sys.argv) > 4 else 6
    rows = [tuple(r) for r in json.load(open(rowsfile))]
    out_path = f'{ROOT}/runs/{tag}.jsonl'
    with ThreadPoolExecutor(max_workers=jobs) as ex:
        results = list(ex.map(lambda r: run_one(tree, r), rows))
    with open(out_path, 'w') as fh:
        for rec in results:
            fh.write(json.dumps(rec) + '\n')
    to = [r['name'] for r in results if r['timeout']]
    print(f"{tag}: {len(results)} rows -> {out_path}; timeouts={to}")

main()
