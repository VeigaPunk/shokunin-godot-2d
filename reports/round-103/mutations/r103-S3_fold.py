#!/usr/bin/env python3
"""r103-S3: derive the r97-F6 fold of r97_scene_marker.gd (7 -> 3 lines).

Exact-string replacement applied to the committed bytes at HEAD (6e3e87f7).
Asserts the replacement count and the resulting shape. Writes the folded bytes
next to the source path given on argv.
"""
import pathlib
import sys

src = pathlib.Path(sys.argv[1])
dst = pathlib.Path(sys.argv[2])

text = src.read_text()
old = '@export var tag := "?"\nvar ready_ticks := 0\n\nfunc _ready() -> void:\n\tready_ticks += 1\n'
new = '@export var tag := "?"\n'
assert text.count(old) == 1, f"fold anchor count != 1: {text.count(old)}"
folded = text.replace(old, new, 1)
lines = folded.splitlines()
assert len(lines) == 3, f"folded line count != 3: {len(lines)}"
assert lines[0] == "extends Node2D"
assert lines[2] == '@export var tag := "?"'
dst.write_text(folded)
print(f"folded {len(text.splitlines())} -> {len(lines)} lines -> {dst}")
