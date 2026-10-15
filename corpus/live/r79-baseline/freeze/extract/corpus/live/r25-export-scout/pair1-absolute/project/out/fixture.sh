#!/bin/sh
printf '\033c\033]0;%s\a' MechanicOneShotTest
base_path="$(dirname "$(realpath "$0")")"
"$base_path/fixture.x86_64" "$@"
