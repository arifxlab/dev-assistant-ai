from pydantic import BaseModel
from typing import List, Optional


# ======================================================
# VARIABLE SCHEMA
# ======================================================
class VariableSchema(BaseModel):
    name: str
    score: int
    reason: str
    line: int
    category: str
    suggestions: List[str]


# ======================================================
# ISSUE SCHEMA
# ======================================================
class IssueSchema(BaseModel):
    type: str
    severity: str
    detail: Optional[str] = None


# ======================================================
# METRICS SCHEMA
# ======================================================
class MetricsSchema(BaseModel):
    length: int
    args: int
    has_defaults: bool
    is_async: bool
    has_docstring: bool
    line_start: int
    line_end: int


# ======================================================
# FUNCTION ANALYSIS SCHEMA
# ======================================================
class FunctionAnalysisSchema(BaseModel):
    name: str

    metrics: MetricsSchema

    complexity: int
    nesting: int
    return_count: int
    comment_density: float

    variables: List[VariableSchema]
    unused: List[str]

    issues: List[IssueSchema]

    score: int

    ai_review: str
    insight: str

    engine_version: str


# ======================================================
# MODULE STATS SCHEMA
# ======================================================
class ModuleStatsSchema(BaseModel):
    total_functions: int
    total_classes: int
    average_score: float

    total_issues: int

    severity_counts: dict

    undocumented: int
    async_functions: int


# ======================================================
# FULL API RESPONSE
# ======================================================
class AnalysisResponseSchema(BaseModel):
    functions: List[FunctionAnalysisSchema]

    worst: List[FunctionAnalysisSchema]

    problematic: List[FunctionAnalysisSchema]

    critical: List[FunctionAnalysisSchema]

    stats: ModuleStatsSchema