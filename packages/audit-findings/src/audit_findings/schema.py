"""The findings file format: record types, their fields, and validation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

SEVERITIES = ["critical", "high", "medium", "low", "info"]
LANGUAGES = ["en", "pt"]
REQUIRED_FIELDS = [
    "title",
    "project",
    "date",
    "scope",
    "methodology",
    "categories",
    "findings",
    "strengths",
    "recommendations",
    "issues",
]
FINDING_FIELDS = ["id", "category", "severity", "title", "location", "description", "impact", "fix"]
CATEGORY_STATUSES = ["todo", "doing", "done"]


@dataclass(frozen=True)
class RecordType:
    name: str
    fields: tuple[str, ...]
    required: tuple[str, ...]
    # Generated ids are `prefix` plus a number; without a prefix, the record carries its own `id`.
    prefix: str = ""

    @property
    def keyed(self) -> bool:
        return not self.prefix


RECORD_TYPES = {
    t.name: t
    for t in [
        RecordType("meta", ("lang", "title", "project", "date", "scope", "methodology"), ()),
        RecordType("category", ("id", "title", "applies", "note", "status"), ("id", "title")),
        RecordType(
            "finding",
            (
                "category",
                "severity",
                "title",
                "location",
                "snippet",
                "language",
                "description",
                "impact",
                "fix",
                "conditions",
                "screenshot",
                "mechanical",
            ),
            ("category", "severity", "title", "location", "description", "impact", "fix"),
            "F",
        ),
        RecordType("strength", ("category", "text", "evidence"), ("text",), "S"),
        RecordType("risk", ("text",), ("text",), "R"),
        RecordType("recommendation", ("priority", "text", "findings"), ("priority", "text"), "REC"),
        RecordType(
            "issue",
            ("title", "labels", "findings", "summary", "acceptance"),
            ("title", "findings", "summary", "acceptance"),
            "I",
        ),
        RecordType("inventory", ("id", "title", "columns"), ("id", "columns")),
        RecordType("row", ("table", "cells"), ("table", "cells"), "ROW"),
    ]
}
META_ID = "meta"


def validate_record(
    kind: str, record: dict, ids: dict[str, set[str]], base_dir: Path, columns: dict[str, int]
) -> list[str]:
    """Check one record on its own and against the ids already recorded.

    `ids` maps each record type to its live ids; `columns` maps each inventory
    table to its column count.
    """
    rtype = RECORD_TYPES[kind]
    errors = [
        f"unknown field '{key}'; expected one of {list(rtype.fields)}" for key in record if key not in rtype.fields
    ]
    errors += [f"missing '{key}'" for key in rtype.required if record.get(key) in (None, "", [])]
    if errors:
        return errors

    if kind == "meta" and "lang" in record and record["lang"] not in LANGUAGES:
        errors.append(f"'lang' is '{record['lang']}'; expected one of {LANGUAGES}")
    if kind == "category" and record.get("status", "todo") not in CATEGORY_STATUSES:
        errors.append(f"'status' is '{record['status']}'; expected one of {CATEGORY_STATUSES}")
    if kind == "finding":
        if record["severity"] not in SEVERITIES:
            errors.append(f"'severity' is '{record['severity']}'; expected one of {SEVERITIES}")
        screenshot = record.get("screenshot")
        if screenshot and not (base_dir / screenshot).is_file():
            errors.append(f"screenshot '{screenshot}' does not exist relative to {base_dir}")
        if not isinstance(record.get("mechanical", False), bool):
            errors.append("'mechanical' must be true or false")
    if kind in ("finding", "strength") and record.get("category") and record["category"] not in ids["category"]:
        errors.append(f"category '{record['category']}' does not exist; add it first")
    if kind in ("recommendation", "issue"):
        refs = record.get("findings", [])
        if not isinstance(refs, list):
            errors.append("'findings' must be a list of finding ids")
        else:
            errors += [f"finding '{ref}' does not exist" for ref in refs if ref not in ids["finding"]]
    if kind == "issue":
        for key in ("labels", "acceptance"):
            if key in record and not isinstance(record[key], list):
                errors.append(f"'{key}' must be a list")
    if kind == "inventory" and not isinstance(record["columns"], list):
        errors.append("'columns' must be a list")
    if kind == "row":
        if record["table"] not in columns:
            errors.append(f"inventory '{record['table']}' does not exist; add it first")
        elif not isinstance(record["cells"], list):
            errors.append("'cells' must be a list")
        elif len(record["cells"]) != columns[record["table"]]:
            n = columns[record["table"]]
            errors.append(f"row has {len(record['cells'])} cells; inventory '{record['table']}' has {n} columns")
    return errors


def validate_report(data: object, base_dir: Path) -> list[str]:
    """Check a whole findings file, as the renderer reads it."""
    if not isinstance(data, dict):
        return ["the top level must be a JSON object"]
    errors = [f"missing required field '{key}'" for key in REQUIRED_FIELDS if key not in data]
    if errors:
        return errors

    lang = data.get("lang", "en")
    if lang not in LANGUAGES:
        errors.append(f"'lang' is '{lang}'; expected one of {LANGUAGES}")

    category_ids = set()
    for i, category in enumerate(data["categories"]):
        for key in ("id", "title"):
            if key not in category:
                errors.append(f"categories[{i}] is missing '{key}'")
        category_ids.add(category.get("id"))

    finding_ids = set()
    for i, finding in enumerate(data["findings"]):
        where = f"findings[{i}] ({finding.get('id', '?')})"
        missing = [key for key in FINDING_FIELDS if not finding.get(key)]
        if missing:
            errors.append(f"{where} is missing {', '.join(missing)}")
        if finding.get("id") in finding_ids:
            errors.append(f"{where} reuses id '{finding['id']}'")
        finding_ids.add(finding.get("id"))
        if finding.get("severity") not in SEVERITIES:
            errors.append(f"{where} has severity '{finding.get('severity')}'; expected one of {SEVERITIES}")
        if finding.get("category") not in category_ids:
            errors.append(f"{where} has category '{finding.get('category')}', which is not in 'categories'")
        screenshot = finding.get("screenshot")
        if screenshot and not (base_dir / screenshot).is_file():
            errors.append(f"{where} has screenshot '{screenshot}', which does not exist relative to {base_dir}")
        if not isinstance(finding.get("mechanical", False), bool):
            errors.append(f"{where} has 'mechanical' that is not true or false")

    for i, strength in enumerate(data["strengths"]):
        if not strength.get("text"):
            errors.append(f"strengths[{i}] is missing 'text'")
        if strength.get("category") and strength["category"] not in category_ids:
            errors.append(f"strengths[{i}] has category '{strength['category']}', which is not in 'categories'")

    for section in ("recommendations", "issues"):
        for i, item in enumerate(data[section]):
            for ref in item.get("findings", []):
                if ref not in finding_ids:
                    errors.append(f"{section}[{i}] refers to finding '{ref}', which does not exist")
    for i, rec in enumerate(data["recommendations"]):
        for key in ("priority", "text"):
            if not rec.get(key):
                errors.append(f"recommendations[{i}] is missing '{key}'")
    for i, issue in enumerate(data["issues"]):
        for key in ("title", "findings", "summary", "acceptance"):
            if not issue.get(key):
                errors.append(f"issues[{i}] is missing '{key}'")

    inventory = data.get("inventory")
    if inventory is not None and not isinstance(inventory, (dict, list)):
        errors.append("'inventory' must be an object or a list of objects")
    for n, table in enumerate(inventories(data)):
        name = "inventory" if isinstance(inventory, dict) else f"inventory[{n}]"
        columns = table.get("columns", [])
        for i, row in enumerate(table.get("rows", [])):
            if len(row) != len(columns):
                errors.append(f"{name}.rows[{i}] has {len(row)} cells; 'columns' has {len(columns)}")
    return errors


def uncovered(data: dict, include_info: bool = False) -> dict[str, list[str]]:
    """Finding ids that no issue and no recommendation refers to, keyed by `issues` and `recommendations`.

    Findings of severity `info` are left out unless `include_info` is set.
    Mechanical findings need no issue: the renderer files them in one batch.
    """
    wanted = [f for f in data["findings"] if include_info or f["severity"] != "info"]
    result = {}
    for section in ("issues", "recommendations"):
        referenced = {ref for item in data[section] for ref in item.get("findings", [])}
        exempt = section == "issues"
        result[section] = [
            f["id"] for f in wanted if f["id"] not in referenced and not (exempt and f.get("mechanical"))
        ]
    return result


def inventories(data: dict) -> list[dict]:
    """The coverage tables: `inventory` may hold one table or a list of tables."""
    inventory = data.get("inventory")
    tables = inventory if isinstance(inventory, list) else [inventory]
    return [table for table in tables if isinstance(table, dict)]
