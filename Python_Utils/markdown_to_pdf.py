#!/usr/bin/env python3
"""
Markdown to PDF Report Converter
Supports: headers (H1-H6), tables, bold, italic, bold+italic,
          inline code, code blocks, blockquotes, ordered/unordered lists,
          horizontal rules, and strikethrough.
"""

import re
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, ListFlowable, ListItem, Preformatted
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER


# ── Colour palette ────────────────────────────────────────────────────────────
H1_COLOR       = colors.HexColor("#1a1a2e")
H2_COLOR       = colors.HexColor("#16213e")
H3_COLOR       = colors.HexColor("#0f3460")
H4_COLOR       = colors.HexColor("#533483")
H5_COLOR       = colors.HexColor("#6a4c93")
H6_COLOR       = colors.HexColor("#8b6914")
BLOCKQUOTE_BG  = colors.HexColor("#f0f4ff")
BLOCKQUOTE_BAR = colors.HexColor("#4a90d9")
CODE_BG        = colors.HexColor("#f5f5f5")
CODE_COLOR     = colors.HexColor("#c7254e")
TABLE_HEADER   = colors.HexColor("#2c3e50")
TABLE_ALT_ROW  = colors.HexColor("#f8f9fa")
TABLE_BORDER   = colors.HexColor("#dee2e6")
HR_COLOR       = colors.HexColor("#cccccc")


# ── Style definitions ─────────────────────────────────────────────────────────
def build_styles():
    base = getSampleStyleSheet()

    def add(name, **kw):
        if name not in base:
            base.add(ParagraphStyle(name=name, **kw))
        return base[name]

    add("H1", parent=base["Normal"], fontSize=26, leading=32,
        textColor=H1_COLOR, spaceAfter=10, spaceBefore=16,
        fontName="Helvetica-Bold", borderPadding=(0, 0, 4, 0))

    add("H2", parent=base["Normal"], fontSize=20, leading=26,
        textColor=H2_COLOR, spaceAfter=8, spaceBefore=14,
        fontName="Helvetica-Bold")

    add("H3", parent=base["Normal"], fontSize=16, leading=22,
        textColor=H3_COLOR, spaceAfter=6, spaceBefore=12,
        fontName="Helvetica-Bold")

    add("H4", parent=base["Normal"], fontSize=13, leading=18,
        textColor=H4_COLOR, spaceAfter=5, spaceBefore=10,
        fontName="Helvetica-Bold")

    add("H5", parent=base["Normal"], fontSize=11, leading=16,
        textColor=H5_COLOR, spaceAfter=4, spaceBefore=8,
        fontName="Helvetica-BoldOblique")

    add("H6", parent=base["Normal"], fontSize=10, leading=14,
        textColor=H6_COLOR, spaceAfter=4, spaceBefore=6,
        fontName="Helvetica-Oblique")

    add("Body", parent=base["Normal"], fontSize=10, leading=15,
        spaceAfter=6, fontName="Helvetica")

    add("Blockquote", parent=base["Normal"], fontSize=10, leading=15,
        leftIndent=20, spaceAfter=8, fontName="Helvetica-Oblique",
        textColor=colors.HexColor("#444466"),
        backColor=BLOCKQUOTE_BG)

    add("CodeBlock", parent=base["Normal"], fontSize=9, leading=13,
        fontName="Courier", backColor=CODE_BG, leftIndent=12,
        rightIndent=12, spaceAfter=8, spaceBefore=4,
        textColor=colors.HexColor("#333333"))

    add("TableHeader", parent=base["Normal"], fontSize=10,
        fontName="Helvetica-Bold", textColor=colors.white, alignment=TA_LEFT)

    add("TableCell", parent=base["Normal"], fontSize=10,
        fontName="Helvetica", textColor=colors.HexColor("#333333"),
        alignment=TA_LEFT)

    return base


# ── Inline markdown → ReportLab XML ──────────────────────────────────────────
_RL_FORMAT_TAG = re.compile(r'<(/)?(b|i|strike|font)[^>]*>', re.IGNORECASE)


def _sanitize_inline(html_text: str) -> str:
    """
    Validate that b/i/strike/font tags are properly nested for ReportLab.
    If any mismatch is detected, strip all formatting tags and return plain text.
    This guards against LLM output with overlapping inline markup like
    **some _bold** italic_ which otherwise causes a ReportLab ValueError.
    """
    stack = []
    for m in _RL_FORMAT_TAG.finditer(html_text):
        closing = bool(m.group(1))
        tag = m.group(2).lower()
        if not closing:
            stack.append(tag)
        else:
            if not stack or stack[-1] != tag:
                return _RL_FORMAT_TAG.sub('', html_text)
            stack.pop()
    if stack:
        return _RL_FORMAT_TAG.sub('', html_text)
    return html_text


def inline_to_rl(text: str) -> str:
    """Convert inline markdown modifiers to ReportLab Paragraph markup."""
    # Escape XML special chars first (but not inside code spans)
    parts = re.split(r'(`[^`]+`)', text)
    escaped_parts = []
    for part in parts:
        if part.startswith('`') and part.endswith('`') and len(part) > 1:
            inner = part[1:-1].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            escaped_parts.append(
                f'<font name="Courier" color="{CODE_COLOR.hexval()}" '
                f'backColor="{CODE_BG.hexval()}"> {inner} </font>'
            )
        else:
            p = part.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            escaped_parts.append(p)
    text = ''.join(escaped_parts)

    # Bold + italic  ***text*** or ___text___
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<b><i>\1</i></b>', text)
    text = re.sub(r'___(.+?)___',       r'<b><i>\1</i></b>', text)
    # Bold  **text** or __text__
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.+?)__',     r'<b>\1</b>', text)
    # Italic  *text* or _text_
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    text = re.sub(r'_(.+?)_',   r'<i>\1</i>', text)
    # Strikethrough  ~~text~~
    text = re.sub(r'~~(.+?)~~', r'<strike>\1</strike>', text)

    return _sanitize_inline(text)


# ── Table builder ─────────────────────────────────────────────────────────────
def build_table(rows: list[list[str]], styles_map, available_width: float | None = None) -> Table:
    """Render a parsed markdown table as a styled ReportLab Table."""
    if available_width is None:
        available_width = letter[0] - 2 * inch

    col_count = max(len(r) for r in rows) if rows else 1
    col_width = available_width / col_count

    # Cap cell text so no single row exceeds ~500pt (safe for any margin config).
    # inner_col_w approximates the wrappable text width (minus left+right cell padding).
    inner_col_w = max(col_width - 16, 5)
    chars_per_line = max(inner_col_w / 5.5, 1)
    max_cell_chars = max(int(35 * chars_per_line), 50)

    rl_rows = []
    for r_idx, row in enumerate(rows):
        rl_row = []
        for cell in row:
            text = cell.strip()
            if len(text) > max_cell_chars:
                text = text[:max_cell_chars] + "…"
            style = styles_map["TableHeader"] if r_idx == 0 else styles_map["TableCell"]
            rl_row.append(Paragraph(inline_to_rl(text), style))
        rl_rows.append(rl_row)

    t = Table(rl_rows, colWidths=[col_width] * col_count, repeatRows=1, splitByRow=1)

    style_cmds = [
        ("BACKGROUND",    (0, 0), (-1, 0),  TABLE_HEADER),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0),  10),
        ("ALIGN",         (0, 0), (-1, -1), "LEFT"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("GRID",          (0, 0), (-1, -1), 0.5, TABLE_BORDER),
        ("ROWBACKGROUND", (0, 1), (-1, -1), [colors.white, TABLE_ALT_ROW]),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("ROUNDEDCORNERS",(0, 0), (-1, -1), [3, 3, 3, 3]),
    ]
    t.setStyle(TableStyle(style_cmds))
    return t


# ── Main parser ───────────────────────────────────────────────────────────────
def parse_markdown(md_text: str, styles_map, available_width: float | None = None) -> list:
    """Walk markdown lines and produce a list of ReportLab flowables."""
    flowables = []
    lines = md_text.splitlines()
    i = 0
    list_buffer = []          # pending list items  (text, level, ordered)
    table_buffer = []         # pending table rows

    def flush_list():
        if not list_buffer:
            return
        # Split into contiguous ordered / unordered runs
        run_items = []
        run_ordered = list_buffer[0][2]
        run = []
        for text, level, ordered in list_buffer:
            if ordered != run_ordered:
                run_items.append((run_ordered, run))
                run = []
                run_ordered = ordered
            run.append((text, level))
        run_items.append((run_ordered, run))

        for ordered, items in run_items:
            rl_items = []
            for text, _level in items:
                p = Paragraph(inline_to_rl(text), styles_map["Body"])
                rl_items.append(ListItem(p, leftIndent=20, bulletIndent=8))
            if ordered:
                flowables.append(ListFlowable(rl_items, bulletType="1",
                                              start=1, spaceAfter=6))
            else:
                flowables.append(ListFlowable(rl_items, bulletType="bullet",
                                              bulletChar="•", spaceAfter=6))
        list_buffer.clear()

    def flush_table():
        if not table_buffer:
            return
        # Remove the separator row (row index 1 with dashes)
        data = [r for r in table_buffer if not all(
            re.fullmatch(r':?-+:?', c.strip()) for c in r if c.strip()
        )]
        if data:
            flowables.append(build_table(data, styles_map, available_width))
            flowables.append(Spacer(1, 6))
        table_buffer.clear()

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # ── Fenced code block  ```...``` ─────────────────────────────────────
        if stripped.startswith("```"):
            flush_list()
            flush_table()
            i += 1
            code_lines = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            code_text = "\n".join(code_lines)
            flowables.append(
                Preformatted(code_text, styles_map["CodeBlock"],
                             maxLineLength=90)
            )
            flowables.append(Spacer(1, 4))
            i += 1
            continue

        # ── Horizontal rule  ---  /  ***  /  ___ ────────────────────────────
        if re.fullmatch(r'(\*{3,}|-{3,}|_{3,})', stripped):
            flush_list()
            flush_table()
            flowables.append(Spacer(1, 4))
            flowables.append(HRFlowable(width="100%", thickness=1,
                                        color=HR_COLOR, spaceAfter=4))
            i += 1
            continue

        # ── ATX Headers  # H1 … ###### H6 ───────────────────────────────────
        m = re.match(r'^(#{1,6})\s+(.*)', stripped)
        if m:
            flush_list()
            flush_table()
            level = len(m.group(1))
            text  = m.group(2)
            style = styles_map[f"H{level}"]
            # H1 gets a decorative underline via HRFlowable
            flowables.append(Paragraph(inline_to_rl(text), style))
            if level == 1:
                flowables.append(
                    HRFlowable(width="100%", thickness=2,
                               color=H1_COLOR, spaceAfter=6)
                )
            elif level == 2:
                flowables.append(
                    HRFlowable(width="100%", thickness=1,
                               color=H2_COLOR, spaceAfter=4)
                )
            i += 1
            continue

        # ── Setext H1/H2  (text\n===  or  text\n---) ────────────────────────
        if i + 1 < len(lines):
            next_stripped = lines[i + 1].strip()
            if re.fullmatch(r'=+', next_stripped) and stripped:
                flush_list(); flush_table()
                flowables.append(Paragraph(inline_to_rl(stripped), styles_map["H1"]))
                flowables.append(HRFlowable(width="100%", thickness=2,
                                            color=H1_COLOR, spaceAfter=6))
                i += 2
                continue
            if re.fullmatch(r'-+', next_stripped) and stripped:
                flush_list(); flush_table()
                flowables.append(Paragraph(inline_to_rl(stripped), styles_map["H2"]))
                flowables.append(HRFlowable(width="100%", thickness=1,
                                            color=H2_COLOR, spaceAfter=4))
                i += 2
                continue

        # ── Blockquote  > text ───────────────────────────────────────────────
        if stripped.startswith(">"):
            flush_list(); flush_table()
            content = re.sub(r'^>\s?', '', stripped)
            # Collect consecutive blockquote lines
            bq_lines = [content]
            i += 1
            while i < len(lines) and lines[i].strip().startswith(">"):
                bq_lines.append(re.sub(r'^>\s?', '', lines[i].strip()))
                i += 1
            bq_text = " ".join(bq_lines)
            # Draw left bar via a 1-column table
            bq_para = Paragraph(inline_to_rl(bq_text), styles_map["Blockquote"])
            bq_table = Table([[bq_para]], colWidths=[letter[0] - 2.2 * inch])
            bq_table.setStyle(TableStyle([
                ("LEFTPADDING",   (0, 0), (-1, -1), 12),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
                ("TOPPADDING",    (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("BACKGROUND",    (0, 0), (-1, -1), BLOCKQUOTE_BG),
                ("LINEBEFORE",    (0, 0), (0, -1),  4, BLOCKQUOTE_BAR),
            ]))
            flowables.append(bq_table)
            flowables.append(Spacer(1, 4))
            continue

        # ── Table row  | col | col | ─────────────────────────────────────────
        if stripped.startswith("|") and stripped.endswith("|"):
            flush_list()
            row_cells = [c.strip() for c in stripped[1:-1].split("|")]
            table_buffer.append(row_cells)
            i += 1
            continue
        elif table_buffer:
            flush_table()

        # ── Unordered list  - / * / + ────────────────────────────────────────
        m = re.match(r'^(\s*)[-*+]\s+(.*)', line)
        if m:
            flush_table()
            level = len(m.group(1)) // 2
            list_buffer.append((m.group(2), level, False))
            i += 1
            continue

        # ── Ordered list  1. / 2. ────────────────────────────────────────────
        m = re.match(r'^(\s*)\d+\.\s+(.*)', line)
        if m:
            flush_table()
            level = len(m.group(1)) // 2
            list_buffer.append((m.group(2), level, True))
            i += 1
            continue

        # ── Blank line ───────────────────────────────────────────────────────
        if not stripped:
            flush_list()
            flush_table()
            flowables.append(Spacer(1, 6))
            i += 1
            continue

        # ── Normal paragraph ─────────────────────────────────────────────────
        flush_list()
        flush_table()
        flowables.append(Paragraph(inline_to_rl(stripped), styles_map["Body"]))
        i += 1

    flush_list()
    flush_table()
    return flowables


# ── Entry point ───────────────────────────────────────────────────────────────
def convert(input_path: str, output_path: str):
    with open(input_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    styles_map = build_styles()

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=inch,
        rightMargin=inch,
        topMargin=inch,
        bottomMargin=inch,
    )

    flowables = parse_markdown(md_text, styles_map)
    doc.build(flowables)
    print(f"✓ Converted '{input_path}' → '{output_path}'")


def convert_markdown_to_pdf(md_text: str, output_path: str):
    styles_map = build_styles()
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=inch,
        rightMargin=inch,
        topMargin=inch,
        bottomMargin=inch,
    )
    flowables = parse_markdown(md_text, styles_map)
    doc.build(flowables)
    print(f"✓ Converted markdown text to '{output_path}'")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python md_to_pdf.py <input.md> [output.pdf]")
        sys.exit(1)

    inp = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else inp.rsplit(".", 1)[0] + ".pdf"
    convert(inp, out)
