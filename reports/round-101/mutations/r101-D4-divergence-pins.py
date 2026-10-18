#!/usr/bin/env python3
"""r101-D4 divergence-pin certificate for the r100b 14-cell replay (C1/C2 depth).

CONTEXT
  The battery rows `r100b_seq_clean` / `r100b_seq_noclean` pin SCALAR STRINGS
  against merged stdout+stderr (`classify_process` = substring test + ERROR
  allowlist).  Today each row pins exactly one cell line of the fixture's
  14-cell replay, so (r100-critic F2) a forged extra output line inside the
  replay leaves both rows PASS and 3 of the replay's 4 measured divergences are
  unconstrained.  The fixture bytes themselves are frozen (byte-copy of the
  r100-boundary probe, sha256 4718a19e...a94dd) and must not grow a certificate
  print, so the divergence fields below are a REVIEW-SIDE certificate with a
  mechanical checker -- they compose with D2/D3's full-transcript byte pins
  (bytes) by pinning their MEANING (cause + delta + census).

WHAT A DIVERGENCE-PIN FIELD IS
      <cell>.<key>[#<occurrence>]        field-id
      fresh   exact bytes in that cell's fresh-process pin (CASES sig)
      replay  exact bytes in the frozen replay transcript
      cause   the cell whose Input.parse_input_event() wrote the leaked state
      delta   replay != fresh, and for pos fields replay == the parse position
              derived from the cause cell's source (static derivation)

  The checker reconstructs the expected clean transcript from the fresh pins +
  the declared deltas alone (no captured-bytes input), so a stale delta, an
  erased divergence, a relocated divergence, an extra line or a duplicated
  block all fail -- including forgeries a bare joined-line pin cannot see.

USAGE
  python3 r101-D4-divergence-pins.py --capture     /var/tmp/r101-D4/cert
  python3 r101-D4-divergence-pins.py --check       /var/tmp/r101-D4/cert
  python3 r101-D4-divergence-pins.py --forge-tests /var/tmp/r101-D4/cert
  python3 r101-D4-divergence-pins.py --emit        /var/tmp/r101-D4/cert

Exit 0 = all checks passed. Never imports or runs corpus/fixtures/run_battery.py
(only AST-parsed); never writes inside the repository.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
FIXTURES = REPO / "corpus" / "fixtures"
HARNESS = FIXTURES / "run_battery.py"
GODOT = "godot"
SEQ = "r100b_seq.gd"
ENGINE_BANNER_PREFIX = "Godot Engine v4.7.2.stable"
ERROR_BLOCK = [
    'ERROR: Parameter "t" is null.',
    "   at: texture_2d_get (./servers/rendering/dummy/storage/texture_storage.h:110)",
    "   GDScript backtrace (most recent call first):",
    "       [0] _cell_render (res://r100b_seq.gd:762)",
    "       [1] _run (res://r100b_seq.gd:116)",
]
# frame [2] is the coroutine chain and is the ONE line that differs per variant
ERROR_FRAME2 = {
    "clean": "       [2] _cleanup (res://r100b_seq.gd:135)",
    "noclean": "       [2] _cell_focus (res://r100b_seq.gd:750)",
}

CLEAN_ROW = "r100b_seq_clean"
NOCLEAN_ROW = "r100b_seq_noclean"

CELL_ORDER = ["census", "routing", "hover", "motion", "localpos", "cursor",
              "clip", "drag", "touch", "subvp", "warp", "focus", "render",
              "osmeta"]

DECLARED = {
    "clean": {
        "row": CLEAN_ROW,
        "flag": "1",
        "fields": [
            {"id": "cursor.c0", "class": "pos", "cause": "localpos"},
            {"id": "cursor.c1_push_mm", "class": "pos", "cause": "localpos"},
            {"id": "cursor.c2_push_mb", "class": "pos", "cause": "localpos"},
            {"id": "touch.a#1", "class": "list", "cause": "cursor",
             "absent_entry": "A:mb(b=1,p=1,dc=0,bm=1,pos=8.0,8.0,gpos=8.0,8.0)|"},
            {"id": "subvp.cursor_root", "class": "pos", "cause": "touch"},
            {"id": "subvp.root#3", "class": "pos", "cause": "touch"},
            {"id": "warp.cursor#1", "class": "pos", "cause": "touch"},
            {"id": "warp.cursor#2", "class": "pos", "cause": "touch"},
            {"id": "warp.cursor#3", "class": "pos", "cause": "touch"},
            {"id": "warp.cursor#4", "class": "pos", "cause": "touch"},
        ],
        "divergent_cells": ["cursor", "touch", "subvp", "warp"],
    },
    "noclean": {
        "row": NOCLEAN_ROW,
        "flag": "0",
        "fields": [
            {"id": "hover.h0", "class": "literal", "cause": "routing"},
        ],
        "divergent_cells": ["hover", "motion", "localpos", "cursor", "clip",
                            "drag", "touch", "subvp", "warp"],
    },
}


# --------------------------------------------------------------------------- io
def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def harness_pins() -> dict[str, str]:
    for node in ast.walk(ast.parse(HARNESS.read_text())):
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", None) == "CASES":
            cases = ast.literal_eval(node.value)
            break
    else:
        raise SystemExit("CASES not found in run_battery.py")
    return {name: sig for name, _s, _f, _rc, sig in cases
            if name.startswith("r100_gui_")}


def pins_by_cell() -> dict[str, str]:
    return {n.removeprefix("r100_gui_"): s for n, s in harness_pins().items()}


def split_raw(facts: str) -> list[str]:
    """Split a PASS fact string at top-level spaces (values keep inner spaces)."""
    toks, cur, depth = [], "", 0
    for ch in facts:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == " " and depth == 0:
            toks.append(cur)
            cur = ""
        else:
            cur += ch
    toks.append(cur)
    return toks


def facts_of(line: str) -> str:
    return line.split(" ", 3)[3]


def cell_of(line: str) -> str:
    return line.split(" ", 3)[2]


def token_index(line: str, field_id: str) -> tuple[int, str, str]:
    """Return (token index, key, occurrence) of `key[#occ]` in the line."""
    key = field_id.split(".", 1)[1]
    occ = 1
    if "#" in key:
        key, occ_s = key.split("#", 1)
        occ = int(occ_s)
    seen = 0
    for i, tok in enumerate(split_raw(facts_of(line))):
        if "=" not in tok:
            continue
        if tok.split("=", 1)[0] == key:
            seen += 1
            if seen == occ:
                return i, key, occ
    raise KeyError(f"{field_id} absent from {line[:70]!r}")


def field_value(line: str, field_id: str) -> str:
    i, _key, _occ = token_index(line, field_id)
    return split_raw(facts_of(line))[i].split("=", 1)[1]


def with_field(line: str, field_id: str, value: str) -> str:
    toks = split_raw(facts_of(line))
    i, key, _occ = token_index(line, field_id)
    toks[i] = f"{key}={value}"
    return f"PASS r100_gui {cell_of(line)} " + " ".join(toks)


def transcript_lines(path: Path) -> list[str]:
    return path.read_text().splitlines()


def transcript_cells(path: Path) -> dict[str, str]:
    cells: dict[str, str] = {}
    for ln in transcript_lines(path):
        if ln.startswith("PASS r100_gui "):
            cells.setdefault(cell_of(ln), ln)
    return cells


# ------------------------------------------------------- source-side derivation
POS_RE = re.compile(r"Vector2\(\s*(-?[0-9.]+)\s*,\s*(-?[0-9.]+)\s*\)")
CALL_RE = re.compile(r"Input\.parse_input_event\((.*)\)")


def cell_source(cell: str) -> list[str]:
    out, on = [], False
    for ln in (FIXTURES / SEQ).read_text().splitlines():
        if ln.startswith(f"func _cell_{cell}("):
            on = True
        elif on and ln.startswith("func "):
            break
        if on:
            out.append(ln)
    if not out:
        raise SystemExit(f"cell {cell} not found in {SEQ}")
    return out


def last_parse_positions(cell: str) -> list[tuple[float, float]]:
    """Positions handed to Input.parse_input_event inside one cell, in order.

    Covers both call shapes in the fixture: the direct
    `parse_input_event(_mb(Vector2(x, y), ...))` form and the two-step
    `var st := InputEventScreenTouch.new(); st.position = Vector2(..)` form.
    """
    positions: list[tuple[float, float]] = []
    pending_var: str | None = None
    pending_pos: tuple[float, float] | None = None
    for ln in cell_source(cell):
        m = re.search(r"var (\w+)\s*:=\s*InputEventScreen(Touch|Drag)\.new\(\)", ln)
        if m:
            pending_var, pending_pos = m.group(1), None
            continue
        m = re.search(r"\b(\w+)\.position\s*=\s*Vector2\(\s*(-?[0-9.]+)\s*,\s*(-?[0-9.]+)\s*\)", ln)
        if m and pending_var and m.group(1) == pending_var:
            pending_pos = (float(m.group(2)), float(m.group(3)))
            continue
        m = CALL_RE.search(ln)
        if m:
            args = m.group(1)
            vm = POS_RE.search(args)
            if vm:
                positions.append((float(vm.group(1)), float(vm.group(2))))
            elif pending_var and pending_var in args and pending_pos is not None:
                positions.append(pending_pos)
            pending_var, pending_pos = None, None
    return positions


def predicted_leak(target: str) -> tuple[tuple[float, float], str]:
    """Last cursor-writing parse in the cell prefix (push_input never writes it)."""
    for cell in reversed(CELL_ORDER[:CELL_ORDER.index(target)]):
        pos = last_parse_positions(cell)
        if pos:
            return pos[-1], cell
    raise SystemExit(f"no cursor-writing parse before {target}")


def fmt_vec(v: str) -> tuple[float, float]:
    m = re.fullmatch(r"\((-?[0-9.]+), (-?[0-9.]+)\)", v)
    if not m:
        raise ValueError(f"not a Vector2 literal: {v!r}")
    return float(m.group(1)), float(m.group(2))


# ------------------------------------------------------------------- capture
def capture(dest: Path) -> None:
    scratch = dest / "scratch"
    if scratch.exists():
        shutil.rmtree(scratch)
    scratch.mkdir(parents=True)
    for item in sorted(FIXTURES.iterdir()):
        if item.name == "run_battery.py" or item.name.startswith("."):
            continue
        if item.is_dir():
            shutil.copytree(item, scratch / item.name)
        else:
            shutil.copy2(item, scratch / item.name)
    for variant, flag in (("clean", "--clean=1"), ("noclean", "--clean=0")):
        out = dest / f"seq_{variant}.merged"
        cmd = [GODOT, "--headless", "--path", str(scratch), "--script",
               f"res://{SEQ}", "--", flag]
        with out.open("wb") as fh:
            proc = subprocess.run(cmd, stdout=fh, stderr=subprocess.STDOUT,
                                  timeout=60)
        print(f"capture {variant}: rc={proc.returncode} lines={len(transcript_lines(out))} "
              f"sha256={sha256(out)} path={out}")
    print(f"fixture sha256({SEQ}) = {sha256(FIXTURES / SEQ)}")


# ------------------------------------------------------------------- checking
def check(dest: Path) -> int:
    pins = pins_by_cell()
    failures: list[str] = []
    for variant, decl in DECLARED.items():
        path = dest / f"seq_{variant}.merged"
        if not path.is_file():
            failures.append(f"{variant}: missing transcript {path}")
            continue
        cells = transcript_cells(path)
        measured = [c for c in CELL_ORDER if cells.get(c) != pins.get(c)]
        if measured != decl["divergent_cells"]:
            failures.append(f"{variant}: divergent-cell set drift: measured "
                            f"{measured} != declared {decl['divergent_cells']}")
        else:
            print(f"OK {variant}: divergent cells {len(measured)}/{len(CELL_ORDER)}"
                  " == declared")

        for fld in decl["fields"]:
            cell = fld["id"].split(".", 1)[0]
            line, fresh_line = cells[cell], pins[cell]
            rv, fv = field_value(line, fld["id"]), field_value(fresh_line, fld["id"])
            if rv == fv:
                failures.append(f"{variant}.{fld['id']}: replay == fresh ({rv}); "
                                "divergence claim is false")
                continue
            if fld["class"] == "literal":
                print(f"OK {variant}.{fld['id']}: fresh={fv} replay={rv}")
            elif fld["class"] == "list":
                entry = fld["absent_entry"]
                if not (entry in fv and fv.replace(entry, "", 1) == rv):
                    failures.append(f"{variant}.{fld['id']}: expected replay = "
                                    f"fresh minus entry {entry!r}; fresh={fv} "
                                    f"replay={rv}")
                elif entry in rv:
                    failures.append(f"{variant}.{fld['id']}: entry still present "
                                    "in replay")
                else:
                    print(f"OK {variant}.{fld['id']}: entry {entry[:30]}... absent "
                          f"(cause={fld['cause']})")
            else:  # pos
                rvv, fvv = fmt_vec(rv), fmt_vec(fv)
                pv, pcell = predicted_leak(cell)
                if pcell != fld["cause"]:
                    failures.append(f"{variant}.{fld['id']}: declared cause "
                                    f"{fld['cause']} but the last cursor-writing "
                                    f"parse lives in {pcell}")
                elif rvv != pv:
                    failures.append(f"{variant}.{fld['id']}: replay {rv} != derived "
                                    f"leak {pv} from {pcell}")
                else:
                    print(f"OK {variant}.{fld['id']}: replay={rv} fresh={fv} "
                          f"delta=({rvv[0]-fvv[0]:+.1f},{rvv[1]-fvv[1]:+.1f}) "
                          f"derived from {pcell}")

    # every other field of the 4 divergent cells must be byte-identical to the pin
    cells = transcript_cells(dest / "seq_clean.merged")
    for cell in DECLARED["clean"]["divergent_cells"]:
        r_toks, f_toks = split_raw(facts_of(cells[cell])), split_raw(facts_of(pins[cell]))
        if [t.split("=", 1)[0] for t in r_toks] != [t.split("=", 1)[0] for t in f_toks]:
            failures.append(f"clean.{cell}: field-key sequence changed")
            continue
        declared = {f["id"].split(".", 1)[1].split("#")[0]
                    for f in DECLARED["clean"]["fields"] if f["id"].startswith(cell + ".")}
        seen: dict[str, int] = {}
        for r_tok, f_tok in zip(r_toks, f_toks):
            if "=" not in r_tok:
                continue
            key = r_tok.split("=", 1)[0]
            seen[key] = seen.get(key, 0) + 1
            if r_tok != f_tok and key not in declared:
                failures.append(f"clean.{cell}.{key}#{seen[key]}: undeclared "
                                f"divergence {f_tok!r} -> {r_tok!r}")

    if failures:
        print("\nFAILED CHECKS:")
        print("\n".join("  - " + f for f in failures))
        return 1
    failures += reconstruction_report(dest)
    if failures:
        print("\nFAILED CHECKS:")
        print("\n".join("  - " + f for f in failures))
        return 1
    print("\nALL DIVERGENCE-PIN CHECKS PASSED")
    return 0


def reconstruction_report(dest: Path) -> list[str]:
    """Fidelity of derive_transcript(): how many of the captured lines the
    certificate can rebuild from the pins + declared deltas alone."""
    failures: list[str] = []
    for variant in ("clean", "noclean"):
        path = dest / f"seq_{variant}.merged"
        got = transcript_lines(path)
        exp = derive_transcript(variant)
        if len(got) != len(exp):
            failures.append(f"{variant}: capture has {len(got)} lines, "
                            f"derivation predicts {len(exp)}")
            continue
        same = sum(1 for g, e in zip(got, exp) if e == "<banner>" or g == e)
        banner = got[0].startswith(ENGINE_BANNER_PREFIX)
        print(f"reconstruction {variant}: {same}/{len(exp)} lines rebuilt "
              f"(banner-prefix ok={banner}); undeclared-divergence lines: "
              f"{len(exp) - same + (0 if banner else 1)}")
        if variant == "clean" and (same != len(exp) or not banner):
            failures.append(f"clean: derivation rebuilds only {same}/{len(exp)} "
                            "lines -- divergence table is stale or incomplete")
    return failures


# ---------------------------------------------- derived transcript (certificate)
def derive_transcript(variant: str) -> list[str]:
    """Rebuild the variant's expected 23-line transcript WITHOUT reading it.

    Sources: the fresh single-cell CASES pins (10 non-divergent cells verbatim),
    the declared divergence fields applied to the 4 divergent cells' pins, the
    fixed engine banner / ERROR block / SEQ_DONE frame.
    """
    pins = pins_by_cell()
    decl = DECLARED[variant]
    cells: list[str] = []
    for cell in CELL_ORDER:
        line = pins[cell]
        for fld in decl["fields"]:
            if not fld["id"].startswith(cell + "."):
                continue
            if fld["class"] == "pos":
                pos, _cause = predicted_leak(cell)
                line = with_field(line, fld["id"], f"({pos[0]:.1f}, {pos[1]:.1f})")
            elif fld["class"] == "list":
                fv = field_value(line, fld["id"])
                line = with_field(line, fld["id"], fv.replace(fld["absent_entry"], "", 1))
            elif fld["class"] == "literal":
                line = with_field(line, fld["id"], "P")
        cells.append(line)
    out = ["<banner>", ""]
    out += cells[:12]              # census .. focus  (indices 2..13)
    out += ERROR_BLOCK + [ERROR_FRAME2[variant]]   # indices 14..19
    out += cells[12:]              # render, osmeta    (indices 20..21)
    out += [f"SEQ_DONE clean={decl['flag']}"]
    return out


def cert_ok(text: str, variant: str) -> bool:
    lines = text.splitlines()
    expected = derive_transcript(variant)
    if len(lines) != len(expected):
        return False
    if not lines[0].startswith(ENGINE_BANNER_PREFIX):
        return False
    for got, exp in zip(lines, expected):
        if exp == "<banner>":
            continue
        if got != exp:
            return False
    # exactly one transcript line per cell, no duplicates anywhere
    cell_lines = [ln for ln in lines if ln.startswith("PASS r100_gui ")]
    if len(cell_lines) != len(CELL_ORDER):
        return False
    return True


# ------------------------------------------------------------ forge experiments
def classify(output: str, signature: str) -> bool:
    """classify_process() semantics for a PASS row: signature is a substring of
    merged stdout+stderr and every ERROR: line is allowlisted (the r100b_seq rows
    allowlist exactly `Parameter "t" is null.`)."""
    if signature not in output:
        return False
    for ln in output.splitlines():
        if ln.startswith(("ERROR:", "SCRIPT ERROR:", "Parse Error:")) and \
                'Parameter "t" is null.' not in ln:
            return False
    return True


def forge_tests(dest: Path) -> int:
    path = dest / "seq_clean.merged"
    lines = transcript_lines(path)
    cells = transcript_cells(path)
    pins = pins_by_cell()
    touch, subvp, warp, cursor = (cells["touch"], cells["subvp"], cells["warp"],
                                  cells["cursor"])

    # NOTE: the 6-line ERROR block sits between the `focus` line and the
    # `render` line, so a `"\n".join` of the 14 cell lines is NOT a substring of
    # the real transcript (control M0 measures this).  The critic's "smallest
    # safe correction -- a multi-line signature ... `"\n".join` of the replay's
    # 14 lines" is unsatisfiable as literally written; the working forms are the
    # whole-file join (M0 PASS) or two segment joins with the ERROR block.
    def joined_cells_only() -> str:
        return "\n".join(cells[c] for c in CELL_ORDER)

    def joined_whole() -> str:
        return "\n".join(lines)

    shapes = {
        # today: the clean row pins ONE cell line (cursor); noclean pins hover
        "today 2-cell": ([cursor],),
        # one row per cell (14 separate substring rows, no adjacency)
        "per-cell 14": ([cells[c] for c in CELL_ORDER],),
        # the critic's literal proposal
        "joined cells-only": (None, joined_cells_only()),
        # whole 23-line transcript as one signature
        "joined 23-line": (None, joined_whole()),
    }

    def passes(shape: str, cand: str) -> bool:
        if shape == "joined cells-only":
            return classify(cand, joined_cells_only())
        if shape == "joined 23-line":
            return classify(cand, joined_whole())
        return all(classify(cand, s) for s in shapes[shape][0])

    mutations = {
        "M0 control: unmutated transcript": list(lines),
        "M1 extra non-cell line (critic m_seq)":
            lines[:9] + ["FORGED_EXTRA_CELL_OUTPUT"] + lines[9:],
        "M2 forged clean-mimicking cursor line":
            lines[:3] + [pins["cursor"]] + lines[3:],
        "M3 subvp divergence erased":
            [ln.replace("cursor_root=(20.0, 4.0)", "cursor_root=(0.0, 0.0)")
             if ln == subvp else ln for ln in lines],
        "M4 warp divergence relocated (w2 only)":
            [ln.replace("w2 after_input_warp cursor=(20.0, 4.0)",
                        "w2 after_input_warp cursor=(0.0, 0.0)")
             if ln == warp else ln for ln in lines],
        "M5 touch divergence erased":
            [pins["touch"] if ln == touch else ln for ln in lines],
        "M6 whole 14-cell block appended":
            lines + [cells[c] for c in CELL_ORDER],
        "M7 single trailing cell line appended":
            lines + [cursor],
    }

    print("forge experiments on the captured clean transcript")
    header = f"{'experiment':44s} {'today 2-cell':13s} {'per-cell 14':12s} " \
             f"{'joined cells':13s} {'joined 23':10s} certificate"
    print(header)
    results: dict[str, tuple[bool, bool, bool, bool, bool]] = {}
    for label, cand_lines in mutations.items():
        cand = "\n".join(cand_lines)
        got = (passes("today 2-cell", cand), passes("per-cell 14", cand),
               passes("joined cells-only", cand), passes("joined 23-line", cand),
               cert_ok(cand, "clean"))
        results[label] = got
        print(f"{label:44s} " + " ".join(
            f"{'PASS' if g else 'REJECT':{w}s}"
            for g, w in zip(got, (13, 12, 13, 10, 0))))
    expected = {
        "M0 control: unmutated transcript": (True, True, False, True, True),
        "M1 extra non-cell line (critic m_seq)": (True, True, False, False, False),
        "M2 forged clean-mimicking cursor line": (True, True, False, False, False),
        "M3 subvp divergence erased": (True, False, False, False, False),
        "M4 warp divergence relocated (w2 only)": (True, False, False, False, False),
        "M5 touch divergence erased": (True, False, False, False, False),
        "M6 whole 14-cell block appended": (True, True, True, True, False),
        "M7 single trailing cell line appended": (True, True, False, True, False),
    }
    bad = 0
    for label, exp in expected.items():
        if results[label] != exp:
            print(f"MISMATCH {label!r}: expected {exp} got {results[label]}")
            bad += 1
    print("accept = the forgery survives the pin; "
          f"matrix {'AS EXPECTED' if bad == 0 else str(bad) + ' MISMATCHES'}")
    return 0 if bad == 0 else 1


# ----------------------------------------------------------------------- emit
def emit(dest: Path) -> int:
    pins = pins_by_cell()
    print("| row | cell | field-id | fresh (single-cell pin) | replay (frozen replay) | cause |")
    print("|---|---|---|---|---|---|")
    for variant, decl in DECLARED.items():
        cells = transcript_cells(dest / f"seq_{variant}.merged")
        for fld in decl["fields"]:
            cell = fld["id"].split(".", 1)[0]
            print(f"| {decl['row']} | {cell} | `{fld['id']}` | "
                  f"`{field_value(pins[cell], fld['id'])}` | "
                  f"`{field_value(cells[cell], fld['id'])}` | `{fld['cause']}` |")
    print()
    print(json.dumps(DECLARED, indent=2))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--capture", type=Path, metavar="DIR")
    ap.add_argument("--check", type=Path, metavar="DIR")
    ap.add_argument("--forge-tests", type=Path, metavar="DIR")
    ap.add_argument("--emit", type=Path, nargs="?", const=Path("/var/tmp/r101-D4/cert"),
                    metavar="DIR")
    args = ap.parse_args()
    if not any((args.capture, args.check, args.forge_tests, args.emit)):
        ap.print_help()
        return 2
    rc = 0
    if args.capture:
        capture(args.capture)
    if args.check:
        rc |= check(args.check)
    if args.forge_tests:
        rc |= forge_tests(args.forge_tests)
    if args.emit:
        rc |= emit(args.emit)
    return rc


if __name__ == "__main__":
    sys.exit(main())
