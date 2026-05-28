import json
from pathlib import Path
from typing import Any

from .accounts import export_account
from .ledger import export_ledger, round_money


def load_transactions(path: str | Path) -> list[dict[str, Any]]:
    input_path = Path(path)
    files = [input_path] if input_path.is_file() else sorted(input_path.glob("*.json"))
    if not files:
        raise FileNotFoundError(f"No transaction files found: {input_path}")

    transactions: list[dict[str, Any]] = []
    for file in files:
        data = json.loads(file.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError(f"Transaction file must contain a JSON list: {file}")
        transactions.extend(data)
    return transactions


def save_outputs(bank_state: dict[str, Any], output_dir: str | Path) -> None:
    output_path = Path(output_dir)
    accounts_dir = output_path / "konten"
    accounts_dir.mkdir(parents=True, exist_ok=True)

    for account in bank_state["accounts"].values():
        data = export_account(account)
        filename = f"{customer_filename(account['customer']['name'])}.json"
        write_json(accounts_dir / filename, data)

    ledger = export_ledger(bank_state)
    write_json(output_path / "bankkonten.json", ledger)
    write_json(output_path / "zusammenfassung.json", create_summary(bank_state, ledger))


def create_summary(bank_state: dict[str, Any], ledger: dict[str, Any]) -> dict[str, Any]:
    transactions = bank_state.get("input_transactions", [])
    return {
        "simulation_start": min((tx["datum"] for tx in transactions if tx["typ"] == "zeit"), default=None),
        "simulation_end": max((tx["datum"] for tx in transactions if tx["typ"] == "zeit"), default=None),
        "anzahl_kunden": len(bank_state["accounts"]),
        "anzahl_transaktionen": len(transactions),
        "anzahl_buchungen": len(bank_state["ledger"]["entries"]),
        "kontostande": summarize_accounts(bank_state),
        "bankkonten": {
            key: ledger[key]
            for key in ("zentralbankkonto", "verpflichtungskonto", "kreditkonto_aktiva", "einnahmenkonto")
        },
    }


def summarize_accounts(bank_state: dict[str, Any]) -> dict[str, Any]:
    return {
        account["iban"]: {
            "name": account["customer"]["name"],
            "kontostand": round_money(account["balance"]),
            "kredit_stand": round_money(account["credit_balance"]),
            "status": account["status"],
            "anzahl_transaktionen": len(account["transactions"]),
        }
        for account in bank_state["accounts"].values()
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def read_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def customer_filename(name: str) -> str:
    return (
        name.lower()
        .replace("ä", "ae")
        .replace("ö", "oe")
        .replace("ü", "ue")
        .replace("ß", "ss")
        .replace(" ", "_")
    )

