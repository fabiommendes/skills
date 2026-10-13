#!/usr/bin/env bash
# Link this checkout's skills and agents for local development.
#
# Usage: dev-install.sh [--lang pt|en]
#
# Skills and agents exist in pt-BR/ (the source) and, when mature, in skills/
# and agents/ (English, published). --lang picks which version to link when
# both exist; the other version is the fallback. Default: pt.
set -euo pipefail

lang=pt
while [[ $# -gt 0 ]]; do
    case "$1" in
        --lang) lang="${2:-}"; shift 2 ;;
        --lang=*) lang="${1#--lang=}"; shift ;;
        *) echo "unknown argument: $1" >&2; exit 2 ;;
    esac
done
[[ "$lang" == pt || "$lang" == en ]] || { echo "--lang must be pt or en" >&2; exit 2; }

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skills_dir="$HOME/.agents/skills"
agents_dir="$HOME/.claude/agents"

# link SRC DEST: replace DEST with a symlink to SRC, unless DEST is a real file.
# rm before ln: uutils `ln -sfn` fails on a broken link under a symlinked dir.
link() {
    local src="$1" dest="$2"
    if [[ -e "$dest" && ! -L "$dest" ]]; then
        echo "  skip $(basename "$dest"): $dest exists and is not a symlink" >&2
        return
    fi
    [[ -L "$dest" ]] && rm -- "$dest"
    ln -s "$src" "$dest"
}

# pick PT_DIR EN_DIR: print the directory to link, by language preference.
pick() {
    local pt="$1" en="$2" first second
    if [[ "$lang" == pt ]]; then first="$pt" second="$en"; else first="$en" second="$pt"; fi
    if [[ -n "$first" ]]; then echo "$first"; else echo "$second"; fi
}

declare -A pt_skills en_skills
while IFS= read -r -d '' manifest; do
    src="$(dirname "$manifest")"; pt_skills["$(basename "$src")"]="$src"
done < <(find "$repo/pt-BR" -path "$repo/pt-BR/agents" -prune -o -type f -name SKILL.md -print0 2>/dev/null)
while IFS= read -r -d '' manifest; do
    src="$(dirname "$manifest")"; en_skills["$(basename "$src")"]="$src"
done < <(find "$repo/skills" -type f -name SKILL.md -print0)

echo "Linking skills into $skills_dir (prefer $lang)..."
mkdir -p "$skills_dir"
for name in $(printf '%s\n' "${!pt_skills[@]}" "${!en_skills[@]}" | sort -u); do
    src="$(pick "${pt_skills[$name]:-}" "${en_skills[$name]:-}")"
    link "$src" "$skills_dir/$name"
    echo "  $name -> ${src#"$repo/"}"
done

while IFS= read -r -d '' dest; do
    if [[ ! -e "$dest" ]]; then
        rm -- "$dest"
        echo "  removed broken link $(basename "$dest")"
    fi
done < <(find "$skills_dir" -mindepth 1 -maxdepth 1 -type l -print0)

echo "Linking agents into $agents_dir (prefer $lang)..."
mkdir -p "$agents_dir"
for name in $( { ls "$repo/pt-BR/agents" 2>/dev/null; ls "$repo/agents"; } | sort -u); do
    pt=""; en=""
    [[ -f "$repo/pt-BR/agents/$name/AGENT.md" ]] && pt="$repo/pt-BR/agents/$name"
    [[ -f "$repo/agents/$name/AGENT.md" ]] && en="$repo/agents/$name"
    src="$(pick "$pt" "$en")"
    [[ -n "$src" ]] || continue
    link "$src" "$agents_dir/$name"
    echo "  $name -> ${src#"$repo/"}"
done

# Remove links to agents that no longer exist in this repository.
for dest in "$agents_dir"/*; do
    if [[ -L "$dest" && ! -e "$dest" && "$(readlink "$dest")" == "$repo/"* ]]; then
        rm "$dest"
        echo "  removed stale link $(basename "$dest")"
    fi
done
