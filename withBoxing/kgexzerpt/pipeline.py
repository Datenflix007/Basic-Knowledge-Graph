from __future__ import annotations
from pathlib import Path
from typing import Iterable
from .loaders import load_sources
from .extractors import SpacyOrRegexEntityExtractor, PatternRelationExtractor, EntityExtractor, RelationExtractor
from .graph import KnowledgeGraph
from .ontology import add_domain_tbox


def build_knowledge_graph(
    paths: Iterable[str | Path],
    entity_extractor: EntityExtractor | None = None,
    relation_extractor: RelationExtractor | None = None,
) -> KnowledgeGraph:
    entity_extractor = entity_extractor or SpacyOrRegexEntityExtractor()
    relation_extractor = relation_extractor or PatternRelationExtractor()
    kg = KnowledgeGraph()
    for row in load_sources(paths):
        kg.add_excerpt(row)
        entities = entity_extractor.extract(row)
        for ent in entities:
            kg.add_entity(ent)
        for triple in relation_extractor.extract(row, entities):
            kg.add_triple(triple)
    add_domain_tbox(kg)
    kg.classify_entities_by_aliases()
    return kg
