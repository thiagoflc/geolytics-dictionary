"""AgentState definition for the Geolytics LangGraph reference agent."""

from __future__ import annotations

from typing import Any, Optional
from typing_extensions import TypedDict


class Violation(TypedDict):
    """A single semantic validation violation."""

    rule: str
    evidence: str
    suggested_fix: str


class ValidationResult(TypedDict):
    """Result of the SemanticValidator node."""

    valid: bool
    violations: list[Violation]


class AgentState(TypedDict, total=False):
    """Shared mutable state threaded through all DAG nodes."""

    # Input
    question: str

    # Router output
    classification: str  # "lookup" | "multi_hop" | "validation"

    # Decomposer output (used for multi_hop)
    decomposed: list[str]

    # GraphQuery output
    graph_results: list[dict[str, Any]]

    # RAGRetrieve output
    rag_results: list[dict[str, Any]]

    # Synthesizer draft answer (pre-validation)
    draft: str

    # SemanticValidator output
    validation: ValidationResult

    # Counts how many validator -> synthesizer correction loops have run
    iteration: int

    # Final output
    final_answer: str
