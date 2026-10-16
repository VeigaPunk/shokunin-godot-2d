#!/bin/bash
cd "$(dirname "$0")"
if [ -f pids.txt ]; then
  while read -r p; do kill "$p" 2>/dev/null; done < pids.txt
fi
echo "stopped hogs at $(date -u +%FT%TZ)"
