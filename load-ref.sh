#!/usr/bin/env bash
# Clone or update the third-party skill repositories kept under ref/ for
# reference. Repos are shallow clones; ref/ is git-ignored.
set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ref_dir="$repo/ref"

# <directory>=<git url>
refs=(
    "mattpocock-skills=https://github.com/mattpocock/skills"
    "cursor-plugins=https://github.com/cursor/plugins"
)

mkdir -p "$ref_dir"

for entry in "${refs[@]}"; do
    name="${entry%%=*}"
    url="${entry#*=}"
    dest="$ref_dir/$name"

    if [[ -d "$dest/.git" ]]; then
        echo "Updating $name..."
        git -C "$dest" fetch --depth 1 origin
        git -C "$dest" reset --hard '@{upstream}'
    else
        echo "Cloning $name..."
        git clone --depth 1 "$url" "$dest"
    fi
done
