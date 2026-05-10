from pydantic import BaseModel
from typing import List, Optional, Dict, Any


# ======================================================
# VARIABLE REPORT
# ======================================================
class VariableReport(BaseModel):
    name: str
    score: int
    reason: str
    line: int
    category: str
    suggestions: List[str]


# ======================================================
# ISSUE REPORT
# ======================================================
class IssueReport(BaseModel):
    type: str
    severity: str
    detail: str


# ======================================================
# FUNCTION METRICS
# ======================================================
class FunctionMetrics(BaseModel):
    length: int
    args: int
    has_defaults: bool
    is_async: bool
    has_docstring: bool
    line_start: int
    line_end: int


# ======================================================
# FUNCTION ANALYSIS
# ======================================================
class FunctionAnalysis(BaseModel):
    name: str

    metrics: FunctionMetrics

    complexity: int
    nesting: int
    return_count: int
    comment_density: float

    variables: List[VariableReport]
    unused: List[str]

    issues: List[IssueReport]

    score: int

    ai_review: str
    insight: str

    engine_version: str


# ======================================================
# MODULE SUMMARY
# ======================================================
class ModuleSummary(BaseModel):
    total_functions: int
    total_classes: int
    average_score: float
    total_issues: int

    severity_counts: Dict[str, int]

    undocumented: int
    async_functions: int


# ======================================================
# FINAL RESPONSE
# ======================================================
class AnalysisResponse(BaseModel):
    status: str

    summary: ModuleSummary

    analysis: List[FunctionAnalysis]

    worst_functions: List[FunctionAnalysis]

    problematic_functions: List[FunctionAnalysis]

    critical_functions: List[FunctionAnalysis]

    undocumented_functions: List[FunctionAnalysis]