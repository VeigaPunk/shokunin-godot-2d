#!/usr/bin/env python3
"""r103-S2: apply the r100-simplifier SP2+SP3 fold to r100b_seq.gd (in place).

Re-derived from reports/round-100/r100-simplifier.md §3/§5 (the named patch of
record corpus/live/r100-simplifier/r100-simplifier-fold-9ede7c50.patch is absent
from the tree — see reports/round-102/r102-S0.md §7). Three exact-string edits,
each asserted to occur exactly once:

  SP2  delete the 3-line dead `--arm=` parse in `_initialize`
  SP3a delete `var arm := ""` (decl)
  SP3b collapse `arm = a` + `match arm:` -> `match a:`

Total: -5 lines. Expected folded sha256 prefix e77dc55c (r100-simplifier §5).
"""
import hashlib
import sys


def must_replace_once(text, old, new, label):
    n = text.count(old)
    assert n == 1, f"{label}: expected 1 occurrence, found {n}"
    return text.replace(old, new, 1)


def main(path):
    text = open(path).read()
    before = hashlib.sha256(text.encode()).hexdigest()

    text = must_replace_once(
        text,
        'func _initialize() -> void:\n'
        '\tfor a in OS.get_cmdline_user_args():\n'
        '\t\tif a.begins_with("--arm="):\n'
        '\t\t\tarm = a.substr(6)\n'
        '\tcall_deferred("_run")\n',
        'func _initialize() -> void:\n'
        '\tcall_deferred("_run")\n',
        "SP2",
    )
    text = must_replace_once(text, 'var arm := ""\n', '', "SP3a")
    text = must_replace_once(text, '\t\tarm = a\n\t\tmatch arm:\n', '\t\tmatch a:\n', "SP3b")

    open(path, "w").write(text)
    after = hashlib.sha256(text.encode()).hexdigest()
    print(f"{path}\n  before {before}\n  after  {after}\n  lines {len(text.splitlines())}")


if __name__ == "__main__":
    main(sys.argv[1])
