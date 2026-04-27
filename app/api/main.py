from fastapi import FastAPI
from pydantic import BaseModel
from app.analyzer.code_analyzer import CodeAnalyzer
import ast

class CodeRequest(BaseModel):
    code: str


app = FastAPI()


@app.get("/")
def home():
    return {"message": "Dev Assistant AI API running"}


@app.post("/analyze")
def analyze(request: CodeRequest):

    analyzer = CodeAnalyzer("")
    analyzer.load_code(request.code)

    return {
        "analysis": analyzer.full_analysis(),
        "worst": analyzer.get_worst_functions(),
        "problematic": analyzer.get_problematic_functions(),
        "critical": analyzer.get_critical_functions()
    }