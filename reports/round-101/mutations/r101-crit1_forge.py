#!/usr/bin/env python3
"""r101-crit1 forge matrix: score forged receipt lines with the LIVE
classify_process extracted (AST) from corpus/fixtures/run_battery.py.

The function is nested inside main(); we extract its source segment verbatim and
exec it, so every verdict below is the real harness expression, not a copy.
"""
import ast
import pathlib

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
SRC = REPO / "corpus/fixtures/run_battery.py"
ATT = pathlib.Path("/var/tmp/r101-CRIT-1/attack")


def extract_classify_process():
    text = SRC.read_text()
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
            seg = ast.get_source_segment(text, node)
            ns = {}
            exec(seg, ns)
            return ns["classify_process"], node.lineno, node.end_lineno
    raise SystemExit("classify_process not found")


def whole_line_hits(text, signature):
    return sum(1 for line in text.splitlines() if line == signature)


def lines_with(text, needle):
    return [line for line in text.splitlines() if needle in line]


def main():
    classify, l0, l1 = extract_classify_process()
    print(f"# classify_process extracted from run_battery.py lines {l0}-{l1}")

    real = (ATT / "mainpack.real.out").read_text()
    real_c = (ATT / "content.real.out").read_text()
    flip_c = (ATT / "content.flip.out").read_text()
    census_measure = (ATT / "negcontrol.out.keep.out").read_text()
    census_echo = (ATT / "census.echo.out").read_text()
    census_flip = (ATT / "negcontrol.atk-a3-payload-flip.out").read_text()
    marker = "MAIN_SCENE_RECEIPT scene=main marker=CRIT1_MAIN frames=0"
    alt_marker = "MAIN_SCENE_RECEIPT scene=alt marker=CRIT1_ALT frames=0"
    banner = "Godot Engine v4.7.2.stable.arch_linux.ed1daf0bf (2026-08-17 01:18:38 UTC) - https://godotengine.org"

    rows = []

    def score(tid, what, transcript, signature, expected_exit):
        p = classify(0 if expected_exit == 0 else expected_exit, None, transcript,
                     expected_exit, signature)
        rows.append((tid, what, p, whole_line_hits(transcript, signature.split("\n")[0])))

    score("T1", "real run receipt, single-line pin", real, marker, 0)

    forged_append = real + "\n" + alt_marker + "\n"
    score("T2", "real run + APPENDED alt-scene receipt; pin=alt marker", forged_append, alt_marker, 0)

    dup = real + "\n" + marker + "\n"
    score("T3", "real run + DUPLICATED pinned line; pin=marker", dup, marker, 0)

    three = banner + "\n\n" + marker
    inserted = banner + "\nFORGED_INSERTED_CELL\n\n" + marker
    score("T4", "3-line contiguous pin, line INSERTED mid-block", inserted, three, 0)
    appended_block = three + "\nFORGED_APPENDED_LINE"
    score("T5", "3-line contiguous pin, line APPENDED after block", appended_block, three, 0)

    census_line = "CENSUS magic=GDPC ver=4 4.7.2 count=17 md5_bad=0 tail=0 pck_sha256=1bacf493e2616158c28bebb06f023a552160ce6a17c8e51a6cf8b94679095af8"
    score("T6a", "census full-line pin on MEASURED transcript", census_measure, census_line, 0)
    score("T6b", "census full-line pin on ECHO transcript (no measurement)", census_echo, census_line, 0)
    forged_census = census_echo.replace("1bacf493e", "0000000000")
    score("T6c", "census full-line pin vs ECHO with fabricated sha", forged_census, census_line, 0)
    score("T6d", "census PREFIX pin vs ECHO with fabricated sha", forged_census, "CENSUS magic=GDPC ver=4", 0)

    neg_line = "CENSUS magic=GDPC ver=4 4.7.2 count=17 md5_bad=1 tail=0 pck_sha256=b49e548c486eef8bff6e57ab4424608cedd6a3b1a5a3794e2cbb564ddcdba754"
    score("T7", "negative-control arm: corrupted artifact, expect rc=2 + md5_bad=1", census_flip, neg_line, 2)

    err_forge = real + "\nERROR: forged unrelated diagnostic\n"
    score("T8", "real run + APPENDED 'ERROR:' line (harness control)", err_forge, marker, 0)

    # Forged content receipt: real pack receipt vs flipped pack receipt.
    note_pin = "MAIN_SCENE_RECEIPT scene=main marker=CRIT1_MAIN frames=0 note_md5=3555bc34fefb6050d7c54e7a3492f9e5"
    score("T9", "content-coupled pin vs FLIPPED pack (receipt has other md5)", flip_c, note_pin, 0)

    print(f"{'id':4} {'pass':5} {'wlh':4} shape")
    for tid, what, p, wlh in rows:
        print(f"{tid:4} {str(p):5} {wlh:<4} {what}")

    print("\n# external audit (r100-critic style) on the same transcripts")
    print("T3 whole_line_hits(marker) =", whole_line_hits(dup, marker), "(1 expected) -> duplicate detectable only here")
    print("T2 whole_line_hits(alt marker) =", whole_line_hits(forged_append, alt_marker),
          "| additional captured lines vs real =",
          len(forged_append.splitlines()) - len(real.splitlines()))
    print("T5 captured lines vs pinned block lines =",
          len(appended_block.splitlines()), "vs", len(three.splitlines()))
    print("T7 transcript rc: measure-flip line =", census_flip.strip().splitlines()[-1][:60] + "...")


if __name__ == "__main__":
    main()
