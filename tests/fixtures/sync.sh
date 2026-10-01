#!/usr/bin/env bash
# Prepare the audit fixtures outside this repository, so that audit runs see
# neither this repository nor the ground truth in tests/ground-truth/.
#
# Usage: tests/fixtures/sync.sh [dest]   (default: /tmp/audit-fixtures)
#
# - External fixtures (external.tsv) are fetched at their pinned commit.
# - Planted fixtures (planted/<name>/) are copied and committed into a fresh
#   git repository, so audits can use git history and git status.
# Existing fixtures are reset to their pristine state.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dest="${1:-/tmp/audit-fixtures}"
mkdir -p "$dest"

while IFS=$'\t' read -r name url commit; do
  [[ -z "$name" || "$name" == \#* ]] && continue
  dir="$dest/$name"
  if [[ ! -d "$dir/.git" ]]; then
    git init --quiet "$dir"
    git -C "$dir" remote add origin "$url"
  fi
  if ! git -C "$dir" cat-file -e "$commit^{commit}" 2>/dev/null; then
    git -C "$dir" fetch --quiet --depth 1 origin "$commit"
  fi
  git -C "$dir" checkout --quiet --force --detach "$commit"
  git -C "$dir" clean --quiet -fdx
  echo "$name: $commit"
done < "$here/external.tsv"

if [[ -d "$here/planted" ]]; then
  for src in "$here"/planted/*/; do
    name="$(basename "$src")"
    dir="$dest/$name"
    rm -rf "$dir"
    cp -r "$src" "$dir"
    git -C "$dir" init --quiet
    git -C "$dir" add -A
    git -C "$dir" -c user.name=fixture -c user.email=fixture@example.com \
      commit --quiet -m "Fixture $name"
    echo "$name: planted"
  done
fi
