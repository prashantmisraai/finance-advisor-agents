from __future__ import annotations

from finance_advisor.models import AgentResult, AgentState


class RecommendationAgent:
    name = "recommendation_agent"

    def run(self, state: AgentState) -> AgentResult:
        spending = state.results.get("spending_analysis_agent")
        if not spending:
            return AgentResult(self.name, "Run spending analysis first.", {"recommendations": []})

        insights = spending.data
        preferences = state.memory.get("preferences", {})
        recommendations: list[str] = []

        dining = insights["category_spend"].get("Dining", 0.0)
        dining_budget = preferences.get("dining_budget", 260.0)
        if dining > dining_budget:
            recommendations.append(
                f"Cap dining at ${dining_budget:.0f} next month by moving 2-3 meals from delivery to planned groceries."
            )

        shopping = insights["category_spend"].get("Shopping", 0.0)
        shopping_budget = preferences.get("shopping_budget", 350.0)
        if shopping > shopping_budget:
            recommendations.append(
                "Use a 48-hour rule for non-essential shopping; this month has large discretionary purchases."
            )

        savings_goal = preferences.get("monthly_savings_goal", 1000.0)
        if insights["net_cash_flow"] < savings_goal:
            gap = savings_goal - insights["net_cash_flow"]
            recommendations.append(
                f"To hit the ${savings_goal:.0f} savings goal, reduce flexible spend by about ${gap:.0f}."
            )

        if insights["savings_rate"] >= 20:
            recommendations.append("Savings rate is healthy; route surplus into an emergency fund or short-term goal.")

        if not recommendations:
            recommendations.append("Current spending is broadly on track; keep monitoring flexible categories weekly.")

        return AgentResult(
            agent_name=self.name,
            summary="Generated personalized recommendations from spending insights.",
            data={"recommendations": recommendations},
            reasoning_trace=["Mapped spend categories and savings gap to simple customer actions."],
        )
