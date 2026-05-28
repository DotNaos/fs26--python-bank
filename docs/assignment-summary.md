# Python-Bank Aufgabenstellung

Diese Zusammenfassung basiert auf der Moodle-Datei `Aufgabenstellung Python Bank Update`.
Sie beschreibt, was das System können muss und wie die Abgabe aufgebaut sein soll.

## Was das System fachlich können muss

### Kunden

- Nur natürliche Personen
- Stammdaten:
  - Name
  - Adresse
  - Geburtsdatum
- Kunden können Konten eröffnen und schliessen
- Kundendaten können geändert werden

### Konten

- Genau ein Kontokorrentkonto pro Kunde
- Keine weiteren Kontoarten
- Jedes Konto hat eine IBAN
- Kontoführungsgebühr:
  - CHF 100 pro Jahr
  - quartalsweise belastet
  - also CHF 25 pro Quartal
- Zusätzlich existiert pro Kunde ein Kreditkonto
  - es wird bei der Kontoeröffnung angelegt
  - es bleibt bei null, solange kein Kredit läuft

### Zahlungsverkehr

- Ausgehende Überweisungen auf eine IBAN
- Eingehende Zahlungen auf Kundenkonten
- Kein Bargeld

### Transaktionsdaten

- Alle Eingaben kommen als Datensätze aus Dateien
- Jede Transaktion hat einen eindeutigen Zeitstempel
- Die Reihenfolge wird vollständig über den Zeitstempel bestimmt

### Kredit

- Eröffnung über eine Kredit-Transaktion
- Laufzeit: 1 Jahr
- Betrag:
  - mindestens CHF 1’000
  - höchstens CHF 15’000
- Bearbeitungsgebühr: CHF 250
- Ablauf:
  - Kreditbetrag auf Kundenkonto auszahlen
  - danach Gebühr belasten
- Zinssatz: 15 % p. a.
  - monatlich berechnet
- Rückzahlung:
  - jederzeit ganz oder teilweise möglich
- Amortisation:
  - monatlich automatisch vom Kundenkonto abbuchen
- Zahlungsausfall:
  - Konto sperren, wenn die Belastung das Konto unter null bringen würde
  - normaler Kreditzins läuft weiter
  - zusätzlich 30 % p. a. Strafzins, täglich berechnet
  - Konto erst wieder freigeben, wenn neues Geld eingeht und alles wieder tragbar ist
- Abschreibung:
  - nach 6 Monaten ohne Kreditzahlung als Verlust abschreiben

### Interne Bankbuchhaltung

Es müssen vier interne Bankkonten geführt werden:

- Verpflichtungskonto:
  - Verbindlichkeiten gegenüber Kunden
- Zentralbankkonto:
  - Vermögenskonto der Bank
- Kreditkonto:
  - ausstehende Kredite als Aktivum
- Einnahmenkonto:
  - Gebühren und Zinsen
  - auch Kreditverluste

Zusätzlich gilt:

- Jede Kundentransaktion braucht die passenden Gegenbuchungen
- Die Bilanz muss stimmen:
  - Aktiva = Passiva + Eigenkapital

### Zeitsimulation

- Es gibt eine spezielle Zeit-Transaktion
- Sie stellt den neuen Arbeitstag ein
- Beim Einlesen werden periodische Berechnungen ausgelöst:
  - Gebühren
  - Zinsen
  - Amortisation
  - Strafzinsen
  - Abschreibungen

### Speicherung

- Alles als JSON
- Jedes Konto enthält seine komplette Transaktionshistorie
- Auch abgelehnte Transaktionen müssen gespeichert werden
- Bei Ablehnungen muss der Kontostand vor der Transaktion sichtbar sein
- Die Bankkonten müssen zusätzlich separat ausgegeben werden

## Welche Teilaufgaben laut Moodle umgesetzt werden müssen

### A. Transaktions-Engine

- JSON-Datei einlesen
- Nach Zeitstempel sortieren
- Nach Transaktionstyp an die richtige Funktion weiterleiten
- Zeit-Transaktion verarbeiten

### B. Kontoverwaltung

- Konto eröffnen
- Konto schliessen
- Kundendaten ändern
- Ausgehende Überweisung mit Deckungsprüfung
- Eingehende Zahlung verbuchen

### C. Kreditverwaltung

- Kredit vergeben
- Kredit amortisieren
- Kreditzinsen berechnen
- Strafzinsen berechnen
- Freiwillige Rückzahlung verarbeiten
- Abschreibung prüfen

### D. Buchungssystem

- Vier interne Bankkonten führen
- Gegenbuchungen für jede relevante Kundenaktion
- Bilanzprüfung

### E. Speicherung und Ausgabe

- Kontodaten inklusive Historie speichern
- Abgelehnte Transaktionen mitspeichern
- Bankkonten separat ausgeben

### F. Zeitsimulation und Test

- Zeit-Transaktionen korrekt verarbeiten
- Quartalsgebühren, Monatsläufe und tägliche Strafzinsen korrekt auslösen
- Gegen die bereitgestellten Testdaten validieren

## Wie die Abgabe aussehen soll

### Python-Dateien

Moodle nennt diese Zielstruktur:

- `engine.py`
- `konten.py`
- `kredit.py`
- `buchung.py`
- `speicherung.py`

Wichtig ist laut Aufgabenstellung:

- nur Funktionen
- keine Klassen
- keine objektorientierte Architektur

### Ausgabe-Dateien

- pro Kunde eine JSON-Datei
- zusätzlich eine JSON-Datei für die Bankkonten

### Dokumentation

- kurze Beschreibung der Architektur
- kurze Beschreibung der getroffenen Entscheidungen

## Was bei der Validierung entscheidend ist

Die bereitgestellten Referenzdaten sind nicht nur Beispielmaterial.
Laut Moodle soll die Software am Ende dieselben Kontostände und dieselben Transaktionshistorien erzeugen.
