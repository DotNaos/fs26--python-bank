# Bankbuchungssystem

Das Bankbuchungssystem bildet dieselben Vorgänge aus Sicht der Bank ab.
Im Repo ist das `buchung.py`.

## Aufgabe der Komponente

Die Kundenkonten allein reichen nicht aus.
Eine Bank muss zusätzlich ihre eigene Bilanzseite mitführen.

Diese Komponente verwaltet vier interne Konten:

- `zentralbankkonto`
- `verpflichtungskonto`
- `kreditkonto_aktiva`
- `einnahmenkonto`

## Bedeutung der vier Konten

### Zentralbankkonto

Das ist das liquide Vermögen der Bank.
Bei Einzahlungen steigt es, bei Auszahlungen sinkt es.

### Verpflichtungen gegenüber Kunden

Das ist die Schuld der Bank gegenüber ihren Kunden.
Wenn Kundenguthaben steigen, steigt auch dieses Konto.
Wenn Geld abfliesst, sinkt es.

### Kreditkonto

Das sind die offenen Kredite als Aktivum der Bank.
Wenn ein Kredit vergeben wird, steigt dieses Konto.
Wenn Kredite zurückgezahlt oder abgeschrieben werden, sinkt es.

### Einnahmenkonto

Hier landen:

- Gebühren
- Zinsen

Hier landen aber auch Verluste, wenn Kredite abgeschrieben werden.

## Buchungsregeln

`buchung_erfassen()` setzt diese Gegenlogik um und hält zusätzlich die Buchungsliste fest.

Beispiele:

- `ueberweisung_ein`
  - Zentralbank rauf
  - Verpflichtungen rauf
- `ueberweisung_aus`
  - Verpflichtungen runter
  - Zentralbank runter
- `kredit_auszahlung`
  - Kreditkonto rauf
  - Verpflichtungen rauf
- `kredit_gebuehr`
  - Verpflichtungen runter
  - Einnahmen rauf
- `kredit_amortisation` und `kredit_rueckzahlung`
  - Verpflichtungen runter
  - Kreditkonto runter
- `kredit_zinsen`
  - Verpflichtungen runter
  - Einnahmen rauf
- `kredit_abschreibung`
  - Einnahmen runter
  - Kreditkonto runter

## Bilanzprüfung

`bilanz_pruefen()` prüft, ob die Bankbilanz noch stimmt.

Vereinfacht wird geprüft:

- Aktiva:
  - Zentralbankkonto
  - Kreditkonto
- Passiva plus Erfolg:
  - Verpflichtungen
  - Einnahmen

Wenn die Differenz zu gross wird, löst das System einen Fehler aus.

## Warum diese Komponente wichtig ist

Ohne diese Komponente wäre das System nur ein Kontosimulator.
Erst hier wird es zu einem Banksystem, weil jede Kundenaktion zusätzlich eine Bankwirkung hat.

Diese Schicht zeigt:

- warum eine Einzahlung für die Bank nicht neutral ist
- warum ein Kredit gleichzeitig Guthaben beim Kunden und Risiko bei der Bank erzeugt
- warum Zinsen und Gebühren den Gewinn verändern
