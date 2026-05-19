from __future__ import annotations

from pathlib import Path
from typing import Any, TypedDict

from finance_advisor.agents.alert import AlertAgent
from finance_advisor.agents.planner import PlannerAgent
from finance_advisor.agents.recommendation import RecommendationAgent
from finance_advisor.agents.spending_analysis import SpendingAnalysisAgent
from finance_advisor.config import load_config
from finance_advisor.llm import build_llm
from finance_advisor.memory import CustomerMemory
from finance_advisor.models import AgentResult, AgentState


class GraphRuntimeState(TypedDict, total=False):
    state: AgentState
    next_agent: str
    final_answer: str


class FinanceAdvisorOrchestrator:
    """LangGraph orchestration with planner-controlled routing."""

    def __init__(self, transactions_path: Path, memory_path: Path) -> None:
        self.config = load_config()
        self.llm = build_llm(self.config)
        self.memory = CustomerMemory(memory_path)
        self.planner = PlannerAgent(self.llm)
        self.agents = {
            "spending_analysis_agent": SpendingAnalysisAgent(transactions_path),
            "recommendation_agent": RecommendationAgent(self.llm),
            "alert_agent": AlertAgent(),
        }
        self.graph = self._build_langgraph()

    def run(self, customer_id: str, query: str, month: str | None = None, show_trace: bool = False) -> str:
        state = AgentState(
            customer_id=customer_id,
            query=query,
            month=month,
            memory=self.memory.get_customer(customer_id),
        )

        if self.graph:
            output = self.graph.invoke({"state": state})
            final_answer = output["final_answer"]
            state = output["state"]
        else:
            final_answer = self._run_without_langgraph(state)

        self.memory.remember_run(customer_id, query, state.route, final_answer)

        if show_trace:
            final_answer += "\n\nReasoning and orchestration trace"
            final_answer += self._format_trace(state.results)
            final_answer += f"\n\nRuntime: {'LangGraph' if self.graph else 'Python fallback'}"
            final_answer += f"\nLLM provider: {self.llm.provider_name}"
            if self.llm.last_error:
                final_answer += f"\nLLM status: unavailable - {self.llm.last_error}"

        return final_answer

    def _run_without_langgraph(self, state: AgentState) -> str:
        planner_result = self.planner.plan(state)
        state.results[planner_result.agent_name] = planner_result

        for agent_name in state.route:
            result = self.agents[agent_name].run(state)
            state.results[result.agent_name] = result
            if result.agent_name == "spending_analysis_agent":
                self.memory.remember_insights(state.customer_id, result.data)

        return self.planner.synthesize(state)

    def _build_langgraph(self) -> Any | None:
        try:
            from langgraph.graph import END, StateGraph
        except ImportError:
            return None

        graph = StateGraph(GraphRuntimeState)

        def planner_node(graph_state: GraphRuntimeState) -> GraphRuntimeState:
            state = graph_state["state"]
            result = self.planner.plan(state)
            state.results[result.agent_name] = result
            next_agent = state.route[0] if state.route else "synthesize"
            return {"state": state, "next_agent": next_agent}

        def spending_node(graph_state: GraphRuntimeState) -> GraphRuntimeState:
            state = graph_state["state"]
            result = self.agents["spending_analysis_agent"].run(state)
            state.results[result.agent_name] = result
            self.memory.remember_insights(state.customer_id, result.data)
            return {"state": state, "next_agent": self._next_after(state, "spending_analysis_agent")}

        def recommendation_node(graph_state: GraphRuntimeState) -> GraphRuntimeState:
            state = graph_state["state"]
            result = self.agents["recommendation_agent"].run(state)
            state.results[result.agent_name] = result
            return {"state": state, "next_agent": self._next_after(state, "recommendation_agent")}

        def alert_node(graph_state: GraphRuntimeState) -> GraphRuntimeState:
            state = graph_state["state"]
            result = self.agents["alert_agent"].run(state)
            state.results[result.agent_name] = result
            return {"state": state, "next_agent": self._next_after(state, "alert_agent")}

        def synthesize_node(graph_state: GraphRuntimeState) -> GraphRuntimeState:
            state = graph_state["state"]
            return {"state": state, "final_answer": self.planner.synthesize(state), "next_agent": "end"}

        graph.add_node("planner", planner_node)
        graph.add_node("spending_analysis_agent", spending_node)
        graph.add_node("recommendation_agent", recommendation_node)
        graph.add_node("alert_agent", alert_node)
        graph.add_node("synthesize", synthesize_node)

        graph.set_entry_point("planner")
        graph.add_conditional_edges("planner", self._route_from_runtime)
        graph.add_conditional_edges("spending_analysis_agent", self._route_from_runtime)
        graph.add_conditional_edges("recommendation_agent", self._route_from_runtime)
        graph.add_conditional_edges("alert_agent", self._route_from_runtime)
        graph.add_edge("synthesize", END)
        return graph.compile()

    def _route_from_runtime(self, graph_state: GraphRuntimeState) -> str:
        return graph_state.get("next_agent", "synthesize")

    def _next_after(self, state: AgentState, current_agent: str) -> str:
        current_index = state.route.index(current_agent)
        next_index = current_index + 1
        if next_index >= len(state.route):
            return "synthesize"
        return state.route[next_index]

    def _format_trace(self, results: dict[str, AgentResult]) -> str:
        lines: list[str] = []
        for result in results.values():
            lines.append(f"\n{result.agent_name}: {result.summary}")
            for step in result.reasoning_trace:
                lines.append(f"- reasoning: {step}")
            for call in result.tool_calls:
                lines.append(f"- tool: {call.name} input={call.input} output={call.output_summary}")
        return "\n".join(lines)
