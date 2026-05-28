# Speicherung und Ausgabe

Die Speicher-Komponente macht den Systemzustand nach aussen sichtbar.
Im Repo ist das `speicherung.py`.

## Aufgabe der Komponente

Nach der Verarbeitung müssen die Ergebnisse nicht nur im Speicher existieren.
Sie müssen als JSON-Dateien ausgegeben werden, damit man:

- Konten prüfen kann
- Resultate mit Referenzdaten vergleichen kann
- Fehler nachvollziehen kann

## Welche Dateien geschrieben werden

### Pro Kunde eine Datei

`daten_speichern()` schreibt für jedes Konto eine eigene JSON-Datei.

Darin stehen:

- IBAN
- Kundendaten
- Kontostand
- Kreditstand
- Status
- komplette Transaktionshistorie

### Eine Datei für die Bankkonten

`daten_speichern()` schreibt die vier internen Bankkonten separat nach `bankkonten.json`.

Damit sieht man sofort die Bankseite des Systems, ohne jede Kundendatei einzeln lesen zu müssen.

### Eine Zusammenfassung

`daten_speichern()` schreibt `zusammenfassung.json` mit Zeitraum, Anzahl Kunden, Anzahl Transaktionen, Anzahl Bankbuchungen und den wichtigsten Endständen.

## Exportstruktur

`konto_exportieren()` baut die Kundenstruktur vor dem Schreiben auf.

Die Funktion hat eine wichtige Zusatzrolle:

- sie erzeugt eine einheitliche Ausgabe

## Warum diese Komponente wichtig ist

Diese Komponente macht das System prüfbar.
Ohne sie könnte man die fachliche Korrektheit kaum sauber vergleichen.

Gerade für die Moodle-Aufgabe ist das zentral, weil die Abgabe am Ende an den erzeugten JSON-Dateien gemessen wird.
