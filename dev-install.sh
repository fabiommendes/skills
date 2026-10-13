#!/usr/bin/env bash
# Link this checkout's skills and agents for local development.
set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skills_dir="$HOME/.agents/skills"
agents_dir="$HOME/.claude/agents"

echo "Linking skills into $skills_dir..."
mkdir -p "$skills_dir"

while IFS= read -r -d '' manifest; do
    src="$(dirname "$manifest")"
    name="$(basename "$src")"
    dest="$skills_dir/$name"

    if [[ -e "$dest" && ! -L "$dest" ]]; then
        echo "  skip $name: $dest exists and is not a symlink" >&2
        continue
    fi
    ln -sfn "$src" "$dest"
    echo "  $name"
done < <(find "$repo/skills" -type f -name SKILL.md -print0)

while IFS= read -r -d '' dest; do
    if [[ ! -e "$dest" ]]; then
        rm -- "$dest"
        echo "  removed broken link $(basename "$dest")"
    fi
done < <(find "$skills_dir" -mindepth 1 -maxdepth 1 -type l -print0)

echo "Linking agents into $agents_dir..."
mkdir -p "$agents_dir"

for src in "$repo"/agents/*/; do
    src="${src%/}"
    name="$(basename "$src")"
    dest="$agents_dir/$name"

    if [[ -e "$dest" && ! -L "$dest" ]]; then
        echo "  skip $name: $dest exists and is not a symlink" >&2
        continue
    fi
    ln -sfn "$src" "$dest"
    echo "  $name"
done

# Remove links to agents that no longer exist in this repository.
for dest in "$agents_dir"/*; do
    if [[ -L "$dest" && ! -e "$dest" && "$(readlink "$dest")" == "$repo/agents/"* ]]; then
        rm "$dest"
        echo "  removed stale link $(basename "$dest")"
    fi
done
