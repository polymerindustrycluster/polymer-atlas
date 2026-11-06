#!/bin/sh
set -eu
attributes=$(git rev-parse --git-path info/attributes)
mkdir -p "$(dirname "$attributes")"
touch "$attributes"
grep -qxF 'data/*.csv merge=atlascsv' "$attributes" || printf '%s\n' 'data/*.csv merge=atlascsv' >> "$attributes"
git config --local merge.atlascsv.name 'Atlas keyed CSV merge'
git config --local merge.atlascsv.driver 'python3 "$(git rev-parse --show-toplevel)/scripts/csv_merge_driver.py" %O %A %B %P'
