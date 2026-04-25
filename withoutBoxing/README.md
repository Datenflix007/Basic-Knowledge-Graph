# Basic Knowledge Graph withoutBoxing

`withoutBoxing` ist die Grundversion des Projekts. Sie erzeugt aus Exzerpten einen nachvollziehbaren Wissensgraphen, ohne eine zusaetzliche Klassen- oder Box-Schicht einzubauen. Alles, was im Browser sichtbar wird, stammt direkt aus den Eingabedateien oder aus der einfachen regelbasierten Extraktion.

## Inhaltsverzeichnis

- [Wofuer diese Version gedacht ist](#wofuer-diese-version-gedacht-ist)
- [Schnellstart](#schnellstart)
- [Exzerpte eingeben](#exzerpte-eingeben)
- [Wie die Verarbeitung funktioniert](#wie-die-verarbeitung-funktioniert)
- [Bedienung](#bedienung)
- [Technische Dokumentation](#technische-dokumentation)
- [Geschichtswissenschaftlicher Anspruch](#geschichtswissenschaftlicher-anspruch)
- [Manuelle Installation](#manuelle-installation)
- [Benutzte Literatur](#benutzte-literatur)

## Wofuer diese Version gedacht ist

Diese Variante eignet sich, wenn die unmittelbare Exzerptstruktur im Vordergrund stehen soll: Welche Datei wurde eingelesen? Welche Textstelle steht auf welcher Seite? Welche Begriffe wurden darin erkannt? Welche einfachen Relationen lassen sich aus den Saetzen ableiten?

Die Version unterscheidet Dokumente, Exzerpte, erkannte Entitaeten und extrahierte Relationen. Sie fuegt aber keine fachliche TBox hinzu. Dadurch bleibt der Graph kleiner und naeher am Eingabetext.

![Knowledge Graph Ansicht](image/README/1777141057602.png)

![Detailansicht](image/README/1777141064098.png)

## Schnellstart

Unter Windows reicht in der Regel:

```bat
quickstart.bat
```

Das Skript richtet alles ein:

1. erstellt bei Bedarf eine Python-Umgebung unter `.venv`
2. installiert die Python-Abhaengigkeiten
3. installiert optional das deutsche spaCy-Modell
4. baut `graph.json`
5. kopiert die Graphdaten nach `svelte-app/public/graph.json`
6. installiert die Node-Abhaengigkeiten und startet den Vite-Server

Voraussetzungen sind Python 3.10+ und Node.js/npm. Nach dem Start zeigt Vite die lokale URL im Terminal an, typischerweise `http://localhost:5173/`.

## Exzerpte eingeben

Beim Start fragt `quickstart.bat`, ob das Standardbeispiel oder eigene Exzerpte verwendet werden sollen. Bei eigenen Exzerpten oeffnet sich ein Dateidialog. Dort koennen eine oder mehrere Markdown- oder PDF-Dateien ausgewaehlt werden. Danach fragt das Skript, ob weitere Exzerpte hinzugefuegt werden sollen. Erst wenn diese Frage nicht mit `j` beantwortet wird, baut das Skript den Wissensgraphen.

Markdown-Exzerpte sollten diese Tabellenstruktur verwenden:

```markdown
| Seite | Inhalt | Anmerkung |
|-------|--------|-----------|
| 12 | Die Quelle beschreibt die Neuordnung lokaler Herrschaft. | Begriff "Herrschaft" pruefen. |
| 13 | Der Stadtrat ist Teil der lokalen Verwaltung. | Beleg fuer institutionelle Beziehung. |
```

Optional koennen vor der Tabelle Metadaten notiert werden:

```markdown
- **Haupttitel:** Beispielquelle
- **Autor:** Muster, Maria
- **Jahr:** 1848
```

Die CLI kann ebenfalls mehrere Dateien direkt verarbeiten:

```bash
python -m kgexzerpt.cli build exzerpt.md exzerpt2.md quelle.pdf --out graph.json --format svelte
```

## Wie die Verarbeitung funktioniert

Die Verarbeitung laeuft in mehreren Schritten. Zuerst liest der Loader Markdown-Tabellen oder PDF-Seiten ein. Danach wird pro Eingabedatei ein `Document`-Knoten erzeugt. Jede Tabellenzeile beziehungsweise jede PDF-Seite wird ein `Excerpt`-Knoten.

Aus dem Text in `Inhalt` und `Anmerkung` werden Entitaeten erkannt. Wenn spaCy verfuegbar ist, nutzt das Projekt das deutsche Modell und uebernimmt zum Beispiel Personen, Organisationen, Orte und Nominalphrasen. Falls kein Modell installiert ist, greift ein Regex-Fallback auf auffaellige Grossschreibungen, Akronyme und Mehrwortbegriffe zurueck.

Anschliessend sucht der Relationsextraktor nach einfachen Satzmustern. Ein Satz wie "Der Stadtrat ist Teil der lokalen Verwaltung" kann zum Beispiel eine `PART_OF`-Relation erzeugen. Die Kante merkt sich den Evidenzsatz, damit im Browser nachvollziehbar bleibt, aus welcher Formulierung die Relation stammt.

## Bedienung

In der Visualisierung stehen diese Steuerungen zur Verfuegung:

- Suche: filtert Knoten und Kanten ueber das Suchfeld.
- Mausrad: zoomt in den Graphen hinein oder heraus.
- Linke Maustaste auf freier Flaeche ziehen: rotiert die Ansicht.
- Rechte Maustaste auf freier Flaeche ziehen: verschiebt die Ansicht.
- Knoten anklicken: oeffnet rechts die Detailansicht mit Typ und Rohdaten.

Die Anzeige unterscheidet Dokumente, Exzerpte und erkannte Entitaeten. Kanten zeigen Provenienz- und Relationsinformationen, soweit sie aus den Exzerpten ableitbar sind.

## Technische Dokumentation

### Pipeline von Exzerpt zu JSON

Der Einstiegspunkt ist die CLI in `kgexzerpt/cli.py`. Der Quickstart ruft intern diesen Befehl auf:

```bash
python -m kgexzerpt.cli build exzerpt.md exzerpt2.md --out graph.json --format svelte
```

Die CLI ruft `build_knowledge_graph()` aus `kgexzerpt/pipeline.py` auf. Dort wird fuer jede Eingabedatei diese Verarbeitung ausgefuehrt:

1. `load_sources()` liest Markdown- oder PDF-Dateien.
2. Markdown wird in `load_markdown_excerpt()` aus Tabellen mit den Spalten `Seite`, `Inhalt` und `Anmerkung` gelesen.
3. PDF-Dateien werden seitenweise mit PyMuPDF gelesen; jede PDF-Seite wird ein eigenes Exzerpt.
4. `KnowledgeGraph.add_excerpt()` erzeugt pro Datei einen `Document`-Knoten und pro Tabellenzeile oder PDF-Seite einen `Excerpt`-Knoten.
5. `SpacyOrRegexEntityExtractor.extract()` erkennt Entitaeten aus `Inhalt` plus `Anmerkung`.
6. `PatternRelationExtractor.extract()` sucht einfache Satzmuster und erzeugt daraus gerichtete Relationen.
7. `KnowledgeGraph.export_json()` schreibt den Graphen als `graph.json`.

Intern liegt der Graph als `networkx.MultiDiGraph` vor. Dadurch koennen mehrere Kanten zwischen denselben Knoten existieren, zum Beispiel eine `MENTIONS`-Kante und zusaetzlich eine fachliche Relation.

### JSON-Struktur

Die Datei `graph.json` hat zwei Hauptfelder:

```json
{
  "nodes": [
    {
      "id": "doc:...",
      "label": "exzerpt",
      "kind": "Document"
    }
  ],
  "edges": [
    {
      "id": "HAS_EXCERPT:...",
      "source": "doc:...",
      "target": "excerpt:...",
      "type": "HAS_EXCERPT"
    }
  ]
}
```

Knoten enthalten mindestens `id`, `label` und `kind`. Typische `kind`-Werte sind:

- `Document`: eine Eingabedatei.
- `Excerpt`: eine Tabellenzeile oder PDF-Seite.
- spaCy-Labels wie `PER`, `ORG`, `LOC`, `MISC`.
- `Concept`: erkannte Nominalphrasen.
- `Entity`: Regex-Fallback, falls kein spaCy-Modell verfuegbar ist.

Kanten enthalten mindestens `id`, `source`, `target` und `type`. Die IDs werden stabil aus Inhalt, Quelle oder Relation berechnet, damit derselbe Input reproduzierbare Knoten- und Kanten-IDs erzeugt.

### Kantentypen

- `HAS_EXCERPT`: verbindet ein `Document` mit seinen `Excerpt`-Knoten.
- `MENTIONS`: verbindet ein `Excerpt` mit einer darin erkannten Entitaet.
- `EVIDENCE_FOR`: verbindet ein `Excerpt` mit Subjekt und Objekt einer extrahierten Relation.
- `IS_A`: entsteht bei Mustern wie `ist`, `sind`, `gilt als`, `wird als`.
- `HAS_PART`: entsteht bei Mustern wie `enthaelt`, `umfasst`, `beinhaltet`, `besteht aus`.
- `USES`: entsteht bei Mustern wie `nutzt`, `verwendet`, `setzt ein`.
- `CAUSES_OR_ENABLES`: entsteht bei Mustern wie `fuehrt zu`, `ermoeglicht`, `bewirkt`, `schafft`.
- `DEPENDS_ON`: entsteht bei Mustern wie `haengt ab von`, `abhaengig von`.
- `PART_OF`: entsteht bei Mustern wie `ist Teil von`, `gehoert zu`.

Die Relationsextraktion ist bewusst heuristisch und konservativ. Fuer jeden passenden Satz wird das beste Subjekt und Objekt aus den bereits erkannten Entitaeten gesucht. Wenn kein Treffer gefunden wird, wird aus den letzten Woertern des Satzteils ein `Concept` erzeugt.

### Darstellung im Browser

Nach dem Bau kopiert `quickstart.bat` die erzeugte Datei nach `svelte-app/public/graph.json`. Die Svelte-App laedt diese Datei in `KnowledgeGraph.svelte` mit:

```js
graph = await fetch(url).then(r => r.json());
```

Danach wird der Graph mit D3 gerendert:

- Knoten werden als SVG-Kreise gezeichnet.
- Kanten werden als SVG-Linien gezeichnet.
- Kantenlabels zeigen den jeweiligen `type`.
- Das Suchfeld filtert Knoten und blendet nur Kanten ein, deren Quelle und Ziel noch sichtbar sind.
- Ein Klick auf einen Knoten zeigt rechts die Rohdaten aus dem JSON.

## Geschichtswissenschaftlicher Anspruch

Der Graph ist kein Ersatz fuer Quellenkritik, sondern ein Werkzeug zur strukturierten Exploration. Jede Wissenseinheit soll aus einem Exzerpt mit Seitenangabe, Inhalt und Anmerkung hervorgehen, damit Aussagen auf ihre Belegstelle zurueckgefuehrt werden koennen. Gerade fuer historische Arbeit ist wichtig, dass der Graph nicht vorgibt, Ambivalenz aufzuloesen: Er macht Verdichtungen, wiederkehrende Begriffe, Akteurskonstellationen und moegliche Relationen sichtbar, die anschliessend hermeneutisch und quellenkritisch geprueft werden muessen.

Die automatische Extraktion arbeitet bewusst konservativ. Sie erzeugt Vorschlaege fuer Entitaeten und Relationen, aber keine abschliessenden historischen Urteile. Der wissenschaftliche Mehrwert liegt in der Nachvollziehbarkeit der Belege, der Vergleichbarkeit vieler Exzerpte und der Moeglichkeit, Forschungshypothesen sichtbar zu machen, ohne die argumentative Pruefung auszulagern.

## Manuelle Installation

Falls der Quickstart nicht genutzt werden soll:

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -e .
python -m kgexzerpt.cli build exzerpt.md --out graph.json --format svelte
```

## Benutzte Literatur

- [Building Knowledge Graphs](https://go.neo4j.com/rs/710-RRC-335/images/Building-Knowledge-Graphs-Practitioner's-Guide-OReilly-book.pdf)
- [Knowledge Graphs data.world.pdf](https://page.data.world/hubfs/Knowledge%20Graphs%20data.world.pdf)
- [Knowledge Graphs](https://web.stanford.edu/class/cs520/How_To_Create_A_Knowledge_Graph_From_Data.pdf)
- [developers-guide-how-to-build-knowledge-graph.pdf](https://content.gitbook.com/content/sasnIfbOiAFHeOBcNUBB/blobs/MAe5jxOScBtqIFO1NjXV/developers-guide-how-to-build-knowledge-graph.pdf)
- [Construction of Knowledge Graphs: Current State and Challenges](https://dbs.uni-leipzig.de/files/research/publications/2024-8/pdf/information-15-00509-with-cover.pdf)
