from __future__ import annotations

from pathlib import Path
from typing import Any

from finance_advisor.models import AgentResult, AgentState, ToolCall
from finance_advisor.tools import (
    category_spend,
    compare_to_baseline,
    filter_month,
    find_unusual_transactions,
    infer_latest_month,
    load_transactions,
    merchant_spend,
    monthly_totals,
    savings_rate,
)


class SpendingAnalysisAgent:
    """Deep agent: performs tool-style analysis over customer transactions."""

    name = "spending_analysis_agent"

    def __init__(self, transactions_path: Path) -> None:
        self.transactions_path = transactions_path

    def run(self, state: AgentState) -> AgentResult:
        reasoning_trace: list[str] = []
        tool_calls: list[ToolCall] = []

        transactions = load_transactions(self.transactions_path, state.customer_id)
        tool_calls.append(
            ToolCall(
                name="load_transactions",
                input={"customer_id": state.customer_id, "path": str(self.transactions_path)},
                output_summary=f"Loaded {len(transactions)} transactions.",
            )
        )
        reasoning_trace.append("Loaded customer transactions and limited analysis to the active customer.")

        month = state.month or infer_latest_month(transactions)
        month_transactions = filter_month(transactions, month)
        tool_calls.append(
            ToolCall(
                name="filter_month",
                input={"month": month},
                output_summary=f"Selected {len(month_transactions)} transactions for {month}.",
            )
        )
        reasoning_trace.append(f"Selected {month} as the target month for spending analysis.")

        totals_by_month = monthly_totals(transactions)
        current_totals = totals_by_month.get(month, {"income": 0.0, "spend": 0.0})
        tool_calls.append(
            ToolCall(
                name="monthly_totals",
                input={"months": "all"},
                output_summary=f"Current spend ${current_totals['spend']:.2f}, income ${current_totals['income']:.2f}.",
            )
        )
        reasoning_trace.append("Calculated income, debit spend, and savings rate to understand cash-flow health.")

        current_category_spend = category_spend(month_transactions)
        top_merchants = merchant_spend(month_transactions)
        tool_calls.append(
            ToolCall(
                name="category_spend",
                input={"month": month},
                output_summary=f"Found {len(current_category_spend)} spending categories.",
            )
        )

        baseline_comparison = compare_to_baseline(transactions, month, current_category_spend)
        tool_calls.append(
            ToolCall(
                name="compare_to_baseline",
                input={"month": month, "categories": list(current_category_spend)},
                output_summary="Compared current category spend with prior-month averages.",
            )
        )
        reasoning_trace.append("Compared each category to historical baseline to catch behavior shifts.")

        unusual_transactions = find_unusual_transactions(month_transactions)
        tool_calls.append(
            ToolCall(
                name="find_unusual_transactions",
                input={"month": month},
                output_summary=f"Flagged {len(unusual_transactions)} unusual transactions.",
            )
        )
        reasoning_trace.append("Flagged individual large transactions for proactive alerting.")

        insights = self._build_insights(
            month=month,
            totals=current_totals,
            category_spend=current_category_spend,
            merchant_spend=top_merchants,
            comparison=baseline_comparison,
            unusual_transactions=unusual_transactions,
        )

        summary = self._summarize(insights)
        return AgentResult(
            agent_name=self.name,
            summary=summary,
            data=insights,
            reasoning_trace=reasoning_trace,
            tool_calls=tool_calls,
        )

    def _build_insights(
        self,
        month: str,
        totals: dict[str, float],
        category_spend: dict[str, float],
        merchant_spend: dict[str, float],
        comparison: dict[str, dict[str, float]],
        unusual_transactions: list[dict[str, Any]],
    ) -> dict[str, Any]:
        spend = totals["spend"]
        income = totals["income"]
        rate = savings_rate(income, spend)
        top_categories = list(category_spend.items())[:5]
        increased_categories = [
            {"category": category, **values}
            for category, values in comparison.items()
            if values["baseline"] > 0 and values["percent_change"] >= 30
        ]
        increased_categories.sort(key=lambda item: item["delta"], reverse=True)

        return {
            "month": month,
            "income": round(income, 2),
            "total_spend": round(spend, 2),
            "net_cash_flow": round(income - spend, 2),
            "savings_rate": rate,
            "category_spend": {key: round(value, 2) for key, value in category_spend.items()},
            "top_categories": [{"category": key, "amount": round(value, 2)} for key, value in top_categories],
            "top_merchants": [
                {"merchant": key, "amount": round(value, 2)} for key, value in list(merchant_spend.items())[:5]
            ],
            "baseline_comparison": comparison,
            "increased_categories": increased_categories[:5],
            "unusual_transactions": unusual_transactions,
        }

    def _summarize(self, insights: dict[str, Any]) -> str:
        top = insights["top_categories"][0] if insights["top_categories"] else {"category": "none", "amount": 0}
        unusual_count = len(insights["unusual_transactions"])
        return (
            f"For {insights['month']}, spend was ${insights['total_spend']:.2f} against "
            f"${insights['income']:.2f} income, leaving ${insights['net_cash_flow']:.2f}. "
            f"Top category: {top['category']} (${top['amount']:.2f}). "
            f"Unusual transactions flagged: {unusual_count}."
        )
