ANC=$PPID
while read -r _ _ _ pp _ < /proc/self/stat && [ "$pp" = "$ANC" ]; do sleep 0.05; done
read -r _ _ _ PP _ < /proc/self/stat
echo "GC_ORPHANED pid=$$ ppid_now=$PP"
sleep 1.0
echo "GC_RELEASED"
