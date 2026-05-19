# Demo Output

This sample run shows the personal finance advisor using:

- LangGraph for orchestration
- Groq API through LangChain for LLM reasoning and final response generation
- Deterministic Python tools for transaction calculations
- Multi-agent flow across planner, spending analysis, recommendation, and alert agents

Command:

```powershell
.\run_demo.ps1
```

Expected trace indicators:

```text
Runtime: LangGraph
LLM provider: groq_via_langchain
```

Sample output:

```text
Here's a full financial health review with alerts and recommendations for you:

Financial Overview:
- Income: $5200.00
- Total Spend: $4522.78
- Net Cash Flow: $677.22
- Savings Rate: 13.0%

Top Spending Areas:
1. Rent: $1450.00
2. Shopping: $1098.70
3. Travel: $620.00

Key Trends:
- Shopping is up 1075.7% against the baseline, with a $1005.25 increase.
- Groceries spending has increased by 100.1% versus the baseline, with a $278.20 higher spend.
- Dining spending is up 153.9% versus the baseline, with a $186.50 higher spend.
- Subscriptions spending has increased by 369.0% versus the baseline, with a $59.00 higher spend.
- Transport spending is up 63.2% versus the baseline, with a $40.20 higher spend.

Proactive Alerts:
- Medium severity: Shopping, Groceries, Dining, Subscriptions, and Transport spending are higher than baseline.
- High severity: Unusual transactions for Rent, Shopping, and Travel.

Recommendations:
1. Cap dining at $260 next month by moving 2-3 meals from delivery to planned groceries.
2. Use a 48-hour rule for non-essential shopping to reduce large discretionary purchases.
3. Reduce flexible spend by about $323 to hit the $1000 savings goal.

Please review these points to better understand your financial health and make informed decisions.

Reasoning and orchestration trace
planner_agent: Planner selected route: spending_analysis_agent -> recommendation_agent -> alert_agent.
- reasoning: Interpreted user intent.
- reasoning: Spending analysis is the base agent because other agents depend on its insights.
- reasoning: Selected downstream agents based on whether the query asks for advice, alerts, or full health.

spending_analysis_agent: For 2026-04, spend was $4522.78 against $5200.00 income, leaving $677.22. Top category: Rent ($1450.00). Unusual transactions flagged: 3.
- reasoning: Loaded customer transactions and limited analysis to the active customer.
- reasoning: Selected 2026-04 as the target month for spending analysis.
- reasoning: Calculated income, debit spend, and savings rate to understand cash-flow health.
- reasoning: Compared each category to historical baseline to catch behavior shifts.
- reasoning: Flagged individual large transactions for proactive alerting.
- tool: load_transactions input={'customer_id': 'CUST001', 'path': 'data\\mock_transactions.csv'} output=Loaded 45 transactions.
- tool: filter_month input={'month': '2026-04'} output=Selected 18 transactions for 2026-04.
- tool: monthly_totals input={'months': 'all'} output=Current spend $4522.78, income $5200.00.
- tool: category_spend input={'month': '2026-04'} output=Found 9 spending categories.
- tool: compare_to_baseline input={'month': '2026-04', 'categories': ['Rent', 'Shopping', 'Travel', 'Groceries', 'Dining', 'Utilities', 'Transport', 'Entertainment', 'Subscriptions']} output=Compared current category spend with prior-month averages.
- tool: find_unusual_transactions input={'month': '2026-04'} output=Flagged 3 unusual transactions.

recommendation_agent: Generated personalized recommendations from spending insights.
- reasoning: Mapped spend categories and savings gap to simple customer actions.

alert_agent: Generated 10 proactive alerts.
- reasoning: Checked threshold breaches, behavior shifts, and unusual transactions.

Runtime: LangGraph
LLM provider: groq_via_langchain
```

## What This Proves

The output demonstrates:

- **Multi-agent orchestration**: planner routes execution to specialized agents.
- **Agent coordination**: recommendation and alert agents use spending analysis output.
- **Autonomous reasoning flow**: planner decides execution order from the user query.
- **Tool/function calling**: spending agent calls transaction analysis tools.
- **Basic memory handling**: customer preferences and recent runs are stored locally.
- **Personal recommendations**: recommendations are based on calculated insights.
- **Conversational interaction**: the same flow can run in `--chat` mode.
