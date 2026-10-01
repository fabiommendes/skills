#!/usr/bin/env python3
"""Render an audit findings file into a PDF report and a Markdown file of issues.

Usage:
    uv run --with reportlab --with pillow python render_report.py FINDINGS_JSON

Writes report.pdf, report.html, and issues.md next to FINDINGS_JSON. The file format is
described in the audit-report skill's SKILL.md.
"""

from __future__ import annotations

import base64
import html
import json
import re
import sys
import textwrap
from collections import Counter
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.graphics.charts.barcharts import HorizontalBarChart
from reportlab.graphics.charts.doughnut import Doughnut
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

SEVERITIES = ["critical", "high", "medium", "low", "info"]
COLORS = {
    "critical": "#B91C1C",
    "high": "#EA580C",
    "medium": "#D97706",
    "low": "#2563EB",
    "info": "#6B7280",
    "strength": "#059669",
}
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

# A4 width (21 cm) minus 2 cm margins on each side.
CONTENT_WIDTH = 17 * cm
# Characters per line that fit CONTENT_WIDTH in an 8 pt monospace font.
MONO_WRAP = 95

LABELS = {
    "en": {
        "date": "Date",
        "scope": "Scope",
        "methodology": "Methodology",
        "summary": "Executive summary",
        "total": "Total findings",
        "by_severity": "Findings by severity",
        "by_category": "Findings by category",
        "no_findings": "No findings.",
        "strengths_risks": "Strengths and weaknesses",
        "strengths": "Strengths",
        "risks": "Central risks",
        "details": "Detailed findings",
        "severity": "Severity",
        "location": "Location",
        "description": "Description",
        "impact": "Impact",
        "fix": "Suggested fix",
        "conditions": "Exploitability conditions",
        "evidence": "Evidence",
        "not_applicable": "Not applicable",
        "category_clean": "No findings in this category.",
        "recommendations": "Prioritized recommendations",
        "issues": "GitHub issues",
        "issues_intro": "Each block below is a complete issue, ready to paste.",
        "problem": "Problem",
        "acceptance": "Acceptance criteria",
        "labels": "Labels",
        "coverage": "Appendix: coverage",
        "page": "Page",
        "findings_ref": "Findings",
        "copy": "Copy",
        "copied": "Copied",
    },
    "pt": {
        "date": "Data",
        "scope": "Escopo",
        "methodology": "Metodologia",
        "summary": "Resumo executivo",
        "total": "Total de achados",
        "by_severity": "Achados por severidade",
        "by_category": "Achados por categoria",
        "no_findings": "Nenhum achado.",
        "strengths_risks": "Pontos fortes e fracos",
        "strengths": "Pontos fortes",
        "risks": "Riscos centrais",
        "details": "Achados detalhados",
        "severity": "Severidade",
        "location": "Local",
        "description": "Descrição",
        "impact": "Impacto",
        "fix": "Correção sugerida",
        "conditions": "Condições de exploração",
        "evidence": "Evidência",
        "not_applicable": "Não se aplica",
        "category_clean": "Nenhum achado nesta categoria.",
        "recommendations": "Recomendações priorizadas",
        "issues": "Issues do GitHub",
        "issues_intro": "Cada bloco abaixo é uma issue completa, pronta para colar.",
        "problem": "Problema",
        "acceptance": "Critérios de aceite",
        "labels": "Labels",
        "coverage": "Apêndice: cobertura",
        "page": "Página",
        "findings_ref": "Achados",
        "copy": "Copiar",
        "copied": "Copiado",
    },
}


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    findings_path = Path(argv[1]).resolve()
    try:
        data = json.loads(findings_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"error: {findings_path} does not exist", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"error: {findings_path} is not valid JSON: {exc}", file=sys.stderr)
        return 1

    errors = validate(data, findings_path.parent)
    if errors:
        print(f"error: {findings_path} has {len(errors)} problem(s):", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    labels = LABELS[data.get("lang", "en")]
    out_dir = findings_path.parent
    report = prepare(data)
    (out_dir / "issues.md").write_text(render_issues(data, labels), encoding="utf-8")
    (out_dir / "report.html").write_text(render_html(data, report, labels, out_dir), encoding="utf-8")
    render_pdf(data, report, labels, out_dir / "report.pdf", out_dir)

    counts = report["counts"]
    summary = ", ".join(f"{counts[s]} {s}" for s in SEVERITIES if counts[s])
    for name in ("report.pdf", "report.html", "issues.md"):
        print(f"wrote {out_dir / name}")
    print(f"{len(data['findings'])} findings ({summary or 'none'}), {len(data['issues'])} issues")
    return 0


def prepare(data: dict) -> dict:
    """Derive what every renderer needs from a validated findings file."""
    by_category: dict[str, list] = {c["id"]: [] for c in data["categories"]}
    for finding in sorted(data["findings"], key=lambda f: SEVERITIES.index(f["severity"])):
        by_category[finding["category"]].append(finding)
    return {
        "heading": f"{data['title']}: {data['project']}",
        "counts": Counter(f["severity"] for f in data["findings"]),
        "counts_by_category": {cid: Counter(f["severity"] for f in fs) for cid, fs in by_category.items()},
        "by_category": by_category,
        "titles": {c["id"]: c["title"] for c in data["categories"]},
        "recommendations": sorted(data["recommendations"], key=lambda r: r["priority"]),
    }


# Validation -----------------------------------------------------------------


def validate(data: object, base_dir: Path) -> list[str]:
    if not isinstance(data, dict):
        return ["the top level must be a JSON object"]
    errors = [f"missing required field '{key}'" for key in REQUIRED_FIELDS if key not in data]
    if errors:
        return errors

    lang = data.get("lang", "en")
    if lang not in LABELS:
        errors.append(f"'lang' is '{lang}'; expected one of {sorted(LABELS)}")

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
    if inventory is not None:
        columns = inventory.get("columns", [])
        for i, row in enumerate(inventory.get("rows", [])):
            if len(row) != len(columns):
                errors.append(f"inventory.rows[{i}] has {len(row)} cells; 'columns' has {len(columns)}")
    return errors


# Issues ---------------------------------------------------------------------


def render_issues(data: dict, labels: dict) -> str:
    return "\n\n".join(issue_blocks(data, labels)) + "\n"


def issue_blocks(data: dict, labels: dict) -> list[str]:
    findings = {f["id"]: f for f in data["findings"]}
    blocks = []
    for n, issue in enumerate(data["issues"], start=1):
        related = [findings[ref] for ref in issue["findings"]]
        severities = sorted({f["severity"] for f in related}, key=SEVERITIES.index)
        issue_labels = issue.get("labels") or [*severities]
        multiple = len(related) > 1

        lines = [f"--- ISSUE {n} ---", f"# {issue['title']}", ""]
        lines += [f"**{labels['labels']}:** {', '.join(issue_labels)}", ""]
        lines += [f"## {labels['problem']}", "", issue["summary"], ""]
        lines += [f"## {labels['evidence']}", ""]
        for f in related:
            lines.append(f"- `{f['location']}`: {f['title']}")
            if f.get("snippet"):
                lines += ["", f"  ```{f.get('language', '')}"]
                lines += [f"  {line}" for line in f["snippet"].rstrip().splitlines()]
                lines.append("  ```")
        lines.append("")
        for heading, key in ((labels["impact"], "impact"), (labels["fix"], "fix")):
            lines += [f"## {heading}", ""]
            if multiple:
                lines += [f"- **{f['title']}:** {f[key]}" for f in related]
            else:
                lines.append(related[0][key])
            lines.append("")
        lines += [f"## {labels['acceptance']}", ""]
        lines += [f"- [ ] {item}" for item in issue["acceptance"]]
        lines += ["", f"--- END ISSUE {n} ---"]
        blocks.append("\n".join(lines))
    return blocks


# PDF ------------------------------------------------------------------------


def register_fonts() -> tuple[str, str, str]:
    """Use DejaVu when installed, for Unicode coverage; fall back to the PDF base fonts."""
    search_dirs = [
        Path("/usr/share/fonts/truetype/dejavu"),
        Path("/usr/share/fonts/TTF"),
        Path("/usr/share/fonts/dejavu"),
        Path("/usr/local/share/fonts"),
        Path.home() / ".local/share/fonts",
        Path("/Library/Fonts"),
        Path.home() / "Library/Fonts",
    ]
    wanted = {
        "DejaVuSans": "DejaVuSans.ttf",
        "DejaVuSans-Bold": "DejaVuSans-Bold.ttf",
        "DejaVuSansMono": "DejaVuSansMono.ttf",
    }
    found = {}
    for name, filename in wanted.items():
        for directory in search_dirs:
            path = directory / filename
            if path.is_file():
                found[name] = path
                break
    if len(found) == len(wanted):
        for name, path in found.items():
            pdfmetrics.registerFont(TTFont(name, str(path)))
        pdfmetrics.registerFontFamily("DejaVuSans", normal="DejaVuSans", bold="DejaVuSans-Bold")
        return "DejaVuSans", "DejaVuSans-Bold", "DejaVuSansMono"
    return "Helvetica", "Helvetica-Bold", "Courier"


def make_styles(regular: str, bold: str, mono: str) -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    body = ParagraphStyle("body", parent=base["BodyText"], fontName=regular, fontSize=9.5, leading=13)
    return {
        "body": body,
        "small": ParagraphStyle("small", parent=body, fontSize=8.5, leading=11),
        "cover_title": ParagraphStyle(
            "cover_title", parent=body, fontName=bold, fontSize=24, leading=30, spaceAfter=18
        ),
        "h1": ParagraphStyle("h1", parent=body, fontName=bold, fontSize=16, leading=20, spaceBefore=6, spaceAfter=10),
        "h2": ParagraphStyle("h2", parent=body, fontName=bold, fontSize=12, leading=15, spaceBefore=10, spaceAfter=6),
        "h3": ParagraphStyle("h3", parent=body, fontName=bold, fontSize=10, leading=13, spaceBefore=6, spaceAfter=3),
        "chip": ParagraphStyle(
            "chip", parent=body, fontName=bold, fontSize=8, leading=10, textColor=colors.white, alignment=TA_CENTER
        ),
        "mono": ParagraphStyle("mono", parent=body, fontName=mono, fontSize=8, leading=10),
        "mono_font": mono,
    }


def inline(text: str, mono: str) -> str:
    """Escape text for a Paragraph, render `code` spans, and keep line breaks."""
    out = escape(str(text))
    out = re.sub(r"`([^`]+)`", lambda m: f'<font face="{mono}">{m.group(1)}</font>', out)
    return out.replace("\n", "<br/>")


def paragraphs(text: str, style: ParagraphStyle, mono: str, label: str = "") -> list:
    """Split text on blank lines into Paragraphs; prefix the first with a bold label."""
    chunks = [chunk.strip() for chunk in re.split(r"\n\s*\n", str(text)) if chunk.strip()]
    result = [Paragraph(inline(chunk, mono), style) for chunk in chunks]
    if label and chunks:
        result[0] = Paragraph(f"<b>{escape(label)}:</b> {inline(chunks[0], mono)}", style)
    return result


def wrapped(text: str, style: ParagraphStyle) -> Preformatted:
    lines = []
    for line in str(text).rstrip().splitlines() or [""]:
        lines += textwrap.wrap(line, MONO_WRAP, replace_whitespace=False, drop_whitespace=False) or [""]
    return Preformatted("\n".join(lines), style)


def chip(severity: str, styles: dict) -> Table:
    table = Table([[Paragraph(severity.upper(), styles["chip"])]], colWidths=[2.0 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(COLORS[severity])),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return table


def grid_table(rows: list[list], col_widths: list[float], header: bool = True) -> Table:
    table = Table(rows, colWidths=col_widths, repeatRows=1 if header else 0)
    style = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D1D5DB")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if header:
        style.append(("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F3F4F6")))
    table.setStyle(TableStyle(style))
    return table


def severity_chart(counts: Counter, font: str) -> Drawing:
    present = [s for s in SEVERITIES if counts[s]]
    drawing = Drawing(CONTENT_WIDTH / 2, 6 * cm)
    chart = Doughnut()
    chart.x, chart.y, chart.width, chart.height = 0.5 * cm, 0.5 * cm, 5 * cm, 5 * cm
    chart.data = [counts[s] for s in present]
    chart.innerRadiusFraction = 0.55
    chart.simpleLabels = 0
    chart.slices.strokeColor = colors.white
    for i, severity in enumerate(present):
        chart.slices[i].fillColor = colors.HexColor(COLORS[severity])
    drawing.add(chart)
    legend = Legend()
    legend.x, legend.y = 6 * cm, 4.5 * cm
    legend.fontName = font
    legend.fontSize = 8
    legend.colorNamePairs = [(colors.HexColor(COLORS[s]), f"{s} ({counts[s]})") for s in present]
    drawing.add(legend)
    return drawing


def category_chart(data: dict, report: dict, font: str) -> Drawing:
    counts_by_category = report["counts_by_category"]
    categories = [c for c in data["categories"] if sum(counts_by_category[c["id"]].values())]
    height = max(3 * cm, (len(categories) * 0.7 + 1) * cm)
    drawing = Drawing(CONTENT_WIDTH, height)
    chart = HorizontalBarChart()
    chart.x, chart.y = 6 * cm, 0.5 * cm
    chart.width, chart.height = CONTENT_WIDTH - 7 * cm, height - 1 * cm
    chart.categoryAxis.style = "stacked"
    # Reverse so the first category is drawn at the top.
    ordered = list(reversed(categories))
    chart.categoryAxis.categoryNames = [c["title"][:40] for c in ordered]
    chart.categoryAxis.labels.fontName = font
    chart.categoryAxis.labels.fontSize = 8
    chart.valueAxis.labels.fontName = font
    chart.valueAxis.labels.fontSize = 8
    chart.valueAxis.valueMin = 0
    largest = max((sum(counts_by_category[c["id"]].values()) for c in categories), default=1)
    chart.valueAxis.valueStep = max(1, largest // 5)
    chart.data = [[counts_by_category[c["id"]][s] for c in ordered] for s in SEVERITIES]
    for i, severity in enumerate(SEVERITIES):
        chart.bars[i].fillColor = colors.HexColor(COLORS[severity])
        chart.bars[i].strokeColor = None
    drawing.add(chart)
    return drawing


def render_pdf(data: dict, report: dict, labels: dict, out_path: Path, base_dir: Path) -> None:
    regular, bold, mono = register_fonts()
    # The PDF base fonts have no check mark glyph.
    check = "✓" if regular == "DejaVuSans" else "+"
    styles = make_styles(regular, bold, mono)
    body, small, h1, h2, h3 = (styles[k] for k in ("body", "small", "h1", "h2", "h3"))
    heading = report["heading"]
    findings = data["findings"]
    counts = report["counts"]

    story: list = []

    # Cover.
    story += [Spacer(1, 4 * cm), Paragraph(inline(heading, mono), styles["cover_title"])]
    story += [Paragraph(f"<b>{labels['date']}:</b> {inline(data['date'], mono)}", body), Spacer(1, 6)]
    story += [Paragraph(f"<b>{labels['scope']}:</b> {inline(data['scope'], mono)}", body), Spacer(1, 12)]
    story += [Paragraph(labels["methodology"], h2), *paragraphs(data["methodology"], body, mono)]
    story.append(PageBreak())

    # Executive summary.
    story.append(Paragraph(labels["summary"], h1))
    count_rows = [[Paragraph(f"<b>{labels['severity']}</b>", body), Paragraph("#", body)]]
    count_rows += [[chip(s, styles), Paragraph(str(counts[s]), body)] for s in SEVERITIES]
    count_rows.append([Paragraph(f"<b>{labels['total']}</b>", body), Paragraph(f"<b>{len(findings)}</b>", body)])
    story.append(grid_table(count_rows, [3 * cm, 2 * cm]))
    story.append(Paragraph(labels["by_severity"], h2))
    story.append(severity_chart(counts, regular) if findings else Paragraph(labels["no_findings"], body))
    story.append(Paragraph(labels["by_category"], h2))
    story.append(category_chart(data, report, regular) if findings else Paragraph(labels["no_findings"], body))
    story.append(PageBreak())

    # Strengths and weaknesses.
    story.append(Paragraph(labels["strengths_risks"], h1))
    story.append(Paragraph(labels["strengths"], h2))
    green = COLORS["strength"]
    for s in data["strengths"]:
        evidence = f" <font color='{green}'>({inline(s['evidence'], mono)})</font>" if s.get("evidence") else ""
        prefix = f"<b>{inline(report['titles'][s['category']], mono)}:</b> " if s.get("category") else ""
        text = f"<font color='{green}'>{check}</font> {prefix}{inline(s['text'], mono)}{evidence}"
        story.append(Paragraph(text, body))
    if data.get("risks"):
        story.append(Paragraph(labels["risks"], h2))
        story += [Paragraph(f"• {inline(r, mono)}", body) for r in data["risks"]]
    story.append(Spacer(1, 12))

    # Detailed findings, per category.
    story.append(Paragraph(labels["details"], h1))
    for category in data["categories"]:
        story.append(Paragraph(inline(category["title"], mono), h2))
        if category.get("applies") is False:
            note = f": {inline(category['note'], mono)}" if category.get("note") else ""
            story.append(Paragraph(f"<i>{labels['not_applicable']}</i>{note}", body))
            continue
        if category.get("note"):
            story.append(Paragraph(inline(category["note"], mono), small))
        in_category = report["by_category"][category["id"]]
        if not in_category:
            story.append(Paragraph(labels["category_clean"], body))
            continue
        rows = [[Paragraph(f"<b>{labels[k]}</b>", small) for k in ("severity", "location", "description")]]
        for f in in_category:
            rows.append(
                [
                    chip(f["severity"], styles),
                    Paragraph(inline(f["location"], mono), small),
                    Paragraph(f"<b>{inline(f['id'], mono)}</b> {inline(f['title'], mono)}", small),
                ]
            )
        story.append(grid_table(rows, [2.4 * cm, 5.6 * cm, CONTENT_WIDTH - 8 * cm]))
        for f in in_category:
            block = [Paragraph(f"{inline(f['id'], mono)}: {inline(f['title'], mono)}", h3)]
            block.append(Paragraph(f"<b>{labels['location']}:</b> {inline(f['location'], mono)}", small))
            if f.get("snippet"):
                block += [Spacer(1, 3), wrapped(f["snippet"], styles["mono"])]
            for key in ("description", "impact", "fix", "conditions"):
                if f.get(key):
                    block += paragraphs(f[key], body, mono, label=labels[key])
            if f.get("screenshot"):
                block.append(scaled_image(base_dir / f["screenshot"]))
            story.append(KeepTogether(block))
    story.append(Spacer(1, 12))

    # Recommendations.
    story.append(Paragraph(labels["recommendations"], h1))
    for rec in report["recommendations"]:
        refs = ""
        if rec.get("findings"):
            refs = f" <font size='8' color='#6B7280'>({labels['findings_ref']}: {', '.join(rec['findings'])})</font>"
        story.append(Paragraph(f"<b>{inline(rec['priority'], mono)}:</b> {inline(rec['text'], mono)}{refs}", body))
        story.append(Spacer(1, 4))
    story.append(PageBreak())

    # Issues.
    story.append(Paragraph(labels["issues"], h1))
    story.append(Paragraph(labels["issues_intro"], body))
    for block in issue_blocks(data, labels):
        story.append(KeepTogether([Spacer(1, 8), wrapped(block, styles["mono"])]))

    # Coverage appendix.
    inventory = data.get("inventory")
    if inventory and inventory.get("rows"):
        story.append(PageBreak())
        story.append(Paragraph(labels["coverage"], h1))
        if inventory.get("title"):
            story.append(Paragraph(inline(inventory["title"], mono), h2))
        columns = inventory["columns"]
        width = CONTENT_WIDTH / len(columns)
        rows = [[Paragraph(f"<b>{inline(c, mono)}</b>", small) for c in columns]]
        rows += [[Paragraph(inline(cell, mono), small) for cell in row] for row in inventory["rows"]]
        story.append(grid_table(rows, [width] * len(columns)))

    def decorate(canvas, doc) -> None:
        canvas.saveState()
        canvas.setFont(regular, 8)
        canvas.setFillColor(colors.HexColor("#6B7280"))
        width, height = A4
        canvas.drawString(2 * cm, height - 1.3 * cm, heading)
        canvas.line(2 * cm, height - 1.45 * cm, width - 2 * cm, height - 1.45 * cm)
        canvas.drawRightString(width - 2 * cm, 1.2 * cm, f"{labels['page']} {doc.page}")
        canvas.restoreState()

    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=heading,
        author=data["project"],
    )
    doc.build(story, onFirstPage=decorate, onLaterPages=decorate)


def scaled_image(path: Path) -> Image:
    image = Image(str(path))
    # Fit within the content width and at most 10 cm high, keeping the aspect ratio.
    scale = min(CONTENT_WIDTH / image.imageWidth, 10 * cm / image.imageHeight, 1.0)
    image.drawWidth = image.imageWidth * scale
    image.drawHeight = image.imageHeight * scale
    return image


# HTML -----------------------------------------------------------------------

HTML_CSS = """
:root { --border: #D1D5DB; --muted: #6B7280; --bg-soft: #F3F4F6; }
* { box-sizing: border-box; }
body { margin: 0; font: 15px/1.55 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; color: #111827; }
main { max-width: 60rem; margin: 0 auto; padding: 2rem 1.5rem 4rem; }
header { border-bottom: 3px solid #111827; padding-bottom: 1rem; margin-bottom: 1.5rem; }
header h1 { margin: 0 0 .5rem; font-size: 2rem; line-height: 1.2; }
.meta { color: var(--muted); margin: .2rem 0; }
nav { background: var(--bg-soft); border-radius: 6px; padding: .6rem 1rem; margin-bottom: 2rem; }
nav a { margin-right: 1.2rem; color: #1F2937; text-decoration: none; font-weight: 600; }
nav a:hover { text-decoration: underline; }
h2 { margin-top: 2.5rem; border-bottom: 1px solid var(--border); padding-bottom: .3rem; }
h3 { margin-top: 1.8rem; }
code, pre { font-family: ui-monospace, "DejaVu Sans Mono", Menlo, Consolas, monospace; font-size: .85em; }
code { background: var(--bg-soft); padding: .05em .3em; border-radius: 3px; }
pre { background: #F9FAFB; border: 1px solid var(--border); border-radius: 6px; padding: .8rem;
      overflow-x: auto; white-space: pre-wrap; word-break: break-word; }
table { border-collapse: collapse; width: 100%; margin: .8rem 0; font-size: .92em; }
th, td { border: 1px solid var(--border); padding: .4rem .6rem; text-align: left; vertical-align: top; }
th { background: var(--bg-soft); }
.chip { display: inline-block; min-width: 5.5rem; padding: .1rem .5rem; border-radius: 4px; color: #fff;
        font-size: .75rem; font-weight: 700; text-align: center; text-transform: uppercase; letter-spacing: .03em; }
.cards { display: flex; flex-wrap: wrap; gap: .8rem; margin: 1rem 0; }
.card { flex: 1 1 7rem; border: 1px solid var(--border); border-top: 5px solid; border-radius: 6px;
        padding: .6rem .8rem; }
.card .n { font-size: 1.8rem; font-weight: 700; }
.card .label { color: var(--muted); text-transform: uppercase; font-size: .75rem; letter-spacing: .05em; }
.charts { display: flex; flex-wrap: wrap; gap: 2.5rem; align-items: flex-start; }
.donut { width: 11rem; height: 11rem; border-radius: 50%; position: relative; flex: none; }
.donut::after { content: ""; position: absolute; inset: 25%; background: #fff; border-radius: 50%; }
.donut span { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
              font-size: 1.6rem; font-weight: 700; z-index: 1; }
.legend { list-style: none; padding: 0; margin: 0; }
.legend li { margin: .25rem 0; }
.swatch { display: inline-block; width: .8rem; height: .8rem; border-radius: 2px; margin-right: .4rem;
          vertical-align: -1px; }
.bars { flex: 1 1 22rem; }
.bar-row { display: grid; grid-template-columns: 12rem 1fr 2rem; gap: .6rem; align-items: center; margin: .35rem 0; }
.bar-row .name { font-size: .9em; text-align: right; }
.bar { display: flex; height: 1.1rem; border-radius: 3px; overflow: hidden; background: var(--bg-soft); }
.bar span { display: block; height: 100%; }
.strengths li::marker { content: "✓  "; color: #059669; font-weight: 700; }
.evidence { color: #059669; }
.na { color: var(--muted); font-style: italic; }
.finding { border: 1px solid var(--border); border-left: 5px solid; border-radius: 6px;
           padding: .2rem 1rem .6rem; margin: 1rem 0; }
.finding h4 { margin: .6rem 0 .3rem; font-size: 1.05rem; }
.finding img { max-width: 100%; border: 1px solid var(--border); border-radius: 4px; }
.recs li { margin: .4rem 0; }
.prio { font-weight: 700; margin-right: .4rem; }
.refs { color: var(--muted); font-size: .85em; }
.issue { position: relative; margin: 1rem 0; }
.issue button { position: absolute; top: .5rem; right: .5rem; border: 1px solid var(--border); background: #fff;
                border-radius: 4px; padding: .2rem .7rem; cursor: pointer; font: inherit; font-size: .8rem; }
footer { margin-top: 3rem; color: var(--muted); font-size: .85em; border-top: 1px solid var(--border);
         padding-top: .8rem; }
@media print {
  @page { size: A4; margin: 2cm; }
  body { font-size: 10.5pt; }
  main { max-width: none; padding: 0; }
  nav, .issue button { display: none; }
  h2 { break-after: avoid; }
  .finding, .issue, tr { break-inside: avoid; }
  #summary, #issues { break-before: page; }
  * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
}
"""

HTML_SCRIPT = """
document.querySelectorAll(".issue button").forEach((button) => {
  button.addEventListener("click", async () => {
    const text = document.getElementById(button.dataset.target).textContent;
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      const range = document.createRange();
      range.selectNodeContents(document.getElementById(button.dataset.target));
      getSelection().removeAllRanges();
      getSelection().addRange(range);
      document.execCommand("copy");
    }
    const label = button.textContent;
    button.textContent = button.dataset.copied;
    setTimeout(() => (button.textContent = label), 1500);
  });
});
"""

IMAGE_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
}


def html_inline(text: str) -> str:
    out = html.escape(str(text))
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    return out.replace("\n", "<br>")


def html_paragraphs(text: str, label: str = "") -> str:
    chunks = [chunk.strip() for chunk in re.split(r"\n\s*\n", str(text)) if chunk.strip()]
    parts = [html_inline(chunk) for chunk in chunks]
    if label and parts:
        parts[0] = f"<strong>{html.escape(label)}:</strong> {parts[0]}"
    return "".join(f"<p>{part}</p>" for part in parts)


def html_chip(severity: str) -> str:
    return f'<span class="chip" style="background:{COLORS[severity]}">{severity}</span>'


def html_donut(counts: Counter) -> str:
    total = sum(counts.values())
    stops, start = [], 0.0
    for severity in SEVERITIES:
        if counts[severity]:
            end = start + 100 * counts[severity] / total
            stops.append(f"{COLORS[severity]} {start:.2f}% {end:.2f}%")
            start = end
    legend = "".join(
        f'<li><span class="swatch" style="background:{COLORS[s]}"></span>{s} ({counts[s]})</li>'
        for s in SEVERITIES
        if counts[s]
    )
    return (
        f'<div class="donut" style="background:conic-gradient({", ".join(stops)})"><span>{total}</span></div>'
        f'<ul class="legend">{legend}</ul>'
    )


def html_bars(data: dict, report: dict) -> str:
    totals = {cid: sum(c.values()) for cid, c in report["counts_by_category"].items()}
    largest = max(totals.values(), default=0) or 1
    rows = []
    for category in data["categories"]:
        total = totals[category["id"]]
        if not total:
            continue
        counts = report["counts_by_category"][category["id"]]
        spans = "".join(
            f'<span style="width:{100 * counts[s] / largest:.2f}%;background:{COLORS[s]}"'
            f' title="{s}: {counts[s]}"></span>'
            for s in SEVERITIES
            if counts[s]
        )
        rows.append(
            f'<div class="bar-row"><div class="name">{html_inline(category["title"])}</div>'
            f'<div class="bar">{spans}</div><div>{total}</div></div>'
        )
    return f'<div class="bars">{"".join(rows)}</div>'


def html_image(path: Path) -> str:
    mime = IMAGE_TYPES.get(path.suffix.lower(), "application/octet-stream")
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f'<p><img src="data:{mime};base64,{encoded}" alt="{html.escape(path.name)}"></p>'


def render_html(data: dict, report: dict, labels: dict, base_dir: Path) -> str:
    findings = data["findings"]
    counts = report["counts"]
    inventory = data.get("inventory")
    has_inventory = bool(inventory and inventory.get("rows"))
    out: list[str] = []

    sections = [
        ("summary", labels["summary"]),
        ("strengths", labels["strengths_risks"]),
        ("findings", labels["details"]),
        ("recommendations", labels["recommendations"]),
        ("issues", labels["issues"]),
    ]
    if has_inventory:
        sections.append(("coverage", labels["coverage"]))
    out.append(f"<nav>{''.join(f'<a href=#{sid}>{html.escape(title)}</a>' for sid, title in sections)}</nav>")

    out.append(f"<h2>{labels['methodology']}</h2>{html_paragraphs(data['methodology'])}")

    out.append(f'<section id="summary"><h2>{labels["summary"]}</h2><div class="cards">')
    for severity in SEVERITIES:
        out.append(
            f'<div class="card" style="border-top-color:{COLORS[severity]}">'
            f'<div class="n">{counts[severity]}</div><div class="label">{severity}</div></div>'
        )
    out.append(
        f'<div class="card" style="border-top-color:#111827"><div class="n">{len(findings)}</div>'
        f'<div class="label">{labels["total"]}</div></div></div>'
    )
    if findings:
        out.append(
            f'<div class="charts"><div><h3>{labels["by_severity"]}</h3><div class="charts">{html_donut(counts)}'
            f'</div></div><div class="bars"><h3>{labels["by_category"]}</h3>{html_bars(data, report)}</div></div>'
        )
    else:
        out.append(f"<p>{labels['no_findings']}</p>")
    out.append("</section>")

    out.append(
        f'<section id="strengths"><h2>{labels["strengths_risks"]}</h2><h3>{labels["strengths"]}</h3>'
        '<ul class="strengths">'
    )
    for s in data["strengths"]:
        prefix = f"<strong>{html_inline(report['titles'][s['category']])}:</strong> " if s.get("category") else ""
        evidence = f' <span class="evidence">({html_inline(s["evidence"])})</span>' if s.get("evidence") else ""
        out.append(f"<li>{prefix}{html_inline(s['text'])}{evidence}</li>")
    out.append("</ul>")
    if data.get("risks"):
        out.append(f"<h3>{labels['risks']}</h3><ul>")
        out += [f"<li>{html_inline(r)}</li>" for r in data["risks"]]
        out.append("</ul>")
    out.append("</section>")

    out.append(f'<section id="findings"><h2>{labels["details"]}</h2>')
    for category in data["categories"]:
        out.append(f"<h3>{html_inline(category['title'])}</h3>")
        if category.get("applies") is False:
            note = f": {html_inline(category['note'])}" if category.get("note") else ""
            out.append(f'<p class="na">{labels["not_applicable"]}{note}</p>')
            continue
        if category.get("note"):
            out.append(f'<p class="meta">{html_inline(category["note"])}</p>')
        in_category = report["by_category"][category["id"]]
        if not in_category:
            out.append(f"<p>{labels['category_clean']}</p>")
            continue
        out.append(
            f"<table><tr><th>{labels['severity']}</th><th>{labels['location']}</th>"
            f"<th>{labels['description']}</th></tr>"
        )
        for f in in_category:
            out.append(
                f"<tr><td>{html_chip(f['severity'])}</td><td><code>{html.escape(f['location'])}</code></td>"
                f'<td><a href="#{html.escape(f["id"])}"><strong>{html.escape(f["id"])}</strong></a> '
                f"{html_inline(f['title'])}</td></tr>"
            )
        out.append("</table>")
        for f in in_category:
            out.append(
                f'<article class="finding" id="{html.escape(f["id"])}"'
                f' style="border-left-color:{COLORS[f["severity"]]}">'
                f"<h4>{html_chip(f['severity'])} {html.escape(f['id'])}: {html_inline(f['title'])}</h4>"
                f"<p><strong>{labels['location']}:</strong> <code>{html.escape(f['location'])}</code></p>"
            )
            if f.get("snippet"):
                out.append(f"<pre><code>{html.escape(f['snippet'].rstrip())}</code></pre>")
            for key in ("description", "impact", "fix", "conditions"):
                if f.get(key):
                    out.append(html_paragraphs(f[key], label=labels[key]))
            if f.get("screenshot"):
                out.append(html_image(base_dir / f["screenshot"]))
            out.append("</article>")
    out.append("</section>")

    out.append(f'<section id="recommendations"><h2>{labels["recommendations"]}</h2><ul class="recs">')
    for rec in report["recommendations"]:
        refs = ""
        if rec.get("findings"):
            links = ", ".join(f'<a href="#{html.escape(ref)}">{html.escape(ref)}</a>' for ref in rec["findings"])
            refs = f' <span class="refs">({labels["findings_ref"]}: {links})</span>'
        out.append(f'<li><span class="prio">{html_inline(rec["priority"])}</span>{html_inline(rec["text"])}{refs}</li>')
    out.append("</ul></section>")

    out.append(f'<section id="issues"><h2>{labels["issues"]}</h2><p>{labels["issues_intro"]}</p>')
    for n, block in enumerate(issue_blocks(data, labels), start=1):
        out.append(
            f'<div class="issue"><button type="button" data-target="issue-{n}" data-copied="{labels["copied"]}">'
            f'{labels["copy"]}</button><pre id="issue-{n}">{html.escape(block)}</pre></div>'
        )
    out.append("</section>")

    if has_inventory:
        out.append(f'<section id="coverage"><h2>{labels["coverage"]}</h2>')
        if inventory.get("title"):
            out.append(f"<h3>{html_inline(inventory['title'])}</h3>")
        out.append("<table><tr>" + "".join(f"<th>{html_inline(c)}</th>" for c in inventory["columns"]) + "</tr>")
        for row in inventory["rows"]:
            out.append("<tr>" + "".join(f"<td>{html_inline(cell)}</td>" for cell in row) + "</tr>")
        out.append("</table></section>")

    heading = html.escape(report["heading"])
    return f"""<!DOCTYPE html>
<html lang="{html.escape(data.get("lang", "en"))}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{heading}</title>
<style>{HTML_CSS}</style>
</head>
<body>
<main>
<header>
<h1>{heading}</h1>
<p class="meta"><strong>{labels["date"]}:</strong> {html_inline(data["date"])}</p>
<p class="meta"><strong>{labels["scope"]}:</strong> {html_inline(data["scope"])}</p>
</header>
{"".join(out)}
<footer>{heading} · {html_inline(data["date"])}</footer>
</main>
<script>{HTML_SCRIPT}</script>
</body>
</html>
"""


if __name__ == "__main__":
    sys.exit(main(sys.argv))
