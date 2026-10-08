"""The append-only findings log and the state it replays into.

Each line of `findings.jsonl` is one event:

    {"op": "add", "type": "finding", "id": "F3", "data": {...}, "agent": "a1", "ts": "..."}
    {"op": "update", "id": "F3", "data": {"severity": "high"}, ...}
    {"op": "remove", "id": "F3", ...}

Updates merge into the record; a `null` value deletes the field. Writers hold
an exclusive lock on `findings.jsonl.lock` from reading the log to appending,
so ids stay unique across parallel agents.
"""

from __future__ import annotations

import json
import os
import re
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from filelock import FileLock

from .schema import META_ID, RECORD_TYPES

LOG_NAME = "findings.jsonl"


class LogError(Exception):
    pass


@dataclass
class Record:
    kind: str
    id: str
    data: dict
    agent: str | None = None


@dataclass
class State:
    records: dict[str, Record] = field(default_factory=dict)
    # Every id ever used, including removed ones, so numbers are never reused.
    used: set[str] = field(default_factory=set)

    def apply(self, event: dict) -> None:
        op, rid = event["op"], event["id"]
        if op == "add":
            self.records[rid] = Record(event["type"], rid, dict(event["data"]), event.get("agent"))
            self.used.add(rid)
        elif op == "update":
            record = self.records[rid]
            for key, value in event["data"].items():
                if value is None:
                    record.data.pop(key, None)
                else:
                    record.data[key] = value
            if event.get("agent"):
                record.agent = event["agent"]
        elif op == "remove":
            del self.records[rid]

    def of(self, kind: str) -> list[Record]:
        return [r for r in self.records.values() if r.kind == kind]

    def ids(self) -> dict[str, set[str]]:
        result: dict[str, set[str]] = {kind: set() for kind in RECORD_TYPES}
        for record in self.records.values():
            result[record.kind].add(record.id)
        return result

    def columns(self) -> dict[str, int]:
        return {r.id: len(r.data.get("columns", [])) for r in self.of("inventory")}

    def next_id(self, prefix: str) -> str:
        pattern = re.compile(rf"^{re.escape(prefix)}(\d+)$")
        numbers = [int(m[1]) for rid in self.used if (m := pattern.match(rid))]
        return f"{prefix}{max(numbers, default=0) + 1}"

    def referrers(self, rid: str) -> list[str]:
        """Ids of the records that point to `rid`."""
        target = self.records[rid]
        result = []
        for record in self.records.values():
            data = record.data
            if (
                target.kind == "category"
                and data.get("category") == rid
                and record.kind in ("finding", "strength")
                or target.kind == "finding"
                and rid in data.get("findings", [])
                or target.kind == "inventory"
                and record.kind == "row"
                and data.get("table") == rid
            ):
                result.append(record.id)
        return result

    def to_report(self) -> dict:
        """The findings file the renderer reads."""
        meta = self.records[META_ID].data if META_ID in self.records else {}
        report: dict = {"lang": "en", **meta}
        report["categories"] = [{k: v for k, v in r.data.items() if k != "status"} for r in self.of("category")]
        report["findings"] = [{"id": r.id, **r.data} for r in self.of("finding")]
        report["strengths"] = [r.data for r in self.of("strength")]
        report["risks"] = [r.data["text"] for r in self.of("risk")]
        report["recommendations"] = [r.data for r in self.of("recommendation")]
        report["issues"] = [r.data for r in self.of("issue")]
        tables = []
        for table in self.of("inventory"):
            rows: list[list] = []
            for row in self.of("row"):
                if row.data["table"] == table.id and row.data["cells"] not in rows:
                    rows.append(row.data["cells"])
            tables.append({"title": table.data.get("title", ""), "columns": table.data["columns"], "rows": rows})
        if tables:
            report["inventory"] = tables
        return report


class Log:
    def __init__(self, directory: Path):
        self.dir = directory
        self.path = directory / LOG_NAME
        self.lock = FileLock(str(self.path) + ".lock")

    def exists(self) -> bool:
        return self.path.is_file()

    def read(self) -> State:
        """Replay the log. Hold the lock while calling, or a half-written line may appear."""
        state = State()
        if not self.exists():
            raise LogError(f"{self.path} does not exist; run `audit-findings init` first")
        with self.path.open(encoding="utf-8") as file:
            for number, line in enumerate(file, start=1):
                if not line.strip():
                    continue
                try:
                    state.apply(json.loads(line))
                except (json.JSONDecodeError, KeyError) as exc:
                    raise LogError(
                        f"{self.path}:{number} is not a valid event ({exc}); fix or delete that line"
                    ) from exc
        return state

    @contextmanager
    def reading(self) -> Iterator[State]:
        with self.lock:
            yield self.read()

    @contextmanager
    def writing(self, agent: str | None = None) -> Iterator[Writer]:
        """Lock the log, replay it, and append the events written inside the block.

        Events are appended only if the block finishes without an exception.
        """
        with self.lock:
            writer = Writer(self.read(), agent, self.dir)
            yield writer
            if writer.events:
                lines = "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in writer.events)
                with self.path.open("a", encoding="utf-8") as file:
                    file.write(lines)
                    file.flush()
                    os.fsync(file.fileno())

    def create(self) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)
        with self.lock:
            if self.exists():
                raise LogError(f"{self.path} already exists")
            self.path.touch()
        ignore = self.dir / ".gitignore"
        if not ignore.exists():
            ignore.write_text(f"{self.path.name}.lock\n", encoding="utf-8")


class Writer:
    """Collects events and applies them to the replayed state as they are written."""

    def __init__(self, state: State, agent: str | None, directory: Path):
        self.state = state
        self.agent = agent
        self.dir = directory
        self.events: list[dict] = []

    def emit(self, op: str, rid: str, data: dict | None = None, kind: str | None = None) -> None:
        event: dict = {"op": op, "id": rid}
        if kind:
            event["type"] = kind
        if data is not None:
            event["data"] = data
        if self.agent:
            event["agent"] = self.agent
        event["ts"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        self.state.apply(event)
        self.events.append(event)
