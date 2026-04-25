from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal
import hashlib
import re


def slug(text: str, max_len: int = 80) -> str:
    s = re.sub(r"[^\w\-]+", "_", text.strip().lower(), flags=re.UNICODE).strip("_")
    return s[:max_len] or hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]


def stable_id(*parts: Any) -> str:
    raw = "|".join(str(p) for p in parts)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


@dataclass(frozen=True)
class SourceDocument:
    path: Path
    title: str | None = None
    doc_id: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)

    def id(self) -> str:
        return self.doc_id or f"doc:{stable_id(self.path.resolve())}"


@dataclass(frozen=True)
class ExcerptRow:
    source: SourceDocument
    page: str
    content: str
    note: str = ""

    def id(self) -> str:
        return f"excerpt:{stable_id(self.source.id(), self.page, self.content, self.note)}"


@dataclass(frozen=True)
class EntityMention:
    text: str
    label: str = "Entity"
    confidence: float = 0.5
    source_excerpt_id: str | None = None

    @property
    def canonical(self) -> str:
        return re.sub(r"\s+", " ", self.text.strip())

    def node_id(self) -> str:
        return f"entity:{slug(self.canonical)}"


@dataclass(frozen=True)
class Triple:
    subject: EntityMention
    predicate: str
    obj: EntityMention
    confidence: float = 0.5
    evidence: str = ""
    source_excerpt_id: str | None = None


@dataclass
class GraphNode:
    id: str
    label: str
    kind: str
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphEdge:
    id: str
    source: str
    target: str
    type: str
    properties: dict[str, Any] = field(default_factory=dict)
