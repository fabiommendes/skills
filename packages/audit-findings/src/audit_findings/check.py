"""Check that the code locations and snippets cited by findings exist in the source.

Each `path:line` or `path:start-end` in a finding's `location` must name an
existing file and lines inside it, and every line of `snippet` must appear in
the cited lines. Strength `evidence` gets the same location check. Locations
that are not file paths (routes, screens) are skipped.

Snippets may elide code with `...` (whole lines or inside a line), mask secrets
with `****`, and join a statement split over up to three source lines.
Whitespace is ignored when comparing.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

# Lines a snippet line may sit outside the cited range before it counts as wrong.
TOLERANCE = 2
# Source lines joined when matching a snippet line, for statements split over lines.
JOIN = 3
WILDCARDS = re.compile(r"\*\*\*\*|\.\.\.|…")
ELISIONS = {"...", "…", "# ...", "// ...", "/* ... */", "<!-- ... -->", "-- ..."}
PATH_LINE = re.compile(r"^(?P<path>[^\s:]+?):(?P<lines>\d+(?:-\d+)?(?:,\d+(?:-\d+)?)*)$")
SEPARATORS = re.compile(r"[\s;]+|,\s+")
STRIP = "`'\"()[]<>"


@dataclass
class Ref:
    path: str
    ranges: list[tuple[int, int]]  # empty: the whole file


def parse_location(location: str) -> tuple[list[Ref], list[str]]:
    """Split a location string into file references and unparsed tokens."""
    refs: list[Ref] = []
    skipped: list[str] = []
    for raw in SEPARATORS.split(location):
        token = raw.strip(STRIP).rstrip(".,")
        if not token:
            continue
        match = PATH_LINE.match(token)
        if match:
            ranges = []
            for part in match["lines"].split(","):
                start, _, end = part.partition("-")
                ranges.append((int(start), int(end or start)))
            refs.append(Ref(match["path"], ranges))
        elif looks_like_file(token):
            refs.append(Ref(token, []))
        else:
            skipped.append(token)
    return refs, skipped


def looks_like_file(token: str) -> bool:
    """A relative path with a directory or an extension, not a route like /users/{id}."""
    if token.startswith("/") or "{" in token or "://" in token:
        return False
    return "/" in token or bool(re.search(r"\.[A-Za-z0-9]{1,8}$", token))


def overlaps(a: str, b: str) -> str | None:
    """The first file range two locations share, as `path:start-end`, or None."""
    refs_b, _ = parse_location(b)
    for ref_a in parse_location(a)[0]:
        for ref_b in refs_b:
            if ref_a.path != ref_b.path:
                continue
            if not ref_a.ranges or not ref_b.ranges:
                return ref_a.path
            for start_a, end_a in ref_a.ranges:
                for start_b, end_b in ref_b.ranges:
                    if start_a <= end_b and start_b <= end_a:
                        return f"{ref_a.path}:{max(start_a, start_b)}-{min(end_a, end_b)}"
    return None


def normalize(line: str) -> str:
    return re.sub(r"\s+", "", line)


def line_pattern(line: str) -> re.Pattern[str]:
    """Match a snippet line against source, letting **** (masked) and ... (elided) stand for any text."""
    parts = [re.escape(normalize(part)) for part in WILDCARDS.split(line)]
    return re.compile(".*?".join(parts))


def window(lines: list[str], number: int) -> str:
    """Source line `number` (1-based) joined with the next JOIN - 1 lines, whitespace removed."""
    return "".join(normalize(text) for text in lines[number - 1 : number - 1 + JOIN])


def read_lines(path: Path) -> list[str] | None:
    try:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()
    except (OSError, UnicodeError):
        return None


class Checker:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.cache: dict[str, list[str] | None] = {}
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def lines(self, path: str) -> list[str] | None:
        if path not in self.cache:
            file = (self.root / path).resolve()
            ok = file.is_file() and file.is_relative_to(self.root)
            self.cache[path] = read_lines(file) if ok else None
        return self.cache[path]

    def check(self, data: dict) -> None:
        for finding in data.get("findings", []):
            self.check_finding(f"finding {finding.get('id', '?')}", finding)
        for index, strength in enumerate(data.get("strengths", []), start=1):
            if isinstance(strength, dict):
                self.check_strength(f"strength {index}", strength)

    def check_finding(self, where: str, finding: dict) -> None:
        refs, skipped = parse_location(str(finding.get("location", "")))
        valid = self.check_refs(where, refs)
        snippet = finding.get("snippet")
        if not snippet:
            return
        if valid:
            self.check_snippet(where, snippet, valid)
        elif not refs:
            self.warnings.append(f"{where}: snippet not checked; location has no file path ({' '.join(skipped)})")

    def check_strength(self, where: str, strength: dict) -> None:
        if strength.get("evidence"):
            refs, _ = parse_location(str(strength["evidence"]))
            self.check_refs(where, refs)

    def check_refs(self, where: str, refs: list[Ref]) -> list[Ref]:
        """Report missing files and out-of-range lines; return the valid refs."""
        valid = []
        for ref in refs:
            lines = self.lines(ref.path)
            if lines is None:
                self.errors.append(f"{where}: file not found: {ref.path} (relative to {self.root})")
                continue
            bad = [(s, e) for s, e in ref.ranges if s < 1 or e < s or e > len(lines)]
            for start, end in bad:
                self.errors.append(f"{where}: {ref.path} has {len(lines)} lines; {start}-{end} is out of range")
            if not bad:
                valid.append(ref)
        return valid

    def check_snippet(self, where: str, snippet: str, refs: list[Ref]) -> None:
        wanted = [line for line in snippet.splitlines() if normalize(line) and line.strip() not in ELISIONS]
        for line in wanted:
            pattern = line_pattern(line)
            if self.found_in_range(pattern, refs):
                continue
            elsewhere = self.found_anywhere(pattern, refs)
            text = line.strip()
            if elsewhere:
                self.errors.append(f"{where}: snippet line found at {elsewhere}, outside the cited lines: {text}")
            else:
                self.errors.append(f"{where}: snippet line not found in the cited files: {text}")

    def found_in_range(self, pattern: re.Pattern[str], refs: list[Ref]) -> bool:
        for ref in refs:
            lines = self.lines(ref.path) or []
            spans = ref.ranges or [(1, len(lines))]
            for start, end in spans:
                lo, hi = max(1, start - TOLERANCE), min(len(lines), end + TOLERANCE)
                if any(pattern.search(window(lines, i)) for i in range(lo, hi + 1)):
                    return True
        return False

    def found_anywhere(self, pattern: re.Pattern[str], refs: list[Ref]) -> str | None:
        for ref in refs:
            lines = self.lines(ref.path) or []
            numbers = range(1, len(lines) + 1)
            # Prefer a single-line match so the reported line is exact.
            number = next((n for n in numbers if pattern.search(normalize(lines[n - 1]))), None)
            number = number or next((n for n in numbers if pattern.search(window(lines, n))), None)
            if number:
                return f"{ref.path}:{number}"
        return None
