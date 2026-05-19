# Demo Guide: Personal Finance Advisor Agent

## What This Project Does

This project simulates a personal finance advisor that goes beyond generic transaction notifications. It analyzes mock customer transactions, identifies spending behavior, generates recommendations, and creates proactive alerts.

## Frameworks Used

- **Python** for core implementation.
- **LangGraph** for multi-agent orchestration.
- **LangChain** for connecting to the LLM.
- **Groq API** as the LLM provider.

The system still keeps financial calculations in deterministic Python tools. This is important because an LLM should explain financial insights, but it should not guess transaction totals.

## Architecture Pattern

The architecture follows a planner-orchestrated multi-agent graph pattern:

```text
User Query
  -> Planner Agent
  -> LangGraph StateGraph
  -> Spending Analysis Agent
  -> Recommendation Agent / Alert Agent
  -> Planner Final Synthesis
  -> Customer Response
```

## Why This Pattern Was Chosen

I chose this pattern because a financial advisor system needs both intelligence and accuracy.

- LangGraph gives clear control over agent execution flow.
- LangChain makes the LLM provider replaceable.
- Groq API helps with natural-language planning, recommendations, and final response wording.
- Python tools keep transaction calculations auditable and reliable.
- Shared memory allows personalization across customer interactions.

## Agent Responsibilities

### Planner Agent

The planner understands the user query and decides which agents should run. With `GROQ_API_KEY` configured, Groq API helps decide the route. Without the key, the system uses a local fallback for demo safety.

Example:

```text
"show alerts" -> spending_analysis_agent -> alert_agent
"how can I save more" -> spending_analysis_agent -> recommendation_agent
"full financial health review" -> spending_analysis_agent -> recommendation_agent -> alert_agent
```

### Spending Analysis Agent

This is the deeply implemented agent. It uses tool functions to:

- Load customer transactions.
- Filter by month.
- Calculate monthly income and spending.
- Categorize expenses.
- Compare spending against previous-month baselines.
- Detect unusual transactions.
- Generate structured insights.

This agent is deterministic and explainable.

### Recommendation Agent

This agent receives structured insights from the spending agent. If Groq API is configured, it asks the model to produce concise personalized recommendations using only the calculated facts. Otherwise, it uses a rule-based fallback.

### Alert Agent

This agent checks:

- Spending threshold breaches.
- Overspending behavior.
- Unusual transactions.
- Category increases versus baseline.

## Memory Handling

The system uses `.advisor_memory.json` for basic local memory:

- Customer preferences.
- Recent runs.
- Latest spending insights.

## Commands

Install dependencies:

```powershell
pip install -r requirements.txt
```

Set Groq API key:

```powershell
$env:GROQ_API_KEY="your_groq_api_key"
```

Check Groq setup:

```powershell
python check_groq.py
```

Run the main demo:

```powershell
.\run_demo.ps1
```

If PowerShell script execution is blocked:

```powershell
.\run_demo.bat
```

Run chat mode:

```powershell
.\run_chat.ps1
```

Run a custom query:

```powershell
python main.py "show unusual spending and alerts" --month 2026-04 --trace
```

## What To Show In The Demo

Use `--trace` output to prove:

- Planner selected a route.
- LangGraph executed the flow.
- Spending agent called tools.
- Recommendation and alert agents consumed spending insights.
- Runtime is LangGraph.
- LLM provider is either `groq_via_langchain` or `rule_based_fallback`.

Expected live Groq API trace:

```text
Runtime: LangGraph
LLM provider: groq_via_langchain
```

Expected no-key fallback trace:

```text
Runtime: LangGraph
LLM provider: rule_based_fallback
```

## Scaling Plan

To scale this into a real system:

- Replace CSV with a banking transaction database.
- Use authenticated customer profiles.
- Add streaming event alerts.
- Add a UI with Streamlit, FastAPI, or React.
- Store memory in Redis/Postgres/vector database.
- Add more agents: budget agent, debt agent, investment agent, fraud-risk agent.
- Add evaluation tests for financial insight quality.
- Add human approval for sensitive financial actions.

## Demo Summary Line

This is a LangGraph-orchestrated personal finance advisor using LangChain and Groq API for intelligent planning and response generation, while deterministic Python tools perform the financial calculations for accuracy and explainability.
