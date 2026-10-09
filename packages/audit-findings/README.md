# audit-findings

Records the findings of a code or interface audit in an append-only log and
renders them into a PDF report, an HTML report, and ready-to-paste GitHub
issues. It is the tool behind the `audit-*` skills in
[fabiommendes/skills](https://github.com/fabiommendes/skills).

The log lets several agents record findings in parallel, and an audit continue
across sessions, without any of them reading or rewriting the whole report:

- every write goes through the command line, which holds a file lock, assigns
  ids, and validates the record before appending it;
- a finding's location and snippet are checked against the source when it is
  recorded, so mistakes surface to the agent that made them;
- `status` prints a compact summary to resume from, including the findings
  subagents recorded that nobody has reviewed yet;
- `--agent NAME` labels who made each change, and removed records keep the
  reason, so a later session does not record them again.

## Usage

```bash
uvx audit-findings --help
```

Records are JSON objects passed on stdin:

```bash
audit-findings -a webserver init <<'EOF'
{"lang": "en", "title": "Security Audit Report", "project": "acme-api"}
EOF

audit-findings -a webserver add category <<'EOF'
[{"id": "idor", "title": "IDOR"},
 {"id": "xss", "title": "XSS", "applies": false, "note": "no HTML rendering"}]
EOF

audit-findings -a webserver add finding <<'EOF'
{"category": "idor", "severity": "critical",
 "title": "GET /invoices/{id} does not check the tenant",
 "location": "src/api/invoices.py:42-47",
 "snippet": "return db.query(Invoice).filter(Invoice.id == invoice_id).first()",
 "description": "...", "impact": "...", "fix": "..."}
EOF
# prints the new id: F1

audit-findings -a webserver status
audit-findings -a webserver render
```

The log is `docs/audits/<area>/findings.jsonl`. `--area` and `--dir` may be
omitted when the project holds a single log.

| Command | Purpose |
|---|---|
| `init` | Create the log; optional `meta` JSON on stdin. |
| `import FILE` | Create the log from an existing `findings.json`. |
| `add KIND` | Add a record or an array of records; prints the ids. |
| `update ID` | Merge a JSON object into a record; `null` deletes a field. |
| `remove ID... --reason TEXT` | Remove records nothing else refers to, saying why. |
| `merge DUPLICATE KEPT` | Move references to the kept finding and remove the duplicate. |
| `accept ID...` | Mark records as reviewed; a later update clears the mark. |
| `start`, `done`, `reopen` | Track progress per category. |
| `status`, `list`, `show` | Read the log; `show` includes who changed a record and when. |
| `check` | Check every location and snippet against the source again. |
| `build` | Validate and write `findings.json`. |
| `render [FILE]` | Build, then write `report.pdf`, `report.html`, `issues.md`. |

Record kinds: `category`, `finding`, `strength`, `risk`, `recommendation`,
`issue`, `inventory` (a coverage table), and `row` (a row of one). The fields
are described in the `audit-report` skill.

## Log format

Each line of `findings.jsonl` is one event:

```json
{"op": "add", "type": "finding", "id": "F3", "data": {"...": "..."}, "agent": "a1", "ts": "2026-10-08T12:00:00+00:00"}
{"op": "update", "id": "F3", "data": {"severity": "high"}, "ts": "..."}
{"op": "remove", "id": "F3", "reason": "duplicate of F1", "ts": "..."}
{"op": "accept", "id": "F4", "ts": "..."}
```

Replaying the events gives the current records; `build` turns them into
`findings.json`. Removed ids are never reused.
