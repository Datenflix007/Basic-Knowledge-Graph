from __future__ import annotations

import re
from abc import ABC, abstractmethod
from collections import Counter
from typing import Iterable

from .models import EntityMention, ExcerptRow, Triple


class EntityExtractor(ABC):
    @abstractmethod
    def extract(self, row: ExcerptRow) -> list[EntityMention]: ...


class RelationExtractor(ABC):
    @abstractmethod
    def extract(self, row: ExcerptRow, entities: list[EntityMention]) -> list[Triple]: ...


class SpacyOrRegexEntityExtractor(EntityExtractor):
    def __init__(self, model: str = "de_core_news_lg", min_len: int = 3):
        self.min_len = min_len
        self.nlp = None
        try:
            import spacy
            self.nlp = spacy.load(model)
        except Exception:
            self.nlp = None

    def extract(self, row: ExcerptRow) -> list[EntityMention]:
        text = f"{row.content} {row.note}".strip()
        mentions: list[EntityMention] = []
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                if len(ent.text.strip()) >= self.min_len:
                    mentions.append(EntityMention(ent.text, ent.label_, 0.85, row.id()))
            # wichtige Nominalphrasen ergänzen
            for chunk in getattr(doc, "noun_chunks", []):
                t = chunk.text.strip()
                if len(t) >= self.min_len and len(t.split()) <= 5:
                    mentions.append(EntityMention(t, "Concept", 0.65, row.id()))
        else:
            # Fallback: deutsche Mehrwort-Komposita, Akronyme, Produkt-/Projektmuster
            pat = re.compile(r"\b(?:[A-ZÄÖÜ][\wÄÖÜäöüß\-]{2,}|[A-Z]{2,}|[a-zäöüß]+(?:[A-Z][a-zäöüß]+)+)(?:\s+(?:[A-ZÄÖÜ][\wÄÖÜäöüß\-]{2,}|[A-Z]{2,}|[a-zäöüß]+(?:[A-Z][a-zäöüß]+)+)){0,4}")
            for m in pat.finditer(text):
                mentions.append(EntityMention(m.group(0), "Entity", 0.55, row.id()))
        return _dedupe_mentions(mentions)


class PatternRelationExtractor(RelationExtractor):
    """Deterministische, auditierbare Relationen aus Exzerptsätzen.

    Die Heuristiken sind absichtlich konservativ. Für hohe Recall-Werte kann man diese
    Klasse durch einen LLMRelationExtractor mit demselben Interface ersetzen.
    """
    VERBS = [
        (r"(?P<s>.+?)\s+(?:ist|sind|gilt als|gelten als|wird als|werden als)\s+(?P<o>.+)", "IS_A"),
        (r"(?P<s>.+?)\s+(?:enthält|umfasst|beinhaltet|besteht aus)\s+(?P<o>.+)", "HAS_PART"),
        (r"(?P<s>.+?)\s+(?:nutzt|verwenden|verwendet|setzt ein|setzen ein)\s+(?P<o>.+)", "USES"),
        (r"(?P<s>.+?)\s+(?:führt zu|ermöglicht|bewirkt|schafft)\s+(?P<o>.+)", "CAUSES_OR_ENABLES"),
        (r"(?P<s>.+?)\s+(?:hängt ab von|abhängig von)\s+(?P<o>.+)", "DEPENDS_ON"),
        (r"(?P<s>.+?)\s+(?:ist Teil von|gehört zu)\s+(?P<o>.+)", "PART_OF"),
    ]

    def extract(self, row: ExcerptRow, entities: list[EntityMention]) -> list[Triple]:
        triples: list[Triple] = []
        text = row.content
        sentences = re.split(r"(?<=[.!?])\s+", text)
        for sent in sentences:
            for pattern, rel in self.VERBS:
                m = re.search(pattern, sent, flags=re.I)
                if not m:
                    continue
                subj = _best_entity(m.group("s"), entities)
                obj = _best_entity(m.group("o"), entities)
                if subj and obj and subj.node_id() != obj.node_id():
                    triples.append(Triple(subj, rel, obj, 0.62, sent[:500], row.id()))
        return triples


def _dedupe_mentions(xs: Iterable[EntityMention]) -> list[EntityMention]:
    best: dict[str, EntityMention] = {}
    for x in xs:
        key = x.canonical.lower()
        if len(key) < 3 or key in {"und", "oder", "sowie", "dass", "dies"}:
            continue
        if key not in best or x.confidence > best[key].confidence:
            best[key] = x
    return sorted(best.values(), key=lambda e: (-e.confidence, e.canonical))


def _best_entity(span: str, entities: list[EntityMention]) -> EntityMention | None:
    span_l = span.lower()
    candidates = [e for e in entities if e.canonical.lower() in span_l]
    if candidates:
        return max(candidates, key=lambda e: (len(e.canonical), e.confidence))
    cleaned = re.sub(r"[^\wÄÖÜäöüß\- ]", " ", span).strip()
    words = cleaned.split()
    if not words:
        return None
    label = " ".join(words[-4:])
    if len(label) < 3:
        return None
    return EntityMention(label, "Concept", 0.35)
