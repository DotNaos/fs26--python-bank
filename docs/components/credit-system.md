# Kreditverwaltung

Die Kreditverwaltung beschreibt den kompletten Lebenszyklus eines Kredits.
Im Repo ist das `kredit.py`.

## Aufgabe der Komponente

Sie kümmert sich um alles, was über ein normales Konto hinausgeht:

- Kreditvergabe
- Kreditgebühr
- freiwillige Rückzahlungen
- monatliche Zinsen
- monatliche Amortisation
- tägliche Strafzinsen
- Abschreibung

## Kreditvergabe

`kredit_vergeben()` setzt die Vergabe in zwei getrennten Schritten um:

1. Kreditbetrag auszahlen
2. Bearbeitungsgebühr belasten

Vorher prüft die Funktion:

- Konto existiert
- es läuft nicht bereits ein aktiver Kredit
- Betrag liegt zwischen CHF 1’000 und CHF 15’000

Danach werden gleichzeitig drei Ebenen aktualisiert:

- Kontostand des Kunden
- Kreditdaten im Konto
- interne Bankbuchung

## Freiwillige Rückzahlung

`kredit_rueckzahlung()` verarbeitet eine freiwillige Rückzahlung:

1. sie prüft, ob ein aktiver Kredit vorhanden ist
2. sie prüft, ob der Kontostand die Rückzahlung deckt
3. sie reduziert die Restschuld und bucht die Bankseite mit

Das hält Kundensaldo, Kreditstand und Bankbuchhaltung zusammen.

## Monatliche Zinsen

`kredit_zinsen_berechnen()` belastet den regulären Kreditzins.
Die Formel orientiert sich an der Moodle-Vorgabe:

- 15 % p. a.
- monatlich berechnet

Die Zinsen werden laut Aufgabenstellung immer belastet, auch wenn der Kontostand dadurch negativ wird.

## Monatliche Amortisation

`kredit_amortisation()` zieht die planmässige Rate ein oder sperrt das Konto, wenn die Rate nicht gedeckt ist.

Die Logik:

- Restschuld
- geteilt durch verbleibende Monate
- ergibt die lineare Tilgung

Auch hier gilt:

- wenn das Konto dadurch unter null fällt, wird gesperrt
- die Rate wird nicht stillschweigend angenommen

## Strafzinsen

`kredit_strafzinsen()` läuft täglich, aber nur für problematische Kredite.

Voraussetzung:

- Kredit ist aktiv
- Kredit ist im Ausfallzustand gesperrt

Dann wird der Strafzins auf den offenen Betrag addiert.
Damit wächst die Schuld weiter, bis wieder genug Geld vorhanden ist.

## Wiederfreigabe

`gesperrtes_konto_bei_eingang_pruefen()` hebt die Sperre wieder auf, wenn nach einem Geldeingang die nächste Rate gedeckt ist.

Das ist der zentrale Übergang zurück von:

- problematischem Kredit
- zu wieder aktivem Konto

## Abschreibung

`kredit_abschreibung_pruefen()` prüft, ob seit der letzten Zahlung sechs Monate vergangen sind.

Wenn ja:

- wird der offene Betrag abgeschrieben
- der Kredit intern als abgeschrieben markiert
- der Verlust auf Bankseite verbucht

Das ist die Stelle, an der aus einem schlechten Kredit ein echter Bankverlust wird.

## Warum diese Komponente wichtig ist

Hier sieht man den Unterschied zwischen einem einfachen Zahlungssystem und einer Bank.
Die Kreditverwaltung verbindet:

- Kundensaldo
- Zeit
- Risiko
- Ertrag
- Verlust

Wenn du die „eigentliche Banklogik“ verstehen willst, ist diese Komponente der Kern.
