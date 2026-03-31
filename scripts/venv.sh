#!/bin/sh

set_venv_python() {
  root_dir="$1"
  venv_python="$root_dir/.venv/Scripts/python.exe"

  if [ ! -f "$venv_python" ]; then
    venv_python="$root_dir/.venv/bin/python"
  fi

  if [ ! -f "$venv_python" ]; then
    echo "Python venv not found. Create it in $root_dir/.venv first." >&2
    return 1
  fi

  VENV_PY="$venv_python"
  return 0
}
