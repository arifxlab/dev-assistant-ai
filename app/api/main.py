from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.schemas.analysis_schema import AnalysisResponse
from app.analyzer.code_analyzer import CodeAnalyzer


# ======================================================
# REQUEST MODEL
# ======================================================
class CodeRequest(BaseModel):
    code: str


# ======================================================
# FASTAPI APP
# ======================================================
app = FastAPI(
    title="Dev Assistant AI",
    description="AI-powered Python static code analysis API",
    version="2.0.0"
)


# ======================================================
# ROOT
# ======================================================
@app.get("/")
def home():
    return {
        "message": "Dev Assistant AI API running",
        "version": "2.0.0",
        "status": "online"
    }


# ======================================================
# ANALYZE ENDPOINT
# ======================================================
@app.post("/analyze", response_model=AnalysisResponse)
def analyze(request: CodeRequest):

    analyzer = CodeAnalyzer()

    success = analyzer.load_code(request.code)

    # ----------------------------------------------
    # Syntax Error Handling
    # ----------------------------------------------
    if not success:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid Python syntax",
                "message": analyzer.parse_error
            }
        )

    # ----------------------------------------------
    # Analysis Response
    # ----------------------------------------------
    return {
        "status": "success",

        "summary": analyzer.module_stats(),

        "analysis": analyzer.full_analysis(),

        "worst_functions": analyzer.get_worst_functions(),

        "problematic_functions": analyzer.get_problematic_functions(),

        "critical_functions": analyzer.get_critical_functions(),

        "undocumented_functions": analyzer.get_undocumented_functions()
    }