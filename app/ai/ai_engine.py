import requests

class AIEngine:
    def __init__(self, model="mistral"):
        self.model = model
        self.url = "http://localhost:11434/api/generate"

    def generate_review(self, code_snippet: str):
        prompt = f"""
You are a senior software engineer.

Analyze the following Python function and explain:
- What is wrong
- Why it is bad
- How to improve it

Keep answer short and professional.

Code:
{code_snippet}
"""

        response = requests.post(
            self.url,
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
        )

        return response.json()["response"]