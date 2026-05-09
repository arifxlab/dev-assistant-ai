# 🔍 Code Analyzer API

A Python-based **static code analysis engine** that evaluates function quality using structural metrics, variable intelligence, severity-based scoring, and AI-powered insights.

---

## 🚀 Features

### 📊 Code Metrics

- Function length  
- Number of arguments  
- Cyclomatic complexity  
- Nesting depth  
- Return count  
- Async function detection  
- Comment density analysis  

---

### 🧠 Smart Variable Analysis (Advanced v2.0)

- Variable quality scoring (0–10)
- Context-aware evaluation:
  - Loop variables (`i`, `j`, etc.)
  - Parameters vs local variables
  - Accumulators detection
  - Function-size awareness
- Categorization system:
  - `param`
  - `loop`
  - `accumulator`
  - `local`
- Suggestion engine for better naming

Example:

```json
{
  "variables": [
    {
      "name": "temp",
      "score": 6,
      "reason": "'temp' (local variable) is unclear — consider a more descriptive name",
      "category": "local",
      "suggestions": [
        "Replace 'temp' with a meaningful name like 'intermediate_result'"
      ]
    }
  ]
}
🧹 Unused Variable Detection
Detects assigned but unused variables
Ignores:
Function parameters
Built-in Python names
⚠️ Issue Detection (Severity-Based System)

Severity levels:

Low
Medium
High
Critical

Detects:

Too long functions
Too many arguments
Deep nesting
High complexity
Missing docstrings
Unused variables
Poor variable naming
Excessive return statements
📊 Severity-Weighted Scoring

Each issue reduces score based on severity:

Critical → -2.5
High → -1.5
Medium → -1.0
Low → -0.5

Final function score: 0–10

🤖 AI Code Review
Human-like function explanation
Suggestions for improvement
Structural + complexity awareness
⚡ Performance Optimizations
Hash-based caching system
Lazy AI initialization
Optimized AST traversal
Reduced redundant computation
📡 API Usage
Endpoint
POST /analyze
Request Body
{
  "code": "def example(a, b): return a + b"
}
Response
{
  "functions": [
    {
      "name": "example",
      "metrics": {
        "length": 1,
        "args": 2,
        "is_async": false,
        "has_docstring": false
      },
      "complexity": 1,
      "nesting": 0,
      "return_count": 1,
      "comment_density": 0.0,
      "variables": [],
      "unused": [],
      "issues": [
        {
          "type": "No docstring",
          "severity": "Low"
        }
      ],
      "score": 9,
      "ai_review": "Clean and simple function",
      "insight": "Clean structure",
      "engine_version": "2.0.0"
    }
  ]
}
🛠️ Installation
git clone <your-repo>
cd <your-project>
pip install -r requirements.txt
▶️ Run Server
uvicorn app.api.main:app --reload

Open:

http://127.0.0.1:8000/docs
🧪 Example Tests
Weak Code
def messy(a, b):
    temp = 0
    x = 5
    return temp
Clean Code
def calculate_total(price, tax_rate):
    return price + (price * tax_rate)
🧱 Architecture
app/
 ├── analyzer/
 │   ├── code_analyzer.py
 │   ├── complexity_analyzer.py
 │   └── variable_analyzer.py
 │
 ├── ai/
 │   └── ai_engine.py
 │
 ├── api/
 │   └── main.py
 │
 ├── core/
 │   └── config.py
 │
 └── main.py
🎯 Roadmap
 Variable intelligence system
 Severity-based scoring engine
 AI-powered review system
 Caching + optimization layer
 GitHub integration
 Refactoring suggestion engine
 Code smell detection
 Web dashboard UI
🧠 Philosophy

This project focuses on:

Code understanding, not just rules
Context-aware quality scoring
Actionable engineering feedback
AI-assisted code reasoning
👨‍💻 Author

Built as an advanced engineering learning project focused on:

Static analysis + AI-assisted code review + software architecture design


---

## ⚠️ Important Fix (why yours looked “basic”)

Your issue was:
- missing proper Markdown blocks
- no consistent headers (`##`, `###`)
- no fenced code blocks (```)

Now this version will render like:
- GitHub README
- PyCharm Markdown preview
- professional open-source project

---

If you want next upgrade, I can help you turn this into:

🔥 GitHub-ready SaaS landing README (with badges + screenshots section + API docs UI style)
put everything in this coding box all read me file stuff cmon whats wrong with you 

Got it — you want the entire README inside one single code block, clean and ready to paste. No splitting, no extra explanation.

Here it is:

# 🔍 Code Analyzer API

A Python-based **static code analysis engine** that evaluates function quality using structural metrics, variable intelligence, severity-based scoring, and AI-powered insights.

---

## 🚀 Features

### 📊 Code Metrics

- Function length  
- Number of arguments  
- Cyclomatic complexity  
- Nesting depth  
- Return count  
- Async function detection  
- Comment density analysis  

---

### 🧠 Smart Variable Analysis (Advanced v2.0)

- Variable quality scoring (0–10)
- Context-aware evaluation:
  - Loop variables (`i`, `j`, etc.)
  - Parameters vs local variables
  - Accumulators detection
  - Function-size awareness
- Categorization system:
  - `param`
  - `loop`
  - `accumulator`
  - `local`
- Suggestion engine for better naming

Example:

```json
{
  "variables": [
    {
      "name": "temp",
      "score": 6,
      "reason": "'temp' (local variable) is unclear — consider a more descriptive name",
      "category": "local",
      "suggestions": [
        "Replace 'temp' with a meaningful name like 'intermediate_result'"
      ]
    }
  ]
}
🧹 Unused Variable Detection
Detects assigned but unused variables
Ignores:
Function parameters
Built-in Python names
⚠️ Issue Detection (Severity-Based System)

Severity levels:

Low
Medium
High
Critical

Detects:

Too long functions
Too many arguments
Deep nesting
High complexity
Missing docstrings
Unused variables
Poor variable naming
Excessive return statements
📊 Severity-Weighted Scoring

Each issue reduces score based on severity:

Critical → -2.5
High → -1.5
Medium → -1.0
Low → -0.5

Final function score: 0–10

🤖 AI Code Review
Human-like function explanation
Suggestions for improvement
Structural + complexity awareness
⚡ Performance Optimizations
Hash-based caching system
Lazy AI initialization
Optimized AST traversal
Reduced redundant computation
📡 API Usage
Endpoint
POST /analyze
Request Body
{
  "code": "def example(a, b): return a + b"
}
Response
{
  "functions": [
    {
      "name": "example",
      "metrics": {
        "length": 1,
        "args": 2,
        "is_async": false,
        "has_docstring": false
      },
      "complexity": 1,
      "nesting": 0,
      "return_count": 1,
      "comment_density": 0.0,
      "variables": [],
      "unused": [],
      "issues": [
        {
          "type": "No docstring",
          "severity": "Low"
        }
      ],
      "score": 9,
      "ai_review": "Clean and simple function",
      "insight": "Clean structure",
      "engine_version": "2.0.0"
    }
  ]
}
🛠️ Installation
git clone <your-repo>
cd <your-project>
pip install -r requirements.txt
▶️ Run Server
uvicorn app.api.main:app --reload

Open:

http://127.0.0.1:8000/docs
🧪 Example Tests
Weak Code
def messy(a, b):
    temp = 0
    x = 5
    return temp
Clean Code
def calculate_total(price, tax_rate):
    return price + (price * tax_rate)
🧱 Architecture
app/
 ├── analyzer/
 │   ├── code_analyzer.py
 │   ├── complexity_analyzer.py
 │   └── variable_analyzer.py
 │
 ├── ai/
 │   └── ai_engine.py
 │
 ├── api/
 │   └── main.py
 │
 ├── core/
 │   └── config.py
 │
 └── main.py
🎯 Roadmap
 Variable intelligence system
 Severity-based scoring engine
 AI-powered review system
 Caching + optimization layer
 GitHub integration
 Refactoring suggestion engine
 Code smell detection
 Web dashboard UI
🧠 Philosophy

This project focuses on:

Code understanding, not just rules
Context-aware quality scoring
Actionable engineering feedback
AI-assisted code reasoning
👨‍💻 Author

Built as an advanced engineering learning project focused on:

Static analysis + AI-assisted code review + software architecture design
