#!/usr/bin/env python3
"""r101-E12 verifier: builds the row pins from the measured runs and tests the
classifier contract (faithful re-implementation of the harness's
`classify_process`, copied verbatim in semantics; the harness itself is never
imported or executed).

Inputs (measured under /tmp/r101-E12/, see shard r101-E12.md):
  clean1.out/clean2.out     --clean=1, two independent runs
  noclean1.out/noclean2.out --clean=0, two independent runs
  forge_clean.out           --clean=1 with a forged print() in the hover cell

Checks:
  1. determinism: clean1==clean2 and noclean1==noclean2 byte-for-byte;
  2. pin extraction: stdout span SEQ_BEGIN..SEQ_END digest=... inclusive;
  3. classification matrix on the merged blob (stdout+stderr, harness order):
     real clean / real noclean -> PASS; forged -> FAIL with the new pin and
     PASS with the old r100b_seq one-line pin (the F2 gap reproduced);
  4. emits reports/round-101/mutations/r101-E12-pins.py with the literal pins.
"""
import hashlib
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[2]
SCRATCH = pathlib.Path("/tmp/r101-E12")
OUT_PINS = HERE / "r101-E12-pins.py"

ALLOWED = ('ERROR: Parameter "t" is null.',)


# --- verbatim semantics of corpus/fixtures/run_battery.py classify_process ---
def classify_process(code, error, output, expected_exit, signature, allowed_errors=()):
    lines = output.splitlines()

    def allowed_error(line, allowed):
        stripped = line.strip()
        if stripped == allowed:
            return True
        if allowed.endswith(","):
            return stripped.startswith(allowed) and stripped.count("ERROR:") == 1
        if allowed == "ERROR: chain incomplete":
            return (stripped.startswith("ERROR: chain incomplete collections=")
                    and "scene=SceneB:<Node#" in stripped and "old_alive=false" in stripped
                    and stripped.count("ERROR:") == 1)
        return False

    unrelated_errors = [line for line in lines if "ERROR:" in line
                        and not any(allowed_error(line, allowed) for allowed in allowed_errors)]
    return (code == expected_exit and error is None and signature in output
            and not unrelated_errors and "SCRIPT ERROR:" not in output and "Parse Error:" not in output)


def span(stdout: str) -> str:
    lines = stdout.splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith("SEQ_BEGIN "))
    end = next(i for i, l in enumerate(lines) if l.startswith("SEQ_END digest="))
    assert end - start == 16, f"expected 17 pinned lines (SEQ_BEGIN + 14 cells + SEQ_CENSUS + SEQ_END), got {end - start + 1}"
    return "\n".join(lines[start:end + 1])


def cells(stdout: str):
    return [l for l in stdout.splitlines() if l.startswith("PASS r100_gui ")]


def read(mode: str):
    so = (SCRATCH / f"{mode}.out").read_text()
    err = SCRATCH / f"{mode}.err"
    return so, (err.read_text() if err.exists() else "")


def main() -> int:
    clean1, clean1e = read("clean1")
    clean2, _ = read("clean2")
    clean3, _ = read("clean3")
    clean4, _ = read("clean4")
    noclean1, noclean1e = read("noclean1")
    noclean2, _ = read("noclean2")
    noclean3, _ = read("noclean3")
    noclean4, _ = read("noclean4")
    ff30, _ = read("ff30_clean")
    sts, _ = read("sts_clean")
    forge, forge_e = read("forge_clean")
    forge2, forge2e = read("forge2_clean")
    rc = 0

    def check(name, cond, detail=""):
        nonlocal rc
        print(f"{'PASS' if cond else 'FAIL'}  {name}{('  ' + detail) if detail else ''}")
        rc |= 0 if cond else 1

    check("determinism clean=1 (4 runs)", len({clean1, clean2, clean3, clean4}) == 1,
          hashlib.sha256(clean1.encode()).hexdigest())
    check("determinism clean=0 (4 runs)", len({noclean1, noclean2, noclean3, noclean4}) == 1,
          hashlib.sha256(noclean1.encode()).hexdigest())
    check("clean=1 under --fixed-fps 30 == default pin", ff30 == clean1)
    check("clean=1 under --single-threaded-scene == default pin", sts == clean1)
    check("clean stdout line count", len(clean1.splitlines()) == 19, str(len(clean1.splitlines())))
    check("noclean stdout line count", len(noclean1.splitlines()) == 19, str(len(noclean1.splitlines())))

    sig_c, sig_n = span(clean1), span(noclean1)
    check("clean pin = 17 lines", len(sig_c.splitlines()) == 17)
    check("noclean pin = 17 lines", len(sig_n.splitlines()) == 17)
    check("pins differ between modes", sig_c != sig_n)

    # merged blob exactly as run_process builds it: stdout then stderr
    real_c = classify_process(0, None, clean1 + clean1e, 0, sig_c, ALLOWED)
    real_n = classify_process(0, None, noclean1 + noclean1e, 0, sig_n, ALLOWED)
    forge_new_c = classify_process(0, None, forge + forge_e, 0, sig_c, ALLOWED)
    forge_new_n = classify_process(0, None, forge + forge_e, 0, sig_n, ALLOWED)
    # old-style single-line pins (what r100b_seq_clean / r100_gui_hover pin)
    old_cursor = [l for l in cells(clean1) if l.startswith("PASS r100_gui cursor ")][0]
    old_hover = [l for l in cells(clean1) if l.startswith("PASS r100_gui hover ")][0]
    forge_old_cursor = classify_process(0, None, forge + forge_e, 0, old_cursor, ALLOWED)
    forge_old_hover = classify_process(0, None, forge + forge_e, 0, old_hover, ALLOWED)

    check("real clean=1 vs new pin", real_c is True)
    check("real clean=0 vs new pin", real_n is True)
    check("FORGED output vs new clean pin", forge_new_c is False, "rejects (F2 closed)")
    check("FORGED output vs new noclean pin", forge_new_n is False, "rejects")
    check("FORGED output vs OLD one-line cursor pin", forge_old_cursor is True, "the r100 F2 gap, reproduced")
    check("FORGED output vs OLD one-line hover pin", forge_old_hover is True, "the r100 F2 gap, reproduced")

    flines = forge.splitlines()
    f_start = next(i for i, l in enumerate(flines) if l.startswith("SEQ_BEGIN "))
    f_end = next(i for i, l in enumerate(flines) if l.startswith("SEQ_END digest="))
    f_at = next(i for i, l in enumerate(flines) if l == "FORGED_EXTRA_CELL_OUTPUT")
    check("forged line present strictly inside the pinned span", f_start < f_at < f_end,
          f"index {f_at} in ({f_start}, {f_end})")
    check("forged digest == clean digest (digest alone is blind here)",
          "SEQ_END digest=" + sig_c.rsplit("SEQ_END digest=", 1)[1] in forge)
    check("forged census == clean census",
          [l for l in forge.splitlines() if l.startswith("SEQ_CENSUS ")][0]
          == [l for l in clean1.splitlines() if l.startswith("SEQ_CENSUS ")][0])

    # content forgery: one contaminated cell's value edited in an UNCONSTRAINED
    # cell (subvp is not pinned by either r100b_seq row); line count unchanged
    forge2_new_c = classify_process(0, None, forge2 + forge2e, 0, sig_c, ALLOWED)
    forge2_old_cursor = classify_process(0, None, forge2 + forge2e, 0, old_cursor, ALLOWED)
    forge2_old_hover = classify_process(0, None, forge2 + forge2e, 0, old_hover, ALLOWED)
    check("content-forge stdout line count unchanged", len(forge2.splitlines()) == len(clean1.splitlines()),
          str(len(forge2.splitlines())))
    check("content-forge subvp line carries the edit",
          "cursor_root=(20.0, 4.0)_FORGED" in [l for l in forge2.splitlines() if l.startswith("PASS r100_gui subvp ")][0])
    check("content-forge digest differs from clean digest",
          [l for l in forge2.splitlines() if l.startswith("SEQ_END ")][0]
          != [l for l in clean1.splitlines() if l.startswith("SEQ_END ")][0])
    check("content-forge census unchanged (set-level clause is blind to it)",
          [l for l in forge2.splitlines() if l.startswith("SEQ_CENSUS ")][0]
          == [l for l in clean1.splitlines() if l.startswith("SEQ_CENSUS ")][0])
    check("CONTENT-FORGED output vs new clean pin", forge2_new_c is False, "rejects (F2 second half closed)")
    check("CONTENT-FORGED output vs OLD one-line cursor pin", forge2_old_cursor is True, "gap reproduced")
    check("CONTENT-FORGED output vs OLD one-line hover pin", forge2_old_hover is True, "gap reproduced")

    # per-cell identity vs the harness's fresh pins, both modes
    import ast
    tree = ast.parse((REPO / "corpus/fixtures/run_battery.py").read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
            pins_table = {r[0][len("r100_gui_"):]: r[4] for r in ast.literal_eval(node.value)
                          if r[0].startswith("r100_gui_")}
            break
    for mode, text in (("clean", clean1), ("noclean", noclean1)):
        lines = cells(text)
        diff = [l.split()[2] for l in lines if l != pins_table[l.split()[2]]]
        census = [l for l in text.splitlines() if l.startswith("SEQ_CENSUS ")][0]
        expected = f"SEQ_CENSUS identical={14 - len(diff)} divergent_n={len(diff)} divergent=[{'|'.join(diff)}]"
        check(f"{mode}: fixture census == recomputed vs harness pins", census == expected, census)

    pin_src = (
        '"""r101-E12 measured pins (generated by r101-E12-verify.py; do not hand-edit).\n\n'
        "Rows for run_battery.py CASES (append to the CASES list; also add\n"
        "expected_errors entries for each row name):\n"
        '    ("r101_seqfull_clean", "r101_seqfull.gd", ["--clean=1"], 0, SIG_CLEAN),\n'
        '    ("r101_seqfull_noclean", "r101_seqfull.gd", ["--clean=0"], 0, SIG_NOCLEAN),\n'
        "expected_errors += {name: ('ERROR: Parameter \"t\" is null.',) for name in (...)}\n"
        '"""\n'
        f"# fixture sha256: {hashlib.sha256((REPO / 'corpus/fixtures/r101_seqfull.gd').read_bytes()).hexdigest()}\n"
        f"# measured stdout sha256: clean={hashlib.sha256(clean1.encode()).hexdigest()} "
        f"noclean={hashlib.sha256(noclean1.encode()).hexdigest()}\n"
        "# determinism: 4/4 runs byte-identical per mode; clean=1 also byte-identical under\n"
        "# --fixed-fps 30 and --single-threaded-scene (measured; see r101-E12.md).\n"
        "# row names must be added to the harness expected_errors allowlist:\n"
        "#   r101_seqfull_clean / r101_seqfull_noclean -> ('ERROR: Parameter \"t\" is null.',)\n\n"
        "SIG_CLEAN = " + repr(sig_c) + "\n\n"
        "SIG_NOCLEAN = " + repr(sig_n) + "\n\n"
        "TRANSCRIPT_CLEAN = " + repr(cells(clean1)) + "\n\n"
        "TRANSCRIPT_NOCLEAN = " + repr(cells(noclean1)) + "\n"
    )
    OUT_PINS.write_text(pin_src)
    check("wrote pins file", OUT_PINS.is_file(), str(OUT_PINS.relative_to(REPO)))

    print(f"\nfixture sha256: {hashlib.sha256((REPO / 'corpus/fixtures/r101_seqfull.gd').read_bytes()).hexdigest()}")
    print(f"clean pin sha256:   {hashlib.sha256(sig_c.encode()).hexdigest()}")
    print(f"noclean pin sha256: {hashlib.sha256(sig_n.encode()).hexdigest()}")
    print("VERDICT:", "PASS" if rc == 0 else "FAIL")
    return rc


if __name__ == "__main__":
    sys.exit(main())
