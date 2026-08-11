#!/usr/bin/env bash
set -euo pipefail

info() { echo "[INFO] $*"; }
err() { echo "[ERROR] $*" >&2; exit 1; }

# Find a Python interpreter >= 3.11
find_python() {
  candidates=(python3.11 python3 python)
  for py in "${candidates[@]}"; do
    if command -v "$py" >/dev/null 2>&1; then
      ver=$($py -c 'import sys; print("%d.%d" % (sys.version_info[0], sys.version_info[1]))' 2>/dev/null || true)
      if [[ -n "$ver" ]]; then
        major=${ver%%.*}
        minor=${ver##*.}
        if (( major > 3 )) || ( (( major == 3 )) && (( minor >= 11 )) ); then
          echo "$py"
          return 0
        fi
      fi
    fi
  done
  return 1
}

PY=$(find_python) || true
if [[ -z "$PY" ]]; then
  err "No Python >= 3.11 found. Install Python 3.11+ and re-run this script."
fi

info "Using Python interpreter: $PY"

# Create venv at .venv (idempotent)
if [[ -d .venv ]]; then
  if [[ -x .venv/bin/python ]]; then
    venv_ver=$(.venv/bin/python -c 'import sys; print(f"%d.%d" % (sys.version_info[0], sys.version_info[1]))' 2>/dev/null || true)
    if [[ -n "$venv_ver" ]]; then
      v_major=${venv_ver%%.*}
      v_minor=${venv_ver##*.}
      if (( v_major > 3 )) || ( (( v_major == 3 )) && (( v_minor >= 11 )) ); then
        info "Using existing .venv (Python $venv_ver)"
      else
        info "Existing .venv Python $venv_ver is older than 3.11 — recreating with $PY"
        rm -rf .venv
        "$PY" -m venv .venv
      fi
    else
      info ".venv exists but its Python version couldn't be determined — recreating"
      rm -rf .venv
      "$PY" -m venv .venv
    fi
  else
    info ".venv exists but has no Python executable — recreating"
    rm -rf .venv
    "$PY" -m venv .venv
  fi
else
  info "Creating virtual environment at .venv"
  "$PY" -m venv .venv
fi

VENV_PY=".venv/bin/python"
VENV_PIP=".venv/bin/pip"

info "Upgrading pip, setuptools and wheel inside venv"
"$VENV_PY" -m pip install --upgrade pip setuptools wheel >/dev/null

info "Installing package and developer tools in editable mode"
"$VENV_PIP" install -e ".[dev]"

info "Setup complete. Activate the venv with: source .venv/bin/activate"
