#!/bin/sh

find_venv_python() {
  root_dir="$1"
  venv_name="$2"
  venv_python="$root_dir/$venv_name/Scripts/python.exe"

  if [ ! -f "$venv_python" ]; then
    venv_python="$root_dir/$venv_name/bin/python"
  fi

  if [ ! -f "$venv_python" ]; then
    echo "Python venv not found. Create it in $root_dir/$venv_name first." >&2
    return 1
  fi

  printf '%s\n' "$venv_python"
  return 0
}

set_venv_python() {
  root_dir="$1"
  VENV_PY=$(find_venv_python "$root_dir" ".venv") || return 1
  return 0
}

set_tools_venv_python() {
  root_dir="$1"
  TOOLS_VENV_PY=$(find_venv_python "$root_dir" ".venv-tools") || return 1
  return 0
}
