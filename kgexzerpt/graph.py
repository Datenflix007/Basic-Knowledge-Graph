from __future__ import annotations
import json
from pathlib import Path
from typing import Any
import networkx as nx
from .models import ExcerptRow, EntityMention, Triple, stable_id
from .resolution import EntityResolver


class KnowledgeGraph:
    def __init__(self, resolver: EntityResolver | None = None):
        self.g = nx.MultiDiGraph()
        self.resolver = resolver or EntityResolver()

    def add_excerpt(self, row: ExcerptRow) -> None:
        doc_id = row.source.id()
        self.g.add_node(doc_id, label=row.source.title or row.source.path.stem, kind="Document", **row.source.metadata, path=str(row.source.path))
        ex_id = row.id()
        self.g.add_node(ex_id, label=f"S. {row.page}", kind="Excerpt", page=row.page, content=row.content, note=row.note)
        self.g.add_edge(doc_id, ex_id, key=f"HAS_EXCERPT:{ex_id}", type="HAS_EXCERPT")

    def add_entity(self, mention: EntityMention) -> str:
        node_id = self.resolver.resolve(mention)
        if node_id not in self.g:
            self.g.add_node(node_id, label=mention.canonical, kind=mention.label, aliases=[mention.canonical])
        else:
            aliases = set(self.g.nodes[node_id].get("aliases", [])); aliases.add(mention.canonical)
            self.g.nodes[node_id]["aliases"] = sorted(aliases)
        if mention.source_excerpt_id:
            eid = f"MENTIONS:{mention.source_excerpt_id}:{node_id}"
            self.g.add_edge(mention.source_excerpt_id, node_id, key=eid, type="MENTIONS", confidence=mention.confidence)
        return node_id

    def add_triple(self, triple: Triple) -> None:
        s = self.add_entity(triple.subject)
        o = self.add_entity(triple.obj)
        eid = f"{triple.predicate}:{stable_id(s, o, triple.evidence)}"
        self.g.add_edge(s, o, key=eid, type=triple.predicate, confidence=triple.confidence, evidence=triple.evidence, source_excerpt_id=triple.source_excerpt_id)
        if triple.source_excerpt_id:
            self.g.add_edge(triple.source_excerpt_id, s, key=f"EVIDENCE_FOR:{eid}:s", type="EVIDENCE_FOR")
            self.g.add_edge(triple.source_excerpt_id, o, key=f"EVIDENCE_FOR:{eid}:o", type="EVIDENCE_FOR")

    def to_svelte_json(self) -> dict[str, Any]:
        return {
            "nodes": [{"id": n, **data} for n, data in self.g.nodes(data=True)],
            "edges": [{"id": k, "source": u, "target": v, **data} for u, v, k, data in self.g.edges(keys=True, data=True)],
        }

    def export_json(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_svelte_json(), ensure_ascii=False, indent=2), encoding="utf-8")

    def export_graphml(self, path: str | Path) -> None:
        h = nx.MultiDiGraph()
        for n, data in self.g.nodes(data=True):
            h.add_node(n, **{k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v for k, v in data.items()})
        for u, v, k, data in self.g.edges(keys=True, data=True):
            h.add_edge(u, v, key=k, **{kk: json.dumps(vv, ensure_ascii=False) if isinstance(vv, (dict, list)) else vv for kk, vv in data.items()})
        nx.write_graphml(h, path)
