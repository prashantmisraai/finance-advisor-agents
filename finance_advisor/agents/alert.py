from __future__ import annotations

from finance_advisor.models import AgentResult, AgentState


class AlertAgent:
    name = "alert_agent"

    def run(self, state: AgentState) -> AgentResult:
        spending = state.results.get("spending_analysis_agent")
        if not spending:
            return AgentResult(self.name, "Run spending analysis first.", {"alerts": []})

        insights = spending.data
        preferences = state.memory.get("preferences", {})
        alerts: list[dict[str, str]] = []

        for category in insights.get("increased_categories", []):
            alerts.append(
                {
                    "severity": "medium",
                    "message": (
                        f"{category['category']} spending is up {category['percent_change']}% "
                        f"versus baseline (${category['delta']:.2f} higher)."
                    ),
                }
            )

        for txn in insights.get("unusual_transactions", []):
            alerts.append(
                {
                    "severity": "high" if float(txn["amount"]) >= 500 else "medium",
                    "message": f"Unusual {txn['category']} transaction: {txn['merchant']} for ${txn['amount']}.",
                }
            )

        dining_budget = preferences.get("dining_budget", 260.0)
        dining_spend = insights["category_spend"].get("Dining", 0.0)
        if dining_spend > dining_budget:
            alerts.append(
                {
                    "severity": "medium",
                    "message": f"Dining budget exceeded by ${dining_spend - dining_budget:.2f}.",
                }
            )

        travel_budget = preferences.get("travel_budget", 300.0)
        travel_spend = insights["category_spend"].get("Travel", 0.0)
        if travel_spend > travel_budget:
            alerts.append(
                {
                    "severity": "medium",
                    "message": f"Travel budget exceeded by ${travel_spend - travel_budget:.2f}.",
                }
            )

        return AgentResult(
            agent_name=self.name,
            summary=f"Generated {len(alerts)} proactive alerts.",
            data={"alerts": alerts},
            reasoning_trace=["Checked threshold breaches, behavior shifts, and unusual transactions."],
        )
