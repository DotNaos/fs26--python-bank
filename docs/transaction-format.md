# Transaction Format

Use one JSON list.
Each entry must be one transaction object.

## Required Base Fields

Every transaction needs:

- `typ`
- `zeitstempel`

`zeitstempel` must look like this:

```json
"2026-01-02T08:00:00Z"
```

## Supported Transaction Types

### Time step

```json
{
  "typ": "zeit",
  "zeitstempel": "2026-01-02T08:00:00Z",
  "datum": "2026-01-02"
}
```

### Open account

```json
{
  "typ": "konto_eroeffnen",
  "zeitstempel": "2026-01-02T09:00:00Z",
  "kunde": {
    "name": "Anna Muster",
    "adresse": "Bahnhofstrasse 1, 7000 Chur",
    "geburtsdatum": "1990-05-15"
  }
}
```

The customer object also accepts `address` and `birth_date`.

### Incoming transfer

```json
{
  "typ": "ueberweisung_ein",
  "zeitstempel": "2026-01-02T10:00:00Z",
  "ziel_iban": "CH0001",
  "betrag": 5000.0,
  "waehrung": "CHF",
  "absender_iban": "CH9999",
  "referenz": "Lohn Januar"
}
```

### Outgoing transfer

```json
{
  "typ": "ueberweisung_aus",
  "zeitstempel": "2026-01-03T09:00:00Z",
  "von_iban": "CH0001",
  "nach_iban": "CHEXTERN1234",
  "betrag": 750.0
}
```

### Credit request

```json
{
  "typ": "kredit_antrag",
  "zeitstempel": "2026-01-15T14:00:00Z",
  "kunden_iban": "CH0001",
  "betrag": 10000.0
}
```

### Credit repayment

```json
{
  "typ": "kredit_rueckzahlung",
  "zeitstempel": "2026-02-05T10:00:00Z",
  "kunden_iban": "CH0001",
  "betrag": 500.0
}
```

## Sample File

This scaffold does not include sample transaction files.
When implementation work starts, add representative fixtures under `tests/fixtures/` and document the default sample file here.
