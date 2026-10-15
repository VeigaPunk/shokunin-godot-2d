#!/bin/sh
# r66-scribe descendant arm
while read -r _ _ _ pp _ < /proc/self/stat && [ "$pp" = "$1" ]; do sleep 0.05; done
printf 'ERR\nOR: R66 real escaped error\n'
printf 'ERROR'
printf ': SAVE EXPECTED NEGATIVE: malformed JSON rejected signature=JSON_PARSE_ERROR\n' >&2
echo "R66 write_ppid=$pp" >&2
