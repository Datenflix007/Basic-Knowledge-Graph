from __future__ import annotations

from pathlib import Path
import re
from typing import Iterable

from .models import SourceDocument, ExcerptRow


def load_sources(paths: Iterable[str | Path]) -> list[ExcerptRow]:
    rows: list[ExcerptRow] = []
    for p in map(Path, paths):
        if p.suffix.lower() == ".md":
            rows.extend(load_markdown_excerpt(p))
        elif p.suffix.lower() == ".pdf":
            rows.extend(load_pdf_as_excerpts(p))
        else:
            raise ValueError(f"Nicht unterstütztes Format: {p}")
    return rows


def load_markdown_excerpt(path: Path) -> list[ExcerptRow]:
    text = path.read_text(encoding="utf-8")
    metadata = _parse_metadata(text)
    doc = SourceDocument(path=path, title=metadata.get("Haupttitel") or path.stem, metadata=metadata)
    rows: list[ExcerptRow] = []
    in_table = False
    for line in text.splitlines():
        if re.match(r"^\|\s*Seite\s*\|\s*Inhalt\s*\|\s*Anmerkung\s*\|", line, re.I):
            in_table = True
            continue
        if in_table and re.match(r"^\|\s*-+\s*\|", line):
            continue
        if in_table:
            if not line.strip().startswith("|"):
                if rows:
                    in_table = False
                continue
            cells = _split_md_row(line)
            if len(cells) >= 3:
                page, content, note = cells[:3]
                if page.strip():
                    rows.append(ExcerptRow(doc, page.strip(), _clean(content), _clean(note)))
    return rows


def load_pdf_as_excerpts(path: Path) -> list[ExcerptRow]:
    try:
        import fitz  # PyMuPDF
    except ImportError as e:
        raise ImportError("Für PDF-Import: pip install pymupdf") from e
    doc = SourceDocument(path=path, title=path.stem)
    out: list[ExcerptRow] = []
    with fitz.open(path) as pdf:
        for i, page in enumerate(pdf, start=1):
            text = re.sub(r"\s+", " ", page.get_text("text")).strip()
            if text:
                out.append(ExcerptRow(doc, str(i), text, "Automatisch aus PDF-Seitentext extrahiert"))
    return out


def _split_md_row(line: str) -> list[str]:
    # Markdown-Tabellen mit escaped pipes werden grob robust behandelt.
    parts, buf, esc = [], [], False
    s = line.strip().strip("|")
    for ch in s:
        if ch == "\\" and not esc:
            esc = True; buf.append(ch); continue
        if ch == "|" and not esc:
            parts.append("".join(buf).strip()); buf = []
        else:
            buf.append(ch)
        esc = False
    parts.append("".join(buf).strip())
    return parts


def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("\\|", "|")).strip()


def _parse_metadata(text: str) -> dict[str, str]:
    meta: dict[str, str] = {}
    for line in text.splitlines():
        m = re.match(r"^- \*\*(.+?):\*\*\s*(.+)$", line.strip())
        if m:
            meta[m.group(1).strip()] = m.group(2).strip()
    return meta
