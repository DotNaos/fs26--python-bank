# Transaktions-Engine

Die Transaktions-Engine ist das zentrale Steuermodul des Systems.
Im Repo ist das `engine.py`.

## Aufgabe der Engine

Die Engine beantwortet vier Kernfragen:

- Welche Transaktionen kommen rein?
- In welcher Reihenfolge müssen sie verarbeitet werden?
- Welche Fachfunktion ist zuständig?
- Wann müssen periodische Prozesse ausgelöst werden?

## Was in der Engine passiert

### 1. Startzustand aufbauen

`bank_status_anlegen()` aus `konten.py` erzeugt den gesamten Anfangszustand.
Dazu gehören:

- Konten
- interne Bankkonten
- Metadaten über Verarbeitung und Fehler

Das ist wichtig, weil danach alle anderen Komponenten auf denselben Zustand schreiben.

### 2. Transaktionen laden

`transaktionen_laden()` liest eine JSON-Datei oder ein Verzeichnis mit Monatsdateien ein.
Erwartet wird pro Datei eine Liste von Datensätzen.

Wenn die Datei fehlt oder kein JSON-Array enthält, stoppt die Verarbeitung sofort.

### 3. Nach Tagen gruppieren und Tages-Batch sortieren

`transaktionen_nach_tag_gruppieren()` gruppiert die Eingangsliste nach Arbeitstag.
`tages_batch_sortieren()` bringt die Transaktionen innerhalb des Tages in die Moodle-Reihenfolge:

- Kontoeröffnungen
- Eingänge
- Zeit-Transaktion mit periodischer Verarbeitung
- Kredite
- Stammdatenänderungen und Schliessungen
- Ausgänge

### 4. Dispatch

`transaktion_ausfuehren()` ist der Umschalter zwischen Datensatz und Fachlogik.
Hier wird anhand von `typ` entschieden, welche Funktion aufgerufen wird.

Beispiele:

- `konto_eroeffnen` geht an die Kontoverwaltung
- `kredit_antrag` geht an die Kreditverwaltung
- `zeit` bleibt in der Engine, weil sie die periodischen Läufe steuert

## Zeit-Transaktionen

Die wichtigste Sonderrolle der Engine ist die Behandlung von `zeit`.

`periodische_verarbeitung()` macht drei Dinge:

1. Den aktuellen Tag im System fortschreiben
2. Tagesprozesse anstossen
3. Falls nötig Monats- oder Quartalsprozesse auslösen

### Monatsprozesse

`monatliche_kreditverarbeitung()` startet:

- monatliche Kreditzinsen
- monatliche Kreditamortisation
- Abschreibungsprüfung

### Quartalsprozesse

`quartalsgebuehren_belasten()` startet:

- Kontoführungsgebühren

### Tagesprozesse

`taegliche_strafzinsen()` bucht tägliche Strafzinsen für gesperrte Konten.

Damit setzt die Engine genau die Moodle-Idee um, dass die Zeit-Transaktion die internen Berechnungen auslöst.

## Fehlerbehandlung

Fachliche Ablehnungen werden als Einträge in der betroffenen Kontohistorie gespeichert.
Beispiele sind fehlende Deckung, gesperrte Konten oder nicht mögliche Rückzahlungen.

So bleibt die restliche Datei weiter verarbeitbar.

## Warum die Engine für das Gesamtverständnis wichtig ist

Wenn du verstehen willst, wie aus einer Datei ein Banksystem in Bewegung wird, musst du die Engine verstehen.
Sie ist der Übergang zwischen:

- rohen JSON-Daten
- fachlicher Verarbeitung
- periodischer Banklogik
- finaler Ausgabe
