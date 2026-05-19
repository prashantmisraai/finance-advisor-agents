from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any


@dataclass(frozen=True)
class Transaction:
    transaction_id: str
    customer_id: str
    date: date
    merchant: str
    category: str
    amount: float
    type: str


@dataclass
class ToolCall:
    name: str
    input: dict[str, Any]
    output_summary: str


@dataclass
class AgentResult:
    agent_name: str
    summary: str
    data: dict[str, Any] = field(default_factory=dict)
    reasoning_trace: list[str] = field(default_factory=list)
    tool_calls: list[ToolCall] = field(default_factory=list)


@dataclass
class AgentState:
    customer_id: str
    query: str
    month: str | None
    route: list[str] = field(default_factory=list)
    results: dict[str, AgentResult] = field(default_factory=dict)
    memory: dict[str, Any] = field(default_factory=dict)
