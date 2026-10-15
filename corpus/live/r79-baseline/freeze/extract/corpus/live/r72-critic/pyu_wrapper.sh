#!/bin/sh
# r72-critic: force the battery's probe process unbuffered (midline control
# run) without touching the tracked battery. Used as `--python` value.
exec python3 -u "$@"
