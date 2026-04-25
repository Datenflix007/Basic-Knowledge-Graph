# Basic Knowledge Graph

Werkzeug zum Erzeugen und Erkunden eines nachvollziehbaren Wissensgraphen aus historischen Exzerpten. Die Exzerpte werden aus Markdown-Tabellen oder PDFs gelesen, in Dokument-, Exzerpt-, Entitaets- und Relationsknoten ueberfuehrt und anschliessend in einer Svelte/D3-Visualisierung angezeigt.

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

Gruene Boxen markieren die TBox, also die begriffliche Ordnung des Wissensgraphen: Klassen, Unterklassen und Synonyme. Der Graph enthaelt z. B. eine kleine DIN-EN-1789-Systematik fuer Rettungsdienstfahrzeuge mit `Rettungsdienstfahrzeug`, `Krankentransportwagen`, `Krankentransportwagen Typ A1/A2`, `Notfallkrankenwagen` und `Rettungswagen (Typ C)`. Synonyme wie `RTW`, `Rettungswagen` oder `KTW Typ C` werden als eigene Synonym-Knoten an die passende Klasse gebunden. Normale Entitaeten und belegte Exzerptaussagen bleiben die ABox und werden ueber `CLASSIFIED_AS` an diese Klassen angeschlossen.

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
