# Basic Knowledge Graph

Werkzeug zum Erzeugen und Erkunden eines nachvollziehbaren Wissensgraphen aus historischen Exzerpten. Die Exzerpte werden aus Markdown-Tabellen oder PDFs gelesen, in Dokument-, Exzerpt-, Entitaets- und Relationsknoten ueberfuehrt und anschliessend in einer Svelte/D3-Visualisierung angezeigt.

![1777144608430](image/README/1777144608430.png)

![1777144611294](image/README/1777144611294.png)

![1777144616390](image/README/1777144616390.png)

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

## Exzerpte Eingeben

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

## Bedienung

In der Visualisierung stehen diese Steuerungen zur Verfuegung:

- Suche: filtert Knoten und Kanten ueber das Suchfeld.
- Mausrad: zoomt in den Graphen hinein oder heraus.
- Linke Maustaste auf freier Flaeche ziehen: rotiert die Ansicht.
- Rechte Maustaste auf freier Flaeche ziehen: verschiebt die Ansicht.
- Knoten anklicken: oeffnet rechts die Detailansicht mit Typ und Rohdaten.

Die Anzeige unterscheidet Dokumente, Exzerpte und erkannte Entitaeten. Kanten zeigen Provenienz- und Relationsinformationen, soweit sie aus den Exzerpten ableitbar sind.

Gruene Boxen markieren die TBox, also die begriffliche Ordnung des Wissensgraphen: Klassen, Unterklassen und Synonyme. Diese Ordnung ist nicht mehr nur fuer die DIN-EN-1789-Systematik angelegt, sondern fuer den ganzen Graphen. Sie umfasst u. a. `Akteur`, `Organisation`, `Ort`, `Rettungsdienst`, `Rettungsdienstfahrzeug`, `Medizinprodukt`, `Vernetztes System`, `Schnittstelle`, `Drahtlose Kommunikation`, `IT-Sicherheit`, `Schwachstelle`, `Angriff und Angriffsmodell`, `Kryptographie und Verschluesselung`, `Daten und Datenschutz`, `Firmware und Update` sowie `Norm und Standard`.

Die DIN-EN-1789-Boxen bleiben als fachlicher Teilbereich erhalten: `Rettungsdienstfahrzeug`, `Krankentransportwagen`, `Krankentransportwagen Typ A1/A2`, `Notfallkrankenwagen`, `Rettungswagen (Typ C)` und `DIN EN 1789`. Synonyme wie `RTW`, `Rettungswagen`, `KTW Typ C`, `BSI`, `TLS 1.3`, `BitLocker`, `Bluetooth` oder `Patientendaten` werden als eigene Synonym-Knoten an passende Klassen gebunden. Normale Entitaeten und belegte Exzerptaussagen bleiben die ABox und werden automatisch ueber `CLASSIFIED_AS` an TBox-Klassen angeschlossen. Die Klassifizierung nutzt erkannte Entitaetstypen, Aliase und fachliche Keywords.

## Technische Dokumentation

### Pipeline von Exzerpt zu JSON

Der Einstiegspunkt ist die CLI in `kgexzerpt/cli.py`. Der Quickstart ruft intern diesen Befehl auf:

```bash
python -m kgexzerpt.cli build exzerpt.md exzerpt2.md --out graph.json --format svelte
```

Die CLI ruft `build_knowledge_graph()` aus `kgexzerpt/pipeline.py` auf. Die Verarbeitung laeuft in vier Schichten:

1. `load_sources()` liest Markdown- oder PDF-Dateien.
2. `KnowledgeGraph` baut aus Dokumenten, Exzerpten, Entitaeten und Relationen die ABox.
3. `add_domain_tbox()` aus `kgexzerpt/ontology.py` fuegt die TBox-Klassen, Synonyme und Klassenrelationen hinzu.
4. `classify_entities_by_aliases()` verbindet ABox-Entitaeten ueber `CLASSIFIED_AS` mit passenden TBox-Klassen.

Intern wird ein `networkx.MultiDiGraph` verwendet. Beim Export erzeugt `to_svelte_json()` daraus eine JSON-Struktur mit `nodes` und `edges`; `export_json()` schreibt diese Struktur als UTF-8 nach `graph.json`.

### JSON-Struktur

Die Datei `graph.json` hat zwei Hauptfelder:

```json
{
  "nodes": [
    {
      "id": "class:it-sicherheit",
      "label": "IT-Sicherheit",
      "kind": "Class",
      "layer": "TBox"
    }
  ],
  "edges": [
    {
      "id": "CLASSIFIED_AS:...",
      "source": "entity:...",
      "target": "class:it-sicherheit",
      "type": "CLASSIFIED_AS",
      "layer": "ABox_to_TBox"
    }
  ]
}
```

Knoten enthalten mindestens `id`, `label` und `kind`. In `withBoxing` gibt es drei wichtige Gruppen:

- ABox-Knoten: `Document`, `Excerpt`, `Concept`, `PER`, `ORG`, `LOC`, `MISC` und weitere erkannte Entitaetstypen.
- TBox-Knoten: `Class`, also gruene Boxen wie `IT-Sicherheit`, `Rettungsdienst`, `Schnittstelle` oder `DIN EN 1789`.
- Synonym-Knoten: `Synonym`, also gelbe gestrichelte Boxen wie `RTW`, `Bluetooth`, `BitLocker` oder `BSI`.

Kanten enthalten mindestens `id`, `source`, `target` und `type`. Zusaetzlich tragen TBox-Kanten `layer: "TBox"`, Klassifizierungskanten `layer: "ABox_to_TBox"` und normale Extraktionskanten keinen Layer oder ABox-Eigenschaften wie `confidence` und `evidence`.

### ABox-Kantentypen

Diese Kanten entstehen aus den Eingabedaten und den extrahierten Textmustern:

- `HAS_EXCERPT`: wird in `add_excerpt()` erzeugt und verbindet Dokumente mit ihren Exzerpten.
- `MENTIONS`: wird in `add_entity()` erzeugt und verbindet ein Exzerpt mit jeder darin erkannten Entitaet.
- `EVIDENCE_FOR`: wird in `add_triple()` erzeugt und verbindet ein Exzerpt mit Subjekt und Objekt einer extrahierten Relation.
- `IS_A`: entsteht bei Mustern wie `ist`, `sind`, `gilt als`, `wird als`.
- `HAS_PART`: entsteht bei Mustern wie `enthaelt`, `umfasst`, `beinhaltet`, `besteht aus`.
- `USES`: entsteht bei Mustern wie `nutzt`, `verwendet`, `setzt ein`.
- `CAUSES_OR_ENABLES`: entsteht bei Mustern wie `fuehrt zu`, `ermoeglicht`, `bewirkt`, `schafft`.
- `DEPENDS_ON`: entsteht bei Mustern wie `haengt ab von`, `abhaengig von`.
- `PART_OF`: entsteht bei Mustern wie `ist Teil von`, `gehoert zu`.

Die Relationsextraktion sitzt in `PatternRelationExtractor`. Sie zerlegt den Exzerptinhalt in Saetze, prueft jeden Satz gegen die definierten Regex-Muster und waehlt fuer Subjekt und Objekt die beste bereits erkannte Entitaet. Gibt es keinen direkten Treffer, wird aus den letzten Woertern des Satzteils ein `Concept` gebildet. Jede extrahierte Relation bekommt eine `confidence`, den Evidenzsatz und die `source_excerpt_id`.

### TBox-Kantentypen

Diese Kanten werden in `kgexzerpt/ontology.py` explizit aufgebaut:

- `SUBCLASS_OF`: ordnet Klassen hierarchisch ein, zum Beispiel `Schwachstelle -> IT-Sicherheit`, `Drahtlose Kommunikation -> Schnittstelle` oder `Rettungswagen (Typ C) -> Rettungsdienstfahrzeug`.
- `SYNONYM_OF`: verbindet Synonym-Knoten mit ihrer Klasse, zum Beispiel `RTW -> Rettungswagen (Typ C)` oder `BitLocker -> Kryptographie und Verschluesselung`.
- `DEFINED_BY`: verbindet normativ definierte Fahrzeugklassen mit `DIN EN 1789`.
- `RELATED_BUT_DISTINCT_FROM`: markiert fachlich verwandte, aber nicht identische Klassen; aktuell `Rettungswagen (Typ C) -> Krankentransportwagen`.
- `USED_IN`: verbindet Klassen mit ihrem Einsatzkontext, zum Beispiel `Medizinprodukt -> Rettungsdienst`.
- `PART_OF`: beschreibt Klassenbestandteile, zum Beispiel `Schnittstelle -> Vernetztes System` oder `Firmware und Update -> Vernetztes System`.
- `RELATED_TO`: beschreibt lose fachliche Naehe, zum Beispiel `Daseinsvorsorge und Gefahrenabwehr -> Rettungsdienst`.
- `SECURITY_MEASURE`: verbindet `Kryptographie und Verschluesselung` mit `IT-Sicherheit`.
- `PROTECTS_OR_ENDANGERS`: verbindet `Daten und Datenschutz` mit `IT-Sicherheit`.

Diese TBox-Kanten haben `layer: "TBox"` und werden in der Visualisierung gruener und staerker gezeichnet.

### CLASSIFIED_AS-Berechnung

`CLASSIFIED_AS` ist die Bruecke von ABox zu TBox. Sie wird nicht aus einem einzelnen Satzmuster gelesen, sondern nach dem Aufbau der TBox automatisch berechnet:

1. Alle `Class`-Knoten werden gesammelt.
2. Fuer jede Klasse werden `aliases`, `keywords` und optional `entity_kinds` normalisiert.
3. Alle ABox-Entitaeten werden durchlaufen; `Class`, `Synonym`, `Document` und `Excerpt` werden uebersprungen.
4. Pro Entitaet werden `label` und `aliases` normalisiert.
5. Eine `CLASSIFIED_AS`-Kante entsteht, wenn einer dieser Tests passt:
   - Der Entitaetstyp passt zu `entity_kinds`, zum Beispiel `ORG -> Organisation` oder `PER -> Person`.
   - Ein Alias stimmt exakt ueberein.
   - Ein Alias mit mindestens fuenf Zeichen ist im Entitaetslabel enthalten oder umgekehrt.
   - Ein Keyword mit mindestens vier Zeichen kommt im Entitaetslabel vor.
6. Die Kante bekommt `layer: "ABox_to_TBox"` und `matched_by`, zum Beispiel `entity_kind:ORG`, `alias` oder `keyword:bluetooth`.

Dadurch entstehen die Box-Verbindungen fuer den ganzen Graphen: Die extrahierten Textknoten bleiben unveraendert, werden aber fachlich an die TBox angebunden.

### Darstellung im Browser

Nach dem Bau kopiert `quickstart.bat` `graph.json` nach `svelte-app/public/graph.json`. Die Svelte-App laedt die Datei in `KnowledgeGraph.svelte` mit:

```js
graph = await fetch(url).then(r => r.json());
```

Danach rendert D3 eine Force-Layout-Simulation:

- `Class` wird als gruene Box gezeichnet.
- `Synonym` wird als gelbe gestrichelte Box gezeichnet.
- ABox-Knoten werden als Kreise gezeichnet.
- `layer: "TBox"` wird als gruene Kante gezeichnet.
- `layer: "ABox_to_TBox"` wird als gestrichelte Klassifizierungskante gezeichnet.
- Normale ABox-Kanten werden grau gezeichnet.
- Das Suchfeld filtert Knoten und zeigt nur Kanten, deren Quelle und Ziel sichtbar bleiben.
- Ein Klick auf einen Knoten zeigt rechts die Rohdaten aus dem JSON.

## Geschichtswissenschaftlicher Anspruch

Der Graph ist kein Ersatz fuer Quellenkritik, sondern ein Werkzeug zur strukturierten Exploration. Jede Wissenseinheit soll aus einem Exzerpt mit Seitenangabe, Inhalt und Anmerkung hervorgehen, damit Aussagen auf ihre Belegstelle zurueckgefuehrt werden koennen. Gerade fuer historische Arbeit ist wichtig, dass der Graph nicht vorgibt, Ambivalenz aufzulosen: Er macht Verdichtungen, wiederkehrende Begriffe, Akteurskonstellationen und moegliche Relationen sichtbar, die anschliessend hermeneutisch und quellenkritisch geprueft werden muessen.

Die automatische Extraktion arbeitet bewusst konservativ. Sie erzeugt Vorschlaege fuer Entitaeten und Relationen, aber keine abschliessenden historischen Urteile. Der wissenschaftliche Mehrwert liegt in der Nachvollziehbarkeit der Belege, der Vergleichbarkeit vieler Exzerpte und der Moeglichkeit, Forschungshypothesen sichtbar zu machen, ohne die argumentative Pruefung auszulagern.

## Manuelle Installation

Falls der Quickstart nicht genutzt werden soll:

```bash
python -m venv .venv
.\.venv\Scripts\activate


```

## benutzte Literatur:

- [Building Knowledge Graphs](https://go.neo4j.com/rs/710-RRC-335/images/Building-Knowledge-Graphs-Practitioner's-Guide-OReilly-book.pdf)
- [Knowledge Graphs data.world.pdf](https://page.data.world/hubfs/Knowledge%20Graphs%20data.world.pdf)
- [Knowledge Graphs](https://web.stanford.edu/class/cs520/How_To_Create_A_Knowledge_Graph_From_Data.pdf)
- [developers-guide-how-to-build-knowledge-graph.pdf](https://content.gitbook.com/content/sasnIfbOiAFHeOBcNUBB/blobs/MAe5jxOScBtqIFO1NjXV/developers-guide-how-to-build-knowledge-graph.pdf)
- [Construction of Knowledge Graphs: Current State and Challenges](https://dbs.uni-leipzig.de/files/research/publications/2024-8/pdf/information-15-00509-with-cover.pdf)
- [Knowledge Graph Chunking for RAG: TBox, ABox, and Advanced Strategies | by Vishal Mysore | Medium](https://medium.com/@visrow/knowledge-graph-chunking-for-rag-tbox-abox-and-advanced-strategies-b922ea286a6c)
