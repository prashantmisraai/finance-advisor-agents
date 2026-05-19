from __future__ import annotations

from pathlib import Path

from finance_advisor.agents.alert import AlertAgent
from finance_advisor.agents.planner import PlannerAgent
from finance_advisor.agents.recommendation import RecommendationAgent
from finance_advisor.agents.spending_analysis import SpendingAnalysisAgent
from finance_advisor.memory import CustomerMemory
from finance_advisor.models import AgentResult, AgentState


class FinanceAdvisorOrchestrator:
    """Lightweight graph-style orchestration with planner-controlled routing."""

    def __init__(self, transactions_path: Path, memory_path: Path) -> None:
        self.memory = CustomerMemory(memory_path)
        self.planner = PlannerAgent()
        self.agents = {
            "spending_analysis_agent": SpendingAnalysisAgent(transactions_path),
            "recommendation_agent": RecommendationAgent(),
            "alert_agent": AlertAgent(),
        }

    def run(self, customer_id: str, query: str, month: str | None = None, show_trace: bool = False) -> str:
        state = AgentState(
            customer_id=customer_id,
            query=query,
            month=month,
            memory=self.memory.get_customer(customer_id),
        )

        planner_result = self.planner.plan(state)
        state.results[planner_result.agent_name] = planner_result

        for agent_name in state.route:
            result = self.agents[agent_name].run(state)
            state.results[result.agent_name] = result
            if result.agent_name == "spending_analysis_agent":
                self.memory.remember_insights(customer_id, result.data)

        final_answer = self.planner.synthesize(state)
        self.memory.remember_run(customer_id, query, state.route, final_answer)

        if show_trace:
            final_answer += "\n\nReasoning and orchestration trace"
            final_answer += self._format_trace(state.results)

        return final_answer

    def _format_trace(self, results: dict[str, AgentResult]) -> str:
        lines: list[str] = []
        for result in results.values():
            lines.append(f"\n{result.agent_name}: {result.summary}")
            for step in result.reasoning_trace:
                lines.append(f"- reasoning: {step}")
            for call in result.tool_calls:
                lines.append(f"- tool: {call.name} input={call.input} output={call.output_summary}")
        return "\n".join(lines)
