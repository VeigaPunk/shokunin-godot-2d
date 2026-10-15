import hashlib, os, sys
from pathlib import Path

for d in sys.argv[1:]:
    root = Path(d)
    man = root / "manifest.sha256"
    entries = {}
    for line in man.read_text().splitlines():
        line = line.strip()
        if not line: continue
        h, _, p = line.partition("  ")
        if not p:
            h, _, p = line.partition(" *")
        p = p.lstrip("./")
        entries[p] = h
    files = set()
    for dirpath, dirnames, filenames in os.walk(root):
        for f in filenames:
            rel = os.path.relpath(os.path.join(dirpath, f), root)
            files.add(rel)
    self_listed = "manifest.sha256" in entries
    missing = sorted(files - set(entries))          # on disk, not in manifest
    extra   = sorted(set(entries) - files)          # in manifest, not on disk
    print(f"== {d}")
    print(f"   manifest entries={len(entries)}  files_on_disk={len(files)}  self_listed={self_listed}")
    print(f"   on_disk_not_in_manifest={len(missing)} {missing[:8]}")
    print(f"   in_manifest_not_on_disk={len(extra)} {extra[:8]}")
