#!/usr/bin/env python3
"""VER-11 export-side kill matrix (r101, C1 export_prod lattice).

Real bytes only: the artifacts and captures written by
reports/round-101/mutations/ver11_exportpack.sh. Every clause is a function of
(rc, error, merged output, artifact bytes), so each arm below is arithmetic over
captured bytes — no Godot call, no run_battery.py execution.

Landed row shape reproduced from run_battery.py:1877-1880 (`__godot_export__`):
    classify_process(code, error, out, 0, "[ DONE ]") and "savepack" in out
    and artifact.is_file() and artifact.stat().st_size > 0

Output: corpus/live/r101-ver11/exportmatrix.json + stdout table
"""
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
LIVE = REPO / "corpus" / "live" / "r101-ver11"
REC = LIVE / "receipts"
PROJ = LIVE / "scratch" / "exportproj" / "out"
FORGED_RECEIPT = "EXPORT PROD PASS preset=Linux/X11 executable=nonempty magic=GDPC census=12/12"
FORGED_ERROR = "ERROR: r101-ver11 forged receipt diagnostic"


def classify_process(code, error, output, expected_exit, signature, allowed_errors=()):
    """Verbatim replica of run_battery.py:1725-1742."""
    lines = output.splitlines()

    def allowed_error(line, allowed):
        stripped = line.strip()
        if stripped == allowed:
            return True
        if allowed.endswith(","):
            return stripped.startswith(allowed) and stripped.count("ERROR:") == 1
        return False

    unrelated = [l for l in lines if "ERROR:" in l and not any(allowed_error(l, a) for a in allowed_errors)]
    return (code == expected_exit and error is None and signature in output and not unrelated
            and "SCRIPT ERROR:" not in output and "Parse Error:" not in output)


def landed(code, error, out, path, _line):
    return (classify_process(code, error, out, 0, "[ DONE ]") and "savepack" in out
            and path.is_file() and path.stat().st_size > 0)


def magic(code, error, out, path, _line):
    return landed(code, error, out, path, _line) and path.is_file() \
        and path.read_bytes()[:4] == b"GDPC"


def sha_pin(code, error, out, path, line):
    return landed(code, error, out, path, line) \
        and hashlib.sha256(path.read_bytes()).hexdigest() == line


def line_pin(code, error, out, path, line):
    return classify_process(code, error, out, 0, line)


ANSI = re.compile(r"\x1b\[[0-9;]*m")


def strip_ansi(text):
    return ANSI.sub("", text)


def line_set_pin(code, error, out, path, line):
    """Every pinned receipt line must appear with exactly its pinned multiplicity."""
    pinned = [l for l in line.split("\n") if l.strip()]
    have = [strip_ansi(l).strip() for l in out.splitlines()]
    return all(sum(1 for l in have if p in l) == sum(1 for q in pinned if q == p) for p in pinned)


def exact_transcript_pin(code, error, out, path, line):
    """Whole-transcript pin: ANSI-stripped non-empty lines must match exactly."""
    have = [s for s in (strip_ansi(l).rstrip() for l in out.splitlines()) if s.strip()]
    want = [l for l in line.split("\n") if l.strip()]
    return code == 0 and error is None and have == want


def main():
    pack_out = (REC / "exp_pack1.out").read_text()
    exe_out = (REC / "exp_exe1.out").read_text()
    launch_out = (REC / "exp_launch.out").read_text()
    pck = PROJ / "prod1.pck"
    exe = PROJ / "prod.x86_64"
    real_pck_sha = hashlib.sha256(pck.read_bytes()).hexdigest()
    # arm working copies under LIVE (scratch, gitignored)
    tmp = LIVE / "armartifacts"
    tmp.mkdir(exist_ok=True)
    junk = tmp / "junk.bin"
    junk.write_bytes(b"MUT2-JUNK" * 512)
    empty = tmp / "empty.bin"
    empty.write_bytes(b"")
    absent = tmp / "absent.bin"
    if absent.exists():
        absent.unlink()
    tampered = tmp / "prod_magic_tampered.pck"
    real = pck.read_bytes()
    tampered.write_bytes(b"GDPX" + real[4:])

    flipped = tmp / "prod_body_flip.pck"
    buf = bytearray(real)
    buf[64] ^= 0x01
    flipped.write_bytes(bytes(buf))

    json_art = tmp / "not_a_pack.json"
    json_art.write_text('{"forged": "receipt"}\n')

    arms = [
        ("A0_control", "real PCK export, real artifact, real receipt", 0, pack_out, pck),
        ("A1_extra_success", "real receipt + forged success receipt line", 0, pack_out + "\n" + FORGED_RECEIPT + "\n", pck),
        ("A1b_dupe_done", "real receipt + duplicate '[ DONE ] savepack' marker", 0, pack_out + "\n[ DONE ] savepack\n", pck),
        ("A2_forged_error", "real receipt + forged ERROR: line", 0, pack_out + "\n" + FORGED_ERROR + "\n", pck),
        ("A3_junk_artifact", "real receipt + artifact swapped to junk (magic MUT2, size>0)", 0, pack_out, junk),
        ("A4_json_artifact", "real receipt + artifact swapped to a JSON file", 0, pack_out, json_art),
        ("A5_magic_tampered", "real receipt + real PCK with magic patched GDPC->GDPX", 0, pack_out, tampered),
        ("A6_empty_artifact", "real receipt + artifact truncated to 0 bytes", 0, pack_out, empty),
        ("A7_absent_artifact", "real receipt + artifact deleted", 0, pack_out, absent),
        ("A5b_body_byte_flip", "real PCK with one body byte flipped (magic+size intact, sha changed)", 0, pack_out, flipped),
        ("A8_marker_substituted", "true '[ DONE ]' marker line substituted (line-pin kill)", 0, pack_out.replace("[ DONE ]", "[ DONE2 ]"), pck),
    ]
    cols = [("landed_size_only", landed), ("magic_gdp_c", magic), ("sha256_pin", sha_pin),
            ("receipt_line_pin", line_pin), ("receipt_line_set_pin", line_set_pin),
            ("exact_transcript_pin", exact_transcript_pin)]
    transcript_pin = "\n".join(strip_ansi(l).rstrip() for l in pack_out.splitlines() if l.strip())
    table = []
    for name, desc, rc, out, art in arms:
        row = {"arm": name, "desc": desc, "artifact": str(art), "bytes": art.stat().st_size if art.is_file() else 0,
               "sha256": hashlib.sha256(art.read_bytes()).hexdigest() if art.is_file() else None,
               "magic": art.read_bytes()[:4].decode("latin1") if art.is_file() and art.stat().st_size >= 4 else None}
        # the receipt line each clause pins
        probe_line = FORGED_RECEIPT if name == "A1_extra_success" else (
            real_pck_sha if name == "A8_marker_substituted" else ("[ DONE ] savepack" if name == "A1b_dupe_done" else "[ DONE ]"))
        for label, fn in cols:
            arg = real_pck_sha if label == "sha256_pin" else (
                transcript_pin if label == "exact_transcript_pin" else probe_line)
            row[label] = "PASS" if fn(rc, None, out, art, arg) else "FAIL"
        table.append(row)

    # launch-receipt arms (the --main-pack receipt row)
    receipt = "VER11_PACK_STARTED scene=main"
    launch_arms = [
        ("L0_control", "real launch output, real receipt", launch_out, receipt),
        ("L1_forged_scene", "receipt line replaced by a foreign scene value", launch_out.replace(receipt, "VER11_PACK_STARTED scene=other"), receipt),
        ("L2_prefix_pin_forge", "same foreign-scene bytes vs a prefix-only pin", launch_out.replace(receipt, "VER11_PACK_STARTED scene=other"), "VER11_PACK_STARTED"),
        ("L3_silent_plus_forge", "launch output with receipt stripped then a forged receipt appended", "\n".join(l for l in launch_out.splitlines() if receipt not in l) + "\n" + receipt + "\n", receipt),
    ]
    launch_table = []
    for name, desc, out, pin in launch_arms:
        ok = classify_process(0, None, out, 0, pin)
        launch_table.append({"arm": name, "desc": desc, "pin": pin, "verdict": "PASS" if ok else "FAIL",
                             "receipt_lines": [l for l in out.splitlines() if "VER11_PACK_STARTED" in l]})

    payload = {
        "captures": {"pack_out_sha256": hashlib.sha256(pack_out.encode()).hexdigest(),
                     "exe_out_sha256": hashlib.sha256(exe_out.encode()).hexdigest(),
                     "launch_out_sha256": hashlib.sha256(launch_out.encode()).hexdigest()},
        "real_pck": {"path": str(pck), "bytes": pck.stat().st_size, "sha256": real_pck_sha, "magic": "GDPC"},
        "real_exe": {"path": str(exe), "bytes": exe.stat().st_size,
                     "sha256": hashlib.sha256(exe.read_bytes()).hexdigest(),
                     "magic": exe.read_bytes()[:4].decode("latin1")},
        "forged_line": FORGED_RECEIPT, "forged_error": FORGED_ERROR,
        "table": table, "launch_table": launch_table,
        "landed_row_shape": "run_battery.py:1877-1880 (size-only, no magic/sha/receipt-line conjunct)",
    }
    (LIVE / "exportmatrix.json").write_text(json.dumps(payload, indent=1) + "\n")

    print(f"real PCK bytes={payload['real_pck']['bytes']} sha={real_pck_sha[:16]}… magic=GDPC")
    print(f"real EXE bytes={payload['real_exe']['bytes']} magic={payload['real_exe']['magic']!r}")
    hdr = ["arm", "bytes", "magic"] + [c for c, _ in cols]
    print(" | ".join(f"{h:18s}" for h in hdr))
    for r in table:
        print(" | ".join([f"{r['arm']:18s}", f"{r['bytes']:<18}", f"{str(r['magic']):18s}"]
                         + [f"{r[c]:18s}" for c, _ in cols]), "|", r["desc"][:44])
    print("-- launch receipt arms --")
    for r in launch_table:
        print(f"{r['arm']:20s} {r['verdict']:4s} pin={r['pin']!r} receipt_lines={r['receipt_lines']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
