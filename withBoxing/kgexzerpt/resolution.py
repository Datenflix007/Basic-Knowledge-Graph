from __future__ import annotations
from rapidfuzz import fuzz
from .models import EntityMention


class EntityResolver:
    def __init__(self, threshold: int = 92):
        self.threshold = threshold
        self.alias_to_id: dict[str, str] = {}

    def resolve(self, mention: EntityMention) -> str:
        key = mention.canonical.lower()
        if key in self.alias_to_id:
            return self.alias_to_id[key]
        for alias, node_id in self.alias_to_id.items():
            if fuzz.token_sort_ratio(key, alias) >= self.threshold:
                self.alias_to_id[key] = node_id
                return node_id
        node_id = mention.node_id()
        self.alias_to_id[key] = node_id
        return node_id
