# KG Exzerpt Builder

Python-Paket, um aus PDFs oder Markdown-Exzerpten im Format `| Seite | Inhalt | Anmerkung |` einen nachvollziehbaren Property-Graphen aufzubauen.

## Installation

```bash
python -m venv .venv
# on linux: 
# source .venv/bin/activate
# on windows:
.\.venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download de_core_news_lg  # optional, aber empfohlen
```

## CLI

```bash
python -m kgexzerpt.cli build ./exzerpt1.md ./exzerpt2.md --out graph.json --format svelte
python -m kgexzerpt.cli build ./paper.pdf --out graph.graphml --format graphml
```

## Einbindung

```python
from kgexzerpt.pipeline import build_knowledge_graph

graph = build_knowledge_graph(["exzerpt.md", "dokument.pdf"])
graph.export_json("graph.json")
```

## Svelte

`/svelte/KnowledgeGraph.svelte` lädt die exportierte JSON-Struktur (`nodes`, `edges`) und rendert sie mit `d3-force`.
