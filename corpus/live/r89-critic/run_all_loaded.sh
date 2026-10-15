#!/usr/bin/env bash
set -u
cd "$(dirname "$0")"
GEO_ARMS="census ops contain joins trig pred pipedges edge offempty offdeg atlasempty polyendpoly bridge ring ring2 ring4 ringhits lineempty"
for a in $GEO_ARMS; do bash run_arms.sh geo2d_lattice.gd "$a" "${1:-3}" "${2:-load}"; done
for a in exact axisdev; do bash run_arms.sh input89_edges.gd "$a" "${1:-3}" "${2:-load}"; done
