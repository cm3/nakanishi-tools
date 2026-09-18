#!/bin/sh
set -eu

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
source_csv="$repo_dir/../../work/2026-09-03-sample-iiif-registration/nakanishi_import_9records_reviewed_comma.csv"

cd "$repo_dir"
python scripts/build_pilot.py \
  --csv "$source_csv" \
  --base-url https://cm3.github.io/nakanishi-tools
