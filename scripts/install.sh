#!/bin/sh

set -e

root_dir=$(git rev-parse --show-toplevel)
branch_name=$(git rev-parse --abbrev-ref HEAD)
env_file="$root_dir/.env"
venv_helper="$root_dir/scripts/venv.sh"
dist_dir="$root_dir/dist"
build_dir="$root_dir/build"

if [ "$branch_name" != "main" ]; then
  echo "Skipping install because the current branch is not main."
  exit 0
fi

if [ ! -f "$env_file" ]; then
  echo ".env file not found at $env_file."
  exit 1
fi

if [ ! -f "$venv_helper" ]; then
  echo "Virtual environment helper not found at $venv_helper."
  exit 1
fi

echo "Loading environment variables..."

. "$env_file"
. "$venv_helper"

set_venv_python "$root_dir"

if [ -z "${CLI_APP_NAME:-}" ]; then
  echo "CLI_APP_NAME environment variable is not set."
  exit 1
fi

if [ -z "${CLI_APP_INSTALLATION_DIR:-}" ]; then
  echo "CLI_APP_INSTALLATION_DIR environment variable is not set."
  exit 1
fi

echo "Creating executable..."

rm -rf "$dist_dir"

"$VENV_PY" -m PyInstaller "$root_dir/lotto/__main__.py" \
  --name "$CLI_APP_NAME" \
  --exclude-module pyinstaller \
  --distpath "$dist_dir" \
  --workpath "$build_dir" \
  --log-level WARN

echo "Removing existing installation at $CLI_APP_INSTALLATION_DIR..."

rm -rf "$CLI_APP_INSTALLATION_DIR/$CLI_APP_NAME"

echo "Copying executable to $CLI_APP_INSTALLATION_DIR..."

cp "$root_dir/config.yaml" "$dist_dir/$CLI_APP_NAME/config.yaml"
cp -r "$dist_dir/$CLI_APP_NAME" "$CLI_APP_INSTALLATION_DIR"
