from fastapi import FastAPI
from app.analyzer.code_analyzer import CodeAnalyzer
import os

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Dev Assistant AI API running"}

@app.post("/analyze")
def analyze():
    file_path = os.path.join("app", "main.py")

    analyzer = CodeAnalyzer(file_path)
    analyzer.load_file()

    return {
        "analysis": analyzer.full_analysis(),
        "worst": analyzer.get_worst_functions(),
        "problematic": analyzer.get_problematic_functions(),
        "critical": analyzer.get_critical_functions()
    }