ANC=$PPID
while read -r _ _ _ pp _ < /proc/self/stat && [ "$pp" = "$ANC" ]; do sleep 0.05; done
read -r _ _ _ PP _ < /proc/self/stat
echo "GC_ORPHANED pid=$$ ppid_now=$PP"
sleep 3.5
echo d2_hang-gc-outlived > /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r63-boundary/arms/d2_hang.gc-outlived
