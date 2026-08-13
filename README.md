# 🛡️ Enterprise LLM Evaluation & Observability Suite

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()

An end-to-end, enterprise-grade LLM evaluation engine and dashboard for automated benchmarking, side-by-side model comparison, prompt assertion testing, and bias audit (positional/length bias). Built to evaluate system prompt adherence, factual correctness, and safety criteria for LLM workflows.

---

## 📐 System Architecture

```text
                               +-----------------------------+
                               |     FastAPI Dashboard UI    |
                               | (Interactive Web Framework) |
                               +--------------+--------------+
                                              |
                                              v
                              +---------------+---------------+
                              |    Execution Orchestrator     |
                              |      (run_evaluation.py)      |
                              +---------------+---------------+
                                              |
                     +------------------------+------------------------+
                     |                                                 |
                     v                                                 v
      +--------------+--------------+                   +--------------+--------------+
      |  Single Model Evaluator     |                   |    Pairwise Comparison      |
      |  (src/judge.py & evaluator) |                   |  (src/pairwise_judge.py)    |
      +--------------+--------------+                   +--------------+--------------+
                     |                                                 |
                     +------------------------+------------------------+
                                              |
                                              v
                              +---------------+---------------+
                              |   Structured Parser & Logger  |
                              | (parser.py / judge_logs.jsonl)|
                              +---------------+---------------+
                                              |
                                              v
                              +---------------+---------------+
                              |   Metrics & Report Generator  |
                              |     (reports/report.json)     |
                              +-------------------------------+

```

---

## 📂 Repository Layout

```text
PROBLEM 2/
├── data/
│   ├── test_suite.json           # Primary evaluation dataset (golden queries & baselines)
│   └── ab_test_suite.json        # A/B candidate dataset for side-by-side evaluation
├── logs/
│   └── judge_logs.jsonl          # Production JSONL execution & runtime evaluation logs
├── prompts/
│   ├── judge_prompt.txt          # System prompt template for single model grading
│   └── pairwise_prompt.txt       # System prompt template for pairwise model selection
├── reports/
│   └── report.json               # Compiled evaluation metrics, pass/fail rates, & scores
├── src/
│   ├── __init__.py               # Package initializer
│   ├── bias.py                   # Statistical engine for position & verbosity bias detection
│   ├── compare.py                # Model comparison matrix aggregator
│   ├── evaluator.py              # Core evaluation engine
│   ├── judge.py                  # Single-response evaluator logic
│   ├── logger.py                 # Structured logging provider
│   ├── pairwise_judge.py         # Pairwise comparison LLM judge module
│   ├── parser.py                 # Structured output extraction & JSON sanitizer
│   └── validation.py             # Input dataset schema and response validation
├── .env                          # Local secrets, API credentials, and configs
├── .gitignore                    # Version control exclusion rules
├── app.py                        # FastAPI production web server and frontend UI
├── config.py                     # Environment and application parameters
├── README.md                     # Platform documentation
├── requirements.txt              # Project dependencies
├── run_analysis.py               # Statistical evaluation & bias analyzer runner
├── run_comparison.py             # Multi-model comparative assessment CLI
├── run_evaluation.py             # Single-model evaluation pipeline runner
├── run_pairwise.py               # Pairwise evaluation test runner
└── test_api.py                   # API connectivity and integration test harness

```

---

## ✨ Key Platform Capabilities

* **Quantitative LLM Grading:** Evaluates outputs against defined metrics:
* **Factual Correctness:** Accuracy against baseline standard responses.
* **Context Faithfulness:** Hallucination detection and relevance checking.
* **Instruction Adherence:** Formatting, output structural compliance, and system prompt constraints.
* **Completeness & Tone:** Coverage of required key points and professional communication register.


* **Pairwise Blind Evaluation:** Eliminates positional preference by conducting randomized head-to-head model output evaluations.
* **Bias Auditing:** Built-in analyzer (`src/bias.py`) to measure model preference toward longer context (verbosity bias) or first-presented answers (position bias).
* **Automated Reporting:** Generates structured structured execution logs (`logs/judge_logs.jsonl`) and summary reports (`reports/report.json`).

---

## ⚡ Quick Start

### 1. Prerequisites

* Python 3.10 or higher
* Valid API Provider Key (e.g., Groq, OpenAI, or Gemini)

### 2. Virtual Environment Setup

```bash
# Clone the repository and navigate to root directory
cd "Problem 2"

# Create virtual environment
python -m venv Assign2env

# Activate virtual environment
# On Windows (PowerShell/CMD):
Assign2env\Scripts\activate
# On macOS/Linux:
source Assign2env/bin/activate

# Install required dependencies
pip install -r requirements.txt

```

### 3. Environment Configuration

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=your_groq_api_key_here
JUDGE_MODEL=llama-3.3-70b-versatile
GENERATOR_MODEL=llama-3.1-8b-instant
TEMPERATURE=0.0
MAX_OUTPUT_TOKENS=1024

```

---

## 🖥️ Platform Usage

### 1. Web Dashboard (FastAPI Interface)

Launch the production web server to monitor evaluation, add test cases, and trigger runs visually:

```bash
python app.py

```

Open browser at: `http://127.0.0.1:8000`

---

### 2. Command Line Interfaces (CLI)

#### Standard Single Model Evaluation Pipeline

Executes test cases in `data/test_suite.json`, grades output, and generates `reports/report.json`:

```bash
python run_evaluation.py

```

#### Pairwise Model Comparison

Runs head-to-head tournament evaluation between two LLM candidates:

```bash
python run_pairwise.py

```

#### Multi-Model Matrix Analysis

```bash
python run_comparison.py

```

#### Bias Audit & Statistical Analytics

Detects length bias and position bias across previous execution logs:

```bash
python run_analysis.py

```

#### Integration & API Diagnostics

Verifies provider credentials and model latency:

```bash
python test_api.py

```

---

## 📊 Logging & Diagnostics

* **Detailed Evaluation Logs:** Written line-by-line to `logs/judge_logs.jsonl` for real-time streaming and auditability.
* **Aggregated Reports:** Serialized to `reports/report.json` containing pass/fail ratios, average metric scores, and latency stats.

```

```
