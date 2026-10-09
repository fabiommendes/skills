"""Command line for recording audit findings and rendering the report.

Record JSON goes in on stdin, so multi-line snippets need no shell quoting:

    audit-findings -a webserver add finding <<'EOF'
    {"category": "idor", "severity": "high", ...}
    EOF
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from datetime import date
from pathlib import Path

from . import __version__
from .check import Checker, overlaps
from .log import LOG_NAME, Log, LogError, Record, State, Writer
from .schema import (
    CATEGORY_STATUSES,
    META_ID,
    RECORD_TYPES,
    REQUIRED_FIELDS,
    SEVERITIES,
    inventories,
    uncovered,
    validate_record,
    validate_report,
)

AUDITS_DIR = Path("docs/audits")
REPORT_NAME = "findings.json"


class UsageError(Exception):
    pass


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        return args.func(args)
    except (UsageError, LogError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="audit-findings", description=__doc__.splitlines()[0])
    p.add_argument("--version", action="version", version=__version__)
    where = p.add_mutually_exclusive_group()
    where.add_argument("-a", "--area", help="audit area; the log is docs/audits/AREA/findings.jsonl")
    where.add_argument("-d", "--dir", type=Path, help="directory holding findings.jsonl")
    p.add_argument("--agent", default=os.environ.get("AUDIT_AGENT") or None, help="who records (default: $AUDIT_AGENT)")
    p.add_argument("--root", type=Path, default=Path.cwd(), help="project directory for location checks (default: .)")
    sub = p.add_subparsers(required=True, metavar="COMMAND")
    kinds = [k for k in RECORD_TYPES if k != "meta"]

    c = sub.add_parser("init", help="create the log; optional meta JSON on stdin")
    c.set_defaults(func=cmd_init)
    c = sub.add_parser("import", help="create the log from an existing findings.json")
    c.add_argument("file", type=Path)
    c.set_defaults(func=cmd_import)
    c = sub.add_parser("add", help="add records from a JSON object or array on stdin; prints their ids")
    c.add_argument("kind", choices=kinds)
    c.set_defaults(func=cmd_add)
    c = sub.add_parser("update", help="merge a JSON object on stdin into a record; null deletes a field")
    c.add_argument("id", help="record id, or 'meta'")
    c.set_defaults(func=cmd_update)
    c = sub.add_parser("remove", help="remove records, saying why")
    c.add_argument("ids", nargs="+")
    c.add_argument("--reason", required=True, help="why, such as 'duplicate of F1' or 'code is not reachable'")
    c.set_defaults(func=cmd_remove)
    c = sub.add_parser("merge", help="fold a duplicate finding into another and remove it")
    c.add_argument("duplicate")
    c.add_argument("into")
    c.set_defaults(func=cmd_merge)
    c = sub.add_parser("accept", help="mark records as reviewed")
    c.add_argument("ids", nargs="+")
    c.set_defaults(func=cmd_accept)
    for name, status in (("start", "doing"), ("done", "done"), ("reopen", "todo")):
        c = sub.add_parser(name, help=f"mark categories as {status}")
        c.add_argument("ids", nargs="+")
        c.set_defaults(func=cmd_progress, status=status)
    c = sub.add_parser("status", help="summary of the audit so far")
    c.set_defaults(func=cmd_status)
    c = sub.add_parser("list", help="one line per record")
    c.add_argument("kind", nargs="?", choices=kinds)
    c.add_argument("--category")
    c.add_argument("--severity", choices=SEVERITIES)
    c.add_argument("--agent", dest="by", metavar="AGENT", help="only records this agent created")
    c.add_argument("--to-review", action="store_true", help="only records subagents created and nobody accepted")
    c.add_argument("--removed", action="store_true", help="list removed records and why")
    c.set_defaults(func=cmd_list)
    c = sub.add_parser("show", help="print records as JSON, with who changed them")
    c.add_argument("ids", nargs="+")
    c.set_defaults(func=cmd_show)
    c = sub.add_parser("coverage", help="list findings that no issue or no recommendation refers to")
    c.add_argument("--all", action="store_true", help="include findings of severity info")
    c.set_defaults(func=cmd_coverage)
    c = sub.add_parser("check", help="check every location and snippet against the source")
    c.set_defaults(func=cmd_check)
    c = sub.add_parser("build", help="validate and write findings.json")
    c.add_argument("--no-check", action="store_true", help="skip checking locations against the source")
    c.set_defaults(func=cmd_build)
    c = sub.add_parser("render", help="build, then write report.pdf, report.html, and issues.md")
    c.add_argument("file", nargs="?", type=Path, help="render this findings.json instead of the log")
    c.add_argument("--no-check", action="store_true", help="skip checking locations against the source")
    c.set_defaults(func=cmd_render)
    return p


# Commands ---------------------------------------------------------------------


def cmd_init(args: argparse.Namespace) -> int:
    if not (args.area or args.dir):
        raise UsageError("init needs --area or --dir")
    log = Log(directory(args))
    meta = {"lang": "en", "date": date.today().isoformat(), **read_stdin(optional=True)}
    log.create()
    with log.writing(args.agent) as writer:
        add_record(writer, "meta", meta, args.root, rid=META_ID)
    print(f"created {log.path}")
    return 0


def cmd_import(args: argparse.Namespace) -> int:
    data = json.loads(args.file.read_text(encoding="utf-8"))
    errors = validate_report(data, args.file.parent)
    if errors:
        raise UsageError(f"{args.file} has problems:\n" + "\n".join(f"  - {e}" for e in errors))
    log = Log(directory(args) if (args.area or args.dir) else args.file.parent)
    log.create()
    with log.writing(args.agent) as writer:
        meta = {k: data[k] for k in RECORD_TYPES["meta"].fields if k in data}
        writer.emit("add", META_ID, meta, "meta")
        for category in data["categories"]:
            writer.emit("add", category["id"], category, "category")
        for finding in data["findings"]:
            writer.emit("add", finding["id"], {k: v for k, v in finding.items() if k != "id"}, "finding")
        for kind, items in (
            ("strength", data["strengths"]),
            ("risk", [{"text": r} for r in data.get("risks", [])]),
            ("recommendation", data["recommendations"]),
            ("issue", data["issues"]),
        ):
            for item in items:
                writer.emit("add", writer.state.next_id(RECORD_TYPES[kind].prefix), item, kind)
        for n, table in enumerate(inventories(data), start=1):
            tid = f"inventory{n}"
            writer.emit(
                "add", tid, {"id": tid, "title": table.get("title", ""), "columns": table["columns"]}, "inventory"
            )
            for cells in table.get("rows", []):
                writer.emit("add", writer.state.next_id("ROW"), {"table": tid, "cells": cells}, "row")
        count = len(writer.events)
    print(f"created {log.path} with {count} records")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    items = read_stdin()
    items = items if isinstance(items, list) else [items]
    with open_log(args).writing(args.agent) as writer:
        added = [add_record(writer, args.kind, item, args.root, where=f"item {n}") for n, item in enumerate(items, 1)]
    for rid, warnings in added:
        print(rid)
        for warning in warnings:
            print(f"warning: {warning}")
    return 0


def cmd_update(args: argparse.Namespace) -> int:
    patch = read_stdin()
    if not isinstance(patch, dict):
        raise UsageError("update expects a JSON object on stdin")
    with open_log(args).writing(args.agent) as writer:
        record = get(writer.state, args.id)
        if record.kind in ("category", "inventory") and patch.get("id", record.id) != record.id:
            raise UsageError(f"cannot change the id of '{record.id}'; remove it and add a new one")
        merged = {k: v for k, v in {**record.data, **patch}.items() if v is not None}
        warnings = check_record(
            writer.state, record.kind, merged, args.root, record.id, writer.dir, overlap="location" in patch
        )
        writer.emit("update", record.id, patch)
    print(f"updated {record.id}")
    for warning in warnings:
        print(f"warning: {warning}")
    return 0


def cmd_remove(args: argparse.Namespace) -> int:
    with open_log(args).writing(args.agent) as writer:
        for rid in args.ids:
            get(writer.state, rid)
            if rid == META_ID:
                raise UsageError("cannot remove meta")
            referrers = writer.state.referrers(rid)
            if referrers:
                raise UsageError(f"{rid} is referenced by {', '.join(referrers)}; update or remove those first")
            writer.emit("remove", rid, reason=args.reason)
    print(f"removed {', '.join(args.ids)}")
    return 0


def cmd_merge(args: argparse.Namespace) -> int:
    with open_log(args).writing(args.agent) as writer:
        state = writer.state
        duplicate, into = get(state, args.duplicate), get(state, args.into)
        if duplicate.kind != "finding" or into.kind != "finding" or duplicate.id == into.id:
            raise UsageError("merge takes two different findings")
        for referrer in state.referrers(duplicate.id):
            refs = state.records[referrer].data["findings"]
            retargeted = list(dict.fromkeys(into.id if ref == duplicate.id else ref for ref in refs))
            writer.emit("update", referrer, {"findings": retargeted})
        writer.emit("remove", duplicate.id, reason=f"duplicate of {into.id}")
    print(f"merged {duplicate.id} into {into.id}")
    if duplicate.data["location"] != into.data["location"]:
        print(f"{duplicate.id} location: {duplicate.data['location']}")
        print(f"{into.id} location: {into.data['location']}")
        print(f"if {into.id} misses places {duplicate.id} cited, add them with `update {into.id}`")
    return 0


def cmd_accept(args: argparse.Namespace) -> int:
    with open_log(args).writing(args.agent) as writer:
        for rid in args.ids:
            if get(writer.state, rid).kind == "meta":
                raise UsageError("cannot accept meta")
            writer.emit("accept", rid)
    print(f"accepted {', '.join(args.ids)}")
    return 0


def cmd_progress(args: argparse.Namespace) -> int:
    with open_log(args).writing(args.agent) as writer:
        for rid in args.ids:
            record = get(writer.state, rid)
            if record.kind != "category":
                raise UsageError(f"{rid} is a {record.kind}, not a category")
            writer.emit("update", rid, {"status": args.status})
    print(f"{', '.join(args.ids)}: {args.status}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    log = open_log(args)
    with log.reading() as state:
        print(status_text(state, log))
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    with open_log(args).reading() as state:
        records = state.removed if args.removed else state.records
        for record in records.values():
            if record.kind == "meta" or (args.kind and record.kind != args.kind):
                continue
            if args.category and record.data.get("category") != args.category:
                continue
            if args.severity and record.data.get("severity") != args.severity:
                continue
            if args.by and record.creator != args.by:
                continue
            if args.to_review and not to_review(record):
                continue
            print(summary_line(record))
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    with open_log(args).reading() as state:
        records = [get(state, rid, removed=True) for rid in args.ids]
    for record in records:
        shown = {"id": record.id, "type": record.kind, **record.data}
        if record.reason:
            shown["removed"] = record.reason
        shown["accepted"] = record.accepted
        shown["history"] = [{k: v for k, v in vars(c).items() if v} for c in record.history]
        print(json.dumps(shown, ensure_ascii=False, indent=2))
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    with open_log(args).reading() as state:
        report = state.to_report()
    return report_check(report, args.root)


def cmd_coverage(args: argparse.Namespace) -> int:
    with open_log(args).reading() as state:
        report = state.to_report()
    lines = coverage_lines(report, args.all)
    for line in lines:
        print(line)
    if lines:
        return 1
    scope = "every finding" if args.all else "every finding above info"
    print(f"OK: {scope} is in an issue and a recommendation.")
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    path = build(args)
    if path is None:
        return 1
    print(f"wrote {path}")
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    if args.file:
        path = args.file.resolve()
        data = json.loads(path.read_text(encoding="utf-8"))
        if not report_valid(data, path, None if args.no_check else args.root):
            return 1
    else:
        built = build(args)
        if built is None:
            return 1
        path = built
        data = json.loads(path.read_text(encoding="utf-8"))

    from .render import render_all

    for out in render_all(data, path.parent):
        print(f"wrote {out}")
    for line in coverage_lines(data):
        print(f"warning: {line}")
    counts = Counter(f["severity"] for f in data["findings"])
    summary = ", ".join(f"{counts[s]} {s}" for s in SEVERITIES if counts[s])
    print(f"{len(data['findings'])} findings ({summary or 'none'}), {len(data['issues'])} issues")
    return 0


# Helpers ----------------------------------------------------------------------


def coverage_lines(report: dict, include_info: bool = False) -> list[str]:
    missing = uncovered(report, include_info)
    return [f"findings in no {section[:-1]}: {', '.join(ids)}" for section, ids in missing.items() if ids]


def directory(args: argparse.Namespace) -> Path:
    if args.dir:
        return args.dir
    if args.area:
        return AUDITS_DIR / args.area
    found = sorted(Path.cwd().glob(f"{AUDITS_DIR}/*/{LOG_NAME}"))
    if len(found) == 1:
        return found[0].parent
    if not found:
        raise UsageError(f"no {AUDITS_DIR}/*/{LOG_NAME} here; pass --area or --dir")
    raise UsageError(f"several logs found ({', '.join(str(f.parent) for f in found)}); pass --area or --dir")


def open_log(args: argparse.Namespace) -> Log:
    return Log(directory(args))


def read_stdin(optional: bool = False) -> dict | list:
    text = "" if optional and sys.stdin.isatty() else sys.stdin.read()
    if not text.strip():
        if optional:
            return {}
        raise UsageError("expected JSON on stdin")
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise UsageError(f"stdin is not valid JSON: {exc}") from exc


def get(state: State, rid: str, removed: bool = False) -> Record:
    if rid in state.records:
        return state.records[rid]
    if removed and rid in state.removed:
        return state.removed[rid]
    if rid in state.removed:
        raise UsageError(f"{rid} was removed ({state.removed[rid].reason}); `show {rid}` prints it")
    raise UsageError(f"no record '{rid}'; run `audit-findings list` to see the ids")


def to_review(record: Record) -> bool:
    """Findings and strengths a subagent recorded that nobody accepted since their last change."""
    return record.kind in ("finding", "strength") and record.creator is not None and not record.accepted


def add_record(
    writer: Writer, kind: str, item: object, root: Path, where: str = "", rid: str | None = None
) -> tuple[str, list[str]]:
    """Validate one record, give it an id, and emit it. Returns the id and any warnings."""
    prefix = f"{where}: " if where else ""
    rtype = RECORD_TYPES[kind]
    if kind == "risk" and isinstance(item, str):
        item = {"text": item}
    if not isinstance(item, dict):
        raise UsageError(f"{prefix}expected a JSON object")
    if rid is None and rtype.keyed:
        rid = item.get("id")
        if not rid:
            raise UsageError(f"{prefix}a {kind} needs an 'id'")
        if rid in writer.state.records:
            raise UsageError(f"{prefix}'{rid}' already exists; use `update {rid}` to change it")
    elif rid is None:
        if "id" in item:
            raise UsageError(f"{prefix}{kind} ids are assigned by the log; omit 'id'")
        rid = writer.state.next_id(rtype.prefix)
    try:
        warnings = check_record(writer.state, kind, item, root, rid, writer.dir)
    except UsageError as exc:
        raise UsageError(f"{prefix}{exc}") from exc
    writer.emit("add", rid, item, kind)
    return rid, warnings


def check_record(
    state: State, kind: str, data: dict, root: Path, rid: str, base_dir: Path, overlap: bool = True
) -> list[str]:
    """Raise UsageError if the record is invalid; return warnings worth showing.

    With `overlap`, warn about findings that share lines with this one.
    """
    errors = validate_record(kind, data, state.ids(), base_dir, state.columns())
    checker = Checker(root)
    if not errors and kind == "finding":
        checker.check_finding(rid, data)
    elif not errors and kind == "strength":
        checker.check_strength(rid, data)
    errors += checker.errors
    if errors:
        raise UsageError("; ".join(errors))
    warnings = list(checker.warnings)
    if kind == "finding" and overlap:
        for other in state.of("finding"):
            shared = other.id != rid and overlaps(data["location"], other.data["location"])
            if shared:
                warnings.append(
                    f"{rid} overlaps {other.id} at {shared} ({other.data['title']}); "
                    f"if it is the same defect, run `merge {rid} {other.id}`"
                )
        for other in state.removed.values():
            shared = other.kind == "finding" and overlaps(data["location"], other.data["location"])
            if shared:
                warnings.append(
                    f"{rid} overlaps {other.id} at {shared}, removed earlier ({other.reason}); "
                    f"if the same reason applies, remove {rid}"
                )
    return warnings


def build(args: argparse.Namespace) -> Path | None:
    """Write findings.json from the log; print the problems and return None if it is not valid."""
    log = open_log(args)
    with log.reading() as state:
        report = state.to_report()
    path = log.dir / REPORT_NAME
    if not report_valid(report, path, None if args.no_check else args.root):
        return None
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def report_valid(report: dict, path: Path, root: Path | None) -> bool:
    """Validate the report, and check its locations against the source unless `root` is None."""
    errors = validate_report(report, path.parent)
    if errors:
        print(f"error: the report has {len(errors)} problem(s):", file=sys.stderr)
        for error in errors:
            hint = " (set it with `update meta`)" if error.startswith("missing required field") else ""
            print(f"  - {error}{hint}", file=sys.stderr)
        return False
    return root is None or report_check(report, root) == 0


def report_check(report: dict, root: Path) -> int:
    checker = Checker(root)
    checker.check(report)
    for warning in checker.warnings:
        print(f"warning: {warning}")
    for error in checker.errors:
        print(f"error: {error}", file=sys.stderr)
    if checker.errors:
        print(f"{len(checker.errors)} problem(s): fix the location or snippet with `update`, or remove the finding.")
        return 1
    print(f"OK: {len(report['findings'])} findings, locations and snippets match the source.")
    return 0


# Output -----------------------------------------------------------------------


def summary_line(record: Record) -> str:
    line = record_line(record.kind, record.id, record.data)
    if record.reason:
        line += f"  -- removed: {record.reason}"
    return line + (f"  (by {record.creator})" if record.creator else "")


def record_line(kind: str, rid: str, data: dict) -> str:
    if kind == "finding":
        return f"{rid}  {data['severity']:<8}  {data['category']:<14}  {data['title']}  [{data['location']}]"
    if kind == "category":
        mark = "n/a" if data.get("applies") is False else data.get("status", "todo")
        return f"{rid:<14}  {mark:<5}  {data['title']}"
    if kind == "strength":
        return f"{rid}  {data.get('category', '-'):<14}  {data['text']}"
    if kind == "recommendation":
        refs = ", ".join(data.get("findings", []))
        return f"{rid}  {data['priority']}  {data['text']}" + (f"  ({refs})" if refs else "")
    if kind == "issue":
        return f"{rid}  {data['title']}  ({', '.join(data['findings'])})"
    if kind == "inventory":
        return f"{rid}  {data.get('title', '')}  columns: {', '.join(map(str, data['columns']))}"
    if kind == "row":
        return f"{rid}  {data['table']}  {' | '.join(map(str, data['cells']))}"
    return f"{rid}  {data.get('text', '')}"


def status_text(state: State, log: Log) -> str:
    meta = state.records[META_ID].data if META_ID in state.records else {}
    findings = state.of("finding")
    counts = Counter(f.data["severity"] for f in findings)
    by_severity = ", ".join(f"{counts[s]} {s}" for s in SEVERITIES if counts[s]) or "none"
    lines = [f"{log.path}  ({meta.get('project', '?')}, lang {meta.get('lang', 'en')})"]
    missing = [k for k in REQUIRED_FIELDS if k in RECORD_TYPES["meta"].fields and not meta.get(k)]
    if missing:
        lines.append(f"meta missing: {', '.join(missing)}")
    totals = {kind: len(state.of(kind)) for kind in ("strength", "risk", "recommendation", "issue", "row")}
    lines.append(
        f"findings: {len(findings)} ({by_severity}); strengths: {totals['strength']}; risks: {totals['risk']}; "
        f"recommendations: {totals['recommendation']}; issues: {totals['issue']}; inventory rows: {totals['row']}"
    )

    lines.append("categories:")
    per_category = Counter(f.data["category"] for f in findings)
    strengths = Counter(s.data.get("category") for s in state.of("strength"))
    progress = Counter()
    width = max([14, *(len(c.id) for c in state.of("category"))])
    for category in state.of("category"):
        data = category.data
        mark = "n/a" if data.get("applies") is False else data.get("status", "todo")
        progress[mark] += 1
        who = f"  ({category.agent})" if mark == "doing" and category.agent else ""
        lines.append(
            f"  {category.id:<{width}} {mark:<5} {per_category[category.id]} findings, "
            f"{strengths[category.id]} strengths{who}"
        )
    if not state.of("category"):
        lines.append("  none; add them with `add category`")
    pending = [s for s in CATEGORY_STATUSES if s != "done" and progress[s]]
    if pending:
        lines.append("progress: " + ", ".join(f"{progress[s]} {s}" for s in pending))

    if findings:
        lines.append("findings:")
        lines += [f"  {summary_line(f)}" for f in findings]
    if state.of("issue") or state.of("recommendation"):
        lines += coverage_lines(state.to_report())
    pairs = []
    for i, a in enumerate(findings):
        for b in findings[i + 1 :]:
            shared = overlaps(a.data["location"], b.data["location"])
            if shared:
                pairs.append(f"{a.id}/{b.id} at {shared}")
    if pairs:
        lines.append(f"overlapping findings (possible duplicates): {'; '.join(pairs)}")
    pending_review = [f"{r.id} ({r.creator})" for r in state.records.values() if to_review(r)]
    if pending_review:
        lines.append(f"to review: {', '.join(pending_review)}")
    if state.removed:
        lines.append(f"removed: {', '.join(f'{r.id} ({r.reason})' for r in state.removed.values())}")
    return "\n".join(lines)
