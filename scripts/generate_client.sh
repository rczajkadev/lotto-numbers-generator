#!/bin/sh
set -e

root_dir=$(git rev-parse --show-toplevel)

. "$root_dir/scripts/venv.sh"
set_tools_venv_python "$root_dir"

openapi_url="${1:-https://func-lotto-api-test1.azurewebsites.net/api/openapi/1.json}"
output_path="${2:-$root_dir/lotto/api_client}"
download_path="$root_dir/build/openapi-client/lotto-api.json"
venv_bin=$(dirname "$TOOLS_VENV_PY")
venv_bin_win=$(cygpath -w "$venv_bin")

PATH="$venv_bin_win;$PATH"

mkdir -p "$(dirname "$download_path")"

echo "Downloading OpenAPI schema..."

curl -fsSL "$openapi_url" -o "$download_path"

echo "Generating API client..."

rm -rf "$output_path"

"$TOOLS_VENV_PY" -m openapi_python_client generate \
  --path "$download_path" \
  --meta none \
  --output-path "$output_path" \
  --overwrite

echo "API client generated in $output_path"
