from __future__ import annotations

import argparse
from pathlib import Path

from finance_advisor.orchestrator import FinanceAdvisorOrchestrator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Personal Finance Advisor Agent")
    parser.add_argument(
        "query",
        nargs="?",
        default="Give me a full financial health review with alerts and recommendations.",
        help="Customer question or task for the planner agent.",
    )
    parser.add_argument("--customer", default="CUST001", help="Customer id from mock transaction data.")
    parser.add_argument("--month", default=None, help="Month to analyze in YYYY-MM format. Defaults to latest month.")
    parser.add_argument("--trace", action="store_true", help="Show reasoning flow, route, and tool calls.")
    parser.add_argument("--chat", action="store_true", help="Start a simple conversational CLI loop.")
    parser.add_argument(
        "--data",
        default=str(Path("data") / "mock_transactions.csv"),
        help="Path to mock transactions CSV.",
    )
    parser.add_argument(
        "--memory",
        default=".advisor_memory.json",
        help="Path to local JSON memory file.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    orchestrator = FinanceAdvisorOrchestrator(
        transactions_path=Path(args.data),
        memory_path=Path(args.memory),
    )

    if args.chat:
        print("Personal Finance Advisor Agent. Type 'exit' to stop.")
        while True:
            query = input("\nYou: ").strip()
            if query.lower() in {"exit", "quit"}:
                break
            if not query:
                continue
            answer = orchestrator.run(args.customer, query, month=args.month, show_trace=args.trace)
            print(f"\nAdvisor:\n{answer}")
        return

    print(orchestrator.run(args.customer, args.query, month=args.month, show_trace=args.trace))
