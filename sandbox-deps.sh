# Dependency setup shared by test-sandbox.sh and run-sandbox.sh. Source it; do not run it.
#
# `install_dependencies` installs the dependencies into .venv, trying in order:
#   1. the versions in uv.lock, offline (from the uv cache);
#   2. the versions in uv.lock, with network;
#   3. when the package index refuses versions the lockfile pins (a mirror that lags behind, or a
#      "minimum release age" policy): a new resolution within the ranges of pyproject.toml that
#      skips releases newer than N days, for each N in SANDBOX_DEPS_MIN_AGE_DAYS, offline first
#      and then with network.
# Step 3 never rewrites uv.lock: it installs with `uv pip` and prints a warning, since the
# versions differ from the lockfile. It remembers in .sandbox/deps/ which N worked: while the
# lockfile is unchanged, later runs go straight to that N (delete .sandbox/deps/ to try the
# lockfile again).
#
# Settings (environment variables):
#   SANDBOX_DEPS=locked                  use only the lockfile (steps 1 and 2), never step 3
#   SANDBOX_OFFLINE=1                    never use the network
#   SANDBOX_DEPS_MIN_AGE_DAYS="14 30"    the N values step 3 tries (default "14 30 60 90")
#
# Afterwards, run commands with `edu_run <command>`: it uses .venv as installed and never syncs it
# again (so it also works offline). It also puts src/ on PYTHONPATH, so `python -m edugames…`
# works even where PYTHONSAFEPATH is set, and it selects SDL's dummy video and audio drivers,
# since a sandbox has no screen or sound card.

SANDBOX_DEPS="${SANDBOX_DEPS:-auto}"
SANDBOX_OFFLINE="${SANDBOX_OFFLINE:-0}"
SANDBOX_DEPS_MIN_AGE_DAYS="${SANDBOX_DEPS_MIN_AGE_DAYS:-14 30 60 90}"
_deps_state_dir=".sandbox/deps"
_deps_log="$(mktemp "${TMPDIR:-/tmp}/edugames-deps-XXXXXX")"

edu_run() {
  UV_OFFLINE=1 PYTHONPATH="$PWD/src${PYTHONPATH:+:$PYTHONPATH}" \
    SDL_VIDEODRIVER="${SDL_VIDEODRIVER:-dummy}" SDL_AUDIODRIVER="${SDL_AUDIODRIVER:-dummy}" \
    uv run --no-sync "$@"
}

_deps_note() {
  echo "sandbox-deps: $*" >&2
}

# Run a quiet attempt; keep its output in the log for the final error message.
_deps_try() {
  echo "\$ $*" >>"$_deps_log"
  "$@" >>"$_deps_log" 2>&1
}

# The date N days ago (UTC), with GNU or BSD date.
_deps_days_ago() {
  date -u -d "-$1 days" +%F 2>/dev/null || date -u -v "-$1d" +%F
}

# The network modes to try: offline first, then online unless SANDBOX_OFFLINE=1.
_deps_networks() {
  if [ "$SANDBOX_OFFLINE" = "1" ]; then echo offline; else echo "offline online"; fi
}

_deps_env() {
  if [ "$1" = "offline" ]; then echo "UV_OFFLINE=1"; else echo "-u UV_OFFLINE"; fi
}

_deps_locked() {
  # shellcheck disable=SC2046 # one env argument or two
  _deps_try env $(_deps_env "$1") uv sync --frozen
}

_deps_fallback() {
  local cutoff
  cutoff="$(_deps_days_ago "$2")"
  # shellcheck disable=SC2046 # one env argument or two
  _deps_try env $(_deps_env "$1") uv venv --allow-existing --quiet &&
    _deps_try env $(_deps_env "$1") uv pip install --quiet -e . --group dev \
      --exclude-newer "$cutoff"
}

install_dependencies() {
  local checksum network age remembered=""
  _deps_note "installing dependencies (details in $_deps_log)..."
  checksum="$(cat uv.lock pyproject.toml | cksum | cut -d ' ' -f 1)"
  if [ "$SANDBOX_DEPS" != "locked" ] && [ -f "$_deps_state_dir/python" ]; then
    remembered="$(awk -v sum="$checksum" '$1 == sum { print $2 }' "$_deps_state_dir/python")"
  fi
  for age in $remembered; do
    for network in $(_deps_networks); do
      if _deps_fallback "$network" "$age"; then
        _deps_note "WARNING: installed from version ranges, skipping releases newer than" \
          "$age days (remembered in $_deps_state_dir). uv.lock is unchanged."
        rm -f "$_deps_log"
        return 0
      fi
    done
  done
  for network in $(_deps_networks); do
    if _deps_locked "$network"; then
      rm -f "$_deps_state_dir/python" "$_deps_log"
      return 0
    fi
  done
  if [ "$SANDBOX_DEPS" = "locked" ]; then
    _deps_note "the versions in uv.lock could not be installed (SANDBOX_DEPS=locked)."
    tail -n 20 "$_deps_log" >&2
    return 1
  fi
  for age in $SANDBOX_DEPS_MIN_AGE_DAYS; do
    [ "$age" != "$remembered" ] || continue
    for network in $(_deps_networks); do
      if _deps_fallback "$network" "$age"; then
        mkdir -p "$_deps_state_dir"
        echo "$checksum $age" >"$_deps_state_dir/python"
        _deps_note "WARNING: the versions in uv.lock are not available here, so the" \
          "dependencies were installed from their version ranges, skipping releases newer" \
          "than $age days ($network). uv.lock is unchanged."
        rm -f "$_deps_log"
        return 0
      fi
    done
  done
  _deps_note "no way to install the dependencies worked."
  tail -n 20 "$_deps_log" >&2
  return 1
}
