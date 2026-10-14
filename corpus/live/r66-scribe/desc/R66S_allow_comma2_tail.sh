#!/bin/sh
# r66-scribe descendant arm
while read -r _ _ _ pp _ < /proc/self/stat && [ "$pp" = "$1" ]; do sleep 0.05; done
echo "ERROR: UI BUTTON ASSERTION FAILED: expected release1 text=Activated 1 receipts=1,FORGED_SUFFIX receipts=9"
echo "R66 write_ppid=$pp"
