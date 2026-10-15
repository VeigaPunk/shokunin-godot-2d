#!/bin/sh
# r66-scribe descendant arm
while read -r _ _ _ pp _ < /proc/self/stat && [ "$pp" = "$1" ]; do sleep 0.05; done
echo "ERROR: chain incomplete collections=9 scene=SceneB:<Node#9>"
echo "R66 write_ppid=$pp"
