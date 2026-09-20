#!/bin/sh
set -eu

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
source_csv="$repo_dir/../../work/2026-09-03-sample-iiif-registration/nakanishi_import_9records_reviewed_comma.csv"
registration_csv="$repo_dir/../../work/2026-09-20-v3-choice-image3-rollout/nakanishi_import_9records_v3_choice_image3.csv"

cd "$repo_dir"
python scripts/build_pilot.py \
  --csv "$source_csv" \
  --base-url https://cm3.github.io/nakanishi-tools

python scripts/build_collection_choice3.py \
  --csv "$source_csv" \
  --site-url https://cm3.github.io/nakanishi-tools \
  --registration-output "$registration_csv"
