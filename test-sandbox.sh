#!/usr/bin/env bash
# Run the checks with no screen, no sound card and (once the dependencies are cached) no
# network: ruff, then pytest with coverage. Arguments go to pytest, for example
# `./test-sandbox.sh -k memory`. Dependencies: see sandbox-deps.sh.
set -euo pipefail
cd "$(dirname "$0")"
source ./sandbox-deps.sh

install_dependencies
edu_run ruff check .
edu_run ruff format --check .
edu_run pytest "$@"
