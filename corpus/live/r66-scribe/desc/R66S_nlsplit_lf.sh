#!/bin/sh
# r66-scribe descendant arm
while read -r _ _ _ pp _ < /proc/self/stat && [ "$pp" = "$1" ]; do sleep 0.05; done
printf 'ERR\n'; sleep 0.05; printf 'OR: R66 newline-split diagnostic\n'
echo "R66 write_ppid=$pp"
