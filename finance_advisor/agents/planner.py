from __future__ import annotations

from finance_advisor.models import AgentResult, AgentState


class PlannerAgent:
    name = "planner_agent"

    def plan(self, state: AgentState) -> AgentResult:
        query = state.query.lower()
        route = ["spending_analysis_agent"]

        wants_alerts = any(token in query for token in ["alert", "risk", "warn", "overspend", "unusual"])
        wants_recommendations = any(
            token in query for token in ["recommend", "advice", "improve", "save", "suggest", "what should"]
        )
        wants_full_review = any(token in query for token in ["full", "health", "financial"])

        if wants_recommendations or wants_full_review or not wants_alerts:
            route.append("recommendation_agent")
        if wants_alerts or wants_full_review:
            route.append("alert_agent")

        state.route = route
        return AgentResult(
            agent_name=self.name,
            summary=f"Planner selected route: {' -> '.join(route)}.",
            data={"route": route},
            reasoning_trace=[
                "Interpreted user intent from keywords.",
                "Spending analysis is the base agent because other agents depend on its insights.",
                "Selected downstream agents based on whether the query asks for advice, alerts, or full health.",
            ],
        )

    def synthesize(self, state: AgentState) -> str:
        spending = state.results.get("spending_analysis_agent")
        recommendation = state.results.get("recommendation_agent")
        alert = state.results.get("alert_agent")

        lines: list[str] = []
        if spending:
            data = spending.data
            lines.append(f"Financial health for {data['month']}")
            lines.append(
                f"- Income: ${data['income']:.2f}; spend: ${data['total_spend']:.2f}; "
                f"net cash flow: ${data['net_cash_flow']:.2f}; savings rate: {data['savings_rate']}%."
            )
            top_categories = ", ".join(
                f"{item['category']} ${item['amount']:.2f}" for item in data.get("top_categories", [])[:3]
            )
            lines.append(f"- Top spending areas: {top_categories}.")
            if data.get("increased_categories"):
                biggest = data["increased_categories"][0]
                lines.append(
                    f"- Biggest trend: {biggest['category']} is up {biggest['percent_change']}% "
                    f"against baseline."
                )

        if alert:
            alerts = alert.data.get("alerts", [])
            if alerts:
                lines.append("Proactive alerts")
                for item in alerts[:4]:
                    lines.append(f"- [{item['severity']}] {item['message']}")
            else:
                lines.append("Proactive alerts: no major threshold breaches found.")

        if recommendation:
            lines.append("Recommendations")
            for item in recommendation.data.get("recommendations", [])[:4]:
                lines.append(f"- {item}")

        return "\n".join(lines)
