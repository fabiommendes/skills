#!/usr/bin/env bash
# List English skills and agents whose Portuguese source changed after the
# translation.
#
# An English SKILL.md or AGENT.md records the commit of its pt-BR source in
# `metadata.translatedFrom`. The translation is stale when the last commit that
# touched the pt-BR directory is not that commit. Exit status 1 if any is stale.
set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$repo"
stale=0

while IFS= read -r manifest; do
    en_dir="$(dirname "$manifest")"
    from="$(sed -n '/^---$/,/^---$/s/^ *translatedFrom: *//p' "$manifest" | tr -d '"'"'"' ')"
    [[ -n "$from" ]] || continue

    case "$en_dir" in
        skills/*) pt_dir="pt-BR/${en_dir#skills/}" ;;
        agents/*) pt_dir="pt-BR/$en_dir" ;;
    esac
    if [[ ! -d "$pt_dir" ]]; then
        echo "missing  $en_dir: no source at $pt_dir"
        stale=1
        continue
    fi

    last="$(git log -1 --format=%H -- "$pt_dir")"
    if ! git cat-file -e "$from^{commit}" 2>/dev/null; then
        echo "unknown  $en_dir: translatedFrom $from is not in the history"
        stale=1
    elif [[ "$(git rev-parse "$from")" != "$last" ]]; then
        echo "stale    $en_dir"
        echo "         git diff ${from:0:12} -- $pt_dir"
        stale=1
    else
        echo "ok       $en_dir"
    fi
    if [[ -n "$(git status --porcelain -- "$pt_dir")" ]]; then
        echo "         $pt_dir has uncommitted changes"
    fi
done < <(find skills agents -type f \( -name SKILL.md -o -name AGENT.md \) | sort)

exit "$stale"
