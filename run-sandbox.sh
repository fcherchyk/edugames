#!/usr/bin/env bash
# A sandbox has no screen, so this plays a scripted game headless and saves a PNG of every screen
# (players, new player, home, goal paths, Letter Pairs, victory, the shop, and Letter Rain with and
# without the keyboard, with pictures and with three letters to choose) to .sandbox/screens/, or
# to the folder given as the first argument. It uses a throwaway data folder, so no real profile
# is touched. Dependencies: see sandbox-deps.sh.
set -euo pipefail
cd "$(dirname "$0")"
source ./sandbox-deps.sh

out="${1:-.sandbox/screens}"
install_dependencies
rm -rf "$out"
edu_run python -m edugames.demo "$out"
echo "Screens saved in $out"
