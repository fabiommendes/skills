import io
import json
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pytest

from audit_findings.cli import main

SOURCE = """\
def get_invoice(invoice_id):
    user = current_user()
    return db.query(Invoice).filter(Invoice.id == invoice_id).first()


def list_users():
    return db.query(User).filter(User.tenant == tenant()).all()
"""

META = {"title": "Security Audit Report", "project": "acme", "scope": "src/", "methodology": "Read every route."}


def finding(**overrides):
    data = {
        "category": "idor",
        "severity": "critical",
        "title": "GET /invoices/{id} does not check the tenant",
        "location": "src/api.py:1-3",
        "snippet": "return db.query(Invoice).filter(Invoice.id == invoice_id).first()",
        "description": "No tenant filter.",
        "impact": "Read other tenants' invoices.",
        "fix": "Filter by tenant.",
    }
    return {**data, **overrides}


@pytest.fixture
def project(tmp_path, monkeypatch):
    (tmp_path / "src").mkdir()
    (tmp_path / "src/api.py").write_text(SOURCE)
    monkeypatch.chdir(tmp_path)
    return tmp_path


def run(monkeypatch, capsys, *args, stdin=None):
    monkeypatch.setattr(sys, "stdin", io.StringIO("" if stdin is None else json.dumps(stdin)))
    code = main(["-a", "web", *args])
    out, err = capsys.readouterr()
    return code, out, err


@pytest.fixture
def audit(project, monkeypatch, capsys):
    def call(*args, stdin=None):
        return run(monkeypatch, capsys, *args, stdin=stdin)

    assert call("init", stdin=META)[0] == 0
    assert call("add", "category", stdin=[{"id": "idor", "title": "IDOR"}, {"id": "xss", "title": "XSS"}])[0] == 0
    return call


def log_lines(project: Path) -> list[dict]:
    return [json.loads(line) for line in (project / "docs/audits/web/findings.jsonl").read_text().splitlines()]


def test_init_ignores_the_lock_file(audit, project):
    assert (project / "docs/audits/web/.gitignore").read_text() == "findings.jsonl.lock\n"


def test_add_assigns_sequential_ids(audit):
    code, out, _ = audit("add", "finding", stdin=[finding(), finding(location="src/api.py:6-7", snippet="")])
    assert code == 0
    assert out.split() == ["F1", "F2"]


def test_add_rejects_snippet_missing_from_source(audit, project):
    before = len(log_lines(project))
    code, _, err = audit("add", "finding", stdin=finding(snippet="return Invoice.objects.all()"))
    assert code == 1
    assert "snippet line not found" in err
    assert len(log_lines(project)) == before


def test_add_rejects_snippet_outside_cited_lines(audit):
    code, _, err = audit("add", "finding", stdin=finding(location="src/api.py:7"))
    assert code == 1
    assert "outside the cited lines" in err


def test_batch_is_atomic(audit, project):
    before = len(log_lines(project))
    code, _, err = audit("add", "finding", stdin=[finding(), finding(category="nope")])
    assert code == 1
    assert "item 2" in err and "category 'nope' does not exist" in err
    assert len(log_lines(project)) == before


def test_add_rejects_unknown_fields_and_explicit_ids(audit):
    assert "unknown field 'sevrity'" in audit("add", "finding", stdin={**finding(), "sevrity": "x"})[2]
    assert "omit 'id'" in audit("add", "finding", stdin={**finding(), "id": "F9"})[2]


def test_add_warns_about_overlapping_findings(audit):
    audit("add", "finding", stdin=finding())
    code, out, _ = audit("add", "finding", stdin=finding(title="Same thing again", location="src/api.py:3"))
    assert code == 0
    assert "F2 overlaps F1 at src/api.py:3-3" in out


def test_update_warns_about_overlaps_only_when_the_location_changes(audit):
    audit("add", "finding", stdin=[finding(), finding(title="Other", location="src/api.py:6-7", snippet="")])
    assert "overlaps" not in audit("update", "F1", stdin={"fix": "Filter by tenant id."})[1]
    assert "F2 overlaps F1" in audit("update", "F2", stdin={"location": "src/api.py:2-3"})[1]


def test_update_merges_and_null_deletes(audit):
    audit("add", "finding", stdin=finding(conditions="Any user."))
    assert audit("update", "F1", stdin={"severity": "high", "conditions": None})[0] == 0
    shown = json.loads(audit("show", "F1")[1])
    assert shown["severity"] == "high"
    assert "conditions" not in shown


def test_update_validates_the_merged_record(audit):
    audit("add", "finding", stdin=finding())
    code, _, err = audit("update", "F1", stdin={"severity": "urgent"})
    assert code == 1
    assert "'severity' is 'urgent'" in err


def test_remove_refuses_referenced_records(audit):
    audit("add", "finding", stdin=finding())
    audit("add", "recommendation", stdin={"priority": "P1", "text": "Fix it.", "findings": ["F1"]})
    code, _, err = audit("remove", "F1")
    assert code == 1
    assert "referenced by REC1" in err


def test_removed_ids_are_not_reused(audit):
    audit("add", "finding", stdin=finding())
    audit("remove", "F1")
    assert audit("add", "finding", stdin=finding())[1].split() == ["F2"]


def test_status_shows_progress_and_findings(audit):
    audit("add", "finding", stdin=finding())
    audit("--agent", "a1", "start", "idor")
    audit("done", "xss")
    out = audit("status")[1]
    assert "findings: 1 (1 critical)" in out
    assert "idor           doing 1 findings, 0 strengths  (a1)" in out
    assert "xss            done" in out
    assert "F1  critical" in out


def test_render_writes_the_deliverables(audit, project):
    audit("add", "finding", stdin=finding())
    audit("add", "strength", stdin={"category": "idor", "text": "Users are scoped.", "evidence": "src/api.py:6-7"})
    audit("add", "risk", stdin=["Manual tenant filters."])
    audit("add", "recommendation", stdin={"priority": "P1", "text": "Fix it.", "findings": ["F1"]})
    audit("add", "issue", stdin={"title": "[Security] IDOR", "findings": ["F1"], "summary": "S", "acceptance": ["A"]})
    audit("add", "inventory", stdin={"id": "routes", "title": "Routes", "columns": ["Method", "Path"]})
    audit(
        "add", "row", stdin=[{"table": "routes", "cells": ["GET", "/x"]}, {"table": "routes", "cells": ["GET", "/x"]}]
    )
    code, out, err = audit("render")
    assert code == 0, err
    out_dir = project / "docs/audits/web"
    for name in ("findings.json", "report.pdf", "report.html", "issues.md"):
        assert (out_dir / name).is_file()
    report = json.loads((out_dir / "findings.json").read_text())
    assert report["findings"][0]["id"] == "F1"
    assert report["risks"] == ["Manual tenant filters."]
    assert report["inventory"] == [{"title": "Routes", "columns": ["Method", "Path"], "rows": [["GET", "/x"]]}]
    assert "1 findings (1 critical), 1 issues" in out


def test_build_reports_missing_meta(project, monkeypatch, capsys):
    run(monkeypatch, capsys, "init", stdin={"project": "acme"})
    code, _, err = run(monkeypatch, capsys, "build")
    assert code == 1
    assert "missing required field 'title' (set it with `update meta`)" in err


def test_import_round_trips(audit, project, monkeypatch, capsys):
    audit("add", "finding", stdin=finding())
    audit("add", "issue", stdin={"title": "T", "findings": ["F1"], "summary": "S", "acceptance": ["A"]})
    audit("add", "recommendation", stdin={"priority": "P1", "text": "R"})
    audit("build")
    original = json.loads((project / "docs/audits/web/findings.json").read_text())
    copy = project / "old/findings.json"
    copy.parent.mkdir()
    copy.write_text(json.dumps(original))
    monkeypatch.setattr(sys, "stdin", io.StringIO(""))
    assert main(["-d", "old", "import", str(copy)]) == 0
    assert main(["-d", "old", "build"]) == 0
    assert json.loads(copy.read_text()) == original


def test_directory_is_detected_when_there_is_one_log(audit, monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO(""))
    assert main(["status"]) == 0
    assert "docs/audits/web/findings.jsonl" in capsys.readouterr().out


def add_from_process(args: tuple[str, int]) -> str:
    cwd, n = args
    record = json.dumps(finding(title=f"Finding {n}", location="src/api.py", snippet=""))
    result = subprocess.run(
        [sys.executable, "-m", "audit_findings", "-a", "web", "add", "finding"],
        input=record,
        capture_output=True,
        text=True,
        cwd=cwd,
        check=True,
    )
    return result.stdout.split()[0]


def test_parallel_writers_get_unique_ids(audit, project):
    with ProcessPoolExecutor(max_workers=8) as pool:
        ids = list(pool.map(add_from_process, [(str(project), n) for n in range(16)]))
    assert sorted(ids, key=lambda i: int(i[1:])) == [f"F{n}" for n in range(1, 17)]
    assert sum(1 for e in log_lines(project) if e.get("type") == "finding") == 16
