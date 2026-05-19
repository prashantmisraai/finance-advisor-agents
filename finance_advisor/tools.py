from __future__ import annotations

import csv
from collections import defaultdict
from datetime import date
from pathlib import Path
from statistics import mean

from finance_advisor.models import Transaction


def load_transactions(csv_path: Path, customer_id: str) -> list[Transaction]:
    rows: list[Transaction] = []
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if row["customer_id"] != customer_id:
                continue
            rows.append(
                Transaction(
                    transaction_id=row["transaction_id"],
                    customer_id=row["customer_id"],
                    date=date.fromisoformat(row["date"]),
                    merchant=row["merchant"],
                    category=row["category"],
                    amount=float(row["amount"]),
                    type=row["type"].lower(),
                )
            )
    return rows


def infer_latest_month(transactions: list[Transaction]) -> str:
    if not transactions:
        raise ValueError("No transactions available.")
    latest = max(txn.date for txn in transactions)
    return latest.strftime("%Y-%m")


def filter_month(transactions: list[Transaction], month: str) -> list[Transaction]:
    return [txn for txn in transactions if txn.date.strftime("%Y-%m") == month]


def monthly_totals(transactions: list[Transaction]) -> dict[str, dict[str, float]]:
    totals: dict[str, dict[str, float]] = defaultdict(lambda: {"income": 0.0, "spend": 0.0})
    for txn in transactions:
        month_key = txn.date.strftime("%Y-%m")
        if txn.type == "credit":
            totals[month_key]["income"] += txn.amount
        else:
            totals[month_key]["spend"] += txn.amount
    return {month: dict(values) for month, values in sorted(totals.items())}


def category_spend(transactions: list[Transaction]) -> dict[str, float]:
    totals: dict[str, float] = defaultdict(float)
    for txn in transactions:
        if txn.type == "debit":
            totals[txn.category] += txn.amount
    return dict(sorted(totals.items(), key=lambda item: item[1], reverse=True))


def merchant_spend(transactions: list[Transaction]) -> dict[str, float]:
    totals: dict[str, float] = defaultdict(float)
    for txn in transactions:
        if txn.type == "debit":
            totals[txn.merchant] += txn.amount
    return dict(sorted(totals.items(), key=lambda item: item[1], reverse=True))


def compare_to_baseline(
    transactions: list[Transaction], month: str, current_category_spend: dict[str, float]
) -> dict[str, dict[str, float]]:
    historical: dict[str, list[float]] = defaultdict(list)
    month_keys = sorted({txn.date.strftime("%Y-%m") for txn in transactions if txn.date.strftime("%Y-%m") < month})

    for month_key in month_keys:
        month_spend = category_spend(filter_month(transactions, month_key))
        for category, amount in month_spend.items():
            historical[category].append(amount)

    comparison: dict[str, dict[str, float]] = {}
    for category, current in current_category_spend.items():
        previous_values = historical.get(category, [])
        baseline = mean(previous_values) if previous_values else 0.0
        delta = current - baseline
        percent_change = (delta / baseline * 100) if baseline else 0.0
        comparison[category] = {
            "current": round(current, 2),
            "baseline": round(baseline, 2),
            "delta": round(delta, 2),
            "percent_change": round(percent_change, 1),
        }
    return comparison


def find_unusual_transactions(month_transactions: list[Transaction]) -> list[dict[str, str | float]]:
    debits = [txn for txn in month_transactions if txn.type == "debit"]
    if not debits:
        return []

    by_category: dict[str, list[float]] = defaultdict(list)
    for txn in debits:
        by_category[txn.category].append(txn.amount)

    unusual: list[dict[str, str | float]] = []
    for txn in debits:
        category_values = by_category[txn.category]
        category_avg = mean(category_values)
        high_category_item = len(category_values) > 1 and txn.amount >= category_avg * 1.75
        high_absolute_item = txn.amount >= 400.0
        if high_category_item or high_absolute_item:
            unusual.append(
                {
                    "transaction_id": txn.transaction_id,
                    "date": txn.date.isoformat(),
                    "merchant": txn.merchant,
                    "category": txn.category,
                    "amount": round(txn.amount, 2),
                    "reason": "large relative to category" if high_category_item else "large absolute spend",
                }
            )
    return sorted(unusual, key=lambda item: float(item["amount"]), reverse=True)


def savings_rate(income: float, spend: float) -> float:
    if income <= 0:
        return 0.0
    return round((income - spend) / income * 100, 1)
