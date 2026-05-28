# System-Überblick

Dieses System ist eine kleine Bank-Simulation.
Es verarbeitet Transaktionen aus JSON-Dateien und hält dabei gleichzeitig zwei Ebenen konsistent:

- die Kundenkonten
- die internen Bankkonten

## Der Hauptfluss

1. Eine JSON-Datei mit Transaktionen wird eingelesen.
2. Die Engine sortiert alles nach Zeitstempel.
3. Jede Transaktion wird an die passende Fachfunktion weitergegeben.
4. Fachfunktionen ändern:
   - Kundenkonten
   - Kreditdaten
   - interne Bankkonten
   - Transaktionshistorien
5. Am Ende wird der gesamte Zustand wieder als JSON gespeichert.

## Die fünf Hauptkomponenten

### 1. Transaktions-Engine

Die Engine ist der Dirigent.
Sie entscheidet nicht die Fachlogik im Detail, aber sie entscheidet:

- in welcher Reihenfolge verarbeitet wird
- welche Funktion für welchen Datensatz zuständig ist
- wann Zeitereignisse Monats- oder Quartalslogik auslösen

### 2. Kontoverwaltung

Die Kontoverwaltung kümmert sich um alles, was direkt am Kundenkonto passiert:

- Konto eröffnen
- Konto schliessen
- Kundendaten anpassen
- eingehende Zahlungen
- ausgehende Zahlungen
- Kontogebühren

### 3. Kreditverwaltung

Die Kreditverwaltung steuert den Lebenszyklus eines Kredits:

- Kreditvergabe
- Kreditgebühr
- freiwillige Rückzahlung
- monatliche Zinsen
- monatliche Amortisation
- Strafzinsen
- Abschreibung

### 4. Bankbuchungssystem

Diese Komponente bildet dieselben Vorgänge aus Sicht der Bank ab.
Sie führt die vier internen Bankkonten:

- Zentralbank
- Verpflichtungen
- Kredite
- Einnahmen

Damit wird sichtbar, ob die Kundenvorgänge auch buchhalterisch korrekt gespiegelt werden.

### 5. Speicherung

Die Speicherung schreibt den aktuellen Stand in JSON-Dateien zurück.
So kann man das Ergebnis prüfen oder mit Referenzdaten vergleichen.

## Das zentrale Datenmodell

Das ganze System arbeitet mit einem gemeinsamen `bank_status`.
Das ist ein grosses Python-Dictionary mit fünf wichtigen Bereichen:

- `aktuelles_datum`
- `konten`
- `bankkonten`
- `meta`

Dadurch greifen alle Komponenten auf denselben Zustand zu, statt eigene isolierte Objekte zu pflegen.

## Warum man mit dieser Doku das ganze Banksystem versteht

Wenn du die Komponenten in der Reihenfolge unten liest, siehst du den kompletten Weg einer Banktransaktion:

1. Eingang in die Engine
2. Änderung am Kundenkonto
3. Änderung an Kreditdaten, falls nötig
4. Gegenbuchung in den Bankkonten
5. Speicherung als Ausgabedatei

Genau diese Kette bildet die eigentliche Funktionsweise des Systems ab.
