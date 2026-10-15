#!/bin/sh
# r66-scribe descendant arm
while read -r _ _ _ pp _ < /proc/self/stat && [ "$pp" = "$1" ]; do sleep 0.05; done
printf 'ERROR: R66 head line\nrest of it\n'
echo "R66 write_ppid=$pp"
