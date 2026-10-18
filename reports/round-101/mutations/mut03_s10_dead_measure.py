#!/usr/bin/env python3
"""MUT-3 stage 2: dead measure applied to the real landed C1 fixture
`corpus/fixtures/export_prod_s10.gd` (icon/uid census row, E10).

Variants generated from the landed source (read-only) into /tmp/r101-mut03/proj/:

  s10_pristine          baseline control, only SCRATCH_ROOT redirected.
  s10_control_tampered  + injected corruption of one packed-body byte after the
                        export (negative environment). All checks intact.
  s10_dead_tampered     same tamper, plus the mut03 dead measure: `_check` and
                        `_fail` keep printing their receipt rows but the verdict
                        no longer gates anything (failure swallowed).

Measured: does the dead variant still print the pristine PASS receipt and exit 0
on a corrupted artifact while the honest control rejects it?  A Python PCK
recompute (md5 per entry, same rule the fixture itself uses) shows the corruption
is byte-detectable, i.e. an external recompute kills the mutant.

Usage: python3 mut03_s10_dead_measure.py    (exit 0 = model matched)
Scratch only; never runs run_battery.py, never edits corpus/fixtures.
"""
import hashlib
import pathlib
import re
import shlex
import subprocess
import sys

GODOT = "/usr/bin/godot"
ROOT = pathlib.Path("/tmp/r101-mut03")
PROJ = ROOT / "proj"
EVID = ROOT / "evidence"
SRC = pathlib.Path("corpus/fixtures/export_prod_s10.gd")
S10_ROOT = "/tmp/r101-mut03/s10"
PCK = pathlib.Path(S10_ROOT) / "s10" / "out" / "game.pck"

TAMPER = (
    "\t# mut03 tamper injection (negative environment: flip one packed-body byte)\n"
    "\tvar _tam := FileAccess.get_file_as_bytes(OUT_PCK)\n"
    "\tvar _fb := int(_tam.decode_u64(24))\n"
    "\tif _fb > 0 and _fb < _tam.size():\n"
    "\t\t_tam[_fb] = _tam[_fb] ^ 0xFF\n"
    "\tvar _tw := FileAccess.open(OUT_PCK, FileAccess.WRITE)\n"
    "\t_tw.store_buffer(_tam)\n"
    "\t_tw.close()\n"
)
ANCHOR = "\tvar exported := _export(exe)\n"

CHECK_OLD = (
    "func _check(cond: bool, name: String, detail: String) -> void:\n"
    "\tif cond:\n"
    "\t\t_row(\"ok \" + name, detail)\n"
    "\telse:\n"
    "\t\t_fail(name, detail)\n"
)
CHECK_DEAD = (
    "func _check(cond: bool, name: String, detail: String) -> void:\n"
    "\t# mut03 dead measure: verdict dropped, receipt kept\n"
    "\t_row(\"ok \" + name, detail)\n"
)
FAIL_OLD = (
    "func _fail(name: String, detail: String) -> void:\n"
    "\t_fails.append(\"%s: %s\" % [name, detail])\n"
    "\tprint(\"FAIL %s = %s\" % [name, detail])\n"
)
FAIL_DEAD = (
    "func _fail(name: String, detail: String) -> void:\n"
    "\t# mut03 dead measure: failure swallowed, receipt kept\n"
    "\t_row(\"ok \" + name, detail)\n"
)

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def build_variants():
    src = SRC.read_text()
    print(f"MUT03-S10 SOURCE {SRC} bytes={len(src.encode())} sha256={hashlib.sha256(src.encode()).hexdigest()}")
    guard = 'const SCRATCH_ROOT := "/tmp/r101-E10"'
    assert src.count(guard) == 1 and src.count(ANCHOR) == 1
    base = src.replace(guard, f'const SCRATCH_ROOT := "{S10_ROOT}"')
    assert base.count(CHECK_OLD) == 1 and base.count(FAIL_OLD) == 1
    control = base.replace(ANCHOR, ANCHOR + TAMPER, 1)
    dead = control.replace(CHECK_OLD, CHECK_DEAD, 1).replace(FAIL_OLD, FAIL_DEAD, 1)
    assert dead != control and "mut03 dead measure" in dead
    m = re.search(r'print\("(PASS export_prod_s10 [^"]*)"\)', src)
    assert m, "source declares no literal PASS receipt"
    expected_pass = m.group(1)
    for name, text in (("s10_pristine", base), ("s10_control_tampered", control),
                       ("s10_dead_tampered", dead)):
        (PROJ / f"{name}.gd").write_text(text)
        (EVID / f"{name}.gd").write_text(text)
    return {"s10_pristine": base, "s10_control_tampered": control, "s10_dead_tampered": dead}, expected_pass


def run_variant(name):
    cmd = [GODOT, "--headless", "--path", str(PROJ), "--script", f"res://{name}.gd"]
    print("MUT03-S10 CMD " + shlex.join(cmd))
    proc = subprocess.run(cmd, capture_output=True, timeout=300)
    out, err = proc.stdout, proc.stderr
    (EVID / f"{name}.stdout.txt").write_bytes(out)
    (EVID / f"{name}.stderr.txt").write_bytes(err)
    text = ANSI_RE.sub("", (out + b"\n" + err).decode("utf-8", "replace"))
    lines = text.splitlines()
    fails = [ln for ln in lines if ln.startswith("FAIL ")]
    receipt = [ln for ln in lines if ln.startswith("PASS export_prod_s10") or ln.startswith("FAIL export_prod_s10")]
    tail = receipt[-1] if receipt else "<no final receipt>"
    print(f"MUT03-S10 RUN {name} rc={proc.returncode} stdout_sha={hashlib.sha256(out).hexdigest()} "
          f"fail_lines={len(fails)} stderr_bytes={len(err)}")
    print(f"MUT03-S10 RECEIPT {name} {tail}")
    for ln in fails[:4]:
        print(f"MUT03-S10 FAIL_LINE {name} {ln}")
    return {"rc": proc.returncode, "stdout": out, "text": text, "receipt": tail, "fails": fails}


def parse_pck(data):
    if data[:4] != b"GDPC":
        return []
    fb = int.from_bytes(data[24:32], "little")
    table = int.from_bytes(data[32:40], "little")
    count = int.from_bytes(data[table:table + 4], "little")
    p = table + 4
    entries = []
    for _ in range(count):
        pl = int.from_bytes(data[p:p + 4], "little")
        p += 4
        path = data[p:p + pl].split(b"\0", 1)[0].decode("latin1")
        p += pl
        ofs = int.from_bytes(data[p:p + 8], "little")
        size = int.from_bytes(data[p + 8:p + 16], "little")
        md5 = data[p + 16:p + 32]
        p += 36
        body = data[fb + ofs:fb + ofs + size]
        entries.append({"path": path, "size": size,
                        "md5_ok": hashlib.md5(body).digest() == md5,
                        "sha256": hashlib.sha256(body).hexdigest()})
    return entries


def recompute_report(label):
    if not PCK.is_file():
        print(f"MUT03-S10 RECOMPUTE {label} pck_missing path={PCK}")
        return None
    data = PCK.read_bytes()
    entries = parse_pck(data)
    bad = [e["path"] for e in entries if not e["md5_ok"]]
    print(f"MUT03-S10 RECOMPUTE {label} bytes={len(data)} entries={len(entries)} "
          f"md5_mismatch={len(bad)} {bad[:3]}")
    return {"bytes": len(data), "entries": len(entries), "bad": bad}


def main():
    EVID.mkdir(parents=True, exist_ok=True)
    variants, expected_pass = build_variants()
    results = {}
    recompute = {}
    for name in ("s10_pristine", "s10_control_tampered", "s10_dead_tampered"):
        results[name] = run_variant(name)
        recompute[name] = recompute_report(name)

    p, c, d = results["s10_pristine"], results["s10_control_tampered"], results["s10_dead_tampered"]
    tamper_sigs = ("pck:md5", "icon:ctex_magic", "zip:bytes_match")
    control_extra = len(c["fails"]) - len(p["fails"])
    control_detected = (c["rc"] == 1 and control_extra >= 2
                        and sum(any(sig in ln for ln in c["fails"]) for sig in tamper_sigs) >= 2)
    dead_survives = (d["rc"] == 0 and len(d["fails"]) == 0 and d["receipt"] == expected_pass)
    recompute_kills = bool(recompute.get("s10_dead_tampered") and recompute["s10_dead_tampered"]["bad"])

    print(f"MUT03-S10 BASELINE pristine_rc={p['rc']} pristine_fails={len(p['fails'])} "
          f"pristine_receipt={p['receipt'][:72]!r}")
    print(f"MUT03-S10 MODEL control_fails={len(c['fails'])} control_extra_over_baseline={control_extra} "
          f"control_detects_tamper={control_detected} dead_survives_on_tampered={dead_survives} "
          f"dead_receipt_is_declared_pass={d['receipt'] == expected_pass} "
          f"independent_recompute_detects_tamper={recompute_kills}")
    ok = control_detected and dead_survives and recompute_kills
    print("MUT03-S10 " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
