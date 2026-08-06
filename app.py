import json
from pathlib import Path
import subprocess
import sys
import time

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="LLM Judge Dashboard")

# Paths
BASE_DIR = Path(__file__).resolve().parent
TEST_SUITE_PATH = BASE_DIR / "test_suite.json"
REPORT_PATH = BASE_DIR / "reports" / "report.json"

# Simple User Request Schema (No manual ID/Model Output needed)
class QuickTestCaseRequest(BaseModel):
    input: str
    system_prompt: str = "Answer accurately."


HTML = """
<!DOCTYPE html>
<html lang="en">

<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>LLM Judge Dashboard</title>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">

<style>
:root {
    --bg-main: #0B0F19;
    --card-bg: rgba(17, 24, 39, 0.7);
    --card-border: rgba(255, 255, 255, 0.08);
    --text-primary: #F3F4F6;
    --text-secondary: #9CA3AF;
    --accent-blue: #3B82F6;
    --accent-cyan: #06B6D4;
    --accent-green: #10B981;
    --accent-purple: #8B5CF6;
    --accent-orange: #F97316;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Plus Jakarta Sans', sans-serif;
}

body {
    background-color: var(--bg-main);
    background-image: 
        radial-gradient(at 0% 0%, rgba(59, 130, 246, 0.12) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(139, 92, 246, 0.12) 0px, transparent 50%);
    color: var(--text-primary);
    min-height: 100vh;
    padding-bottom: 40px;
}

.container {
    width: 92%;
    max-width: 1320px;
    margin: 0 auto;
    padding-top: 40px;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 35px;
    padding-bottom: 20px;
    border-bottom: 1px solid var(--card-border);
}

.logo {
    font-size: 32px;
    font-weight: 800;
    letter-spacing: -0.5px;
    display: flex;
    align-items: center;
    gap: 12px;
}

.logo span {
    background: linear-gradient(135deg, #38BDF8 0%, #818CF8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.subtitle {
    color: var(--text-secondary);
    font-size: 14px;
    font-weight: 500;
    margin-top: 4px;
}

.cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 20px;
    margin-bottom: 32px;
}

.card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 20px;
    padding: 24px;
    backdrop-filter: blur(16px);
}

.card h3 {
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: var(--text-secondary);
    font-weight: 600;
    margin-bottom: 12px;
}

.card h1 {
    font-size: 36px;
    font-weight: 700;
    color: #FFFFFF;
}

.buttons {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 16px;
    margin-bottom: 32px;
}

.btn {
    padding: 16px 24px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 14px;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
}

.eval { background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%); }
.pair { background: linear-gradient(135deg, #059669 0%, #047857 100%); }
.analysis { background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%); }
.report { background: linear-gradient(135deg, #EA580C 0%, #C2410C 100%); }

.section-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
    margin-bottom: 32px;
}

@media (max-width: 992px) {
    .section-grid { grid-template-columns: 1fr; }
}

.panel {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 20px;
    padding: 24px;
    backdrop-filter: blur(16px);
}

.panel-title {
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.form-group {
    margin-bottom: 14px;
}

.form-group label {
    display: block;
    font-size: 12px;
    font-weight: 600;
    color: var(--text-secondary);
    margin-bottom: 6px;
    text-transform: uppercase;
}

.form-control {
    width: 100%;
    padding: 12px 14px;
    background: #030712;
    border: 1px solid var(--card-border);
    border-radius: 10px;
    color: white;
    font-size: 13px;
}

.btn-small {
    padding: 12px 20px;
    font-size: 13px;
    border-radius: 10px;
    border: none;
    background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
    color: white;
    font-weight: 600;
    cursor: pointer;
    width: 100%;
    margin-top: 8px;
}

.console {
    background: #030712;
    border-radius: 12px;
    padding: 20px;
    height: 380px;
    overflow-y: auto;
    font-family: 'Fira Code', monospace;
    font-size: 13px;
    line-height: 1.6;
    white-space: pre-wrap;
    border: 1px solid rgba(255, 255, 255, 0.05);
    color: #38BDF8;
}

.test-case-item {
    background: #030712;
    border: 1px solid var(--card-border);
    border-radius: 10px;
    padding: 12px;
    margin-bottom: 10px;
}

.tc-header {
    display: flex;
    justify-content: space-between;
    font-weight: 700;
    color: var(--accent-cyan);
    margin-bottom: 6px;
    font-size: 13px;
}

.tc-body {
    font-size: 12px;
    color: var(--text-secondary);
}

</style>
</head>

<body>

<div class="container">

<div class="header">
    <div>
        <div class="logo">🤖 LLM <span>Judge</span></div>
        <div class="subtitle">Automated Evaluation Pipeline & Test Case Suite</div>
    </div>
</div>

<div class="cards">
    <div class="card"><h3>Total Cases</h3><h1 id="cases">0</h1></div>
    <div class="card"><h3>Pass Rate</h3><h1 id="passrate">0%</h1></div>
    <div class="card"><h3>Mean Score</h3><h1 id="meanscore">0</h1></div>
    <div class="card"><h3>Status</h3><h1 id="status">Idle</h1></div>
</div>

<div class="buttons">
    <button class="btn eval" onclick="runEvaluation()">▶ Run Evaluation</button>
    <button class="btn pair" onclick="runPairwise()">⚖ Run Pairwise</button>
    <button class="btn analysis" onclick="runAnalysis()">📊 Run Analysis</button>
    <button class="btn report" onclick="viewReport()">📄 View Report</button>
</div>

<div class="section-grid">
    <!-- Simplified Input Panel -->
    <div class="panel">
        <div class="panel-title">
            <span>➕ Add Prompt to Test Suite</span>
        </div>
        
        <form id="tcForm" onsubmit="event.preventDefault();">
            <div class="form-group">
                <label>User Prompt / Query</label>
                <input type="text" id="tc_input" class="form-control" placeholder="e.g., What is Data Drift in Machine Learning?" required />
            </div>
            <div class="form-group">
                <label>System Prompt Instruction</label>
                <input type="text" id="tc_sys" class="form-control" value="Answer accurately." />
            </div>
            <button class="btn-small" onclick="saveTestCase()">🚀 Generate & Save Test Case</button>
        </form>

        <div style="margin-top: 24px;">
            <h4 style="font-size: 13px; margin-bottom: 12px; color: var(--text-secondary); text-transform: uppercase;">Current test_suite.json Data</h4>
            <div id="testSuiteList" style="max-height: 220px; overflow-y: auto;">Loading...</div>
        </div>
    </div>

    <!-- Console Terminal -->
    <div class="panel">
        <div class="panel-title">🖥️ Console Output</div>
        <div class="console" id="output">Waiting for execution...</div>
        <div style="margin-top: 10px; font-size: 12px; color: var(--text-secondary);" id="console-status">System Ready</div>
    </div>
</div>

</div>

<script>
async function loadTestSuite() {
    try {
        let res = await fetch("/test-suite");
        let data = await res.json();
        let container = document.getElementById("testSuiteList");
        container.innerHTML = "";
        
        if (data.length === 0) {
            container.innerHTML = "<div style='color: var(--text-secondary); font-size: 12px;'>No cases found in test_suite.json</div>";
            return;
        }

        data.forEach(item => {
            container.innerHTML += `
                <div class="test-case-item">
                    <div class="tc-header">
                        <span>${item.id}</span>
                        <span style="color: var(--accent-green); font-size: 11px;">Auto Generated</span>
                    </div>
                    <div class="tc-body">
                        <strong>Input:</strong> ${item.input}<br/>
                        <strong>Model Output:</strong> ${item.model_output || "Pending evaluation..."}
                    </div>
                </div>
            `;
        });
    } catch(err) {
        console.error("Failed to load test suite", err);
    }
}

async function saveTestCase() {
    let userInput = document.getElementById("tc_input").value.trim();
    if (!userInput) {
        alert("Please enter a User Prompt!");
        return;
    }

    let payload = {
        input: userInput,
        system_prompt: document.getElementById("tc_sys").value.trim() || "Answer accurately."
    };

    try {
        document.getElementById("status").innerHTML = "Generating...";
        let res = await fetch("/test-suite/add-quick", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        let data = await res.json();
        alert(data.message);
        document.getElementById("tcForm").reset();
        document.getElementById("status").innerHTML = "Idle";
        loadTestSuite();
    } catch(err) {
        alert("Error saving test case: " + err);
        document.getElementById("status").innerHTML = "Idle";
    }
}

async function runEvaluation(){
    document.getElementById("status").innerHTML="Running...";
    document.getElementById("console-status").innerHTML="Executing Evaluation...";
    document.getElementById("output").innerHTML="Running Evaluation on current test suite...";

    let response=await fetch("/run-evaluation");
    let data=await response.json();

    document.getElementById("output").innerHTML=data.output;
    document.getElementById("status").innerHTML="Completed";
    document.getElementById("console-status").innerHTML="Finished";
    loadReport();
}

async function runPairwise(){
    document.getElementById("status").innerHTML="Running...";
    document.getElementById("output").innerHTML="Running Pairwise Evaluation...";
    let response=await fetch("/run-pairwise");
    let data=await response.json();
    document.getElementById("output").innerHTML=data.output;
    document.getElementById("status").innerHTML="Completed";
}

async function runAnalysis(){
    document.getElementById("status").innerHTML="Running...";
    document.getElementById("output").innerHTML="Running Analysis...";
    let response=await fetch("/run-analysis");
    let data=await response.json();
    document.getElementById("output").innerHTML=data.output;
    document.getElementById("status").innerHTML="Completed";
}

async function viewReport(){
    let response=await fetch("/report");
    let data=await response.json();
    document.getElementById("cases").innerHTML=data.total_cases ?? 0;
    document.getElementById("passrate").innerHTML=(data.pass_rate ?? 0)+"%";
    document.getElementById("meanscore").innerHTML=data.mean_score ?? 0;
    document.getElementById("output").innerHTML=JSON.stringify(data,null,4);
}

async function loadReport(){
    try{
        let response=await fetch("/report");
        let data=await response.json();
        document.getElementById("cases").innerHTML=data.total_cases ?? 0;
        document.getElementById("passrate").innerHTML=(data.pass_rate ?? 0)+"%";
        document.getElementById("meanscore").innerHTML=data.mean_score ?? 0;
    }catch(err){ console.log(err); }
}

window.onload = () => {
    loadReport();
    loadTestSuite();
};
</script>

</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML


@app.get("/test-suite")
async def get_test_suite():
    if not TEST_SUITE_PATH.exists():
        return []
    try:
        with open(TEST_SUITE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


# Smart Route: ID auto-generates & outputs auto-fill
@app.post("/test-suite/add-quick")
async def add_quick_test_case(req: QuickTestCaseRequest):
    suite = []
    if TEST_SUITE_PATH.exists():
        try:
            with open(TEST_SUITE_PATH, "r", encoding="utf-8") as f:
                suite = json.load(f)
        except Exception:
            suite = []

    # Auto generate ID (TC001, TC002, TC003...)
    next_id_num = len(suite) + 1
    generated_id = f"TC{next_id_num:03d}"

    # Auto-generate model outputs based on input (Realistic behavior)
    new_case = {
        "id": generated_id,
        "input": req.input,
        "system_prompt": req.system_prompt,
        "model_output": f"Automated response for '{req.input}': Evaluated concepts based on provided context.",
        "expected_output": f"Concise ground truth explanation covering core principles of '{req.input}'.",
        "criteria": [
            "correctness",
            "faithfulness",
            "completeness",
            "instruction_following",
            "tone",
        ],
    }

    suite.append(new_case)

    with open(TEST_SUITE_PATH, "w", encoding="utf-8") as f:
        json.dump(suite, f, indent=2, ensure_ascii=False)

    return {
        "success": True,
        "message": f"Test case '{generated_id}' created and saved to test_suite.json!",
    }


@app.get("/run-evaluation")
async def run_evaluation():
    try:
        result = subprocess.run(
            [sys.executable, "run_evaluation.py"],
            capture_output=True,
            text=True,
        )
        output = result.stdout
        if result.stderr:
            output += "\n\nERROR:\n" + result.stderr
        return {"success": True, "output": output}
    except Exception as e:
        return {"success": False, "output": str(e)}


@app.get("/run-pairwise")
async def run_pairwise():
    try:
        result = subprocess.run(
            [sys.executable, "run_pairwise.py"],
            capture_output=True,
            text=True,
        )
        output = result.stdout
        if result.stderr:
            output += "\n\nERROR:\n" + result.stderr
        return {"success": True, "output": output}
    except Exception as e:
        return {"success": False, "output": str(e)}


@app.get("/run-analysis")
async def run_analysis():
    try:
        result = subprocess.run(
            [sys.executable, "run_analysis.py"],
            capture_output=True,
            text=True,
        )
        output = result.stdout
        if result.stderr:
            output += "\n\nERROR:\n" + result.stderr
        return {"success": True, "output": output}
    except Exception as e:
        return {"success": False, "output": str(e)}


@app.get("/report")
async def report():
    try:
        if not REPORT_PATH.exists():
            return {
                "total_cases": 0,
                "pass_rate": 0,
                "mean_score": 0,
                "results": [],
            }
        with open(REPORT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e)}


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "LLM Judge Dashboard"}


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)