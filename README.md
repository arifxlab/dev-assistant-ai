# 🔍 Code Analyzer API

A Python-based static code analysis tool that evaluates function quality using structural metrics, variable intelligence, and AI-powered insights.

---

## 🚀 Features

### 📊 Code Metrics

* Function length
* Number of arguments
* Cyclomatic complexity
* Nesting depth

### 🧠 Smart Variable Analysis (NEW)

* Variable quality scoring (0–10)
* Context-aware evaluation:

  * Loop variables handled correctly (`i`, `j`, etc.)
  * Parameter strictness
  * Function size awareness
* Meaningful feedback instead of simple “bad/good”

Example:

```json
"variables": {
  "quality": [
    {
      "name": "temp",
      "score": 6,
      "reason": "Weak naming, consider improving"
    }
  ],
  "unused": ["x"],
  "count": 5
}
```

### 🧹 Unused Variable Detection

* Detects assigned but never used variables
* Ignores:

  * Function parameters
  * Built-in names

### ⚠️ Issue Detection

* Too long functions
* Too many arguments
* Deep nesting
* High complexity
* Unused variables
* Weak variable naming

### 🤖 AI Code Review

* Human-like feedback
* Suggestions for improvement
* Design-level insights

---

## 📡 API Usage

### Endpoint

```
POST /analyze
```

### Request Body

```json
{
  "code": "def example(a, b): return a + b"
}
```

### Response

```json
{
  "analysis": [...],
  "worst": [...],
  "problematic": [...],
  "critical": [...]
}
```

---

## 🛠️ Installation

```bash
git clone <your-repo>
cd <your-project>
pip install -r requirements.txt
```

---

## ▶️ Run Server

```bash
uvicorn app.main:app --reload
```

Open:

```
http://127.0.0.1:8000/docs
```

---

## 🧪 Example Tests

### 1. Weak variables

```python
def messy(a, b, c):
    temp = 0
    x = 5
    return temp
```

### 2. Clean function

```python
def calculate_total(price, tax_rate):
    return price + (price * tax_rate)
```

---

## 🧱 Architecture

```
app/
 ├── analyzer/
 │   ├── complexity_analyzer.py
 │   ├── code_analyzer.py
 │   └── variable_analyzer.py
 ├── ai/
 │   └── ai_engine.py
 └── main.py
```

---

## 🎯 Roadmap

* [ ] Variable role detection (accumulator, flag, constant)
* [ ] Better naming suggestions (AI-assisted)
* [ ] Code smell detection (duplicate logic, dead code)
* [ ] Visualization dashboard

---

## 🧠 Philosophy

This project moves beyond simple linting by:

* Understanding **context**
* Scoring **code quality**
* Providing **actionable insights**

---

## 👨‍💻 Author

Built as a learning + advanced engineering project to explore static analysis and AI-assisted code review.
