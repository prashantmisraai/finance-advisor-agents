from __future__ import annotations

import json

from finance_advisor.llm import LLMClient, RuleBasedLLM
from finance_advisor.models import AgentResult, AgentState


class PlannerAgent:
    name = "planner_agent"

    def __init__(self, llm: LLMClient | None = None) -> None:
        self.llm = llm or RuleBasedLLM()

    def plan(self, state: AgentState) -> AgentResult:
        route = self._llm_route(state.query) or self._keyword_route(state.query)
        state.route = route
        return AgentResult(
            agent_name=self.name,
            summary=f"Planner selected route: {' -> '.join(route)}.",
            data={"route": route, "planner_provider": self.llm.provider_name},
            reasoning_trace=[
                "Interpreted user intent.",
                "Spending analysis is the base agent because other agents depend on its insights.",
                "Selected downstream agents based on whether the query asks for advice, alerts, or full health.",
            ],
        )

    def _keyword_route(self, query_text: str) -> list[str]:
        query = query_text.lower()
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

        return route

    def _llm_route(self, query: str) -> list[str] | None:
        if self.llm.provider_name == "rule_based_fallback":
            return None

        system_prompt = (
            "You are the planner agent for a personal finance advisor. "
            "Return only JSON with an `agents` array. Valid agents are "
            "spending_analysis_agent, recommendation_agent, alert_agent. "
            "Always include spending_analysis_agent first. Include recommendation_agent for advice, "
            "improvement, savings, or full financial health. Include alert_agent for risk, warning, "
            "threshold, unusual spend, overspending, or full financial health."
        )
        user_prompt = f"Customer query: {query}"
        response = self.llm.generate(system_prompt, user_prompt)
        try:
            parsed = json.loads(response)
            agents = parsed.get("agents", [])
            valid = {"spending_analysis_agent", "recommendation_agent", "alert_agent"}
            route = [agent for agent in agents if agent in valid]
            if route and route[0] == "spending_analysis_agent":
                return route
        except json.JSONDecodeError:
            return None
        return None

    def synthesize(self, state: AgentState) -> str:
        fallback = self._template_synthesis(state)
        if self.llm.provider_name == "rule_based_fallback":
            return fallback

        system_prompt = (
            "You are the final financial advisor response agent. "
            "Use only the supplied structured facts. Do not invent transactions. "
            "Be concise, practical, and customer friendly."
        )
        user_prompt = json.dumps(
            {
                "customer_query": state.query,
                "route": state.route,
                "spending": state.results.get("spending_analysis_agent").data
                if state.results.get("spending_analysis_agent")
                else {},
                "recommendations": state.results.get("recommendation_agent").data
                if state.results.get("recommendation_agent")
                else {},
                "alerts": state.results.get("alert_agent").data if state.results.get("alert_agent") else {},
                "fallback_answer": fallback,
            },
            indent=2,
        )
        response = self.llm.generate(system_prompt, user_prompt)
        return response or fallback

    def _template_synthesis(self, state: AgentState) -> str:
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
