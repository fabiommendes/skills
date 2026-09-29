#!/usr/bin/env bash
# Install every skill and agent in this repository for the current user.
#
# Skills are copied with `npx skills`. Agents are symlinked into
# ~/.claude/agents, so edits in this repository take effect immediately.
set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
agents_dir="$HOME/.claude/agents"

echo "Installing skills..."
npx --yes skills add "$repo" --global --skill '*' --agent claude-code --yes

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
