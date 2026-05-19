from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


class CustomerMemory:
    """Tiny JSON-backed memory for preferences, previous insights, and runs."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._store: dict[str, Any] = self._load()

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}

    def get_customer(self, customer_id: str) -> dict[str, Any]:
        return self._store.setdefault(
            customer_id,
            {
                "preferences": {
                    "dining_budget": 260.0,
                    "shopping_budget": 350.0,
                    "travel_budget": 300.0,
                    "monthly_savings_goal": 1000.0,
                },
                "recent_runs": [],
                "last_insights": {},
            },
        )

    def remember_run(self, customer_id: str, query: str, route: list[str], final_answer: str) -> None:
        customer = self.get_customer(customer_id)
        customer["recent_runs"].append(
            {
                "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
                "query": query,
                "route": route,
                "final_answer": final_answer[:700],
            }
        )
        customer["recent_runs"] = customer["recent_runs"][-5:]
        self.save()

    def remember_insights(self, customer_id: str, insights: dict[str, Any]) -> None:
        self.get_customer(customer_id)["last_insights"] = insights
        self.save()

    def save(self) -> None:
        self.path.write_text(json.dumps(self._store, indent=2), encoding="utf-8")
