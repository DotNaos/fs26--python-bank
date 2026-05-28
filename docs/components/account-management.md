# Kontoverwaltung

Die Kontoverwaltung beschreibt alles, was direkt mit dem Kundenkonto passiert.
Im Repo ist das vor allem `konten.py`.

## Aufgabe der Komponente

Die Kontoverwaltung ist für den sichtbaren Zustand des Kunden zuständig:

- welches Konto existiert
- welche Stammdaten gespeichert sind
- wie hoch der Kontostand ist
- welche Transaktionen auf dem Konto stehen
- ob das Konto aktiv, gesperrt oder geschlossen ist

## Kontoeröffnung

`konto_eroeffnen()` macht mehr als nur ein Konto anzulegen.

Die Funktion:

- vergibt eine neue IBAN
- legt das eigentliche Konto an
- legt gleichzeitig die Kreditstruktur an
- schreibt die erste Transaktion in die Historie

Wichtig ist dabei:

- pro Kunde genau ein aktives Konto im Systemmodell
- zusätzlich existiert die Kreditstruktur schon ab Beginn

Das passt zur Moodle-Vorgabe, dass bei Kontoeröffnung auch das Kreditkonto vorhanden sein soll.

## Kundendaten ändern

`kunden_daten_aendern()` aktualisiert Name, Adresse und Geburtsdatum.

Jede Änderung wird als Transaktion mitprotokolliert.

## Eingehende Zahlung

`einzahlung_verbuchen()` verbucht Geld, das von aussen auf ein Kundenkonto kommt.

Dabei passieren zwei Dinge gleichzeitig:

1. Das Kundenkonto wird erhöht
2. Die Bankbuchung wird über `buchung_erfassen()` gespiegelt

Dadurch bleibt nicht nur der Kontostand richtig, sondern auch die interne Bankbilanz.

## Ausgehende Zahlung

`ueberweisung_ausfuehren()` behandelt zwei Fälle:

- interne Überweisung zwischen zwei Kundenkonten
- externe Überweisung an eine fremde IBAN

Vorher wird geprüft:

- Betrag muss positiv sein
- Senderkonto muss aktiv sein
- Deckung muss vorhanden sein

Bei internen Zahlungen werden nur die beiden Kundenkonten angepasst.
Bei externen Zahlungen wird zusätzlich die Bankbuchung ausgelöst.

## Konto schliessen

`konto_schliessen()` erlaubt die Schliessung nur, wenn:

- Kontostand null ist
- gesamter offener Kredit null ist

Wenn das nicht erfüllt ist, wird die Transaktion als abgelehnt protokolliert.
Das entspricht direkt der offiziellen Aufgabenstellung.

## Quartalsgebühren

`quartalsgebuehren_belasten()` zieht CHF 25 pro Quartal ein.

Das ist die technische Umsetzung von:

- CHF 100 pro Jahr
- quartalsweise belastet

Die Gebühr wird gemäss Moodle auch dann belastet, wenn der Kontostand dadurch negativ wird.

## Warum diese Komponente wichtig ist

Die Kontoverwaltung ist die Oberfläche des Banksystems aus Kundensicht.
Hier sieht man am klarsten:

- welche Aktionen ein Kunde auslösen kann
- welche Prüfungen davor liegen
- wie sich Kontostand und Historie verändern

Wer das Kundenverhalten im System verstehen will, muss diese Komponente zuerst lesen.
